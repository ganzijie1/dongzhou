"""Evaluate a saved HAPPO policy across every Dongzhou battle stage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.happo import HAPPO, decision_role, happo_decision

from rl.mengde_env import MengdeEnv


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=41)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--max-episode-actions", type=int, default=120)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def load_model(path: Path, state_features: int) -> HAPPO:
    payload = torch.load(path, map_location="cpu")
    model = HAPPO(state_features, seed=2026)
    model.actors.load_state_dict(payload["actors"])
    model.critic.load_state_dict(payload["critic"])
    model.actors.eval()
    model.critic.eval()
    return model


def main() -> None:
    args = parse_args()
    env = MengdeEnv(
        executable=args.executable,
        scenario="dongzhou",
        max_episode_actions=args.max_episode_actions,
    )
    rows: list[dict[str, object]] = []
    model: HAPPO | None = None
    try:
        for stage in range(args.stage_count):
            env._restart_process(stage)
            story = env.story_info()
            if bool(story.get("story_only", False)):
                continue
            stage_results = []
            for episode in range(args.episodes):
                observation, _ = env.reset(seed=args.seed + stage * 101 + episode)
                if model is None:
                    model = load_model(args.model, len(observation))
                map_info = env.map_info()
                width = int(map_info["width"])
                height = int(map_info["height"])
                total_reward = 0.0
                status = 0
                actions = 0
                while actions < args.max_episode_actions:
                    decision = happo_decision(env, observation, width, height)
                    role = decision_role(env, decision)
                    choice, _ = model.choose(decision, role, deterministic=True)
                    observation, reward, terminated, truncated, info = env.step(
                        int(decision.actions[choice]["index"])
                    )
                    total_reward += float(reward)
                    actions += 1
                    status = int(info.get("status", 0))
                    if terminated or truncated:
                        break
                stage_results.append(
                    {"reward": total_reward, "status": status, "actions": actions}
                )
            rows.append(
                {
                    "stage_index": stage,
                    "stage_id": story.get("stage_id", str(stage)),
                    "win_rate": float(np.mean([
                        int(item["status"] == VICTORY) for item in stage_results
                    ])),
                    "mean_reward": float(np.mean([
                        item["reward"] for item in stage_results
                    ])),
                    "mean_actions": float(np.mean([
                        item["actions"] for item in stage_results
                    ])),
                }
            )
            print(json.dumps(rows[-1], ensure_ascii=True), flush=True)
    finally:
        env.close()
    report = {
        "model": str(args.model),
        "battle_stages": len(rows),
        "episodes_per_stage": args.episodes,
        "win_rate": float(np.mean([row["win_rate"] for row in rows])),
        "mean_reward": float(np.mean([row["mean_reward"] for row in rows])),
        "mean_actions": float(np.mean([row["mean_actions"] for row in rows])),
        "stages": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
