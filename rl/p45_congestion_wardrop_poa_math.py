"""P45 Wardrop equilibria, congestion potentials, and price-of-anarchy audits."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np


def _affine_inputs(slopes: Sequence[float], intercepts: Sequence[float], demand: float) -> tuple[np.ndarray, np.ndarray]:
    slope = np.asarray(slopes, dtype=np.float64)
    intercept = np.asarray(intercepts, dtype=np.float64)
    if (
        slope.ndim != 1
        or slope.size == 0
        or intercept.shape != slope.shape
        or np.any(~np.isfinite(slope))
        or np.any(slope <= 0.0)
        or np.any(~np.isfinite(intercept))
        or not isfinite(demand)
        or demand < 0.0
    ):
        raise ValueError("affine congestion inputs are invalid")
    return slope, intercept


def _water_fill(slopes: np.ndarray, intercepts: np.ndarray, demand: float, multiplier: float) -> np.ndarray:
    if demand == 0.0:
        return np.zeros_like(slopes)
    low = float(np.min(intercepts))
    high = float(np.max(intercepts) + multiplier * np.max(slopes) * demand + 1.0)
    for _ in range(100):
        level = (low + high) / 2.0
        flow = np.maximum(0.0, (level - intercepts) / (multiplier * slopes))
        if flow.sum() < demand:
            low = level
        else:
            high = level
    flow = np.maximum(0.0, ((low + high) / 2.0 - intercepts) / (multiplier * slopes))
    return flow * demand / flow.sum()


@dataclass(frozen=True)
class ParallelRoutingResult:
    flows: np.ndarray
    latencies: np.ndarray
    total_cost: float
    variational_gap: float


def wardrop_parallel_affine(
    slopes: Sequence[float], intercepts: Sequence[float], demand: float
) -> ParallelRoutingResult:
    slope, intercept = _affine_inputs(slopes, intercepts, demand)
    flow = _water_fill(slope, intercept, demand, 1.0)
    latency = slope * flow + intercept
    gap = wardrop_variational_gap(flow, latency, demand)
    return ParallelRoutingResult(flow, latency, float(flow @ latency), gap)


def social_optimum_parallel_affine(
    slopes: Sequence[float], intercepts: Sequence[float], demand: float
) -> ParallelRoutingResult:
    slope, intercept = _affine_inputs(slopes, intercepts, demand)
    flow = _water_fill(slope, intercept, demand, 2.0)
    latency = slope * flow + intercept
    return ParallelRoutingResult(
        flow, latency, float(flow @ latency), wardrop_variational_gap(flow, latency, demand)
    )


def wardrop_variational_gap(flows: Sequence[float], latencies: Sequence[float], demand: float) -> float:
    flow = np.asarray(flows, dtype=np.float64)
    latency = np.asarray(latencies, dtype=np.float64)
    if (
        flow.ndim != 1
        or latency.shape != flow.shape
        or np.any(flow < 0.0)
        or np.any(~np.isfinite(flow))
        or np.any(~np.isfinite(latency))
        or demand < 0.0
        or not np.isclose(flow.sum(), demand)
    ):
        raise ValueError("variational-gap inputs are invalid")
    return float(flow @ latency - demand * np.min(latency))


def price_of_anarchy(equilibrium_cost: float, optimum_cost: float) -> float:
    if not isfinite(equilibrium_cost) or not isfinite(optimum_cost) or equilibrium_cost < 0.0 or optimum_cost <= 0.0:
        raise ValueError("costs are invalid")
    return equilibrium_cost / optimum_cost


def smoothness_poa_bound(smoothness_lambda: float, smoothness_mu: float) -> float:
    if not isfinite(smoothness_lambda) or not isfinite(smoothness_mu) or smoothness_lambda < 0.0 or not 0.0 <= smoothness_mu < 1.0:
        raise ValueError("smoothness parameters are invalid")
    return smoothness_lambda / (1.0 - smoothness_mu)


def rosenthal_potential(loads: Sequence[int], latency_table: Sequence) -> float:
    load = np.asarray(loads)
    table = np.asarray(latency_table, dtype=np.float64)
    if load.ndim != 1 or table.ndim != 2 or table.shape[0] != load.size or np.any(load < 0) or np.any(load != np.floor(load)) or np.max(load, initial=0) >= table.shape[1]:
        raise ValueError("Rosenthal potential inputs are invalid")
    return float(sum(np.sum(table[resource, 1 : int(count) + 1]) for resource, count in enumerate(load)))
