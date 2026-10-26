import numpy as np

from rl.p48_uncertainty_quantification_math import (
    dynamic_sobol_indices,
    mlmc_estimate,
    mlmc_optimal_allocation,
    pce_statistics,
    smolyak_level_indices,
)


def test_orthonormal_pce_statistics_and_sobol_decomposition():
    stats = pce_statistics([2.0, 3.0, 4.0, 5.0], [(0, 0), (1, 0), (0, 1), (1, 1)])
    assert np.isclose(stats.mean, 2.0)
    assert np.isclose(stats.variance, 50.0)
    assert np.allclose(stats.first_order_sobol, [9.0 / 50.0, 16.0 / 50.0])
    assert np.allclose(stats.total_sobol, [34.0 / 50.0, 41.0 / 50.0])


def test_dynamic_sobol_integrates_time_resolved_indices():
    first, total = dynamic_sobol_indices([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], [(0, 0), (1, 0), (0, 1)], [0.0, 1.0])
    assert np.allclose(first, [0.5, 0.5])
    assert np.allclose(total, [0.5, 0.5])


def test_smolyak_and_mlmc_bookkeeping():
    assert set(smolyak_level_indices(2, 2)) == {(1, 1), (1, 2), (2, 1)}
    allocation = mlmc_optimal_allocation([1.0, 0.25], [1.0, 4.0], rmse=0.5)
    assert allocation[0] > allocation[1]
    assert np.isclose(mlmc_estimate([[1.0, 3.0], [0.5, 1.5]]), 3.0)
