"""Finite-horizon control, opponent learning, survival, and matching."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment


State = Hashable
Action = Hashable
Context = Hashable


@dataclass(frozen=True)
class MPCResult:
    first_action: Action
    actions: tuple[Action, ...]
    states: tuple[State, ...]
    expected_cost: float


class DiscreteMPC:
    """Finite-horizon deterministic MPC with receding-horizon first actions."""

    def __init__(self, horizon: int = 4) -> None:
        if horizon <= 0:
            raise ValueError("MPC horizon must be positive")
        self.horizon = int(horizon)

    def solve(
        self,
        initial_state: State,
        actions: Callable[[State, int], Sequence[Action]],
        transition: Callable[[State, Action, int], State],
        stage_cost: Callable[[State, Action, State, int], float],
        terminal_cost: Callable[[State], float] | None = None,
    ) -> MPCResult:
        terminal = terminal_cost or (lambda _state: 0.0)
        policy: dict[tuple[int, State], tuple[Action, State]] = {}

        @lru_cache(maxsize=None)
        def value(time: int, state: State) -> float:
            if time == self.horizon:
                result = float(terminal(state))
                if not isfinite(result):
                    raise ValueError("MPC terminal cost must be finite")
                return result
            candidates = tuple(actions(state, time))
            if not candidates:
                raise ValueError(f"MPC state has no action at time {time}: {state!r}")
            ranked = []
            for action in candidates:
                next_state = transition(state, action, time)
                immediate = float(stage_cost(state, action, next_state, time))
                if not isfinite(immediate):
                    raise ValueError("MPC stage cost must be finite")
                ranked.append((immediate + value(time + 1, next_state), repr(action), action, next_state))
            cost, _, selected, next_state = min(ranked, key=lambda item: (item[0], item[1]))
            policy[(time, state)] = (selected, next_state)
            return cost

        expected = value(0, initial_state)
        states = [initial_state]
        selected_actions = []
        state = initial_state
        for time in range(self.horizon):
            action, state = policy[(time, state)]
            selected_actions.append(action)
            states.append(state)
        return MPCResult(selected_actions[0], tuple(selected_actions), tuple(states), expected)


class DirichletOpponentModel:
    """Contextual Bayesian categorical model with a Dirichlet prior."""

    def __init__(self, actions: Sequence[Action], *, prior: float = 1.0) -> None:
        self.actions = tuple(dict.fromkeys(actions))
        if not self.actions or not isfinite(prior) or prior <= 0.0:
            raise ValueError("opponent actions and positive finite prior are required")
        self.prior = float(prior)
        self.counts: dict[Context, dict[Action, float]] = {}

    def update(self, context: Context, action: Action, *, weight: float = 1.0) -> None:
        if action not in self.actions:
            raise ValueError(f"unknown opponent action: {action!r}")
        if not isfinite(weight) or weight <= 0.0:
            raise ValueError("opponent observation weight must be positive and finite")
        counts = self.counts.setdefault(context, {})
        counts[action] = counts.get(action, 0.0) + float(weight)

    def predictive(self, context: Context) -> dict[Action, float]:
        counts = self.counts.get(context, {})
        total = len(self.actions) * self.prior + sum(counts.values())
        return {
            action: (self.prior + counts.get(action, 0.0)) / total
            for action in self.actions
        }

    def expected_payoff(
        self, context: Context, payoffs: Mapping[Action, float]
    ) -> float:
        probabilities = self.predictive(context)
        return sum(probabilities[action] * float(payoffs.get(action, 0.0)) for action in self.actions)


@dataclass(frozen=True)
class SurvivalPoint:
    time: float
    at_risk: int
    events: int
    censored: int
    hazard: float
    survival: float


class KaplanMeierEstimator:
    """Non-parametric survival and discrete hazard estimator."""

    def __init__(self) -> None:
        self.points: tuple[SurvivalPoint, ...] = ()

    def fit(self, durations: Sequence[float], events: Sequence[bool]) -> "KaplanMeierEstimator":
        if len(durations) != len(events) or not durations:
            raise ValueError("survival durations and events must be non-empty and aligned")
        observations = [(float(time), bool(event)) for time, event in zip(durations, events)]
        if any(not isfinite(time) or time < 0.0 for time, _ in observations):
            raise ValueError("survival durations must be finite and non-negative")
        at_risk = len(observations)
        survival = 1.0
        points = []
        for time in sorted({time for time, _ in observations}):
            events_at_time = sum(1 for observed_time, event in observations if observed_time == time and event)
            censored = sum(1 for observed_time, event in observations if observed_time == time and not event)
            hazard = events_at_time / at_risk
            survival *= 1.0 - hazard
            points.append(SurvivalPoint(time, at_risk, events_at_time, censored, hazard, survival))
            at_risk -= events_at_time + censored
        self.points = tuple(points)
        return self

    def survival_at(self, time: float) -> float:
        if not self.points:
            raise RuntimeError("survival estimator must be fitted first")
        value = 1.0
        for point in self.points:
            if point.time > time:
                break
            value = point.survival
        return value

    def hazard_at(self, time: float) -> float:
        if not self.points:
            raise RuntimeError("survival estimator must be fitted first")
        for point in self.points:
            if point.time == time:
                return point.hazard
        return 0.0


@dataclass(frozen=True)
class MatchingResult:
    assignments: Mapping[Hashable, Hashable]
    utility: float


def maximum_weight_matching(
    agents: Sequence[Hashable],
    tasks: Sequence[Hashable],
    utilities: Mapping[tuple[Hashable, Hashable], float],
    *,
    minimum_utility: float = 0.0,
) -> MatchingResult:
    """Maximum-weight rectangular bipartite matching with optional unmatched agents."""

    left = tuple(dict.fromkeys(agents))
    right = tuple(dict.fromkeys(tasks))
    if not isfinite(minimum_utility):
        raise ValueError("minimum_utility must be finite")
    if not left or not right:
        return MatchingResult({}, 0.0)
    # One dummy task per agent makes remaining unmatched a real optimizer choice.
    columns = len(right) + len(left)
    weights = np.full((len(left), columns), float(minimum_utility), dtype=np.float64)
    for row, agent in enumerate(left):
        for column, task in enumerate(right):
            value = float(utilities.get((agent, task), minimum_utility))
            if not isfinite(value):
                raise ValueError("matching utilities must be finite")
            weights[row, column] = value
    rows, columns = linear_sum_assignment(-weights)
    assignments: dict[Hashable, Hashable] = {}
    total = 0.0
    for row, column in zip(rows, columns):
        if column >= len(right):
            continue
        value = float(weights[row, column])
        if value + 1e-12 < minimum_utility:
            continue
        assignments[left[row]] = right[column]
        total += value
    return MatchingResult(assignments, total)
