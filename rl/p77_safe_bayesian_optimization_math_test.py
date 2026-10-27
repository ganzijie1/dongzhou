import numpy as np

from rl.p77_safe_bayesian_optimization_math import autoregressive_multifidelity_covariance, cost_aware_acquisition, expected_improvement, gp_posterior, rbf_kernel, safeopt_sets


def test_gp_posterior_interpolates_low_noise_training_point():
    mean, variance = gp_posterior([[0.0], [1.0]], [0.0, 1.0], [[0.0]], noise_variance=1e-10)
    assert np.allclose(mean, [0.0], atol=1e-7) and variance[0] < 1e-7
    assert np.allclose(np.diag(rbf_kernel([[0.0], [1.0]], [[0.0], [1.0]])), 1.0)


def test_expected_improvement_and_safeopt_sets():
    improvement = expected_improvement([0.0, 2.0], [0.0, 1.0], best=1.0)
    assert np.isclose(improvement[0], 1.0) and improvement[1] > 0.0
    sets = safeopt_sets([[0.0], [1.0], [2.0]], [1.0, 2.0, 3.0], [0.01] * 3, [2.0, 1.5, 0.0], [0.01] * 3, threshold=1.0, beta=1.0, lipschitz=0.4)
    assert np.array_equal(sets.safe, [True, True, False])
    assert sets.expanders[1]


def test_multifidelity_covariance_and_cost_awareness():
    cross, high = autoregressive_multifidelity_covariance([[2.0]], [[1.0]], 0.5)
    assert np.allclose(cross, [[1.0]]) and np.allclose(high, [[1.5]])
    assert np.allclose(cost_aware_acquisition([2.0, 3.0], [1.0, 3.0]), [2.0, 1.0])
