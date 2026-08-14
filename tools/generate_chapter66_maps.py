from __future__ import annotations
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import generate_chapter60_maps as common
import generate_chapter43_maps as structures

ROOT=Path(__file__).resolve().parents[1];CELL=48
def tint(image,bounds,color=(124,104,77,78)):
    x0,y0,x1,y1=bounds;l=Image.new("RGBA",image.size,(0,0,0,0));ImageDraw.Draw(l).rectangle((x0*CELL,y0*CELL,(x1+1)*CELL,(y1+1)*CELL),fill=color);return Image.alpha_composite(image,l.filter(ImageFilter.GaussianBlur(6)))
def yu_village():
    w,h=56,40;rows=common.natural_rows(w,h)
    for y in range(4,36):
        for x in range(28,52):rows[y][x]="F" if (x*5+y*3)%7<4 else "f"
    for y in range(13,27):
        for x in range(35,48):rows[y][x]="f"
    pit={(41,19),(41,20)};source="chapter47-linghu-night-base-gpt2.png";image=common.base_image(source,w,h,rows)
    layer=Image.new("RGBA",image.size,(0,0,0,0));d=ImageDraw.Draw(layer)
    for x,y in pit:d.ellipse((x*CELL+5,y*CELL+6,(x+1)*CELL-5,(y+1)*CELL-4),fill=(55,39,27,190),outline=(106,79,45,230),width=4)
    image=Image.alpha_composite(image,layer.filter(ImageFilter.GaussianBlur(2)))
    dep=[{"name":"SunKuai61","force":1,"position":[46,17]},{"name":"YongChu65","force":1,"position":[31,22]},{"name":"ZhiChuo62","force":3,"position":[17,20]}]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical forest ambush map\nPrimary request: Maoshi western woodland, winding route into Yu village, a low central hill and two concealed pit cells.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI or visible grid.\n"
    common.save_map("m111","ch66a",image,rows,source,prompt,set(),set(),set(),dep,{"yu_village":[[35,13],[47,26]],"forest_ambush":[[28,4],[51,35]],"pit":[[41,19],[41,20]]},{"type":"yu_village_trap","trap":[41,19],"historical_death":"ZhiChuo62"})
    p=ROOT/"assets/lzc/map_sources/m111_ch66a_manifest.json";x=json.loads(p.read_text(encoding="utf-8"));x["trap_cells"]=[[41,19],[41,20]];p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
def ning_manor():
    w,h=50,38;rows=common.natural_rows(w,h);b=(8,4,42,32);g={(24,32),(25,32)};walls=structures.rectangle_perimeter(*b)-g
    for y in range(5,32):
        for x in range(9,42):rows[y][x]="i" if (x+y)%7 else "h"
    sites={(25,10),(17,23)}
    for x,y in walls:rows[y][x]="W"
    for x,y in g:rows[y][x]="G"
    for x,y in sites:rows[y][x]="C"
    source="chapter50-taoyuan-base-gpt2.png";image=tint(common.base_image(source,w,h,rows),b);structures.draw_walls(image,walls,b);structures.draw_sites(image,sites)
    dep=[{"name":"GongSunMianYu66","force":1,"position":[24,35]},{"name":"NingXi65","force":3,"position":[25,10]},{"name":"YouZaiGu65","force":3,"position":[17,23]}]
    common.save_map("m112","ch66b",image,rows,source,"Use case: historical-scene\nAsset type: Mengde tactical manor assault\nPrimary request: continuous-walled Ning clan manor with a two-cell south gate, banquet hall and inner court.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI or visible grid.\n",walls,g,sites,dep,{"ning_manor":[[8,4],[42,32]],"south_gate":[[24,32],[25,32]]},{"type":"ning_manor_coup","gate_name":"ning_south_gate","capture":["NingXi65","YouZaiGu65"]})
def reuse_cui():
    src=ROOT/"assets/lzc/map_sources/m108_ch65a_manifest.json";d=json.loads(src.read_text(encoding="utf-8"))
    d["deployments"]=[{"name":"LuPuBie66","force":1,"position":[24,30]},{"name":"QingFeng62","force":1,"position":[19,29]},{"name":"CuiCheng65","force":3,"position":[20,15]},{"name":"CuiJiang65","force":3,"position":[29,15]}]
    d["mission"]={"type":"cui_clan_collapse","defeat":["CuiCheng65","CuiJiang65"],"historical_death":"CuiZhu62"}
    (ROOT/"assets/lzc/map_sources/m108_ch66c_manifest.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    image=Image.open(ROOT/d["map"]).convert("RGBA");rows=d["terrain_rows"]
    structures.review_image(image,rows,{"walls":{tuple(q) for q in d["wall_cells"]},"fences":set(),"gates":{tuple(q) for z in d["gates"] for q in z["cells"]},"sites":{tuple(q) for q in d["supply_sites"]}},d["deployments"],ROOT/"output/terrain_model/m108_ch66c_review.png")
def shuju():
    w,h=68,46;rows=common.natural_rows(w,h)
    for y in range(h):
        for x in range(19,28):rows[y][x]="F"
    for y in range(17,29):
        for x in range(16,33):rows[y][x]="f"
    b=(47,8,64,37);g={(47,22),(47,23)};fences=structures.rectangle_perimeter(*b)-g;sites={(56,16),(57,29)}
    for x,y in fences:rows[y][x]="P"
    for x,y in sites:rows[y][x]="e"
    source="chapter53-zhulin-base-gpt2.png";image=common.base_image(source,w,h,rows);structures.draw_fences(image,fences,b);structures.draw_sites(image,sites)
    dep=[{"name":"QuJian66","force":1,"position":[14,20]},{"name":"ZiJiang66","force":1,"position":[17,24]},{"name":"XiHuan66","force":1,"position":[21,21]},{"name":"YiMei60","force":3,"position":[34,20]},{"name":"QuHuYong66","force":3,"position":[38,24]}]
    common.save_map("m113","ch66d",image,rows,source,"Use case: historical-scene\nAsset type: large Mengde forest ambush and stockade map\nPrimary request: Qishan forest ambush in the west, broad Ershan battlefield and a separate fenced Shuju stockade in the east.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no structures, units, text, UI or visible grid; stockade is a separate center-axis fence overlay.\n",set(),g,sites,dep,{"qishan_ambush":[[16,17],[32,28]],"shuju_stockade":[[47,8],[64,37]],"west_gate":[[47,22],[47,23]]},{"type":"shuju_campaign","gate_name":"shuju_west_gate","phases":["ershan_ambush","relief_defeat","stockade_capture"]})
    p=ROOT/"assets/lzc/map_sources/m113_ch66d_manifest.json";x=json.loads(p.read_text(encoding="utf-8"));x["fence_cells"]=[list(q) for q in sorted(fences)];x["fence_geometry"]="impassable cell center-axis; corners use two half-axis segments; west gate omits two cells";x["camp_icon_cells"]=[list(q) for q in sorted(sites)];x["camp_cells"]=[list(q) for q in sorted(sites)];p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8");structures.review_image(image,rows,{"walls":set(),"fences":fences,"gates":g,"sites":sites},dep,ROOT/"output/terrain_model/m113_ch66d_review.png")
def jize():
    w,h=60,42;rows=common.natural_rows(w,h)
    for y in range(h):
        for x in range(27,34):rows[y][x]="w" if (x+y)%3 else "v"
    for y in range(15,28):
        for x in range(24,38):rows[y][x]="f"
    source="chapter55-qingcao-base-gpt2.png";image=common.base_image(source,w,h,rows)
    dep=[{"name":"ChuanFengShu66","force":1,"position":[14,20]},{"name":"GongZiWei66","force":2,"position":[18,23]},{"name":"HuangJie66","force":3,"position":[45,21]}]
    common.save_map("m114","ch66e",image,rows,source,"Use case: historical-scene\nAsset type: Mengde tactical marsh battle\nPrimary request: broad Jize plain with crossable shallow marsh bands and open ground for Chu and Zheng chariots.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no structures, units, text, UI or visible grid.\n",set(),set(),set(),dep,{"jize_marsh":[[24,0],[37,41]],"chu_start":[[10,16],[20,26]],"zheng_line":[[42,16],[50,27]]},{"type":"jize_capture","capture":"HuangJie66"})
if __name__=="__main__":yu_village();ning_manor();reuse_cui();shuju();jize();print("chapter 66 maps generated: m111, m112, m113, m114")
