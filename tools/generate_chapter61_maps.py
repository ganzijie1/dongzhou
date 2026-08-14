from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter60_maps as common
import generate_chapter43_maps as structures


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def base(source: str, width: int, height: int, rows: list[list[str]]) -> Image.Image:
    return common.base_image(source, width, height, rows)


def build_zheng_palace() -> None:
    width, height = 50, 34
    rows = common.natural_rows(width, height)
    bounds = (8, 4, 41, 27); gates = {(24,27),(25,27)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(24,10),(16,18),(34,18)}
    for y in range(5,27):
        for x in range(9,41): rows[y][x] = "i"
    for x0,y0,x1,y1 in ((18,7,31,12),(12,15,19,21),(31,15,38,21)):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): rows[y][x]="h"
    for x,y in walls: rows[y][x]="W"
    for x,y in gates: rows[y][x]="G"
    for x,y in sites: rows[y][x]="C"
    image=base("chapter36-jiang-palace-base-gpt2.png",width,height,rows)
    shade=Image.new("RGBA",image.size,(0,0,0,0)); ImageDraw.Draw(shade).rectangle((9*CELL,5*CELL,41*CELL,27*CELL),fill=(135,112,82,75))
    image=Image.alpha_composite(image,shade.filter(ImageFilter.GaussianBlur(7)))
    structures.draw_walls(image,walls,bounds); structures.draw_sites(image,sites)
    deployments=[
        {"name":"GongSunXia61","force":1,"position":[21,30]},{"name":"ZiChan61","force":1,"position":[25,30]},
        {"name":"GongSunChai61","force":1,"position":[29,30]},{"name":"WeiZhi61","force":3,"position":[24,10]},
        {"name":"SiChen61","force":3,"position":[16,18]},{"name":"HouJin61","force":3,"position":[34,18]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical city map\nPrimary request: broad level terrain reserved for Zheng west palace, north palace and connected city streets.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no structures, units, text, UI, or visible grid; palace walls are separate overlays.\n"
    common.save_map("m098","ch61a",image,rows,"chapter36-jiang-palace-base-gpt2.png",prompt,walls,gates,sites,deployments,
                    {"zheng_palace":[[8,4],[41,27]],"south_gate":[[24,27],[25,27]]},
                    {"type":"zheng_palace_revolt","gate_name":"zheng_palace_south_gate","capture":["WeiZhi61","SiChen61","HouJin61"]})


def build_yulin() -> None:
    width,height=62,40
    rows=common.natural_rows(width,height)
    # Jing River crosses the western half; a three-cell ford remains passable.
    for y in range(height):
        for x in range(19,25): rows[y][x]="~"
    for y in range(17,21):
        for x in range(19,25): rows[y][x]="v"
    # Qin camp is a real enclosure: center-axis fence cells and a two-cell west gate.
    x0,y0,x1,y1=42,8,58,31
    gates={(42,19),(42,20)}
    fences=structures.rectangle_perimeter(x0,y0,x1,y1)-gates
    sites={(50,18),(53,23)}
    for x,y in fences: rows[y][x]="P"
    for x,y in sites: rows[y][x]="e"
    image=base("chapter48-hequ-base-gpt2.png",width,height,rows)
    # Reuse the project fence renderer when available; the terrain review remains authoritative.
    if hasattr(structures,"draw_fences"): structures.draw_fences(image,fences,(x0,y0,x1,y1))
    structures.draw_sites(image,sites)
    deployments=[
        {"name":"LuanZhen58","force":1,"position":[31,18]},{"name":"FanYang61","force":1,"position":[31,21]},
        {"name":"QinJingGong61","force":3,"position":[50,18]},{"name":"YingZhan61","force":3,"position":[53,23]},
        {"name":"GongZiWuDi61","force":3,"position":[44,20]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical field map\nPrimary request: broad Jing River plain at Yulin with western coalition bank and large reserved eastern Qin camp.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no camp, fence, units, text, UI, or visible grid; camp is a separate source-of-truth overlay.\n"
    # save_map expects walls; then patch the manifest with the strict fence contract.
    common.save_map("m099","ch61b",image,rows,"chapter48-hequ-base-gpt2.png",prompt,set(),gates,sites,deployments,
                    {"qin_camp":[[42,8],[58,31]],"west_gate":[[42,19],[42,20]]},
                    {"type":"yulin_last_charge","gate_name":"qin_camp_west_gate","historical_death":"LuanZhen58"})
    path=ROOT/"assets/lzc/map_sources/m099_ch61b_manifest.json"
    import json
    data=json.loads(path.read_text(encoding="utf-8")); data["fence_cells"]=[list(p) for p in sorted(fences)]; data["camp_cells"]=[list(p) for p in sorted(sites)]; data["camp_icon_cells"]=[list(p) for p in sorted(sites)]; data["fence_geometry"]="impassable cell center-axis; corners use two half-axis segments; west gate omits two cells"
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    structures.review_image(image,rows,{"walls":set(),"fences":fences,"gates":gates,"sites":sites},deployments,ROOT/"output/terrain_model/m099_ch61b_review.png")


def build_wei_escape() -> None:
    width,height=64,38
    rows=common.natural_rows(width,height)
    bounds=(3,5,22,31); gates={(22,17),(22,18)}
    walls=structures.rectangle_perimeter(*bounds)-gates
    sites={(12,12)}
    for y in range(6,31):
        for x in range(4,22): rows[y][x]="i"
    for x,y in walls: rows[y][x]="W"
    for x,y in gates: rows[y][x]="G"
    for x,y in sites: rows[y][x]="C"
    # A broad eastbound road crosses marshy Heze without becoming an artificial narrow corridor.
    for y in range(height):
        for x in range(24,width):
            rows[y][x]="w" if (x*3+y*5)%11<4 else "g"
    for x in range(20,width):
        for y in range(16,21): rows[y][x]="f"
    image=base("chapter50-jiao-base-gpt2.png",width,height,rows)
    structures.draw_walls(image,walls,bounds); structures.draw_sites(image,sites)
    road=Image.new("RGBA",image.size,(0,0,0,0)); ImageDraw.Draw(road).line([(20*CELL,18*CELL),(63*CELL,18*CELL)],fill=(145,119,78,120),width=CELL*5)
    image=Image.alpha_composite(image,road.filter(ImageFilter.GaussianBlur(6)))
    deployments=[
        {"name":"WeiXianGong61","force":1,"position":[18,17]},{"name":"GongSunDing61","force":1,"position":[19,19]},
        {"name":"SunKuai61","force":3,"position":[12,25]},{"name":"SunJia61","force":3,"position":[15,27]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical pursuit map\nPrimary request: Wei capital at west, broad east gate road through Heze marsh toward distant Qi border.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\nConstraints: no walls, units, text, UI, or visible grid; city structures are separate overlays.\n"
    common.save_map("m100","ch61c",image,rows,"chapter50-jiao-base-gpt2.png",prompt,walls,gates,sites,deployments,
                    {"wei_capital":[[3,5],[22,31]],"east_road":[[20,16],[63,20]]},
                    {"type":"wei_exile_escape","gate_name":"wei_east_gate","exit":[62,18],"merged_source":"chapter_62_opening"})


if __name__=="__main__":
    build_zheng_palace(); build_yulin(); build_wei_escape()
    print("chapter 61 maps generated: m098 50x34, m099 62x40, m100 64x38")
