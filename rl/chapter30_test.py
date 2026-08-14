"""Regression checks for chapter thirty's Yuanling and Hanyuan battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def by_name(env: MengdeEnv) -> dict[str, dict]:
    return {unit["name"]: unit for unit in living(env)}


def wait_once(env: MengdeEnv) -> tuple:
    action = next(item for item in env.list_actions() if int(item["type"]) == 0)
    return env.step(int(action["index"]))


def assert_spawns_passable(env: MengdeEnv) -> None:
    assert all(unit["terrain"] not in IMPASSABLE for unit in living(env))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 50")
        story = env.story_info()
        assert story["chapter"] == "第三十回·上"
        assert story["battle_title"] == "缘陵救杞"
        assert story["map_asset"] == "m050.png"
        assert len(story["intro"]) == 16 and len(story["victory"]) == 16
        assert_spawns_passable(env)
        units = by_name(env)
        assert units["QiHuanGong30"]["class"] == "Lord"
        assert units["BaoShuYa30"]["class"] == "Strategist"
        assert units["QiHou30"]["class"] == "Lord"

        info = env.map_info()
        width = int(info["width"])
        terrain = list(info["terrain"])
        assert (width, int(info["height"])) == (19, 14)
        assert all(terrain[10 * width + x] == ("Gate" if x == 9 else "Fence") for x in range(5, 14))
        assert all(terrain[13 * width + x] == "Fence" for x in range(5, 14))
        assert {(int(s["x"]), int(s["y"])) for s in env.supply_info()["sites"]} == {
            (3, 2), (9, 10), (9, 12)
        }

        win = env.snapshot()
        next(unit for unit in win["units"] if unit["name"] == "HuaiYiLord30")["hp"] = 0
        next(unit for unit in win["units"] if unit["name"] == "QiHou30").update({"x": 3, "y": 2})
        env.restore(win)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

        env._request("LOAD_STAGE 51")
        story = env.story_info()
        assert story["chapter"] == "第三十回·下"
        assert story["battle_title"] == "韩原大战"
        assert story["map_asset"] == "m051.png"
        assert len(story["intro"]) == 17 and len(story["victory"]) == 19
        assert [(d["attacker"], d["defender"], d["outcome"]) for d in story["duels"]] == [
            ("BaiYiBing30", "TuAnYi30", "capture"),
            ("GongSunZhi30", "JinHuiGong30", "capture"),
        ]
        assert_spawns_passable(env)
        info = env.map_info()
        width = int(info["width"])
        terrain = list(info["terrain"])
        assert all(terrain[y * width + x] == "Wasteland" for y in range(6, 10) for x in range(9, 13))

        turn_five = env.snapshot()
        turn_five["turn_current"] = 5
        env.restore(turn_five)
        wait_once(env)
        wild = [unit for unit in living(env) if unit["name"] in {"WildWarrior30", "WildArcher30"}]
        assert len(wild) == 3 and all(unit["terrain"] not in IMPASSABLE for unit in wild)

        env._request("LOAD_STAGE 51")
        duel = env.snapshot()
        next(unit for unit in duel["units"] if unit["name"] == "BaiYiBing30").update({"x": 9, "y": 5})
        env.restore(duel)
        units = by_name(env)
        _, reward, terminated, truncated, _ = env.resolve_duel(
            int(units["BaiYiBing30"]["id"]), int(units["TuAnYi30"]["id"])
        )
        assert reward >= 2.0 and not terminated and not truncated and "TuAnYi30" not in by_name(env)

        capture = env.snapshot()
        next(unit for unit in capture["units"] if unit["name"] == "GongSunZhi30").update({"x": 12, "y": 4})
        env.restore(capture)
        units = by_name(env)
        _, reward, terminated, truncated, result = env.resolve_duel(
            int(units["GongSunZhi30"]["id"]), int(units["JinHuiGong30"]["id"])
        )
        assert reward >= 2.0 and terminated and not truncated and int(result["status"]) == 3

    maps = [Path("assets/lzc/map/m049.png"), Path("assets/lzc/map/m050.png"), Path("assets/lzc/map/m051.png")]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 3
    print("chapter 30 ok: two battles, escort terrain, mud trap, reinforcements, and capture duels")


if __name__ == "__main__":
    main()
