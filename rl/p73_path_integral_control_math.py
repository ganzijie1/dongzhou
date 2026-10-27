"""P73 linearly solvable, path-integral, MPPI, and inference control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.special import logsumexp


@dataclass(frozen=True)
class ExponentialWeights:
    weights: np.ndarray
    effective_sample_size: float
    log_normalizer: float


def exponential_cost_weights(costs: Sequence[float], temperature: float) -> ExponentialWeights:
    values = np.asarray(costs, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or temperature <= 0.0:
        raise ValueError("path-integral weights are invalid")
    logits = -values / temperature
    log_normalizer = float(logsumexp(logits))
    weights = np.exp(logits - log_normalizer)
    return ExponentialWeights(weights, float(1.0 / (weights @ weights)), log_normalizer)


def entropic_risk(costs: Sequence[float], risk_parameter: float) -> float:
    values = np.asarray(costs, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or not np.isfinite(risk_parameter):
        raise ValueError("entropic risk inputs are invalid")
    if abs(risk_parameter) < 1e-10:
        return float(values.mean())
    scaled = risk_parameter * values
    return float((logsumexp(scaled) - np.log(values.size)) / risk_parameter)


def desirability(values: Sequence[float], temperature: float) -> np.ndarray:
    costs = np.asarray(values, dtype=np.float64)
    if np.any(~np.isfinite(costs)) or temperature <= 0.0:
        raise ValueError("desirability inputs are invalid")
    return np.exp(-costs / temperature)


def kl_control_policy(passive_transition: Sequence, successor_values: Sequence[float], temperature: float) -> np.ndarray:
    passive = np.asarray(passive_transition, dtype=np.float64)
    values = np.asarray(successor_values, dtype=np.float64)
    if passive.ndim != 1 or values.shape != passive.shape or np.any(passive < 0.0) or not np.isclose(passive.sum(), 1.0) or temperature <= 0.0:
        raise ValueError("KL control inputs are invalid")
    unnormalized = passive * desirability(values, temperature)
    if unnormalized.sum() <= 0.0:
        raise ValueError("KL control has zero supported mass")
    return unnormalized / unnormalized.sum()


def control_as_inference_posterior(prior: Sequence[float], costs: Sequence[float], temperature: float) -> np.ndarray:
    probability = np.asarray(prior, dtype=np.float64)
    values = np.asarray(costs, dtype=np.float64)
    if probability.ndim != 1 or values.shape != probability.shape or np.any(probability < 0.0) or not np.isclose(probability.sum(), 1.0):
        raise ValueError("control-as-inference inputs are invalid")
    logits = np.full_like(probability, -np.inf)
    supported = probability > 0.0
    logits[supported] = np.log(probability[supported]) - values[supported] / temperature
    normalizer = logsumexp(logits)
    if not np.isfinite(normalizer):
        raise ValueError("posterior has zero mass")
    return np.exp(logits - normalizer)


def mppi_control_update(nominal_controls: Sequence, perturbations: Sequence, costs: Sequence[float], temperature: float) -> tuple[np.ndarray, ExponentialWeights]:
    controls = np.asarray(nominal_controls, dtype=np.float64)
    noise = np.asarray(perturbations, dtype=np.float64)
    values = np.asarray(costs, dtype=np.float64)
    if controls.ndim != 2 or noise.ndim != 3 or noise.shape[1:] != controls.shape or values.shape != (noise.shape[0],):
        raise ValueError("MPPI inputs are invalid")
    weighting = exponential_cost_weights(values, temperature)
    update = np.tensordot(weighting.weights, noise, axes=(0, 0))
    return controls + update, weighting


def shift_control_horizon(controls: Sequence, terminal_control: Sequence[float] | None = None) -> np.ndarray:
    values = np.asarray(controls, dtype=np.float64)
    if values.ndim != 2 or values.shape[0] == 0:
        raise ValueError("control horizon is invalid")
    terminal = values[-1] if terminal_control is None else np.asarray(terminal_control, dtype=np.float64)
    if terminal.shape != (values.shape[1],):
        raise ValueError("terminal control is invalid")
    return np.vstack((values[1:], terminal)) if values.shape[0] > 1 else terminal[None, :]
