import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / "game/sce/dongzhou/stage"
BLOCKED = {"r", "W", "P", "~"}


def load_stage(stage_id):
    text = (STAGES / f"{stage_id}.lua").read_text(encoding="utf-8")
    match = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert match
    rows = re.findall(r'"([fgFwmrWiChbGeDP~]+)"', match.group(1))
    return rows, text


def reachable(rows, start):
    width, height = len(rows[0]), len(rows)
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            px, py = point
            if not (0 <= px < width and 0 <= py < height):
                continue
            if point in seen or rows[py][px] in BLOCKED:
                continue
            seen.add(point)
            stack.append(point)
    return seen


def test_map_contracts_and_deployments():
    cases = {
        "46a": ("m070", 38, 26, [(7,13),(8,11),(8,15),(6,10),(6,16),(30,13),(13,9),(29,17)]),
        "46b": ("m071", 42, 28, [(7,14),(5,16),(6,12),(10,14),(35,14),(34,11),(34,17),(22,15),(23,14)]),
        "46c": ("m072", 36, 28, [(17,24),(17,21),(14,23),(20,23),(19,25),(17,5),(16,17),(18,17)]),
    }
    for stage_id, (map_id, width, height, points) in cases.items():
        rows, _ = load_stage(stage_id)
        manifest = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_ch46_manifest.json").read_text(encoding="utf-8"))
        assert len(rows) == height
        assert all(len(row) == width for row in rows)
        assert rows == manifest["terrain_rows"]
        assert manifest["grid"] == [width, height]
        for x, y in points:
            assert rows[y][x] not in BLOCKED, (stage_id, x, y, rows[y][x])
        area = reachable(rows, points[0])
        assert all(point in area for point in points)
        with Image.open(ROOT / f"assets/lzc/map/{map_id}.png") as image:
            assert image.size == (width * 48, height * 48)
            assert any(high - low > 40 for low, high in image.convert("RGB").getextrema())
        prediction = json.loads((ROOT / f"output/terrain_model/{map_id}_ch46_prediction.json").read_text(encoding="utf-8"))
        assert prediction["grid"] == [width, height]
        assert prediction["auto_apply"] is False


def test_wangguan_structures():
    rows, _ = load_stage("46c")
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m072_ch46_manifest.json").read_text(encoding="utf-8"))
    lua_walls = {(x, y) for y, row in enumerate(rows) for x, tile in enumerate(row) if tile == "W"}
    manifest_walls = {tuple(cell) for cell in manifest["wall_cells"]}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    assert lua_walls == manifest_walls
    assert gates == {(16, 17), (17, 17), (18, 17)}
    assert all(rows[y][x] == "G" for x, y in gates)
    assert all(rows[y][x] == "C" for x, y in manifest["castle_cells"])
    assert (17, 5) in reachable(rows, (17, 24))


def test_chapter46_logic_and_story():
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    a = (STAGES / "46a.lua").read_text(encoding="utf-8")
    b = (STAGES / "46b.lua").read_text(encoding="utf-8")
    c = (STAGES / "46c.lua").read_text(encoding="utf-8")
    previous = (STAGES / "45b.lua").read_text(encoding="utf-8")

    assert '"45a", "45b", "46a", "46b", "46c", "47a"' in config
    for hero in ("BaiTun46", "JinChariot46", "XianBo46", "WangguanCommander46"):
        assert f'id = "{hero}"' in config
        assert f'"{hero}"' in gui
    assert "max(999" in gui
    assert 'battle_title = "大谷之战"' in a
    assert "换尸" not in re.search(r'battle_title\s*=\s*"([^"]+)"', a).group(1)
    assert 'game:set_unit_invulnerable("BaiTun46", true)' in a
    assert 'game:are_units_within("HuSheGu27", "BaiTun46", 1)' in a

    for hero in ("MengMingShi26", "XiQiShu26", "BaiYiBing26"):
        assert f'game:set_unit_invulnerable("{hero}"' not in b
        assert f'not game:has_unit("{hero}")' in b
    assert "均可正常击退" in b
    assert "qin_regular_alive(game) <= 3" in b
    assert "XianBo46" in b and "狼瞫遍体是伤" in b
    assert 'HISTORICAL_DEATH_HEROES.update({"DouBo33", "ChuChengWang33", "XianBo46", "LangTan45"})' in gui

    assert "连续城墙不可跨越" in c
    assert "孟明视接近王官城池" in c
    assert "收葬当年死士遗骨" in c
    assert "白屯" not in previous
    assert "旁白" not in a and "旁白" not in b and "旁白" not in c


if __name__ == "__main__":
    test_map_contracts_and_deployments()
    test_wangguan_structures()
    test_chapter46_logic_and_story()
    print("chapter46 regression checks passed")
