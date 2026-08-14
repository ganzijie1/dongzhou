from collections import deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / "game/sce/dongzhou/stage"
BLOCKED = {"r", "W", "~", "P"}


def load_manifest(name):
    return json.loads((ROOT / "assets/lzc/map_sources" / name).read_text(encoding="utf-8"))


def passable(rows, position):
    x, y = position
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def reachable(rows, start, goal):
    if not passable(rows, start) or not passable(rows, goal):
        return False
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


def lua_rows(stage_text):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage_text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def test_map_contracts():
    cases = [
        ("47a.lua", "m073_ch47a_manifest.json", (36, 26), (1728, 1248)),
        ("47b.lua", "m074_ch47b_manifest.json", (42, 28), (2016, 1344)),
    ]
    for stage_name, manifest_name, grid, pixels in cases:
        manifest = load_manifest(manifest_name)
        rows = manifest["terrain_rows"]
        assert manifest["grid"] == list(grid)
        assert len(rows) == grid[1] and all(len(row) == grid[0] for row in rows)
        assert lua_rows((STAGES / stage_name).read_text(encoding="utf-8")) == rows
        assert Image.open(ROOT / manifest["map"]).size == pixels
        for deployment in manifest["deployments"]:
            assert passable(rows, deployment["position"]), deployment

    manifest = load_manifest("m074_ch47b_manifest.json")
    rows = manifest["terrain_rows"]
    fences = {tuple(cell) for cell in manifest["fence_cells"]}
    gates = {tuple(cell) for item in manifest["gates"] for cell in item["cells"]}
    camps = {tuple(cell) for cell in manifest["camp_cells"]}
    assert fences == {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "P"}
    assert camps == {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "e"}
    assert camps == {tuple(cell) for cell in manifest["camp_icon_cells"]}
    assert camps == {tuple(cell) for cell in manifest["supply_sites"]}
    assert gates == {(6, 13), (6, 14), (25, 13), (25, 14)}
    assert all(passable(rows, gate) and gate not in fences for gate in gates)
    assert reachable(rows, (35, 13), (15, 14))
    assert reachable(rows, (15, 14), (2, 14))


def test_story_and_battle_logic():
    stage47a = (STAGES / "47a.lua").read_text(encoding="utf-8")
    stage47b = (STAGES / "47b.lua").read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"46a", "46b", "46c", "47a", "47b", "48a", "48b" }' in config
    assert 'battle_title = "雪夜陷长翟"' in stage47a
    assert 'battle_title = "令狐夜袭"' in stage47b
    assert "弄玉" in stage47a and "三良" in stage47a and "阳处父" in stage47a
    assert "穆嬴" in stage47b and "公子雍" in stage47b and "刳首" in stage47b
    assert stage47a.count("{ speaker =") >= 28
    assert stage47b.count("{ speaker =") >= 30
    assert "旁白" not in stage47a and "旁白" not in stage47b

    assert 'gduel_enabled = false' in stage47a
    assert 'game:set_unit_invulnerable("QiaoRu47", true)' in stage47a
    assert 'game:is_unit_within("QiaoRu47", {18,13}, 2)' in stage47a
    assert 'game:set_unit_invulnerable("QiaoRu47", false)' in stage47a
    assert 'gduel_enabled = true' in stage47a
    assert 'attacker = "FuFuZhongSheng47", defender = "QiaoRu47"' in stage47a
    assert 'outcome = "kill"' in stage47a

    for survivor in ("BaiYiBing26", "XianMie47", "ShiHui47"):
        assert f'game:set_unit_invulnerable("{survivor}", true)' in stage47b
    assert 'game:set_unit_invulnerable("GongZiYong47", true)' not in stage47b
    assert 'not game:has_unit("GongZiYong47")' in stage47b
    assert "qin_regular_alive(game) <= 4" in stage47b
    assert 'HISTORICAL_DEATH_HEROES.update({"QiaoRu47", "GongZiYong47"})' in gui


def test_prediction_reports_are_evidence_only():
    for name in ("m073_ch47_prediction.json", "m074_ch47_prediction.json"):
        report = json.loads((ROOT / "output/terrain_model" / name).read_text(encoding="utf-8"))
        assert report["auto_apply"] is False
        assert report["threshold"] >= 0.72


if __name__ == "__main__":
    test_map_contracts()
    test_story_and_battle_logic()
    test_prediction_reports_are_evidence_only()
    print("chapter47 regression checks passed")
