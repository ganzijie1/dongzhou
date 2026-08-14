from collections import deque
from pathlib import Path
import json, re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"r","W","~","P"}

def passable(rows,p):
    x,y=p; return 0<=y<len(rows) and 0<=x<len(rows[0]) and rows[y][x] not in BLOCKED

def reachable(rows,start,goal):
    q=deque([tuple(start)]); seen={tuple(start)}
    while q:
        x,y=q.popleft()
        if (x,y)==tuple(goal): return True
        for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if n not in seen and passable(rows,n): seen.add(n); q.append(n)
    return False

def lua_rows(text):
    b=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",text,re.S); assert b
    return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"',b.group(1))

def positions(text):
    pts=[(int(x),int(y)) for x,y in re.findall(r"position\s*=\s*\{(\d+),(\d+)\}",text)]
    for b in re.findall(r"many\(game,[^\n]+\{\{(.*?)\}\},",text): pts += [(int(x),int(y)) for x,y in re.findall(r"(\d+),(\d+)",b)]
    return pts

def check(stage_id,manifest_name,grid,pixels):
    stage=(ROOT/f"game/sce/dongzhou/stage/{stage_id}.lua").read_text(encoding="utf-8")
    data=json.loads((ROOT/f"assets/lzc/map_sources/{manifest_name}").read_text(encoding="utf-8")); rows=data["terrain_rows"]
    assert data["grid"]==grid and len(rows)==grid[1] and all(len(r)==grid[0] for r in rows)
    assert lua_rows(stage)==rows and Image.open(ROOT/data["map"]).size==pixels and data["visual_grid_in_game"] is False
    for p in positions(stage): assert passable(rows,p),p
    report=json.loads((ROOT/f"output/terrain_model/{manifest_name.replace('_manifest.json','_prediction.json')}").read_text(encoding="utf-8"))
    assert report["auto_apply"] is False and report["threshold"]>=.72
    return stage,data,rows

def test_main_battle():
    s,d,r=check("54a","m085_ch54a_manifest.json",[58,36],(2784,1728))
    assert reachable(r,(48,18),(25,18)) and 'battle_title = "邲之战"' in s
    assert 'not game:has_unit("JinCenterGuard54")' in s and 'not game:has_unit("XunYing54")' in s
    assert 'set_unit_invulnerable("XunLinFu47",true)' in s and 'set_unit_invulnerable("ShiHui47",true)' in s

def test_counterattack():
    s,d,r=check("54b","m086_ch54b_manifest.json",[52,34],(2496,1632))
    assert all(r[y][x]=="~" for y in range(4,7) for x in range(47))
    assert all(passable(r,(x,y)) for y in range(4,7) for x in range(47,52))
    assert reachable(r,(44,9),(24,20)) and reachable(r,(24,20),(48,8))
    assert 'attacker = "XunShou54", defender = "XiangLao54"' in s and 'outcome = "kill"' in s
    assert 'not game:has_unit("GongZiGuChen54")' in s

def test_story_and_history():
    a=(ROOT/"game/sce/dongzhou/stage/54a.lua").read_text(encoding="utf-8"); b=(ROOT/"game/sce/dongzhou/stage/54b.lua").read_text(encoding="utf-8")
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8"); gui=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
    assert '"53a", "53b", "54a", "54b", "55a", "55b" }' in config and a.count("{ speaker =")+b.count("{ speaker =")>=45
    assert 'speaker = "旁白"' not in a+b
    for t in ("六百乘","乐伯","赵旃","荀罃","黄河","襄老","京观","先谷","孙叔敖","优孟","寝邱"): assert t in a+b
    deaths="\n".join(x for x in gui.splitlines() if "HISTORICAL_DEATH_HEROES" in x)
    assert "XiangLao54" in deaths and "GongZiGuChen54" not in deaths and "XunYing54" not in deaths
    for h in ("ChuZhuangWang51","GongZiYingQi51","GongZiCe51","LeBo51","YangYouJi51","XunLinFu47","ShiHui47"): assert config.count(f'id = "{h}"')==1
    assert '_LARGE_BATTLE_MAPS["m085.png"] = (58, 36, 48)' in gui and '_LARGE_BATTLE_MAPS["m086.png"] = (52, 34, 48)' in gui

if __name__=="__main__": test_main_battle(); test_counterattack(); test_story_and_history(); print("chapter54 regression checks passed")
