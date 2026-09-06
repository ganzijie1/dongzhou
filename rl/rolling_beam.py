"""Deterministic rolling-beam planning over Mengde's native legal actions.

The native process remains authoritative for legality and real execution.  This
module uses a small, cloneable data model to compare short action sequences
without restarting the native process for every search node.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Protocol, Sequence


WAIT = 0
MOVE = 1
BASIC_ATTACK = 2
MAGIC = 3


def _clamp_probability(value: Any, default: float = 1.0) -> float:
    try:
        return min(1.0, max(0.0, float(value) / 100.0))
    except (TypeError, ValueError):
        return default


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _coalition(force: int) -> int:
    return 4 if force == 4 else 3


def _friendly(force: int, acting_force: int) -> bool:
    return _coalition(force) == _coalition(acting_force)


def _class_advantage(attacker: str, defender: str) -> int:
    attacker_archer = attacker in {"Archer", "HorseArcher"}
    defender_archer = defender in {"Archer", "HorseArcher"}
    if (
        (attacker == "Cavalry" and defender == "Infantry")
        or (attacker == "Infantry" and defender_archer)
        or (attacker_archer and defender == "Cavalry")
    ):
        return 120
    if (
        (defender == "Cavalry" and attacker == "Infantry")
        or (defender == "Infantry" and attacker_archer)
        or (defender_archer and attacker == "Cavalry")
    ):
        return 80
    return 100


def _damage_base(attack: int, defense: int, level: int) -> int:
    # int(float) matches C++ truncation toward zero for a negative difference.
    return max(1, int((attack - defense) / 3) + level + 25)


def _accuracy(attack: int, defense: int) -> int:
    defense = max(1, defense)
    if attack >= defense // 3:
        return min(100, int((attack - defense) * 10 / defense) + 90)
    third = max(1, defense // 3)
    return max(attack - third, 0) * 30 // third + 30


def _double_or_critical(attack: int, defense: int) -> int:
    defense = max(1, defense)
    if attack >= defense * 3:
        return 100
    if attack >= defense * 2:
        return (attack - defense * 2) * 80 // defense + 20
    if attack >= defense:
        return (attack - defense) * 18 // defense + 2
    return 1


@dataclass
class PlanningUnit:
    id: int
    force: int
    class_id: str
    level: int
    hp: float
    max_hp: float
    mp: float
    max_mp: float
    x: int
    y: int
    done: bool
    dead: bool
    invulnerable: bool
    attack: int
    defense: int
    dexterity: int
    intelligence: int
    morale: int
    move: int
    attack_min: int
    attack_max: int
    attack_offsets: frozenset[tuple[int, int]]
    terrain_effect: int
    skills: tuple[dict[str, Any], ...]

    @classmethod
    def from_native(cls, value: dict[str, Any]) -> "PlanningUnit":
        offsets = frozenset(
            (int(item[0]), int(item[1]))
            for item in value.get("attack_offsets", ())
        )
        return cls(
            id=int(value["id"]),
            force=int(value["force"]),
            class_id=str(value.get("class", "")),
            level=int(value.get("level", 1)),
            hp=float(value.get("hp", 0)),
            max_hp=max(1.0, float(value.get("max_hp", 1))),
            mp=float(value.get("mp", 0)),
            max_mp=max(1.0, float(value.get("max_mp", 1))),
            x=int(value.get("x", 0)),
            y=int(value.get("y", 0)),
            done=bool(value.get("done", False)),
            dead=bool(value.get("dead", False)),
            invulnerable=bool(value.get("invulnerable", False)),
            attack=int(value.get("atk", 1)),
            defense=int(value.get("def", 1)),
            dexterity=int(value.get("dex", 1)),
            intelligence=int(value.get("int", 1)),
            morale=int(value.get("mor", 1)),
            move=int(value.get("move", 0)),
            attack_min=int(value.get("attack_min", 1)),
            attack_max=int(value.get("attack_max", 1)),
            attack_offsets=offsets,
            terrain_effect=int(value.get("terrain_effect", 100)),
            skills=tuple(dict(skill) for skill in value.get("skills", ())),
        )

    def clone(self) -> "PlanningUnit":
        return PlanningUnit(**vars(self))

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y


@dataclass
class PlanningWorld:
    units: dict[int, PlanningUnit]

    @classmethod
    def from_native(cls, units: Sequence[dict[str, Any]]) -> "PlanningWorld":
        return cls({unit.id: unit for unit in map(PlanningUnit.from_native, units)})

    def clone(self) -> "PlanningWorld":
        return PlanningWorld({unit_id: unit.clone() for unit_id, unit in self.units.items()})


@dataclass(frozen=True)
class PlannerConfig:
    horizon: int = 2
    beam_width: int = 6
    scenario_count: int = 3
    cvar_alpha: float = 0.25
    max_actions_per_actor: int = 10
    include_opponent_response: bool = True

    def __post_init__(self) -> None:
        if self.horizon <= 0:
            raise ValueError("planner horizon must be positive")
        if self.beam_width <= 0 or self.max_actions_per_actor <= 0:
            raise ValueError("beam widths must be positive")
        if self.scenario_count <= 0:
            raise ValueError("scenario_count must be positive")
        if not 0.0 < self.cvar_alpha <= 1.0:
            raise ValueError("cvar_alpha must be in (0, 1]")


@dataclass
class SearchStats:
    elapsed_ms: float = 0.0
    expanded: int = 0
    invalid_pruned: int = 0
    dominated_pruned: int = 0
    width_pruned: int = 0
    transposition_hits: int = 0
    depth_reached: int = 0


@dataclass(frozen=True)
class PlanResult:
    action_index: int
    action_sequence: tuple[int, ...]
    cvar: float
    mean: float
    stats: SearchStats


@dataclass
class _BeamNode:
    worlds: tuple[PlanningWorld, ...]
    returns: tuple[float, ...]
    actions: tuple[int, ...] = ()


class OpponentResponseModel(Protocol):
    """Estimate the next hostile turn from information visible to the planner."""

    def losses(
        self, worlds: Sequence[PlanningWorld], acting_force: int
    ) -> tuple[float, ...]: ...


class ReachableBasicAttackOpponent:
    """Conservative one-turn opponent model using movement and basic range."""

    @staticmethod
    def _can_reach(attacker: PlanningUnit, defender: PlanningUnit) -> bool:
        distance = _distance(attacker.position, defender.position)
        return distance <= attacker.move + max(1, attacker.attack_max)

    @staticmethod
    def _expected_damage(attacker: PlanningUnit, defender: PlanningUnit) -> float:
        attack = attacker.attack * attacker.terrain_effect // 100
        defense = defender.defense * defender.terrain_effect // 100
        damage = _damage_base(attack, defense, attacker.level)
        damage = damage * _class_advantage(attacker.class_id, defender.class_id) // 100
        accuracy = _accuracy(attacker.dexterity, defender.dexterity) / 100.0
        critical = _double_or_critical(attacker.morale, defender.morale) / 100.0
        double_attack = _double_or_critical(attacker.dexterity, defender.dexterity) / 100.0
        return damage * accuracy * (1.0 + 0.5 * critical) * (1.0 + 0.75 * double_attack)

    def losses(
        self, worlds: Sequence[PlanningWorld], acting_force: int
    ) -> tuple[float, ...]:
        result: list[float] = []
        for world in worlds:
            forecast = world.clone()
            loss = 0.0
            attackers = sorted(
                (
                    unit for unit in forecast.units.values()
                    if not unit.dead and not _friendly(unit.force, acting_force)
                ),
                key=lambda unit: unit.id,
            )
            for attacker in attackers:
                targets = [
                    unit for unit in forecast.units.values()
                    if not unit.dead
                    and _friendly(unit.force, acting_force)
                    and self._can_reach(attacker, unit)
                ]
                if not targets:
                    continue
                target = max(
                    targets,
                    key=lambda unit: (
                        self._expected_damage(attacker, unit),
                        -unit.hp,
                        -unit.id,
                    ),
                )
                damage = min(target.hp, self._expected_damage(attacker, target))
                target.hp -= damage
                loss += 0.5 * damage
                if target.hp <= 0.0:
                    target.dead = True
                    loss += 2.0
            result.append(loss)
        return tuple(result)


class RollingBeamPlanner:
    """Search short sequences and return one authoritative native action index."""

    def __init__(
        self,
        config: PlannerConfig | None = None,
        opponent_model: OpponentResponseModel | None = None,
    ) -> None:
        self.config = config or PlannerConfig()
        self.opponent_model = opponent_model or ReachableBasicAttackOpponent()

    @staticmethod
    def _skill(actor: PlanningUnit, skill_id: str) -> dict[str, Any] | None:
        return next(
            (skill for skill in actor.skills if str(skill.get("id", "")) == skill_id),
            None,
        )

    @staticmethod
    def _native_basic_damage(actor: PlanningUnit, target: PlanningUnit) -> int:
        attack = actor.attack * actor.terrain_effect // 100
        defense = target.defense * target.terrain_effect // 100
        damage = _damage_base(attack, defense, actor.level)
        return damage * _class_advantage(actor.class_id, target.class_id) // 100

    def _action_values(
        self, action: dict[str, Any], world: PlanningWorld
    ) -> dict[str, float]:
        actor = world.units[int(action["unit"])]
        target_value = action.get("target")
        target = world.units.get(int(target_value)) if target_value is not None else None
        action_type = int(action["type"])
        damage = float(action.get("damage", 0.0))
        heal = float(action.get("heal", 0.0))
        accuracy = _clamp_probability(action.get("accuracy", 100.0))
        critical = _clamp_probability(action.get("critical", 0.0), 0.0)
        double_attack = _clamp_probability(action.get("double", 0.0), 0.0)
        mp_cost = float(action.get("mp_cost", 0.0))
        counter_damage = float(action.get("counter_damage", 0.0))
        counter_accuracy = _clamp_probability(
            action.get("counter_accuracy", 0.0), 0.0
        )

        if target is not None and action_type == BASIC_ATTACK and "damage" not in action:
            damage = float(self._native_basic_damage(actor, target))
            accuracy = _accuracy(actor.dexterity, target.dexterity) / 100.0
            critical = _double_or_critical(actor.morale, target.morale) / 100.0
            double_attack = _double_or_critical(actor.dexterity, target.dexterity) / 100.0
        elif target is not None and action_type == MAGIC:
            skill = self._skill(actor, str(action.get("skill", "")))
            if skill is not None:
                mp_cost = float(skill.get("mp", mp_cost))
                base = _damage_base(actor.intelligence, target.intelligence, actor.level)
                power = int(skill.get("power", 100)) or 100
                amount = float(base * power // 100)
                accuracy = _accuracy(
                    actor.intelligence + actor.morale,
                    target.intelligence + target.morale,
                ) / 100.0
                if bool(skill.get("target_enemy", False)) and "damage" not in action:
                    damage = amount
                elif not bool(skill.get("target_enemy", False)) and "heal" not in action:
                    heal = amount

        return {
            "damage": damage,
            "heal": heal,
            "accuracy": accuracy,
            "critical": critical,
            "double": double_attack,
            "mp_cost": mp_cost,
            "counter_damage": counter_damage,
            "counter_accuracy": counter_accuracy,
        }

    @staticmethod
    def _quantile(scenario: int, count: int, offset: float = 0.0) -> float:
        return ((scenario + 0.5) / count + offset) % 1.0

    def _sample_attack_damage(
        self, values: dict[str, float], scenario: int
    ) -> float:
        count = self.config.scenario_count
        if self._quantile(scenario, count) >= values["accuracy"]:
            first = 0.0
        else:
            first = values["damage"]
            if self._quantile(scenario, count, 0.38196601125) < values["critical"]:
                first *= 1.5
        second = 0.0
        if self._quantile(scenario, count, 0.61803398875) < values["double"]:
            if self._quantile(scenario, count, 0.2360679775) < values["accuracy"]:
                second = values["damage"] * 0.75
                if self._quantile(scenario, count, 0.85410196625) < values["critical"]:
                    second *= 1.5
        return first + second

    @staticmethod
    def _deal_damage(unit: PlanningUnit, damage: float) -> float:
        actual = min(unit.hp, max(0.0, damage))
        if unit.invulnerable and damage >= unit.hp:
            unit.hp = unit.max_hp
            return 0.0
        unit.hp -= actual
        if unit.hp <= 0.0:
            unit.hp = 0.0
            unit.dead = True
            unit.done = True
        return actual

    @staticmethod
    def _health(world: PlanningWorld, acting_force: int) -> tuple[float, float, int, int]:
        own_hp = enemy_hp = 0.0
        own_alive = enemy_alive = 0
        for unit in world.units.values():
            if _friendly(unit.force, acting_force):
                own_hp += max(0.0, unit.hp)
                own_alive += int(not unit.dead)
            else:
                enemy_hp += max(0.0, unit.hp)
                enemy_alive += int(not unit.dead)
        return own_hp, enemy_hp, own_alive, enemy_alive

    def _apply(
        self,
        world: PlanningWorld,
        action: dict[str, Any],
        acting_force: int,
        scenario: int,
    ) -> tuple[PlanningWorld, float]:
        result = world.clone()
        before = self._health(result, acting_force)
        actor = result.units[int(action["unit"])]
        actor.x = int(action["x"])
        actor.y = int(action["y"])
        actor.done = True
        values = self._action_values(action, result)
        actor.mp = max(0.0, actor.mp - values["mp_cost"])
        target_value = action.get("target")
        target = result.units.get(int(target_value)) if target_value is not None else None

        if target is not None and not target.dead:
            if values["damage"] > 0.0:
                damage = self._sample_attack_damage(values, scenario)
                self._deal_damage(target, damage)
            if values["heal"] > 0.0 and self._quantile(
                scenario, self.config.scenario_count
            ) < values["accuracy"]:
                target.hp = min(target.max_hp, target.hp + values["heal"])
            if (
                int(action["type"]) == BASIC_ATTACK
                and not target.dead
                and values["counter_damage"] > 0.0
                and self._quantile(scenario, self.config.scenario_count, 0.5)
                < values["counter_accuracy"]
            ):
                self._deal_damage(actor, values["counter_damage"])

        after = self._health(result, acting_force)
        own_hp_loss = before[0] - after[0]
        enemy_hp_loss = before[1] - after[1]
        own_deaths = before[2] - after[2]
        enemy_deaths = before[3] - after[3]
        reward = -0.01 + 0.5 * (enemy_hp_loss - own_hp_loss)
        reward += 2.0 * enemy_deaths - 2.0 * own_deaths
        if after[3] == 0 and before[3] > 0:
            reward += 10.0
        if after[2] == 0 and before[2] > 0:
            reward -= 10.0
        return result, reward

    @staticmethod
    def _valid_action(action: dict[str, Any], worlds: Sequence[PlanningWorld]) -> bool:
        actor_id = int(action["unit"])
        target_value = action.get("target")
        destination = int(action["x"]), int(action["y"])
        for world in worlds:
            actor = world.units.get(actor_id)
            if actor is None or actor.dead or actor.done:
                return False
            occupied = {
                unit.position for unit in world.units.values()
                if not unit.dead and unit.id != actor_id
            }
            if destination in occupied:
                return False
            if target_value is not None:
                target = world.units.get(int(target_value))
                if target is None or target.dead:
                    return False
        return True

    def _pre_score(
        self, action: dict[str, Any], world: PlanningWorld, acting_force: int
    ) -> tuple[float, float, float]:
        values = self._action_values(action, world)
        net = (
            values["damage"] * values["accuracy"]
            + values["heal"] * values["accuracy"]
            - values["counter_damage"] * values["counter_accuracy"]
        )
        actor = world.units[int(action["unit"])]
        opponents = [
            unit for unit in world.units.values()
            if not unit.dead and not _friendly(unit.force, acting_force)
        ]
        old_distance = min(
            (_distance(actor.position, target.position) for target in opponents),
            default=0,
        )
        destination = int(action["x"]), int(action["y"])
        new_distance = min(
            (_distance(destination, target.position) for target in opponents),
            default=0,
        )
        desired = max(1, actor.attack_max)
        positioning = abs(old_distance - desired) - abs(new_distance - desired)
        return net, float(positioning), -values["mp_cost"]

    def _candidate_actions(
        self,
        node: _BeamNode,
        catalog: dict[int, list[dict[str, Any]]],
        acting_force: int,
        stats: SearchStats,
    ) -> list[dict[str, Any]]:
        representative = node.worlds[0]
        ready = sorted(
            unit.id for unit in representative.units.values()
            if unit.force == acting_force and not unit.dead and not unit.done
        )
        if not ready:
            return []
        candidates = catalog.get(ready[0], [])
        valid = []
        seen: set[tuple[Any, ...]] = set()
        for action in candidates:
            key = (
                int(action["type"]), int(action["x"]), int(action["y"]),
                action.get("target"), str(action.get("skill", "")),
            )
            if key in seen:
                stats.dominated_pruned += 1
                continue
            seen.add(key)
            if not self._valid_action(action, node.worlds):
                stats.invalid_pruned += 1
                continue
            valid.append(action)
        if len(valid) <= self.config.max_actions_per_actor:
            return valid

        ranked = sorted(
            valid,
            key=lambda action: self._pre_score(action, representative, acting_force),
            reverse=True,
        )
        required: list[dict[str, Any]] = []
        represented: set[tuple[int, str]] = set()
        for action in ranked:
            group = int(action["type"]), str(action.get("skill", ""))
            if group not in represented:
                represented.add(group)
                required.append(action)
        selected = required[: self.config.max_actions_per_actor]
        selected_ids = {int(action["index"]) for action in selected}
        for action in ranked:
            if len(selected) >= self.config.max_actions_per_actor:
                break
            if int(action["index"]) not in selected_ids:
                selected.append(action)
                selected_ids.add(int(action["index"]))
        stats.width_pruned += len(valid) - len(selected)
        return selected

    @staticmethod
    def _state_key(node: _BeamNode) -> tuple[Any, ...]:
        world = node.worlds[0]
        return tuple(
            (
                unit.id, unit.x, unit.y, round(unit.hp), round(unit.mp),
                unit.done, unit.dead,
            )
            for unit in sorted(world.units.values(), key=lambda item: item.id)
        )

    @staticmethod
    def _cvar(values: Sequence[float], alpha: float) -> float:
        ordered = sorted(values)
        count = max(1, int(math.ceil(len(ordered) * alpha)))
        return sum(ordered[:count]) / count

    @staticmethod
    def _position_score(
        world: PlanningWorld, initial: PlanningWorld, acting_force: int,
        width: int, height: int,
    ) -> float:
        diagonal = max(1, width + height - 2)
        opponents = [
            unit for unit in world.units.values()
            if not unit.dead and not _friendly(unit.force, acting_force)
        ]
        if not opponents:
            return 1.0
        score = 0.0
        count = 0
        for unit in world.units.values():
            if not _friendly(unit.force, acting_force) or unit.dead:
                continue
            original = initial.units[unit.id]
            old_distance = min(
                _distance(original.position, target.position) for target in opponents
            )
            new_distance = min(
                _distance(unit.position, target.position) for target in opponents
            )
            desired = max(1, unit.attack_max)
            score += abs(old_distance - desired) - abs(new_distance - desired)
            count += 1
        return score / max(1, count * diagonal)

    def _score(
        self,
        node: _BeamNode,
        initial: PlanningWorld,
        acting_force: int,
        width: int,
        height: int,
    ) -> tuple[float, float, float, float, float, float]:
        values = list(node.returns)
        if self.config.include_opponent_response:
            losses = self.opponent_model.losses(node.worlds, acting_force)
            values = [value - loss for value, loss in zip(values, losses)]
        wins = losses_count = 0
        for world in node.worlds:
            _, _, own_alive, enemy_alive = self._health(world, acting_force)
            wins += int(enemy_alive == 0 and own_alive > 0)
            losses_count += int(own_alive == 0)
        mean = sum(values) / len(values)
        cvar = self._cvar(values, self.config.cvar_alpha)
        position = sum(
            self._position_score(world, initial, acting_force, width, height)
            for world in node.worlds
        ) / len(node.worlds)
        resource = sum(
            sum(
                unit.mp / unit.max_mp for unit in world.units.values()
                if _friendly(unit.force, acting_force) and not unit.dead
            )
            for world in node.worlds
        ) / len(node.worlds)
        return (
            -losses_count / len(node.worlds),
            wins / len(node.worlds),
            cvar,
            mean,
            position,
            resource,
        )

    def plan(
        self,
        actions: Sequence[dict[str, Any]],
        units: Sequence[dict[str, Any]],
        width: int,
        height: int,
    ) -> PlanResult:
        started = time.perf_counter()
        stats = SearchStats()
        if not actions:
            raise ValueError("rolling beam received no legal actions")
        if not units:
            raise ValueError("rolling beam received no units")
        initial = PlanningWorld.from_native(units)
        first_actor = min(int(action["unit"]) for action in actions)
        if first_actor not in initial.units:
            raise ValueError(f"legal action references unknown unit {first_actor}")
        acting_force = initial.units[first_actor].force
        catalog: dict[int, list[dict[str, Any]]] = {}
        for action in actions:
            catalog.setdefault(int(action["unit"]), []).append(dict(action))

        worlds = tuple(initial.clone() for _ in range(self.config.scenario_count))
        beam = [_BeamNode(worlds, (0.0,) * self.config.scenario_count)]
        completed: list[_BeamNode] = []
        for depth in range(self.config.horizon):
            expanded: list[_BeamNode] = []
            for node in beam:
                candidates = self._candidate_actions(
                    node, catalog, acting_force, stats
                )
                if not candidates:
                    completed.append(node)
                    continue
                for action in candidates:
                    next_worlds = []
                    next_returns = []
                    for scenario, (world, value) in enumerate(
                        zip(node.worlds, node.returns)
                    ):
                        next_world, reward = self._apply(
                            world, action, acting_force, scenario
                        )
                        next_worlds.append(next_world)
                        next_returns.append(value + reward)
                    expanded.append(_BeamNode(
                        tuple(next_worlds), tuple(next_returns),
                        node.actions + (int(action["index"]),),
                    ))
                    stats.expanded += 1
            if not expanded:
                break
            best_by_state: dict[tuple[Any, ...], _BeamNode] = {}
            for node in expanded:
                key = self._state_key(node)
                incumbent = best_by_state.get(key)
                if incumbent is None or self._score(
                    node, initial, acting_force, width, height
                ) > self._score(
                    incumbent, initial, acting_force, width, height
                ):
                    if incumbent is not None:
                        stats.transposition_hits += 1
                    best_by_state[key] = node
                else:
                    stats.transposition_hits += 1
            ranked = sorted(
                best_by_state.values(),
                key=lambda node: self._score(
                    node, initial, acting_force, width, height
                ),
                reverse=True,
            )
            stats.width_pruned += max(0, len(ranked) - self.config.beam_width)
            beam = ranked[: self.config.beam_width]
            stats.depth_reached = depth + 1
        candidates = [node for node in (*completed, *beam) if node.actions]
        if not candidates:
            raise RuntimeError("rolling beam found no executable legal sequence")
        best = max(
            candidates,
            key=lambda node: self._score(
                node, initial, acting_force, width, height
            ),
        )
        score = self._score(best, initial, acting_force, width, height)
        stats.elapsed_ms = (time.perf_counter() - started) * 1000.0
        legal_indices = {int(action["index"]) for action in actions}
        if best.actions[0] not in legal_indices:
            raise RuntimeError("rolling beam selected a non-native action")
        return PlanResult(
            action_index=best.actions[0],
            action_sequence=best.actions,
            cvar=score[2],
            mean=score[3],
            stats=stats,
        )

    def choose(
        self,
        env: Any,
        actions: Sequence[dict[str, Any]],
        width: int,
        height: int,
    ) -> PlanResult:
        return self.plan(actions, env.unit_info(), width, height)
