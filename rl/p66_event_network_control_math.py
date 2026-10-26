"""P66 age-of-information, packet loss, quantization, and event triggering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class AgeOfInformationTracker:
    generation_time: float | None = None

    def receive(self, generated_at: float, received_at: float) -> float:
        if not np.isfinite(generated_at) or not np.isfinite(received_at) or generated_at > received_at:
            raise ValueError("message timestamps are invalid")
        if self.generation_time is None or generated_at >= self.generation_time:
            self.generation_time = generated_at
        return self.age(received_at)

    def age(self, now: float) -> float:
        if self.generation_time is None or not np.isfinite(now) or now < self.generation_time:
            raise ValueError("AoI is not defined at this time")
        return float(now - self.generation_time)


def uniform_quantize(values: Sequence[float], *, bits: int, limit: float) -> tuple[np.ndarray, np.ndarray]:
    data = np.asarray(values, dtype=np.float64)
    if data.ndim == 0 or np.any(~np.isfinite(data)) or bits <= 0 or limit <= 0.0:
        raise ValueError("quantizer inputs are invalid")
    levels = 2**bits
    clipped = np.clip(data, -limit, limit)
    indices = np.rint((clipped + limit) * (levels - 1) / (2.0 * limit))
    quantized = indices * (2.0 * limit) / (levels - 1) - limit
    return quantized, np.abs(data) > limit


def event_trigger(error: Sequence[float], state: Sequence[float], *, relative_threshold: float, absolute_threshold: float = 0.0) -> bool:
    residual = np.asarray(error, dtype=np.float64)
    current = np.asarray(state, dtype=np.float64)
    if residual.shape != current.shape or residual.ndim != 1 or relative_threshold < 0.0 or absolute_threshold < 0.0:
        raise ValueError("event-trigger inputs are invalid")
    return bool(np.linalg.norm(residual) >= relative_threshold * np.linalg.norm(current) + absolute_threshold)


def packet_hold_update(previous: Sequence[float], transmitted: Sequence[float], received: bool) -> np.ndarray:
    old = np.asarray(previous, dtype=np.float64)
    new = np.asarray(transmitted, dtype=np.float64)
    if old.shape != new.shape or old.ndim == 0:
        raise ValueError("packet update inputs are invalid")
    return new.copy() if received else old.copy()


def data_rate_lower_bound(eigenvalues: Sequence[complex]) -> float:
    values = np.asarray(eigenvalues, dtype=np.complex128)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)):
        raise ValueError("eigenvalues are invalid")
    unstable = np.abs(values[np.abs(values) > 1.0])
    return float(np.log2(unstable).sum())
