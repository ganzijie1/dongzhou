"""P21 adaptive safety, economic transfer operators, and replay causality."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.stats import t


def _transition_kernel(value: Sequence, dimensions: int) -> np.ndarray:
    kernel = np.asarray(value, dtype=np.float64)
    if kernel.ndim != dimensions:
        raise ValueError(f"transition kernel must have {dimensions} dimensions")
    if dimensions == 3:
        states, _, next_states = kernel.shape
    else:
        _, states, _, next_states = kernel.shape
    if (
        states == 0
        or next_states != states
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=-1), 1.0)
    ):
        raise ValueError("transition kernel is invalid")
    return kernel


def _state_mask(states: int, selected: Sequence[int] | Sequence[bool]) -> np.ndarray:
    values = np.asarray(selected)
    if values.dtype == bool:
        if values.shape != (states,):
            raise ValueError("state mask has the wrong shape")
        return values.copy()
    mask = np.zeros(states, dtype=bool)
    indices = tuple(dict.fromkeys(int(value) for value in selected))
    if any(value < 0 or value >= states for value in indices):
        raise ValueError("state index is out of range")
    mask[list(indices)] = True
    return mask


@dataclass(frozen=True)
class FiniteSurvivalResult:
    values: np.ndarray
    policy: np.ndarray
    safe_states: tuple[int, ...]
    horizon: int


def finite_horizon_survival_probability(
    transition: Sequence,
    safe_states: Sequence[int] | Sequence[bool],
    *,
    horizon: int,
) -> FiniteSurvivalResult:
    """Maximize the probability of remaining safe for every step up to a horizon."""

    kernel = _transition_kernel(transition, 3)
    states, _, _ = kernel.shape
    safe = _state_mask(states, safe_states)
    if not np.any(safe) or horizon < 0:
        raise ValueError("finite-horizon survival inputs are invalid")
    values = np.zeros((horizon + 1, states))
    values[0, safe] = 1.0
    policy = np.zeros((horizon, states), dtype=np.int64)
    for remaining in range(1, horizon + 1):
        q_values = np.einsum("san,n->sa", kernel, values[remaining - 1])
        values[remaining, safe] = np.max(q_values[safe], axis=1)
        policy[remaining - 1, safe] = np.argmax(q_values[safe], axis=1)
    return FiniteSurvivalResult(
        values,
        policy,
        tuple(int(value) for value in np.flatnonzero(safe)),
        horizon,
    )


@dataclass(frozen=True)
class InfiniteSurvivalResult:
    values: np.ndarray
    policy: tuple[int, ...]
    iterations: int
    converged: bool
    residual: float


def infinite_horizon_survival_probability(
    transition: Sequence,
    safe_states: Sequence[int] | Sequence[bool],
    *,
    tolerance: float = 1e-10,
    max_iterations: int = 100_000,
) -> InfiniteSurvivalResult:
    """Compute the greatest fixed point for staying safe forever."""

    kernel = _transition_kernel(transition, 3)
    states, _, _ = kernel.shape
    safe = _state_mask(states, safe_states)
    if (
        not np.any(safe)
        or not isfinite(tolerance)
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("infinite-horizon survival inputs are invalid")
    values = safe.astype(np.float64)
    q_values = np.zeros(kernel.shape[:2])
    residual = np.inf
    for iteration in range(1, max_iterations + 1):
        q_values = np.einsum("san,n->sa", kernel, values)
        updated = np.zeros(states)
        updated[safe] = np.max(q_values[safe], axis=1)
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        if residual <= tolerance:
            return InfiniteSurvivalResult(
                values,
                tuple(int(value) for value in np.argmax(q_values, axis=1)),
                iteration,
                True,
                residual,
            )
    return InfiniteSurvivalResult(
        values,
        tuple(int(value) for value in np.argmax(q_values, axis=1)),
        max_iterations,
        False,
        residual,
    )


@dataclass(frozen=True)
class ScenarioRobustMDPResult:
    values: np.ndarray
    q_values: np.ndarray
    policy: tuple[int, ...]
    worst_case_scenarios: np.ndarray
    iterations: int
    converged: bool
    bellman_residual: float


def scenario_robust_value_iteration(
    transition_scenarios: Sequence,
    reward: Sequence,
    *,
    discount: float = 0.95,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> ScenarioRobustMDPResult:
    """Robust Bellman iteration over a finite state-action rectangular scenario set."""

    kernel = _transition_kernel(transition_scenarios, 4)
    scenarios, states, actions, _ = kernel.shape
    rewards = np.asarray(reward, dtype=np.float64)
    if rewards.shape == (states, actions):
        rewards = np.broadcast_to(rewards, (scenarios, states, actions))
    if (
        rewards.shape != (scenarios, states, actions)
        or np.any(~np.isfinite(rewards))
        or not 0.0 <= discount < 1.0
        or not isfinite(tolerance)
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("scenario-robust MDP inputs are invalid")
    values = np.zeros(states)
    q_values = np.zeros((states, actions))
    worst = np.zeros((states, actions), dtype=np.int64)
    residual = np.inf
    for iteration in range(1, max_iterations + 1):
        scenario_values = rewards + discount * np.einsum(
            "ksan,n->ksa", kernel, values
        )
        worst = np.argmin(scenario_values, axis=0)
        q_values = np.min(scenario_values, axis=0)
        updated = np.max(q_values, axis=1)
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        if residual <= tolerance:
            return ScenarioRobustMDPResult(
                values,
                q_values.copy(),
                tuple(int(value) for value in np.argmax(q_values, axis=1)),
                worst.copy(),
                iteration,
                True,
                residual,
            )
    return ScenarioRobustMDPResult(
        values,
        q_values.copy(),
        tuple(int(value) for value in np.argmax(q_values, axis=1)),
        worst.copy(),
        max_iterations,
        False,
        residual,
    )


@dataclass(frozen=True)
class RobustViabilityResult:
    viable_states: tuple[int, ...]
    viable_actions: tuple[tuple[int, ...], ...]
    worst_case_retention: np.ndarray
    iterations: int
    minimum_probability: float


def robust_viability_kernel(
    transition_scenarios: Sequence,
    safe_states: Sequence[int] | Sequence[bool],
    *,
    minimum_probability: float = 1.0,
) -> RobustViabilityResult:
    """Find states with one action that is viable in every transition scenario."""

    kernel = _transition_kernel(transition_scenarios, 4)
    _, states, actions, _ = kernel.shape
    safe = _state_mask(states, safe_states)
    if not np.any(safe) or not 0.0 <= minimum_probability <= 1.0:
        raise ValueError("robust viability inputs are invalid")
    viable = safe.copy()
    worst_retention = np.zeros((states, actions))
    for iteration in range(1, states + 2):
        retention = kernel[:, :, :, viable].sum(axis=3)
        worst_retention = np.min(retention, axis=0)
        next_viable = viable.copy()
        next_viable[viable] = (
            np.max(worst_retention[viable], axis=1)
            >= minimum_probability - 1e-12
        )
        if np.array_equal(next_viable, viable):
            break
        viable = next_viable
    viable_actions = []
    for state in range(states):
        if not viable[state]:
            viable_actions.append(())
            continue
        viable_actions.append(
            tuple(
                int(action)
                for action in np.flatnonzero(
                    worst_retention[state] >= minimum_probability - 1e-12
                )
            )
        )
    return RobustViabilityResult(
        tuple(int(value) for value in np.flatnonzero(viable)),
        tuple(viable_actions),
        worst_retention,
        iteration,
        minimum_probability,
    )


@dataclass(frozen=True)
class CUSUMEvent:
    alarm: bool
    direction: str | None
    positive_statistic: float
    negative_statistic: float
    observations: int


class TwoSidedCUSUMDetector:
    """Two-sided CUSUM detector for a metric with a calibrated baseline mean."""

    def __init__(
        self,
        baseline_mean: float,
        *,
        allowance: float,
        threshold: float,
        minimum_observations: int = 1,
        reset_after_alarm: bool = True,
    ) -> None:
        if (
            not isfinite(baseline_mean)
            or not isfinite(allowance)
            or allowance < 0.0
            or not isfinite(threshold)
            or threshold <= 0.0
            or minimum_observations <= 0
        ):
            raise ValueError("CUSUM settings are invalid")
        self.baseline_mean = float(baseline_mean)
        self.allowance = float(allowance)
        self.threshold = float(threshold)
        self.minimum_observations = minimum_observations
        self.reset_after_alarm = reset_after_alarm
        self.observations = 0
        self.positive = 0.0
        self.negative = 0.0

    def reset(self) -> None:
        self.observations = 0
        self.positive = 0.0
        self.negative = 0.0

    def update(self, value: float) -> CUSUMEvent:
        if not isfinite(value):
            raise ValueError("CUSUM observation must be finite")
        self.observations += 1
        self.positive = max(
            0.0, self.positive + value - self.baseline_mean - self.allowance
        )
        self.negative = max(
            0.0, self.negative + self.baseline_mean - value - self.allowance
        )
        direction = None
        if self.observations >= self.minimum_observations:
            if self.positive >= self.threshold:
                direction = "up"
            elif self.negative >= self.threshold:
                direction = "down"
        event = CUSUMEvent(
            direction is not None,
            direction,
            self.positive,
            self.negative,
            self.observations,
        )
        if event.alarm and self.reset_after_alarm:
            self.reset()
        return event


@dataclass(frozen=True)
class PolicySelectionEvent:
    active_policy: int
    changed: bool
    probabilities: np.ndarray
    observations: int


class FixedSharePolicySelector:
    """Track non-stationary policy experts with fixed-share exponential weights."""

    def __init__(
        self,
        policy_count: int,
        *,
        learning_rate: float,
        share: float = 0.02,
        switch_margin: float = 0.05,
        minimum_dwell: int = 1,
        initial_policy: int = 0,
    ) -> None:
        if (
            policy_count <= 0
            or not isfinite(learning_rate)
            or learning_rate <= 0.0
            or not 0.0 <= share <= 1.0
            or not 0.0 <= switch_margin <= 1.0
            or minimum_dwell <= 0
            or not 0 <= initial_policy < policy_count
        ):
            raise ValueError("fixed-share selector settings are invalid")
        self.policy_count = policy_count
        self.learning_rate = float(learning_rate)
        self.share = float(share)
        self.switch_margin = float(switch_margin)
        self.minimum_dwell = minimum_dwell
        self.active_policy = initial_policy
        self.probabilities = np.full(policy_count, 1.0 / policy_count)
        self.observations = 0
        self._dwell = 0

    def update(self, losses: Sequence[float]) -> PolicySelectionEvent:
        values = np.asarray(losses, dtype=np.float64)
        if values.shape != (self.policy_count,) or np.any(~np.isfinite(values)):
            raise ValueError("one finite loss per policy is required")
        shifted = values - np.min(values)
        weights = self.probabilities * np.exp(-self.learning_rate * shifted)
        if not np.any(weights > 0.0):
            weights = np.ones(self.policy_count)
        weights /= weights.sum()
        self.probabilities = (
            (1.0 - self.share) * weights + self.share / self.policy_count
        )
        self.observations += 1
        self._dwell += 1
        candidate = int(np.argmax(self.probabilities))
        changed = (
            candidate != self.active_policy
            and self._dwell >= self.minimum_dwell
            and self.probabilities[candidate]
            >= self.probabilities[self.active_policy] + self.switch_margin
        )
        if changed:
            self.active_policy = candidate
            self._dwell = 0
        return PolicySelectionEvent(
            self.active_policy,
            changed,
            self.probabilities.copy(),
            self.observations,
        )


@dataclass(frozen=True)
class PerronFrobeniusResult:
    spectral_radius: float
    right_vector: np.ndarray
    left_vector: np.ndarray
    right_residual: float
    left_residual: float
    irreducible: bool


def perron_frobenius_analysis(matrix: Sequence[Sequence[float]]) -> PerronFrobeniusResult:
    """Return normalized Perron vectors and residuals for a non-negative matrix."""

    values = np.asarray(matrix, dtype=np.float64)
    if (
        values.ndim != 2
        or values.shape[0] == 0
        or values.shape[0] != values.shape[1]
        or np.any(~np.isfinite(values))
        or np.any(values < 0.0)
    ):
        raise ValueError("Perron-Frobenius matrix must be finite, square, and non-negative")
    eigenvalues, right_vectors = np.linalg.eig(values)
    radius = float(np.max(np.abs(eigenvalues)))
    if radius <= 1e-15:
        uniform = np.full(values.shape[0], 1.0 / values.shape[0])
        return PerronFrobeniusResult(
            0.0,
            uniform.copy(),
            uniform.copy(),
            0.0,
            0.0,
            values.shape[0] == 1,
        )
    index = int(np.argmin(np.abs(eigenvalues - radius)))
    right = np.abs(np.real_if_close(right_vectors[:, index]).real)
    left_values, left_vectors = np.linalg.eig(values.T)
    left_index = int(np.argmin(np.abs(left_values - radius)))
    left = np.abs(np.real_if_close(left_vectors[:, left_index]).real)
    if right.sum() <= 1e-15 or left.sum() <= 1e-15:
        raise RuntimeError("failed to recover non-negative Perron vectors")
    right /= right.sum()
    left /= left.sum()
    irreducible = bool(
        connected_components(
            values > 0.0, directed=True, connection="strong", return_labels=False
        )
        == 1
    )
    return PerronFrobeniusResult(
        radius,
        right,
        left,
        float(np.linalg.norm(values @ right - radius * right)),
        float(np.linalg.norm(left @ values - radius * left)),
        irreducible,
    )


@dataclass(frozen=True)
class LeontiefResult:
    gross_output: np.ndarray
    leontief_inverse: np.ndarray
    spectral_radius: float
    productive: bool
    balance_residual: float
    labor_values: np.ndarray | None
    augmented_spectral_radius: float | None
    maximum_profit_rate: float | None


def leontief_input_output_analysis(
    technical_coefficients: Sequence[Sequence[float]],
    final_demand: Sequence[float],
    *,
    direct_labor: Sequence[float] | None = None,
    real_wage_bundle: Sequence[float] | None = None,
) -> LeontiefResult:
    """Analyze x = Ax + d and an optional wage-augmented Sraffian system."""

    coefficients = np.asarray(technical_coefficients, dtype=np.float64)
    demand = np.asarray(final_demand, dtype=np.float64)
    if (
        coefficients.ndim != 2
        or coefficients.shape[0] == 0
        or coefficients.shape[0] != coefficients.shape[1]
        or demand.shape != (coefficients.shape[0],)
        or np.any(~np.isfinite(coefficients))
        or np.any(~np.isfinite(demand))
        or np.any(coefficients < 0.0)
        or np.any(demand < 0.0)
    ):
        raise ValueError("Leontief inputs are invalid")
    pf = perron_frobenius_analysis(coefficients)
    identity = np.eye(coefficients.shape[0])
    productive = pf.spectral_radius < 1.0 - 1e-12
    if not productive:
        raise ValueError("technical coefficients are not productive: spectral radius >= 1")
    inverse = np.linalg.inv(identity - coefficients)
    output = inverse @ demand
    labor_values = None
    labor = None
    if direct_labor is not None:
        labor = np.asarray(direct_labor, dtype=np.float64)
        if (
            labor.shape != demand.shape
            or np.any(~np.isfinite(labor))
            or np.any(labor < 0.0)
        ):
            raise ValueError("direct labor coefficients are invalid")
        labor_values = labor @ inverse
    augmented_radius = None
    maximum_profit_rate = None
    if real_wage_bundle is not None:
        wage = np.asarray(real_wage_bundle, dtype=np.float64)
        if (
            labor is None
            or wage.shape != demand.shape
            or np.any(~np.isfinite(wage))
            or np.any(wage < 0.0)
        ):
            raise ValueError("a valid direct-labor vector is required with wages")
        augmented = coefficients + np.outer(wage, labor)
        augmented_radius = perron_frobenius_analysis(augmented).spectral_radius
        maximum_profit_rate = (
            np.inf if augmented_radius <= 1e-15 else 1.0 / augmented_radius - 1.0
        )
    return LeontiefResult(
        output,
        inverse,
        pf.spectral_radius,
        productive,
        float(np.max(np.abs(output - coefficients @ output - demand))),
        labor_values,
        augmented_radius,
        maximum_profit_rate,
    )


@dataclass(frozen=True)
class LaggedReplayDesign:
    predictors: np.ndarray
    targets: np.ndarray
    feature_map: tuple[tuple[int, int], ...]
    episode_indices: np.ndarray
    time_indices: np.ndarray
    maximum_lag: int


def lagged_replay_design(
    trajectories: Sequence[Sequence[Sequence[float]]],
    *,
    maximum_lag: int,
) -> LaggedReplayDesign:
    """Build lagged samples without allowing rows to cross episode boundaries."""

    episodes = tuple(np.asarray(value, dtype=np.float64) for value in trajectories)
    if (
        not episodes
        or maximum_lag <= 0
        or any(value.ndim != 2 or np.any(~np.isfinite(value)) for value in episodes)
        or len({value.shape[1] for value in episodes}) != 1
        or any(value.shape[0] <= maximum_lag for value in episodes)
    ):
        raise ValueError("lagged replay inputs are invalid")
    features = episodes[0].shape[1]
    rows = []
    targets = []
    episode_indices = []
    time_indices = []
    for episode_index, episode in enumerate(episodes):
        for time_index in range(maximum_lag, episode.shape[0]):
            rows.append(
                np.concatenate(
                    [episode[time_index - lag] for lag in range(1, maximum_lag + 1)]
                )
            )
            targets.append(episode[time_index])
            episode_indices.append(episode_index)
            time_indices.append(time_index)
    feature_map = tuple(
        (lag, feature)
        for lag in range(1, maximum_lag + 1)
        for feature in range(features)
    )
    return LaggedReplayDesign(
        np.asarray(rows),
        np.asarray(targets),
        feature_map,
        np.asarray(episode_indices, dtype=np.int64),
        np.asarray(time_indices, dtype=np.int64),
        maximum_lag,
    )


@dataclass(frozen=True)
class LaggedCausalGraphResult:
    adjacency: np.ndarray
    coefficients: np.ndarray
    p_values: np.ndarray
    condition_number: float
    observations: int


def lagged_conditional_independence_graph(
    design: LaggedReplayDesign,
    *,
    significance: float = 0.01,
    minimum_effect: float = 0.0,
) -> LaggedCausalGraphResult:
    """Screen lagged edges by joint linear regression and coefficient t-tests."""

    predictors = np.asarray(design.predictors, dtype=np.float64)
    targets = np.asarray(design.targets, dtype=np.float64)
    if (
        predictors.ndim != 2
        or targets.ndim != 2
        or predictors.shape[0] != targets.shape[0]
        or predictors.shape[1] != len(design.feature_map)
        or predictors.shape[0] <= predictors.shape[1] + 1
        or np.any(~np.isfinite(predictors))
        or np.any(~np.isfinite(targets))
        or not 0.0 < significance < 1.0
        or not isfinite(minimum_effect)
        or minimum_effect < 0.0
    ):
        raise ValueError("lagged conditional-independence inputs are invalid")
    observations = predictors.shape[0]
    matrix = np.c_[np.ones(observations), predictors]
    coefficients = np.linalg.lstsq(matrix, targets, rcond=None)[0]
    residual = targets - matrix @ coefficients
    degrees = observations - matrix.shape[1]
    covariance_base = np.linalg.pinv(matrix.T @ matrix)
    residual_variance = np.sum(residual**2, axis=0) / degrees
    standard_errors = np.sqrt(
        np.maximum(0.0, covariance_base.diagonal()[:, None] * residual_variance)
    )
    statistics = np.divide(
        coefficients,
        standard_errors,
        out=np.zeros_like(coefficients),
        where=standard_errors > 1e-15,
    )
    p_values = 2.0 * t.sf(np.abs(statistics), degrees)
    edge_coefficients = coefficients[1:]
    edge_p_values = p_values[1:]
    features = targets.shape[1]
    reshaped_coefficients = edge_coefficients.reshape(
        design.maximum_lag, features, features
    )
    reshaped_p_values = edge_p_values.reshape(
        design.maximum_lag, features, features
    )
    adjacency = (reshaped_p_values <= significance) & (
        np.abs(reshaped_coefficients) >= minimum_effect
    )
    return LaggedCausalGraphResult(
        adjacency,
        reshaped_coefficients,
        reshaped_p_values,
        float(np.linalg.cond(matrix)),
        observations,
    )


@dataclass(frozen=True)
class CrossEnvironmentTransferResult:
    held_out_rmse: np.ndarray
    coefficients: np.ndarray
    worst_environment_rmse: float
    coefficient_spread: float


def cross_environment_transfer_diagnostics(
    environments: Sequence[Sequence[Sequence[float]]],
    target: int,
    predictors: Sequence[int],
) -> CrossEnvironmentTransferResult:
    """Evaluate a proposed invariant predictor set by leave-one-environment-out fits."""

    samples = tuple(np.asarray(value, dtype=np.float64) for value in environments)
    selected = tuple(dict.fromkeys(int(value) for value in predictors))
    if (
        len(samples) < 2
        or any(value.ndim != 2 or value.shape[0] < 2 for value in samples)
        or len({value.shape[1] for value in samples}) != 1
        or any(np.any(~np.isfinite(value)) for value in samples)
        or not 0 <= target < samples[0].shape[1]
        or target in selected
        or any(value < 0 or value >= samples[0].shape[1] for value in selected)
    ):
        raise ValueError("cross-environment transfer inputs are invalid")
    coefficients = []
    errors = []
    for held_out, test in enumerate(samples):
        training = np.vstack(
            [value for index, value in enumerate(samples) if index != held_out]
        )
        train_design = (
            np.c_[np.ones(training.shape[0]), training[:, selected]]
            if selected
            else np.ones((training.shape[0], 1))
        )
        coefficient = np.linalg.lstsq(
            train_design, training[:, target], rcond=None
        )[0]
        test_design = (
            np.c_[np.ones(test.shape[0]), test[:, selected]]
            if selected
            else np.ones((test.shape[0], 1))
        )
        prediction = test_design @ coefficient
        coefficients.append(coefficient)
        errors.append(float(np.sqrt(np.mean((test[:, target] - prediction) ** 2))))
    coefficient_array = np.asarray(coefficients)
    center = coefficient_array.mean(axis=0)
    spread = float(np.max(np.linalg.norm(coefficient_array - center, axis=1)))
    error_array = np.asarray(errors)
    return CrossEnvironmentTransferResult(
        error_array,
        coefficient_array,
        float(np.max(error_array)),
        spread,
    )
