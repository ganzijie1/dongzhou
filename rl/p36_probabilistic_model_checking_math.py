"""P36 PCTL/CSL kernels, probabilistic automata, and statistical checking."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, exp, isfinite, log, sqrt
from typing import Sequence

import numpy as np


def _stochastic_matrix(transition: Sequence) -> np.ndarray:
    matrix = np.asarray(transition, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[0] != matrix.shape[1]
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix.sum(axis=1), 1.0)
    ):
        raise ValueError("transition must be a square stochastic matrix")
    return matrix


@dataclass(frozen=True)
class ReachabilityResult:
    probabilities: np.ndarray
    residual: float
    iterations: int
    policy: np.ndarray | None = None


def dtmc_reachability(
    transition: Sequence,
    targets: Sequence[bool],
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100_000,
) -> ReachabilityResult:
    """Least fixed point for unbounded DTMC reachability."""

    matrix = _stochastic_matrix(transition)
    target = np.asarray(targets, dtype=bool)
    if target.shape != (matrix.shape[0],) or tolerance <= 0.0 or max_iterations < 1:
        raise ValueError("DTMC reachability settings are invalid")
    value = target.astype(np.float64)
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        updated = value.copy()
        updated[~target] = matrix[~target] @ value
        residual = float(np.max(np.abs(updated - value)))
        value = updated
        if residual <= tolerance:
            break
    return ReachabilityResult(value, residual, iteration)


def mdp_reachability(
    transition: Sequence,
    targets: Sequence[bool],
    *,
    maximize: bool,
    enabled: Sequence | None = None,
    tolerance: float = 1e-12,
    max_iterations: int = 100_000,
) -> ReachabilityResult:
    """PCTL min/max reachability for a finite MDP or probabilistic automaton."""

    dynamics = np.asarray(transition, dtype=np.float64)
    if dynamics.ndim != 3:
        raise ValueError("MDP transition must have state, action, next-state axes")
    states, actions, next_states = dynamics.shape
    target = np.asarray(targets, dtype=bool)
    mask = np.ones((states, actions), dtype=bool) if enabled is None else np.asarray(enabled, dtype=bool)
    if (
        states == 0
        or next_states != states
        or target.shape != (states,)
        or mask.shape != (states, actions)
        or np.any(~mask.any(axis=1))
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=2)[mask], 1.0)
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("MDP reachability inputs are invalid")
    value = target.astype(np.float64)
    policy = np.zeros(states, dtype=np.int64)
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        q_values = np.einsum("sak,k->sa", dynamics, value)
        q_values[~mask] = -np.inf if maximize else np.inf
        chosen = np.argmax(q_values, axis=1) if maximize else np.argmin(q_values, axis=1)
        updated = q_values[np.arange(states), chosen]
        updated[target] = 1.0
        residual = float(np.max(np.abs(updated - value)))
        value = updated
        policy = chosen
        if residual <= tolerance:
            break
    return ReachabilityResult(value, residual, iteration, policy)


def pctl_bounded_until(
    transition: Sequence,
    invariant: Sequence[bool],
    targets: Sequence[bool],
    *,
    steps: int,
) -> np.ndarray:
    """DTMC probability of invariant U^{<=steps} target."""

    matrix = _stochastic_matrix(transition)
    allowed = np.asarray(invariant, dtype=bool)
    target = np.asarray(targets, dtype=bool)
    if allowed.shape != target.shape or target.shape != (matrix.shape[0],) or steps < 0:
        raise ValueError("bounded-until inputs are invalid")
    value = target.astype(np.float64)
    active = allowed & ~target
    for _ in range(steps):
        updated = target.astype(np.float64)
        updated[active] = matrix[active] @ value
        value = updated
    return value


def _generator(matrix: Sequence) -> np.ndarray:
    generator = np.asarray(matrix, dtype=np.float64)
    if (
        generator.ndim != 2
        or generator.shape[0] == 0
        or generator.shape[0] != generator.shape[1]
        or np.any(~np.isfinite(generator))
        or np.any(generator - np.diag(np.diag(generator)) < -1e-12)
        or np.any(np.diag(generator) > 1e-12)
        or not np.allclose(generator.sum(axis=1), 0.0)
    ):
        raise ValueError("CTMC generator is invalid")
    return generator


@dataclass(frozen=True)
class UniformizationResult:
    distribution: np.ndarray
    rate: float
    poisson_terms: int
    truncated_mass: float


def ctmc_uniformization(
    generator: Sequence,
    initial: Sequence[float],
    *,
    time: float,
    tolerance: float = 1e-13,
    max_terms: int = 1_000_000,
) -> UniformizationResult:
    """Transient CTMC distribution using uniformization."""

    q_matrix = _generator(generator)
    start = np.asarray(initial, dtype=np.float64)
    if (
        start.shape != (q_matrix.shape[0],)
        or np.any(~np.isfinite(start))
        or np.any(start < 0.0)
        or not np.isclose(start.sum(), 1.0)
        or not isfinite(time)
        or time < 0.0
        or tolerance <= 0.0
        or max_terms < 1
    ):
        raise ValueError("uniformization inputs are invalid")
    rate = float(np.max(-np.diag(q_matrix)))
    if time == 0.0 or rate == 0.0:
        return UniformizationResult(start.copy(), rate, 1, 0.0)
    embedded = np.eye(q_matrix.shape[0]) + q_matrix / rate
    mean = rate * time
    poisson = exp(-mean)
    cumulative = poisson
    power = start.copy()
    result = poisson * power
    terms = 1
    while 1.0 - cumulative > tolerance and terms < max_terms:
        power = power @ embedded
        poisson *= mean / terms
        result += poisson * power
        cumulative += poisson
        terms += 1
    if terms == max_terms and 1.0 - cumulative > tolerance:
        raise RuntimeError("uniformization Poisson truncation did not converge")
    result = np.maximum(result, 0.0)
    result /= result.sum()
    return UniformizationResult(result, rate, terms, max(0.0, 1.0 - cumulative))


def csl_time_bounded_reachability(
    generator: Sequence,
    targets: Sequence[bool],
    *,
    time: float,
    tolerance: float = 1e-13,
) -> np.ndarray:
    """CSL F^[0,time] target probabilities by making targets absorbing."""

    q_matrix = _generator(generator).copy()
    target = np.asarray(targets, dtype=bool)
    if target.shape != (q_matrix.shape[0],):
        raise ValueError("CSL target mask is invalid")
    q_matrix[target] = 0.0
    probabilities = np.empty(q_matrix.shape[0])
    for state in range(q_matrix.shape[0]):
        start = np.zeros(q_matrix.shape[0])
        start[state] = 1.0
        transient = ctmc_uniformization(
            q_matrix, start, time=time, tolerance=tolerance
        ).distribution
        probabilities[state] = transient[target].sum()
    return probabilities


@dataclass(frozen=True)
class SMCResult:
    estimate: float
    lower: float
    upper: float
    samples: int


def statistical_model_check(
    outcomes: Sequence[bool], *, delta: float
) -> SMCResult:
    """Bernoulli estimate with a fixed-sample Hoeffding confidence interval."""

    values = np.asarray(outcomes, dtype=np.float64)
    if (
        values.ndim != 1
        or values.size == 0
        or np.any((values != 0.0) & (values != 1.0))
        or not 0.0 < delta < 1.0
    ):
        raise ValueError("SMC outcomes or confidence are invalid")
    estimate = float(values.mean())
    radius = sqrt(log(2.0 / delta) / (2.0 * values.size))
    return SMCResult(
        estimate,
        max(0.0, estimate - radius),
        min(1.0, estimate + radius),
        values.size,
    )


def hoeffding_sample_size(*, epsilon: float, delta: float) -> int:
    if not 0.0 < epsilon < 1.0 or not 0.0 < delta < 1.0:
        raise ValueError("epsilon and delta must lie in (0, 1)")
    return ceil(log(2.0 / delta) / (2.0 * epsilon**2))


@dataclass(frozen=True)
class SPRTResult:
    decision: str
    samples: int
    log_likelihood_ratio: float


def sequential_probability_ratio_test(
    outcomes: Sequence[bool],
    *,
    null_probability: float,
    alternative_probability: float,
    alpha: float,
    beta: float,
) -> SPRTResult:
    """Wald test for H0:p>=p0 versus H1:p<=p1, with p1<p0."""

    values = np.asarray(outcomes, dtype=np.float64)
    if (
        values.ndim != 1
        or values.size == 0
        or np.any((values != 0.0) & (values != 1.0))
        or not 0.0 < alternative_probability < null_probability < 1.0
        or not 0.0 < alpha < 1.0
        or not 0.0 < beta < 1.0
    ):
        raise ValueError("SPRT inputs are invalid")
    lower = log(beta / (1.0 - alpha))
    upper = log((1.0 - beta) / alpha)
    ratio = 0.0
    for index, value in enumerate(values, start=1):
        ratio += value * log(alternative_probability / null_probability)
        ratio += (1.0 - value) * log(
            (1.0 - alternative_probability) / (1.0 - null_probability)
        )
        if ratio <= lower:
            return SPRTResult("accept_null", index, ratio)
        if ratio >= upper:
            return SPRTResult("accept_alternative", index, ratio)
    return SPRTResult("continue", values.size, ratio)
