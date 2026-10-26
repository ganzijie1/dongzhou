"""P53 marked point-process intensity, likelihood, and residual diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


def _events(times: Sequence[float], marks: Sequence[int], mark_count: int) -> tuple[np.ndarray, np.ndarray]:
    event_times = np.asarray(times, dtype=np.float64)
    event_marks = np.asarray(marks)
    if event_times.ndim != 1 or event_marks.shape != event_times.shape or np.any(~np.isfinite(event_times)) or np.any(event_times < 0.0) or np.any(np.diff(event_times) < 0.0) or np.any(event_marks != np.floor(event_marks)) or np.any(event_marks < 0) or np.any(event_marks >= mark_count):
        raise ValueError("marked events are invalid")
    return event_times, event_marks.astype(int)


@dataclass(frozen=True)
class IntensityResult:
    raw_intensity: np.ndarray
    intensity: np.ndarray


def marked_exponential_intensity(
    query_time: float,
    event_times: Sequence[float],
    event_marks: Sequence[int],
    baseline: Sequence[float],
    excitation: Sequence,
    decay: Sequence,
) -> IntensityResult:
    base = np.asarray(baseline, dtype=np.float64)
    alpha = np.asarray(excitation, dtype=np.float64)
    beta = np.asarray(decay, dtype=np.float64)
    if base.ndim != 1 or base.size == 0 or np.any(~np.isfinite(base)) or np.any(base < 0.0) or alpha.shape != (base.size, base.size) or beta.shape != alpha.shape or np.any(~np.isfinite(alpha)) or np.any(~np.isfinite(beta)) or np.any(beta <= 0.0) or not np.isfinite(query_time) or query_time < 0.0:
        raise ValueError("intensity parameters are invalid")
    times, marks = _events(event_times, event_marks, base.size)
    past = times < query_time
    raw = base.copy()
    for time, mark in zip(times[past], marks[past]):
        raw += alpha[:, mark] * np.exp(-beta[:, mark] * (query_time - time))
    return IntensityResult(raw, np.maximum(raw, 0.0))


def exponential_hawkes_log_likelihood(
    event_times: Sequence[float],
    event_marks: Sequence[int],
    baseline: Sequence[float],
    excitation: Sequence,
    decay: Sequence,
    horizon: float,
) -> float:
    base = np.asarray(baseline, dtype=np.float64)
    alpha = np.asarray(excitation, dtype=np.float64)
    beta = np.asarray(decay, dtype=np.float64)
    if base.ndim != 1 or base.size == 0 or np.any(base <= 0.0) or np.any(~np.isfinite(base)) or alpha.shape != (base.size, base.size) or beta.shape != alpha.shape or np.any(alpha < 0.0) or np.any(~np.isfinite(alpha)) or np.any(beta <= 0.0) or np.any(~np.isfinite(beta)) or not np.isfinite(horizon) or horizon <= 0.0:
        raise ValueError("Hawkes parameters are invalid")
    times, marks = _events(event_times, event_marks, base.size)
    if np.any(times > horizon):
        raise ValueError("events must lie inside the observation horizon")
    log_intensity = 0.0
    for index, (time, mark) in enumerate(zip(times, marks)):
        intensity = base[mark]
        for past_time, past_mark in zip(times[:index], marks[:index]):
            intensity += alpha[mark, past_mark] * np.exp(-beta[mark, past_mark] * (time - past_time))
        log_intensity += np.log(intensity)
    compensator = float(base.sum() * horizon)
    for time, source_mark in zip(times, marks):
        remaining = horizon - time
        compensator += float(np.sum(alpha[:, source_mark] / beta[:, source_mark] * (1.0 - np.exp(-beta[:, source_mark] * remaining))))
    return float(log_intensity - compensator)


def total_compensator_increments(
    event_times: Sequence[float],
    event_marks: Sequence[int],
    baseline: Sequence[float],
    excitation: Sequence,
    decay: Sequence,
) -> np.ndarray:
    base = np.asarray(baseline, dtype=np.float64)
    alpha = np.asarray(excitation, dtype=np.float64)
    beta = np.asarray(decay, dtype=np.float64)
    if base.ndim != 1 or np.any(base < 0.0) or alpha.shape != (base.size, base.size) or beta.shape != alpha.shape or np.any(alpha < 0.0) or np.any(beta <= 0.0):
        raise ValueError("compensator parameters are invalid")
    times, marks = _events(event_times, event_marks, base.size)
    increments = np.empty(times.size)
    start = 0.0
    for index, end in enumerate(times):
        integral = float(base.sum() * (end - start))
        for time, mark in zip(times[:index], marks[:index]):
            lower = max(start, time)
            if lower < end:
                integral += float(np.sum(alpha[:, mark] / beta[:, mark] * (np.exp(-beta[:, mark] * (lower - time)) - np.exp(-beta[:, mark] * (end - time)))))
        increments[index] = integral
        start = end
    return increments


def branching_ratio(excitation: Sequence, decay: Sequence) -> tuple[np.ndarray, float]:
    alpha = np.asarray(excitation, dtype=np.float64)
    beta = np.asarray(decay, dtype=np.float64)
    if alpha.ndim != 2 or alpha.shape[0] != alpha.shape[1] or beta.shape != alpha.shape or np.any(alpha < 0.0) or np.any(beta <= 0.0) or np.any(~np.isfinite(alpha)) or np.any(~np.isfinite(beta)):
        raise ValueError("branching parameters are invalid")
    offspring = alpha / beta
    radius = float(np.max(np.abs(np.linalg.eigvals(offspring))))
    return offspring, radius
