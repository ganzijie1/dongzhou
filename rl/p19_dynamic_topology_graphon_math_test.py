from itertools import combinations

import numpy as np

from rl.p19_dynamic_topology_graphon_math import (
    estimate_dynamic_sbm_unknown_labels,
    graphon_logit_mean_field,
    histogram_graphon_estimate,
    hodge_laplacian,
    mapper_graph,
    match_persistence_diagrams,
    persistent_homology,
    simplicial_heat_diffusion,
    zigzag_persistence,
)


def _triangle_boundary():
    return [(0,), (1,), (2,), (0, 1), (1, 2), (0, 2)]


def _tetrahedron_boundary():
    vertices = [(index,) for index in range(4)]
    edges = list(combinations(range(4), 2))
    triangles = list(combinations(range(4), 3))
    return vertices + edges + triangles


def test_persistent_homology_returns_h1_and_h2_intervals():
    triangle_filtration = [
        *((simplex, 0.0) for simplex in [(0,), (1,), (2,)]),
        *((simplex, 1.0) for simplex in [(0, 1), (1, 2), (0, 2)]),
        ((0, 1, 2), 2.0),
    ]
    triangle_intervals = persistent_homology(triangle_filtration)
    assert any(
        value.dimension == 1 and value.birth == 1.0 and value.death == 2.0
        for value in triangle_intervals
    )
    tetra_filtration = []
    for simplex in _tetrahedron_boundary():
        tetra_filtration.append((simplex, float(len(simplex) - 1)))
    tetra_filtration.append(((0, 1, 2, 3), 3.0))
    tetra_intervals = persistent_homology(tetra_filtration)
    assert any(
        value.dimension == 2 and value.birth == 2.0 and value.death == 3.0
        for value in tetra_intervals
    )


def test_exact_zigzag_intervals_capture_temporary_h1_and_h2():
    path = [(0,), (1,), (2,), (0, 1), (1, 2)]
    cycle = _triangle_boundary()
    h1 = zigzag_persistence([path, cycle, path], homology_dimension=1)
    assert h1.betti_numbers == (0, 1, 0)
    assert h1.directions == ("forward", "backward")
    assert h1.intervals == ((1, 1, 1),)

    boundary = _tetrahedron_boundary()
    punctured = boundary[:-1]
    h2 = zigzag_persistence([punctured, boundary, punctured], homology_dimension=2)
    assert h2.betti_numbers == (0, 1, 0)
    assert h2.intervals == ((1, 1, 1),)


def test_vineyard_matching_tracks_nearby_features_and_unmatched_points():
    result = match_persistence_diagrams(
        [[0.0, 2.0], [1.0, 4.0]],
        [[0.1, 2.1], [8.0, 9.0]],
        maximum_distance=0.5,
    )
    assert result.matches[0][:2] == (0, 0)
    assert np.isclose(result.matches[0][2], 0.1)
    assert result.unmatched_previous == (1,)
    assert result.unmatched_current == (1,)


def test_mapper_builds_overlap_edges_between_local_components():
    points = [[0.0], [0.4], [0.8], [1.2], [1.6]]
    result = mapper_graph(
        points,
        [0.0, 0.4, 0.8, 1.2, 1.6],
        interval_count=2,
        overlap=0.5,
        cluster_radius=0.5,
    )
    assert len(result.node_members) == 2
    assert result.edges == ((0, 1),)


def test_unknown_label_dynamic_sbm_recovers_two_persistent_blocks():
    adjacency = np.zeros((2, 6, 6))
    for time in range(2):
        for group in ((0, 1, 2), (3, 4, 5)):
            for left, right in combinations(group, 2):
                adjacency[time, left, right] = 1.0
                adjacency[time, right, left] = 1.0
    result = estimate_dynamic_sbm_unknown_labels(adjacency, 2)
    assert len(set(result.labels[0, :3])) == 1
    assert len(set(result.labels[0, 3:])) == 1
    assert result.labels[0, 0] != result.labels[0, 3]
    assert np.array_equal(result.labels[0], result.labels[1])
    assert np.all(np.diag(result.transition_matrix) > 0.99)


def test_graphon_histogram_and_logit_mean_field_fixed_point():
    adjacency = np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
        ]
    )
    estimate = histogram_graphon_estimate(
        adjacency, 2, ordering_scores=[0.0, 0.1, 1.0, 1.1]
    )
    assert np.allclose(estimate.block_graphon, [[1.0, 0.0], [0.0, 1.0]])
    result = graphon_logit_mean_field(
        estimate.block_graphon,
        [0.5, 0.5],
        [0.0, 0.0],
        interaction=1.0,
    )
    assert result.converged
    assert np.allclose(result.action_probabilities[0], result.action_probabilities[1])
    assert np.all((result.action_probabilities > 0.5) & (result.action_probabilities < 1.0))


def test_hodge_laplacian_and_simplicial_heat_are_psd_and_contracting():
    complex_value = _triangle_boundary()
    laplacian = hodge_laplacian(complex_value, 1)
    assert np.allclose(laplacian, laplacian.T)
    assert np.min(np.linalg.eigvalsh(laplacian)) >= -1e-10
    signal = np.array([1.0, -1.0, 0.5])
    diffused = simplicial_heat_diffusion(
        complex_value, 1, signal, time=0.5
    )
    assert np.linalg.norm(diffused) <= np.linalg.norm(signal) + 1e-10
