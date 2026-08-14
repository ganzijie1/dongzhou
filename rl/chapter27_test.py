"""Regression checks for chapter twenty-seven's escape and Caisang defense."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十七回·上", "蒲城突围", "m046.png", 18, 10),
    ("第二十七回·下", "采桑拒晋", "m047.png", 17, 18),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def action(env: MengdeEnv) -> int:
    return int(env.list_actions()[0]["index"])


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 46")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert story["title"] == "骊姬巧计杀申生 献公临终嘱荀息"
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count

            map_info = env.map_info()
            assert (int(map_info["width"]), int(map_info["height"])) == (19, 14)
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units and all(unit["terrain"] not in IMPASSABLE for unit in units)
            by_name = {}
            for unit in units:
                by_name.setdefault(unit["name"], []).append(unit)

            assert by_name["ChongEr27"][0]["class"] == "Lord"
            assert by_name["HuMao27"][0]["class"] == "Strategist"
            assert by_name["HuYan27"][0]["class"] == "Strategist"
            assert by_name["BoDi27"][0]["class"] == "Cavalry"
            if offset == 0:
                terrain = list(map_info["terrain"])
                width = 19
                assert terrain[5 * width + 16] == "Flatland"
                assert terrain[5 * width + 18] == "Grass"
                assert terrain[8 * width + 8] == "Flatland"
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (4, 11), (14, 11)
                }
            else:
                assert by_name["ZhaoShuai27"][0]["class"] == "Strategist"
                assert by_name["XuChen27"][0]["class"] == "Support"
                assert by_name["WeiChou27"][0]["class"] == "Cavalry"
                assert by_name["HuSheGu27"][0]["class"] == "Archer"
                assert by_name["DianJie27"][0]["class"] == "Infantry"
                assert by_name["JieZiTui27"][0]["class"] == "Infantry"

        # A companion at the exit must not substitute for Chong Er.
        env._request("LOAD_STAGE 46")
        companion_exit = env.snapshot()
        hu_yan = next(unit for unit in companion_exit["units"] if unit["name"] == "HuYan27")
        hu_yan.update({"x": 18, "y": 5})
        env.restore(companion_exit)
        _, _, terminated, _, _ = env.step(action(env))
        assert not terminated

        # Chong Er himself at the exit wins and carries his progression forward.
        env._request("LOAD_STAGE 46")
        chonger_exit = env.snapshot()
        chonger = next(unit for unit in chonger_exit["units"] if unit["name"] == "ChongEr27")
        chonger.update({"x": 18, "y": 5, "level": 7, "exp": 41})
        env.restore(chonger_exit)
        _, _, terminated, _, info = env.step(action(env))
        assert terminated and int(info["status"]) == 3
        env.restore(chonger_exit)
        assert env.next_stage() is not None
        inherited = next(unit for unit in env.snapshot()["units"] if unit["name"] == "ChongEr27")
        assert (int(inherited["level"]), int(inherited["exp"])) == (7, 41)

        # The Caisang defense ends at turn ten even if Bo Di is still active.
        env._request("LOAD_STAGE 47")
        turn_ten = env.snapshot()
        turn_ten["turn_current"] = 10
        env.restore(turn_ten)
        _, _, terminated, _, info = env.step(action(env))
        assert terminated and int(info["status"]) == 3

    maps = [Path("assets/lzc/map/m046.png"), Path("assets/lzc/map/m047.png")]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 2
    print("chapter 27 ok: Chong Er-only escape, Caisang defense, cast, terrain, story, and progression")


if __name__ == "__main__":
    main()
