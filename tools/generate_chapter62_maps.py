from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter60_maps as common
import generate_chapter43_maps as structures


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def _paint_city(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(layer).rectangle((x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL), fill=(124, 105, 78, 82))
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(7)))


def build_qi_campaign() -> None:
    width, height = 86, 56
    rows = common.natural_rows(width, height)
    # The Fangmen defensive trench is deep water except for the three-cell filled crossing.
    for y in range(6, 51):
        for x in range(25, 29):
            rows[y][x] = "~"
    trench_crossing = {(x, y) for y in range(27, 30) for x in range(25, 29)}
    for x, y in trench_crossing:
        rows[y][x] = "v"

    pingyin = (34, 14, 49, 35)
    pingyin_gates = {(34, 24), (34, 25), (49, 24), (49, 25)}
    pingyin_walls = structures.rectangle_perimeter(*pingyin) - pingyin_gates
    for y in range(15, 35):
        for x in range(35, 49):
            rows[y][x] = "i"

    # Shimen is a narrow but fully connected pass between rocky shoulders.
    for y in range(5, 51):
        for x in range(55, 65):
            rows[y][x] = "m"
    for y in range(24, 29):
        for x in range(53, 67):
            rows[y][x] = "f"

    linzi = (68, 5, 84, 45)
    linzi_gates = {(68, 24), (68, 25)}
    linzi_walls = structures.rectangle_perimeter(*linzi) - linzi_gates
    for y in range(6, 45):
        for x in range(69, 84):
            rows[y][x] = "i"
    sites = {(42, 20), (76, 13), (78, 30)}
    walls = pingyin_walls | linzi_walls
    gates = pingyin_gates | linzi_gates
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter49-mengzhu-base-gpt2.png"
    image = common.base_image(source, width, height, rows)
    image = _paint_city(_paint_city(image, pingyin), linzi)
    structures.draw_walls(image, pingyin_walls, pingyin)
    structures.draw_walls(image, linzi_walls, linzi)
    structures.draw_sites(image, sites)
    deployments = [
        {"name": "XunYan58", "force": 1, "position": [12, 25]},
        {"name": "ShiGai60", "force": 1, "position": [10, 28]},
        {"name": "ZhaoWu59", "force": 1, "position": [12, 31]},
        {"name": "HanQi62", "force": 1, "position": [8, 24]},
        {"name": "WeiJiang62", "force": 1, "position": [8, 32]},
        {"name": "ZhouChuo62", "force": 1, "position": [15, 28]},
        {"name": "LuanYing62", "force": 1, "position": [10, 35]},
        {"name": "XiGuiFu62", "force": 3, "position": [31, 28]},
        {"name": "ZhiChuo62", "force": 3, "position": [61, 25]},
        {"name": "GuoZui62", "force": 3, "position": [61, 28]},
        {"name": "QiLingGong62", "force": 3, "position": [76, 13]},
        {"name": "CuiZhu62", "force": 3, "position": [71, 23]},
        {"name": "QingFeng62", "force": 3, "position": [72, 28]},
    ]
    prompt = "Use case: historical-scene\nAsset type: very large Mengde tactical campaign map\nPrimary request: Fangmen trench, walled Pingyin, rocky Shimen pass, and continuous walled Linzi in one scrolling battlefield.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\nConstraints: no units, text, UI, or visible grid; walls, gates and cities are source-of-truth overlays.\n"
    common.save_map("m101", "ch62a", image, rows, source, prompt, walls, gates, sites, deployments,
                    {"fangmen_trench": [[25, 6], [28, 50]], "pingyin": [[34, 14], [49, 35]], "shimen": [[53, 24], [66, 28]], "linzi": [[68, 5], [84, 45]]},
                    {"type": "qi_campaign_merged", "gate_name": "campaign_passages", "phases": ["fangmen", "pingyin", "shimen", "linzi_six_days"]})
    p = ROOT / "assets/lzc/map_sources/m101_ch62a_manifest.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["gates"] = [{"name": "pingyin_gates", "cells": [list(c) for c in sorted(pingyin_gates)]}, {"name": "linzi_west_gate", "cells": [list(c) for c in sorted(linzi_gates)]}, {"name": "filled_fangmen_trench", "cells": [list(c) for c in sorted(trench_crossing)]}]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def build_gaotang() -> None:
    width, height = 58, 42
    rows = common.natural_rows(width, height)
    bounds = (12, 4, 48, 34)
    # Main south gate and the northeast rope breach are explicit passable cells.
    gates = {(29, 34), (30, 34), (48, 7), (48, 8)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    for y in range(5, 34):
        for x in range(13, 48):
            rows[y][x] = "i"
    sites = {(29, 11), (39, 18)}
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"
    source = "chapter47-linghu-night-base-gpt2.png"
    image = _paint_city(common.base_image(source, width, height, rows), bounds)
    structures.draw_walls(image, walls, bounds)
    structures.draw_sites(image, sites)
    deployments = [
        {"name": "QiZhuangGong62", "force": 1, "position": [23, 38]},
        {"name": "ZhiChuo62", "force": 1, "position": [51, 7]},
        {"name": "GuoZui62", "force": 1, "position": [52, 9]},
        {"name": "GongLou62", "force": 2, "position": [46, 8]},
        {"name": "SuShaWei62", "force": 3, "position": [29, 11]},
    ]
    prompt = "Use case: historical-scene\nAsset type: Mengde tactical siege map\nPrimary request: continuous walled Gaotang city, broad south approach, and reserved northeast wall corner for a night rope breach.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; the northeast rope entry and south gate remain distinct passable cells.\n"
    common.save_map("m102", "ch62b", image, rows, source, prompt, walls, gates, sites, deployments,
                    {"gaotang": [[12, 4], [48, 34]], "rope_breach": [[48, 7], [48, 8]], "south_gate": [[29, 34], [30, 34]]},
                    {"type": "gaotang_night_breach", "gate_name": "gaotang_passages", "capture": ["SuShaWei62"]})
    p = ROOT / "assets/lzc/map_sources/m102_ch62b_manifest.json"
    d = json.loads(p.read_text(encoding="utf-8")); d["gates"] = [{"name": "gaotang_south_gate", "cells": [[29, 34], [30, 34]]}, {"name": "northeast_rope_breach", "cells": [[48, 7], [48, 8]]}]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def build_shuhu_manor() -> None:
    width, height = 50, 36
    rows = common.natural_rows(width, height)
    bounds = (13, 5, 38, 28)
    gates = {(25, 28), (26, 28)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    for y in range(6, 28):
        for x in range(14, 38):
            rows[y][x] = "i"
    sites = {(25, 11)}
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"
    source = "chapter56-an-base-gpt2.png"
    image = _paint_city(common.base_image(source, width, height, rows), bounds)
    structures.draw_walls(image, walls, bounds); structures.draw_sites(image, sites)
    deployments = [
        {"name": "FanYang61", "force": 1, "position": [24, 32]},
        {"name": "ShuHu62", "force": 3, "position": [24, 18]},
        {"name": "JiYi62", "force": 3, "position": [28, 18]},
        {"name": "HuangYuan62", "force": 3, "position": [42, 18]},
    ]
    prompt = "Use case: historical-scene\nAsset type: Mengde tactical manor siege map\nPrimary request: continuous-walled Jin noble manor with a broad south gate and open road for Xun Wu reinforcements.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic.\nConstraints: no units, text, UI, or visible grid; only the burned south gate is passable.\n"
    common.save_map("m103", "ch62c", image, rows, source, prompt, walls, gates, sites, deployments,
                    {"shuhu_manor": [[13, 5], [38, 28]], "burned_gate": [[25, 28], [26, 28]]},
                    {"type": "shuhu_manor_arrest", "gate_name": "burned_south_gate", "capture": ["ShuHu62", "JiYi62", "HuangYuan62"]})


if __name__ == "__main__":
    build_qi_campaign(); build_gaotang(); build_shuhu_manor()
    print("chapter 62 maps generated: m101 86x56, m102 58x42, m103 50x36")
