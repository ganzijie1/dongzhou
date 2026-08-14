"""Regression checks for chapter twenty-three's two battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXPECTED = (
    ("第二十三回·上", "荥泽死守", "m038.png", 18, 17),
    ("第二十三回·下", "纯门反袭", "m039.png", 14, 21),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 38")
        for offset, (chapter, battle, asset, intro_count, victory_count) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert len(story["intro"]) == intro_count
            assert len(story["victory"]) == victory_count

            map_info = env.map_info()
            width = int(map_info["width"])
            terrain = list(map_info["terrain"])
            assert (width, len(terrain) // width) == (19, 14)
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units
            assert all(unit["terrain"] not in IMPASSABLE for unit in units)

            by_name = {unit["name"]: unit for unit in units}
            if offset == 0:
                assert (by_name["WeiYiGong23"]["x"], by_name["WeiYiGong23"]["y"],
                        by_name["WeiYiGong23"]["terrain"]) == (9, 12, "Camp")
                assert {"QuKong23", "YuBo23", "HuangYi23", "KongYingQi23", "SouMan23"} <= set(by_name)
                assert "DiAmbusher23" not in by_name
                assert [skill["id"] for skill in by_name["QuKong23"]["skills"]] == ["fire_0"]
                assert "inspire_0" in {skill["id"] for skill in by_name["WeiYiGong23"]["skills"]}
                assert by_name["WeiGuard23"]["skills"] == []
                assert all(terrain[y * width + x] == "Water" for x, y in ((5, 2), (13, 2), (4, 4), (14, 4)))
            else:
                assert (by_name["DouZhang23"]["x"], by_name["DouZhang23"]["y"],
                        by_name["DouZhang23"]["terrain"]) == (4, 12, "Camp")
                assert (by_name["DanBo23"]["x"], by_name["DanBo23"]["y"],
                        by_name["DanBo23"]["terrain"]) == (7, 2, "Camp")
                assert by_name["DouZhang23"]["class"] == "Cavalry"
                assert by_name["DanBo23"]["class"] == "Strategist"
                assert "DouLian23" not in by_name
                assert by_name["DouZhang23"]["skills"] == []
                assert [skill["id"] for skill in by_name["DanBo23"]["skills"]] == ["fire_0"]
                duel = story["duels"][0]
                assert (duel["attacker"], duel["defender"], duel["outcome"], duel["exp"]) == (
                    "DouZhang23", "DanBo23", "retreat", 65
                )

    maps = [Path("assets/lzc/map/m038.png"), Path("assets/lzc/map/m039.png")]
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 2
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    print("chapter 23 ok: two battles, dense original-story adaptation, distinct maps, terrain, roles, and transitions")


if __name__ == "__main__":
    main()