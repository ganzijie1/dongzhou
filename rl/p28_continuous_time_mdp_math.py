"""P28 continuous-time MDPs and uniformization."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.stats import poisson


def _generators(value: Sequence) -> np.ndarray:
    generators = np.asarray(value, dtype=np.float64)
    if generators.ndim == 2:
        generators = generators[:, None, :]
    if (
        generators.ndim != 3
        or generators.shape[0] != generators.shape[2]
        or np.any(~np.isfinite(generators))
    ):
        raise ValueError("generator array must have shape [state, action, state]")
    states, actions, _ = generators.shape
    diagonal = np.arange(states)
    off_diagonal = generators.copy()
    off_diagonal[diagonal, :, diagonal] = 0.0
    if (
        np.any(off_diagonal < -1e-12)
        or np.any(generators[diagonal, :, diagonal] > 1e-12)
        or not np.allclose(generators.sum(axis=2), 0.0, atol=1e-10)
        or actions < 1
    ):
        raise ValueError("each action matrix must be a conservative generator")
    return generators


@dataclass(frozen=True)
class UniformizedCTMDP:
    transition: np.ndarray
    rate: float
    exit_rates: np.ndarray


def uniformize_ctmdp(
    generators: Sequence,
    *,
    rate: float | None = None,
) -> UniformizedCTMDP:
    """Convert action generators to discrete kernels with a shared clock."""

    matrix = _generators(generators)
    states = matrix.shape[0]
    exit_rates = -matrix[np.arange(states), :, np.arange(states)]
    minimum_rate = float(np.max(exit_rates))
    clock = minimum_rate if rate is None else float(rate)
    if not isfinite(clock) or clock < minimum_rate - 1e-12 or clock < 0.0:
        raise ValueError("uniformization rate must dominate every exit rate")
    if clock == 0.0:
        transition = np.broadcast_to(
            np.eye(states)[:, None, :], matrix.shape
        ).copy()
    else:
        transition = matrix / clock
        transition[np.arange(states), :, np.arange(states)] += 1.0
        transition = np.maximum(transition, 0.0)
        transition /= transition.sum(axis=2, keepdims=True)
    return UniformizedCTMDP(transition, clock, exit_rates)


@dataclass(frozen=True)
class DiscountedCTMDPResult:
    values: np.ndarray
    policy: np.ndarray
    residual: float
    iterations: int
    uniformization_rate: float
    discrete_discount: float


def discounted_ctmdp_value_iteration(
    generators: Sequence,
    reward_rates: Sequence,
    *,
    discount_rate: float,
    uniformization_rate: float | None = None,
    tolerance: float = 1e-10,
    max_iterations: int = 100_000,
) -> DiscountedCTMDPResult:
    """Solve ``beta V = max_a(r + Q_a V)`` by uniformization."""

    matrix = _generators(generators)
    rewards = np.asarray(reward_rates, dtype=np.float64)
    if (
        rewards.shape != matrix.shape[:2]
        or np.any(~np.isfinite(rewards))
        or not isfinite(discount_rate)
        or discount_rate <= 0.0
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("discounted CTMDP settings are invalid")
    model = uniformize_ctmdp(matrix, rate=uniformization_rate)
    denominator = discount_rate + model.rate
    gamma = 0.0 if model.rate == 0.0 else model.rate / denominator
    values = np.zeros(matrix.shape[0])
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        action_values = rewards / denominator + gamma * np.einsum(
            "san,n->sa", model.transition, values
        )
        updated = np.max(action_values, axis=1)
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        if residual <= tolerance * (1.0 - gamma):
            break
    action_values = rewards + np.einsum("san,n->sa", matrix, values)
    policy = np.argmax(action_values, axis=1)
    hjb_residual = float(
        np.max(np.abs(discount_rate * values - np.max(action_values, axis=1)))
    )
    return DiscountedCTMDPResult(
        values, policy, hjb_residual, iteration, model.rate, gamma
    )


def evaluate_ctmdp_policy(
    generators: Sequence,
    reward_rates: Sequence,
    policy: Sequence[int],
    *,
    discount_rate: float,
) -> np.ndarray:
    """Evaluate a deterministic stationary CTMDP policy exactly."""

    matrix = _generators(generators)
    rewards = np.asarray(reward_rates, dtype=np.float64)
    strategy = np.asarray(policy, dtype=np.int64)
    states, actions = matrix.shape[:2]
    if (
        rewards.shape != (states, actions)
        or strategy.shape != (states,)
        or np.any(strategy < 0)
        or np.any(strategy >= actions)
        or not isfinite(discount_rate)
        or discount_rate <= 0.0
    ):
        raise ValueError("CTMDP policy-evaluation inputs are invalid")
    chosen = matrix[np.arange(states), strategy]
    chosen_reward = rewards[np.arange(states), strategy]
    return np.linalg.solve(
        discount_rate * np.eye(states) - chosen,
        chosen_reward,
    )


@dataclass(frozen=True)
class AverageRewardCTMDPResult:
    gain: float
    bias: np.ndarray
    policy: np.ndarray
    span_residual: float
    iterations: int
    uniformization_rate: float


def average_reward_ctmdp(
    generators: Sequence,
    reward_rates: Sequence,
    *,
    reference_state: int = 0,
    uniformization_rate: float | None = None,
    tolerance: float = 1e-10,
    max_iterations: int = 100_000,
) -> AverageRewardCTMDPResult:
    """Relative value iteration for communicating average-reward CTMDPs."""

    matrix = _generators(generators)
    rewards = np.asarray(reward_rates, dtype=np.float64)
    states = matrix.shape[0]
    if (
        rewards.shape != matrix.shape[:2]
        or np.any(~np.isfinite(rewards))
        or not 0 <= reference_state < states
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("average-reward CTMDP settings are invalid")
    model = uniformize_ctmdp(matrix, rate=uniformization_rate)
    if model.rate == 0.0:
        policy = np.argmax(rewards, axis=1)
        gains = rewards[np.arange(states), policy]
        if not np.allclose(gains, gains[reference_state]):
            raise ValueError("zero-rate model is not communicating with one gain")
        return AverageRewardCTMDPResult(
            float(gains[reference_state]), np.zeros(states), policy, 0.0, 1, 0.0
        )
    bias = np.zeros(states)
    span_residual = float("inf")
    gain = 0.0
    for iteration in range(1, max_iterations + 1):
        action_values = rewards / model.rate + np.einsum(
            "san,n->sa", model.transition, bias
        )
        raw = np.max(action_values, axis=1)
        increment = raw - bias
        span_residual = float(np.max(increment) - np.min(increment))
        gain = model.rate * float(raw[reference_state])
        bias = raw - raw[reference_state]
        if span_residual <= tolerance:
            break
    policy = np.argmax(
        rewards + np.einsum("san,n->sa", matrix, bias), axis=1
    )
    return AverageRewardCTMDPResult(
        gain, bias, policy, span_residual, iteration, model.rate
    )


def uniformized_transient_distribution(
    generator: Sequence,
    initial: Sequence[float],
    time: float,
    *,
    tolerance: float = 1e-13,
    max_terms: int = 100_000,
) -> tuple[np.ndarray, float, int]:
    """Compute ``p(0) exp(Qt)`` by the uniformization Poisson series."""

    matrix = _generators(generator)
    if matrix.shape[1] != 1:
        raise ValueError("transient propagation needs one fixed-policy generator")
    start = np.asarray(initial, dtype=np.float64)
    states = matrix.shape[0]
    if (
        start.shape != (states,)
        or np.any(~np.isfinite(start))
        or np.any(start < 0.0)
        or not np.isclose(start.sum(), 1.0)
        or not isfinite(time)
        or time < 0.0
        or tolerance <= 0.0
        or max_terms < 1
    ):
        raise ValueError("transient-distribution inputs are invalid")
    model = uniformize_ctmdp(matrix)
    if time == 0.0 or model.rate == 0.0:
        return start.copy(), 0.0, 1
    kernel = model.transition[:, 0, :]
    mean = model.rate * time
    lower = max(0, int(poisson.ppf(tolerance / 2.0, mean)))
    upper = int(poisson.ppf(1.0 - tolerance / 2.0, mean))
    if upper - lower + 1 > max_terms:
        raise ValueError("uniformization series did not reach the tolerance")
    state = start @ np.linalg.matrix_power(kernel, lower)
    weight = float(poisson.pmf(lower, mean))
    result = weight * state
    cumulative = weight
    for term in range(lower + 1, upper + 1):
        state = state @ kernel
        weight = float(poisson.pmf(term, mean))
        result += weight * state
        cumulative += weight
    omitted = float(poisson.cdf(lower - 1, mean) + poisson.sf(upper, mean))
    if omitted > tolerance:
        raise ValueError("uniformization series did not reach the tolerance")
    result = np.maximum(result, 0.0)
    result /= result.sum()
    return result, omitted, upper - lower + 1
