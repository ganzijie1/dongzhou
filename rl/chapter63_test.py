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
    wall_matrix={(x,y) for y,row in enumerate(d["terrain_rows"]) for x,t in enumerate(row) if t=="W"}
    assert wall_matrix=={tuple(p) for p in d["wall_cells"]}
    for unit in d["deployments"]:
        x,y=unit["position"];assert d["terrain_rows"][y][x] not in BLOCKED,unit
    return d


def main():
    jiang=contract("m104","ch63a","63a",[74,52]);quwo=contract("m105","ch63b","63b",[58,42])
    assert reachable(jiang["terrain_rows"],(19,12),{(56,35),(57,35),(56,8),(57,8)})
    assert reachable(jiang["terrain_rows"],(36,39),{(56,35),(57,35)})
    assert reachable(quwo["terrain_rows"],(53,17),{(48,18),(48,19)})
    assert reachable(quwo["terrain_rows"],(28,10),{(28,34),(29,34),(48,18),(48,19)})
    a=(ROOT/"game/sce/dongzhou/stage/63a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/63b.lua").read_text(encoding="utf-8")
    assert 'battle_title="固宫保卫战"' in a and 'game:is_unit_within("WeiShu63",{57,16},8)' in a
    assert 'set_unit_invulnerable("DuRong63",false)' in a and 'not game:has_unit("LuanLe63")' in a
    assert 'battle_title="曲沃灭栾"' in b and 'set_unit_invulnerable("LuanFang63",true)' in b
    assert 'not game:has_unit("XuWu63") and not game:has_unit("LuanRong63")' in b
    for text in (a,b):assert 'speaker="旁白"' not in text and text.count('speaker=')>=16
    config=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");gui=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
    start=CURRENT_DONGZHOU_STAGES.index("62a")
    assert CURRENT_DONGZHOU_STAGES[start:start+5]==("62a","62b","62c","63a","63b") and STAGE_TABLE_VERSION>=7
    assert '"62c", "63a", "63b", "64a"' in config
    for hero in ("WeiShu63","DuRong63","LuanLe63","LuanFang63","XuWu63","FeiBao63"):
        assert config.count(f'id = "{hero}"')==1 and f'"{hero}"' in gui
    with MengdeEnv(EXE,scenario="dongzhou",max_units=999,interactive=True) as env:
        env.reset()
        for sid,asset in (("63a","m104.png"),("63b","m105.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid));assert env.story_info()["map_asset"]==asset
            assert not any(u["terrain"] in {"Wall","RockyMountain","Water","Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 63 ok: Gugong defense, Quwo siege, maps, phases, and save table")


if __name__=="__main__":main()
