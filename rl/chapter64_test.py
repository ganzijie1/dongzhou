from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re

from PIL import Image,ImageStat

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES,STAGE_TABLE_VERSION


ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/"build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED={"r","W","~","P"}


def rows(text):
    block=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",text,re.S);assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"',block.group(1))


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
    stage=(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8")
    d=json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    assert d["grid"]==grid and rows(stage)==d["terrain_rows"]
    assert Image.open(ROOT/d["map"]).size==(grid[0]*48,grid[1]*48)
    for u in d["deployments"]:
        x,y=u["position"];assert d["terrain_rows"][y][x] not in BLOCKED,u
    assert {(x,y) for y,row in enumerate(d["terrain_rows"]) for x,t in enumerate(row) if t=="W"}=={tuple(p) for p in d["wall_cells"]}
    return d


def main():
    retreat=contract("m106","ch64a","64a",[60,40]);qieyu=contract("m107","ch64b","64b",[68,46])
    assert reachable(retreat["terrain_rows"],(19,19),{(58,20)})
    assert reachable(qieyu["terrain_rows"],(12,21),{(46,22),(46,23)})
    assert reachable(qieyu["terrain_rows"],(46,22),{(52,22),(52,23)})
    fire={tuple(p) for p in qieyu["fire_trench_cells"]};cross={(46,22),(46,23)}
    assert fire=={(46,y) for y in range(18,28)}-cross
    assert all(qieyu["terrain_rows"][y][x]=="~" for x,y in fire)
    assert all(qieyu["terrain_rows"][y][x]=="G" for x,y in cross)
    texture=Image.open(ROOT/qieyu["fire_texture"]).convert("RGB")
    assert texture.width>=1024 and texture.height>=512 and max(ImageStat.Stat(texture).var)>100
    a=(ROOT/"game/sce/dongzhou/stage/64a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/64b.lua").read_text(encoding="utf-8")
    assert 'battle_title="少水断后"' in a and 'is_unit_within("QiZhuangGong62",{58,20},1)' in a
    assert 'battle_title="且于门死战"' in b and 'is_unit_within("XiHouZhong64",{46,22},1)' in b
    assert 'not game:has_unit("JuGateCaptain64")' in b
    for text in (a,b):assert 'speaker="旁白"' not in text and text.count("speaker=")>=15
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");gui=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
    start=CURRENT_DONGZHOU_STAGES.index("63a")
    assert CURRENT_DONGZHOU_STAGES[start:start+4]==("63a","63b","64a","64b") and STAGE_TABLE_VERSION>=8
    assert '"63b", "64a", "64b", "65a"' in config
    for hero in ("WangSunHui64","YanMao64","ZhaoSheng64","HuaZhou64","QiLiang64","XiHouZhong64","JuLiBiGong64"):
        assert config.count(f'id = "{hero}"')==1 and f'"{hero}"' in gui
    with MengdeEnv(EXE,scenario="dongzhou",max_units=999,interactive=True) as env:
        env.reset()
        for sid,asset in (("64a","m106.png"),("64b","m107.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid));assert env.story_info()["map_asset"]==asset
            assert not any(u["terrain"] in {"Wall","RockyMountain","Water","Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 64 ok: Shaoshui retreat, Qieyu fire trench, maps, phases, and save table")


if __name__=="__main__":main()
