"""Calibrate target ranking while distilling an already capable HAPPO policy."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import numpy as np
import torch

from rl.evaluate_happo_target_priority import candidate
from rl.happo import HAPPO, ROLE_NAMES
from rl.happo_target_aux import target_priority_ranking_loss


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--seed", type=int, default=2051)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    payload = torch.load(args.input, map_location="cpu")
    model = HAPPO(516, seed=args.seed)
    model.actors.load_state_dict(payload["actors"])
    reference = copy.deepcopy(model.actors).eval()
    optimizers = {
        role: torch.optim.Adam(model.actors[role].parameters(), lr=2e-4)
        for role in ROLE_NAMES
    }

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

    for role in ROLE_NAMES:
        optimizer = optimizers[role]
        for _ in range(args.steps):
            local = torch.randn((batch, 20)) * 0.18
            logits = model.actors[role](local, candidates)
            with torch.no_grad():
                old_logits = reference[role](local, candidates)
            ranking = target_priority_ranking_loss(
                logits, candidates, mask, margin=0.22
            )
            distillation = torch.square(logits - old_logits).mean()
            loss = ranking + 0.04 * distillation
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.actors[role].parameters(), 0.5)
            optimizer.step()

    output = dict(payload)
    output["actors"] = model.actors.state_dict()
    output["target_priority_calibration"] = {
        "source": str(args.input),
        "steps_per_role": args.steps,
        "distillation_weight": 0.04,
        "pairwise_margin": 0.22,
        "seed": args.seed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(output, args.output)
    print(f"calibrated HAPPO target priority: {args.output}")


if __name__ == "__main__":
    main()
