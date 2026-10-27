"""P70 contraction metrics, incremental stability, and CCM helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def metric_bounds(metric: Sequence) -> tuple[float, float, float]:
    matrix = np.asarray(metric, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.allclose(matrix, matrix.T):
        raise ValueError("metric must be a symmetric square matrix")
    eigenvalues = np.linalg.eigvalsh(matrix)
    if eigenvalues[0] <= 0.0 or np.any(~np.isfinite(eigenvalues)):
        raise ValueError("metric must be positive definite")
    return float(eigenvalues[0]), float(eigenvalues[-1]), float(eigenvalues[-1] / eigenvalues[0])


def contraction_residual(jacobian: Sequence, metric: Sequence, *, metric_derivative: Sequence | None = None, rate: float = 0.0) -> np.ndarray:
    a = np.asarray(jacobian, dtype=np.float64)
    m = np.asarray(metric, dtype=np.float64)
    mdot = np.zeros_like(m) if metric_derivative is None else np.asarray(metric_derivative, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or m.shape != a.shape or mdot.shape != a.shape or rate < 0.0:
        raise ValueError("contraction inputs are invalid")
    metric_bounds(m)
    residual = mdot + a.T @ m + m @ a + 2.0 * rate * m
    return 0.5 * (residual + residual.T)


def maximum_contraction_rate(jacobian: Sequence, metric: Sequence, *, metric_derivative: Sequence | None = None) -> float:
    m = np.asarray(metric, dtype=np.float64)
    base = contraction_residual(jacobian, m, metric_derivative=metric_derivative)
    eigenvalues, vectors = np.linalg.eigh(m)
    inverse_root = (vectors / np.sqrt(eigenvalues)) @ vectors.T
    generalized = inverse_root @ base @ inverse_root
    return float(-0.5 * np.linalg.eigvalsh(generalized)[-1])


def discrete_contraction_factor(jacobian: Sequence, metric_current: Sequence, metric_next: Sequence) -> float:
    a = np.asarray(jacobian, dtype=np.float64)
    current = np.asarray(metric_current, dtype=np.float64)
    following = np.asarray(metric_next, dtype=np.float64)
    if a.ndim != 2 or current.shape != a.shape or following.shape != a.shape:
        raise ValueError("discrete contraction inputs are invalid")
    metric_bounds(current)
    metric_bounds(following)
    eigenvalues, vectors = np.linalg.eigh(current)
    inverse_root = (vectors / np.sqrt(eigenvalues)) @ vectors.T
    mapped = inverse_root @ a.T @ following @ a @ inverse_root
    return float(np.sqrt(max(0.0, np.linalg.eigvalsh(mapped)[-1])))


def incremental_error_bound(initial_distance: float, rate: float, disturbance_bound: float, horizon: Sequence[float] | float) -> np.ndarray:
    times = np.asarray(horizon, dtype=np.float64)
    if initial_distance < 0.0 or rate <= 0.0 or disturbance_bound < 0.0 or np.any(times < 0.0) or np.any(~np.isfinite(times)):
        raise ValueError("incremental error inputs are invalid")
    decay = np.exp(-rate * times)
    return decay * initial_distance + disturbance_bound * (1.0 - decay) / rate


def geodesic_energy(points: Sequence, metrics: Sequence) -> float:
    path = np.asarray(points, dtype=np.float64)
    metric = np.asarray(metrics, dtype=np.float64)
    if path.ndim != 2 or path.shape[0] < 2 or metric.shape != (path.shape[0] - 1, path.shape[1], path.shape[1]):
        raise ValueError("geodesic inputs are invalid")
    energy = 0.0
    for delta, matrix in zip(np.diff(path, axis=0), metric, strict=True):
        metric_bounds(matrix)
        energy += float(delta @ matrix @ delta)
    return energy * (path.shape[0] - 1)


def geodesic_feedback(reference_control: Sequence[float], points: Sequence, gains: Sequence) -> np.ndarray:
    control = np.asarray(reference_control, dtype=np.float64).copy()
    path = np.asarray(points, dtype=np.float64)
    gain = np.asarray(gains, dtype=np.float64)
    if path.ndim != 2 or path.shape[0] < 2 or gain.shape[:2] != (path.shape[0] - 1, control.size) or gain.shape[2] != path.shape[1]:
        raise ValueError("geodesic feedback inputs are invalid")
    for matrix, delta in zip(gain, np.diff(path, axis=0), strict=True):
        control += matrix @ delta
    return control
