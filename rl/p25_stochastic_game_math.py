"""P25 Shapley operators, stochastic games, MPE, and potential structure."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class ZeroSumMatrixSolution:
    row_policy: np.ndarray
    column_policy: np.ndarray
    value: float
    duality_gap: float


def solve_zero_sum_matrix_game(payoff: Sequence) -> ZeroSumMatrixSolution:
    matrix = np.asarray(payoff, dtype=np.float64)
    if matrix.ndim != 2 or min(matrix.shape) == 0 or np.any(~np.isfinite(matrix)):
        raise ValueError("payoff must be a finite non-empty matrix")
    rows, columns = matrix.shape
    row = linprog(
        np.r_[np.zeros(rows), -1.0],
        A_ub=np.hstack((-matrix.T, np.ones((columns, 1)))),
        b_ub=np.zeros(columns),
        A_eq=np.r_[np.ones(rows), 0.0][None, :],
        b_eq=np.array([1.0]),
        bounds=[(0.0, 1.0)] * rows + [(None, None)],
        method="highs",
    )
    column = linprog(
        np.r_[np.zeros(columns), 1.0],
        A_ub=np.hstack((matrix, -np.ones((rows, 1)))),
        b_ub=np.zeros(rows),
        A_eq=np.r_[np.ones(columns), 0.0][None, :],
        b_eq=np.array([1.0]),
        bounds=[(0.0, 1.0)] * columns + [(None, None)],
        method="highs",
    )
    if not row.success or not column.success:
        message = row.message if not row.success else column.message
        raise RuntimeError(f"zero-sum matrix solve failed: {message}")
    row_policy = np.maximum(row.x[:rows], 0.0)
    column_policy = np.maximum(column.x[:columns], 0.0)
    row_policy /= row_policy.sum()
    column_policy /= column_policy.sum()
    lower = float(row.x[-1])
    upper = float(column.x[-1])
    return ZeroSumMatrixSolution(
        row_policy,
        column_policy,
        0.5 * (lower + upper),
        max(0.0, upper - lower),
    )


def _game_arrays(transition: Sequence, reward: Sequence):
    transitions = np.asarray(transition, dtype=np.float64)
    rewards = np.asarray(reward, dtype=np.float64)
    if transitions.ndim != 4:
        raise ValueError(
            "transition must have shape [state, row_action, column_action, next_state]"
        )
    states, row_actions, column_actions, next_states = transitions.shape
    if states == 0 or next_states != states:
        raise ValueError("transition state dimensions are inconsistent")
    if rewards.shape != (states, row_actions, column_actions):
        raise ValueError("reward shape is inconsistent")
    if (
        np.any(~np.isfinite(transitions))
        or np.any(~np.isfinite(rewards))
        or np.any(transitions < 0.0)
        or not np.allclose(transitions.sum(axis=3), 1.0)
    ):
        raise ValueError("stochastic game arrays are invalid")
    return transitions, rewards


@dataclass(frozen=True)
class ShapleyIterationResult:
    value: np.ndarray
    row_policy: np.ndarray
    column_policy: np.ndarray
    bellman_residual: float
    maximum_stage_duality_gap: float
    iterations: int


def shapley_value_iteration(
    transition: Sequence,
    reward: Sequence,
    *,
    discount: float,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> ShapleyIterationResult:
    """Solve a finite discounted two-player zero-sum stochastic game."""

    transitions, rewards = _game_arrays(transition, reward)
    if (
        not isfinite(discount)
        or not 0.0 <= discount < 1.0
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("Shapley iteration settings are invalid")
    states, row_actions, column_actions, _ = transitions.shape
    value = np.zeros(states)
    row_policy = np.zeros((states, row_actions))
    column_policy = np.zeros((states, column_actions))
    maximum_gap = 0.0
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        updated = np.empty(states)
        gaps = []
        for state in range(states):
            matrix = rewards[state] + discount * np.einsum(
                "abk,k->ab", transitions[state], value
            )
            solved = solve_zero_sum_matrix_game(matrix)
            updated[state] = solved.value
            row_policy[state] = solved.row_policy
            column_policy[state] = solved.column_policy
            gaps.append(solved.duality_gap)
        residual = float(np.max(np.abs(updated - value)))
        maximum_gap = max(maximum_gap, max(gaps, default=0.0))
        value = updated
        if residual <= tolerance:
            break
    return ShapleyIterationResult(
        value,
        row_policy,
        column_policy,
        residual,
        maximum_gap,
        iteration,
    )


@dataclass(frozen=True)
class AverageRewardGameResult:
    gain: float
    bias: np.ndarray
    row_policy: np.ndarray
    column_policy: np.ndarray
    span_residual: float
    iterations: int


def average_reward_zero_sum_game(
    transition: Sequence,
    reward: Sequence,
    *,
    reference_state: int = 0,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> AverageRewardGameResult:
    """Relative value iteration for a unichain/ergodic zero-sum game."""

    transitions, rewards = _game_arrays(transition, reward)
    states, row_actions, column_actions, _ = transitions.shape
    if (
        not 0 <= reference_state < states
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("average-reward settings are invalid")
    bias = np.zeros(states)
    row_policy = np.zeros((states, row_actions))
    column_policy = np.zeros((states, column_actions))
    gain = 0.0
    span = float("inf")
    for iteration in range(1, max_iterations + 1):
        raw = np.empty(states)
        for state in range(states):
            matrix = rewards[state] + np.einsum(
                "abk,k->ab", transitions[state], bias
            )
            solved = solve_zero_sum_matrix_game(matrix)
            raw[state] = solved.value
            row_policy[state] = solved.row_policy
            column_policy[state] = solved.column_policy
        gain = float(raw[reference_state])
        updated = raw - gain
        difference = updated - bias
        span = float(np.max(difference) - np.min(difference))
        bias = updated
        if span <= tolerance:
            break
    return AverageRewardGameResult(
        gain, bias, row_policy, column_policy, span, iteration
    )


def _policies(
    row_policy: Sequence,
    column_policy: Sequence,
    states: int,
    row_actions: int,
    column_actions: int,
) -> tuple[np.ndarray, np.ndarray]:
    row = np.asarray(row_policy, dtype=np.float64)
    column = np.asarray(column_policy, dtype=np.float64)
    if (
        row.shape != (states, row_actions)
        or column.shape != (states, column_actions)
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or np.any(row < 0.0)
        or np.any(column < 0.0)
        or not np.allclose(row.sum(axis=1), 1.0)
        or not np.allclose(column.sum(axis=1), 1.0)
    ):
        raise ValueError("policies must be row-normalized")
    return row, column


def evaluate_general_sum_policy(
    transition: Sequence,
    rewards: Sequence,
    row_policy: Sequence,
    column_policy: Sequence,
    *,
    discount: float,
) -> np.ndarray:
    """Evaluate a stationary policy pair for any number of payoff channels."""

    transitions = np.asarray(transition, dtype=np.float64)
    payoffs = np.asarray(rewards, dtype=np.float64)
    if transitions.ndim != 4:
        raise ValueError("transition must be four-dimensional")
    states, row_actions, column_actions, next_states = transitions.shape
    if (
        states == 0
        or next_states != states
        or payoffs.ndim != 4
        or payoffs.shape[1:] != (states, row_actions, column_actions)
        or np.any(~np.isfinite(transitions))
        or np.any(transitions < 0.0)
        or not np.allclose(transitions.sum(axis=3), 1.0)
        or np.any(~np.isfinite(payoffs))
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("general-sum game arrays are invalid")
    row, column = _policies(
        row_policy, column_policy, states, row_actions, column_actions
    )
    joint = row[:, :, None] * column[:, None, :]
    kernel = np.einsum("sab,sabk->sk", joint, transitions)
    values = np.empty((payoffs.shape[0], states))
    system = np.eye(states) - discount * kernel
    for player in range(payoffs.shape[0]):
        stage = np.einsum("sab,sab->s", joint, payoffs[player])
        values[player] = np.linalg.solve(system, stage)
    return values


def _best_response_value(
    transition: np.ndarray,
    reward: np.ndarray,
    opponent_policy: np.ndarray,
    *,
    row_player: bool,
    discount: float,
    tolerance: float,
    max_iterations: int,
) -> np.ndarray:
    states, row_actions, column_actions, _ = transition.shape
    action_count = row_actions if row_player else column_actions
    value = np.zeros(states)
    for _ in range(max_iterations):
        q = np.empty((states, action_count))
        for state in range(states):
            for action in range(action_count):
                if row_player:
                    probabilities = opponent_policy[state]
                    stage = probabilities @ reward[state, action, :]
                    kernel = probabilities @ transition[state, action, :, :]
                else:
                    probabilities = opponent_policy[state]
                    stage = probabilities @ reward[state, :, action]
                    kernel = probabilities @ transition[state, :, action, :]
                q[state, action] = stage + discount * kernel @ value
        updated = np.max(q, axis=1)
        if np.max(np.abs(updated - value)) <= tolerance:
            value = updated
            break
        value = updated
    return value


@dataclass(frozen=True)
class MarkovPerfectGap:
    values: np.ndarray
    row_best_response: np.ndarray
    column_best_response: np.ndarray
    row_gap: np.ndarray
    column_gap: np.ndarray
    maximum_gap: float


def markov_perfect_equilibrium_gap(
    transition: Sequence,
    rewards: Sequence,
    row_policy: Sequence,
    column_policy: Sequence,
    *,
    discount: float,
    tolerance: float = 1e-11,
    max_iterations: int = 20_000,
) -> MarkovPerfectGap:
    transitions = np.asarray(transition, dtype=np.float64)
    payoffs = np.asarray(rewards, dtype=np.float64)
    if payoffs.shape[0] != 2:
        raise ValueError("MPE gap currently supports two players")
    states, row_actions, column_actions, _ = transitions.shape
    row, column = _policies(
        row_policy, column_policy, states, row_actions, column_actions
    )
    values = evaluate_general_sum_policy(
        transitions, payoffs, row, column, discount=discount
    )
    row_best = _best_response_value(
        transitions,
        payoffs[0],
        column,
        row_player=True,
        discount=discount,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )
    column_best = _best_response_value(
        transitions,
        payoffs[1],
        row,
        row_player=False,
        discount=discount,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )
    row_gap = np.maximum(row_best - values[0], 0.0)
    column_gap = np.maximum(column_best - values[1], 0.0)
    return MarkovPerfectGap(
        values,
        row_best,
        column_best,
        row_gap,
        column_gap,
        float(max(np.max(row_gap), np.max(column_gap))),
    )


@dataclass(frozen=True)
class PureMarkovEquilibrium:
    row_actions: tuple[int, ...]
    column_actions: tuple[int, ...]
    values: np.ndarray
    maximum_gap: float


def enumerate_pure_markov_perfect_equilibria(
    transition: Sequence,
    rewards: Sequence,
    *,
    discount: float,
    tolerance: float = 1e-9,
    maximum_policy_pairs: int = 250_000,
) -> tuple[PureMarkovEquilibrium, ...]:
    transitions = np.asarray(transition, dtype=np.float64)
    payoffs = np.asarray(rewards, dtype=np.float64)
    if transitions.ndim != 4 or payoffs.ndim != 4 or payoffs.shape[0] != 2:
        raise ValueError("pure MPE enumeration needs a two-player finite game")
    states, row_actions, column_actions, _ = transitions.shape
    count = row_actions**states * column_actions**states
    if count > maximum_policy_pairs:
        raise ValueError("pure policy enumeration exceeds maximum_policy_pairs")
    equilibria = []
    for row_choice in product(range(row_actions), repeat=states):
        row = np.zeros((states, row_actions))
        row[np.arange(states), row_choice] = 1.0
        for column_choice in product(range(column_actions), repeat=states):
            column = np.zeros((states, column_actions))
            column[np.arange(states), column_choice] = 1.0
            gap = markov_perfect_equilibrium_gap(
                transitions, payoffs, row, column, discount=discount
            )
            if gap.maximum_gap <= tolerance:
                equilibria.append(
                    PureMarkovEquilibrium(
                        tuple(row_choice),
                        tuple(column_choice),
                        gap.values,
                        gap.maximum_gap,
                    )
                )
    return tuple(equilibria)


def stage_potential_residual(
    rewards: Sequence,
    potential: Sequence,
) -> float:
    """Maximum unilateral-deviation mismatch for two-player stage potentials."""

    payoffs = np.asarray(rewards, dtype=np.float64)
    phi = np.asarray(potential, dtype=np.float64)
    if (
        payoffs.ndim != 4
        or payoffs.shape[0] != 2
        or phi.shape != payoffs.shape[1:]
        or np.any(~np.isfinite(payoffs))
        or np.any(~np.isfinite(phi))
    ):
        raise ValueError("potential arrays are inconsistent")
    _, states, row_actions, column_actions = payoffs.shape
    residual = 0.0
    for state in range(states):
        for column_action in range(column_actions):
            for before in range(row_actions):
                for after in range(row_actions):
                    player = (
                        payoffs[0, state, after, column_action]
                        - payoffs[0, state, before, column_action]
                    )
                    potential_difference = (
                        phi[state, after, column_action]
                        - phi[state, before, column_action]
                    )
                    residual = max(residual, abs(player - potential_difference))
        for row_action in range(row_actions):
            for before in range(column_actions):
                for after in range(column_actions):
                    player = (
                        payoffs[1, state, row_action, after]
                        - payoffs[1, state, row_action, before]
                    )
                    potential_difference = (
                        phi[state, row_action, after]
                        - phi[state, row_action, before]
                    )
                    residual = max(residual, abs(player - potential_difference))
    return float(residual)
