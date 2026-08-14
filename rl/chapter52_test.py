from collections import deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGE_PATH = ROOT / "game/sce/dongzhou/stage/52.lua"
MANIFEST_PATH = ROOT / "assets/lzc/map_sources/m082_ch52_manifest.json"
BLOCKED = {"r", "W", "~", "P"}


def passable(rows, point):
    x, y = point
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def reachable(rows, start, goal):
    queue = deque([tuple(start)])
    seen = {tuple(start)}
    while queue:
        x, y = queue.popleft()
        if (x, y) == tuple(goal):
            return True
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in seen and passable(rows, nxt):
                seen.add(nxt)
                queue.append(nxt)
    return False


def lua_rows(stage):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def parse_positions(stage):
    points = [(int(x), int(y)) for x, y in re.findall(r"position\s*=\s*\{(\d+),(\d+)\}", stage)]
    for block in re.findall(r"many\(game,[^\n]+\{\{(.*?)\}\},", stage):
        points.extend((int(x), int(y)) for x, y in re.findall(r"(\d+),(\d+)", block))
    return points


def test_map_contract_and_deployment():
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = data["terrain_rows"]
    stage = STAGE_PATH.read_text(encoding="utf-8")
    assert data["grid"] == [46, 30]
    assert len(rows) == 30 and all(len(row) == 46 for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / data["map"]).size == (2208, 1440)
    assert data["visual_grid_in_game"] is False
    for key in ("wall_cells", "fence_cells", "camp_cells", "supply_sites"):
        assert not data[key]
    for item in data["deployments"]:
        assert passable(rows, item["position"]), item
    for point in parse_positions(stage):
        assert passable(rows, point), point
    assert reachable(rows, (6, 5), (20, 11))
    assert reachable(rows, (20, 11), (27, 17))
    assert reachable(rows, (27, 17), (41, 16))


def test_story_battle_and_history_contract():
    stage = STAGE_PATH.read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '"50b", "50c", "51", "52", "53a", "53b" }' in config
    assert 'battle_title = "柳棼救郑"' in stage
    assert stage.count("{ speaker =") >= 50
    assert 'speaker = "旁白"' not in stage
    for topic in ("食指", "染指", "土囊", "郑襄公", "黑壤", "柳棼", "颍水", "株林", "泄冶"):
        assert topic in stage
    assert 'gcommanders = { "XiQue45" }' in stage
    assert 'game:is_unit_within("XiQue45", {20,11}, 3)' in stage
    assert 'not game:has_unit("ChuLiufenGuard52")' in stage
    assert 'not game:has_unit("ChuLiufenArcher52")' in stage
    for hero in ("ChuZhuangWang51", "ZhengXiangGong52", "GongZiQuJi52"):
        assert f'game:set_unit_invulnerable("{hero}", true)' in stage
    historical_lines = "\n".join(line for line in gui.splitlines() if "HISTORICAL_DEATH_HEROES" in line)
    for hero in ("ChuZhuangWang51", "ZhengXiangGong52", "GongZiQuJi52"):
        assert hero not in historical_lines
    assert config.count('id = "XiQue45"') == 1
    assert config.count('id = "ChuZhuangWang51"') == 1
    assert '_LARGE_BATTLE_MAPS["m082.png"] = (46, 30, 48)' in gui


def test_prediction_is_evidence_only():
    report = json.loads((ROOT / "output/terrain_model/m082_ch52_prediction.json").read_text(encoding="utf-8"))
    assert report["grid"] == [46, 30]
    assert report["threshold"] >= 0.72
    assert report["auto_apply"] is False


if __name__ == "__main__":
    test_map_contract_and_deployment()
    test_story_battle_and_history_contract()
    test_prediction_is_evidence_only()
    print("chapter52 regression checks passed")
