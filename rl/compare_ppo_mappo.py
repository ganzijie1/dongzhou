"""Train and compare MaskablePPO and parameter-sharing MAPPO fairly."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from sb3_contrib import MaskablePPO

from rl.mappo import MAPPO, current_decision
from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--steps", type=int, default=30_000)
    parser.add_argument("--rollout-steps", type=int, default=512)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("rl/models/ppo_mappo_comparison"))
    return parser.parse_args()


def make_env(args: argparse.Namespace) -> MengdeEnv:
    return MengdeEnv(
        find_executable(args.executable), scenario=args.scenario,
        max_episode_actions=args.max_episode_actions,
    )


def summarize(episodes: list[dict[str, float]]) -> dict[str, float]:
    return {
        "mean_return": float(np.mean([episode["return"] for episode in episodes])),
        "return_std": float(np.std([episode["return"] for episode in episodes])),
        "win_rate": float(np.mean([episode["victory"] for episode in episodes])),
        "mean_actions": float(np.mean([episode["actions"] for episode in episodes])),
    }


def evaluate_ppo(model: MaskablePPO, env: MengdeEnv, episodes: int, seed: int) -> dict[str, float]:
    results = []
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total = 0.0
        actions = 0
        while True:
            action, _ = model.predict(
                observation, action_masks=env.action_masks(), deterministic=True
            )
            observation, reward, terminated, truncated, info = env.step(int(action))
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        results.append(
            {"return": total, "victory": float(int(info["status"]) == VICTORY), "actions": float(actions)}
        )
    return summarize(results)


def evaluate_mappo(model: MAPPO, env: MengdeEnv, episodes: int, seed: int) -> dict[str, float]:
    results = []
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total = 0.0
        actions = 0
        while True:
            decision = current_decision(env, observation, width, height)
            choice, _, _ = model.choose(decision, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        results.append(
            {"return": total, "victory": float(int(info["status"]) == VICTORY), "actions": float(actions)}
        )
    return summarize(results)


def timed(function: Callable[[], Any]) -> tuple[Any, float]:
    started = time.perf_counter()
    return function(), time.perf_counter() - started


def main() -> None:
    args = parse_args()
    if args.steps <= 0 or args.rollout_steps <= 1 or args.eval_episodes <= 0:
        raise ValueError("steps, rollout steps, and evaluation episodes must be positive")
    args.output.mkdir(parents=True, exist_ok=True)

    with make_env(args) as ppo_env:
        ppo = MaskablePPO(
            "MlpPolicy", ppo_env, learning_rate=3e-4,
            n_steps=args.rollout_steps,
            batch_size=min(128, args.rollout_steps),
            n_epochs=4, gamma=0.99, gae_lambda=0.95,
            policy_kwargs={"net_arch": {"pi": [128, 128], "vf": [128, 128]}},
            seed=args.seed, verbose=0,
        )
        _, ppo_seconds = timed(lambda: ppo.learn(total_timesteps=args.steps))
        ppo.save(args.output / "ppo")
        ppo_parameters = sum(parameter.numel() for parameter in ppo.policy.parameters())
    with make_env(args) as ppo_eval_env:
        ppo_metrics = evaluate_ppo(ppo, ppo_eval_env, args.eval_episodes, args.seed + 10_000)

    with make_env(args) as mappo_env:
        mappo = MAPPO(
            int(mappo_env.observation_space.shape[0]), seed=args.seed
        )
        history, mappo_seconds = timed(
            lambda: mappo.learn(
                mappo_env, args.steps, rollout_steps=args.rollout_steps,
                epochs=4, batch_size=min(128, args.rollout_steps), seed=args.seed,
            )
        )
        mappo.save(args.output / "mappo.pt")
    with make_env(args) as mappo_eval_env:
        mappo_metrics = evaluate_mappo(
            mappo, mappo_eval_env, args.eval_episodes, args.seed + 10_000
        )

    report = {
        "configuration": {
            "scenario": args.scenario, "steps": args.steps,
            "rollout_steps": args.rollout_steps,
            "eval_episodes": args.eval_episodes, "seed": args.seed,
            "max_episode_actions": args.max_episode_actions,
        },
        "ppo": {
            **ppo_metrics, "training_seconds": ppo_seconds,
            "parameters": ppo_parameters,
            "actor_observation": "complete battle state",
            "critic_observation": "complete battle state",
        },
        "mappo": {
            **mappo_metrics, "training_seconds": mappo_seconds,
            "parameters": mappo.parameter_count,
            "actor_observation": "active unit plus candidate action features",
            "critic_observation": "complete battle state",
            "last_update": history[-1],
        },
        "interpretation": {
            "mappo_strength": "shared unit policy and centralized training favor coordination and transfer across unit counts",
            "mappo_cost": "candidate scoring and extra native queries make training slower per environment step",
            "ppo_strength": "simpler mature implementation and faster iteration on small fixed battles",
            "ppo_cost": "global action indices couple the policy more strongly to a particular deployment layout",
        },
    }
    destination = args.output / "report.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"saved comparison to {destination}")


if __name__ == "__main__":
    main()
