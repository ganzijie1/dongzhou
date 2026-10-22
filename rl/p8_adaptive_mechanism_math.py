"""P8 mechanisms, adaptive allocation, Gaussian processes, and online validity."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, exp, isfinite, lgamma, log, pi, sqrt
from typing import Hashable, Mapping, Sequence

import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import linprog
from scipy.special import ndtr


Agent = Hashable
Outcome = Hashable
Arm = Hashable


@dataclass(frozen=True)
class VCGResult:
    outcome: Outcome
    welfare: float
    payments: Mapping[Agent, float]
    utilities: Mapping[Agent, float]


def vcg_mechanism(
    agents: Sequence[Agent],
    outcomes: Sequence[Outcome],
    valuations: Mapping[tuple[Agent, Outcome], float],
) -> VCGResult:
    """Finite VCG social choice with Clarke pivot payments."""

    ordered_agents = tuple(dict.fromkeys(agents))
    ordered_outcomes = tuple(dict.fromkeys(outcomes))
    if not ordered_agents or not ordered_outcomes:
        raise ValueError("VCG agents and outcomes must be non-empty")
    values: dict[tuple[Agent, Outcome], float] = {}
    for agent in ordered_agents:
        for outcome in ordered_outcomes:
            value = float(valuations.get((agent, outcome), 0.0))
            if not isfinite(value):
                raise ValueError("VCG valuations must be finite")
            values[(agent, outcome)] = value

    def welfare(outcome: Outcome, excluded: Agent | None = None) -> float:
        return sum(values[(agent, outcome)] for agent in ordered_agents if agent != excluded)

    chosen = max(ordered_outcomes, key=lambda outcome: (welfare(outcome), repr(outcome)))
    payments = {}
    utilities = {}
    for agent in ordered_agents:
        external_welfare = max(welfare(outcome, agent) for outcome in ordered_outcomes)
        others_at_chosen = welfare(chosen, agent)
        payment = external_welfare - others_at_chosen
        payments[agent] = float(payment)
        utilities[agent] = values[(agent, chosen)] - float(payment)
    return VCGResult(chosen, welfare(chosen), payments, utilities)


@dataclass(frozen=True)
class ContractResult:
    wages: np.ndarray
    expected_wage: float
    desired_utility: float
    incentive_slacks: np.ndarray


def solve_limited_liability_contract(
    outcome_probabilities: Sequence[Sequence[float]],
    action_costs: Sequence[float],
    desired_action: int,
    *,
    reservation_utility: float = 0.0,
) -> ContractResult:
    """Minimum expected wage inducing one action under observable outcomes."""

    probabilities = np.asarray(outcome_probabilities, dtype=np.float64)
    costs = np.asarray(action_costs, dtype=np.float64)
    if probabilities.ndim != 2 or probabilities.shape[0] != costs.size or costs.size == 0:
        raise ValueError("contract action and outcome dimensions are invalid")
    if (
        np.any(~np.isfinite(probabilities))
        or np.any(probabilities < 0.0)
        or not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)
        or np.any(~np.isfinite(costs))
        or not 0 <= desired_action < costs.size
        or not isfinite(reservation_utility)
    ):
        raise ValueError("contract inputs are invalid")
    desired = probabilities[desired_action]
    inequalities = []
    bounds = []
    for action in range(costs.size):
        if action == desired_action:
            continue
        inequalities.append(probabilities[action] - desired)
        bounds.append(costs[action] - costs[desired_action])
    inequalities.append(-desired)
    bounds.append(-float(reservation_utility) - costs[desired_action])
    solved = linprog(
        desired,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(bounds),
        bounds=[(0.0, None)] * probabilities.shape[1],
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"limited-liability contract is infeasible: {solved.message}")
    wages = solved.x
    utilities = probabilities @ wages - costs
    return ContractResult(
        wages,
        float(desired @ wages),
        float(utilities[desired_action]),
        utilities[desired_action] - utilities,
    )


class LinUCBBandit:
    """Per-arm disjoint LinUCB for contextual resource allocation."""

    def __init__(
        self,
        arms: Sequence[Arm],
        dimension: int,
        *,
        exploration: float = 1.0,
        ridge: float = 1.0,
    ) -> None:
        self.arms = tuple(dict.fromkeys(arms))
        if (
            not self.arms
            or dimension <= 0
            or not isfinite(exploration)
            or exploration < 0.0
            or not isfinite(ridge)
            or ridge <= 0.0
        ):
            raise ValueError("LinUCB parameters are invalid")
        self.dimension = int(dimension)
        self.exploration = float(exploration)
        self.design = {arm: float(ridge) * np.eye(dimension) for arm in self.arms}
        self.response = {arm: np.zeros(dimension) for arm in self.arms}

    def scores(self, contexts: Mapping[Arm, Sequence[float]]) -> dict[Arm, float]:
        result = {}
        for arm in self.arms:
            if arm not in contexts:
                raise ValueError(f"missing context for arm {arm!r}")
            context = np.asarray(contexts[arm], dtype=np.float64)
            if context.shape != (self.dimension,) or np.any(~np.isfinite(context)):
                raise ValueError("LinUCB context is invalid")
            inverse_context = np.linalg.solve(self.design[arm], context)
            mean = float(self.response[arm] @ inverse_context)
            bonus = self.exploration * sqrt(max(0.0, float(context @ inverse_context)))
            result[arm] = mean + bonus
        return result

    def select(self, contexts: Mapping[Arm, Sequence[float]]) -> Arm:
        values = self.scores(contexts)
        return max(self.arms, key=lambda arm: (values[arm], repr(arm)))

    def update(self, arm: Arm, context: Sequence[float], reward: float) -> None:
        if arm not in self.design or not isfinite(reward):
            raise ValueError("LinUCB arm or reward is invalid")
        vector = np.asarray(context, dtype=np.float64)
        if vector.shape != (self.dimension,) or np.any(~np.isfinite(vector)):
            raise ValueError("LinUCB update context is invalid")
        self.design[arm] += np.outer(vector, vector)
        self.response[arm] += float(reward) * vector


@dataclass(frozen=True)
class RestlessArm:
    passive_transition: np.ndarray
    active_transition: np.ndarray
    passive_reward: np.ndarray
    active_reward: np.ndarray


@dataclass(frozen=True)
class WhittleResult:
    indices: np.ndarray
    indexable: bool


def _validate_restless_arm(arm: RestlessArm) -> RestlessArm:
    passive = np.asarray(arm.passive_transition, dtype=np.float64)
    active = np.asarray(arm.active_transition, dtype=np.float64)
    passive_reward = np.asarray(arm.passive_reward, dtype=np.float64)
    active_reward = np.asarray(arm.active_reward, dtype=np.float64)
    if passive.shape != (2, 2) or active.shape != (2, 2):
        raise ValueError("current Whittle implementation requires two-state arms")
    if passive_reward.shape != (2,) or active_reward.shape != (2,):
        raise ValueError("restless-arm reward vectors must have two states")
    if any(np.any(~np.isfinite(value)) for value in (passive, active, passive_reward, active_reward)):
        raise ValueError("restless-arm values must be finite")
    if np.any(passive < 0.0) or np.any(active < 0.0):
        raise ValueError("restless-arm transitions must be non-negative")
    if not np.allclose(passive.sum(axis=1), 1.0) or not np.allclose(active.sum(axis=1), 1.0):
        raise ValueError("restless-arm transition rows must sum to one")
    return RestlessArm(passive, active, passive_reward, active_reward)


def _restless_advantage(
    arm: RestlessArm,
    subsidy: float,
    discount: float,
    *,
    tolerance: float,
) -> np.ndarray:
    value = np.zeros(2)
    for _ in range(100_000):
        passive = arm.passive_reward + subsidy + discount * (arm.passive_transition @ value)
        active = arm.active_reward + discount * (arm.active_transition @ value)
        updated = np.maximum(passive, active)
        if float(np.max(np.abs(updated - value))) <= tolerance:
            value = updated
            break
        value = updated
    else:
        raise RuntimeError("restless-arm value iteration did not converge")
    passive = arm.passive_reward + subsidy + discount * (arm.passive_transition @ value)
    active = arm.active_reward + discount * (arm.active_transition @ value)
    return active - passive


def whittle_indices(
    arm: RestlessArm,
    *,
    discount: float = 0.95,
    lower_subsidy: float = -1_000.0,
    upper_subsidy: float = 1_000.0,
    tolerance: float = 1e-9,
) -> WhittleResult:
    """Compute two-state discounted Whittle indices and an indexability diagnostic."""

    checked = _validate_restless_arm(arm)
    if not 0.0 < discount < 1.0 or tolerance <= 0.0 or lower_subsidy >= upper_subsidy:
        raise ValueError("Whittle solver settings are invalid")
    grid = np.linspace(lower_subsidy, upper_subsidy, 101)
    passive_sets = [
        _restless_advantage(checked, float(subsidy), discount, tolerance=tolerance) <= tolerance
        for subsidy in grid
    ]
    indexable = all(
        not np.any(passive_sets[index] & ~passive_sets[index + 1])
        for index in range(len(passive_sets) - 1)
    )
    indices = np.empty(2)
    for state in range(2):
        low, high = float(lower_subsidy), float(upper_subsidy)
        low_advantage = _restless_advantage(checked, low, discount, tolerance=tolerance)[state]
        high_advantage = _restless_advantage(checked, high, discount, tolerance=tolerance)[state]
        if low_advantage <= 0.0 or high_advantage >= 0.0:
            raise ValueError("Whittle subsidy bracket does not contain the state index")
        while high - low > tolerance:
            middle = (low + high) / 2.0
            advantage = _restless_advantage(checked, middle, discount, tolerance=tolerance)[state]
            if advantage > 0.0:
                low = middle
            else:
                high = middle
        indices[state] = (low + high) / 2.0
    return WhittleResult(indices, indexable)


@dataclass(frozen=True)
class GaussianProcessPrediction:
    mean: np.ndarray
    standard_deviation: np.ndarray


class GaussianProcessRegressor:
    """Small exact RBF Gaussian process with auditable posterior uncertainty."""

    def __init__(
        self,
        *,
        length_scale: float = 1.0,
        signal_variance: float = 1.0,
        noise_variance: float = 1e-6,
    ) -> None:
        parameters = (length_scale, signal_variance, noise_variance)
        if any(not isfinite(value) or value <= 0.0 for value in parameters):
            raise ValueError("Gaussian-process parameters must be positive and finite")
        self.length_scale = float(length_scale)
        self.signal_variance = float(signal_variance)
        self.noise_variance = float(noise_variance)
        self.inputs: np.ndarray | None = None
        self.targets: np.ndarray | None = None
        self._factor: tuple[np.ndarray, bool] | None = None
        self._alpha: np.ndarray | None = None

    def _kernel(self, left: np.ndarray, right: np.ndarray) -> np.ndarray:
        squared = np.sum((left[:, None, :] - right[None, :, :]) ** 2, axis=2)
        return self.signal_variance * np.exp(-0.5 * squared / self.length_scale**2)

    def fit(self, inputs: Sequence[Sequence[float]], targets: Sequence[float]) -> "GaussianProcessRegressor":
        points = np.asarray(inputs, dtype=np.float64)
        values = np.asarray(targets, dtype=np.float64)
        if points.ndim != 2 or points.shape[0] != values.size or values.size == 0:
            raise ValueError("Gaussian-process training data are misaligned")
        if np.any(~np.isfinite(points)) or np.any(~np.isfinite(values)):
            raise ValueError("Gaussian-process training data must be finite")
        covariance = self._kernel(points, points)
        covariance.flat[:: covariance.shape[0] + 1] += self.noise_variance
        self.inputs = points.copy()
        self.targets = values.copy()
        self._factor = cho_factor(covariance, lower=True, check_finite=True)
        self._alpha = cho_solve(self._factor, values)
        return self

    def predict(self, inputs: Sequence[Sequence[float]]) -> GaussianProcessPrediction:
        if self.inputs is None or self._factor is None or self._alpha is None:
            raise RuntimeError("Gaussian process must be fitted first")
        points = np.asarray(inputs, dtype=np.float64)
        if points.ndim != 2 or points.shape[1] != self.inputs.shape[1] or np.any(~np.isfinite(points)):
            raise ValueError("Gaussian-process prediction inputs are invalid")
        cross = self._kernel(points, self.inputs)
        mean = cross @ self._alpha
        solved = cho_solve(self._factor, cross.T)
        variance = self.signal_variance - np.einsum("ij,ji->i", cross, solved)
        return GaussianProcessPrediction(mean, np.sqrt(np.maximum(variance, 0.0)))

    def propose(
        self,
        candidates: Sequence[Sequence[float]],
        *,
        maximize: bool = True,
        exploration: float = 0.01,
    ) -> tuple[int, np.ndarray]:
        if self.targets is None or not isfinite(exploration) or exploration < 0.0:
            raise RuntimeError("Gaussian process must be fitted and exploration must be valid")
        prediction = self.predict(candidates)
        incumbent = float(self.targets.max() if maximize else self.targets.min())
        improvement = (
            prediction.mean - incumbent - exploration
            if maximize
            else incumbent - prediction.mean - exploration
        )
        acquisition = np.maximum(improvement, 0.0)
        positive = prediction.standard_deviation > 0.0
        z = np.zeros_like(improvement)
        z[positive] = improvement[positive] / prediction.standard_deviation[positive]
        acquisition[positive] = (
            improvement[positive] * ndtr(z[positive])
            + prediction.standard_deviation[positive]
            * np.exp(-0.5 * z[positive] ** 2)
            / sqrt(2.0 * pi)
        )
        index = int(np.argmax(acquisition))
        return index, acquisition


def _conformal_radius(residuals: Sequence[float], alpha: float) -> float:
    values = np.asarray(residuals, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("online conformal residuals are invalid")
    if not 0.0 < alpha < 1.0:
        raise ValueError("online conformal alpha must be in (0, 1)")
    rank = ceil((values.size + 1) * (1.0 - alpha))
    return float("inf") if rank > values.size else float(np.sort(values)[rank - 1])


class AdaptiveConformalRegressor:
    """Rolling conformal intervals with adaptive miscoverage control."""

    def __init__(
        self,
        calibration_residuals: Sequence[float],
        *,
        target_alpha: float = 0.1,
        learning_rate: float = 0.01,
        window: int = 200,
    ) -> None:
        if not 0.0 < target_alpha < 1.0 or learning_rate <= 0.0 or window <= 0:
            raise ValueError("adaptive conformal settings are invalid")
        residuals = [float(value) for value in calibration_residuals]
        _conformal_radius(residuals, target_alpha)
        self.residuals = residuals[-window:]
        self.target_alpha = float(target_alpha)
        self.current_alpha = float(target_alpha)
        self.learning_rate = float(learning_rate)
        self.window = int(window)

    def interval(self, prediction: float) -> tuple[float, float]:
        if not isfinite(prediction):
            raise ValueError("conformal prediction must be finite")
        radius = _conformal_radius(self.residuals, self.current_alpha)
        return float(prediction - radius), float(prediction + radius)

    def update(self, prediction: float, target: float) -> bool:
        if not isfinite(prediction) or not isfinite(target):
            raise ValueError("conformal update values must be finite")
        lower, upper = self.interval(prediction)
        missed = not lower <= target <= upper
        self.current_alpha += self.learning_rate * (self.target_alpha - float(missed))
        self.current_alpha = min(1.0 - 1e-6, max(1e-6, self.current_alpha))
        self.residuals.append(abs(float(target) - float(prediction)))
        self.residuals = self.residuals[-self.window :]
        return missed


@dataclass(frozen=True)
class EProcessStatus:
    observations: int
    successes: int
    e_value: float
    maximum_e_value: float


class BernoulliMixtureEProcess:
    """Anytime-valid beta-mixture e-process for a fixed Bernoulli null."""

    def __init__(self, null_probability: float, *, alpha: float = 0.5, beta: float = 0.5) -> None:
        if not 0.0 < null_probability < 1.0 or alpha <= 0.0 or beta <= 0.0:
            raise ValueError("e-process parameters are invalid")
        self.null_probability = float(null_probability)
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.observations = 0
        self.successes = 0
        self.maximum_e_value = 1.0

    def update(self, success: bool) -> EProcessStatus:
        self.observations += 1
        self.successes += int(bool(success))
        failures = self.observations - self.successes
        log_mixture = (
            lgamma(self.alpha + self.successes)
            + lgamma(self.beta + failures)
            - lgamma(self.alpha + self.beta + self.observations)
            - lgamma(self.alpha)
            - lgamma(self.beta)
            + lgamma(self.alpha + self.beta)
        )
        log_null = self.successes * log(self.null_probability) + failures * log(
            1.0 - self.null_probability
        )
        e_value = exp(log_mixture - log_null)
        self.maximum_e_value = max(self.maximum_e_value, e_value)
        return EProcessStatus(
            self.observations,
            self.successes,
            float(e_value),
            float(self.maximum_e_value),
        )

    def rejects(self, significance: float = 0.05) -> bool:
        if not 0.0 < significance < 1.0:
            raise ValueError("e-process significance must be in (0, 1)")
        return self.maximum_e_value >= 1.0 / significance
