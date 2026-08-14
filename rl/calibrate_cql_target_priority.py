"""Pairwise target calibration for CQL Q-functions with value distillation."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import numpy as np
import torch

from rl.evaluate_happo_target_priority import candidate
from rl.happo import HAPPO_ACTION_FEATURES
from rl.happo_target_aux import target_priority_ranking_loss
from rl.offline_rl import CQL


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--seed", type=int, default=2055)
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    payload = torch.load(args.input, map_location="cpu")
    model = CQL(516, action_features=HAPPO_ACTION_FEATURES, seed=args.seed)
    model.q1.load_state_dict(payload["q1"])
    model.q2.load_state_dict(payload["q2"])
    reference_q1 = copy.deepcopy(model.q1).eval()
    reference_q2 = copy.deepcopy(model.q2).eval()
    optimizer = torch.optim.Adam(
        [*model.q1.parameters(), *model.q2.parameters()], lr=1.5e-4
    )
    base = np.stack([
        candidate(2, 0.85),
        candidate(2, 0.20, hp=1, lowest_hp=1),
        candidate(2, 0.70, defense=1, lowest_def=1),
        candidate(3, 0.85),
        candidate(3, 0.20, hp=1, lowest_hp=1),
        candidate(3, 0.70, spirit=1, lowest_spirit=1),
    ])
    batch = 48
    candidates = torch.from_numpy(np.repeat(base[None, :, :], batch, axis=0))
    mask = torch.ones((batch, len(base)), dtype=torch.bool)
    for _ in range(args.steps):
        states = torch.randn((batch, 516)) * 0.10
        q1 = model.q1(states, candidates)
        q2 = model.q2(states, candidates)
        with torch.no_grad():
            old_q1 = reference_q1(states, candidates)
            old_q2 = reference_q2(states, candidates)
        ranking = 0.5 * (
            target_priority_ranking_loss(q1, candidates, mask, margin=0.18)
            + target_priority_ranking_loss(q2, candidates, mask, margin=0.18)
        )
        distillation = 0.5 * (
            torch.square(q1 - old_q1).mean() + torch.square(q2 - old_q2).mean()
        )
        loss = ranking + 0.06 * distillation
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_([*model.q1.parameters(), *model.q2.parameters()], 1.0)
        optimizer.step()
    output = dict(payload)
    output["q1"] = model.q1.state_dict()
    output["q2"] = model.q2.state_dict()
    output["target_priority_calibration"] = {
        "source": str(args.input), "steps": args.steps,
        "distillation_weight": 0.06, "pairwise_margin": 0.18,
        "seed": args.seed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(output, args.output)
    print(f"calibrated CQL target priority: {args.output}")


if __name__ == "__main__":
    main()
