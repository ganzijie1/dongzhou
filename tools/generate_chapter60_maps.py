from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat

import generate_chapter43_maps as structures
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
BLOCKED = {"r", "W", "~", "P"}


def natural_rows(width: int, height: int) -> list[list[str]]:
    return [["F" if (x * 5 + y * 7) % 23 < 3 else "g" if (x * 3 + y * 11) % 17 < 6 else "f"
             for x in range(width)] for y in range(height)]


def save_map(map_id: str, suffix: str, image: Image.Image, rows: list[list[str]], source: str,
             prompt: str, walls: set[tuple[int, int]], gates: set[tuple[int, int]],
             sites: set[tuple[int, int]], deployments: list[dict], regions: dict, mission: dict) -> None:
    width, height = len(rows[0]), len(rows)
    row_strings = ["".join(row) for row in rows]
    assert all(len(row) == width for row in row_strings)
    for unit in deployments:
        x, y = unit["position"]
        assert 0 <= x < width and 0 <= y < height and rows[y][x] not in BLOCKED, unit
    output = ROOT / f"assets/lzc/map/{map_id}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG", compress_level=3)
    prompt_path = ROOT / f"output/imagegen/{map_id}_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    manifest = {
        "map": f"assets/lzc/map/{map_id}.png", "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{map_id}_prompt.txt", "grid": [width, height],
        "cell_pixels": CELL, "terrain_rows": row_strings,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m", "v"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "recomposed saved GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry",
        "structure_regions": regions, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [list(p) for p in sorted(walls)],
        "gates": [{"name": mission.get("gate_name", "passage"), "cells": [list(p) for p in sorted(gates)]}] if gates else [],
        "castle_cells": [list(p) for p in sorted(sites)], "supply_sites": [list(p) for p in sorted(sites)],
        "blocked_edges": [], "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }
    source_path = ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path = ROOT / f"output/terrain_model/{map_id}_{suffix}_review.png"
    structures.review_image(image, rows, {"walls": walls, "fences": set(), "gates": gates, "sites": sites}, deployments, review_path)
    prediction = {"map": manifest["map"], "grid": manifest["grid"],
                  "backend": "reviewed-contract-with-dinov3-evidence-slot", "threshold": 0.72,
                  "auto_apply": False, "review_required": [],
                  "note": "Visual predictions cannot overwrite reviewed barriers, passages, sites, or deployments."}
    (ROOT / f"output/terrain_model/{map_id}_{suffix}_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    assert image.size == (width * CELL, height * CELL)
    assert max(ImageStat.Stat(image.convert("RGB")).var) > 100


def base_image(source: str, width: int, height: int, rows: list[list[str]]) -> Image.Image:
    base = Image.open(ROOT / "output/imagegen" / source).convert("RGB")
    return natural.natural_overlay(natural.cover_resize(base, (width * CELL, height * CELL)), rows)


def build_pengcheng() -> None:
    width, height = 54, 38
    rows = natural_rows(width, height)
    bounds = (9, 3, 44, 27)
    gates = {(26, 27), (27, 27)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(26, 9), (18, 17), (35, 17)}
    for y in range(4, 27):
        for x in range(10, 44):
            rows[y][x] = "i"
    for x0, y0, x1, y1 in ((13, 7, 20, 11), (32, 7, 40, 11), (15, 20, 21, 23), (33, 20, 39, 23)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                rows[y][x] = "h"
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    source = "chapter55-suiyang-base-gpt2.png"
    image = base_image(source, width, height, rows)
    city = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(city).rectangle((10 * CELL, 4 * CELL, 44 * CELL, 27 * CELL), fill=(137, 118, 88, 78))
    image = Image.alpha_composite(image, city.filter(ImageFilter.GaussianBlur(7)))
    structures.draw_walls(image, walls, bounds)
    structures.draw_sites(image, sites)
    deployments = [
        {"name": "JinDaoGong60", "force": 1, "position": [24, 33]}, {"name": "HanJue48", "force": 1, "position": [28, 33]},
        {"name": "XunYan58", "force": 1, "position": [22, 35]}, {"name": "LuanYan60", "force": 1, "position": [30, 35]},
        {"name": "XiangShu60", "force": 2, "position": [20, 31]}, {"name": "ZhongSunMie60", "force": 2, "position": [33, 31]},
        {"name": "YuShi60", "force": 3, "position": [26, 9]}, {"name": "XiangWeiRen60", "force": 3, "position": [18, 17]},
        {"name": "LinZhu60", "force": 3, "position": [35, 17]}, {"name": "XiangDai60", "force": 3, "position": [22, 22]},
        {"name": "YuFu60", "force": 3, "position": [31, 22]},
    ]
    prompt = "Use case: historical-scene\nAsset type: Mengde tactical battle-map base\nPrimary request: broad natural plain around Pengcheng, reserved central ground for a walled Song city and southern coalition camp.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\nConstraints: no structures, units, text, UI, or visible grid; city geometry is a separate source-of-truth overlay.\n"
    save_map("m095", "ch60a", image, rows, source, prompt, walls, gates, sites, deployments,
             {"pengcheng": [[9, 3], [44, 27]], "south_gate": [[26, 27], [27, 27]]},
             {"type": "pengcheng_recapture", "gate_name": "pengcheng_south_gate", "capture": ["YuShi60", "XiangWeiRen60", "LinZhu60", "XiangDai60", "YuFu60"]})


def build_caishi() -> None:
    width, height = 62, 40
    rows = [["~" for _ in range(width)] for _ in range(height)]
    # Wide navigable river bends; deep-water margins remain hard boundaries.
    for y in range(height):
        center = 18 + y * 24 // (height - 1)
        for x in range(width):
            d = abs(x - center)
            if d <= 9: rows[y][x] = "v"
            elif d <= 12: rows[y][x] = "g"
            elif d <= 17: rows[y][x] = "f"
    # Caishi shoal and Jiuzi eastern fort are connected to the navigable channel.
    for y in range(14, 27):
        for x in range(28, 43): rows[y][x] = "v" if (x + y) % 5 else "g"
    for y in range(13, 28):
        for x in range(48, 60): rows[y][x] = "i"
    walls = {(47, y) for y in range(12, 29)} | {(60, y) for y in range(12, 29)} | {(x, 12) for x in range(47, 61)} | {(x, 28) for x in range(47, 61)}
    gates = {(47, 19), (47, 20)}
    walls -= gates
    sites = {(55, 20)}
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    source = "chapter54-river-retreat-base-gpt2.png"
    image = base_image(source, width, height, rows)
    water = Image.new("RGBA", image.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(water)
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            if terrain == "~": draw.rectangle((x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL), fill=(26, 75, 105, 170))
            elif terrain == "v": draw.rectangle((x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL), fill=(72, 130, 145, 105))
    image = Image.alpha_composite(image, water.filter(ImageFilter.GaussianBlur(5)))
    structures.draw_walls(image, walls, (47, 12, 60, 28)); structures.draw_sites(image, sites)
    deployments = [
        {"name": "ZhuFan60", "force": 1, "position": [18, 12]}, {"name": "YiMei60", "force": 1, "position": [24, 20]},
        {"name": "DengLiao60", "force": 3, "position": [34, 20]}, {"name": "YinQi60", "force": 3, "position": [55, 20]},
    ]
    prompt = "Use case: historical-scene\nAsset type: Mengde tactical river battle-map base\nPrimary request: broad Yangtze tributary, Caishi shallows, winding navigable channel, and open eastern bank reserved for Jiuzi fort.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural water transitions.\nConstraints: no units, text, UI, or visible grid; deep and shallow water semantics remain source-of-truth overlays.\n"
    save_map("m096", "ch60b", image, rows, source, prompt, walls, gates, sites, deployments,
             {"caishi": [[28, 14], [42, 26]], "jiuzi": [[47, 12], [60, 28]]},
             {"type": "caishi_ambush", "gate_name": "jiuzi_west_gate", "ambush_center": [28, 20], "recapture": [55, 20]})


def build_biyang() -> None:
    width, height = 56, 42
    rows = natural_rows(width, height)
    bounds = (8, 7, 47, 35)
    gates = {(27, 7), (28, 7)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(27, 27), (17, 18), (38, 18)}
    for y in range(8, 35):
        for x in range(9, 47): rows[y][x] = "i"
    for x0, y0, x1, y1 in ((13, 11, 21, 15), (34, 11, 42, 15), (14, 23, 21, 28), (34, 23, 41, 28)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): rows[y][x] = "h"
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    for y in range(0, 7):
        for x in range(width):
            if rows[y][x] not in {"W", "G"}: rows[y][x] = "w" if (x + y) % 4 else "g"
    source = "chapter46-wangguan-base-gpt2.png"
    image = base_image(source, width, height, rows)
    city = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(city).rectangle((9*CELL, 8*CELL, 47*CELL, 35*CELL), fill=(128, 111, 84, 76))
    image = Image.alpha_composite(image, city.filter(ImageFilter.GaussianBlur(7)))
    structures.draw_walls(image, walls, bounds); structures.draw_sites(image, sites)
    deployments = [
        {"name": "XunYing54", "force": 1, "position": [24, 3]}, {"name": "XunYan58", "force": 1, "position": [29, 3]},
        {"name": "ShiGai60", "force": 1, "position": [19, 4]}, {"name": "ZhongSunMie60", "force": 1, "position": [34, 4]},
        {"name": "ShuLiangHe60", "force": 1, "position": [26, 5]}, {"name": "QinJinFu60", "force": 1, "position": [22, 5]},
        {"name": "DiSiMi60", "force": 1, "position": [31, 5]}, {"name": "YunBan60", "force": 3, "position": [27, 25]},
        {"name": "BiYangLord60", "force": 3, "position": [27, 27]},
    ]
    prompt = "Use case: historical-scene\nAsset type: Mengde tactical siege-map base\nPrimary request: broad rain-soaked northern approach reserved for a large continuous-walled Biyang city, dense streets and public squares.\nStyle: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\nConstraints: no structures, units, text, UI, or visible grid; walls, hanging gate, and city sites are separate overlays.\n"
    save_map("m097", "ch60c", image, rows, source, prompt, walls, gates, sites, deployments,
             {"biyang": [[8, 7], [47, 35]], "north_gate": [[27, 7], [28, 7]]},
             {"type": "biyang_merged_siege", "gate_name": "biyang_north_hanging_gate", "merged_source": "chapter_61_opening", "rain_deadline_turns": 5})


if __name__ == "__main__":
    build_pengcheng(); build_caishi(); build_biyang()
    print("chapter 60 maps generated: m095 54x38, m096 62x40, m097 56x42")
