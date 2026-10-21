"""Reliability, rare-event estimation, and finite constraint verification."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import exp, isfinite, log
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class AbsorbingChainResult:
    transient_states: tuple[int, ...]
    absorbing_states: tuple[int, ...]
    fundamental_matrix: np.ndarray
    absorption_probabilities: np.ndarray
    expected_steps: tuple[float, ...]


def analyze_absorbing_markov_chain(
    transitions: Sequence[Sequence[float]],
    *,
    absorbing_states: Sequence[int] | None = None,
) -> AbsorbingChainResult:
    """Compute the fundamental matrix, absorption odds, and mean duration."""

    probability = np.asarray(transitions, dtype=np.float64)
    if probability.ndim != 2 or probability.shape[0] != probability.shape[1] or not probability.size:
        raise ValueError("absorbing-chain transition matrix must be non-empty and square")
    if np.any(~np.isfinite(probability)) or np.any(probability < 0.0):
        raise ValueError("absorbing-chain probabilities must be finite and non-negative")
    if not np.allclose(probability.sum(axis=1), 1.0):
        raise ValueError("absorbing-chain transition rows must sum to one")
    count = probability.shape[0]
    if absorbing_states is None:
        absorbing = tuple(
            state
            for state in range(count)
            if np.isclose(probability[state, state], 1.0)
            and np.isclose(np.delete(probability[state], state).sum(), 0.0)
        )
    else:
        absorbing = tuple(dict.fromkeys(int(state) for state in absorbing_states))
    if not absorbing or any(state < 0 or state >= count for state in absorbing):
        raise ValueError("absorbing-chain absorbing states are invalid")
    for state in absorbing:
        expected = np.zeros(count)
        expected[state] = 1.0
        if not np.allclose(probability[state], expected):
            raise ValueError("declared absorbing state is not absorbing")
    transient = tuple(state for state in range(count) if state not in absorbing)
    if not transient:
        return AbsorbingChainResult(
            (), absorbing, np.empty((0, 0)), np.empty((0, len(absorbing))), ()
        )
    q_matrix = probability[np.ix_(transient, transient)]
    r_matrix = probability[np.ix_(transient, absorbing)]
    try:
        fundamental = np.linalg.inv(np.eye(len(transient)) - q_matrix)
    except np.linalg.LinAlgError as error:
        raise ValueError("chain is not absorbing from every transient state") from error
    absorption = fundamental @ r_matrix
    if not np.allclose(absorption.sum(axis=1), 1.0, atol=1e-8):
        raise ValueError("chain is not absorbing with probability one")
    expected_steps = fundamental @ np.ones(len(transient))
    return AbsorbingChainResult(
        transient,
        absorbing,
        fundamental,
        absorption,
        tuple(float(value) for value in expected_steps),
    )


@dataclass(frozen=True)
class RenewalResult:
    renewal_mass: tuple[float, ...]
    expected_renewals: tuple[float, ...]


def discrete_renewal_process(
    interarrival_probabilities: Sequence[float], horizon: int
) -> RenewalResult:
    """Solve the discrete renewal equation through a finite horizon.

    Input index zero denotes an interarrival time of one step.
    """

    distribution = np.asarray(interarrival_probabilities, dtype=np.float64)
    if distribution.ndim != 1 or not distribution.size:
        raise ValueError("renewal interarrival distribution must be a vector")
    if np.any(~np.isfinite(distribution)) or np.any(distribution < 0.0):
        raise ValueError("renewal probabilities must be finite and non-negative")
    if not np.isclose(distribution.sum(), 1.0):
        raise ValueError("renewal interarrival probabilities must sum to one")
    if horizon < 0:
        raise ValueError("renewal horizon must be non-negative")
    mass = np.zeros(horizon + 1, dtype=np.float64)
    mass[0] = 1.0
    for time in range(1, horizon + 1):
        mass[time] = sum(
            distribution[delay - 1] * mass[time - delay]
            for delay in range(1, min(time, distribution.size) + 1)
        )
    expected = np.cumsum(mass)
    expected -= 1.0
    return RenewalResult(
        tuple(float(value) for value in mass),
        tuple(float(value) for value in expected),
    )


def series_reliability(component_probabilities: Sequence[float]) -> float:
    """Reliability of independent components that must all function."""

    probabilities = _reliability_probabilities(component_probabilities)
    return float(np.prod(probabilities))


def parallel_reliability(component_probabilities: Sequence[float]) -> float:
    """Reliability of independent components where any one can function."""

    probabilities = _reliability_probabilities(component_probabilities)
    return float(1.0 - np.prod(1.0 - probabilities))


def k_out_of_n_reliability(
    component_probabilities: Sequence[float], required: int
) -> float:
    """Probability that at least ``required`` independent components work."""

    probabilities = _reliability_probabilities(component_probabilities)
    if required < 0 or required > probabilities.size:
        raise ValueError("required component count is out of range")
    distribution = np.zeros(probabilities.size + 1, dtype=np.float64)
    distribution[0] = 1.0
    for probability in probabilities:
        next_distribution = distribution * (1.0 - probability)
        next_distribution[1:] += distribution[:-1] * probability
        distribution = next_distribution
    return float(distribution[required:].sum())


def _reliability_probabilities(values: Sequence[float]) -> np.ndarray:
    probabilities = np.asarray(values, dtype=np.float64)
    if probabilities.ndim != 1 or not probabilities.size:
        raise ValueError("component reliabilities must be a non-empty vector")
    if np.any(~np.isfinite(probabilities)) or np.any(
        (probabilities < 0.0) | (probabilities > 1.0)
    ):
        raise ValueError("component reliabilities must lie in [0, 1]")
    return probabilities


@dataclass(frozen=True)
class ImportanceSamplingResult:
    estimate: float
    standard_error: float
    effective_sample_size: float
    samples: int


def importance_sampling_estimate(
    proposal: Callable[[np.random.Generator, int], Sequence[float]],
    log_likelihood_ratio: Callable[[np.ndarray], Sequence[float]],
    statistic: Callable[[np.ndarray], Sequence[float]],
    *,
    samples: int,
    seed: int = 2026,
) -> ImportanceSamplingResult:
    """Estimate an expectation under a target law from proposal samples."""

    if samples <= 1:
        raise ValueError("importance sampling needs at least two samples")
    random = np.random.default_rng(seed)
    draws = np.asarray(proposal(random, samples), dtype=np.float64)
    if draws.shape[0] != samples or np.any(~np.isfinite(draws)):
        raise ValueError("importance proposal returned invalid samples")
    log_weights = np.asarray(log_likelihood_ratio(draws), dtype=np.float64)
    values = np.asarray(statistic(draws), dtype=np.float64)
    if log_weights.shape != (samples,) or values.shape != (samples,):
        raise ValueError("importance weights and statistics must be sample vectors")
    if np.any(~np.isfinite(log_weights)) or np.any(~np.isfinite(values)):
        raise ValueError("importance weights and statistics must be finite")
    maximum = float(np.max(log_weights))
    scaled = np.exp(log_weights - maximum)
    weighted_values = scaled * values
    scale = exp(maximum)
    estimate = scale * float(np.mean(weighted_values))
    standard_error = scale * float(np.std(weighted_values, ddof=1) / np.sqrt(samples))
    effective = float(scaled.sum() ** 2 / np.sum(scaled * scaled))
    return ImportanceSamplingResult(estimate, standard_error, effective, samples)


def normal_tail_importance_sampling(
    threshold: float,
    *,
    proposal_mean: float | None = None,
    samples: int = 20_000,
    seed: int = 2026,
) -> ImportanceSamplingResult:
    """Estimate P[Z >= threshold] for standard normal Z by exponential tilting."""

    if not isfinite(threshold):
        raise ValueError("normal-tail threshold must be finite")
    mean = max(0.0, threshold) if proposal_mean is None else float(proposal_mean)
    if not isfinite(mean):
        raise ValueError("normal-tail proposal mean must be finite")
    return importance_sampling_estimate(
        lambda random, count: random.normal(mean, 1.0, size=count),
        lambda draws: -mean * draws + 0.5 * mean * mean,
        lambda draws: (draws >= threshold).astype(np.float64),
        samples=samples,
        seed=seed,
    )


def bernoulli_large_deviation_rate(observed_fraction: float, base_rate: float) -> float:
    """Cramer rate D(q || p) for a Bernoulli sample mean."""

    q_value = float(observed_fraction)
    p_value = float(base_rate)
    if not isfinite(q_value) or not isfinite(p_value):
        raise ValueError("large-deviation probabilities must be finite")
    if not 0.0 <= q_value <= 1.0 or not 0.0 < p_value < 1.0:
        raise ValueError("large-deviation probabilities are outside their domains")
    left = 0.0 if q_value == 0.0 else q_value * log(q_value / p_value)
    right = (
        0.0
        if q_value == 1.0
        else (1.0 - q_value) * log((1.0 - q_value) / (1.0 - p_value))
    )
    return left + right


def bernoulli_chernoff_bound(
    trials: int, observed_fraction: float, base_rate: float
) -> float:
    """Chernoff upper-tail bound exp(-n D(q || p))."""

    if trials <= 0:
        raise ValueError("Chernoff trial count must be positive")
    if observed_fraction < base_rate:
        raise ValueError("upper-tail Chernoff bound requires q >= p")
    return exp(
        -trials * bernoulli_large_deviation_rate(observed_fraction, base_rate)
    )


Assignment = Mapping[str, Hashable]
Constraint = Callable[[Assignment], bool]


@dataclass(frozen=True)
class FiniteConstraintResult:
    satisfiable: bool
    solutions: tuple[Mapping[str, Hashable], ...]
    examined_assignments: int
    complete: bool


def solve_finite_constraints(
    domains: Mapping[str, Sequence[Hashable]],
    constraints: Sequence[Constraint],
    *,
    max_solutions: int = 1,
    max_assignments: int = 1_000_000,
) -> FiniteConstraintResult:
    """Exact bounded SMT-style satisfiability over explicit finite domains."""

    names = tuple(sorted(domains))
    if not names or any(not domains[name] for name in names):
        raise ValueError("finite constraint variables need non-empty domains")
    if max_solutions <= 0 or max_assignments <= 0:
        raise ValueError("finite constraint limits must be positive")
    choices = tuple(tuple(dict.fromkeys(domains[name])) for name in names)
    search_size = int(np.prod([len(values) for values in choices], dtype=object))
    examined = 0
    solutions: list[Mapping[str, Hashable]] = []
    for values in product(*choices):
        if examined >= max_assignments:
            break
        examined += 1
        assignment = dict(zip(names, values))
        if all(bool(constraint(assignment)) for constraint in constraints):
            solutions.append(assignment)
            if len(solutions) >= max_solutions:
                break
    complete = examined >= search_size or (not solutions and examined == search_size)
    return FiniteConstraintResult(bool(solutions), tuple(solutions), examined, complete)
