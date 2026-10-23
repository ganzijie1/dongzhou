"""P15 inverse optimization, inverse MDP, and inverse Stackelberg models.

The routines in this module only infer parameters from explicitly supplied
observations.  They expose residuals, slacks, and rank diagnostics because an
inverse model can be feasible without being uniquely identifiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog, minimize
from scipy.special import logsumexp


@dataclass(frozen=True)
class InverseLPObservation:
    """One observed optimum for ``min c @ x`` subject to ``A @ x <= b``."""

    a_ub: np.ndarray
    b_ub: np.ndarray
    decision: np.ndarray


@dataclass(frozen=True)
class InverseLPResult:
    cost: np.ndarray
    duals: tuple[np.ndarray, ...]
    objective_change: float
    primal_violation: float
    stationarity_residual: float
    complementarity_residual: float
    active_sets: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class InverseLinearRHSResult:
    bounds: np.ndarray
    adjustments: np.ndarray
    maximum_primal_violation: float
    active_residual: float


def inverse_linear_rhs(
    constraint_normals: Sequence[Sequence[float]],
    observed_decisions: Sequence[Sequence[float]],
    reference_bounds: Sequence[float],
    *,
    active_constraints: Sequence[Sequence[int]] | None = None,
    tolerance: float = 1e-8,
) -> InverseLinearRHSResult:
    """Infer ``b`` in ``A @ x <= b`` when the constraint normals are known.

    Without declared active constraints, the closest feasible right-hand side
    is the componentwise projection of the reference above all observations.
    Declared active rows are pinned to their observed boundary values.
    """

    normals = np.asarray(constraint_normals, dtype=np.float64)
    decisions = np.asarray(observed_decisions, dtype=np.float64)
    reference = np.asarray(reference_bounds, dtype=np.float64)
    if (
        normals.ndim != 2
        or min(normals.shape) == 0
        or decisions.ndim != 2
        or decisions.shape[0] == 0
        or decisions.shape[1] != normals.shape[1]
        or reference.shape != (normals.shape[0],)
        or np.any(~np.isfinite(normals))
        or np.any(~np.isfinite(decisions))
        or np.any(~np.isfinite(reference))
        or tolerance < 0.0
    ):
        raise ValueError("inverse linear RHS inputs are invalid")
    observed_left = decisions @ normals.T
    lower_bounds = np.max(observed_left, axis=0)
    inferred = np.maximum(reference, lower_bounds)
    active_values: dict[int, float] = {}
    if active_constraints is not None:
        if len(active_constraints) != decisions.shape[0]:
            raise ValueError("active-constraint rows must align with observations")
        for observation_index, rows in enumerate(active_constraints):
            for raw_index in rows:
                index = int(raw_index)
                if not 0 <= index < normals.shape[0]:
                    raise ValueError("active-constraint index is out of range")
                value = float(observed_left[observation_index, index])
                if index in active_values and not np.isclose(
                    active_values[index], value, atol=tolerance, rtol=0.0
                ):
                    raise ValueError(
                        "one inferred constraint cannot be active at inconsistent levels"
                    )
                active_values[index] = value
        for index, value in active_values.items():
            if lower_bounds[index] > value + tolerance:
                raise ValueError("an active boundary would exclude another observation")
            inferred[index] = value
    violation = float(np.max(observed_left - inferred[None, :], initial=0.0))
    active_residual = max(
        (
            abs(inferred[index] - value)
            for index, value in active_values.items()
        ),
        default=0.0,
    )
    return InverseLinearRHSResult(
        inferred,
        inferred - reference,
        max(0.0, violation),
        float(active_residual),
    )


def _normalization_row(
    variable_count: int,
    normalization: tuple[int, float] | None,
    dimension: int,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    if normalization is None:
        return None, None
    index, value = normalization
    if not 0 <= index < dimension or not isfinite(value) or value == 0.0:
        raise ValueError("normalization needs a valid index and non-zero value")
    row = np.zeros((1, variable_count), dtype=np.float64)
    row[0, index] = 1.0
    return row, np.array([float(value)], dtype=np.float64)


def inverse_linear_program(
    observations: Sequence[InverseLPObservation],
    reference_cost: Sequence[float],
    *,
    active_tolerance: float = 1e-8,
    feasibility_tolerance: float = 1e-8,
    normalization: tuple[int, float] | None = None,
) -> InverseLPResult:
    """Find the closest cost vector satisfying the observations' KKT systems.

    Constraints are interpreted as ``A @ x <= b``.  The L1 distance to the
    reference cost fixes the otherwise unavoidable scale ambiguity.  An
    optional component normalization can impose an external scale convention.
    """

    if not observations or active_tolerance <= 0.0 or feasibility_tolerance < 0.0:
        raise ValueError("inverse LP needs observations and valid tolerances")
    reference = np.asarray(reference_cost, dtype=np.float64)
    if reference.ndim != 1 or reference.size == 0 or np.any(~np.isfinite(reference)):
        raise ValueError("reference cost must be a finite non-empty vector")
    dimension = reference.size
    checked: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    maximum_primal_violation = 0.0
    total_active = 0
    for observation in observations:
        matrix = np.asarray(observation.a_ub, dtype=np.float64)
        bound = np.asarray(observation.b_ub, dtype=np.float64)
        decision = np.asarray(observation.decision, dtype=np.float64)
        if (
            matrix.ndim != 2
            or matrix.shape[1] != dimension
            or bound.shape != (matrix.shape[0],)
            or decision.shape != (dimension,)
            or np.any(~np.isfinite(matrix))
            or np.any(~np.isfinite(bound))
            or np.any(~np.isfinite(decision))
        ):
            raise ValueError("inverse LP observation dimensions are inconsistent")
        residual = matrix @ decision - bound
        violation = float(max(0.0, np.max(residual, initial=0.0)))
        maximum_primal_violation = max(maximum_primal_violation, violation)
        if violation > feasibility_tolerance:
            raise ValueError("an observed inverse-LP decision is infeasible")
        active = np.flatnonzero(np.abs(residual) <= active_tolerance)
        checked.append((matrix, bound, decision, active))
        total_active += active.size

    # Variables are cost, L1 deviations from the reference, and active duals.
    variable_count = 2 * dimension + total_active
    objective = np.zeros(variable_count, dtype=np.float64)
    objective[dimension : 2 * dimension] = 1.0
    if total_active:
        objective[2 * dimension :] = 1e-10
    a_ub = []
    b_ub = []
    for index in range(dimension):
        positive = np.zeros(variable_count)
        positive[index] = 1.0
        positive[dimension + index] = -1.0
        a_ub.append(positive)
        b_ub.append(reference[index])
        negative = np.zeros(variable_count)
        negative[index] = -1.0
        negative[dimension + index] = -1.0
        a_ub.append(negative)
        b_ub.append(-reference[index])

    equalities = []
    equality_bounds = []
    dual_offset = 2 * dimension
    active_sets = []
    for matrix, _bound, _decision, active in checked:
        block = np.zeros((dimension, variable_count), dtype=np.float64)
        block[:, :dimension] = np.eye(dimension)
        if active.size:
            block[:, dual_offset : dual_offset + active.size] = matrix[active].T
        equalities.extend(block)
        equality_bounds.extend(np.zeros(dimension))
        active_sets.append(tuple(int(value) for value in active))
        dual_offset += active.size
    norm_a, norm_b = _normalization_row(
        variable_count, normalization, dimension
    )
    if norm_a is not None:
        equalities.extend(norm_a)
        equality_bounds.extend(norm_b)
    bounds = (
        [(None, None)] * dimension
        + [(0.0, None)] * dimension
        + [(0.0, None)] * total_active
    )
    solved = linprog(
        objective,
        A_ub=np.asarray(a_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.asarray(equalities),
        b_eq=np.asarray(equality_bounds),
        bounds=bounds,
        method="highs",
    )
    if not solved.success or solved.x is None:
        raise RuntimeError(f"inverse LP KKT system is infeasible: {solved.message}")

    cost = np.asarray(solved.x[:dimension], dtype=np.float64)
    duals = []
    stationarity = 0.0
    complementarity = 0.0
    dual_offset = 2 * dimension
    for matrix, bound, decision, active in checked:
        dual = np.zeros(matrix.shape[0], dtype=np.float64)
        dual[active] = solved.x[dual_offset : dual_offset + active.size]
        dual_offset += active.size
        duals.append(dual)
        stationarity = max(
            stationarity, float(np.max(np.abs(cost + matrix.T @ dual)))
        )
        complementarity = max(
            complementarity,
            float(np.max(np.abs(dual * (matrix @ decision - bound)), initial=0.0)),
        )
    return InverseLPResult(
        cost,
        tuple(duals),
        float(np.sum(np.abs(cost - reference))),
        maximum_primal_violation,
        stationarity,
        complementarity,
        tuple(active_sets),
    )


@dataclass(frozen=True)
class RevealedLinearResult:
    cost: np.ndarray
    slacks: np.ndarray
    maximum_violation: float
    comparison_rank: int
    objective_change: float


def _fit_margin_model(
    rows: np.ndarray,
    reference: np.ndarray,
    *,
    margin: float,
    slack_penalty: float,
    normalization: tuple[int, float] | None,
) -> tuple[np.ndarray, np.ndarray, int, float]:
    """Fit ``rows @ weights >= margin`` with L1 movement and soft slacks."""

    if (
        rows.ndim != 2
        or rows.shape[1] != reference.size
        or rows.shape[0] == 0
        or np.any(~np.isfinite(rows))
        or not isfinite(margin)
        or margin < 0.0
        or not isfinite(slack_penalty)
        or slack_penalty <= 0.0
    ):
        raise ValueError("inverse margin model inputs are invalid")
    dimension = reference.size
    comparison_count = rows.shape[0]
    variable_count = 2 * dimension + comparison_count
    objective = np.zeros(variable_count)
    objective[dimension : 2 * dimension] = 1.0
    objective[2 * dimension :] = slack_penalty
    inequalities = []
    bounds_vector = []
    for index in range(dimension):
        row = np.zeros(variable_count)
        row[index] = 1.0
        row[dimension + index] = -1.0
        inequalities.append(row)
        bounds_vector.append(reference[index])
        row = np.zeros(variable_count)
        row[index] = -1.0
        row[dimension + index] = -1.0
        inequalities.append(row)
        bounds_vector.append(-reference[index])
    for index, comparison in enumerate(rows):
        row = np.zeros(variable_count)
        row[:dimension] = -comparison
        row[2 * dimension + index] = -1.0
        inequalities.append(row)
        bounds_vector.append(-margin)
    equality, equality_bound = _normalization_row(
        variable_count, normalization, dimension
    )
    solved = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.asarray(bounds_vector),
        A_eq=equality,
        b_eq=equality_bound,
        bounds=(
            [(None, None)] * dimension
            + [(0.0, None)] * dimension
            + [(0.0, None)] * comparison_count
        ),
        method="highs",
    )
    if not solved.success or solved.x is None:
        raise RuntimeError(f"inverse margin fitting failed: {solved.message}")
    weights = np.asarray(solved.x[:dimension], dtype=np.float64)
    slacks = np.asarray(solved.x[2 * dimension :], dtype=np.float64)
    return (
        weights,
        slacks,
        int(np.linalg.matrix_rank(rows)),
        float(np.sum(np.abs(weights - reference))),
    )


def fit_revealed_linear_cost(
    chosen_decisions: Sequence[Sequence[float]],
    feasible_alternatives: Sequence[Sequence[Sequence[float]]],
    reference_cost: Sequence[float],
    *,
    margin: float = 0.0,
    slack_penalty: float = 100.0,
    normalization: tuple[int, float] | None = None,
) -> RevealedLinearResult:
    """Fit a minimization cost from chosen-versus-alternative comparisons.

    This soft-margin form also covers inverse discrete optimization, where a
    compact KKT system is unavailable but candidate feasible actions are known.
    """

    chosen = [np.asarray(value, dtype=np.float64) for value in chosen_decisions]
    alternatives = [np.asarray(value, dtype=np.float64) for value in feasible_alternatives]
    reference = np.asarray(reference_cost, dtype=np.float64)
    if (
        not chosen
        or len(chosen) != len(alternatives)
        or reference.ndim != 1
        or reference.size == 0
        or np.any(~np.isfinite(reference))
    ):
        raise ValueError("revealed-cost observations are inconsistent")
    rows = []
    for selected, candidates in zip(chosen, alternatives, strict=True):
        if (
            selected.shape != reference.shape
            or candidates.ndim != 2
            or candidates.shape[1] != reference.size
            or candidates.shape[0] == 0
            or np.any(~np.isfinite(selected))
            or np.any(~np.isfinite(candidates))
        ):
            raise ValueError("revealed-cost observation dimensions are inconsistent")
        # Minimization optimality c @ chosen <= c @ alternative.
        rows.extend(candidates - selected)
    matrix = np.asarray(rows, dtype=np.float64)
    cost, slacks, rank, change = _fit_margin_model(
        matrix,
        reference,
        margin=margin,
        slack_penalty=slack_penalty,
        normalization=normalization,
    )
    violation = np.maximum(0.0, margin - matrix @ cost)
    return RevealedLinearResult(
        cost,
        slacks,
        float(np.max(violation, initial=0.0)),
        rank,
        change,
    )


@dataclass(frozen=True)
class OccupancyResult:
    state: np.ndarray
    state_action: np.ndarray
    feature_expectations: np.ndarray | None


def discounted_occupancy(
    transition: Sequence,
    policy: Sequence,
    initial_distribution: Sequence[float],
    *,
    discount: float,
    features: Sequence | None = None,
) -> OccupancyResult:
    """Compute unnormalized discounted state-action occupancy and features."""

    kernel = np.asarray(transition, dtype=np.float64)
    strategy = np.asarray(policy, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("transition must have shape (states, actions, states)")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or strategy.shape != (states, actions)
        or initial.shape != (states,)
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(strategy))
        or np.any(~np.isfinite(initial))
        or np.any(kernel < 0.0)
        or np.any(strategy < 0.0)
        or np.any(initial < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not np.allclose(strategy.sum(axis=1), 1.0)
        or not np.isclose(initial.sum(), 1.0)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("discounted occupancy inputs are invalid")
    policy_transition = np.einsum("sa,san->sn", strategy, kernel)
    state = np.linalg.solve(
        np.eye(states) - discount * policy_transition.T, initial
    )
    state_action = state[:, None] * strategy
    expectation = None
    if features is not None:
        feature_array = np.asarray(features, dtype=np.float64)
        if (
            feature_array.ndim != 3
            or feature_array.shape[:2] != (states, actions)
            or np.any(~np.isfinite(feature_array))
        ):
            raise ValueError("occupancy features must have shape (states, actions, k)")
        expectation = np.einsum("sa,sak->k", state_action, feature_array)
    return OccupancyResult(state, state_action, expectation)


@dataclass(frozen=True)
class InverseMDPResult:
    reward_weights: np.ndarray
    rewards: np.ndarray
    state_values: np.ndarray
    advantages: np.ndarray
    slacks: np.ndarray
    policy: tuple[int, ...]
    comparison_rank: int
    objective_change: float


def inverse_mdp_policy(
    transition: Sequence,
    reward_features: Sequence,
    observed_policy: Sequence[int],
    reference_weights: Sequence[float],
    *,
    discount: float = 0.95,
    margin: float = 0.0,
    slack_penalty: float = 100.0,
    normalization: tuple[int, float] | None = None,
) -> InverseMDPResult:
    """Infer linear rewards that make a deterministic policy near-optimal."""

    kernel = np.asarray(transition, dtype=np.float64)
    features = np.asarray(reward_features, dtype=np.float64)
    policy = np.asarray(observed_policy, dtype=np.int64)
    reference = np.asarray(reference_weights, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("transition must have shape (states, actions, states)")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or features.ndim != 3
        or features.shape[:2] != (states, actions)
        or reference.shape != (features.shape[2],)
        or policy.shape != (states,)
        or np.any(policy < 0)
        or np.any(policy >= actions)
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(features))
        or np.any(~np.isfinite(reference))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("inverse MDP inputs are invalid")
    policy_transition = kernel[np.arange(states), policy]
    policy_features = features[np.arange(states), policy]
    value_features = np.linalg.solve(
        np.eye(states) - discount * policy_transition, policy_features
    )
    comparisons = []
    comparison_positions = []
    for state in range(states):
        chosen = policy[state]
        chosen_return = (
            features[state, chosen] + discount * kernel[state, chosen] @ value_features
        )
        for action in range(actions):
            if action == chosen:
                continue
            alternative_return = (
                features[state, action]
                + discount * kernel[state, action] @ value_features
            )
            comparisons.append(chosen_return - alternative_return)
            comparison_positions.append((state, action))
    matrix = np.asarray(comparisons, dtype=np.float64)
    weights, slacks, rank, change = _fit_margin_model(
        matrix,
        reference,
        margin=margin,
        slack_penalty=slack_penalty,
        normalization=normalization,
    )
    rewards = np.einsum("sak,k->sa", features, weights)
    values = value_features @ weights
    q_values = rewards + discount * np.einsum("san,n->sa", kernel, values)
    advantages = q_values[np.arange(states), policy, None] - q_values
    return InverseMDPResult(
        weights,
        rewards,
        values,
        advantages,
        slacks,
        tuple(int(action) for action in policy),
        rank,
        change,
    )


def potential_based_reward_shaping(
    transition: Sequence,
    reward: Sequence,
    potential: Sequence[float],
    *,
    discount: float,
) -> np.ndarray:
    """Apply ``r' = r + gamma * Phi(next) - Phi(state)``.

    A state-action reward receives the transition expectation of the shaping
    term; a state-action-next-state reward receives the term pointwise.
    """

    kernel = np.asarray(transition, dtype=np.float64)
    base = np.asarray(reward, dtype=np.float64)
    phi = np.asarray(potential, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("transition must have shape (states, actions, states)")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or phi.shape != (states,)
        or base.shape not in ((states, actions), (states, actions, states))
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(base))
        or np.any(~np.isfinite(phi))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("potential shaping inputs are invalid")
    shaping = discount * phi[None, None, :] - phi[:, None, None]
    if base.ndim == 3:
        return base + shaping
    return base + np.einsum("san,san->sa", kernel, shaping)


@dataclass(frozen=True)
class BayesianInverseMDPResult:
    candidate_weights: np.ndarray
    posterior: np.ndarray
    map_index: int
    map_weights: np.ndarray
    posterior_mean: np.ndarray
    log_evidence: float
    action_probabilities: np.ndarray


def bayesian_inverse_mdp(
    transition: Sequence,
    reward_features: Sequence,
    demonstrations: Sequence[tuple[int, int]],
    candidate_weights: Sequence[Sequence[float]],
    *,
    prior: Sequence[float] | None = None,
    discount: float = 0.95,
    precision: float = 1.0,
    value_tolerance: float = 1e-10,
    max_value_iterations: int = 10_000,
) -> BayesianInverseMDPResult:
    """Exact finite-hypothesis Bayesian IRL with Boltzmann-optimal actions."""

    kernel = np.asarray(transition, dtype=np.float64)
    features = np.asarray(reward_features, dtype=np.float64)
    candidates = np.asarray(candidate_weights, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("transition must have shape (states, actions, states)")
    states, actions, next_states = kernel.shape
    if (
        next_states != states
        or features.ndim != 3
        or features.shape[:2] != (states, actions)
        or candidates.ndim != 2
        or candidates.shape[0] == 0
        or candidates.shape[1] != features.shape[2]
        or np.any(~np.isfinite(kernel))
        or np.any(~np.isfinite(features))
        or np.any(~np.isfinite(candidates))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not 0.0 <= discount < 1.0
        or not isfinite(precision)
        or precision <= 0.0
        or value_tolerance <= 0.0
        or max_value_iterations <= 0
        or not demonstrations
    ):
        raise ValueError("Bayesian inverse MDP inputs are invalid")
    observed = tuple((int(state), int(action)) for state, action in demonstrations)
    if any(
        state < 0 or state >= states or action < 0 or action >= actions
        for state, action in observed
    ):
        raise ValueError("Bayesian inverse MDP demonstration is out of range")
    if prior is None:
        prior_array = np.full(candidates.shape[0], 1.0 / candidates.shape[0])
    else:
        prior_array = np.asarray(prior, dtype=np.float64)
        if (
            prior_array.shape != (candidates.shape[0],)
            or np.any(~np.isfinite(prior_array))
            or np.any(prior_array < 0.0)
            or prior_array.sum() <= 0.0
        ):
            raise ValueError("Bayesian inverse MDP prior is invalid")
        prior_array = prior_array / prior_array.sum()
    probabilities = np.empty((candidates.shape[0], states, actions))
    log_likelihood = np.zeros(candidates.shape[0])
    for candidate_index, weights in enumerate(candidates):
        rewards = np.einsum("sak,k->sa", features, weights)
        values = np.zeros(states)
        for _ in range(max_value_iterations):
            q_values = rewards + discount * np.einsum(
                "san,n->sa", kernel, values
            )
            updated = np.max(q_values, axis=1)
            if np.max(np.abs(updated - values)) <= value_tolerance:
                values = updated
                break
            values = updated
        else:
            raise RuntimeError("Bayesian inverse MDP value iteration did not converge")
        q_values = rewards + discount * np.einsum("san,n->sa", kernel, values)
        logits = precision * q_values
        log_probabilities = logits - logsumexp(logits, axis=1)[:, None]
        probabilities[candidate_index] = np.exp(log_probabilities)
        log_likelihood[candidate_index] = sum(
            log_probabilities[state, action] for state, action in observed
        )
    log_prior = np.full_like(prior_array, -np.inf)
    positive = prior_array > 0.0
    log_prior[positive] = np.log(prior_array[positive])
    log_joint = log_prior + log_likelihood
    log_evidence = float(logsumexp(log_joint))
    posterior = np.exp(log_joint - log_evidence)
    map_index = int(np.argmax(posterior))
    return BayesianInverseMDPResult(
        candidates,
        posterior,
        map_index,
        candidates[map_index].copy(),
        posterior @ candidates,
        log_evidence,
        probabilities,
    )


@dataclass(frozen=True)
class StackelbergObservation:
    leader_strategy: np.ndarray
    follower_response: int


@dataclass(frozen=True)
class InverseStackelbergResult:
    follower_weights: np.ndarray
    follower_payoffs: np.ndarray
    slacks: np.ndarray
    regrets: np.ndarray
    comparison_rank: int
    objective_change: float


def inverse_stackelberg_follower_utility(
    payoff_features: Sequence,
    observations: Sequence[StackelbergObservation],
    reference_weights: Sequence[float],
    *,
    margin: float = 0.0,
    slack_penalty: float = 100.0,
    normalization: tuple[int, float] | None = None,
) -> InverseStackelbergResult:
    """Infer follower payoff weights from leader commitments and responses."""

    features = np.asarray(payoff_features, dtype=np.float64)
    reference = np.asarray(reference_weights, dtype=np.float64)
    if (
        features.ndim != 3
        or min(features.shape[:2]) == 0
        or reference.shape != (features.shape[2],)
        or np.any(~np.isfinite(features))
        or np.any(~np.isfinite(reference))
        or not observations
    ):
        raise ValueError("inverse Stackelberg inputs are invalid")
    leader_actions, follower_actions, _ = features.shape
    comparisons = []
    checked = []
    for observation in observations:
        strategy = np.asarray(observation.leader_strategy, dtype=np.float64)
        response = int(observation.follower_response)
        if (
            strategy.shape != (leader_actions,)
            or np.any(~np.isfinite(strategy))
            or np.any(strategy < 0.0)
            or not np.isclose(strategy.sum(), 1.0)
            or not 0 <= response < follower_actions
        ):
            raise ValueError("invalid observed Stackelberg response")
        expected_features = np.einsum("l,lfk->fk", strategy, features)
        for alternative in range(follower_actions):
            if alternative != response:
                comparisons.append(
                    expected_features[response] - expected_features[alternative]
                )
        checked.append((strategy, response))
    matrix = np.asarray(comparisons, dtype=np.float64)
    weights, slacks, rank, change = _fit_margin_model(
        matrix,
        reference,
        margin=margin,
        slack_penalty=slack_penalty,
        normalization=normalization,
    )
    payoffs = np.einsum("lfk,k->lf", features, weights)
    regrets = []
    for strategy, response in checked:
        expected = strategy @ payoffs
        regrets.append(float(np.max(expected) - expected[response]))
    return InverseStackelbergResult(
        weights,
        payoffs,
        slacks,
        np.asarray(regrets),
        rank,
        change,
    )


@dataclass(frozen=True)
class LogitStackelbergResult:
    follower_weights: np.ndarray
    choice_probabilities: np.ndarray
    negative_log_likelihood: float
    converged: bool
    iterations: int
    information_rank: int


def inverse_logit_stackelberg_utility(
    payoff_features: Sequence,
    observations: Sequence[StackelbergObservation],
    initial_weights: Sequence[float],
    *,
    precision: float = 1.0,
    l2_regularization: float = 1e-6,
    max_iterations: int = 1_000,
) -> LogitStackelbergResult:
    """Maximum-likelihood follower utility inference under a Logit response."""

    features = np.asarray(payoff_features, dtype=np.float64)
    initial = np.asarray(initial_weights, dtype=np.float64)
    if (
        features.ndim != 3
        or initial.shape != (features.shape[2],)
        or np.any(~np.isfinite(features))
        or np.any(~np.isfinite(initial))
        or not observations
        or not isfinite(precision)
        or precision <= 0.0
        or not isfinite(l2_regularization)
        or l2_regularization < 0.0
        or max_iterations <= 0
    ):
        raise ValueError("inverse Logit Stackelberg inputs are invalid")
    leader_actions, follower_actions, _ = features.shape
    expected_features = []
    responses = []
    for observation in observations:
        strategy = np.asarray(observation.leader_strategy, dtype=np.float64)
        response = int(observation.follower_response)
        if (
            strategy.shape != (leader_actions,)
            or np.any(~np.isfinite(strategy))
            or np.any(strategy < 0.0)
            or not np.isclose(strategy.sum(), 1.0)
            or not 0 <= response < follower_actions
        ):
            raise ValueError("invalid observed Logit Stackelberg response")
        expected_features.append(np.einsum("l,lfk->fk", strategy, features))
        responses.append(response)
    design = np.asarray(expected_features, dtype=np.float64)
    response_array = np.asarray(responses, dtype=np.int64)

    def objective(weights: np.ndarray) -> tuple[float, np.ndarray]:
        logits = precision * np.einsum("ofk,k->of", design, weights)
        log_normalizer = logsumexp(logits, axis=1)
        selected = logits[np.arange(logits.shape[0]), response_array]
        value = float(np.sum(log_normalizer - selected))
        shifted = logits - log_normalizer[:, None]
        probabilities = np.exp(shifted)
        expected = np.einsum("of,ofk->ok", probabilities, design)
        selected_features = design[np.arange(design.shape[0]), response_array]
        gradient = precision * np.sum(expected - selected_features, axis=0)
        difference = weights - initial
        value += 0.5 * l2_regularization * float(difference @ difference)
        gradient += l2_regularization * difference
        return value, gradient

    solved = minimize(
        lambda value: objective(value)[0],
        initial,
        jac=lambda value: objective(value)[1],
        method="L-BFGS-B",
        options={"maxiter": max_iterations},
    )
    weights = np.asarray(solved.x, dtype=np.float64)
    logits = precision * np.einsum("ofk,k->of", design, weights)
    probabilities = np.exp(logits - logsumexp(logits, axis=1)[:, None])
    centered = design - design.mean(axis=1, keepdims=True)
    information_rank = int(np.linalg.matrix_rank(centered.reshape(-1, features.shape[2])))
    return LogitStackelbergResult(
        weights,
        probabilities,
        float(objective(weights)[0]),
        bool(solved.success),
        int(solved.nit),
        information_rank,
    )


@dataclass(frozen=True)
class IncentiveStackelbergResult:
    reaction_map: tuple[int, ...]
    follower_response: int
    leader_value: float
    follower_value: float
    best_response_set: tuple[int, ...]
    tie_breaking: str


def solve_incentive_stackelberg(
    leader_payoffs: Sequence[Sequence[float]],
    follower_payoffs: Sequence[Sequence[float]],
    *,
    tie_breaking: str = "strong",
    tolerance: float = 1e-10,
    max_profiles: int = 1_000_000,
) -> IncentiveStackelbergResult:
    """Solve a finite inverse/reaction-map Stackelberg commitment exactly.

    The leader commits to one leader action for every possible follower action.
    The follower then selects a best response to that announced reaction map.
    """

    leader = np.asarray(leader_payoffs, dtype=np.float64)
    follower = np.asarray(follower_payoffs, dtype=np.float64)
    if (
        leader.ndim != 2
        or leader.shape != follower.shape
        or min(leader.shape) == 0
        or np.any(~np.isfinite(leader))
        or np.any(~np.isfinite(follower))
        or tie_breaking not in {"strong", "weak"}
        or tolerance < 0.0
        or max_profiles <= 0
    ):
        raise ValueError("incentive Stackelberg inputs are invalid")
    leader_actions, follower_actions = leader.shape
    profile_count = leader_actions**follower_actions
    if profile_count > max_profiles:
        raise ValueError("reaction-map profile budget exceeded")
    best: IncentiveStackelbergResult | None = None
    best_score = None
    for mapping in product(range(leader_actions), repeat=follower_actions):
        follower_values = np.array(
            [follower[mapping[action], action] for action in range(follower_actions)]
        )
        maximum = float(np.max(follower_values))
        best_responses = tuple(
            int(action)
            for action in np.flatnonzero(follower_values >= maximum - tolerance)
        )
        if tie_breaking == "strong":
            response = max(
                best_responses,
                key=lambda action: (leader[mapping[action], action], -action),
            )
        else:
            response = min(
                best_responses,
                key=lambda action: (leader[mapping[action], action], action),
            )
        leader_value = float(leader[mapping[response], response])
        follower_value = float(follower[mapping[response], response])
        score = (
            leader_value,
            follower_value,
            -response,
            tuple(-action for action in mapping),
        )
        if best is None or score > best_score:
            best = IncentiveStackelbergResult(
                tuple(int(action) for action in mapping),
                int(response),
                leader_value,
                follower_value,
                best_responses,
                tie_breaking,
            )
            best_score = score
    if best is None:
        raise RuntimeError("no inverse Stackelberg reaction map was enumerated")
    return best
