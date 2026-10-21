"""Random geometry for reproducible, constrained tactical deployments.

The module follows a strict separation of concerns:

* point processes propose spatial variation;
* hard constraints reject illegal or unfair layouts;
* statistics measure clustering, coverage, and connectivity;
* the existing MAPF planner handles motion after deployment.

All distances can use :class:`LatticeGraph`, so walls and terrain replace the
infinite-plane assumptions that are inappropriate for a tactical map.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import inf, isfinite, log, sqrt
from random import Random
from statistics import fmean
from typing import Callable, Iterable, Mapping, Sequence

from rl.lattice_geometry import Cell, LatticeCoordinate, LatticeShape


Distance = Callable[[Cell, Cell], float]
Intensity = Mapping[Cell, float] | Callable[[Cell], float]
PairSeparation = float | Callable[[Cell, Cell], float]
LayoutValidator = Callable[[tuple[Cell, ...]], bool]


def _quantile(values: Sequence[float], probability: float) -> float:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("quantile probability must be between zero and one")
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return inf
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _intensity_value(intensity: Intensity, cell: Cell) -> float:
    value = intensity(cell) if callable(intensity) else intensity.get(cell, 0.0)
    value = float(value)
    if value < 0.0:
        raise ValueError("intensity cannot be negative")
    return value


@dataclass
class LatticeGraph:
    """A traversable lattice with optional asymmetric entry and edge costs."""

    cells: frozenset[Cell]
    entry_costs: Mapping[Cell, float] = field(default_factory=dict)
    edge_costs: Mapping[tuple[Cell, Cell], float] = field(default_factory=dict)
    _distance_cache: dict[Cell, dict[Cell, float]] = field(
        default_factory=dict, init=False, repr=False
    )

    @classmethod
    def from_size(
        cls,
        width: int,
        height: int,
        blocked: Iterable[Cell] = (),
        entry_costs: Mapping[Cell, float] | None = None,
    ) -> "LatticeGraph":
        if width <= 0 or height <= 0:
            raise ValueError("graph dimensions must be positive")
        excluded = set(blocked)
        return cls(
            frozenset(
                (x, y)
                for y in range(height)
                for x in range(width)
                if (x, y) not in excluded
            ),
            dict(entry_costs or {}),
        )

    def __post_init__(self) -> None:
        if any(float(value) <= 0.0 for value in self.entry_costs.values()):
            raise ValueError("entry costs must be positive")
        if any(float(value) <= 0.0 for value in self.edge_costs.values()):
            raise ValueError("edge costs must be positive")

    def neighbors(self, cell: Cell) -> tuple[Cell, ...]:
        if cell not in self.cells:
            return ()
        return tuple(
            neighbor
            for neighbor in LatticeCoordinate.neighbors4(cell)
            if neighbor in self.cells
        )

    def step_cost(self, source: Cell, target: Cell) -> float:
        if target not in self.neighbors(source):
            return inf
        return float(
            self.edge_costs.get((source, target), self.entry_costs.get(target, 1.0))
        )

    def shortest_distances(self, source: Cell) -> dict[Cell, float]:
        if source not in self.cells:
            return {}
        cached = self._distance_cache.get(source)
        if cached is not None:
            return cached
        distances = {source: 0.0}
        frontier: list[tuple[float, Cell]] = [(0.0, source)]
        while frontier:
            spent, cell = heappop(frontier)
            if spent != distances.get(cell):
                continue
            for neighbor in self.neighbors(cell):
                candidate = spent + self.step_cost(cell, neighbor)
                if candidate >= distances.get(neighbor, inf):
                    continue
                distances[neighbor] = candidate
                heappush(frontier, (candidate, neighbor))
        self._distance_cache[source] = distances
        return distances

    def distance(self, source: Cell, target: Cell) -> float:
        return self.shortest_distances(source).get(target, inf)

    def ball(self, center: Cell, radius: float) -> frozenset[Cell]:
        if radius < 0.0:
            raise ValueError("radius must be non-negative")
        return frozenset(
            cell
            for cell, distance in self.shortest_distances(center).items()
            if distance <= radius
        )

    def shortest_path(
        self,
        starts: Iterable[Cell],
        goals: Iterable[Cell],
        blocked: Iterable[Cell] = (),
    ) -> tuple[Cell, ...]:
        forbidden = set(blocked)
        goal_set = set(goals) & self.cells - forbidden
        roots = sorted(set(starts) & self.cells - forbidden)
        if not roots or not goal_set:
            return ()
        frontier: list[tuple[float, Cell]] = []
        distances: dict[Cell, float] = {}
        parents: dict[Cell, Cell] = {}
        for root in roots:
            distances[root] = 0.0
            heappush(frontier, (0.0, root))
        while frontier:
            spent, cell = heappop(frontier)
            if spent != distances.get(cell):
                continue
            if cell in goal_set:
                path = [cell]
                while path[-1] not in roots:
                    path.append(parents[path[-1]])
                return tuple(reversed(path))
            for neighbor in self.neighbors(cell):
                if neighbor in forbidden:
                    continue
                candidate = spent + self.step_cost(cell, neighbor)
                if candidate >= distances.get(neighbor, inf):
                    continue
                distances[neighbor] = candidate
                parents[neighbor] = cell
                heappush(frontier, (candidate, neighbor))
        return ()


@dataclass(frozen=True)
class MarkedPoint:
    cell: Cell
    mark: str
    radius: float = 0.5
    facing: Cell = (0, 1)
    arrival_time: int = 0

    def __post_init__(self) -> None:
        if self.radius < 0.0:
            raise ValueError("point radius must be non-negative")
        if self.arrival_time < 0:
            raise ValueError("arrival time must be non-negative")


def weighted_sample_without_replacement(
    candidates: Iterable[Cell],
    intensity: Intensity,
    count: int,
    rng: Random,
) -> tuple[Cell, ...]:
    """Weighted sampling via independent exponential-race keys."""
    if count < 0:
        raise ValueError("sample count must be non-negative")
    keyed: list[tuple[float, Cell]] = []
    for cell in sorted(set(candidates)):
        weight = _intensity_value(intensity, cell)
        if weight <= 0.0:
            continue
        uniform = max(rng.random(), 1e-15)
        keyed.append((-log(uniform) / weight, cell))
    if count > len(keyed):
        raise ValueError("not enough positive-intensity candidates")
    keyed.sort()
    return tuple(cell for _, cell in keyed[:count])


def matern_type_ii(
    candidates: Iterable[Cell],
    distance: Distance,
    minimum_distance: PairSeparation,
    rng: Random,
) -> tuple[Cell, ...]:
    """Graph-distance Matérn-II thinning with deterministic tie handling."""
    points = sorted(set(candidates))
    priorities = {cell: rng.random() for cell in points}

    def separation(left: Cell, right: Cell) -> float:
        value = minimum_distance
        if callable(minimum_distance):
            value = max(minimum_distance(left, right), minimum_distance(right, left))
        if value < 0.0:
            raise ValueError("minimum distance must be non-negative")
        return float(value)

    retained = []
    for cell in points:
        key = priorities[cell], cell
        if all(
            distance(cell, other) >= separation(cell, other)
            or key < (priorities[other], other)
            for other in points
            if other != cell
        ):
            retained.append(cell)
    return tuple(retained)


def heterogeneous_matern_type_ii(
    candidates: Sequence[MarkedPoint],
    distance: Distance,
    minimum_distance: Callable[[MarkedPoint, MarkedPoint], float] | None,
    rng: Random,
) -> tuple[MarkedPoint, ...]:
    """Matérn-II thinning for units with pair-dependent body sizes."""
    points = sorted(candidates, key=lambda point: (point.cell, point.mark))
    priorities = {index: rng.random() for index in range(len(points))}
    retained = []
    for index, point in enumerate(points):
        keep = True
        for other_index, other in enumerate(points):
            if index == other_index:
                continue
            threshold = point.radius + other.radius
            if minimum_distance is not None:
                threshold = max(
                    minimum_distance(point, other),
                    minimum_distance(other, point),
                )
            if threshold < 0.0:
                raise ValueError("minimum distance must be non-negative")
            if distance(point.cell, other.cell) >= threshold:
                continue
            if (priorities[other_index], other.cell, other.mark) < (
                priorities[index],
                point.cell,
                point.mark,
            ):
                keep = False
                break
        if keep:
            retained.append(point)
    return tuple(retained)


def assign_marks(
    cells: Sequence[Cell],
    mark_counts: Mapping[str, int],
    affinities: Mapping[str, Intensity] | None,
    rng: Random,
    radii: Mapping[str, float] | None = None,
) -> tuple[MarkedPoint, ...]:
    """Allocate exact joint mark counts without independent per-cell draws."""
    if any(count < 0 for count in mark_counts.values()):
        raise ValueError("mark counts must be non-negative")
    if sum(mark_counts.values()) != len(cells):
        raise ValueError("mark counts must equal the number of cells")
    available = set(cells)
    result: list[MarkedPoint] = []
    mark_slots = [
        mark for mark, count in sorted(mark_counts.items()) for _ in range(count)
    ]
    rng.shuffle(mark_slots)
    for mark in mark_slots:
        affinity: Intensity = (
            affinities.get(mark, {cell: 1.0 for cell in available})
            if affinities is not None
            else {cell: 1.0 for cell in available}
        )
        selected = weighted_sample_without_replacement(available, affinity, 1, rng)
        for cell in selected:
            result.append(MarkedPoint(cell, mark, float((radii or {}).get(mark, 0.5))))
            available.remove(cell)
    return tuple(sorted(result, key=lambda point: point.cell))


class RandomGeometryStatistics:
    @staticmethod
    def nearest_neighbor_distances(
        points: Iterable[Cell], distance: Distance
    ) -> tuple[float, ...]:
        cells = tuple(dict.fromkeys(points))
        if len(cells) < 2:
            return ()
        return tuple(
            min(distance(cell, other) for other in cells if other != cell)
            for cell in cells
        )

    @classmethod
    def nearest_neighbor_summary(
        cls, points: Iterable[Cell], distance: Distance
    ) -> dict[str, float]:
        values = cls.nearest_neighbor_distances(points, distance)
        if not values:
            return {"minimum": inf, "p10": inf, "mean": inf}
        return {
            "minimum": min(values),
            "p10": _quantile(values, 0.1),
            "mean": fmean(values),
        }

    @staticmethod
    def contact_distribution(
        sample_cells: Iterable[Cell],
        points: Iterable[Cell],
        radii: Sequence[float],
        distance: Distance,
    ) -> dict[float, float]:
        samples = tuple(sample_cells)
        sites = tuple(points)
        if not samples:
            raise ValueError("contact distribution needs sample cells")
        nearest = [
            min((distance(cell, point) for point in sites), default=inf)
            for cell in samples
        ]
        return {
            float(radius): sum(value <= radius for value in nearest) / len(nearest)
            for radius in radii
        }

    @classmethod
    def nearest_neighbor_cdf(
        cls,
        points: Iterable[Cell],
        radii: Sequence[float],
        distance: Distance,
    ) -> dict[float, float]:
        nearest = cls.nearest_neighbor_distances(points, distance)
        if not nearest:
            return {float(radius): 0.0 for radius in radii}
        return {
            float(radius): sum(value <= radius for value in nearest) / len(nearest)
            for radius in radii
        }

    @staticmethod
    def j_function(
        contact: Mapping[float, float], nearest: Mapping[float, float]
    ) -> dict[float, float]:
        if set(contact) != set(nearest):
            raise ValueError("contact and nearest-neighbor radii must match")
        result = {}
        for radius in sorted(contact):
            denominator = 1.0 - contact[radius]
            result[radius] = (
                inf if denominator <= 0.0 else (1.0 - nearest[radius]) / denominator
            )
        return result

    @staticmethod
    def ripley_k(
        points: Iterable[Cell],
        radii: Sequence[float],
        distance: Distance,
        domain_size: int,
    ) -> dict[float, float]:
        cells = tuple(dict.fromkeys(points))
        if domain_size <= 0:
            raise ValueError("domain size must be positive")
        if len(cells) < 2:
            return {float(radius): 0.0 for radius in radii}
        denominator = len(cells) * (len(cells) - 1)
        return {
            float(radius): domain_size
            * sum(
                distance(left, right) <= radius
                for left in cells
                for right in cells
                if left != right
            )
            / denominator
            for radius in radii
        }

    @staticmethod
    def cross_k(
        left_points: Iterable[Cell],
        right_points: Iterable[Cell],
        radii: Sequence[float],
        distance: Distance,
        domain_size: int,
    ) -> dict[float, float]:
        left = tuple(dict.fromkeys(left_points))
        right = tuple(dict.fromkeys(right_points))
        if domain_size <= 0:
            raise ValueError("domain size must be positive")
        if not left or not right:
            return {float(radius): 0.0 for radius in radii}
        return {
            float(radius): domain_size
            * sum(distance(a, b) <= radius for a in left for b in right)
            / (len(left) * len(right))
            for radius in radii
        }

    @staticmethod
    def pair_distance_distribution(
        points: Iterable[Cell],
        bin_upper_bounds: Sequence[float],
        distance: Distance,
    ) -> dict[float, float]:
        """Normalized unordered-pair counts for increasing distance bins."""
        bounds = tuple(float(value) for value in bin_upper_bounds)
        if any(value < 0.0 for value in bounds) or any(
            right <= left for left, right in zip(bounds, bounds[1:])
        ):
            raise ValueError("pair-distance bin bounds must be positive and increasing")
        cells = tuple(dict.fromkeys(points))
        pair_distances = [
            distance(left, right)
            for index, left in enumerate(cells)
            for right in cells[index + 1 :]
        ]
        if not pair_distances:
            return {bound: 0.0 for bound in bounds}
        result: dict[float, float] = {}
        lower = -inf
        for upper in bounds:
            result[upper] = sum(
                lower < value <= upper for value in pair_distances
            ) / len(pair_distances)
            lower = upper
        return result

    @classmethod
    def pair_correlation(
        cls,
        points: Iterable[Cell],
        baseline_samples: Sequence[Iterable[Cell]],
        bin_upper_bounds: Sequence[float],
        distance: Distance,
    ) -> dict[float, float]:
        """Pair correlation relative to same-map Monte Carlo deployments."""
        if not baseline_samples:
            raise ValueError("pair correlation needs Monte Carlo baseline samples")
        observed = cls.pair_distance_distribution(points, bin_upper_bounds, distance)
        baseline = [
            cls.pair_distance_distribution(sample, bin_upper_bounds, distance)
            for sample in baseline_samples
        ]
        result = {}
        for bound, value in observed.items():
            expected = fmean(sample[bound] for sample in baseline)
            if expected == 0.0:
                result[bound] = inf if value > 0.0 else 0.0
            else:
                result[bound] = value / expected
        return result


def coverage_multiplicity(
    domain: Iterable[Cell],
    points: Iterable[Cell],
    influence: LatticeShape | Callable[[Cell], LatticeShape],
) -> dict[Cell, int]:
    domain_set = set(domain)
    counts = {cell: 0 for cell in domain_set}
    for point in points:
        shape = influence(point) if callable(influence) else influence
        for cell in shape.occupied(point):
            if cell in counts:
                counts[cell] += 1
    return counts


def coverage_fraction(counts: Mapping[Cell, int], minimum_layers: int = 1) -> float:
    if minimum_layers < 1:
        raise ValueError("minimum coverage layers must be positive")
    if not counts:
        return 0.0
    return sum(value >= minimum_layers for value in counts.values()) / len(counts)


def safe_corridor_exists(
    graph: LatticeGraph,
    starts: Iterable[Cell],
    goals: Iterable[Cell],
    coverage: Mapping[Cell, int],
    maximum_layers: int = 0,
) -> bool:
    blocked = {cell for cell, layers in coverage.items() if layers > maximum_layers}
    return bool(graph.shortest_path(starts, goals, blocked))


def graph_voronoi(
    graph: LatticeGraph, sites: Iterable[Cell]
) -> dict[Cell, frozenset[Cell]]:
    unique_sites = tuple(sorted(set(sites) & graph.cells))
    if not unique_sites:
        return {}
    distances = {site: graph.shortest_distances(site) for site in unique_sites}
    regions = {site: set() for site in unique_sites}
    for cell in graph.cells:
        owner = min(
            unique_sites,
            key=lambda site: (distances[site].get(cell, inf), site),
        )
        if isfinite(distances[owner].get(cell, inf)):
            regions[owner].add(cell)
    return {site: frozenset(cells) for site, cells in regions.items()}


def delaunay_adjacency(
    graph: LatticeGraph, sites: Iterable[Cell]
) -> frozenset[tuple[Cell, Cell]]:
    regions = graph_voronoi(graph, sites)
    owner_by_cell = {cell: owner for owner, cells in regions.items() for cell in cells}
    edges: set[tuple[Cell, Cell]] = set()
    for cell, owner in owner_by_cell.items():
        for neighbor in graph.neighbors(cell):
            other = owner_by_cell.get(neighbor)
            if other is not None and other != owner:
                edges.add(tuple(sorted((owner, other))))
    return frozenset(edges)


def random_geometric_graph(
    points: Iterable[Cell], radius: float, distance: Distance
) -> frozenset[tuple[Cell, Cell]]:
    if radius < 0.0:
        raise ValueError("connection radius must be non-negative")
    cells = sorted(set(points))
    return frozenset(
        (left, right)
        for index, left in enumerate(cells)
        for right in cells[index + 1 :]
        if distance(left, right) <= radius
    )


def graph_component_count(
    points: Iterable[Cell], edges: Iterable[tuple[Cell, Cell]]
) -> int:
    remaining = set(points)
    adjacency = {point: set() for point in remaining}
    for left, right in edges:
        if left in adjacency and right in adjacency:
            adjacency[left].add(right)
            adjacency[right].add(left)
    count = 0
    while remaining:
        count += 1
        root = min(remaining)
        remaining.remove(root)
        frontier = [root]
        while frontier:
            for neighbor in adjacency[frontier.pop()]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    frontier.append(neighbor)
    return count


def voronoi_area_cv(graph: LatticeGraph, points: Iterable[Cell]) -> float:
    areas = [len(region) for region in graph_voronoi(graph, points).values()]
    if not areas or fmean(areas) == 0.0:
        return 0.0
    mean = fmean(areas)
    return sqrt(fmean((area - mean) ** 2 for area in areas)) / mean


@dataclass(frozen=True)
class DeploymentResult:
    seed: int
    cells: tuple[Cell, ...]
    attempts: int
    candidate_count: int


class DeploymentError(RuntimeError):
    pass


class RandomDeploymentGenerator:
    """Candidate intensity, Matérn-II thinning, then hard-constraint projection."""

    def __init__(self, graph: LatticeGraph, seed: int) -> None:
        self.graph = graph
        self.seed = int(seed)

    def generate(
        self,
        count: int,
        intensity: Intensity,
        minimum_distance: PairSeparation = 1.0,
        forbidden: Iterable[Cell] = (),
        validators: Sequence[LayoutValidator] = (),
        max_attempts: int = 64,
        oversample_factor: int = 4,
    ) -> DeploymentResult:
        if count < 0:
            raise ValueError("deployment count must be non-negative")
        if max_attempts <= 0 or oversample_factor <= 0:
            raise ValueError("attempt and oversampling limits must be positive")
        legal = self.graph.cells - set(forbidden)
        positive = {cell for cell in legal if _intensity_value(intensity, cell) > 0.0}
        if count == 0:
            return DeploymentResult(self.seed, (), 0, len(positive))
        if len(positive) < count:
            raise DeploymentError("fewer legal positive-intensity cells than units")
        rng = Random(self.seed)
        candidate_count = min(len(positive), max(count, count * oversample_factor))
        thinning_failures = 0
        validator_failures = [0] * len(validators)
        for attempt in range(1, max_attempts + 1):
            candidates = weighted_sample_without_replacement(
                positive, intensity, candidate_count, rng
            )
            retained = matern_type_ii(
                candidates, self.graph.distance, minimum_distance, rng
            )
            if len(retained) < count:
                thinning_failures += 1
                continue
            selected = weighted_sample_without_replacement(
                retained, intensity, count, rng
            )
            layout = tuple(sorted(selected))
            rejected_by = [
                index
                for index, validator in enumerate(validators)
                if not validator(layout)
            ]
            if not rejected_by:
                return DeploymentResult(self.seed, layout, attempt, candidate_count)
            for index in rejected_by:
                validator_failures[index] += 1
        failure_details = [f"thinning={thinning_failures}"]
        failure_details.extend(
            f"{getattr(validator, '__name__', f'validator_{index}')}={failures}"
            for index, (validator, failures) in enumerate(
                zip(validators, validator_failures)
            )
            if failures
        )
        raise DeploymentError(
            f"no legal deployment after {max_attempts} attempts; "
            f"failure counts: {', '.join(failure_details)}"
        )


@dataclass(frozen=True)
class DeploymentMetrics:
    minimum_nearest_neighbor: float
    p10_nearest_neighbor: float
    mean_nearest_neighbor: float
    component_count: int
    mean_degree: float
    voronoi_area_cv: float


def deployment_metrics(
    graph: LatticeGraph,
    points: Iterable[Cell],
    connection_radius: float,
) -> DeploymentMetrics:
    cells = tuple(dict.fromkeys(points))
    nearest = RandomGeometryStatistics.nearest_neighbor_summary(cells, graph.distance)
    edges = random_geometric_graph(cells, connection_radius, graph.distance)
    mean_degree = 0.0 if not cells else 2.0 * len(edges) / len(cells)
    return DeploymentMetrics(
        nearest["minimum"],
        nearest["p10"],
        nearest["mean"],
        graph_component_count(cells, edges),
        mean_degree,
        voronoi_area_cv(graph, cells),
    )


def monte_carlo_envelope(
    samples: Sequence[Mapping[str, float]],
    lower_probability: float = 0.05,
    upper_probability: float = 0.95,
) -> dict[str, tuple[float, float, float]]:
    if not samples:
        raise ValueError("Monte Carlo envelope needs samples")
    keys = set(samples[0])
    if any(set(sample) != keys for sample in samples):
        raise ValueError("all Monte Carlo samples must have the same metrics")
    return {
        key: (
            _quantile([sample[key] for sample in samples], lower_probability),
            _quantile([sample[key] for sample in samples], 0.5),
            _quantile([sample[key] for sample in samples], upper_probability),
        )
        for key in sorted(keys)
    }


def log_linear_intensity(
    features: Mapping[Cell, Mapping[str, float]],
    coefficients: Mapping[str, float],
    intercept: float = 0.0,
) -> dict[Cell, float]:
    """Build a positive inhomogeneous intensity without optional ML packages."""
    from math import exp

    return {
        cell: exp(
            intercept
            + sum(
                coefficients.get(name, 0.0) * float(value)
                for name, value in values.items()
            )
        )
        for cell, values in features.items()
    }


def cooldown_reinforcement_intensity(
    base: Mapping[Cell, float],
    pressure_multiplier: float,
    current_time: int,
    last_used: Mapping[Cell, int],
    cooldown: int,
    forbidden: Iterable[Cell] = (),
) -> dict[Cell, float]:
    """Conditional entry intensity with cooldown instead of Hawkes self-excitation."""
    if pressure_multiplier < 0.0 or cooldown < 0 or current_time < 0:
        raise ValueError("reinforcement parameters must be non-negative")
    blocked = set(forbidden)
    return {
        cell: (
            0.0
            if cell in blocked
            or current_time - last_used.get(cell, -cooldown) < cooldown
            else float(value) * pressure_multiplier
        )
        for cell, value in base.items()
    }
