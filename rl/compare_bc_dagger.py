"""Compare equal-update behavior cloning and HAPPO-labeled DAgger."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rl.compare_ppo_mappo import make_env, summarize
from rl.dagger import (
    BehaviorCloning, collect_expert_data, dagger_aggregate, expert_choice,
    load_happo_expert, save_samples,
)
from rl.mappo import current_decision


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--initial-episodes", type=int, default=24)
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--rollout-episodes", type=int, default=6)
    parser.add_argument("--initial-updates", type=int, default=300)
    parser.add_argument("--updates-per-iteration", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path, default=Path("rl/models/bc_dagger_comparison")
    )
    return parser.parse_args()


def evaluate(model, env, episodes: int, seed: int, *, expert=False) -> dict[str, float]:
    results = []
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total, actions = 0.0, 0
        while True:
            decision = current_decision(env, observation, width, height)
            choice = (
                expert_choice(model, env, decision) if expert else model.choose(decision)
            )
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
    with make_env(args) as data_env:
        expert = load_happo_expert(int(data_env.observation_space.shape[0]))
        started = time.perf_counter()
        initial, initial_summary = collect_expert_data(
            data_env, expert, args.initial_episodes, seed=args.seed
        )
        initial_collection_seconds = time.perf_counter() - started
    save_samples(initial, args.output / "initial_expert_dataset.npz")

    total_updates = args.initial_updates + args.iterations * args.updates_per_iteration
    bc = BehaviorCloning(seed=args.seed)
    started = time.perf_counter()
    bc_update = bc.train(initial, total_updates, batch_size=args.batch_size)
    bc_seconds = time.perf_counter() - started
    bc.save(args.output / "bc.pt", "behavior-cloning")

    dagger = BehaviorCloning(seed=args.seed)
    started = time.perf_counter()
    dagger_updates = [
        dagger.train(initial, args.initial_updates, batch_size=args.batch_size)
    ]
    dagger_training_seconds = time.perf_counter() - started
    aggregated = list(initial)
    iteration_reports = []
    aggregation_seconds = 0.0
    with make_env(args) as dagger_env:
        for iteration in range(args.iterations):
            beta = 0.5 ** (iteration + 1)
            started = time.perf_counter()
            added, rollout = dagger_aggregate(
                dagger_env, expert, dagger, args.rollout_episodes,
                beta=beta, seed=args.seed + 1000 + iteration * args.rollout_episodes,
            )
            aggregation_seconds += time.perf_counter() - started
            aggregated.extend(added)
            started = time.perf_counter()
            update = dagger.train(
                aggregated, args.updates_per_iteration, batch_size=args.batch_size
            )
            dagger_training_seconds += time.perf_counter() - started
            dagger_updates.append(update)
            iteration_reports.append(
                {"iteration": iteration + 1, "total_samples": len(aggregated),
                 **rollout, "update": update}
            )
    save_samples(aggregated, args.output / "dagger_dataset.npz")
    dagger.save(args.output / "dagger.pt", "dagger")

    evaluation_seed = args.seed + 10_000
    with make_env(args) as expert_env:
        expert_metrics = evaluate(
            expert, expert_env, args.eval_episodes, evaluation_seed, expert=True
        )
    with make_env(args) as bc_env:
        bc_metrics = evaluate(bc, bc_env, args.eval_episodes, evaluation_seed)
    with make_env(args) as dagger_eval_env:
        dagger_metrics = evaluate(
            dagger, dagger_eval_env, args.eval_episodes, evaluation_seed
        )

    report = {
        "configuration": {
            "scenario": args.scenario, "initial_episodes": args.initial_episodes,
            "dagger_iterations": args.iterations,
            "rollout_episodes_per_iteration": args.rollout_episodes,
            "total_updates_per_learner": total_updates,
            "batch_size": args.batch_size, "eval_episodes": args.eval_episodes,
            "max_episode_actions": args.max_episode_actions, "seed": args.seed,
        },
        "expert_dataset": {
            **initial_summary, "collection_seconds": initial_collection_seconds,
        },
        "happo_expert": {**expert_metrics, "parameters": expert.parameter_count},
        "behavior_cloning": {
            **bc_metrics, "training_seconds": bc_seconds,
            "parameters": bc.parameter_count, "last_update": bc_update,
        },
        "dagger": {
            **dagger_metrics, "training_seconds": dagger_training_seconds,
            "aggregation_seconds": aggregation_seconds,
            "parameters": dagger.parameter_count,
            "initial_samples": len(initial), "final_samples": len(aggregated),
            "iterations": iteration_reports,
            "last_update": dagger_updates[-1],
        },
        "scope": (
            "BC and DAgger use identical policy networks, initialization, total "
            "gradient updates, and initial expert data. DAgger alone queries the "
            "HAPPO expert on learner-visited states."
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
