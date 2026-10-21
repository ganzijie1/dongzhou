"""Multi-objective, transport, spectral, and robust-game mathematics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


Key = Hashable


def pareto_front(
    objectives: Mapping[Key, Sequence[float]],
    *,
    maximize: Sequence[bool] | None = None,
    tolerance: float = 1e-12,
) -> tuple[Key, ...]:
    """Return non-dominated keys in deterministic order."""

    if not objectives:
        return ()
    dimensions = len(next(iter(objectives.values())))
    if dimensions == 0 or any(len(values) != dimensions for values in objectives.values()):
        raise ValueError("objective vectors must have one shared positive dimension")
    directions = tuple(maximize or (True,) * dimensions)
    if len(directions) != dimensions:
        raise ValueError("maximize flags must match objective dimensions")
    signed = {
        key: tuple(
            float(value) if direction else -float(value)
            for value, direction in zip(values, directions)
        )
        for key, values in objectives.items()
    }
    if any(not all(isfinite(value) for value in values) for values in signed.values()):
        raise ValueError("objectives must be finite")
    result = []
    for candidate, values in signed.items():
        dominated = False
        for rival, other in signed.items():
            if rival == candidate:
                continue
            no_worse = all(
                right + tolerance >= left for left, right in zip(values, other)
            )
            strictly_better = any(
                right > left + tolerance for left, right in zip(values, other)
            )
            if no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            result.append(candidate)
    return tuple(sorted(result, key=repr))


def lexicographic_choice(
    objectives: Mapping[Key, Sequence[float]],
    *,
    maximize: Sequence[bool] | None = None,
    tolerances: Sequence[float] | None = None,
) -> Key:
    """Apply epsilon-lexicographic filtering without scalarizing objectives."""

    if not objectives:
        raise ValueError("lexicographic choice needs candidates")
    dimensions = len(next(iter(objectives.values())))
    if dimensions == 0 or any(len(values) != dimensions for values in objectives.values()):
        raise ValueError("objective vectors must have one shared positive dimension")
    directions = tuple(maximize or (True,) * dimensions)
    epsilon = tuple(tolerances or (0.0,) * dimensions)
    if len(directions) != dimensions or len(epsilon) != dimensions:
        raise ValueError("lexicographic options must match objective dimensions")
    candidates = list(objectives)
    for index in range(dimensions):
        signed = {
            key: (1.0 if directions[index] else -1.0) * float(objectives[key][index])
            for key in candidates
        }
        best = max(signed.values())
        candidates = [
            key for key in candidates
            if signed[key] + float(epsilon[index]) >= best
        ]
        if len(candidates) == 1:
            return candidates[0]
    return min(candidates, key=repr)


@dataclass(frozen=True)
class TransportResult:
    plan: Mapping[tuple[Key, Key], float]
    cost: float
    source_marginals: Mapping[Key, float]
    target_marginals: Mapping[Key, float]


def optimal_transport(
    source_mass: Mapping[Key, float],
    target_mass: Mapping[Key, float],
    costs: Mapping[tuple[Key, Key], float] | Callable[[Key, Key], float],
) -> TransportResult:
    """Solve a balanced finite Kantorovich optimal transport problem."""

    sources = tuple(sorted(source_mass, key=repr))
    targets = tuple(sorted(target_mass, key=repr))
    if not sources or not targets:
        raise ValueError("optimal transport needs sources and targets")
    supply = np.asarray([float(source_mass[key]) for key in sources])
    demand = np.asarray([float(target_mass[key]) for key in targets])
    if np.any(~np.isfinite(supply)) or np.any(~np.isfinite(demand)):
        raise ValueError("transport masses must be finite")
    if np.any(supply < 0.0) or np.any(demand < 0.0):
        raise ValueError("transport masses must be non-negative")
    if not np.isclose(supply.sum(), demand.sum(), rtol=1e-9, atol=1e-9):
        raise ValueError("optimal transport requires balanced total mass")
    pairs = tuple((source, target) for source in sources for target in targets)
    get_cost = costs if callable(costs) else lambda left, right: costs[(left, right)]
    objective = np.asarray([float(get_cost(left, right)) for left, right in pairs])
    if np.any(~np.isfinite(objective)):
        raise ValueError("transport costs must be finite")
    equality = np.zeros((len(sources) + len(targets), len(pairs)))
    for variable, (source, target) in enumerate(pairs):
        equality[sources.index(source), variable] = 1.0
        equality[len(sources) + targets.index(target), variable] = 1.0
    result = linprog(
        objective,
        A_eq=equality,
        b_eq=np.concatenate((supply, demand)),
        bounds=[(0.0, None)] * len(pairs),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"optimal transport failed: {result.message}")
    plan = {
        pair: float(value)
        for pair, value in zip(pairs, result.x)
        if value > 1e-10
    }
    return TransportResult(
        plan,
        float(result.fun),
        {key: float(value) for key, value in zip(sources, supply)},
        {key: float(value) for key, value in zip(targets, demand)},
    )


def integral_transport_assignment(result: TransportResult) -> dict[Key, Key]:
    """Extract deterministic assignments from a unit-mass transport plan."""

    assignment: dict[Key, Key] = {}
    claimed: set[Key] = set()
    for (source, target), mass in sorted(
        result.plan.items(), key=lambda item: (-item[1], repr(item[0]))
    ):
        if mass <= 1e-9 or source in assignment or target in claimed:
            continue
        assignment[source] = target
        claimed.add(target)
    return assignment


@dataclass(frozen=True)
class SpectralResult:
    nodes: tuple[Key, ...]
    eigenvalues: tuple[float, ...]
    fiedler_vector: Mapping[Key, float]
    left_partition: frozenset[Key]
    right_partition: frozenset[Key]
    algebraic_connectivity: float


class SpectralGraph:
    """Undirected weighted graph analysis through its combinatorial Laplacian."""

    def __init__(self, edges: Mapping[tuple[Key, Key], float]) -> None:
        weights: dict[frozenset[Key], float] = {}
        singleton_nodes: set[Key] = set()
        for (left, right), raw in edges.items():
            value = float(raw)
            if not isfinite(value) or value < 0.0:
                raise ValueError("spectral edge weights must be finite and non-negative")
            singleton_nodes.update((left, right))
            if left == right or value == 0.0:
                continue
            key = frozenset((left, right))
            weights[key] = max(weights.get(key, 0.0), value)
        self.nodes = tuple(sorted(singleton_nodes, key=repr))
        self.index = {node: index for index, node in enumerate(self.nodes)}
        self.adjacency = np.zeros((len(self.nodes), len(self.nodes)), dtype=np.float64)
        for edge, value in weights.items():
            left, right = tuple(edge)
            i, j = self.index[left], self.index[right]
            self.adjacency[i, j] = self.adjacency[j, i] = value
        degree = np.diag(self.adjacency.sum(axis=1))
        self.laplacian = degree - self.adjacency

    @classmethod
    def from_grid(cls, cells: Sequence[tuple[int, int]]) -> "SpectralGraph":
        region = set(cells)
        edges: dict[tuple[Key, Key], float] = {}
        for x, y in region:
            for neighbor in ((x + 1, y), (x, y + 1)):
                if neighbor in region:
                    edges[((x, y), neighbor)] = 1.0
        graph = cls(edges)
        if len(graph.nodes) != len(region):
            # Preserve isolated cells as zero-weight self references.
            graph = cls({**edges, **{(cell, cell): 0.0 for cell in region}})
        return graph

    def analyze(self) -> SpectralResult:
        if not self.nodes:
            return SpectralResult((), (), {}, frozenset(), frozenset(), 0.0)
        values, vectors = np.linalg.eigh(self.laplacian)
        values[np.abs(values) < 1e-12] = 0.0
        positive = [index for index, value in enumerate(values) if value > 1e-10]
        vector_index = positive[0] if positive else min(1, len(values) - 1)
        vector = vectors[:, vector_index]
        median = float(np.median(vector))
        left = {node for node, value in zip(self.nodes, vector) if value <= median}
        right = set(self.nodes) - left
        if not left or not right:
            midpoint = max(1, len(self.nodes) // 2)
            left = set(self.nodes[:midpoint])
            right = set(self.nodes[midpoint:])
        connectivity = float(values[1]) if len(values) > 1 else 0.0
        return SpectralResult(
            self.nodes,
            tuple(float(value) for value in values),
            {node: float(value) for node, value in zip(self.nodes, vector)},
            frozenset(left),
            frozenset(right),
            connectivity,
        )

    def effective_resistance(self) -> dict[tuple[Key, Key], float]:
        if not self.nodes:
            return {}
        inverse = np.linalg.pinv(self.laplacian, hermitian=True)
        result: dict[tuple[Key, Key], float] = {}
        for left_index, left in enumerate(self.nodes):
            for right_index in range(left_index + 1, len(self.nodes)):
                right = self.nodes[right_index]
                value = (
                    inverse[left_index, left_index]
                    + inverse[right_index, right_index]
                    - 2.0 * inverse[left_index, right_index]
                )
                result[(left, right)] = max(0.0, float(value))
        return result

    def resistance_centrality(self) -> dict[Key, float]:
        resistance = self.effective_resistance()
        result: dict[Key, float] = {}
        for node in self.nodes:
            total = sum(
                value for pair, value in resistance.items() if node in pair
            )
            result[node] = 0.0 if total <= 1e-12 else (len(self.nodes) - 1) / total
        return result


@dataclass(frozen=True)
class ZeroSumSolution:
    row_strategy: tuple[float, ...]
    column_strategy: tuple[float, ...]
    value: float
    duality_gap: float
    pure_worst_cases: tuple[float, ...]


def solve_zero_sum_game(payoffs: Sequence[Sequence[float]]) -> ZeroSumSolution:
    """Solve a finite zero-sum game for max-row versus min-column players."""

    matrix = np.asarray(payoffs, dtype=np.float64)
    if matrix.ndim != 2 or not matrix.shape[0] or not matrix.shape[1]:
        raise ValueError("zero-sum payoff matrix must be non-empty and two-dimensional")
    if np.any(~np.isfinite(matrix)):
        raise ValueError("zero-sum payoffs must be finite")
    rows, columns = matrix.shape
    row_objective = np.zeros(rows + 1)
    row_objective[-1] = -1.0
    row_ub = np.hstack((-matrix.T, np.ones((columns, 1))))
    row_result = linprog(
        row_objective,
        A_ub=row_ub,
        b_ub=np.zeros(columns),
        A_eq=np.asarray([[1.0] * rows + [0.0]]),
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, 1.0)] * rows + [(None, None)],
        method="highs",
    )
    column_objective = np.zeros(columns + 1)
    column_objective[-1] = 1.0
    column_ub = np.hstack((matrix, -np.ones((rows, 1))))
    column_result = linprog(
        column_objective,
        A_ub=column_ub,
        b_ub=np.zeros(rows),
        A_eq=np.asarray([[1.0] * columns + [0.0]]),
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, 1.0)] * columns + [(None, None)],
        method="highs",
    )
    if not row_result.success or not column_result.success:
        message = row_result.message if not row_result.success else column_result.message
        raise RuntimeError(f"zero-sum game solve failed: {message}")
    lower = float(row_result.x[-1])
    upper = float(column_result.x[-1])
    row_strategy = np.maximum(row_result.x[:-1], 0.0)
    column_strategy = np.maximum(column_result.x[:-1], 0.0)
    row_strategy /= row_strategy.sum()
    column_strategy /= column_strategy.sum()
    return ZeroSumSolution(
        tuple(float(value) for value in row_strategy),
        tuple(float(value) for value in column_strategy),
        0.5 * (lower + upper),
        max(0.0, upper - lower),
        tuple(float(value) for value in matrix.min(axis=1)),
    )

