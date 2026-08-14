"""Regression checks for chapter thirty-four's Suiyang and Hong River battles."""

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
        env._request("LOAD_STAGE 56")
        story = env.story_info()
        assert story["chapter"] == "第三十四回·上"
        assert story["title"] == "宋襄公假仁失众 齐姜氏乘醉遣夫"
        assert story["battle_title"] == "睢阳守城"
        assert story["map_asset"] == "m056.png"
        assert len(story["intro"]) == 19
        assert len(story["victory"]) == 15

        info = env.map_info()
        width, height = int(info["width"]), int(info["height"])
        terrain = list(info["terrain"])
        assert (width, height) == (19, 14)
        assert all(terrain[x] == "Wall" for x in range(3, 16))
        assert all(terrain[y * width + 3] == "Wall" for y in range(1, 8))
        assert all(terrain[y * width + 15] == "Wall" for y in range(1, 8))
        assert terrain[7 * width + 9] == "Gate"
        assert all(
            terrain[7 * width + x] == "Wall" for x in range(3, 16) if x != 9
        )
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
            (9, 1), (9, 7), (4, 11), (9, 11), (14, 11)
        }
        units = living(env)
        assert len(units) == 14
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)
        assert by_name["GongZiMuYi33"][0]["class"] == "Strategist"
        assert by_name["GongSunGu33"][0]["class"] == "Cavalry"
        assert by_name["SongPrinceChen34"][0]["class"] == "Lord"
        assert by_name["ChuChengWang33"][0]["class"] == "King"

        # The southern gate is the only route through the continuous wall.
        gongsun = by_name["GongSunGu33"][0]
        gate_path = env.movement_path(int(gongsun["id"]), 9, 8)
        assert gate_path == [(9, 6), (9, 7), (9, 8)]
        for x in (3, 8, 10, 15):
            assert env.movement_path(int(gongsun["id"]), x, 7) == [(x, 7)]

        hold = env.snapshot()
        hold["turn_current"] = 4
        env.restore(hold)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第三十四回·下"
        assert story["battle_title"] == "泓水败阵"
        assert story["map_asset"] == "m057.png"
        assert len(story["intro"]) == 19
        assert len(story["victory"]) == 17

        info = env.map_info()
        width, height = int(info["width"]), int(info["height"])
        terrain = list(info["terrain"])
        assert (width, height) == (19, 14)
        for y in (3, 4):
            assert all(
                terrain[y * width + x] == ("Flatland" if x in {8, 9, 10} else "Water")
                for x in range(width)
            )
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
            (7, 1), (9, 1), (11, 1), (9, 11)
        }
        units = living(env)
        assert len(units) == 17
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)
        assert by_name["LePuYi34"][0]["class"] == "Infantry"
        assert by_name["HuaXiuLao34"][0]["class"] == "Archer"
        assert by_name["XiangZiShou34"][0]["class"] == "Cavalry"
        assert by_name["LuChen34"][0]["class"] == "Cavalry"

        # Song Xianggong cannot win before Chu completes its formation.
        early_exit = env.snapshot()
        next(unit for unit in early_exit["units"] if unit["name"] == "SongXiangGong33").update(
            {"x": 9, "y": 13}
        )
        env.restore(early_exit)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        # An escort at the exit cannot substitute for the named ruler.
        env._request("LOAD_STAGE 57")
        escort_exit = env.snapshot()
        escort_exit["turn_current"] = 3
        next(unit for unit in escort_exit["units"] if unit["name"] == "SongGuard33").update(
            {"x": 9, "y": 13}
        )
        env.restore(escort_exit)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        env._request("LOAD_STAGE 57")
        ruler_exit = env.snapshot()
        ruler_exit["turn_current"] = 3
        next(unit for unit in ruler_exit["units"] if unit["name"] == "SongXiangGong33").update(
            {"x": 9, "y": 13}
        )
        env.restore(ruler_exit)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    maps = [Path(f"assets/lzc/map/m0{number}.png") for number in (55, 56, 57)]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 3

    for name, expected_mean in (("m056_ch34a", 0.69), ("m057_ch34b", 0.70)):
        prediction = json.loads(
            Path(f"output/terrain_model/{name}_prediction.json").read_text(encoding="utf-8")
        )
        assert prediction["grid"] == [19, 14]
        assert prediction["feature_backend"] == "dinov3-directional-v2"
        assert float(prediction["mean_confidence"]) >= expected_mean

    print("chapter 34 ok: Suiyang defense, Hong River defeat, terrain, story, and objectives")


if __name__ == "__main__":
    main()
