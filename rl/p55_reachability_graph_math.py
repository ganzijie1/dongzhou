"""P55 graph reachability, safe paths, SCCs, attractors, and probabilities."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Sequence

import numpy as np


def reachable_set(adjacency: Sequence, start_states: Sequence[int], *, max_steps: int | None = None) -> np.ndarray:
    graph = np.asarray(adjacency, dtype=bool)
    starts = np.asarray(start_states)
    if graph.ndim != 2 or graph.shape[0] != graph.shape[1] or graph.shape[0] == 0 or starts.ndim != 1 or np.any(starts != np.floor(starts)) or np.any(starts < 0) or np.any(starts >= graph.shape[0]) or (max_steps is not None and (not isinstance(max_steps, int) or max_steps < 0)):
        raise ValueError("reachability inputs are invalid")
    reached = np.zeros(graph.shape[0], dtype=bool)
    reached[starts.astype(int)] = True
    frontier = reached.copy()
    steps = 0
    while np.any(frontier) and (max_steps is None or steps < max_steps):
        following = np.any(graph[frontier], axis=0) & ~reached
        reached |= following
        frontier = following
        steps += 1
    return reached


@dataclass(frozen=True)
class SafePathResult:
    path: tuple[int, ...]
    cost: float


def shortest_reach_avoid_path(
    edge_costs: Sequence,
    start: int,
    target_states: Sequence[int],
    forbidden_states: Sequence[int] = (),
) -> SafePathResult:
    costs = np.asarray(edge_costs, dtype=np.float64)
    targets = set(int(value) for value in target_states)
    forbidden = set(int(value) for value in forbidden_states)
    count = costs.shape[0] if costs.ndim == 2 else 0
    if costs.shape != (count, count) or count == 0 or np.any(np.isnan(costs)) or np.any(costs < 0.0) or start < 0 or start >= count or any(value < 0 or value >= count for value in targets | forbidden) or not targets or start in forbidden:
        raise ValueError("safe-path inputs are invalid")
    distance = np.full(count, np.inf)
    parent = np.full(count, -1, dtype=int)
    distance[start] = 0.0
    queue = [(0.0, start)]
    goal = -1
    while queue:
        current_distance, state = heappop(queue)
        if current_distance != distance[state]:
            continue
        if state in targets:
            goal = state
            break
        for following, edge in enumerate(costs[state]):
            if following in forbidden or not np.isfinite(edge) or following == state:
                continue
            candidate = current_distance + edge
            if candidate < distance[following]:
                distance[following] = candidate
                parent[following] = state
                heappush(queue, (candidate, following))
    if goal < 0:
        return SafePathResult((), float("inf"))
    path = []
    state = goal
    while state >= 0:
        path.append(state)
        state = parent[state]
    return SafePathResult(tuple(reversed(path)), float(distance[goal]))


def strongly_connected_components(adjacency: Sequence) -> tuple[tuple[int, ...], ...]:
    graph = np.asarray(adjacency, dtype=bool)
    if graph.ndim != 2 or graph.shape[0] != graph.shape[1] or graph.shape[0] == 0:
        raise ValueError("adjacency must be a non-empty square matrix")
    index = 0
    indices = np.full(graph.shape[0], -1, dtype=int)
    low = np.zeros(graph.shape[0], dtype=int)
    stack: list[int] = []
    on_stack = np.zeros(graph.shape[0], dtype=bool)
    components: list[tuple[int, ...]] = []

    def visit(vertex: int) -> None:
        nonlocal index
        indices[vertex] = low[vertex] = index
        index += 1
        stack.append(vertex)
        on_stack[vertex] = True
        for following in np.flatnonzero(graph[vertex]):
            if indices[following] < 0:
                visit(int(following))
                low[vertex] = min(low[vertex], low[following])
            elif on_stack[following]:
                low[vertex] = min(low[vertex], indices[following])
        if low[vertex] == indices[vertex]:
            component = []
            while True:
                item = stack.pop()
                on_stack[item] = False
                component.append(item)
                if item == vertex:
                    break
            components.append(tuple(sorted(component)))

    for vertex in range(graph.shape[0]):
        if indices[vertex] < 0:
            visit(vertex)
    return tuple(sorted(components))


@dataclass(frozen=True)
class AttractorResult:
    winning: np.ndarray
    rank: np.ndarray
    policy: np.ndarray


def adversarial_attractor(successors: Sequence, target_states: Sequence[int]) -> AttractorResult:
    transition = np.asarray(successors)
    if transition.ndim != 3 or transition.shape[0] == 0 or np.any(transition != np.floor(transition)) or np.any(transition < 0) or np.any(transition >= transition.shape[0]):
        raise ValueError("successors must have shape [state, action, adversary_action]")
    transition = transition.astype(int)
    winning = np.zeros(transition.shape[0], dtype=bool)
    targets = np.asarray(target_states)
    if targets.ndim != 1 or np.any(targets != np.floor(targets)) or np.any(targets < 0) or np.any(targets >= transition.shape[0]):
        raise ValueError("target states are invalid")
    winning[targets.astype(int)] = True
    rank = np.full(transition.shape[0], -1, dtype=int)
    rank[winning] = 0
    policy = np.full(transition.shape[0], -1, dtype=int)
    step = 0
    while True:
        step += 1
        added = np.zeros_like(winning)
        for state in np.flatnonzero(~winning):
            for action in range(transition.shape[1]):
                if np.all(winning[transition[state, action]]):
                    added[state] = True
                    policy[state] = action
                    rank[state] = step
                    break
        if not np.any(added):
            break
        winning |= added
    return AttractorResult(winning, rank, policy)


def maximum_reach_probability(
    transitions: Sequence,
    target_states: Sequence[int],
    avoid_states: Sequence[int] = (),
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 10_000,
) -> tuple[np.ndarray, np.ndarray]:
    probability = np.asarray(transitions, dtype=np.float64)
    if probability.ndim != 3 or probability.shape[0] == 0 or probability.shape[2] != probability.shape[0] or np.any(probability < 0.0) or np.any(~np.isfinite(probability)) or not np.allclose(probability.sum(axis=2), 1.0) or tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("probabilistic reachability inputs are invalid")
    target = np.zeros(probability.shape[0], dtype=bool)
    avoid = np.zeros_like(target)
    target[np.asarray(target_states, dtype=int)] = True
    avoid[np.asarray(avoid_states, dtype=int)] = True
    if np.any(target & avoid):
        raise ValueError("target and avoid sets must be disjoint")
    value = target.astype(np.float64)
    policy = np.full(probability.shape[0], -1, dtype=int)
    for _ in range(max_iterations):
        q_values = probability @ value
        updated = np.max(q_values, axis=1)
        updated[target] = 1.0
        updated[avoid] = 0.0
        policy = np.argmax(q_values, axis=1)
        policy[target | avoid] = -1
        if np.max(np.abs(updated - value)) <= tolerance:
            return updated, policy
        value = updated
    raise RuntimeError("reachability value iteration did not converge")
