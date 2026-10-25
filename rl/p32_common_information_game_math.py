"""P32 common-information beliefs, occupancy games, policy graphs, and BCE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if (
        result.ndim != 1
        or result.size == 0
        or np.any(~np.isfinite(result))
        or np.any(result < 0.0)
        or not np.isclose(result.sum(), 1.0)
    ):
        raise ValueError(f"{name} must be a finite probability vector")
    return result


def common_information_belief_update(
    prior: Sequence[float],
    action_likelihood: Sequence[float],
    transition: Sequence[Sequence[float]],
    observation_likelihood: Sequence[float],
) -> np.ndarray:
    """Bayes update after a public action and public observation.

    ``action_likelihood[s]`` is the probability of the observed public action
    in hidden state ``s``. ``observation_likelihood[s']`` is the probability of
    the observed public signal after the transition.
    """

    belief = _probability_vector(prior, "prior")
    action = np.asarray(action_likelihood, dtype=np.float64)
    dynamics = np.asarray(transition, dtype=np.float64)
    observation = np.asarray(observation_likelihood, dtype=np.float64)
    if (
        action.shape != belief.shape
        or observation.shape != belief.shape
        or dynamics.shape != (belief.size, belief.size)
        or np.any(~np.isfinite(action))
        or np.any(~np.isfinite(observation))
        or np.any(action < 0.0)
        or np.any(observation < 0.0)
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=1), 1.0)
    ):
        raise ValueError("common-information update inputs are invalid")
    predictive = (belief * action) @ dynamics
    posterior = predictive * observation
    normalizer = posterior.sum()
    if normalizer <= 0.0:
        raise ValueError("observed common information has zero probability")
    return posterior / normalizer


def occupancy_state_transition(
    occupancy: Sequence,
    first_policy: Sequence,
    second_policy: Sequence,
    kernel: Sequence,
) -> np.ndarray:
    """Advance a two-agent occupancy state through decentralized policies.

    Occupancy has axes ``[state, type1, type2]``; policies map private type to
    action; the kernel has axes
    ``[state,type1,type2,action1,action2,next_state,next_type1,next_type2]``.
    """

    distribution = np.asarray(occupancy, dtype=np.float64)
    policy_one = np.asarray(first_policy, dtype=np.float64)
    policy_two = np.asarray(second_policy, dtype=np.float64)
    dynamics = np.asarray(kernel, dtype=np.float64)
    if distribution.ndim != 3 or min(distribution.shape) == 0:
        raise ValueError("occupancy must have state and two private-type axes")
    states, types_one, types_two = distribution.shape
    if policy_one.ndim != 2 or policy_one.shape[0] != types_one:
        raise ValueError("first policy has inconsistent private types")
    if policy_two.ndim != 2 or policy_two.shape[0] != types_two:
        raise ValueError("second policy has inconsistent private types")
    actions_one = policy_one.shape[1]
    actions_two = policy_two.shape[1]
    expected_shape = (
        states,
        types_one,
        types_two,
        actions_one,
        actions_two,
        states,
        types_one,
        types_two,
    )
    arrays = (distribution, policy_one, policy_two, dynamics)
    if (
        dynamics.shape != expected_shape
        or any(np.any(~np.isfinite(value)) for value in arrays)
        or any(np.any(value < 0.0) for value in arrays)
        or not np.isclose(distribution.sum(), 1.0)
        or not np.allclose(policy_one.sum(axis=1), 1.0)
        or not np.allclose(policy_two.sum(axis=1), 1.0)
        or not np.allclose(dynamics.sum(axis=(5, 6, 7)), 1.0)
    ):
        raise ValueError("occupancy transition inputs are invalid")
    updated = np.einsum(
        "stu,ta,ub,stuabijk->ijk",
        distribution,
        policy_one,
        policy_two,
        dynamics,
    )
    return updated / updated.sum()


@dataclass(frozen=True)
class PolicyGraphResult:
    expected_return: float
    stage_rewards: np.ndarray
    final_occupancy: np.ndarray


def evaluate_two_agent_policy_graph(
    initial_state: Sequence[float],
    initial_nodes: tuple[int, int],
    transition: Sequence,
    observation: Sequence,
    reward: Sequence,
    first_action_policy: Sequence,
    second_action_policy: Sequence,
    first_node_transition: Sequence,
    second_node_transition: Sequence,
    *,
    horizon: int,
    discount: float = 1.0,
) -> PolicyGraphResult:
    """Evaluate a finite-horizon two-agent Dec-POMDP policy graph exactly."""

    state = _probability_vector(initial_state, "initial state")
    dynamics = np.asarray(transition, dtype=np.float64)
    sensor = np.asarray(observation, dtype=np.float64)
    payoff = np.asarray(reward, dtype=np.float64)
    first_actions = np.asarray(first_action_policy, dtype=np.float64)
    second_actions = np.asarray(second_action_policy, dtype=np.float64)
    first_nodes = np.asarray(first_node_transition, dtype=np.float64)
    second_nodes = np.asarray(second_node_transition, dtype=np.float64)
    states = state.size
    if dynamics.ndim != 4:
        raise ValueError("transition must have state, two actions, and next state")
    _, actions_one, actions_two, next_states = dynamics.shape
    nodes_one, policy_actions_one = first_actions.shape
    nodes_two, policy_actions_two = second_actions.shape
    if sensor.ndim != 5:
        raise ValueError("observation kernel must include two observation axes")
    observations_one, observations_two = sensor.shape[-2:]
    expected_shapes = (
        dynamics.shape[:1] == (states,),
        next_states == states,
        payoff.shape == (states, actions_one, actions_two),
        policy_actions_one == actions_one,
        policy_actions_two == actions_two,
        sensor.shape[:3] == (states, actions_one, actions_two),
        first_nodes.shape == (nodes_one, observations_one, nodes_one),
        second_nodes.shape == (nodes_two, observations_two, nodes_two),
        0 <= initial_nodes[0] < nodes_one,
        0 <= initial_nodes[1] < nodes_two,
        horizon >= 1,
        0.0 <= discount <= 1.0,
    )
    arrays = (
        dynamics,
        sensor,
        payoff,
        first_actions,
        second_actions,
        first_nodes,
        second_nodes,
    )
    if (
        not all(expected_shapes)
        or any(np.any(~np.isfinite(value)) for value in arrays)
        or np.any(dynamics < 0.0)
        or np.any(sensor < 0.0)
        or np.any(first_actions < 0.0)
        or np.any(second_actions < 0.0)
        or np.any(first_nodes < 0.0)
        or np.any(second_nodes < 0.0)
        or not np.allclose(dynamics.sum(axis=3), 1.0)
        or not np.allclose(sensor.sum(axis=(3, 4)), 1.0)
        or not np.allclose(first_actions.sum(axis=1), 1.0)
        or not np.allclose(second_actions.sum(axis=1), 1.0)
        or not np.allclose(first_nodes.sum(axis=2), 1.0)
        or not np.allclose(second_nodes.sum(axis=2), 1.0)
    ):
        raise ValueError("policy-graph inputs are invalid")
    occupancy = np.zeros((states, nodes_one, nodes_two))
    occupancy[:, initial_nodes[0], initial_nodes[1]] = state
    stage_rewards = []
    for _ in range(horizon):
        expected = np.einsum(
            "sij,ia,jb,sab->", occupancy, first_actions, second_actions, payoff
        )
        stage_rewards.append(float(expected))
        occupancy = np.einsum(
            "sij,ia,jb,sabk,kabuv,iup,jvq->kpq",
            occupancy,
            first_actions,
            second_actions,
            dynamics,
            sensor,
            first_nodes,
            second_nodes,
        )
    discounted = sum(
        discount**index * value for index, value in enumerate(stage_rewards)
    )
    return PolicyGraphResult(
        float(discounted), np.asarray(stage_rewards), occupancy
    )


@dataclass(frozen=True)
class BayesianCorrelatedEquilibrium:
    joint_distribution: np.ndarray
    expected_payoffs: np.ndarray
    objective: float
    minimum_obedience_slack: float


def bayesian_correlated_equilibrium(
    prior: Sequence,
    payoffs: Sequence,
    *,
    welfare_weights: Sequence[float] = (1.0, 1.0),
) -> BayesianCorrelatedEquilibrium:
    """Welfare-optimal BCE for a finite two-player Bayesian game."""

    type_prior = np.asarray(prior, dtype=np.float64)
    utility = np.asarray(payoffs, dtype=np.float64)
    weights = np.asarray(welfare_weights, dtype=np.float64)
    if type_prior.ndim != 2 or min(type_prior.shape) == 0:
        raise ValueError("prior must have two type axes")
    types_one, types_two = type_prior.shape
    if utility.ndim != 5 or utility.shape[:3] != (2, types_one, types_two):
        raise ValueError("payoffs must have player, type, type, action, action axes")
    actions_one, actions_two = utility.shape[-2:]
    if (
        weights.shape != (2,)
        or np.any(~np.isfinite(type_prior))
        or np.any(type_prior < 0.0)
        or not np.isclose(type_prior.sum(), 1.0)
        or np.any(~np.isfinite(utility))
        or np.any(~np.isfinite(weights))
    ):
        raise ValueError("BCE inputs are invalid")
    shape = (types_one, types_two, actions_one, actions_two)
    variables = int(np.prod(shape))
    welfare = weights[0] * utility[0] + weights[1] * utility[1]
    objective = -(welfare.reshape(-1))
    equality_rows = []
    equality_rhs = []
    for first_type in range(types_one):
        for second_type in range(types_two):
            row = np.zeros(shape)
            row[first_type, second_type, :, :] = 1.0
            equality_rows.append(row.reshape(-1))
            equality_rhs.append(type_prior[first_type, second_type])
    obedience_rows = []
    for player in range(2):
        own_types = types_one if player == 0 else types_two
        own_actions = actions_one if player == 0 else actions_two
        for own_type in range(own_types):
            for recommended in range(own_actions):
                for deviation in range(own_actions):
                    if deviation == recommended:
                        continue
                    row = np.zeros(shape)
                    if player == 0:
                        for other_type in range(types_two):
                            for other_action in range(actions_two):
                                row[own_type, other_type, recommended, other_action] = -(
                                    utility[
                                        0,
                                        own_type,
                                        other_type,
                                        recommended,
                                        other_action,
                                    ]
                                    - utility[
                                        0,
                                        own_type,
                                        other_type,
                                        deviation,
                                        other_action,
                                    ]
                                )
                    else:
                        for other_type in range(types_one):
                            for other_action in range(actions_one):
                                row[other_type, own_type, other_action, recommended] = -(
                                    utility[
                                        1,
                                        other_type,
                                        own_type,
                                        other_action,
                                        recommended,
                                    ]
                                    - utility[
                                        1,
                                        other_type,
                                        own_type,
                                        other_action,
                                        deviation,
                                    ]
                                )
                    obedience_rows.append(row.reshape(-1))
    solved = linprog(
        objective,
        A_ub=np.asarray(obedience_rows) if obedience_rows else None,
        b_ub=np.zeros(len(obedience_rows)) if obedience_rows else None,
        A_eq=np.asarray(equality_rows),
        b_eq=np.asarray(equality_rhs),
        bounds=[(0.0, None)] * variables,
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"Bayesian correlated equilibrium failed: {solved.message}")
    joint = np.maximum(solved.x.reshape(shape), 0.0)
    slacks = -np.asarray(obedience_rows) @ solved.x if obedience_rows else np.array([0.0])
    expected = np.array([np.sum(joint * utility[player]) for player in range(2)])
    return BayesianCorrelatedEquilibrium(
        joint,
        expected,
        float(weights @ expected),
        float(np.min(slacks)),
    )
