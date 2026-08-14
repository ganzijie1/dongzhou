"""Probe deterministic Q/support fusion without retraining AdaptiveCQL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.adaptive_cql import AdaptiveCQL
from rl.compare_adaptive_cql_happo import normalized_entropy
from rl.compare_ppo_mappo import make_env
from rl.mappo import current_decision
from rl.offline_dataset import OfflineDataset


VICTORY = 3


def load_model(path: Path, state_features: int) -> AdaptiveCQL:
    payload = torch.load(path, map_location="cpu")
    model = AdaptiveCQL(state_features)
    model.q1.load_state_dict(payload["q1"])
    model.q2.load_state_dict(payload["q2"])
    model.policy.load_state_dict(payload["policy"])
    model.q1.eval(); model.q2.eval(); model.policy.eval()
    return model


@torch.no_grad()
def distribution(model, observation, decision, support_weight):
    state = torch.as_tensor(observation).unsqueeze(0)
    local = torch.as_tensor(decision.local).unsqueeze(0)
    candidates = torch.as_tensor(decision.candidates).unsqueeze(0)
    q = torch.minimum(
        model.q1(state, local, candidates), model.q2(state, local, candidates)
    )[0]
    q = (q - q.mean()) / q.std().clamp(min=0.25)
    support = torch.log_softmax(model.policy(local, candidates)[0], dim=-1)
    return torch.softmax(q + support_weight * support, dim=-1).cpu().numpy()


def evaluate(model, weight, args):
    rows, entropies = [], []
    counts = np.zeros(4, dtype=np.int64)
    with make_env(args) as env:
        map_info = env.map_info(); width=int(map_info["width"]); height=int(map_info["height"])
        for episode in range(args.eval_episodes):
            observation, info = env.reset(seed=args.seed + 10_000 + episode)
            total = 0.0; actions = 0
            while True:
                decision = current_decision(env, observation, width, height)
                probability = distribution(model, observation, decision, weight)
                choice = int(np.argmax(probability))
                counts[int(decision.actions[choice]["type"])] += 1
                entropies.append(normalized_entropy(probability))
                observation, reward, terminated, truncated, info = env.step(
                    int(decision.actions[choice]["index"])
                )
                total += float(reward); actions += 1
                if terminated or truncated: break
            rows.append((total, float(int(info["status"]) == VICTORY), actions))
    return {
        "mean_return": float(np.mean([r[0] for r in rows])),
        "win_rate": float(np.mean([r[1] for r in rows])),
        "mean_actions": float(np.mean([r[2] for r in rows])),
        "mean_normalized_entropy": float(np.mean(entropies)),
        "action_type_counts": counts.tolist(),
        "max_action_type_share": float(counts.max() / max(1, counts.sum())),
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable",type=Path,required=True)
    parser.add_argument("--checkpoint",type=Path,required=True)
    parser.add_argument("--dataset",type=Path,default=Path("rl/models/offline_iql_cql_comparison/dataset.npz"))
    parser.add_argument("--eval-episodes",type=int,default=10)
    parser.add_argument("--max-episode-actions",type=int,default=100)
    parser.add_argument("--seed",type=int,default=2026)
    parser.add_argument("--scenario",default="example")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(); torch.set_num_threads(1)
    dataset=OfflineDataset.load(args.dataset)
    model=load_model(args.checkpoint,int(dataset.states.shape[1]))
    results={str(w):evaluate(model,w,args) for w in (0.0,0.25,0.5,1.0,2.0)}
    args.output.write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2),flush=True)


if __name__=="__main__": main()