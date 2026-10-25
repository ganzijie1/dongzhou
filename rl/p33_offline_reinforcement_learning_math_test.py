import numpy as np

from rl.p33_offline_reinforcement_learning_math import (
    conservative_q_learning,
    discounted_occupancy_ratio,
    fitted_q_evaluation,
    fitted_q_iteration,
    linear_bellman_completeness_diagnostic,
    make_offline_batch,
    marginalized_importance_value,
)


def _batch():
    return make_offline_batch(
        [0, 0, 1, 1],
        [0, 1, 0, 1],
        [1.0, 0.0, 2.0, 2.0],
        [1, 0, 1, 1],
        [False, False, True, True],
        state_count=2,
        action_count=2,
    )


def test_fqe_evaluates_fixed_policy_and_fqi_improves_greedily():
    policy = np.array([[1.0, 0.0], [0.5, 0.5]])
    evaluated = fitted_q_evaluation(_batch(), policy, discount=0.9)
    improved = fitted_q_iteration(_batch(), discount=0.9)
    assert np.allclose(evaluated.q_values[1], [2.0, 2.0])
    assert np.isclose(evaluated.q_values[0, 0], 2.8)
    assert improved.policy[0, 0] == 1.0


def test_cql_penalizes_unseen_action():
    batch = make_offline_batch(
        np.zeros(20, dtype=int),
        np.zeros(20, dtype=int),
        np.ones(20),
        np.zeros(20, dtype=int),
        np.ones(20, dtype=bool),
        state_count=1,
        action_count=2,
    )
    result = conservative_q_learning(
        batch, discount=0.9, alpha=1.0, learning_rate=0.05, iterations=1000
    )
    assert result.q_values[0, 0] > result.q_values[0, 1]
    assert result.policy[0, 0] == 1.0


def test_discounted_occupancy_ratio_recovers_target_value():
    transition = np.array([[[1.0], [1.0]]])
    target = np.array([[1.0, 0.0]])
    behavior = np.array([[0.5, 0.5]])
    ratio = discounted_occupancy_ratio(
        transition, target, behavior, [1.0], discount=0.9
    )
    assert np.allclose(ratio.density_ratio, [[2.0, 0.0]])
    value = marginalized_importance_value(
        ratio.behavior_occupancy, ratio.density_ratio, [[1.0, 0.0]], discount=0.9
    )
    assert np.isclose(value, 10.0)
    assert ratio.unsupported_mass == 0.0


def test_occupancy_ratio_reports_unsupported_target_mass():
    transition = np.array([[[1.0], [1.0]]])
    result = discounted_occupancy_ratio(
        transition,
        [[0.0, 1.0]],
        [[1.0, 0.0]],
        [1.0],
        discount=0.5,
    )
    assert result.unsupported_mass == 1.0
    assert np.isinf(result.concentrability)


def test_linear_bellman_completeness_reports_projection_error():
    exact = linear_bellman_completeness_diagnostic(
        [[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]], [1.0, 3.0, 5.0]
    )
    misspecified = linear_bellman_completeness_diagnostic(
        [[1.0], [1.0], [1.0]], [1.0, 3.0, 5.0]
    )
    assert exact.maximum_residual < 1e-10
    assert misspecified.maximum_residual > 1.0
