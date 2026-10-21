"""Causal estimators for offline strategy and ablation evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from statistics import NormalDist
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class DoublyRobustEstimate:
    effect: float
    standard_error: float
    confidence_interval: tuple[float, float]
    samples: int


def doubly_robust_ate(
    outcomes: Sequence[float],
    treatments: Sequence[int | bool],
    propensities: Sequence[float],
    predicted_treated: Sequence[float],
    predicted_control: Sequence[float],
    *,
    confidence: float = 0.95,
    propensity_clip: float = 1e-3,
) -> DoublyRobustEstimate:
    """Estimate an average treatment effect with an augmented IPW score."""

    outcome = np.asarray(outcomes, dtype=np.float64)
    treatment = np.asarray(treatments, dtype=np.float64)
    propensity = np.asarray(propensities, dtype=np.float64)
    treated = np.asarray(predicted_treated, dtype=np.float64)
    control = np.asarray(predicted_control, dtype=np.float64)
    shapes = {array.shape for array in (outcome, treatment, propensity, treated, control)}
    if len(shapes) != 1 or outcome.ndim != 1 or outcome.size < 2:
        raise ValueError("causal vectors must be aligned and contain at least two samples")
    if any(np.any(~np.isfinite(array)) for array in (outcome, propensity, treated, control)):
        raise ValueError("causal inputs must be finite")
    if np.any((treatment != 0.0) & (treatment != 1.0)):
        raise ValueError("treatments must be binary")
    if not 0.0 < propensity_clip < 0.5:
        raise ValueError("propensity_clip must be in (0, 0.5)")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    propensity = np.clip(propensity, propensity_clip, 1.0 - propensity_clip)
    scores = (
        treated
        - control
        + treatment * (outcome - treated) / propensity
        - (1.0 - treatment) * (outcome - control) / (1.0 - propensity)
    )
    effect = float(scores.mean())
    standard_error = float(scores.std(ddof=1) / sqrt(scores.size))
    critical = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    radius = critical * standard_error
    if not all(isfinite(value) for value in (effect, standard_error, radius)):
        raise ValueError("causal estimate is not finite")
    return DoublyRobustEstimate(
        effect,
        standard_error,
        (effect - radius, effect + radius),
        int(scores.size),
    )
