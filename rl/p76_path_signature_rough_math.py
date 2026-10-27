"""P76 path signatures, log-signatures, lead-lag paths, and CDEs."""

from __future__ import annotations

from math import factorial
from typing import Callable, Sequence

import numpy as np


def signature_dimension(channels: int, order: int, *, include_scalar: bool = True) -> int:
    if channels <= 0 or order < 0:
        raise ValueError("signature dimensions are invalid")
    start = 0 if include_scalar else 1
    return sum(channels**level for level in range(start, order + 1))


def _mobius(value: int) -> int:
    count = 0
    remaining = value
    prime = 2
    while prime * prime <= remaining:
        if remaining % prime == 0:
            remaining //= prime
            count += 1
            if remaining % prime == 0:
                return 0
            while remaining % prime == 0:
                remaining //= prime
        prime += 1
    if remaining > 1:
        count += 1
    return -1 if count % 2 else 1


def logsignature_dimension(channels: int, order: int) -> int:
    if channels <= 0 or order < 0:
        raise ValueError("log-signature dimensions are invalid")
    total = 0
    for level in range(1, order + 1):
        lie_dimension = sum(_mobius(divisor) * channels ** (level // divisor) for divisor in range(1, level + 1) if level % divisor == 0) // level
        total += lie_dimension
    return total


def signature_level_two(path: Sequence) -> tuple[np.ndarray, np.ndarray]:
    points = np.asarray(path, dtype=np.float64)
    if points.ndim != 2 or points.shape[0] == 0 or np.any(~np.isfinite(points)):
        raise ValueError("path is invalid")
    level_one = np.zeros(points.shape[1])
    level_two = np.zeros((points.shape[1], points.shape[1]))
    for increment in np.diff(points, axis=0):
        level_two += np.outer(level_one, increment) + 0.5 * np.outer(increment, increment)
        level_one += increment
    return level_one, level_two


def combine_level_two(left: tuple[Sequence, Sequence], right: tuple[Sequence, Sequence]) -> tuple[np.ndarray, np.ndarray]:
    left_one, left_two = np.asarray(left[0], dtype=np.float64), np.asarray(left[1], dtype=np.float64)
    right_one, right_two = np.asarray(right[0], dtype=np.float64), np.asarray(right[1], dtype=np.float64)
    if left_one.shape != right_one.shape or left_two.shape != right_two.shape or left_two.shape != (left_one.size, left_one.size):
        raise ValueError("signature levels are invalid")
    return left_one + right_one, left_two + np.outer(left_one, right_one) + right_two


def logsignature_level_two(path: Sequence) -> tuple[np.ndarray, np.ndarray]:
    level_one, level_two = signature_level_two(path)
    return level_one, level_two - 0.5 * np.outer(level_one, level_one)


def shuffle_residual(level_one: Sequence, level_two: Sequence) -> float:
    first, second = np.asarray(level_one, dtype=np.float64), np.asarray(level_two, dtype=np.float64)
    if second.shape != (first.size, first.size):
        raise ValueError("signature levels are invalid")
    return float(np.linalg.norm(np.outer(first, first) - second - second.T))


def lead_lag_transform(sequence: Sequence) -> np.ndarray:
    values = np.asarray(sequence, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0:
        raise ValueError("lead-lag sequence is invalid")
    result = [np.concatenate((values[0], values[0]))]
    for previous, current in zip(values[:-1], values[1:], strict=True):
        result.append(np.concatenate((current, previous)))
        result.append(np.concatenate((current, current)))
    return np.asarray(result)


def path_variation(path: Sequence, order: float = 1.0) -> float:
    points = np.asarray(path, dtype=np.float64)
    if points.ndim != 2 or points.shape[0] == 0 or order < 1.0:
        raise ValueError("variation inputs are invalid")
    increments = np.linalg.norm(np.diff(points, axis=0), axis=1)
    return float(np.sum(increments**order) ** (1.0 / order))


def controlled_euler(path: Sequence, initial_state: Sequence[float], vector_field: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    points = np.asarray(path, dtype=np.float64)
    state = np.asarray(initial_state, dtype=np.float64).copy()
    if points.ndim != 2 or points.shape[0] == 0 or state.ndim != 1:
        raise ValueError("CDE inputs are invalid")
    trajectory = [state.copy()]
    for increment in np.diff(points, axis=0):
        field = np.asarray(vector_field(state), dtype=np.float64)
        if field.shape != (state.size, points.shape[1]):
            raise ValueError("vector field has an invalid shape")
        state = state + field @ increment
        trajectory.append(state.copy())
    return np.asarray(trajectory)


def one_dimensional_signature(displacement: float, order: int) -> np.ndarray:
    if order < 0:
        raise ValueError("signature order is invalid")
    return np.asarray([displacement**level / factorial(level) for level in range(order + 1)])
