"""P35 Donsker-Varadhan duality, large deviations, and risk-sensitive DP."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp


def _probability(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if (
        result.ndim != 1
        or result.size == 0
        or np.any(~np.isfinite(result))
        or np.any(result < 0.0)
        or not np.isclose(result.sum(), 1.0)
    ):
        raise ValueError(f"{name} must be a finite probability vector")
    return result


def discrete_kl(first: Sequence[float], second: Sequence[float]) -> float:
    """KL(first || second), including infinite support-mismatch cost."""

    p = _probability(first, "first distribution")
    q = _probability(second, "second distribution")
    if p.shape != q.shape:
        raise ValueError("KL distributions must have equal shape")
    if np.any((p > 0.0) & (q == 0.0)):
        return float("inf")
    active = p > 0.0
    return float(np.sum(p[active] * np.log(p[active] / q[active])))


@dataclass(frozen=True)
class DVResult:
    log_moment: float
    tilted_distribution: np.ndarray
    variational_value: float
    kl_cost: float


def donsker_varadhan_discrete(
    reference: Sequence[float], payoff: Sequence[float]
) -> DVResult:
    """Exact finite-space Donsker-Varadhan optimizer."""

    probability = _probability(reference, "reference")
    values = np.asarray(payoff, dtype=np.float64)
    if values.shape != probability.shape or np.any(~np.isfinite(values)):
        raise ValueError("DV payoff is invalid")
    log_weights = np.full_like(probability, -np.inf)
    active = probability > 0.0
    log_weights[active] = np.log(probability[active]) + values[active]
    normalizer = float(logsumexp(log_weights))
    tilted = np.exp(log_weights - normalizer)
    kl = discrete_kl(tilted, probability)
    variational = float(tilted @ values - kl)
    return DVResult(normalizer, tilted, variational, kl)


def entropy_robust_expectation(
    reference: Sequence[float], losses: Sequence[float], *, theta: float
) -> DVResult:
    """Entropic risk and its KL-penalized adversarial distribution."""

    if not isfinite(theta) or theta <= 0.0:
        raise ValueError("theta must be positive")
    base = donsker_varadhan_discrete(reference, theta * np.asarray(losses))
    return DVResult(
        base.log_moment / theta,
        base.tilted_distribution,
        base.variational_value / theta,
        base.kl_cost / theta,
    )


@dataclass(frozen=True)
class CramerResult:
    rate: float
    tilt: float
    log_moment: float


def cramer_transform(
    values: Sequence[float],
    probabilities: Sequence[float],
    target: float,
    *,
    lower_tilt: float = -50.0,
    upper_tilt: float = 50.0,
) -> CramerResult:
    """Legendre-Fenchel transform of a finite distribution log-MGF."""

    support = np.asarray(values, dtype=np.float64)
    probability = _probability(probabilities, "probabilities")
    if (
        support.shape != probability.shape
        or np.any(~np.isfinite(support))
        or not isfinite(target)
        or not lower_tilt < upper_tilt
    ):
        raise ValueError("Cramer-transform inputs are invalid")

    def log_mgf(tilt: float) -> float:
        logs = np.full_like(probability, -np.inf)
        active = probability > 0.0
        logs[active] = np.log(probability[active]) + tilt * support[active]
        return float(logsumexp(logs))

    solved = minimize_scalar(
        lambda tilt: -(tilt * target - log_mgf(tilt)),
        bounds=(lower_tilt, upper_tilt),
        method="bounded",
    )
    if not solved.success:
        raise RuntimeError("Cramer-transform optimization failed")
    tilt = float(solved.x)
    cumulant = log_mgf(tilt)
    return CramerResult(max(0.0, tilt * target - cumulant), tilt, cumulant)


def chernoff_tail_bound(
    values: Sequence[float],
    probabilities: Sequence[float],
    threshold: float,
    *,
    upper_tilt: float = 50.0,
) -> CramerResult:
    """Optimized right-tail Chernoff bound represented by its rate."""

    result = cramer_transform(
        values,
        probabilities,
        threshold,
        lower_tilt=0.0,
        upper_tilt=upper_tilt,
    )
    return result


@dataclass(frozen=True)
class RiskSensitiveDPResult:
    values: np.ndarray
    policy: np.ndarray
    certainty_equivalent: np.ndarray


def finite_horizon_risk_sensitive_dp(
    transition: Sequence,
    costs: Sequence,
    terminal_cost: Sequence[float],
    *,
    horizon: int,
    theta: float,
) -> RiskSensitiveDPResult:
    """Finite-horizon multiplicative DP for a tabular controlled Markov chain."""

    dynamics = np.asarray(transition, dtype=np.float64)
    stage = np.asarray(costs, dtype=np.float64)
    terminal = np.asarray(terminal_cost, dtype=np.float64)
    if dynamics.ndim != 3:
        raise ValueError("transition must have state, action, next-state axes")
    states, actions, next_states = dynamics.shape
    if (
        states == 0
        or next_states != states
        or stage.shape != (states, actions)
        or terminal.shape != (states,)
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=2), 1.0)
        or np.any(~np.isfinite(stage))
        or np.any(~np.isfinite(terminal))
        or horizon < 1
        or not isfinite(theta)
    ):
        raise ValueError("risk-sensitive DP inputs are invalid")
    values = np.empty((horizon + 1, states))
    policy = np.empty((horizon, states), dtype=np.int64)
    values[horizon] = terminal
    for time in range(horizon - 1, -1, -1):
        q_values = np.empty((states, actions))
        for state in range(states):
            for action in range(actions):
                if abs(theta) < 1e-10:
                    future = dynamics[state, action] @ values[time + 1]
                else:
                    active = dynamics[state, action] > 0.0
                    future = logsumexp(
                        np.log(dynamics[state, action, active])
                        + theta * values[time + 1, active]
                    ) / theta
                q_values[state, action] = stage[state, action] + future
        policy[time] = np.argmin(q_values, axis=1)
        values[time] = q_values[np.arange(states), policy[time]]
    certainty = np.exp(np.clip(theta * values, -700.0, 700.0)) if theta else values.copy()
    return RiskSensitiveDPResult(values, policy, certainty)


def freidlin_wentzell_action(
    path: Sequence,
    drift: Callable[[np.ndarray], np.ndarray],
    covariance: Sequence,
    *,
    time_step: float,
) -> float:
    """Euler discretization of the small-noise path action."""

    trajectory = np.asarray(path, dtype=np.float64)
    diffusion = np.asarray(covariance, dtype=np.float64)
    if (
        trajectory.ndim != 2
        or trajectory.shape[0] < 2
        or np.any(~np.isfinite(trajectory))
        or diffusion.shape != (trajectory.shape[1], trajectory.shape[1])
        or np.any(~np.isfinite(diffusion))
        or time_step <= 0.0
    ):
        raise ValueError("path-action inputs are invalid")
    inverse = np.linalg.inv(diffusion)
    action = 0.0
    for current, following in zip(trajectory[:-1], trajectory[1:], strict=True):
        velocity = (following - current) / time_step
        expected = np.asarray(drift(current), dtype=np.float64)
        if expected.shape != current.shape or np.any(~np.isfinite(expected)):
            raise ValueError("drift returned an invalid vector")
        residual = velocity - expected
        action += 0.5 * time_step * float(residual @ inverse @ residual)
    return action


@dataclass(frozen=True)
class ExponentialTilt:
    weights: np.ndarray
    normalized_weights: np.ndarray
    effective_sample_size: float
    log_normalizer: float


def exponential_tilt_samples(
    samples: Sequence[float], *, theta: float
) -> ExponentialTilt:
    """Stable empirical exponential tilt and weight-degeneracy diagnostic."""

    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or not isfinite(theta):
        raise ValueError("tilt samples are invalid")
    logits = theta * values
    log_normalizer = float(logsumexp(logits) - np.log(values.size))
    normalized = np.exp(logits - logsumexp(logits))
    weights = np.exp(np.clip(logits - log_normalizer, -700.0, 700.0))
    ess = float(1.0 / np.sum(normalized**2))
    return ExponentialTilt(weights, normalized, ess, log_normalizer)
