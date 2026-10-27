"""P75 Fisher-Rao geometry, natural gradients, and mirror flows."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def validate_simplex(probabilities: Sequence[float], *, strictly_positive: bool = True) -> np.ndarray:
    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 1 or values.size < 2 or np.any(~np.isfinite(values)) or np.any(values < 0.0) or not np.isclose(values.sum(), 1.0) or strictly_positive and np.any(values <= 0.0):
        raise ValueError("probabilities are not in the required simplex")
    return values


def categorical_fisher_inner_product(probabilities: Sequence[float], left: Sequence[float], right: Sequence[float]) -> float:
    p = validate_simplex(probabilities)
    u, v = np.asarray(left, dtype=np.float64), np.asarray(right, dtype=np.float64)
    if u.shape != p.shape or v.shape != p.shape or not np.isclose(u.sum(), 0.0) or not np.isclose(v.sum(), 0.0):
        raise ValueError("Fisher tangent vectors are invalid")
    return float(np.sum(u * v / p))


def fisher_rao_distance(left: Sequence[float], right: Sequence[float]) -> float:
    p, q = validate_simplex(left), validate_simplex(right)
    if p.shape != q.shape:
        raise ValueError("probability dimensions do not match")
    coefficient = float(np.clip(np.sqrt(p * q).sum(), -1.0, 1.0))
    return float(2.0 * np.arccos(coefficient))


def fisher_rao_geodesic(left: Sequence[float], right: Sequence[float], time: float) -> np.ndarray:
    p, q = validate_simplex(left), validate_simplex(right)
    if p.shape != q.shape or not 0.0 <= time <= 1.0:
        raise ValueError("geodesic inputs are invalid")
    root_p, root_q = np.sqrt(p), np.sqrt(q)
    angle = float(np.arccos(np.clip(root_p @ root_q, -1.0, 1.0)))
    if angle < 1e-10:
        return p.copy()
    root = np.sin((1.0 - time) * angle) * root_p / np.sin(angle) + np.sin(time * angle) * root_q / np.sin(angle)
    result = root**2
    return result / result.sum()


def categorical_natural_gradient(probabilities: Sequence[float], euclidean_gradient: Sequence[float], *, maximize: bool = False) -> np.ndarray:
    p = validate_simplex(probabilities)
    gradient = np.asarray(euclidean_gradient, dtype=np.float64)
    if gradient.shape != p.shape or np.any(~np.isfinite(gradient)):
        raise ValueError("natural-gradient inputs are invalid")
    direction = p * (gradient - p @ gradient)
    return direction if maximize else -direction


def entropy_mirror_step(probabilities: Sequence[float], gradient: Sequence[float], step_size: float, *, maximize: bool = False) -> np.ndarray:
    p = validate_simplex(probabilities)
    g = np.asarray(gradient, dtype=np.float64)
    if g.shape != p.shape or step_size < 0.0:
        raise ValueError("mirror-step inputs are invalid")
    sign = 1.0 if maximize else -1.0
    logits = np.log(p) + sign * step_size * g
    logits -= logits.max()
    result = np.exp(logits)
    return result / result.sum()


def probability_floor(probabilities: Sequence[float], minimum: float) -> np.ndarray:
    p = validate_simplex(probabilities, strictly_positive=False)
    if minimum <= 0.0 or minimum * p.size >= 1.0:
        raise ValueError("probability floor is invalid")
    floored = np.maximum(p, minimum)
    return floored / floored.sum()


def empirical_fisher(scores: Sequence, *, damping: float = 0.0) -> np.ndarray:
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0 or damping < 0.0 or np.any(~np.isfinite(values)):
        raise ValueError("score samples are invalid")
    matrix = values.T @ values / values.shape[0]
    return matrix + damping * np.eye(values.shape[1])


def parameter_natural_gradient(scores: Sequence, gradient: Sequence[float], *, damping: float = 1e-8) -> tuple[np.ndarray, float]:
    fisher = empirical_fisher(scores, damping=damping)
    vector = np.asarray(gradient, dtype=np.float64)
    if vector.shape != (fisher.shape[0],):
        raise ValueError("parameter gradient is invalid")
    solution = np.linalg.solve(fisher, vector)
    return solution, float(np.linalg.norm(fisher @ solution - vector))
