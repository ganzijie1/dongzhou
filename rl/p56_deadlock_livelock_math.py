"""P56 runtime deadlock, livelock, oscillation, and winding diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Sequence

import numpy as np


def wait_for_cycles(wait_for_adjacency: Sequence) -> tuple[tuple[int, ...], ...]:
    graph = np.asarray(wait_for_adjacency, dtype=bool)
    if graph.ndim != 2 or graph.shape[0] != graph.shape[1] or graph.shape[0] == 0:
        raise ValueError("wait-for graph must be a non-empty square matrix")
    count = graph.shape[0]
    closure = graph.copy()
    for middle in range(count):
        closure |= closure[:, middle, None] & closure[None, middle, :]
    unseen = set(range(count))
    cycles = []
    while unseen:
        vertex = min(unseen)
        component = tuple(sorted(node for node in unseen if closure[vertex, node] and closure[node, vertex]))
        if component:
            unseen.difference_update(component)
            if len(component) > 1 or graph[component[0], component[0]]:
                cycles.append(component)
        else:
            unseen.remove(vertex)
    return tuple(cycles)


def winding_number(positions: Sequence, center: Sequence[float]) -> float:
    path = np.asarray(positions, dtype=np.float64)
    origin = np.asarray(center, dtype=np.float64)
    if path.ndim != 2 or path.shape[0] < 2 or path.shape[1] != 2 or origin.shape != (2,) or np.any(~np.isfinite(path)) or np.any(~np.isfinite(origin)) or np.any(np.linalg.norm(path - origin, axis=1) <= 1e-12):
        raise ValueError("winding inputs are invalid")
    angles = np.unwrap(np.arctan2(path[:, 1] - origin[1], path[:, 0] - origin[0]))
    return float((angles[-1] - angles[0]) / (2.0 * np.pi))


def periodicity_score(states: Sequence[Hashable], *, max_period: int) -> tuple[int, float]:
    values = list(states)
    if len(values) < 2 or not isinstance(max_period, int) or max_period <= 0:
        raise ValueError("periodicity inputs are invalid")
    best_period = 1
    best_score = 0.0
    for period in range(1, min(max_period, len(values) - 1) + 1):
        score = sum(values[index] == values[index - period] for index in range(period, len(values))) / (len(values) - period)
        if score > best_score:
            best_period, best_score = period, score
    return best_period, float(best_score)


def direction_flip_count(positions: Sequence, direction: Sequence[float]) -> int:
    path = np.asarray(positions, dtype=np.float64)
    axis = np.asarray(direction, dtype=np.float64)
    if path.ndim != 2 or path.shape[0] < 3 or axis.shape != (path.shape[1],) or np.any(~np.isfinite(path)) or np.any(~np.isfinite(axis)) or np.linalg.norm(axis) <= 0.0:
        raise ValueError("direction-flip inputs are invalid")
    axis = axis / np.linalg.norm(axis)
    velocity = np.diff(path @ axis)
    nonzero = velocity[np.abs(velocity) > 1e-12]
    return int(np.sum(nonzero[1:] * nonzero[:-1] < 0.0))


@dataclass(frozen=True)
class BehaviorDiagnostic:
    path_length: float
    displacement: float
    command_effort: float
    progress: float
    stuck: bool
    livelock: bool
    idle: bool
    orbiting: bool


def diagnose_behavior_window(
    positions: Sequence,
    movement_commands: Sequence,
    progress_values: Sequence[float],
    *,
    obstacle_center: Sequence[float] | None = None,
    legal_wait: bool = False,
    displacement_tolerance: float = 0.1,
    progress_tolerance: float = 0.01,
    effort_threshold: float = 0.5,
    orbit_threshold: float = 0.75,
) -> BehaviorDiagnostic:
    path = np.asarray(positions, dtype=np.float64)
    commands = np.asarray(movement_commands, dtype=np.float64)
    progress_series = np.asarray(progress_values, dtype=np.float64)
    if path.ndim != 2 or path.shape[0] < 2 or commands.shape != (path.shape[0] - 1, path.shape[1]) or progress_series.shape != (path.shape[0],) or np.any(~np.isfinite(path)) or np.any(~np.isfinite(commands)) or np.any(~np.isfinite(progress_series)) or min(displacement_tolerance, progress_tolerance, effort_threshold, orbit_threshold) < 0.0:
        raise ValueError("behavior window is invalid")
    distances = np.linalg.norm(np.diff(path, axis=0), axis=1)
    path_length = float(distances.sum())
    displacement = float(np.linalg.norm(path[-1] - path[0]))
    effort = float(np.linalg.norm(commands, axis=1).sum())
    progress = float(progress_series[-1] - progress_series[0])
    stuck = effort >= effort_threshold and path_length <= displacement_tolerance
    idle = not legal_wait and effort < effort_threshold and path_length <= displacement_tolerance and abs(progress) <= progress_tolerance
    livelock = path_length > displacement_tolerance and displacement <= displacement_tolerance and progress <= progress_tolerance
    orbiting = False
    if obstacle_center is not None:
        orbiting = abs(winding_number(path, obstacle_center)) >= orbit_threshold and progress <= progress_tolerance
        livelock = livelock or orbiting
    return BehaviorDiagnostic(path_length, displacement, effort, progress, stuck, livelock, idle, orbiting)
