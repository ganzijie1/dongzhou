"""P64 hybrid automata, saltation, dwell-time, and Zeno diagnostics."""

from __future__ import annotations

from typing import Hashable, Sequence

import numpy as np


def saltation_matrix(vector_before: Sequence[float], vector_after: Sequence[float], guard_gradient: Sequence[float], reset_jacobian: Sequence | None = None, *, guard_time_derivative: float = 0.0) -> np.ndarray:
    before = np.asarray(vector_before, dtype=np.float64)
    after = np.asarray(vector_after, dtype=np.float64)
    normal = np.asarray(guard_gradient, dtype=np.float64)
    reset = np.eye(before.size) if reset_jacobian is None else np.asarray(reset_jacobian, dtype=np.float64)
    if before.ndim != 1 or after.shape != before.shape or normal.shape != before.shape or reset.shape != (before.size, before.size):
        raise ValueError("saltation inputs are invalid")
    denominator = float(normal @ before + guard_time_derivative)
    if abs(denominator) <= 1e-12:
        raise ValueError("guard crossing is tangential")
    return reset + np.outer(after - reset @ before, normal) / denominator


def switching_lyapunov_bound(initial_value: float, decay_rate: float, jump_factor: float, switches: int, duration: float) -> float:
    if initial_value < 0.0 or decay_rate < 0.0 or jump_factor < 1.0 or switches < 0 or duration < 0.0:
        raise ValueError("switching Lyapunov inputs are invalid")
    return float(initial_value * jump_factor**switches * np.exp(-decay_rate * duration))


def minimum_average_dwell_time(decay_rate: float, jump_factor: float) -> float:
    if decay_rate <= 0.0 or jump_factor < 1.0:
        raise ValueError("dwell-time inputs are invalid")
    return float(np.log(jump_factor) / decay_rate)


def validate_hybrid_trace(modes: Sequence[Hashable], event_times: Sequence[float], allowed_transitions: set[tuple[Hashable, Hashable]]) -> bool:
    times = np.asarray(event_times, dtype=np.float64)
    if len(modes) != times.size + 1 or np.any(~np.isfinite(times)) or np.any(np.diff(times) <= 0.0):
        raise ValueError("hybrid trace is invalid")
    return all((modes[index], modes[index + 1]) in allowed_transitions for index in range(len(modes) - 1))


def detect_zeno(event_times: Sequence[float], *, minimum_interval: float, consecutive: int = 3) -> bool:
    times = np.asarray(event_times, dtype=np.float64)
    if times.ndim != 1 or np.any(~np.isfinite(times)) or np.any(np.diff(times) <= 0.0) or minimum_interval <= 0.0 or consecutive <= 0:
        raise ValueError("Zeno diagnostic inputs are invalid")
    if times.size <= consecutive:
        return False
    short = np.diff(times) < minimum_interval
    return any(np.all(short[start:start + consecutive]) for start in range(short.size - consecutive + 1))
