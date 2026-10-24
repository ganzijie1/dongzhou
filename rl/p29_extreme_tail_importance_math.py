"""P29 extreme-value tails, tail dependence, and CE importance sampling."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Callable, Literal, Sequence

import numpy as np
from scipy.stats import genextreme, genpareto, multivariate_normal, rankdata, t


@dataclass(frozen=True)
class GEVFit:
    location: float
    scale: float
    shape: float
    log_likelihood: float


def fit_gev(block_maxima: Sequence[float]) -> GEVFit:
    """Maximum-likelihood GEV fit using the conventional shape ``xi``."""

    sample = np.asarray(block_maxima, dtype=np.float64)
    if sample.ndim != 1 or sample.size < 3 or np.any(~np.isfinite(sample)):
        raise ValueError("GEV fitting needs at least three finite block maxima")
    scipy_shape, location, scale = genextreme.fit(sample)
    if not isfinite(scale) or scale <= 0.0:
        raise ValueError("GEV fit produced an invalid scale")
    likelihood = float(
        np.sum(genextreme.logpdf(sample, scipy_shape, loc=location, scale=scale))
    )
    return GEVFit(float(location), float(scale), float(-scipy_shape), likelihood)


def gev_cdf(
    value: Sequence[float] | float,
    *,
    location: float,
    scale: float,
    shape: float,
) -> np.ndarray:
    """GEV CDF with shape ``xi`` (SciPy uses the opposite sign)."""

    if scale <= 0.0 or not all(isfinite(x) for x in (location, scale, shape)):
        raise ValueError("GEV parameters are invalid")
    return np.asarray(
        genextreme.cdf(value, -shape, loc=location, scale=scale),
        dtype=np.float64,
    )


def gev_return_level(
    non_exceedance_probability: float,
    *,
    location: float,
    scale: float,
    shape: float,
) -> float:
    """Quantile exceeded with probability ``1 - p`` per block."""

    if not 0.0 < non_exceedance_probability < 1.0:
        raise ValueError("GEV probability must lie strictly between zero and one")
    result = genextreme.ppf(
        non_exceedance_probability, -shape, loc=location, scale=scale
    )
    if not isfinite(result):
        raise ValueError("requested GEV return level lies outside the support")
    return float(result)


@dataclass(frozen=True)
class GPDFit:
    scale: float
    shape: float
    log_likelihood: float


def fit_gpd(exceedances: Sequence[float]) -> GPDFit:
    """Fit a threshold excess distribution with location fixed at zero."""

    sample = np.asarray(exceedances, dtype=np.float64)
    if (
        sample.ndim != 1
        or sample.size < 3
        or np.any(~np.isfinite(sample))
        or np.any(sample < 0.0)
    ):
        raise ValueError("GPD fitting needs nonnegative finite exceedances")
    shape, _, scale = genpareto.fit(sample, floc=0.0)
    likelihood = float(np.sum(genpareto.logpdf(sample, shape, loc=0.0, scale=scale)))
    return GPDFit(float(scale), float(shape), likelihood)


def gpd_conditional_survival(
    excess: Sequence[float] | float,
    *,
    scale: float,
    shape: float,
) -> np.ndarray:
    """Conditional probability that an excess exceeds ``y``."""

    if scale <= 0.0 or not isfinite(scale) or not isfinite(shape):
        raise ValueError("GPD parameters are invalid")
    return np.asarray(genpareto.sf(excess, shape, loc=0.0, scale=scale))


def pot_tail_probability(
    value: Sequence[float] | float,
    *,
    threshold: float,
    threshold_exceedance_probability: float,
    scale: float,
    shape: float,
) -> np.ndarray:
    """POT tail estimate above the fitted threshold."""

    query = np.asarray(value, dtype=np.float64)
    if (
        np.any(query < threshold)
        or not 0.0 <= threshold_exceedance_probability <= 1.0
    ):
        raise ValueError("POT queries must be above a valid threshold")
    return threshold_exceedance_probability * gpd_conditional_survival(
        query - threshold, scale=scale, shape=shape
    )


def empirical_tail_dependence(
    first: Sequence[float],
    second: Sequence[float],
    *,
    quantile: float = 0.95,
    tail: Literal["upper", "lower"] = "upper",
) -> float:
    """Rank-based finite-threshold tail-dependence estimate."""

    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    if (
        left.ndim != 1
        or right.shape != left.shape
        or left.size < 2
        or np.any(~np.isfinite(left))
        or np.any(~np.isfinite(right))
        or not 0.5 < quantile < 1.0
        or tail not in ("upper", "lower")
    ):
        raise ValueError("tail-dependence inputs are invalid")
    u = rankdata(left, method="average") / (left.size + 1.0)
    v = rankdata(right, method="average") / (right.size + 1.0)
    if tail == "upper":
        joint = np.mean((u > quantile) & (v > quantile))
    else:
        cutoff = 1.0 - quantile
        joint = np.mean((u < cutoff) & (v < cutoff))
    return float(joint / (1.0 - quantile))


def student_t_tail_dependence(correlation: float, degrees_of_freedom: float) -> float:
    """Common upper/lower tail coefficient of a Student-t copula."""

    if (
        not -1.0 < correlation < 1.0
        or not isfinite(degrees_of_freedom)
        or degrees_of_freedom <= 0.0
    ):
        raise ValueError("Student-t copula parameters are invalid")
    argument = -sqrt(
        (degrees_of_freedom + 1.0)
        * (1.0 - correlation)
        / (1.0 + correlation)
    )
    return float(2.0 * t.cdf(argument, degrees_of_freedom + 1.0))


def archimedean_tail_dependence(
    family: Literal["clayton", "gumbel"], shape: float
) -> tuple[float, float]:
    """Return ``(lower, upper)`` asymptotic tail coefficients."""

    if family == "clayton" and shape > 0.0:
        return float(2.0 ** (-1.0 / shape)), 0.0
    if family == "gumbel" and shape >= 1.0:
        return 0.0, float(2.0 - 2.0 ** (1.0 / shape))
    raise ValueError("copula family or shape is invalid")


@dataclass(frozen=True)
class CrossEntropyISResult:
    probability: float
    standard_error: float
    effective_sample_size: float
    proposal_mean: np.ndarray
    proposal_covariance: np.ndarray
    elite_thresholds: tuple[float, ...]
    event_count: int


def _score_values(score: Callable[[np.ndarray], Sequence[float]], sample: np.ndarray):
    values = np.asarray(score(sample), dtype=np.float64)
    if values.shape != (sample.shape[0],) or np.any(~np.isfinite(values)):
        raise ValueError("score must return one finite value per sample")
    return values


def cross_entropy_gaussian_importance_sampling(
    mean: Sequence[float],
    covariance: Sequence,
    score: Callable[[np.ndarray], Sequence[float]],
    threshold: float,
    *,
    adaptation_samples: int = 4_000,
    evaluation_samples: int = 20_000,
    elite_fraction: float = 0.1,
    iterations: int = 5,
    smoothing: float = 0.7,
    defensive_fraction: float = 0.1,
    covariance_floor: float = 1e-6,
    seed: int | None = None,
) -> CrossEntropyISResult:
    """Adaptive Gaussian CE proposal with defensive-mixture evaluation."""

    base_mean = np.asarray(mean, dtype=np.float64)
    base_covariance = np.asarray(covariance, dtype=np.float64)
    dimension = base_mean.size
    if (
        base_mean.ndim != 1
        or dimension == 0
        or base_covariance.shape != (dimension, dimension)
        or np.any(~np.isfinite(base_mean))
        or np.any(~np.isfinite(base_covariance))
        or np.min(np.linalg.eigvalsh(base_covariance)) <= 0.0
        or not isfinite(threshold)
        or adaptation_samples < 10
        or evaluation_samples < 10
        or not 0.0 < elite_fraction < 1.0
        or iterations < 1
        or not 0.0 < smoothing <= 1.0
        or not 0.0 < defensive_fraction < 1.0
        or covariance_floor <= 0.0
    ):
        raise ValueError("cross-entropy importance-sampling settings are invalid")
    rng = np.random.default_rng(seed)
    proposal_mean = base_mean.copy()
    proposal_covariance = base_covariance.copy()
    elite_thresholds = []
    for _ in range(iterations):
        sample = rng.multivariate_normal(
            proposal_mean, proposal_covariance, size=adaptation_samples
        )
        scores = _score_values(score, sample)
        level = min(float(threshold), float(np.quantile(scores, 1.0 - elite_fraction)))
        elite = scores >= level
        log_weights = multivariate_normal.logpdf(
            sample[elite], base_mean, base_covariance
        ) - multivariate_normal.logpdf(
            sample[elite], proposal_mean, proposal_covariance
        )
        log_weights -= np.max(log_weights)
        weights = np.exp(log_weights)
        weights /= weights.sum()
        target_mean = weights @ sample[elite]
        centered = sample[elite] - target_mean
        target_covariance = (centered * weights[:, None]).T @ centered
        target_covariance += covariance_floor * np.eye(dimension)
        proposal_mean = (
            (1.0 - smoothing) * proposal_mean + smoothing * target_mean
        )
        proposal_covariance = (
            (1.0 - smoothing) * proposal_covariance
            + smoothing * target_covariance
        )
        proposal_covariance += covariance_floor * np.eye(dimension)
        elite_thresholds.append(level)
        if level >= threshold:
            break

    use_base = rng.random(evaluation_samples) < defensive_fraction
    sample = np.empty((evaluation_samples, dimension))
    sample[use_base] = rng.multivariate_normal(
        base_mean, base_covariance, size=int(np.sum(use_base))
    )
    sample[~use_base] = rng.multivariate_normal(
        proposal_mean, proposal_covariance, size=int(np.sum(~use_base))
    )
    base_log = multivariate_normal.logpdf(sample, base_mean, base_covariance)
    proposal_log = multivariate_normal.logpdf(
        sample, proposal_mean, proposal_covariance
    )
    maximum = np.maximum(base_log, proposal_log)
    mixture_log = maximum + np.log(
        defensive_fraction * np.exp(base_log - maximum)
        + (1.0 - defensive_fraction) * np.exp(proposal_log - maximum)
    )
    weights = np.exp(base_log - mixture_log)
    event = _score_values(score, sample) >= threshold
    contributions = weights * event
    estimate = float(np.mean(contributions))
    standard_error = float(np.std(contributions, ddof=1) / sqrt(evaluation_samples))
    event_weights = contributions[event]
    effective = (
        float(event_weights.sum() ** 2 / np.sum(event_weights**2))
        if event_weights.size and np.sum(event_weights**2) > 0.0
        else 0.0
    )
    return CrossEntropyISResult(
        estimate,
        standard_error,
        effective,
        proposal_mean,
        proposal_covariance,
        tuple(elite_thresholds),
        int(np.sum(event)),
    )
