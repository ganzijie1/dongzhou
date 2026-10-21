"""Quantum-ready QUBO optimization for joint tactical actions.

The module compiles native legal actions into a QUBO, but deliberately keeps
the default solvers classical and auditable.  Real QAOA or annealing backends
can be injected through ``SampledQUBOSolver``; invalid samples never bypass the
native legality and space-time conflict checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite, prod
from typing import Callable, Mapping, Protocol, Sequence

from rl.lattice_geometry import Cell, SpaceTimeGrid


class QUBOError(ValueError):
    """Raised when a tactical QUBO or solver result violates its contract."""


class QUBOSizeError(QUBOError):
    """Raised when a solver cannot safely handle the compiled problem size."""


@dataclass(frozen=True)
class QUBOAction:
    action_index: int
    unit_id: int
    utility: float
    path: tuple[Cell, ...]

    def __post_init__(self) -> None:
        if not isfinite(self.utility):
            raise QUBOError("QUBO action utility must be finite")
        if not self.path:
            raise QUBOError("QUBO action path cannot be empty")


@dataclass(frozen=True)
class TacticalQUBO:
    actions: tuple[QUBOAction, ...]
    linear: tuple[float, ...]
    quadratic: Mapping[tuple[int, int], float]
    offset: float
    groups: Mapping[int, tuple[int, ...]]
    conflicts: frozenset[tuple[int, int]]

    @property
    def variable_count(self) -> int:
        return len(self.actions)

    @property
    def combination_count(self) -> int:
        return prod(len(group) for group in self.groups.values())

    def energy(self, selected: Sequence[int]) -> float:
        chosen = frozenset(int(value) for value in selected)
        if any(value < 0 or value >= self.variable_count for value in chosen):
            raise QUBOError("QUBO selection references an unknown variable")
        value = self.offset + sum(self.linear[index] for index in chosen)
        value += sum(
            coefficient
            for (left, right), coefficient in self.quadratic.items()
            if left in chosen and right in chosen
        )
        return float(value)

    def is_feasible(self, selected: Sequence[int]) -> bool:
        chosen = frozenset(int(value) for value in selected)
        if any(
            sum(variable in chosen for variable in variables) != 1
            for variables in self.groups.values()
        ):
            return False
        return not any(
            left in chosen and right in chosen for left, right in self.conflicts
        )

    def action_indices(self, selected: Sequence[int]) -> tuple[int, ...]:
        return tuple(sorted(self.actions[index].action_index for index in selected))


@dataclass(frozen=True)
class QUBOSolution:
    selected_variables: tuple[int, ...]
    selected_actions: tuple[int, ...]
    energy: float
    backend: str
    evaluated_states: int
    used_fallback: bool = False
    backend_error: str | None = None
    optimal: bool | None = None
    relative_gap: float | None = None
    solve_time_ms: float | None = None
    status: str | None = None


@dataclass(frozen=True)
class QuantumOptimizationConfig:
    exact_variable_limit: int = 20
    exact_combination_limit: int = 100_000
    bounded_node_limit: int = 25_000
    penalty_multiplier: float = 2.0
    time_horizon: int = 12

    def __post_init__(self) -> None:
        if self.exact_variable_limit <= 0 or self.exact_combination_limit <= 0:
            raise QUBOError("exact QUBO limits must be positive")
        if self.bounded_node_limit <= 0:
            raise QUBOError("bounded QUBO node limit must be positive")
        if not isfinite(self.penalty_multiplier) or self.penalty_multiplier <= 1.0:
            raise QUBOError(
                "QUBO penalty multiplier must be finite and greater than one"
            )
        if self.time_horizon < 0:
            raise QUBOError("QUBO time horizon must be non-negative")


def _paths_conflict(left: Sequence[Cell], right: Sequence[Cell], horizon: int) -> bool:
    reservations = SpaceTimeGrid()
    if not reservations.reserve_path(left, 1, horizon):
        raise QUBOError("unable to reserve a candidate path")
    return reservations.path_conflict(right, 2, horizon)


class TacticalQUBOCompiler:
    def __init__(self, config: QuantumOptimizationConfig | None = None) -> None:
        self.config = config or QuantumOptimizationConfig()

    def compile(self, actions: Sequence[QUBOAction]) -> TacticalQUBO:
        candidates = tuple(actions)
        if not candidates:
            raise QUBOError("cannot compile an empty tactical QUBO")
        if len({action.action_index for action in candidates}) != len(candidates):
            raise QUBOError("QUBO action indices must be unique")

        groups_mutable: dict[int, list[int]] = {}
        for variable, action in enumerate(candidates):
            groups_mutable.setdefault(action.unit_id, []).append(variable)
        groups = {
            unit_id: tuple(variables)
            for unit_id, variables in sorted(groups_mutable.items())
        }
        utility_bound = sum(
            max(abs(candidates[index].utility) for index in variables)
            for variables in groups.values()
        )
        penalty = self.config.penalty_multiplier * max(1.0, utility_bound + 1.0)
        linear = [-action.utility for action in candidates]
        quadratic: dict[tuple[int, int], float] = {}
        offset = 0.0

        # A(1 - sum x)^2 = A - A sum x + 2A sum_{i<j} x_i x_j.
        for variables in groups.values():
            offset += penalty
            for variable in variables:
                linear[variable] -= penalty
            for position, left in enumerate(variables):
                for right in variables[position + 1 :]:
                    quadratic[(left, right)] = (
                        quadratic.get((left, right), 0.0) + 2.0 * penalty
                    )

        conflicts: set[tuple[int, int]] = set()
        for left, left_action in enumerate(candidates):
            for right in range(left + 1, len(candidates)):
                right_action = candidates[right]
                if left_action.unit_id == right_action.unit_id:
                    continue
                if _paths_conflict(
                    left_action.path,
                    right_action.path,
                    self.config.time_horizon,
                ):
                    conflicts.add((left, right))
                    quadratic[(left, right)] = (
                        quadratic.get((left, right), 0.0) + penalty
                    )

        return TacticalQUBO(
            actions=candidates,
            linear=tuple(linear),
            quadratic=quadratic,
            offset=offset,
            groups=groups,
            conflicts=frozenset(conflicts),
        )


class QUBOSolver(Protocol):
    name: str

    def solve(self, model: TacticalQUBO) -> QUBOSolution: ...


class ExactQUBOSolver:
    name = "qubo-exact"

    def __init__(self, combination_limit: int = 100_000) -> None:
        self.combination_limit = int(combination_limit)

    def solve(self, model: TacticalQUBO) -> QUBOSolution:
        if model.combination_count > self.combination_limit:
            raise QUBOSizeError("QUBO exact combination limit exceeded")
        best: tuple[float, tuple[int, ...], tuple[int, ...]] | None = None
        evaluated = 0
        for selected in product(*model.groups.values()):
            evaluated += 1
            if not model.is_feasible(selected):
                continue
            actions = model.action_indices(selected)
            candidate = (model.energy(selected), actions, tuple(selected))
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        if best is None:
            raise QUBOError("tactical QUBO has no feasible joint action")
        return QUBOSolution(best[2], best[1], best[0], self.name, evaluated)


class BoundedQUBOSolver:
    """Deterministic branch search used when exact enumeration is too large."""

    name = "qubo-bounded"

    def __init__(self, node_limit: int = 25_000) -> None:
        self.node_limit = int(node_limit)

    def solve(self, model: TacticalQUBO) -> QUBOSolution:
        ordered_groups = sorted(
            model.groups.values(),
            key=lambda group: (len(group), model.actions[group[0]].unit_id),
        )
        ranked = [
            tuple(
                sorted(
                    group,
                    key=lambda index: (
                        -model.actions[index].utility,
                        model.actions[index].action_index,
                    ),
                )
            )
            for group in ordered_groups
        ]
        conflict_lookup = {variable: set() for variable in range(model.variable_count)}
        for left, right in model.conflicts:
            conflict_lookup[left].add(right)
            conflict_lookup[right].add(left)

        best: tuple[float, tuple[int, ...], tuple[int, ...]] | None = None
        selected: list[int] = []
        selected_set: set[int] = set()
        visited = 0

        def search(depth: int) -> None:
            nonlocal best, visited
            if visited >= self.node_limit:
                return
            visited += 1
            if depth == len(ranked):
                chosen = tuple(selected)
                actions = model.action_indices(chosen)
                candidate = (model.energy(chosen), actions, chosen)
                if best is None or candidate[:2] < best[:2]:
                    best = candidate
                return
            for variable in ranked[depth]:
                if conflict_lookup[variable] & selected_set:
                    continue
                selected.append(variable)
                selected_set.add(variable)
                search(depth + 1)
                selected_set.remove(variable)
                selected.pop()
                if visited >= self.node_limit:
                    return

        search(0)
        if best is None:
            raise QUBOError("bounded QUBO search found no feasible joint action")
        return QUBOSolution(best[2], best[1], best[0], self.name, visited)


QUBOSampler = Callable[
    [TacticalQUBO],
    Mapping[int, int | bool] | Sequence[Mapping[int, int | bool]],
]


class SampledQUBOSolver:
    """Adapter for QAOA, gate-model simulators, or quantum annealers."""

    def __init__(self, sampler: QUBOSampler, *, name: str) -> None:
        if not name or not name.strip():
            raise QUBOError("sampled QUBO backend needs a name")
        self.sampler = sampler
        self.name = "qubo-" + name.strip().lower().replace(" ", "-")

    def solve(self, model: TacticalQUBO) -> QUBOSolution:
        raw = self.sampler(model)
        samples = [raw] if isinstance(raw, Mapping) else list(raw)
        best: tuple[float, tuple[int, ...], tuple[int, ...]] | None = None
        for sample in samples:
            if not isinstance(sample, Mapping):
                continue
            if any(
                int(index) < 0 or int(index) >= model.variable_count for index in sample
            ):
                continue
            selected = tuple(
                sorted(int(index) for index, value in sample.items() if bool(value))
            )
            if not model.is_feasible(selected):
                continue
            actions = model.action_indices(selected)
            candidate = (model.energy(selected), actions, selected)
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        if best is None:
            raise QUBOError(f"{self.name} returned no feasible sample")
        return QUBOSolution(best[2], best[1], best[0], self.name, len(samples))


class TacticalQUBOOptimizer:
    """Compile, solve, validate, and fall back without weakening game rules."""

    def __init__(
        self,
        config: QuantumOptimizationConfig | None = None,
        *,
        external_solver: QUBOSolver | None = None,
    ) -> None:
        self.config = config or QuantumOptimizationConfig()
        self.compiler = TacticalQUBOCompiler(self.config)
        self.external_solver = external_solver
        self.exact_solver = ExactQUBOSolver(self.config.exact_combination_limit)
        self.bounded_solver = BoundedQUBOSolver(self.config.bounded_node_limit)

    def solve(self, actions: Sequence[QUBOAction]) -> QUBOSolution:
        model = self.compiler.compile(actions)
        backend_error: str | None = None
        if self.external_solver is not None:
            try:
                solution = self.external_solver.solve(model)
                if not model.is_feasible(solution.selected_variables):
                    raise QUBOError(
                        "external QUBO solver returned an infeasible sample"
                    )
                return solution
            except (
                ArithmeticError,
                KeyError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as error:
                backend_error = str(error)

        use_exact = (
            model.variable_count <= self.config.exact_variable_limit
            and model.combination_count <= self.config.exact_combination_limit
        )
        solver: QUBOSolver = self.exact_solver if use_exact else self.bounded_solver
        solution = solver.solve(model)
        if not model.is_feasible(solution.selected_variables):
            raise QUBOError("classical QUBO fallback returned an infeasible solution")
        if backend_error is None:
            return solution
        return QUBOSolution(
            selected_variables=solution.selected_variables,
            selected_actions=solution.selected_actions,
            energy=solution.energy,
            backend=solution.backend,
            evaluated_states=solution.evaluated_states,
            used_fallback=True,
            backend_error=backend_error,
        )
