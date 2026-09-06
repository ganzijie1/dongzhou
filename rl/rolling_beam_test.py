"""Fast unit tests for the lightweight rolling-beam battle model."""

from __future__ import annotations

from copy import deepcopy

from rl.rolling_beam import PlannerConfig, PlanningWorld, RollingBeamPlanner


def unit(
    unit_id: int, force: int, x: int, y: int, *, hp: int = 100,
    attack_max: int = 1, done: bool = False,
) -> dict:
    return {
        "id": unit_id,
        "name": f"unit-{unit_id}",
        "force": force,
        "class": "Infantry",
        "level": 1,
        "hp": hp,
        "max_hp": 100,
        "mp": 30,
        "max_mp": 30,
        "x": x,
        "y": y,
        "done": done,
        "dead": hp <= 0,
        "invulnerable": False,
        "atk": 50,
        "def": 35,
        "dex": 40,
        "int": 30,
        "mor": 35,
        "move": 4,
        "attack_min": 1,
        "attack_max": attack_max,
        "attack_offsets": [[1, 0], [-1, 0], [0, 1], [0, -1]],
        "terrain_effect": 100,
        "skills": [],
    }


def wait(index: int, actor: int, x: int, y: int) -> dict:
    return {
        "index": index, "unit": actor, "type": 0,
        "x": x, "y": y, "target": None, "skill": "",
    }


def test_lethal_attack_beats_wait() -> None:
    units = [unit(1, 4, 0, 0), unit(2, 1, 1, 0, hp=40)]
    actions = [
        wait(0, 1, 0, 0),
        {
            "index": 1, "unit": 1, "type": 2, "x": 0, "y": 0,
            "target": 2, "skill": "", "damage": 60, "accuracy": 100,
            "critical": 0, "double": 0, "counter_damage": 0,
            "counter_accuracy": 0,
        },
    ]
    planner = RollingBeamPlanner(PlannerConfig(
        horizon=1, scenario_count=5, include_opponent_response=False
    ))
    result = planner.plan(actions, units, 8, 8)
    assert result.action_index == 1
    assert result.mean > 10.0


def test_cvar_rejects_risky_exchange() -> None:
    units = [unit(1, 4, 0, 0), unit(2, 1, 1, 0, hp=100)]
    actions = [
        wait(0, 1, 0, 0),
        {
            "index": 1, "unit": 1, "type": 2, "x": 0, "y": 0,
            "target": 2, "skill": "", "damage": 100, "accuracy": 40,
            "critical": 0, "double": 0, "counter_damage": 100,
            "counter_accuracy": 100,
        },
        {
            "index": 2, "unit": 1, "type": 3, "x": 0, "y": 0,
            "target": 2, "skill": "safe", "damage": 35, "accuracy": 100,
            "heal": 0, "mp_cost": 5,
        },
    ]
    planner = RollingBeamPlanner(PlannerConfig(
        horizon=1, scenario_count=10, cvar_alpha=0.2,
        include_opponent_response=False,
    ))
    result = planner.plan(actions, units, 8, 8)
    assert result.action_index == 2
    assert result.cvar > 0.0


def test_move_toward_effective_range_beats_wait() -> None:
    units = [unit(1, 4, 0, 0), unit(2, 1, 6, 0)]
    actions = [wait(0, 1, 0, 0), {
        "index": 1, "unit": 1, "type": 1,
        "x": 4, "y": 0, "target": None, "skill": "",
    }]
    planner = RollingBeamPlanner(PlannerConfig(
        horizon=1, scenario_count=3, include_opponent_response=False
    ))
    result = planner.plan(actions, units, 8, 8)
    assert result.action_index == 1


def test_stat_magic_does_not_invent_damage() -> None:
    units = [unit(1, 4, 0, 0), unit(2, 1, 1, 0)]
    units[0]["skills"] = [{
        "id": "debuff", "mp": 4, "power": 250, "target_enemy": True,
    }]
    action = {
        "index": 0, "unit": 1, "type": 3, "x": 0, "y": 0,
        "target": 2, "skill": "debuff", "damage": 0, "heal": 0,
        "accuracy": 100, "mp_cost": 4, "stat_modifier": True,
    }
    planner = RollingBeamPlanner(PlannerConfig(include_opponent_response=False))
    values = planner._action_values(action, PlanningWorld.from_native(units))
    assert values["damage"] == 0.0


def test_multi_unit_sequence_and_determinism() -> None:
    units = [
        unit(1, 4, 0, 0), unit(3, 4, 0, 1),
        unit(5, 1, 1, 0, hp=100),
    ]
    attack_one = {
        "index": 1, "unit": 1, "type": 2, "x": 0, "y": 0,
        "target": 5, "skill": "", "damage": 30, "accuracy": 100,
        "critical": 0, "double": 0,
    }
    attack_two = {
        "index": 3, "unit": 3, "type": 2, "x": 0, "y": 1,
        "target": 5, "skill": "", "damage": 30, "accuracy": 100,
        "critical": 0, "double": 0,
    }
    actions = [
        wait(0, 1, 0, 0), attack_one,
        wait(2, 3, 0, 1), attack_two,
    ]
    planner = RollingBeamPlanner(PlannerConfig(
        horizon=2, beam_width=8, scenario_count=7,
        include_opponent_response=False,
    ))
    first = planner.plan(deepcopy(actions), deepcopy(units), 8, 8)
    second = planner.plan(deepcopy(actions), deepcopy(units), 8, 8)
    assert first.action_index == 1
    assert first.action_sequence == (1, 3)
    assert second.action_sequence == first.action_sequence
    assert first.mean == second.mean
    assert first.stats.depth_reached == 2


def main() -> None:
    test_lethal_attack_beats_wait()
    test_cvar_rejects_risky_exchange()
    test_move_toward_effective_range_beats_wait()
    test_stat_magic_does_not_invent_damage()
    test_multi_unit_sequence_and_determinism()
    print("rolling beam ok: lethality, CVaR, positioning, depth, determinism")


if __name__ == "__main__":
    main()
