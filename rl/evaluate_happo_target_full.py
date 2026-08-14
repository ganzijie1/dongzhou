"""Full-battle evaluation for a calibrated Dongzhou HAPPO checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from rl.happo import HAPPO
from rl.mengde_env import MengdeEnv
from rl.train_happo_dongzhou import discover_battles, evaluate_enemy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=79)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    env = MengdeEnv(
        args.executable, scenario="dongzhou", max_episode_actions=160,
        interactive=True,
    )
    try:
        stages = discover_battles(env, args.stage_count)
        env._restart_process(stages[0])
        observation, _ = env.reset(seed=2052)
        payload = torch.load(args.model, map_location="cpu")
        model = HAPPO(len(observation), seed=2052)
        model.actors.load_state_dict(payload["actors"])
        model.critic.load_state_dict(payload["critic"])
        result = evaluate_enemy(model, env, stages, 902052)
    finally:
        env.close()
    report = {"model": str(args.model), "battle_stages": stages, "evaluation": result}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
