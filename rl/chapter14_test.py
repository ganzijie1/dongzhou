"""Regression checks for Dongzhou chapter 14 battles and story content."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def assert_units(env: MengdeEnv, expected: dict[str, tuple[str, int]]) -> None:
    units = {unit["name"]: unit for unit in env.unit_info()}
    for name, (unit_class, force) in expected.items():
        assert units[name]["class"] == unit_class, (name, units[name]["class"])
        assert int(units[name]["force"]) == force, (name, units[name]["force"])


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 22")
        story = env.story_info()
        assert story["chapter"] == "第十四回·上"
        assert story["battle_title"] == "卫城破围"
        assert story["map_asset"] == "m020.png"
        assert_units(env, {
            "QiXiangGong14": ("Lord", 1), "WeiHuiGong14": ("Lord", 1),
            "LuZhuangGong14": ("Lord", 1), "QianMou14": ("Lord", 4),
            "NingGui14": ("Strategist", 4), "WeiArcher14": ("Archer", 4),
        })
        terrain = env.map_info()["terrain"]
        assert terrain[4 * 19 + 9] == "Gate"
        assert all(terrain[4 * 19 + x] == "Wall" for x in range(19) if x != 9)

        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第十四回·下"
        assert story["battle_title"] == "姑棼宫变"
        assert story["map_asset"] == "m021.png"
        assert_units(env, {
            "LianCheng14": ("Infantry", 1), "GuanZhiFu14": ("Infantry", 1),
            "QiXiangGong142": ("Lord", 4), "ShiZhiFenRu14": ("Cavalry", 4),
            "QiPalaceArcher14": ("Archer", 4),
        })
        terrain = env.map_info()["terrain"]
        assert terrain[6 * 19 + 9] == "Gate"
        assert all(terrain[6 * 19 + x] == "Wall" for x in range(19) if x != 9)

    root = Path("assets/lzc/map")
    for name in ("m020.png", "m021.png"):
        assert (root / name).stat().st_size > 1_000_000

    scripts = Path("game/sce/dongzhou/stage/14b.lua").read_text(encoding="utf-8")
    for defender in ("TuRenFei14", "ShiZhiFenRu14", "MengYang14", "QiXiangGong142"):
        assert f'defender = "{defender}"' in scripts
    print("chapter 14 ok: two battles, roles, walls, maps, and four historical duels")


if __name__ == "__main__":
    main()
