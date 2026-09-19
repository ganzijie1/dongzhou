"""Learned action ranker for formation-aware enemy tactics."""

from __future__ import annotations

import heapq
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch import nn


FEATURE_NAMES = (
    "wait",
    "move",
    "attack",
    "magic",
    "damage",
    "actor_ranged",
    "actor_melee",
    "actor_hp",
    "target_hp_missing",
    "advance",
    "retreat",
    "ends_at_range",
    "team_ranged_shot",
    "actor_ranged_shot",
    "actor_melee_attack",
    "blocks_ranged_path",
    "clears_ranged_path",
    "move_after_clear",
    "near_friendly_ranged",
    "low_hp_actor",
)
FEATURE_COUNT = len(FEATURE_NAMES)
DEFAULT_MODEL_PATH = Path(__file__).with_name("models") / "enemy_tactical_ranker.pt"


class TacticalRanker(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(FEATURE_COUNT, 48),
            nn.Tanh(),
            nn.Linear(48, 24),
            nn.Tanh(),
            nn.Linear(24, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features).squeeze(-1)


def load_ranker(path: str | Path = DEFAULT_MODEL_PATH) -> TacticalRanker:
    payload = torch.load(Path(path), map_location="cpu")
    if tuple(payload.get("feature_names", ())) != FEATURE_NAMES:
        raise ValueError("tactical policy feature schema does not match this runtime")
    model = TacticalRanker()
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _attack_offsets(unit: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    offsets = unit.get("attack_offsets")
    if offsets:
        return tuple((int(offset[0]), int(offset[1])) for offset in offsets)
    minimum = int(unit.get("attack_min", 1))
    maximum = int(unit.get("attack_max", minimum))
    return tuple(
        (dx, dy)
        for dx in range(-maximum, maximum + 1)
        for dy in range(-maximum, maximum + 1)
        if minimum <= abs(dx) + abs(dy) <= maximum
    )


def _attack_limits(unit: dict[str, Any]) -> tuple[int, int]:
    distances = [abs(dx) + abs(dy) for dx, dy in _attack_offsets(unit)]
    return (min(distances), max(distances)) if distances else (0, 0)


def _in_attack_range(position: tuple[int, int], target: tuple[int, int], unit: dict[str, Any]) -> bool:
    relative = (target[0] - position[0], target[1] - position[1])
    return relative in _attack_offsets(unit)


def attack_offsets(unit: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    """Return the native attack mask in a planner-friendly immutable form."""
    return _attack_offsets(unit)


def attack_limits(unit: dict[str, Any]) -> tuple[int, int]:
    """Return the minimum and maximum Manhattan radii of the attack mask."""
    return _attack_limits(unit)


def in_attack_range(
    position: tuple[int, int], target: tuple[int, int], unit: dict[str, Any]
) -> bool:
    return _in_attack_range(position, target, unit)


def _shortest_path(
    width: int,
    height: int,
    costs: Sequence[int],
    start: tuple[int, int],
    goals: set[tuple[int, int]],
    blocked: set[tuple[int, int]],
) -> list[tuple[int, int]] | None:
    """Dijkstra over the real class-specific terrain costs."""
    if not goals:
        return None
    distance = {start: 0}
    parent: dict[tuple[int, int], tuple[int, int]] = {}
    queue = [(0, start)]
    while queue:
        current_cost, current = heapq.heappop(queue)
        if current_cost != distance.get(current):
            continue
        if current in goals:
            path = [current]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            return path
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            nxt = (current[0] + dx, current[1] + dy)
            if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                continue
            if nxt in blocked and nxt != start:
                continue
            step_cost = int(costs[nxt[1] * width + nxt[0]])
            if step_cost >= 255:
                continue
            candidate = current_cost + step_cost
            if candidate >= distance.get(nxt, 1 << 30):
                continue
            distance[nxt] = candidate
            parent[nxt] = current
            heapq.heappush(queue, (candidate, nxt))
    return None


def _ranged_path_blockers(
    units: Sequence[dict[str, Any]],
    acting_force: int,
    opponents: Sequence[dict[str, Any]],
    width: int,
    height: int,
    movement_costs: dict[int, Sequence[int]] | None,
) -> dict[int, set[tuple[int, int]]]:
    """Return only rear melee units that prevent every route to a firing cell."""
    alive = [unit for unit in units if not bool(unit.get("dead", False))]
    occupied = {(int(unit["x"]), int(unit["y"])): unit for unit in alive}
    opponent_cells = {(int(unit["x"]), int(unit["y"])) for unit in opponents}
    blockers: dict[int, set[tuple[int, int]]] = {}

    for archer in alive:
        archer_id = int(archer["id"])
        if (
            int(archer["force"]) != acting_force
            or bool(archer.get("done", False))
            or _attack_limits(archer)[0] < 2
        ):
            continue
        start = (int(archer["x"]), int(archer["y"]))
        costs = (
            list(movement_costs[archer_id])
            if movement_costs is not None and archer_id in movement_costs
            else [1] * (width * height)
        )
        goals: set[tuple[int, int]] = set()
        for target in opponents:
            target_cell = (int(target["x"]), int(target["y"]))
            for dx, dy in _attack_offsets(archer):
                cell = (target_cell[0] - dx, target_cell[1] - dy)
                if (
                    0 <= cell[0] < width
                    and 0 <= cell[1] < height
                    and int(costs[cell[1] * width + cell[0]]) < 255
                    and cell not in opponent_cells
                ):
                    goals.add(cell)

        all_occupied = set(occupied) - {start}
        if _shortest_path(width, height, costs, start, goals, all_occupied) is not None:
            continue

        # If terrain itself has no route, moving allies cannot help. Otherwise
        # inspect the best route with friendly occupancy temporarily removed.
        path = _shortest_path(width, height, costs, start, goals, opponent_cells)
        if path is None:
            continue
        for cell in path[1:]:
            unit = occupied.get(cell)
            if unit is None or int(unit["force"]) != acting_force:
                continue
            unit_id = int(unit["id"])
            if _attack_limits(unit)[0] >= 2:
                continue
            nearest_enemy = min(
                (_distance(cell, (int(target["x"]), int(target["y"]))) for target in opponents),
                default=99,
            )
            if nearest_enemy <= 1:
                continue
            blockers.setdefault(unit_id, set()).update(path)
            break
    return blockers


def ranged_path_blockers(
    units: Sequence[dict[str, Any]],
    acting_force: int,
    opponents: Sequence[dict[str, Any]],
    width: int,
    height: int,
    movement_costs: dict[int, Sequence[int]] | None,
) -> dict[int, set[tuple[int, int]]]:
    """Expose exact Dijkstra blocker detection to the joint-turn planner."""
    return _ranged_path_blockers(
        units, acting_force, opponents, width, height, movement_costs
    )


def _local_ranged_blockers(
    units: Sequence[dict[str, Any]], acting_force: int,
    opponents: Sequence[dict[str, Any]],
) -> dict[int, set[tuple[int, int]]]:
    """Cheap blocker signal for large RL rollouts; exact runtime uses Dijkstra."""
    friendly = [
        unit for unit in units
        if int(unit["force"]) == acting_force and not bool(unit.get("dead", False))
    ]
    ranged = [unit for unit in friendly if _attack_limits(unit)[0] >= 2]
    blockers: dict[int, set[tuple[int, int]]] = {}
    for unit in friendly:
        if _attack_limits(unit)[0] >= 2:
            continue
        cell = (int(unit["x"]), int(unit["y"]))
        nearest_enemy = min(
            opponents,
            key=lambda enemy: _distance(
                cell, (int(enemy["x"]), int(enemy["y"]))
            ),
            default=None,
        )
        if nearest_enemy is None:
            continue
        target = (int(nearest_enemy["x"]), int(nearest_enemy["y"]))
        if _distance(cell, target) <= 1:
            continue
        for archer in ranged:
            origin = (int(archer["x"]), int(archer["y"]))
            if (
                _distance(origin, cell) <= 2
                and _distance(origin, cell) + _distance(cell, target)
                <= _distance(origin, target) + 1
            ):
                blockers[int(unit["id"])] = {cell}
                break
    return blockers


def action_features(
    actions: Sequence[dict[str, Any]],
    units: Sequence[dict[str, Any]],
    width: int,
    height: int,
    movement_costs: dict[int, Sequence[int]] | None = None,
    fast_path_features: bool = False,
) -> np.ndarray:
    """Describe each legal action without encoding hero or stage identities."""
    by_id = {int(unit["id"]): unit for unit in units if not bool(unit.get("dead", False))}
    if not actions:
        return np.empty((0, FEATURE_COUNT), dtype=np.float32)

    acting_force = int(by_id[int(actions[0]["unit"])]["force"])
    opponents = [unit for unit in by_id.values() if int(unit["force"]) != acting_force]
    ready_ranged = [
        unit
        for unit in by_id.values()
        if int(unit["force"]) == acting_force
        and not bool(unit.get("done", False))
        and _attack_limits(unit)[0] >= 2
    ]
    ranged_ids = {int(unit["id"]) for unit in ready_ranged}
    team_ranged_shot = any(
        int(action["type"]) == 2 and int(action["unit"]) in ranged_ids for action in actions
    )
    path_blockers = (
        _local_ranged_blockers(list(by_id.values()), acting_force, opponents)
        if fast_path_features
        else _ranged_path_blockers(
            list(by_id.values()), acting_force, opponents, width, height, movement_costs
        )
    )

    result = np.zeros((len(actions), FEATURE_COUNT), dtype=np.float32)
    for row, action in enumerate(actions):
        actor = by_id[int(action["unit"])]
        actor_id = int(actor["id"])
        action_type = int(action["type"])
        current = (int(actor["x"]), int(actor["y"]))
        destination = (int(action["x"]), int(action["y"]))
        attack_min, _ = _attack_limits(actor)
        is_ranged = attack_min >= 2

        current_distance = min(
            (_distance(current, (int(unit["x"]), int(unit["y"]))) for unit in opponents),
            default=0,
        )
        destination_distance = min(
            (_distance(destination, (int(unit["x"]), int(unit["y"]))) for unit in opponents),
            default=0,
        )
        delta = float(current_distance - destination_distance) / 12.0

        target = by_id.get(int(action["target"])) if action.get("target") is not None else None
        target_missing = 0.0
        if target is not None:
            target_missing = 1.0 - float(target["hp"]) / max(1.0, float(target["max_hp"]))

        actor_hp = float(actor["hp"]) / max(1.0, float(actor["max_hp"]))
        near_ranged = any(
            int(unit["id"]) != actor_id
            and _distance(current, (int(unit["x"]), int(unit["y"]))) <= 2
            for unit in ready_ranged
        )
        blocking_paths = path_blockers.get(actor_id, set())
        clears_path = (
            bool(blocking_paths)
            and action_type == 1
            and destination != current
            and destination not in blocking_paths
        )

        result[row] = (
            action_type == 0,
            action_type == 1,
            action_type == 2,
            action_type == 3,
            min(1.0, float(action.get("damage", 0)) / 160.0),
            is_ranged,
            not is_ranged,
            actor_hp,
            target_missing,
            max(0.0, delta),
            max(0.0, -delta),
            any(
                _in_attack_range(destination, (int(unit["x"]), int(unit["y"])), actor)
                for unit in opponents
            ),
            team_ranged_shot,
            is_ranged and action_type == 2,
            (not is_ranged) and action_type == 2,
            bool(blocking_paths),
            clears_path,
            clears_path and destination_distance >= 1,
            near_ranged,
            actor_hp < 0.35,
        )
    return result


def choose_action(
    model: TacticalRanker,
    actions: Sequence[dict[str, Any]],
    units: Sequence[dict[str, Any]],
    width: int,
    height: int,
    ppo_probabilities: np.ndarray | None = None,
    movement_costs: dict[int, Sequence[int]] | None = None,
) -> int:
    features = action_features(actions, units, width, height, movement_costs)
    with torch.no_grad():
        scores = model(torch.from_numpy(features)).cpu().numpy()
    if ppo_probabilities is not None:
        indices = np.asarray([int(action["index"]) for action in actions], dtype=np.int64)
        prior = np.log(np.maximum(ppo_probabilities[indices], 1e-9))
        scores = scores + 0.18 * np.clip(prior, -10.0, 0.0)
    return int(actions[int(np.argmax(scores))]["index"])
