"""Compare support-regularized CQL with legacy CQL and HAPPO."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

from rl.adaptive_cql import SupportedCQL
from rl.compare_adaptive_cql_happo import evaluate
from rl.compare_happo_enemy_checkpoints import LegacyHAPPO
from rl.offline_dataset import OfflineDataset
from rl.offline_rl import CQL


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable",type=Path,required=True)
    parser.add_argument("--dataset",type=Path,default=Path("rl/models/offline_iql_cql_comparison/dataset.npz"))
    parser.add_argument("--legacy-cql",type=Path,default=Path("rl/models/offline_iql_cql_comparison/cql.pt"))
    parser.add_argument("--happo",type=Path,default=Path("rl/models/ppo_mappo_happo_comparison/happo.pt"))
    parser.add_argument("--updates",type=int,default=600)
    parser.add_argument("--batch-size",type=int,default=128)
    parser.add_argument("--eval-episodes",type=int,default=10)
    parser.add_argument("--max-episode-actions",type=int,default=100)
    parser.add_argument("--seed",type=int,default=2026)
    parser.add_argument("--scenario",default="example")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(); torch.set_num_threads(1); args.output.mkdir(parents=True,exist_ok=True)
    dataset=OfflineDataset.load(args.dataset); state_features=int(dataset.states.shape[1])

    legacy=CQL(state_features,seed=args.seed); payload=torch.load(args.legacy_cql,map_location="cpu")
    legacy.q1.load_state_dict(payload["q1"]); legacy.q2.load_state_dict(payload["q2"])
    legacy.q1.eval(); legacy.q2.eval()

    supported=SupportedCQL(state_features,seed=args.seed)
    supported.load_legacy_values(args.legacy_cql)
    started=time.perf_counter(); training=supported.train_support(dataset,args.updates,batch_size=args.batch_size)
    training_seconds=time.perf_counter()-started

    happo=LegacyHAPPO(args.happo)
    results={"legacy_cql":evaluate(legacy,"legacy_cql",args),"happo":evaluate(happo,"happo",args)}
    for weight in (0.02,0.05,0.1,0.2):
        supported.support_weight=weight
        results[f"supported_cql_{weight}"]=evaluate(supported,"supported_cql",args)
    supported.support_weight=0.05
    supported.save(args.output/"supported_cql.pt")
    report={
        "configuration":{"dataset":str(args.dataset),"transitions":len(dataset),"updates":args.updates,"batch_size":args.batch_size,"eval_episodes":args.eval_episodes,"evaluation_seed_start":args.seed+10000},
        "support_training":{"seconds":training_seconds,"parameters":supported.parameter_count,**training},
        "results":results,
        "selection":"support_weight=0.05 is the deployment candidate only if it preserves legacy CQL win rate while reducing concentration.",
        "scope":"All policies use identical example-scenario episodes and seeds. SupportedCQL reuses the proven legacy twin-Q checkpoint.",
    }
    (args.output/"supported_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=="__main__": main()