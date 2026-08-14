from collections import deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"r", "W", "~", "P"}


def passable(rows, point):
    x, y = point
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def reachable(rows, start, goal):
    queue = deque([tuple(start)]); seen = {tuple(start)}
    while queue:
        point = queue.popleft()
        if point == tuple(goal): return True
        x, y = point
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in seen and passable(rows, nxt):
                seen.add(nxt); queue.append(nxt)
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


def validate_map(stage_name, manifest_name, expected_grid, expected_pixels):
    stage = (ROOT / f"game/sce/dongzhou/stage/{stage_name}.lua").read_text(encoding="utf-8")
    data = json.loads((ROOT / f"assets/lzc/map_sources/{manifest_name}").read_text(encoding="utf-8"))
    rows = data["terrain_rows"]
    assert data["grid"] == expected_grid
    assert len(rows) == expected_grid[1] and all(len(row) == expected_grid[0] for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / data["map"]).size == expected_pixels
    assert data["visual_grid_in_game"] is False
    walls = {tuple(p) for p in data["wall_cells"]}
    assert walls == {(x, y) for y, row in enumerate(rows) for x, tile in enumerate(row) if tile == "W"}
    for gate in data["gates"]:
        for point in gate["cells"]:
            assert passable(rows, point) and tuple(point) not in walls
    for point in parse_positions(stage):
        assert passable(rows, point), point
    report = json.loads((ROOT / f"output/terrain_model/{stage_name.replace('53a','m083_ch53a').replace('53b','m084_ch53b')}_prediction.json").read_text(encoding="utf-8"))
    assert report["threshold"] >= 0.72 and report["auto_apply"] is False
    return stage, data, rows


def test_zhulin_contract():
    stage, data, rows = validate_map("53a", "m083_ch53a_manifest.json", [46, 30], (2208, 1440))
    assert reachable(rows, (7, 15), (36, 15))
    path_gates = [tuple(p) for g in data["gates"] for p in g["cells"]]
    assert any(reachable(rows, (7, 15), gate) for gate in path_gates)
    assert 'not game:has_unit("XiaZhengShu53")' in stage
    assert 'battle_title = "株林讨逆"' in stage


def test_zheng_contract():
    stage, data, rows = validate_map("53b", "m084_ch53b_manifest.json", [52, 34], (2496, 1632))
    assert reachable(rows, (20, 16), (31, 16))
    assert all(rows[y][x] == "W" for x, y in map(tuple, data["wall_cells"]))
    assert 'not game:has_unit("ZhengHuangmenGuard53")' in stage
    assert 'game:is_unit_within("LeBo51", {31,16}, 2)' in stage
    for hero in ("ZhengXiangGong52", "GongZiQuJi52"):
        assert f'game:set_unit_invulnerable("{hero}", true)' in stage


def test_story_sequence_and_outcomes():
    a = (ROOT / "game/sce/dongzhou/stage/53a.lua").read_text(encoding="utf-8")
    b = (ROOT / "game/sce/dongzhou/stage/53b.lua").read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '"50c", "51", "52", "53a", "53b", "54a", "54b" }' in config
    assert a.count("{ speaker =") + b.count("{ speaker =") >= 55
    assert 'speaker = "旁白"' not in a + b
    for topic in ("泄冶", "株林", "夏征舒", "车裂", "蹊田夺牛", "唐狡", "十七日", "三个月", "牵羊", "六百乘", "管城"):
        assert topic in a + b
    historical_lines = "\n".join(line for line in gui.splitlines() if "HISTORICAL_DEATH_HEROES" in line)
    assert "XiaZhengShu53" in historical_lines
    for hero in ("ZhengXiangGong52", "GongZiQuJi52", "ChuZhuangWang51"):
        assert hero not in historical_lines
    for reused in ("ChuZhuangWang51", "GongZiYingQi51", "GongZiCe51", "LeBo51"):
        assert config.count(f'id = "{reused}"') == 1
    assert '_LARGE_BATTLE_MAPS["m083.png"] = (46, 30, 48)' in gui
    assert '_LARGE_BATTLE_MAPS["m084.png"] = (52, 34, 48)' in gui


if __name__ == "__main__":
    test_zhulin_contract(); test_zheng_contract(); test_story_sequence_and_outcomes()
    print("chapter53 regression checks passed")
