"""P50 finite reachability, backward tubes, and pursuit-evasion primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Sequence

import numpy as np


def _state_mask(states: Sequence[int], state_count: int) -> np.ndarray:
    mask = np.zeros(state_count, dtype=bool)
    indices = np.asarray(states)
    if indices.ndim != 1 or np.any(indices != np.floor(indices)) or np.any(indices < 0) or np.any(indices >= state_count):
        raise ValueError("state indices are invalid")
    mask[indices.astype(int)] = True
    return mask


@dataclass(frozen=True)
class BackwardReachabilityResult:
    layers: np.ndarray
    entry_time: np.ndarray
    policy: np.ndarray


def backward_reachable_tube(
    successors: Sequence,
    target_states: Sequence[int],
    avoid_states: Sequence[int],
    horizon: int,
) -> BackwardReachabilityResult:
    """Compute states that can force target entry against every disturbance."""
    transition = np.asarray(successors)
    if transition.ndim != 3 or transition.shape[0] == 0 or transition.shape[1] == 0 or transition.shape[2] == 0:
        raise ValueError("successors must have shape [state, action, disturbance]")
    state_count = transition.shape[0]
    if np.any(transition != np.floor(transition)) or np.any(transition < 0) or np.any(transition >= state_count):
        raise ValueError("successor indices are invalid")
    if not isinstance(horizon, int) or horizon < 0:
        raise ValueError("horizon must be a non-negative integer")
    transition = transition.astype(int)
    target = _state_mask(target_states, state_count)
    avoid = _state_mask(avoid_states, state_count)
    if np.any(target & avoid):
        raise ValueError("target and avoid sets must be disjoint")

    layers = np.zeros((horizon + 1, state_count), dtype=bool)
    layers[0] = target
    entry_time = np.full(state_count, -1, dtype=int)
    entry_time[target] = 0
    policy = np.full((horizon + 1, state_count), -1, dtype=int)
    current = target.copy()
    for step in range(1, horizon + 1):
        updated = current.copy()
        for state in range(state_count):
            if updated[state] or avoid[state]:
                continue
            for action in range(transition.shape[1]):
                if np.all(current[transition[state, action]]):
                    updated[state] = True
                    entry_time[state] = step
                    policy[step, state] = action
                    break
        layers[step] = updated
        current = updated
    return BackwardReachabilityResult(layers, entry_time, policy)


@dataclass(frozen=True)
class ReachAvoidResult:
    values: np.ndarray
    policy: np.ndarray


def stochastic_reach_avoid(
    transitions: Sequence,
    target_states: Sequence[int],
    avoid_states: Sequence[int],
    horizon: int,
) -> ReachAvoidResult:
    probability = np.asarray(transitions, dtype=np.float64)
    if probability.ndim != 3 or probability.shape[0] == 0 or probability.shape[2] != probability.shape[0] or np.any(~np.isfinite(probability)) or np.any(probability < 0.0) or not np.allclose(probability.sum(axis=2), 1.0):
        raise ValueError("transitions must be row-stochastic [state, action, next_state]")
    if not isinstance(horizon, int) or horizon < 0:
        raise ValueError("horizon must be a non-negative integer")
    state_count = probability.shape[0]
    target = _state_mask(target_states, state_count)
    avoid = _state_mask(avoid_states, state_count)
    if np.any(target & avoid):
        raise ValueError("target and avoid sets must be disjoint")
    values = np.zeros((horizon + 1, state_count), dtype=np.float64)
    values[0, target] = 1.0
    policy = np.full((horizon, state_count), -1, dtype=int)
    for step in range(1, horizon + 1):
        q_values = probability @ values[step - 1]
        policy[step - 1] = np.argmax(q_values, axis=1)
        values[step] = np.max(q_values, axis=1)
        values[step, target] = 1.0
        values[step, avoid] = 0.0
    return ReachAvoidResult(values, policy)


def intercept_time(
    relative_position: Sequence[float],
    relative_velocity: Sequence[float],
    pursuer_speed: float,
) -> float:
    position = np.asarray(relative_position, dtype=np.float64)
    velocity = np.asarray(relative_velocity, dtype=np.float64)
    if position.ndim != 1 or position.size == 0 or velocity.shape != position.shape or np.any(~np.isfinite(position)) or np.any(~np.isfinite(velocity)) or not isfinite(pursuer_speed) or pursuer_speed <= 0.0:
        raise ValueError("intercept inputs are invalid")
    a = float(velocity @ velocity - pursuer_speed**2)
    b = float(2.0 * position @ velocity)
    c = float(position @ position)
    if c == 0.0:
        return 0.0
    if abs(a) < 1e-12:
        return -c / b if b < 0.0 else float("inf")
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return float("inf")
    roots = [(-b - sqrt(discriminant)) / (2.0 * a), (-b + sqrt(discriminant)) / (2.0 * a)]
    feasible = [root for root in roots if root >= 0.0]
    return min(feasible) if feasible else float("inf")
