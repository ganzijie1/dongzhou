"""Ensure every heterogeneous runtime actor learned target vulnerability."""

from pathlib import Path

import numpy as np
import torch

from rl.evaluate_happo_target_priority import candidate
from rl.happo import HAPPO, ROLE_NAMES


def main() -> None:
    payload = torch.load(Path("rl/models/runtime/happo.pt"), map_location="cpu")
    model = HAPPO(516, seed=2053)
    model.actors.load_state_dict(payload["actors"])
    probes = torch.from_numpy(np.stack([
        candidate(2, 0.85),
        candidate(2, 0.20, hp=1, lowest_hp=1),
        candidate(2, 0.70, defense=1, lowest_def=1),
        candidate(3, 0.85),
        candidate(3, 0.20, hp=1, lowest_hp=1),
        candidate(3, 0.70, spirit=1, lowest_spirit=1),
    ])).unsqueeze(0)
    local = torch.zeros((1, 20), dtype=torch.float32)
    with torch.no_grad():
        for role in ROLE_NAMES:
            logits = model.actors[role](local, probes)[0]
            assert float(logits[1]) > float(logits[0]), (role, "physical low HP")
            assert float(logits[2]) > float(logits[0]), (role, "physical low DEF")
            assert float(logits[4]) > float(logits[3]), (role, "magic low HP")
            assert float(logits[5]) > float(logits[3]), (role, "magic low INT")
    print(f"happo all-role targeting ok: {len(ROLE_NAMES) * 4} preference checks")


if __name__ == "__main__":
    main()
