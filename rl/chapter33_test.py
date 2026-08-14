"""Regression checks for chapter thirty-three's two battles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def wait_once(env: MengdeEnv) -> tuple:
    action = next(item for item in env.list_actions() if int(item["type"]) == 0)
    return env.step(int(action["index"]))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 54")
        story = env.story_info()
        assert story["chapter"] == "第三十三回·上"
        assert story["title"] == "宋公伐齐纳子昭 楚人伏兵劫盟主"
        assert story["battle_title"] == "齐郊夜战"
        assert story["map_asset"] == "m054.png"
        assert len(story["intro"]) == 19
        assert len(story["victory"]) == 22

        info = env.map_info()
        width, height = int(info["width"]), int(info["height"])
        terrain = list(info["terrain"])
        assert (width, height) == (19, 14)
        assert terrain[10] == "Gate"
        assert all(terrain[x] == "Wall" for x in range(width) if x != 10)
        assert not ({"Water", "Fence"} & set(terrain))
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == {
            (10, 0), (3, 11), (9, 11), (15, 11)
        }

        units = living(env)
        assert len(units) == 20
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)
        expected_classes = {
            "GongZiZhao32": "Lord",
            "CuiYao32": "Cavalry",
            "SongXiangGong33": "Lord",
            "GongZiDang33": "Infantry",
            "GongSunGu33": "Cavalry",
            "HuaYuShi33": "Archer",
            "GaoHu33": "Strategist",
            "GongZiYuan33": "Lord",
            "GongZiPan33": "Cavalry",
            "GongZiShangRen33": "Infantry",
        }
        assert {name: by_name[name][0]["class"] for name in expected_classes} == expected_classes

        # The north edge is sealed except for the central gate.
        zhao = by_name["GongZiZhao32"][0]
        gate_path = env.movement_path(int(zhao["id"]), 10, 0)
        assert len(gate_path) > 1 and gate_path[0] == (int(zhao["x"]), int(zhao["y"]))
        for x in (0, 9, 11, 18):
            assert env.movement_path(int(zhao["id"]), x, 0) == [(x, 0)]

        # Reaching the gate before all three rival princes withdraw does not win.
        early_gate = env.snapshot()
        next(unit for unit in early_gate["units"] if unit["name"] == "GongZiZhao32").update(
            {"x": 10, "y": 0}
        )
        env.restore(early_gate)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        next_result = env.next_stage()
        assert next_result is not None
        story = env.story_info()
        assert story["chapter"] == "第三十三回·下"
        assert story["title"] == "宋公伐齐纳子昭 楚人伏兵劫盟主"
        assert story["battle_title"] == "盂地脱险"
        assert story["map_asset"] == "m055.png"
        assert len(story["intro"]) == 19
        assert len(story["victory"]) == 7

        info = env.map_info()
        terrain = list(info["terrain"])
        assert (int(info["width"]), int(info["height"])) == (19, 14)
        assert not ({"Wall", "Fence", "Water"} & set(terrain))
        assert env.supply_info()["sites"] == []
        units = living(env)
        assert len(units) == 13
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)
        assert by_name["GongZiMuYi33"][0]["class"] == "Strategist"
        assert by_name["ChuChengWang33"][0]["class"] == "King"
        assert by_name["ChengDeChen33"][0]["class"] == "Cavalry"
        assert by_name["DouBo33"][0]["class"] == "Infantry"

        muyi = by_name["GongZiMuYi33"][0]
        assert env.movement_path(int(muyi["id"]), 9, 13)

        # An unnamed escort cannot satisfy the named escape objective.
        escort_exit = env.snapshot()
        next(unit for unit in escort_exit["units"] if unit["name"] == "SongGuard33").update(
            {"x": 9, "y": 13}
        )
        env.restore(escort_exit)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        # Gongzi Muyi himself reaching the south road wins.
        env._request("LOAD_STAGE 55")
        muyi_exit = env.snapshot()
        next(unit for unit in muyi_exit["units"] if unit["name"] == "GongZiMuYi33").update(
            {"x": 9, "y": 13}
        )
        env.restore(muyi_exit)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    maps = [Path(f"assets/lzc/map/m0{number}.png") for number in (53, 54, 55)]
    assert all(path.stat().st_size > 1_000_000 for path in maps)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 3

    for name, expected_mean in (("m054_ch33a", 0.70), ("m055_ch33b", 0.80)):
        prediction = json.loads(
            Path(f"output/terrain_model/{name}_prediction.json").read_text(encoding="utf-8")
        )
        assert prediction["grid"] == [19, 14]
        assert prediction["feature_backend"] == "dinov3-directional-v2"
        assert float(prediction["mean_confidence"]) >= expected_mean

    print("chapter 33 ok: Qi night battle, Meng ambush escape, terrain, story, and stage chain")


if __name__ == "__main__":
    main()
