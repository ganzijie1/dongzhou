"""P16 multi-agent partial observation and equilibrium algorithms.

All solvers target finite explicitly supplied games.  Enumeration-based
Stackelberg routines expose profile budgets instead of hiding exponential
complexity.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Mapping, Sequence

import numpy as np
from scipy.optimize import linprog

from rl.decision_math import solve_zero_sum_game


@dataclass(frozen=True)
class DecPOMDPPolicyResult:
    expected_return: float
    leaf_probability: float
    visited_policy_nodes: int


class FiniteDecPOMDP:
    """Finite cooperative Dec-POMDP with factored local action/observation sets."""

    def __init__(
        self,
        action_counts: Sequence[int],
        observation_counts: Sequence[int],
        transition: Sequence,
        observation_probability: Sequence,
        reward: Sequence,
    ) -> None:
        self.action_counts = tuple(int(value) for value in action_counts)
        self.observation_counts = tuple(int(value) for value in observation_counts)
        if (
            not self.action_counts
            or len(self.action_counts) != len(self.observation_counts)
            or any(value <= 0 for value in self.action_counts)
            or any(value <= 0 for value in self.observation_counts)
        ):
            raise ValueError("Dec-POMDP needs positive local action/observation counts")
        self.joint_action_count = int(np.prod(self.action_counts))
        self.joint_observation_count = int(np.prod(self.observation_counts))
        self.transition = np.asarray(transition, dtype=np.float64)
        self.observation_probability = np.asarray(
            observation_probability, dtype=np.float64
        )
        self.reward = np.asarray(reward, dtype=np.float64)
        if self.transition.ndim != 3:
            raise ValueError("Dec-POMDP transition must be three-dimensional")
        states, joint_actions, next_states = self.transition.shape
        if (
            states == 0
            or next_states != states
            or joint_actions != self.joint_action_count
            or self.observation_probability.shape
            != (states, self.joint_action_count, self.joint_observation_count)
            or self.reward.shape != (states, self.joint_action_count)
            or np.any(~np.isfinite(self.transition))
            or np.any(~np.isfinite(self.observation_probability))
            or np.any(~np.isfinite(self.reward))
            or np.any(self.transition < 0.0)
            or np.any(self.observation_probability < 0.0)
            or not np.allclose(self.transition.sum(axis=2), 1.0)
            or not np.allclose(self.observation_probability.sum(axis=2), 1.0)
        ):
            raise ValueError("Dec-POMDP arrays are inconsistent")
        self.state_count = states

    def joint_action_index(self, local_actions: Sequence[int]) -> int:
        actions = tuple(int(value) for value in local_actions)
        if len(actions) != len(self.action_counts) or any(
            action < 0 or action >= count
            for action, count in zip(actions, self.action_counts, strict=True)
        ):
            raise ValueError("local Dec-POMDP action is out of range")
        return int(np.ravel_multi_index(actions, self.action_counts))

    def local_observations(self, joint_observation: int) -> tuple[int, ...]:
        if not 0 <= joint_observation < self.joint_observation_count:
            raise ValueError("joint Dec-POMDP observation is out of range")
        return tuple(
            int(value)
            for value in np.unravel_index(
                joint_observation, self.observation_counts
            )
        )

    def belief_update(
        self,
        belief: Sequence[float],
        joint_action: int,
        joint_observation: int,
    ) -> tuple[np.ndarray, float]:
        prior = np.asarray(belief, dtype=np.float64)
        if (
            prior.shape != (self.state_count,)
            or np.any(~np.isfinite(prior))
            or np.any(prior < 0.0)
            or not np.isclose(prior.sum(), 1.0)
            or not 0 <= joint_action < self.joint_action_count
            or not 0 <= joint_observation < self.joint_observation_count
        ):
            raise ValueError("Dec-POMDP belief update inputs are invalid")
        predicted = prior @ self.transition[:, joint_action, :]
        unnormalized = predicted * self.observation_probability[
            :, joint_action, joint_observation
        ]
        probability = float(unnormalized.sum())
        if probability <= 0.0:
            raise ValueError("conditioned Dec-POMDP observation has zero probability")
        return unnormalized / probability, probability

    def evaluate_policy_trees(
        self,
        policy_trees: Sequence[Mapping[tuple[int, ...], int]],
        initial_belief: Sequence[float],
        *,
        horizon: int,
        discount: float = 1.0,
    ) -> DecPOMDPPolicyResult:
        """Evaluate deterministic local policy trees keyed by observation history."""

        if (
            len(policy_trees) != len(self.action_counts)
            or horizon <= 0
            or not isfinite(discount)
            or not 0.0 <= discount <= 1.0
        ):
            raise ValueError("Dec-POMDP policy-tree settings are invalid")
        initial = np.asarray(initial_belief, dtype=np.float64)
        if (
            initial.shape != (self.state_count,)
            or np.any(~np.isfinite(initial))
            or np.any(initial < 0.0)
            or not np.isclose(initial.sum(), 1.0)
        ):
            raise ValueError("initial Dec-POMDP belief is invalid")
        visited = 0

        def walk(
            belief: np.ndarray,
            histories: tuple[tuple[int, ...], ...],
            time: int,
        ) -> tuple[float, float]:
            nonlocal visited
            local_actions = []
            for agent, history in enumerate(histories):
                if history not in policy_trees[agent]:
                    raise ValueError("Dec-POMDP policy tree is missing a history")
                action = int(policy_trees[agent][history])
                if not 0 <= action < self.action_counts[agent]:
                    raise ValueError("Dec-POMDP policy tree contains an invalid action")
                local_actions.append(action)
            visited += 1
            joint_action = self.joint_action_index(local_actions)
            stage = float(belief @ self.reward[:, joint_action])
            if time + 1 == horizon:
                return stage, 1.0
            predicted = belief @ self.transition[:, joint_action, :]
            future = 0.0
            probability_mass = 0.0
            for joint_observation in range(self.joint_observation_count):
                unnormalized = predicted * self.observation_probability[
                    :, joint_action, joint_observation
                ]
                probability = float(unnormalized.sum())
                if probability <= 1e-15:
                    continue
                local_observation = self.local_observations(joint_observation)
                next_histories = tuple(
                    history + (local_observation[agent],)
                    for agent, history in enumerate(histories)
                )
                branch, leaf_mass = walk(
                    unnormalized / probability, next_histories, time + 1
                )
                future += probability * branch
                probability_mass += probability * leaf_mass
            return stage + discount * future, probability_mass

        value, leaf_probability = walk(
            initial, tuple(() for _ in self.action_counts), 0
        )
        return DecPOMDPPolicyResult(value, leaf_probability, visited)


@dataclass(frozen=True)
class SequenceFormResult:
    row_realization: np.ndarray
    column_realization: np.ndarray
    value: float
    duality_gap: float
    row_flow_residual: float
    column_flow_residual: float


def solve_sequence_form_zero_sum(
    payoff: Sequence,
    row_flow_matrix: Sequence,
    row_flow_rhs: Sequence[float],
    column_flow_matrix: Sequence,
    column_flow_rhs: Sequence[float],
) -> SequenceFormResult:
    """Solve a zero-sum sequence-form game from realization-plan constraints."""

    matrix = np.asarray(payoff, dtype=np.float64)
    row_flow = np.asarray(row_flow_matrix, dtype=np.float64)
    row_rhs = np.asarray(row_flow_rhs, dtype=np.float64)
    column_flow = np.asarray(column_flow_matrix, dtype=np.float64)
    column_rhs = np.asarray(column_flow_rhs, dtype=np.float64)
    if (
        matrix.ndim != 2
        or min(matrix.shape) == 0
        or row_flow.ndim != 2
        or row_flow.shape[1] != matrix.shape[0]
        or row_rhs.shape != (row_flow.shape[0],)
        or column_flow.ndim != 2
        or column_flow.shape[1] != matrix.shape[1]
        or column_rhs.shape != (column_flow.shape[0],)
        or any(
            np.any(~np.isfinite(value))
            for value in (matrix, row_flow, row_rhs, column_flow, column_rhs)
        )
    ):
        raise ValueError("sequence-form arrays are inconsistent")
    row_sequences, column_sequences = matrix.shape

    # max column_rhs @ q, with F.T q <= A.T x and E x = e.
    row_objective = np.r_[
        np.zeros(row_sequences), -column_rhs
    ]
    row_inequality = np.hstack(
        (-matrix.T, column_flow.T)
    )
    row_result = linprog(
        row_objective,
        A_ub=row_inequality,
        b_ub=np.zeros(column_sequences),
        A_eq=np.hstack(
            (row_flow, np.zeros((row_flow.shape[0], column_flow.shape[0])))
        ),
        b_eq=row_rhs,
        bounds=[(0.0, None)] * row_sequences
        + [(None, None)] * column_flow.shape[0],
        method="highs",
    )
    # min row_rhs @ p, with E.T p >= A y and F y = f.
    column_objective = np.r_[
        np.zeros(column_sequences), row_rhs
    ]
    column_inequality = np.hstack(
        (matrix, -row_flow.T)
    )
    column_result = linprog(
        column_objective,
        A_ub=column_inequality,
        b_ub=np.zeros(row_sequences),
        A_eq=np.hstack(
            (column_flow, np.zeros((column_flow.shape[0], row_flow.shape[0])))
        ),
        b_eq=column_rhs,
        bounds=[(0.0, None)] * column_sequences
        + [(None, None)] * row_flow.shape[0],
        method="highs",
    )
    if not row_result.success or not column_result.success:
        message = row_result.message if not row_result.success else column_result.message
        raise RuntimeError(f"sequence-form solve failed: {message}")
    row_plan = np.maximum(row_result.x[:row_sequences], 0.0)
    column_plan = np.maximum(column_result.x[:column_sequences], 0.0)
    lower = float(-row_result.fun)
    upper = float(column_result.fun)
    return SequenceFormResult(
        row_plan,
        column_plan,
        0.5 * (lower + upper),
        max(0.0, upper - lower),
        float(np.max(np.abs(row_flow @ row_plan - row_rhs), initial=0.0)),
        float(
            np.max(
                np.abs(column_flow @ column_plan - column_rhs), initial=0.0
            )
        ),
    )


@dataclass(frozen=True)
class CFRPlusResult:
    row_strategy: np.ndarray
    column_strategy: np.ndarray
    value: float
    exploitability: float
    iterations: int


def cfr_plus_zero_sum(
    payoff: Sequence[Sequence[float]],
    *,
    iterations: int = 10_000,
    averaging_delay: int = 0,
) -> CFRPlusResult:
    """CFR+ regret matching for a finite two-player zero-sum matrix game."""

    matrix = np.asarray(payoff, dtype=np.float64)
    if (
        matrix.ndim != 2
        or min(matrix.shape) == 0
        or np.any(~np.isfinite(matrix))
        or iterations <= 0
        or averaging_delay < 0
    ):
        raise ValueError("CFR+ inputs are invalid")
    row_regret = np.zeros(matrix.shape[0])
    column_regret = np.zeros(matrix.shape[1])
    row_average = np.zeros(matrix.shape[0])
    column_average = np.zeros(matrix.shape[1])

    def regret_strategy(regret: np.ndarray) -> np.ndarray:
        positive = np.maximum(regret, 0.0)
        if positive.sum() <= 1e-15:
            return np.full(regret.size, 1.0 / regret.size)
        return positive / positive.sum()

    for iteration in range(1, iterations + 1):
        row_strategy = regret_strategy(row_regret)
        column_strategy = regret_strategy(column_regret)
        row_values = matrix @ column_strategy
        column_values = row_strategy @ matrix
        value = float(row_strategy @ row_values)
        row_regret = np.maximum(0.0, row_regret + row_values - value)
        column_regret = np.maximum(0.0, column_regret + value - column_values)
        weight = max(0, iteration - averaging_delay)
        row_average += weight * row_strategy
        column_average += weight * column_strategy
    if row_average.sum() <= 0.0:
        row_average = row_strategy
        column_average = column_strategy
    else:
        row_average /= row_average.sum()
        column_average /= column_average.sum()
    lower = float(np.min(row_average @ matrix))
    upper = float(np.max(matrix @ column_average))
    return CFRPlusResult(
        row_average,
        column_average,
        0.5 * (lower + upper),
        max(0.0, upper - lower),
        iterations,
    )


@dataclass(frozen=True)
class OraclePopulationResult:
    row_population: tuple[int, ...]
    column_population: tuple[int, ...]
    row_strategy: np.ndarray
    column_strategy: np.ndarray
    value: float
    exploitability: float
    exploitability_history: tuple[float, ...]


def double_oracle_zero_sum(
    payoff: Sequence[Sequence[float]],
    *,
    initial_rows: Sequence[int] = (0,),
    initial_columns: Sequence[int] = (0,),
    tolerance: float = 1e-9,
    max_iterations: int = 1_000,
) -> OraclePopulationResult:
    """Finite zero-sum double oracle with exact pure best responses."""

    matrix = np.asarray(payoff, dtype=np.float64)
    if (
        matrix.ndim != 2
        or min(matrix.shape) == 0
        or np.any(~np.isfinite(matrix))
        or tolerance < 0.0
        or max_iterations <= 0
    ):
        raise ValueError("double-oracle inputs are invalid")
    row_population = list(dict.fromkeys(int(value) for value in initial_rows))
    column_population = list(dict.fromkeys(int(value) for value in initial_columns))
    if (
        not row_population
        or not column_population
        or any(value < 0 or value >= matrix.shape[0] for value in row_population)
        or any(value < 0 or value >= matrix.shape[1] for value in column_population)
    ):
        raise ValueError("double-oracle initial population is invalid")
    history = []
    for _ in range(max_iterations):
        restricted = matrix[np.ix_(row_population, column_population)]
        solved = solve_zero_sum_game(restricted)
        row_meta = np.asarray(solved.row_strategy)
        column_meta = np.asarray(solved.column_strategy)
        full_row = np.zeros(matrix.shape[0])
        full_column = np.zeros(matrix.shape[1])
        full_row[row_population] = row_meta
        full_column[column_population] = column_meta
        row_values = matrix @ full_column
        column_values = full_row @ matrix
        row_best = int(np.argmax(row_values))
        column_best = int(np.argmin(column_values))
        exploitability = max(
            0.0, float(row_values[row_best] - column_values[column_best])
        )
        history.append(exploitability)
        added = False
        if row_best not in row_population and row_values[row_best] > solved.value + tolerance:
            row_population.append(row_best)
            added = True
        if (
            column_best not in column_population
            and column_values[column_best] < solved.value - tolerance
        ):
            column_population.append(column_best)
            added = True
        if not added:
            return OraclePopulationResult(
                tuple(row_population),
                tuple(column_population),
                full_row,
                full_column,
                float(solved.value),
                exploitability,
                tuple(history),
            )
    raise RuntimeError("double-oracle iteration limit reached")


def psro_zero_sum(
    payoff: Sequence[Sequence[float]],
    *,
    seed_rows: Sequence[int] = (0,),
    seed_columns: Sequence[int] = (0,),
    tolerance: float = 1e-9,
    max_iterations: int = 1_000,
) -> OraclePopulationResult:
    """Nash-meta-solver PSRO for a finite explicit zero-sum policy library."""

    return double_oracle_zero_sum(
        payoff,
        initial_rows=seed_rows,
        initial_columns=seed_columns,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )


@dataclass(frozen=True)
class CorrelatedEquilibriumResult:
    distribution: np.ndarray
    row_value: float
    column_value: float
    welfare: float
    maximum_incentive_violation: float
    equilibrium_type: str


def correlated_equilibrium(
    row_payoff: Sequence[Sequence[float]],
    column_payoff: Sequence[Sequence[float]],
    *,
    equilibrium_type: str = "ce",
) -> CorrelatedEquilibriumResult:
    """Find a welfare-maximizing CE or CCE of a finite bimatrix game."""

    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or row.shape != column.shape
        or min(row.shape) == 0
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or equilibrium_type not in {"ce", "cce"}
    ):
        raise ValueError("correlated-equilibrium inputs are invalid")
    rows, columns = row.shape
    constraints = []
    if equilibrium_type == "ce":
        for recommendation in range(rows):
            for deviation in range(rows):
                if recommendation == deviation:
                    continue
                coefficients = np.zeros((rows, columns))
                coefficients[recommendation, :] = -(
                    row[recommendation, :] - row[deviation, :]
                )
                constraints.append(coefficients.ravel())
        for recommendation in range(columns):
            for deviation in range(columns):
                if recommendation == deviation:
                    continue
                coefficients = np.zeros((rows, columns))
                coefficients[:, recommendation] = -(
                    column[:, recommendation] - column[:, deviation]
                )
                constraints.append(coefficients.ravel())
    else:
        for deviation in range(rows):
            constraints.append((row[deviation, None, :] - row).ravel())
        for deviation in range(columns):
            constraints.append((column[:, deviation, None] - column).ravel())
    solved = linprog(
        -(row + column).ravel(),
        A_ub=np.asarray(constraints) if constraints else None,
        b_ub=np.zeros(len(constraints)) if constraints else None,
        A_eq=np.ones((1, rows * columns)),
        b_eq=np.ones(1),
        bounds=[(0.0, 1.0)] * (rows * columns),
        method="highs",
    )
    if not solved.success or solved.x is None:
        raise RuntimeError(f"correlated-equilibrium solve failed: {solved.message}")
    distribution = solved.x.reshape(rows, columns)
    violations = (
        np.asarray(constraints) @ solved.x if constraints else np.zeros(1)
    )
    row_value = float(np.sum(distribution * row))
    column_value = float(np.sum(distribution * column))
    return CorrelatedEquilibriumResult(
        distribution,
        row_value,
        column_value,
        row_value + column_value,
        float(max(0.0, np.max(violations, initial=0.0))),
        equilibrium_type,
    )


@dataclass(frozen=True)
class NoRegretResult:
    empirical_distribution: np.ndarray
    row_average_regret: float
    column_average_regret: float
    cce_violation: float
    iterations: int


def multiplicative_weights_bimatrix(
    row_payoff: Sequence[Sequence[float]],
    column_payoff: Sequence[Sequence[float]],
    *,
    iterations: int = 20_000,
    learning_rate: float | None = None,
) -> NoRegretResult:
    """Full-information multiplicative weights and empirical CCE diagnostics."""

    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or row.shape != column.shape
        or min(row.shape) == 0
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or iterations <= 0
    ):
        raise ValueError("no-regret game inputs are invalid")
    if learning_rate is None:
        payoff_range = max(
            float(np.ptp(row)), float(np.ptp(column)), 1e-12
        )
        learning_rate = np.sqrt(
            2.0 * np.log(max(row.shape)) / iterations
        ) / payoff_range
    if not isfinite(learning_rate) or learning_rate <= 0.0:
        raise ValueError("learning rate must be positive and finite")
    row_log_weights = np.zeros(row.shape[0])
    column_log_weights = np.zeros(row.shape[1])
    empirical = np.zeros_like(row)
    row_actual = 0.0
    column_actual = 0.0
    row_counterfactual = np.zeros(row.shape[0])
    column_counterfactual = np.zeros(row.shape[1])
    row_scale = max(float(np.ptp(row)), 1.0)
    column_scale = max(float(np.ptp(column)), 1.0)
    for _ in range(iterations):
        row_strategy = np.exp(row_log_weights - logsumexp_local(row_log_weights))
        column_strategy = np.exp(
            column_log_weights - logsumexp_local(column_log_weights)
        )
        joint = np.outer(row_strategy, column_strategy)
        empirical += joint
        row_action_values = row @ column_strategy
        column_action_values = row_strategy @ column
        row_value = float(row_strategy @ row_action_values)
        column_value = float(column_action_values @ column_strategy)
        row_actual += row_value
        column_actual += column_value
        row_counterfactual += row_action_values
        column_counterfactual += column_action_values
        row_log_weights += learning_rate * row_action_values / row_scale
        column_log_weights += learning_rate * column_action_values / column_scale
    empirical /= iterations
    row_regret = max(0.0, float(np.max(row_counterfactual) - row_actual))
    column_regret = max(
        0.0, float(np.max(column_counterfactual) - column_actual)
    )
    return NoRegretResult(
        empirical,
        row_regret / iterations,
        column_regret / iterations,
        max(row_regret, column_regret) / iterations,
        iterations,
    )


def logsumexp_local(values: np.ndarray) -> float:
    maximum = float(np.max(values))
    return maximum + float(np.log(np.exp(values - maximum).sum()))


@dataclass(frozen=True)
class MultiFollowerStackelbergResult:
    leader_strategy: np.ndarray
    follower_response: tuple[int, ...]
    leader_value: float
    follower_values: tuple[float, ...]
    incentive_slacks: tuple[float, ...]


def solve_multi_follower_stackelberg(
    leader_payoff: Sequence,
    follower_payoffs: Sequence[Sequence],
) -> MultiFollowerStackelbergResult:
    """Optimistic commitment inducing a pure Nash response among followers."""

    leader = np.asarray(leader_payoff, dtype=np.float64)
    followers = tuple(np.asarray(value, dtype=np.float64) for value in follower_payoffs)
    if (
        leader.ndim < 2
        or not followers
        or len(followers) != leader.ndim - 1
        or any(value.shape != leader.shape for value in followers)
        or any(np.any(~np.isfinite(value)) for value in (leader, *followers))
        or min(leader.shape) == 0
    ):
        raise ValueError("multi-follower Stackelberg arrays are inconsistent")
    leader_actions = leader.shape[0]
    follower_counts = leader.shape[1:]
    candidates = []
    for response in product(*(range(count) for count in follower_counts)):
        inequalities = []
        for follower_index, follower in enumerate(followers):
            current = (slice(None), *response)
            current_payoff = follower[current]
            for alternative in range(follower_counts[follower_index]):
                if alternative == response[follower_index]:
                    continue
                deviated = list(response)
                deviated[follower_index] = alternative
                deviation_payoff = follower[(slice(None), *deviated)]
                inequalities.append(deviation_payoff - current_payoff)
        solved = linprog(
            -leader[(slice(None), *response)],
            A_ub=np.asarray(inequalities) if inequalities else None,
            b_ub=np.zeros(len(inequalities)) if inequalities else None,
            A_eq=np.ones((1, leader_actions)),
            b_eq=np.ones(1),
            bounds=[(0.0, 1.0)] * leader_actions,
            method="highs",
        )
        if not solved.success or solved.x is None:
            continue
        strategy = np.maximum(solved.x, 0.0)
        strategy /= strategy.sum()
        slacks = []
        for follower_index, follower in enumerate(followers):
            current_value = float(strategy @ follower[(slice(None), *response)])
            best_deviation = current_value
            for alternative in range(follower_counts[follower_index]):
                deviated = list(response)
                deviated[follower_index] = alternative
                best_deviation = max(
                    best_deviation,
                    float(strategy @ follower[(slice(None), *deviated)]),
                )
            slacks.append(current_value - best_deviation)
        candidates.append(
            MultiFollowerStackelbergResult(
                strategy,
                tuple(int(value) for value in response),
                float(strategy @ leader[(slice(None), *response)]),
                tuple(
                    float(strategy @ follower[(slice(None), *response)])
                    for follower in followers
                ),
                tuple(slacks),
            )
        )
    if not candidates:
        raise RuntimeError("no inducible pure follower Nash response exists")
    return max(
        candidates,
        key=lambda result: (
            result.leader_value,
            sum(result.follower_values),
            tuple(-value for value in result.follower_response),
        ),
    )


@dataclass(frozen=True)
class DynamicStackelbergResult:
    leader_policy: np.ndarray
    follower_policy: np.ndarray
    leader_value: float
    follower_value: float
    tie_breaking: str
    policies_evaluated: int


def solve_dynamic_stackelberg(
    transition: Sequence,
    leader_reward: Sequence,
    follower_reward: Sequence,
    initial_distribution: Sequence[float],
    *,
    horizon: int,
    discount: float = 1.0,
    tie_breaking: str = "strong",
    max_policies: int = 1_000_000,
) -> DynamicStackelbergResult:
    """Enumerate deterministic Markov commitments in a finite-horizon game."""

    kernel = np.asarray(transition, dtype=np.float64)
    leader = np.asarray(leader_reward, dtype=np.float64)
    follower = np.asarray(follower_reward, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    if kernel.ndim != 4:
        raise ValueError("dynamic Stackelberg transition must be four-dimensional")
    states, leader_actions, follower_actions, next_states = kernel.shape
    if (
        next_states != states
        or leader.shape != (states, leader_actions, follower_actions)
        or follower.shape != leader.shape
        or initial.shape != (states,)
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(leader))
        or np.any(~np.isfinite(follower))
        or np.any(~np.isfinite(initial))
        or np.any(kernel < 0.0)
        or np.any(initial < 0.0)
        or not np.allclose(kernel.sum(axis=3), 1.0)
        or not np.isclose(initial.sum(), 1.0)
        or horizon <= 0
        or not 0.0 <= discount <= 1.0
        or tie_breaking not in {"strong", "weak"}
        or max_policies <= 0
    ):
        raise ValueError("dynamic Stackelberg inputs are invalid")
    policy_count = leader_actions ** (states * horizon)
    if policy_count > max_policies:
        raise ValueError("dynamic Stackelberg policy budget exceeded")
    best = None
    best_score = None
    for flat_policy in product(range(leader_actions), repeat=states * horizon):
        leader_policy = np.asarray(flat_policy, dtype=np.int64).reshape(horizon, states)
        follower_policy = np.zeros((horizon, states), dtype=np.int64)
        leader_next = np.zeros(states)
        follower_next = np.zeros(states)
        for time in range(horizon - 1, -1, -1):
            leader_value = np.zeros(states)
            follower_value = np.zeros(states)
            for state in range(states):
                leader_action = leader_policy[time, state]
                follower_values = follower[state, leader_action] + discount * (
                    kernel[state, leader_action] @ follower_next
                )
                leader_values = leader[state, leader_action] + discount * (
                    kernel[state, leader_action] @ leader_next
                )
                maximum = float(np.max(follower_values))
                responses = np.flatnonzero(
                    follower_values >= maximum - 1e-12
                )
                if tie_breaking == "strong":
                    response = int(
                        max(responses, key=lambda value: (leader_values[value], -value))
                    )
                else:
                    response = int(
                        min(responses, key=lambda value: (leader_values[value], value))
                    )
                follower_policy[time, state] = response
                follower_value[state] = follower_values[response]
                leader_value[state] = leader_values[response]
            leader_next = leader_value
            follower_next = follower_value
        candidate_leader = float(initial @ leader_next)
        candidate_follower = float(initial @ follower_next)
        score = (
            candidate_leader,
            candidate_follower,
            tuple(-value for value in flat_policy),
        )
        if best is None or score > best_score:
            best = DynamicStackelbergResult(
                leader_policy.copy(),
                follower_policy.copy(),
                candidate_leader,
                candidate_follower,
                tie_breaking,
                policy_count,
            )
            best_score = score
    if best is None:
        raise RuntimeError("no dynamic Stackelberg policy was enumerated")
    return best
