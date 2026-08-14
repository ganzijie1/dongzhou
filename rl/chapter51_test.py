from collections import deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGE_PATH = ROOT / "game/sce/dongzhou/stage/51.lua"
MANIFEST_PATH = ROOT / "assets/lzc/map_sources/m081_ch51_manifest.json"
BLOCKED = {"r", "W", "~", "P"}


def passable(rows, point):
    x, y = point
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def find_path(rows, start, goal):
    queue = deque([tuple(start)])
    previous = {tuple(start): None}
    while queue:
        point = queue.popleft()
        if point == tuple(goal):
            path = []
            while point is not None:
                path.append(point)
                point = previous[point]
            return list(reversed(path))
        x, y = point
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in previous and passable(rows, nxt):
                previous[nxt] = point
                queue.append(nxt)
    return []


def reachable(rows, start, goal):
    return bool(find_path(rows, start, goal))


def lua_rows(stage):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def parse_positions(stage):
    points = [(int(x), int(y)) for x, y in re.findall(r"position\s*=\s*\{(\d+),(\d+)\}", stage)]
    for block in re.findall(r"many\(game,[^\n]+\{\{(.*?)\}\},", stage):
        points.extend((int(x), int(y)) for x, y in re.findall(r"(\d+),(\d+)", block))
    return points


def test_map_contract():
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = data["terrain_rows"]
    stage = STAGE_PATH.read_text(encoding="utf-8")
    assert data["grid"] == [48, 34]
    assert len(rows) == 34 and all(len(row) == 48 for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / data["map"]).size == (2304, 1632)
    assert data["visual_grid_in_game"] is False
    assert not data["wall_cells"] and not data["fence_cells"]
    assert not data["camp_cells"] and not data["supply_sites"]
    for item in data["deployments"]:
        assert passable(rows, item["position"]), item
    for point in parse_positions(stage):
        assert passable(rows, point), (point, rows[point[1]][point[0]])

    # Qinghe is an unbroken three-cell water barrier except for the explicit east ford.
    assert all(rows[y][x] == "~" for y in range(27, 30) for x in range(44))
    assert all(passable(rows, (x, y)) for y in range(27, 30) for x in range(44, 48))
    assert not passable(rows, (24, 28))
    cross_river_path = find_path(rows, (24, 25), (24, 31))
    assert cross_river_path
    assert any(x >= 44 and 27 <= y <= 29 for x, y in cross_river_path)
    assert reachable(rows, (24, 25), (45, 31))
    assert reachable(rows, (19, 23), (24, 16))


def test_story_duel_and_outcomes():
    stage = STAGE_PATH.read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"49", "50a", "50b", "50c", "51", "52" }' in config
    assert 'battle_title = "清河桥之战"' in stage
    assert stage.count("{ speaker =") >= 55
    assert 'speaker = "旁白"' not in stage
    for topic in ("赵穿", "董狐", "九鼎", "斗越椒", "绝缨", "孙叔敖"):
        assert topic in stage
    assert 'attacker = "YangYouJi51", defender = "DouYueJiao40"' in stage
    assert 'outcome = "kill"' in stage and 'exp = 100' in stage
    assert 'not game:has_unit("DouYueJiao40")' in stage
    assert 'game:set_unit_invulnerable("DouBenHuang51", true)' in stage
    assert 'HISTORICAL_DEATH_HEROES.add("DouYueJiao40")' in gui
    historical_lines = "\n".join(line for line in gui.splitlines() if "HISTORICAL_DEATH_HEROES" in line)
    assert "DouBenHuang51" not in historical_lines
    assert 'class = "King"' in re.search(r'.{0,30}id = "ChuZhuangWang51".{0,150}', config).group(0)
    assert '_LARGE_BATTLE_MAPS["m081.png"] = (48, 34, 48)' in gui


def test_prediction_is_evidence_only():
    report = json.loads((ROOT / "output/terrain_model/m081_ch51_prediction.json").read_text(encoding="utf-8"))
    assert report["grid"] == [48, 34]
    assert report["threshold"] >= 0.72
    assert report["auto_apply"] is False


if __name__ == "__main__":
    test_map_contract()
    test_story_duel_and_outcomes()
    test_prediction_is_evidence_only()
    print("chapter51 regression checks passed")
