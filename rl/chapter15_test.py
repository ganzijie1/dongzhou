"""Regression checks for chapter 15, chapter 16 transition, and requested saves."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.save_system import read_slot


def assert_units(env: MengdeEnv, expected: dict[str, tuple[str, int]]) -> None:
    units = {unit["name"]: unit for unit in env.unit_info()}
    for name, (unit_class, force) in expected.items():
        assert units[name]["class"] == unit_class, (name, units[name]["class"])
        assert int(units[name]["force"]) == force, (name, units[name]["force"])


def main() -> None:
    requested_save = read_slot(2)
    assert requested_save is not None
    assert requested_save["stage_table_version"] == 2
    assert 0 <= int(requested_save["battle"]["stage_index"]) < 95

    third_battle_save = read_slot(4)
    assert third_battle_save is not None
    assert third_battle_save["stage_table_version"] == 2
    assert third_battle_save["metadata"]["battle_title"] == "四国复镐"
    assert int(third_battle_save["battle"]["stage_index"]) == 3
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env.restore(requested_save["battle"])
        assert env.story_info()["battle_title"] == requested_save["metadata"]["battle_title"]

        env._request("LOAD_STAGE 24")
        story = env.story_info()
        assert story["chapter"] == "第十五回"
        assert story["battle_title"] == "乾时之战"
        assert story["map_asset"] == "m022.png"
        assert_units(env, {
            "QiHuanGong15": ("Lord", 1), "BaoShuYa15": ("Strategist", 1),
            "WangZiChengFu15": ("Cavalry", 1), "LuZhuangGong15": ("Lord", 4),
            "CaoMo15": ("Cavalry", 4), "GuanYiWu15": ("Strategist", 4),
            "QinZi15": ("Archer", 4),
        })

        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第十六回"
        assert story["battle_title"] == "长勺鼓阵"
        assert story["map_asset"] == "m025.png"
        assert_units(env, {
            "LuZhuangGong16": ("Lord", 1), "CaoGui16": ("Strategist", 1),
            "BaoShuYa16": ("Strategist", 4), "QiVanguard16": ("Cavalry", 4),
        })
    root = Path("assets/lzc/map")
    for name in ("m022.png", "m025.png"):
        image = root / name
        assert image.stat().st_size > 1_000_000
    print("chapter 15-16 ok: merged battle, requested saves, transition, roles, and maps")


if __name__ == "__main__":
    main()
