"""Regression checks for chapter thirty-five's Yunmeng hunt."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def by_name(env: MengdeEnv) -> dict[str, dict]:
    return {unit["name"]: unit for unit in living(env)}


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 58")
        story = env.story_info()
        assert story["chapter"] == "第三十五回"
        assert story["title"] == "晋重耳周游列国 秦怀嬴重婚公子"
        assert story["battle_title"] == "云梦围猎"
        assert story["map_asset"] == "m058.png"
        assert len(story["intro"]) == 18
        assert len(story["victory"]) == 19
        assert [(duel["attacker"], duel["defender"], duel["outcome"]) for duel in story["duels"]] == [
            ("ChongEr27", "HumanBear35", "kill"),
            ("WeiChou27", "MoBeast35", "capture"),
        ]

        assert [(event["id"], event["trigger"]) for event in story["events"]] == [
            ("bear_approach", "approach"),
            ("mo_arrives", "defeated"),
        ]
        info = env.map_info()
        width, height = int(info["width"]), int(info["height"])
        terrain = list(info["terrain"])
        assert (width, height) == (23, 16)
        water = {5: range(10, 13), 6: range(9, 14), 7: range(9, 14), 8: range(10, 13)}
        assert all(terrain[y * width + x] == "Water" for y, xs in water.items() for x in xs)
        assert not ({"Wall", "Fence"} & set(terrain))
        assert env.supply_info()["sites"] == []

        units = living(env)
        assert len(units) == 8
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        names = by_name(env)
        assert names["ChongEr27"]["class"] == "Lord"
        assert names["HuYan27"]["class"] == "Strategist"
        assert names["ZhaoShuai27"]["class"] == "Strategist"
        assert names["WeiChou27"]["class"] == "Cavalry"
        assert names["HumanBear35"]["class"] == "Infantry"
        assert "MoBeast35" not in names

        bear_duel = env.snapshot()
        next(unit for unit in bear_duel["units"] if unit["name"] == "ChongEr27").update({"x": 15, "y": 7})
        env.restore(bear_duel)
        names = by_name(env)
        _, reward, terminated, truncated, _ = env.resolve_duel(
            int(names["ChongEr27"]["id"]), int(names["HumanBear35"]["id"])
        )
        assert reward >= 2.0 and not terminated and not truncated
        assert "HumanBear35" not in by_name(env)
        action = next(item for item in env.list_actions() if int(item["type"]) == 0)
        env.step(int(action["index"]))
        assert "MoBeast35" in by_name(env)
        mo = by_name(env)["MoBeast35"]
        assert (int(mo["x"]), int(mo["y"]), mo["terrain"]) == (19, 3, "Forest")

        capture = env.snapshot()
        next(unit for unit in capture["units"] if unit["name"] == "WeiChou27").update({"x": 18, "y": 3})
        env.restore(capture)
        wait_action = next(item for item in env.list_actions() if int(item["type"]) == 0)
        env.step(int(wait_action["index"]))
        names = by_name(env)
        assert len([unit for unit in living(env) if unit["name"] == "MoBeast35"]) == 1
        _, reward, terminated, truncated, result = env.resolve_duel(
            int(names["WeiChou27"]["id"]), int(names["MoBeast35"]["id"])
        )
        assert reward >= 2.0
        assert terminated and not truncated and int(result["status"]) == 3

    manifest = json.loads(Path("assets/lzc/map_sources/m058_ch35_manifest.json").read_text(encoding="utf-8"))
    assert manifest["grid"] == [23, 16]
    assert manifest["cell_pixels"] == 48
    stage_text = Path("game/sce/dongzhou/stage/35.lua").read_text(encoding="utf-8")
    assert all(f'"{row}"' in stage_text for row in manifest["terrain_rows"])
    assert manifest["camp_cells"] == manifest["fence_cells"] == manifest["supply_sites"] == []

    assert Image.open("assets/lzc/map/m058.png").size == (23 * 48, 16 * 48)
    for portrait in ("chapter35-human-bear.png", "chapter35-mo-beast.png"):
        assert Image.open(Path("rl/assets/portraits") / portrait).size == (256, 256)
    required = {"stand_down.png", "down_0.png", "down_1.png", "attack_down_0.png", "hit_down.png", "weak_0.png"}
    for role in ("bear", "mo_beast"):
        files = {path.name for path in (Path("rl/assets/unit_anim") / role).glob("*.png")}
        assert required <= files and len(files) >= 28

    print("chapter 35 ok: dense story, scrolling Yunmeng map, staged beasts, capture duel, and custom art")


if __name__ == "__main__":
    main()