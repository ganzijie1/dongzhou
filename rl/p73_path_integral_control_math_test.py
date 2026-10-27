import numpy as np

from rl.p73_path_integral_control_math import control_as_inference_posterior, entropic_risk, exponential_cost_weights, kl_control_policy, mppi_control_update, shift_control_horizon


def test_exponential_weights_and_entropic_risk_are_stable():
    result = exponential_cost_weights([10000.0, 10001.0], 1.0)
    assert np.isclose(result.weights.sum(), 1.0) and result.weights[0] > result.weights[1]
    assert np.isclose(entropic_risk([1.0, 3.0], 0.0), 2.0)
    assert entropic_risk([1.0, 3.0], 1.0) > 2.0


def test_kl_control_and_inference_preserve_support():
    policy = kl_control_policy([0.5, 0.5, 0.0], [2.0, 0.0, -100.0], 1.0)
    posterior = control_as_inference_posterior([0.5, 0.5, 0.0], [2.0, 0.0, -100.0], 1.0)
    assert np.allclose(policy, posterior) and policy[2] == 0.0


def test_mppi_update_and_horizon_shift():
    controls = np.zeros((2, 1))
    perturbations = np.array([[[1.0], [2.0]], [[-1.0], [-2.0]]])
    updated, weights = mppi_control_update(controls, perturbations, [0.0, 10.0], 1.0)
    assert np.all(updated > 0.9) and weights.effective_sample_size < 1.01
    assert np.allclose(shift_control_horizon(updated, [3.0])[-1], [3.0])
