"""Evaluate hierarchical H-PPO on the saved PPO/MAPPO/HAPPO benchmark."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rl.compare_ppo_mappo import make_env, summarize
from rl.hppo import HPPO
from rl.mappo import current_decision


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
    parser.add_argument("--num-options", type=int, default=4)
    parser.add_argument("--option-horizon", type=int, default=4)
    parser.add_argument(
        "--baseline-report", type=Path,
        default=Path("rl/models/ppo_mappo_happo_comparison/report.json"),
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("rl/models/ppo_mappo_happo_hppo_comparison"),
    )
    return parser.parse_args()


def evaluate_hppo(model: HPPO, env, episodes: int, seed: int) -> dict:
    results = []
    option_counts = [0] * model.num_options
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        option = None
        remaining = 0
        total = 0.0
        actions = 0
        while True:
            if option is None or remaining == 0:
                option, _, _ = model.choose_option(observation, deterministic=True)
                option_counts[option] += 1
                remaining = model.option_horizon
            decision = current_decision(env, observation, width, height)
            choice, _ = model.choose_action(decision, option, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            total += float(reward)
            actions += 1
            remaining -= 1
            if terminated or truncated:
                break
        results.append(
            {
                "return": total,
                "victory": float(int(info["status"]) == VICTORY),
                "actions": float(actions),
            }
        )
    metrics = summarize(results)
    total_options = max(1, sum(option_counts))
    metrics["evaluation_option_usage"] = [count / total_options for count in option_counts]
    return metrics


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
            "baseline configuration differs; rerun the baselines with matching arguments"
        )
    args.output.mkdir(parents=True, exist_ok=True)

    with make_env(args) as train_env:
        model = HPPO(
            int(train_env.observation_space.shape[0]),
            num_options=args.num_options, option_horizon=args.option_horizon,
            seed=args.seed,
        )
        started = time.perf_counter()
        history = model.learn(
            train_env, args.steps, rollout_steps=args.rollout_steps,
            epochs=4, batch_size=min(128, args.rollout_steps), seed=args.seed,
        )
        training_seconds = time.perf_counter() - started
        model.save(args.output / "hppo.pt")
    with make_env(args) as eval_env:
        metrics = evaluate_hppo(
            model, eval_env, args.eval_episodes, args.seed + 10_000
        )

    report = {
        "configuration": expected,
        "ppo": baseline["ppo"],
        "mappo": baseline["mappo"],
        "happo": baseline["happo"],
        "hppo": {
            **metrics,
            "training_seconds": training_seconds,
            "parameters": model.parameter_count,
            "manager_observation": "complete battle state",
            "worker_observation": "active unit, latent option, and candidate actions",
            "num_options": model.num_options,
            "option_horizon": model.option_horizon,
            "hard_coded_option_rules": False,
            "last_update": history[-1],
        },
        "scope": (
            "HiPPO-style temporal hierarchy: a manager samples a latent option and "
            "an option-conditioned worker executes native legal actions."
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
