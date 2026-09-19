"""Use beam MPC decisions as supervised initialization for HAPPO actors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from torch.distributions import Categorical

from rl.beam_mpc import BeamMPC
from rl.happo import HAPPO, decision_role, happo_decision, normalized_role, pad_happo_candidates


@dataclass
class BeamTeacherSample:
    role: str
    local: np.ndarray
    candidates: np.ndarray
    choice: int


def collect_beam_teacher(
    env: Any, planner: BeamMPC, episodes: int, *, seed: int,
) -> tuple[list[BeamTeacherSample], dict[str, float]]:
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    samples: list[BeamTeacherSample] = []
    returns: list[float] = []
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total = 0.0
        while True:
            decision = happo_decision(env, observation, width, height)
            result = planner.search(env, observation)
            samples.append(BeamTeacherSample(
                decision_role(env, decision), decision.local.copy(),
                decision.candidates.copy(), result.choice,
            ))
            observation, reward, terminated, truncated, info = env.step(result.action)
            total += float(reward)
            if terminated or truncated:
                break
        returns.append(total)
    return samples, {
        "episodes": float(episodes), "samples": float(len(samples)),
        "mean_return": float(np.mean(returns)),
    }


def pretrain_happo_from_beam(
    model: HAPPO,
    samples: list[BeamTeacherSample],
    *,
    updates: int = 500,
    batch_size: int = 64,
    seed: int = 2026,
) -> dict[str, float]:
    if not samples:
        raise ValueError("beam initialization requires teacher samples")
    rng = np.random.default_rng(seed)
    metrics: list[tuple[float, float]] = []
    by_role = {
        role: [sample for sample in samples if normalized_role(sample.role) == role]
        for role in model.actors
    }
    populated = [role for role, values in by_role.items() if values]
    for _ in range(updates):
        role = populated[int(rng.integers(len(populated)))]
        pool = by_role[role]
        selected = [pool[int(index)] for index in rng.integers(len(pool), size=min(batch_size, len(pool)))]
        candidates, mask = pad_happo_candidates(
            [sample.candidates for sample in selected], model.device
        )
        local = torch.as_tensor(
            np.stack([sample.local for sample in selected]), device=model.device
        )
        labels = torch.as_tensor(
            [sample.choice for sample in selected], device=model.device
        )
        logits = model.actors[role](local, candidates).masked_fill(~mask, -1e9)
        distribution = Categorical(logits=logits)
        loss = -distribution.log_prob(labels).mean()
        optimizer = model.actor_optimizers[role]
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.actors[role].parameters(), 1.0)
        optimizer.step()
        accuracy = (torch.argmax(logits, dim=1) == labels).float().mean()
        metrics.append((float(loss.detach()), float(accuracy)))
    mean = np.mean(metrics[-100:], axis=0)
    return {
        "cross_entropy": float(mean[0]), "teacher_accuracy": float(mean[1]),
        "updates": float(updates), "samples": float(len(samples)),
    }
