import numpy as np

from rl.p13_metric_persistence_spacetime_math import (
    MultiparameterPersistenceModule,
    PersistentSheafSequence,
    bond_percolation,
    causally_precedes,
    conductance_laplacian,
    effective_resistance,
    estimate_spectral_dimension,
    explicit_graph_diffusion_step,
    finite_gromov_hausdorff_distance,
    first_passage_time,
    fused_gromov_wasserstein_distance,
    gromov_wasserstein_distance,
    minkowski_interval,
    site_percolation,
    time_expanded_shortest_path,
    wasserstein_distance,
)
from rl.p6_structure_math import CellularSheaf


def test_wasserstein_exact_transport():
    result = wasserstein_distance([0.5, 0.5], [0.5, 0.5], [[0, 2], [2, 0]], order=1)
    assert np.isclose(result.distance, 0.0)
    assert np.allclose(result.coupling.sum(axis=1), [0.5, 0.5])


def test_gw_and_fgw_endpoints_on_isometric_two_point_spaces():
    distance = [[0, 1], [1, 0]]
    gw = gromov_wasserstein_distance(distance, distance, [0.5, 0.5], [0.5, 0.5])
    assert gw.distance < 1e-8
    features = [[0, 3], [3, 0]]
    feature_only = fused_gromov_wasserstein_distance(
        distance, distance, [0.5, 0.5], [0.5, 0.5], features, structure_weight=0.0
    )
    assert feature_only.cost < 1e-8


def test_finite_gromov_hausdorff_is_exact_for_scaled_pairs():
    result = finite_gromov_hausdorff_distance([[0, 1], [1, 0]], [[0, 3], [3, 0]])
    assert np.isclose(result.distance, 1.0)
    assert all(any(i == left for i, _ in result.correspondence) for left in range(2))


def test_multiparameter_rank_invariant_and_fibered_path():
    dimensions = {(0, 0): 2, (1, 0): 2, (0, 1): 2, (1, 1): 1}
    projection = np.array([[1.0, 0.0]])
    module = MultiparameterPersistenceModule(
        dimensions,
        {
            ((0, 0), (1, 0)): np.eye(2),
            ((0, 0), (0, 1)): np.eye(2),
            ((1, 0), (1, 1)): projection,
            ((0, 1), (1, 1)): projection,
        },
    )
    assert module.rank_invariant((0, 0), (1, 1)) == 1
    ranks = module.fibered_path_ranks([(0, 0), (1, 0), (1, 1)])
    assert ranks[(0, 2)] == 1


def _constant_graph_sheaf(edge_scale=1.0):
    return CellularSheaf(
        {"a": 1, "b": 1},
        {("a", "b"): 1},
        {
            ("a", ("a", "b")): [[edge_scale]],
            ("b", ("a", "b")): [[edge_scale]],
        },
    )


def test_persistent_sheaf_tracks_global_sections_and_spectra():
    sequence = PersistentSheafSequence(
        [_constant_graph_sheaf(1.0), _constant_graph_sheaf(2.0)],
        [np.eye(2)],
    )
    assert sequence.betti_numbers == (1, 1)
    assert sequence.persistent_betti(0, 1) == 1
    assert np.isclose(sequence.laplacian_spectra()[0][0], 0.0)


def test_minkowski_causality_and_time_expanded_waiting():
    assert np.isclose(minkowski_interval((0, 0, 0), (2, 1, 0)), 3.0)
    assert causally_precedes((0, 0), (1, 1))
    assert not causally_precedes((0, 0), (1, 2))
    path = time_expanded_shortest_path(
        ["a", "b", "c"],
        [("a", "b"), ("b", "c")],
        "a",
        "c",
        4,
        blocked={1: ["b"]},
    )
    assert path == ("a", "a", "b", "c")


def test_diffusion_conserves_mass_and_reduces_range():
    values = np.array([1.0, 0.0, 0.0])
    weights = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    updated = explicit_graph_diffusion_step(values, weights, 0.25)
    assert np.isclose(updated.sum(), values.sum())
    assert np.ptp(updated) < np.ptp(values)


def test_percolation_conductance_resistance_and_first_passage():
    nodes = [0, 1, 2]
    edges = [(0, 1), (1, 2)]
    assert site_percolation(nodes, edges, 1.0, seed=1).clusters == (frozenset(nodes),)
    assert bond_percolation(nodes, edges, 0.0, seed=1).clusters == tuple(
        frozenset([n]) for n in nodes
    )
    conductances = {(0, 1): 1.0, (1, 2): 1.0}
    laplacian = conductance_laplacian(nodes, conductances)
    assert np.allclose(laplacian @ np.ones(3), 0.0)
    assert np.isclose(effective_resistance(nodes, conductances, 0, 2), 2.0)
    assert np.isclose(effective_resistance([0, 1, 2, 3], conductances, 0, 2), 2.0)
    time, path = first_passage_time(nodes, {(0, 1): 2.0, (1, 2): 1.0}, 0, 2)
    assert time == 3.0 and path == (0, 1, 2)
    estimate = estimate_spectral_dimension(laplacian, [0.1, 0.2, 0.4, 0.8])
    assert estimate.dimension > 0.0
    assert np.all(np.diff(estimate.return_probabilities) < 0.0)
