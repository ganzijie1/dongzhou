"""P77 Gaussian processes, acquisitions, SafeOpt, and multi-fidelity BO."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.linalg import solve_triangular
from scipy.stats import norm


def rbf_kernel(left: Sequence, right: Sequence, *, variance: float = 1.0, length_scales: Sequence[float] | float = 1.0) -> np.ndarray:
    x, y = np.atleast_2d(np.asarray(left, dtype=np.float64)), np.atleast_2d(np.asarray(right, dtype=np.float64))
    scales = np.asarray(length_scales, dtype=np.float64)
    if x.shape[1] != y.shape[1] or scales.shape not in ((), (x.shape[1],)) or variance <= 0.0 or np.any(scales <= 0.0):
        raise ValueError("RBF kernel inputs are invalid")
    differences = (x[:, None, :] - y[None, :, :]) / scales
    return variance * np.exp(-0.5 * np.sum(differences**2, axis=2))


def gp_posterior(train_x: Sequence, train_y: Sequence[float], test_x: Sequence, *, noise_variance: float = 1e-6, variance: float = 1.0, length_scales: Sequence[float] | float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    x = np.atleast_2d(np.asarray(train_x, dtype=np.float64))
    y = np.asarray(train_y, dtype=np.float64)
    query = np.atleast_2d(np.asarray(test_x, dtype=np.float64))
    if y.shape != (x.shape[0],) or query.shape[1] != x.shape[1] or noise_variance < 0.0:
        raise ValueError("GP posterior inputs are invalid")
    kernel = rbf_kernel(x, x, variance=variance, length_scales=length_scales) + (noise_variance + 1e-10) * np.eye(x.shape[0])
    cross = rbf_kernel(x, query, variance=variance, length_scales=length_scales)
    factor = np.linalg.cholesky(kernel)
    alpha = solve_triangular(factor.T, solve_triangular(factor, y, lower=True), lower=False)
    mean = cross.T @ alpha
    projected = solve_triangular(factor, cross, lower=True)
    covariance = rbf_kernel(query, query, variance=variance, length_scales=length_scales) - projected.T @ projected
    return mean, np.maximum(np.diag(covariance), 0.0)


def confidence_bounds(mean: Sequence[float], variance: Sequence[float], beta: float) -> tuple[np.ndarray, np.ndarray]:
    average, uncertainty = np.asarray(mean, dtype=np.float64), np.asarray(variance, dtype=np.float64)
    if average.shape != uncertainty.shape or np.any(uncertainty < 0.0) or beta < 0.0:
        raise ValueError("confidence-bound inputs are invalid")
    radius = np.sqrt(beta * uncertainty)
    return average - radius, average + radius


def expected_improvement(mean: Sequence[float], variance: Sequence[float], best: float, *, exploration: float = 0.0, minimize: bool = True) -> np.ndarray:
    average, uncertainty = np.asarray(mean, dtype=np.float64), np.asarray(variance, dtype=np.float64)
    if average.shape != uncertainty.shape or np.any(uncertainty < 0.0) or exploration < 0.0:
        raise ValueError("EI inputs are invalid")
    standard = np.sqrt(uncertainty)
    improvement = best - average - exploration if minimize else average - best - exploration
    result = np.maximum(improvement, 0.0)
    active = standard > 0.0
    z = improvement[active] / standard[active]
    result[active] = improvement[active] * norm.cdf(z) + standard[active] * norm.pdf(z)
    return result


def gp_confidence_acquisition(mean: Sequence[float], variance: Sequence[float], beta: float, *, minimize: bool = True) -> np.ndarray:
    lower, upper = confidence_bounds(mean, variance, beta)
    return lower if minimize else upper


@dataclass(frozen=True)
class SafeOptSets:
    safe: np.ndarray
    potential_maximizers: np.ndarray
    expanders: np.ndarray


def safeopt_sets(points: Sequence, objective_mean: Sequence[float], objective_variance: Sequence[float], safety_mean: Sequence[float], safety_variance: Sequence[float], *, threshold: float, beta: float, lipschitz: float) -> SafeOptSets:
    locations = np.asarray(points, dtype=np.float64)
    objective_lower, objective_upper = confidence_bounds(objective_mean, objective_variance, beta)
    safety_lower, _ = confidence_bounds(safety_mean, safety_variance, beta)
    if locations.ndim != 2 or locations.shape[0] != objective_lower.size or safety_lower.shape != objective_lower.shape or lipschitz < 0.0:
        raise ValueError("SafeOpt inputs are invalid")
    safe = safety_lower >= threshold
    if not np.any(safe):
        raise ValueError("SafeOpt requires a certified safe seed")
    conservative_best = float(np.max(objective_lower[safe]))
    maximizers = safe & (objective_upper >= conservative_best)
    distances = np.linalg.norm(locations[:, None, :] - locations[None, :, :], axis=2)
    unsafe = ~safe
    expanders = np.zeros(safe.shape, dtype=bool)
    for index in np.flatnonzero(safe):
        certified = safety_lower[index] - lipschitz * distances[index, unsafe]
        expanders[index] = (
            bool(np.any(certified >= threshold - 1e-12)) if np.any(unsafe) else False
        )
    return SafeOptSets(safe, maximizers, expanders)


def autoregressive_multifidelity_covariance(low_covariance: Sequence, discrepancy_covariance: Sequence, correlation: float) -> tuple[np.ndarray, np.ndarray]:
    low = np.asarray(low_covariance, dtype=np.float64)
    discrepancy = np.asarray(discrepancy_covariance, dtype=np.float64)
    if low.ndim != 2 or low.shape[0] != low.shape[1] or discrepancy.shape != low.shape or not np.isfinite(correlation):
        raise ValueError("multi-fidelity covariance inputs are invalid")
    return correlation * low, correlation**2 * low + discrepancy


def cost_aware_acquisition(acquisition: Sequence[float], costs: Sequence[float]) -> np.ndarray:
    values, expense = np.asarray(acquisition, dtype=np.float64), np.asarray(costs, dtype=np.float64)
    if values.shape != expense.shape or np.any(expense <= 0.0) or np.any(~np.isfinite(values)):
        raise ValueError("cost-aware acquisition inputs are invalid")
    return values / expense
