from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re

from PIL import Image

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION

ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/"build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED={"r","W","~","P"}

def lua_rows(text):
    block=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",text,re.S);assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"',block.group(1))

def reachable(rows,start,goals):
    q=deque([start]);seen={start}
    while q:
        x,y=q.popleft()
        if (x,y) in goals:return True
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            px,py=p
            if p not in seen and 0<=py<len(rows) and 0<=px<len(rows[0]) and rows[py][px] not in BLOCKED:
                seen.add(p);q.append(p)
    return False

def contract(mid,suffix,sid,grid):
    stage=(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8")
    d=json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    assert d["grid"]==grid and lua_rows(stage)==d["terrain_rows"]
    assert Image.open(ROOT/d["map"]).size==(grid[0]*48,grid[1]*48)
    for u in d["deployments"]:
        x,y=u["position"];assert d["terrain_rows"][y][x] not in BLOCKED,u
    return d

def main():
    z=contract("m098","ch61a","61a",[50,34]); y=contract("m099","ch61b","61b",[62,40]); w=contract("m100","ch61c","61c",[64,38])
    assert reachable(z["terrain_rows"],(21,30),{(24,27),(25,27)}) and reachable(z["terrain_rows"],(24,10),{(24,27),(25,27)})
    fences={tuple(p) for p in y["fence_cells"]}; matrix={(x,yy) for yy,row in enumerate(y["terrain_rows"]) for x,t in enumerate(row) if t=="P"}
    assert fences==matrix and fences
    gates={tuple(p) for g in y["gates"] for p in g["cells"]}; assert gates=={(42,19),(42,20)} and not gates&fences
    assert reachable(y["terrain_rows"],(31,18),gates) and reachable(y["terrain_rows"],(50,18),gates)
    assert all(y["terrain_rows"][yy][x] in {"v","~"} for yy in range(40) for x in range(19,25))
    assert reachable(w["terrain_rows"],(18,17),{(62,18)})
    a=(ROOT/"game/sce/dongzhou/stage/61a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/61b.lua").read_text(encoding="utf-8");c=(ROOT/"game/sce/dongzhou/stage/61c.lua").read_text(encoding="utf-8")
    assert 'battle_title="郑宫平乱"' in a and 'battle_title="棫林突秦"' in b and 'battle_title="卫侯出奔"' in c
    assert 'not game:has_unit("LuanZhen58")' in b and 'is_unit_within("FanYang61",{16,19},2)' in b
    assert 'generate_unit("YinGongTuo61"' in c and 'not game:has_unit("YinGongTuo61")' in c and "第六十二回开端" in c
    for text in (a,b,c):assert 'speaker="旁白"' not in text and text.count('{speaker=')>=16
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");gui=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
    start=CURRENT_DONGZHOU_STAGES.index("60a")
    assert CURRENT_DONGZHOU_STAGES[start:start+6]==("60a","60b","60c","61a","61b","61c") and STAGE_TABLE_VERSION>=5
    assert '"61a", "61b", "61c", "62a"' in config
    for hero in ("GongSunXia61","ZiChan61","GongSunChai61","WeiZhi61","FanYang61","QinJingGong61","WeiXianGong61","GongSunDing61","YinGongTuo61"):
        assert config.count(f'id = "{hero}"')==1 and f'"{hero}"' in gui
    with MengdeEnv(EXE,scenario="dongzhou",max_units=999,interactive=True) as env:
        env.reset()
        for sid,asset in (("61a","m098.png"),("61b","m099.png"),("61c","m100.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid));assert env.story_info()["map_asset"]==asset
            assert not any(u["terrain"] in {"Wall","RockyMountain","Water","Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 61 ok: Zheng revolt, Yulin last charge, Wei escape, maps, events, and save table")

if __name__=="__main__":main()
