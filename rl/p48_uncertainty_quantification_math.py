"""P48 PCE, sparse-grid index sets, MLMC, and dynamic Sobol analysis."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Sequence

import numpy as np


def total_degree_indices(variable_count: int, degree: int) -> tuple[tuple[int, ...], ...]:
    if variable_count < 1 or degree < 0:
        raise ValueError("PCE dimensions are invalid")
    return tuple(index for index in product(range(degree + 1), repeat=variable_count) if sum(index) <= degree)


@dataclass(frozen=True)
class PCEStatistics:
    mean: float
    variance: float
    first_order_sobol: np.ndarray
    total_sobol: np.ndarray


def pce_statistics(coefficients: Sequence[float], indices: Sequence[Sequence[int]]) -> PCEStatistics:
    coefficient = np.asarray(coefficients, dtype=np.float64)
    powers = np.asarray(indices, dtype=int)
    if coefficient.ndim != 1 or powers.ndim != 2 or powers.shape[0] != coefficient.size or np.any(powers < 0) or np.any(~np.isfinite(coefficient)):
        raise ValueError("PCE inputs are invalid")
    constant = np.all(powers == 0, axis=1)
    if np.count_nonzero(constant) != 1:
        raise ValueError("PCE basis must contain exactly one constant")
    contributions = coefficient**2
    variance = float(np.sum(contributions[~constant]))
    first = np.zeros(powers.shape[1])
    total = np.zeros(powers.shape[1])
    if variance > 0.0:
        for variable in range(powers.shape[1]):
            active = powers[:, variable] > 0
            only = active & (np.count_nonzero(powers, axis=1) == 1)
            first[variable] = float(np.sum(contributions[only]) / variance)
            total[variable] = float(np.sum(contributions[active]) / variance)
    return PCEStatistics(float(coefficient[constant][0]), variance, first, total)


def dynamic_sobol_indices(
    coefficient_trajectory: Sequence,
    indices: Sequence[Sequence[int]],
    times: Sequence[float],
) -> tuple[np.ndarray, np.ndarray]:
    coefficients = np.asarray(coefficient_trajectory, dtype=np.float64)
    time = np.asarray(times, dtype=np.float64)
    if coefficients.ndim != 2 or time.shape != (coefficients.shape[0],) or np.any(np.diff(time) <= 0.0):
        raise ValueError("dynamic Sobol inputs are invalid")
    first = np.vstack([pce_statistics(row, indices).first_order_sobol for row in coefficients])
    total = np.vstack([pce_statistics(row, indices).total_sobol for row in coefficients])
    duration = time[-1] - time[0]
    if duration <= 0.0:
        raise ValueError("at least two increasing times are required")
    return np.trapezoid(first, time, axis=0) / duration, np.trapezoid(total, time, axis=0) / duration


def smolyak_level_indices(dimension: int, level: int) -> tuple[tuple[int, ...], ...]:
    if dimension < 1 or level < 1:
        raise ValueError("Smolyak dimensions are invalid")
    maximum = level + dimension - 1
    return tuple(index for index in product(range(1, maximum + 1), repeat=dimension) if sum(index) <= maximum)


def mlmc_optimal_allocation(variances: Sequence[float], costs: Sequence[float], *, rmse: float) -> np.ndarray:
    variance = np.asarray(variances, dtype=np.float64)
    cost = np.asarray(costs, dtype=np.float64)
    if variance.ndim != 1 or cost.shape != variance.shape or np.any(variance < 0.0) or np.any(cost <= 0.0) or not isfinite(rmse) or rmse <= 0.0:
        raise ValueError("MLMC inputs are invalid")
    scale = 2.0 * np.sum(np.sqrt(variance * cost)) / (rmse**2)
    return np.maximum(1, np.ceil(scale * np.sqrt(variance / cost))).astype(int)


def mlmc_estimate(level_corrections: Sequence[Sequence[float]]) -> float:
    levels = [np.asarray(level, dtype=np.float64) for level in level_corrections]
    if not levels or any(level.ndim != 1 or level.size == 0 or np.any(~np.isfinite(level)) for level in levels):
        raise ValueError("MLMC corrections are invalid")
    return float(sum(np.mean(level) for level in levels))
