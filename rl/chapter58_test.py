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


def reachable(rows, start, goals):
    goals = {tuple(p) for p in goals}
    queue = deque([tuple(start)])
    seen = {tuple(start)}
    while queue:
        point = queue.popleft()
        if point in goals:
            return True
        x, y = point
        for nxt in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if nxt not in seen and passable(rows, nxt):
                seen.add(nxt); queue.append(nxt)
    return False


def lua_rows(text):
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))


def test_map_contract():
    stage = (ROOT / "game/sce/dongzhou/stage/58.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m092_ch58_manifest.json").read_text(encoding="utf-8"))
    rows = manifest["terrain_rows"]
    assert manifest["grid"] == [64, 44]
    assert len(rows) == 44 and all(len(row) == 64 for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / manifest["map"]).size == (3072, 2112)
    assert manifest["visual_grid_in_game"] is False
    fences = {tuple(p) for p in manifest["fence_cells"]}
    matrix_fences = {(x,y) for y,row in enumerate(rows) for x,t in enumerate(row) if t == "P"}
    assert fences == matrix_fences and len(fences) == 224
    camps = {tuple(p) for p in manifest["camp_cells"]}
    assert camps == {tuple(p) for p in manifest["camp_icon_cells"]}
    assert camps == {tuple(p) for p in manifest["supply_sites"]} and len(camps) == 6
    gates = {tuple(p) for gate in manifest["gates"] for p in gate["cells"]}
    assert len(gates) == 18 and not (gates & fences)
    assert all(passable(rows, p) for p in gates)
    for camp in camps:
        assert reachable(rows, camp, gates)
    for item in manifest["deployments"]:
        assert passable(rows, item["position"]), item
    assert any("w" in row for row in rows)
    prediction = json.loads((ROOT / "output/terrain_model/m092_ch58_prediction.json").read_text(encoding="utf-8"))
    assert prediction["auto_apply"] is False


def test_stage_rules_and_story():
    stage = (ROOT / "game/sce/dongzhou/stage/58.lua").read_text(encoding="utf-8")
    assert 'battle_title="鄢陵交锋"' in stage
    assert 'gcommanders={"JinLiGong58","LuanShu58","ShiXie58","HanJue48","WeiQi54"' in stage
    assert 'required_commanders={"JinLiGong58","LuanShu58","ShiXie58","HanJue48","LuanZhen58"' in stage
    assert 'set_unit_invulnerable("WeiQi54",true)' in stage
    assert 'set_unit_invulnerable("WeiQi54",false)' in stage
    assert 'not game:has_unit("XiongFa58")' in stage
    assert 'is_unit_within("WeiQi54",{32,36},3)' in stage
    assert 'not game:has_unit("WeiQi54")' in stage
    assert 'wei_fallen_turn=game:get_turn_current()' in stage
    assert 'game:get_turn_current()>=wei_fallen_turn+1' in stage
    assert 'if chu_retreat then return Enum.status.victory end' in stage
    assert 'speaker="旁白"' not in stage
    assert stage.count('{speaker=') >= 42
    for topic in ("魏相", "高缓", "膏肓", "新麦", "西门", "伯宗", "平灶填井", "百步穿杨", "熊茷", "左眼", "养一箭", "椒汤", "连夜拔营", "自缢"):
        assert topic in stage
    assert stage.index('not game:has_unit("XiongFa58")') < stage.index('xiongfa_captured and not king_wounded') < stage.index('king_wounded and not wei_fallen')


def test_config_and_gui():
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '"56a", "56b", "57", "58", "59a", "59b" }' in config
    for hero in ("JinLiGong58","LuanShu58","ShiXie58","LuanZhen58","XiZhi58","XiQi58","XunYan58","ChuGongWang58","GongZiRenFu58","XiongFa58","PanDang58","GongYinXiang58"):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui
    assert '_LARGE_BATTLE_MAPS["m092.png"] = (64, 44, 48)' in gui
    assert 'HISTORICAL_DEATH_HEROES.add("WeiQi54")' in gui
    assert config.count('id = "WeiQi54"') == 1
    assert config.count('id = "YangYouJi51"') == 1


if __name__ == "__main__":
    test_map_contract()
    test_stage_rules_and_story()
    test_config_and_gui()
    print("chapter58 regression checks passed")