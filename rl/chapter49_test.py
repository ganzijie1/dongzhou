from collections import deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGE_PATH = ROOT / "game/sce/dongzhou/stage/49.lua"
MANIFEST_PATH = ROOT / "assets/lzc/map_sources/m077_ch49_manifest.json"
BLOCKED = {"r", "W", "~", "P"}


def passable(rows, position):
    x, y = position
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def reachable(rows, start, goal):
    queue = deque([tuple(start)])
    seen = {tuple(start)}
    while queue:
        x, y = queue.popleft()
        if (x, y) == tuple(goal):
            return True
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point not in seen and passable(rows, point):
                seen.add(point)
                queue.append(point)
    return False


def lua_rows(stage):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def test_map_contract():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = manifest["terrain_rows"]
    stage = STAGE_PATH.read_text(encoding="utf-8")
    assert manifest["grid"] == [44, 30]
    assert len(rows) == 30 and all(len(row) == 44 for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / manifest["map"]).size == (2112, 1440)
    assert manifest["visual_grid_in_game"] is False
    assert not manifest["fence_cells"] and not manifest["wall_cells"]
    assert not manifest["camp_cells"] and not manifest["supply_sites"]
    for deployment in manifest["deployments"]:
        assert passable(rows, deployment["position"]), deployment
    assert reachable(rows, (36, 13), (11, 14))
    assert reachable(rows, (11, 14), (9, 14))


def test_story_and_battle_logic():
    stage = STAGE_PATH.read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"47a", "47b", "48a", "48b", "49", "50a", "50b", "50c" }' in config
    assert 'battle_title = "孟诸之变"' in stage
    assert stage.count("{ speaker =") >= 50
    assert 'speaker = "旁白"' not in stage
    assert "士会" in stage and "蔡国" in stage and "齐懿公" in stage
    assert "公子鲍" in stage and "竹林" in stage and "鲁文公" in stage
    assert 'gcommanders = { "HuaOu49" }' in stage
    assert 'game:set_unit_invulnerable("SongZhaoGong49", true)' in stage
    assert 'not game:has_unit("DangYiZhu49")' in stage
    assert 'game:set_unit_invulnerable("SongZhaoGong49", false)' in stage
    assert 'protector_fallen and not game:has_unit("SongZhaoGong49")' in stage
    assert 'HISTORICAL_DEATH_HEROES.update({"DangYiZhu49", "SongZhaoGong49"})' in gui
    assert '_LARGE_BATTLE_MAPS["m077.png"] = (44, 30, 48)' in gui
    assert '"HuaOu49": "华耦"' in gui and '"DangYiZhu49": "荡意诸"' in gui


def test_prediction_is_evidence_only():
    report = json.loads((ROOT / "output/terrain_model/m077_ch49_prediction.json").read_text(encoding="utf-8"))
    assert report["grid"] == [44, 30]
    assert report["auto_apply"] is False
    assert report["threshold"] >= 0.72


if __name__ == "__main__":
    test_map_contract()
    test_story_and_battle_logic()
    test_prediction_is_evidence_only()
    print("chapter49 regression checks passed")
