"""Regression checks for chapter nineteen's two battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 28")
        first = env.story_info()
        assert first["chapter"] == "第十九回·上"
        assert first["battle_title"] == "栎城复郑"
        assert first["map_asset"] == "m028.png"
        assert len(first["intro"]) == 15
        assert len(first["victory"]) == 17

        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        expected_first = {
            "ZhengLiGong19": ("Lord", 1),
            "BinXuWu19": ("Cavalry", 1),
            "QiArcher19": ("Archer", 1),
            "FuXia19": ("Cavalry", 4),
            "ZhengArcher19": ("Archer", 4),
        }
        for name, (unit_class, force) in expected_first.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])
            assert units[name]["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"}

        map_info = env.map_info()
        width = int(map_info["width"])
        terrain = list(map_info["terrain"])
        assert (width, len(terrain) // width) == (19, 14)
        assert terrain[1 * width + 8] == "Castle"
        assert terrain[4 * width + 9] == "Gate"
        assert all(terrain[4 * width + x] == ("Gate" if x == 9 else "Wall") for x in range(3, 14))

        assert env.next_stage() is not None
        second = env.story_info()
        assert second["chapter"] == "第十九回·下"
        assert second["battle_title"] == "成周反正"
        assert second["map_asset"] == "m029.png"
        assert len(second["intro"]) == 15
        assert len(second["victory"]) == 15

        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        expected_second = {
            "ZhengLiGong19": ("Lord", 1),
            "XiGuoGong19": ("Lord", 1),
            "ShiShu19": ("Strategist", 1),
            "ZhouHuiWang19": ("King", 2),
            "WangZiTui19": ("Lord", 4),
            "WeiGuo19": ("Strategist", 4),
            "BianBo19": ("Cavalry", 4),
            "ZhanFu19": ("Archer", 4),
        }
        for name, (unit_class, force) in expected_second.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])
            assert units[name]["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"}

        map_info = env.map_info()
        width = int(map_info["width"])
        terrain = list(map_info["terrain"])
        assert (width, len(terrain) // width) == (19, 14)
        assert terrain[2 * width + 9] == "Castle"
        assert terrain[5 * width + 2] == "Gate"
        assert terrain[8 * width + 9] == "Gate"
        site_positions = {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]}
        assert {(9, 2), (2, 5), (9, 8), (4, 12), (14, 12)} <= site_positions

    first_map = Path("assets/lzc/map/m028.png")
    second_map = Path("assets/lzc/map/m029.png")
    assert first_map.stat().st_size > 1_000_000
    assert second_map.stat().st_size > 1_000_000
    assert hashlib.sha256(first_map.read_bytes()).digest() != hashlib.sha256(second_map.read_bytes()).digest()
    print("chapter 19 ok: two battles, full story, distinct maps, roles, walls, gates, and progression")


if __name__ == "__main__":
    main()