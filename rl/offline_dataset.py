"""Fixed offline dataset collection for candidate-based Mengde policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from rl.happo import decision_role
from rl.mappo import (
    ACTION_FEATURES, LOCAL_FEATURES, MAPPO, SharedActor, current_decision,
)
from rl.mengde_env import MengdeEnv


@dataclass
class OfflineDataset:
    states: np.ndarray
    locals: np.ndarray
    candidates: np.ndarray
    masks: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    next_states: np.ndarray
    next_locals: np.ndarray
    next_candidates: np.ndarray
    next_masks: np.ndarray
    dones: np.ndarray

    def __len__(self) -> int:
        return len(self.actions)

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(destination, **self.__dict__)

    @classmethod
    def load(cls, path: str | Path) -> "OfflineDataset":
        with np.load(Path(path), allow_pickle=False) as payload:
            return cls(**{name: payload[name] for name in cls.__annotations__})


LEGACY_ROLES = (
    "Lord", "Infantry", "Cavalry", "Archer", "Strategist", "Artillery",
    "Fighter", "Bandit", "Other",
)


class LegacyBehaviorHAPPO:
    """Loads the 14-feature HAPPO expert used to build the offline dataset."""

    def __init__(self, path: Path) -> None:
        self.actors = nn.ModuleDict({role: SharedActor() for role in LEGACY_ROLES})
        self.actors.load_state_dict(torch.load(path, map_location="cpu")["actors"])
        self.actors.eval()

    @torch.no_grad()
    def choose(
        self, decision, role: str, deterministic: bool = True
    ) -> tuple[int, float]:
        local = torch.as_tensor(decision.local).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates).unsqueeze(0)
        key = role if role in LEGACY_ROLES else "Other"
        distribution = Categorical(logits=self.actors[key](local, candidates)[0])
        choice = torch.argmax(distribution.logits) if deterministic else distribution.sample()
        return int(choice), float(distribution.log_prob(choice))

def load_behavior_models(state_features: int) -> tuple[LegacyBehaviorHAPPO, MAPPO]:
    happo = LegacyBehaviorHAPPO(
        Path("rl/models/ppo_mappo_happo_comparison/happo.pt")
    )
    mappo = MAPPO(state_features, seed=2026)
    mappo_payload = torch.load(
        Path("rl/models/ppo_mappo_comparison/mappo.pt"), map_location="cpu"
    )
    mappo.actor.load_state_dict(mappo_payload["actor"])
    mappo.critic.load_state_dict(mappo_payload["critic"])
    return happo, mappo


def _pack(records: list[dict[str, Any]]) -> OfflineDataset:
    if not records:
        raise ValueError("cannot pack an empty offline dataset")
    feature_count = int(records[0]["candidates"].shape[1])
    if any(
        int(item["candidates"].shape[1]) != feature_count
        or int(item["next_candidates"].shape[1]) != feature_count
        for item in records
    ):
        raise ValueError("offline candidate feature schemas do not match")
    maximum = max(
        max(len(item["candidates"]), len(item["next_candidates"])) for item in records
    )
    count = len(records)
    candidates = np.zeros((count, maximum, feature_count), dtype=np.float32)
    next_candidates = np.zeros_like(candidates)
    masks = np.zeros((count, maximum), dtype=np.bool_)
    next_masks = np.zeros_like(masks)
    for row, item in enumerate(records):
        current_count = len(item["candidates"])
        next_count = len(item["next_candidates"])
        candidates[row, :current_count] = item["candidates"]
        next_candidates[row, :next_count] = item["next_candidates"]
        masks[row, :current_count] = True
        next_masks[row, :next_count] = True
    return OfflineDataset(
        states=np.stack([item["state"] for item in records]).astype(np.float32),
        locals=np.stack([item["local"] for item in records]).astype(np.float32),
        candidates=candidates, masks=masks,
        actions=np.asarray([item["action"] for item in records], dtype=np.int64),
        rewards=np.asarray([item["reward"] for item in records], dtype=np.float32),
        next_states=np.stack([item["next_state"] for item in records]).astype(np.float32),
        next_locals=np.stack([item["next_local"] for item in records]).astype(np.float32),
        next_candidates=next_candidates, next_masks=next_masks,
        dones=np.asarray([item["done"] for item in records], dtype=np.float32),
    )


def collect_offline_dataset(
    env: MengdeEnv,
    episodes: int,
    *,
    seed: int = 2026,
    epsilon: float = 0.15,
) -> tuple[OfflineDataset, dict[str, Any]]:
    if episodes < 3:
        raise ValueError("use at least three episodes to cover all behavior policies")
    happo, mappo = load_behavior_models(int(env.observation_space.shape[0]))
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    modes = ("happo", "happo", "mappo", "random")
    for episode in range(episodes):
        mode = modes[episode % len(modes)]
        observation, info = env.reset(seed=seed + episode)
        episode_return = 0.0
        episode_actions = 0
        while True:
            decision = current_decision(env, observation, width, height)
            if mode == "random" or rng.random() < epsilon:
                choice = int(rng.integers(len(decision.actions)))
            elif mode == "happo":
                role = decision_role(env, decision)
                choice, _ = happo.choose(decision, role, deterministic=True)
            else:
                choice, _, _ = mappo.choose(decision, deterministic=True)
            next_observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            done = terminated or truncated
            if done:
                next_local = np.zeros(LOCAL_FEATURES, dtype=np.float32)
                next_candidates = np.zeros((1, ACTION_FEATURES), dtype=np.float32)
            else:
                next_decision = current_decision(
                    env, next_observation, width, height
                )
                next_local = next_decision.local
                next_candidates = next_decision.candidates
            records.append(
                {
                    "state": observation.copy(), "local": decision.local.copy(),
                    "candidates": decision.candidates.copy(), "action": choice,
                    "reward": float(reward), "next_state": next_observation.copy(),
                    "next_local": next_local.copy(),
                    "next_candidates": next_candidates.copy(), "done": done,
                }
            )
            observation = next_observation
            episode_return += float(reward)
            episode_actions += 1
            if done:
                break
        summaries.append(
            {"mode": mode, "return": episode_return, "actions": episode_actions,
             "victory": int(info["status"]) == 3}
        )
    dataset = _pack(records)
    return dataset, {
        "episodes": episodes,
        "transitions": len(dataset),
        "maximum_candidates": int(dataset.candidates.shape[1]),
        "mean_return": float(np.mean([item["return"] for item in summaries])),
        "win_rate": float(np.mean([item["victory"] for item in summaries])),
        "mean_actions": float(np.mean([item["actions"] for item in summaries])),
        "behavior_counts": {
            mode: sum(item["mode"] == mode for item in summaries)
            for mode in sorted(set(item["mode"] for item in summaries))
        },
        "epsilon": epsilon,
    }
