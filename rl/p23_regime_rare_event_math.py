"""P23 online regimes, explicit-duration states, and rare-event simulation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi
from typing import Callable, Sequence

import numpy as np
from scipy.special import logsumexp


@dataclass(frozen=True)
class BOCPDUpdate:
    run_length_posterior: np.ndarray
    change_probability: float
    map_run_length: int
    predictive_log_evidence: float
    pruned_mass: float


class BayesianOnlineChangePointDetector:
    """Normal-Normal BOCPD with known observation variance and bounded memory."""

    def __init__(
        self,
        *,
        hazard: float,
        observation_variance: float,
        prior_mean: float = 0.0,
        prior_mean_variance: float = 10.0,
        maximum_run_length: int | None = None,
    ) -> None:
        if (
            not isfinite(hazard)
            or not 0.0 < hazard < 1.0
            or not isfinite(observation_variance)
            or observation_variance <= 0.0
            or not isfinite(prior_mean)
            or not isfinite(prior_mean_variance)
            or prior_mean_variance <= 0.0
            or maximum_run_length is not None
            and maximum_run_length < 1
        ):
            raise ValueError("BOCPD parameters are invalid")
        self.hazard = float(hazard)
        self.observation_variance = float(observation_variance)
        self.prior_mean = float(prior_mean)
        self.prior_mean_variance = float(prior_mean_variance)
        self.maximum_run_length = maximum_run_length
        self.reset()

    def reset(self) -> None:
        self.time = 0
        self._log_joint = np.array([0.0])
        self._means = np.array([self.prior_mean])
        self._mean_variances = np.array([self.prior_mean_variance])

    @staticmethod
    def _normal_logpdf(value: float, mean: np.ndarray, variance: np.ndarray) -> np.ndarray:
        return -0.5 * (
            np.log(2.0 * pi * variance) + (value - mean) ** 2 / variance
        )

    def _posterior_update(
        self,
        value: float,
        means: np.ndarray,
        variances: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        precision = 1.0 / variances + 1.0 / self.observation_variance
        posterior_variance = 1.0 / precision
        posterior_mean = posterior_variance * (
            means / variances + value / self.observation_variance
        )
        return posterior_mean, posterior_variance

    def update(self, observation: float) -> BOCPDUpdate:
        """Consume one scalar observation and return the normalized run-length posterior."""

        value = float(observation)
        if not isfinite(value):
            raise ValueError("BOCPD observation must be finite")
        predictive_variance = self.observation_variance + self._mean_variances
        predictive = self._normal_logpdf(
            value, self._means, predictive_variance
        )
        prior_predictive = float(
            self._normal_logpdf(
                value,
                np.array([self.prior_mean]),
                np.array(
                    [self.observation_variance + self.prior_mean_variance]
                ),
            )[0]
        )
        growth = self._log_joint + log(1.0 - self.hazard) + predictive
        change = logsumexp(self._log_joint + log(self.hazard)) + prior_predictive
        full_log_joint = np.r_[change, growth]
        full_evidence = float(logsumexp(full_log_joint))
        full_posterior = np.exp(full_log_joint - full_evidence)

        prior_mean, prior_variance = self._posterior_update(
            value,
            np.array([self.prior_mean]),
            np.array([self.prior_mean_variance]),
        )
        grown_mean, grown_variance = self._posterior_update(
            value, self._means, self._mean_variances
        )
        new_means = np.r_[prior_mean, grown_mean]
        new_variances = np.r_[prior_variance, grown_variance]
        pruned_mass = 0.0
        if (
            self.maximum_run_length is not None
            and full_posterior.size > self.maximum_run_length + 1
        ):
            keep = self.maximum_run_length + 1
            pruned_mass = float(np.sum(full_posterior[keep:]))
            full_log_joint = full_log_joint[:keep]
            new_means = new_means[:keep]
            new_variances = new_variances[:keep]
        normalization = float(logsumexp(full_log_joint))
        posterior = np.exp(full_log_joint - normalization)
        self._log_joint = full_log_joint - normalization
        self._means = new_means
        self._mean_variances = new_variances
        self.time += 1
        return BOCPDUpdate(
            posterior.copy(),
            float(posterior[0]),
            int(np.argmax(posterior)),
            full_evidence,
            pruned_mass,
        )


def _probability_vector(value: Sequence[float], size: int, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float64)
    if (
        vector.shape != (size,)
        or np.any(~np.isfinite(vector))
        or np.any(vector < 0.0)
        or not np.isclose(vector.sum(), 1.0)
    ):
        raise ValueError(f"{name} must be a probability vector")
    return vector


def _hsmm_inputs(
    emission_log_likelihood: Sequence[Sequence[float]],
    transition: Sequence[Sequence[float]],
    initial: Sequence[float],
    duration_probability: Sequence[Sequence[float]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    emission = np.asarray(emission_log_likelihood, dtype=np.float64)
    matrix = np.asarray(transition, dtype=np.float64)
    duration = np.asarray(duration_probability, dtype=np.float64)
    if (
        emission.ndim != 2
        or min(emission.shape) == 0
        or np.any(~np.isfinite(emission))
    ):
        raise ValueError("HSMM emission log likelihood is invalid")
    _, states = emission.shape
    if (
        matrix.shape != (states, states)
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix.sum(axis=1), 1.0)
        or duration.ndim != 2
        or duration.shape[0] != states
        or duration.shape[1] == 0
        or np.any(~np.isfinite(duration))
        or np.any(duration < 0.0)
        or not np.allclose(duration.sum(axis=1), 1.0)
    ):
        raise ValueError("HSMM transition or duration probabilities are invalid")
    start = _probability_vector(initial, states, "HSMM initial distribution")
    return emission, matrix, start, duration


def _safe_log_probabilities(probabilities: np.ndarray) -> np.ndarray:
    result = np.full_like(probabilities, -np.inf)
    positive = probabilities > 0.0
    result[positive] = np.log(probabilities[positive])
    return result


@dataclass(frozen=True)
class HSMMForwardResult:
    log_end_probability: np.ndarray
    log_likelihood: float
    maximum_duration: int


def hsmm_forward(
    emission_log_likelihood: Sequence[Sequence[float]],
    transition: Sequence[Sequence[float]],
    initial: Sequence[float],
    duration_probability: Sequence[Sequence[float]],
) -> HSMMForwardResult:
    """Run the segment-ending HSMM forward recursion in the log domain."""

    emission, matrix, start, duration = _hsmm_inputs(
        emission_log_likelihood, transition, initial, duration_probability
    )
    time_steps, states = emission.shape
    maximum_duration = duration.shape[1]
    log_transition = _safe_log_probabilities(matrix)
    log_initial = _safe_log_probabilities(start)
    log_duration = _safe_log_probabilities(duration)
    prefix = np.vstack((np.zeros(states), np.cumsum(emission, axis=0)))
    forward = np.full((time_steps, states), -np.inf)
    for end in range(time_steps):
        for state in range(states):
            terms = []
            for length in range(1, min(maximum_duration, end + 1) + 1):
                if not np.isfinite(log_duration[state, length - 1]):
                    continue
                segment_start = end + 1 - length
                segment = prefix[end + 1, state] - prefix[segment_start, state]
                if segment_start == 0:
                    predecessor = log_initial[state]
                else:
                    predecessor = logsumexp(
                        forward[segment_start - 1] + log_transition[:, state]
                    )
                terms.append(
                    predecessor + log_duration[state, length - 1] + segment
                )
            if terms:
                forward[end, state] = logsumexp(terms)
    likelihood = float(logsumexp(forward[-1]))
    if not isfinite(likelihood):
        raise ValueError("the HSMM assigns zero probability to the sequence")
    return HSMMForwardResult(forward, likelihood, maximum_duration)


@dataclass(frozen=True)
class HSMMViterbiResult:
    states: np.ndarray
    segments: tuple[tuple[int, int, int], ...]
    log_probability: float


def hsmm_viterbi(
    emission_log_likelihood: Sequence[Sequence[float]],
    transition: Sequence[Sequence[float]],
    initial: Sequence[float],
    duration_probability: Sequence[Sequence[float]],
) -> HSMMViterbiResult:
    """Decode the maximum-probability HSMM segmentation."""

    emission, matrix, start, duration = _hsmm_inputs(
        emission_log_likelihood, transition, initial, duration_probability
    )
    time_steps, states = emission.shape
    maximum_duration = duration.shape[1]
    log_transition = _safe_log_probabilities(matrix)
    log_initial = _safe_log_probabilities(start)
    log_duration = _safe_log_probabilities(duration)
    prefix = np.vstack((np.zeros(states), np.cumsum(emission, axis=0)))
    scores = np.full((time_steps, states), -np.inf)
    previous_state = np.full((time_steps, states), -1, dtype=np.int64)
    selected_duration = np.zeros((time_steps, states), dtype=np.int64)
    for end in range(time_steps):
        for state in range(states):
            best = -np.inf
            best_state = -1
            best_duration = 0
            for length in range(1, min(maximum_duration, end + 1) + 1):
                if not np.isfinite(log_duration[state, length - 1]):
                    continue
                segment_start = end + 1 - length
                segment = prefix[end + 1, state] - prefix[segment_start, state]
                if segment_start == 0:
                    candidate = log_initial[state]
                    predecessor = -1
                else:
                    predecessor_values = (
                        scores[segment_start - 1] + log_transition[:, state]
                    )
                    predecessor = int(np.argmax(predecessor_values))
                    candidate = predecessor_values[predecessor]
                candidate += log_duration[state, length - 1] + segment
                if candidate > best:
                    best = float(candidate)
                    best_state = predecessor
                    best_duration = length
            scores[end, state] = best
            previous_state[end, state] = best_state
            selected_duration[end, state] = best_duration
    state = int(np.argmax(scores[-1]))
    if not np.isfinite(scores[-1, state]):
        raise ValueError("the HSMM has no valid Viterbi path")
    decoded = np.empty(time_steps, dtype=np.int64)
    segments = []
    end = time_steps - 1
    while end >= 0:
        length = int(selected_duration[end, state])
        if length <= 0:
            raise RuntimeError("HSMM Viterbi backpointer is invalid")
        begin = end + 1 - length
        decoded[begin : end + 1] = state
        segments.append((state, begin, end + 1))
        predecessor = int(previous_state[end, state])
        end = begin - 1
        state = predecessor
    segments.reverse()
    return HSMMViterbiResult(
        decoded,
        tuple(segments),
        float(np.max(scores[-1])),
    )


@dataclass(frozen=True)
class AMSResult:
    probability: float
    levels: tuple[float, ...]
    iterations: int
    final_scores: np.ndarray
    target_count: int
    ancestors: np.ndarray
    genealogy_concentration: float
    tied_levels: int
    converged: bool


def adaptive_multilevel_splitting(
    simulate: Callable[[np.random.Generator], object],
    branch: Callable[[object, float, np.random.Generator], object],
    score: Callable[[object], float],
    *,
    target_level: float,
    particle_count: int,
    kill_count: int = 1,
    random_state: int | np.random.Generator | None = None,
    max_iterations: int = 10_000,
) -> AMSResult:
    """Run trajectory AMS with explicit branching and genealogy diagnostics."""

    if (
        not isfinite(target_level)
        or particle_count < 2
        or kill_count < 1
        or kill_count >= particle_count
        or max_iterations <= 0
    ):
        raise ValueError("AMS parameters are invalid")
    rng = (
        random_state
        if isinstance(random_state, np.random.Generator)
        else np.random.default_rng(random_state)
    )
    particles = [simulate(rng) for _ in range(particle_count)]
    scores = np.asarray([score(particle) for particle in particles], dtype=np.float64)
    if np.any(~np.isfinite(scores)):
        raise ValueError("AMS score must be finite")
    ancestors = np.arange(particle_count, dtype=np.int64)
    survival_factor = 1.0
    levels = []
    tied_levels = 0
    converged = False
    for iteration in range(max_iterations + 1):
        permutation = rng.permutation(particle_count)
        order = permutation[np.argsort(scores[permutation], kind="stable")]
        threshold = float(scores[order[kill_count - 1]])
        if threshold >= target_level:
            converged = True
            break
        if iteration == max_iterations:
            break
        if np.count_nonzero(np.isclose(scores, threshold)) > 1:
            tied_levels += 1
        levels.append(threshold)
        killed = order[:kill_count]
        survivors = order[kill_count:]
        survival_factor *= 1.0 - kill_count / particle_count
        for index in killed:
            parent = int(rng.choice(survivors))
            child = branch(particles[parent], threshold, rng)
            child_score = float(score(child))
            if not isfinite(child_score) or child_score < threshold - 1e-10:
                raise ValueError("AMS branch must preserve the crossed level")
            particles[index] = child
            scores[index] = child_score
            ancestors[index] = ancestors[parent]
    target_count = int(np.count_nonzero(scores >= target_level))
    probability = survival_factor * target_count / particle_count
    counts = np.bincount(ancestors, minlength=particle_count)
    concentration = float(np.sum((counts / particle_count) ** 2))
    return AMSResult(
        float(probability),
        tuple(levels),
        min(iteration, max_iterations),
        scores.copy(),
        target_count,
        ancestors.copy(),
        concentration,
        tied_levels,
        converged,
    )


@dataclass(frozen=True)
class SubsetSimulationResult:
    probability: float
    levels: tuple[float, ...]
    conditional_probabilities: tuple[float, ...]
    acceptance_rates: tuple[float, ...]
    samples: np.ndarray
    scores: np.ndarray
    converged: bool


def subset_simulation(
    initial_sampler: Callable[[int, np.random.Generator], Sequence],
    log_density: Callable[[np.ndarray], float],
    score: Callable[[np.ndarray], float],
    *,
    target_level: float,
    sample_count: int,
    conditional_probability: float = 0.1,
    proposal_scale: float | Sequence[float] = 1.0,
    random_state: int | np.random.Generator | None = None,
    max_levels: int = 20,
) -> SubsetSimulationResult:
    """Estimate P(score(X) >= target) with adaptive conditional MCMC subsets."""

    if (
        not isfinite(target_level)
        or sample_count < 10
        or not 0.0 < conditional_probability < 1.0
        or sample_count * conditional_probability < 1.0
        or max_levels < 1
    ):
        raise ValueError("subset simulation parameters are invalid")
    rng = (
        random_state
        if isinstance(random_state, np.random.Generator)
        else np.random.default_rng(random_state)
    )
    samples = np.asarray(initial_sampler(sample_count, rng), dtype=np.float64)
    if samples.ndim == 1:
        samples = samples[:, None]
    if (
        samples.ndim != 2
        or samples.shape[0] != sample_count
        or samples.shape[1] == 0
        or np.any(~np.isfinite(samples))
    ):
        raise ValueError("initial subset samples have the wrong shape")
    scale = np.asarray(proposal_scale, dtype=np.float64)
    if scale.ndim == 0:
        scale = np.full(samples.shape[1], float(scale))
    if scale.shape != (samples.shape[1],) or np.any(scale <= 0.0):
        raise ValueError("subset proposal scale is invalid")

    def evaluate(values: np.ndarray) -> np.ndarray:
        result = np.asarray([score(value) for value in values], dtype=np.float64)
        if np.any(~np.isfinite(result)):
            raise ValueError("subset score must be finite")
        return result

    scores = evaluate(samples)
    probability_prefix = 1.0
    levels = []
    conditional = []
    acceptance_rates = []
    converged = False
    previous_level = -np.inf
    for _ in range(max_levels):
        level = float(
            np.quantile(
                scores,
                1.0 - conditional_probability,
                method="higher",
            )
        )
        if level >= target_level:
            final_probability = float(np.mean(scores >= target_level))
            conditional.append(final_probability)
            probability_prefix *= final_probability
            converged = final_probability > 0.0
            break
        if level <= previous_level + 1e-14:
            break
        previous_level = level
        levels.append(level)
        seed_indices = np.flatnonzero(scores >= level)
        layer_probability = seed_indices.size / sample_count
        conditional.append(float(layer_probability))
        probability_prefix *= layer_probability
        seeds = samples[seed_indices]
        generated = []
        accepted = 0
        proposals = 0
        seed_order = rng.permutation(seeds.shape[0])
        while len(generated) < sample_count:
            for seed_index in seed_order:
                current = seeds[seed_index].copy()
                current_log_density = float(log_density(current))
                if not isfinite(current_log_density):
                    raise ValueError("seed has nonfinite log density")
                generated.append(current.copy())
                if len(generated) >= sample_count:
                    break
                proposal = current + rng.normal(scale=scale)
                proposals += 1
                proposal_score = float(score(proposal))
                proposal_log_density = float(log_density(proposal))
                if (
                    proposal_score >= level
                    and isfinite(proposal_log_density)
                    and log(rng.random())
                    < min(0.0, proposal_log_density - current_log_density)
                ):
                    current = proposal
                    accepted += 1
                generated.append(current.copy())
                if len(generated) >= sample_count:
                    break
        samples = np.asarray(generated[:sample_count])
        scores = evaluate(samples)
        acceptance_rates.append(accepted / max(1, proposals))
    else:
        final_probability = float(np.mean(scores >= target_level))
        conditional.append(final_probability)
        probability_prefix *= final_probability
    return SubsetSimulationResult(
        float(probability_prefix),
        tuple(levels),
        tuple(conditional),
        tuple(acceptance_rates),
        samples,
        scores,
        converged,
    )
