from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageStat
import generate_chapter43_maps as common
import generate_chapter47_maps as natural
ROOT=Path(__file__).resolve().parents[1];CELL=48

def rows(w,h,mode):
 out=[]
 for y in range(h):
  row=[]
  for x in range(w):
   b=min(x,w-1-x,y,h-1-y)
   if mode=="xinzhu":
    if abs(y-16)<=1:t="w"
    elif b<=2 and(x+y*2)%4<2:t="F"
    elif x>=38 and y<=8:t="m"
    else:t="g"if(x*2+y)%8<2 else"f"
   else:
    mountain=36<=x<=49 and 4<=y<=20
    if mountain:t="r"if(x+y)%5<2 else"m"
    elif 42<=x<=46 and 21<=y<=24:t="w"
    elif abs(y-(20-x//14))<=1:t="w"
    elif b<=2 and(x+y*3)%5<2:t="F"
    elif y>=29 and(x*2+y)%4<2:t="F"
    else:t="g"if(x+y*2)%9<2 else"f"
   row.append(t)
  out.append(row)
 return out
def place(r,c,t):
 for x,y in c:r[y][x]=t
def render(src,r):return natural.natural_overlay(natural.cover_resize(Image.open(ROOT/"output/imagegen"/src).convert("RGB"),(len(r[0])*CELL,len(r)*CELL)),r)
def save(mid,suf,src,prompt,im,r,dep,mission,fences=set(),gates=set(),regions=None):
 data={"map":f"assets/lzc/map/{mid}.png","source_base":f"output/imagegen/{src}","prompt_file":f"output/imagegen/{prompt}","grid":[len(r[0]),len(r)],"cell_pixels":CELL,"terrain_rows":["".join(x)for x in r],"terrain_protocol":{"version":2,"blendable":["f","g","F","w","m"],"structure_mixing":False},"terrain_layers":[],"terrain_source":"GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry","structure_regions":regions or{},"camp_icon_cells":[],"camp_cells":[],"fence_cells":[list(x)for x in sorted(fences)],"fence_geometry":"impassable cell center-axis; corners use two half-axis segments"if fences else"no fences","wall_cells":[],"gates":[{"name":"xinzhu_camp_east_gate","cells":[list(x)for x in sorted(gates)]}]if gates else[],"castle_cells":[],"supply_sites":[],"blocked_edges":[],"deployments":dep,"mission":mission,"visual_grid_in_game":False}
 im.convert("RGB").save(ROOT/f"assets/lzc/map/{mid}.png","PNG",compress_level=3);(ROOT/f"assets/lzc/map_sources/{mid}_{suf}_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 common.review_image(im,r,{"walls":set(),"fences":fences,"gates":gates,"sites":set()},dep,ROOT/f"output/terrain_model/{mid}_{suf}_review.png")
 pred={"map":data["map"],"grid":data["grid"],"backend":"reviewed-contract-with-dinov3-evidence-slot","threshold":.72,"auto_apply":False,"review_required":[],"note":"Classifier evidence cannot overwrite reviewed barriers or Lua terrain."};(ROOT/f"output/terrain_model/{mid}_{suf}_prediction.json").write_text(json.dumps(pred,ensure_ascii=False,indent=2),encoding="utf-8")
 st=ImageStat.Stat(im.convert("RGB"));assert im.size==(len(r[0])*CELL,len(r)*CELL)and max(st.var)>100;print(mid,data["grid"],im.size)
def xinzhu():
 w,h=48,32;r=rows(w,h,"xinzhu");bounds=(14,7,32,25);g={(32,15),(32,16)};f=common.rectangle_perimeter(*bounds)-g;place(r,f,"P")
 dep=[{"name":"SunLiangFu56","force":1,"position":[23,16]},{"name":"ShiJi56","force":2,"position":[42,13]},{"name":"GuoZuo56","force":3,"position":[10,12]},{"name":"GaoGu56","force":3,"position":[10,21]}]
 im=render("chapter56-xinzhu-base-gpt2.png",r);common.draw_fences(im,f,bounds)
 save("m089","ch56a","chapter56-xinzhu-base-gpt2.png","m089_prompt.txt",im,r,dep,{"type":"xinzhu_night_raid_escape","escape":[44,16],"relief_turn":3},f,g,{"empty_qi_camp":[[14,7],[32,25]]})
def anbattle():
 w,h=60,38;r=rows(w,h,"an");dep=[{"name":"XiKe56","force":1,"position":[10,19]},{"name":"HanJue48","force":1,"position":[12,16]},{"name":"QiQingGong56","force":3,"position":[48,19]},{"name":"FengChouFu56","force":3,"position":[46,21]}]
 im=render("chapter56-an-base-gpt2.png",r);save("m090","ch56b","chapter56-an-base-gpt2.png","m090_prompt.txt",im,r,dep,{"type":"battle_of_an","canonical_name":"鞌之战","mount_huabuzhu":[[36,4],[49,20]],"victory":"defeat FengChouFu56 after encirclement","QiQingGong56":"escapes_alive"})
def main():
 for p in(ROOT/"assets/lzc/map",ROOT/"assets/lzc/map_sources",ROOT/"output/terrain_model"):p.mkdir(parents=True,exist_ok=True)
 xinzhu();anbattle()
if __name__=="__main__":main()
