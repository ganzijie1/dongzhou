"""Regression checks for chapter thirty-six's two battle stages."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def grouped(env: MengdeEnv) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for unit in living(env):
        result.setdefault(unit["name"], []).append(unit)
    return result


def wait_once(env: MengdeEnv):
    action = next(item for item in env.list_actions() if int(item["type"]) == 0)
    return env.step(int(action["index"]))


def assert_map(env: MengdeEnv, rows: list[str], sites: list[list[int]]) -> None:
    info = env.map_info()
    width, height = int(info["width"]), int(info["height"])
    assert (width, height) == (21, 15)
    assert len(info["terrain"]) == width * height
    units = living(env)
    assert all(unit["terrain"] not in IMPASSABLE for unit in units)
    actual_sites = [[int(site["x"]), int(site["y"])] for site in env.supply_info()["sites"]]
    assert actual_sites == sites
    for y, row in enumerate(rows):
        assert len(row) == width
        for x, code in enumerate(row):
            if code == "W":
                assert info["terrain"][y * width + x] == "Wall"


def main() -> None:
    manifests = {
        60: json.loads(Path("assets/lzc/map_sources/m059_ch36_manifest.json").read_text(encoding="utf-8")),
        61: json.loads(Path("assets/lzc/map_sources/m060_ch36_manifest.json").read_text(encoding="utf-8")),
    }

    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 59")
        story = env.story_info()
        assert story["chapter"] == "第三十六回·上"
        assert story["battle_title"] == "令狐破城"
        assert story["map_asset"] == "m059.png"
        assert len(story["intro"]) == 18
        assert len(story["victory"]) == 14
        assert [(d["attacker"], d["defender"], d["outcome"]) for d in story["duels"]] == [
            ("PiBao36", "DengHun36", "kill")
        ]
        assert_map(env, manifests[60]["terrain_rows"], manifests[60]["supply_sites"])

        units = grouped(env)
        assert units["PiBao36"][0]["class"] == "Cavalry"
        assert units["ChongEr27"][0]["class"] == "Lord"
        assert units["GongZiZhi30"][0]["class"] == "Strategist"
        assert units["HuYan27"][0]["class"] == "Strategist"
        assert units["ZhaoShuai27"][0]["class"] == "Strategist"
        assert units["WeiChou27"][0]["class"] == "Cavalry"
        assert units["DengHun36"][0]["class"] == "Infantry"
        assert len(units["LinghuArcher36"]) == 4

        duel = env.snapshot()
        next(unit for unit in duel["units"] if unit["name"] == "PiBao36").update({"x": 9, "y": 3})
        env.restore(duel)
        units = grouped(env)
        _, reward, terminated, truncated, _ = env.resolve_duel(
            int(units["PiBao36"][0]["id"]), int(units["DengHun36"][0]["id"])
        )
        assert reward >= 2.0 and not terminated and not truncated
        assert "DengHun36" not in grouped(env)

        occupied = env.snapshot()
        next(unit for unit in occupied["units"] if unit["name"] == "ChongEr27").update({"x": 10, "y": 3})
        env.restore(occupied)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 60")
        story = env.story_info()
        assert story["chapter"] == "第三十六回·下"
        assert story["battle_title"] == "绛宫火变"
        assert story["map_asset"] == "m060.png"
        assert len(story["intro"]) == 18
        assert len(story["victory"]) == 76
        victory_text = "\n".join(entry["text"] for entry in story["victory"])
        assert "第三十七回　介子推守志焚绵上　太叔带怙宠入宫中" in victory_text
        assert "改绵山为介山" in victory_text
        assert "北邙山大集车徒" in victory_text
        assert "就留待第38回继续" in victory_text
        assert story["duels"] == []
        assert_map(env, manifests[61]["terrain_rows"], manifests[61]["supply_sites"])

        units = grouped(env)
        assert set(("HuMao27", "ZhaoShuai27", "WeiChou27", "LuanZhi36")) <= set(units)
        assert "ChongEr27" not in units
        assert units["LuanZhi36"][0]["class"] == "Strategist"
        assert units["LvSheng36"][0]["class"] == "Strategist"
        assert units["XiRui36"][0]["class"] == "Strategist"

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        wait_once(env)
        units = grouped(env)
        assert len(units["JinClanGuard36"]) == 2
        assert len(units["JinClanArcher36"]) == 2
        after_spawn = env.snapshot()
        env.restore(after_spawn)
        wait_once(env)
        units = grouped(env)
        assert len(units["JinClanGuard36"]) == 2
        assert len(units["JinClanArcher36"]) == 2

        victory = env.snapshot()
        for unit in victory["units"]:
            if unit["name"] in {"LvSheng36", "XiRui36"}:
                unit["hp"] = 0
        env.restore(victory)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    for index, name in ((60, "m059"), (61, "m060")):
        manifest = manifests[index]
        assert manifest["grid"] == [21, 15]
        assert manifest["cell_pixels"] == 64
        assert manifest["visual_grid_in_game"] is False
        stage = Path(f"game/sce/dongzhou/stage/{'36a' if index == 60 else '36b'}.lua").read_text(
            encoding="utf-8"
        )
        assert all(f'"{row}"' in stage for row in manifest["terrain_rows"])
        assert Image.open(f"assets/lzc/map/{name}.png").size == (1344, 960)

    assert Path("assets/lzc/map/m059.png").read_bytes() != Path("assets/lzc/map/m060.png").read_bytes()
    assert json.loads(Path("output/terrain_model/m059_ch36_prediction.json").read_text(encoding="utf-8"))[
        "auto_apply"
    ] is False
    assert json.loads(Path("output/terrain_model/m060_ch36_prediction.json").read_text(encoding="utf-8"))[
        "auto_apply"
    ] is False
    print("chapter 36 ok: Linghu siege, palace fire, terrain, duel, relief, story, and progression")


if __name__ == "__main__":
    main()
