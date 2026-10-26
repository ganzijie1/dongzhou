import numpy as np

from rl.p54_spatial_point_process_math import (
    audit_dpp_marginal_kernel,
    contact_distances,
    dpp_pair_inclusion_probability,
    l_ensemble_subset_probability,
    nearest_neighbor_distances,
    poisson_nearest_distance_cdf,
    poisson_void_probability,
    thomas_pair_correlation,
)


def test_poisson_void_and_nearest_distance_are_consistent():
    assert np.isclose(poisson_void_probability(2.0, 3.0), np.exp(-6.0))
    assert np.isclose(poisson_nearest_distance_cdf(1.0, 1.0), 1.0 - np.exp(-np.pi))


def test_finite_dpp_kernel_and_l_ensemble_probabilities():
    kernel = np.diag([0.5, 0.5])
    audit = audit_dpp_marginal_kernel(kernel)
    assert audit.valid_marginal_kernel
    assert np.isclose(audit.expected_cardinality, 1.0)
    assert np.isclose(dpp_pair_inclusion_probability(kernel, 0, 1), 0.25)
    assert np.isclose(l_ensemble_subset_probability(np.eye(2), []), 0.25)
    assert np.isclose(l_ensemble_subset_probability(np.eye(2), [0]), 0.25)


def test_contact_and_nearest_neighbor_distances_have_distinct_origins():
    points = [[0.0, 0.0], [3.0, 0.0], [0.0, 4.0]]
    assert np.allclose(nearest_neighbor_distances(points), [3.0, 3.0, 4.0])
    assert np.allclose(contact_distances(points, [[1.0, 0.0], [10.0, 0.0]]), [1.0, 7.0])


def test_thomas_pair_correlation_exhibits_clustering():
    values = thomas_pair_correlation([0.0, 100.0], 0.5, 1.0)
    assert values[0] > 1.0
    assert np.isclose(values[1], 1.0)
