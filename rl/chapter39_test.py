"""Regression checks for chapter thirty-nine's Cao funeral-cart assault."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image
from rl.mengde_env import MengdeEnv

EXE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}

def living(env):
    return [u for u in env.unit_info() if not u["dead"]]

def grouped(env):
    out = {}
    for unit in living(env):
        out.setdefault(unit["name"], []).append(unit)
    return out

def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "assets/lzc/map_sources/m063_ch39_manifest.json").read_text(encoding="utf-8")
    )
    with MengdeEnv(EXE, scenario="dongzhou", interactive=True, max_episode_actions=100) as env:
        env._request("LOAD_STAGE 63")
        story = env.story_info()
        assert story["chapter"] == "第三十九回"
        assert story["map_asset"] == "m063.png"
        assert len(story["intro"]) >= 29 and len(story["victory"]) >= 16
        assert [(d["attacker"], d["defender"], d["outcome"]) for d in story["duels"]] == [
            ("WeiChou27", "CaoGongGong39", "capture"),
            ("DianJie27", "YuLang39", "kill"),
        ]

        info = env.map_info()
        assert (int(info["width"]), int(info["height"])) == (25, 19)
        terrain = info["terrain"]
        assert all(terrain[3 * 25 + x] == "Wall" for x in list(range(4, 11)) + list(range(14, 21)))
        assert all(terrain[14 * 25 + x] == "Wall" for x in list(range(4, 11)) + list(range(14, 21)))
        assert all(terrain[3 * 25 + x] == "Gate" for x in (11, 12, 13))
        assert all(terrain[14 * 25 + x] == "Gate" for x in (11, 12, 13))
        assert all(terrain[y * 25 + 4] == "Gate" for y in (7, 8, 9))
        assert all(terrain[y * 25 + 20] == "Gate" for y in (7, 8, 9))
        assert all(unit["terrain"] not in IMPASSABLE for unit in living(env))

        roster = grouped(env)
        assert roster["CaoGongGong39"][0]["class"] == "Lord"
        assert roster["YuLang39"][0]["class"] == "Strategist"
        assert roster["XiFuJi39"][0]["class"] == "Strategist"
        assert int(roster["XiFuJi39"][0]["force"]) == 2
        assert len(roster["CaoGateGuard39"]) == 4
        assert len(roster["CaoArcher39"]) == 8
        assert len(roster["JinGuard39"]) == 3
        assert len(roster["JinArcher39"]) == 3

        snap = env.snapshot()
        next(u for u in snap["units"] if u["name"] == "WeiChou27").update({"x": 11, "y": 6})
        next(u for u in snap["units"] if u["name"] == "DianJie27").update({"x": 11, "y": 10})
        env.restore(snap)
        roster = grouped(env)
        _, _, terminated, truncated, _ = env.resolve_duel(
            int(roster["WeiChou27"][0]["id"]), int(roster["CaoGongGong39"][0]["id"])
        )
        assert not terminated and not truncated
        roster = grouped(env)
        _, _, terminated, truncated, result = env.resolve_duel(
            int(roster["DianJie27"][0]["id"]), int(roster["YuLang39"][0]["id"])
        )
        assert terminated and not truncated and int(result["status"]) == 3

    stage = (root / "game/sce/dongzhou/stage/39.lua").read_text(encoding="utf-8")
    config = (root / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    assert '"38a", "38b", "39"' in config
    assert "城墙不可跨越" in stage and "只能从四座三格城门入城" in stage
    assert "gally_hold_position = true" in stage
    assert Image.open(root / "assets/lzc/map/m063.png").size == (1600, 1216)
    assert manifest["grid"] == [25, 19]
    assert len(manifest["deployments"]) == len(living_manifest(manifest))
    prediction = json.loads(
        (root / "output/terrain_model/m063_ch39_prediction.json").read_text(encoding="utf-8")
    )
    assert prediction["auto_apply"] is False
    print("chapter 39 ok: four gates, Cao capture, Yu Lang duel, and dense source story")

def living_manifest(manifest):
    return manifest["deployments"]

if __name__ == "__main__":
    main()
