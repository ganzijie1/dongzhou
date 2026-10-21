"""Reachability, barrier certificates, distributional robustness, and interdiction."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog

from rl.strategic_flow import CapacityNetwork, Edge


State = Hashable
Control = Hashable
Disturbance = Hashable
Action = Hashable


@dataclass(frozen=True)
class ReachabilityResult:
    """Finite-horizon robust reach-avoid sets and a witnessing feedback policy."""

    reachable: tuple[frozenset[State], ...]
    policy: Mapping[tuple[int, State], Control]

    def can_reach(self, state: State, *, remaining_steps: int | None = None) -> bool:
        index = len(self.reachable) - 1 if remaining_steps is None else int(remaining_steps)
        if not 0 <= index < len(self.reachable):
            raise ValueError("remaining_steps is outside the reachability horizon")
        return state in self.reachable[index]


def hamilton_jacobi_reachability(
    states: Sequence[State],
    controls: Callable[[State], Sequence[Control]],
    disturbances: Callable[[State, Control], Sequence[Disturbance]],
    transition: Callable[[State, Control, Disturbance], State],
    targets: Sequence[State],
    *,
    unsafe: Sequence[State] = (),
    horizon: int = 4,
) -> ReachabilityResult:
    """Solve a discrete HJ-Isaacs reach-avoid game by backward recursion.

    A state is winning when there exists a control whose every admissible
    disturbance leads into the previous winning set.
    """

    if horizon < 0:
        raise ValueError("reachability horizon must be non-negative")
    state_set = frozenset(states)
    if not state_set:
        raise ValueError("reachability needs at least one state")
    unsafe_set = frozenset(unsafe)
    target_set = frozenset(targets) & state_set - unsafe_set
    if not target_set:
        raise ValueError("reachability needs a safe target state")
    layers = [target_set]
    policy: dict[tuple[int, State], Control] = {}
    for step in range(1, horizon + 1):
        previous = layers[-1]
        winning = set(previous)
        for state in sorted(state_set - unsafe_set - previous, key=repr):
            for control in sorted(controls(state), key=repr):
                possible = tuple(disturbances(state, control))
                if not possible:
                    possible = (None,)
                successors = {
                    transition(state, control, disturbance)
                    for disturbance in possible
                }
                if successors and successors <= previous:
                    winning.add(state)
                    policy[(step, state)] = control
                    break
        layers.append(frozenset(winning))
    return ReachabilityResult(tuple(layers), policy)


@dataclass(frozen=True)
class BarrierAction:
    action: Action
    next_state: State
    barrier_value: float
    margin: float
    safe: bool


def control_barrier_filter(
    state: State,
    actions: Sequence[Action],
    transition: Callable[[State, Action], State],
    barrier: Callable[[State], float],
    *,
    alpha: float = 0.2,
) -> tuple[BarrierAction, ...]:
    """Apply the discrete CBF condition h(x+) >= (1-alpha) h(x)."""

    if not 0.0 < alpha <= 1.0:
        raise ValueError("barrier alpha must be in (0, 1]")
    current = float(barrier(state))
    if not isfinite(current):
        raise ValueError("barrier values must be finite")
    results = []
    for action in actions:
        next_state = transition(state, action)
        value = float(barrier(next_state))
        if not isfinite(value):
            raise ValueError("barrier values must be finite")
        margin = value - (1.0 - alpha) * current
        results.append(BarrierAction(action, next_state, value, margin, margin >= -1e-12))
    return tuple(results)


@dataclass(frozen=True)
class DistributionallyRobustResult:
    worst_case_expectation: float
    adversarial_distribution: tuple[float, ...]
    transport_plan: np.ndarray
    transport_cost: float


def wasserstein_worst_case_expectation(
    nominal: Sequence[float],
    losses: Sequence[float],
    distances: Sequence[Sequence[float]],
    *,
    radius: float,
) -> DistributionallyRobustResult:
    """Maximize expected loss in a finite 1-Wasserstein ambiguity ball."""

    probability = np.asarray(nominal, dtype=np.float64)
    loss = np.asarray(losses, dtype=np.float64)
    metric = np.asarray(distances, dtype=np.float64)
    if probability.ndim != 1 or loss.shape != probability.shape or probability.size == 0:
        raise ValueError("nominal probabilities and losses must be aligned vectors")
    if metric.shape != (probability.size, probability.size):
        raise ValueError("distance matrix has invalid dimensions")
    if any(np.any(~np.isfinite(array)) for array in (probability, loss, metric)):
        raise ValueError("distributionally robust inputs must be finite")
    if np.any(probability < 0.0) or np.any(metric < 0.0):
        raise ValueError("probabilities and transport distances must be non-negative")
    if not isfinite(radius) or radius < 0.0 or probability.sum() <= 0.0:
        raise ValueError("Wasserstein radius and nominal mass are invalid")
    probability = probability / probability.sum()
    size = probability.size
    objective = -np.tile(loss, size)
    equality = np.zeros((size, size * size), dtype=np.float64)
    for source in range(size):
        equality[source, source * size : (source + 1) * size] = 1.0
    result = linprog(
        objective,
        A_ub=metric.reshape(1, -1),
        b_ub=np.asarray([radius], dtype=np.float64),
        A_eq=equality,
        b_eq=probability,
        bounds=[(0.0, None)] * (size * size),
        method="highs",
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"Wasserstein DRO failed: {result.message}")
    plan = np.asarray(result.x, dtype=np.float64).reshape(size, size)
    adversarial = plan.sum(axis=0)
    return DistributionallyRobustResult(
        float(adversarial @ loss),
        tuple(float(value) for value in adversarial),
        plan,
        float(np.sum(plan * metric)),
    )


@dataclass(frozen=True)
class InterdictionResult:
    removed_edges: tuple[Edge, ...]
    remaining_flow: float
    spent_budget: float
    examined_subsets: int


def solve_network_interdiction(
    network: CapacityNetwork,
    source: State,
    sink: State,
    *,
    budget: float,
    interdiction_costs: Mapping[Edge, float] | None = None,
    candidate_edges: Sequence[Edge] | None = None,
    maximum_candidates: int = 20,
) -> InterdictionResult:
    """Solve a small exact leader-follower network interdiction problem."""

    if not isfinite(budget) or budget < 0.0:
        raise ValueError("interdiction budget must be finite and non-negative")
    candidates = tuple(
        sorted(candidate_edges or tuple(network.capacities), key=repr)
    )
    if len(candidates) > maximum_candidates:
        raise ValueError("exact interdiction candidate set exceeds configured limit")
    if any(edge not in network.capacities for edge in candidates):
        raise ValueError("interdiction candidate is not a network edge")
    costs = {
        edge: float((interdiction_costs or {}).get(edge, 1.0))
        for edge in candidates
    }
    if any(not isfinite(cost) or cost <= 0.0 for cost in costs.values()):
        raise ValueError("interdiction costs must be positive and finite")
    best_edges: tuple[Edge, ...] = ()
    best_flow = network.max_flow(source, sink).value
    best_spent = 0.0
    examined = 1
    for count in range(1, len(candidates) + 1):
        for subset in combinations(candidates, count):
            spent = sum(costs[edge] for edge in subset)
            if spent > budget + 1e-12:
                continue
            examined += 1
            removed = set(subset)
            capacities = {
                edge: capacity
                for edge, capacity in network.capacities.items()
                if edge not in removed
            }
            flow = CapacityNetwork(capacities).max_flow(source, sink).value
            candidate_key = (flow, spent, tuple(map(repr, subset)))
            best_key = (best_flow, best_spent, tuple(map(repr, best_edges)))
            if candidate_key < best_key:
                best_edges = tuple(subset)
                best_flow = flow
                best_spent = spent
    return InterdictionResult(best_edges, best_flow, best_spent, examined)
