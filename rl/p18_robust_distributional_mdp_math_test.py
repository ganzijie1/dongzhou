import numpy as np

from rl.p18_robust_distributional_mdp_math import (
    PageHinkleyPolicySwitcher,
    categorical_bellman_projection,
    discrete_cvar,
    entropic_risk_value_iteration,
    quantile_bellman_targets,
    quantile_huber_loss,
    robust_reward_occupancy_lp,
    robust_value_iteration,
    stochastic_reach_avoid,
    worst_case_discrete_expectation,
)


def test_tv_kl_and_wasserstein_worst_case_expectations():
    tv = worst_case_discrete_expectation([0.5, 0.5], [0.0, 10.0], 0.2)
    wasserstein = worst_case_discrete_expectation(
        [0.5, 0.5],
        [0.0, 10.0],
        0.2,
        ambiguity_type="wasserstein",
        ground_cost=[[0.0, 1.0], [1.0, 0.0]],
    )
    kl = worst_case_discrete_expectation(
        [0.5, 0.5], [0.0, 10.0], 0.1, ambiguity_type="kl"
    )
    assert np.allclose(tv.distribution, [0.7, 0.3])
    assert np.allclose(wasserstein.distribution, [0.7, 0.3])
    assert np.isclose(tv.value, 3.0)
    assert np.isclose(wasserstein.value, 3.0)
    assert kl.value < 5.0
    assert kl.ambiguity_measure <= 0.1 + 1e-7


def test_rectangular_robust_value_iteration_uses_adversarial_transition():
    transition = np.array(
        [
            [[0.5, 0.5], [1.0, 0.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    reward = [[0.0, 0.0], [1.0, 1.0]]
    nominal = robust_value_iteration(
        transition, reward, 0.0, discount=0.9
    )
    robust = robust_value_iteration(
        transition, reward, 0.4, discount=0.9
    )
    assert nominal.converged and robust.converged
    assert robust.values[0] <= nominal.values[0]
    assert np.allclose(robust.worst_case_transitions.sum(axis=2), 1.0)


def test_categorical_and_quantile_bellman_operators():
    projected = categorical_bellman_projection(
        [0.5, 0.5], [0.0, 2.0], reward=1.0, discount=0.5
    )
    assert np.allclose(projected, [0.25, 0.75])
    targets = quantile_bellman_targets(
        [-1.0, 1.0], reward=2.0, discount=0.5
    )
    assert np.allclose(targets, [1.5, 2.5])
    assert quantile_huber_loss(targets, targets) >= 0.0
    assert quantile_huber_loss(targets, targets) < 0.2


def test_entropic_risk_iteration_and_discrete_cvar():
    transition = np.array(
        [
            [[0.5, 0.5], [1.0, 0.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    reward = [[0.0, 0.2], [1.0, 1.0]]
    result = entropic_risk_value_iteration(
        transition, reward, risk_parameter=-1.0, discount=0.8
    )
    assert result.converged
    assert len(result.policy) == 2
    assert discrete_cvar([-10.0, 2.0, 5.0], [0.1, 0.4, 0.5], tail_probability=0.2) == -4.0
    assert discrete_cvar(
        [-10.0, 2.0, 5.0], [0.1, 0.4, 0.5], tail_probability=0.2, tail="upper"
    ) == 5.0


def test_stochastic_reach_avoid_selects_safe_action():
    # State 0 is active, 1 target, 2 avoid.
    transition = np.array(
        [
            [[0.0, 0.8, 0.2], [0.0, 0.4, 0.6]],
            [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    result = stochastic_reach_avoid(transition, [1], [2], horizon=2)
    assert np.isclose(result.values[1, 0], 0.8)
    assert result.policy[0, 0] == 0
    assert result.values[2, 1] == 1.0
    assert result.values[2, 2] == 0.0


def test_robust_reward_occupancy_maximizes_worst_scenario():
    transition = np.ones((1, 2, 1))
    rewards = np.array(
        [
            [[2.0, 0.0]],
            [[0.0, 2.0]],
        ]
    )
    result = robust_reward_occupancy_lp(
        transition, [1.0], rewards, discount=0.5
    )
    assert np.allclose(result.policy, [[0.5, 0.5]])
    assert np.allclose(result.scenario_returns, [2.0, 2.0])
    assert np.isclose(result.guaranteed_return, 2.0)
    assert result.flow_residual < 1e-9


def test_page_hinkley_switches_after_upward_loss_drift():
    switcher = PageHinkleyPolicySwitcher(
        3, threshold=2.0, minimum_observations=5
    )
    events = [switcher.update(0.0) for _ in range(5)]
    assert not any(event.changed for event in events)
    changed = switcher.update(10.0)
    assert changed.changed
    assert changed.active_policy == 1
    assert switcher.update(0.0).active_policy == 1
