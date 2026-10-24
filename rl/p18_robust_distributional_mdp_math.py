"""P18 robust, distributional, and risk-sensitive finite MDP algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog, minimize
from scipy.special import logsumexp


@dataclass(frozen=True)
class WorstCaseExpectationResult:
    value: float
    distribution: np.ndarray
    ambiguity_measure: float
    ambiguity_type: str


def worst_case_discrete_expectation(
    nominal_distribution: Sequence[float],
    values: Sequence[float],
    radius: float,
    *,
    ambiguity_type: str = "tv",
    ground_cost: Sequence[Sequence[float]] | None = None,
) -> WorstCaseExpectationResult:
    """Minimize an expectation over TV, KL, or Wasserstein ambiguity balls."""

    nominal = np.asarray(nominal_distribution, dtype=np.float64)
    outcome_values = np.asarray(values, dtype=np.float64)
    if (
        nominal.ndim != 1
        or nominal.size == 0
        or outcome_values.shape != nominal.shape
        or np.any(~np.isfinite(nominal))
        or np.any(~np.isfinite(outcome_values))
        or np.any(nominal < 0.0)
        or not np.isclose(nominal.sum(), 1.0)
        or not isfinite(radius)
        or radius < 0.0
        or ambiguity_type not in {"tv", "kl", "wasserstein"}
    ):
        raise ValueError("worst-case expectation inputs are invalid")
    size = nominal.size
    if radius == 0.0:
        return WorstCaseExpectationResult(
            float(nominal @ outcome_values), nominal.copy(), 0.0, ambiguity_type
        )
    if ambiguity_type == "tv":
        # Variables q and u enforce |q-p| <= u and sum(u) <= 2 radius.
        objective = np.r_[outcome_values, np.zeros(size)]
        inequality = []
        bound = []
        for index in range(size):
            row = np.zeros(2 * size)
            row[index] = 1.0
            row[size + index] = -1.0
            inequality.append(row)
            bound.append(nominal[index])
            row = np.zeros(2 * size)
            row[index] = -1.0
            row[size + index] = -1.0
            inequality.append(row)
            bound.append(-nominal[index])
        inequality.append(np.r_[np.zeros(size), np.ones(size)])
        bound.append(2.0 * radius)
        solved = linprog(
            objective,
            A_ub=np.asarray(inequality),
            b_ub=np.asarray(bound),
            A_eq=np.r_[np.ones(size), np.zeros(size)][None, :],
            b_eq=[1.0],
            bounds=[(0.0, 1.0)] * size + [(0.0, None)] * size,
            method="highs",
        )
        if not solved.success or solved.x is None:
            raise RuntimeError(f"TV ambiguity solve failed: {solved.message}")
        distribution = np.maximum(solved.x[:size], 0.0)
        distribution /= distribution.sum()
        measure = 0.5 * float(np.sum(np.abs(distribution - nominal)))
    elif ambiguity_type == "wasserstein":
        if ground_cost is None:
            raise ValueError("Wasserstein ambiguity requires a ground-cost matrix")
        cost = np.asarray(ground_cost, dtype=np.float64)
        if (
            cost.shape != (size, size)
            or np.any(~np.isfinite(cost))
            or np.any(cost < 0.0)
            or not np.allclose(np.diag(cost), 0.0)
        ):
            raise ValueError("Wasserstein ground cost is invalid")
        # pi[i,j] moves nominal mass i to adversarial outcome j.
        objective = np.tile(outcome_values, size)
        row_equalities = np.zeros((size, size * size))
        for origin in range(size):
            row_equalities[origin, origin * size : (origin + 1) * size] = 1.0
        solved = linprog(
            objective,
            A_ub=cost.ravel()[None, :],
            b_ub=[radius],
            A_eq=row_equalities,
            b_eq=nominal,
            bounds=[(0.0, None)] * (size * size),
            method="highs",
        )
        if not solved.success or solved.x is None:
            raise RuntimeError(f"Wasserstein ambiguity solve failed: {solved.message}")
        transport = solved.x.reshape(size, size)
        distribution = transport.sum(axis=0)
        measure = float(np.sum(transport * cost))
    else:
        support = nominal > 0.0
        supported_nominal = nominal[support]
        supported_values = outcome_values[support]

        def divergence(probability: np.ndarray) -> float:
            positive = probability > 0.0
            return float(
                np.sum(
                    probability[positive]
                    * np.log(probability[positive] / supported_nominal[positive])
                )
            )

        solved = minimize(
            lambda probability: float(probability @ supported_values),
            supported_nominal,
            method="SLSQP",
            bounds=[(0.0, 1.0)] * supported_nominal.size,
            constraints=(
                {"type": "eq", "fun": lambda probability: probability.sum() - 1.0},
                {"type": "ineq", "fun": lambda probability: radius - divergence(probability)},
            ),
            options={"ftol": 1e-12, "maxiter": 1_000},
        )
        if not solved.success:
            raise RuntimeError(f"KL ambiguity solve failed: {solved.message}")
        distribution = np.zeros(size)
        distribution[support] = np.maximum(solved.x, 0.0)
        distribution /= distribution.sum()
        measure = divergence(distribution[support])
    return WorstCaseExpectationResult(
        float(distribution @ outcome_values), distribution, measure, ambiguity_type
    )


@dataclass(frozen=True)
class RobustMDPResult:
    values: np.ndarray
    q_values: np.ndarray
    policy: tuple[int, ...]
    worst_case_transitions: np.ndarray
    iterations: int
    converged: bool
    bellman_residual: float
    ambiguity_type: str


def robust_value_iteration(
    nominal_transition: Sequence,
    reward: Sequence[Sequence[float]],
    ambiguity_radius: float | Sequence,
    *,
    discount: float = 0.95,
    ambiguity_type: str = "tv",
    ground_cost: Sequence[Sequence[float]] | None = None,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> RobustMDPResult:
    """Rectangular robust value iteration with independent state-action balls."""

    transition = np.asarray(nominal_transition, dtype=np.float64)
    rewards = np.asarray(reward, dtype=np.float64)
    if transition.ndim != 3:
        raise ValueError("robust MDP transition must be three-dimensional")
    states, actions, next_states = transition.shape
    radius = np.asarray(ambiguity_radius, dtype=np.float64)
    if radius.ndim == 0:
        radius = np.full((states, actions), float(radius))
    if (
        next_states != states
        or rewards.shape != (states, actions)
        or radius.shape != (states, actions)
        or np.any(~np.isfinite(transition))
        or np.any(~np.isfinite(rewards))
        or np.any(~np.isfinite(radius))
        or np.any(transition < 0.0)
        or np.any(radius < 0.0)
        or not np.allclose(transition.sum(axis=2), 1.0)
        or not 0.0 <= discount < 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("robust MDP inputs are invalid")
    values = np.zeros(states)
    q_values = np.zeros((states, actions))
    worst = transition.copy()
    residual = np.inf
    for iteration in range(1, max_iterations + 1):
        for state in range(states):
            for action in range(actions):
                result = worst_case_discrete_expectation(
                    transition[state, action],
                    values,
                    float(radius[state, action]),
                    ambiguity_type=ambiguity_type,
                    ground_cost=ground_cost,
                )
                worst[state, action] = result.distribution
                q_values[state, action] = rewards[state, action] + discount * result.value
        updated = np.max(q_values, axis=1)
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        if residual <= tolerance:
            return RobustMDPResult(
                values,
                q_values.copy(),
                tuple(int(value) for value in np.argmax(q_values, axis=1)),
                worst.copy(),
                iteration,
                True,
                residual,
                ambiguity_type,
            )
    return RobustMDPResult(
        values,
        q_values.copy(),
        tuple(int(value) for value in np.argmax(q_values, axis=1)),
        worst.copy(),
        max_iterations,
        False,
        residual,
        ambiguity_type,
    )


def categorical_bellman_projection(
    next_distribution: Sequence[float],
    support: Sequence[float],
    *,
    reward: float,
    discount: float,
    terminal: bool = False,
) -> np.ndarray:
    """Project one C51 Bellman target onto an equally spaced fixed support."""

    probability = np.asarray(next_distribution, dtype=np.float64)
    atoms = np.asarray(support, dtype=np.float64)
    if (
        probability.ndim != 1
        or atoms.shape != probability.shape
        or atoms.size < 2
        or np.any(~np.isfinite(probability))
        or np.any(~np.isfinite(atoms))
        or np.any(probability < 0.0)
        or not np.isclose(probability.sum(), 1.0)
        or not np.all(np.diff(atoms) > 0.0)
        or not np.allclose(np.diff(atoms), atoms[1] - atoms[0])
        or not isfinite(reward)
        or not 0.0 <= discount <= 1.0
    ):
        raise ValueError("categorical Bellman projection inputs are invalid")
    transformed = np.clip(
        reward + (0.0 if terminal else discount) * atoms, atoms[0], atoms[-1]
    )
    positions = (transformed - atoms[0]) / (atoms[1] - atoms[0])
    lower = np.floor(positions).astype(int)
    upper = np.ceil(positions).astype(int)
    projected = np.zeros_like(probability)
    for index, mass in enumerate(probability):
        if lower[index] == upper[index]:
            projected[lower[index]] += mass
        else:
            projected[lower[index]] += mass * (upper[index] - positions[index])
            projected[upper[index]] += mass * (positions[index] - lower[index])
    return projected


def quantile_bellman_targets(
    next_quantiles: Sequence[float],
    *,
    reward: float,
    discount: float,
    terminal: bool = False,
) -> np.ndarray:
    quantiles = np.asarray(next_quantiles, dtype=np.float64)
    if (
        quantiles.ndim != 1
        or quantiles.size == 0
        or np.any(~np.isfinite(quantiles))
        or not isfinite(reward)
        or not 0.0 <= discount <= 1.0
    ):
        raise ValueError("quantile Bellman target inputs are invalid")
    return reward + (0.0 if terminal else discount) * quantiles


def quantile_huber_loss(
    predicted_quantiles: Sequence[float],
    target_samples: Sequence[float],
    *,
    kappa: float = 1.0,
) -> float:
    """Pairwise quantile Huber loss used by quantile-regression RL."""

    predicted = np.asarray(predicted_quantiles, dtype=np.float64)
    targets = np.asarray(target_samples, dtype=np.float64)
    if (
        predicted.ndim != 1
        or targets.ndim != 1
        or predicted.size == 0
        or targets.size == 0
        or np.any(~np.isfinite(predicted))
        or np.any(~np.isfinite(targets))
        or not isfinite(kappa)
        or kappa <= 0.0
    ):
        raise ValueError("quantile Huber inputs are invalid")
    errors = targets[None, :] - predicted[:, None]
    absolute = np.abs(errors)
    huber = np.where(
        absolute <= kappa,
        0.5 * errors**2,
        kappa * (absolute - 0.5 * kappa),
    )
    quantile_levels = (np.arange(predicted.size) + 0.5) / predicted.size
    weights = np.abs(quantile_levels[:, None] - (errors < 0.0))
    return float(np.mean(weights * huber / kappa))


@dataclass(frozen=True)
class EntropicMDPResult:
    values: np.ndarray
    policy: tuple[int, ...]
    iterations: int
    converged: bool
    bellman_residual: float


def entropic_risk_value_iteration(
    transition: Sequence,
    reward: Sequence[Sequence[float]],
    *,
    risk_parameter: float,
    discount: float = 0.95,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> EntropicMDPResult:
    """Risk-sensitive Bellman iteration using exponential certainty equivalents."""

    kernel = np.asarray(transition, dtype=np.float64)
    rewards = np.asarray(reward, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("entropic MDP transition must be three-dimensional")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or rewards.shape != (states, actions)
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(rewards))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not isfinite(risk_parameter)
        or risk_parameter == 0.0
        or not 0.0 <= discount < 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("entropic MDP inputs are invalid")
    values = np.zeros(states)
    residual = np.inf
    q_values = np.zeros((states, actions))
    for iteration in range(1, max_iterations + 1):
        for state in range(states):
            for action in range(actions):
                probabilities = kernel[state, action]
                positive = probabilities > 0.0
                log_expectation = logsumexp(
                    np.log(probabilities[positive])
                    + risk_parameter * discount * values[positive]
                )
                q_values[state, action] = (
                    rewards[state, action] + log_expectation / risk_parameter
                )
        updated = np.max(q_values, axis=1)
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        if residual <= tolerance:
            return EntropicMDPResult(
                values,
                tuple(int(value) for value in np.argmax(q_values, axis=1)),
                iteration,
                True,
                residual,
            )
    return EntropicMDPResult(
        values,
        tuple(int(value) for value in np.argmax(q_values, axis=1)),
        max_iterations,
        False,
        residual,
    )


def discrete_cvar(
    values: Sequence[float],
    probabilities: Sequence[float],
    *,
    tail_probability: float,
    tail: str = "lower",
) -> float:
    """Exact finite lower- or upper-tail CVaR, including a fractional atom."""

    outcomes = np.asarray(values, dtype=np.float64)
    weights = np.asarray(probabilities, dtype=np.float64)
    if (
        outcomes.ndim != 1
        or outcomes.size == 0
        or weights.shape != outcomes.shape
        or np.any(~np.isfinite(outcomes))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not np.isclose(weights.sum(), 1.0)
        or not 0.0 < tail_probability <= 1.0
        or tail not in {"lower", "upper"}
    ):
        raise ValueError("discrete CVaR inputs are invalid")
    order = np.argsort(outcomes)
    if tail == "upper":
        order = order[::-1]
    remaining = tail_probability
    total = 0.0
    for index in order:
        mass = min(remaining, weights[index])
        total += mass * outcomes[index]
        remaining -= mass
        if remaining <= 1e-15:
            break
    return total / tail_probability


@dataclass(frozen=True)
class ReachAvoidResult:
    values: np.ndarray
    policy: np.ndarray
    horizon: int


def stochastic_reach_avoid(
    transition: Sequence,
    target_states: Sequence[int],
    avoid_states: Sequence[int],
    *,
    horizon: int,
) -> ReachAvoidResult:
    """Maximize target-before-avoid probability over a finite horizon."""

    kernel = np.asarray(transition, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("reach-avoid transition must be three-dimensional")
    states, actions, next_states = kernel.shape
    target = frozenset(int(value) for value in target_states)
    avoid = frozenset(int(value) for value in avoid_states)
    if (
        next_states != states
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not target
        or target & avoid
        or any(value < 0 or value >= states for value in target | avoid)
        or horizon < 0
    ):
        raise ValueError("reach-avoid inputs are invalid")
    values = np.zeros((horizon + 1, states))
    values[:, list(target)] = 1.0
    values[:, list(avoid)] = 0.0
    policy = np.zeros((horizon, states), dtype=np.int64)
    ordinary = [state for state in range(states) if state not in target | avoid]
    for remaining in range(1, horizon + 1):
        q_values = np.einsum("san,n->sa", kernel, values[remaining - 1])
        if ordinary:
            values[remaining, ordinary] = np.max(q_values[ordinary], axis=1)
            policy[remaining - 1, ordinary] = np.argmax(q_values[ordinary], axis=1)
    return ReachAvoidResult(values, policy, horizon)


@dataclass(frozen=True)
class RobustOccupancyResult:
    occupancy: np.ndarray
    policy: np.ndarray
    guaranteed_return: float
    scenario_returns: np.ndarray
    flow_residual: float


def robust_reward_occupancy_lp(
    transition: Sequence,
    initial_distribution: Sequence[float],
    reward_scenarios: Sequence,
    *,
    discount: float = 0.95,
) -> RobustOccupancyResult:
    """Maximize worst reward-scenario return with discounted occupancy measures."""

    kernel = np.asarray(transition, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    rewards = np.asarray(reward_scenarios, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("occupancy transition must be three-dimensional")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or initial.shape != (states,)
        or rewards.ndim != 3
        or rewards.shape[1:] != (states, actions)
        or rewards.shape[0] == 0
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(initial))
        or np.any(~np.isfinite(rewards))
        or np.any(kernel < 0.0)
        or np.any(initial < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not np.isclose(initial.sum(), 1.0)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("robust occupancy inputs are invalid")
    occupancy_variables = states * actions
    objective = np.r_[np.zeros(occupancy_variables), -1.0]
    inequality = np.hstack(
        (-rewards.reshape(rewards.shape[0], occupancy_variables), np.ones((rewards.shape[0], 1)))
    )
    flow = np.zeros((states, occupancy_variables + 1))
    for state in range(states):
        for action in range(actions):
            flow[state, state * actions + action] += 1.0
        for source in range(states):
            for action in range(actions):
                flow[state, source * actions + action] -= (
                    discount * kernel[source, action, state]
                )
    solved = linprog(
        objective,
        A_ub=inequality,
        b_ub=np.zeros(rewards.shape[0]),
        A_eq=flow,
        b_eq=initial,
        bounds=[(0.0, None)] * occupancy_variables + [(None, None)],
        method="highs",
    )
    if not solved.success or solved.x is None:
        raise RuntimeError(f"robust occupancy solve failed: {solved.message}")
    occupancy = solved.x[:occupancy_variables].reshape(states, actions)
    state_mass = occupancy.sum(axis=1)
    policy = np.divide(
        occupancy,
        state_mass[:, None],
        out=np.full_like(occupancy, 1.0 / actions),
        where=state_mass[:, None] > 1e-15,
    )
    scenario_returns = np.einsum("ksa,sa->k", rewards, occupancy)
    return RobustOccupancyResult(
        occupancy,
        policy,
        float(solved.x[-1]),
        scenario_returns,
        float(np.max(np.abs(flow @ solved.x - initial), initial=0.0)),
    )


@dataclass(frozen=True)
class PolicySwitchEvent:
    active_policy: int
    changed: bool
    statistic: float
    observations: int


class PageHinkleyPolicySwitcher:
    """One-sided Page-Hinkley loss-drift detector with cyclic policy switching."""

    def __init__(
        self,
        policy_count: int,
        *,
        threshold: float,
        tolerance: float = 0.0,
        minimum_observations: int = 5,
    ) -> None:
        if (
            policy_count <= 0
            or not isfinite(threshold)
            or threshold <= 0.0
            or not isfinite(tolerance)
            or tolerance < 0.0
            or minimum_observations <= 0
        ):
            raise ValueError("Page-Hinkley switcher settings are invalid")
        self.policy_count = policy_count
        self.threshold = float(threshold)
        self.tolerance = float(tolerance)
        self.minimum_observations = minimum_observations
        self.active_policy = 0
        self._reset_statistics()

    def _reset_statistics(self) -> None:
        self.observations = 0
        self.mean = 0.0
        self.cumulative = 0.0
        self.minimum_cumulative = 0.0

    def update(self, loss: float) -> PolicySwitchEvent:
        if not isfinite(loss):
            raise ValueError("Page-Hinkley loss must be finite")
        self.observations += 1
        self.mean += (loss - self.mean) / self.observations
        self.cumulative += loss - self.mean - self.tolerance
        self.minimum_cumulative = min(self.minimum_cumulative, self.cumulative)
        statistic = self.cumulative - self.minimum_cumulative
        changed = (
            self.observations >= self.minimum_observations
            and statistic > self.threshold
        )
        observations = self.observations
        if changed:
            self.active_policy = (self.active_policy + 1) % self.policy_count
            self._reset_statistics()
        return PolicySwitchEvent(
            self.active_policy, changed, float(statistic), observations
        )
