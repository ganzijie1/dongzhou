"""Regression checks for Dongzhou chapter 13 story and battle content."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 20")
        story = env.story_info()
        assert story["chapter"] == "第十三回·上"
        assert story["story_only"] is True
        assert story["map_asset"] == "m018.png"

        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第十三回·下"
        assert story["battle_title"] == "首止诛逆"
        assert story["map_asset"] == "m019.png"

        expected = {
            "QiXiangGong13": ("Lord", 1),
            "WangZiChengFu13": ("Cavalry", 1),
            "GuanZhiFu13": ("Infantry", 1),
            "ZiWei13": ("Lord", 4),
            "GaoQuMi13": ("Cavalry", 4),
            "ZhengArcher13": ("Archer", 4),
        }
        units = {unit["name"]: unit for unit in env.unit_info()}
        for name, (unit_class, force) in expected.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])

        sites = {(site["x"], site["y"]) for site in env.supply_info()["sites"]}
        assert sites == {(3, 3), (15, 3)}

    root = Path("assets/lzc/map")
    for name in ("m018.png", "m019.png"):
        assert (root / name).stat().st_size > 1_000_000
    print("chapter 13 ok: story transition, battle roles, camps, and maps")


if __name__ == "__main__":
    main()
