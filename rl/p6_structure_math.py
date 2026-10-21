"""P6 sheaves, topology, entropic bridges, information geometry, and matroids."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, inf, isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.linalg import expm


Vertex = Hashable
Edge = tuple[Vertex, Vertex]
Item = Hashable


class CellularSheaf:
    """A finite cellular sheaf on a graph with linear vertex-to-edge maps."""

    def __init__(
        self,
        vertex_dimensions: Mapping[Vertex, int],
        edge_dimensions: Mapping[Edge, int],
        restrictions: Mapping[tuple[Vertex, Edge], Sequence[Sequence[float]]],
    ) -> None:
        self.vertices = tuple(sorted(vertex_dimensions, key=repr))
        self.edges = tuple(sorted(edge_dimensions, key=repr))
        self.vertex_dimensions = {vertex: int(vertex_dimensions[vertex]) for vertex in self.vertices}
        self.edge_dimensions = {edge: int(edge_dimensions[edge]) for edge in self.edges}
        if not self.vertices or any(value <= 0 for value in self.vertex_dimensions.values()):
            raise ValueError("sheaf vertex stalk dimensions must be positive")
        if any(
            len(edge) != 2
            or edge[0] == edge[1]
            or edge[0] not in self.vertex_dimensions
            or edge[1] not in self.vertex_dimensions
            or self.edge_dimensions[edge] <= 0
            for edge in self.edges
        ):
            raise ValueError("sheaf edges and edge stalk dimensions are invalid")
        self.restrictions: dict[tuple[Vertex, Edge], np.ndarray] = {}
        for edge in self.edges:
            for vertex in edge:
                key = (vertex, edge)
                if key not in restrictions:
                    raise ValueError(f"missing sheaf restriction map: {key!r}")
                matrix = np.asarray(restrictions[key], dtype=np.float64)
                expected = (self.edge_dimensions[edge], self.vertex_dimensions[vertex])
                if matrix.shape != expected or np.any(~np.isfinite(matrix)):
                    raise ValueError("sheaf restriction map has invalid shape or values")
                self.restrictions[key] = matrix
        self._vertex_offsets = self._offsets(self.vertices, self.vertex_dimensions)
        self._edge_offsets = self._offsets(self.edges, self.edge_dimensions)

    @staticmethod
    def _offsets(keys: Sequence[Hashable], dimensions: Mapping[Hashable, int]) -> dict[Hashable, int]:
        offsets = {}
        position = 0
        for key in keys:
            offsets[key] = position
            position += dimensions[key]
        return offsets

    @property
    def total_vertex_dimension(self) -> int:
        return sum(self.vertex_dimensions.values())

    @property
    def total_edge_dimension(self) -> int:
        return sum(self.edge_dimensions.values())

    def coboundary(self) -> np.ndarray:
        matrix = np.zeros(
            (self.total_edge_dimension, self.total_vertex_dimension),
            dtype=np.float64,
        )
        for edge in self.edges:
            tail, head = edge
            row = self._edge_offsets[edge]
            edge_dimension = self.edge_dimensions[edge]
            for vertex, sign in ((tail, -1.0), (head, 1.0)):
                column = self._vertex_offsets[vertex]
                dimension = self.vertex_dimensions[vertex]
                matrix[
                    row : row + edge_dimension,
                    column : column + dimension,
                ] = sign * self.restrictions[(vertex, edge)]
        return matrix

    def laplacian(self) -> np.ndarray:
        coboundary = self.coboundary()
        return coboundary.T @ coboundary

    def pack(self, values: Mapping[Vertex, Sequence[float]]) -> np.ndarray:
        vector = np.empty(self.total_vertex_dimension, dtype=np.float64)
        for vertex in self.vertices:
            value = np.asarray(values[vertex], dtype=np.float64)
            dimension = self.vertex_dimensions[vertex]
            if value.shape != (dimension,) or np.any(~np.isfinite(value)):
                raise ValueError("sheaf vertex value has invalid shape or values")
            offset = self._vertex_offsets[vertex]
            vector[offset : offset + dimension] = value
        return vector

    def unpack(self, vector: Sequence[float]) -> dict[Vertex, tuple[float, ...]]:
        value = np.asarray(vector, dtype=np.float64)
        if value.shape != (self.total_vertex_dimension,) or np.any(~np.isfinite(value)):
            raise ValueError("packed sheaf vector has invalid shape or values")
        return {
            vertex: tuple(
                map(
                    float,
                    value[
                        self._vertex_offsets[vertex] : self._vertex_offsets[vertex]
                        + self.vertex_dimensions[vertex]
                    ],
                )
            )
            for vertex in self.vertices
        }

    def consistency_energy(self, values: Mapping[Vertex, Sequence[float]]) -> float:
        vector = self.pack(values)
        residual = self.coboundary() @ vector
        return float(residual @ residual)

    def global_sections(self, *, tolerance: float = 1e-10) -> np.ndarray:
        if tolerance <= 0.0:
            raise ValueError("sheaf nullspace tolerance must be positive")
        coboundary = self.coboundary()
        _left, singular, right_t = np.linalg.svd(coboundary, full_matrices=True)
        rank = int(np.sum(singular > tolerance))
        return right_t[rank:].T.copy()

    def diffuse(
        self,
        values: Mapping[Vertex, Sequence[float]],
        *,
        time: float = 1.0,
    ) -> dict[Vertex, tuple[float, ...]]:
        if not isfinite(time) or time < 0.0:
            raise ValueError("sheaf diffusion time must be finite and non-negative")
        result = expm(-float(time) * self.laplacian()) @ self.pack(values)
        return self.unpack(result)


@dataclass(frozen=True)
class MorseCriticalPoint:
    vertex: Vertex
    kind: str
    index: int
    lower_components: int
    upper_components: int


def _induced_component_count(
    vertices: set[Vertex], adjacency: Mapping[Vertex, Sequence[Vertex]]
) -> int:
    remaining = set(vertices)
    count = 0
    while remaining:
        count += 1
        frontier = [min(remaining, key=repr)]
        remaining.remove(frontier[0])
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency.get(current, ()):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    frontier.append(neighbor)
    return count


def discrete_morse_critical_points(
    adjacency: Mapping[Vertex, Sequence[Vertex]],
    values: Mapping[Vertex, float],
) -> tuple[MorseCriticalPoint, ...]:
    """Classify graph/complex vertices from connected lower and upper links."""

    vertices = tuple(sorted(values, key=repr))
    if not vertices or any(not isfinite(float(values[vertex])) for vertex in vertices):
        raise ValueError("discrete Morse values must be finite and non-empty")
    for vertex in vertices:
        for neighbor in adjacency.get(vertex, ()):
            if neighbor not in values or vertex not in adjacency.get(neighbor, ()):
                raise ValueError("discrete Morse adjacency must be symmetric and closed")
            if float(values[vertex]) == float(values[neighbor]):
                raise ValueError("discrete Morse values must differ across adjacent vertices")
    result = []
    for vertex in vertices:
        neighbors = set(adjacency.get(vertex, ()))
        lower = {neighbor for neighbor in neighbors if values[neighbor] < values[vertex]}
        upper = neighbors - lower
        lower_components = _induced_component_count(lower, adjacency)
        upper_components = _induced_component_count(upper, adjacency)
        if not lower:
            kind, index = "minimum", 0
        elif not upper:
            kind, index = "maximum", 2
        elif lower_components > 1 or upper_components > 1:
            kind, index = "saddle", 1
        else:
            kind, index = "regular", -1
        if kind != "regular":
            result.append(
                MorseCriticalPoint(
                    vertex, kind, index, lower_components, upper_components
                )
            )
    return tuple(result)


@dataclass(frozen=True)
class ReebNode:
    identifier: int
    value: float
    members: frozenset[Vertex]


@dataclass(frozen=True)
class ReebGraph:
    nodes: tuple[ReebNode, ...]
    edges: tuple[tuple[int, int], ...]
    vertex_to_node: Mapping[Vertex, int]


def discrete_reeb_graph(
    adjacency: Mapping[Vertex, Sequence[Vertex]],
    values: Mapping[Vertex, float],
) -> ReebGraph:
    """Quotient a discrete graph by connected components of equal-valued levels."""

    if not values or any(not isfinite(float(value)) for value in values.values()):
        raise ValueError("Reeb graph needs finite scalar values")
    unassigned = set(values)
    components = []
    while unassigned:
        seed = min(unassigned, key=lambda vertex: (values[vertex], repr(vertex)))
        level = float(values[seed])
        component = {seed}
        unassigned.remove(seed)
        frontier = [seed]
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency.get(current, ()):
                if neighbor not in values:
                    raise ValueError("Reeb adjacency references an unknown vertex")
                if neighbor in unassigned and float(values[neighbor]) == level:
                    unassigned.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        components.append((level, frozenset(component)))
    components.sort(key=lambda item: (item[0], tuple(map(repr, sorted(item[1], key=repr)))))
    nodes = tuple(
        ReebNode(identifier, level, members)
        for identifier, (level, members) in enumerate(components)
    )
    vertex_to_node = {
        vertex: node.identifier for node in nodes for vertex in node.members
    }
    edges = set()
    for vertex in values:
        for neighbor in adjacency.get(vertex, ()):
            if neighbor not in values:
                raise ValueError("Reeb adjacency references an unknown vertex")
            left, right = vertex_to_node[vertex], vertex_to_node[neighbor]
            if left != right:
                edges.add(tuple(sorted((left, right))))
    return ReebGraph(nodes, tuple(sorted(edges)), vertex_to_node)


@dataclass(frozen=True)
class SchrodingerBridgeResult:
    coupling: np.ndarray
    transition: np.ndarray
    iterations: int
    marginal_error: float


def schrodinger_bridge(
    initial: Sequence[float],
    target: Sequence[float],
    reference_kernel: Sequence[Sequence[float]],
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100_000,
) -> SchrodingerBridgeResult:
    """Finite one-step Schrodinger bridge by Sinkhorn scaling."""

    left = np.asarray(initial, dtype=np.float64)
    right = np.asarray(target, dtype=np.float64)
    kernel = np.asarray(reference_kernel, dtype=np.float64)
    if left.ndim != 1 or right.ndim != 1 or kernel.shape != (left.size, right.size):
        raise ValueError("Schrodinger bridge dimensions are inconsistent")
    if any(np.any(~np.isfinite(array)) for array in (left, right, kernel)):
        raise ValueError("Schrodinger bridge inputs must be finite")
    if np.any(left <= 0.0) or np.any(right <= 0.0) or np.any(kernel <= 0.0):
        raise ValueError("Schrodinger bridge currently requires strictly positive inputs")
    left = left / left.sum()
    right = right / right.sum()
    if tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("Schrodinger bridge solver parameters are invalid")
    u = np.ones_like(left)
    v = np.ones_like(right)
    error = inf
    for iteration in range(1, max_iterations + 1):
        u = left / (kernel @ v)
        v = right / (kernel.T @ u)
        coupling = u[:, None] * kernel * v[None, :]
        error = float(
            max(
                np.max(np.abs(coupling.sum(axis=1) - left)),
                np.max(np.abs(coupling.sum(axis=0) - right)),
            )
        )
        if error <= tolerance:
            transition = coupling / left[:, None]
            return SchrodingerBridgeResult(coupling, transition, iteration, error)
    raise RuntimeError(f"Schrodinger bridge did not converge; error={error}")


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    probability = np.asarray(values, dtype=np.float64)
    if probability.ndim != 1 or probability.size == 0 or np.any(~np.isfinite(probability)):
        raise ValueError(f"{name} must be a finite probability vector")
    if np.any(probability <= 0.0) or probability.sum() <= 0.0:
        raise ValueError(f"{name} probabilities must be strictly positive")
    return probability / probability.sum()


def categorical_fisher_information(probabilities: Sequence[float]) -> np.ndarray:
    probability = _probability_vector(probabilities, "categorical distribution")
    return np.diag(probability) - np.outer(probability, probability)


def fisher_rao_distance(left: Sequence[float], right: Sequence[float]) -> float:
    first = _probability_vector(left, "left distribution")
    second = _probability_vector(right, "right distribution")
    if first.shape != second.shape:
        raise ValueError("Fisher-Rao distributions must have equal dimensions")
    affinity = float(np.sum(np.sqrt(first * second)))
    return 2.0 * acos(min(1.0, max(-1.0, affinity)))


def kl_divergence(left: Sequence[float], right: Sequence[float]) -> float:
    first = _probability_vector(left, "left distribution")
    second = _probability_vector(right, "right distribution")
    if first.shape != second.shape:
        raise ValueError("KL distributions must have equal dimensions")
    return float(np.sum(first * np.log(first / second)))


def categorical_natural_gradient_step(
    probabilities: Sequence[float],
    gradient: Sequence[float],
    *,
    step_size: float = 0.1,
    maximize: bool = True,
) -> tuple[float, ...]:
    probability = _probability_vector(probabilities, "categorical distribution")
    direction = np.asarray(gradient, dtype=np.float64)
    if direction.shape != probability.shape or np.any(~np.isfinite(direction)):
        raise ValueError("natural-gradient direction is invalid")
    if not isfinite(step_size) or step_size <= 0.0:
        raise ValueError("natural-gradient step size must be positive and finite")
    sign = 1.0 if maximize else -1.0
    logits = np.log(probability) + sign * step_size * direction
    logits -= logits.max()
    updated = np.exp(logits)
    updated /= updated.sum()
    return tuple(map(float, updated))


def max_plus_matmul(
    left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]
) -> np.ndarray:
    first = np.asarray(left, dtype=np.float64)
    second = np.asarray(right, dtype=np.float64)
    if first.ndim != 2 or second.ndim != 2 or first.shape[1] != second.shape[0]:
        raise ValueError("max-plus matrix dimensions are inconsistent")
    if np.any(np.isnan(first)) or np.any(np.isnan(second)):
        raise ValueError("max-plus matrices cannot contain NaN")
    return np.max(first[:, :, None] + second[None, :, :], axis=1)


def max_plus_power(matrix: Sequence[Sequence[float]], exponent: int) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or exponent < 0:
        raise ValueError("max-plus power needs a square matrix and non-negative exponent")
    size = value.shape[0]
    result = np.full((size, size), -np.inf, dtype=np.float64)
    np.fill_diagonal(result, 0.0)
    base = value.copy()
    power = int(exponent)
    while power:
        if power & 1:
            result = max_plus_matmul(result, base)
        base = max_plus_matmul(base, base)
        power //= 2
    return result


def max_plus_cycle_mean(matrix: Sequence[Sequence[float]]) -> float:
    """Maximum directed cycle mean for A[i,j] = weight j -> i."""

    value = np.asarray(matrix, dtype=np.float64)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or np.any(np.isnan(value)):
        raise ValueError("max-plus cycle mean needs a square matrix without NaN")
    size = value.shape[0]
    dynamic = np.full((size + 1, size), -np.inf, dtype=np.float64)
    dynamic[0] = 0.0
    for length in range(1, size + 1):
        dynamic[length] = np.max(value + dynamic[length - 1][None, :], axis=1)
    candidates = []
    for vertex in range(size):
        if not isfinite(dynamic[size, vertex]):
            continue
        ratios = [
            (dynamic[size, vertex] - dynamic[length, vertex]) / (size - length)
            for length in range(size)
            if isfinite(dynamic[length, vertex])
        ]
        if ratios:
            candidates.append(min(ratios))
    return max(candidates, default=-inf)


@dataclass(frozen=True)
class MatroidResult:
    selected: tuple[Item, ...]
    value: float
    marginal_gains: tuple[float, ...]


def matroid_greedy(
    items: Sequence[Item],
    weights: Mapping[Item, float],
    independent: Callable[[frozenset[Item]], bool],
) -> MatroidResult:
    """Exact maximum-weight greedy algorithm for a valid matroid oracle."""

    candidates = tuple(dict.fromkeys(items))
    values = {item: float(weights.get(item, 0.0)) for item in candidates}
    if any(not isfinite(value) for value in values.values()):
        raise ValueError("matroid weights must be finite")
    selected: set[Item] = set()
    gains = []
    for item in sorted(candidates, key=lambda candidate: (-values[candidate], repr(candidate))):
        if values[item] <= 0.0:
            continue
        proposal = frozenset(selected | {item})
        if independent(proposal):
            selected.add(item)
            gains.append(values[item])
    if not independent(frozenset(selected)):
        raise ValueError("matroid independence oracle returned inconsistent results")
    order = tuple(
        item
        for item in sorted(candidates, key=lambda candidate: (-values[candidate], repr(candidate)))
        if item in selected
    )
    return MatroidResult(order, sum(gains), tuple(gains))


def partition_matroid_oracle(
    groups: Mapping[Item, Hashable], capacities: Mapping[Hashable, int]
) -> Callable[[frozenset[Item]], bool]:
    if any(int(capacity) < 0 for capacity in capacities.values()):
        raise ValueError("partition matroid capacities must be non-negative")

    def independent(selected: frozenset[Item]) -> bool:
        counts: dict[Hashable, int] = {}
        for item in selected:
            if item not in groups:
                return False
            group = groups[item]
            counts[group] = counts.get(group, 0) + 1
            if counts[group] > int(capacities.get(group, 0)):
                return False
        return True

    return independent


def submodular_matroid_greedy(
    items: Sequence[Item],
    value: Callable[[frozenset[Item]], float],
    independent: Callable[[frozenset[Item]], bool],
    *,
    tolerance: float = 1e-12,
) -> MatroidResult:
    """Greedy monotone submodular maximization under a matroid constraint."""

    candidates = tuple(dict.fromkeys(items))
    selected: set[Item] = set()
    current = float(value(frozenset()))
    if not isfinite(current):
        raise ValueError("submodular matroid values must be finite")
    gains = []
    order = []
    while True:
        feasible = []
        for item in candidates:
            if item in selected or not independent(frozenset(selected | {item})):
                continue
            updated = float(value(frozenset(selected | {item})))
            if not isfinite(updated):
                raise ValueError("submodular matroid values must be finite")
            feasible.append((updated - current, item, updated))
        if not feasible:
            break
        gain, item, updated = max(feasible, key=lambda entry: entry[0])
        if gain < -tolerance:
            raise ValueError("submodular matroid greedy requires a monotone objective")
        if gain <= tolerance:
            break
        selected.add(item)
        order.append(item)
        gains.append(gain)
        current = updated
    return MatroidResult(tuple(order), current, tuple(gains))
