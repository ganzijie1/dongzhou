"""P41 discounted Gittins/Whittle indices and restless-bandit diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np


def _kernel(value: Sequence, states: int | None = None) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.float64)
    expected = matrix.shape[0] if matrix.ndim == 2 else -1
    if (
        matrix.ndim != 2
        or matrix.shape != (expected, expected)
        or (states is not None and expected != states)
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix.sum(axis=1), 1.0)
    ):
        raise ValueError("transition kernel is invalid")
    return matrix


def _discount(value: float) -> float:
    if not isfinite(value) or not 0.0 <= value < 1.0:
        raise ValueError("discount must be in [0, 1)")
    return value


def _retirement_value(kernel: np.ndarray, rewards: np.ndarray, charge: float, discount: float) -> np.ndarray:
    value = np.zeros(rewards.size)
    for _ in range(10000):
        updated = np.maximum(0.0, rewards - charge + discount * kernel @ value)
        if np.max(np.abs(updated - value)) < 1e-12:
            return updated
        value = updated
    raise RuntimeError("retirement value iteration did not converge")


def gittins_index(
    transition: Sequence, rewards: Sequence[float], state: int, *, discount: float
) -> float:
    """Discounted Gittins retirement index for a finite Markov arm."""

    kernel = _kernel(transition)
    reward = np.asarray(rewards, dtype=np.float64)
    beta = _discount(discount)
    if reward.shape != (kernel.shape[0],) or np.any(~np.isfinite(reward)) or not 0 <= state < reward.size:
        raise ValueError("Gittins inputs are invalid")
    span = max(1.0, float(np.ptp(reward))) / max(1e-12, 1.0 - beta)
    low, high = float(np.min(reward) - span), float(np.max(reward) + span)
    for _ in range(100):
        middle = (low + high) / 2.0
        continuation = reward[state] - middle + beta * kernel[state] @ _retirement_value(
            kernel, reward, middle, beta
        )
        if continuation > 0.0:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _restless_value(
    active_kernel: np.ndarray,
    passive_kernel: np.ndarray,
    active_reward: np.ndarray,
    passive_reward: np.ndarray,
    subsidy: float,
    discount: float,
) -> tuple[np.ndarray, np.ndarray]:
    value = np.zeros(active_reward.size)
    for _ in range(10000):
        active = active_reward + discount * active_kernel @ value
        passive = passive_reward + subsidy + discount * passive_kernel @ value
        updated = np.maximum(active, passive)
        if np.max(np.abs(updated - value)) < 1e-12:
            return updated, passive >= active - 1e-11
        value = updated
    raise RuntimeError("restless-bandit value iteration did not converge")


@dataclass(frozen=True)
class WhittleResult:
    indices: np.ndarray
    indexable: bool
    subsidies: np.ndarray
    passive_sets: np.ndarray


def whittle_indices(
    active_transition: Sequence,
    passive_transition: Sequence,
    active_rewards: Sequence[float],
    passive_rewards: Sequence[float],
    *,
    discount: float,
    subsidy_bounds: tuple[float, float] = (-100.0, 100.0),
    diagnostic_points: int = 201,
) -> WhittleResult:
    active_kernel = _kernel(active_transition)
    passive_kernel = _kernel(passive_transition, active_kernel.shape[0])
    active = np.asarray(active_rewards, dtype=np.float64)
    passive = np.asarray(passive_rewards, dtype=np.float64)
    beta = _discount(discount)
    low_bound, high_bound = subsidy_bounds
    if (
        active.shape != (active_kernel.shape[0],)
        or passive.shape != active.shape
        or np.any(~np.isfinite(active))
        or np.any(~np.isfinite(passive))
        or not isfinite(low_bound)
        or not isfinite(high_bound)
        or low_bound >= high_bound
        or diagnostic_points < 2
    ):
        raise ValueError("Whittle inputs are invalid")
    subsidies = np.linspace(low_bound, high_bound, diagnostic_points)
    sets = np.vstack(
        [
            _restless_value(active_kernel, passive_kernel, active, passive, value, beta)[1]
            for value in subsidies
        ]
    )
    indexable = bool(np.all(np.diff(sets.astype(np.int8), axis=0) >= 0))
    indices = np.full(active.size, np.nan)
    for state in range(active.size):
        lo, hi = low_bound, high_bound
        _, lo_set = _restless_value(active_kernel, passive_kernel, active, passive, lo, beta)
        _, hi_set = _restless_value(active_kernel, passive_kernel, active, passive, hi, beta)
        if lo_set[state] or not hi_set[state]:
            continue
        for _ in range(80):
            middle = (lo + hi) / 2.0
            _, selected = _restless_value(
                active_kernel, passive_kernel, active, passive, middle, beta
            )
            if selected[state]:
                hi = middle
            else:
                lo = middle
        indices[state] = (lo + hi) / 2.0
    return WhittleResult(indices, indexable, subsidies, sets)


def select_whittle_arms(indices: Sequence[float], capacity: int) -> np.ndarray:
    values = np.asarray(indices, dtype=np.float64)
    if values.ndim != 1 or np.any(~np.isfinite(values)) or not 0 <= capacity <= values.size:
        raise ValueError("selection inputs are invalid")
    return np.argsort(values, kind="stable")[::-1][:capacity]
