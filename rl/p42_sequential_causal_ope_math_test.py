import numpy as np

from rl.p42_sequential_causal_ope_math import (
    marginal_sensitivity_probability_bounds,
    per_decision_importance_sampling,
    proximal_bridge_score,
    sequential_doubly_robust,
    sequential_g_computation,
)


def test_g_computation_evaluates_intervened_policy():
    transitions = np.array([[[[1.0], [1.0]]]])
    value = sequential_g_computation(transitions, [[[2.0, 6.0]]], [[[0.25, 0.75]]], [1.0])
    assert np.isclose(value, 5.0)


def test_pdis_uses_cumulative_action_ratios():
    result = per_decision_importance_sampling(
        [[1.0, 2.0], [2.0, 1.0]],
        [[0.5, 0.5], [1.0, 0.5]],
        [[0.5, 0.25], [0.5, 0.5]],
    )
    assert np.allclose(result.trajectory_returns, [5.0, 6.0])
    assert np.isclose(result.estimate, 5.5)


def test_sequential_dr_is_exact_when_bellman_residual_is_zero():
    result = sequential_doubly_robust(
        [[1.0, 2.0]], [[3.0, 2.0]], [[3.0, 2.0, 0.0]], [[0.5, 0.5]], [[0.25, 0.25]]
    )
    assert np.isclose(result.estimate, 3.0)


def test_proximal_score_and_sensitivity_bounds_are_auditable():
    assert np.isclose(proximal_bridge_score([1.0, 1.0], [2.0, 2.0], [2.0, 0.0], [0.5, 0.5]), 1.0)
    lower, upper = marginal_sensitivity_probability_bounds(0.5, gamma=2.0)
    assert np.allclose([lower, upper], [1.0 / 3.0, 2.0 / 3.0])
