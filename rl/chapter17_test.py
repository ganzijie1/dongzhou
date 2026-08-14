"""Regression checks for expanded chapter four and chapter seventeen."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 4")
        fourth = env.story_info()
        assert fourth["chapter"] == "第四回·上"
        assert len(fourth["intro"]) >= 14
        assert len(fourth["victory"]) >= 9

        env._request("LOAD_STAGE 5")
        fifth_units = [unit for unit in env.unit_info() if not unit["dead"]]
        assert all(int(unit["level"]) == 1 for unit in fifth_units)
        fifth_enemies = [unit for unit in fifth_units if int(unit["force"]) == 4]
        fifth_guards = [unit for unit in fifth_enemies if unit["name"] == "DuanGuard"]
        assert len(fifth_guards) == 8
        assert sum(int(unit["y"]) == 2 for unit in fifth_guards) == 5
        assert {(int(unit["x"]), int(unit["y"])) for unit in fifth_guards if int(unit["y"]) > 2} == {
            (9, 4), (9, 6), (9, 7)
        }
        fifth_archers = [unit for unit in fifth_enemies if unit["name"] == "DuanArcher"]
        assert {(int(unit["x"]), int(unit["y"])) for unit in fifth_archers} == {(7, 1), (11, 1), (7, 5), (11, 5)}
        assert all(unit["terrain"] in {"CityInterior", "Storehouse", "Residence", "Castle", "Gate"} for unit in fifth_enemies)
        fifth_terrain = env.map_info()["terrain"]

        assert fifth_terrain[0 * 19 + 9] == "Castle"
        assert fifth_terrain[4 * 19 + 9] == "Gate"
        assert fifth_terrain[7 * 19 + 9] == "Gate"
        gong_shu_duan = next(unit for unit in fifth_enemies if unit["name"] == "GongShuDuan")
        assert (gong_shu_duan["x"], gong_shu_duan["y"], gong_shu_duan["terrain"]) == (9, 0, "Castle")
        assert {(9, 0), (9, 4), (9, 7), (10, 0), (2, 10)} <= {
            (int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]
        }
        assert all(
            fifth_terrain[y * 19 + x] in {"CityInterior", "Storehouse", "Castle", "Wall", "Gate"}
            for y in range(0, 7) for x in range(2, 17)
        )

        env._request("LOAD_STAGE 26")
        story = env.story_info()
        assert story["chapter"] == "第十七回"
        assert story["battle_title"] == "亳城平乱"
        assert story["map_asset"] == "m026.png"
        assert len(story["intro"]) >= 16
        assert len(story["victory"]) >= 16

        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        expected = {
            "SongHuanGong17": ("Lord", 1),
            "XiaoShuDaXin17": ("Strategist", 1),
            "NanGongNiu17": ("Cavalry", 4),
            "MengHuo17": ("Infantry", 4),
            "ZiYou17": ("Lord", 4),
            "RebelArcher17": ("Archer", 4),
        }
        for name, (unit_class, force) in expected.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])
            assert units[name]["terrain"] != "Wall", name

        terrain = env.map_info()["terrain"]
        assert terrain[5 * 19 + 5] == "Gate"
        assert terrain[5 * 19 + 13] == "Gate"
        assert terrain[7 * 19 + 9] == "Gate"
        assert env.supply_info()["sites"]

    print("chapters 4 and 17 ok: expanded story, battle, roles, terrain, and supplies")


if __name__ == "__main__":
    main()
