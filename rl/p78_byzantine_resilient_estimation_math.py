"""P78 Byzantine-resilient consensus, aggregation, and attack detection."""

from __future__ import annotations

from itertools import combinations
from typing import Sequence

import numpy as np


def trimmed_mean(values: Sequence[float], faults: int) -> float:
    data = np.sort(np.asarray(values, dtype=np.float64))
    if data.ndim != 1 or np.any(~np.isfinite(data)) or faults < 0 or data.size < 2 * faults + 1:
        raise ValueError("trimmed-mean inputs are invalid")
    return float(data[faults:data.size - faults if faults else None].mean())


def wmsr_scalar_step(self_value: float, neighbor_values: Sequence[float], faults: int, weights: Sequence[float] | None = None) -> tuple[float, np.ndarray]:
    neighbors = np.asarray(neighbor_values, dtype=np.float64)
    if neighbors.ndim != 1 or np.any(~np.isfinite(neighbors)) or faults < 0:
        raise ValueError("W-MSR inputs are invalid")
    high = np.flatnonzero(neighbors > self_value)
    low = np.flatnonzero(neighbors < self_value)
    remove_high = high[np.argsort(neighbors[high])[::-1][:faults]]
    remove_low = low[np.argsort(neighbors[low])[:faults]]
    keep = np.ones(neighbors.size, dtype=bool)
    keep[np.concatenate((remove_high, remove_low)).astype(int)] = False
    retained = np.concatenate(([self_value], neighbors[keep]))
    if weights is None:
        normalized = np.full(retained.size, 1.0 / retained.size)
    else:
        all_weights = np.asarray(weights, dtype=np.float64)
        if all_weights.shape != (neighbors.size + 1,) or np.any(all_weights < 0.0):
            raise ValueError("W-MSR weights are invalid")
        normalized = np.concatenate(([all_weights[0]], all_weights[1:][keep]))
        if normalized.sum() <= 0.0:
            raise ValueError("retained W-MSR weight is zero")
        normalized /= normalized.sum()
    return float(normalized @ retained), np.flatnonzero(keep)


def geometric_median(points: Sequence, weights: Sequence[float] | None = None, *, tolerance: float = 1e-9, max_iterations: int = 10000) -> np.ndarray:
    values = np.asarray(points, dtype=np.float64)
    probability = np.ones(values.shape[0]) if weights is None else np.asarray(weights, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0 or probability.shape != (values.shape[0],) or np.any(probability < 0.0) or probability.sum() <= 0.0 or tolerance <= 0.0:
        raise ValueError("geometric-median inputs are invalid")
    probability /= probability.sum()
    estimate = np.average(values, axis=0, weights=probability)
    for _ in range(max_iterations):
        distances = np.linalg.norm(values - estimate, axis=1)
        coincident = np.flatnonzero(distances <= tolerance)
        if coincident.size and probability[coincident].sum() >= 0.5:
            return values[coincident[0]].copy()
        inverse = probability / np.maximum(distances, tolerance)
        updated = np.sum(inverse[:, None] * values, axis=0) / inverse.sum()
        if np.linalg.norm(updated - estimate) <= tolerance:
            return updated
        estimate = updated
    raise RuntimeError("geometric median did not converge")


def innovation_score(innovation: Sequence[float], covariance: Sequence) -> float:
    residual, matrix = np.asarray(innovation, dtype=np.float64), np.asarray(covariance, dtype=np.float64)
    if matrix.shape != (residual.size, residual.size):
        raise ValueError("innovation inputs are invalid")
    return float(residual @ np.linalg.solve(matrix, residual))


def cusum_update(previous: float, score: float, drift_allowance: float) -> float:
    if previous < 0.0 or drift_allowance < 0.0 or not np.isfinite(score):
        raise ValueError("CUSUM inputs are invalid")
    return float(max(0.0, previous + score - drift_allowance))


def static_attack_residual(measurement_matrix: Sequence, measurement: Sequence[float]) -> np.ndarray:
    matrix, observed = np.asarray(measurement_matrix, dtype=np.float64), np.asarray(measurement, dtype=np.float64)
    if matrix.ndim != 2 or observed.shape != (matrix.shape[0],):
        raise ValueError("static residual inputs are invalid")
    return observed - matrix @ np.linalg.pinv(matrix) @ observed


def observability_matrix(transition: Sequence, observation: Sequence) -> np.ndarray:
    a, c = np.asarray(transition, dtype=np.float64), np.asarray(observation, dtype=np.float64)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or c.ndim != 2 or c.shape[1] != a.shape[0]:
        raise ValueError("observability inputs are invalid")
    return np.vstack([c @ np.linalg.matrix_power(a, power) for power in range(a.shape[0])])


def sparse_observability_audit(transition: Sequence, observation: Sequence, attacked_sensors: int) -> bool:
    a, c = np.asarray(transition, dtype=np.float64), np.asarray(observation, dtype=np.float64)
    remove = 2 * attacked_sensors
    if attacked_sensors < 0 or remove >= c.shape[0]:
        raise ValueError("sparse observability budget is invalid")
    for deleted in combinations(range(c.shape[0]), remove):
        retained = np.delete(c, deleted, axis=0)
        if np.linalg.matrix_rank(observability_matrix(a, retained)) < a.shape[0]:
            return False
    return True


def graph_r_reachable(adjacency: Sequence, subset: Sequence[int], robustness: int) -> bool:
    graph = np.asarray(adjacency, dtype=bool)
    selected = np.asarray(subset, dtype=int)
    if graph.ndim != 2 or graph.shape[0] != graph.shape[1] or robustness < 0 or np.any((selected < 0) | (selected >= graph.shape[0])):
        raise ValueError("graph reachability inputs are invalid")
    outside = np.setdiff1d(np.arange(graph.shape[0]), selected)
    return any(np.count_nonzero(graph[outside, node]) >= robustness for node in selected)
