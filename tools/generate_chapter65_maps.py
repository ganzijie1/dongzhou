from __future__ import annotations

import json
from pathlib import Path

from PIL import Image,ImageDraw,ImageFilter

import generate_chapter60_maps as common
import generate_chapter43_maps as structures

ROOT=Path(__file__).resolve().parents[1]
CELL=48

def tint(image,bounds,color=(125,104,77,80)):
    x0,y0,x1,y1=bounds;layer=Image.new("RGBA",image.size,(0,0,0,0));ImageDraw.Draw(layer).rectangle((x0*CELL,y0*CELL,(x1+1)*CELL,(y1+1)*CELL),fill=color)
    return Image.alpha_composite(image,layer.filter(ImageFilter.GaussianBlur(6)))

def manor():
    width,height=50,38;rows=common.natural_rows(width,height);bounds=(7,3,42,32);gates={(24,32),(25,32)};outer_walls=structures.rectangle_perimeter(*bounds)-gates
    for y in range(4,32):
        for x in range(8,42):rows[y][x]="i" if (x+y)%8 else "h"
    # Inner court has two open passages, not false wall crossings.
    inner={(x,17) for x in range(12,38)}-{(24,17),(25,17)}
    walls=outer_walls|inner;sites={(24,9),(15,24)}
    for x,y in walls:rows[y][x]="W"
    for x,y in gates|{(24,17),(25,17)}:rows[y][x]="G"
    for x,y in sites:rows[y][x]="C"
    source="chapter36-jiang-palace-base-gpt2.png";image=tint(common.base_image(source,width,height,rows),bounds);structures.draw_walls(image,outer_walls,bounds);structures.draw_walls(image,inner,(12,17,37,17));structures.draw_sites(image,sites)
    deployments=[{"name":"TangWuJiu65","force":1,"position":[24,9]},{"name":"CuiCheng65","force":1,"position":[20,15]},{"name":"CuiJiang65","force":1,"position":[29,15]},{"name":"DongGuoYan65","force":1,"position":[15,24]},{"name":"QiZhuangGong62","force":3,"position":[24,22]},{"name":"JiaJu65","force":3,"position":[25,20]},{"name":"ZhouChuoQi65","force":3,"position":[22,29]},{"name":"GongSunAo65","force":3,"position":[27,29]},{"name":"LouYan65","force":3,"position":[30,28]}]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical manor ambush map\nPrimary request: large continuous-walled Cui clan manor, inner residence, open courtyard, southern gate and two explicit inner passages.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; walls and sites are source-of-truth overlays.\n"
    common.save_map("m108","ch65a",image,rows,source,prompt,walls,gates|{(24,17),(25,17)},sites,deployments,{"cui_manor":[[7,3],[42,32]],"inner_court":[[12,17],[37,17]],"south_gate":[[24,32],[25,32]]},{"type":"cui_manor_regicide","gate_name":"cui_manor_passages","defeat":["QiZhuangGong62","JiaJu65","ZhouChuoQi65","GongSunAo65","LouYan65"]})

def chao():
    width,height=52,36;rows=common.natural_rows(width,height);city=(34,3,50,32);gates={(34,17),(34,18)};walls=structures.rectangle_perimeter(*city)-gates
    for y in range(4,32):
        for x in range(35,50):rows[y][x]="i"
    # Short wall used by Niu Chen is a genuine impassable firing screen.
    short={(28,y) for y in range(13,23)}-{(28,17),(28,18)};walls|=short;sites={(43,10)}
    for x,y in walls:rows[y][x]="W"
    for x,y in gates|{(28,17),(28,18)}:rows[y][x]="G"
    for x,y in sites:rows[y][x]="C"
    source="chapter45-dagu-base-gpt2.png";image=tint(common.base_image(source,width,height,rows),city);structures.draw_walls(image,walls,city);structures.draw_sites(image,sites)
    deployments=[{"name":"NiuChen65","force":1,"position":[30,16]},{"name":"ChaoGuard65","force":1,"position":[31,20]},{"name":"ZhuFan60","force":3,"position":[22,17]}]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical gate defense map\nPrimary request: continuous-walled Chao city at east, two-cell west gate, open approach and a short firing wall immediately before the gate.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; wall geometry is a reviewed overlay.\n"
    common.save_map("m109","ch65b",image,rows,source,prompt,walls,gates|{(28,17),(28,18)},sites,deployments,{"chao_city":[[34,3],[50,32]],"short_wall":[[28,13],[28,22]],"west_gate":[[34,17],[34,18]]},{"type":"chao_gate_ambush","gate_name":"chao_passages","historical_death":"ZhuFan60"})

def diqiu():
    width,height=70,48;rows=common.natural_rows(width,height)
    sun=(4,6,30,39);sun_gates={(30,21),(30,22)};sun_walls=structures.rectangle_perimeter(*sun)-sun_gates
    palace=(45,5,67,40);palace_gates={(45,22),(45,23)};palace_walls=structures.rectangle_perimeter(*palace)-palace_gates
    for box in (sun,palace):
        x0,y0,x1,y1=box
        for y in range(y0+1,y1):
            for x in range(x0+1,x1):rows[y][x]="i" if (x*3+y)%8 else "h"
    walls=sun_walls|palace_walls;gates=sun_gates|palace_gates;sites={(16,13),(23,29),(56,13)}
    for x,y in walls:rows[y][x]="W"
    for x,y in gates:rows[y][x]="G"
    for x,y in sites:rows[y][x]="C"
    source="chapter38-wangcheng-base-gpt2.png";image=tint(tint(common.base_image(source,width,height,rows),sun),palace);structures.draw_walls(image,sun_walls,sun);structures.draw_walls(image,palace_walls,palace);structures.draw_sites(image,sites)
    deployments=[{"name":"NingXi65","force":1,"position":[35,19]},{"name":"YouZaiGu65","force":1,"position":[35,23]},{"name":"BeiGongYi65","force":1,"position":[38,20]},{"name":"GongSunDing61","force":1,"position":[38,24]},{"name":"SunXiang65","force":3,"position":[27,21]},{"name":"ChuDai65","force":3,"position":[23,29]},{"name":"YongChu65","force":3,"position":[16,13]},{"name":"WeiShangGong65","force":3,"position":[56,13]},{"name":"TaiZiJiao65","force":3,"position":[58,18]}]
    prompt="Use case: historical-scene\nAsset type: large Mengde tactical coup map\nPrimary request: separate continuous-walled Sun clan manor in the west and Wei palace in the east, joined by broad Diqiu streets.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; both enclosures have explicit two-cell gates.\n"
    common.save_map("m110","ch65c",image,rows,source,prompt,walls,gates,sites,deployments,{"sun_manor":[[4,6],[30,39]],"wei_palace":[[45,5],[67,40]],"diqiu_street":[[31,16],[44,28]]},{"type":"diqiu_restoration","gate_name":"diqiu_gates","phases":["sun_manor_first_attack","night_assault","palace_deposition"]})
    p=ROOT/"assets/lzc/map_sources/m110_ch65c_manifest.json";d=json.loads(p.read_text(encoding="utf-8"));d["gates"]=[{"name":"sun_manor_east_gate","cells":[[30,21],[30,22]]},{"name":"wei_palace_west_gate","cells":[[45,22],[45,23]]}];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":manor();chao();diqiu();print("chapter 65 maps generated: m108 50x38, m109 52x36, m110 70x48")
