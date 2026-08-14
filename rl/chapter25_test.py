"""Regression checks for chapter twenty-five's two battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十五回·上", "下阳破关", "m042.png", 24, 12),
    ("第二十五回·下", "箕山袭虞", "m043.png", 12, 29),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(
        executable, scenario="dongzhou", max_episode_actions=100, interactive=True
    ) as env:
        env._request("LOAD_STAGE 42")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert story["title"] == "智荀息假途灭虢 穷百里饲牛拜相"
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count

            map_info = env.map_info()
            width, height = int(map_info["width"]), int(map_info["height"])
            assert (width, height) == (19, 14)
            terrain = list(map_info["terrain"])
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units and all(unit["terrain"] not in IMPASSABLE for unit in units)
            by_name = {}
            for unit in units:
                by_name.setdefault(unit["name"], []).append(unit)

            if offset == 0:
                assert by_name["LiKe25"][0]["class"] == "Cavalry"
                assert by_name["XunXi25"][0]["class"] == "Strategist"
                assert by_name["ZhouZhiQiao25"][0]["class"] == "Strategist"
                assert (by_name["XiayangCaptain25"][0]["x"],
                        by_name["XiayangCaptain25"][0]["y"],
                        by_name["XiayangCaptain25"][0]["terrain"]) == (9, 5, "Gate")
                assert all(
                    terrain[5 * width + x] == ("Gate" if x == 9 else "Wall")
                    for x in range(4, 15)
                )
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (9, 5), (6, 3), (9, 12)
                }
            else:
                assert by_name["LiKe25"][0]["level"] == by_name["XunXi25"][0]["level"]
                assert (by_name["YuCapitalCaptain25"][0]["x"],
                        by_name["YuCapitalCaptain25"][0]["y"],
                        by_name["YuCapitalCaptain25"][0]["terrain"]) == (9, 0, "Castle")
                assert all(
                    terrain[4 * width + x] == ("Gate" if x == 9 else "Wall")
                    for x in range(4, 15)
                )
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (9, 0), (6, 2), (9, 4), (15, 10)
                }

        env._request("LOAD_STAGE 42")
        snapshot = env.snapshot()
        for unit in snapshot["units"]:
            if unit["name"] in {"XiayangCaptain25", "ZhouZhiQiao25"}:
                unit.update({"dead": True, "hp": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 3

        env._request("LOAD_STAGE 43")
        snapshot = env.snapshot()
        captain = next(unit for unit in snapshot["units"] if unit["name"] == "YuCapitalCaptain25")
        captain.update({"dead": True, "hp": 0})
        li_ke = next(unit for unit in snapshot["units"] if unit["name"] == "LiKe25")
        li_ke.update({"x": 9, "y": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 3

        env._request("LOAD_STAGE 43")
        env.restore(env.snapshot())
        steps = 0
        while not any(unit["name"] == "YuGong25" for unit in env.unit_info()):
            wait = next(action for action in env.list_actions() if int(action["type"]) == 0)
            env.step(int(wait["index"]))
            steps += 1
            assert steps < 40
        returned = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        assert returned["YuGong25"]["terrain"] not in IMPASSABLE
        assert returned["BailiXi25"]["class"] == "Strategist"
    maps = [Path("assets/lzc/map/m042.png"), Path("assets/lzc/map/m043.png")]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 2
    print("chapter 25 ok: Xiayang and Yu battles, dense story, walls, supplies, deployment, and outcomes")


if __name__ == "__main__":
    main()
