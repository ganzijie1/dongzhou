"""Regression checks for chapter twenty-eight's Jiang capital coup."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv


IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}
EXPECTED_DUELS = (
    ("TuAnYi28", "DongGuanWu28", "kill", 65),
    ("LiKe28", "LiangWu28", "kill", 70),
    ("TuAnYi28", "XunXi28", "kill", 75),
)


def units_by_name(env: MengdeEnv) -> dict[str, dict]:
    return {unit["name"]: unit for unit in env.unit_info()}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 48")
        story = env.story_info()
        assert story["chapter"] == "第二十八回"
        assert story["title"] == "里克两弑孤主 穆公一平晋乱"
        assert story["battle_title"] == "绛都宫变"
        assert story["map_asset"] == "m048.png"
        assert len(story["intro"]) == 20
        assert len(story["victory"]) == 25
        assert tuple(
            (duel["attacker"], duel["defender"], duel["outcome"], int(duel["exp"]))
            for duel in story["duels"]
        ) == EXPECTED_DUELS

        map_info = env.map_info()
        width = int(map_info["width"])
        terrain = list(map_info["terrain"])
        assert (width, int(map_info["height"])) == (19, 14)
        assert all(
            terrain[6 * width + x] == ("Flatland" if x in {8, 9} else "Wall")
            for x in range(width)
        )
        assert env.supply_info()["sites"] == []

        units = units_by_name(env)
        assert all(not unit["dead"] and unit["terrain"] not in IMPASSABLE for unit in units.values())
        assert units["LiKe28"]["class"] == "Cavalry"
        assert units["PiZhengFu28"]["class"] == "Strategist"
        assert units["TuAnYi28"]["class"] == "Infantry"
        assert units["ZhuiTuan28"]["class"] == "Cavalry"
        assert units["GongHua28"]["class"] == "Infantry"
        assert units["XunXi28"]["class"] == "Strategist"
        assert (units["TuAnYi28"]["x"], units["TuAnYi28"]["y"]) == (12, 9)
        assert (units["DongGuanWu28"]["x"], units["DongGuanWu28"]["y"]) == (13, 9)

        # Original-text kill sequence: Tu An-yi, Li Ke, then Tu An-yi again.
        _, reward, terminated, truncated, _ = env.resolve_duel(
            int(units["TuAnYi28"]["id"]), int(units["DongGuanWu28"]["id"])
        )
        assert reward >= 2.0 and not terminated and not truncated
        assert units_by_name(env)["DongGuanWu28"]["dead"]

        snapshot = env.snapshot()
        next(unit for unit in snapshot["units"] if unit["name"] == "LiKe28").update({"x": 9, "y": 4})
        env.restore(snapshot)
        units = units_by_name(env)
        _, reward, terminated, truncated, _ = env.resolve_duel(
            int(units["LiKe28"]["id"]), int(units["LiangWu28"]["id"])
        )
        assert reward >= 2.0 and not terminated and not truncated
        assert units_by_name(env)["LiangWu28"]["dead"]

        snapshot = env.snapshot()
        next(unit for unit in snapshot["units"] if unit["name"] == "TuAnYi28").update({"x": 8, "y": 1})
        env.restore(snapshot)
        units = units_by_name(env)
        _, reward, terminated, truncated, info = env.resolve_duel(
            int(units["TuAnYi28"]["id"]), int(units["XunXi28"]["id"])
        )
        assert reward >= 2.0 and terminated and not truncated and int(info["status"]) == 3
        assert units_by_name(env)["XunXi28"]["dead"]

    map_path = Path("assets/lzc/map/m048.png")
    previous = [Path("assets/lzc/map/m046.png"), Path("assets/lzc/map/m047.png")]
    assert map_path.stat().st_size > 1_000_000
    digests = {hashlib.sha256(path.read_bytes()).digest() for path in [*previous, map_path]}
    assert len(digests) == 3
    print("chapter 28 ok: dense story, palace wall, roles, and three historical kill duels")


if __name__ == "__main__":
    main()
