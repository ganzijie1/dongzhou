import numpy as np

from rl.p35_large_deviation_risk_math import (
    chernoff_tail_bound,
    cramer_transform,
    discrete_kl,
    donsker_varadhan_discrete,
    entropy_robust_expectation,
    exponential_tilt_samples,
    finite_horizon_risk_sensitive_dp,
    freidlin_wentzell_action,
)


def test_dv_optimizer_matches_log_moment_and_tilts_high_payoff():
    result = donsker_varadhan_discrete([0.5, 0.5], [0.0, 2.0])
    assert np.isclose(result.log_moment, result.variational_value)
    assert result.tilted_distribution[1] > 0.8
    assert discrete_kl(result.tilted_distribution, [0.5, 0.5]) > 0.0


def test_entropic_risk_exceeds_mean_loss():
    result = entropy_robust_expectation([0.5, 0.5], [0.0, 2.0], theta=1.0)
    assert result.log_moment > 1.0
    assert np.isclose(result.log_moment, result.variational_value)


def test_bernoulli_cramer_transform_and_chernoff_rate():
    result = cramer_transform([0.0, 1.0], [0.5, 0.5], 0.75)
    bound = chernoff_tail_bound([0.0, 1.0], [0.5, 0.5], 0.75)
    expected = 0.75 * np.log(1.5) + 0.25 * np.log(0.5)
    assert np.isclose(result.rate, expected, atol=1e-8)
    assert np.isclose(bound.rate, result.rate, atol=1e-8)


def test_risk_sensitive_dp_avoids_tail_risk():
    transition = np.array(
        [
            [[1.0, 0.0], [0.5, 0.5]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    costs = np.array([[1.0, 0.0], [0.0, 0.0]])
    terminal = np.array([0.0, 5.0])
    neutral = finite_horizon_risk_sensitive_dp(
        transition, costs, terminal, horizon=1, theta=0.0
    )
    averse = finite_horizon_risk_sensitive_dp(
        transition, costs, terminal, horizon=1, theta=2.0
    )
    assert neutral.policy[0, 0] == 0
    assert averse.policy[0, 0] == 0
    assert averse.values[0, 0] >= neutral.values[0, 0]


def test_freidlin_action_zero_on_deterministic_drift_path():
    path = np.array([[0.0], [1.0], [2.0]])
    action = freidlin_wentzell_action(
        path, lambda _state: np.array([1.0]), [[1.0]], time_step=1.0
    )
    assert action == 0.0


def test_exponential_tilt_reports_weight_degeneracy():
    result = exponential_tilt_samples([0.0, 0.0, 10.0], theta=1.0)
    assert result.normalized_weights[-1] > 0.99
    assert result.effective_sample_size < 1.1
