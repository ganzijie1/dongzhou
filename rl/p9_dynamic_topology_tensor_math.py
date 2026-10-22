"""P9 exact graph H0 zigzags, graph curvature, and tensor decomposition."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.linalg import null_space
from scipy.optimize import linprog


Vertex = Hashable
Edge = tuple[Vertex, Vertex]


def _canonical_edge(edge: Sequence[Vertex]) -> Edge:
    if len(edge) != 2 or edge[0] == edge[1]:
        raise ValueError("graph edges must contain two distinct vertices")
    left, right = edge
    return (left, right) if repr(left) <= repr(right) else (right, left)


def _components(vertices: tuple[Vertex, ...], edges: frozenset[Edge]) -> tuple[frozenset[Vertex], ...]:
    adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(vertices)
    result = []
    while remaining:
        seed = min(remaining, key=repr)
        remaining.remove(seed)
        component = {seed}
        frontier = [seed]
        while frontier:
            current = frontier.pop()
            for neighbor in sorted(adjacency[current], key=repr):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        result.append(frozenset(component))
    return tuple(sorted(result, key=lambda component: min(map(repr, component))))


def _inclusion_map(
    source: tuple[frozenset[Vertex], ...],
    target: tuple[frozenset[Vertex], ...],
) -> np.ndarray:
    target_index = {vertex: index for index, component in enumerate(target) for vertex in component}
    result = np.zeros((len(target), len(source)))
    for source_index, component in enumerate(source):
        images = {target_index[vertex] for vertex in component}
        if len(images) != 1:
            raise ValueError("component inclusion is inconsistent")
        result[images.pop(), source_index] = 1.0
    return result


def _matrix_rank(matrix: np.ndarray, tolerance: float) -> int:
    return int(np.linalg.matrix_rank(matrix, tol=tolerance)) if matrix.size else 0


def _generalized_rank(
    dimensions: Sequence[int],
    maps: Sequence[np.ndarray],
    directions: Sequence[str],
    start: int,
    end: int,
    tolerance: float,
) -> int:
    local_dimensions = tuple(dimensions[start : end + 1])
    offsets = np.cumsum((0, *local_dimensions))
    total = int(offsets[-1])
    if start == end:
        return local_dimensions[0]
    constraint_blocks = []
    relation_blocks = []
    for local_edge, global_edge in enumerate(range(start, end)):
        left_dimension = local_dimensions[local_edge]
        right_dimension = local_dimensions[local_edge + 1]
        left = slice(offsets[local_edge], offsets[local_edge + 1])
        right = slice(offsets[local_edge + 1], offsets[local_edge + 2])
        linear_map = maps[global_edge]
        if directions[global_edge] == "forward":
            constraint = np.zeros((right_dimension, total))
            constraint[:, left] = -linear_map
            constraint[:, right] = np.eye(right_dimension)
            relation = np.zeros((total, left_dimension))
            relation[left, :] = np.eye(left_dimension)
            relation[right, :] = -linear_map
        else:
            constraint = np.zeros((left_dimension, total))
            constraint[:, left] = np.eye(left_dimension)
            constraint[:, right] = -linear_map
            relation = np.zeros((total, right_dimension))
            relation[right, :] = np.eye(right_dimension)
            relation[left, :] = -linear_map
        constraint_blocks.append(constraint)
        relation_blocks.append(relation)
    constraints = np.vstack(constraint_blocks)
    relations = np.hstack(relation_blocks)
    limit_basis = null_space(constraints, rcond=tolerance)
    if limit_basis.shape[1] == 0:
        return 0
    canonical = np.zeros((total, limit_basis.shape[1]))
    canonical[: local_dimensions[0]] = limit_basis[: local_dimensions[0]]
    return _matrix_rank(np.hstack((relations, canonical)), tolerance) - _matrix_rank(
        relations, tolerance
    )


@dataclass(frozen=True)
class ZigzagInterval:
    birth: int
    death: int


@dataclass(frozen=True)
class ZigzagH0Result:
    intervals: tuple[ZigzagInterval, ...]
    component_dimensions: tuple[int, ...]
    generalized_ranks: Mapping[tuple[int, int], int]


def graph_h0_zigzag_persistence(
    vertices: Sequence[Vertex],
    edge_snapshots: Sequence[Sequence[Sequence[Vertex]]],
    directions: Sequence[str],
    *,
    tolerance: float = 1e-9,
) -> ZigzagH0Result:
    """Exact H0 interval decomposition for a finite graph zigzag.

    ``forward`` means K_i is included in K_(i+1); ``backward`` means the
    inclusion points from K_(i+1) to K_i. Vertices remain fixed while edges
    may be inserted or removed.
    """

    ordered_vertices = tuple(dict.fromkeys(vertices))
    vertex_set = set(ordered_vertices)
    if not ordered_vertices or not edge_snapshots or tolerance <= 0.0:
        raise ValueError("zigzag graph inputs are invalid")
    if len(directions) != len(edge_snapshots) - 1 or any(
        direction not in {"forward", "backward"} for direction in directions
    ):
        raise ValueError("zigzag directions are invalid")
    snapshots = []
    for snapshot in edge_snapshots:
        edges = frozenset(_canonical_edge(edge) for edge in snapshot)
        if any(left not in vertex_set or right not in vertex_set for left, right in edges):
            raise ValueError("zigzag edge references an unknown vertex")
        snapshots.append(edges)
    components = tuple(_components(ordered_vertices, edges) for edges in snapshots)
    maps = []
    for index, direction in enumerate(directions):
        if direction == "forward":
            if not snapshots[index].issubset(snapshots[index + 1]):
                raise ValueError("forward zigzag step is not a graph inclusion")
            maps.append(_inclusion_map(components[index], components[index + 1]))
        else:
            if not snapshots[index + 1].issubset(snapshots[index]):
                raise ValueError("backward zigzag step is not a graph inclusion")
            maps.append(_inclusion_map(components[index + 1], components[index]))
    dimensions = tuple(len(value) for value in components)
    ranks = {
        (start, end): _generalized_rank(
            dimensions, maps, directions, start, end, tolerance
        )
        for start in range(len(snapshots))
        for end in range(start, len(snapshots))
    }
    intervals = []
    for birth in range(len(snapshots)):
        for death in range(birth, len(snapshots)):
            multiplicity = ranks[(birth, death)]
            if birth > 0:
                multiplicity -= ranks[(birth - 1, death)]
            if death + 1 < len(snapshots):
                multiplicity -= ranks[(birth, death + 1)]
            if birth > 0 and death + 1 < len(snapshots):
                multiplicity += ranks[(birth - 1, death + 1)]
            if multiplicity < 0:
                raise RuntimeError("zigzag interval multiplicity became negative")
            intervals.extend(ZigzagInterval(birth, death) for _ in range(multiplicity))
    return ZigzagH0Result(tuple(intervals), dimensions, ranks)


def _graph_distances(vertices: tuple[Vertex, ...], edges: tuple[Edge, ...]) -> np.ndarray:
    index = {vertex: position for position, vertex in enumerate(vertices)}
    adjacency = {vertex: [] for vertex in vertices}
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    distances = np.full((len(vertices), len(vertices)), np.inf)
    for source in vertices:
        source_index = index[source]
        distances[source_index, source_index] = 0.0
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if not isfinite(distances[source_index, index[neighbor]]):
                    distances[source_index, index[neighbor]] = (
                        distances[source_index, index[current]] + 1.0
                    )
                    queue.append(neighbor)
    return distances


def forman_ricci_curvature(
    vertices: Sequence[Vertex], edges: Sequence[Sequence[Vertex]]
) -> dict[Edge, float]:
    """Unweighted Forman-Ricci edge curvature."""

    ordered_vertices = tuple(dict.fromkeys(vertices))
    edge_values = tuple(sorted({_canonical_edge(edge) for edge in edges}, key=repr))
    vertex_set = set(ordered_vertices)
    if not ordered_vertices or any(a not in vertex_set or b not in vertex_set for a, b in edge_values):
        raise ValueError("Forman graph is invalid")
    degree = {vertex: 0 for vertex in ordered_vertices}
    for left, right in edge_values:
        degree[left] += 1
        degree[right] += 1
    return {
        edge: float(4 - degree[edge[0]] - degree[edge[1]]) for edge in edge_values
    }


def ollivier_ricci_curvature(
    vertices: Sequence[Vertex],
    edges: Sequence[Sequence[Vertex]],
    *,
    idleness: float = 0.5,
) -> dict[Edge, float]:
    """Exact finite unweighted Ollivier-Ricci edge curvature via transport LPs."""

    ordered_vertices = tuple(dict.fromkeys(vertices))
    edge_values = tuple(sorted({_canonical_edge(edge) for edge in edges}, key=repr))
    vertex_set = set(ordered_vertices)
    if (
        not ordered_vertices
        or not 0.0 <= idleness <= 1.0
        or any(a not in vertex_set or b not in vertex_set for a, b in edge_values)
    ):
        raise ValueError("Ollivier graph or idleness is invalid")
    index = {vertex: position for position, vertex in enumerate(ordered_vertices)}
    neighbors = {vertex: set() for vertex in ordered_vertices}
    for left, right in edge_values:
        neighbors[left].add(right)
        neighbors[right].add(left)
    distances = _graph_distances(ordered_vertices, edge_values)
    size = len(ordered_vertices)

    def distribution(vertex: Vertex) -> np.ndarray:
        result = np.zeros(size)
        result[index[vertex]] = idleness
        if neighbors[vertex]:
            share = (1.0 - idleness) / len(neighbors[vertex])
            for neighbor in neighbors[vertex]:
                result[index[neighbor]] += share
        else:
            result[index[vertex]] = 1.0
        return result

    result = {}
    for edge in edge_values:
        left_mass, right_mass = distribution(edge[0]), distribution(edge[1])
        support = np.flatnonzero((left_mass > 0.0) | (right_mass > 0.0))
        support_size = support.size
        cost = distances[np.ix_(support, support)]
        if np.any(~np.isfinite(cost)):
            raise ValueError("Ollivier edge neighborhoods are not mutually reachable")
        equality = np.zeros((2 * support_size, support_size * support_size))
        for row in range(support_size):
            equality[row, row * support_size : (row + 1) * support_size] = 1.0
        for column in range(support_size):
            equality[support_size + column, column::support_size] = 1.0
        solved = linprog(
            cost.reshape(-1),
            A_eq=equality,
            b_eq=np.r_[left_mass[support], right_mass[support]],
            bounds=[(0.0, None)] * (support_size * support_size),
            method="highs",
        )
        if not solved.success:
            raise RuntimeError(f"Ollivier transport failed: {solved.message}")
        result[edge] = 1.0 - float(solved.fun)
    return result


def _mode_product(tensor: np.ndarray, matrix: np.ndarray, mode: int) -> np.ndarray:
    product_value = np.tensordot(matrix, tensor, axes=(1, mode))
    return np.moveaxis(product_value, 0, mode)


@dataclass(frozen=True)
class HOSVDResult:
    core: np.ndarray
    factors: tuple[np.ndarray, ...]
    relative_error: float

    def reconstruct(self) -> np.ndarray:
        result = self.core.copy()
        for mode, factor in enumerate(self.factors):
            result = _mode_product(result, factor, mode)
        return result


def multirelational_hosvd(
    tensor: Sequence,
    ranks: Sequence[int],
) -> HOSVDResult:
    """Truncated HOSVD for actor-by-actor-by-relation(-by-time) tensors."""

    value = np.asarray(tensor, dtype=np.float64)
    rank_values = tuple(int(rank) for rank in ranks)
    if value.ndim < 3 or len(rank_values) != value.ndim or value.size == 0:
        raise ValueError("HOSVD tensor and rank dimensions are invalid")
    if np.any(~np.isfinite(value)) or any(
        rank <= 0 or rank > dimension for rank, dimension in zip(rank_values, value.shape)
    ):
        raise ValueError("HOSVD tensor values or ranks are invalid")
    factors = []
    for mode, rank in enumerate(rank_values):
        unfolding = np.moveaxis(value, mode, 0).reshape(value.shape[mode], -1)
        left, _singular, _right = np.linalg.svd(unfolding, full_matrices=False)
        factors.append(left[:, :rank])
    core = value.copy()
    for mode, factor in enumerate(factors):
        core = _mode_product(core, factor.T, mode)
    result = HOSVDResult(core, tuple(factors), 0.0)
    reconstruction = result.reconstruct()
    denominator = float(np.linalg.norm(value))
    error = float(np.linalg.norm(value - reconstruction))
    relative = error / denominator if denominator > 0.0 else error
    return HOSVDResult(core, tuple(factors), relative)
