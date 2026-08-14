"""Train and evaluate AlphaZero policy-only and policy-plus-MCTS variants."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from rl.alphazero import AlphaZero, TrainingSample
from rl.compare_ppo_mappo import make_env, summarize
from rl.mappo import current_decision


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--train-episodes", type=int, default=8)
    parser.add_argument("--simulations", type=int, default=8)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--eval-simulations", type=int, default=8)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path, default=Path("rl/models/alphazero_comparison")
    )
    return parser.parse_args()


def evaluate_policy(model: AlphaZero, env, episodes: int, seed: int) -> dict[str, float]:
    results = []
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total, actions = 0.0, 0
        while True:
            decision = current_decision(env, observation, width, height)
            priors, _ = model.evaluate(observation, decision)
            choice = int(np.argmax(priors))
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        results.append(
            {"return": total, "victory": float(int(info["status"]) == VICTORY),
             "actions": float(actions)}
        )
    return summarize(results)


def evaluate_mcts(
    model: AlphaZero, env, simulator, episodes: int, seed: int, simulations: int
) -> dict[str, float]:
    results = []
    simulator_steps = 0
    for episode in range(episodes):
        episode_seed = seed + episode
        observation, info = env.reset(seed=episode_seed)
        history: list[int] = []
        total = 0.0
        while True:
            result = model.search(
                simulator, history, episode_seed, simulations=simulations,
                temperature=0.0, add_noise=False,
            )
            history.append(result.action)
            simulator_steps += result.replay_steps
            observation, reward, terminated, truncated, info = env.step(result.action)
            total += float(reward)
            if terminated or truncated:
                break
        results.append(
            {"return": total, "victory": float(int(info["status"]) == VICTORY),
             "actions": float(len(history))}
        )
    metrics = summarize(results)
    metrics["simulator_steps"] = float(simulator_steps)
    metrics["simulator_steps_per_real_action"] = float(
        simulator_steps / max(1.0, sum(item["actions"] for item in results))
    )
    return metrics


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    replay: list[TrainingSample] = []
    episode_metrics = []
    histories = []
    started = time.perf_counter()
    with make_env(args) as env, make_env(args) as simulator:
        model = AlphaZero(int(env.observation_space.shape[0]), seed=args.seed)
        for episode in range(args.train_episodes):
            samples, metrics = model.self_play_episode(
                env, simulator, seed=args.seed + episode,
                simulations=args.simulations,
            )
            replay.extend(samples)
            replay = replay[-2048:]
            update = model.update(replay, epochs=4, batch_size=64)
            episode_metrics.append(metrics)
            histories.append(update)
        training_seconds = time.perf_counter() - started
        model.save(args.output / "alphazero.pt")

    with make_env(args) as policy_env:
        policy_metrics = evaluate_policy(
            model, policy_env, args.eval_episodes, args.seed + 10_000
        )
    search_started = time.perf_counter()
    with make_env(args) as search_env, make_env(args) as search_simulator:
        mcts_metrics = evaluate_mcts(
            model, search_env, search_simulator, args.eval_episodes,
            args.seed + 10_000, args.eval_simulations,
        )
    search_seconds = time.perf_counter() - search_started

    report = {
        "configuration": {
            "scenario": args.scenario,
            "train_episodes": args.train_episodes,
            "self_play_simulations_per_move": args.simulations,
            "eval_episodes": args.eval_episodes,
            "eval_simulations_per_move": args.eval_simulations,
            "max_episode_actions": args.max_episode_actions,
            "seed": args.seed,
        },
        "training": {
            "seconds": training_seconds,
            "real_actions": int(sum(item["actions"] for item in episode_metrics)),
            "simulator_steps": int(sum(item["simulator_steps"] for item in episode_metrics)),
            "samples": len(replay),
            "parameters": model.parameter_count,
            "last_update": histories[-1],
        },
        "policy_only": policy_metrics,
        "policy_plus_mcts": {
            **mcts_metrics, "evaluation_seconds": search_seconds,
        },
        "scope": (
            "Single-agent AlphaZero adaptation using shaped discounted return. "
            "The simulator resets and replays action history because the native "
            "engine does not expose an in-memory clone."
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
