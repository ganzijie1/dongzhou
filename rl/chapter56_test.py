from collections import deque
from pathlib import Path
import json,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BLOCKED={"r","W","~","P"}
def pas(r,p):x,y=p;return 0<=y<len(r)and 0<=x<len(r[0])and r[y][x]not in BLOCKED
def reach(r,a,b):
 q=deque([tuple(a)]);s={tuple(a)}
 while q:
  x,y=q.popleft()
  if(x,y)==tuple(b):return True
  for n in((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
   if n not in s and pas(r,n):s.add(n);q.append(n)
 return False
def lr(s):b=re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file",s,re.S);assert b;return re.findall(r'"([fgFwmrW~cbeGDPihC]+)"',b.group(1))
def pts(s):
 p=[(int(x),int(y))for x,y in re.findall(r"position\s*=\s*\{(\d+),(\d+)\}",s)]
 for b in re.findall(r"many\(game,[^\n]+\{\{(.*?)\}\},",s):p +=[(int(x),int(y))for x,y in re.findall(r"(\d+),(\d+)",b)]
 return p
def chk(sid,mn,g,pix):
 s=(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8");d=json.loads((ROOT/f"assets/lzc/map_sources/{mn}").read_text(encoding="utf-8"));r=d["terrain_rows"]
 assert d["grid"]==g and lr(s)==r and Image.open(ROOT/d["map"]).size==pix and d["visual_grid_in_game"]is False
 for p in pts(s):assert pas(r,p),p
 pr=json.loads((ROOT/f"output/terrain_model/{mn.replace('_manifest.json','_prediction.json')}").read_text(encoding="utf-8"));assert pr["auto_apply"]is False
 return s,d,r
def test_xinzhu():
 s,d,r=chk("56a","m089_ch56a_manifest.json",[48,32],(2304,1536));f={tuple(x)for x in d["fence_cells"]};assert f=={(x,y)for y,z in enumerate(r)for x,t in enumerate(z)if t=="P"};assert reach(r,(23,16),(45,16))
 assert 'get_turn_current()>=3'in s and 'ZhongShuYuXi56' in s
def test_an():
 s,d,r=chk("56b","m090_ch56b_manifest.json",[60,38],(2880,1824));assert reach(r,(10,19),(42,23))and not pas(r,(40,10));assert 'battle_title="鞌之战"'in s and 'battle_title="鞍之战"'not in s
 assert 'set_unit_invulnerable("QiQingGong56",true)'in s and 'not game:has_unit("FengChouFu56")'in s
def test_story():
 a=(ROOT/"game/sce/dongzhou/stage/56a.lua").read_text(encoding="utf-8");b=(ROOT/"game/sce/dongzhou/stage/56b.lua").read_text(encoding="utf-8");c=(ROOT/"game/sce/dongzhou/config.lua").read_text(encoding="utf-8");g=(ROOT/"rl/play_gui.py").read_text(encoding="utf-8")
 assert '"55a", "55b", "56a", "56b", "57" }'in c and a.count("{speaker=")+b.count("{speaker=")>=35 and 'speaker="旁白"'not in a+b
 for t in("郤雍","士会","萧夫人","龙邑","新筑","八百乘","鞌之战","华不注","逢丑父"):assert t in a+b
 deaths="\n".join(x for x in g.splitlines()if"HISTORICAL_DEATH_HEROES"in x);assert"QiQingGong56"not in deaths and"FengChouFu56"not in deaths
 assert c.count('id = "HanJue48"')==1
if __name__=="__main__":test_xinzhu();test_an();test_story();print("chapter56 regression checks passed")
