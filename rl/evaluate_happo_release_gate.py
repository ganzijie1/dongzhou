"""Compare a trained Dongzhou enemy policy with the deterministic rule baseline."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Literal

import numpy as np
import torch

from rl.happo import HAPPO, decision_role, happo_decision
from rl.mappo import select_agent_actions
from rl.mengde_env import MengdeEnv
from rl.train_happo_dongzhou import (
    DONGZHOU_STAGE_COUNT,
    discover_battles,
    scripted_action,
)


DEFEAT = 4
ENEMY_FORCE = 4


def wilson_interval(successes: int, total: int, z: float = 1.96) -> list[float]:
    if total <= 0:
        return [0.0, 0.0]
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    margin = z * math.sqrt(
        proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)
    ) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def load_model(path: Path, state_features: int) -> tuple[HAPPO, dict[str, object]]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    model = HAPPO(state_features, seed=2026)
    model.actors.load_state_dict(payload["actors"])
    model.critic.load_state_dict(payload["critic"])
    model.actors.eval()
    model.critic.eval()
    return model, payload


def evaluate(
    env: MengdeEnv,
    model: HAPPO,
    stages: list[int],
    episodes: int,
    seed: int,
    enemy_policy: Literal["happo", "scripted"],
) -> dict[str, float]:
    wins: list[float] = []
    returns: list[float] = []
    lengths: list[float] = []
    timeouts: list[float] = []
    stage_win_rates: list[float] = []
    for stage in stages:
        env._restart_process(stage)
        stage_wins: list[float] = []
        for episode in range(episodes):
            observation, _ = env.reset(seed=seed + stage * 101 + episode)
            info = env.map_info()
            width, height = int(info["width"]), int(info["height"])
            total = 0.0
            status = 0
            actions_taken = 0
            while actions_taken < int(env._process_args[3]):
                actions = env.list_actions()
                agent_id, _ = select_agent_actions(actions)
                units = env.unit_info()
                actor = next(unit for unit in units if int(unit["id"]) == agent_id)
                is_enemy = int(actor["force"]) == ENEMY_FORCE
                if is_enemy and enemy_policy == "happo":
                    decision = happo_decision(
                        env, observation, width, height, actions=actions
                    )
                    choice, _ = model.choose(
                        decision, decision_role(env, decision), deterministic=True
                    )
                    action_index = int(decision.actions[choice]["index"])
                else:
                    action_index = scripted_action(actions, units, width, height)
                observation, reward, terminated, truncated, info = env.step(action_index)
                if is_enemy:
                    total -= float(reward)
                actions_taken += 1
                status = int(info.get("status", 0))
                if terminated or truncated:
                    break
            won = float(status == DEFEAT)
            wins.append(won)
            stage_wins.append(won)
            returns.append(total)
            lengths.append(float(actions_taken))
            timeouts.append(float(actions_taken >= int(env._process_args[3]) and status not in (3, DEFEAT)))
        stage_win_rates.append(float(np.mean(stage_wins)))
    successes = int(sum(wins))
    return {
        "enemy_win_rate": float(np.mean(wins)),
        "enemy_win_rate_ci95": wilson_interval(successes, len(wins)),
        "enemy_mean_return": float(np.mean(returns)),
        "mean_actions": float(np.mean(lengths)),
        "timeout_rate": float(np.mean(timeouts)),
        "stage_win_rate_p10": float(np.quantile(stage_win_rates, 0.10)),
        "stage_win_rate_p50": float(np.quantile(stage_win_rates, 0.50)),
        "episodes": float(len(wins)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=DONGZHOU_STAGE_COUNT)
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--max-episode-actions", type=int, default=160)
    parser.add_argument("--seed", type=int, default=12026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = MengdeEnv(
        args.executable,
        scenario="dongzhou",
        max_episode_actions=args.max_episode_actions,
        interactive=True,
    )
    try:
        stages = discover_battles(env, args.stage_count)
        env._restart_process(stages[0])
        observation, _ = env.reset(seed=args.seed)
        model, payload = load_model(args.model, len(observation))
        baseline = evaluate(
            env, model, stages, args.episodes, args.seed, "scripted"
        )
        happo = evaluate(env, model, stages, args.episodes, args.seed, "happo")
    finally:
        env.close()

    win_delta = happo["enemy_win_rate"] - baseline["enemy_win_rate"]
    return_delta = happo["enemy_mean_return"] - baseline["enemy_mean_return"]
    beats_baseline = win_delta > 0.0 or (
        win_delta == 0.0 and return_delta > 0.05
    )
    enough_seeds = args.episodes >= 3
    trained_roles = list(payload.get("trained_roles", ()))
    core_roles = {"King", "Infantry", "Cavalry", "Archer", "Strategist", "Support"}
    untrained_core_roles = sorted(core_roles.difference(trained_roles))
    gate_passed = beats_baseline and enough_seeds and happo["timeout_rate"] <= 0.05
    balance_calibrated = 0.15 <= happo["enemy_win_rate"] <= 0.85
    report = {
        "model": str(args.model),
        "scope": "enemy policy versus the same deterministic scripted player",
        "battle_stages": len(stages),
        "episodes_per_stage": args.episodes,
        "trained_roles": trained_roles,
        "untrained_core_roles": untrained_core_roles,
        "scripted_baseline": baseline,
        "happo": happo,
        "delta": {
            "enemy_win_rate": win_delta,
            "enemy_mean_return": return_delta,
        },
        "release_gate": {
            "beats_scripted_baseline": beats_baseline,
            "multiple_seeds": enough_seeds,
            "timeout_rate_at_most_5_percent": happo["timeout_rate"] <= 0.05,
            "balanced_against_scripted_player": balance_calibrated,
            "requires_runtime_fallback_for_untrained_roles": bool(untrained_core_roles),
            "status": (
                "pass-with-runtime-calibration-required"
                if gate_passed and not balance_calibrated
                else "pass-with-runtime-guards" if gate_passed else "candidate-only"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
