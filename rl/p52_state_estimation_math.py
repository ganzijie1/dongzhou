"""P52 EKF, unscented, particle, IMM, and H-infinity estimation primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class GaussianEstimate:
    mean: np.ndarray
    covariance: np.ndarray
    innovation: np.ndarray | None = None
    innovation_covariance: np.ndarray | None = None


def _covariance(value: Sequence, dimension: int, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.float64)
    if matrix.shape != (dimension, dimension) or np.any(~np.isfinite(matrix)) or not np.allclose(matrix, matrix.T) or np.min(np.linalg.eigvalsh(matrix)) < -1e-10:
        raise ValueError(f"{name} is not a valid covariance")
    return matrix


def ekf_predict(
    mean: Sequence[float],
    covariance: Sequence,
    transition: Callable[[np.ndarray], Sequence[float]],
    transition_jacobian: Callable[[np.ndarray], Sequence],
    process_covariance: Sequence,
) -> GaussianEstimate:
    state = np.asarray(mean, dtype=np.float64)
    if state.ndim != 1 or state.size == 0 or np.any(~np.isfinite(state)):
        raise ValueError("mean is invalid")
    cov = _covariance(covariance, state.size, "covariance")
    process = _covariance(process_covariance, state.size, "process covariance")
    jacobian = np.asarray(transition_jacobian(state), dtype=np.float64)
    predicted = np.asarray(transition(state), dtype=np.float64)
    if jacobian.shape != cov.shape or predicted.shape != state.shape or np.any(~np.isfinite(jacobian)) or np.any(~np.isfinite(predicted)):
        raise ValueError("transition output is invalid")
    predicted_cov = jacobian @ cov @ jacobian.T + process
    return GaussianEstimate(predicted, (predicted_cov + predicted_cov.T) / 2.0)


def ekf_update(
    mean: Sequence[float],
    covariance: Sequence,
    measurement: Sequence[float],
    observation: Callable[[np.ndarray], Sequence[float]],
    observation_jacobian: Callable[[np.ndarray], Sequence],
    measurement_covariance: Sequence,
) -> GaussianEstimate:
    state = np.asarray(mean, dtype=np.float64)
    cov = _covariance(covariance, state.size, "covariance")
    observed = np.asarray(measurement, dtype=np.float64)
    predicted_observation = np.asarray(observation(state), dtype=np.float64)
    jacobian = np.asarray(observation_jacobian(state), dtype=np.float64)
    if observed.ndim != 1 or predicted_observation.shape != observed.shape or jacobian.shape != (observed.size, state.size) or np.any(~np.isfinite(observed)) or np.any(~np.isfinite(predicted_observation)) or np.any(~np.isfinite(jacobian)):
        raise ValueError("observation inputs are invalid")
    noise = _covariance(measurement_covariance, observed.size, "measurement covariance")
    innovation = observed - predicted_observation
    innovation_cov = jacobian @ cov @ jacobian.T + noise
    gain = np.linalg.solve(innovation_cov, jacobian @ cov).T
    updated = state + gain @ innovation
    identity = np.eye(state.size)
    residual = identity - gain @ jacobian
    updated_cov = residual @ cov @ residual.T + gain @ noise @ gain.T
    return GaussianEstimate(updated, (updated_cov + updated_cov.T) / 2.0, innovation, innovation_cov)


def scaled_sigma_points(
    mean: Sequence[float],
    covariance: Sequence,
    *,
    alpha: float = 1e-3,
    beta: float = 2.0,
    kappa: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    state = np.asarray(mean, dtype=np.float64)
    cov = _covariance(covariance, state.size, "covariance")
    if not 0.0 < alpha or not np.isfinite(beta) or not np.isfinite(kappa):
        raise ValueError("sigma-point parameters are invalid")
    dimension = state.size
    lam = alpha**2 * (dimension + kappa) - dimension
    scale = dimension + lam
    if scale <= 0.0:
        raise ValueError("sigma-point scale must be positive")
    root = np.linalg.cholesky(scale * (cov + 1e-14 * np.eye(dimension)))
    points = np.vstack([state, state + root.T, state - root.T])
    mean_weights = np.full(2 * dimension + 1, 1.0 / (2.0 * scale))
    covariance_weights = mean_weights.copy()
    mean_weights[0] = lam / scale
    covariance_weights[0] = lam / scale + (1.0 - alpha**2 + beta)
    return points, mean_weights, covariance_weights


def unscented_transform(
    points: Sequence,
    mean_weights: Sequence[float],
    covariance_weights: Sequence[float],
    noise_covariance: Sequence | None = None,
) -> GaussianEstimate:
    samples = np.asarray(points, dtype=np.float64)
    wm = np.asarray(mean_weights, dtype=np.float64)
    wc = np.asarray(covariance_weights, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[0] == 0 or wm.shape != (samples.shape[0],) or wc.shape != wm.shape or np.any(~np.isfinite(samples)) or np.any(~np.isfinite(wm)) or np.any(~np.isfinite(wc)) or not np.isclose(wm.sum(), 1.0):
        raise ValueError("unscented-transform inputs are invalid")
    mean = wm @ samples
    centered = samples - mean
    covariance = (centered.T * wc) @ centered
    if noise_covariance is not None:
        covariance += _covariance(noise_covariance, samples.shape[1], "noise covariance")
    return GaussianEstimate(mean, (covariance + covariance.T) / 2.0)


def systematic_resample(weights: Sequence[float], rng: np.random.Generator) -> np.ndarray:
    probability = np.asarray(weights, dtype=np.float64)
    if probability.ndim != 1 or probability.size == 0 or np.any(~np.isfinite(probability)) or np.any(probability < 0.0) or not np.isclose(probability.sum(), 1.0):
        raise ValueError("particle weights are invalid")
    positions = (rng.random() + np.arange(probability.size)) / probability.size
    return np.searchsorted(np.cumsum(probability), positions, side="right")


@dataclass(frozen=True)
class ParticleUpdate:
    particles: np.ndarray
    weights: np.ndarray
    effective_sample_size: float
    resampled: bool


def particle_filter_update(
    particles: Sequence,
    prior_weights: Sequence[float],
    likelihoods: Sequence[float],
    *,
    rng: np.random.Generator,
    resample_fraction: float = 0.5,
) -> ParticleUpdate:
    samples = np.asarray(particles, dtype=np.float64)
    weights = np.asarray(prior_weights, dtype=np.float64)
    likelihood = np.asarray(likelihoods, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[0] == 0 or weights.shape != (samples.shape[0],) or likelihood.shape != weights.shape or np.any(~np.isfinite(samples)) or np.any(~np.isfinite(weights)) or np.any(weights < 0.0) or not np.isclose(weights.sum(), 1.0) or np.any(~np.isfinite(likelihood)) or np.any(likelihood < 0.0) or not 0.0 < resample_fraction <= 1.0:
        raise ValueError("particle-filter inputs are invalid")
    posterior = weights * likelihood
    total = posterior.sum()
    if total <= 0.0:
        raise ValueError("all particles have zero likelihood")
    posterior /= total
    ess = float(1.0 / (posterior @ posterior))
    if ess < resample_fraction * samples.shape[0]:
        indices = systematic_resample(posterior, rng)
        return ParticleUpdate(samples[indices], np.full(samples.shape[0], 1.0 / samples.shape[0]), ess, True)
    return ParticleUpdate(samples.copy(), posterior, ess, False)


def imm_mixing_probabilities(
    mode_probabilities: Sequence[float], transition_matrix: Sequence
) -> tuple[np.ndarray, np.ndarray]:
    mode = np.asarray(mode_probabilities, dtype=np.float64)
    transition = np.asarray(transition_matrix, dtype=np.float64)
    if mode.ndim != 1 or mode.size == 0 or transition.shape != (mode.size, mode.size) or np.any(mode < 0.0) or np.any(~np.isfinite(mode)) or not np.isclose(mode.sum(), 1.0) or np.any(transition < 0.0) or np.any(~np.isfinite(transition)) or not np.allclose(transition.sum(axis=1), 1.0):
        raise ValueError("IMM inputs are invalid")
    predicted = mode @ transition
    if np.any(predicted <= 0.0):
        raise ValueError("every destination mode needs positive predicted probability")
    mixing = mode[:, None] * transition / predicted[None, :]
    return predicted, mixing


def hinfinity_information_covariance(
    prior_covariance: Sequence,
    observation_matrix: Sequence,
    measurement_covariance: Sequence,
    *,
    gamma: float,
) -> np.ndarray:
    prior = np.asarray(prior_covariance, dtype=np.float64)
    if prior.ndim != 2 or prior.shape[0] != prior.shape[1]:
        raise ValueError("prior covariance is invalid")
    prior = _covariance(prior, prior.shape[0], "prior covariance")
    observation = np.asarray(observation_matrix, dtype=np.float64)
    if observation.ndim != 2 or observation.shape[1] != prior.shape[0] or np.any(~np.isfinite(observation)) or not np.isfinite(gamma) or gamma <= 0.0:
        raise ValueError("H-infinity inputs are invalid")
    measurement = _covariance(measurement_covariance, observation.shape[0], "measurement covariance")
    information = np.linalg.inv(prior) + observation.T @ np.linalg.solve(measurement, observation) - np.eye(prior.shape[0]) / gamma**2
    if np.min(np.linalg.eigvalsh((information + information.T) / 2.0)) <= 0.0:
        raise ValueError("gamma is too small for a positive-definite information update")
    covariance = np.linalg.inv(information)
    return (covariance + covariance.T) / 2.0
