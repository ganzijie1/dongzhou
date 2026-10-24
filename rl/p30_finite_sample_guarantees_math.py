"""P30 PAC, confidence-sequence, and conformal risk guarantees."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, sqrt
from typing import Sequence

import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class PACMDPDiagnostics:
    bad_steps: int
    total_steps: int
    bad_fraction: float
    maximum_gap: float
    satisfies_claimed_bound: bool | None


def pac_mdp_diagnostics(
    achieved_values: Sequence[float],
    optimal_values: Sequence[float],
    *,
    epsilon: float,
    claimed_bad_step_bound: int | None = None,
) -> PACMDPDiagnostics:
    """Audit the observable consequence of a claimed PAC-MDP guarantee.

    This deliberately does not invent a sample-complexity theorem: callers may
    pass the bound proved for their specific algorithm and assumptions.
    """

    achieved = np.asarray(achieved_values, dtype=np.float64)
    optimal = np.asarray(optimal_values, dtype=np.float64)
    if (
        achieved.ndim != 1
        or achieved.size == 0
        or optimal.shape != achieved.shape
        or np.any(~np.isfinite(achieved))
        or np.any(~np.isfinite(optimal))
        or not isfinite(epsilon)
        or epsilon < 0.0
        or claimed_bad_step_bound is not None
        and claimed_bad_step_bound < 0
    ):
        raise ValueError("PAC-MDP diagnostic inputs are invalid")
    gaps = np.maximum(optimal - achieved, 0.0)
    bad_steps = int(np.sum(gaps > epsilon))
    satisfies = (
        None
        if claimed_bad_step_bound is None
        else bad_steps <= claimed_bad_step_bound
    )
    return PACMDPDiagnostics(
        bad_steps,
        achieved.size,
        bad_steps / achieved.size,
        float(np.max(gaps)),
        satisfies,
    )


def binary_kl(first: float, second: float) -> float:
    """Bernoulli KL divergence with continuous boundary conventions."""

    if not 0.0 <= first <= 1.0 or not 0.0 <= second <= 1.0:
        raise ValueError("Bernoulli probabilities must lie in [0, 1]")
    if second == 0.0:
        return 0.0 if first == 0.0 else float("inf")
    if second == 1.0:
        return 0.0 if first == 1.0 else float("inf")
    result = 0.0
    if first > 0.0:
        result += first * log(first / second)
    if first < 1.0:
        result += (1.0 - first) * log((1.0 - first) / (1.0 - second))
    return result


def pac_bayes_kl_upper(
    empirical_risk: float,
    kl_to_prior: float,
    sample_size: int,
    delta: float,
) -> float:
    """Invert the PAC-Bayes-kl inequality for a bounded loss."""

    if (
        not 0.0 <= empirical_risk <= 1.0
        or not isfinite(kl_to_prior)
        or kl_to_prior < 0.0
        or sample_size < 1
        or not 0.0 < delta < 1.0
    ):
        raise ValueError("PAC-Bayes inputs are invalid")
    complexity = (
        kl_to_prior + log(2.0 * sqrt(sample_size) / delta)
    ) / sample_size
    if empirical_risk == 1.0 or binary_kl(empirical_risk, 1.0 - 1e-15) <= complexity:
        return 1.0
    return float(
        brentq(
            lambda candidate: binary_kl(empirical_risk, candidate) - complexity,
            empirical_risk,
            1.0 - 1e-15,
        )
    )


@dataclass(frozen=True)
class PACBayesStrategyBound:
    empirical_risk: float
    kl_to_prior: float
    upper_risk: float


def pac_bayes_strategy_bound(
    policy_empirical_risks: Sequence[float],
    posterior: Sequence[float],
    prior: Sequence[float],
    *,
    sample_size: int,
    delta: float,
) -> PACBayesStrategyBound:
    """Bound the Gibbs strategy risk for finite policy classes."""

    risks = np.asarray(policy_empirical_risks, dtype=np.float64)
    post = np.asarray(posterior, dtype=np.float64)
    base = np.asarray(prior, dtype=np.float64)
    if (
        risks.ndim != 1
        or risks.size == 0
        or post.shape != risks.shape
        or base.shape != risks.shape
        or np.any((risks < 0.0) | (risks > 1.0))
        or np.any(post < 0.0)
        or np.any(base < 0.0)
        or not np.isclose(post.sum(), 1.0)
        or not np.isclose(base.sum(), 1.0)
        or np.any((post > 0.0) & (base == 0.0))
    ):
        raise ValueError("PAC-Bayes strategy distributions are invalid")
    positive = post > 0.0
    divergence = float(np.sum(post[positive] * np.log(post[positive] / base[positive])))
    empirical = float(post @ risks)
    return PACBayesStrategyBound(
        empirical,
        divergence,
        pac_bayes_kl_upper(empirical, divergence, sample_size, delta),
    )


def empirical_bernstein_upper(
    observations: Sequence[float],
    *,
    delta: float,
    lower: float = 0.0,
    upper: float = 1.0,
) -> float:
    """One-sided empirical Bernstein bound for bounded IID observations."""

    sample = np.asarray(observations, dtype=np.float64)
    if (
        sample.ndim != 1
        or sample.size < 2
        or np.any(~np.isfinite(sample))
        or not isfinite(lower)
        or not isfinite(upper)
        or lower >= upper
        or np.any(sample < lower)
        or np.any(sample > upper)
        or not 0.0 < delta < 1.0
    ):
        raise ValueError("empirical Bernstein inputs are invalid")
    radius_log = log(3.0 / delta)
    variance = float(np.var(sample, ddof=1))
    radius = sqrt(2.0 * variance * radius_log / sample.size)
    radius += 3.0 * (upper - lower) * radius_log / sample.size
    return float(min(upper, np.mean(sample) + radius))


@dataclass(frozen=True)
class AnytimeConfidenceSequence:
    means: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    radii: np.ndarray


def anytime_hoeffding_confidence_sequence(
    observations: Sequence[float],
    *,
    delta: float,
    lower: float = 0.0,
    upper: float = 1.0,
) -> AnytimeConfidenceSequence:
    """Anytime-valid sequence via a summable per-time error allocation."""

    sample = np.asarray(observations, dtype=np.float64)
    if (
        sample.ndim != 1
        or sample.size == 0
        or np.any(~np.isfinite(sample))
        or lower >= upper
        or np.any(sample < lower)
        or np.any(sample > upper)
        or not 0.0 < delta < 1.0
    ):
        raise ValueError("confidence-sequence inputs are invalid")
    times = np.arange(1, sample.size + 1, dtype=np.float64)
    means = np.cumsum(sample) / times
    allocated = delta / (times * (times + 1.0))
    radii = (upper - lower) * np.sqrt(np.log(2.0 / allocated) / (2.0 * times))
    return AnytimeConfidenceSequence(
        means,
        np.maximum(lower, means - radii),
        np.minimum(upper, means + radii),
        radii,
    )


@dataclass(frozen=True)
class ConformalRiskControlResult:
    selected_index: int | None
    selected_lambda: float | None
    upper_risks: np.ndarray
    feasible_indices: np.ndarray


def conformal_risk_control(
    calibration_losses: Sequence,
    lambdas: Sequence[float],
    *,
    risk_level: float,
    loss_upper_bound: float = 1.0,
) -> ConformalRiskControlResult:
    """Finite-sample CRC selector, choosing the largest feasible lambda."""

    losses = np.asarray(calibration_losses, dtype=np.float64)
    controls = np.asarray(lambdas, dtype=np.float64)
    if (
        losses.ndim != 2
        or losses.shape[0] == 0
        or losses.shape[1] != controls.size
        or controls.ndim != 1
        or np.any(~np.isfinite(losses))
        or np.any(~np.isfinite(controls))
        or np.any(losses < 0.0)
        or np.any(losses > loss_upper_bound)
        or not 0.0 <= risk_level <= loss_upper_bound
        or not isfinite(loss_upper_bound)
        or loss_upper_bound <= 0.0
    ):
        raise ValueError("conformal risk-control inputs are invalid")
    upper_risks = (losses.sum(axis=0) + loss_upper_bound) / (losses.shape[0] + 1.0)
    feasible = np.flatnonzero(upper_risks <= risk_level)
    selected = int(feasible[np.argmax(controls[feasible])]) if feasible.size else None
    return ConformalRiskControlResult(
        selected,
        None if selected is None else float(controls[selected]),
        upper_risks,
        feasible,
    )


def weighted_conformal_quantile(
    calibration_scores: Sequence[float],
    calibration_weights: Sequence[float],
    *,
    test_weight: float,
    alpha: float,
) -> float:
    """Weighted split-conformal quantile including test mass at infinity."""

    scores = np.asarray(calibration_scores, dtype=np.float64)
    weights = np.asarray(calibration_weights, dtype=np.float64)
    if (
        scores.ndim != 1
        or scores.size == 0
        or weights.shape != scores.shape
        or np.any(~np.isfinite(scores))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not isfinite(test_weight)
        or test_weight < 0.0
        or weights.sum() + test_weight <= 0.0
        or not 0.0 < alpha < 1.0
    ):
        raise ValueError("weighted conformal inputs are invalid")
    order = np.argsort(scores, kind="stable")
    sorted_scores = scores[order]
    cumulative = np.cumsum(weights[order])
    target = (1.0 - alpha) * (weights.sum() + test_weight)
    index = int(np.searchsorted(cumulative, target, side="left"))
    return float(sorted_scores[index]) if index < scores.size else float("inf")


def density_ratio_weights(
    target_density: Sequence[float],
    calibration_density: Sequence[float],
    *,
    maximum_weight: float | None = None,
) -> np.ndarray:
    """Construct covariate-shift weights from supplied density evaluations."""

    target = np.asarray(target_density, dtype=np.float64)
    source = np.asarray(calibration_density, dtype=np.float64)
    if (
        target.ndim != 1
        or source.shape != target.shape
        or target.size == 0
        or np.any(~np.isfinite(target))
        or np.any(~np.isfinite(source))
        or np.any(target < 0.0)
        or np.any(source <= 0.0)
        or maximum_weight is not None
        and (not isfinite(maximum_weight) or maximum_weight <= 0.0)
    ):
        raise ValueError("density-ratio inputs are invalid")
    result = target / source
    if maximum_weight is not None:
        result = np.minimum(result, maximum_weight)
    return result


def effective_sample_size(weights: Sequence[float]) -> float:
    """Kish effective sample size of nonnegative importance weights."""

    values = np.asarray(weights, dtype=np.float64)
    if (
        values.ndim != 1
        or values.size == 0
        or np.any(~np.isfinite(values))
        or np.any(values < 0.0)
        or values.sum() <= 0.0
    ):
        raise ValueError("importance weights are invalid")
    return float(values.sum() ** 2 / np.sum(values**2))
