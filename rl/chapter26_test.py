"""Regression checks for chapter twenty-six's two western battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十六回·上", "瓜州逐戎", "m044.png", 24, 12),
    ("第二十六回·下", "西戎归秦", "m045.png", 12, 17),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 44")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert story["title"] == "歌扊扅百里认妻 获陈宝穆公证梦"
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count

            map_info = env.map_info()
            width, height = int(map_info["width"]), int(map_info["height"])
            terrain = list(map_info["terrain"])
            assert (width, height) == (19, 14)
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units and all(unit["terrain"] not in IMPASSABLE for unit in units)
            by_name = {}
            for unit in units:
                by_name.setdefault(unit["name"], []).append(unit)

            assert by_name["MengMingShi26"][0]["class"] == "Cavalry"
            assert by_name["XiQiShu26"][0]["class"] == "Infantry"
            assert by_name["BaiYiBing26"][0]["class"] == "Archer"
            if offset == 0:
                assert (by_name["WuLi26"][0]["x"], by_name["WuLi26"][0]["y"],
                        by_name["WuLi26"][0]["terrain"]) == (9, 1, "Camp")
                assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
                    (9, 1), (9, 12)
                }
            else:
                assert by_name["YouYu26"][0]["class"] == "Strategist"
                assert by_name["ChiBan26"][0]["class"] == "Lord"
                assert (by_name["ChiBan26"][0]["x"], by_name["ChiBan26"][0]["y"],
                        by_name["ChiBan26"][0]["terrain"]) == (9, 1, "Camp")
                assert terrain.count("RockyMountain") > 20

        env._request("LOAD_STAGE 44")
        snapshot = env.snapshot()
        for unit in snapshot["units"]:
            if unit["name"] == "MengMingShi26":
                unit.update({"level": 7, "exp": 41})
            if unit["name"] == "WuLi26":
                unit.update({"dead": True, "hp": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 3

        env.restore(snapshot)
        assert env.next_stage() is not None
        inherited = next(unit for unit in env.snapshot()["units"] if unit["name"] == "MengMingShi26")
        assert (int(inherited["level"]), int(inherited["exp"])) == (7, 41)

        env._request("LOAD_STAGE 45")
        snapshot = env.snapshot()
        chiban = next(unit for unit in snapshot["units"] if unit["name"] == "ChiBan26")
        chiban.update({"dead": True, "hp": 0})
        env.restore(snapshot)
        _, _, terminated, _, info = env.step(int(env.list_actions()[0]["index"]))
        assert terminated and int(info["status"]) == 3

    maps = [Path("assets/lzc/map/m044.png"), Path("assets/lzc/map/m045.png")]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 2
    print("chapter 26 ok: two western battles, dense story, roles, terrain, supplies, progression, and outcomes")


if __name__ == "__main__":
    main()
