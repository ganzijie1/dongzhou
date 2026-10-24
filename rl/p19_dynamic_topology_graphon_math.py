"""P19 higher persistence, dynamic topology, SBM, and graphon models."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Hashable, Sequence

import numpy as np
from scipy.linalg import expm
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans


Simplex = tuple[Hashable, ...]


def _canonical(simplex: Sequence[Hashable]) -> Simplex:
    values = tuple(sorted(set(simplex), key=repr))
    if not values:
        raise ValueError("a simplex cannot be empty")
    return values


def _complex(simplices: Sequence[Sequence[Hashable]]) -> frozenset[Simplex]:
    result = frozenset(_canonical(simplex) for simplex in simplices)
    for simplex in result:
        for size in range(1, len(simplex)):
            for face in combinations(simplex, size):
                if face not in result:
                    raise ValueError("simplicial complex is not closed under faces")
    return result


def _gf2_rref(matrix: np.ndarray) -> tuple[np.ndarray, tuple[int, ...]]:
    value = np.asarray(matrix, dtype=np.uint8).copy() % 2
    rows, columns = value.shape
    pivots = []
    pivot_row = 0
    for column in range(columns):
        candidates = np.flatnonzero(value[pivot_row:, column])
        if candidates.size == 0:
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            value[[pivot_row, selected]] = value[[selected, pivot_row]]
        for row in range(rows):
            if row != pivot_row and value[row, column]:
                value[row] ^= value[pivot_row]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    return value, tuple(pivots)


def _gf2_rank(matrix: np.ndarray) -> int:
    if matrix.size == 0:
        return 0
    return len(_gf2_rref(matrix)[1])


def _gf2_null_space(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.uint8) % 2
    columns = value.shape[1]
    reduced, pivots = _gf2_rref(value)
    free = [column for column in range(columns) if column not in pivots]
    basis = np.zeros((columns, len(free)), dtype=np.uint8)
    for basis_index, free_column in enumerate(free):
        basis[free_column, basis_index] = 1
        for row, pivot in enumerate(pivots):
            basis[pivot, basis_index] = reduced[row, free_column]
    return basis


def _gf2_column_basis(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.uint8) % 2
    if value.shape[1] == 0:
        return np.zeros((value.shape[0], 0), dtype=np.uint8)
    selected = []
    rank = 0
    for column in range(value.shape[1]):
        candidate = value[:, selected + [column]]
        candidate_rank = _gf2_rank(candidate)
        if candidate_rank > rank:
            selected.append(column)
            rank = candidate_rank
    return value[:, selected]


def _gf2_solve(matrix: np.ndarray, right_hand_side: np.ndarray) -> np.ndarray:
    coefficient = np.asarray(matrix, dtype=np.uint8) % 2
    rhs = np.asarray(right_hand_side, dtype=np.uint8) % 2
    if rhs.ndim == 1:
        rhs = rhs[:, None]
    augmented = np.hstack((coefficient, rhs))
    reduced, pivots_all = _gf2_rref(augmented)
    variable_count = coefficient.shape[1]
    pivots = [pivot for pivot in pivots_all if pivot < variable_count]
    for row in range(reduced.shape[0]):
        if not np.any(reduced[row, :variable_count]) and np.any(
            reduced[row, variable_count:]
        ):
            raise ValueError("GF(2) linear system is inconsistent")
    solution = np.zeros((variable_count, rhs.shape[1]), dtype=np.uint8)
    for row, pivot in enumerate(pivots):
        solution[pivot] = reduced[row, variable_count:]
    return solution


def _simplices_by_dimension(
    complex_value: frozenset[Simplex], dimension: int
) -> tuple[Simplex, ...]:
    return tuple(
        sorted(
            (simplex for simplex in complex_value if len(simplex) == dimension + 1),
            key=lambda simplex: tuple(map(repr, simplex)),
        )
    )


def _boundary_matrix(
    complex_value: frozenset[Simplex], dimension: int
) -> np.ndarray:
    columns = _simplices_by_dimension(complex_value, dimension)
    if dimension == 0:
        return np.zeros((0, len(columns)), dtype=np.uint8)
    rows = _simplices_by_dimension(complex_value, dimension - 1)
    row_index = {simplex: index for index, simplex in enumerate(rows)}
    matrix = np.zeros((len(rows), len(columns)), dtype=np.uint8)
    for column, simplex in enumerate(columns):
        for omitted in range(len(simplex)):
            face = simplex[:omitted] + simplex[omitted + 1 :]
            matrix[row_index[face], column] = 1
    return matrix


def _oriented_boundary_matrix(
    complex_value: frozenset[Simplex], dimension: int
) -> np.ndarray:
    columns = _simplices_by_dimension(complex_value, dimension)
    if dimension == 0:
        return np.zeros((0, len(columns)), dtype=np.float64)
    rows = _simplices_by_dimension(complex_value, dimension - 1)
    row_index = {simplex: index for index, simplex in enumerate(rows)}
    matrix = np.zeros((len(rows), len(columns)), dtype=np.float64)
    for column, simplex in enumerate(columns):
        for omitted in range(len(simplex)):
            face = simplex[:omitted] + simplex[omitted + 1 :]
            matrix[row_index[face], column] = -1.0 if omitted % 2 else 1.0
    return matrix


@dataclass(frozen=True)
class PersistenceInterval:
    dimension: int
    birth: float
    death: float | None
    birth_simplex: Simplex | None = None
    death_simplex: Simplex | None = None


def persistent_homology(
    filtered_simplices: Sequence[tuple[Sequence[Hashable], float]],
    *,
    maximum_homology_dimension: int = 2,
) -> tuple[PersistenceInterval, ...]:
    """Compute H0/H1/H2 persistence by standard GF(2) column reduction."""

    if not filtered_simplices or maximum_homology_dimension < 0:
        raise ValueError("persistent homology needs a non-empty filtration")
    filtration = {}
    for raw_simplex, raw_time in filtered_simplices:
        simplex = _canonical(raw_simplex)
        time = float(raw_time)
        if not isfinite(time):
            raise ValueError("filtration values must be finite")
        if simplex in filtration and not np.isclose(filtration[simplex], time):
            raise ValueError("a simplex has conflicting filtration values")
        filtration[simplex] = time
    for simplex, time in filtration.items():
        for size in range(1, len(simplex)):
            for face in combinations(simplex, size):
                if face not in filtration or filtration[face] > time:
                    raise ValueError("filtration is not face-closed and monotone")
    ordered = tuple(
        sorted(
            filtration,
            key=lambda simplex: (
                filtration[simplex],
                len(simplex),
                tuple(map(repr, simplex)),
            ),
        )
    )
    index = {simplex: position for position, simplex in enumerate(ordered)}
    reduced_columns: list[int] = []
    pivot_owner: dict[int, int] = {}
    zero_columns = []
    paired_births = set()
    intervals = []
    for column_index, simplex in enumerate(ordered):
        column = 0
        if len(simplex) > 1:
            for omitted in range(len(simplex)):
                face = simplex[:omitted] + simplex[omitted + 1 :]
                column ^= 1 << index[face]
        while column:
            pivot = column.bit_length() - 1
            if pivot not in pivot_owner:
                break
            column ^= reduced_columns[pivot_owner[pivot]]
        reduced_columns.append(column)
        if column == 0:
            zero_columns.append(column_index)
            continue
        pivot = column.bit_length() - 1
        pivot_owner[pivot] = column_index
        paired_births.add(pivot)
        dimension = len(ordered[pivot]) - 1
        if dimension <= maximum_homology_dimension:
            intervals.append(
                PersistenceInterval(
                    dimension,
                    filtration[ordered[pivot]],
                    filtration[simplex],
                    ordered[pivot],
                    simplex,
                )
            )
    for birth in zero_columns:
        if birth in paired_births:
            continue
        dimension = len(ordered[birth]) - 1
        if dimension <= maximum_homology_dimension:
            intervals.append(
                PersistenceInterval(
                    dimension,
                    filtration[ordered[birth]],
                    None,
                    ordered[birth],
                    None,
                )
            )
    return tuple(
        sorted(
            intervals,
            key=lambda value: (
                value.dimension,
                value.birth,
                np.inf if value.death is None else value.death,
                repr(value.birth_simplex),
            ),
        )
    )


@dataclass(frozen=True)
class _HomologyData:
    chains: tuple[Simplex, ...]
    boundaries: np.ndarray
    homology: np.ndarray


def _homology_data(
    complex_value: frozenset[Simplex], dimension: int
) -> _HomologyData:
    chains = _simplices_by_dimension(complex_value, dimension)
    boundary = _boundary_matrix(complex_value, dimension)
    cycles = _gf2_null_space(boundary)
    next_boundary = _boundary_matrix(complex_value, dimension + 1)
    boundary_basis = _gf2_column_basis(next_boundary)
    combined = boundary_basis.copy()
    rank = _gf2_rank(combined)
    homology_columns = []
    for column in range(cycles.shape[1]):
        candidate_vector = cycles[:, column : column + 1]
        candidate = np.hstack((combined, candidate_vector))
        candidate_rank = _gf2_rank(candidate)
        if candidate_rank > rank:
            homology_columns.append(candidate_vector[:, 0])
            combined = candidate
            rank = candidate_rank
    homology = (
        np.column_stack(homology_columns).astype(np.uint8)
        if homology_columns
        else np.zeros((len(chains), 0), dtype=np.uint8)
    )
    return _HomologyData(chains, boundary_basis, homology)


def _induced_homology_map(
    source: _HomologyData, target: _HomologyData
) -> np.ndarray:
    source_dimension = source.homology.shape[1]
    target_dimension = target.homology.shape[1]
    result = np.zeros((target_dimension, source_dimension), dtype=np.uint8)
    if source_dimension == 0:
        return result
    target_index = {simplex: index for index, simplex in enumerate(target.chains)}
    embedding = np.zeros((len(target.chains), len(source.chains)), dtype=np.uint8)
    for source_index, simplex in enumerate(source.chains):
        if simplex not in target_index:
            raise ValueError("homology map requires a simplicial inclusion")
        embedding[target_index[simplex], source_index] = 1
    decomposition = np.hstack((target.boundaries, target.homology))
    for column in range(source_dimension):
        image = embedding @ source.homology[:, column]
        coordinates = _gf2_solve(decomposition, image)[:, 0]
        result[:, column] = coordinates[target.boundaries.shape[1] :]
    return result


def _generalized_rank(
    dimensions: Sequence[int],
    arrows: Sequence[tuple[str, np.ndarray]],
    start: int,
    end: int,
) -> int:
    local_dimensions = tuple(dimensions[start : end + 1])
    offsets = np.cumsum((0, *local_dimensions))
    total = int(offsets[-1])
    if start == end:
        return local_dimensions[0]
    constraint_rows = []
    relation_columns = []
    for local_edge, (direction, matrix) in enumerate(arrows[start:end]):
        left_dimension = local_dimensions[local_edge]
        right_dimension = local_dimensions[local_edge + 1]
        left_slice = slice(offsets[local_edge], offsets[local_edge + 1])
        right_slice = slice(offsets[local_edge + 1], offsets[local_edge + 2])
        if direction == "forward":
            constraint = np.zeros((right_dimension, total), dtype=np.uint8)
            constraint[:, left_slice] = matrix
            constraint[:, right_slice] = np.eye(right_dimension, dtype=np.uint8)
            relation = np.zeros((total, left_dimension), dtype=np.uint8)
            relation[left_slice, :] = np.eye(left_dimension, dtype=np.uint8)
            relation[right_slice, :] = matrix
        else:
            constraint = np.zeros((left_dimension, total), dtype=np.uint8)
            constraint[:, left_slice] = np.eye(left_dimension, dtype=np.uint8)
            constraint[:, right_slice] = matrix
            relation = np.zeros((total, right_dimension), dtype=np.uint8)
            relation[left_slice, :] = matrix
            relation[right_slice, :] = np.eye(right_dimension, dtype=np.uint8)
        constraint_rows.append(constraint)
        relation_columns.append(relation)
    constraints = np.vstack(constraint_rows)
    relations = np.hstack(relation_columns)
    limit_basis = _gf2_null_space(constraints)
    canonical = np.zeros((total, limit_basis.shape[1]), dtype=np.uint8)
    canonical[: local_dimensions[0]] = limit_basis[: local_dimensions[0]]
    return _gf2_rank(np.hstack((relations, canonical))) - _gf2_rank(relations)


@dataclass(frozen=True)
class ZigzagPersistenceResult:
    dimension: int
    intervals: tuple[tuple[int, int, int], ...]
    betti_numbers: tuple[int, ...]
    directions: tuple[str, ...]
    generalized_ranks: np.ndarray


def zigzag_persistence(
    complex_sequence: Sequence[Sequence[Sequence[Hashable]]],
    *,
    homology_dimension: int,
) -> ZigzagPersistenceResult:
    """Exact finite H0/H1/H2 zigzag intervals via homology quiver ranks."""

    if not complex_sequence or not 0 <= homology_dimension <= 2:
        raise ValueError("zigzag persistence supports non-empty H0/H1/H2 sequences")
    complexes = tuple(_complex(value) for value in complex_sequence)
    homology = tuple(
        _homology_data(value, homology_dimension) for value in complexes
    )
    dimensions = tuple(value.homology.shape[1] for value in homology)
    arrows = []
    directions = []
    for index in range(len(complexes) - 1):
        if complexes[index] <= complexes[index + 1]:
            directions.append("forward")
            arrows.append(
                (
                    "forward",
                    _induced_homology_map(homology[index], homology[index + 1]),
                )
            )
        elif complexes[index + 1] <= complexes[index]:
            directions.append("backward")
            arrows.append(
                (
                    "backward",
                    _induced_homology_map(homology[index + 1], homology[index]),
                )
            )
        else:
            raise ValueError("adjacent zigzag complexes must be related by inclusion")
    count = len(complexes)
    ranks = np.zeros((count, count), dtype=np.int64)
    for start in range(count):
        for end in range(start, count):
            ranks[start, end] = _generalized_rank(
                dimensions, arrows, start, end
            )
    intervals = []
    for birth in range(count):
        for death in range(birth, count):
            multiplicity = int(ranks[birth, death])
            if birth > 0:
                multiplicity -= int(ranks[birth - 1, death])
            if death + 1 < count:
                multiplicity -= int(ranks[birth, death + 1])
            if birth > 0 and death + 1 < count:
                multiplicity += int(ranks[birth - 1, death + 1])
            if multiplicity < 0:
                raise RuntimeError("zigzag generalized ranks produced negative multiplicity")
            if multiplicity:
                intervals.append((birth, death, multiplicity))
    return ZigzagPersistenceResult(
        homology_dimension,
        tuple(intervals),
        dimensions,
        tuple(directions),
        ranks,
    )


@dataclass(frozen=True)
class VineyardMatchResult:
    matches: tuple[tuple[int, int, float], ...]
    unmatched_previous: tuple[int, ...]
    unmatched_current: tuple[int, ...]


def match_persistence_diagrams(
    previous: Sequence[Sequence[float]],
    current: Sequence[Sequence[float]],
    *,
    maximum_distance: float = np.inf,
) -> VineyardMatchResult:
    """Match consecutive finite persistence diagrams using L-infinity cost."""

    left = np.asarray(previous, dtype=np.float64)
    right = np.asarray(current, dtype=np.float64)
    if left.size == 0:
        left = np.empty((0, 2))
    if right.size == 0:
        right = np.empty((0, 2))
    if (
        left.ndim != 2
        or left.shape[1] != 2
        or right.ndim != 2
        or right.shape[1] != 2
        or np.any(~np.isfinite(left))
        or np.any(~np.isfinite(right))
        or maximum_distance < 0.0
    ):
        raise ValueError("vineyard diagram inputs are invalid")
    if not len(left) or not len(right):
        return VineyardMatchResult(
            (), tuple(range(len(left))), tuple(range(len(right)))
        )
    cost = np.max(np.abs(left[:, None, :] - right[None, :, :]), axis=2)
    left_indices, right_indices = linear_sum_assignment(cost)
    matches = []
    matched_left = set()
    matched_right = set()
    for left_index, right_index in zip(left_indices, right_indices, strict=True):
        distance = float(cost[left_index, right_index])
        if distance <= maximum_distance:
            matches.append((int(left_index), int(right_index), distance))
            matched_left.add(int(left_index))
            matched_right.add(int(right_index))
    return VineyardMatchResult(
        tuple(matches),
        tuple(index for index in range(len(left)) if index not in matched_left),
        tuple(index for index in range(len(right)) if index not in matched_right),
    )


@dataclass(frozen=True)
class MapperResult:
    node_members: tuple[tuple[int, ...], ...]
    edges: tuple[tuple[int, int], ...]
    cover_intervals: tuple[tuple[float, float], ...]


def mapper_graph(
    points: Sequence[Sequence[float]],
    filter_values: Sequence[float],
    *,
    interval_count: int,
    overlap: float = 0.25,
    cluster_radius: float = 1.0,
) -> MapperResult:
    """Construct a one-dimensional-cover Mapper graph with radius components."""

    data = np.asarray(points, dtype=np.float64)
    filter_array = np.asarray(filter_values, dtype=np.float64)
    if (
        data.ndim != 2
        or data.shape[0] == 0
        or filter_array.shape != (data.shape[0],)
        or np.any(~np.isfinite(data))
        or np.any(~np.isfinite(filter_array))
        or interval_count <= 0
        or not 0.0 <= overlap < 1.0
        or cluster_radius <= 0.0
    ):
        raise ValueError("Mapper inputs are invalid")
    minimum = float(filter_array.min())
    maximum = float(filter_array.max())
    if np.isclose(minimum, maximum):
        intervals = [(minimum, maximum)]
    else:
        width = (maximum - minimum) / (
            interval_count - (interval_count - 1) * overlap
        )
        step = width * (1.0 - overlap)
        intervals = [
            (minimum + index * step, minimum + index * step + width)
            for index in range(interval_count)
        ]
    nodes = []
    for interval_index, (lower, upper) in enumerate(intervals):
        if interval_index + 1 == len(intervals):
            members = np.flatnonzero(
                (filter_array >= lower) & (filter_array <= upper + 1e-12)
            )
        else:
            members = np.flatnonzero(
                (filter_array >= lower) & (filter_array < upper)
            )
        remaining = set(int(value) for value in members)
        while remaining:
            seed = min(remaining)
            component = {seed}
            frontier = [seed]
            remaining.remove(seed)
            while frontier:
                current = frontier.pop()
                neighbors = [
                    candidate
                    for candidate in remaining
                    if np.linalg.norm(data[current] - data[candidate])
                    <= cluster_radius
                ]
                for neighbor in neighbors:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
            nodes.append(tuple(sorted(component)))
    edges = []
    member_sets = [set(node) for node in nodes]
    for left in range(len(nodes)):
        for right in range(left + 1, len(nodes)):
            if member_sets[left] & member_sets[right]:
                edges.append((left, right))
    return MapperResult(tuple(nodes), tuple(edges), tuple(intervals))


@dataclass(frozen=True)
class DynamicSBMResult:
    labels: np.ndarray
    block_probabilities: np.ndarray
    transition_matrix: np.ndarray
    log_likelihood: float


def estimate_dynamic_sbm_unknown_labels(
    adjacency_sequence: Sequence,
    community_count: int,
    *,
    random_state: int = 0,
) -> DynamicSBMResult:
    """Spectral per-snapshot dynamic SBM estimate with temporal label alignment."""

    adjacency = np.asarray(adjacency_sequence, dtype=np.float64)
    if (
        adjacency.ndim != 3
        or adjacency.shape[0] == 0
        or adjacency.shape[1] != adjacency.shape[2]
        or community_count <= 0
        or community_count > adjacency.shape[1]
        or np.any(~np.isfinite(adjacency))
        or np.any(adjacency < 0.0)
        or not np.allclose(adjacency, adjacency.transpose(0, 2, 1))
        or not np.allclose(np.diagonal(adjacency, axis1=1, axis2=2), 0.0)
    ):
        raise ValueError("dynamic SBM adjacency input is invalid")
    times, nodes, _ = adjacency.shape
    labels = np.zeros((times, nodes), dtype=np.int64)
    for time in range(times):
        eigenvalues, eigenvectors = np.linalg.eigh(adjacency[time])
        embedding = eigenvectors[:, np.argsort(np.abs(eigenvalues))[-community_count:]]
        norm = np.linalg.norm(embedding, axis=1, keepdims=True)
        embedding = np.divide(
            embedding, norm, out=np.zeros_like(embedding), where=norm > 1e-12
        )
        current = KMeans(
            n_clusters=community_count, n_init=10, random_state=random_state
        ).fit_predict(embedding)
        if time > 0:
            overlap_matrix = np.zeros((community_count, community_count))
            for previous_label in range(community_count):
                for current_label in range(community_count):
                    overlap_matrix[previous_label, current_label] = np.count_nonzero(
                        (labels[time - 1] == previous_label)
                        & (current == current_label)
                    )
            old, new = linear_sum_assignment(-overlap_matrix)
            relabel = {int(new_value): int(old_value) for old_value, new_value in zip(old, new, strict=True)}
            current = np.array([relabel[int(value)] for value in current])
        labels[time] = current
    block = np.zeros((times, community_count, community_count))
    log_likelihood = 0.0
    for time in range(times):
        for left_label in range(community_count):
            left_nodes = np.flatnonzero(labels[time] == left_label)
            for right_label in range(community_count):
                right_nodes = np.flatnonzero(labels[time] == right_label)
                pairs = [
                    (left, right)
                    for left in left_nodes
                    for right in right_nodes
                    if left < right
                    or (left_label != right_label and left != right)
                ]
                if left_label != right_label:
                    # Count an undirected cross-block edge only once.
                    pairs = [pair for pair in pairs if pair[0] < pair[1]]
                if pairs:
                    probability = float(
                        np.mean([adjacency[time, left, right] for left, right in pairs])
                    )
                else:
                    probability = 0.0
                block[time, left_label, right_label] = probability
        block[time] = 0.5 * (block[time] + block[time].T)
        for left in range(nodes):
            for right in range(left + 1, nodes):
                probability = np.clip(
                    block[time, labels[time, left], labels[time, right]],
                    1e-12,
                    1.0 - 1e-12,
                )
                edge = adjacency[time, left, right]
                log_likelihood += edge * np.log(probability) + (1.0 - edge) * np.log(
                    1.0 - probability
                )
    transition_counts = np.ones((community_count, community_count)) * 1e-9
    for time in range(1, times):
        for previous, current in zip(labels[time - 1], labels[time], strict=True):
            transition_counts[previous, current] += 1.0
    transition = transition_counts / transition_counts.sum(axis=1, keepdims=True)
    return DynamicSBMResult(labels, block, transition, float(log_likelihood))


@dataclass(frozen=True)
class GraphonEstimate:
    ordering: np.ndarray
    latent_positions: np.ndarray
    block_graphon: np.ndarray
    fitted_probability: np.ndarray


def histogram_graphon_estimate(
    adjacency: Sequence[Sequence[float]],
    bin_count: int,
    *,
    ordering_scores: Sequence[float] | None = None,
) -> GraphonEstimate:
    """Estimate a step graphon after degree- or externally supplied ordering."""

    matrix = np.asarray(adjacency, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or matrix.shape[0] == 0
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix, matrix.T)
        or bin_count <= 0
        or bin_count > matrix.shape[0]
    ):
        raise ValueError("graphon adjacency input is invalid")
    if ordering_scores is None:
        scores = matrix.sum(axis=1)
    else:
        scores = np.asarray(ordering_scores, dtype=np.float64)
        if scores.shape != (matrix.shape[0],) or np.any(~np.isfinite(scores)):
            raise ValueError("graphon ordering scores are invalid")
    ordering = np.argsort(scores, kind="stable")
    bins = np.array_split(ordering, bin_count)
    graphon = np.zeros((bin_count, bin_count))
    for left, left_nodes in enumerate(bins):
        for right, right_nodes in enumerate(bins):
            entries = matrix[np.ix_(left_nodes, right_nodes)]
            if left == right:
                mask = ~np.eye(len(left_nodes), dtype=bool)
                values = entries[mask]
            else:
                values = entries.ravel()
            graphon[left, right] = float(values.mean()) if values.size else 0.0
    fitted = np.zeros_like(matrix)
    for left, left_nodes in enumerate(bins):
        for right, right_nodes in enumerate(bins):
            fitted[np.ix_(left_nodes, right_nodes)] = graphon[left, right]
    positions = np.empty(matrix.shape[0])
    positions[ordering] = (np.arange(matrix.shape[0]) + 0.5) / matrix.shape[0]
    return GraphonEstimate(ordering, positions, graphon, fitted)


@dataclass(frozen=True)
class GraphonMeanFieldResult:
    action_probabilities: np.ndarray
    aggregate_field: np.ndarray
    iterations: int
    converged: bool
    residual: float


def graphon_logit_mean_field(
    graphon: Sequence[Sequence[float]],
    type_weights: Sequence[float],
    base_advantage: Sequence[float],
    *,
    interaction: float,
    precision: float = 1.0,
    damping: float = 0.5,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> GraphonMeanFieldResult:
    """Solve a binary-action graphon Logit mean-field fixed point."""

    kernel = np.asarray(graphon, dtype=np.float64)
    weights = np.asarray(type_weights, dtype=np.float64)
    base = np.asarray(base_advantage, dtype=np.float64)
    if (
        kernel.ndim != 2
        or kernel.shape[0] != kernel.shape[1]
        or weights.shape != (kernel.shape[0],)
        or base.shape != weights.shape
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(weights))
        or np.any(~np.isfinite(base))
        or np.any(kernel < 0.0)
        or np.any(weights < 0.0)
        or not np.isclose(weights.sum(), 1.0)
        or not isfinite(interaction)
        or not isfinite(precision)
        or precision <= 0.0
        or not 0.0 < damping <= 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("graphon mean-field inputs are invalid")
    probabilities = np.full(weights.size, 0.5)
    residual = np.inf
    for iteration in range(1, max_iterations + 1):
        field = kernel @ (weights * probabilities)
        logits = np.clip(precision * (base + interaction * field), -700.0, 700.0)
        response = 1.0 / (1.0 + np.exp(-logits))
        updated = (1.0 - damping) * probabilities + damping * response
        residual = float(np.max(np.abs(updated - probabilities)))
        probabilities = updated
        if residual <= tolerance:
            return GraphonMeanFieldResult(
                probabilities, kernel @ (weights * probabilities), iteration, True, residual
            )
    return GraphonMeanFieldResult(
        probabilities,
        kernel @ (weights * probabilities),
        max_iterations,
        False,
        residual,
    )


def hodge_laplacian(
    simplices: Sequence[Sequence[Hashable]], dimension: int
) -> np.ndarray:
    """Combinatorial Hodge Laplacian on k-simplices for k=0,1,2."""

    if not 0 <= dimension <= 2:
        raise ValueError("Hodge Laplacian supports dimensions zero through two")
    complex_value = _complex(simplices)
    lower_boundary = _oriented_boundary_matrix(complex_value, dimension)
    upper_boundary = _oriented_boundary_matrix(complex_value, dimension + 1)
    size = len(_simplices_by_dimension(complex_value, dimension))
    lower = lower_boundary.T @ lower_boundary if dimension > 0 else np.zeros((size, size))
    upper = upper_boundary @ upper_boundary.T
    return np.asarray(lower + upper, dtype=np.float64)


def simplicial_heat_diffusion(
    simplices: Sequence[Sequence[Hashable]],
    dimension: int,
    signal: Sequence[float],
    *,
    time: float,
) -> np.ndarray:
    """Diffuse a k-cochain with ``exp(-time * L_k)``."""

    laplacian = hodge_laplacian(simplices, dimension)
    values = np.asarray(signal, dtype=np.float64)
    if (
        values.shape != (laplacian.shape[0],)
        or np.any(~np.isfinite(values))
        or not isfinite(time)
        or time < 0.0
    ):
        raise ValueError("simplicial heat-diffusion inputs are invalid")
    return expm(-time * laplacian) @ values
