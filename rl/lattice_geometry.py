"""Shared square-lattice geometry for maps, combat queries, and MAPF planning.

Coordinates are integer cell indices.  World-to-cell conversion always uses
floor, including for negative coordinates.  Geometry routines are deliberately
free of game-state dependencies so previews and authoritative resolution can
share the same definitions.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from heapq import heappop, heappush
from math import cos, floor, gcd, hypot, inf, pi, sqrt
from typing import Callable, Iterable, Sequence


Cell = tuple[int, int]
Passable = Callable[[Cell], bool]


class DiagonalPolicy(Enum):
    """How an eight-neighbor move may pass two orthogonal blockers."""

    NEVER = "never"
    ONE_CLEAR = "one-clear"
    BOTH_CLEAR = "both-clear"


class LatticeCoordinate:
    FOUR_OFFSETS: tuple[Cell, ...] = ((0, -1), (0, 1), (-1, 0), (1, 0))
    DIAGONAL_OFFSETS: tuple[Cell, ...] = (
        (-1, -1),
        (1, -1),
        (-1, 1),
        (1, 1),
    )

    @staticmethod
    def world_to_cell(
        point: tuple[float, float],
        cell_size: tuple[float, float] = (1.0, 1.0),
        origin: tuple[float, float] = (0.0, 0.0),
    ) -> Cell:
        if cell_size[0] <= 0 or cell_size[1] <= 0:
            raise ValueError("cell size must be positive")
        return (
            floor((point[0] - origin[0]) / cell_size[0]),
            floor((point[1] - origin[1]) / cell_size[1]),
        )

    @staticmethod
    def cell_center(
        cell: Cell,
        cell_size: tuple[float, float] = (1.0, 1.0),
        origin: tuple[float, float] = (0.0, 0.0),
    ) -> tuple[float, float]:
        if cell_size[0] <= 0 or cell_size[1] <= 0:
            raise ValueError("cell size must be positive")
        return (
            origin[0] + (cell[0] + 0.5) * cell_size[0],
            origin[1] + (cell[1] + 0.5) * cell_size[1],
        )

    @classmethod
    def neighbors4(cls, cell: Cell) -> tuple[Cell, ...]:
        return tuple((cell[0] + dx, cell[1] + dy) for dx, dy in cls.FOUR_OFFSETS)

    @classmethod
    def neighbors8(
        cls,
        cell: Cell,
        passable: Passable | None = None,
        diagonal_policy: DiagonalPolicy = DiagonalPolicy.BOTH_CLEAR,
    ) -> tuple[Cell, ...]:
        candidates = list(cls.neighbors4(cell))
        for dx, dy in cls.DIAGONAL_OFFSETS:
            diagonal = cell[0] + dx, cell[1] + dy
            if diagonal_policy is DiagonalPolicy.NEVER:
                continue
            if passable is not None:
                orthogonal = (
                    passable((cell[0] + dx, cell[1])),
                    passable((cell[0], cell[1] + dy)),
                )
                if diagonal_policy is DiagonalPolicy.BOTH_CLEAR and not all(orthogonal):
                    continue
                if diagonal_policy is DiagonalPolicy.ONE_CLEAR and not any(orthogonal):
                    continue
            candidates.append(diagonal)
        if passable is not None:
            candidates = [candidate for candidate in candidates if passable(candidate)]
        return tuple(candidates)

    @staticmethod
    def manhattan(left: Cell, right: Cell) -> int:
        return abs(left[0] - right[0]) + abs(left[1] - right[1])

    @staticmethod
    def chebyshev(left: Cell, right: Cell) -> int:
        return max(abs(left[0] - right[0]), abs(left[1] - right[1]))

    @staticmethod
    def euclidean(left: Cell, right: Cell) -> float:
        return hypot(left[0] - right[0], left[1] - right[1])

    @staticmethod
    def octile(left: Cell, right: Cell) -> float:
        dx, dy = abs(left[0] - right[0]), abs(left[1] - right[1])
        return max(dx, dy) + (sqrt(2.0) - 1.0) * min(dx, dy)

    @staticmethod
    def primitive_direction(start: Cell, end: Cell) -> Cell:
        dx, dy = end[0] - start[0], end[1] - start[1]
        divisor = gcd(abs(dx), abs(dy))
        return (0, 0) if divisor == 0 else (dx // divisor, dy // divisor)

    @classmethod
    def segment_lattice_points(cls, start: Cell, end: Cell) -> tuple[Cell, ...]:
        direction = cls.primitive_direction(start, end)
        count = gcd(abs(end[0] - start[0]), abs(end[1] - start[1]))
        return tuple(
            (start[0] + step * direction[0], start[1] + step * direction[1])
            for step in range(count + 1)
        )


@dataclass(frozen=True)
class LatticeShape:
    """A finite set of occupied offsets, normally relative to an anchor."""

    cells: frozenset[Cell]

    @classmethod
    def from_cells(cls, cells: Iterable[Cell]) -> "LatticeShape":
        return cls(frozenset((int(x), int(y)) for x, y in cells))

    @classmethod
    def manhattan_ball(cls, radius: int, center: Cell = (0, 0)) -> "LatticeShape":
        if radius < 0:
            raise ValueError("radius must be non-negative")
        return cls.from_cells(
            (center[0] + x, center[1] + y)
            for x in range(-radius, radius + 1)
            for y in range(-radius, radius + 1)
            if abs(x) + abs(y) <= radius
        )

    @classmethod
    def chebyshev_ball(cls, radius: int, center: Cell = (0, 0)) -> "LatticeShape":
        if radius < 0:
            raise ValueError("radius must be non-negative")
        return cls.from_cells(
            (center[0] + x, center[1] + y)
            for x in range(-radius, radius + 1)
            for y in range(-radius, radius + 1)
        )

    @classmethod
    def euclidean_ball(cls, radius: float, center: Cell = (0, 0)) -> "LatticeShape":
        if radius < 0:
            raise ValueError("radius must be non-negative")
        bound = int(floor(radius))
        squared = radius * radius
        return cls.from_cells(
            (center[0] + x, center[1] + y)
            for x in range(-bound, bound + 1)
            for y in range(-bound, bound + 1)
            if x * x + y * y <= squared
        )

    @classmethod
    def ring(
        cls,
        inner_radius: float,
        outer_radius: float,
        center: Cell = (0, 0),
    ) -> "LatticeShape":
        if inner_radius < 0 or outer_radius < inner_radius:
            raise ValueError("ring radii must satisfy 0 <= inner <= outer")
        return cls.from_cells(
            cell
            for cell in cls.euclidean_ball(outer_radius, center).cells
            if LatticeCoordinate.euclidean(cell, center) + 1e-12 >= inner_radius
        )

    @classmethod
    def sector(
        cls,
        radius: float,
        direction: tuple[float, float],
        half_angle_degrees: float,
        center: Cell = (0, 0),
    ) -> "LatticeShape":
        length = hypot(direction[0], direction[1])
        if length == 0:
            raise ValueError("sector direction must be non-zero")
        if not 0 <= half_angle_degrees <= 180:
            raise ValueError("half angle must be between 0 and 180 degrees")
        threshold = cos(half_angle_degrees * pi / 180.0)
        cells = {center}
        for cell in cls.euclidean_ball(radius, center).cells:
            dx, dy = cell[0] - center[0], cell[1] - center[1]
            distance = hypot(dx, dy)
            if distance == 0:
                continue
            alignment = (dx * direction[0] + dy * direction[1]) / (distance * length)
            if alignment + 1e-12 >= threshold:
                cells.add(cell)
        return cls(frozenset(cells))

    def translate(self, offset: Cell) -> "LatticeShape":
        return self.from_cells((x + offset[0], y + offset[1]) for x, y in self.cells)

    def rotate_quarter(self, turns: int = 1, pivot: Cell = (0, 0)) -> "LatticeShape":
        turns %= 4

        def rotate(cell: Cell) -> Cell:
            x, y = cell[0] - pivot[0], cell[1] - pivot[1]
            for _ in range(turns):
                x, y = -y, x
            return x + pivot[0], y + pivot[1]

        return self.from_cells(rotate(cell) for cell in self.cells)

    def mirror(self, axis: str = "x", pivot: Cell = (0, 0)) -> "LatticeShape":
        if axis not in {"x", "y"}:
            raise ValueError("mirror axis must be 'x' or 'y'")
        if axis == "x":
            return self.from_cells((x, 2 * pivot[1] - y) for x, y in self.cells)
        return self.from_cells((2 * pivot[0] - x, y) for x, y in self.cells)

    def union(self, other: "LatticeShape") -> "LatticeShape":
        return LatticeShape(self.cells | other.cells)

    def intersection(self, other: "LatticeShape") -> "LatticeShape":
        return LatticeShape(self.cells & other.cells)

    def difference(self, other: "LatticeShape") -> "LatticeShape":
        return LatticeShape(self.cells - other.cells)

    def dilate(self, kernel: "LatticeShape") -> "LatticeShape":
        return self.from_cells(
            (x + dx, y + dy)
            for x, y in self.cells
            for dx, dy in kernel.cells
        )

    def erode(self, kernel: "LatticeShape") -> "LatticeShape":
        return self.from_cells(
            anchor
            for anchor in self.cells
            if all(
                (anchor[0] + dx, anchor[1] + dy) in self.cells
                for dx, dy in kernel.cells
            )
        )

    def opening(self, kernel: "LatticeShape") -> "LatticeShape":
        """Remove protrusions too small to contain the structuring element."""
        return self.erode(kernel).dilate(kernel)

    def closing(self, kernel: "LatticeShape") -> "LatticeShape":
        """Fill gaps that are smaller than the structuring element."""
        return self.dilate(kernel).erode(kernel)

    def morphological_gradient(self, kernel: "LatticeShape") -> "LatticeShape":
        """Return the two-sided boundary band dilation minus erosion."""
        return self.dilate(kernel).difference(self.erode(kernel))

    @staticmethod
    def configuration_obstacles(
        obstacles: Iterable[Cell], footprint: "LatticeShape"
    ) -> "LatticeShape":
        reflected = footprint.from_cells((-x, -y) for x, y in footprint.cells)
        return LatticeShape.from_cells(obstacles).dilate(reflected)

    def occupied(self, anchor: Cell) -> frozenset[Cell]:
        return frozenset((anchor[0] + x, anchor[1] + y) for x, y in self.cells)

    def overlaps(self, anchor: Cell, blocked: Iterable[Cell]) -> bool:
        return not self.occupied(anchor).isdisjoint(blocked)


class LatticeRay:
    @staticmethod
    def bresenham(start: Cell, end: Cell) -> tuple[Cell, ...]:
        x0, y0 = start
        x1, y1 = end
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        error = dx - dy
        points: list[Cell] = []
        while True:
            points.append((x0, y0))
            if (x0, y0) == (x1, y1):
                return tuple(points)
            doubled = 2 * error
            if doubled > -dy:
                error -= dy
                x0 += sx
            if doubled < dx:
                error += dx
                y0 += sy

    @staticmethod
    def supercover(start: Cell, end: Cell) -> tuple[Cell, ...]:
        """Return every cell touched by the center-to-center segment.

        At an exact grid-corner crossing both side cells are included.  This is
        the conservative form needed for deterministic line-of-sight checks.
        """
        x, y = start
        dx, dy = end[0] - x, end[1] - y
        nx, ny = abs(dx), abs(dy)
        sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
        ix = iy = 0
        result: list[Cell] = [(x, y)]

        def append(cell: Cell) -> None:
            if cell not in result:
                result.append(cell)

        while ix < nx or iy < ny:
            decision = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
            if decision == 0:
                append((x + sx, y))
                append((x, y + sy))
                x += sx
                y += sy
                ix += 1
                iy += 1
            elif decision < 0:
                x += sx
                ix += 1
            else:
                y += sy
                iy += 1
            append((x, y))
        return tuple(result)

    @classmethod
    def line_of_sight(
        cls,
        start: Cell,
        end: Cell,
        opaque: Callable[[Cell], bool],
        *,
        include_end: bool = True,
    ) -> bool:
        cells = cls.supercover(start, end)[1:]
        if not include_end:
            cells = cells[:-1]
        return not any(opaque(cell) for cell in cells)

    @classmethod
    def height_visible(
        cls,
        start: Cell,
        end: Cell,
        height: Callable[[Cell], float],
        observer_height: float = 0.0,
        target_height: float = 0.0,
    ) -> bool:
        ray = cls.supercover(start, end)
        if len(ray) <= 2:
            return True
        source = height(start) + observer_height
        target = height(end) + target_height
        total = LatticeCoordinate.euclidean(start, end)
        for cell in ray[1:-1]:
            progress = LatticeCoordinate.euclidean(start, cell) / total
            sight_height = source + progress * (target - source)
            if height(cell) >= sight_height:
                return False
        return True


class LatticeRegion:
    @staticmethod
    def connected_components(
        cells: Iterable[Cell], connectivity: int = 4
    ) -> tuple[frozenset[Cell], ...]:
        remaining = set(cells)
        result: list[frozenset[Cell]] = []
        if connectivity not in {4, 8}:
            raise ValueError("connectivity must be 4 or 8")
        while remaining:
            root = min(remaining)
            remaining.remove(root)
            component = {root}
            frontier = [root]
            while frontier:
                cell = frontier.pop()
                neighbors = (
                    LatticeCoordinate.neighbors4(cell)
                    if connectivity == 4
                    else LatticeCoordinate.neighbors8(
                        cell, diagonal_policy=DiagonalPolicy.ONE_CLEAR
                    )
                )
                for neighbor in neighbors:
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        component.add(neighbor)
                        frontier.append(neighbor)
            result.append(frozenset(component))
        return tuple(result)

    @staticmethod
    def perimeter(cells: Iterable[Cell]) -> int:
        region = set(cells)
        return sum(
            neighbor not in region
            for cell in region
            for neighbor in LatticeCoordinate.neighbors4(cell)
        )

    @classmethod
    def compactness(cls, cells: Iterable[Cell]) -> float:
        region = set(cells)
        perimeter = cls.perimeter(region)
        return 0.0 if perimeter == 0 else 4.0 * pi * len(region) / (perimeter**2)

    @staticmethod
    def distance_transform(
        cells: Iterable[Cell], sources: Iterable[Cell]
    ) -> dict[Cell, int]:
        region = set(cells)
        distance = {source: 0 for source in sources if source in region}
        frontier = deque(distance)
        while frontier:
            cell = frontier.popleft()
            for neighbor in LatticeCoordinate.neighbors4(cell):
                if neighbor in region and neighbor not in distance:
                    distance[neighbor] = distance[cell] + 1
                    frontier.append(neighbor)
        return distance

    @staticmethod
    def boundary(cells: Iterable[Cell]) -> frozenset[Cell]:
        region = set(cells)
        return frozenset(
            cell
            for cell in region
            if any(neighbor not in region for neighbor in LatticeCoordinate.neighbors4(cell))
        )

    @classmethod
    def narrow_cells(cls, cells: Iterable[Cell], max_clearance: int) -> frozenset[Cell]:
        region = set(cells)
        distance = cls.distance_transform(region, cls.boundary(region))
        return frozenset(cell for cell, value in distance.items() if value <= max_clearance)

    @staticmethod
    def convex_hull(points: Iterable[Cell]) -> tuple[Cell, ...]:
        ordered = sorted(set(points))
        if len(ordered) <= 1:
            return tuple(ordered)

        def cross(origin: Cell, left: Cell, right: Cell) -> int:
            return ((left[0] - origin[0]) * (right[1] - origin[1])
                    - (left[1] - origin[1]) * (right[0] - origin[0]))

        lower: list[Cell] = []
        for point in ordered:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
                lower.pop()
            lower.append(point)
        upper: list[Cell] = []
        for point in reversed(ordered):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
                upper.pop()
            upper.append(point)
        return tuple(lower[:-1] + upper[:-1])

    @staticmethod
    def polygon_double_area(vertices: Sequence[Cell]) -> int:
        if len(vertices) < 3:
            return 0
        return abs(
            sum(
                left[0] * right[1] - right[0] * left[1]
                for left, right in zip(vertices, vertices[1:] + vertices[:1])
            )
        )

    @staticmethod
    def polygon_boundary_points(vertices: Sequence[Cell]) -> int:
        if len(vertices) < 2:
            return len(vertices)
        return sum(
            gcd(abs(right[0] - left[0]), abs(right[1] - left[1]))
            for left, right in zip(vertices, vertices[1:] + vertices[:1])
        )

    @classmethod
    def pick_interior_points(cls, vertices: Sequence[Cell]) -> int:
        if len(vertices) < 3:
            return 0
        numerator = cls.polygon_double_area(vertices) - cls.polygon_boundary_points(vertices) + 2
        if numerator < 0 or numerator % 2:
            raise ValueError("vertices do not define a simple lattice polygon")
        return numerator // 2

    @classmethod
    def ehrhart_count(cls, vertices: Sequence[Cell], scale: int) -> int:
        if scale < 0:
            raise ValueError("scale must be non-negative")
        area = Fraction(cls.polygon_double_area(vertices), 2)
        boundary = cls.polygon_boundary_points(vertices)
        value = area * scale * scale + Fraction(boundary * scale, 2) + 1
        if value.denominator != 1:
            raise ValueError("vertices do not define a lattice polygon")
        return value.numerator


@dataclass
class SpaceTimeGrid:
    """Reservation table for vertex, destination, and edge-swap conflicts."""

    destinations: dict[Cell, int] = field(default_factory=dict)
    vertices: dict[tuple[int, Cell], int] = field(default_factory=dict)
    edges: dict[tuple[int, Cell, Cell], int] = field(default_factory=dict)

    def reserve_destination(self, cell: Cell, owner_id: int) -> bool:
        owner = self.destinations.get(cell)
        if owner is not None and owner != owner_id:
            return False
        self.destinations[cell] = owner_id
        return True

    def path_conflict(
        self, path: Sequence[Cell], owner_id: int, horizon: int
    ) -> bool:
        if not path:
            return False
        if horizon < 0:
            raise ValueError("horizon must be non-negative")
        destination_owner = self.destinations.get(path[-1])
        if destination_owner is not None and destination_owner != owner_id:
            return True
        clipped = tuple(path[: horizon + 1])
        for time, cell in enumerate(clipped):
            vertex_owner = self.vertices.get((time, cell))
            if vertex_owner is not None and vertex_owner != owner_id:
                return True
            if time:
                previous = clipped[time - 1]
                reverse_owner = self.edges.get((time, cell, previous))
                if reverse_owner is not None and reverse_owner != owner_id:
                    return True
        destination = clipped[-1]
        for time in range(len(clipped), horizon + 1):
            vertex_owner = self.vertices.get((time, destination))
            if vertex_owner is not None and vertex_owner != owner_id:
                return True
        return False

    def reserve_path(
        self, path: Sequence[Cell], owner_id: int, horizon: int
    ) -> bool:
        if not path or self.path_conflict(path, owner_id, horizon):
            return False
        clipped = tuple(path[: horizon + 1])
        for time, cell in enumerate(clipped):
            self.vertices[(time, cell)] = owner_id
            if time:
                self.edges[(time, clipped[time - 1], cell)] = owner_id
        destination = clipped[-1]
        for time in range(len(clipped), horizon + 1):
            self.vertices[(time, destination)] = owner_id
        return self.reserve_destination(path[-1], owner_id)

    def copy(self) -> "SpaceTimeGrid":
        return SpaceTimeGrid(
            destinations=dict(self.destinations),
            vertices=dict(self.vertices),
            edges=dict(self.edges),
        )


def weighted_shortest_path(
    start: Cell,
    destination: Cell,
    width: int,
    height: int,
    costs: Sequence[int],
) -> tuple[Cell, ...]:
    """A* on the four-neighbor lattice; impassable cells have cost >= 255."""
    if width <= 0 or height <= 0 or len(costs) != width * height:
        raise ValueError("cost grid dimensions do not match")
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        return ()
    if not (0 <= destination[0] < width and 0 <= destination[1] < height):
        return ()
    if start == destination:
        return (start,)
    frontier: list[tuple[float, float, Cell]] = [
        (float(LatticeCoordinate.manhattan(start, destination)), 0.0, start)
    ]
    parents: dict[Cell, Cell] = {}
    best = {start: 0.0}
    while frontier:
        _, spent, cell = heappop(frontier)
        if spent != best.get(cell):
            continue
        if cell == destination:
            path = [cell]
            while path[-1] != start:
                path.append(parents[path[-1]])
            return tuple(reversed(path))
        for neighbor in LatticeCoordinate.neighbors4(cell):
            if not (0 <= neighbor[0] < width and 0 <= neighbor[1] < height):
                continue
            step = int(costs[neighbor[1] * width + neighbor[0]])
            if step >= 255:
                continue
            candidate = spent + max(1, step)
            if candidate >= best.get(neighbor, inf):
                continue
            best[neighbor] = candidate
            parents[neighbor] = cell
            estimate = candidate + LatticeCoordinate.manhattan(neighbor, destination)
            heappush(frontier, (estimate, candidate, neighbor))
    return ()
