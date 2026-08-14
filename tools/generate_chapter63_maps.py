from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter60_maps as common
import generate_chapter43_maps as structures


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def tint_city(image: Image.Image, bounds: tuple[int, int, int, int]) -> Image.Image:
    x0, y0, x1, y1 = bounds
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle((x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL), fill=(126, 105, 77, 82))
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(7)))


def build_gugong() -> None:
    width, height = 74, 52
    rows = common.natural_rows(width, height)
    jiang = (2, 2, 71, 49)
    jiang_gates = {(36, 49), (37, 49)}
    outer_walls = structures.rectangle_perimeter(*jiang) - jiang_gates
    for y in range(3, 49):
        for x in range(3, 71):
            rows[y][x] = "i" if (x + y) % 7 else "h"

    palace = (45, 8, 68, 35)
    palace_gates = {(56, 35), (57, 35), (56, 8), (57, 8)}
    palace_walls = structures.rectangle_perimeter(*palace) - palace_gates
    for y in range(9, 35):
        for x in range(46, 68):
            rows[y][x] = "i"
    sites = {(57, 16), (63, 25), (18, 12)}
    walls = outer_walls | palace_walls
    gates = jiang_gates | palace_gates
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    source = "chapter38-wangcheng-base-gpt2.png"
    image = tint_city(common.base_image(source, width, height, rows), jiang)
    image = tint_city(image, palace)
    structures.draw_walls(image, outer_walls, jiang); structures.draw_walls(image, palace_walls, palace); structures.draw_sites(image, sites)
    deployments = [
        {"name":"FanYang61","force":1,"position":[17,12]}, {"name":"WeiShu63","force":1,"position":[19,12]},
        {"name":"ZhaoWu59","force":1,"position":[54,31]}, {"name":"XunWu62","force":1,"position":[60,31]},
        {"name":"HanQi62","force":1,"position":[57,12]}, {"name":"LuanYing62","force":3,"position":[36,39]},
        {"name":"DuRong63","force":3,"position":[38,43]}, {"name":"LuanLe63","force":3,"position":[55,39]},
        {"name":"LuanFang63","force":3,"position":[60,40]},
    ]
    prompt = "Use case: historical-scene\nAsset type: very large Mengde tactical city-defense map\nPrimary request: continuous outer walls of Jiang, broad southern breach avenue, northern Wei residence, and a separate strongly walled Gugong palace in the east.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural city streets.\nConstraints: no units, text, UI, or visible grid; all walls, gates and supply buildings are separate source-of-truth overlays.\n"
    common.save_map("m104", "ch63a", image, rows, source, prompt, walls, gates, sites, deployments,
                    {"jiang_city":[[2,2],[71,49]],"wei_residence":[[14,9],[22,15]],"gugong":[[45,8],[68,35]],"south_breach":[[36,49],[37,49]]},
                    {"type":"gugong_defense","gate_name":"jiang_and_gugong_gates","phases":["seize_weishu","escort_gugong","du_rong","north_gate_fire"]})
    p=ROOT/"assets/lzc/map_sources/m104_ch63a_manifest.json"; d=json.loads(p.read_text(encoding="utf-8"))
    d["gates"]=[{"name":"jiang_south_breach","cells":[[36,49],[37,49]]},{"name":"gugong_south_gate","cells":[[56,35],[57,35]]},{"name":"gugong_north_gate","cells":[[56,8],[57,8]]}]
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")


def build_quwo() -> None:
    width, height = 58, 42
    rows = common.natural_rows(width, height)
    bounds = (9, 4, 48, 34)
    gates = {(28,34),(29,34),(48,18),(48,19)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    for y in range(5,34):
        for x in range(10,48): rows[y][x]="i" if (x*3+y)%9 else "h"
    sites={(28,10),(18,21),(38,21)}
    for x,y in walls: rows[y][x]="W"
    for x,y in gates: rows[y][x]="G"
    for x,y in sites: rows[y][x]="C"
    source="chapter36-linghu-base-gpt2.png"
    image=tint_city(common.base_image(source,width,height,rows),bounds)
    structures.draw_walls(image,walls,bounds); structures.draw_sites(image,sites)
    deployments=[
        {"name":"FanYang61","force":1,"position":[53,17]},{"name":"XunWu62","force":1,"position":[53,21]},
        {"name":"LuanYing62","force":3,"position":[28,10]},{"name":"XuWu63","force":3,"position":[18,21]},
        {"name":"LuanRong63","force":3,"position":[38,21]},{"name":"LuanFang63","force":3,"position":[28,29]},
    ]
    prompt="Use case: historical-scene\nAsset type: Mengde tactical siege map\nPrimary request: broad continuous-walled Quwo city with south and east gates, interior streets, clan hall and two defended arsenals.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; walls, gates and restorative sites are separate source-of-truth overlays.\n"
    common.save_map("m105","ch63b",image,rows,source,prompt,walls,gates,sites,deployments,
                    {"quwo":[[9,4],[48,34]],"east_gate":[[48,18],[48,19]],"south_gate":[[28,34],[29,34]]},
                    {"type":"quwo_final_siege","gate_name":"quwo_gates","capture":["LuanYing62","LuanRong63"],"historical_escape":"LuanFang63"})
    p=ROOT/"assets/lzc/map_sources/m105_ch63b_manifest.json"; d=json.loads(p.read_text(encoding="utf-8"))
    d["gates"]=[{"name":"quwo_east_gate","cells":[[48,18],[48,19]]},{"name":"quwo_south_gate","cells":[[28,34],[29,34]]}]
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":
    build_gugong(); build_quwo(); print("chapter 63 maps generated: m104 74x52, m105 58x42")
