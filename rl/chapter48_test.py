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
        ("48a.lua", "m075_ch48a_manifest.json", (40, 28), (1920, 1344)),
        ("48b.lua", "m076_ch48b_manifest.json", (54, 32), (2592, 1536)),
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

        fences = {tuple(cell) for cell in manifest["fence_cells"]}
        gates = {tuple(cell) for item in manifest["gates"] for cell in item["cells"]}
        camps = {tuple(cell) for cell in manifest["camp_cells"]}
        assert fences == {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "P"}
        assert camps == {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "e"}
        assert camps == {tuple(cell) for cell in manifest["camp_icon_cells"]}
        assert camps == {tuple(cell) for cell in manifest["supply_sites"]}
        assert all(passable(rows, gate) and gate not in fences for gate in gates)

    rows75 = load_manifest("m075_ch48a_manifest.json")["terrain_rows"]
    assert reachable(rows75, (36, 14), (19, 14))
    assert reachable(rows75, (19, 14), (18, 3))
    assert reachable(rows75, (19, 14), (18, 25))

    rows76 = load_manifest("m076_ch48b_manifest.json")["terrain_rows"]
    assert all(rows76[y][x] == "~" for y in range(32) for x in range(5))
    assert reachable(rows76, (14, 15), (30, 15))
    assert reachable(rows76, (46, 15), (30, 15))
    assert not reachable(rows76, (14, 15), (2, 15))


def test_story_and_battle_logic():
    stage48a = (STAGES / "48a.lua").read_text(encoding="utf-8")
    stage48b = (STAGES / "48b.lua").read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"47a", "47b", "48a", "48b", "49" }' in config
    assert 'battle_title = "郑境诱营"' in stage48a
    assert 'battle_title = "河曲之战"' in stage48b
    assert "五将" in stage48a and "先克" in stage48a and "厥貉" in stage48a
    assert "羁马" in stage48b and "寿馀" in stage48b and "绕朝" in stage48b
    assert stage48a.count("{ speaker =") >= 28
    assert stage48b.count("{ speaker =") >= 30
    assert "旁白" not in stage48a and "旁白" not in stage48b

    for survivor in ("GongZiJian48", "GongZiPang48", "YueEr48"):
        assert f'not game:has_unit("{survivor}")' in stage48a
        assert survivor not in re.search(r"HISTORICAL_DEATH_HEROES.update\([^\n]*", gui).group(0)
    assert "ambush_triggered" in stage48a
    assert 'game:is_unit_within("GongZiJian48", {19,14}, 2)' in stage48a
    assert "被俘并释放" in stage48a

    for survivor in ("QinKangGong48", "XiQiShu26", "BaiYiBing26", "ShiHui47"):
        assert f'game:set_unit_invulnerable("{survivor}", true)' in stage48b or survivor in stage48b
    assert "game:are_units_within(hero, \"ZhaoChuan48\", 1)" in stage48b
    assert "rescue_turn = game:get_turn_current()" in stage48b
    assert "game:get_turn_current() >= rescue_turn + 3" in stage48b
    assert 'game:is_unit_within("ZhaoChuan48", {46,15}, 7)' in stage48b
    assert '_LARGE_BATTLE_MAPS["m075.png"] = (40, 28, 48)' in gui
    assert '_LARGE_BATTLE_MAPS["m076.png"] = (54, 32, 48)' in gui


def test_prediction_reports_are_evidence_only():
    for name in ("m075_ch48_prediction.json", "m076_ch48_prediction.json"):
        report = json.loads((ROOT / "output/terrain_model" / name).read_text(encoding="utf-8"))
        assert report["auto_apply"] is False
        assert report["threshold"] >= 0.72


if __name__ == "__main__":
    test_map_contracts()
    test_story_and_battle_logic()
    test_prediction_reports_are_evidence_only()
    print("chapter48 regression checks passed")
