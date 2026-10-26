"""P58 queueing networks, fluid limits, and heavy-traffic approximations."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite, sqrt
from typing import Sequence

import numpy as np


def little_law(arrival_rate: float, mean_time: float) -> float:
    if not isfinite(arrival_rate) or not isfinite(mean_time) or arrival_rate < 0.0 or mean_time < 0.0:
        raise ValueError("Little-law inputs are invalid")
    return arrival_rate * mean_time


@dataclass(frozen=True)
class MM1Metrics:
    utilization: float
    mean_system_size: float
    mean_queue_size: float
    mean_system_time: float
    mean_waiting_time: float


def mm1_metrics(arrival_rate: float, service_rate: float) -> MM1Metrics:
    if not isfinite(arrival_rate) or not isfinite(service_rate) or arrival_rate < 0.0 or service_rate <= arrival_rate:
        raise ValueError("M/M/1 requires 0 <= arrival_rate < service_rate")
    utilization = arrival_rate / service_rate
    mean_system_size = utilization / (1.0 - utilization)
    mean_queue_size = utilization**2 / (1.0 - utilization)
    mean_system_time = 1.0 / (service_rate - arrival_rate)
    mean_waiting_time = utilization / (service_rate - arrival_rate)
    return MM1Metrics(utilization, mean_system_size, mean_queue_size, mean_system_time, mean_waiting_time)


def jackson_traffic_rates(external_arrivals: Sequence[float], routing_matrix: Sequence) -> np.ndarray:
    external = np.asarray(external_arrivals, dtype=np.float64)
    routing = np.asarray(routing_matrix, dtype=np.float64)
    if external.ndim != 1 or external.size == 0 or routing.shape != (external.size, external.size) or np.any(~np.isfinite(external)) or np.any(external < 0.0) or np.any(~np.isfinite(routing)) or np.any(routing < 0.0) or np.any(routing.sum(axis=1) > 1.0 + 1e-12):
        raise ValueError("Jackson traffic inputs are invalid")
    matrix = np.eye(external.size) - routing.T
    if np.linalg.matrix_rank(matrix) < external.size:
        raise ValueError("routing matrix has no transient open-network solution")
    rates = np.linalg.solve(matrix, external)
    if np.any(rates < -1e-10):
        raise ValueError("traffic equations produced negative rates")
    return np.maximum(rates, 0.0)


@dataclass(frozen=True)
class JacksonMetrics:
    arrival_rates: np.ndarray
    utilizations: np.ndarray
    mean_node_sizes: np.ndarray
    mean_total_size: float
    external_mean_time: float


def jackson_network_metrics(
    external_arrivals: Sequence[float], routing_matrix: Sequence, service_rates: Sequence[float]
) -> JacksonMetrics:
    rates = jackson_traffic_rates(external_arrivals, routing_matrix)
    service = np.asarray(service_rates, dtype=np.float64)
    if service.shape != rates.shape or np.any(~np.isfinite(service)) or np.any(service <= rates):
        raise ValueError("every Jackson node must be stable")
    utilization = rates / service
    sizes = utilization / (1.0 - utilization)
    external_total = float(np.sum(external_arrivals))
    mean_time = float(sizes.sum() / external_total) if external_total > 0.0 else 0.0
    return JacksonMetrics(rates, utilization, sizes, float(sizes.sum()), mean_time)


def kingman_mean_wait(
    arrival_rate: float,
    mean_service_time: float,
    arrival_scv: float,
    service_scv: float,
) -> float:
    if min(arrival_rate, mean_service_time, arrival_scv, service_scv) < 0.0 or not all(isfinite(value) for value in (arrival_rate, mean_service_time, arrival_scv, service_scv)):
        raise ValueError("Kingman inputs are invalid")
    utilization = arrival_rate * mean_service_time
    if utilization >= 1.0:
        raise ValueError("Kingman approximation requires utilization below one")
    return utilization / (1.0 - utilization) * (arrival_scv + service_scv) / 2.0 * mean_service_time


def infinite_server_mean_populations(arrival_rates: Sequence[float], mean_service_times: Sequence[float]) -> np.ndarray:
    arrival = np.asarray(arrival_rates, dtype=np.float64)
    service = np.asarray(mean_service_times, dtype=np.float64)
    if arrival.ndim != 1 or service.shape != arrival.shape or np.any(~np.isfinite(arrival)) or np.any(~np.isfinite(service)) or np.any(arrival < 0.0) or np.any(service < 0.0):
        raise ValueError("infinite-server inputs are invalid")
    return arrival * service


def fluid_queue_path(
    times: Sequence[float],
    initial_queue: float,
    arrival_rates: Sequence[float],
    service_rates: Sequence[float],
) -> np.ndarray:
    grid = np.asarray(times, dtype=np.float64)
    arrivals = np.asarray(arrival_rates, dtype=np.float64)
    services = np.asarray(service_rates, dtype=np.float64)
    if grid.ndim != 1 or grid.size < 2 or grid[0] != 0.0 or np.any(~np.isfinite(grid)) or np.any(np.diff(grid) <= 0.0) or arrivals.shape != (grid.size - 1,) or services.shape != arrivals.shape or np.any(arrivals < 0.0) or np.any(services < 0.0) or not isfinite(initial_queue) or initial_queue < 0.0:
        raise ValueError("fluid-queue inputs are invalid")
    queue = np.empty(grid.size)
    queue[0] = initial_queue
    for index, duration in enumerate(np.diff(grid)):
        queue[index + 1] = max(0.0, queue[index] + (arrivals[index] - services[index]) * duration)
    return queue


def reflected_brownian_path(
    times: Sequence[float],
    *,
    initial: float,
    drift: float,
    volatility: float,
    rng: np.random.Generator,
) -> np.ndarray:
    grid = np.asarray(times, dtype=np.float64)
    if grid.ndim != 1 or grid.size < 2 or grid[0] != 0.0 or np.any(np.diff(grid) <= 0.0) or min(initial, volatility) < 0.0 or not all(isfinite(value) for value in (initial, drift, volatility)):
        raise ValueError("reflected Brownian inputs are invalid")
    unconstrained = np.empty(grid.size)
    unconstrained[0] = initial
    for index, duration in enumerate(np.diff(grid), start=1):
        unconstrained[index] = unconstrained[index - 1] + drift * duration + volatility * sqrt(duration) * rng.normal()
    regulator = -np.minimum.accumulate(np.minimum(unconstrained, 0.0))
    return unconstrained + regulator


def square_root_staffing(offered_load: float, safety_factor: float) -> int:
    if not isfinite(offered_load) or not isfinite(safety_factor) or offered_load < 0.0 or safety_factor < 0.0:
        raise ValueError("staffing inputs are invalid")
    return int(ceil(offered_load + safety_factor * sqrt(offered_load)))
