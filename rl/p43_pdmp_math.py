"""P43 piecewise-deterministic Markov process simulation and control primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Callable, Sequence

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq


ArrayFunction = Callable[[float], Sequence[float]]


def next_event_time_by_hazard(
    flow: ArrayFunction,
    intensity: Callable[[np.ndarray], float],
    uniform: float,
    *,
    max_time: float,
) -> float | None:
    """Invert integrated hazard along a deterministic flow."""

    if not 0.0 < uniform < 1.0 or not isfinite(max_time) or max_time <= 0.0:
        raise ValueError("event-time inputs are invalid")
    target = -log(uniform)

    def cumulative(time: float) -> float:
        result, _ = quad(lambda point: float(intensity(np.asarray(flow(point), dtype=float))), 0.0, time)
        if not isfinite(result) or result < -1e-12:
            raise ValueError("intensity must integrate to a nonnegative finite value")
        return result

    if cumulative(max_time) < target:
        return None
    return float(brentq(lambda time: cumulative(time) - target, 0.0, max_time))


def linear_hazard_event_time(base: float, slope: float, uniform: float) -> float:
    """Exact inversion for lambda(t)=base+slope*t with nonnegative coefficients."""

    if base < 0.0 or slope < 0.0 or not isfinite(base) or not isfinite(slope) or not 0.0 < uniform < 1.0:
        raise ValueError("linear hazard inputs are invalid")
    target = -log(uniform)
    if slope == 0.0:
        if base == 0.0:
            return float("inf")
        return target / base
    return float((-base + np.sqrt(base * base + 2.0 * slope * target)) / slope)


def pdmp_generator(
    drift: Sequence[float],
    gradient: Sequence[float],
    intensity: float,
    current_value: float,
    jump_values: Sequence[float],
    jump_probabilities: Sequence[float],
) -> float:
    vector = np.asarray(drift, dtype=np.float64)
    derivative = np.asarray(gradient, dtype=np.float64)
    values = np.asarray(jump_values, dtype=np.float64)
    probabilities = np.asarray(jump_probabilities, dtype=np.float64)
    if (
        vector.ndim != 1
        or derivative.shape != vector.shape
        or values.ndim != 1
        or values.size == 0
        or probabilities.shape != values.shape
        or np.any(~np.isfinite(vector))
        or np.any(~np.isfinite(derivative))
        or np.any(~np.isfinite(values))
        or np.any(probabilities < 0.0)
        or not np.isclose(probabilities.sum(), 1.0)
        or not isfinite(intensity)
        or intensity < 0.0
        or not isfinite(current_value)
    ):
        raise ValueError("generator inputs are invalid")
    return float(vector @ derivative + intensity * (probabilities @ values - current_value))


@dataclass(frozen=True)
class PDMPControlResult:
    action: int
    action_values: np.ndarray


def controlled_hjb_backup(
    running_costs: Sequence[float],
    drift_gradient_terms: Sequence[float],
    intensities: Sequence[float],
    expected_jump_values: Sequence[float],
    current_value: float,
) -> PDMPControlResult:
    running = np.asarray(running_costs, dtype=np.float64)
    drift = np.asarray(drift_gradient_terms, dtype=np.float64)
    rates = np.asarray(intensities, dtype=np.float64)
    jumps = np.asarray(expected_jump_values, dtype=np.float64)
    if not (running.shape == drift.shape == rates.shape == jumps.shape) or running.ndim != 1 or running.size == 0:
        raise ValueError("HJB arrays have incompatible shapes")
    if (
        np.any(~np.isfinite(running))
        or np.any(~np.isfinite(drift))
        or np.any(~np.isfinite(rates))
        or np.any(~np.isfinite(jumps))
        or np.any(rates < 0.0)
        or not isfinite(current_value)
    ):
        raise ValueError("HJB inputs are invalid")
    values = running + drift + rates * (jumps - current_value)
    return PDMPControlResult(int(np.argmin(values)), values)


def time_rescaling_increments(integrated_hazards: Sequence[float]) -> np.ndarray:
    values = np.asarray(integrated_hazards, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("integrated hazards are invalid")
    return values.copy()
