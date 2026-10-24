import numpy as np

from rl.p25_stochastic_game_math import (
    average_reward_zero_sum_game,
    enumerate_pure_markov_perfect_equilibria,
    markov_perfect_equilibrium_gap,
    shapley_value_iteration,
    solve_zero_sum_matrix_game,
    stage_potential_residual,
)


def test_zero_sum_matrix_and_shapley_iteration_solve_matching_pennies():
    payoff = np.array([[1.0, -1.0], [-1.0, 1.0]])
    matrix = solve_zero_sum_matrix_game(payoff)
    assert np.allclose(matrix.row_policy, [0.5, 0.5])
    assert np.allclose(matrix.column_policy, [0.5, 0.5])
    transition = np.ones((1, 2, 2, 1))
    solved = shapley_value_iteration(
        transition, payoff[None, :, :], discount=0.9
    )
    assert np.isclose(solved.value[0], 0.0)
    assert np.allclose(solved.row_policy[0], [0.5, 0.5])
    assert solved.bellman_residual < 1e-9


def test_average_reward_game_returns_constant_gain():
    transition = np.ones((1, 1, 1, 1))
    result = average_reward_zero_sum_game(
        transition, np.array([[[2.5]]])
    )
    assert np.isclose(result.gain, 2.5)
    assert np.isclose(result.bias[0], 0.0)
    assert result.span_residual < 1e-12


def test_pure_mpe_enumeration_finds_coordination_equilibria():
    transition = np.ones((1, 2, 2, 1))
    common = np.array([[[3.0, 0.0], [0.0, 2.0]]])
    rewards = np.stack([common, common])
    equilibria = enumerate_pure_markov_perfect_equilibria(
        transition, rewards, discount=0.8
    )
    choices = {(item.row_actions, item.column_actions) for item in equilibria}
    assert ((0,), (0,)) in choices
    assert ((1,), (1,)) in choices


def test_markov_perfect_gap_detects_profitable_deviation():
    transition = np.ones((1, 2, 2, 1))
    row_payoff = np.array([[[3.0, 0.0], [1.0, 2.0]]])
    column_payoff = np.array([[[3.0, 1.0], [0.0, 2.0]]])
    rewards = np.stack([row_payoff, column_payoff])
    row = np.array([[1.0, 0.0]])
    column = np.array([[0.0, 1.0]])
    gap = markov_perfect_equilibrium_gap(
        transition, rewards, row, column, discount=0.5
    )
    assert gap.maximum_gap > 0.5


def test_exact_common_interest_game_has_zero_stage_potential_residual():
    common = np.array(
        [
            [[3.0, 0.0], [0.0, 2.0]],
            [[1.0, 2.0], [4.0, 0.0]],
        ]
    )
    rewards = np.stack([common, common])
    assert np.isclose(stage_potential_residual(rewards, common), 0.0)
