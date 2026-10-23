"""P11 multistage stochastic optimization, decomposition, and cutting planes.

The solvers target finite, explicitly supplied models.  Benders currently
requires relatively complete recourse; infeasible subproblems are reported
instead of silently inventing feasibility cuts.  The SDDP implementation is a
small scalar-inventory specialization whose cuts come from LP duals.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from random import Random
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp


Key = Hashable


@dataclass(frozen=True)
class ScenarioNode:
    name: Key
    stage: int
    parent: Key | None
    conditional_probability: float


class ScenarioTree:
    """Finite rooted scenario tree with conditional branch probabilities."""

    def __init__(self, nodes: Sequence[ScenarioNode]) -> None:
        if not nodes or len({node.name for node in nodes}) != len(nodes):
            raise ValueError("scenario nodes must be non-empty and unique")
        self.nodes = {node.name: node for node in nodes}
        roots = [node for node in nodes if node.parent is None]
        if len(roots) != 1 or roots[0].stage != 0:
            raise ValueError("scenario tree needs one stage-zero root")
        self.root = roots[0].name
        children: dict[Key, list[Key]] = {node.name: [] for node in nodes}
        for node in nodes:
            probability = float(node.conditional_probability)
            if not isfinite(probability) or probability < 0.0:
                raise ValueError(
                    "scenario probabilities must be finite and non-negative"
                )
            if node.parent is None:
                if not np.isclose(probability, 1.0):
                    raise ValueError("scenario root probability must equal one")
                continue
            if node.parent not in self.nodes:
                raise ValueError("scenario parent is unknown")
            parent = self.nodes[node.parent]
            if node.stage != parent.stage + 1:
                raise ValueError("scenario stages must increase by one along each edge")
            children[node.parent].append(node.name)
        for parent, child_names in children.items():
            if child_names and not np.isclose(
                sum(self.nodes[name].conditional_probability for name in child_names),
                1.0,
                atol=1e-9,
            ):
                raise ValueError(
                    "conditional probabilities must sum to one at each branch"
                )
        self.children = {key: tuple(value) for key, value in children.items()}
        self._probabilities = {self.root: 1.0}
        for node in sorted(nodes, key=lambda value: value.stage):
            if node.parent is not None:
                self._probabilities[node.name] = (
                    self._probabilities[node.parent] * node.conditional_probability
                )

    def probability(self, node: Key) -> float:
        if node not in self._probabilities:
            raise ValueError("unknown scenario node")
        return self._probabilities[node]

    def path(self, node: Key) -> tuple[Key, ...]:
        if node not in self.nodes:
            raise ValueError("unknown scenario node")
        result = []
        current: Key | None = node
        while current is not None:
            result.append(current)
            current = self.nodes[current].parent
        return tuple(reversed(result))

    @property
    def leaves(self) -> tuple[Key, ...]:
        return tuple(name for name in self.nodes if not self.children[name])


@dataclass(frozen=True)
class ScenarioLinearNode:
    """One information-node decision block in a multistage stochastic LP.

    Local inequalities use ``a_ub @ x_node <= b_ub``. For non-root nodes,
    edge inequalities use
    ``parent_a_ub @ x_parent + current_a_ub @ x_node <= link_b_ub``.
    A decision is shared by all scenarios with the same history because each
    scenario-tree information node owns exactly one variable block.
    """

    name: Key
    cost: np.ndarray
    a_ub: np.ndarray
    b_ub: np.ndarray
    parent_a_ub: np.ndarray
    current_a_ub: np.ndarray
    link_b_ub: np.ndarray
    bounds: tuple[tuple[float | None, float | None], ...]


@dataclass(frozen=True)
class MultistageScenarioResult:
    decisions: Mapping[Key, np.ndarray]
    objective: float


def solve_multistage_scenario_tree_lp(
    tree: ScenarioTree,
    models: Sequence[ScenarioLinearNode],
) -> MultistageScenarioResult:
    """Solve a finite scenario-tree LP with history-based nonanticipativity."""
    by_name = {model.name: model for model in models}
    if len(by_name) != len(models) or set(by_name) != set(tree.nodes):
        raise ValueError("every scenario-tree node needs one unique linear model")
    ordered = tuple(
        sorted(tree.nodes, key=lambda name: (tree.nodes[name].stage, repr(name)))
    )
    offsets = {}
    total_size = 0
    validated = {}
    for name in ordered:
        model = by_name[name]
        cost = np.asarray(model.cost, dtype=np.float64)
        local_a = np.asarray(model.a_ub, dtype=np.float64)
        local_b = np.asarray(model.b_ub, dtype=np.float64)
        parent_a = np.asarray(model.parent_a_ub, dtype=np.float64)
        current_a = np.asarray(model.current_a_ub, dtype=np.float64)
        link_b = np.asarray(model.link_b_ub, dtype=np.float64)
        if local_a.size == 0:
            local_a = np.zeros((0, cost.size))
            local_b = np.zeros(0)
        if current_a.size == 0:
            current_a = np.zeros((0, cost.size))
            link_b = np.zeros(0)
        parent = tree.nodes[name].parent
        parent_size = 0 if parent is None else np.asarray(by_name[parent].cost).size
        if parent_a.size == 0:
            parent_a = np.zeros((current_a.shape[0], parent_size))
        arrays = (local_a, local_b, parent_a, current_a, link_b)
        if (
            cost.ndim != 1
            or cost.size == 0
            or np.any(~np.isfinite(cost))
            or local_a.shape != (local_b.size, cost.size)
            or current_a.shape != (link_b.size, cost.size)
            or parent_a.shape != (link_b.size, parent_size)
            or any(np.any(~np.isfinite(value)) for value in arrays)
            or len(model.bounds) != cost.size
        ):
            raise ValueError(
                "scenario-tree linear node dimensions or values are invalid"
            )
        if parent is None and link_b.size:
            raise ValueError("scenario-tree root cannot have parent-link constraints")
        bounds = []
        for lower, upper in model.bounds:
            if lower is not None and not isfinite(float(lower)):
                raise ValueError("scenario-tree variable lower bound must be finite")
            if upper is not None and not isfinite(float(upper)):
                raise ValueError("scenario-tree variable upper bound must be finite")
            if lower is not None and upper is not None and lower > upper:
                raise ValueError("scenario-tree variable bounds are inconsistent")
            bounds.append((lower, upper))
        offsets[name] = total_size
        total_size += cost.size
        validated[name] = (
            cost,
            local_a,
            local_b,
            parent_a,
            current_a,
            link_b,
            tuple(bounds),
        )
    objective = np.zeros(total_size)
    rows = []
    rhs = []
    all_bounds = []
    for name in ordered:
        cost, local_a, local_b, parent_a, current_a, link_b, bounds = validated[name]
        offset = offsets[name]
        objective[offset : offset + cost.size] = tree.probability(name) * cost
        all_bounds.extend(bounds)
        for local_row, bound in zip(local_a, local_b):
            row = np.zeros(total_size)
            row[offset : offset + cost.size] = local_row
            rows.append(row)
            rhs.append(bound)
        parent = tree.nodes[name].parent
        if parent is not None:
            parent_cost = validated[parent][0]
            parent_offset = offsets[parent]
            for parent_row, current_row, bound in zip(parent_a, current_a, link_b):
                row = np.zeros(total_size)
                row[parent_offset : parent_offset + parent_cost.size] = parent_row
                row[offset : offset + cost.size] = current_row
                rows.append(row)
                rhs.append(bound)
    solved = linprog(
        objective,
        A_ub=np.asarray(rows) if rows else None,
        b_ub=np.asarray(rhs) if rhs else None,
        bounds=all_bounds,
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"multistage scenario-tree LP failed: {solved.message}")
    decisions = {
        name: solved.x[offsets[name] : offsets[name] + validated[name][0].size]
        for name in ordered
    }
    return MultistageScenarioResult(decisions, float(solved.fun))


@dataclass(frozen=True)
class TwoStageScenario:
    name: Key
    probability: float
    recourse_cost: np.ndarray
    technology: np.ndarray
    recourse: np.ndarray
    demand: np.ndarray


@dataclass(frozen=True)
class TwoStageResult:
    first_stage: np.ndarray
    recourse: Mapping[Key, np.ndarray]
    objective: float


def _validate_two_stage(
    first_cost: Sequence[float],
    scenarios: Sequence[TwoStageScenario],
) -> tuple[np.ndarray, tuple[TwoStageScenario, ...]]:
    cost = np.asarray(first_cost, dtype=np.float64)
    values = tuple(scenarios)
    if cost.ndim != 1 or cost.size == 0 or np.any(~np.isfinite(cost)) or not values:
        raise ValueError("two-stage first-stage model is invalid")
    if not np.isclose(sum(value.probability for value in values), 1.0, atol=1e-9):
        raise ValueError("two-stage scenario probabilities must sum to one")
    names = {value.name for value in values}
    if len(names) != len(values):
        raise ValueError("two-stage scenario names must be unique")
    for scenario in values:
        q = np.asarray(scenario.recourse_cost, dtype=np.float64)
        technology = np.asarray(scenario.technology, dtype=np.float64)
        recourse = np.asarray(scenario.recourse, dtype=np.float64)
        demand = np.asarray(scenario.demand, dtype=np.float64)
        if (
            not isfinite(float(scenario.probability))
            or scenario.probability < 0.0
            or q.ndim != 1
            or technology.shape != (demand.size, cost.size)
            or recourse.shape != (demand.size, q.size)
            or demand.ndim != 1
            or np.any(~np.isfinite(q))
            or np.any(q < 0.0)
            or np.any(~np.isfinite(technology))
            or np.any(~np.isfinite(recourse))
            or np.any(~np.isfinite(demand))
        ):
            raise ValueError("two-stage recourse model is invalid")
    return cost, values


def solve_two_stage_stochastic_lp(
    first_cost: Sequence[float],
    first_a_ub: Sequence[Sequence[float]],
    first_b_ub: Sequence[float],
    scenarios: Sequence[TwoStageScenario],
    *,
    first_bounds: Sequence[tuple[float | None, float | None]] | None = None,
) -> TwoStageResult:
    """Solve a deterministic equivalent with W_s y_s >= h_s - T_s x."""
    cost, scenario_values = _validate_two_stage(first_cost, scenarios)
    first_a = np.asarray(first_a_ub, dtype=np.float64)
    first_b = np.asarray(first_b_ub, dtype=np.float64)
    if first_a.size == 0:
        first_a = np.zeros((0, cost.size))
        first_b = np.zeros(0)
    if first_a.shape != (first_b.size, cost.size):
        raise ValueError("first-stage inequality dimensions are invalid")
    offsets = {}
    size = cost.size
    objective = list(cost)
    for scenario in scenario_values:
        q = np.asarray(scenario.recourse_cost, dtype=np.float64)
        offsets[scenario.name] = size
        size += q.size
        objective.extend(scenario.probability * q)
    rows = []
    rhs = []
    for row, bound in zip(first_a, first_b):
        full = np.zeros(size)
        full[: cost.size] = row
        rows.append(full)
        rhs.append(bound)
    for scenario in scenario_values:
        technology = np.asarray(scenario.technology, dtype=np.float64)
        recourse = np.asarray(scenario.recourse, dtype=np.float64)
        demand = np.asarray(scenario.demand, dtype=np.float64)
        offset = offsets[scenario.name]
        for row_index in range(demand.size):
            full = np.zeros(size)
            full[: cost.size] = -technology[row_index]
            full[offset : offset + recourse.shape[1]] = -recourse[row_index]
            rows.append(full)
            rhs.append(-demand[row_index])
    bounds = list(first_bounds or [(0.0, None)] * cost.size)
    if len(bounds) != cost.size:
        raise ValueError("first-stage bounds dimension is invalid")
    bounds.extend((0.0, None) for _ in range(size - cost.size))
    solved = linprog(
        objective,
        A_ub=np.asarray(rows),
        b_ub=np.asarray(rhs),
        bounds=bounds,
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(
            f"two-stage deterministic equivalent failed: {solved.message}"
        )
    recourse_values = {}
    for scenario in scenario_values:
        offset = offsets[scenario.name]
        width = np.asarray(scenario.recourse_cost).size
        recourse_values[scenario.name] = solved.x[offset : offset + width]
    return TwoStageResult(solved.x[: cost.size], recourse_values, float(solved.fun))


@dataclass(frozen=True)
class BendersResult:
    first_stage: np.ndarray
    recourse_values: Mapping[Key, np.ndarray]
    objective: float
    lower_bound: float
    upper_bound: float
    iterations: int
    cut_count: int


def solve_two_stage_benders(
    first_cost: Sequence[float],
    first_a_ub: Sequence[Sequence[float]],
    first_b_ub: Sequence[float],
    scenarios: Sequence[TwoStageScenario],
    *,
    first_bounds: Sequence[tuple[float | None, float | None]] | None = None,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
) -> BendersResult:
    """L-shaped Benders with one optimality-cut pool per scenario."""
    cost, scenario_values = _validate_two_stage(first_cost, scenarios)
    first_a = np.asarray(first_a_ub, dtype=np.float64)
    first_b = np.asarray(first_b_ub, dtype=np.float64)
    if first_a.size == 0:
        first_a = np.zeros((0, cost.size))
        first_b = np.zeros(0)
    if (
        first_a.shape != (first_b.size, cost.size)
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("Benders first-stage model or configuration is invalid")
    x_bounds = list(first_bounds or [(0.0, None)] * cost.size)
    if len(x_bounds) != cost.size:
        raise ValueError("Benders first-stage bounds dimension is invalid")
    cuts: list[tuple[int, np.ndarray, float]] = []
    lower_bound = -float("inf")
    upper_bound = float("inf")
    best_x = None
    best_recourse: dict[Key, np.ndarray] = {}
    theta_offset = cost.size
    master_cost = np.r_[cost, [scenario.probability for scenario in scenario_values]]
    master_bounds = x_bounds + [(0.0, None)] * len(scenario_values)
    for iteration in range(1, max_iterations + 1):
        master_rows = []
        master_rhs = []
        for row, bound in zip(first_a, first_b):
            master_rows.append(np.r_[row, np.zeros(len(scenario_values))])
            master_rhs.append(bound)
        for scenario_index, slope, intercept in cuts:
            row = np.zeros(master_cost.size)
            row[: cost.size] = -slope
            row[theta_offset + scenario_index] = -1.0
            master_rows.append(row)
            master_rhs.append(-intercept)
        master = linprog(
            master_cost,
            A_ub=np.asarray(master_rows) if master_rows else None,
            b_ub=np.asarray(master_rhs) if master_rhs else None,
            bounds=master_bounds,
            method="highs",
        )
        if not master.success:
            raise RuntimeError(f"Benders master failed: {master.message}")
        x = master.x[: cost.size]
        lower_bound = float(master.fun)
        recourse_total = 0.0
        current_recourse = {}
        violated = False
        for scenario_index, scenario in enumerate(scenario_values):
            q = np.asarray(scenario.recourse_cost, dtype=np.float64)
            technology = np.asarray(scenario.technology, dtype=np.float64)
            recourse = np.asarray(scenario.recourse, dtype=np.float64)
            demand = np.asarray(scenario.demand, dtype=np.float64)
            subproblem = linprog(
                q,
                A_ub=-recourse,
                b_ub=technology @ x - demand,
                bounds=[(0.0, None)] * q.size,
                method="highs",
            )
            if not subproblem.success:
                raise RuntimeError(
                    "Benders subproblem is infeasible or unbounded; "
                    "this solver requires relatively complete recourse"
                )
            current_recourse[scenario.name] = subproblem.x
            recourse_total += scenario.probability * float(subproblem.fun)
            dual = -np.asarray(subproblem.ineqlin.marginals, dtype=np.float64)
            slope = dual @ technology
            intercept = float(dual @ demand)
            theta = master.x[theta_offset + scenario_index]
            if float(subproblem.fun) > theta + tolerance:
                cuts.append((scenario_index, slope, intercept))
                violated = True
        candidate_upper = float(cost @ x + recourse_total)
        if candidate_upper < upper_bound:
            upper_bound = candidate_upper
            best_x = x.copy()
            best_recourse = current_recourse
        if not violated and upper_bound - lower_bound <= tolerance:
            return BendersResult(
                best_x if best_x is not None else x,
                best_recourse or current_recourse,
                upper_bound,
                lower_bound,
                upper_bound,
                iteration,
                len(cuts),
            )
    if best_x is None:
        raise RuntimeError("Benders did not produce a feasible incumbent")
    return BendersResult(
        best_x,
        best_recourse,
        upper_bound,
        lower_bound,
        upper_bound,
        max_iterations,
        len(cuts),
    )


@dataclass(frozen=True)
class MasterColumn:
    name: Key
    cost: float
    coefficients: np.ndarray


@dataclass(frozen=True)
class ColumnGenerationResult:
    weights: Mapping[Key, float]
    objective: float
    dual_prices: np.ndarray
    columns: tuple[MasterColumn, ...]
    iterations: int


PricingOracle = Callable[[np.ndarray], MasterColumn | None]


def column_generation(
    demand: Sequence[float],
    initial_columns: Sequence[MasterColumn],
    pricing: PricingOracle,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 100,
) -> ColumnGenerationResult:
    """Dantzig-Wolfe column generation for min c*lambda, A*lambda = demand."""
    rhs = np.asarray(demand, dtype=np.float64)
    columns = list(initial_columns)
    if (
        rhs.ndim != 1
        or rhs.size == 0
        or np.any(~np.isfinite(rhs))
        or not columns
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("column-generation master is invalid")

    def validate(column: MasterColumn) -> None:
        coefficients = np.asarray(column.coefficients, dtype=np.float64)
        if (
            coefficients.shape != rhs.shape
            or np.any(~np.isfinite(coefficients))
            or not isfinite(float(column.cost))
        ):
            raise ValueError("master column is invalid")

    for column in columns:
        validate(column)
    for iteration in range(1, max_iterations + 1):
        matrix = np.column_stack([column.coefficients for column in columns])
        solved = linprog(
            [column.cost for column in columns],
            A_eq=matrix,
            b_eq=rhs,
            bounds=[(0.0, None)] * len(columns),
            method="highs",
        )
        if not solved.success:
            raise RuntimeError(f"restricted master failed: {solved.message}")
        dual = np.asarray(solved.eqlin.marginals, dtype=np.float64)
        candidate = pricing(dual.copy())
        if candidate is None:
            return ColumnGenerationResult(
                {
                    column.name: float(weight)
                    for column, weight in zip(columns, solved.x)
                    if weight > tolerance
                },
                float(solved.fun),
                dual,
                tuple(columns),
                iteration,
            )
        validate(candidate)
        reduced_cost = float(candidate.cost - dual @ candidate.coefficients)
        if reduced_cost >= -tolerance:
            return ColumnGenerationResult(
                {
                    column.name: float(weight)
                    for column, weight in zip(columns, solved.x)
                    if weight > tolerance
                },
                float(solved.fun),
                dual,
                tuple(columns),
                iteration,
            )
        if any(
            candidate.name == existing.name
            or (
                np.allclose(candidate.coefficients, existing.coefficients)
                and np.isclose(candidate.cost, existing.cost)
            )
            for existing in columns
        ):
            raise RuntimeError(
                "pricing returned a duplicate negative-reduced-cost column"
            )
        columns.append(candidate)
    raise RuntimeError("column generation reached its iteration limit")


@dataclass(frozen=True)
class AffineCut:
    intercept: float
    slope: float

    def value(self, state: float) -> float:
        return self.intercept + self.slope * state


class PiecewiseLinearLowerBound:
    def __init__(self, cuts: Sequence[AffineCut] = (AffineCut(0.0, 0.0),)) -> None:
        if not cuts or any(
            not isfinite(cut.intercept) or not isfinite(cut.slope) for cut in cuts
        ):
            raise ValueError("piecewise-linear value needs finite cuts")
        self.cuts = list(cuts)

    def value(self, state: float) -> float:
        return max(cut.value(state) for cut in self.cuts)

    def add_support(self, state: float, value: float, slope: float) -> AffineCut:
        if not all(isfinite(item) for item in (state, value, slope)):
            raise ValueError("SDDP support point must be finite")
        cut = AffineCut(value - slope * state, slope)
        self.cuts.append(cut)
        return cut


@dataclass(frozen=True)
class InventoryStage:
    demands: tuple[float, ...]
    probabilities: tuple[float, ...]
    order_cost: float
    holding_cost: float
    shortage_cost: float
    order_capacity: float

    def __post_init__(self) -> None:
        if (
            not self.demands
            or len(self.demands) != len(self.probabilities)
            or any(not isfinite(value) for value in self.demands)
            or any(value < 0.0 or not isfinite(value) for value in self.probabilities)
            or not np.isclose(sum(self.probabilities), 1.0, atol=1e-9)
            or any(
                value < 0.0 or not isfinite(value)
                for value in (
                    self.order_cost,
                    self.holding_cost,
                    self.shortage_cost,
                    self.order_capacity,
                )
            )
        ):
            raise ValueError("inventory SDDP stage is invalid")


@dataclass(frozen=True)
class InventoryStageSolution:
    objective: float
    order: float
    subgradient: float


def _solve_inventory_stage(
    state: float,
    stage: InventoryStage,
    next_value: PiecewiseLinearLowerBound,
) -> InventoryStageSolution:
    scenario_count = len(stage.demands)
    size = 1 + 3 * scenario_count
    objective = np.zeros(size)
    objective[0] = stage.order_cost
    equalities = np.zeros((scenario_count, size))
    equality_rhs = np.zeros(scenario_count)
    inequalities = []
    inequality_rhs = []
    for index, (demand, probability) in enumerate(
        zip(stage.demands, stage.probabilities)
    ):
        positive = 1 + 3 * index
        negative = positive + 1
        theta = positive + 2
        objective[positive] = probability * stage.holding_cost
        objective[negative] = probability * stage.shortage_cost
        objective[theta] = probability
        equalities[index, positive] = 1.0
        equalities[index, negative] = -1.0
        equalities[index, 0] = -1.0
        equality_rhs[index] = state - demand
        for cut in next_value.cuts:
            row = np.zeros(size)
            row[positive] = cut.slope
            row[negative] = -cut.slope
            row[theta] = -1.0
            inequalities.append(row)
            inequality_rhs.append(-cut.intercept)
    bounds = [(0.0, stage.order_capacity)]
    for _ in range(scenario_count):
        bounds.extend(((0.0, None), (0.0, None), (None, None)))
    solved = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(inequality_rhs),
        A_eq=equalities,
        b_eq=equality_rhs,
        bounds=bounds,
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"inventory stage LP failed: {solved.message}")
    gradient = float(np.sum(solved.eqlin.marginals))
    return InventoryStageSolution(float(solved.fun), float(solved.x[0]), gradient)


@dataclass(frozen=True)
class SDDPResult:
    value_functions: tuple[tuple[AffineCut, ...], ...]
    lower_bound: float
    first_order: float
    iterations: int


def sddp_inventory(
    stages: Sequence[InventoryStage],
    initial_inventory: float,
    *,
    iterations: int = 50,
    seed: int = 0,
    terminal_holding: float = 0.0,
    terminal_shortage: float = 0.0,
) -> SDDPResult:
    """Dual-cut SDDP for a scalar inventory problem with stagewise independence."""
    stage_values = tuple(stages)
    if (
        not stage_values
        or not isfinite(initial_inventory)
        or iterations <= 0
        or terminal_holding < 0.0
        or terminal_shortage < 0.0
    ):
        raise ValueError("inventory SDDP configuration is invalid")
    values = [PiecewiseLinearLowerBound() for _ in stage_values]
    terminal = PiecewiseLinearLowerBound(
        (AffineCut(0.0, terminal_holding), AffineCut(0.0, -terminal_shortage))
    )
    values.append(terminal)
    rng = Random(seed)
    for _ in range(iterations):
        visited = []
        state = float(initial_inventory)
        for stage_index, stage in enumerate(stage_values):
            visited.append(state)
            solved = _solve_inventory_stage(state, stage, values[stage_index + 1])
            demand = rng.choices(stage.demands, weights=stage.probabilities, k=1)[0]
            state = state + solved.order - demand
        for stage_index in reversed(range(len(stage_values))):
            solved = _solve_inventory_stage(
                visited[stage_index], stage_values[stage_index], values[stage_index + 1]
            )
            values[stage_index].add_support(
                visited[stage_index], solved.objective, solved.subgradient
            )
    first = _solve_inventory_stage(initial_inventory, stage_values[0], values[1])
    return SDDPResult(
        tuple(tuple(value.cuts) for value in values),
        values[0].value(initial_inventory),
        first.order,
        iterations,
    )


@dataclass(frozen=True)
class Polyhedron:
    a_ub: np.ndarray
    b_ub: np.ndarray

    def __post_init__(self) -> None:
        a = np.asarray(self.a_ub, dtype=np.float64)
        b = np.asarray(self.b_ub, dtype=np.float64)
        if (
            a.ndim != 2
            or b.shape != (a.shape[0],)
            or a.shape[1] == 0
            or np.any(~np.isfinite(a))
            or np.any(~np.isfinite(b))
        ):
            raise ValueError("polyhedron inequalities are invalid")
        object.__setattr__(self, "a_ub", a)
        object.__setattr__(self, "b_ub", b)

    def contains(self, point: Sequence[float], tolerance: float = 1e-9) -> bool:
        value = np.asarray(point, dtype=np.float64)
        return value.shape == (self.a_ub.shape[1],) and bool(
            np.all(self.a_ub @ value <= self.b_ub + tolerance)
        )

    def vertices(self, tolerance: float = 1e-9) -> tuple[np.ndarray, ...]:
        """Enumerate vertices of a small bounded full-dimensional polyhedron."""
        dimension = self.a_ub.shape[1]
        found = []
        for active in combinations(range(self.a_ub.shape[0]), dimension):
            matrix = self.a_ub[list(active)]
            if np.linalg.matrix_rank(matrix) < dimension:
                continue
            point = np.linalg.solve(matrix, self.b_ub[list(active)])
            if not self.contains(point, tolerance):
                continue
            if not any(
                np.allclose(point, existing, atol=tolerance) for existing in found
            ):
                found.append(point)
        return tuple(sorted(found, key=lambda point: tuple(point)))


@dataclass(frozen=True)
class LinearCut:
    coefficients: np.ndarray
    rhs: float

    def violation(self, point: Sequence[float]) -> float:
        return float(self.coefficients @ np.asarray(point, dtype=np.float64) - self.rhs)


def chvatal_gomory_cut(
    a_ub: Sequence[Sequence[float]],
    b_ub: Sequence[float],
    multiplier: Sequence[float],
    *,
    tolerance: float = 1e-9,
) -> LinearCut:
    """Build floor(u*A)x <= floor(u*b) for integer x and u >= 0."""
    matrix = np.asarray(a_ub, dtype=np.float64)
    rhs = np.asarray(b_ub, dtype=np.float64)
    weights = np.asarray(multiplier, dtype=np.float64)
    if (
        matrix.ndim != 2
        or rhs.shape != (matrix.shape[0],)
        or weights.shape != rhs.shape
        or np.any(~np.isfinite(matrix))
        or np.any(~np.isfinite(rhs))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
    ):
        raise ValueError("Chvatal-Gomory input is invalid")
    combined = weights @ matrix
    rounded = np.rint(combined)
    if not np.allclose(combined, rounded, atol=tolerance):
        raise ValueError("Chvatal-Gomory multiplier must yield integral coefficients")
    return LinearCut(
        rounded.astype(np.float64), float(np.floor(weights @ rhs + tolerance))
    )


def minimal_cover_cut(
    weights: Sequence[float],
    capacity: float,
    fractional_solution: Sequence[float],
) -> tuple[tuple[int, ...], LinearCut]:
    """Greedily separate a violated minimal 0-1 knapsack cover cut."""
    item_weights = np.asarray(weights, dtype=np.float64)
    point = np.asarray(fractional_solution, dtype=np.float64)
    if (
        item_weights.ndim != 1
        or point.shape != item_weights.shape
        or item_weights.size == 0
        or np.any(~np.isfinite(item_weights))
        or np.any(item_weights <= 0.0)
        or not isfinite(capacity)
        or capacity < 0.0
        or np.any(point < 0.0)
        or np.any(point > 1.0)
    ):
        raise ValueError("cover-cut knapsack data is invalid")
    order = sorted(
        range(item_weights.size), key=lambda i: (-point[i], -item_weights[i], i)
    )
    cover = []
    total = 0.0
    for index in order:
        cover.append(index)
        total += item_weights[index]
        if total > capacity:
            break
    if total <= capacity:
        raise ValueError("no cover exists for the supplied knapsack")
    changed = True
    while changed:
        changed = False
        for index in tuple(cover):
            if total - item_weights[index] > capacity:
                cover.remove(index)
                total -= item_weights[index]
                changed = True
    coefficients = np.zeros(item_weights.size)
    coefficients[cover] = 1.0
    cut = LinearCut(coefficients, float(len(cover) - 1))
    if cut.violation(point) <= 1e-9:
        raise ValueError("the generated cover is not violated by the supplied point")
    return tuple(sorted(cover)), cut


@dataclass(frozen=True)
class BinaryMILPResult:
    solution: np.ndarray
    objective: float


def solve_binary_linear_program(
    objective: Sequence[float],
    a_ub: Sequence[Sequence[float]],
    b_ub: Sequence[float],
    *,
    maximize: bool = False,
) -> BinaryMILPResult:
    """Small auditable binary MILP helper used to verify generated cuts."""
    cost = np.asarray(objective, dtype=np.float64)
    matrix = np.asarray(a_ub, dtype=np.float64)
    rhs = np.asarray(b_ub, dtype=np.float64)
    if cost.ndim != 1 or matrix.shape != (rhs.size, cost.size):
        raise ValueError("binary MILP dimensions are invalid")
    sign = -1.0 if maximize else 1.0
    solved = milp(
        sign * cost,
        integrality=np.ones(cost.size),
        bounds=Bounds(np.zeros(cost.size), np.ones(cost.size)),
        constraints=LinearConstraint(matrix, -np.inf, rhs),
    )
    if not solved.success:
        raise RuntimeError(f"binary MILP failed: {solved.message}")
    objective_value = float(cost @ solved.x)
    return BinaryMILPResult(np.rint(solved.x).astype(int), objective_value)
