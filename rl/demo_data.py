"""Serialization helpers shared by demonstration collection and training."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from imitation.data.types import Transitions


def save_transitions(
    path: str | Path,
    observations: list[np.ndarray],
    actions: list[int],
    next_observations: list[np.ndarray],
    dones: list[bool],
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination,
        obs=np.asarray(observations, dtype=np.float32),
        acts=np.asarray(actions, dtype=np.int64),
        next_obs=np.asarray(next_observations, dtype=np.float32),
        dones=np.asarray(dones, dtype=np.bool_),
    )


def load_transitions(path: str | Path) -> Transitions:
    with np.load(Path(path), allow_pickle=False) as data:
        count = len(data["acts"])
        return Transitions(
            obs=data["obs"].astype(np.float32),
            acts=data["acts"].astype(np.int64),
            next_obs=data["next_obs"].astype(np.float32),
            dones=data["dones"].astype(np.bool_),
            infos=np.asarray([{} for _ in range(count)], dtype=object),
        )
