"""Regression checks for chapter twenty's four battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十回·一", "方伯伐卫", "m030.png", 15, 9),
    ("第二十回·二", "骊山问戎", "m031.png", 15, 15),
    ("第二十回·三", "狄霍魏之战", "m032.png", 12, 11),
    ("第二十回·四", "楚宫靖难", "m033.png", 18, 16),
)


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 30")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert story["chapter"] == chapter
            assert story["battle_title"] == battle
            assert story["map_asset"] == asset
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count

            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units
            assert all(int(unit["level"]) == 1 for unit in units)
            assert all(
                unit["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"}
                for unit in units
            )
            map_info = env.map_info()
            width = int(map_info["width"])
            terrain = list(map_info["terrain"])
            assert (width, len(terrain) // width) == (19, 14)

        by_name = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        assert by_name["DouGuWuTu20"]["class"] == "Strategist"
        assert by_name["DouBan20"]["class"] == "Cavalry"
        assert by_name["DouLian20"]["class"] == "Strategist"
        assert by_name["ZiYuan20"]["class"] == "Lord"
        assert int(by_name["ZiYuan20"]["force"]) == 4

    paths = [Path(f"assets/lzc/map/m{number:03d}.png") for number in range(30, 34)]
    hashes = {hashlib.sha256(path.read_bytes()).digest() for path in paths}
    assert len(hashes) == 4
    assert all(path.stat().st_size > 1_000_000 for path in paths)
    print("chapter 20 ok: four battles, dense story, distinct maps, roles, terrain, and transitions")


if __name__ == "__main__":
    main()