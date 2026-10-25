"""P33 tabular FQE/FQI/CQL, occupancy ratios, and offline-RL diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.special import softmax


@dataclass(frozen=True)
class OfflineBatch:
    states: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    next_states: np.ndarray
    terminals: np.ndarray
    state_count: int
    action_count: int


def make_offline_batch(
    states: Sequence[int],
    actions: Sequence[int],
    rewards: Sequence[float],
    next_states: Sequence[int],
    terminals: Sequence[bool],
    *,
    state_count: int,
    action_count: int,
) -> OfflineBatch:
    arrays = (
        np.asarray(states, dtype=np.int64),
        np.asarray(actions, dtype=np.int64),
        np.asarray(rewards, dtype=np.float64),
        np.asarray(next_states, dtype=np.int64),
        np.asarray(terminals, dtype=bool),
    )
    if (
        state_count < 1
        or action_count < 1
        or any(value.ndim != 1 for value in arrays)
        or len({value.size for value in arrays}) != 1
        or arrays[0].size == 0
        or np.any(~np.isfinite(arrays[2]))
        or np.any(arrays[0] < 0)
        or np.any(arrays[0] >= state_count)
        or np.any(arrays[3] < 0)
        or np.any(arrays[3] >= state_count)
        or np.any(arrays[1] < 0)
        or np.any(arrays[1] >= action_count)
    ):
        raise ValueError("offline batch is invalid")
    return OfflineBatch(*arrays, state_count, action_count)


def _policy(policy: Sequence, states: int, actions: int) -> np.ndarray:
    result = np.asarray(policy, dtype=np.float64)
    if (
        result.shape != (states, actions)
        or np.any(~np.isfinite(result))
        or np.any(result < 0.0)
        or not np.allclose(result.sum(axis=1), 1.0)
    ):
        raise ValueError("policy must be row-normalized")
    return result


@dataclass(frozen=True)
class FittedQResult:
    q_values: np.ndarray
    policy: np.ndarray
    observed: np.ndarray
    residuals: np.ndarray
    iterations: int


def fitted_q_evaluation(
    batch: OfflineBatch,
    evaluation_policy: Sequence,
    *,
    discount: float,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> FittedQResult:
    """Tabular FQE with empirical least-squares Bellman regression."""

    policy = _policy(evaluation_policy, batch.state_count, batch.action_count)
    if not 0.0 <= discount < 1.0 or tolerance <= 0.0 or max_iterations < 1:
        raise ValueError("FQE settings are invalid")
    q_values = np.zeros((batch.state_count, batch.action_count))
    counts = np.zeros_like(q_values)
    np.add.at(counts, (batch.states, batch.actions), 1.0)
    observed = counts > 0.0
    residuals = []
    for _ in range(max_iterations):
        next_value = np.sum(policy[batch.next_states] * q_values[batch.next_states], axis=1)
        targets = batch.rewards + discount * (~batch.terminals) * next_value
        sums = np.zeros_like(q_values)
        np.add.at(sums, (batch.states, batch.actions), targets)
        updated = np.zeros_like(q_values)
        updated[observed] = sums[observed] / counts[observed]
        residuals.append(float(np.max(np.abs(updated - q_values))))
        q_values = updated
        if residuals[-1] <= tolerance:
            break
    return FittedQResult(q_values, policy, observed, np.asarray(residuals), len(residuals))


def fitted_q_iteration(
    batch: OfflineBatch,
    *,
    discount: float,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> FittedQResult:
    """Tabular FQI; unobserved state-actions retain the neutral zero estimate."""

    if not 0.0 <= discount < 1.0 or tolerance <= 0.0 or max_iterations < 1:
        raise ValueError("FQI settings are invalid")
    q_values = np.zeros((batch.state_count, batch.action_count))
    counts = np.zeros_like(q_values)
    np.add.at(counts, (batch.states, batch.actions), 1.0)
    observed = counts > 0.0
    residuals = []
    for _ in range(max_iterations):
        targets = batch.rewards + discount * (~batch.terminals) * np.max(
            q_values[batch.next_states], axis=1
        )
        sums = np.zeros_like(q_values)
        np.add.at(sums, (batch.states, batch.actions), targets)
        updated = np.zeros_like(q_values)
        updated[observed] = sums[observed] / counts[observed]
        residuals.append(float(np.max(np.abs(updated - q_values))))
        q_values = updated
        if residuals[-1] <= tolerance:
            break
    greedy = np.zeros_like(q_values)
    greedy[np.arange(batch.state_count), np.argmax(q_values, axis=1)] = 1.0
    return FittedQResult(q_values, greedy, observed, np.asarray(residuals), len(residuals))


@dataclass(frozen=True)
class CQLResult:
    q_values: np.ndarray
    policy: np.ndarray
    conservative_gaps: np.ndarray
    losses: np.ndarray


def conservative_q_learning(
    batch: OfflineBatch,
    *,
    discount: float,
    alpha: float,
    learning_rate: float = 0.05,
    iterations: int = 2_000,
) -> CQLResult:
    """Small tabular CQL optimizer with Bellman and log-sum-exp penalties."""

    if (
        not 0.0 <= discount < 1.0
        or not isfinite(alpha)
        or alpha < 0.0
        or not isfinite(learning_rate)
        or learning_rate <= 0.0
        or iterations < 1
    ):
        raise ValueError("CQL settings are invalid")
    q_values = np.zeros((batch.state_count, batch.action_count))
    counts = np.zeros_like(q_values)
    np.add.at(counts, (batch.states, batch.actions), 1.0)
    state_counts = counts.sum(axis=1)
    action_frequency = np.divide(
        counts,
        state_counts[:, None],
        out=np.zeros_like(counts),
        where=state_counts[:, None] > 0.0,
    )
    losses = []
    for _ in range(iterations):
        target = batch.rewards + discount * (~batch.terminals) * np.max(
            q_values[batch.next_states], axis=1
        )
        error = q_values[batch.states, batch.actions] - target
        gradient = np.zeros_like(q_values)
        np.add.at(gradient, (batch.states, batch.actions), error)
        gradient = np.divide(
            gradient,
            np.maximum(counts, 1.0),
            out=np.zeros_like(gradient),
            where=counts > 0.0,
        )
        active = state_counts > 0.0
        conservative = np.zeros_like(q_values)
        conservative[active] = softmax(q_values[active], axis=1) - action_frequency[active]
        gradient += alpha * conservative
        q_values -= learning_rate * gradient
        log_partition = np.logaddexp.reduce(q_values[active], axis=1)
        data_value = np.sum(action_frequency[active] * q_values[active], axis=1)
        losses.append(float(0.5 * np.mean(error**2) + alpha * np.mean(log_partition - data_value)))
    policy = np.zeros_like(q_values)
    policy[np.arange(batch.state_count), np.argmax(q_values, axis=1)] = 1.0
    gaps = np.full(batch.state_count, np.nan)
    active = state_counts > 0.0
    gaps[active] = np.logaddexp.reduce(q_values[active], axis=1) - np.sum(
        action_frequency[active] * q_values[active], axis=1
    )
    return CQLResult(q_values, policy, gaps, np.asarray(losses))


def _mdp_arrays(transition: Sequence, policy: Sequence, initial: Sequence[float]):
    dynamics = np.asarray(transition, dtype=np.float64)
    if dynamics.ndim != 3:
        raise ValueError("transition must have state, action, and next-state axes")
    states, actions, next_states = dynamics.shape
    start = np.asarray(initial, dtype=np.float64)
    chosen = _policy(policy, states, actions)
    if (
        states == 0
        or next_states != states
        or start.shape != (states,)
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=2), 1.0)
        or np.any(~np.isfinite(start))
        or np.any(start < 0.0)
        or not np.isclose(start.sum(), 1.0)
    ):
        raise ValueError("MDP occupancy inputs are invalid")
    return dynamics, chosen, start


def discounted_state_action_occupancy(
    transition: Sequence,
    policy: Sequence,
    initial: Sequence[float],
    *,
    discount: float,
) -> np.ndarray:
    """Normalized discounted occupancy with total mass one."""

    dynamics, chosen, start = _mdp_arrays(transition, policy, initial)
    if not 0.0 <= discount < 1.0:
        raise ValueError("discount must lie in [0, 1)")
    policy_transition = np.einsum("sa,sak->sk", chosen, dynamics)
    state_occupancy = np.linalg.solve(
        np.eye(start.size) - discount * policy_transition.T,
        (1.0 - discount) * start,
    )
    return state_occupancy[:, None] * chosen


@dataclass(frozen=True)
class OccupancyRatioResult:
    target_occupancy: np.ndarray
    behavior_occupancy: np.ndarray
    density_ratio: np.ndarray
    concentrability: float
    unsupported_mass: float


def discounted_occupancy_ratio(
    transition: Sequence,
    target_policy: Sequence,
    behavior_policy: Sequence,
    initial: Sequence[float],
    *,
    discount: float,
) -> OccupancyRatioResult:
    """Exact tabular marginalized density ratios, the population DICE target."""

    target = discounted_state_action_occupancy(
        transition, target_policy, initial, discount=discount
    )
    behavior = discounted_state_action_occupancy(
        transition, behavior_policy, initial, discount=discount
    )
    unsupported = float(target[behavior <= 0.0].sum())
    ratio = np.divide(
        target,
        behavior,
        out=np.full_like(target, np.inf),
        where=behavior > 0.0,
    )
    ratio[(target == 0.0) & (behavior == 0.0)] = 0.0
    finite = ratio[np.isfinite(ratio)]
    concentrability = float(np.max(finite)) if unsupported == 0.0 else float("inf")
    return OccupancyRatioResult(target, behavior, ratio, concentrability, unsupported)


def marginalized_importance_value(
    behavior_occupancy: Sequence,
    density_ratio: Sequence,
    rewards: Sequence,
    *,
    discount: float,
) -> float:
    """Return discounted value from exact or estimated marginal ratios."""

    behavior = np.asarray(behavior_occupancy, dtype=np.float64)
    ratio = np.asarray(density_ratio, dtype=np.float64)
    payoff = np.asarray(rewards, dtype=np.float64)
    if (
        behavior.shape != ratio.shape
        or behavior.shape != payoff.shape
        or np.any(~np.isfinite(behavior))
        or np.any(~np.isfinite(ratio))
        or np.any(~np.isfinite(payoff))
        or np.any(behavior < 0.0)
        or np.any(ratio < 0.0)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("marginal importance inputs are invalid")
    return float(np.sum(behavior * ratio * payoff) / (1.0 - discount))


@dataclass(frozen=True)
class BellmanCompletenessDiagnostic:
    coefficients: np.ndarray
    fitted_backup: np.ndarray
    maximum_residual: float
    root_mean_square_residual: float


def linear_bellman_completeness_diagnostic(
    features: Sequence,
    bellman_backup: Sequence[float],
) -> BellmanCompletenessDiagnostic:
    """Project a Bellman backup into a supplied linear function class."""

    design = np.asarray(features, dtype=np.float64)
    target = np.asarray(bellman_backup, dtype=np.float64)
    if (
        design.ndim != 2
        or design.shape[0] == 0
        or target.shape != (design.shape[0],)
        or np.any(~np.isfinite(design))
        or np.any(~np.isfinite(target))
    ):
        raise ValueError("Bellman-completeness inputs are invalid")
    coefficients, *_ = np.linalg.lstsq(design, target, rcond=None)
    fitted = design @ coefficients
    residual = fitted - target
    return BellmanCompletenessDiagnostic(
        coefficients,
        fitted,
        float(np.max(np.abs(residual))),
        float(np.sqrt(np.mean(residual**2))),
    )
