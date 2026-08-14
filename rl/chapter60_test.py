from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re

from PIL import Image

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED = {"r", "W", "~", "P"}

def lua_rows(text: str) -> list[str]:
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))

def reachable(rows: list[str], start: tuple[int, int], goals: set[tuple[int, int]]) -> bool:
    queue = deque([start]); seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals: return True
        for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            px, py = point
            if point not in seen and 0 <= py < len(rows) and 0 <= px < len(rows[0]) and rows[py][px] not in BLOCKED:
                seen.add(point); queue.append(point)
    return False

def contract(map_id: str, suffix: str, stage_id: str, grid: list[int]) -> dict:
    stage = (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").read_text(encoding="utf-8")
    data = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    assert data["grid"] == grid and lua_rows(stage) == data["terrain_rows"]
    assert Image.open(ROOT / data["map"]).size == (grid[0] * 48, grid[1] * 48)
    assert data["visual_grid_in_game"] is False and data["fence_cells"] == [] and data["blocked_edges"] == []
    for unit in data["deployments"]:
        x, y = unit["position"]
        assert data["terrain_rows"][y][x] not in BLOCKED, unit
    prediction = json.loads((ROOT / f"output/terrain_model/{map_id}_{suffix}_prediction.json").read_text(encoding="utf-8"))
    assert prediction["auto_apply"] is False
    return data

def main() -> None:
    peng = contract("m095", "ch60a", "60a", [54, 38])
    cai = contract("m096", "ch60b", "60b", [62, 40])
    biy = contract("m097", "ch60c", "60c", [56, 42])
    for data in (peng, cai, biy):
        rows = data["terrain_rows"]
        assert {(x,y) for y,row in enumerate(rows) for x,t in enumerate(row) if t == "W"} == {tuple(p) for p in data["wall_cells"]}
        for gate in data["gates"]: assert all(rows[y][x] == "G" for x,y in gate["cells"])
    assert reachable(peng["terrain_rows"], (24,33), {(26,27),(27,27)})
    assert reachable(peng["terrain_rows"], (26,9), {(26,27),(27,27)})
    assert reachable(cai["terrain_rows"], (18,12), {(55,20)})
    assert "~" in "".join(cai["terrain_rows"]) and "v" in "".join(cai["terrain_rows"])
    assert reachable(biy["terrain_rows"], (24,3), {(27,7),(28,7)})
    assert reachable(biy["terrain_rows"], (27,25), {(27,7),(28,7)})

    a = (ROOT / "game/sce/dongzhou/stage/60a.lua").read_text(encoding="utf-8")
    b = (ROOT / "game/sce/dongzhou/stage/60b.lua").read_text(encoding="utf-8")
    c = (ROOT / "game/sce/dongzhou/stage/60c.lua").read_text(encoding="utf-8")
    assert 'battle_title="彭城复宋"' in a and 'battle_title="采石水战"' in b and 'battle_title="偪阳之战"' in c
    assert 'set_unit_invulnerable(h,true)' in a and 'set_unit_invulnerable(h,false)' in a
    assert 'is_unit_within("DengLiao60",{28,20},2)' in b and 'generate_unit("YuJi60"' in b
    assert b.index('is_unit_within("DengLiao60"') < b.index('not game:has_unit("DengLiao60")')
    assert 'game:get_turn_current()>=6' in c and 'assault_turn+5' in c
    assert 'set_unit_invulnerable("BiYangLord60",true)' in c and 'set_unit_invulnerable("YunBan60",false)' in c
    assert "第六十一回开端" in c and "云般阵亡" in c
    for text in (a,b,c):
        assert 'speaker="旁白"' not in text and "gally_hold_position=true" in text and text.count('{speaker=') >= 16

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-10:] == ("57","58","59a","59b","60a","60b","60c","61a","61b","61c") and STAGE_TABLE_VERSION == 5
    assert '"59a", "59b", "60a", "60b", "60c", "61a", "61b", "61c" }' in config
    for hero in ("JinDaoGong60","LuanYan60","XiangShu60","ZhongSunMie60","YuShi60","ZhuFan60","YiMei60","YuJi60","DengLiao60","ShiGai60","ShuLiangHe60","QinJinFu60","DiSiMi60","YunBan60","BiYangLord60"):
        assert config.count(f'id = "{hero}"') == 1 and f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for stage_id, asset in (("60a","m095.png"),("60b","m096.png"),("60c","m097.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(stage_id))
            assert env.story_info()["map_asset"] == asset
            assert not any(u["terrain"] in {"Wall","RockyMountain","Water","Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 60 ok: Pengcheng capture, Caishi ambush, merged Biyang assault, maps, story, and save table")

if __name__ == "__main__": main()
