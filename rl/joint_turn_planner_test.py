"""Regression tests for retreat, fire-lane reservations, and action ordering."""

from __future__ import annotations

import numpy as np

from rl.happo import HAPPO, HAPPO_ACTION_FEATURES
from rl.joint_turn_planner import (
    JointTurnPlanner,
    TacticalSlot,
    TurnReservationTable,
    UnitSlotAllocator,
)
from rl.mappo import ACTION_FEATURES, LOCAL_FEATURES, Decision
from rl.offline_rl import CQL
from rl.runtime_policy import RuntimeBattlePolicy


MELEE = ((0, -1), (0, 1), (-1, 0), (1, 0))
RANGE_TWO = (
    (0, -2), (1, -1), (2, 0), (1, 1),
    (0, 2), (-1, 1), (-2, 0), (-1, -1),
)


def unit(
    unit_id: int,
    force: int,
    unit_class: str,
    x: int,
    y: int,
    offsets=MELEE,
    *,
    hp: int = 100,
    done: bool = False,
) -> dict:
    distances = [abs(dx) + abs(dy) for dx, dy in offsets]
    return {
        "id": unit_id,
        "force": force,
        "class": unit_class,
        "x": x,
        "y": y,
        "attack_offsets": offsets,
        "attack_min": min(distances),
        "attack_max": max(distances),
        "move": 5,
        "hp": hp,
        "max_hp": 100,
        "atk": 100,
        "done": done,
        "dead": False,
    }


def action(index: int, actor: int, kind: int, x: int, y: int, target=None, damage=0):
    return {
        "index": index,
        "unit": actor,
        "type": kind,
        "x": x,
        "y": y,
        "target": target,
        "damage": damage,
    }


def corridor_costs(width: int, height: int) -> list[int]:
    costs = [255] * (width * height)
    for y in range(1, 8):
        costs[y * width + 5] = 1
    return costs


def test_optimal_slot_assignment() -> None:
    slots = [
        TacticalSlot((1, 1), "ranged", 0.0, frozenset()),
        TacticalSlot((2, 2), "ranged", 0.0, frozenset()),
    ]
    assignment = UnitSlotAllocator().assign(
        [1, 2],
        slots,
        {
            (1, (1, 1)): 9.0,
            (1, (2, 2)): 8.0,
            (2, (1, 1)): 7.0,
        },
    )
    assert assignment[1].cell == (2, 2)
    assert assignment[2].cell == (1, 1)

    artillery_slot = TacticalSlot(
        (3, 3), "artillery", 20.0, frozenset({"Artillery"})
    )
    assert not UnitSlotAllocator().assign(
        [1], [artillery_slot], {(1, (3, 3)): 20.0}, {1: "Archer"}
    )
    assert UnitSlotAllocator().assign(
        [1], [artillery_slot], {(1, (3, 3)): 20.0}, {1: "Artillery"}
    )[1].cell == (3, 3)


def test_retreat_then_preserve_ranged_corridor() -> None:
    width, height = 10, 9
    planner = JointTurnPlanner()
    units = [
        unit(0, 1, "Archer", 5, 1, ((0, 3),)),
        unit(1, 4, "Infantry", 5, 4, hp=25),
        unit(2, 4, "Archer", 5, 6, RANGE_TWO),
        unit(3, 4, "Infantry", 4, 4),
    ]
    first_actions = [
        action(0, 1, 0, 5, 4),
        action(1, 1, 2, 5, 4, target=0, damage=25),
        action(2, 1, 1, 4, 5),
        action(3, 2, 0, 5, 6),
        action(4, 3, 0, 4, 4),
        action(5, 3, 1, 4, 5),
    ]
    first = planner.choose(
        first_actions,
        units,
        width,
        height,
        movement_costs={2: corridor_costs(width, height)},
    )
    assert first.action_index == 2, first
    assert first.reason == "retreat", first

    units[1].update(x=4, y=5, done=True)
    second_actions = [
        action(0, 2, 0, 5, 6),
        action(1, 2, 1, 5, 3),
        action(2, 3, 0, 4, 4),
        action(3, 3, 1, 5, 4),
        action(4, 3, 1, 3, 4),
    ]
    second = planner.choose(
        second_actions,
        units,
        width,
        height,
        movement_costs={2: corridor_costs(width, height)},
    )
    assert second.unit_id == 2, second
    assert second.destination == (5, 3), second
    assert second.reason == "ranged-slot", second


def test_ineffective_gate_front_moves_back() -> None:
    width, height = 8, 7
    terrain = ["Plain"] * (width * height)
    terrain[2 * width + 4] = "Gate"
    units = [
        unit(0, 1, "Infantry", 4, 0),
        unit(1, 4, "Infantry", 4, 3),
        unit(2, 4, "Archer", 4, 5, RANGE_TWO),
    ]
    actions = [
        action(0, 1, 0, 4, 3),
        action(1, 1, 1, 3, 4),
        action(2, 2, 0, 4, 5),
    ]
    chosen = JointTurnPlanner().choose(
        actions, units, width, height, terrain=terrain
    )
    assert chosen.action_index == 1
    assert chosen.reason == "clear-front"


def test_artillery_fires_before_unproductive_melee() -> None:
    units = [
        unit(0, 1, "Infantry", 3, 1),
        unit(1, 4, "Infantry", 2, 4),
        unit(2, 4, "Artillery", 3, 5, RANGE_TWO),
    ]
    actions = [
        action(0, 1, 0, 2, 4),
        action(1, 1, 1, 2, 3),
        action(2, 2, 2, 3, 3, target=0, damage=40),
    ]
    chosen = JointTurnPlanner().choose(actions, units, 8, 8)
    assert chosen.action_index == 2
    assert chosen.reason == "artillery-attack"


def test_reservations_reject_duplicate_destinations() -> None:
    table = TurnReservationTable()
    assert table.reserve_destination((2, 2), 1)
    assert not table.reserve_destination((2, 2), 2)
    table.reserve_corridor([(3, 3), (3, 4)], [7])
    assert table.corridor_blocked(2, (3, 3), False)
    assert not table.corridor_blocked(7, (3, 3), True)


def test_time_expanded_reservations_reject_vertex_and_edge_conflicts() -> None:
    table = TurnReservationTable()
    assert table.reserve_path([(0, 0), (1, 0), (2, 0)], 1, 4)
    assert table.path_conflict([(0, 1), (1, 0), (1, 1)], 2, 4)

    swap = TurnReservationTable()
    assert swap.reserve_path([(0, 0), (1, 0)], 1, 2)
    assert swap.path_conflict([(1, 0), (0, 0)], 2, 2)
    assert not swap.reserve_path([(1, 0), (0, 0)], 2, 2)


def test_wait_age_rotates_equal_priority_units() -> None:
    units = [
        unit(1, 4, "Infantry", 1, 1),
        unit(2, 4, "Infantry", 3, 1),
    ]
    actions = [
        action(0, 1, 0, 1, 1),
        action(1, 2, 0, 3, 1),
    ]
    planner = JointTurnPlanner()
    assert planner.choose(actions, units, 6, 4).unit_id == 1
    assert planner.choose(actions, units, 6, 4).unit_id == 2


def test_conflicting_unit_uses_local_alternative() -> None:
    units = [
        unit(1, 4, "Infantry", 0, 0),
        unit(2, 4, "Infantry", 2, 0),
    ]
    actions = [
        action(0, 1, 1, 2, 0),
        action(1, 2, 1, 0, 0),
        action(2, 2, 1, 2, 1),
    ]
    costs = {1: [1] * 15, 2: [1] * 15}
    plan = JointTurnPlanner().plan(
        actions, units, 5, 3, movement_costs=costs
    )
    by_unit = {item.unit_id: item for item in plan.actions}
    assert by_unit[1].destination == (2, 0)
    assert by_unit[2].destination == (2, 1)


class FakeEnv:
    max_units = 8

    def __init__(self, units, terrain, costs):
        self._units = units
        self._terrain = terrain
        self._costs = costs

    def unit_info(self):
        return [dict(value) for value in self._units]

    def map_info(self):
        return {"width": 10, "height": 9, "terrain": list(self._terrain)}

    def movement_costs(self, unit_id):
        return list(self._costs[unit_id])


def test_runtime_uses_rule_planner_without_models() -> None:
    units = [
        unit(0, 1, "Archer", 5, 1, ((0, 3),)),
        unit(1, 4, "Infantry", 5, 4, hp=25),
        unit(2, 4, "Archer", 5, 6, RANGE_TWO),
    ]
    actions = [
        action(0, 1, 0, 5, 4),
        action(1, 1, 1, 4, 5),
        action(2, 2, 0, 5, 6),
    ]
    env = FakeEnv(
        units,
        ["Plain"] * 90,
        {2: corridor_costs(10, 9)},
    )
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
    )
    selected = policy.choose(env, actions, np.zeros(132, dtype=np.float32), 10, 9)
    assert selected == 1
    assert policy.backend == "joint-mapf"
    assert policy.last_plan_reason == "retreat"


def test_model_priors_cover_every_candidate() -> None:
    actions = [
        action(0, 1, 0, 1, 1),
        action(1, 1, 1, 2, 1),
        action(2, 1, 2, 2, 1, target=3, damage=20),
    ]
    happo_decision = Decision(
        agent_id=1,
        actions=actions,
        local=np.zeros(LOCAL_FEATURES, dtype=np.float32),
        candidates=np.zeros((len(actions), HAPPO_ACTION_FEATURES), dtype=np.float32),
    )
    happo_scores = HAPPO(132, seed=7).score(
        happo_decision, "Infantry"
    )
    assert happo_scores.shape == (len(actions),)
    assert np.isclose(np.exp(happo_scores).sum(), 1.0)

    cql_decision = Decision(
        agent_id=1,
        actions=actions,
        local=np.zeros(LOCAL_FEATURES, dtype=np.float32),
        candidates=np.zeros((len(actions), ACTION_FEATURES), dtype=np.float32),
    )
    cql_scores = CQL(132, seed=7).score(
        np.zeros(132, dtype=np.float32), cql_decision
    )
    assert cql_scores.shape == (len(actions),)


def main() -> None:
    test_optimal_slot_assignment()
    test_retreat_then_preserve_ranged_corridor()
    test_ineffective_gate_front_moves_back()
    test_artillery_fires_before_unproductive_melee()
    test_reservations_reject_duplicate_destinations()
    test_time_expanded_reservations_reject_vertex_and_edge_conflicts()
    test_wait_age_rotates_equal_priority_units()
    test_conflicting_unit_uses_local_alternative()
    test_runtime_uses_rule_planner_without_models()
    test_model_priors_cover_every_candidate()
    print(
        "joint turn planner ok: retreat, gate clearing, ranged/artillery slots, "
        "reservations, and model-free runtime fallback"
    )


if __name__ == "__main__":
    main()
