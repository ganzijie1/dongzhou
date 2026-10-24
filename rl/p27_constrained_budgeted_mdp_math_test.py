import numpy as np

from rl.p27_constrained_budgeted_mdp_math import (
    evaluate_discounted_policy,
    finite_horizon_budgeted_mdp,
    pareto_prune,
    solve_discounted_cmdp,
)


def test_discounted_cmdp_obeys_flow_and_active_budget():
    transition = np.ones((1, 2, 1))
    result = solve_discounted_cmdp(
        transition,
        [[2.0, 10.0]],
        [[[0.0, 2.0]]],
        [1.0],
        [2.0],
        discount=0.5,
    )
    assert np.allclose(result.occupancy, [[1.0, 1.0]])
    assert np.allclose(result.policy, [[0.5, 0.5]])
    assert np.isclose(result.expected_reward, 12.0)
    assert np.allclose(result.expected_costs, [2.0])
    assert result.flow_residual < 1e-10
    assert np.all(result.budget_violations == 0.0)
    assert result.budget_shadow_prices[0] > 0.0


def test_policy_evaluation_uses_discounted_sum_units():
    total, values = evaluate_discounted_policy(
        np.ones((1, 2, 1)),
        [[2.0, 10.0]],
        [1.0],
        [[0.5, 0.5]],
        discount=0.5,
    )
    assert np.allclose(values, [12.0])
    assert np.isclose(total, 12.0)


def test_budgeted_mdp_enforces_pathwise_remaining_budget():
    transition = np.ones((1, 2, 1))
    reward = np.array([[[1.0], [5.0]]])
    cost = np.array([[[0], [2]]], dtype=np.int64)
    result = finite_horizon_budgeted_mdp(
        transition,
        reward,
        cost,
        horizon=2,
        maximum_budget=3,
        discount=0.9,
    )
    assert result.policy[0, 0, 0] == 0
    assert result.policy[0, 0, 2] == 1
    assert np.isclose(result.values[0, 0, 2], 5.9)
    assert np.isclose(result.values[0, 0, 3], 5.9)


def test_budgeted_mdp_rejects_action_if_any_successor_exceeds_budget():
    transition = np.array([[[0.5, 0.5]], [[1.0, 0.0]]])
    reward = np.ones_like(transition)
    cost = np.array([[[0, 2]], [[0, 0]]], dtype=np.int64)
    result = finite_horizon_budgeted_mdp(
        transition, reward, cost, horizon=1, maximum_budget=1
    )
    assert not result.feasible[0, 0, 1]
    assert result.policy[0, 0, 1] == -1


def test_pareto_prune_removes_only_dominated_points():
    indices = pareto_prune(
        [5.0, 4.0, 6.0, 5.0],
        [[2.0, 2.0], [3.0, 3.0], [4.0, 1.0], [1.0, 3.0]],
    )
    assert np.array_equal(indices, [0, 2, 3])
