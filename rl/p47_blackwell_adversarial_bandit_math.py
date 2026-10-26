"""P47 Blackwell approachability, EXP3, regret, monitoring, and calibration."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np


def exp3_probabilities(log_weights: Sequence[float], exploration: float) -> np.ndarray:
    values = np.asarray(log_weights, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or not isfinite(exploration) or not 0.0 <= exploration <= 1.0:
        raise ValueError("EXP3 inputs are invalid")
    weights = np.exp(values - np.max(values))
    base = weights / weights.sum()
    return (1.0 - exploration) * base + exploration / values.size


@dataclass(frozen=True)
class EXP3Result:
    actions: np.ndarray
    probabilities: np.ndarray
    final_probabilities: np.ndarray
    cumulative_loss: float


def run_exp3(losses: Sequence, *, exploration: float, seed: int = 0) -> EXP3Result:
    loss = np.asarray(losses, dtype=np.float64)
    if loss.ndim != 2 or loss.shape[1] == 0 or np.any(~np.isfinite(loss)) or np.any(loss < 0.0) or np.any(loss > 1.0):
        raise ValueError("loss matrix must be finite and in [0, 1]")
    rng = np.random.default_rng(seed)
    log_weights = np.zeros(loss.shape[1])
    actions = np.empty(loss.shape[0], dtype=int)
    probabilities = np.empty_like(loss)
    total = 0.0
    eta = exploration / loss.shape[1]
    for time in range(loss.shape[0]):
        probability = exp3_probabilities(log_weights, exploration)
        action = int(rng.choice(loss.shape[1], p=probability))
        estimate = loss[time, action] / probability[action]
        log_weights[action] -= eta * estimate
        actions[time] = action
        probabilities[time] = probability
        total += loss[time, action]
    return EXP3Result(actions, probabilities, exp3_probabilities(log_weights, exploration), total)


def external_regret(losses: Sequence, actions: Sequence[int]) -> float:
    loss = np.asarray(losses, dtype=np.float64)
    selected = np.asarray(actions)
    if loss.ndim != 2 or np.any(~np.isfinite(loss)) or selected.shape != (loss.shape[0],) or np.any(selected != np.floor(selected)) or np.any(selected < 0) or np.any(selected >= loss.shape[1]):
        raise ValueError("regret inputs are invalid")
    selected = selected.astype(int)
    actual = float(np.sum(loss[np.arange(loss.shape[0]), selected]))
    return actual - float(np.min(loss.sum(axis=0)))


def swap_regret(losses: Sequence, actions: Sequence[int]) -> float:
    loss = np.asarray(losses, dtype=np.float64)
    selected = np.asarray(actions)
    if loss.ndim != 2 or np.any(~np.isfinite(loss)) or selected.shape != (loss.shape[0],) or np.any(selected != np.floor(selected)) or np.any(selected < 0) or np.any(selected >= loss.shape[1]):
        raise ValueError("swap-regret inputs are invalid")
    selected = selected.astype(int)
    regret = 0.0
    for source in range(loss.shape[1]):
        mask = selected == source
        if np.any(mask):
            actual = float(np.sum(loss[mask, source]))
            regret += max(0.0, actual - float(np.min(loss[mask].sum(axis=0))))
    return regret


def blackwell_action(vector_payoffs: Sequence, average_payoff: Sequence[float], target_upper_bounds: Sequence[float]) -> int:
    payoffs = np.asarray(vector_payoffs, dtype=np.float64)
    average = np.asarray(average_payoff, dtype=np.float64)
    bounds = np.asarray(target_upper_bounds, dtype=np.float64)
    if payoffs.ndim != 2 or average.shape != (payoffs.shape[1],) or bounds.shape != average.shape:
        raise ValueError("Blackwell inputs are invalid")
    normal = np.maximum(average - bounds, 0.0)
    return int(np.argmin(payoffs @ normal))


def global_observability_residual(loss_matrix: Sequence, signal_matrices: Sequence[Sequence]) -> float:
    losses = np.asarray(loss_matrix, dtype=np.float64)
    signals = [np.asarray(matrix, dtype=np.float64) for matrix in signal_matrices]
    if losses.ndim != 2 or len(signals) != losses.shape[0] or any(matrix.ndim != 2 or matrix.shape[1] != losses.shape[1] for matrix in signals):
        raise ValueError("partial-monitoring inputs are invalid")
    span = np.vstack(signals).T
    residual = 0.0
    for first in range(losses.shape[0]):
        for second in range(first):
            difference = losses[first] - losses[second]
            coefficients, *_ = np.linalg.lstsq(span, difference, rcond=None)
            residual = max(residual, float(np.linalg.norm(span @ coefficients - difference)))
    return residual


def calibration_error(predictions: Sequence[float], outcomes: Sequence[float], *, bins: int = 10) -> float:
    predicted = np.asarray(predictions, dtype=np.float64)
    observed = np.asarray(outcomes, dtype=np.float64)
    if predicted.ndim != 1 or observed.shape != predicted.shape or np.any(predicted < 0.0) or np.any(predicted > 1.0) or np.any(observed < 0.0) or np.any(observed > 1.0) or bins < 1:
        raise ValueError("calibration inputs are invalid")
    assignments = np.minimum((predicted * bins).astype(int), bins - 1)
    error = 0.0
    for index in range(bins):
        mask = assignments == index
        if np.any(mask):
            error += float(np.mean(mask)) * abs(float(np.mean(predicted[mask]) - np.mean(observed[mask])))
    return error
