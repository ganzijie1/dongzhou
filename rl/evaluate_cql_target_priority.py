"""Controlled Q-value probe for 34-feature CQL target priorities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.evaluate_happo_target_priority import candidate
from rl.happo import HAPPO_ACTION_FEATURES
from rl.offline_rl import CQL


def load_model(path: Path) -> CQL:
    payload = torch.load(path, map_location="cpu")
    model = CQL(516, action_features=HAPPO_ACTION_FEATURES, seed=2054)
    model.q1.load_state_dict(payload["q1"])
    model.q2.load_state_dict(payload["q2"])
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    model = load_model(args.model)
    probes = torch.from_numpy(np.stack([
        candidate(2, 0.85),
        candidate(2, 0.20, hp=1, lowest_hp=1),
        candidate(2, 0.70, defense=1, lowest_def=1),
        candidate(3, 0.85),
        candidate(3, 0.20, hp=1, lowest_hp=1),
        candidate(3, 0.70, spirit=1, lowest_spirit=1),
    ])).unsqueeze(0)
    state = torch.zeros((1, 516), dtype=torch.float32)
    with torch.no_grad():
        q1 = model.q1(state, probes)[0]
        q2 = model.q2(state, probes)[0]
        values = torch.minimum(q1, q2).tolist()
    checks = {
        "physical_low_hp_over_robust": values[1] > values[0],
        "physical_low_def_over_robust": values[2] > values[0],
        "magic_low_hp_over_robust": values[4] > values[3],
        "magic_low_spirit_over_robust": values[5] > values[3],
    }
    report = {
        "model": str(args.model), "q_values": values, "checks": checks,
        "checks_passed": sum(checks.values()), "checks_total": len(checks),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
