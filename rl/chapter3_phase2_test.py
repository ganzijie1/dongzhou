"""Regression checks for chapter three's retaking-Haojing battle phase."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def living_units(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def force_count(env: MengdeEnv, force: int) -> int:
    return sum(int(unit["force"]) == force for unit in living_units(env))


def wait_any(env: MengdeEnv) -> None:
    action = next(action for action in env.list_actions() if int(action["type"]) == 0)
    env.step(int(action["index"]))


def move_unit(snapshot: dict, name: str, position: tuple[int, int]) -> None:
    unit = next(unit for unit in snapshot["units"] if unit["name"] == name)
    unit["x"], unit["y"] = position


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 3")

        story = env.story_info()
        assert story["chapter"] == "第三回·下"
        assert story["battle_title"] == "四国复镐"
        assert story["map_asset"] == "m024.png"
        assert len(story["intro"]) == 9
        assert len(story["victory"]) >= 20

        initial = {unit["name"]: unit for unit in living_units(env)}
        assert initial["ZhengWuGong"]["class"] == "Lord"
        assert initial["GongZiCheng3"]["class"] == "Strategist"
        assert "BoDing41" not in initial
        assert "WeiWuGong" not in initial
        assert "QinXiangGong" not in initial
        assert "JinWenHou" not in initial

        gate_snapshot = env.snapshot()
        move_unit(gate_snapshot, "ZhengWuGong", (9, 11))
        env.restore(gate_snapshot)
        zheng = next(unit for unit in living_units(env) if unit["name"] == "ZhengWuGong")
        assert env.movement_path(int(zheng["id"]), 9, 10) == [(9, 11), (9, 10)]

        ambush_snapshot = env.snapshot()
        move_unit(ambush_snapshot, "ZhengWuGong", (8, 11))
        env.restore(ambush_snapshot)
        enemies_before = force_count(env, 4)
        wait_any(env)
        assert force_count(env, 4) - enemies_before == 4
        assert any(unit["name"] == "BoDing41" for unit in living_units(env))

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        own_before = force_count(env, 1)
        wait_any(env)
        assert force_count(env, 1) - own_before == 3
        assert any(unit["name"] == "WeiWuGong" for unit in living_units(env))

        turn_five = env.snapshot()
        turn_five["turn_current"] = 5
        env.restore(turn_five)
        own_before = force_count(env, 1)
        wait_any(env)
        assert force_count(env, 1) - own_before == 4

        final = {unit["name"]: unit for unit in living_units(env)}
        assert final["QinXiangGong"]["class"] == "Lord"
        assert final["JinWenHou"]["class"] == "Cavalry"
        for name in ("ZhengWuGong", "GongZiCheng3", "WeiWuGong", "QinXiangGong", "JinWenHou"):
            assert int(final[name]["force"]) == 1
            assert int(final[name]["level"]) == 1

        carried = env.snapshot()
        qin = next(unit for unit in carried["units"] if unit["name"] == "QinXiangGong")
        qin["level"], qin["exp"] = 3, 45
        env.restore(carried)
        assert env.next_stage() is not None
        next_story = env.story_info()
        assert next_story["chapter"] == "第四回·上"
        assert next_story["battle_title"] == "岐丰逐戎"
        next_qin = next(unit for unit in living_units(env) if unit["name"] == "QinXiangGong")
        assert (int(next_qin["level"]), int(next_qin["exp"])) == (3, 45)

    map_path = Path("assets/lzc/map/m024.png")
    assert map_path.stat().st_size > 1_000_000
    print("chapter three phase two ok: story, gates, ambush, turn-3 and turn-5 reinforcements")


if __name__ == "__main__":
    main()