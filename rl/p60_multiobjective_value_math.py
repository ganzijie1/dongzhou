"""P60 vector values, non-dominated Bellman backups, Chebyshev, and hypervolume."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

import numpy as np


def nondominated_mask(values: Sequence, *, tolerance: float = 1e-12) -> np.ndarray:
    points = np.asarray(values, dtype=np.float64)
    if points.ndim != 2 or points.shape[0] == 0 or points.shape[1] == 0 or np.any(~np.isfinite(points)) or tolerance < 0.0:
        raise ValueError("Pareto values are invalid")
    keep = np.ones(points.shape[0], dtype=bool)
    for index, point in enumerate(points):
        dominates = np.all(points >= point - tolerance, axis=1) & np.any(points > point + tolerance, axis=1)
        dominates[index] = False
        if np.any(dominates):
            keep[index] = False
    return keep


def nondominated(values: Sequence, *, tolerance: float = 1e-12) -> np.ndarray:
    points = np.asarray(values, dtype=np.float64)
    mask = nondominated_mask(points, tolerance=tolerance)
    result = points[mask]
    if result.size == 0:
        return result
    rounded = np.round(result / max(tolerance, 1e-15)) if tolerance > 0.0 else result
    _, unique = np.unique(rounded, axis=0, return_index=True)
    return result[np.sort(unique)]


def weighted_minkowski_sum(value_sets: Sequence[Sequence], weights: Sequence[float]) -> np.ndarray:
    sets = [np.asarray(values, dtype=np.float64) for values in value_sets]
    probability = np.asarray(weights, dtype=np.float64)
    if not sets or probability.shape != (len(sets),) or np.any(~np.isfinite(probability)) or np.any(probability < 0.0) or not np.isclose(probability.sum(), 1.0) or any(values.ndim != 2 or values.shape[0] == 0 for values in sets) or len({values.shape[1] for values in sets}) != 1:
        raise ValueError("weighted Minkowski inputs are invalid")
    candidates = []
    for selection in product(*(range(values.shape[0]) for values in sets)):
        candidates.append(sum(probability[index] * sets[index][choice] for index, choice in enumerate(selection)))
    return np.asarray(candidates)


@dataclass(frozen=True)
class BellmanFront:
    values: np.ndarray
    actions: np.ndarray


def nondominated_bellman_backup(
    transition_probabilities: Sequence,
    rewards: Sequence,
    successor_fronts: Sequence[Sequence],
    *,
    discount: float,
    tolerance: float = 1e-12,
) -> BellmanFront:
    transition = np.asarray(transition_probabilities, dtype=np.float64)
    reward = np.asarray(rewards, dtype=np.float64)
    fronts = [np.asarray(front, dtype=np.float64) for front in successor_fronts]
    if transition.ndim != 2 or transition.shape[0] == 0 or reward.ndim != 3 or reward.shape[:2] != transition.shape or not fronts or len(fronts) != transition.shape[1] or any(front.ndim != 2 or front.shape[0] == 0 or front.shape[1] != reward.shape[2] for front in fronts) or np.any(transition < 0.0) or np.any(~np.isfinite(transition)) or not np.allclose(transition.sum(axis=1), 1.0) or np.any(~np.isfinite(reward)) or not 0.0 <= discount < 1.0:
        raise ValueError("non-dominated Bellman inputs are invalid")
    candidates = []
    actions = []
    for action in range(transition.shape[0]):
        active = np.flatnonzero(transition[action] > 0.0)
        sets = [reward[action, state][None, :] + discount * fronts[state] for state in active]
        values = weighted_minkowski_sum(sets, transition[action, active])
        candidates.extend(values)
        actions.extend([action] * values.shape[0])
    candidate_array = np.asarray(candidates)
    mask = nondominated_mask(candidate_array, tolerance=tolerance)
    selected = candidate_array[mask]
    selected_actions = np.asarray(actions, dtype=int)[mask]
    return BellmanFront(selected, selected_actions)


def chebyshev_loss(
    values: Sequence,
    weights: Sequence[float],
    reference: Sequence[float],
    *,
    augmentation: float = 0.0,
) -> np.ndarray:
    points = np.asarray(values, dtype=np.float64)
    weight = np.asarray(weights, dtype=np.float64)
    ideal = np.asarray(reference, dtype=np.float64)
    if points.ndim != 2 or points.shape[0] == 0 or weight.shape != (points.shape[1],) or ideal.shape != weight.shape or np.any(~np.isfinite(points)) or np.any(~np.isfinite(weight)) or np.any(weight <= 0.0) or not np.isclose(weight.sum(), 1.0) or np.any(~np.isfinite(ideal)) or not np.isfinite(augmentation) or augmentation < 0.0:
        raise ValueError("Chebyshev inputs are invalid")
    gaps = weight * (ideal - points)
    return np.max(gaps, axis=1) + augmentation * np.sum(gaps, axis=1)


def hypervolume_2d(values: Sequence, reference: Sequence[float]) -> float:
    points = nondominated(values)
    ref = np.asarray(reference, dtype=np.float64)
    if points.shape[1] != 2 or ref.shape != (2,) or np.any(~np.isfinite(ref)) or np.any(points < ref - 1e-12):
        raise ValueError("2D hypervolume inputs are invalid")
    order = np.argsort(points[:, 0])
    sorted_points = points[order]
    volume = 0.0
    previous_x = ref[0]
    for x, y in sorted_points:
        volume += (x - previous_x) * (y - ref[1])
        previous_x = x
    return float(volume)


def hypervolume_contributions_2d(values: Sequence, reference: Sequence[float]) -> np.ndarray:
    points = np.asarray(values, dtype=np.float64)
    total = hypervolume_2d(points, reference)
    contributions = np.zeros(points.shape[0])
    for index in range(points.shape[0]):
        remaining = np.delete(points, index, axis=0)
        contributions[index] = total if remaining.shape[0] == 0 else total - hypervolume_2d(remaining, reference)
    return contributions
