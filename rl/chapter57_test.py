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


def lua_rows(text):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"', block.group(1))


def test_map_contract_and_route():
    stage = (ROOT / "game/sce/dongzhou/stage/57.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m091_ch57_manifest.json").read_text(encoding="utf-8"))
    rows = manifest["terrain_rows"]
    assert manifest["grid"] == [48, 32]
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / manifest["map"]).size == (2304, 1536)
    assert manifest["visual_grid_in_game"] is False
    assert manifest["camp_cells"] == [] and manifest["supply_sites"] == []
    walls = {tuple(cell) for cell in manifest["wall_cells"]}
    matrix_walls = {(x, y) for y, row in enumerate(rows) for x, tile in enumerate(row) if tile == "W"}
    assert walls == matrix_walls and len(walls) == 118
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    assert gates == {(39, 15), (39, 16)}
    assert all(passable(rows, p) for p in gates)
    assert reachable(rows, (10, 16), (44, 15))
    for item in manifest["deployments"]:
        assert passable(rows, item["position"]), item
    prediction = json.loads((ROOT / "output/terrain_model/m091_ch57_prediction.json").read_text(encoding="utf-8"))
    assert prediction["auto_apply"] is False


def test_stage_rules():
    stage = (ROOT / "game/sce/dongzhou/stage/57.lua").read_text(encoding="utf-8")
    assert 'gcommanders={"PalaceDoctor57","HanJue48"}' in stage
    assert 'set_unit_invulnerable("TuAnGu50",true)' in stage
    assert 'is_unit_within("PalaceDoctor57",{44,15},1)' in stage
    assert 'get_num_commanders_alive()<#gcommanders' in stage
    assert 'battle_title="藏孤出宫"' in stage
    assert stage.index("我已备好药囊") < stage.index("真孤脱宫之后")
    assert 'id="medicine_bag_check"' in stage
    assert 'id="east_gate"' in stage
    assert 'id="handoff"' in stage
    assert "medicine_bag_warning" in stage and "handoff_warning" in stage
    assert 'speaker="旁白"' not in stage
    assert stage.count("{speaker=") >= 45
    for topic in ("袁娄", "萧同叔子", "申公巫臣", "吴人车战", "下宫", "赵武", "首阳山", "盂山", "新绛"):
        assert topic in stage


def test_config_and_gui_metadata():
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '"55a", "55b", "56a", "56b", "57" }' in config
    assert config.count('id = "HanJue48"') == 1
    assert config.count('id = "TuAnGu50"') == 1
    for hero in ("PalaceDoctor57", "PalaceSearchGuard57", "PalaceSearchArcher57"):
        assert f'id = "{hero}"' in config
        assert f'"{hero}"' in gui
    assert '_LARGE_BATTLE_MAPS["m091.png"] = (48, 32, 48)' in gui
    death_lines = "\n".join(line for line in gui.splitlines() if "HISTORICAL_DEATH_HEROES" in line)
    assert "PalaceDoctor57" not in death_lines
    assert "PalaceSearchGuard57" not in death_lines
    assert "TuAnGu50" not in death_lines


if __name__ == "__main__":
    test_map_contract_and_route()
    test_stage_rules()
    test_config_and_gui_metadata()
    print("chapter57 regression checks passed")
