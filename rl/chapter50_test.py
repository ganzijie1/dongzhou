from collections import Counter, deque
from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STAGES = ROOT / "game/sce/dongzhou/stage"
BLOCKED = {"r", "W", "~", "P"}


def manifest(name):
    return json.loads((ROOT / "assets/lzc/map_sources" / name).read_text(encoding="utf-8"))


def passable(rows, point):
    x, y = point
    return 0 <= y < len(rows) and 0 <= x < len(rows[0]) and rows[y][x] not in BLOCKED


def reachable(rows, start, goal):
    queue, seen = deque([tuple(start)]), {tuple(start)}
    while queue:
        point = queue.popleft()
        if point == tuple(goal):
            return True
        x, y = point
        for nxt in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nxt not in seen and passable(rows, nxt):
                seen.add(nxt)
                queue.append(nxt)
    return False


def lua_rows(text):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def all_spawn_positions(stage):
    return [(int(x), int(y)) for x, y in re.findall(r"generate_unit\([^\n]+\{(\d+),(\d+)\}", stage)]


def test_map_contracts():
    cases = [
        ("50a.lua", "m078_ch50a_manifest.json", [42, 28], (2016, 1344)),
        ("50b.lua", "m079_ch50b_manifest.json", [46, 30], (2208, 1440)),
        ("50c.lua", "m080_ch50c_manifest.json", [38, 26], (1824, 1248)),
    ]
    for stage_name, manifest_name, grid, pixels in cases:
        data = manifest(manifest_name)
        rows = data["terrain_rows"]
        stage = (STAGES / stage_name).read_text(encoding="utf-8")
        assert data["grid"] == grid
        assert len(rows) == grid[1] and all(len(row) == grid[0] for row in rows)
        assert lua_rows(stage) == rows
        assert Image.open(ROOT / data["map"]).size == pixels
        assert data["visual_grid_in_game"] is False
        for item in data["deployments"]:
            assert passable(rows, item["position"]), item
        for point in all_spawn_positions(stage):
            assert passable(rows, point), (stage_name, point, rows[point[1]][point[0]])

        walls = {tuple(cell) for cell in data["wall_cells"]}
        lua_walls = {(x, y) for y, row in enumerate(rows) for x, tile in enumerate(row) if tile == "W"}
        assert walls == lua_walls
        gates = {tuple(cell) for gate in data["gates"] for cell in gate["cells"]}
        assert all(rows[y][x] == "G" and (x, y) not in walls for x, y in gates)
        assert not data["camp_cells"] and not data["fence_cells"] and not data["supply_sites"]

    daji = manifest("m078_ch50a_manifest.json")["terrain_rows"]
    assert reachable(daji, (34, 13), (8, 14))

    jiao = manifest("m079_ch50b_manifest.json")["terrain_rows"]
    assert reachable(jiao, (39, 14), (15, 14))
    assert reachable(jiao, (15, 14), (12, 14))
    assert not passable(jiao, (15, 13)) and not passable(jiao, (15, 16))

    taoyuan = manifest("m080_ch50c_manifest.json")["terrain_rows"]
    assert reachable(taoyuan, (29, 12), (12, 12))
    assert reachable(taoyuan, (12, 12), (1, 13))
    assert not passable(taoyuan, (12, 11)) and not passable(taoyuan, (12, 14))


def test_story_and_logic():
    a = (STAGES / "50a.lua").read_text(encoding="utf-8")
    b = (STAGES / "50b.lua").read_text(encoding="utf-8")
    c = (STAGES / "50c.lua").read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"48a", "48b", "49", "50a", "50b", "50c", "51" }' in config
    assert a.count("{ speaker =") >= 35 and b.count("{ speaker =") >= 13 and c.count("{ speaker =") >= 30
    assert all('speaker = "旁白"' not in stage for stage in (a, b, c))
    assert "公子恶" in a and "叔仲彭生" in a and "叔肹" in a
    assert "三年不飞" in a and "北林" in a and "解扬" in a
    assert 'not game:has_unit("HuaYuan50")' in a
    death_line = re.search(r'HISTORICAL_DEATH_HEROES.update\(\{"TiMiMing50", "LingAo50"\}\)', gui)
    assert death_line
    assert "HuaYuan50" not in death_line.group(0)

    assert 'game:is_unit_within("ZhaoChuan48", {15,14}, 2)' in b
    assert "game:get_turn_current() >= relief_turn + 3" in b
    assert "qin_retreat" in b and 'game:set_unit_invulnerable("QinSiegeCaptain50", true)' in b

    assert 'game:generate_unit("TiMiMing50", 1, Enum.force.own' in c
    assert 'not game:has_unit("LingAo50")' in c
    assert 'game:is_unit_within("ZhaoDun47", {12,13}, 1)' in c
    assert 'game:generate_unit("LingZhe50", 1, Enum.force.ally, {10,13})' in c
    assert 'game:is_unit_within("ZhaoDun47", {1,13}, 0)' in c
    assert 'game:set_unit_invulnerable("JinLingGong50", true)' in c or "JinLingGong50" in c
    assert '"LingAo50": "灵獒"' in gui and 'return "lingao"' in gui
    for name, size in (("m078.png", (42, 28, 48)), ("m079.png", (46, 30, 48)), ("m080.png", (38, 26, 48))):
        assert f'_LARGE_BATTLE_MAPS["{name}"] = {size}' in gui


def test_lingao_assets_and_predictions():
    portrait = Image.open(ROOT / "rl/assets/portraits/chapter50-lingao.png")
    assert portrait.size == (256, 256)
    anim = ROOT / "rl/assets/unit_anim/lingao"
    files = list(anim.glob("*.png"))
    assert len(files) == 36
    for path in files:
        image = Image.open(path).convert("RGBA")
        assert image.size == (64, 64)
        alpha = Counter(image.getchannel("A").get_flattened_data())
        assert alpha[0] > 200 and sum(count for value, count in alpha.items() if value > 0) > 100

    for name in ("m078_ch50_prediction.json", "m079_ch50_prediction.json", "m080_ch50_prediction.json"):
        report = json.loads((ROOT / "output/terrain_model" / name).read_text(encoding="utf-8"))
        assert report["auto_apply"] is False and report["threshold"] >= 0.72


if __name__ == "__main__":
    test_map_contracts()
    test_story_and_logic()
    test_lingao_assets_and_predictions()
    print("chapter50 regression checks passed")
