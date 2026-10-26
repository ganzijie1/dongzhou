"""P63 tube, min-max, chance-constrained, and scenario MPC helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def minimal_rpi_box_radius(closed_loop: Sequence, disturbance_radius: Sequence[float], *, tolerance: float = 1e-10, max_iterations: int = 10000) -> np.ndarray:
    matrix = np.asarray(closed_loop, dtype=np.float64)
    disturbance = np.asarray(disturbance_radius, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or disturbance.shape != (matrix.shape[0],) or np.any(disturbance < 0.0) or tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("RPI inputs are invalid")
    absolute = np.abs(matrix)
    if np.max(np.abs(np.linalg.eigvals(absolute))) >= 1.0:
        raise ValueError("absolute closed-loop dynamics must be stable")
    radius = np.zeros_like(disturbance)
    for _ in range(max_iterations):
        updated = absolute @ radius + disturbance
        if np.max(np.abs(updated - radius)) <= tolerance:
            fixed_point = np.linalg.solve(np.eye(matrix.shape[0]) - absolute, disturbance)
            if np.any(fixed_point < -tolerance) or np.any(~np.isfinite(fixed_point)):
                raise ValueError("RPI fixed point is invalid")
            return np.maximum(fixed_point, 0.0)
        radius = updated
    raise RuntimeError("RPI iteration did not converge")


def tightened_box_bounds(lower: Sequence[float], upper: Sequence[float], error_radius: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    low, high, radius = (np.asarray(value, dtype=np.float64) for value in (lower, upper, error_radius))
    if low.ndim != 1 or low.shape != high.shape or low.shape != radius.shape or np.any(low > high) or np.any(radius < 0.0):
        raise ValueError("box tightening inputs are invalid")
    tightened_low, tightened_high = low + radius, high - radius
    if np.any(tightened_low > tightened_high):
        raise ValueError("tube makes the constraint set empty")
    return tightened_low, tightened_high


def box_is_robust_invariant(closed_loop: Sequence, radius: Sequence[float], disturbance_radius: Sequence[float], *, tolerance: float = 1e-12) -> bool:
    matrix = np.asarray(closed_loop, dtype=np.float64)
    bound = np.asarray(radius, dtype=np.float64)
    disturbance = np.asarray(disturbance_radius, dtype=np.float64)
    if matrix.shape != (bound.size, bound.size) or bound.ndim != 1 or disturbance.shape != bound.shape or np.any(bound < 0.0) or np.any(disturbance < 0.0):
        raise ValueError("invariance inputs are invalid")
    return bool(np.all(np.abs(matrix) @ bound + disturbance <= bound + tolerance))


def scenario_feasible(constraint_values: Sequence, *, maximum_violations: int = 0, tolerance: float = 0.0) -> tuple[bool, float]:
    values = np.asarray(constraint_values, dtype=np.float64)
    if values.ndim < 1 or values.shape[0] == 0 or np.any(~np.isfinite(values)) or maximum_violations < 0 or maximum_violations >= values.shape[0] or tolerance < 0.0:
        raise ValueError("scenario inputs are invalid")
    violated = np.any(values > tolerance, axis=tuple(range(1, values.ndim))) if values.ndim > 1 else values > tolerance
    count = int(violated.sum())
    return count <= maximum_violations, count / values.shape[0]


def empirical_chance_margin(samples: Sequence[float], limit: float, required_probability: float) -> tuple[float, float]:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or not np.isfinite(limit) or not 0.0 < required_probability <= 1.0:
        raise ValueError("chance-constraint inputs are invalid")
    quantile = float(np.quantile(values, required_probability, method="higher"))
    return limit - quantile, float(np.mean(values <= limit))
