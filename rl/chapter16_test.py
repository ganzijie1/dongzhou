"""Regression checks for chapter sixteen and the battle of Changshao."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def action_types(env: MengdeEnv) -> set[int]:
    return {int(action["type"]) for action in env.list_actions()}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 25")

        story = env.story_info()
        assert story["chapter"] == "第十六回"
        assert story["battle_title"] == "长勺鼓阵"
        assert story["map_asset"] == "m025.png"
        assert len(story["intro"]) >= 28
        assert len(story["victory"]) == 10
        assert "前两回合" in story["objective"]

        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        expected = {
            "LuZhuangGong16": ("Lord", 1),
            "CaoGui16": ("Strategist", 1),
            "BaoShuYa16": ("Strategist", 4),
            "QiVanguard16": ("Cavalry", 4),
            "QiArcher16": ("Archer", 4),
        }
        for name, (unit_class, force) in expected.items():
            assert units[name]["class"] == unit_class, (name, units[name]["class"])
            assert int(units[name]["force"]) == force, (name, units[name]["force"])
        assert not any(unit["terrain"] == "Mountain" for unit in units.values())

        assert action_types(env) == {0}

        turn_two = env.snapshot()
        turn_two["turn_current"] = 2
        env.restore(turn_two)
        assert action_types(env) == {0}

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        assert 1 in action_types(env)
        assert action_types(env) != {0}

        map_info = env.map_info()
        width = int(map_info["width"])
        terrain = list(map_info["terrain"])
        for y in range(1, 13):
            for x in range(8, 11):
                expected_terrain = "Camp" if x == 9 and y in {1, 12} else "Wasteland"
                assert terrain[y * width + x] == expected_terrain
        assert {(site["x"], site["y"]) for site in env.supply_info()["sites"]} == {
            (9, 1), (9, 12)
        }

    map_path = Path("assets/lzc/map/m025.png")
    assert map_path.stat().st_size > 1_000_000
    print("chapter 16 ok: full story, roles, aligned terrain, two-turn hold, and third-turn counterattack")


if __name__ == "__main__":
    main()