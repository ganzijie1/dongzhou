"""Compare HAPPO, pure beam MPC, and HAPPO-prior beam MPC."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch

from rl.beam_happo_init import collect_beam_teacher, pretrain_happo_from_beam
from rl.beam_mpc import BeamMPC, BeamMPCConfig, HAPPOPrior
from rl.happo import HAPPO, decision_role, happo_decision
from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="dongzhou")
    parser.add_argument("--happo-model", type=Path)
    parser.add_argument("--train-steps", type=int, default=2048)
    parser.add_argument("--rollout-steps", type=int, default=256)
    parser.add_argument("--eval-episodes", type=int, default=3)
    parser.add_argument("--max-episode-actions", type=int, default=40)
    parser.add_argument("--horizon", type=int, default=2)
    parser.add_argument("--beam-width", type=int, default=4)
    parser.add_argument("--candidates", type=int, default=4)
    parser.add_argument("--prior-weight", type=float, default=0.35)
    parser.add_argument("--teacher-episodes", type=int, default=0)
    parser.add_argument("--teacher-updates", type=int, default=300)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("rl/models/beam_mpc_comparison"))
    return parser.parse_args()


def load_happo(path: Path, state_features: int, seed: int) -> HAPPO:
    model = HAPPO(state_features, seed=seed)
    payload = torch.load(path, map_location="cpu", weights_only=True)
    model.actors.load_state_dict(payload["actors"])
    model.critic.load_state_dict(payload["critic"])
    return model


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


def evaluate(
    env: Any, episodes: int, seed: int,
    choose: Callable[[Any, np.ndarray, int, int], tuple[int, int]],
) -> dict[str, float]:
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    rows: list[dict[str, float]] = []
    planning_seconds = 0.0
    expanded_nodes = 0
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total, actions = 0.0, 0
        while True:
            started = time.perf_counter()
            action, expanded = choose(env, observation, width, height)
            planning_seconds += time.perf_counter() - started
            expanded_nodes += expanded
            observation, reward, terminated, truncated, info = env.step(action)
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        rows.append({
            "return": total, "victory": float(int(info["status"]) == 3),
            "actions": float(actions),
        })
    metrics = summarize(rows)
    metrics.update({
        "planning_seconds": planning_seconds,
        "mean_decision_ms": 1000.0 * planning_seconds / max(1, sum(row["actions"] for row in rows)),
        "expanded_nodes": float(expanded_nodes),
    })
    return metrics


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with make_env(args) as env:
        state_features = int(env.observation_space.shape[0])
        if args.happo_model:
            happo = load_happo(args.happo_model, state_features, args.seed)
            training: dict[str, Any] = {"source": str(args.happo_model)}
        else:
            happo = HAPPO(state_features, seed=args.seed)
            teacher_metrics = None
            if args.teacher_episodes > 0:
                teacher_planner = BeamMPC(BeamMPCConfig(
                    horizon=args.horizon, beam_width=args.beam_width,
                    candidates_per_node=args.candidates,
                ))
                samples, collection = collect_beam_teacher(
                    env, teacher_planner, args.teacher_episodes, seed=args.seed
                )
                teacher_metrics = {
                    "collection": collection,
                    "pretraining": pretrain_happo_from_beam(
                        happo, samples, updates=args.teacher_updates, seed=args.seed
                    ),
                }
            started = time.perf_counter()
            history = happo.learn(
                env, args.train_steps, rollout_steps=args.rollout_steps,
                epochs=4, batch_size=min(128, args.rollout_steps), seed=args.seed,
            )
            training = {
                "source": "trained", "seconds": time.perf_counter() - started,
                "last_update": history[-1], "beam_initialization": teacher_metrics,
            }
            happo.save(args.output / "happo.pt")

    pure = BeamMPC(BeamMPCConfig(
        horizon=args.horizon, beam_width=args.beam_width,
        candidates_per_node=args.candidates,
    ))
    hybrid = BeamMPC(BeamMPCConfig(
        horizon=args.horizon, beam_width=args.beam_width,
        candidates_per_node=args.candidates, prior_weight=args.prior_weight,
    ))

    def happo_choice(env, observation, width, height):
        decision = happo_decision(env, observation, width, height)
        choice, _ = happo.choose(decision, decision_role(env, decision), deterministic=True)
        return int(decision.actions[choice]["index"]), 0

    def pure_choice(env, observation, _width, _height):
        result = pure.search(env, observation)
        return result.action, result.expanded_nodes

    def hybrid_choice(env, observation, width, height):
        result = hybrid.search(env, observation, prior=HAPPOPrior(happo, width, height))
        return result.action, result.expanded_nodes

    evaluation_seed = args.seed + 10_000
    with make_env(args) as env:
        happo_metrics = evaluate(env, args.eval_episodes, evaluation_seed, happo_choice)
    with make_env(args) as env:
        pure_metrics = evaluate(env, args.eval_episodes, evaluation_seed, pure_choice)
    with make_env(args) as env:
        hybrid_metrics = evaluate(env, args.eval_episodes, evaluation_seed, hybrid_choice)

    report = {
        "configuration": {
            "scenario": args.scenario, "eval_episodes": args.eval_episodes,
            "max_episode_actions": args.max_episode_actions, "seed": args.seed,
            "horizon": args.horizon, "beam_width": args.beam_width,
            "candidates_per_node": args.candidates,
            "hybrid_prior_weight": args.prior_weight,
        },
        "training": training,
        "happo": happo_metrics,
        "pure_beam_mpc": pure_metrics,
        "happo_prior_beam_mpc": hybrid_metrics,
        "runtime_policy_changed": False,
    }
    destination = args.output / "report.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"saved comparison to {destination}")


if __name__ == "__main__":
    main()
