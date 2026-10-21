"""Queueing, Hodge flow decomposition, persistence, and discrete conformal maps."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite
from typing import Hashable, Mapping, Sequence

import numpy as np


Node = Hashable
Edge = tuple[Node, Node]
Triangle = tuple[Node, Node, Node]


@dataclass(frozen=True)
class QueueMetrics:
    utilization: float
    mean_system_size: float
    mean_queue_size: float
    mean_system_time: float
    mean_wait_time: float


def mm1_queue(arrival_rate: float, service_rate: float) -> QueueMetrics:
    """Return stable M/M/1 congestion metrics for one tactical bottleneck."""

    arrival = float(arrival_rate)
    service = float(service_rate)
    if not isfinite(arrival) or not isfinite(service) or arrival < 0.0 or service <= 0.0:
        raise ValueError("queue rates must be finite with positive service")
    if arrival >= service:
        raise ValueError("M/M/1 queue is unstable when arrival >= service")
    utilization = arrival / service
    system_size = utilization / (1.0 - utilization)
    queue_size = utilization * utilization / (1.0 - utilization)
    system_time = 1.0 / (service - arrival)
    wait_time = arrival / (service * (service - arrival))
    return QueueMetrics(utilization, system_size, queue_size, system_time, wait_time)


@dataclass(frozen=True)
class JacksonNetworkResult:
    throughputs: tuple[float, ...]
    queues: tuple[QueueMetrics, ...]


def jackson_network(
    external_arrivals: Sequence[float],
    routing: Sequence[Sequence[float]],
    service_rates: Sequence[float],
) -> JacksonNetworkResult:
    """Solve open Jackson traffic equations lambda = external + lambda P."""

    external = np.asarray(external_arrivals, dtype=np.float64)
    matrix = np.asarray(routing, dtype=np.float64)
    service = np.asarray(service_rates, dtype=np.float64)
    size = external.size
    if external.ndim != 1 or service.shape != external.shape or matrix.shape != (size, size):
        raise ValueError("Jackson network dimensions are inconsistent")
    if any(np.any(~np.isfinite(array)) for array in (external, matrix, service)):
        raise ValueError("Jackson network values must be finite")
    if np.any(external < 0.0) or np.any(matrix < 0.0) or np.any(matrix.sum(axis=1) > 1.0 + 1e-12):
        raise ValueError("Jackson arrivals/routing are invalid")
    throughputs = np.linalg.solve(np.eye(size) - matrix.T, external)
    queues = tuple(mm1_queue(rate, capacity) for rate, capacity in zip(throughputs, service))
    return JacksonNetworkResult(tuple(float(value) for value in throughputs), queues)


@dataclass(frozen=True)
class HodgeResult:
    edges: tuple[Edge, ...]
    gradient: tuple[float, ...]
    curl: tuple[float, ...]
    harmonic: tuple[float, ...]
    energy_fractions: Mapping[str, float]


def hodge_decomposition(
    edges: Sequence[Edge],
    flows: Sequence[float],
    *,
    faces: Sequence[Sequence[Node]] = (),
) -> HodgeResult:
    """Orthogonally decompose an oriented edge flow into grad/curl/harmonic parts."""

    oriented = tuple(edges)
    flow = np.asarray(flows, dtype=np.float64)
    if len(set(oriented)) != len(oriented) or flow.shape != (len(oriented),):
        raise ValueError("Hodge edges must be unique and aligned with flows")
    if np.any(~np.isfinite(flow)):
        raise ValueError("Hodge flows must be finite")
    nodes = tuple(sorted({node for edge in oriented for node in edge}, key=repr))
    node_index = {node: index for index, node in enumerate(nodes)}
    edge_index = {edge: index for index, edge in enumerate(oriented)}
    incidence = np.zeros((len(nodes), len(oriented)), dtype=np.float64)
    for column, (tail, head) in enumerate(oriented):
        if tail == head:
            raise ValueError("Hodge edges cannot be self loops")
        incidence[node_index[tail], column] = -1.0
        incidence[node_index[head], column] = 1.0
    face_boundary = np.zeros((len(oriented), len(faces)), dtype=np.float64)
    for column, face in enumerate(faces):
        cycle = tuple(face)
        if len(cycle) < 3 or len(set(cycle)) != len(cycle):
            raise ValueError("Hodge faces must be simple cycles")
        for index, tail in enumerate(cycle):
            head = cycle[(index + 1) % len(cycle)]
            if (tail, head) in edge_index:
                face_boundary[edge_index[(tail, head)], column] = 1.0
            elif (head, tail) in edge_index:
                face_boundary[edge_index[(head, tail)], column] = -1.0
            else:
                raise ValueError("face boundary edge is missing from oriented edges")
    if faces and not np.allclose(incidence @ face_boundary, 0.0, atol=1e-10):
        raise ValueError("face boundaries do not form closed cycles")
    potential = np.linalg.lstsq(incidence.T, flow, rcond=None)[0]
    gradient = incidence.T @ potential
    if faces:
        circulation = np.linalg.lstsq(face_boundary, flow, rcond=None)[0]
        curl = face_boundary @ circulation
    else:
        curl = np.zeros_like(flow)
    harmonic = flow - gradient - curl
    energies = {
        "gradient": float(gradient @ gradient),
        "curl": float(curl @ curl),
        "harmonic": float(harmonic @ harmonic),
    }
    total = sum(energies.values())
    fractions = {
        name: (energy / total if total > 1e-15 else 0.0)
        for name, energy in energies.items()
    }
    return HodgeResult(
        oriented,
        tuple(map(float, gradient)),
        tuple(map(float, curl)),
        tuple(map(float, harmonic)),
        fractions,
    )


@dataclass(frozen=True)
class PersistenceInterval:
    dimension: int
    birth: float
    death: float
    creator: tuple[Node, ...]

    @property
    def persistence(self) -> float:
        return self.death - self.birth


def persistent_homology(
    vertices: Mapping[Node, float],
    edges: Mapping[Edge, float],
    triangles: Mapping[Triangle, float] | None = None,
) -> tuple[PersistenceInterval, ...]:
    """Compute H0/H1 persistence of a finite filtered 2D simplicial complex over GF(2)."""

    if not vertices:
        return ()
    simplices: dict[tuple[Node, ...], tuple[int, float]] = {}
    for vertex, filtration in vertices.items():
        value = float(filtration)
        if not isfinite(value):
            raise ValueError("simplex filtrations must be finite")
        simplices[(vertex,)] = (0, value)
    for raw_edge, filtration in edges.items():
        edge = tuple(sorted(raw_edge, key=repr))
        if len(edge) != 2 or edge[0] not in vertices or edge[1] not in vertices:
            raise ValueError("persistent edge has invalid vertices")
        value = max(float(filtration), *(float(vertices[node]) for node in edge))
        if not isfinite(value):
            raise ValueError("simplex filtrations must be finite")
        simplices[edge] = (1, value)
    for raw_triangle, filtration in (triangles or {}).items():
        triangle = tuple(sorted(raw_triangle, key=repr))
        if len(triangle) != 3 or len(set(triangle)) != 3:
            raise ValueError("persistent triangle must contain three vertices")
        boundary_edges = [
            tuple(sorted((triangle[0], triangle[1]), key=repr)),
            tuple(sorted((triangle[0], triangle[2]), key=repr)),
            tuple(sorted((triangle[1], triangle[2]), key=repr)),
        ]
        if any(edge not in simplices for edge in boundary_edges):
            raise ValueError("persistent triangle is missing a boundary edge")
        value = max(float(filtration), *(simplices[edge][1] for edge in boundary_edges))
        if not isfinite(value):
            raise ValueError("simplex filtrations must be finite")
        simplices[triangle] = (2, value)
    ordered = tuple(
        sorted(
            simplices,
            key=lambda simplex: (simplices[simplex][1], simplices[simplex][0], repr(simplex)),
        )
    )
    index = {simplex: position for position, simplex in enumerate(ordered)}
    reduced: dict[int, set[int]] = {}
    pivot_owner: dict[int, int] = {}
    births = set()
    intervals = []
    for column, simplex in enumerate(ordered):
        dimension, death = simplices[simplex]
        boundary = set()
        if dimension > 0:
            for removed in range(len(simplex)):
                face = simplex[:removed] + simplex[removed + 1 :]
                boundary.add(index[face])
        while boundary and max(boundary) in pivot_owner:
            boundary ^= reduced[pivot_owner[max(boundary)]]
        reduced[column] = boundary
        if not boundary:
            births.add(column)
            continue
        pivot = max(boundary)
        pivot_owner[pivot] = column
        birth_simplex = ordered[pivot]
        intervals.append(
            PersistenceInterval(
                simplices[birth_simplex][0],
                simplices[birth_simplex][1],
                death,
                birth_simplex,
            )
        )
    paired = set(pivot_owner)
    for birth in sorted(births - paired):
        simplex = ordered[birth]
        dimension, value = simplices[simplex]
        if dimension <= 1:
            intervals.append(PersistenceInterval(dimension, value, inf, simplex))
    return tuple(sorted(intervals, key=lambda item: (item.dimension, item.birth, item.death, repr(item.creator))))


def _cotangent(origin: np.ndarray, left: np.ndarray, right: np.ndarray) -> float:
    first = left - origin
    second = right - origin
    cross = abs(float(first[0] * second[1] - first[1] * second[0]))
    if cross <= 1e-12:
        raise ValueError("conformal mesh contains a degenerate triangle")
    return float(first @ second) / cross


@dataclass(frozen=True)
class DiscreteConformalResult:
    coordinates: Mapping[Node, tuple[float, float]]
    triangle_distortion: Mapping[Triangle, float]
    maximum_distortion: float


def discrete_conformal_map(
    vertices: Mapping[Node, tuple[float, float]],
    triangles: Sequence[Triangle],
    boundary_positions: Mapping[Node, tuple[float, float]],
) -> DiscreteConformalResult:
    """Cotangent-harmonic parameterization with per-triangle angle distortion."""

    nodes = tuple(vertices)
    if not nodes or not boundary_positions or any(node not in vertices for node in boundary_positions):
        raise ValueError("conformal map needs vertices and fixed boundary positions")
    points = {node: np.asarray(vertices[node], dtype=np.float64) for node in nodes}
    if any(point.shape != (2,) or np.any(~np.isfinite(point)) for point in points.values()):
        raise ValueError("conformal source coordinates must be finite 2D points")
    weights: dict[frozenset[Node], float] = {}
    normalized_triangles = []
    for raw in triangles:
        a, b, c = raw
        if len({a, b, c}) != 3 or any(node not in points for node in raw):
            raise ValueError("conformal triangle is invalid")
        normalized_triangles.append((a, b, c))
        contributions = (
            ((b, c), _cotangent(points[a], points[b], points[c]) / 2.0),
            ((a, c), _cotangent(points[b], points[a], points[c]) / 2.0),
            ((a, b), _cotangent(points[c], points[a], points[b]) / 2.0),
        )
        for edge, value in contributions:
            key = frozenset(edge)
            weights[key] = weights.get(key, 0.0) + value
    node_index = {node: index for index, node in enumerate(nodes)}
    laplacian = np.zeros((len(nodes), len(nodes)), dtype=np.float64)
    for edge, weight in weights.items():
        left, right = tuple(edge)
        i, j = node_index[left], node_index[right]
        laplacian[i, i] += weight
        laplacian[j, j] += weight
        laplacian[i, j] -= weight
        laplacian[j, i] -= weight
    boundary = tuple(boundary_positions)
    interior = tuple(node for node in nodes if node not in boundary_positions)
    mapped = {
        node: np.asarray(boundary_positions[node], dtype=np.float64)
        for node in boundary
    }
    if any(point.shape != (2,) or np.any(~np.isfinite(point)) for point in mapped.values()):
        raise ValueError("conformal boundary coordinates must be finite 2D points")
    if interior:
        interior_index = [node_index[node] for node in interior]
        boundary_index = [node_index[node] for node in boundary]
        system = laplacian[np.ix_(interior_index, interior_index)]
        rhs_matrix = -laplacian[np.ix_(interior_index, boundary_index)]
        boundary_matrix = np.asarray([mapped[node] for node in boundary])
        try:
            solution = np.linalg.solve(system, rhs_matrix @ boundary_matrix)
        except np.linalg.LinAlgError as error:
            raise ValueError("conformal interior system is singular") from error
        mapped.update({node: solution[index] for index, node in enumerate(interior)})
    distortion: dict[Triangle, float] = {}
    for triangle in normalized_triangles:
        a, b, c = triangle
        source = np.column_stack((points[b] - points[a], points[c] - points[a]))
        target = np.column_stack((mapped[b] - mapped[a], mapped[c] - mapped[a]))
        try:
            jacobian = target @ np.linalg.inv(source)
        except np.linalg.LinAlgError as error:
            raise ValueError("conformal source triangle is singular") from error
        singular = np.linalg.svd(jacobian, compute_uv=False)
        ratio = inf if singular[-1] <= 1e-12 else float(singular[0] / singular[-1])
        distortion[triangle] = ratio
    maximum = max(distortion.values(), default=1.0)
    return DiscreteConformalResult(
        {node: tuple(map(float, mapped[node])) for node in nodes},
        distortion,
        maximum,
    )


def corridor_modulus(length: float, width: float) -> float:
    if not isfinite(length) or not isfinite(width) or length < 0.0 or width <= 0.0:
        raise ValueError("corridor length/width must be finite with positive width")
    return float(length) / float(width)
