"""P27 constrained occupancy-measure and budgeted MDP algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


def _discounted_inputs(
    transition: Sequence,
    reward: Sequence,
    initial: Sequence[float],
    discount: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    kernel = np.asarray(transition, dtype=np.float64)
    payoff = np.asarray(reward, dtype=np.float64)
    start = np.asarray(initial, dtype=np.float64)
    if (
        kernel.ndim != 3
        or kernel.shape[0] != kernel.shape[2]
        or payoff.shape != kernel.shape[:2]
        or start.shape != (kernel.shape[0],)
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or np.any(~np.isfinite(payoff))
        or np.any(~np.isfinite(start))
        or np.any(start < 0.0)
        or not np.isclose(start.sum(), 1.0)
        or not isfinite(discount)
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("discounted MDP inputs are invalid")
    return kernel, payoff, start


@dataclass(frozen=True)
class CMDPResult:
    occupancy: np.ndarray
    policy: np.ndarray
    expected_reward: float
    expected_costs: np.ndarray
    flow_residual: float
    budget_violations: np.ndarray
    budget_shadow_prices: np.ndarray


def solve_discounted_cmdp(
    transition: Sequence,
    reward: Sequence,
    costs: Sequence,
    initial: Sequence[float],
    budgets: Sequence[float],
    *,
    discount: float,
) -> CMDPResult:
    """Solve a finite discounted CMDP as an unnormalized occupancy LP.

    The occupancy mass is ``1 / (1 - discount)``. Consequently, rewards,
    costs, and budgets use ordinary discounted-sum units rather than a
    normalized convention.
    """

    kernel, payoff, start = _discounted_inputs(
        transition, reward, initial, discount
    )
    states, actions = payoff.shape
    resource = np.asarray(costs, dtype=np.float64)
    limit = np.asarray(budgets, dtype=np.float64)
    if resource.ndim == 2:
        resource = resource[None, ...]
    if (
        resource.ndim != 3
        or resource.shape[1:] != (states, actions)
        or limit.shape != (resource.shape[0],)
        or np.any(~np.isfinite(resource))
        or np.any(~np.isfinite(limit))
    ):
        raise ValueError("CMDP costs and budgets are invalid")

    variables = states * actions
    flow = np.zeros((states, variables), dtype=np.float64)
    for state in range(states):
        for action in range(actions):
            column = state * actions + action
            flow[state, column] += 1.0
            flow[:, column] -= discount * kernel[state, action]
    flat_costs = resource.reshape(resource.shape[0], variables)
    result = linprog(
        -payoff.ravel(),
        A_ub=flat_costs,
        b_ub=limit,
        A_eq=flow,
        b_eq=start,
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        raise ValueError(f"CMDP occupancy LP is infeasible: {result.message}")
    occupancy = result.x.reshape(states, actions)
    state_mass = occupancy.sum(axis=1, keepdims=True)
    policy = np.divide(
        occupancy,
        state_mass,
        out=np.full_like(occupancy, 1.0 / actions),
        where=state_mass > 1e-12,
    )
    expected_costs = flat_costs @ result.x
    shadow = np.zeros(resource.shape[0], dtype=np.float64)
    if getattr(result, "ineqlin", None) is not None:
        shadow = np.maximum(-np.asarray(result.ineqlin.marginals), 0.0)
    return CMDPResult(
        occupancy,
        policy,
        float(np.sum(occupancy * payoff)),
        expected_costs,
        float(np.max(np.abs(flow @ result.x - start))),
        np.maximum(expected_costs - limit, 0.0),
        shadow,
    )


def evaluate_discounted_policy(
    transition: Sequence,
    reward: Sequence,
    initial: Sequence[float],
    policy: Sequence,
    *,
    discount: float,
) -> tuple[float, np.ndarray]:
    """Return discounted start value and the state-value vector."""

    kernel, payoff, start = _discounted_inputs(
        transition, reward, initial, discount
    )
    strategy = np.asarray(policy, dtype=np.float64)
    if (
        strategy.shape != payoff.shape
        or np.any(~np.isfinite(strategy))
        or np.any(strategy < 0.0)
        or not np.allclose(strategy.sum(axis=1), 1.0)
    ):
        raise ValueError("policy must contain one distribution per state")
    policy_kernel = np.einsum("sa,san->sn", strategy, kernel)
    policy_reward = np.sum(strategy * payoff, axis=1)
    values = np.linalg.solve(
        np.eye(payoff.shape[0]) - discount * policy_kernel,
        policy_reward,
    )
    return float(start @ values), values


@dataclass(frozen=True)
class BudgetedMDPResult:
    values: np.ndarray
    policy: np.ndarray
    feasible: np.ndarray
    horizon: int
    maximum_budget: int


def finite_horizon_budgeted_mdp(
    transition: Sequence,
    transition_reward: Sequence,
    transition_cost: Sequence,
    *,
    horizon: int,
    maximum_budget: int,
    discount: float = 1.0,
) -> BudgetedMDPResult:
    """Dynamic programming for a pathwise integer-budget MDP.

    An action is feasible only if every positive-probability successor stays
    inside the remaining budget. This is the hard-budget, not expected-budget,
    interpretation.
    """

    kernel = np.asarray(transition, dtype=np.float64)
    reward = np.asarray(transition_reward, dtype=np.float64)
    cost = np.asarray(transition_cost)
    if reward.ndim == 2 and kernel.ndim == 3:
        reward = np.broadcast_to(reward[:, :, None], kernel.shape)
    if (
        kernel.ndim != 3
        or kernel.shape[0] != kernel.shape[2]
        or reward.shape != kernel.shape
        or cost.shape != kernel.shape
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or np.any(~np.isfinite(reward))
        or not np.issubdtype(cost.dtype, np.integer)
        or np.any(cost < 0)
        or horizon < 1
        or maximum_budget < 0
        or not isfinite(discount)
        or not 0.0 <= discount <= 1.0
    ):
        raise ValueError("budgeted MDP inputs are invalid")
    states, actions, _ = kernel.shape
    values = np.zeros((horizon + 1, states, maximum_budget + 1))
    policy = np.full((horizon, states, maximum_budget + 1), -1, dtype=np.int64)
    feasible = np.zeros_like(policy, dtype=bool)
    for time in range(horizon - 1, -1, -1):
        for state in range(states):
            for budget in range(maximum_budget + 1):
                best = -np.inf
                best_action = -1
                for action in range(actions):
                    successors = np.flatnonzero(kernel[state, action] > 0.0)
                    if any(cost[state, action, nxt] > budget for nxt in successors):
                        continue
                    candidate = sum(
                        kernel[state, action, nxt]
                        * (
                            reward[state, action, nxt]
                            + discount
                            * values[
                                time + 1,
                                nxt,
                                budget - int(cost[state, action, nxt]),
                            ]
                        )
                        for nxt in successors
                    )
                    if candidate > best:
                        best = float(candidate)
                        best_action = action
                if best_action >= 0:
                    values[time, state, budget] = best
                    policy[time, state, budget] = best_action
                    feasible[time, state, budget] = True
                else:
                    values[time, state, budget] = -np.inf
    return BudgetedMDPResult(values, policy, feasible, horizon, maximum_budget)


def pareto_prune(
    rewards: Sequence[float],
    costs: Sequence[Sequence[float]],
    *,
    tolerance: float = 1e-12,
) -> np.ndarray:
    """Indices not dominated under reward maximization and cost minimization."""

    utility = np.asarray(rewards, dtype=np.float64)
    resource = np.asarray(costs, dtype=np.float64)
    if resource.ndim == 1:
        resource = resource[:, None]
    if (
        utility.ndim != 1
        or resource.ndim != 2
        or resource.shape[0] != utility.size
        or utility.size == 0
        or np.any(~np.isfinite(utility))
        or np.any(~np.isfinite(resource))
        or tolerance < 0.0
    ):
        raise ValueError("Pareto frontier inputs are invalid")
    keep = np.ones(utility.size, dtype=bool)
    for candidate in range(utility.size):
        for rival in range(utility.size):
            if candidate == rival:
                continue
            weak = (
                utility[rival] >= utility[candidate] - tolerance
                and np.all(resource[rival] <= resource[candidate] + tolerance)
            )
            strict = (
                utility[rival] > utility[candidate] + tolerance
                or np.any(resource[rival] < resource[candidate] - tolerance)
            )
            if weak and strict:
                keep[candidate] = False
                break
    return np.flatnonzero(keep)
