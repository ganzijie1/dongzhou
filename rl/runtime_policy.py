"""Rolling-planner policy with learned-policy fallbacks for the frontend."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

from rl.happo import HAPPO, happo_decision, normalized_role
from rl.mappo import Decision, action_features, local_observation
from rl.offline_rl import CQL
from rl.rolling_beam import PlanResult, RollingBeamPlanner


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
    """Select native actions with rolling beam, HAPPO, then conservative CQL."""

    def __init__(
        self, *, happo_path: str | Path | None = None,
        cql_path: str | Path | None = None,
        planner: RollingBeamPlanner | None = None,
        enable_planner: bool = True,
    ) -> None:
        self.happo_path = Path(happo_path) if happo_path else None
        self.cql_path = Path(cql_path) if cql_path else None
        self.happo: HAPPO | None = None
        self.cql: CQL | None = None
        self.planner = planner or RollingBeamPlanner()
        self.enable_planner = enable_planner
        self.last_plan: PlanResult | None = None
        self.planner_error: Exception | None = None
        self.happo_error: Exception | None = None
        self.cql_error: Exception | None = None
        self.backend = "uninitialized"

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
    def _decision(
        env,
        actions: list[dict[str, Any]],
        observation: np.ndarray,
        width: int,
        height: int,
    ) -> tuple[Decision, str]:
        if not actions:
            raise ValueError("runtime policy received no legal actions")
        agent_id = min(int(action["unit"]) for action in actions)
        selected = [
            action for action in actions if int(action["unit"]) == agent_id
        ]
        units = env.unit_info()
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
        if self.enable_planner:
            try:
                self.last_plan = self.planner.choose(
                    env, actions, width, height
                )
                self.planner_error = None
                self.backend = "rolling-beam"
                return self.last_plan.action_index
            except (KeyError, TypeError, ValueError, RuntimeError) as error:
                self.planner_error = error
        decision, role = self._decision(
            env, actions, observation, width, height
        )
        if self.happo_error is None:
            try:
                model = self._load_happo(len(observation))
                happo_choice = happo_decision(
                    env, observation, width, height, actions=actions
                )
                choice, _ = model.choose(happo_choice, role, deterministic=True)
                self.backend = "happo"
                return int(happo_choice.actions[choice]["index"])
            except (FileNotFoundError, KeyError, RuntimeError, ValueError) as error:
                self.happo_error = error
        if self.cql_error is None:
            try:
                model = self._load_cql(len(observation))
                choice = model.choose(observation, decision)
                self.backend = "cql"
                return int(decision.actions[choice]["index"])
            except (FileNotFoundError, KeyError, RuntimeError, ValueError) as error:
                self.cql_error = error
        self.backend = "safe-wait"
        return self._safe_action(actions)
