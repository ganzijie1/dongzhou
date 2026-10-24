import numpy as np

from rl.p16_multiagent_game_math import (
    FiniteDecPOMDP,
    cfr_plus_zero_sum,
    correlated_equilibrium,
    double_oracle_zero_sum,
    multiplicative_weights_bimatrix,
    psro_zero_sum,
    solve_dynamic_stackelberg,
    solve_multi_follower_stackelberg,
    solve_sequence_form_zero_sum,
)


def test_decpomdp_belief_and_local_policy_tree_evaluation():
    # Two agents, one action each, private observations jointly reveal the state.
    transition = np.zeros((2, 1, 2))
    transition[0, 0, 0] = 1.0
    transition[1, 0, 1] = 1.0
    observation = np.zeros((2, 1, 4))
    observation[0, 0, 0] = 1.0  # local observations (0, 0)
    observation[1, 0, 3] = 1.0  # local observations (1, 1)
    model = FiniteDecPOMDP((1, 1), (2, 2), transition, observation, [[1.0], [3.0]])
    posterior, probability = model.belief_update([0.25, 0.75], 0, 3)
    assert np.allclose(posterior, [0.0, 1.0])
    assert np.isclose(probability, 0.75)
    policies = [
        {(): 0, (0,): 0, (1,): 0},
        {(): 0, (0,): 0, (1,): 0},
    ]
    result = model.evaluate_policy_trees(
        policies, [0.25, 0.75], horizon=2, discount=0.5
    )
    assert np.isclose(result.expected_return, 3.75)
    assert np.isclose(result.leaf_probability, 1.0)
    assert result.visited_policy_nodes == 3


def test_sequence_form_reduces_to_normal_form_simplex_constraints():
    payoff = [[1.0, -1.0], [-1.0, 1.0]]
    result = solve_sequence_form_zero_sum(
        payoff, [[1.0, 1.0]], [1.0], [[1.0, 1.0]], [1.0]
    )
    assert np.allclose(result.row_realization, [0.5, 0.5])
    assert np.allclose(result.column_realization, [0.5, 0.5])
    assert abs(result.value) < 1e-9
    assert result.duality_gap < 1e-9
    assert result.row_flow_residual < 1e-9
    assert result.column_flow_residual < 1e-9


def test_cfr_plus_converges_on_matching_pennies():
    result = cfr_plus_zero_sum(
        [[1.0, -1.0], [-1.0, 1.0]], iterations=5_000
    )
    assert np.allclose(result.row_strategy, [0.5, 0.5], atol=0.03)
    assert np.allclose(result.column_strategy, [0.5, 0.5], atol=0.03)
    assert result.exploitability < 0.05


def test_double_oracle_and_psro_expand_a_finite_policy_library():
    payoff = np.array(
        [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]]
    )
    double_oracle = double_oracle_zero_sum(payoff)
    psro = psro_zero_sum(payoff)
    assert set(double_oracle.row_population) == {0, 1, 2}
    assert set(double_oracle.column_population) == {0, 1, 2}
    assert double_oracle.exploitability < 1e-9
    assert np.allclose(psro.row_strategy, [1 / 3, 1 / 3, 1 / 3])
    assert np.allclose(psro.column_strategy, [1 / 3, 1 / 3, 1 / 3])


def test_ce_and_cce_satisfy_incentive_constraints():
    row = [[4.0, 0.0], [0.0, 3.0]]
    column = [[4.0, 0.0], [0.0, 3.0]]
    ce = correlated_equilibrium(row, column, equilibrium_type="ce")
    cce = correlated_equilibrium(row, column, equilibrium_type="cce")
    assert ce.maximum_incentive_violation < 1e-9
    assert cce.maximum_incentive_violation < 1e-9
    assert np.isclose(ce.distribution.sum(), 1.0)
    assert np.isclose(cce.distribution.sum(), 1.0)
    assert ce.welfare == 8.0


def test_no_regret_dynamics_produces_an_approximate_cce():
    result = multiplicative_weights_bimatrix(
        [[1.0, -1.0], [-1.0, 1.0]],
        [[-1.0, 1.0], [1.0, -1.0]],
        iterations=5_000,
    )
    assert np.isclose(result.empirical_distribution.sum(), 1.0)
    assert result.cce_violation < 0.03


def test_multi_follower_stackelberg_induces_joint_nash_response():
    # Leader action 0 rewards joint follower response (0, 0).
    leader = np.array(
        [
            [[5.0, 0.0], [0.0, 1.0]],
            [[1.0, 0.0], [0.0, 4.0]],
        ]
    )
    follower_one = np.array(
        [
            [[2.0, 2.0], [0.0, 0.0]],
            [[0.0, 0.0], [2.0, 2.0]],
        ]
    )
    follower_two = np.array(
        [
            [[2.0, 0.0], [2.0, 0.0]],
            [[0.0, 2.0], [0.0, 2.0]],
        ]
    )
    result = solve_multi_follower_stackelberg(
        leader, [follower_one, follower_two]
    )
    assert result.follower_response == (0, 0)
    assert np.allclose(result.leader_strategy, [1.0, 0.0])
    assert result.leader_value == 5.0
    assert all(value >= -1e-9 for value in result.incentive_slacks)


def test_dynamic_stackelberg_uses_future_follower_response():
    transition = np.ones((1, 2, 2, 1))
    leader_reward = np.array([[[3.0, 0.0], [1.0, 2.0]]])
    follower_reward = np.array([[[2.0, 0.0], [0.0, 1.0]]])
    result = solve_dynamic_stackelberg(
        transition,
        leader_reward,
        follower_reward,
        [1.0],
        horizon=2,
        discount=0.5,
    )
    assert np.array_equal(result.leader_policy, [[0], [0]])
    assert np.array_equal(result.follower_policy, [[0], [0]])
    assert np.isclose(result.leader_value, 4.5)
    assert np.isclose(result.follower_value, 3.0)
