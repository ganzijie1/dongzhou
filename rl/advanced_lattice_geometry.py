"""Discrete calculus, topology-preserving morphology, and lattice geodesics."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf, isfinite, sqrt
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from rl.lattice_geometry import Cell, LatticeCoordinate, LatticeRegion


Vector = tuple[float, float]


def _finite_scalar_field(values: Mapping[Cell, float]) -> dict[Cell, float]:
    result = {cell: float(value) for cell, value in values.items()}
    if not result or any(not isfinite(value) for value in result.values()):
        raise ValueError("lattice scalar field must be finite and non-empty")
    return result


class DiscreteFieldCalculus:
    """Finite differences and graph operators on irregular square-grid domains."""

    @staticmethod
    def gradient(
        values: Mapping[Cell, float], *, spacing: Vector = (1.0, 1.0)
    ) -> dict[Cell, Vector]:
        field = _finite_scalar_field(values)
        dx, dy = map(float, spacing)
        if not isfinite(dx) or not isfinite(dy) or dx <= 0.0 or dy <= 0.0:
            raise ValueError("lattice spacing must be positive and finite")

        def derivative(cell: Cell, positive: Cell, negative: Cell, scale: float) -> float:
            has_positive, has_negative = positive in field, negative in field
            if has_positive and has_negative:
                return (field[positive] - field[negative]) / (2.0 * scale)
            if has_positive:
                return (field[positive] - field[cell]) / scale
            if has_negative:
                return (field[cell] - field[negative]) / scale
            return 0.0

        return {
            cell: (
                derivative(cell, (cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]), dx),
                derivative(cell, (cell[0], cell[1] + 1), (cell[0], cell[1] - 1), dy),
            )
            for cell in field
        }

    @staticmethod
    def divergence(
        vectors: Mapping[Cell, Sequence[float]], *, spacing: Vector = (1.0, 1.0)
    ) -> dict[Cell, float]:
        vector_field = {cell: tuple(map(float, vector)) for cell, vector in vectors.items()}
        if not vector_field or any(
            len(vector) != 2 or any(not isfinite(value) for value in vector)
            for vector in vector_field.values()
        ):
            raise ValueError("lattice vector field must contain finite two-vectors")
        x_component = {cell: vector[0] for cell, vector in vector_field.items()}
        y_component = {cell: vector[1] for cell, vector in vector_field.items()}
        dx = DiscreteFieldCalculus.gradient(x_component, spacing=spacing)
        dy = DiscreteFieldCalculus.gradient(y_component, spacing=spacing)
        return {cell: dx[cell][0] + dy[cell][1] for cell in vector_field}

    @staticmethod
    def graph_laplacian(values: Mapping[Cell, float]) -> dict[Cell, float]:
        """Return neighbor-minus-center Laplacian with a Neumann outer boundary."""

        field = _finite_scalar_field(values)
        return {
            cell: sum(
                field[neighbor] - field[cell]
                for neighbor in LatticeCoordinate.neighbors4(cell)
                if neighbor in field
            )
            for cell in field
        }

    @staticmethod
    def dirichlet_energy(values: Mapping[Cell, float]) -> float:
        field = _finite_scalar_field(values)
        return sum(
            0.5 * (field[cell] - field[neighbor]) ** 2
            for cell in field
            for neighbor in LatticeCoordinate.neighbors4(cell)
            if neighbor in field and cell < neighbor
        )


@dataclass(frozen=True)
class PoissonResult:
    values: Mapping[Cell, float]
    maximum_residual: float


def solve_lattice_poisson(
    domain: Iterable[Cell],
    source: Mapping[Cell, float],
    boundary_values: Mapping[Cell, float],
) -> PoissonResult:
    """Solve ``degree*u - neighbor_sum = source`` with Dirichlet boundary data."""

    cells = frozenset(domain)
    boundary = {cell: float(value) for cell, value in boundary_values.items()}
    forcing = {cell: float(source.get(cell, 0.0)) for cell in cells}
    if (
        not cells
        or not boundary
        or not boundary.keys() <= cells
        or any(not isfinite(value) for value in (*boundary.values(), *forcing.values()))
    ):
        raise ValueError("Poisson domain, source, or boundary data are invalid")
    if any(
        component.isdisjoint(boundary)
        for component in LatticeRegion.connected_components(cells, 4)
    ):
        raise ValueError("every Poisson connected component needs a boundary cell")
    interior = tuple(sorted(cells - boundary.keys()))
    if not interior:
        return PoissonResult(boundary, 0.0)
    positions = {cell: index for index, cell in enumerate(interior)}
    rows: list[int] = []
    columns: list[int] = []
    entries: list[float] = []
    right = np.zeros(len(interior), dtype=np.float64)
    for cell, row in positions.items():
        neighbors = [neighbor for neighbor in LatticeCoordinate.neighbors4(cell) if neighbor in cells]
        if not neighbors:
            raise ValueError("an isolated interior cell makes the Poisson system singular")
        rows.append(row)
        columns.append(row)
        entries.append(float(len(neighbors)))
        right[row] = forcing[cell]
        for neighbor in neighbors:
            if neighbor in positions:
                rows.append(row)
                columns.append(positions[neighbor])
                entries.append(-1.0)
            elif neighbor in boundary:
                right[row] += boundary[neighbor]
    matrix = csr_matrix((entries, (rows, columns)), shape=(len(interior), len(interior)))
    solved = np.asarray(spsolve(matrix, right), dtype=np.float64)
    if solved.shape != (len(interior),) or np.any(~np.isfinite(solved)):
        raise ValueError("Poisson system is singular; every component needs a boundary cell")
    values = dict(boundary)
    values.update({cell: float(solved[index]) for cell, index in positions.items()})
    residual = matrix @ solved - right
    return PoissonResult(values, float(np.max(np.abs(residual), initial=0.0)))


@dataclass(frozen=True)
class GeodesicResult:
    distances: Mapping[Cell, float]
    predecessors: Mapping[Cell, Cell]

    def path_to(self, target: Cell) -> tuple[Cell, ...]:
        if target not in self.distances or not isfinite(self.distances[target]):
            return ()
        path = [target]
        while path[-1] in self.predecessors:
            path.append(self.predecessors[path[-1]])
        return tuple(reversed(path))


def anisotropic_geodesic_distance(
    domain: Iterable[Cell],
    sources: Iterable[Cell],
    metrics: Mapping[Cell, Sequence[Sequence[float]]] | None = None,
    *,
    connectivity: int = 8,
) -> GeodesicResult:
    """Dijkstra approximation of an anisotropic Eikonal metric on a lattice."""

    cells = frozenset(domain)
    starts = frozenset(sources) & cells
    if not cells or not starts or connectivity not in {4, 8}:
        raise ValueError("anisotropic geodesic domain, sources, or connectivity are invalid")
    tensors: dict[Cell, np.ndarray] = {}
    for cell in cells:
        tensor = np.asarray(metrics.get(cell, np.eye(2)) if metrics else np.eye(2), dtype=np.float64)
        if tensor.shape != (2, 2) or np.any(~np.isfinite(tensor)) or not np.allclose(tensor, tensor.T):
            raise ValueError("anisotropic metric tensors must be finite symmetric 2x2 matrices")
        if np.min(np.linalg.eigvalsh(tensor)) <= 0.0:
            raise ValueError("anisotropic metric tensors must be positive definite")
        tensors[cell] = tensor
    distances = {cell: inf for cell in cells}
    predecessors: dict[Cell, Cell] = {}
    frontier: list[tuple[float, Cell]] = []
    for source in starts:
        distances[source] = 0.0
        heappush(frontier, (0.0, source))
    while frontier:
        spent, cell = heappop(frontier)
        if spent != distances[cell]:
            continue
        neighbors = (
            LatticeCoordinate.neighbors4(cell)
            if connectivity == 4
            else LatticeCoordinate.neighbors8(cell)
        )
        for neighbor in neighbors:
            if neighbor not in cells:
                continue
            delta = np.asarray((neighbor[0] - cell[0], neighbor[1] - cell[1]), dtype=np.float64)
            tensor = 0.5 * (tensors[cell] + tensors[neighbor])
            step = sqrt(float(delta @ tensor @ delta))
            candidate = spent + step
            if candidate + 1e-12 < distances[neighbor]:
                distances[neighbor] = candidate
                predecessors[neighbor] = cell
                heappush(frontier, (candidate, neighbor))
    return GeodesicResult(distances, predecessors)


def signed_euclidean_distance(
    domain: Iterable[Cell], foreground: Iterable[Cell]
) -> dict[Cell, float]:
    """Signed distance on a finite domain: positive inside, negative outside."""

    cells = frozenset(domain)
    inside = frozenset(foreground) & cells
    outside = cells - inside
    if not cells:
        raise ValueError("signed distance needs a non-empty domain")
    result = {}
    for cell in cells:
        opposite = outside if cell in inside else inside
        distance = min(
            (LatticeCoordinate.euclidean(cell, other) for other in opposite),
            default=inf,
        )
        result[cell] = distance if cell in inside else -distance
    return result


def morphological_reconstruction(
    marker: Iterable[Cell], mask: Iterable[Cell], *, connectivity: int = 4
) -> frozenset[Cell]:
    """Reconstruct marker components by repeated geodesic dilation under a mask."""

    allowed = frozenset(mask)
    seeds = frozenset(marker)
    if not seeds <= allowed or connectivity not in {4, 8}:
        raise ValueError("morphological marker must lie in its mask")
    reached = set(seeds)
    frontier = list(seeds)
    while frontier:
        cell = frontier.pop()
        neighbors = (
            LatticeCoordinate.neighbors4(cell)
            if connectivity == 4
            else LatticeCoordinate.neighbors8(cell)
        )
        for neighbor in neighbors:
            if neighbor in allowed and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    return frozenset(reached)


def topology_preserving_thinning(cells: Iterable[Cell]) -> frozenset[Cell]:
    """Zhang-Suen thinning for 8-connected foreground on the square lattice."""

    foreground = set(cells)
    if not foreground:
        return frozenset()

    def neighbors(cell: Cell) -> tuple[Cell, ...]:
        x, y = cell
        return (
            (x, y - 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
            (x, y + 1),
            (x - 1, y + 1),
            (x - 1, y),
            (x - 1, y - 1),
        )

    changed = True
    while changed:
        changed = False
        for first_pass in (True, False):
            removable = set()
            for cell in foreground:
                ring = neighbors(cell)
                bits = [neighbor in foreground for neighbor in ring]
                count = sum(bits)
                transitions = sum(
                    not bits[index] and bits[(index + 1) % 8] for index in range(8)
                )
                if not 2 <= count <= 6 or transitions != 1:
                    continue
                north, east, south, west = bits[0], bits[2], bits[4], bits[6]
                if first_pass:
                    blocked = north and east and south or east and south and west
                else:
                    blocked = north and east and west or north and south and west
                if not blocked:
                    removable.add(cell)
            if removable:
                foreground.difference_update(removable)
                changed = True
    return frozenset(foreground)


@dataclass(frozen=True)
class LatticeTopologySignature:
    area: int
    perimeter: int
    components: int
    holes: int
    euler_characteristic: int


def lattice_topology_signature(cells: Iterable[Cell]) -> LatticeTopologySignature:
    """Return digital Minkowski/topology invariants under 4/8 connectivity."""

    region = frozenset(cells)
    if not region:
        return LatticeTopologySignature(0, 0, 0, 0, 0)
    components = len(LatticeRegion.connected_components(region, 4))
    min_x = min(cell[0] for cell in region) - 1
    max_x = max(cell[0] for cell in region) + 1
    min_y = min(cell[1] for cell in region) - 1
    max_y = max(cell[1] for cell in region) + 1
    background = {
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) not in region
    }
    background_components = LatticeRegion.connected_components(background, 8)
    holes = sum(
        not any(
            cell[0] in {min_x, max_x} or cell[1] in {min_y, max_y}
            for cell in component
        )
        for component in background_components
    )
    return LatticeTopologySignature(
        len(region),
        LatticeRegion.perimeter(region),
        components,
        holes,
        components - holes,
    )
