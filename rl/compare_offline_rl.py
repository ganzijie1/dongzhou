"""Collect one fixed dataset, then compare offline IQL and CQL fairly."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rl.compare_ppo_mappo import make_env, summarize
from rl.mappo import current_decision
from rl.offline_dataset import collect_offline_dataset
from rl.offline_rl import CQL, IQL


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--dataset-episodes", type=int, default=48)
    parser.add_argument("--updates", type=int, default=1500)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path, default=Path("rl/models/offline_iql_cql_comparison")
    )
    return parser.parse_args()


def evaluate(model, env, episodes: int, seed: int) -> dict[str, float]:
    results = []
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total, actions = 0.0, 0
        while True:
            decision = current_decision(env, observation, width, height)
            choice = model.choose(observation, decision)
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


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    collection_started = time.perf_counter()
    with make_env(args) as data_env:
        dataset, dataset_summary = collect_offline_dataset(
            data_env, args.dataset_episodes, seed=args.seed
        )
        state_features = int(data_env.observation_space.shape[0])
    collection_seconds = time.perf_counter() - collection_started
    dataset.save(args.output / "dataset.npz")

    iql = IQL(state_features, seed=args.seed)
    started = time.perf_counter()
    iql_update = iql.train(dataset, args.updates, batch_size=args.batch_size)
    iql_seconds = time.perf_counter() - started
    iql.save(args.output / "iql.pt")
    with make_env(args) as iql_env:
        iql_metrics = evaluate(iql, iql_env, args.eval_episodes, args.seed + 10_000)

    cql = CQL(state_features, seed=args.seed)
    started = time.perf_counter()
    cql_update = cql.train(dataset, args.updates, batch_size=args.batch_size)
    cql_seconds = time.perf_counter() - started
    cql.save(args.output / "cql.pt")
    with make_env(args) as cql_env:
        cql_metrics = evaluate(cql, cql_env, args.eval_episodes, args.seed + 10_000)

    report = {
        "configuration": {
            "scenario": args.scenario, "dataset_episodes": args.dataset_episodes,
            "updates_per_algorithm": args.updates, "batch_size": args.batch_size,
            "eval_episodes": args.eval_episodes,
            "max_episode_actions": args.max_episode_actions, "seed": args.seed,
        },
        "dataset": {**dataset_summary, "collection_seconds": collection_seconds,
                    "training_environment_access": False},
        "iql": {**iql_metrics, "training_seconds": iql_seconds,
                "parameters": iql.parameter_count, "last_update": iql_update,
                "expectile": 0.7, "advantage_temperature": 3.0},
        "cql": {**cql_metrics, "training_seconds": cql_seconds,
                "parameters": cql.parameter_count, "last_update": cql_update,
                "conservative_weight": 1.0},
        "scope": (
            "Both algorithms train only from the same immutable candidate-action "
            "dataset. Environment access is limited to collection and final evaluation."
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
