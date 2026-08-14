"""Evaluate CriticAdaptiveCQL directly with discrete max-Q selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.adaptive_cql import CriticAdaptiveCQL
from rl.compare_adaptive_cql_happo import evaluate
from rl.offline_dataset import OfflineDataset


class MaxQPolicy:
    def __init__(self, model): self.model=model
    @torch.no_grad()
    def probabilities(self,state,decision):
        state_tensor=torch.as_tensor(state).unsqueeze(0)
        candidates=torch.as_tensor(decision.candidates).unsqueeze(0)
        q=torch.minimum(self.model.q1(state_tensor,candidates),self.model.q2(state_tensor,candidates))[0]
        return torch.softmax(q-q.max(),dim=-1).cpu().numpy()
    def choose(self,state,decision): return int(np.argmax(self.probabilities(state,decision)))


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
    dataset=OfflineDataset.load(args.dataset); model=CriticAdaptiveCQL(int(dataset.states.shape[1]))
    payload=torch.load(args.checkpoint,map_location="cpu")
    model.q1.load_state_dict(payload["q1"]); model.q2.load_state_dict(payload["q2"])
    model.q1.eval(); model.q2.eval()
    result=evaluate(MaxQPolicy(model),"critic_max_q",args)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2),flush=True)


if __name__=="__main__": main()