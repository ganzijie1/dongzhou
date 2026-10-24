import numpy as np

from rl.p24_belief_space_planning_math import (
    alpha_vector_action,
    alpha_vector_dynamic_programming,
    despot_scenario_plan,
    finite_level_logit_reasoning,
    interactive_belief_update,
    point_based_value_iteration,
    pomcpow_plan,
)


def _sensor_pomdp():
    transition = np.zeros((2, 3, 2))
    transition[:, :, :] = np.eye(2)[:, None, :]
    observation = np.array(
        [
            [[0.5, 0.5], [0.5, 0.5]],
            [[0.9, 0.1], [0.1, 0.9]],
            [[0.5, 0.5], [0.5, 0.5]],
        ]
    )
    reward = np.array([[2.0, -0.2, -2.0], [-2.0, -0.2, 2.0]])
    return transition, observation, reward


def test_exact_alpha_vectors_value_information_before_committing():
    transition, observation, reward = _sensor_pomdp()
    plan = alpha_vector_dynamic_programming(
        transition, observation, reward, horizon=2, discount=1.0
    )
    action, value, _ = alpha_vector_action(plan, [0.5, 0.5])
    assert action == 1
    assert value > 1.0
    assert len(plan.layers) == 2


def test_pbvi_matches_exact_action_on_covered_belief():
    transition, observation, reward = _sensor_pomdp()
    exact = alpha_vector_dynamic_programming(
        transition, observation, reward, horizon=2
    )
    pbvi = point_based_value_iteration(
        transition,
        observation,
        reward,
        [[0.5, 0.5], [0.9, 0.1], [0.1, 0.9]],
        horizon=2,
    )
    assert alpha_vector_action(pbvi, [0.5, 0.5])[0] == 1
    assert np.isclose(
        alpha_vector_action(pbvi, [0.5, 0.5])[1],
        alpha_vector_action(exact, [0.5, 0.5])[1],
    )


def test_pomcpow_prefers_dominant_action_and_builds_sparse_observation_tree():
    def actions(_state):
        return ("safe", "bad")

    def generator(state, action, rng):
        observation = float(state) + rng.normal(scale=0.1)
        reward = 1.0 if action == "safe" else -1.0
        return state, observation, reward

    result = pomcpow_plan(
        [0, 1] * 20,
        actions,
        generator,
        simulations=300,
        horizon=3,
        observation_distance=lambda left, right: abs(float(left) - float(right)),
        random_state=7,
    )
    assert result.action == "safe"
    assert result.action_visits["safe"] > result.action_visits["bad"]
    assert result.observation_nodes < 300


def test_despot_uses_common_scenarios_and_returns_a_valid_upper_bound():
    transition, observation, reward = _sensor_pomdp()
    result = despot_scenario_plan(
        transition,
        observation,
        reward,
        [0.5, 0.5],
        horizon=2,
        scenario_count=200,
        regularization=0.001,
        random_state=11,
    )
    assert result.action == 1
    assert result.tree_size > 1
    assert result.fully_observable_upper_bound >= result.scenario_value - 0.2


def test_interactive_belief_updates_opponent_model_from_observation():
    belief = np.full((2, 2), 0.25)
    transition = np.zeros((1, 2, 2, 2))
    transition[0, 0] = np.eye(2)
    transition[0, 1] = np.array([[0.0, 1.0], [0.0, 1.0]])
    opponent = np.array(
        [
            [[1.0, 0.0], [1.0, 0.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    observation = np.array([[[0.9, 0.1], [0.1, 0.9]]])
    updated = interactive_belief_update(
        belief, 0, 1, transition, opponent, observation
    )
    assert np.isclose(updated.belief.sum(), 1.0)
    assert updated.belief[:, 1].sum() > updated.belief[:, 0].sum()


def test_finite_level_logit_reasoning_preserves_normalized_policies():
    result = finite_level_logit_reasoning(
        [[2.0, 0.0], [0.0, 1.0]],
        [[2.0, 0.0], [0.0, 1.0]],
        levels=3,
        rationality=2.0,
    )
    assert len(result.row_policies) == 4
    assert all(np.isclose(policy.sum(), 1.0) for policy in result.row_policies)
    assert all(np.isclose(policy.sum(), 1.0) for policy in result.column_policies)
