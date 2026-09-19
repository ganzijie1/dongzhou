"""Role-aware, reservation-based MAPF for sequential tactical turns."""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import inf
from typing import Any, Mapping, Sequence

from rl.tactical_policy import (
    attack_limits,
    attack_offsets,
    in_attack_range,
    ranged_path_blockers,
)


Cell = tuple[int, int]
Action = dict[str, Any]


def _position(item: Mapping[str, Any]) -> Cell:
    return int(item["x"]), int(item["y"])


def _distance(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _same_side(left: int, right: int) -> bool:
    if left == right:
        return True
    return bool(left & 0x03) and bool(right & 0x03)


def _weighted_path(
    start: Cell,
    destination: Cell,
    width: int,
    height: int,
    costs: Sequence[int] | None,
) -> tuple[Cell, ...]:
    """Rebuild one terrain-aware spatial path for time-expanded reservations."""
    if start == destination:
        return (start,)
    if costs is None or len(costs) != width * height:
        return (start, destination)
    frontier: list[tuple[float, float, Cell]] = [
        (float(_distance(start, destination)), 0.0, start)
    ]
    parents: dict[Cell, Cell] = {}
    best = {start: 0.0}
    while frontier:
        _, spent, cell = heappop(frontier)
        if spent != best.get(cell):
            continue
        if cell == destination:
            path = [cell]
            while path[-1] != start:
                path.append(parents[path[-1]])
            path.reverse()
            return tuple(path)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            neighbor = cell[0] + dx, cell[1] + dy
            if not (0 <= neighbor[0] < width and 0 <= neighbor[1] < height):
                continue
            step = int(costs[neighbor[1] * width + neighbor[0]])
            if step >= 255:
                continue
            candidate = spent + max(1, step)
            if candidate >= best.get(neighbor, inf):
                continue
            best[neighbor] = candidate
            parents[neighbor] = cell
            estimate = candidate + _distance(neighbor, destination)
            heappush(frontier, (estimate, candidate, neighbor))
    return (start, destination)


@dataclass(frozen=True)
class PlannerConfig:
    retreat_hp_ratio: float = 0.35
    retreat_priority: float = 120.0
    ranged_attack_priority: float = 90.0
    artillery_attack_bonus: float = 20.0
    clear_corridor_priority: float = 80.0
    attack_priority: float = 45.0
    fire_slot_bonus: float = 24.0
    risk_weight: float = 14.0
    distance_weight: float = 2.0
    prior_weight: float = 8.0
    wait_penalty: float = 4.0
    corridor_violation_penalty: float = 1000.0
    max_candidates_per_unit: int = 12
    time_horizon: int = 12
    wait_age_bonus: float = 3.0
    max_wait_age: int = 10


@dataclass(frozen=True)
class TacticalSlot:
    cell: Cell
    kind: str
    utility: float
    allowed_roles: frozenset[str]
    owner: int | None = None


@dataclass(frozen=True)
class CorridorReservation:
    cells: frozenset[Cell]
    beneficiaries: frozenset[int]


@dataclass
class TurnReservationTable:
    destinations: dict[Cell, int] = field(default_factory=dict)
    corridors: list[CorridorReservation] = field(default_factory=list)
    vertices: dict[tuple[int, Cell], int] = field(default_factory=dict)
    edges: dict[tuple[int, Cell, Cell], int] = field(default_factory=dict)

    def reserve_destination(self, cell: Cell, unit_id: int) -> bool:
        owner = self.destinations.get(cell)
        if owner is not None and owner != unit_id:
            return False
        self.destinations[cell] = unit_id
        return True

    def reserve_corridor(
        self, cells: Sequence[Cell], beneficiaries: Sequence[int]
    ) -> None:
        reservation = CorridorReservation(
            frozenset(cells), frozenset(int(value) for value in beneficiaries)
        )
        if reservation.cells and reservation not in self.corridors:
            self.corridors.append(reservation)

    def corridor_blocked(self, unit_id: int, cell: Cell, is_ranged: bool) -> bool:
        if is_ranged:
            return False
        return any(
            cell in reservation.cells
            and unit_id not in reservation.beneficiaries
            for reservation in self.corridors
        )

    def path_conflict(
        self,
        path: Sequence[Cell],
        unit_id: int,
        horizon: int,
    ) -> bool:
        if not path:
            return False
        owner = self.destinations.get(path[-1])
        if owner is not None and owner != unit_id:
            return True
        clipped = tuple(path[: horizon + 1])
        for time, cell in enumerate(clipped):
            owner = self.vertices.get((time, cell))
            if owner is not None and owner != unit_id:
                return True
            if time == 0:
                continue
            previous = clipped[time - 1]
            reverse_owner = self.edges.get((time, cell, previous))
            if reverse_owner is not None and reverse_owner != unit_id:
                return True
        temporal_destination = clipped[-1]
        for time in range(len(clipped), horizon + 1):
            owner = self.vertices.get((time, temporal_destination))
            if owner is not None and owner != unit_id:
                return True
        return False

    def reserve_path(
        self,
        path: Sequence[Cell],
        unit_id: int,
        horizon: int,
    ) -> bool:
        if not path or self.path_conflict(path, unit_id, horizon):
            return False
        clipped = tuple(path[: horizon + 1])
        for time, cell in enumerate(clipped):
            self.vertices[(time, cell)] = unit_id
            if time:
                self.edges[(time, clipped[time - 1], cell)] = unit_id
        temporal_destination = clipped[-1]
        for time in range(len(clipped), horizon + 1):
            self.vertices[(time, temporal_destination)] = unit_id
        return self.reserve_destination(path[-1], unit_id)

    def copy(self) -> "TurnReservationTable":
        return TurnReservationTable(
            destinations=dict(self.destinations),
            corridors=list(self.corridors),
            vertices=dict(self.vertices),
            edges=dict(self.edges),
        )


@dataclass
class PlannerMemory:
    force: int | None = None
    previous_ready: frozenset[int] = frozenset()
    reservations: TurnReservationTable = field(default_factory=TurnReservationTable)
    wait_age: dict[int, int] = field(default_factory=dict)

    def refresh(self, force: int, ready: frozenset[int]) -> None:
        force_changed = self.force != force
        new_turn = force_changed or not ready.issubset(self.previous_ready)
        if new_turn:
            self.reservations = TurnReservationTable()
        if force_changed:
            self.wait_age.clear()
        self.force = force
        self.previous_ready = ready

    def record_choice(self, ready: frozenset[int], chosen: int, limit: int) -> None:
        for unit_id in ready:
            if unit_id == chosen:
                self.wait_age[unit_id] = 0
            else:
                self.wait_age[unit_id] = min(limit, self.wait_age.get(unit_id, 0) + 1)
        for unit_id in tuple(self.wait_age):
            if unit_id not in ready and self.wait_age[unit_id] == 0:
                del self.wait_age[unit_id]


@dataclass
class PlannerMetrics:
    decisions: int = 0
    retreats: int = 0
    corridor_clears: int = 0
    ranged_attacks: int = 0
    artillery_actions: int = 0
    corridor_rejections: int = 0
    time_conflict_rejections: int = 0


@dataclass(frozen=True)
class PlannedAction:
    action_index: int
    unit_id: int
    destination: Cell
    score: float
    reason: str
    path: tuple[Cell, ...] = ()


@dataclass(frozen=True)
class TurnPlan:
    actions: tuple[PlannedAction, ...]
    assignments: Mapping[int, TacticalSlot]

    @property
    def first(self) -> PlannedAction:
        if not self.actions:
            raise ValueError("joint-turn plan is empty")
        return self.actions[0]


class TacticalField:
    def __init__(
        self,
        units: Sequence[Mapping[str, Any]],
        acting_force: int,
        width: int,
        height: int,
        terrain: Sequence[str] | None = None,
    ) -> None:
        self.units = {
            int(unit["id"]): dict(unit)
            for unit in units
            if not bool(unit.get("dead", False))
        }
        self.acting_force = int(acting_force)
        self.width = int(width)
        self.height = int(height)
        self.friendlies = [
            unit
            for unit in self.units.values()
            if _same_side(int(unit["force"]), self.acting_force)
        ]
        self.opponents = [
            unit
            for unit in self.units.values()
            if not _same_side(int(unit["force"]), self.acting_force)
        ]
        self.gates = {
            (index % self.width, index // self.width)
            for index, name in enumerate(terrain or ())
            if str(name).lower() == "gate"
        }

    def is_ranged(self, unit: Mapping[str, Any]) -> bool:
        return attack_limits(dict(unit))[0] >= 2

    @staticmethod
    def is_artillery(unit: Mapping[str, Any]) -> bool:
        return str(unit.get("class", "")).lower() == "artillery"

    def enemy_distance(self, cell: Cell) -> int:
        return min((_distance(cell, _position(unit)) for unit in self.opponents), default=0)

    def gate_distance(self, cell: Cell) -> int:
        return min((_distance(cell, gate) for gate in self.gates), default=0)

    def threat(self, cell: Cell) -> float:
        value = 0.0
        for enemy in self.opponents:
            relative = (cell[0] - int(enemy["x"]), cell[1] - int(enemy["y"]))
            if relative in attack_offsets(dict(enemy)):
                value += max(1.0, float(enemy.get("atk", 100)) / 100.0)
        return value

    def fire_value(self, unit: Mapping[str, Any], cell: Cell) -> float:
        value = 0.0
        for enemy in self.opponents:
            if in_attack_range(cell, _position(enemy), dict(unit)):
                hp = max(1.0, float(enemy.get("max_hp", enemy.get("hp", 1))))
                missing = 1.0 - float(enemy.get("hp", hp)) / hp
                value += 1.0 + missing
        return value


class TacticalSlotGenerator:
    def __init__(self, config: PlannerConfig) -> None:
        self.config = config

    def generate(
        self,
        actions: Sequence[Action],
        field: TacticalField,
    ) -> tuple[list[TacticalSlot], dict[tuple[int, Cell], float]]:
        by_id = field.units
        slots: dict[tuple[str, Cell], TacticalSlot] = {}
        utilities: dict[tuple[int, Cell], float] = {}
        for action in actions:
            unit_id = int(action["unit"])
            unit = by_id[unit_id]
            cell = _position(action)
            hp_ratio = float(unit["hp"]) / max(1.0, float(unit["max_hp"]))
            current = _position(unit)
            if hp_ratio <= self.config.retreat_hp_ratio and int(action["type"]) == 1:
                risk_gain = field.threat(current) - field.threat(cell)
                distance_gain = field.enemy_distance(cell) - field.enemy_distance(current)
                utility = (
                    self.config.risk_weight * risk_gain
                    + self.config.distance_weight * distance_gain
                )
                if utility > 0:
                    slot = TacticalSlot(
                        cell, "retreat", utility, frozenset(), owner=unit_id
                    )
                    slots[("retreat", cell)] = slot
                    utilities[(unit_id, cell)] = max(
                        utility, utilities.get((unit_id, cell), -inf)
                    )
            if field.is_ranged(unit):
                fire = field.fire_value(unit, cell)
                if fire <= 0:
                    continue
                kind = "artillery" if field.is_artillery(unit) else "ranged"
                utility = self.config.fire_slot_bonus * fire - field.threat(cell)
                role = str(unit.get("class", ""))
                slots[(kind, cell)] = TacticalSlot(
                    cell, kind, utility, frozenset({role})
                )
                utilities[(unit_id, cell)] = max(
                    utility, utilities.get((unit_id, cell), -inf)
                )
        return list(slots.values()), utilities


class UnitSlotAllocator:
    """Maximum-weight bipartite assignment using the Hungarian algorithm."""

    def assign(
        self,
        unit_ids: Sequence[int],
        slots: Sequence[TacticalSlot],
        utilities: Mapping[tuple[int, Cell], float],
        roles: Mapping[int, str] | None = None,
    ) -> dict[int, TacticalSlot]:
        units = list(dict.fromkeys(int(value) for value in unit_ids))
        if not units or not slots:
            return {}
        real_columns = len(slots)
        columns = max(len(units), real_columns)
        weights = [
            [
                float(utilities.get((unit_id, slots[column].cell), 0.0))
                if column < real_columns
                and (slots[column].owner is None or slots[column].owner == unit_id)
                and (
                    not slots[column].allowed_roles
                    or (roles or {}).get(unit_id) in slots[column].allowed_roles
                )
                else 0.0
                for column in range(columns)
            ]
            for unit_id in units
        ]
        # Hungarian minimization with cost = -utility, 1-based indexing.
        u = [0.0] * (len(units) + 1)
        v = [0.0] * (columns + 1)
        p = [0] * (columns + 1)
        way = [0] * (columns + 1)
        for row in range(1, len(units) + 1):
            p[0] = row
            minimum = [inf] * (columns + 1)
            used = [False] * (columns + 1)
            column0 = 0
            while True:
                used[column0] = True
                row0 = p[column0]
                delta = inf
                column1 = 0
                for column in range(1, columns + 1):
                    if used[column]:
                        continue
                    current = -weights[row0 - 1][column - 1] - u[row0] - v[column]
                    if current < minimum[column]:
                        minimum[column] = current
                        way[column] = column0
                    if minimum[column] < delta:
                        delta = minimum[column]
                        column1 = column
                for column in range(columns + 1):
                    if used[column]:
                        u[p[column]] += delta
                        v[column] -= delta
                    else:
                        minimum[column] -= delta
                column0 = column1
                if p[column0] == 0:
                    break
            while True:
                column1 = way[column0]
                p[column0] = p[column1]
                column0 = column1
                if column0 == 0:
                    break
        result: dict[int, TacticalSlot] = {}
        for column in range(1, columns + 1):
            row = p[column]
            if row == 0 or column > real_columns:
                continue
            utility = weights[row - 1][column - 1]
            if utility > 0:
                result[units[row - 1]] = slots[column - 1]
        return result


class JointTurnPlanner:
    """Prioritized MAPF that replans after every native sequential action."""

    def __init__(self, config: PlannerConfig | None = None) -> None:
        self.config = config or PlannerConfig()
        self.memory = PlannerMemory()
        self.metrics = PlannerMetrics()
        self.slot_generator = TacticalSlotGenerator(self.config)
        self.slot_allocator = UnitSlotAllocator()

    def reset(self) -> None:
        self.memory = PlannerMemory()

    def _reason_and_score(
        self,
        action: Action,
        unit: Mapping[str, Any],
        field: TacticalField,
        blockers: Mapping[int, set[Cell]],
        assignments: Mapping[int, TacticalSlot],
        prior: float,
        reservations: TurnReservationTable,
        wait_age: int,
    ) -> tuple[float, str]:
        unit_id = int(unit["id"])
        action_type = int(action["type"])
        current = _position(unit)
        destination = _position(action)
        ranged = field.is_ranged(unit)
        artillery = field.is_artillery(unit)
        hp_ratio = float(unit["hp"]) / max(1.0, float(unit["max_hp"]))
        current_threat = field.threat(current)
        destination_threat = field.threat(destination)
        score = (
            self.config.prior_weight * float(prior)
            + self.config.wait_age_bonus * min(wait_age, self.config.max_wait_age)
        )
        reason = "model-prior"

        if reservations.corridor_blocked(unit_id, destination, ranged):
            return -self.config.corridor_violation_penalty, "corridor-blocked"

        target = (
            field.units.get(int(action["target"]))
            if action.get("target") is not None
            else None
        )
        is_hostile_attack = (
            action_type in (2, 3)
            and target is not None
            and not _same_side(int(target["force"]), field.acting_force)
        )
        if is_hostile_attack:
            damage = float(action.get("expected_damage", action.get("damage", 0)))
            score += self.config.attack_priority + min(30.0, damage / 5.0)
            reason = "attack"
            if ranged:
                score += self.config.ranged_attack_priority
                reason = "ranged-attack"
            if artillery:
                score += self.config.artillery_attack_bonus
                reason = "artillery-attack"

        if hp_ratio <= self.config.retreat_hp_ratio and current_threat > 0:
            risk_gain = current_threat - destination_threat
            distance_gain = field.enemy_distance(destination) - field.enemy_distance(current)
            if action_type == 1 and (risk_gain > 0 or distance_gain > 0):
                score += (
                    self.config.retreat_priority
                    + self.config.risk_weight * risk_gain
                    + self.config.distance_weight * distance_gain
                )
                reason = "retreat"
            else:
                score -= self.config.retreat_priority

        blocking_path = blockers.get(unit_id)
        if blocking_path:
            if action_type == 1 and destination not in blocking_path:
                score += self.config.clear_corridor_priority
                if reason != "retreat":
                    reason = "clear-corridor"
            elif destination in blocking_path:
                score -= self.config.clear_corridor_priority

        ineffective_front = (
            bool(field.gates)
            and not ranged
            and field.gate_distance(current) <= 1
            and field.fire_value(unit, current) <= 0
        )
        if ineffective_front:
            if (
                action_type == 1
                and field.gate_distance(destination) > field.gate_distance(current)
            ):
                score += self.config.clear_corridor_priority
                if reason != "retreat":
                    reason = "clear-front"
            elif field.gate_distance(destination) <= field.gate_distance(current):
                score -= self.config.clear_corridor_priority

        assignment = assignments.get(unit_id)
        if assignment is not None:
            if destination == assignment.cell:
                score += assignment.utility
                if reason == "model-prior":
                    reason = f"{assignment.kind}-slot"
            else:
                score -= min(20.0, _distance(destination, assignment.cell) * 3.0)

        if action_type == 0:
            score -= self.config.wait_penalty
        return score, reason

    def plan(
        self,
        actions: Sequence[Action],
        units: Sequence[Mapping[str, Any]],
        width: int,
        height: int,
        *,
        terrain: Sequence[str] | None = None,
        movement_costs: Mapping[int, Sequence[int]] | None = None,
        action_priors: Mapping[int, float] | None = None,
    ) -> TurnPlan:
        if not actions:
            raise ValueError("joint-turn planner received no legal actions")
        by_id = {
            int(unit["id"]): dict(unit)
            for unit in units
            if not bool(unit.get("dead", False))
        }
        acting_force = int(by_id[int(actions[0]["unit"])]["force"])
        ready = frozenset(
            int(action["unit"])
            for action in actions
            if not bool(by_id[int(action["unit"])].get("done", False))
        )
        self.memory.refresh(acting_force, ready)
        field = TacticalField(units, acting_force, width, height, terrain)
        costs = dict(movement_costs or {})
        blockers = ranged_path_blockers(
            list(by_id.values()),
            acting_force,
            field.opponents,
            width,
            height,
            costs,
        )
        ranged_ids = [
            int(unit["id"])
            for unit in field.friendlies
            if not bool(unit.get("done", False)) and field.is_ranged(unit)
        ]
        for path in blockers.values():
            self.memory.reservations.reserve_corridor(path, ranged_ids)

        slots, utilities = self.slot_generator.generate(actions, field)
        assignments = self.slot_allocator.assign(
            ready,
            slots,
            utilities,
            {unit_id: str(by_id[unit_id].get("class", "")) for unit_id in ready},
        )
        grouped: dict[int, list[tuple[float, str, Action, tuple[Cell, ...]]]] = {}
        for action in actions:
            unit_id = int(action["unit"])
            score, reason = self._reason_and_score(
                action,
                by_id[unit_id],
                field,
                blockers,
                assignments,
                float((action_priors or {}).get(int(action["index"]), 0.0)),
                self.memory.reservations,
                self.memory.wait_age.get(unit_id, 0),
            )
            path = _weighted_path(
                _position(by_id[unit_id]),
                _position(action),
                width,
                height,
                costs.get(unit_id),
            )
            grouped.setdefault(unit_id, []).append(
                (score, reason, dict(action), path)
            )

        ranked_units = sorted(
            grouped,
            key=lambda unit_id: (
                max(value[0] for value in grouped[unit_id]),
                -unit_id,
            ),
            reverse=True,
        )
        reservations = self.memory.reservations.copy()
        planned: list[PlannedAction] = []
        for unit_id in ranked_units:
            candidates = sorted(
                grouped[unit_id],
                key=lambda value: (value[0], -int(value[2]["index"])),
                reverse=True,
            )[: self.config.max_candidates_per_unit]
            selected = None
            for score, reason, action, path in candidates:
                destination = _position(action)
                if destination in reservations.destinations:
                    continue
                if reason == "corridor-blocked":
                    self.metrics.corridor_rejections += 1
                    continue
                if reservations.path_conflict(
                    path, unit_id, self.config.time_horizon
                ):
                    self.metrics.time_conflict_rejections += 1
                    continue
                selected = (score, reason, action, path)
                break
            if selected is None:
                continue
            score, reason, action, path = selected
            destination = _position(action)
            reservations.reserve_path(
                path, unit_id, self.config.time_horizon
            )
            planned.append(
                PlannedAction(
                    int(action["index"]),
                    unit_id,
                    destination,
                    score,
                    reason,
                    path,
                )
            )
        if not planned:
            fallback = min(actions, key=lambda action: int(action["index"]))
            planned.append(
                PlannedAction(
                    int(fallback["index"]),
                    int(fallback["unit"]),
                    _position(fallback),
                    -inf,
                    "legal-fallback",
                )
            )
        planned.sort(key=lambda item: (item.score, -item.unit_id), reverse=True)
        return TurnPlan(tuple(planned), assignments)

    def choose(self, *args: Any, **kwargs: Any) -> PlannedAction:
        result = self.plan(*args, **kwargs).first
        self.memory.record_choice(
            self.memory.previous_ready,
            result.unit_id,
            self.config.max_wait_age,
        )
        self.metrics.decisions += 1
        if result.reason == "retreat":
            self.metrics.retreats += 1
        elif result.reason in ("clear-corridor", "clear-front"):
            self.metrics.corridor_clears += 1
        elif result.reason == "ranged-attack":
            self.metrics.ranged_attacks += 1
        elif result.reason == "artillery-attack":
            self.metrics.artillery_actions += 1
        return result
