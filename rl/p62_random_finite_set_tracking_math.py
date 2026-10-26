"""P62 finite-set multi-target tracking primitives."""

from __future__ import annotations

from itertools import product
from typing import Sequence

import numpy as np


def normalize_log_weights(log_weights: Sequence[float]) -> tuple[np.ndarray, float]:
    values = np.asarray(log_weights, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(np.isnan(values)) or np.all(np.isneginf(values)):
        raise ValueError("log weights are invalid")
    maximum = np.max(values)
    total = maximum + np.log(np.exp(values - maximum).sum())
    return np.exp(values - total), float(total)


def jpda_marginals(likelihood: Sequence, miss_weights: Sequence[float]) -> np.ndarray:
    likelihoods = np.asarray(likelihood, dtype=np.float64)
    misses = np.asarray(miss_weights, dtype=np.float64)
    if likelihoods.ndim != 2 or likelihoods.shape[0] == 0 or misses.shape != (likelihoods.shape[0],) or np.any(likelihoods < 0.0) or np.any(misses < 0.0) or np.any(~np.isfinite(likelihoods)) or np.any(~np.isfinite(misses)):
        raise ValueError("JPDA inputs are invalid")
    hypotheses: list[tuple[tuple[int, ...], float]] = []
    for assignment in product(range(likelihoods.shape[1] + 1), repeat=likelihoods.shape[0]):
        used = [value for value in assignment if value]
        if len(set(used)) != len(used):
            continue
        weight = float(np.prod([misses[i] if value == 0 else likelihoods[i, value - 1] for i, value in enumerate(assignment)]))
        hypotheses.append((assignment, weight))
    total = sum(weight for _, weight in hypotheses)
    if total <= 0.0:
        raise ValueError("JPDA hypotheses have zero mass")
    marginals = np.zeros((likelihoods.shape[0], likelihoods.shape[1] + 1))
    for assignment, weight in hypotheses:
        for target, value in enumerate(assignment):
            marginals[target, value] += weight / total
    return marginals


def phd_predict(weights: Sequence[float], survival_probability: Sequence[float] | float, birth_weights: Sequence[float] = ()) -> np.ndarray:
    current = np.asarray(weights, dtype=np.float64)
    survival = np.asarray(survival_probability, dtype=np.float64)
    births = np.asarray(birth_weights, dtype=np.float64)
    if current.ndim != 1 or births.ndim != 1 or np.any(current < 0.0) or np.any(births < 0.0) or np.any(~np.isfinite(current)) or survival.shape not in ((), current.shape) or np.any((survival < 0.0) | (survival > 1.0)):
        raise ValueError("PHD prediction inputs are invalid")
    return np.concatenate((current * survival, births))


def phd_measurement_update(weights: Sequence[float], detection_probability: Sequence[float], likelihood: Sequence[float], clutter_intensity: float) -> np.ndarray:
    weights_array = np.asarray(weights, dtype=np.float64)
    detection = np.asarray(detection_probability, dtype=np.float64)
    evidence = np.asarray(likelihood, dtype=np.float64)
    if weights_array.ndim != 1 or detection.shape != weights_array.shape or evidence.shape != weights_array.shape or np.any(weights_array < 0.0) or np.any((detection < 0.0) | (detection > 1.0)) or np.any(evidence < 0.0) or clutter_intensity < 0.0:
        raise ValueError("PHD update inputs are invalid")
    detected = detection * evidence * weights_array
    denominator = clutter_intensity + detected.sum()
    if denominator <= 0.0:
        raise ValueError("PHD evidence is zero")
    return detected / denominator


def prune_hypotheses(weights: Sequence[float], *, threshold: float = 0.0, maximum: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(weights, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(values < 0.0) or values.sum() <= 0.0 or threshold < 0.0 or maximum is not None and maximum <= 0:
        raise ValueError("hypothesis weights are invalid")
    indices = np.flatnonzero(values >= threshold)
    if maximum is not None:
        indices = indices[np.argsort(values[indices])[::-1][:maximum]]
    kept = values[indices]
    return indices, kept / kept.sum()
