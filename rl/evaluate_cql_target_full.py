"""Evaluate a 34-feature CQL checkpoint as Dongzhou's enemy policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.happo import HAPPO_ACTION_FEATURES, happo_decision
from rl.mengde_env import MengdeEnv
from rl.offline_rl import CQL
from rl.train_happo_dongzhou import discover_battles, scripted_action


DEFEAT = 4
ENEMY_FORCE = 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=79)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = torch.load(args.model, map_location="cpu")
    env = MengdeEnv(args.executable, scenario="dongzhou", max_episode_actions=160, interactive=True)
    rows = []
    try:
        stages = discover_battles(env, args.stage_count)
        env._restart_process(stages[0])
        observation, _ = env.reset(seed=2056)
        model = CQL(len(observation), action_features=HAPPO_ACTION_FEATURES, seed=2056)
        model.q1.load_state_dict(payload["q1"])
        model.q2.load_state_dict(payload["q2"])
        for stage in stages:
            env._restart_process(stage)
            observation, _ = env.reset(seed=902056 + stage * 101)
            map_info = env.map_info()
            width, height = int(map_info["width"]), int(map_info["height"])
            total = 0.0
            status = 0
            for action_count in range(160):
                actions = env.list_actions()
                agent_id = min(int(action["unit"]) for action in actions)
                units = env.unit_info()
                actor = next(unit for unit in units if int(unit["id"]) == agent_id)
                if int(actor["force"]) == ENEMY_FORCE:
                    decision = happo_decision(env, observation, width, height, actions=actions)
                    choice = model.choose(observation, decision)
                    action_index = int(decision.actions[choice]["index"])
                else:
                    action_index = scripted_action(actions, units, width, height)
                observation, reward, terminated, truncated, info = env.step(action_index)
                if int(actor["force"]) == ENEMY_FORCE:
                    total -= float(reward)
                status = int(info.get("status", 0))
                if terminated or truncated:
                    break
            rows.append((total, float(status == DEFEAT), float(action_count + 1)))
    finally:
        env.close()
    result = {
        "enemy_win_rate": float(np.mean([row[1] for row in rows])),
        "enemy_mean_return": float(np.mean([row[0] for row in rows])),
        "mean_actions": float(np.mean([row[2] for row in rows])),
    }
    report = {"model": str(args.model), "battle_stages": stages, "evaluation": result}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
