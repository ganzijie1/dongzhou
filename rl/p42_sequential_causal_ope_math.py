"""P42 sequential causal g-computation, OPE, proximal scores, and sensitivity."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np


def effective_sample_size(weights: Sequence[float]) -> float:
    values = np.asarray(weights, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("weights are invalid")
    square_sum = float(values @ values)
    return 0.0 if square_sum == 0.0 else float(values.sum() ** 2 / square_sum)


def sequential_g_computation(
    transitions: Sequence,
    rewards: Sequence,
    target_policy: Sequence,
    initial_distribution: Sequence[float],
    *,
    discount: float = 1.0,
) -> float:
    """Finite-horizon tabular g-formula for state-action interventions."""

    kernel = np.asarray(transitions, dtype=np.float64)
    reward = np.asarray(rewards, dtype=np.float64)
    policy = np.asarray(target_policy, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    if (
        kernel.ndim != 4
        or kernel.shape[0:3] != reward.shape
        or policy.shape != reward.shape
        or kernel.shape[1] != kernel.shape[3]
        or initial.shape != (kernel.shape[1],)
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=3), 1.0)
        or np.any(~np.isfinite(reward))
        or np.any(policy < 0.0)
        or not np.allclose(policy.sum(axis=2), 1.0)
        or np.any(initial < 0.0)
        or not np.isclose(initial.sum(), 1.0)
        or not isfinite(discount)
        or not 0.0 <= discount <= 1.0
    ):
        raise ValueError("g-computation inputs are invalid")
    value = np.zeros(kernel.shape[1])
    for time in range(kernel.shape[0] - 1, -1, -1):
        q_value = reward[time] + discount * np.einsum("asn,n->as", kernel[time], value)
        value = np.sum(policy[time] * q_value, axis=1)
    return float(initial @ value)


def _trajectory_arrays(
    rewards: Sequence, target_probabilities: Sequence, behavior_probabilities: Sequence
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    reward = np.asarray(rewards, dtype=np.float64)
    target = np.asarray(target_probabilities, dtype=np.float64)
    behavior = np.asarray(behavior_probabilities, dtype=np.float64)
    if (
        reward.ndim != 2
        or target.shape != reward.shape
        or behavior.shape != reward.shape
        or np.any(~np.isfinite(reward))
        or np.any(~np.isfinite(target))
        or np.any(~np.isfinite(behavior))
        or np.any(target < 0.0)
        or np.any(behavior <= 0.0)
    ):
        raise ValueError("trajectory probabilities are invalid")
    return reward, target, behavior


@dataclass(frozen=True)
class OPEResult:
    estimate: float
    trajectory_returns: np.ndarray
    final_weights: np.ndarray
    effective_sample_size: float


def per_decision_importance_sampling(
    rewards: Sequence,
    target_probabilities: Sequence,
    behavior_probabilities: Sequence,
    *,
    discount: float = 1.0,
) -> OPEResult:
    reward, target, behavior = _trajectory_arrays(rewards, target_probabilities, behavior_probabilities)
    if not isfinite(discount) or not 0.0 <= discount <= 1.0:
        raise ValueError("discount is invalid")
    ratios = np.cumprod(target / behavior, axis=1)
    powers = discount ** np.arange(reward.shape[1])
    returns = np.sum(ratios * reward * powers, axis=1)
    final = ratios[:, -1]
    return OPEResult(float(np.mean(returns)), returns, final, effective_sample_size(final))


def sequential_doubly_robust(
    rewards: Sequence,
    q_values: Sequence,
    v_values: Sequence,
    target_probabilities: Sequence,
    behavior_probabilities: Sequence,
    *,
    discount: float = 1.0,
) -> OPEResult:
    reward, target, behavior = _trajectory_arrays(rewards, target_probabilities, behavior_probabilities)
    q_value = np.asarray(q_values, dtype=np.float64)
    v_value = np.asarray(v_values, dtype=np.float64)
    if q_value.shape != reward.shape or v_value.shape != (reward.shape[0], reward.shape[1] + 1):
        raise ValueError("Q/V arrays have invalid shape")
    if np.any(~np.isfinite(q_value)) or np.any(~np.isfinite(v_value)):
        raise ValueError("Q/V arrays must be finite")
    ratios = np.cumprod(target / behavior, axis=1)
    powers = discount ** np.arange(reward.shape[1])
    correction = reward + discount * v_value[:, 1:] - q_value
    returns = v_value[:, 0] + np.sum(powers * ratios * correction, axis=1)
    final = ratios[:, -1]
    return OPEResult(float(np.mean(returns)), returns, final, effective_sample_size(final))


def proximal_bridge_score(
    outcome_bridge: Sequence[float],
    treatment_bridge: Sequence[float],
    outcomes: Sequence[float],
    target_probabilities: Sequence[float],
) -> float:
    """Sample analogue of h(W,a,X)+q(Z,a,X)(Y-h(W,A,X))pi(a|X)."""

    h_value = np.asarray(outcome_bridge, dtype=np.float64)
    q_value = np.asarray(treatment_bridge, dtype=np.float64)
    outcome = np.asarray(outcomes, dtype=np.float64)
    target = np.asarray(target_probabilities, dtype=np.float64)
    if not (h_value.shape == q_value.shape == outcome.shape == target.shape) or h_value.ndim != 1:
        raise ValueError("proximal score arrays have incompatible shapes")
    if np.any(~np.isfinite(h_value)) or np.any(~np.isfinite(q_value)) or np.any(~np.isfinite(outcome)):
        raise ValueError("proximal score inputs must be finite")
    return float(np.mean(h_value + q_value * target * (outcome - h_value)))


def marginal_sensitivity_probability_bounds(probability: float, *, gamma: float) -> tuple[float, float]:
    """Rosenbaum odds-ratio bounds for an unobserved-confounding factor Gamma."""

    if not isfinite(probability) or not 0.0 < probability < 1.0 or not isfinite(gamma) or gamma < 1.0:
        raise ValueError("sensitivity inputs are invalid")
    odds = probability / (1.0 - probability)
    lower_odds, upper_odds = odds / gamma, odds * gamma
    return lower_odds / (1.0 + lower_odds), upper_odds / (1.0 + upper_odds)
