"""Regression checks for impassable terrain and restorative entrances."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES


STAGES = CURRENT_DONGZHOU_STAGES
IMPASSABLE = {"RockyMountain", "Wall", "Water", "Fence"}
# Gates are passable openings, not inherently supply terrain. A stage may opt a
# gate into gsites; only castles and deer forts must always restore by type.
RESTORATIVE = {"DeerFort", "Castle"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    checked_entrances = 0
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env.reset()
        for stage_index, stage_name in enumerate(STAGES):
            env._request(f"LOAD_STAGE {stage_index}")
            map_info = env.map_info()
            width = int(map_info["width"])
            terrain = list(map_info["terrain"])
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            for unit in units:
                for x, y in env.movement_range(int(unit["id"])):
                    name = terrain[y * width + x]
                    assert name not in IMPASSABLE, (stage_name, unit["name"], x, y, name)

            supplies = env.supply_info()
            site_positions = {
                (int(site["x"]), int(site["y"]))
                for site in supplies["sites"]
            }
            for index, name in enumerate(terrain):
                if name not in RESTORATIVE:
                    continue
                position = (index % width, index // width)
                assert position in site_positions, (stage_name, name, position, "missing supply site")
                checked_entrances += 1

            if stage_name == "07":
                assert map_info["width"] == 19 and map_info["height"] == 14
                assert env.story_info()["map_asset"] == "m027.png"

                wall_positions = (
                    {(x, 0) for x in range(4, 16)}
                    | {(4, y) for y in range(1, 4)}
                    | {(15, y) for y in range(1, 4)}
                    | {(x, 4) for x in range(4, 16) if x != 9}
                )
                assert all(
                    terrain[y * width + x] == "Wall"
                    for x, y in wall_positions
                )
                assert terrain[4 * width + 9] == "Gate"

                positions = {(int(unit["x"]), int(unit["y"])) for unit in units}
                assert positions.isdisjoint(wall_positions)
                by_name = {unit["name"]: unit for unit in units}
                assert (by_name["ZhengZhuangGong7"]["x"], by_name["ZhengZhuangGong7"]["y"]) == (9, 1)
                assert (by_name["GongSunE7"]["x"], by_name["GongSunE7"]["y"]) == (9, 3)
                gate_path = env.movement_path(int(by_name["GongSunE7"]["id"]), 9, 5)
                assert gate_path == [(9, 3), (9, 4), (9, 5)]
            if stage_name == "03":
                by_name = {}
                for unit in units:
                    by_name.setdefault(unit["name"], []).append(unit)
                king = by_name["ZhouYouWang"][0]
                guo = by_name["GuoShiFu"][0]
                zheng = by_name["ZhengHuanGong"][0]
                assert (king["x"], king["y"], king["terrain"]) == (9, 0, "Castle")
                assert (guo["x"], guo["y"], guo["terrain"]) == (10, 0, "Castle")
                assert (zheng["x"], zheng["y"], zheng["terrain"]) == (9, 7, "Camp")
                assert zheng["class"] == "Lord"
                assert len(by_name.get("QuanRongArcher", [])) >= 4
                assert len(by_name.get("QuanRongLeftWarrior", [])) == 3
                assert len(by_name.get("QuanRongRightWarrior", [])) == 3
                assert len(by_name.get("BoDing41", [])) == 1
                assert len(by_name.get("ManYeSu41", [])) == 1
                assert {(8, 0), (9, 0), (10, 0), (11, 0), (9, 7), (10, 7)} <= site_positions
                gate_positions = {
                    (x, y)
                    for y in (3, 9, 12)
                    for x in (9, 10)
                } | {(4, 6), (14, 6)}
                assert gate_positions.isdisjoint(site_positions)

                for y in (3, 9, 12):
                    assert all(
                        terrain[y * width + x] == ("Gate" if x in (9, 10) else "Wall")
                        for x in range(width)
                    )
                for y in range(4, 9):
                    assert terrain[y * width] == "Wall"
                    assert terrain[y * width + 18] == "Wall"
                    side_terrain = "Gate" if y == 6 else "Wall"
                    assert terrain[y * width + 4] == side_terrain
                    assert terrain[y * width + 14] == side_terrain
                assert not any(unit["terrain"] == "Wall" for unit in units)
                own_units = [unit for unit in units if int(unit["force"]) == 1]
                assert [(unit["name"], unit["x"], unit["y"]) for unit in own_units] == [
                    ("ZhengHuanGong", 9, 7)
                ]
                ally_guards = {
                    (unit["x"], unit["y"], unit["terrain"])
                    for unit in by_name["RoyalGuard"]
                    if int(unit["force"]) == 2
                }
                assert ally_guards == {
                    (4, 6, "Gate"), (15, 6, "Grass"),
                    (9, 12, "Gate"), (10, 12, "Gate"),
                    (10, 7, "Storehouse"),
                }

            if stage_name == "03b":
                assert len(terrain) == 19 * 14
                for x in range(4, 15):
                    assert terrain[2 * width + x] == ("Gate" if x == 9 else "Wall")
                    assert terrain[10 * width + x] == ("Gate" if x == 9 else "Wall")
                for y in range(2, 11):
                    side = "Gate" if y == 6 else "Wall"
                    assert terrain[y * width + 4] == side
                    assert terrain[y * width + 14] == side
                gate_positions = {(9, 2), (9, 10), (4, 6), (14, 6)}
                assert gate_positions.isdisjoint(site_positions)
                assert not any(unit["terrain"] == "Wall" for unit in units)
                by_name = {unit["name"]: unit for unit in units}
                assert (by_name["ZhengWuGong"]["x"], by_name["ZhengWuGong"]["y"]) == (2, 11)
                assert by_name["ZhengWuGong"]["class"] == "Lord"
                assert (by_name["GongZiCheng3"]["x"], by_name["GongZiCheng3"]["y"]) == (3, 11)
                assert "BoDing41" not in by_name
                assert "WeiWuGong" not in by_name
                assert "JinWenHou" not in by_name
                assert site_positions == {(2, 11), (12, 4)}

            if stage_name == "16":
                assert (width, len(terrain) // width) == (19, 14)
                assert site_positions == {(9, 1), (9, 12)}
                for y in range(1, 13):
                    for x in range(8, 11):
                        expected = "Camp" if x == 9 and y in {1, 12} else "Wasteland"
                        assert terrain[y * width + x] == expected, (x, y, terrain[y * width + x])
                for x, y in {(1, 4), (3, 6), (14, 7), (16, 10)}:
                    assert terrain[y * width + x] == "Mountain"
                assert not any(unit["terrain"] == "Mountain" for unit in units)
                by_name = {unit["name"]: unit for unit in units}
                assert (by_name["LuZhuangGong16"]["x"], by_name["LuZhuangGong16"]["y"]) == (9, 11)
                assert by_name["CaoGui16"]["class"] == "Strategist"
                assert by_name["BaoShuYa16"]["class"] == "Strategist"

            if stage_name == "01":
                assert terrain[3 * width + 17] == "Wasteland"
                assert (17, 3) not in site_positions
                assert terrain[2 * width + 12] != "Storehouse"
                assert terrain[0 * width + 17] == "Storehouse"
                assert all(terrain[y * width + 13] == "Fence" for y in range(3))
                assert all(terrain[3 * width + x] == "Fence" for x in (14, 15, 16, 18))
                left_guard = next(
                    unit for unit in units
                    if unit["name"] == "RoyalGuard" and unit["x"] == 12 and unit["y"] == 1
                )
                inside_guard = next(
                    unit for unit in units
                    if unit["name"] == "RoyalGuard" and unit["x"] == 17 and unit["y"] == 2
                )
                cross_fence = env.movement_path(int(left_guard["id"]), 14, 1)
                through_entrance = env.movement_path(int(inside_guard["id"]), 17, 3)
                assert len(cross_fence) > 2, cross_fence
                assert len(through_entrance) == 2 and set(through_entrance) == {(17, 2), (17, 3)}

    print(f"terrain barriers ok: {len(STAGES)} stages, {checked_entrances} restorative entrances")


if __name__ == "__main__":
    main()