"""Equal-data comparison of HAPPO, CQL, and critic-adaptive CQL."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from rl.adaptive_cql import CriticAdaptiveCQL
from rl.compare_adaptive_cql_happo import normalized_entropy
from rl.compare_ppo_mappo import make_env
from rl.happo import (
    HAPPO, HAPPO_ACTION_FEATURES, HAPPOTransition, decision_role, happo_decision,
)
from rl.mappo import ACTION_FEATURES
from rl.offline_dataset import _pack
from rl.offline_rl import CQL


VICTORY = 3


def parse_args() -> argparse.Namespace:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable",type=Path,required=True)
    parser.add_argument("--scenario",default="example")
    parser.add_argument("--interactions",type=int,default=1024)
    parser.add_argument("--rollout-steps",type=int,default=256)
    parser.add_argument("--happo-epochs",type=int,default=4)
    parser.add_argument("--happo-batch-size",type=int,default=128)
    parser.add_argument("--cql-updates",type=int,default=1024)
    parser.add_argument("--cql-batch-size",type=int,default=128)
    parser.add_argument("--attack-coverage-bonus",type=float,default=3.0)
    parser.add_argument("--attack-setup-bonus",type=float,default=1.25)
    parser.add_argument("--eval-episodes",type=int,default=10)
    parser.add_argument("--max-episode-actions",type=int,default=100)
    parser.add_argument("--seed",type=int,default=2026)
    parser.add_argument("--output",type=Path,required=True)
    return parser.parse_args()


def collect_shared_rollout(
    model,env,count,seed,records,attack_coverage_bonus,attack_setup_bonus
):
    observation,_=env.reset(seed=seed); map_info=env.map_info()
    width=int(map_info["width"]); height=int(map_info["height"])
    transitions=[]; episodes=0
    for step in range(count):
        actions=env.list_actions()
        happo_choice=happo_decision(env,observation,width,height,actions=actions)
        role=decision_role(env,happo_choice); value=model._value(observation)
        behavior_bias=np.asarray([
            attack_coverage_bonus
            if int(action["type"])==2
            else attack_setup_bonus
            if int(action["type"])==1 and happo_choice.candidates[row,ACTION_FEATURES+11]>0
            else 0.0
            for row,action in enumerate(happo_choice.actions)
        ],dtype=np.float32)
        choice,log_probability=model.choose(
            happo_choice,role,behavior_bias=behavior_bias
        )
        next_observation,reward,terminated,truncated,_=env.step(
            int(happo_choice.actions[choice]["index"])
        )
        done=terminated or truncated
        transitions.append(HAPPOTransition(
            state=observation.copy(),local=happo_choice.local,
            candidates=happo_choice.candidates,choice=choice,role=role,
            log_prob=log_probability,value=value,reward=float(reward),done=done,
            behavior_bias=behavior_bias,
        ))
        if done:
            next_local=np.zeros_like(happo_choice.local)
            next_candidates=np.zeros((1,HAPPO_ACTION_FEATURES),dtype=np.float32)
        else:
            next_choice=happo_decision(env,next_observation,width,height)
            next_local=next_choice.local.copy()
            next_candidates=next_choice.candidates.copy()
        records.append({
            "state":observation.copy(),"local":happo_choice.local.copy(),
            "candidates":happo_choice.candidates.copy(),"action":choice,
            "reward":float(reward),"next_state":next_observation.copy(),
            "next_local":next_local,"next_candidates":next_candidates,"done":done,
        })
        observation=next_observation
        if done:
            episodes+=1; observation,_=env.reset(seed=seed+step+1)
    model._bootstrap_value=model._value(observation)
    return transitions,episodes


@torch.no_grad()
def happo_probability(model,decision,role):
    local=torch.as_tensor(decision.local).unsqueeze(0)
    candidates=torch.as_tensor(decision.candidates).unsqueeze(0)
    logits=model.actors[role](local,candidates)[0]
    return torch.softmax(logits,dim=-1).cpu().numpy()


def evaluate(model,algorithm,args):
    rows=[]; entropies=[]; counts=np.zeros(4,dtype=np.int64)
    with make_env(args) as env:
        map_info=env.map_info(); width=int(map_info["width"]); height=int(map_info["height"])
        for episode in range(args.eval_episodes):
            observation,info=env.reset(seed=args.seed+50000+episode)
            total=0.0; actions_taken=0
            while True:
                if algorithm=="happo":
                    decision=happo_decision(env,observation,width,height)
                    role=decision_role(env,decision)
                    probability=happo_probability(model,decision,role)
                    choice,_=model.choose(decision,role,deterministic=True)
                else:
                    decision=happo_decision(env,observation,width,height)
                    probability=model.probabilities(observation,decision) if hasattr(model,"probabilities") else None
                    if probability is None:
                        state=torch.as_tensor(observation).unsqueeze(0)
                        candidates=torch.as_tensor(decision.candidates).unsqueeze(0)
                        values=torch.minimum(model.q1(state,candidates),model.q2(state,candidates))[0]
                        probability=torch.softmax(values-values.max(),dim=-1).detach().cpu().numpy()
                    choice=model.choose(observation,decision)
                entropies.append(normalized_entropy(probability))
                counts[int(decision.actions[choice]["type"])]+=1
                observation,reward,terminated,truncated,info=env.step(
                    int(decision.actions[choice]["index"])
                )
                total+=float(reward); actions_taken+=1
                if terminated or truncated: break
            rows.append((total,float(int(info["status"])==VICTORY),actions_taken))
    return {
        "mean_return":float(np.mean([r[0] for r in rows])),
        "return_std":float(np.std([r[0] for r in rows])),
        "win_rate":float(np.mean([r[1] for r in rows])),
        "mean_actions":float(np.mean([r[2] for r in rows])),
        "mean_normalized_entropy":float(np.mean(entropies)),
        "action_type_counts":counts.tolist(),
        "max_action_type_share":float(counts.max()/max(1,counts.sum())),
    }


def main():
    args=parse_args(); torch.set_num_threads(1); args.output.mkdir(parents=True,exist_ok=True)
    if args.interactions<=0 or args.rollout_steps<=0: raise ValueError("interaction budgets must be positive")
    records=[]; happo_history=[]; collected_episodes=0
    with make_env(args) as env:
        observation,_=env.reset(seed=args.seed)
        state_features=int(env.observation_space.shape[0])
        happo=HAPPO(state_features,seed=args.seed)
        started=time.perf_counter(); completed=0
        while completed<args.interactions:
            count=min(args.rollout_steps,args.interactions-completed)
            transitions,episodes=collect_shared_rollout(
                happo,env,count,args.seed+completed,records,
                args.attack_coverage_bonus,args.attack_setup_bonus,
            )
            metrics=happo.update(
                transitions,epochs=args.happo_epochs,batch_size=args.happo_batch_size
            )
            completed+=count; collected_episodes+=episodes
            happo_history.append({"interactions":completed,**metrics})
        happo_seconds=time.perf_counter()-started
    dataset=_pack(records); assert len(dataset)==args.interactions
    dataset.save(args.output/"equal_data.npz")
    happo.save(args.output/"happo_equal_data.pt")

    cql=CQL(state_features,action_features=HAPPO_ACTION_FEATURES,seed=args.seed)
    started=time.perf_counter(); cql_training=cql.train(dataset,args.cql_updates,batch_size=args.cql_batch_size)
    cql_seconds=time.perf_counter()-started; cql.save(args.output/"cql_equal_data.pt")

    adaptive=CriticAdaptiveCQL(
        state_features,action_features=HAPPO_ACTION_FEATURES,seed=args.seed
    )
    started=time.perf_counter(); adaptive_training=adaptive.train(dataset,args.cql_updates,batch_size=args.cql_batch_size)
    adaptive_seconds=time.perf_counter()-started
    adaptive.save(args.output/"critic_adaptive_cql_equal_data.pt")

    results={
        "happo":evaluate(happo,"happo",args),
        "cql":evaluate(cql,"cql",args),
        "critic_adaptive_cql":evaluate(adaptive,"critic_adaptive_cql",args),
    }
    report={
        "fairness":{
            "environment_interactions_per_algorithm":args.interactions,
            "shared_transition_count":len(dataset),
            "data_origin":"Every transition came from one shared HAPPO behavior run. A fixed, recorded attack-logit bias improves basic-attack coverage and is included in both old and new PPO probabilities.",
            "evaluation_seed_start":args.seed+50000,
            "evaluation_episodes":args.eval_episodes,
            "happo_sample_reuse_epochs":args.happo_epochs,
            "attack_coverage_bonus":args.attack_coverage_bonus,
            "attack_setup_bonus":args.attack_setup_bonus,
            "candidate_action_features":HAPPO_ACTION_FEATURES,
            "cql_gradient_updates":args.cql_updates,
            "cql_batch_size":args.cql_batch_size,
            "compute_budget_equalized":False,
        },
        "collection":{"episodes_completed":collected_episodes,"dataset_action_type_counts":np.bincount(np.argmax(dataset.candidates[np.arange(len(dataset)),dataset.actions,:4],axis=1),minlength=4).tolist()},
        "training":{
            "happo":{"seconds":happo_seconds,"history":happo_history},
            "cql":{"seconds":cql_seconds,**cql_training},
            "critic_adaptive_cql":{"seconds":adaptive_seconds,**adaptive_training},
        },
        "results":results,
        "scope":"Equal environment data and identical evaluation seeds; optimizer compute is reported but intentionally not forced equal because offline CQL reuses a fixed dataset.",
    }
    (args.output/"equal_data_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=="__main__": main()