"""Gradient-level regression for HAPPO target ranking auxiliary loss."""

import torch

from rl.happo import HAPPO_ACTION_FEATURES
from rl.happo_target_aux import target_priority_ranking_loss
from rl.happo_targeting import TARGET_DEF_WEAKNESS, TARGET_LOWEST_DEF
from rl.mappo import ACTION_FEATURES


def main() -> None:
    candidates = torch.zeros((1, 3, HAPPO_ACTION_FEATURES))
    candidates[0, :, 2] = 1.0
    candidates[0, 1, ACTION_FEATURES + TARGET_DEF_WEAKNESS] = 1.0
    candidates[0, 1, ACTION_FEATURES + TARGET_LOWEST_DEF] = 1.0
    logits = torch.zeros((1, 3), requires_grad=True)
    mask = torch.ones((1, 3), dtype=torch.bool)
    before = target_priority_ranking_loss(logits, candidates, mask)
    before.backward()
    assert float(before) > 0.0
    assert logits.grad is not None
    assert float(logits.grad[0, 1]) < 0.0

    preferred = torch.tensor([[0.0, 0.5, 0.0]], requires_grad=True)
    after = target_priority_ranking_loss(preferred, candidates, mask)
    assert float(after) < float(before)
    print("happo target aux ok: pairwise loss raises vulnerable-target logits")


if __name__ == "__main__":
    main()
