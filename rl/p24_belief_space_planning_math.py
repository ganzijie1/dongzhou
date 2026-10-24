"""P24 exact and approximate belief-space planning for finite games."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from math import ceil, isfinite, log, sqrt
from typing import Callable, Hashable, Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.special import softmax


@dataclass(frozen=True)
class AlphaVector:
    values: np.ndarray
    action: int
    continuation: tuple[int, ...] = ()


@dataclass(frozen=True)
class AlphaVectorPlan:
    layers: tuple[tuple[AlphaVector, ...], ...]
    discount: float


def _finite_pomdp_arrays(
    transition: Sequence,
    observation: Sequence,
    reward: Sequence,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    transitions = np.asarray(transition, dtype=np.float64)
    observations = np.asarray(observation, dtype=np.float64)
    rewards = np.asarray(reward, dtype=np.float64)
    if (
        transitions.ndim != 3
        or transitions.shape[0] == 0
        or transitions.shape[0] != transitions.shape[2]
    ):
        raise ValueError("transition must have shape [state, action, next_state]")
    states, actions, _ = transitions.shape
    if observations.ndim != 3 or observations.shape[:2] != (actions, states):
        raise ValueError("observation must have shape [action, next_state, observation]")
    if rewards.shape != (states, actions):
        raise ValueError("reward must have shape [state, action]")
    if any(np.any(~np.isfinite(value)) for value in (transitions, observations, rewards)):
        raise ValueError("POMDP arrays must be finite")
    if (
        np.any(transitions < 0.0)
        or not np.allclose(transitions.sum(axis=2), 1.0)
        or np.any(observations < 0.0)
        or not np.allclose(observations.sum(axis=2), 1.0)
    ):
        raise ValueError("POMDP probability rows must be normalized")
    return transitions, observations, rewards


def _belief(value: Sequence[float], states: int) -> np.ndarray:
    belief = np.asarray(value, dtype=np.float64)
    if (
        belief.shape != (states,)
        or np.any(~np.isfinite(belief))
        or np.any(belief < 0.0)
        or not np.isclose(belief.sum(), 1.0)
    ):
        raise ValueError("belief must be a normalized state distribution")
    return belief


def _deduplicate(vectors: Sequence[AlphaVector], tolerance: float) -> list[AlphaVector]:
    result: list[AlphaVector] = []
    for candidate in vectors:
        if not any(np.max(np.abs(candidate.values - item.values)) <= tolerance for item in result):
            result.append(candidate)
    return result


def prune_alpha_vectors(
    vectors: Sequence[AlphaVector],
    *,
    tolerance: float = 1e-10,
) -> tuple[AlphaVector, ...]:
    """Remove vectors that never strictly maximize value on the belief simplex."""

    unique = _deduplicate(vectors, tolerance)
    if len(unique) <= 1:
        return tuple(unique)
    states = unique[0].values.size
    if any(item.values.shape != (states,) for item in unique):
        raise ValueError("alpha vectors must share one state dimension")
    kept: list[AlphaVector] = []
    for index, candidate in enumerate(unique):
        others = [item for j, item in enumerate(unique) if j != index]
        # b dot (candidate - other) >= margin.
        inequalities = np.array(
            [np.r_[other.values - candidate.values, 1.0] for other in others],
            dtype=np.float64,
        )
        solved = linprog(
            np.r_[np.zeros(states), -1.0],
            A_ub=inequalities,
            b_ub=np.zeros(len(others)),
            A_eq=np.r_[np.ones(states), 0.0][None, :],
            b_eq=np.array([1.0]),
            bounds=[(0.0, 1.0)] * states + [(None, None)],
            method="highs",
        )
        if solved.success and solved.x[-1] > tolerance:
            kept.append(candidate)
    if not kept:
        # Numerically identical envelopes can leave no strict winner.
        values = np.vstack([item.values for item in unique])
        kept.append(unique[int(np.argmax(values.mean(axis=1)))])
    return tuple(kept)


def _backup_alpha(
    transitions: np.ndarray,
    observations: np.ndarray,
    rewards: np.ndarray,
    previous: Sequence[AlphaVector],
    action: int,
    continuation: Sequence[int],
    discount: float,
) -> AlphaVector:
    values = rewards[:, action].copy()
    for observation_index, vector_index in enumerate(continuation):
        vector = previous[vector_index].values
        values += discount * (
            transitions[:, action, :]
            @ (observations[action, :, observation_index] * vector)
        )
    return AlphaVector(values, action, tuple(int(i) for i in continuation))


def alpha_vector_dynamic_programming(
    transition: Sequence,
    observation: Sequence,
    reward: Sequence,
    *,
    horizon: int,
    discount: float = 1.0,
    maximum_candidates: int = 250_000,
    tolerance: float = 1e-10,
) -> AlphaVectorPlan:
    """Exact finite-horizon alpha-vector DP with LP dominance pruning."""

    transitions, observations, rewards = _finite_pomdp_arrays(
        transition, observation, reward
    )
    if (
        horizon < 1
        or not isfinite(discount)
        or not 0.0 <= discount <= 1.0
        or maximum_candidates < 1
    ):
        raise ValueError("alpha-vector settings are invalid")
    actions = transitions.shape[1]
    observation_count = observations.shape[2]
    current = prune_alpha_vectors(
        [AlphaVector(rewards[:, action].copy(), action) for action in range(actions)],
        tolerance=tolerance,
    )
    layers = [current]
    for _ in range(1, horizon):
        candidate_count = actions * len(current) ** observation_count
        if candidate_count > maximum_candidates:
            raise ValueError("exact alpha-vector cross-sum exceeds maximum_candidates")
        candidates = [
            _backup_alpha(
                transitions,
                observations,
                rewards,
                current,
                action,
                continuation,
                discount,
            )
            for action in range(actions)
            for continuation in product(range(len(current)), repeat=observation_count)
        ]
        current = prune_alpha_vectors(candidates, tolerance=tolerance)
        layers.append(current)
    return AlphaVectorPlan(tuple(layers), float(discount))


def alpha_vector_action(
    plan: AlphaVectorPlan,
    belief: Sequence[float],
    *,
    layer: int = -1,
) -> tuple[int, float, int]:
    vectors = plan.layers[layer]
    if not vectors:
        raise ValueError("alpha-vector layer is empty")
    state_count = vectors[0].values.size
    probabilities = _belief(belief, state_count)
    values = np.array([probabilities @ item.values for item in vectors])
    index = int(np.argmax(values))
    return vectors[index].action, float(values[index]), index


def point_based_value_iteration(
    transition: Sequence,
    observation: Sequence,
    reward: Sequence,
    belief_points: Sequence[Sequence[float]],
    *,
    horizon: int,
    discount: float = 1.0,
    tolerance: float = 1e-10,
) -> AlphaVectorPlan:
    """PBVI backups restricted to caller-provided reachable belief points."""

    transitions, observations, rewards = _finite_pomdp_arrays(
        transition, observation, reward
    )
    states, actions, _ = transitions.shape
    beliefs = [_belief(value, states) for value in belief_points]
    if not beliefs or horizon < 1 or not 0.0 <= discount <= 1.0:
        raise ValueError("PBVI needs belief points, positive horizon, and valid discount")
    observation_count = observations.shape[2]
    current = prune_alpha_vectors(
        [AlphaVector(rewards[:, action].copy(), action) for action in range(actions)],
        tolerance=tolerance,
    )
    layers = [current]
    for _ in range(1, horizon):
        selected: list[AlphaVector] = []
        for belief in beliefs:
            action_vectors = []
            for action in range(actions):
                continuation = []
                for observation_index in range(observation_count):
                    projected = [
                        transitions[:, action, :]
                        @ (
                            observations[action, :, observation_index]
                            * item.values
                        )
                        for item in current
                    ]
                    continuation.append(
                        int(np.argmax([belief @ value for value in projected]))
                    )
                action_vectors.append(
                    _backup_alpha(
                        transitions,
                        observations,
                        rewards,
                        current,
                        action,
                        continuation,
                        discount,
                    )
                )
            selected.append(
                max(action_vectors, key=lambda item: float(belief @ item.values))
            )
        current = prune_alpha_vectors(selected, tolerance=tolerance)
        layers.append(current)
    return AlphaVectorPlan(tuple(layers), float(discount))


@dataclass
class _POMCPOWAction:
    visits: int = 0
    value: float = 0.0
    children: dict[Hashable, "_POMCPOWNode"] = field(default_factory=dict)
    observations: dict[Hashable, object] = field(default_factory=dict)


@dataclass
class _POMCPOWNode:
    visits: int = 0
    actions: dict[Hashable, _POMCPOWAction] = field(default_factory=dict)
    particles: list[tuple[object, float]] = field(default_factory=list)


@dataclass(frozen=True)
class POMCPOWResult:
    action: Hashable
    action_values: dict[Hashable, float]
    action_visits: dict[Hashable, int]
    history_nodes: int
    observation_nodes: int
    minimum_particle_ess: float


def pomcpow_plan(
    initial_particles: Sequence,
    legal_actions: Callable[[object], Sequence[Hashable]],
    generative_model: Callable[[object, Hashable, np.random.Generator], tuple[object, object, float]],
    *,
    simulations: int,
    horizon: int,
    discount: float = 1.0,
    exploration: float = 1.0,
    action_widening: tuple[float, float] = (1.5, 0.5),
    observation_widening: tuple[float, float] = (1.5, 0.5),
    observation_distance: Callable[[object, object], float] | None = None,
    observation_likelihood: Callable[[object, object, Hashable], float] | None = None,
    random_state: int | None = None,
) -> POMCPOWResult:
    """Finite-budget POMCPOW with double progressive widening and particles."""

    if (
        not initial_particles
        or simulations < 1
        or horizon < 1
        or not 0.0 <= discount <= 1.0
        or exploration < 0.0
        or any(not isfinite(x) or x <= 0.0 for x in action_widening)
        or any(not isfinite(x) or x <= 0.0 for x in observation_widening)
    ):
        raise ValueError("POMCPOW settings are invalid")
    rng = np.random.default_rng(random_state)
    root = _POMCPOWNode()
    all_nodes = [root]

    def distance(left: object, right: object) -> float:
        if observation_distance is not None:
            return float(observation_distance(left, right))
        return 0.0 if left == right else float("inf")

    def rollout(state: object, depth: int) -> float:
        if depth == 0:
            return 0.0
        actions = tuple(legal_actions(state))
        if not actions:
            return 0.0
        action = actions[int(rng.integers(len(actions)))]
        next_state, _, reward_value = generative_model(state, action, rng)
        return float(reward_value) + discount * rollout(next_state, depth - 1)

    def simulate(node: _POMCPOWNode, state: object, depth: int) -> float:
        if depth == 0:
            return 0.0
        choices = tuple(legal_actions(state))
        if not choices:
            return 0.0
        action_limit = max(
            1, int(ceil(action_widening[0] * max(1, node.visits) ** action_widening[1]))
        )
        missing = [action for action in choices if action not in node.actions]
        if missing and len(node.actions) < min(len(choices), action_limit):
            action = missing[int(rng.integers(len(missing)))]
            node.actions[action] = _POMCPOWAction()
        else:
            available = [action for action in choices if action in node.actions]
            if not available:
                action = choices[0]
                node.actions[action] = _POMCPOWAction()
                available = [action]
            action = max(
                available,
                key=lambda item: node.actions[item].value
                + exploration
                * sqrt(log(node.visits + 2.0) / (node.actions[item].visits + 1.0)),
            )
        stats = node.actions[action]
        next_state, observation_value, reward_value = generative_model(state, action, rng)
        reward_float = float(reward_value)
        if not isfinite(reward_float):
            raise ValueError("generative model returned a non-finite reward")
        observation_limit = max(
            1,
            int(
                ceil(
                    observation_widening[0]
                    * max(1, stats.visits) ** observation_widening[1]
                )
            ),
        )
        key: Hashable
        if len(stats.children) < observation_limit:
            try:
                hash(observation_value)
                key = observation_value
            except TypeError:
                key = repr(observation_value)
            if key not in stats.children:
                stats.children[key] = _POMCPOWNode()
                stats.observations[key] = observation_value
                all_nodes.append(stats.children[key])
        if stats.children:
            key = min(
                stats.children,
                key=lambda item: distance(observation_value, stats.observations[item]),
            )
        else:
            key = repr(observation_value)
            stats.children[key] = _POMCPOWNode()
            stats.observations[key] = observation_value
            all_nodes.append(stats.children[key])
        child = stats.children[key]
        weight = (
            1.0
            if observation_likelihood is None
            else float(observation_likelihood(observation_value, next_state, action))
        )
        if not isfinite(weight) or weight < 0.0:
            raise ValueError("observation likelihood must be finite and non-negative")
        child.particles.append((next_state, weight))
        future = rollout(next_state, depth - 1) if child.visits == 0 else simulate(
            child, next_state, depth - 1
        )
        total = reward_float + discount * future
        node.visits += 1
        stats.visits += 1
        stats.value += (total - stats.value) / stats.visits
        return total

    for _ in range(simulations):
        state = initial_particles[int(rng.integers(len(initial_particles)))]
        simulate(root, state, horizon)
    if not root.actions:
        raise ValueError("root particles have no legal actions")
    best = max(root.actions, key=lambda item: root.actions[item].visits)
    particle_ess = []
    observation_nodes = 0
    for node in all_nodes:
        for stats in node.actions.values():
            observation_nodes += len(stats.children)
        if node.particles:
            weights = np.array([value for _, value in node.particles])
            if weights.sum() > 0.0:
                particle_ess.append(float(weights.sum() ** 2 / np.sum(weights**2)))
    return POMCPOWResult(
        best,
        {action: stats.value for action, stats in root.actions.items()},
        {action: stats.visits for action, stats in root.actions.items()},
        len(all_nodes),
        observation_nodes,
        min(particle_ess, default=0.0),
    )


@dataclass(frozen=True)
class DESPOTResult:
    action: int
    scenario_value: float
    regularized_value: float
    fully_observable_upper_bound: float
    tree_size: int
    scenario_count: int


def despot_scenario_plan(
    transition: Sequence,
    observation: Sequence,
    reward: Sequence,
    belief: Sequence[float],
    *,
    horizon: int,
    scenario_count: int,
    discount: float = 1.0,
    regularization: float = 0.0,
    random_state: int | None = None,
) -> DESPOTResult:
    """Search a sparse common-random-number scenario tree for a finite POMDP."""

    transitions, observations, rewards = _finite_pomdp_arrays(
        transition, observation, reward
    )
    states, actions, _ = transitions.shape
    initial = _belief(belief, states)
    if (
        horizon < 1
        or scenario_count < 1
        or not 0.0 <= discount <= 1.0
        or regularization < 0.0
    ):
        raise ValueError("DESPOT settings are invalid")
    rng = np.random.default_rng(random_state)
    root_states = rng.choice(states, size=scenario_count, p=initial)
    uniforms = rng.random((scenario_count, horizon, actions, 2))

    def draw(probabilities: np.ndarray, uniform: float) -> int:
        return min(int(np.searchsorted(np.cumsum(probabilities), uniform, side="right")), probabilities.size - 1)

    def search(current_states: np.ndarray, scenario_ids: np.ndarray, depth: int):
        if depth == horizon or scenario_ids.size == 0:
            return 0.0, 0.0, 0, -1
        best = (-float("inf"), -float("inf"), 0, 0)
        for action in range(actions):
            next_states = np.empty_like(current_states)
            observed = np.empty_like(current_states)
            immediate = 0.0
            for local, (state, scenario_id) in enumerate(zip(current_states, scenario_ids)):
                immediate += rewards[state, action]
                next_state = draw(
                    transitions[state, action],
                    uniforms[scenario_id, depth, action, 0],
                )
                next_states[local] = next_state
                observed[local] = draw(
                    observations[action, next_state],
                    uniforms[scenario_id, depth, action, 1],
                )
            scenario_value = immediate / scenario_ids.size
            regularized_value = scenario_value - regularization
            tree_size = 1
            for obs in np.unique(observed):
                mask = observed == obs
                child_regularized, child_scenario, child_size, _ = search(
                    next_states[mask], scenario_ids[mask], depth + 1
                )
                weight = float(np.mean(mask))
                regularized_value += discount * weight * child_regularized
                scenario_value += discount * weight * child_scenario
                tree_size += child_size
            candidate = (regularized_value, scenario_value, tree_size, action)
            if candidate[0] > best[0]:
                best = candidate
        return best

    regularized_value, scenario_value, tree_size, action = search(
        root_states, np.arange(scenario_count), 0
    )
    full = np.zeros(states)
    for _ in range(horizon):
        full = np.max(
            rewards.T
            + discount * np.einsum("sak,k->as", transitions, full),
            axis=0,
        )
    upper = float(initial @ full)
    return DESPOTResult(
        action,
        float(scenario_value),
        float(regularized_value),
        upper,
        int(tree_size),
        scenario_count,
    )


@dataclass(frozen=True)
class InteractiveBeliefUpdate:
    belief: np.ndarray
    observation_probability: float


def interactive_belief_update(
    belief: Sequence,
    own_action: int,
    own_observation: int,
    physical_transition: Sequence,
    opponent_policy: Sequence,
    observation_probability: Sequence,
    *,
    model_transition: Sequence | None = None,
) -> InteractiveBeliefUpdate:
    """Bayes update over physical states and a finite opponent-model set."""

    prior = np.asarray(belief, dtype=np.float64)
    transition = np.asarray(physical_transition, dtype=np.float64)
    opponent = np.asarray(opponent_policy, dtype=np.float64)
    observation = np.asarray(observation_probability, dtype=np.float64)
    if prior.ndim != 2:
        raise ValueError("interactive belief must have shape [state, model]")
    states, models = prior.shape
    if (
        transition.ndim != 4
        or transition.shape[2:] != (states, states)
        or opponent.ndim != 3
        or opponent.shape[:2] != (models, states)
        or transition.shape[1] != opponent.shape[2]
        or observation.ndim != 3
        or observation.shape[1] != states
        or not 0 <= own_action < transition.shape[0]
        or not 0 <= own_observation < observation.shape[2]
    ):
        raise ValueError("interactive belief arrays are inconsistent")
    model_kernel = (
        np.eye(models)
        if model_transition is None
        else np.asarray(model_transition, dtype=np.float64)
    )
    if model_kernel.shape != (models, models):
        raise ValueError("model transition must have shape [model, next_model]")
    arrays = (prior, transition, opponent, observation, model_kernel)
    if (
        any(np.any(~np.isfinite(value)) for value in arrays)
        or np.any(prior < 0.0)
        or not np.isclose(prior.sum(), 1.0)
        or np.any(transition < 0.0)
        or not np.allclose(transition.sum(axis=3), 1.0)
        or np.any(opponent < 0.0)
        or not np.allclose(opponent.sum(axis=2), 1.0)
        or np.any(observation < 0.0)
        or not np.allclose(observation.sum(axis=2), 1.0)
        or np.any(model_kernel < 0.0)
        or not np.allclose(model_kernel.sum(axis=1), 1.0)
    ):
        raise ValueError("interactive belief probabilities are invalid")
    predicted = np.zeros((states, models))
    for state in range(states):
        for model in range(models):
            mass = prior[state, model]
            for opponent_action, action_probability in enumerate(opponent[model, state]):
                state_distribution = transition[own_action, opponent_action, state]
                predicted += (
                    mass
                    * action_probability
                    * state_distribution[:, None]
                    * model_kernel[model][None, :]
                )
    likelihood = observation[own_action, :, own_observation][:, None]
    unnormalized = predicted * likelihood
    evidence = float(unnormalized.sum())
    if evidence <= 0.0:
        raise ValueError("interactive observation has zero probability")
    return InteractiveBeliefUpdate(unnormalized / evidence, evidence)


@dataclass(frozen=True)
class LevelKResult:
    row_policies: tuple[np.ndarray, ...]
    column_policies: tuple[np.ndarray, ...]


def finite_level_logit_reasoning(
    row_payoff: Sequence,
    column_payoff: Sequence,
    *,
    levels: int,
    rationality: float = 1.0,
    row_level_zero: Sequence[float] | None = None,
    column_level_zero: Sequence[float] | None = None,
) -> LevelKResult:
    """Finite level-k logit responses for a one-shot opponent-model hierarchy."""

    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or row.shape != column.shape
        or min(row.shape) == 0
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or levels < 0
        or not isfinite(rationality)
        or rationality < 0.0
    ):
        raise ValueError("level-k game settings are invalid")
    row_zero = (
        np.full(row.shape[0], 1.0 / row.shape[0])
        if row_level_zero is None
        else _belief(row_level_zero, row.shape[0])
    )
    column_zero = (
        np.full(row.shape[1], 1.0 / row.shape[1])
        if column_level_zero is None
        else _belief(column_level_zero, row.shape[1])
    )
    row_policies = [row_zero]
    column_policies = [column_zero]
    for _ in range(levels):
        row_policies.append(softmax(rationality * (row @ column_policies[-1])))
        column_policies.append(softmax(rationality * (row_policies[-2] @ column)))
    return LevelKResult(tuple(row_policies), tuple(column_policies))
