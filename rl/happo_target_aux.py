"""Pairwise auxiliary loss for HAPPO target ranking."""

from __future__ import annotations

import torch

from rl.mappo import ACTION_FEATURES
from rl.happo_targeting import (
    TARGET_DEF_WEAKNESS,
    TARGET_HP_WEAKNESS,
    TARGET_LOWEST_DEF,
    TARGET_LOWEST_HP,
    TARGET_LOWEST_SPIRIT,
    TARGET_SPIRIT_WEAKNESS,
)


def target_priority_ranking_loss(
    logits: torch.Tensor, candidates: torch.Tensor, mask: torch.Tensor,
    margin: float = 0.12,
) -> torch.Tensor:
    """Rank vulnerable targets only within physical or magic alternatives."""
    losses: list[torch.Tensor] = []
    offset = ACTION_FEATURES
    for row in range(logits.shape[0]):
        for action_type in (2, 3):
            valid = mask[row] & (candidates[row, :, action_type] > 0.5)
            indices = torch.nonzero(valid, as_tuple=False).flatten()
            if indices.numel() < 2:
                continue
            selected = candidates[row, indices]
            hp = selected[:, offset + TARGET_HP_WEAKNESS]
            low_hp = selected[:, offset + TARGET_LOWEST_HP]
            if action_type == 2:
                resistance = selected[:, offset + TARGET_DEF_WEAKNESS]
                lowest = selected[:, offset + TARGET_LOWEST_DEF]
            else:
                resistance = selected[:, offset + TARGET_SPIRIT_WEAKNESS]
                lowest = selected[:, offset + TARGET_LOWEST_SPIRIT]
            priority = 0.40 * hp + 0.35 * resistance + 0.15 * low_hp + 0.10 * lowest
            pair_preferred = priority[:, None] > priority[None, :] + 1e-5
            if not bool(pair_preferred.any()):
                continue
            score = logits[row, indices]
            score_gap = score[:, None] - score[None, :]
            losses.append(torch.relu(margin - score_gap[pair_preferred]).mean())
    if not losses:
        return logits.sum() * 0.0
    return torch.stack(losses).mean()
