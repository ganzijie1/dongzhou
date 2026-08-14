import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGE_DIR = ROOT / "game/sce/dongzhou/stage"


def stage_rows(stage_name):
    text = (STAGE_DIR / f"{stage_name}.lua").read_text(encoding="utf-8")
    match = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert match, f"terrain block missing in {stage_name}"
    return re.findall(r'"([fgFwmrWiChbGeDP~]+)"', match.group(1)), text


def assert_reachable(rows, points):
    blocked = {"r", "W", "P", "~"}
    width, height = len(rows[0]), len(rows)
    for x, y in points:
        assert 0 <= x < width and 0 <= y < height
        assert rows[y][x] not in blocked, (x, y, rows[y][x])
    start = points[0]
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in seen or rows[ny][nx] in blocked:
                continue
            seen.add((nx, ny))
            stack.append((nx, ny))
    assert all(point in seen for point in points), "mission points are not connected"


def test_chapter45_maps_and_contracts():
    cases = {
        "45a": ("m068", 44, 28, [
            (23,18),(21,18),(11,14),(18,14),(22,12),(26,13),
            (20,7),(22,8),(19,18),(24,17),(7,12),(8,15),
            (37,10),(36,13),(12,11),(32,12),
        ]),
        "45b": ("m069", 36, 26, [
            (18,22),(18,17),(15,21),(21,21),(18,4),(18,13),
            (9,13),(27,13),(10,11),(25,15),(9,12),(26,14),
        ]),
    }
    for stage_name, (map_id, width, height, points) in cases.items():
        rows, _ = stage_rows(stage_name)
        manifest = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_ch45_manifest.json").read_text(encoding="utf-8"))
        assert len(rows) == height
        assert all(len(row) == width for row in rows)
        assert rows == manifest["terrain_rows"]
        assert manifest["grid"] == [width, height]
        assert not manifest["fence_cells"] and not manifest["wall_cells"]
        assert_reachable(rows, points)
        with Image.open(ROOT / f"assets/lzc/map/{map_id}.png") as image:
            assert image.size == (width * 48, height * 48)
            extrema = image.convert("RGB").getextrema()
            assert any(high - low > 40 for low, high in extrema)


def test_chapter45_progression_and_outcomes():
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    stage45a = (STAGE_DIR / "45a.lua").read_text(encoding="utf-8")
    stage45b = (STAGE_DIR / "45b.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"44", "45a", "45b", "46a"' in config
    for hero in ("JinXiangGong45", "XianQieJu45", "LangTan45", "XiQue45", "BaiBuHu45"):
        assert f'id = "{hero}"' in config
        assert f'"{hero}"' in gui

    assert 'set_unit_invulnerable("MengMingShi26"' not in stage45a
    assert 'set_unit_invulnerable("XiQiShu26"' not in stage45a
    assert 'set_unit_invulnerable("BaiYiBing26"' not in stage45a
    assert "孟明视、西乞术、白乙丙被击退视为被俘" in stage45a
    assert 'outcome = "kill"' in stage45a and "BaoManZi44" in stage45a
    assert "ambush_triggered" in stage45a and "spring_ambush" in stage45a

    assert "game:is_unit_within(\"BaiBuHu45\", {18,13}, 3)" in stage45b
    assert "di_remnants(game) <= 2" in stage45b
    assert "xianzhen_sacrificed = true" in stage45b
    assert 'outcome = "kill"' in stage45b and "XiQue45" in stage45b
    assert "先轸卸去盔甲" in stage45b
    assert "旁白" not in stage45a and "旁白" not in stage45b
    assert 'HISTORICAL_DEATH_HEROES.update({"BaoManZi44", "BaiBuHu45", "XianZhen27"})' in gui


if __name__ == "__main__":
    test_chapter45_maps_and_contracts()
    test_chapter45_progression_and_outcomes()
    print("chapter45 regression checks passed")
