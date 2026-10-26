"""P40 time-consistent risk recursion, Nested CVaR, and discrete BSDE tools."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Sequence

import numpy as np


def _probabilities(values: Sequence[float], probabilities: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    losses = np.asarray(values, dtype=np.float64)
    weights = np.asarray(probabilities, dtype=np.float64)
    if (
        losses.ndim != 1
        or losses.size == 0
        or weights.shape != losses.shape
        or np.any(~np.isfinite(losses))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not np.isclose(weights.sum(), 1.0)
    ):
        raise ValueError("losses or probabilities are invalid")
    return losses, weights


@dataclass(frozen=True)
class CVaRResult:
    value: float
    var: float
    tail_weights: np.ndarray


def discrete_cvar(
    losses: Sequence[float], probabilities: Sequence[float], *, alpha: float
) -> CVaRResult:
    """Upper-tail CVaR with an explicit worst-tail probability allocation."""

    values, weights = _probabilities(losses, probabilities)
    if not isfinite(alpha) or not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must be in [0, 1)")
    tail_mass = 1.0 - alpha
    order = np.argsort(values)[::-1]
    allocation = np.zeros_like(weights)
    remaining = tail_mass
    for index in order:
        taken = min(float(weights[index]), remaining)
        allocation[index] = taken / tail_mass
        remaining -= taken
        if remaining <= 1e-15:
            break
    cumulative = np.cumsum(weights[np.argsort(values)])
    ascending = np.argsort(values)
    var_index = min(int(np.searchsorted(cumulative, alpha, side="left")), values.size - 1)
    return CVaRResult(
        value=float(allocation @ values),
        var=float(values[ascending[var_index]]),
        tail_weights=allocation,
    )


def entropic_risk(
    losses: Sequence[float], probabilities: Sequence[float], *, risk_aversion: float
) -> float:
    values, weights = _probabilities(losses, probabilities)
    if not isfinite(risk_aversion) or risk_aversion < 0.0:
        raise ValueError("risk_aversion must be nonnegative")
    if risk_aversion == 0.0:
        return float(weights @ values)
    scaled = risk_aversion * values
    offset = float(np.max(scaled))
    return float((offset + log(float(weights @ np.exp(scaled - offset)))) / risk_aversion)


@dataclass(frozen=True)
class NestedRiskResult:
    initial_value: float
    value_functions: np.ndarray


def nested_cvar_markov_chain(
    transitions: Sequence,
    stage_costs: Sequence,
    terminal_costs: Sequence[float],
    initial_distribution: Sequence[float],
    *,
    alpha: float,
) -> NestedRiskResult:
    """Backward time-consistent CVaR recursion for a fixed finite-state policy."""

    kernel = np.asarray(transitions, dtype=np.float64)
    costs = np.asarray(stage_costs, dtype=np.float64)
    terminal = np.asarray(terminal_costs, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    if (
        kernel.ndim != 3
        or kernel.shape[1] != kernel.shape[2]
        or costs.shape != kernel.shape[:2]
        or terminal.shape != (kernel.shape[1],)
        or initial.shape != terminal.shape
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or np.any(~np.isfinite(costs))
        or np.any(~np.isfinite(terminal))
        or np.any(initial < 0.0)
        or not np.isclose(initial.sum(), 1.0)
    ):
        raise ValueError("Markov risk inputs are invalid")
    horizon, states = costs.shape
    values = np.empty((horizon + 1, states), dtype=np.float64)
    values[-1] = terminal
    for time in range(horizon - 1, -1, -1):
        for state in range(states):
            risk = discrete_cvar(values[time + 1], kernel[time, state], alpha=alpha)
            values[time, state] = costs[time, state] + risk.value
    initial_value = discrete_cvar(values[0], initial, alpha=alpha).value
    return NestedRiskResult(initial_value, values)


def bsde_backward_euler(
    terminal_values: Sequence[float],
    drivers: Sequence,
    information_groups: Sequence,
    *,
    dt: float,
) -> np.ndarray:
    """Euler BSDE recursion using conditional means over supplied information cells."""

    terminal = np.asarray(terminal_values, dtype=np.float64)
    driver = np.asarray(drivers, dtype=np.float64)
    groups = np.asarray(information_groups)
    if (
        terminal.ndim != 1
        or terminal.size == 0
        or driver.ndim != 2
        or driver.shape[1] != terminal.size
        or groups.shape != driver.shape
        or np.any(~np.isfinite(terminal))
        or np.any(~np.isfinite(driver))
        or not isfinite(dt)
        or dt <= 0.0
    ):
        raise ValueError("BSDE inputs are invalid")
    result = np.empty((driver.shape[0] + 1, terminal.size), dtype=np.float64)
    result[-1] = terminal
    for time in range(driver.shape[0] - 1, -1, -1):
        target = result[time + 1] + dt * driver[time]
        for group in np.unique(groups[time]):
            mask = groups[time] == group
            result[time, mask] = float(np.mean(target[mask]))
    return result
