"""Train the runtime HAPPO policy as the enemy across Dongzhou battles."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from rl.happo import HAPPO, HAPPOTransition, decision_role, happo_decision
from rl.happo_targeting import target_selection_reward
from rl.mengde_env import MengdeEnv
from rl.mappo import select_agent_actions
from rl.tactical_policy import action_features as tactical_action_features


DEFEAT = 4
ENEMY_FORCE = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-count", type=int, default=41)
    parser.add_argument("--passes", type=int, default=8)
    parser.add_argument("--steps-per-stage", type=int, default=128)
    parser.add_argument("--stages-per-update", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--max-episode-actions", type=int, default=160)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def scripted_action(
    actions: list[dict[str, Any]], units: list[dict[str, Any]], width: int, height: int
) -> int:
    """A stable sparring opponent; this is not used by the shipped enemy AI."""
    _, selected = select_agent_actions(actions)
    features = tactical_action_features(
        selected, units, width, height, fast_path_features=True
    )
    scores = (
        features[:, 4] * 12.0
        + features[:, 12] * 3.0
        + features[:, 13] * 2.0
        + features[:, 14] * 1.5
        + features[:, 9] * 1.2
        + features[:, 16] * 1.0
        - features[:, 0] * 0.5
        - features[:, 15] * 0.8
    )
    return int(selected[int(np.argmax(scores))]["index"])


def discover_battles(env: MengdeEnv, stage_count: int) -> list[int]:
    stages = []
    for stage in range(stage_count):
        env._restart_process(stage)
        if not bool(env.story_info().get("story_only", False)):
            stages.append(stage)
    return stages


def collect_enemy(
    model: HAPPO, env: MengdeEnv, steps: int, seed: int
) -> list[HAPPOTransition]:
    observation, _ = env.reset(seed=seed)
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    transitions: list[HAPPOTransition] = []
    native_steps = 0
    max_native_steps = max(steps * 12, env._process_args and steps)
    while len(transitions) < steps and native_steps < max_native_steps:
        actions = env.list_actions()
        agent_id, _ = select_agent_actions(actions)
        units = env.unit_info()
        actor = next(unit for unit in units if int(unit["id"]) == agent_id)
        is_enemy = int(actor["force"]) == ENEMY_FORCE
        if is_enemy:
            decision = happo_decision(
                env, observation, width, height, actions=actions
            )
            role = decision_role(env, decision)
            value = model._value(observation)
            choice, log_prob = model.choose(decision, role)
            chosen = decision.actions[choice]
            action_index = int(chosen["index"])
        else:
            action_index = scripted_action(actions, units, width, height)
        next_observation, reward, terminated, truncated, _ = env.step(action_index)
        native_steps += 1
        done = terminated or truncated
        if is_enemy:
            tactical = decision.candidates[choice, 14:]
            action_type = int(chosen["type"])
            shaped_reward = -float(reward)
            shaped_reward += 0.20 * float(action_type in (2, 3))
            shaped_reward += target_selection_reward(chosen, tactical, units)
            shaped_reward += min(
                0.60, float(chosen.get("damage", 0)) / 100.0
            )
            shaped_reward += 0.10 * float(tactical[9])
            shaped_reward += 0.08 * float(tactical[16])
            shaped_reward -= 0.05 * float(tactical[10])
            shaped_reward -= 0.04 * float(action_type == 0)
            transitions.append(
                HAPPOTransition(
                    state=observation.copy(),
                    local=decision.local,
                    candidates=decision.candidates,
                    choice=choice,
                    role=role,
                    log_prob=log_prob,
                    value=value,
                    reward=shaped_reward,
                    done=done,
                )
            )
        if done:
            if transitions:
                transitions[-1].done = True
            observation, _ = env.reset(seed=seed + native_steps)
        else:
            observation = next_observation
    if transitions:
        transitions[-1].done = True
    model._bootstrap_value = 0.0
    return transitions


def evaluate_enemy(
    model: HAPPO, env: MengdeEnv, stages: list[int], seed: int
) -> dict[str, float]:
    wins = []
    returns = []
    lengths = []
    for stage in stages:
        env._restart_process(stage)
        observation, _ = env.reset(seed=seed + stage * 101)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        total = 0.0
        actions_taken = 0
        status = 0
        while actions_taken < int(env._process_args[3]):
            actions = env.list_actions()
            agent_id, _ = select_agent_actions(actions)
            units = env.unit_info()
            actor = next(unit for unit in units if int(unit["id"]) == agent_id)
            is_enemy = int(actor["force"]) == ENEMY_FORCE
            if is_enemy:
                decision = happo_decision(
                    env, observation, width, height, actions=actions
                )
                role = decision_role(env, decision)
                choice, _ = model.choose(decision, role, deterministic=True)
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
        wins.append(float(status == DEFEAT))
        returns.append(total)
        lengths.append(float(actions_taken))
    return {
        "enemy_win_rate": float(np.mean(wins)),
        "enemy_mean_return": float(np.mean(returns)),
        "mean_actions": float(np.mean(lengths)),
    }


def main() -> None:
    args = parse_args()
    torch.set_num_threads(1)
    args.output.mkdir(parents=True, exist_ok=True)
    env = MengdeEnv(
        args.executable,
        scenario="dongzhou",
        max_episode_actions=args.max_episode_actions,
        interactive=True,
    )
    history: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        stages = discover_battles(env, args.stage_count)
        env._restart_process(stages[0])
        observation, _ = env.reset(seed=args.seed)
        model = HAPPO(len(observation), seed=args.seed)
        rng = np.random.default_rng(args.seed)
        completed = 0
        for curriculum_pass in range(1, args.passes + 1):
            ordered = [stages[int(i)] for i in rng.permutation(len(stages))]
            for start in range(0, len(ordered), args.stages_per_update):
                group = ordered[start : start + args.stages_per_update]
                rollout: list[HAPPOTransition] = []
                for stage in group:
                    print(json.dumps({
                        "event": "collect_start", "pass": curriculum_pass,
                        "stage": stage,
                    }), flush=True)
                    env._restart_process(stage)
                    segment = collect_enemy(
                        model,
                        env,
                        args.steps_per_stage,
                        args.seed + curriculum_pass * 10000 + stage * 131,
                    )
                    rollout.extend(segment)
                    print(json.dumps({
                        "event": "collect_done", "pass": curriculum_pass,
                        "stage": stage, "samples": len(segment),
                    }), flush=True)
                if not rollout:
                    continue
                model._bootstrap_value = 0.0
                metrics = model.update(
                    rollout, epochs=args.epochs, batch_size=args.batch_size
                )
                completed += len(rollout)
                row = {
                    "pass": curriculum_pass,
                    "stages": group,
                    "steps": completed,
                    "rollout": len(rollout),
                    **metrics,
                }
                history.append(row)
                print(json.dumps(row, ensure_ascii=True), flush=True)
            model.save(args.output / f"happo-pass-{curriculum_pass}.pt")
            model.save(args.output / "happo.pt")
        evaluation = evaluate_enemy(model, env, stages, args.seed + 900000)
    finally:
        env.close()
    report = {
        "algorithm": "HAPPO",
        "scenario": "dongzhou",
        "battle_stages": stages,
        "configuration": vars(args) | {
            "executable": str(args.executable), "output": str(args.output)
        },
        "enemy_training_steps": completed,
        "training_seconds": time.perf_counter() - started,
        "roles": list(model.actors.keys()),
        "evaluation": evaluation,
        "history": history,
    }
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report | {"history": history[-1:]}, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
