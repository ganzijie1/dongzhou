"""Paired-seed benchmark for rolling beam and a one-step planning baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from rl.mengde_env import MengdeEnv
from rl.rolling_beam import PlannerConfig, RollingBeamPlanner
from rl.smoke_test import find_executable
from rl.train_happo_dongzhou import ENEMY_FORCE, scripted_action


DEFEAT = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260906)
    parser.add_argument("--max-episode-actions", type=int, default=120)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def percentile(values: list[float], quantile: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), quantile))


def evaluate(
    executable: Path,
    planner: RollingBeamPlanner,
    seeds: list[int],
    max_episode_actions: int,
) -> dict[str, Any]:
    wins: list[float] = []
    returns: list[float] = []
    lengths: list[int] = []
    latencies: list[float] = []
    expanded: list[int] = []
    attack_rates: list[float] = []
    with MengdeEnv(
        executable,
        interactive=True,
        max_episode_actions=max_episode_actions,
    ) as env:
        for seed in seeds:
            observation, info = env.reset(seed=seed)
            del observation
            map_info = env.map_info()
            width = int(map_info["width"])
            height = int(map_info["height"])
            total_reward = 0.0
            enemy_actions = 0
            enemy_attacks = 0
            steps = 0
            while steps < max_episode_actions:
                actions = env.list_actions()
                units = env.unit_info()
                actor_id = min(int(action["unit"]) for action in actions)
                actor = next(unit for unit in units if int(unit["id"]) == actor_id)
                if int(actor["force"]) == ENEMY_FORCE:
                    result = planner.plan(actions, units, width, height)
                    action_index = result.action_index
                    chosen = next(
                        action for action in actions
                        if int(action["index"]) == action_index
                    )
                    enemy_actions += 1
                    enemy_attacks += int(int(chosen["type"]) in (2, 3))
                    latencies.append(result.stats.elapsed_ms)
                    expanded.append(result.stats.expanded)
                else:
                    action_index = scripted_action(actions, units, width, height)
                _, reward, terminated, truncated, info = env.step(action_index)
                total_reward += float(reward)
                steps += 1
                if terminated or truncated:
                    break
            wins.append(float(int(info.get("status", 0)) == DEFEAT))
            returns.append(-total_reward)
            lengths.append(steps)
            attack_rates.append(enemy_attacks / max(1, enemy_actions))
    return {
        "enemy_win_rate": mean(wins),
        "enemy_mean_return": mean(returns),
        "mean_actions": mean(lengths),
        "enemy_attack_rate": mean(attack_rates),
        "planner_mean_ms": mean(latencies),
        "planner_p95_ms": percentile(latencies, 95),
        "mean_expanded_nodes": mean(expanded),
    }


def main() -> None:
    args = parse_args()
    executable = find_executable(args.executable)
    seeds = [args.seed + index for index in range(args.episodes)]
    configurations = {
        "rolling_beam": PlannerConfig(
            horizon=2,
            beam_width=6,
            scenario_count=3,
            cvar_alpha=0.25,
            max_actions_per_actor=10,
            include_opponent_response=True,
        ),
        "one_step": PlannerConfig(
            horizon=1,
            beam_width=32,
            scenario_count=1,
            cvar_alpha=1.0,
            include_opponent_response=False,
        ),
    }
    results = {
        name: evaluate(
            executable,
            RollingBeamPlanner(config),
            seeds,
            args.max_episode_actions,
        )
        for name, config in configurations.items()
    }
    report = {
        "protocol": "paired initial seeds; scripted own-force opponent",
        "seeds": seeds,
        "configurations": {
            name: asdict(config) for name, config in configurations.items()
        },
        "results": results,
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
