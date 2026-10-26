"""P65 anisotropic travel costs and dynamic collision potentials."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def anisotropy_ratio(metric: Sequence) -> float:
    matrix = np.asarray(metric, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.allclose(matrix, matrix.T):
        raise ValueError("metric must be symmetric positive definite")
    eigenvalues = np.linalg.eigvalsh(matrix)
    if eigenvalues[0] <= 0.0:
        raise ValueError("metric must be symmetric positive definite")
    return float(np.sqrt(eigenvalues[-1] / eigenvalues[0]))


def randers_cost(metric: Sequence, drift: Sequence[float], displacement: Sequence[float]) -> float:
    matrix = np.asarray(metric, dtype=np.float64)
    bias = np.asarray(drift, dtype=np.float64)
    delta = np.asarray(displacement, dtype=np.float64)
    if matrix.shape != (delta.size, delta.size) or bias.shape != delta.shape or not np.allclose(matrix, matrix.T):
        raise ValueError("Randers inputs are invalid")
    eigenvalues = np.linalg.eigvalsh(matrix)
    if eigenvalues[0] <= 0.0 or float(bias @ np.linalg.solve(matrix, bias)) >= 1.0:
        raise ValueError("Randers drift violates strong convexity")
    return float(np.sqrt(delta @ matrix @ delta) + bias @ delta)


def closest_approach(relative_position: Sequence[float], relative_velocity: Sequence[float], horizon: float) -> tuple[float, float]:
    position = np.asarray(relative_position, dtype=np.float64)
    velocity = np.asarray(relative_velocity, dtype=np.float64)
    if position.ndim != 1 or velocity.shape != position.shape or horizon < 0.0:
        raise ValueError("closest-approach inputs are invalid")
    speed2 = float(velocity @ velocity)
    time = 0.0 if speed2 == 0.0 else float(np.clip(-(position @ velocity) / speed2, 0.0, horizon))
    return time, float(np.linalg.norm(position + time * velocity))


def dynamic_collision_potential(relative_position: Sequence[float], relative_velocity: Sequence[float], *, horizon: float, clearance: float, scale: float = 1.0, time_scale: float = 1.0) -> float:
    if clearance <= 0.0 or scale < 0.0 or time_scale <= 0.0:
        raise ValueError("dynamic potential parameters are invalid")
    time, distance = closest_approach(relative_position, relative_velocity, horizon)
    return float(scale * np.exp(-time / time_scale) / max(distance - clearance, 1e-6) ** 2)


def blend_velocity(global_direction: Sequence[float], avoidance_direction: Sequence[float], *, avoidance_weight: float, maximum_speed: float) -> np.ndarray:
    global_vector = np.asarray(global_direction, dtype=np.float64)
    avoidance = np.asarray(avoidance_direction, dtype=np.float64)
    if global_vector.ndim != 1 or avoidance.shape != global_vector.shape or avoidance_weight < 0.0 or maximum_speed < 0.0:
        raise ValueError("velocity blending inputs are invalid")
    combined = global_vector + avoidance_weight * avoidance
    norm = np.linalg.norm(combined)
    return combined if norm <= maximum_speed or norm == 0.0 else combined * maximum_speed / norm
