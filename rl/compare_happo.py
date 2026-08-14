"""Evaluate turn-based HAPPO against the saved PPO/MAPPO benchmark."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from rl.compare_ppo_mappo import make_env, summarize
from rl.happo import HAPPO, decision_role, happo_decision



VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--steps", type=int, default=4096)
    parser.add_argument("--rollout-steps", type=int, default=512)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--baseline-report", type=Path,
        default=Path("rl/models/ppo_mappo_comparison/report.json"),
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("rl/models/ppo_mappo_happo_comparison"),
    )
    return parser.parse_args()


def evaluate_happo(
    model: HAPPO, env, episodes: int, seed: int
) -> dict[str, float]:
    results = []
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total = 0.0
        actions = 0
        while True:
            decision = happo_decision(env, observation, width, height)
            role = decision_role(env, decision)
            choice, _ = model.choose(decision, role, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        results.append(
            {
                "return": total,
                "victory": float(int(info["status"]) == VICTORY),
                "actions": float(actions),
            }
        )
    return summarize(results)


def main() -> None:
    args = parse_args()
    baseline = json.loads(args.baseline_report.read_text(encoding="utf-8"))
    expected = {
        "scenario": args.scenario,
        "steps": args.steps,
        "rollout_steps": args.rollout_steps,
        "eval_episodes": args.eval_episodes,
        "seed": args.seed,
        "max_episode_actions": args.max_episode_actions,
    }
    if baseline.get("configuration") != expected:
        raise ValueError(
            "baseline configuration differs; rerun compare_ppo_mappo with matching arguments"
        )
    args.output.mkdir(parents=True, exist_ok=True)

    with make_env(args) as train_env:
        model = HAPPO(int(train_env.observation_space.shape[0]), seed=args.seed)
        started = time.perf_counter()
        history = model.learn(
            train_env, args.steps, rollout_steps=args.rollout_steps,
            epochs=4, batch_size=min(128, args.rollout_steps), seed=args.seed,
        )
        training_seconds = time.perf_counter() - started
        model.save(args.output / "happo.pt")
    with make_env(args) as eval_env:
        metrics = evaluate_happo(
            model, eval_env, args.eval_episodes, args.seed + 10_000
        )

    report = {
        "configuration": expected,
        "ppo": baseline["ppo"],
        "mappo": baseline["mappo"],
        "happo": {
            **metrics,
            "training_seconds": training_seconds,
            "parameters": model.parameter_count,
            "actor_observation": "active unit plus candidate action features",
            "critic_observation": "complete battle state",
            "parameter_sharing": False,
            "sequential_update": True,
            "aec_correction": "preceding-role ratios propagated within each episode",
            "last_update": history[-1],
        },
        "scope": (
            "Turn-based AEC adaptation of HAPPO. It is heterogeneous-agent PPO, "
            "not a conventional high-level/low-level hierarchical policy."
        ),
    }
    destination = args.output / "report.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"saved comparison to {destination}")


if __name__ == "__main__":
    main()
