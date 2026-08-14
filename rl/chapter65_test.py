from __future__ import annotations
from collections import deque
import json,re
from pathlib import Path
from PIL import Image
from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES,STAGE_TABLE_VERSION

ROOT=Path(__file__).resolve().parents[1];EXE=ROOT/"build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe";BLOCKED={"r","W","~","P"}
def rows(text):
    b=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",text,re.S);assert b;return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"',b.group(1))
def reachable(matrix,start,goals):
    q=deque([start]);seen={start}
    while q:
        x,y=q.popleft()
        if (x,y) in goals:return True
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            px,py=p
            if p not in seen and 0<=py<len(matrix) and 0<=px<len(matrix[0]) and matrix[py][px] not in BLOCKED:seen.add(p);q.append(p)
    return False
def contract(mid,suffix,sid,grid):
    stage=(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8");d=json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    assert d["grid"]==grid and rows(stage)==d["terrain_rows"] and Image.open(ROOT/d["map"]).size==(grid[0]*48,grid[1]*48)
    assert {(x,y) for y,row in enumerate(d["terrain_rows"]) for x,t in enumerate(row) if t=="W"}=={tuple(p) for p in d["wall_cells"]}
    for u in d["deployments"]:
        x,y=u["position"];assert d["terrain_rows"][y][x] not in BLOCKED,u
    return d
def main():
    manor=contract("m108","ch65a","65a",[50,38]);chao=contract("m109","ch65b","65b",[52,36]);diqiu=contract("m110","ch65c","65c",[70,48])
    assert reachable(manor["terrain_rows"],(24,9),{(24,17),(25,17)}) and reachable(manor["terrain_rows"],(24,22),{(24,32),(25,32)})
    assert reachable(chao["terrain_rows"],(30,16),{(28,17),(28,18)}) and reachable(chao["terrain_rows"],(22,17),{(34,17),(34,18)})
    assert reachable(diqiu["terrain_rows"],(35,19),{(30,21),(30,22)}) and reachable(diqiu["terrain_rows"],(35,19),{(45,22),(45,23)})
    a=(ROOT/"game/sce/dongzhou/stage/65a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/65b.lua").read_text(encoding="utf-8");c=(ROOT/"game/sce/dongzhou/stage/65c.lua").read_text(encoding="utf-8")
    assert 'battle_title="崔府之变"' in a and '"QiZhuangGong62","JiaJu65","ZhouChuoQi65"' in a
    assert 'battle_title="巢门伏射"' in b and 'not game:has_unit("ZhuFan60")' in b
    assert 'battle_title="帝丘复君"' in c and 'set_unit_invulnerable("YongChu65",true)' in c and 'phase=3' in c
    for text in (a,b,c):assert 'speaker="旁白"' not in text and text.count("speaker=")>=10
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");gui=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
    start=CURRENT_DONGZHOU_STAGES.index("64a")
    assert CURRENT_DONGZHOU_STAGES[start:start+5]==("64a","64b","65a","65b","65c") and STAGE_TABLE_VERSION>=9 and '"65c", "66a"' in config
    for hero in ("TangWuJiu65","ZhouChuoQi65","NiuChen65","NingXi65","SunXiang65","WeiShangGong65"):
        assert config.count(f'id = "{hero}"')==1 and f'"{hero}"' in gui
    with MengdeEnv(EXE,scenario="dongzhou",max_units=999,interactive=True) as env:
        env.reset()
        for sid,asset in (("65a","m108.png"),("65b","m109.png"),("65c","m110.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid));assert env.story_info()["map_asset"]==asset
            assert not any(u["terrain"] in {"Wall","RockyMountain","Water","Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 65 ok: Cui manor, Chao gate, Diqiu restoration, maps, phases, and save table")
if __name__=="__main__":main()
