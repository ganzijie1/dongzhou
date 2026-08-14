"""Regression checks for chapter twenty-nine's royal-city relief battle."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def units_by_name(env: MengdeEnv) -> dict[str, dict]:
    return {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}


def wait_once(env: MengdeEnv) -> tuple:
    wait = next(action for action in env.list_actions() if int(action["type"]) == 0)
    return env.step(int(wait["index"]))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 49")
        story = env.story_info()
        assert story["chapter"] == "第二十九回"
        assert story["title"] == "晋惠公大诛群臣 管夷吾病榻论相"
        assert story["battle_title"] == "王城勤王"
        assert story["map_asset"] == "m049.png"
        assert len(story["intro"]) == 25
        assert len(story["victory"]) == 24
        assert story["duels"] == []

        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        terrain = list(map_info["terrain"])
        assert (width, height) == (19, 14)
        assert all(terrain[1 * width + x] == "Wall" for x in range(2, 17))
        for y in range(2, 8):
            assert terrain[y * width + 16] == "Wall"
            assert terrain[y * width + 2] == ("Gate" if y == 5 else "Wall")
        for x in range(2, 17):
            expected = "Gate" if x in {9, 10} else "Wall"
            assert terrain[8 * width + x] == expected

        expected_sites = {(9, 2), (2, 5), (9, 8), (10, 8), (4, 11), (14, 11)}
        actual_sites = {
            (int(site["x"]), int(site["y"]))
            for site in env.supply_info()["sites"]
        }
        assert actual_sites == expected_sites

        assert all(
            unit["dead"] or unit["terrain"] not in IMPASSABLE
            for unit in env.unit_info()
        )
        units = units_by_name(env)
        assert units["QinMuGong29"]["class"] == "Lord"
        assert units["BailiXi29"]["class"] == "Strategist"
        assert units["JinHuiGong29"]["class"] == "Lord"
        assert units["XiRui29"]["class"] == "Strategist"
        assert units["ZhouXiangWang29"]["class"] == "King"
        assert units["YiLuoRongArcher29"]["class"] == "Archer"
        assert "GuanYiWu29" not in units

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        wait_once(env)
        units = units_by_name(env)
        assert units["GuanYiWu29"]["class"] == "Strategist"
        assert (int(units["GuanYiWu29"]["x"]), int(units["GuanYiWu29"]["y"])) == (18, 11)
        assert units["GuanYiWu29"]["terrain"] not in IMPASSABLE

        env._request("LOAD_STAGE 49")
        victory = env.snapshot()
        next(unit for unit in victory["units"] if unit["name"] == "YiLuoRongLord29")["hp"] = 0
        env.restore(victory)
        _, _, terminated, truncated, info = wait_once(env)
        assert terminated and not truncated and int(info["status"]) == 3

        env._request("LOAD_STAGE 49")
        defeat = env.snapshot()
        next(unit for unit in defeat["units"] if unit["name"] == "ZhouXiangWang29")["hp"] = 0
        env.restore(defeat)
        _, _, terminated, truncated, info = wait_once(env)
        assert terminated and not truncated and int(info["status"]) == 4

    map_path = Path("assets/lzc/map/m049.png")
    previous = [Path("assets/lzc/map/m047.png"), Path("assets/lzc/map/m048.png")]
    assert map_path.stat().st_size > 1_000_000
    digests = {hashlib.sha256(path.read_bytes()).digest() for path in [*previous, map_path]}
    assert len(digests) == 3
    print("chapter 29 ok: dense story, continuous royal walls, turn-three Qi relief, and outcomes")


if __name__ == "__main__":
    main()
