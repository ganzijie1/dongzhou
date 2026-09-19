"""Joint-turn MAPF with HAPPO/CQL value priors for the playable frontend."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

from rl.happo import HAPPO, happo_decision_for_agent, normalized_role
from rl.joint_turn_planner import JointTurnPlanner
from rl.mappo import Decision, action_features, local_observation
from rl.offline_rl import CQL


def _model_candidates(filename: str, experiment: str) -> tuple[Path, ...]:
    module_root = Path(__file__).resolve().parent
    candidates = [
        module_root / "models" / "runtime" / filename,
        module_root / "models" / experiment / filename,
    ]
    if getattr(sys, "frozen", False):
        bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidates.insert(0, bundle / "rl" / "models" / "runtime" / filename)
    return tuple(candidates)


def _first_model(filename: str, experiment: str) -> Path:
    candidates = _model_candidates(filename, experiment)
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        f"runtime policy model missing: {', '.join(str(path) for path in candidates)}"
    )


class RuntimeBattlePolicy:
    """Coordinate all ready units while preserving native legal actions."""

    def __init__(
        self, *, happo_path: str | Path | None = None,
        cql_path: str | Path | None = None,
    ) -> None:
        self.happo_path = Path(happo_path) if happo_path else None
        self.cql_path = Path(cql_path) if cql_path else None
        self.happo: HAPPO | None = None
        self.cql: CQL | None = None
        self.happo_error: Exception | None = None
        self.cql_error: Exception | None = None
        self.backend = "uninitialized"
        self.planner = JointTurnPlanner()
        self.last_plan_reason = "uninitialized"
        self._map_signature: tuple[
            int, int, tuple[str, ...], tuple[tuple[int, str, int], ...]
        ] | None = None
        self._movement_costs: dict[int, list[int]] = {}

    def _load_happo(self, state_features: int) -> HAPPO:
        if self.happo is not None:
            return self.happo
        path = self.happo_path or _first_model(
            "happo.pt", "ppo_mappo_happo_comparison"
        )
        payload = torch.load(path, map_location="cpu")
        model = HAPPO(state_features, seed=2026)
        model.actors.load_state_dict(payload["actors"])
        model.critic.load_state_dict(payload["critic"])
        model.actors.eval()
        model.critic.eval()
        self.happo = model
        return model

    def _load_cql(self, state_features: int) -> CQL:
        if self.cql is not None:
            return self.cql
        path = self.cql_path or _first_model(
            "cql.pt", "offline_iql_cql_comparison"
        )
        payload = torch.load(path, map_location="cpu")
        model = CQL(state_features, seed=2026)
        model.q1.load_state_dict(payload["q1"])
        model.q2.load_state_dict(payload["q2"])
        model.q1.eval()
        model.q2.eval()
        self.cql = model
        return model

    @staticmethod
    def _decision_for_agent(
        env,
        actions: list[dict[str, Any]],
        observation: np.ndarray,
        width: int,
        height: int,
        agent_id: int,
        units: list[dict[str, Any]] | None = None,
    ) -> tuple[Decision, str]:
        selected = [
            action for action in actions if int(action["unit"]) == agent_id
        ]
        if not selected:
            raise ValueError(f"runtime policy found no actions for unit {agent_id}")
        units = env.unit_info() if units is None else units
        unit = next(item for item in units if int(item["id"]) == agent_id)
        decision = Decision(
            agent_id=agent_id,
            actions=selected,
            local=local_observation(observation, agent_id, env.max_units),
            candidates=action_features(
                selected, units, width, height, agent_id
            ),
        )
        return decision, normalized_role(str(unit["class"]))

    def _happo_priors(
        self,
        model: HAPPO,
        env,
        actions: list[dict[str, Any]],
        observation: np.ndarray,
        width: int,
        height: int,
        units: list[dict[str, Any]],
    ) -> dict[int, float]:
        by_id = {int(unit["id"]): unit for unit in units}
        priors: dict[int, float] = {}
        for agent_id in sorted({int(action["unit"]) for action in actions}):
            decision = happo_decision_for_agent(
                env, observation, width, height, actions, agent_id, units
            )
            role = normalized_role(str(by_id[agent_id]["class"]))
            values = model.score(decision, role)
            scale = max(1e-6, float(np.std(values)))
            normalized = (values - float(np.mean(values))) / scale
            priors.update(
                (int(action["index"]), float(value))
                for action, value in zip(decision.actions, normalized)
            )
        return priors

    def _cql_priors(
        self,
        model: CQL,
        env,
        actions: list[dict[str, Any]],
        observation: np.ndarray,
        width: int,
        height: int,
        units: list[dict[str, Any]],
    ) -> dict[int, float]:
        priors: dict[int, float] = {}
        for agent_id in sorted({int(action["unit"]) for action in actions}):
            decision, _ = self._decision_for_agent(
                env, actions, observation, width, height, agent_id, units
            )
            values = model.score(observation, decision)
            scale = max(1e-6, float(np.std(values)))
            normalized = (values - float(np.mean(values))) / scale
            priors.update(
                (int(action["index"]), float(value))
                for action, value in zip(decision.actions, normalized)
            )
        return priors

    def _map_context(
        self,
        env,
        units: list[dict[str, Any]],
        actions: list[dict[str, Any]],
        width: int,
        height: int,
    ) -> tuple[list[str], dict[int, list[int]]]:
        try:
            map_info = env.map_info()
            terrain = [str(value) for value in map_info.get("terrain", [])]
        except (AttributeError, KeyError, RuntimeError, ValueError):
            terrain = []
        roster_signature = tuple(
            sorted(
                (
                    int(unit["id"]),
                    str(unit.get("class", "")),
                    int(unit.get("move", 0)),
                )
                for unit in units
                if not bool(unit.get("dead", False))
            )
        )
        signature = (width, height, tuple(terrain), roster_signature)
        if signature != self._map_signature:
            self._map_signature = signature
            self._movement_costs.clear()
            self.planner.reset()
        ready_ids = {int(action["unit"]) for action in actions}
        ready_units = [
            unit for unit in units
            if int(unit["id"]) in ready_ids
            if not bool(unit.get("dead", False))
            and not bool(unit.get("done", False))
        ]
        for unit in ready_units:
            unit_id = int(unit["id"])
            if unit_id in self._movement_costs:
                continue
            try:
                self._movement_costs[unit_id] = list(env.movement_costs(unit_id))
            except (AttributeError, KeyError, RuntimeError, ValueError):
                continue
        return terrain, dict(self._movement_costs)

    @staticmethod
    def _safe_action(actions: list[dict[str, Any]]) -> int:
        if not actions:
            raise ValueError("runtime policy received no legal actions")
        agent_id = min(int(action["unit"]) for action in actions)
        selected = [action for action in actions if int(action["unit"]) == agent_id]
        wait = next(
            (action for action in selected if int(action["type"]) == 0), selected[0]
        )
        return int(wait["index"])

    def choose(
        self,
        env,
        actions: list[dict[str, Any]],
        observation: np.ndarray,
        width: int,
        height: int,
    ) -> int:
        if not actions:
            raise ValueError("runtime policy received no legal actions")
        units = env.unit_info()
        terrain, movement_costs = self._map_context(
            env, units, actions, width, height
        )
        priors: dict[int, float] = {}
        if self.happo_error is None:
            try:
                model = self._load_happo(len(observation))
                priors = self._happo_priors(
                    model, env, actions, observation, width, height, units
                )
                self.backend = "joint-mapf+happo"
            except (FileNotFoundError, KeyError, RuntimeError, ValueError) as error:
                self.happo_error = error
        if not priors and self.cql_error is None:
            try:
                model = self._load_cql(len(observation))
                priors = self._cql_priors(
                    model, env, actions, observation, width, height, units
                )
                self.backend = "joint-mapf+cql"
            except (FileNotFoundError, KeyError, RuntimeError, ValueError) as error:
                self.cql_error = error
        if not priors:
            self.backend = "joint-mapf"
        try:
            choice = self.planner.choose(
                actions,
                units,
                width,
                height,
                terrain=terrain,
                movement_costs=movement_costs,
                action_priors=priors,
            )
            self.last_plan_reason = choice.reason
            return choice.action_index
        except (KeyError, RuntimeError, ValueError) as error:
            self.last_plan_reason = f"planner-error:{error}"
            self.backend = f"{self.backend}+legal-fallback"
            return self._safe_action(actions)
