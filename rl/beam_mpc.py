"""Snapshot-based beam-search model predictive control for Mengde battles.

The native simulator is the dynamics model.  Search is deliberately receding
horizon: only the first action is returned and a fresh tree is built after the
real environment advances.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from rl.happo import HAPPO, decision_role, happo_decision
from rl.mappo import Decision, select_agent_actions


Prior = Callable[[Any, np.ndarray, Decision], np.ndarray]


@dataclass(frozen=True)
class BeamMPCConfig:
    horizon: int = 3
    beam_width: int = 6
    candidates_per_node: int = 6
    gamma: float = 0.99
    leaf_weight: float = 2.0
    prior_weight: float = 0.0
    terminal_value: float = 100.0


@dataclass
class BeamNode:
    snapshot: dict[str, Any]
    observation: np.ndarray
    score: float
    first_action: int
    first_choice: int
    depth: int
    terminated: bool


@dataclass(frozen=True)
class BeamMPCResult:
    action: int
    choice: int
    score: float
    expanded_nodes: int
    depth: int
    root_scores: dict[int, float]


def same_side(left: int, right: int) -> bool:
    """Match the game's player/allied-force convention."""
    return left == right or bool((left & 0x03) and (right & 0x03))


def material_value(units: list[dict[str, Any]], force: int) -> float:
    value = 0.0
    for unit in units:
        hp = max(0.0, float(unit.get("hp", 0)))
        maximum = max(1.0, float(unit.get("max_hp", 1)))
        alive = float(hp > 0.0)
        signed = 1.0 if same_side(int(unit["force"]), force) else -1.0
        value += signed * (hp / maximum + 0.35 * alive)
    return value


def action_heuristic(action: dict[str, Any], units: list[dict[str, Any]]) -> float:
    """Cheap ordering heuristic; simulator returns determine the final score."""
    by_id = {int(unit["id"]): unit for unit in units}
    actor = by_id.get(int(action["unit"]), {})
    target_value = action.get("target")
    target = by_id.get(int(target_value)) if target_value is not None else None
    action_type = int(action.get("type", 0))
    score = 0.0
    if action_type in (1, 2):
        score += 2.0
    if action_type == 3:
        score -= 0.3
    if action.get("skill"):
        score += 0.35
    if target is not None:
        hostile = not same_side(int(actor.get("force", 0)), int(target["force"]))
        missing = 1.0 - float(target.get("hp", 0)) / max(1.0, float(target.get("max_hp", 1)))
        score += (1.0 + missing) if hostile else missing
    score += 0.01 * float(action.get("expected_damage", action.get("damage", 0)))
    return score


class HAPPOPrior:
    def __init__(self, model: HAPPO, width: int, height: int) -> None:
        self.model = model
        self.width = width
        self.height = height

    def __call__(self, env: Any, observation: np.ndarray, decision: Decision) -> np.ndarray:
        rich = happo_decision(
            env, observation, self.width, self.height, actions=decision.actions
        )
        return self.model.score(rich, decision_role(env, rich))


class BeamMPC:
    def __init__(self, config: BeamMPCConfig | None = None) -> None:
        self.config = config or BeamMPCConfig()
        if (
            self.config.horizon < 1
            or self.config.beam_width < 1
            or self.config.candidates_per_node < 1
        ):
            raise ValueError("horizon, beam_width, and candidates_per_node must be positive")

    def search(
        self,
        env: Any,
        observation: np.ndarray,
        *,
        controlled_force: int | None = None,
        prior: Prior | None = None,
    ) -> BeamMPCResult:
        root_snapshot = env.snapshot()
        root_units = env.unit_info()
        root_actions = env.list_actions()
        root_agent, selected = select_agent_actions(root_actions)
        actor = next(unit for unit in root_units if int(unit["id"]) == root_agent)
        force = int(actor["force"]) if controlled_force is None else int(controlled_force)
        root_material = material_value(root_units, force)
        root_decision = self._decision(root_agent, selected)
        root_priors = self._priors(env, observation, root_decision, prior)
        root_scores: dict[int, float] = {}
        frontier: list[BeamNode] = []
        expanded = 0
        episode_limit = getattr(env, "max_episode_actions", None)
        used_actions = int(root_snapshot.get("agent_actions", 0))
        if episode_limit is not None and used_actions + self.config.horizon >= int(episode_limit):
            choice = self._rank(selected, root_units, root_priors)[0]
            score = action_heuristic(selected[choice], root_units)
            score += self.config.prior_weight * float(root_priors[choice])
            return BeamMPCResult(
                int(selected[choice]["index"]), choice, score, 0, 0, {choice: score}
            )
        try:
            candidates = self._rank(selected, root_units, root_priors)
            for choice in candidates:
                self._restore(env, root_snapshot)
                action = int(selected[choice]["index"])
                if not self._action_available(env, action):
                    continue
                next_obs, reward, terminated, truncated, info = env.step(action)
                done = bool(terminated or truncated)
                snapshot = env.snapshot()
                score = self._reward(float(reward), force)
                score += self.config.prior_weight * float(root_priors[choice])
                score += self._leaf(env, info, force, root_material, done)
                root_scores[choice] = score
                frontier.append(BeamNode(
                    snapshot, next_obs.copy(), score, action, choice, 1, done
                ))
                expanded += 1

            frontier = self._trim(frontier)
            for depth in range(1, self.config.horizon):
                children: list[BeamNode] = []
                for node in frontier:
                    if node.terminated:
                        children.append(node)
                        continue
                    self._restore(env, node.snapshot)
                    actions = env.list_actions()
                    agent_id, choices = select_agent_actions(actions)
                    units = env.unit_info()
                    acting_unit = next(
                        unit for unit in units if int(unit["id"]) == agent_id
                    )
                    # End the finite horizon at the opponent boundary. Expanding
                    # enemy choices under a maximizing beam would assume that the
                    # opponent cooperates; opponent modelling belongs in a caller-
                    # supplied value function instead.
                    if not same_side(int(acting_unit["force"]), force):
                        children.append(node)
                        continue
                    decision = self._decision(agent_id, choices)
                    priors = self._priors(env, node.observation, decision, prior)
                    added = False
                    for choice in self._rank(choices, units, priors):
                        self._restore(env, node.snapshot)
                        action = int(choices[choice]["index"])
                        if not self._action_available(env, action):
                            continue
                        next_obs, reward, terminated, truncated, info = env.step(
                            action
                        )
                        done = bool(terminated or truncated)
                        snapshot = env.snapshot()
                        score = node.score
                        score += (self.config.gamma ** depth) * self._reward(float(reward), force)
                        score += self.config.prior_weight * float(priors[choice])
                        score += self._leaf(env, info, force, root_material, done)
                        children.append(BeamNode(
                            snapshot, next_obs.copy(), score, node.first_action,
                            node.first_choice, depth + 1, done,
                        ))
                        added = True
                        expanded += 1
                    if not added:
                        children.append(node)
                frontier = self._trim(children)
                for node in frontier:
                    root_scores[node.first_choice] = max(
                        root_scores.get(node.first_choice, -np.inf), node.score
                    )
                if all(node.terminated for node in frontier):
                    break
            best = max(frontier, key=lambda node: node.score)
            return BeamMPCResult(
                best.first_action, best.first_choice, best.score, expanded,
                best.depth, root_scores,
            )
        finally:
            self._restore(env, root_snapshot)

    @staticmethod
    def _decision(agent_id: int, actions: list[dict[str, Any]]) -> Decision:
        # A prior only needs identity and legal-action alignment. HAPPOPrior
        # reconstructs the rich observation through happo_decision.
        return Decision(
            agent_id, actions, np.empty(0, np.float32),
            np.empty((len(actions), 0), np.float32),
        )

    @staticmethod
    def _restore(env: Any, snapshot: dict[str, Any]) -> None:
        try:
            env.restore(snapshot, restart_process=False)
        except TypeError as error:
            if "restart_process" not in str(error):
                raise
            env.restore(snapshot)

    @staticmethod
    def _action_available(env: Any, action: int) -> bool:
        count = getattr(env, "_action_count", None)
        return count is None or 0 <= action < int(count)

    @staticmethod
    def _priors(
        env: Any, observation: np.ndarray, decision: Decision, prior: Prior | None
    ) -> np.ndarray:
        if prior is None:
            return np.zeros(len(decision.actions), dtype=np.float32)
        values = np.asarray(prior(env, observation, decision), dtype=np.float32)
        if values.shape != (len(decision.actions),):
            raise ValueError("prior must return one score per candidate action")
        return values

    def _rank(
        self, actions: list[dict[str, Any]], units: list[dict[str, Any]], priors: np.ndarray
    ) -> list[int]:
        scores = [
            action_heuristic(action, units)
            + self.config.prior_weight * float(priors[index])
            for index, action in enumerate(actions)
        ]
        order = sorted(range(len(actions)), key=lambda index: (-scores[index], index))
        return order[: self.config.candidates_per_node]

    def _leaf(
        self, env: Any, info: dict[str, Any], force: int,
        root_material: float, terminal: bool,
    ) -> float:
        value = self.config.leaf_weight * (
            material_value(env.unit_info(), force) - root_material
        )
        if terminal:
            status = int(info.get("status", 2))
            player_side = bool(force & 0x03)
            won = (status == 3) if player_side else (status == 4)
            if status in (3, 4):
                value += self.config.terminal_value * (1.0 if won else -1.0)
        return value

    @staticmethod
    def _reward(reward: float, force: int) -> float:
        return reward if force & 0x03 else -reward

    def _trim(self, nodes: list[BeamNode]) -> list[BeamNode]:
        return sorted(nodes, key=lambda node: (-node.score, node.first_action))[
            : self.config.beam_width
        ]
