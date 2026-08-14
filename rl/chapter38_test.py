"""Regression checks for chapter thirty-eight's Wangcheng and Wen-Yuan battles."""
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
    for u in living(env):
        out.setdefault(u["name"], []).append(u)
    return out

def wait_once(env):
    action = next(a for a in env.list_actions() if int(a["type"]) == 0)
    return env.step(int(action["index"]))

def check_map(env, width, height):
    info = env.map_info()
    assert (int(info["width"]), int(info["height"])) == (width, height)
    assert all(u["terrain"] not in IMPASSABLE for u in living(env))
    return info

def main():
    root = Path(__file__).resolve().parents[1]
    manifests = {
        62: json.loads((root / "assets/lzc/map_sources/m061_ch38_manifest.json").read_text(encoding="utf-8")),
        63: json.loads((root / "assets/lzc/map_sources/m062_ch38_manifest.json").read_text(encoding="utf-8")),
    }

    with MengdeEnv(EXE, scenario="dongzhou", interactive=True, max_episode_actions=100) as env:
        env._request("LOAD_STAGE 61")
        story = env.story_info()
        assert story["map_asset"] == "m061.png"
        assert len(story["intro"]) >= 20 and len(story["victory"]) >= 15
        check_map(env, 23, 16)
        roster = grouped(env)
        assert roster["ZhouXiangWang29"][0]["class"] == "King"
        assert roster["FuChen38"][0]["class"] == "Strategist"
        assert roster["ChiDing38"][0]["class"] == "Lord"
        assert (int(roster["FuChen38"][0]["x"]), int(roster["FuChen38"][0]["y"])) == (11, 9)
        snap = env.snapshot()
        next(u for u in snap["units"] if u["name"] == "ZhouXiangWang29").update({"x": 21, "y": 14})
        env.restore(snap)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    with MengdeEnv(EXE, scenario="dongzhou", interactive=True, max_episode_actions=100) as env:
        env._request("LOAD_STAGE 62")
        story = env.story_info()
        assert story["map_asset"] == "m062.png"
        assert len(story["intro"]) >= 18 and len(story["victory"]) >= 23
        info = check_map(env, 27, 17)
        terrain = info["terrain"]
        assert all(terrain[9 * 27 + x] == "Wall" for x in range(15, 26))
        assert all(terrain[9 * 27 + x] == "Gate" for x in (5, 6, 7))
        roster = grouped(env)
        assert roster["TaiShuDai38"][0]["class"] == "Lord"
        assert roster["YuanBoGuan38"][0]["class"] == "Lord"
        assert len(roster["YuanGuard38"]) == 4
        assert len(roster["YuanArcher38"]) == 2
        yuan = [u for u in living(env) if u["name"] in {"YuanBoGuan38", "YuanGuard38", "YuanArcher38"}]
        assert len(yuan) == 7 and all(int(u["x"]) >= 15 and int(u["y"]) < 9 for u in yuan)
        assert [(d["attacker"], d["defender"], d["outcome"]) for d in story["duels"]] == [
            ("WeiChou27", "TaiShuDai38", "kill")
        ]

        snap = env.snapshot()
        next(u for u in snap["units"] if u["name"] == "WeiChou27").update({"x": 5, "y": 4})
        for u in snap["units"]:
            if u["name"] in {"WeiHou38", "WenRebelGuard38", "WenRebelArcher38"}:
                u["hp"] = 0
        env.restore(snap)
        roster = grouped(env)
        _, _, terminated, truncated, _ = env.resolve_duel(
            int(roster["WeiChou27"][0]["id"]), int(roster["TaiShuDai38"][0]["id"])
        )
        assert not terminated and not truncated
        start_turn = int(env.snapshot()["turn_current"])
        for _ in range(80):
            _, _, terminated, truncated, result = wait_once(env)
            assert not truncated
            if terminated:
                break
        assert terminated and int(result["status"]) == 3
        assert int(env.snapshot()["turn_current"]) >= start_turn + 3
        assert all(name in grouped(env) for name in ("YuanBoGuan38", "YuanGuard38", "YuanArcher38"))
        final_roster = grouped(env)
        expected = {"ChongEr27": (17, 11), "ZhaoShuai27": (19, 11), "WeiChou27": (20, 12), "XiZhen38": (21, 11), "LuanZhi36": (23, 11)}
        assert all((int(final_roster[name][0]["x"]), int(final_roster[name][0]["y"])) == pos for name, pos in expected.items())
        assert sorted((int(u["x"]), int(u["y"])) for u in final_roster["JinGuard38"]) == [(18, 12), (22, 12)]
        assert sorted((int(u["x"]), int(u["y"])) for u in final_roster["JinArcher38"]) == [(19, 13), (21, 13)]


    stage = (root / "game/sce/dongzhou/stage/38b.lua").read_text(encoding="utf-8")
    assert "yuan_phase_start_turn + 3" in stage
    assert "replenish_yuan_defenders(game)" in stage
    assert 'fill_yuan_defenders(game, "YuanGuard38", 4, yuan_guard_origins)' in stage
    assert 'fill_yuan_defenders(game, "YuanArcher38", 2, yuan_archer_origins)' in stage
    assert "if not yuan_defenders_alive(game) then return Enum.status.defeat end" not in stage
    assert "持续补员" in stage
    assert "围原第三日" in stage
    assert not (root / "game/sce/dongzhou/stage/38c.lua").exists()
    assert Image.open(root / "assets/lzc/map/m061.png").size == (1472, 1024)
    assert Image.open(root / "assets/lzc/map/m062.png").size == (1728, 1088)
    for idx, dims in ((62, (23, 16)), (63, (27, 17))):
        rows = manifests[idx]["terrain_rows"]
        assert len(rows) == dims[1] and all(len(row) == dims[0] for row in rows)
    print("chapter 38 ok: Wen bosses, enclosed Yuan garrison, three-turn trust phase, and retreat")

if __name__ == "__main__":
    main()
