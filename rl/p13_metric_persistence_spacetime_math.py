"""P13 transport metrics, persistence, and stochastic space-time lattices.

GW and FGW are non-convex and return the best iterate reached from the stated
initial coupling.  Finite Gromov-Hausdorff is exact only within the explicitly
enumerated correspondence limit.  Persistent-sheaf maps are supplied by the
caller and verified on global sections; no comparison map is invented.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import product
from math import inf, isfinite, sqrt
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog

from rl.p6_structure_math import CellularSheaf


Key = Hashable


def _probability(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if (
        result.ndim != 1
        or result.size == 0
        or np.any(~np.isfinite(result))
        or np.any(result < 0.0)
        or not np.isclose(result.sum(), 1.0, atol=1e-9)
    ):
        raise ValueError(f"{name} must be a finite probability vector")
    return result


def _metric(values: Sequence[Sequence[float]], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if (
        result.ndim != 2
        or result.shape[0] == 0
        or result.shape[0] != result.shape[1]
        or np.any(~np.isfinite(result))
        or np.any(result < -1e-12)
        or not np.allclose(result, result.T, atol=1e-9)
        or not np.allclose(np.diag(result), 0.0, atol=1e-9)
    ):
        raise ValueError(f"{name} must be a finite symmetric distance matrix")
    # Triangle inequalities are checked because the public API calls these metrics.
    if np.any(result[:, :, None] > result[:, None, :] + result[None, :, :] + 1e-9):
        raise ValueError(f"{name} violates the triangle inequality")
    return np.maximum(result, 0.0)


def _transport_lp(cost: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    rows, columns = cost.shape
    equality = np.zeros((rows + columns, rows * columns))
    for row in range(rows):
        equality[row, row * columns : (row + 1) * columns] = 1.0
    for column in range(columns):
        equality[rows + column, column::columns] = 1.0
    solved = linprog(
        cost.reshape(-1),
        A_eq=equality,
        b_eq=np.r_[left, right],
        bounds=(0.0, None),
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"finite optimal transport failed: {solved.message}")
    return solved.x.reshape(rows, columns)


@dataclass(frozen=True)
class TransportDistanceResult:
    distance: float
    cost: float
    coupling: np.ndarray
    iterations: int
    converged: bool


def wasserstein_distance(
    left_mass: Sequence[float],
    right_mass: Sequence[float],
    cross_distance: Sequence[Sequence[float]],
    *,
    order: float = 1.0,
) -> TransportDistanceResult:
    """Exact finite p-Wasserstein distance for a supplied cross-distance matrix."""
    left = _probability(left_mass, "left mass")
    right = _probability(right_mass, "right mass")
    distance = np.asarray(cross_distance, dtype=np.float64)
    if (
        distance.shape != (left.size, right.size)
        or np.any(~np.isfinite(distance))
        or np.any(distance < 0.0)
        or not isfinite(order)
        or order < 1.0
    ):
        raise ValueError("Wasserstein cross distances or order are invalid")
    powered = distance**order
    coupling = _transport_lp(powered, left, right)
    cost = float(np.sum(powered * coupling))
    return TransportDistanceResult(cost ** (1.0 / order), cost, coupling, 1, True)


def _structure_linearization(
    left_distance: np.ndarray,
    right_distance: np.ndarray,
    left_mass: np.ndarray,
    right_mass: np.ndarray,
    coupling: np.ndarray,
) -> np.ndarray:
    return (
        (left_distance**2 @ left_mass)[:, None]
        + (right_distance**2 @ right_mass)[None, :]
        - 2.0 * left_distance @ coupling @ right_distance.T
    )


def _structure_cost(
    left_distance: np.ndarray,
    right_distance: np.ndarray,
    left_mass: np.ndarray,
    right_mass: np.ndarray,
    coupling: np.ndarray,
) -> float:
    return float(
        np.sum(
            _structure_linearization(
                left_distance, right_distance, left_mass, right_mass, coupling
            )
            * coupling
        )
    )


def _conditional_gradient_step(
    current: np.ndarray,
    target: np.ndarray,
    objective,
) -> tuple[np.ndarray, float]:
    direction = target - current
    value_zero = float(objective(current))
    value_one = float(objective(target))
    midpoint = current + 0.5 * direction
    value_half = float(objective(midpoint))
    quadratic = 2.0 * (value_one + value_zero - 2.0 * value_half)
    linear = value_one - value_zero - quadratic
    if quadratic > 1e-15:
        step = min(1.0, max(0.0, -linear / (2.0 * quadratic)))
    else:
        step = 1.0 if value_one < value_zero else 0.0
    updated = current + step * direction
    return updated, float(objective(updated))


def gromov_wasserstein_distance(
    left_distance: Sequence[Sequence[float]],
    right_distance: Sequence[Sequence[float]],
    left_mass: Sequence[float],
    right_mass: Sequence[float],
    *,
    initial_coupling: Sequence[Sequence[float]] | None = None,
    tolerance: float = 1e-10,
    max_iterations: int = 200,
) -> TransportDistanceResult:
    """Squared-loss finite GW via conditional-gradient linearizations."""
    left_d = _metric(left_distance, "left internal distance")
    right_d = _metric(right_distance, "right internal distance")
    left = _probability(left_mass, "left mass")
    right = _probability(right_mass, "right mass")
    if left_d.shape[0] != left.size or right_d.shape[0] != right.size:
        raise ValueError("GW metric and mass dimensions are inconsistent")
    if tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("GW solver controls are invalid")
    if initial_coupling is None:
        coupling = np.outer(left, right)
    else:
        coupling = np.asarray(initial_coupling, dtype=np.float64)
        if (
            coupling.shape != (left.size, right.size)
            or np.any(coupling < 0.0)
            or np.any(~np.isfinite(coupling))
            or not np.allclose(coupling.sum(axis=1), left, atol=1e-8)
            or not np.allclose(coupling.sum(axis=0), right, atol=1e-8)
        ):
            raise ValueError("initial GW coupling is infeasible")

    def objective(value: np.ndarray) -> float:
        return _structure_cost(left_d, right_d, left, right, value)

    cost = objective(coupling)
    for iteration in range(1, max_iterations + 1):
        gradient = 2.0 * _structure_linearization(
            left_d, right_d, left, right, coupling
        )
        target = _transport_lp(gradient, left, right)
        updated, updated_cost = _conditional_gradient_step(coupling, target, objective)
        change = float(np.linalg.norm(updated - coupling, ord=1))
        coupling, cost = updated, updated_cost
        if change <= tolerance:
            return TransportDistanceResult(
                sqrt(max(0.0, cost)), cost, coupling, iteration, True
            )
    return TransportDistanceResult(
        sqrt(max(0.0, cost)), cost, coupling, max_iterations, False
    )


def fused_gromov_wasserstein_distance(
    left_distance: Sequence[Sequence[float]],
    right_distance: Sequence[Sequence[float]],
    left_mass: Sequence[float],
    right_mass: Sequence[float],
    feature_cost: Sequence[Sequence[float]],
    *,
    structure_weight: float = 0.5,
    tolerance: float = 1e-10,
    max_iterations: int = 200,
) -> TransportDistanceResult:
    """Finite FGW with linear feature cost and squared structural distortion."""
    left_d = _metric(left_distance, "left internal distance")
    right_d = _metric(right_distance, "right internal distance")
    left = _probability(left_mass, "left mass")
    right = _probability(right_mass, "right mass")
    features = np.asarray(feature_cost, dtype=np.float64)
    if (
        left_d.shape[0] != left.size
        or right_d.shape[0] != right.size
        or features.shape != (left.size, right.size)
        or np.any(~np.isfinite(features))
        or np.any(features < 0.0)
        or not isfinite(structure_weight)
        or not 0.0 <= structure_weight <= 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("FGW inputs or solver controls are invalid")
    coupling = np.outer(left, right)

    def objective(value: np.ndarray) -> float:
        structure = _structure_cost(left_d, right_d, left, right, value)
        return float(
            (1.0 - structure_weight) * np.sum(features * value)
            + structure_weight * structure
        )

    cost = objective(coupling)
    for iteration in range(1, max_iterations + 1):
        gradient = (
            1.0 - structure_weight
        ) * features + 2.0 * structure_weight * _structure_linearization(
            left_d, right_d, left, right, coupling
        )
        target = _transport_lp(gradient, left, right)
        updated, updated_cost = _conditional_gradient_step(coupling, target, objective)
        change = float(np.linalg.norm(updated - coupling, ord=1))
        coupling, cost = updated, updated_cost
        if change <= tolerance:
            return TransportDistanceResult(
                sqrt(max(0.0, cost)), cost, coupling, iteration, True
            )
    return TransportDistanceResult(
        sqrt(max(0.0, cost)), cost, coupling, max_iterations, False
    )


@dataclass(frozen=True)
class GromovHausdorffResult:
    distance: float
    distortion: float
    correspondence: frozenset[tuple[int, int]]
    enumerated_candidates: int


def finite_gromov_hausdorff_distance(
    left_distance: Sequence[Sequence[float]],
    right_distance: Sequence[Sequence[float]],
    *,
    max_candidates: int = 1_000_000,
) -> GromovHausdorffResult:
    """Exact finite GH by enumerating all minimal correspondence generators."""
    left = _metric(left_distance, "left GH distance")
    right = _metric(right_distance, "right GH distance")
    candidate_count = right.shape[0] ** left.shape[0] * left.shape[0] ** right.shape[0]
    if candidate_count > max_candidates or max_candidates <= 0:
        raise ValueError("finite GH enumeration exceeds max_candidates")
    best_distortion = inf
    best_relation: frozenset[tuple[int, int]] = frozenset()
    seen = set()
    enumerated = 0
    for left_to_right in product(range(right.shape[0]), repeat=left.shape[0]):
        base = {(i, j) for i, j in enumerate(left_to_right)}
        for right_to_left in product(range(left.shape[0]), repeat=right.shape[0]):
            relation = frozenset(base | {(i, j) for j, i in enumerate(right_to_left)})
            if relation in seen:
                continue
            seen.add(relation)
            enumerated += 1
            distortion = max(
                abs(left[i, k] - right[j, ell])
                for i, j in relation
                for k, ell in relation
            )
            if distortion < best_distortion - 1e-12:
                best_distortion = float(distortion)
                best_relation = relation
    return GromovHausdorffResult(
        best_distortion / 2.0, best_distortion, best_relation, enumerated
    )


class MultiparameterPersistenceModule:
    """A finite grid-indexed persistence module with checked commuting squares."""

    def __init__(
        self,
        dimensions: Mapping[tuple[int, ...], int],
        cover_maps: Mapping[
            tuple[tuple[int, ...], tuple[int, ...]], Sequence[Sequence[float]]
        ],
        *,
        tolerance: float = 1e-9,
    ) -> None:
        if not dimensions or tolerance <= 0.0:
            raise ValueError(
                "multiparameter module needs dimensions and positive tolerance"
            )
        parameter_size = len(next(iter(dimensions)))
        if parameter_size == 0 or any(
            len(parameter) != parameter_size for parameter in dimensions
        ):
            raise ValueError(
                "multiparameter indices must have one common positive dimension"
            )
        self.dimensions = {
            parameter: int(value) for parameter, value in dimensions.items()
        }
        if any(value < 0 for value in self.dimensions.values()):
            raise ValueError("persistence vector-space dimensions cannot be negative")
        self.parameter_size = parameter_size
        self.tolerance = float(tolerance)
        self.cover_maps = {}
        for (start, end), raw_matrix in cover_maps.items():
            if start not in self.dimensions or end not in self.dimensions:
                raise ValueError(
                    "persistence cover map references an unknown parameter"
                )
            delta = tuple(right - left for left, right in zip(start, end))
            if sum(delta) != 1 or any(value not in {0, 1} for value in delta):
                raise ValueError("persistence maps must be coordinate cover relations")
            matrix = np.asarray(raw_matrix, dtype=np.float64)
            if matrix.shape != (self.dimensions[end], self.dimensions[start]) or np.any(
                ~np.isfinite(matrix)
            ):
                raise ValueError("persistence cover map has invalid shape or values")
            self.cover_maps[(start, end)] = matrix
        self._validate_commuting_squares()

    @staticmethod
    def _leq(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
        return all(a <= b for a, b in zip(left, right))

    def _cover(self, start: tuple[int, ...], axis: int) -> tuple[int, ...]:
        value = list(start)
        value[axis] += 1
        return tuple(value)

    def _validate_commuting_squares(self) -> None:
        for start in self.dimensions:
            for first in range(self.parameter_size):
                for second in range(first + 1, self.parameter_size):
                    a = self._cover(start, first)
                    b = self._cover(start, second)
                    end = self._cover(a, second)
                    required = ((start, a), (a, end), (start, b), (b, end))
                    if end not in self.dimensions or not all(
                        edge in self.cover_maps for edge in required
                    ):
                        continue
                    first_path = self.cover_maps[(a, end)] @ self.cover_maps[(start, a)]
                    second_path = (
                        self.cover_maps[(b, end)] @ self.cover_maps[(start, b)]
                    )
                    if not np.allclose(first_path, second_path, atol=self.tolerance):
                        raise ValueError(
                            "multiparameter persistence square does not commute"
                        )

    def structure_map(self, start: tuple[int, ...], end: tuple[int, ...]) -> np.ndarray:
        if (
            start not in self.dimensions
            or end not in self.dimensions
            or not self._leq(start, end)
        ):
            raise ValueError("persistence parameters are unknown or incomparable")
        result = np.eye(self.dimensions[start])
        current = start
        for axis in range(self.parameter_size):
            while current[axis] < end[axis]:
                following = self._cover(current, axis)
                if (current, following) not in self.cover_maps:
                    raise ValueError("persistence path is missing a cover map")
                result = self.cover_maps[(current, following)] @ result
                current = following
        return result

    def hilbert_function(self) -> dict[tuple[int, ...], int]:
        return dict(self.dimensions)

    def rank_invariant(self, start: tuple[int, ...], end: tuple[int, ...]) -> int:
        return int(
            np.linalg.matrix_rank(self.structure_map(start, end), tol=self.tolerance)
        )

    def fibered_path_ranks(
        self, path: Sequence[tuple[int, ...]]
    ) -> dict[tuple[int, int], int]:
        values = tuple(path)
        if (
            not values
            or any(value not in self.dimensions for value in values)
            or any(
                not self._leq(left, right) for left, right in zip(values, values[1:])
            )
        ):
            raise ValueError(
                "fibered path must be a monotone path through known parameters"
            )
        return {
            (start, end): self.rank_invariant(values[start], values[end])
            for start in range(len(values))
            for end in range(start, len(values))
        }


class PersistentSheafSequence:
    """Forward algebraic persistence of graph cellular sheaves in degree zero."""

    def __init__(
        self,
        sheaves: Sequence[CellularSheaf],
        cochain_maps: Sequence[Sequence[Sequence[float]]],
        *,
        tolerance: float = 1e-9,
    ) -> None:
        self.sheaves = tuple(sheaves)
        if (
            not self.sheaves
            or len(cochain_maps) != len(self.sheaves) - 1
            or tolerance <= 0.0
        ):
            raise ValueError("persistent sheaf sequence dimensions are invalid")
        self.tolerance = float(tolerance)
        self.section_bases = tuple(
            sheaf.global_sections(tolerance=tolerance) for sheaf in self.sheaves
        )
        induced = []
        self.cochain_maps = []
        for index, raw_map in enumerate(cochain_maps):
            value = np.asarray(raw_map, dtype=np.float64)
            expected = (
                self.sheaves[index + 1].total_vertex_dimension,
                self.sheaves[index].total_vertex_dimension,
            )
            if value.shape != expected or np.any(~np.isfinite(value)):
                raise ValueError(
                    "persistent sheaf cochain map has invalid shape or values"
                )
            source_basis = self.section_bases[index]
            target_basis = self.section_bases[index + 1]
            mapped = value @ source_basis
            residual = self.sheaves[index + 1].coboundary() @ mapped
            if residual.size and np.linalg.norm(residual) > tolerance:
                raise ValueError(
                    "cochain map does not send global sections to global sections"
                )
            induced.append(target_basis.T @ mapped)
            self.cochain_maps.append(value)
        self.induced_maps = tuple(induced)

    @property
    def betti_numbers(self) -> tuple[int, ...]:
        return tuple(basis.shape[1] for basis in self.section_bases)

    def persistent_betti(self, start: int, end: int) -> int:
        if not 0 <= start <= end < len(self.sheaves):
            raise ValueError("persistent sheaf indices are invalid")
        result = np.eye(self.section_bases[start].shape[1])
        for index in range(start, end):
            result = self.induced_maps[index] @ result
        return int(np.linalg.matrix_rank(result, tol=self.tolerance))

    def laplacian_spectra(self) -> tuple[np.ndarray, ...]:
        return tuple(np.linalg.eigvalsh(sheaf.laplacian()) for sheaf in self.sheaves)


def minkowski_interval(
    first: Sequence[float], second: Sequence[float], *, propagation_speed: float = 1.0
) -> float:
    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    if (
        left.ndim != 1
        or left.size < 2
        or right.shape != left.shape
        or np.any(~np.isfinite(left))
        or np.any(~np.isfinite(right))
        or not isfinite(propagation_speed)
        or propagation_speed <= 0.0
    ):
        raise ValueError("space-time events or propagation speed are invalid")
    delta = right - left
    return float((propagation_speed * delta[0]) ** 2 - delta[1:] @ delta[1:])


def causally_precedes(
    first: Sequence[float], second: Sequence[float], *, propagation_speed: float = 1.0
) -> bool:
    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    return bool(
        left.shape == right.shape
        and left.size >= 2
        and right[0] >= left[0]
        and minkowski_interval(left, right, propagation_speed=propagation_speed)
        >= -1e-10
    )


def time_expanded_shortest_path(
    nodes: Sequence[Key],
    edges: Sequence[Sequence[Key]],
    start: Key,
    goal: Key,
    horizon: int,
    *,
    blocked: Mapping[int, Sequence[Key]] | None = None,
    allow_wait: bool = True,
) -> tuple[Key, ...]:
    """Earliest feasible path in a discrete space-time graph."""
    node_values = tuple(dict.fromkeys(nodes))
    node_set = set(node_values)
    if start not in node_set or goal not in node_set or horizon < 0:
        raise ValueError("space-time path nodes or horizon are invalid")
    adjacency = {node: set() for node in node_values}
    for edge in edges:
        if (
            len(edge) != 2
            or edge[0] not in node_set
            or edge[1] not in node_set
            or edge[0] == edge[1]
        ):
            raise ValueError("space-time graph edge is invalid")
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    forbidden = {time: set(values) for time, values in (blocked or {}).items()}
    if start in forbidden.get(0, set()):
        return ()
    frontier = [(start, 0)]
    parent: dict[tuple[Key, int], tuple[Key, int]] = {}
    visited = {(start, 0)}
    target = None
    for node, time in frontier:
        if node == goal:
            target = (node, time)
            break
        if time == horizon:
            continue
        candidates = set(adjacency[node])
        if allow_wait:
            candidates.add(node)
        for following in sorted(candidates, key=repr):
            state = (following, time + 1)
            if following in forbidden.get(time + 1, set()) or state in visited:
                continue
            visited.add(state)
            parent[state] = (node, time)
            frontier.append(state)
    if target is None:
        return ()
    states = [target]
    while states[-1] != (start, 0):
        states.append(parent[states[-1]])
    return tuple(node for node, _ in reversed(states))


def explicit_graph_diffusion_step(
    values: Sequence[float],
    conductance: Sequence[Sequence[float]],
    time_step: float,
) -> np.ndarray:
    state = np.asarray(values, dtype=np.float64)
    weights = np.asarray(conductance, dtype=np.float64)
    if (
        state.ndim != 1
        or weights.shape != (state.size, state.size)
        or np.any(~np.isfinite(state))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not np.allclose(weights, weights.T, atol=1e-10)
        or not np.allclose(np.diag(weights), 0.0, atol=1e-10)
        or not isfinite(time_step)
        or time_step < 0.0
    ):
        raise ValueError("graph diffusion inputs are invalid")
    degree = weights.sum(axis=1)
    maximum = float(degree.max(initial=0.0))
    if maximum > 0.0 and time_step > 1.0 / maximum + 1e-12:
        raise ValueError(
            "explicit diffusion time step violates the positivity CFL bound"
        )
    laplacian = np.diag(degree) - weights
    return state - time_step * laplacian @ state


def connected_components(
    nodes: Sequence[Key], edges: Sequence[Sequence[Key]]
) -> tuple[frozenset[Key], ...]:
    node_values = tuple(dict.fromkeys(nodes))
    node_set = set(node_values)
    adjacency = {node: set() for node in node_values}
    for edge in edges:
        if (
            len(edge) != 2
            or edge[0] not in node_set
            or edge[1] not in node_set
            or edge[0] == edge[1]
        ):
            raise ValueError("component graph edge is invalid")
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    remaining = set(node_values)
    result = []
    while remaining:
        root = min(remaining, key=repr)
        remaining.remove(root)
        component = {root}
        stack = [root]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        result.append(frozenset(component))
    return tuple(
        sorted(result, key=lambda value: (-len(value), tuple(sorted(map(repr, value)))))
    )


@dataclass(frozen=True)
class PercolationSample:
    open_nodes: frozenset[Key]
    open_edges: tuple[tuple[Key, Key], ...]
    clusters: tuple[frozenset[Key], ...]


def site_percolation(
    nodes: Sequence[Key],
    edges: Sequence[Sequence[Key]],
    probability: float,
    *,
    seed: int | None = None,
) -> PercolationSample:
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("site-open probability must be between zero and one")
    random = np.random.default_rng(seed)
    node_values = tuple(dict.fromkeys(nodes))
    node_set = set(node_values)
    edge_values = []
    for edge in edges:
        if (
            len(edge) != 2
            or edge[0] not in node_set
            or edge[1] not in node_set
            or edge[0] == edge[1]
        ):
            raise ValueError("site-percolation edge is invalid")
        edge_values.append((edge[0], edge[1]))
    open_nodes = frozenset(
        node for node in node_values if random.random() < probability
    )
    open_edges = tuple(
        (edge[0], edge[1])
        for edge in edge_values
        if edge[0] in open_nodes and edge[1] in open_nodes
    )
    clusters = connected_components(tuple(open_nodes), open_edges) if open_nodes else ()
    return PercolationSample(open_nodes, open_edges, clusters)


def bond_percolation(
    nodes: Sequence[Key],
    edges: Sequence[Sequence[Key]],
    probability: float,
    *,
    seed: int | None = None,
) -> PercolationSample:
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("bond-open probability must be between zero and one")
    node_values = tuple(dict.fromkeys(nodes))
    node_set = set(node_values)
    random = np.random.default_rng(seed)
    open_edges = []
    for edge in edges:
        if (
            len(edge) != 2
            or edge[0] not in node_set
            or edge[1] not in node_set
            or edge[0] == edge[1]
        ):
            raise ValueError("bond-percolation edge is invalid")
        if random.random() < probability:
            open_edges.append((edge[0], edge[1]))
    return PercolationSample(
        frozenset(node_values),
        tuple(open_edges),
        connected_components(node_values, open_edges),
    )


def conductance_laplacian(
    nodes: Sequence[Key], conductances: Mapping[tuple[Key, Key], float]
) -> np.ndarray:
    node_values = tuple(dict.fromkeys(nodes))
    index = {node: position for position, node in enumerate(node_values)}
    matrix = np.zeros((len(node_values), len(node_values)))
    for (left, right), raw_value in conductances.items():
        value = float(raw_value)
        if (
            left == right
            or left not in index
            or right not in index
            or not isfinite(value)
            or value <= 0.0
        ):
            raise ValueError("random conductance edge is invalid")
        i, j = index[left], index[right]
        matrix[i, j] += value
        matrix[j, i] += value
    return np.diag(matrix.sum(axis=1)) - matrix


def effective_resistance(
    nodes: Sequence[Key],
    conductances: Mapping[tuple[Key, Key], float],
    source: Key,
    target: Key,
) -> float:
    node_values = tuple(dict.fromkeys(nodes))
    if source not in node_values or target not in node_values:
        raise ValueError("effective-resistance endpoint is unknown")
    if source == target:
        return 0.0
    full_laplacian = conductance_laplacian(node_values, conductances)
    index = {node: position for position, node in enumerate(node_values)}
    adjacency = {node: set() for node in node_values}
    for left, right in conductances:
        adjacency[left].add(right)
        adjacency[right].add(left)
    component = {source}
    frontier = [source]
    while frontier:
        current = frontier.pop()
        for neighbor in adjacency[current]:
            if neighbor not in component:
                component.add(neighbor)
                frontier.append(neighbor)
    if target not in component:
        return inf
    selected = [index[node] for node in node_values if node in component]
    laplacian = full_laplacian[np.ix_(selected, selected)]
    local_index = {
        node: position
        for position, node in enumerate(
            node for node in node_values if node in component
        )
    }
    inverse = np.linalg.pinv(laplacian, hermitian=True)
    vector = np.zeros(len(selected))
    vector[local_index[source]] = 1.0
    vector[local_index[target]] = -1.0
    return float(vector @ inverse @ vector)


def first_passage_time(
    nodes: Sequence[Key],
    passage_times: Mapping[tuple[Key, Key], float],
    source: Key,
    target: Key,
) -> tuple[float, tuple[Key, ...]]:
    node_values = tuple(dict.fromkeys(nodes))
    node_set = set(node_values)
    if source not in node_set or target not in node_set:
        raise ValueError("first-passage endpoint is unknown")
    adjacency = {node: [] for node in node_values}
    for (left, right), raw_value in passage_times.items():
        value = float(raw_value)
        if (
            left == right
            or left not in node_set
            or right not in node_set
            or not isfinite(value)
            or value < 0.0
        ):
            raise ValueError("passage-time edge is invalid")
        adjacency[left].append((right, value))
        adjacency[right].append((left, value))
    distances = {source: 0.0}
    parent = {}
    queue = [(0.0, repr(source), source)]
    while queue:
        spent, _, node = heappop(queue)
        if spent != distances.get(node):
            continue
        if node == target:
            path = [node]
            while path[-1] != source:
                path.append(parent[path[-1]])
            return spent, tuple(reversed(path))
        for neighbor, weight in adjacency[node]:
            candidate = spent + weight
            if candidate < distances.get(neighbor, inf):
                distances[neighbor] = candidate
                parent[neighbor] = node
                heappush(queue, (candidate, repr(neighbor), neighbor))
    return inf, ()


@dataclass(frozen=True)
class SpectralDimensionEstimate:
    dimension: float
    slope: float
    intercept: float
    r_squared: float
    return_probabilities: np.ndarray


def estimate_spectral_dimension(
    laplacian: Sequence[Sequence[float]], times: Sequence[float]
) -> SpectralDimensionEstimate:
    matrix = np.asarray(laplacian, dtype=np.float64)
    time_values = np.asarray(times, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[0] != matrix.shape[1]
        or np.any(~np.isfinite(matrix))
        or not np.allclose(matrix, matrix.T, atol=1e-10)
        or time_values.ndim != 1
        or time_values.size < 2
        or np.any(~np.isfinite(time_values))
        or np.any(time_values <= 0.0)
    ):
        raise ValueError("spectral-dimension inputs are invalid")
    eigenvalues = np.linalg.eigvalsh(matrix)
    if eigenvalues[0] < -1e-9:
        raise ValueError("spectral-dimension Laplacian must be positive semidefinite")
    returns = np.mean(
        np.exp(-time_values[:, None] * np.maximum(eigenvalues, 0.0)), axis=1
    )
    x = np.log(time_values)
    y = np.log(returns)
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    denominator = float(np.sum((y - y.mean()) ** 2))
    r_squared = (
        1.0
        if denominator <= 1e-30
        else 1.0 - float(np.sum((y - predicted) ** 2)) / denominator
    )
    return SpectralDimensionEstimate(
        float(-2.0 * slope), float(slope), float(intercept), r_squared, returns
    )
