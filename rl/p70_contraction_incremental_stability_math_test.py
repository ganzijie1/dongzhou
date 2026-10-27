import numpy as np

from rl.p70_contraction_incremental_stability_math import (
    contraction_residual,
    discrete_contraction_factor,
    geodesic_energy,
    geodesic_feedback,
    incremental_error_bound,
    maximum_contraction_rate,
    metric_bounds,
)


def test_continuous_and_discrete_contraction_rates():
    a = -2.0 * np.eye(2)
    assert np.allclose(contraction_residual(a, np.eye(2), rate=1.0), -2.0 * np.eye(2))
    assert np.isclose(maximum_contraction_rate(a, np.eye(2)), 2.0)
    assert np.isclose(discrete_contraction_factor(0.5 * np.eye(2), np.eye(2), np.eye(2)), 0.5)


def test_metric_error_bound_and_geodesic_feedback():
    assert metric_bounds([[2.0, 0.0], [0.0, 1.0]]) == (1.0, 2.0, 2.0)
    assert np.allclose(incremental_error_bound(2.0, 1.0, 0.5, [0.0, 100.0]), [2.0, 0.5])
    points = [[0.0], [0.5], [1.0]]
    assert np.isclose(geodesic_energy(points, [[[1.0]], [[1.0]]]), 1.0)
    assert np.allclose(geodesic_feedback([0.0], points, [[[2.0]], [[2.0]]]), [2.0])
