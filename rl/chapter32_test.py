"""Regression checks for chapter thirty-two's Linzi night escape."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def wait_once(env: MengdeEnv) -> tuple:
    action = next(item for item in env.list_actions() if int(item["type"]) == 0)
    return env.step(int(action["index"]))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 53")
        story = env.story_info()
        assert story["chapter"] == "第三十二回"
        assert story["title"] == "晏蛾儿逾墙殉节 群公子大闹朝堂"
        assert story["battle_title"] == "临淄夜逃"
        assert story["map_asset"] == "m053.png"
        assert len(story["intro"]) == 21
        assert len(story["victory"]) == 26

        info = env.map_info()
        width, height = int(info["width"]), int(info["height"])
        terrain = list(info["terrain"])
        assert (width, height) == (19, 14)
        assert all(terrain[x] == "RockyMountain" for x in range(width))
        assert all(terrain[13 * width + x] == "RockyMountain" for x in range(width))
        assert all(terrain[1 * width + x] == "Wall" for x in range(1, 16))
        assert all(terrain[12 * width + x] == "Wall" for x in range(1, 16))
        for y in range(2, 12):
            assert terrain[y * width + 1] == "Wall"
            assert terrain[y * width + 15] == ("Gate" if y == 6 else "Wall")
        assert terrain[6 * width + 18] == "Flatland"
        assert terrain[2 * width + 2] == "Residence"
        assert terrain[9 * width + 5] == "Grass"
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
            (15, 6)
        }

        units = living(env)
        assert len(units) == 12
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)
        assert by_name["GongZiZhao32"][0]["class"] == "Lord"
        assert by_name["CuiYao32"][0]["class"] == "Cavalry"
        assert by_name["YiYa32"][0]["class"] == "Strategist"
        assert by_name["ShuDiao32"][0]["class"] == "Support"
        assert len(by_name["PalaceGuard32"]) == 4
        assert len(by_name["PalaceArcher32"]) == 2

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        wait_once(env)
        units = living(env)
        assert sum(unit["name"] == "PalaceGuard32" for unit in units) == 6
        assert sum(unit["name"] == "PalaceArcher32" for unit in units) == 4
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)

        # Cui Yao cannot substitute for the named heir at the exit.
        env._request("LOAD_STAGE 53")
        companion_exit = env.snapshot()
        next(unit for unit in companion_exit["units"] if unit["name"] == "CuiYao32").update(
            {"x": 18, "y": 6}
        )
        env.restore(companion_exit)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        # Gongzi Zhao himself reaching the road outside the east gate wins.
        env._request("LOAD_STAGE 53")
        heir_exit = env.snapshot()
        next(unit for unit in heir_exit["units"] if unit["name"] == "GongZiZhao32").update(
            {"x": 18, "y": 6}
        )
        env.restore(heir_exit)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    map_path = Path("assets/lzc/map/m053.png")
    assert map_path.stat().st_size > 1_000_000
    maps = [Path("assets/lzc/map/m051.png"), Path("assets/lzc/map/m052.png"), map_path]
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 3

    prediction = json.loads(
        Path("output/terrain_model/m053_ch32_prediction.json").read_text(encoding="utf-8")
    )
    assert prediction["grid"] == [19, 14]
    assert prediction["feature_backend"] == "dinov3-directional-v2"
    assert float(prediction["mean_confidence"]) > 0.8
    print("chapter 32 ok: Linzi escape, continuous walls, east gate, reinforcements, story, and UI data")


if __name__ == "__main__":
    main()
