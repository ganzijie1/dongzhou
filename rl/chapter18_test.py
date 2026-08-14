"""Regression checks for chapter eighteen and the corrected fifth battle deployment."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 5")
        fifth = [unit for unit in env.unit_info() if not unit["dead"]]
        lower_guards = {
            (int(unit["x"]), int(unit["y"]), unit["terrain"])
            for unit in fifth
            if unit["name"] == "DuanGuard" and int(unit["y"]) > 2
        }
        assert lower_guards == {
            (9, 4, "Gate"),
            (9, 6, "CityInterior"),
            (9, 7, "Gate"),
        }

        env._request("LOAD_STAGE 26")
        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第十八回"
        assert story["battle_title"] == "遂邑问罪"
        assert story["map_asset"] == "m027.png"
        assert len(story["intro"]) == 18
        assert len(story["victory"]) == 20

        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        expected = {
            "QiHuanGong18": ("Lord", 1),
            "GuanYiWu18": ("Strategist", 1),
            "BaoShuYa18": ("Strategist", 1),
            "WangZiChengFu18": ("Cavalry", 1),
            "SongHuanGong18": ("Lord", 2),
            "SuiLord18": ("Lord", 4),
            "SuiArcher18": ("Archer", 4),
        }
        for name, (unit_class, force) in expected.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])
            assert units[name]["terrain"] not in {"Wall", "RockyMountain"}, name

        map_info = env.map_info()
        width = int(map_info["width"])
        terrain = list(map_info["terrain"])
        assert (width, len(terrain) // width) == (19, 14)
        assert all(terrain[x] == "Wall" for x in range(4, 16))
        assert all(
            terrain[4 * width + x] == ("Gate" if x == 9 else "Wall")
            for x in range(4, 16)
        )
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
            (9, 1), (13, 2), (9, 4), (4, 12), (14, 12)
        }

    assert Path("assets/lzc/map/m027.png").stat().st_size > 1_000_000
    print("chapter 18 ok: fifth-battle guards, transition, full story, roles, walls, and generated map")


if __name__ == "__main__":
    main()