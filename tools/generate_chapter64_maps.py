from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat

import generate_chapter60_maps as common
import generate_chapter43_maps as structures


ROOT=Path(__file__).resolve().parents[1]
CELL=48


def build_shaoshui():
    width,height=60,40
    rows=common.natural_rows(width,height)
    # Two Taihang shoulders leave a broad east-west pass; Shaoshui is shallow and crossable.
    for y in range(height):
        for x in range(15,29):rows[y][x]="m"
    for y in range(15,25):
        for x in range(12,32):rows[y][x]="f"
    for y in range(height):
        center=35+(y-20)//6
        for x in range(max(0,center-1),min(width,center+2)):rows[y][x]="v"
    for y in range(16,24):
        for x in range(33,39):rows[y][x]="v"
    source="chapter48-hequ-base-gpt2.png"
    image=common.base_image(source,width,height,rows)
    water=Image.new("RGBA",image.size,(0,0,0,0));draw=ImageDraw.Draw(water)
    for y,row in enumerate(rows):
        for x,t in enumerate(row):
            if t=="v":draw.rectangle((x*CELL,y*CELL,(x+1)*CELL,(y+1)*CELL),fill=(79,137,151,96))
    image=Image.alpha_composite(image,water.filter(ImageFilter.GaussianBlur(5)))
    deployments=[
        {"name":"QiZhuangGong62","force":1,"position":[19,19]},{"name":"WangSunHui64","force":1,"position":[22,17]},
        {"name":"ShenXianYu64","force":1,"position":[22,22]},{"name":"YanMao64","force":2,"position":[13,20]},
        {"name":"ZhaoSheng64","force":3,"position":[6,20]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical retreat map\nPrimary request: broad Taihang mountain shoulders, an open east-west withdrawal pass, and crossable Shaoshui shallows toward the eastern exit.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\nConstraints: no structures, units, text, UI, or visible grid.\n"
    common.save_map("m106","ch64a",image,rows,source,prompt,set(),set(),set(),deployments,
                    {"taihang_pass":[[12,15],[31,24]],"shaoshui":[[33,0],[38,39]],"east_exit":[[58,18],[59,22]]},
                    {"type":"shaoshui_rearguard","exit":[58,20],"historical_death":"YanMao64"})


def build_qieyu():
    width,height=68,46
    rows=common.natural_rows(width,height)
    # A narrow approach is bounded by rocky shoulders.
    for y in range(4,42):
        for x in range(38,51):rows[y][x]="m"
    for y in range(18,28):
        for x in range(35,54):rows[y][x]="f"
    # Fire trench blocks the approach except for the explicit two-cell shield crossing.
    fire={(46,y) for y in range(18,28)}
    crossing={(46,22),(46,23)}
    for x,y in fire:rows[y][x]="~"
    for x,y in crossing:rows[y][x]="G"
    city=(52,5,66,40);gates={(52,22),(52,23)};walls=structures.rectangle_perimeter(*city)-gates
    for y in range(6,40):
        for x in range(53,66):rows[y][x]="i"
    sites={(59,12)}
    for x,y in walls:rows[y][x]="W"
    for x,y in gates:rows[y][x]="G"
    for x,y in sites:rows[y][x]="C"
    source="chapter45-dagu-base-gpt2.png"
    image=common.base_image(source,width,height,rows)
    # GPT Image 2 fire texture is feathered into the exact trench strip.
    fire_src=Image.open(ROOT/"output/imagegen/qieyu-fire-trench-gpt2.png").convert("RGB")
    assert max(ImageStat.Stat(fire_src).var)>100
    texture=fire_src.resize((CELL*2,CELL*10),Image.Resampling.LANCZOS).convert("RGBA")
    mask=Image.new("L",texture.size,0);md=ImageDraw.Draw(mask);md.rounded_rectangle((8,4,texture.width-8,texture.height-4),radius=18,fill=235)
    mask=mask.filter(ImageFilter.GaussianBlur(7));texture.putalpha(mask)
    image.alpha_composite(texture,(45*CELL,18*CELL))
    city_tint=Image.new("RGBA",image.size,(0,0,0,0));ImageDraw.Draw(city_tint).rectangle((53*CELL,6*CELL,67*CELL,40*CELL),fill=(124,103,76,78));image=Image.alpha_composite(image,city_tint.filter(ImageFilter.GaussianBlur(6)))
    structures.draw_walls(image,walls,city);structures.draw_sites(image,sites)
    deployments=[
        {"name":"HuaZhou64","force":1,"position":[12,21]},{"name":"QiLiang64","force":1,"position":[12,24]},
        {"name":"XiHouZhong64","force":1,"position":[10,23]},{"name":"JuLiBiGong64","force":3,"position":[29,23]},
        {"name":"JuGateCaptain64","force":3,"position":[52,22]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical siege approach\nPrimary request: broad Ju outskirts, a narrow rocky approach, a visible charcoal fire trench, and continuous walls around Qieyu gate.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; fire trench and city geometry are reviewed source-of-truth overlays.\n"
    common.save_map("m107","ch64b",image,rows,source,prompt,walls,gates|crossing,sites,deployments,
                    {"qieyu_city":[[52,5],[66,40]],"fire_trench":[[46,18],[46,27]],"shield_crossing":[[46,22],[46,23]],"west_gate":[[52,22],[52,23]]},
                    {"type":"qieyu_last_stand","gate_name":"qieyu_passages","phases":["outskirts","shield_bridge","gate_assault"]})
    p=ROOT/"assets/lzc/map_sources/m107_ch64b_manifest.json";d=json.loads(p.read_text(encoding="utf-8"))
    d["gates"]=[{"name":"shield_crossing","cells":[[46,22],[46,23]]},{"name":"qieyu_west_gate","cells":[[52,22],[52,23]]}]
    d["fire_trench_cells"]=[list(p) for p in sorted(fire-crossing)];d["fire_texture"]="output/imagegen/qieyu-fire-trench-gpt2.png"
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":build_shaoshui();build_qieyu();print("chapter 64 maps generated: m106 60x40, m107 68x46")
