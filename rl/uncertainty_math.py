"""Information, particle-belief, chance-constraint, and conformal methods."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil, isfinite, log
from typing import Hashable, Mapping, Sequence

import numpy as np

from rl.belief_risk import conditional_value_at_risk


State = Hashable
Observation = Hashable


def _probabilities(values: Sequence[float]) -> np.ndarray:
    probabilities = np.asarray(values, dtype=np.float64)
    if probabilities.ndim != 1 or probabilities.size == 0:
        raise ValueError("probabilities must be a non-empty vector")
    if np.any(~np.isfinite(probabilities)) or np.any(probabilities < 0.0):
        raise ValueError("probabilities must be finite and non-negative")
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("probabilities must contain positive mass")
    return probabilities / total


def shannon_entropy(values: Sequence[float], *, base: float = 2.0) -> float:
    """Return entropy after normalizing non-negative probability mass."""

    if not isfinite(base) or base <= 0.0 or abs(base - 1.0) <= 1e-12:
        raise ValueError("entropy base must be positive and different from one")
    probabilities = _probabilities(values)
    positive = probabilities[probabilities > 0.0]
    return float(-np.sum(positive * np.log(positive)) / log(base))


def binary_entropy(probability: float) -> float:
    value = float(probability)
    if not 0.0 <= value <= 1.0:
        raise ValueError("binary probability must be in [0, 1]")
    if value in (0.0, 1.0):
        return 0.0
    return -value * log(value, 2.0) - (1.0 - value) * log(1.0 - value, 2.0)


def expected_information_gain(
    prior: Mapping[State, float],
    observation_likelihoods: Mapping[Observation, Mapping[State, float]],
) -> float:
    """Return mutual information I(state; observation) in bits."""

    states = tuple(prior)
    if not states or not observation_likelihoods:
        raise ValueError("information gain needs states and observations")
    prior_values = _probabilities([float(prior[state]) for state in states])
    likelihood = np.asarray(
        [
            [float(observation_likelihoods[observation].get(state, 0.0)) for state in states]
            for observation in observation_likelihoods
        ],
        dtype=np.float64,
    )
    if np.any(~np.isfinite(likelihood)) or np.any(likelihood < 0.0):
        raise ValueError("observation likelihoods must be finite and non-negative")
    state_totals = likelihood.sum(axis=0)
    if not np.allclose(state_totals, 1.0, atol=1e-9):
        raise ValueError("observation likelihoods must sum to one for every state")
    prior_entropy = shannon_entropy(prior_values)
    observation_mass = likelihood @ prior_values
    conditional_entropy = 0.0
    for row, mass in zip(likelihood, observation_mass):
        if mass <= 1e-15:
            continue
        posterior = row * prior_values / mass
        conditional_entropy += float(mass) * shannon_entropy(posterior)
    return max(0.0, prior_entropy - conditional_entropy)


class ParticleBeliefTracker:
    """Bootstrap particle filter for finite hidden tactical states."""

    def __init__(
        self,
        distribution: Mapping[State, float],
        *,
        particle_count: int = 1024,
        seed: int = 2026,
    ) -> None:
        if particle_count <= 0:
            raise ValueError("particle_count must be positive")
        self.particle_count = int(particle_count)
        self.rng = np.random.default_rng(seed)
        states = tuple(distribution)
        probabilities = _probabilities([distribution[state] for state in states])
        indices = self.rng.choice(len(states), size=self.particle_count, p=probabilities)
        self.particles: list[State] = [states[int(index)] for index in indices]

    @property
    def distribution(self) -> dict[State, float]:
        counts = Counter(self.particles)
        return {
            state: count / self.particle_count
            for state, count in sorted(counts.items(), key=lambda item: repr(item[0]))
        }

    def predict(self, transitions: Mapping[State, Mapping[State, float]]) -> None:
        predicted: list[State] = []
        for state in self.particles:
            outcomes = transitions.get(state)
            if not outcomes:
                predicted.append(state)
                continue
            states = tuple(outcomes)
            probabilities = _probabilities([outcomes[target] for target in states])
            predicted.append(states[int(self.rng.choice(len(states), p=probabilities))])
        self.particles = predicted

    def update(self, likelihood: Mapping[State, float]) -> None:
        weights = np.asarray(
            [max(0.0, float(likelihood.get(state, 0.0))) for state in self.particles],
            dtype=np.float64,
        )
        if np.any(~np.isfinite(weights)) or float(weights.sum()) <= 0.0:
            raise ValueError("particle observation has no finite positive likelihood")
        weights /= weights.sum()
        # Systematic resampling has lower variance than independent multinomial draws.
        positions = (self.rng.random() + np.arange(self.particle_count)) / self.particle_count
        cumulative = np.cumsum(weights)
        indices = np.searchsorted(cumulative, positions, side="right")
        self.particles = [self.particles[min(int(index), self.particle_count - 1)] for index in indices]


@dataclass(frozen=True)
class ChanceConstraintResult:
    violation_probability: float
    cvar: float
    feasible: bool


def evaluate_chance_constraint(
    losses: Sequence[float],
    probabilities: Sequence[float],
    *,
    loss_limit: float,
    maximum_violation: float,
    cvar_alpha: float = 0.9,
) -> ChanceConstraintResult:
    """Evaluate P(loss > limit) and upper-tail CVaR for a CMDP-style gate."""

    if len(losses) != len(probabilities) or not losses:
        raise ValueError("losses and probabilities must be non-empty and aligned")
    if not 0.0 <= maximum_violation <= 1.0:
        raise ValueError("maximum_violation must be in [0, 1]")
    weights = _probabilities(probabilities)
    values = np.asarray(losses, dtype=np.float64)
    if np.any(~np.isfinite(values)) or not isfinite(float(loss_limit)):
        raise ValueError("losses and loss_limit must be finite")
    violation = float(weights[values > float(loss_limit)].sum())
    cvar = conditional_value_at_risk(values.tolist(), cvar_alpha, weights.tolist())
    return ChanceConstraintResult(violation, cvar, violation <= maximum_violation + 1e-12)


def _conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    if scores.ndim != 1 or scores.size == 0 or np.any(~np.isfinite(scores)):
        raise ValueError("calibration scores must be a finite non-empty vector")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    rank = ceil((scores.size + 1) * (1.0 - alpha))
    if rank > scores.size:
        return float("inf")
    return float(np.sort(scores)[rank - 1])


class SplitConformalClassifier:
    """Finite-sample split-conformal sets from calibrated class probabilities."""

    def __init__(self) -> None:
        self.scores: np.ndarray | None = None

    def fit(self, probabilities: Sequence[Sequence[float]], labels: Sequence[int]) -> "SplitConformalClassifier":
        matrix = np.asarray(probabilities, dtype=np.float64)
        truth = np.asarray(labels, dtype=np.int64)
        if matrix.ndim != 2 or matrix.shape[0] != truth.size or truth.size == 0:
            raise ValueError("calibration probabilities and labels are misaligned")
        if np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0):
            raise ValueError("class probabilities must be finite and non-negative")
        if np.any(truth < 0) or np.any(truth >= matrix.shape[1]):
            raise ValueError("calibration label is outside the class range")
        row_sums = matrix.sum(axis=1)
        if np.any(row_sums <= 0.0):
            raise ValueError("every probability row needs positive mass")
        normalized = matrix / row_sums[:, None]
        self.scores = 1.0 - normalized[np.arange(truth.size), truth]
        return self

    def predict_sets(
        self, probabilities: Sequence[Sequence[float]], *, alpha: float = 0.1
    ) -> tuple[frozenset[int], ...]:
        if self.scores is None:
            raise RuntimeError("conformal classifier must be calibrated first")
        matrix = np.asarray(probabilities, dtype=np.float64)
        if matrix.ndim != 2 or np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0):
            raise ValueError("prediction probabilities must be a finite matrix")
        totals = matrix.sum(axis=1)
        if np.any(totals <= 0.0):
            raise ValueError("every probability row needs positive mass")
        normalized = matrix / totals[:, None]
        threshold = _conformal_quantile(self.scores, alpha)
        return tuple(
            frozenset(np.flatnonzero(1.0 - row <= threshold + 1e-12).tolist())
            for row in normalized
        )


class SplitConformalRegressor:
    """Symmetric split-conformal intervals around arbitrary point predictions."""

    def __init__(self) -> None:
        self.residuals: np.ndarray | None = None

    def fit(self, predictions: Sequence[float], targets: Sequence[float]) -> "SplitConformalRegressor":
        predicted = np.asarray(predictions, dtype=np.float64)
        observed = np.asarray(targets, dtype=np.float64)
        if predicted.ndim != 1 or predicted.shape != observed.shape or predicted.size == 0:
            raise ValueError("calibration predictions and targets are misaligned")
        if np.any(~np.isfinite(predicted)) or np.any(~np.isfinite(observed)):
            raise ValueError("regression calibration data must be finite")
        self.residuals = np.abs(observed - predicted)
        return self

    def intervals(
        self, predictions: Sequence[float], *, alpha: float = 0.1
    ) -> tuple[tuple[float, float], ...]:
        if self.residuals is None:
            raise RuntimeError("conformal regressor must be calibrated first")
        predicted = np.asarray(predictions, dtype=np.float64)
        if predicted.ndim != 1 or np.any(~np.isfinite(predicted)):
            raise ValueError("predictions must be a finite vector")
        radius = _conformal_quantile(self.residuals, alpha)
        return tuple((float(value - radius), float(value + radius)) for value in predicted)
