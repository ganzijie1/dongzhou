"""Regression checks for chapter forty's large Chengpu battlefield."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image
from rl.mengde_env import MengdeEnv
from rl.save_system import read_slot

EXE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}

def living(env):
    return [unit for unit in env.unit_info() if not unit["dead"]]

def grouped(env):
    result = {}
    for unit in living(env):
        result.setdefault(unit["name"], []).append(unit)
    return result

def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "assets/lzc/map_sources/m064_ch40_manifest.json").read_text(encoding="utf-8")
    )
    assert sum(item["force"] == 1 for item in manifest["deployments"]) == 11
    assert sum(item["force"] == 2 for item in manifest["deployments"]) == 11
    assert sum(item["force"] == 3 for item in manifest["deployments"]) == 50
    assert int(manifest["cell_pixels"]) == 32
    enemy_positions = [item["position"] for item in manifest["deployments"] if item["force"] == 3]
    max_visible_enemies = max(
        sum(x0 <= x < x0 + 29 and y0 <= y < y0 + 21 for x, y in enemy_positions)
        for x0 in range(64 - 29 + 1)
        for y0 in range(42 - 21 + 1)
    )
    assert max_visible_enemies >= 33
    assert sum(17 <= x < 47 and 4 <= y < 26 for x, y in enemy_positions) >= 15

    with MengdeEnv(EXE, scenario="dongzhou", interactive=True, max_episode_actions=100) as env:
        env._request("LOAD_STAGE 64")
        story = env.story_info()
        assert story["chapter"] == "\u7b2c\u56db\u5341\u3001\u56db\u5341\u4e00\u56de"
        assert story["battle_title"] == "\u57ce\u6fee\u4e4b\u6218"
        assert story["map_asset"] == "m064.png"
        assert len(story["intro"]) >= 30 and len(story["victory"]) >= 17
        assert [(d["attacker"], d["defender"], d["outcome"]) for d in story["duels"]] == [
            ("XuChen27", "GongZiYin40", "kill"),
            ("BaiYiBing30", "DouBo33", "retreat"),
        ]

        info = env.map_info()
        assert (int(info["width"]), int(info["height"])) == (64, 42)
        terrain = list(info["terrain"])
        fence_cells = {tuple(cell) for cell in manifest["fence_cells"]}
        camp_cells = {tuple(cell) for cell in manifest["camp_cells"]}
        wall_cells = {tuple(cell) for cell in manifest["wall_cells"]}
        castle_cells = {tuple(cell) for cell in manifest["castle_cells"]}
        gate_cells = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
        assert all(terrain[y * 64 + x] == "Fence" for x, y in fence_cells)
        assert all(terrain[y * 64 + x] == "Camp" for x, y in camp_cells)
        assert all(terrain[y * 64 + x] == "Wall" for x, y in wall_cells)
        assert all(terrain[y * 64 + x] == "Castle" for x, y in castle_cells)
        assert all(terrain[y * 64 + x] not in IMPASSABLE for x, y in gate_cells)
        assert {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]} == camp_cells | castle_cells
        roster = grouped(env)
        own = [unit for unit in living(env) if int(unit["force"]) == 1]
        allies = [unit for unit in living(env) if int(unit["force"]) == 2]
        enemy = [unit for unit in living(env) if int(unit["force"]) == 4]
        assert len(own) == 11 and len(allies) == 11 and len(enemy) == 50
        assert all(int(unit["direction"]) == 3 for unit in enemy)
        assert all(unit["terrain"] not in IMPASSABLE for unit in own + allies + enemy)
        assert roster["DouYiShen40"][0]["class"] == "Cavalry"
        assert roster["DouYueJiao40"][0]["class"] == "Archer"
        assert roster["GongZiYin40"][0]["class"] == "Cavalry"
        assert len(roster["ChenGuard40"]) == 3 and len(roster["CaiGuard40"]) == 3
        assert len(roster["ChuGuard40"]) == 12
        assert "ShiGui40" in roster and "BaiChou40" in roster

        snap = env.snapshot()
        next(u for u in snap["units"] if u["name"] == "XuChen27").update({"x": 53, "y": 28})
        next(u for u in snap["units"] if u["name"] == "BaiYiBing30").update({"x": 48, "y": 32})
        next(u for u in snap["units"] if u["name"] == "DouYiShen40").update({"hp": 0})
        env.restore(snap)
        roster = grouped(env)
        _, _, terminated, truncated, _ = env.resolve_duel(
            int(roster["XuChen27"][0]["id"]), int(roster["GongZiYin40"][0]["id"])
        )
        assert not terminated and not truncated
        assert "GongZiYin40" not in grouped(env)

        requested_save = read_slot(1)
        assert requested_save is not None
        assert int(requested_save["battle"]["stage_index"]) == 64
        env.restore(requested_save["battle"])
        restored = living(env)
        assert len(restored) == 72
        assert all(unit["terrain"] not in IMPASSABLE for unit in restored)

    stage = (root / "game/sce/dongzhou/stage/40.lua").read_text(encoding="utf-8")
    config = (root / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    assert '"38b", "39", "40"' in config
    assert "size = {64, 42}" in stage
    assert "虎皮" in stage and "曳柴扬尘" in stage and "退避三舍" in stage
    assert 'battle_title = "城濮之战"' in stage
    assert 'game:set_force_direction(Enum.force.enemy, 3)' in stage
    assert 'game:set_unit_invulnerable("ChengDeChen33", true)' in stage
    assert 'game:set_unit_invulnerable("DouYueJiao40", true)' not in stage
    assert 'not game:has_unit("WeiChou27") then return Enum.status.defeat' in stage
    assert Image.open(root / "assets/lzc/map/m064.png").size == (2048, 1344)
    assert (root / "output/imagegen/m064_prompt.txt").is_file()
    gui_source = (root / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '_LARGE_BATTLE_MAPS["m064.png"] = (64, 42, 32)' in gui_source
    assert "pygame.MOUSEWHEEL" in gui_source and "pygame.K_PAGEDOWN" in gui_source
    assert 'x=(17 * cell if map_name == "m064.png" else 0)' in gui_source
    prediction = json.loads(
        (root / "output/terrain_model/m064_ch40_prediction.json").read_text(encoding="utf-8")
    )
    assert prediction["auto_apply"] is False
    print("chapter 40 ok: 64x42 Chengpu map, 11 controlled, 11 allied AI, 50 coalition enemies, and source duels")

if __name__ == "__main__":
    main()
