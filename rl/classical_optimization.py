"""CP-SAT and MILP backends for the shared tactical action model.

Both solvers consume the same native-action variables, one-hot groups, and
space-time conflicts as the QUBO backend.  Optional dependency failures,
timeouts, and invalid solutions are explicit and fall through to the next
verified backend in the portfolio.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from time import perf_counter
from typing import Literal, Protocol, Sequence

from rl.quantum_optimization import (
    QUBOAction,
    QUBOError,
    QUBOSolution,
    TacticalQUBO,
    TacticalQUBOCompiler,
    TacticalQUBOOptimizer,
)


class OptimizationBackendUnavailable(RuntimeError):
    """Raised when an optional native optimization backend is unavailable."""


class TacticalActionOptimizer(Protocol):
    def solve(self, actions: Sequence[QUBOAction]) -> QUBOSolution: ...


@dataclass(frozen=True)
class ClassicalOptimizationConfig:
    backend: Literal["auto", "cp-sat", "milp", "qubo"] = "auto"
    cp_sat_time_limit: float = 0.05
    milp_time_limit: float = 0.05
    objective_scale: int = 1000
    relative_gap_limit: float = 0.0
    random_seed: int = 2026

    def __post_init__(self) -> None:
        if self.backend not in {"auto", "cp-sat", "milp", "qubo"}:
            raise ValueError(f"unknown tactical optimizer backend: {self.backend}")
        if self.cp_sat_time_limit <= 0.0 or self.milp_time_limit <= 0.0:
            raise ValueError("optimizer time limits must be positive")
        if self.objective_scale <= 0:
            raise ValueError("CP-SAT objective scale must be positive")
        if not isfinite(self.relative_gap_limit) or self.relative_gap_limit < 0.0:
            raise ValueError("relative gap limit must be finite and non-negative")


def _relative_gap(primal: float, bound: float) -> float:
    return abs(primal - bound) / max(1.0, abs(primal))


def _validate_solution(
    model: TacticalQUBO,
    selected: Sequence[int],
    backend: str,
) -> tuple[int, ...]:
    variables = tuple(sorted(int(value) for value in selected))
    if not model.is_feasible(variables):
        raise QUBOError(f"{backend} returned an infeasible tactical solution")
    return variables


class CPSATActionOptimizer:
    """Solve the shared Boolean action model with Google OR-Tools CP-SAT."""

    def __init__(
        self,
        config: ClassicalOptimizationConfig | None = None,
        *,
        compiler: TacticalQUBOCompiler | None = None,
    ) -> None:
        self.config = config or ClassicalOptimizationConfig(backend="cp-sat")
        self.compiler = compiler or TacticalQUBOCompiler()

    def solve(self, actions: Sequence[QUBOAction]) -> QUBOSolution:
        return self.solve_model(self.compiler.compile(actions))

    def solve_model(self, tactical: TacticalQUBO) -> QUBOSolution:
        try:
            from ortools.sat.python import cp_model
        except ImportError as error:
            raise OptimizationBackendUnavailable(
                "OR-Tools CP-SAT is not installed"
            ) from error

        started = perf_counter()
        model = cp_model.CpModel()
        variables = [
            model.new_bool_var(f"action_{index}_{action.action_index}")
            for index, action in enumerate(tactical.actions)
        ]
        for group in tactical.groups.values():
            model.add_exactly_one(variables[index] for index in group)
        for left, right in tactical.conflicts:
            model.add(variables[left] + variables[right] <= 1)
        coefficients = [
            int(round(action.utility * self.config.objective_scale))
            for action in tactical.actions
        ]
        model.maximize(
            sum(
                coefficient * variable
                for coefficient, variable in zip(coefficients, variables)
            )
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.config.cp_sat_time_limit
        solver.parameters.relative_gap_limit = self.config.relative_gap_limit
        solver.parameters.random_seed = self.config.random_seed
        solver.parameters.num_search_workers = 1
        status = solver.solve(model)
        elapsed = (perf_counter() - started) * 1000.0
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise QUBOError(f"CP-SAT returned {solver.status_name(status)}")
        selected = _validate_solution(
            tactical,
            [
                index
                for index, variable in enumerate(variables)
                if solver.value(variable)
            ],
            "CP-SAT",
        )
        primal = float(solver.objective_value)
        bound = float(solver.best_objective_bound)
        optimal = status == cp_model.OPTIMAL
        return QUBOSolution(
            selected_variables=selected,
            selected_actions=tactical.action_indices(selected),
            energy=tactical.energy(selected),
            backend="cp-sat-optimal" if optimal else "cp-sat-feasible",
            evaluated_states=int(solver.num_branches),
            optimal=optimal,
            relative_gap=0.0 if optimal else _relative_gap(primal, bound),
            solve_time_ms=elapsed,
            status=solver.status_name(status),
        )


class MILPActionOptimizer:
    """Solve the shared binary linear model with SciPy/HiGHS MILP."""

    def __init__(
        self,
        config: ClassicalOptimizationConfig | None = None,
        *,
        compiler: TacticalQUBOCompiler | None = None,
    ) -> None:
        self.config = config or ClassicalOptimizationConfig(backend="milp")
        self.compiler = compiler or TacticalQUBOCompiler()

    def solve(self, actions: Sequence[QUBOAction]) -> QUBOSolution:
        return self.solve_model(self.compiler.compile(actions))

    def solve_model(self, tactical: TacticalQUBO) -> QUBOSolution:
        try:
            import numpy as np
            from scipy.optimize import Bounds, LinearConstraint, milp
            from scipy.sparse import lil_matrix
        except ImportError as error:
            raise OptimizationBackendUnavailable(
                "SciPy MILP is not installed"
            ) from error

        started = perf_counter()
        rows = len(tactical.groups) + len(tactical.conflicts)
        matrix = lil_matrix((rows, tactical.variable_count), dtype=np.float64)
        lower = np.full(rows, -np.inf, dtype=np.float64)
        upper = np.ones(rows, dtype=np.float64)
        row = 0
        for group in tactical.groups.values():
            for variable in group:
                matrix[row, variable] = 1.0
            lower[row] = 1.0
            row += 1
        for left, right in tactical.conflicts:
            matrix[row, left] = 1.0
            matrix[row, right] = 1.0
            row += 1

        result = milp(
            c=np.asarray([-action.utility for action in tactical.actions]),
            integrality=np.ones(tactical.variable_count, dtype=np.int8),
            bounds=Bounds(
                np.zeros(tactical.variable_count),
                np.ones(tactical.variable_count),
            ),
            constraints=LinearConstraint(matrix.tocsr(), lower, upper),
            options={
                "time_limit": self.config.milp_time_limit,
                "mip_rel_gap": self.config.relative_gap_limit,
                "presolve": True,
            },
        )
        elapsed = (perf_counter() - started) * 1000.0
        if result.x is None:
            raise QUBOError(f"MILP returned no solution: {result.message}")
        selected = _validate_solution(
            tactical,
            np.flatnonzero(np.asarray(result.x) >= 0.5),
            "MILP",
        )
        optimal = int(result.status) == 0
        gap_value = getattr(result, "mip_gap", None)
        return QUBOSolution(
            selected_variables=selected,
            selected_actions=tactical.action_indices(selected),
            energy=tactical.energy(selected),
            backend="milp-optimal" if optimal else "milp-feasible",
            evaluated_states=int(getattr(result, "mip_node_count", 0) or 0),
            optimal=optimal,
            relative_gap=float(gap_value) if gap_value is not None else None,
            solve_time_ms=elapsed,
            status=str(result.message),
        )


class TacticalOptimizationPortfolio:
    """Select CP-SAT, MILP, or QUBO and preserve a verified fallback chain."""

    def __init__(
        self,
        config: ClassicalOptimizationConfig | None = None,
        *,
        qubo_optimizer: TacticalQUBOOptimizer | None = None,
    ) -> None:
        self.config = config or ClassicalOptimizationConfig()
        self.compiler = TacticalQUBOCompiler()
        self.cp_sat = CPSATActionOptimizer(self.config, compiler=self.compiler)
        self.milp = MILPActionOptimizer(self.config, compiler=self.compiler)
        self.qubo = qubo_optimizer or TacticalQUBOOptimizer()

    def _order(self) -> tuple[str, ...]:
        if self.config.backend == "auto":
            return "cp-sat", "milp", "qubo"
        if self.config.backend == "qubo":
            return ("qubo",)
        return self.config.backend, "qubo"

    def solve(self, actions: Sequence[QUBOAction]) -> QUBOSolution:
        tactical = self.compiler.compile(actions)
        errors: list[str] = []
        for backend in self._order():
            try:
                if backend == "cp-sat":
                    solution = self.cp_sat.solve_model(tactical)
                elif backend == "milp":
                    solution = self.milp.solve_model(tactical)
                else:
                    solution = self.qubo.solve(actions)
                if not tactical.is_feasible(solution.selected_variables):
                    raise QUBOError(f"{backend} failed portfolio validation")
                if not errors:
                    return solution
                return replace(
                    solution,
                    used_fallback=True,
                    backend_error="; ".join(errors),
                )
            except (
                ArithmeticError,
                ImportError,
                KeyError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as error:
                errors.append(f"{backend}: {error}")
        raise QUBOError(
            "all tactical optimization backends failed: " + "; ".join(errors)
        )
