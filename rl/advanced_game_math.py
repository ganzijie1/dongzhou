"""Stackelberg commitment and counterfactual regret minimization."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Mapping

import numpy as np
from scipy.optimize import linprog


Action = Hashable
InfoSet = Hashable


@dataclass(frozen=True)
class StackelbergSolution:
    leader_strategy: tuple[float, ...]
    follower_response: int
    leader_value: float
    follower_value: float


def solve_stackelberg_game(
    leader_payoffs: list[list[float]] | np.ndarray,
    follower_payoffs: list[list[float]] | np.ndarray,
) -> StackelbergSolution:
    """Solve an optimistic finite Stackelberg game by follower-response LPs."""

    leader = np.asarray(leader_payoffs, dtype=np.float64)
    follower = np.asarray(follower_payoffs, dtype=np.float64)
    if leader.ndim != 2 or leader.shape != follower.shape or min(leader.shape) == 0:
        raise ValueError("Stackelberg payoff matrices must be aligned and non-empty")
    if np.any(~np.isfinite(leader)) or np.any(~np.isfinite(follower)):
        raise ValueError("Stackelberg payoffs must be finite")
    leader_actions, follower_actions = leader.shape
    solutions = []
    for response in range(follower_actions):
        inequalities = []
        for alternative in range(follower_actions):
            if alternative == response:
                continue
            # The declared response must be at least as good for the follower.
            inequalities.append(follower[:, alternative] - follower[:, response])
        result = linprog(
            -leader[:, response],
            A_ub=np.asarray(inequalities) if inequalities else None,
            b_ub=np.zeros(len(inequalities)) if inequalities else None,
            A_eq=np.ones((1, leader_actions), dtype=np.float64),
            b_eq=np.ones(1, dtype=np.float64),
            bounds=[(0.0, 1.0)] * leader_actions,
            method="highs",
        )
        if not result.success or result.x is None:
            continue
        strategy = np.asarray(result.x, dtype=np.float64)
        solutions.append(
            StackelbergSolution(
                tuple(float(value) for value in strategy),
                response,
                float(strategy @ leader[:, response]),
                float(strategy @ follower[:, response]),
            )
        )
    if not solutions:
        raise RuntimeError("Stackelberg game has no feasible follower response")
    return max(
        solutions,
        key=lambda item: (
            item.leader_value,
            item.follower_value,
            -item.follower_response,
        ),
    )


@dataclass(frozen=True)
class TerminalNode:
    utility: float


@dataclass(frozen=True)
class ChanceNode:
    outcomes: Mapping[Action, tuple[float, "GameNode"]]


@dataclass(frozen=True)
class DecisionNode:
    player: int
    information_set: InfoSet
    actions: Mapping[Action, "GameNode"]


GameNode = TerminalNode | ChanceNode | DecisionNode


@dataclass(frozen=True)
class CFRResult:
    strategies: Mapping[InfoSet, Mapping[Action, float]]
    average_utility: float
    iterations: int


class CounterfactualRegretMinimizer:
    """Vanilla CFR for finite two-player zero-sum extensive-form games."""

    def __init__(self) -> None:
        self.regrets: dict[InfoSet, dict[Action, float]] = {}
        self.strategy_sums: dict[InfoSet, dict[Action, float]] = {}
        self.action_sets: dict[InfoSet, tuple[Action, ...]] = {}

    def _strategy(self, information_set: InfoSet, actions: tuple[Action, ...]) -> dict[Action, float]:
        known = self.action_sets.setdefault(information_set, actions)
        if known != actions:
            raise ValueError("all nodes in one information set need identical actions")
        regrets = self.regrets.setdefault(
            information_set, {action: 0.0 for action in actions}
        )
        self.strategy_sums.setdefault(
            information_set, {action: 0.0 for action in actions}
        )
        positive = {action: max(0.0, regrets[action]) for action in actions}
        total = sum(positive.values())
        if total <= 1e-15:
            return {action: 1.0 / len(actions) for action in actions}
        return {action: positive[action] / total for action in actions}

    def _walk(
        self,
        node: GameNode,
        reach_zero: float,
        reach_one: float,
        chance_reach: float,
        iteration_strategies: dict[InfoSet, dict[Action, float]],
    ) -> float:
        if isinstance(node, TerminalNode):
            utility = float(node.utility)
            if not isfinite(utility):
                raise ValueError("terminal utility must be finite")
            return utility
        if isinstance(node, ChanceNode):
            total_probability = sum(float(probability) for probability, _ in node.outcomes.values())
            if not np.isclose(total_probability, 1.0) or any(
                not isfinite(float(probability)) or probability < 0.0
                for probability, _ in node.outcomes.values()
            ):
                raise ValueError("chance probabilities must be finite and sum to one")
            return sum(
                float(probability)
                * self._walk(
                    child,
                    reach_zero,
                    reach_one,
                    chance_reach * float(probability),
                    iteration_strategies,
                )
                for probability, child in node.outcomes.values()
            )
        if node.player not in (0, 1) or not node.actions:
            raise ValueError("decision nodes need player 0/1 and at least one action")
        actions = tuple(node.actions)
        strategy = iteration_strategies.get(node.information_set)
        if strategy is None:
            strategy = self._strategy(node.information_set, actions)
            iteration_strategies[node.information_set] = strategy
        elif self.action_sets[node.information_set] != actions:
            raise ValueError("all nodes in one information set need identical actions")
        action_utilities = {}
        for action, child in node.actions.items():
            probability = strategy[action]
            action_utilities[action] = self._walk(
                child,
                reach_zero * probability if node.player == 0 else reach_zero,
                reach_one * probability if node.player == 1 else reach_one,
                chance_reach,
                iteration_strategies,
            )
        node_utility = sum(strategy[action] * action_utilities[action] for action in actions)
        opponent_reach = reach_one if node.player == 0 else reach_zero
        own_reach = reach_zero if node.player == 0 else reach_one
        sign = 1.0 if node.player == 0 else -1.0
        for action in actions:
            self.regrets[node.information_set][action] += (
                chance_reach
                * opponent_reach
                * sign
                * (action_utilities[action] - node_utility)
            )
            self.strategy_sums[node.information_set][action] += (
                chance_reach * own_reach * strategy[action]
            )
        return node_utility

    def solve(self, root: GameNode, *, iterations: int = 10_000) -> CFRResult:
        if iterations <= 0:
            raise ValueError("CFR iterations must be positive")
        utility = 0.0
        for _ in range(iterations):
            utility += self._walk(root, 1.0, 1.0, 1.0, {})
        averages: dict[InfoSet, dict[Action, float]] = {}
        for information_set, totals in self.strategy_sums.items():
            mass = sum(totals.values())
            if mass <= 1e-15:
                actions = self.action_sets[information_set]
                averages[information_set] = {
                    action: 1.0 / len(actions) for action in actions
                }
            else:
                averages[information_set] = {
                    action: value / mass for action, value in totals.items()
                }
        return CFRResult(averages, utility / iterations, iterations)
