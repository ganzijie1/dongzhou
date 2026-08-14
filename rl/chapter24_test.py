"""Regression checks for chapter twenty-four's two battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十四回·上", "新密围城", "m040.png", 24, 9),
    ("第二十四回·下", "许城解围", "m041.png", 12, 21),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 40")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count
            assert story["title"] == "盟召陵礼款楚大夫 会葵邱义戴周天子"

            map_info = env.map_info()
            width, height = int(map_info["width"]), int(map_info["height"])
            assert (width, height) == (19, 14)
            terrain = list(map_info["terrain"])
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units
            assert all(unit["terrain"] not in IMPASSABLE for unit in units)

            by_name = {}
            for unit in units:
                by_name.setdefault(unit["name"], []).append(unit)
            if offset == 0:
                assert len(story["intro"]) >= 20
                assert (by_name["QiHuanGong24"][0]["x"], by_name["QiHuanGong24"][0]["y"]) == (8, 11)
                assert by_name["GuanYiWu24"][0]["class"] == "Strategist"
                assert by_name["ShenHou24"][0]["class"] == "Support"
                assert (by_name["XinmiGateCaptain24"][0]["x"],
                        by_name["XinmiGateCaptain24"][0]["y"],
                        by_name["XinmiGateCaptain24"][0]["terrain"]) == (9, 7, "Gate")
                assert all(
                    terrain[1 * width + x] == "Wall" for x in range(5, 14)
                )
                assert terrain[5 * width + 5] == "Gate"
                assert terrain[5 * width + 13] == "Gate"
                assert terrain[7 * width + 9] == "Gate"
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (5, 5), (13, 5), (9, 7), (6, 3), (9, 12)
                }
            else:
                assert len(story["victory"]) >= 20
                assert (by_name["XuXiGong24"][0]["x"], by_name["XuXiGong24"][0]["y"],
                        by_name["XuXiGong24"][0]["terrain"]) == (9, 1, "Castle")
                assert by_name["ChuChengWang24"][0]["class"] == "King"
                assert by_name["ZiWen24"][0]["class"] == "Strategist"
                assert int(by_name["XuXiGong24"][0]["force"]) == 2
                assert terrain[4 * width + 9] == "Gate"
                assert all(
                    terrain[4 * width + x] == ("Gate" if x == 9 else "Wall")
                    for x in range(4, 16)
                )
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (9, 1), (13, 2), (9, 4), (4, 12), (14, 12)
                }

        env._request("LOAD_STAGE 40")
        snapshot = env.snapshot()
        for unit in snapshot["units"]:
            if unit["name"] in {"XinmiGateCaptain24", "ZhengGateGuard24"}:
                unit.update({"dead": True, "hp": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 3

        env._request("LOAD_STAGE 41")
        snapshot = env.snapshot()
        qi = next(unit for unit in snapshot["units"] if unit["name"] == "QiHuanGong24")
        chu = next(unit for unit in snapshot["units"] if unit["name"] == "ChuChengWang24")
        qi["x"], qi["y"] = 9, 9
        chu["x"], chu["y"], chu["hp"] = 9, 8, 1
        env.restore(snapshot)
        chu_id = next(
            unit["id"] for unit in env.unit_info()
            if unit["name"] == "ChuChengWang24"
        )
        attack = next(
            action for action in env.list_actions()
            if int(action["type"]) == 2
            and int(action.get("target", -1)) == int(chu_id)
        )
        _, _, terminated, _, info = env.step(int(attack["index"]))
        assert terminated and int(info["status"]) == 3

        env._request("LOAD_STAGE 41")
        snapshot = env.snapshot()
        xu = next(unit for unit in snapshot["units"] if unit["name"] == "XuXiGong24")
        xu.update({"dead": True, "hp": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 4
    maps = [Path("assets/lzc/map/m040.png"), Path("assets/lzc/map/m041.png")]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 2
    print("chapter 24 ok: Xinmi and Xu battles, dense story, distinct maps, valid walls, roles, supplies, and deployment")


if __name__ == "__main__":
    main()