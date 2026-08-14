"""Compare legacy and curriculum HAPPO checkpoints as the enemy policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from rl.happo import HAPPO, happo_decision, normalized_role
from rl.mappo import (
    Decision, SharedActor, action_features, local_observation,
    select_agent_actions,
)
from rl.mengde_env import MengdeEnv
from rl.train_happo_dongzhou import ENEMY_FORCE, scripted_action


DEFEAT = 4
LEGACY_ROLES = (
    "Lord", "Infantry", "Cavalry", "Archer", "Strategist", "Artillery",
    "Fighter", "Bandit", "Other",
)


class LegacyHAPPO:
    def __init__(self, path: Path) -> None:
        self.actors = nn.ModuleDict({role: SharedActor() for role in LEGACY_ROLES})
        self.actors.load_state_dict(torch.load(path, map_location="cpu")["actors"])
        self.actors.eval()

    @torch.no_grad()
    def choose(self, decision: Decision, role: str) -> int:
        local = torch.as_tensor(decision.local).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates).unsqueeze(0)
        key = role if role in LEGACY_ROLES else "Other"
        logits = self.actors[key](local, candidates)[0]
        return int(torch.argmax(Categorical(logits=logits).logits))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--curriculum", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=41)
    parser.add_argument("--max-episode-actions", type=int, default=160)
    parser.add_argument("--seed", type=int, default=902026)
    return parser.parse_args()


def legacy_decision(
    env: MengdeEnv, actions: list[dict[str, Any]], observation: np.ndarray,
    width: int, height: int,
) -> tuple[Decision, str]:
    agent_id, selected = select_agent_actions(actions)
    units = env.unit_info()
    unit = next(item for item in units if int(item["id"]) == agent_id)
    return Decision(
        agent_id=agent_id,
        actions=selected,
        local=local_observation(observation, agent_id, env.max_units),
        candidates=action_features(selected, units, width, height, agent_id),
    ), str(unit["class"])


def load_current(path: Path, state_features: int) -> HAPPO:
    payload = torch.load(path, map_location="cpu")
    model = HAPPO(state_features, seed=2026)
    model.actors.load_state_dict(payload["actors"])
    model.critic.load_state_dict(payload["critic"])
    model.actors.eval()
    model.critic.eval()
    return model


def evaluate(
    env: MengdeEnv, stages: list[int], model: Any, legacy: bool, seed: int,
) -> dict[str, float]:
    wins, returns, lengths, attack_rates, damages = [], [], [], [], []
    for stage in stages:
        env._restart_process(stage)
        observation, _ = env.reset(seed=seed + stage * 101)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        total, status, count = 0.0, 0, 0
        enemy_actions, enemy_attacks, planned_damage = 0, 0, 0.0
        while count < int(env._process_args[3]):
            actions = env.list_actions()
            agent_id, _ = select_agent_actions(actions)
            units = env.unit_info()
            actor = next(unit for unit in units if int(unit["id"]) == agent_id)
            is_enemy = int(actor["force"]) == ENEMY_FORCE
            if is_enemy:
                if legacy:
                    decision, role = legacy_decision(
                        env, actions, observation, width, height
                    )
                    choice = model.choose(decision, role)
                else:
                    decision = happo_decision(
                        env, observation, width, height, actions=actions
                    )
                    choice, _ = model.choose(
                        decision, normalized_role(str(actor["class"])),
                        deterministic=True,
                    )
                chosen = decision.actions[choice]
                action_index = int(chosen["index"])
                enemy_actions += 1
                enemy_attacks += int(int(chosen["type"]) in (2, 3))
                planned_damage += float(chosen.get("damage", 0))
            else:
                action_index = scripted_action(actions, units, width, height)
            observation, reward, terminated, truncated, info = env.step(action_index)
            if is_enemy:
                total -= float(reward)
            count += 1
            status = int(info.get("status", 0))
            if terminated or truncated:
                break
        wins.append(float(status == DEFEAT))
        returns.append(total)
        lengths.append(float(count))
        attack_rates.append(enemy_attacks / max(1, enemy_actions))
        damages.append(planned_damage / max(1, enemy_actions))
    return {
        "enemy_win_rate": float(np.mean(wins)),
        "enemy_mean_return": float(np.mean(returns)),
        "mean_actions": float(np.mean(lengths)),
        "enemy_attack_rate": float(np.mean(attack_rates)),
        "planned_damage_per_enemy_action": float(np.mean(damages)),
    }


def main() -> None:
    args = parse_args()
    torch.set_num_threads(1)
    env = MengdeEnv(
        args.executable, scenario="dongzhou", interactive=True,
        max_episode_actions=args.max_episode_actions,
    )
    try:
        stages = []
        for stage in range(args.stage_count):
            env._restart_process(stage)
            if not bool(env.story_info().get("story_only", False)):
                stages.append(stage)
        legacy = LegacyHAPPO(args.legacy)
        results = {"legacy": evaluate(env, stages, legacy, True, args.seed)}
        checkpoints = sorted(args.curriculum.glob("happo-pass-*.pt"))
        for path in checkpoints:
            env._restart_process(stages[0])
            observation, _ = env.reset(seed=args.seed)
            model = load_current(path, len(observation))
            results[path.stem] = evaluate(env, stages, model, False, args.seed)
            print(json.dumps({path.stem: results[path.stem]}), flush=True)
    finally:
        env.close()
    report = {"battle_stages": stages, "results": results}
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
