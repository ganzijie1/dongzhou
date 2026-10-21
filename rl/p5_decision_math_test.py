"""Regression tests for the P5 decision mathematics suite."""

from __future__ import annotations

from math import isclose

import numpy as np

from rl.p5_decision_math import (
    ExponentiatedGradient,
    OPEStep,
    POMCPPlanner,
    dtmc_reachability,
    dynamic_mode_decomposition,
    extended_dynamic_mode_decomposition,
    finite_horizon_optimal_stopping,
    nested_cvar_mdp,
    sequential_doubly_robust_ope,
    solve_discounted_zero_sum_stochastic_game,
)


def test_pomcp_selects_the_dominant_action() -> None:
    planner = POMCPPlanner(simulations=300, horizon=3, seed=4)

    def model(state, action, _random):
        return state, state, 1.0 if action == "advance" else 0.0

    result = planner.plan(("hidden-left", "hidden-right"), lambda _state: ("wait", "advance"), model)
    assert result.action == "advance"
    assert result.action_values["advance"] > result.action_values["wait"]
    assert sum(result.action_visits.values()) == result.simulations


def test_nested_cvar_prefers_bounded_loss() -> None:
    transitions = np.asarray(
        [[[[0.9, 0.1], [0.5, 0.5]], [[1.0, 0.0], [1.0, 0.0]]]]
    )
    costs = np.asarray(
        [[[[0.0, 10.0], [2.0, 2.0]], [[0.0, 0.0], [0.0, 0.0]]]]
    )
    result = nested_cvar_mdp(transitions, costs, (0.0, 0.0), alpha=0.9)
    assert result.policy[0, 0] == 1
    assert isclose(result.action_values[0, 0, 0], 10.0)
    assert isclose(result.action_values[0, 0, 1], 2.0)


def test_discounted_stochastic_game_finds_matching_pennies() -> None:
    rewards = np.asarray([[[1.0, -1.0], [-1.0, 1.0]]])
    transitions = np.ones((1, 2, 2, 1), dtype=np.float64)
    result = solve_discounted_zero_sum_stochastic_game(
        rewards, transitions, discount=0.9
    )
    assert isclose(result.values[0], 0.0, abs_tol=1e-9)
    assert np.allclose(result.row_strategies[0], (0.5, 0.5), atol=1e-8)
    assert np.allclose(result.column_strategies[0], (0.5, 0.5), atol=1e-8)


def test_dtmc_reachability_and_expected_hitting_time() -> None:
    transitions = (
        (0.5, 0.5, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    )
    result = dtmc_reachability(transitions, (1,), unsafe=(2,))
    assert isclose(result.probabilities[0], 1.0, abs_tol=1e-10)
    assert isclose(result.expected_steps[0], 2.0, abs_tol=1e-9)
    assert result.probabilities[2] == 0.0


def test_optimal_stopping_and_entropic_mirror_ascent() -> None:
    stopping = finite_horizon_optimal_stopping(
        ((1.0,),),
        ((1.0,), (3.0,), (5.0,)),
        ((0.0,), (0.0,)),
    )
    assert np.allclose(stopping.values[:, 0], (5.0, 5.0, 5.0))
    assert not stopping.stop[0, 0] and not stopping.stop[1, 0]
    assert stopping.stop[2, 0]

    learner = ExponentiatedGradient(2, learning_rate=1.0)
    weights = learner.update((1.0, 0.0), maximize=True)
    assert weights[0] > weights[1]
    assert isclose(sum(weights), 1.0)


def test_sequential_doubly_robust_ope() -> None:
    episodes = (
        (OPEStep(1.0, 1.0, 1.0, 0.0, 0.0),),
        (OPEStep(3.0, 1.0, 1.0, 0.0, 0.0),),
    )
    result = sequential_doubly_robust_ope(episodes, (0.0, 0.0))
    assert result.episode_values == (1.0, 3.0)
    assert result.value == 2.0
    assert result.standard_error == 1.0


def test_dmd_and_edmd_recover_linear_feature_dynamics() -> None:
    operator = np.diag((2.0, 0.5))
    states = [np.asarray((1.0, 8.0))]
    for _ in range(5):
        states.append(operator @ states[-1])
    snapshots = np.column_stack(states)
    dmd = dynamic_mode_decomposition(snapshots, rank=2)
    assert np.allclose(dmd.operator, operator, atol=1e-10)
    assert np.allclose(dmd.predict((1.0, 8.0), 2), (4.0, 2.0), atol=1e-9)
    assert dmd.relative_residual < 1e-10

    scalar = np.asarray([[1.0, 2.0, 4.0, 8.0, 16.0]])
    edmd = extended_dynamic_mode_decomposition(
        scalar,
        lambda state: (state[0], state[0] ** 2),
        rank=2,
    )
    assert np.allclose(edmd.operator, np.diag((2.0, 4.0)), atol=1e-9)


def test_dmd_rank_truncation_changes_the_prediction_operator() -> None:
    snapshots = np.array(
        [
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 0.5, 0.25, 0.125],
        ]
    )
    full = dynamic_mode_decomposition(snapshots, rank=2)
    reduced = dynamic_mode_decomposition(snapshots, rank=1)
    assert np.linalg.matrix_rank(reduced.operator, tol=1e-10) == 1
    assert not np.allclose(reduced.operator, full.operator)
