"""Higher-level discrete geometry for tactical maps and formations.

This layer complements ``lattice_geometry`` with hex coordinates, digital
topology, occupancy analysis, formation descriptors, and tactical queries.  It
reuses the same cell, shape, ray, and graph-distance contracts as movement and
random deployment code.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, hypot, inf, isfinite, sqrt
from typing import Callable, Iterable, Iterator, Mapping, Sequence

from rl.lattice_geometry import (
    Cell,
    DiagonalPolicy,
    LatticeCoordinate,
    LatticeRay,
    LatticeRegion,
    LatticeShape,
)


HexCell = tuple[int, int]
Cell3D = tuple[int, int, int]
Distance = Callable[[Cell, Cell], float]


class HexCoordinate:
    """Pointy-top axial coordinates using ``(q, r)``."""

    OFFSETS: tuple[HexCell, ...] = (
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, 0),
        (-1, 1),
        (0, 1),
    )

    @classmethod
    def neighbors(cls, cell: HexCell) -> tuple[HexCell, ...]:
        return tuple((cell[0] + dq, cell[1] + dr) for dq, dr in cls.OFFSETS)

    @staticmethod
    def distance(left: HexCell, right: HexCell) -> int:
        dq, dr = left[0] - right[0], left[1] - right[1]
        return (abs(dq) + abs(dr) + abs(dq + dr)) // 2

    @classmethod
    def ball(cls, center: HexCell, radius: int) -> frozenset[HexCell]:
        if radius < 0:
            raise ValueError("radius must be non-negative")
        return frozenset(
            (center[0] + dq, center[1] + dr)
            for dq in range(-radius, radius + 1)
            for dr in range(-radius, radius + 1)
            if cls.distance((0, 0), (dq, dr)) <= radius
        )

    @classmethod
    def ring(cls, center: HexCell, radius: int) -> frozenset[HexCell]:
        if radius < 0:
            raise ValueError("radius must be non-negative")
        return frozenset(
            cell
            for cell in cls.ball(center, radius)
            if cls.distance(center, cell) == radius
        )

    @staticmethod
    def rotate_sixth(cell: HexCell, turns: int = 1, pivot: HexCell = (0, 0)) -> HexCell:
        """Rotate clockwise by multiples of 60 degrees in cube coordinates."""
        q, r = cell[0] - pivot[0], cell[1] - pivot[1]
        x, z = q, r
        y = -x - z
        for _ in range(turns % 6):
            x, y, z = -z, -x, -y
        return x + pivot[0], z + pivot[1]


class GridGeometry:
    @staticmethod
    def neighbors3d(
        cell: Cell3D,
        connected: Callable[[Cell3D, Cell3D], bool] | None = None,
    ) -> tuple[Cell3D, ...]:
        x, y, z = cell
        candidates = (
            (x - 1, y, z),
            (x + 1, y, z),
            (x, y - 1, z),
            (x, y + 1, z),
            (x, y, z - 1),
            (x, y, z + 1),
        )
        if connected is None:
            return candidates
        return tuple(
            candidate for candidate in candidates if connected(cell, candidate)
        )

    @staticmethod
    def line_cells(start: Cell, end: Cell, strict: bool = True) -> tuple[Cell, ...]:
        return (
            LatticeRay.supercover(start, end)
            if strict
            else LatticeRay.bresenham(start, end)
        )


class OccupancyGeometry:
    @staticmethod
    def legal_anchors(
        domain: Iterable[Cell],
        obstacles: Iterable[Cell],
        footprint: LatticeShape,
    ) -> frozenset[Cell]:
        domain_set = set(domain)
        blocked = set(obstacles)
        return frozenset(
            anchor
            for anchor in domain_set
            if footprint.occupied(anchor) <= domain_set
            and footprint.occupied(anchor).isdisjoint(blocked)
        )

    @staticmethod
    def placements_overlap(
        left_anchor: Cell,
        left_footprint: LatticeShape,
        right_anchor: Cell,
        right_footprint: LatticeShape,
    ) -> bool:
        return not left_footprint.occupied(left_anchor).isdisjoint(
            right_footprint.occupied(right_anchor)
        )

    @staticmethod
    def maximum_empty_cells(
        domain: Iterable[Cell],
        obstacles: Iterable[Cell],
        distance: Distance = LatticeCoordinate.manhattan,
        *,
        include_boundary: bool = True,
    ) -> tuple[float, frozenset[Cell]]:
        domain_set = set(domain)
        blocked = set(obstacles)
        candidates = domain_set - blocked
        if not candidates:
            return 0.0, frozenset()
        barriers = set(blocked)
        if include_boundary:
            barriers.update(
                neighbor
                for cell in domain_set
                for neighbor in LatticeCoordinate.neighbors4(cell)
                if neighbor not in domain_set
            )
        if not barriers:
            return inf, frozenset(candidates)
        clearance = {
            cell: max(0.0, min(distance(cell, barrier) for barrier in barriers) - 1.0)
            for cell in candidates
        }
        radius = max(clearance.values())
        return radius, frozenset(
            cell for cell, value in clearance.items() if value == radius
        )


class VisibilityGeometry:
    @staticmethod
    def field_of_view(
        origin: Cell,
        facing: tuple[float, float],
        radius: float,
        half_angle_degrees: float,
        opaque: Callable[[Cell], bool],
    ) -> frozenset[Cell]:
        sector = LatticeShape.sector(radius, facing, half_angle_degrees, origin)
        return frozenset(
            cell
            for cell in sector.cells
            if LatticeRay.line_of_sight(origin, cell, opaque)
        )

    @staticmethod
    def cover_strength(
        start: Cell,
        end: Cell,
        cover: Mapping[Cell, float],
        *,
        include_target: bool = False,
    ) -> float:
        ray = LatticeRay.supercover(start, end)[1:]
        if not include_target:
            ray = ray[:-1]
        return sum(max(0.0, float(cover.get(cell, 0.0))) for cell in ray)

    @staticmethod
    def line_attack_cells(
        origin: Cell,
        direction: tuple[float, float],
        length: float,
        half_width: float = 0.0,
    ) -> frozenset[Cell]:
        norm = hypot(direction[0], direction[1])
        if norm == 0.0 or length < 0.0 or half_width < 0.0:
            raise ValueError(
                "line attack needs a direction and non-negative dimensions"
            )
        ux, uy = direction[0] / norm, direction[1] / norm
        bound = int(length + half_width) + 1
        result = set()
        for dx in range(-bound, bound + 1):
            for dy in range(-bound, bound + 1):
                projection = dx * ux + dy * uy
                perpendicular = abs(dx * uy - dy * ux)
                if (
                    -1e-12 <= projection <= length + 1e-12
                    and perpendicular <= half_width + 1e-12
                ):
                    result.add((origin[0] + dx, origin[1] + dy))
        return frozenset(result)


class RegionAnalysis:
    @staticmethod
    def _neighbors(cell: Cell, connectivity: int) -> tuple[Cell, ...]:
        if connectivity == 4:
            return LatticeCoordinate.neighbors4(cell)
        if connectivity == 8:
            return LatticeCoordinate.neighbors8(
                cell, diagonal_policy=DiagonalPolicy.ONE_CLEAR
            )
        raise ValueError("connectivity must be 4 or 8")

    @classmethod
    def _cut_structure(
        cls, cells: Iterable[Cell], connectivity: int
    ) -> tuple[frozenset[Cell], frozenset[tuple[Cell, Cell]]]:
        graph = set(cells)
        discovery: dict[Cell, int] = {}
        low: dict[Cell, int] = {}
        parent: dict[Cell, Cell] = {}
        child_count: dict[Cell, int] = {}
        articulation: set[Cell] = set()
        bridges: set[tuple[Cell, Cell]] = set()
        clock = 0

        for root in sorted(graph):
            if root in discovery:
                continue
            clock += 1
            discovery[root] = low[root] = clock
            child_count[root] = 0
            stack: list[tuple[Cell, Iterator[Cell]]] = [
                (root, iter(cls._neighbors(root, connectivity)))
            ]
            while stack:
                cell, neighbors = stack[-1]
                try:
                    neighbor = next(neighbors)
                except StopIteration:
                    stack.pop()
                    ancestor = parent.get(cell)
                    if ancestor is None:
                        if child_count[cell] > 1:
                            articulation.add(cell)
                        continue
                    low[ancestor] = min(low[ancestor], low[cell])
                    if ancestor in parent and low[cell] >= discovery[ancestor]:
                        articulation.add(ancestor)
                    if low[cell] > discovery[ancestor]:
                        bridges.add(tuple(sorted((ancestor, cell))))
                    continue
                if neighbor not in graph:
                    continue
                if neighbor not in discovery:
                    parent[neighbor] = cell
                    child_count[cell] += 1
                    child_count[neighbor] = 0
                    clock += 1
                    discovery[neighbor] = low[neighbor] = clock
                    stack.append(
                        (neighbor, iter(cls._neighbors(neighbor, connectivity)))
                    )
                elif parent.get(cell) != neighbor:
                    low[cell] = min(low[cell], discovery[neighbor])
        return frozenset(articulation), frozenset(bridges)

    @classmethod
    def articulation_points(
        cls, cells: Iterable[Cell], connectivity: int = 4
    ) -> frozenset[Cell]:
        return cls._cut_structure(cells, connectivity)[0]

    @classmethod
    def bridges(
        cls, cells: Iterable[Cell], connectivity: int = 4
    ) -> frozenset[tuple[Cell, Cell]]:
        return cls._cut_structure(cells, connectivity)[1]

    @classmethod
    def holes(
        cls,
        foreground: Iterable[Cell],
        background_connectivity: int = 8,
    ) -> tuple[frozenset[Cell], ...]:
        occupied = set(foreground)
        if not occupied:
            return ()
        min_x = min(cell[0] for cell in occupied) - 1
        max_x = max(cell[0] for cell in occupied) + 1
        min_y = min(cell[1] for cell in occupied) - 1
        max_y = max(cell[1] for cell in occupied) + 1
        background = {
            (x, y)
            for x in range(min_x, max_x + 1)
            for y in range(min_y, max_y + 1)
            if (x, y) not in occupied
        }
        components = LatticeRegion.connected_components(
            background, background_connectivity
        )
        return tuple(
            component
            for component in components
            if not any(
                cell[0] in {min_x, max_x} or cell[1] in {min_y, max_y}
                for cell in component
            )
        )

    @classmethod
    def euler_characteristic(
        cls,
        foreground: Iterable[Cell],
        foreground_connectivity: int = 4,
        background_connectivity: int = 8,
    ) -> int:
        cells = set(foreground)
        components = LatticeRegion.connected_components(cells, foreground_connectivity)
        return len(components) - len(cls.holes(cells, background_connectivity))

    @staticmethod
    def is_orthogonally_convex(cells: Iterable[Cell]) -> bool:
        region = set(cells)
        by_x: dict[int, list[int]] = {}
        by_y: dict[int, list[int]] = {}
        for x, y in region:
            by_x.setdefault(x, []).append(y)
            by_y.setdefault(y, []).append(x)
        return all(
            max(values) - min(values) + 1 == len(values)
            for values in (*by_x.values(), *by_y.values())
        )

    @classmethod
    def skeleton(cls, cells: Iterable[Cell]) -> frozenset[Cell]:
        region = set(cells)
        if not region:
            return frozenset()
        boundary = LatticeRegion.boundary(region)
        clearance = LatticeRegion.distance_transform(region, boundary)
        return frozenset(
            cell
            for cell, value in clearance.items()
            if all(
                clearance.get(neighbor, -1) <= value
                for neighbor in LatticeCoordinate.neighbors8(
                    cell, diagonal_policy=DiagonalPolicy.ONE_CLEAR
                )
                if neighbor in region
            )
        )

    @classmethod
    def local_width(cls, cells: Iterable[Cell]) -> dict[Cell, int]:
        region = set(cells)
        clearance = LatticeRegion.distance_transform(
            region, LatticeRegion.boundary(region)
        )
        return {cell: 2 * distance + 1 for cell, distance in clearance.items()}

    @classmethod
    def chokepoints(cls, cells: Iterable[Cell], unit_diameter: int) -> frozenset[Cell]:
        if unit_diameter <= 0:
            raise ValueError("unit diameter must be positive")
        widths = cls.local_width(cells)
        skeleton = cls.skeleton(cells)
        return frozenset(
            cell for cell in skeleton if widths.get(cell, inf) <= unit_diameter
        )

    @staticmethod
    def weighted_voronoi(
        domain: Iterable[Cell],
        sites: Iterable[Cell],
        distance: Distance,
        weights: Mapping[Cell, float],
    ) -> dict[Cell, frozenset[Cell]]:
        cells = set(domain)
        unique_sites = tuple(sorted(set(sites) & cells))
        regions = {site: set() for site in unique_sites}
        for cell in cells:
            reachable = [
                site for site in unique_sites if isfinite(distance(cell, site))
            ]
            if not reachable:
                continue
            owner = min(
                reachable,
                key=lambda site: (distance(cell, site) - weights.get(site, 0.0), site),
            )
            regions[owner].add(cell)
        return {site: frozenset(region) for site, region in regions.items()}


@dataclass(frozen=True)
class FormationDescriptor:
    centroid: tuple[float, float]
    dispersion: float
    covariance: tuple[tuple[float, float], tuple[float, float]]
    principal_direction: tuple[float, float]
    closest_pair: tuple[Cell, Cell] | None
    closest_distance: float


class FormationGeometry:
    @staticmethod
    def describe(
        points: Sequence[Cell],
        weights: Sequence[float] | None = None,
        distance: Distance = LatticeCoordinate.euclidean,
    ) -> FormationDescriptor:
        cells = tuple(points)
        if not cells:
            raise ValueError("formation needs at least one point")
        values = tuple(
            float(value)
            for value in (weights if weights is not None else [1.0] * len(cells))
        )
        if len(values) != len(cells) or any(value < 0.0 for value in values):
            raise ValueError("formation weights must be non-negative and aligned")
        total = sum(values)
        if total <= 0.0:
            raise ValueError("formation weights must have positive sum")
        centroid = (
            sum(weight * cell[0] for cell, weight in zip(cells, values)) / total,
            sum(weight * cell[1] for cell, weight in zip(cells, values)) / total,
        )
        xx = (
            sum(
                weight * (cell[0] - centroid[0]) ** 2
                for cell, weight in zip(cells, values)
            )
            / total
        )
        yy = (
            sum(
                weight * (cell[1] - centroid[1]) ** 2
                for cell, weight in zip(cells, values)
            )
            / total
        )
        xy = (
            sum(
                weight * (cell[0] - centroid[0]) * (cell[1] - centroid[1])
                for cell, weight in zip(cells, values)
            )
            / total
        )
        trace = xx + yy
        determinant = xx * yy - xy * xy
        eigenvalue = trace / 2 + sqrt(max(0.0, trace * trace / 4 - determinant))
        if abs(xy) > 1e-12:
            direction = eigenvalue - yy, xy
        elif xx >= yy:
            direction = (1.0, 0.0)
        else:
            direction = (0.0, 1.0)
        norm = hypot(direction[0], direction[1])
        principal = (direction[0] / norm, direction[1] / norm)
        closest: tuple[Cell, Cell] | None = None
        closest_distance = inf
        for index, left in enumerate(cells):
            for right in cells[index + 1 :]:
                candidate = distance(left, right)
                if candidate < closest_distance:
                    closest, closest_distance = (left, right), candidate
        return FormationDescriptor(
            centroid,
            xx + yy,
            ((xx, xy), (xy, yy)),
            principal,
            closest,
            closest_distance,
        )

    @staticmethod
    def surrounds(target: Cell, attackers: Iterable[Cell]) -> bool:
        hull = LatticeRegion.convex_hull(attackers)
        if len(hull) < 3:
            return False
        signs = []
        for left, right in zip(hull, hull[1:] + hull[:1]):
            cross = (right[0] - left[0]) * (target[1] - left[1]) - (
                right[1] - left[1]
            ) * (target[0] - left[0])
            if cross:
                signs.append(cross > 0)
        return not signs or all(sign == signs[0] for sign in signs)

    @staticmethod
    def flank_angle(target: Cell, left: Cell, right: Cell) -> float:
        a = left[0] - target[0], left[1] - target[1]
        b = right[0] - target[0], right[1] - target[1]
        denominator = hypot(*a) * hypot(*b)
        if denominator == 0.0:
            return 0.0
        cosine = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / denominator))
        return degrees(acos(cosine))


@dataclass(frozen=True)
class AOEResult:
    center: Cell
    score: float
    enemies_hit: frozenset[Cell]
    friendlies_hit: frozenset[Cell]


class TacticalGeometry:
    @staticmethod
    def best_aoe(
        candidates: Iterable[Cell],
        area: LatticeShape,
        enemies: Mapping[Cell, float],
        friendlies: Mapping[Cell, float] | None = None,
        friendly_fire_weight: float = 1.0,
        falloff: Callable[[float], float] | None = None,
    ) -> AOEResult | None:
        if friendly_fire_weight < 0.0:
            raise ValueError("friendly-fire weight must be non-negative")
        allies = friendlies or {}
        best: AOEResult | None = None
        for center in sorted(set(candidates)):
            covered = area.occupied(center)
            enemies_hit = frozenset(covered & enemies.keys())
            friendlies_hit = frozenset(covered & allies.keys())

            def multiplier(cell: Cell) -> float:
                value = (
                    1.0
                    if falloff is None
                    else float(falloff(LatticeCoordinate.euclidean(center, cell)))
                )
                if value < 0.0:
                    raise ValueError("AOE falloff cannot be negative")
                return value

            score = sum(enemies[cell] * multiplier(cell) for cell in enemies_hit)
            score -= friendly_fire_weight * sum(
                allies[cell] * multiplier(cell) for cell in friendlies_hit
            )
            result = AOEResult(center, score, enemies_hit, friendlies_hit)
            if best is None or (result.score, tuple(-v for v in center)) > (
                best.score,
                tuple(-v for v in best.center),
            ):
                best = result
        return best

    @staticmethod
    def combined_threat_probability(
        threat_fields: Sequence[Mapping[Cell, float]],
        domain: Iterable[Cell],
    ) -> dict[Cell, float]:
        result = {}
        for cell in domain:
            survival = 1.0
            for field in threat_fields:
                probability = float(field.get(cell, 0.0))
                if not 0.0 <= probability <= 1.0:
                    raise ValueError(
                        "threat probabilities must be between zero and one"
                    )
                survival *= 1.0 - probability
            result[cell] = 1.0 - survival
        return result

    @staticmethod
    def risk_weighted_cost(
        base_cost: Mapping[Cell, float],
        threat: Mapping[Cell, float],
        risk_weight: float,
    ) -> dict[Cell, float]:
        if risk_weight < 0.0:
            raise ValueError("risk weight must be non-negative")
        return {
            cell: float(cost) + risk_weight * float(threat.get(cell, 0.0))
            for cell, cost in base_cost.items()
        }
