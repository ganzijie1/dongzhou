from collections import deque
from pathlib import Path
import json,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BLOCKED={"r","W","~","P"}
def passable(r,p):x,y=p;return 0<=y<len(r)and 0<=x<len(r[0])and r[y][x]not in BLOCKED
def reach(r,a,b):
 q=deque([tuple(a)]);s={tuple(a)}
 while q:
  x,y=q.popleft()
  if(x,y)==tuple(b):return True
  for n in((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
   if n not in s and passable(r,n):s.add(n);q.append(n)
 return False
def lrows(s):
 b=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",s,re.S);assert b;return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"',b.group(1))
def pts(s):
 p=[(int(x),int(y))for x,y in re.findall(r"position\s*=\s*\{(\d+),(\d+)\}",s)]
 for b in re.findall(r"many\(game,[^\n]+\{\{(.*?)\}\},",s):p +=[(int(x),int(y))for x,y in re.findall(r"(\d+),(\d+)",b)]
 return p
def check(sid,mname,grid,pixels):
 s=(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8");d=json.loads((ROOT/f"assets/lzc/map_sources/{mname}").read_text(encoding="utf-8"));r=d["terrain_rows"]
 assert d["grid"]==grid and lrows(s)==r and Image.open(ROOT/d["map"]).size==pixels and d["visual_grid_in_game"]is False
 for p in pts(s):assert passable(r,p),p
 pr=json.loads((ROOT/f"output/terrain_model/{mname.replace('_manifest.json','_prediction.json')}").read_text(encoding="utf-8"));assert pr["auto_apply"]is False and pr["threshold"]>=.72
 return s,d,r
def test_suiyang():
 s,d,r=check("55a","m087_ch55a_manifest.json",[54,36],(2592,1728));walls={tuple(x)for x in d["wall_cells"]};assert walls=={(x,y)for y,z in enumerate(r)for x,t in enumerate(z)if t=="W"}
 assert reach(r,(20,18),(31,17)) and 'siege_turn+5' in s and 'set_unit_invulnerable("HuaYuan50",true)' in s
def test_qingcao():
 s,d,r=check("55b","m088_ch55b_manifest.json",[48,32],(2304,1536));assert reach(r,(39,17),(24,18))and reach(r,(8,18),(24,18))
 assert 'set_unit_invulnerable("DuHui55",true)'in s and 'set_unit_invulnerable("DuHui55",false)'in s and 'grass_triggered and not game:has_unit("DuHui55")'in s
def test_story():
 a=(ROOT/"game/sce/dongzhou/stage/55a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/55b.lua").read_text(encoding="utf-8");c=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");g=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
 assert '"54a", "54b", "55a", "55b", "56a", "56b" }'in c and a.count("{speaker=")+b.count("{speaker=")>=40 and 'speaker="旁白"'not in a+b
 for t in("申舟","解扬","九个月","华元","七日","潞国","杜回","青草坡","结草","景钟","郤雍"):assert t in a+b
 deaths="\n".join(x for x in g.splitlines()if"HISTORICAL_DEATH_HEROES"in x);assert"DuHui55"in deaths and"HuaYuan50"not in deaths
 for h in("ChuZhuangWang51","GongZiCe51","HuaYuan50","WeiQi54"):assert c.count(f'id = "{h}"')==1
if __name__=="__main__":test_suiyang();test_qingcao();test_story();print("chapter55 regression checks passed")
