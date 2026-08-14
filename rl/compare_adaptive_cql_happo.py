"""Compare legacy CQL, collapse-resistant AdaptiveCQL, and HAPPO fairly."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from rl.adaptive_cql import AdaptiveCQL
from rl.compare_happo_enemy_checkpoints import LEGACY_ROLES, LegacyHAPPO
from rl.compare_ppo_mappo import make_env
from rl.mappo import Decision, current_decision
from rl.offline_dataset import OfflineDataset
from rl.offline_rl import CQL


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument(
        "--dataset", type=Path,
        default=Path("rl/models/offline_iql_cql_comparison/dataset.npz"),
    )
    parser.add_argument(
        "--legacy-cql", type=Path,
        default=Path("rl/models/offline_iql_cql_comparison/cql.pt"),
    )
    parser.add_argument(
        "--happo", type=Path,
        default=Path("rl/models/ppo_mappo_happo_comparison/happo.pt"),
    )
    parser.add_argument("--updates", type=int, default=600)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--max-episode-actions", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path,
        default=Path("rl/models/adaptive_cql_happo_comparison"),
    )
    parser.add_argument("--scenario", default="example")
    return parser.parse_args()


def normalized_entropy(probability: np.ndarray) -> float:
    if len(probability) <= 1:
        return 1.0
    values = np.clip(probability.astype(np.float64), 1e-12, 1.0)
    return float(-(values * np.log(values)).sum() / np.log(len(values)))


@torch.no_grad()
def legacy_cql_distribution(model: CQL, observation: np.ndarray, decision: Decision) -> np.ndarray:
    state = torch.as_tensor(observation).unsqueeze(0)
    candidates = torch.as_tensor(decision.candidates).unsqueeze(0)
    values = torch.minimum(model.q1(state, candidates), model.q2(state, candidates))[0]
    return torch.softmax(values - values.max(), dim=-1).cpu().numpy()


@torch.no_grad()
def happo_distribution(model: LegacyHAPPO, decision: Decision, role: str) -> np.ndarray:
    local = torch.as_tensor(decision.local).unsqueeze(0)
    candidates = torch.as_tensor(decision.candidates).unsqueeze(0)
    key = role if role in LEGACY_ROLES else "Other"
    logits = model.actors[key](local, candidates)[0]
    return torch.softmax(logits, dim=-1).cpu().numpy()


def evaluate(model: Any, algorithm: str, args: argparse.Namespace) -> dict[str, Any]:
    episode_rows: list[dict[str, Any]] = []
    action_counts = np.zeros(4, dtype=np.int64)
    entropies: list[float] = []
    with make_env(args) as env:
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        for episode in range(args.eval_episodes):
            observation, info = env.reset(seed=args.seed + 10_000 + episode)
            total, actions = 0.0, 0
            while True:
                decision = current_decision(env, observation, width, height)
                if algorithm == "happo":
                    unit = next(
                        item for item in env.unit_info()
                        if int(item["id"]) == decision.agent_id
                    )
                    role = str(unit["class"])
                    probability = happo_distribution(model, decision, role)
                    choice = model.choose(decision, role)
                elif algorithm == "legacy_cql":
                    probability = legacy_cql_distribution(model, observation, decision)
                    choice = model.choose(observation, decision)
                else:
                    probability = model.probabilities(observation, decision)
                    choice = model.choose(observation, decision)
                entropies.append(normalized_entropy(probability))
                action_type = int(decision.actions[choice]["type"])
                action_counts[max(0, min(3, action_type))] += 1
                observation, reward, terminated, truncated, info = env.step(
                    int(decision.actions[choice]["index"])
                )
                total += float(reward)
                actions += 1
                if terminated or truncated:
                    break
            episode_rows.append({
                "return": total,
                "victory": float(int(info["status"]) == VICTORY),
                "actions": float(actions),
            })
    total_actions = max(1, int(action_counts.sum()))
    return {
        "mean_return": float(np.mean([row["return"] for row in episode_rows])),
        "return_std": float(np.std([row["return"] for row in episode_rows])),
        "win_rate": float(np.mean([row["victory"] for row in episode_rows])),
        "mean_actions": float(np.mean([row["actions"] for row in episode_rows])),
        "mean_normalized_entropy": float(np.mean(entropies)),
        "action_type_counts": action_counts.tolist(),
        "max_action_type_share": float(action_counts.max() / total_actions),
    }


def main() -> None:
    args = parse_args()
    torch.set_num_threads(1)
    args.output.mkdir(parents=True, exist_ok=True)
    dataset = OfflineDataset.load(args.dataset)
    state_features = int(dataset.states.shape[1])

    legacy_cql = CQL(state_features, seed=args.seed)
    legacy_payload = torch.load(args.legacy_cql, map_location="cpu")
    legacy_cql.q1.load_state_dict(legacy_payload["q1"])
    legacy_cql.q2.load_state_dict(legacy_payload["q2"])
    legacy_cql.q1.eval()
    legacy_cql.q2.eval()

    adaptive = AdaptiveCQL(state_features, seed=args.seed)
    started = time.perf_counter()
    update_metrics = adaptive.train(
        dataset, args.updates, batch_size=args.batch_size
    )
    training_seconds = time.perf_counter() - started
    adaptive.save(args.output / "adaptive_cql.pt")

    happo = LegacyHAPPO(args.happo)
    results = {
        "legacy_cql": evaluate(legacy_cql, "legacy_cql", args),
        "adaptive_cql": evaluate(adaptive, "adaptive_cql", args),
        "happo": evaluate(happo, "happo", args),
    }
    report = {
        "configuration": {
            "scenario": args.scenario,
            "dataset": str(args.dataset),
            "dataset_transitions": len(dataset),
            "updates": args.updates,
            "batch_size": args.batch_size,
            "eval_episodes": args.eval_episodes,
            "max_episode_actions": args.max_episode_actions,
            "evaluation_seed_start": args.seed + 10_000,
        },
        "adaptive_cql_training": {
            "seconds": training_seconds,
            "parameters": adaptive.parameter_count,
            **update_metrics,
        },
        "results": results,
        "entropy_note": (
            "AdaptiveCQL and HAPPO report policy entropy. Legacy CQL has no actor; "
            "its value is the entropy of softmax-normalized Q scores."
        ),
        "scope": (
            "All policies use identical evaluation episodes and seeds on the example "
            "scenario. The immutable offline dataset is shared with the earlier CQL report."
        ),
    }
    destination = args.output / "report.json"
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()