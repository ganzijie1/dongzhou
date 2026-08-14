"""Controlled actor-logit probe for the trained HAPPO target priorities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from rl.happo import HAPPO, HAPPO_ACTION_FEATURES
from rl.happo_targeting import (
    TARGET_DEF_WEAKNESS,
    TARGET_HP_WEAKNESS,
    TARGET_LOWEST_DEF,
    TARGET_LOWEST_HP,
    TARGET_LOWEST_SPIRIT,
    TARGET_SPIRIT_WEAKNESS,
)


ACTIVE_ROLES = ("King", "Infantry", "Cavalry", "Strategist")


def candidate(action_type: int, hp_ratio: float, *, hp=0.0, defense=0.0, spirit=0.0,
              lowest_hp=0.0, lowest_def=0.0, lowest_spirit=0.0) -> np.ndarray:
    value = np.zeros(HAPPO_ACTION_FEATURES, dtype=np.float32)
    value[action_type] = 1.0
    value[10] = hp_ratio
    offset = 14
    value[offset + action_type] = 1.0
    value[offset + TARGET_HP_WEAKNESS] = hp
    value[offset + TARGET_DEF_WEAKNESS] = defense
    value[offset + TARGET_SPIRIT_WEAKNESS] = spirit
    value[offset + TARGET_LOWEST_HP] = lowest_hp
    value[offset + TARGET_LOWEST_DEF] = lowest_def
    value[offset + TARGET_LOWEST_SPIRIT] = lowest_spirit
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = torch.load(args.model, map_location="cpu")
    model = HAPPO(516, seed=2048)
    model.actors.load_state_dict(payload["actors"])
    local = torch.zeros((1, 20), dtype=torch.float32)
    probes = np.stack([
        candidate(2, 0.85),
        candidate(2, 0.20, hp=1, lowest_hp=1),
        candidate(2, 0.70, defense=1, lowest_def=1),
        candidate(3, 0.85),
        candidate(3, 0.20, hp=1, lowest_hp=1),
        candidate(3, 0.70, spirit=1, lowest_spirit=1),
    ])
    candidates = torch.from_numpy(probes).unsqueeze(0)
    rows = {}
    successes = 0
    checks = 0
    with torch.no_grad():
        for role in ACTIVE_ROLES:
            logits = model.actors[role](local, candidates)[0].tolist()
            passed = {
                "physical_low_hp_over_robust": logits[1] > logits[0],
                "physical_low_def_over_robust": logits[2] > logits[0],
                "magic_low_hp_over_robust": logits[4] > logits[3],
                "magic_low_spirit_over_robust": logits[5] > logits[3],
            }
            successes += sum(passed.values())
            checks += len(passed)
            rows[role] = {"logits": logits, "passed": passed}
    report = {
        "model": str(args.model),
        "active_roles": list(ACTIVE_ROLES),
        "checks_passed": successes,
        "checks_total": checks,
        "pass_rate": successes / checks,
        "roles": rows,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if successes < checks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
