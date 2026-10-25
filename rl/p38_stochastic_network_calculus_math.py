"""P38 min-plus network calculus, effective bandwidth, and queue tail bounds."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Sequence

import numpy as np
from scipy.special import logsumexp


def _curve(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 1 or result.size == 0 or np.any(np.isnan(result)):
        raise ValueError(f"{name} must be a one-dimensional curve")
    return result


def min_plus_convolution(first: Sequence[float], second: Sequence[float]) -> np.ndarray:
    """Discrete min-plus convolution on a shared integer time grid."""

    left = _curve(first, "first curve")
    right = _curve(second, "second curve")
    horizon = min(left.size, right.size)
    result = np.empty(horizon)
    for time in range(horizon):
        result[time] = min(left[index] + right[time - index] for index in range(time + 1))
    return result


def min_plus_deconvolution(first: Sequence[float], second: Sequence[float]) -> np.ndarray:
    """Finite-horizon discrete min-plus deconvolution."""

    left = _curve(first, "first curve")
    right = _curve(second, "second curve")
    horizon = min(left.size, right.size)
    result = np.empty(horizon)
    for time in range(horizon):
        result[time] = max(
            left[time + offset] - right[offset]
            for offset in range(horizon - time)
        )
    return result


@dataclass(frozen=True)
class DeterministicQueueBounds:
    backlog: float
    delay_steps: float
    stable_on_grid: bool


def deterministic_queue_bounds(
    arrival_curve: Sequence[float], service_curve: Sequence[float]
) -> DeterministicQueueBounds:
    """Vertical backlog and horizontal delay deviations on a finite grid."""

    arrival = _curve(arrival_curve, "arrival curve")
    service = _curve(service_curve, "service curve")
    if arrival.size != service.size:
        raise ValueError("arrival and service curves need the same horizon")
    backlog = float(np.max(arrival - service))
    delay = 0
    for source in range(arrival.size):
        matches = np.nonzero(service[source:] >= arrival[source])[0]
        if matches.size == 0:
            return DeterministicQueueBounds(backlog, float("inf"), False)
        delay = max(delay, int(matches[0]))
    return DeterministicQueueBounds(max(0.0, backlog), float(delay), True)


def token_bucket_curve(*, burst: float, rate: float, horizon: int) -> np.ndarray:
    if burst < 0.0 or rate < 0.0 or horizon < 0:
        raise ValueError("token-bucket settings are invalid")
    time = np.arange(horizon + 1, dtype=np.float64)
    result = burst + rate * time
    result[0] = 0.0
    return result


def rate_latency_curve(*, rate: float, latency: float, horizon: int) -> np.ndarray:
    if rate < 0.0 or latency < 0.0 or horizon < 0:
        raise ValueError("rate-latency settings are invalid")
    return rate * np.maximum(np.arange(horizon + 1, dtype=np.float64) - latency, 0.0)


def concatenate_service_curves(curves: Sequence[Sequence[float]]) -> np.ndarray:
    normalized = tuple(_curve(curve, "service curve") for curve in curves)
    if not normalized:
        raise ValueError("at least one service curve is required")
    horizon = min(curve.size for curve in normalized)
    result = normalized[0][:horizon]
    for curve in normalized[1:]:
        result = min_plus_convolution(result, curve[:horizon])
    return result


def leftover_service_curve(
    aggregate_service: Sequence[float], cross_arrival: Sequence[float]
) -> np.ndarray:
    service = _curve(aggregate_service, "aggregate service")
    cross = _curve(cross_arrival, "cross arrival")
    if service.shape != cross.shape:
        raise ValueError("leftover-service curves need equal shape")
    return np.maximum(service - cross, 0.0)


def stochastic_split_bound(
    first_tail: Sequence[float], second_tail: Sequence[float]
) -> np.ndarray:
    """Independence-free infimal split bound min_y f(y)+g(x-y)."""

    first = _curve(first_tail, "first tail")
    second = _curve(second_tail, "second tail")
    if first.shape != second.shape or np.any(first < 0.0) or np.any(second < 0.0):
        raise ValueError("tail bounds are invalid")
    return np.minimum(min_plus_convolution(first, second), 1.0)


def effective_bandwidth(
    arrivals: Sequence[float], *, theta: float, duration: float
) -> float:
    """Empirical finite-horizon effective bandwidth from independent blocks."""

    sample = np.asarray(arrivals, dtype=np.float64)
    if (
        sample.ndim != 1
        or sample.size == 0
        or np.any(~np.isfinite(sample))
        or theta <= 0.0
        or duration <= 0.0
    ):
        raise ValueError("effective-bandwidth inputs are invalid")
    return float((logsumexp(theta * sample) - np.log(sample.size)) / (theta * duration))


def effective_capacity(
    services: Sequence[float], *, theta: float, duration: float
) -> float:
    """Empirical finite-horizon effective capacity from independent blocks."""

    sample = np.asarray(services, dtype=np.float64)
    if (
        sample.ndim != 1
        or sample.size == 0
        or np.any(~np.isfinite(sample))
        or theta <= 0.0
        or duration <= 0.0
    ):
        raise ValueError("effective-capacity inputs are invalid")
    return float(-(logsumexp(-theta * sample) - np.log(sample.size)) / (theta * duration))


def effective_bandwidth_chernoff_bound(
    arrivals: Sequence[float],
    *,
    theta: float,
    duration: float,
    capacity_rate: float,
) -> float:
    bandwidth = effective_bandwidth(arrivals, theta=theta, duration=duration)
    exponent = -theta * duration * (capacity_rate - bandwidth)
    return min(1.0, exp(min(0.0, exponent)))


@dataclass(frozen=True)
class ConstantServiceTailBound:
    traffic_factor: float
    backlog_probability: float
    delay_probability: float


def constant_service_tail_bound(
    increment_log_mgf: float,
    *,
    theta: float,
    service_per_slot: float,
    backlog_threshold: float,
    delay_threshold: float,
) -> ConstantServiceTailBound:
    """Geometric-union queue bound for stationary independent increments."""

    inputs = (
        increment_log_mgf,
        theta,
        service_per_slot,
        backlog_threshold,
        delay_threshold,
    )
    if (
        any(not isfinite(value) for value in inputs)
        or theta <= 0.0
        or service_per_slot <= 0.0
        or backlog_threshold < 0.0
        or delay_threshold < 0.0
    ):
        raise ValueError("constant-service tail inputs are invalid")
    traffic = exp(increment_log_mgf - theta * service_per_slot)
    if traffic >= 1.0:
        return ConstantServiceTailBound(traffic, 1.0, 1.0)
    backlog = min(1.0, exp(-theta * backlog_threshold) / (1.0 - traffic))
    delay = min(
        1.0,
        exp(-theta * service_per_slot * delay_threshold) / (1.0 - traffic),
    )
    return ConstantServiceTailBound(traffic, backlog, delay)


def markov_modulated_effective_bandwidth(
    transition: Sequence,
    state_arrivals: Sequence[float],
    *,
    theta: float,
) -> float:
    """Spectral-radius effective bandwidth for a finite Markov source."""

    matrix = np.asarray(transition, dtype=np.float64)
    arrivals = np.asarray(state_arrivals, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[0] != matrix.shape[1]
        or arrivals.shape != (matrix.shape[0],)
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix.sum(axis=1), 1.0)
        or np.any(~np.isfinite(arrivals))
        or theta <= 0.0
    ):
        raise ValueError("Markov effective-bandwidth inputs are invalid")
    tilted = matrix @ np.diag(np.exp(theta * arrivals))
    radius = float(np.max(np.abs(np.linalg.eigvals(tilted))))
    return float(np.log(radius) / theta)
