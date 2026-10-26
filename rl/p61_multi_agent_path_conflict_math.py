"""P61 multi-agent path conflicts, reservations, CBS/ECBS helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Sequence

import numpy as np


@dataclass(frozen=True)
class PathConflict:
    kind: str
    agents: tuple[int, int]
    time: int
    resource: tuple[Hashable, ...]


def _position(path: Sequence[Hashable], time: int) -> Hashable:
    if not path:
        raise ValueError("paths must be non-empty")
    return path[min(time, len(path) - 1)]


def first_discrete_conflict(paths: Sequence[Sequence[Hashable]]) -> PathConflict | None:
    if not paths or any(not path for path in paths):
        raise ValueError("paths must be non-empty")
    horizon = max(map(len, paths))
    for time in range(horizon):
        for left in range(len(paths)):
            for right in range(left + 1, len(paths)):
                a = _position(paths[left], time)
                b = _position(paths[right], time)
                if a == b:
                    return PathConflict("vertex", (left, right), time, (a,))
                if time > 0 and _position(paths[left], time - 1) == b and _position(paths[right], time - 1) == a:
                    return PathConflict("edge", (left, right), time, (a, b))
    return None


def build_reservation_table(paths: Sequence[Sequence[Hashable]]) -> dict[str, set[tuple]]:
    if any(not path for path in paths):
        raise ValueError("paths must be non-empty")
    vertices: set[tuple] = set()
    edges: set[tuple] = set()
    for agent, path in enumerate(paths):
        for time, vertex in enumerate(path):
            vertices.add((time, vertex, agent))
            if time:
                edges.add((time, path[time - 1], vertex, agent))
    return {"vertices": vertices, "edges": edges}


def path_violates_reservations(path: Sequence[Hashable], table: dict[str, set[tuple]]) -> bool:
    if not path or set(table) != {"vertices", "edges"}:
        raise ValueError("reservation inputs are invalid")
    for time, vertex in enumerate(path):
        if any(item[:2] == (time, vertex) for item in table["vertices"]):
            return True
        if time and any(item[:3] == (time, vertex, path[time - 1]) for item in table["edges"]):
            return True
    return False


def ecbs_focal_indices(costs: Sequence[float], lower_bound: float, suboptimality: float = 1.0) -> np.ndarray:
    values = np.asarray(costs, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or np.any(~np.isfinite(values)) or lower_bound < 0.0 or suboptimality < 1.0:
        raise ValueError("ECBS focal inputs are invalid")
    return np.flatnonzero(values <= suboptimality * lower_bound + 1e-12)


def continuous_time_conflict(
    start_a: Sequence[float], end_a: Sequence[float], start_b: Sequence[float], end_b: Sequence[float],
    *, radius_sum: float, duration: float = 1.0,
) -> tuple[bool, float, float]:
    a0, a1, b0, b1 = (np.asarray(value, dtype=np.float64) for value in (start_a, end_a, start_b, end_b))
    if a0.ndim != 1 or a0.shape != a1.shape or a0.shape != b0.shape or a0.shape != b1.shape or np.any(~np.isfinite(np.concatenate((a0, a1, b0, b1)))) or radius_sum < 0.0 or duration <= 0.0:
        raise ValueError("continuous conflict inputs are invalid")
    relative = a0 - b0
    velocity = ((a1 - a0) - (b1 - b0)) / duration
    speed2 = float(velocity @ velocity)
    time = 0.0 if speed2 == 0.0 else float(np.clip(-(relative @ velocity) / speed2, 0.0, duration))
    distance = float(np.linalg.norm(relative + time * velocity))
    return distance <= radius_sum + 1e-12, time, distance
