from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageStat

import generate_chapter43_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def cover_resize(source, size):
    target_ratio = size[0] / size[1]
    source_ratio = source.width / source.height
    if source_ratio > target_ratio:
        width = round(source.height * target_ratio)
        left = (source.width - width) // 2
        source = source.crop((left, 0, left + width, source.height))
    elif source_ratio < target_ratio:
        height = round(source.width / target_ratio)
        top = (source.height - height) // 2
        source = source.crop((0, top, source.width, top + height))
    return source.resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def snow_rows(width, height):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if border <= 2 and (x * 3 + y) % 5 < 2:
                tile = "F"
            elif border <= 4 and (x + y * 2) % 5 == 0:
                tile = "m"
            elif abs((x + y // 2) - 25) <= 2:
                tile = "w"
            else:
                tile = "g" if (x + y * 2) % 5 < 2 else "f"
            row.append(tile)
        rows.append("".join(row))
    return rows


def linghu_rows(width, height, fences, camps):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if x <= 3:
                tile = "w"
            elif border <= 2 and (x + y * 3) % 5 == 0:
                tile = "F"
            elif y <= 4 and (x * 2 + y) % 4 == 0:
                tile = "m"
            else:
                tile = "g" if (x * 2 + y) % 6 < 2 else "f"
            row.append(tile)
        rows.append(row)
    for x, y in fences:
        rows[y][x] = "P"
    for x, y in camps:
        rows[y][x] = "e"
    return ["".join(row) for row in rows]


def natural_overlay(image, rows, night=False):
    mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    colors = {
        "r": (58, 52, 46, 54), "m": (82, 72, 62, 34), "F": (28, 64, 38, 36),
        "w": (135, 110, 76, 24), "g": (84, 104, 64, 20), "f": (120, 112, 82, 14),
    }
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            if tile in colors:
                draw.rectangle((x * CELL - 6, y * CELL - 6, (x + 1) * CELL + 6,
                                (y + 1) * CELL + 6), fill=colors[tile])
    result = Image.alpha_composite(image, mask.filter(ImageFilter.GaussianBlur(16)))
    if night:
        blue = Image.new("RGBA", result.size, (18, 28, 56, 42))
        result = Image.alpha_composite(result, blue)
    return result


def draw_traps(image, traps):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x, y in traps:
        cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
        draw.ellipse((cx - 18, cy - 11, cx + 18, cy + 11), fill=(58, 48, 40, 72))
        draw.arc((cx - 18, cy - 11, cx + 18, cy + 11), 180, 350, fill=(220, 225, 224, 120), width=3)
        draw.line((cx - 12, cy, cx + 12, cy + 1), fill=(116, 103, 84, 105), width=2)
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(1.2)))


def base_manifest(map_id, source, prompt, rows, deployments, mission):
    return {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{prompt}",
        "grid": [len(rows[0]), len(rows)], "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [],
        "castle_cells": [], "supply_sites": [], "blocked_edges": [],
        "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }


def build_snow_ambush():
    map_id, width, height = "m073", 36, 26
    rows = snow_rows(width, height)
    traps = {(17, 12), (18, 12), (19, 12), (17, 13), (18, 13), (19, 13),
             (17, 14), (18, 14), (19, 14)}
    deployments = [
        {"name": "ShuSunDeChen47", "force": 1, "position": [27, 18]},
        {"name": "FuFuZhongSheng47", "force": 1, "position": [25, 16]},
        {"name": "QiaoRu47", "force": 3, "position": [8, 7]},
    ]
    source_name = "chapter47-snow-ambush-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = cover_resize(source, (width * CELL, height * CELL))
    image = natural_overlay(image, rows)
    snow = ImageEnhance.Color(image.convert("RGB")).enhance(0.72).convert("RGBA")
    image = Image.blend(image, snow, 0.32)
    draw_traps(image, traps)
    image.convert("RGB").save(ROOT / "assets/lzc/map" / f"{map_id}.png", "PNG", compress_level=3)
    manifest = base_manifest(map_id, source_name, "m073_prompt.txt", rows, deployments, {
        "type": "snow_trap_ambush", "trap_cells": [list(c) for c in sorted(traps)],
        "trigger_center": [18, 13], "trigger_radius": 2, "boss_outcome": "historical_death",
    })
    (ROOT / "assets/lzc/map_sources/m073_ch47a_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()},
                        deployments, ROOT / "output/terrain_model/m073_ch47a_review.png")
    return rows


def build_linghu():
    map_id, width, height = "m074", 42, 28
    bounds = (6, 4, 25, 23)
    east_gates = {(25, 13), (25, 14)}
    west_gates = {(6, 13), (6, 14)}
    gates = east_gates | west_gates
    fences = common.rectangle_perimeter(*bounds) - gates
    camps = {(11, 9), (19, 9), (15, 14), (11, 18), (19, 18)}
    rows = linghu_rows(width, height, fences, camps)
    deployments = [
        {"name": "ZhaoDun47", "force": 1, "position": [35, 13]},
        {"name": "XianKe47", "force": 1, "position": [35, 16]},
        {"name": "XunLinFu47", "force": 1, "position": [38, 12]},
        {"name": "XianDu47", "force": 1, "position": [38, 17]},
        {"name": "GongZiYong47", "force": 3, "position": [15, 14]},
        {"name": "BaiYiBing26", "force": 3, "position": [11, 9]},
        {"name": "XianMie47", "force": 3, "position": [19, 9]},
        {"name": "ShiHui47", "force": 3, "position": [19, 18]},
    ]
    source_name = "chapter47-linghu-night-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = cover_resize(source, (width * CELL, height * CELL))
    image = natural_overlay(image, rows, night=True)
    common.draw_fences(image, fences, bounds)
    common.draw_sites(image, camps)
    image.convert("RGB").save(ROOT / "assets/lzc/map" / f"{map_id}.png", "PNG", compress_level=3)
    manifest = base_manifest(map_id, source_name, "m074_prompt.txt", rows, deployments, {
        "type": "linghu_night_raid", "entry_gates": [list(c) for c in sorted(east_gates)],
        "retreat_gates": [list(c) for c in sorted(west_gates)], "pursuit_goal": [2, 14],
        "gongzi_yong_outcome": "historical_death", "survivors": ["BaiYiBing26", "XianMie47", "ShiHui47"],
    })
    manifest.update({
        "structure_regions": {"qin_camp": [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]},
        "camp_icon_cells": [list(c) for c in sorted(camps)], "camp_cells": [list(c) for c in sorted(camps)],
        "fence_cells": [list(c) for c in sorted(fences)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [{"name": "qin_east_gate", "cells": [list(c) for c in sorted(east_gates)]},
                  {"name": "qin_west_gate", "cells": [list(c) for c in sorted(west_gates)]}],
        "supply_sites": [list(c) for c in sorted(camps)],
    })
    (ROOT / "assets/lzc/map_sources/m074_ch47b_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": set(), "fences": fences, "gates": gates, "sites": camps},
                        deployments, ROOT / "output/terrain_model/m074_ch47b_review.png")
    return rows


def validate_image(path, size):
    image = Image.open(path).convert("RGB")
    stat = ImageStat.Stat(image)
    assert image.size == size
    assert max(stat.var) > 120.0
    return {"size": image.size, "variance": [round(v, 2) for v in stat.var]}


def print_rows(map_id, rows):
    print(f"{map_id}: {len(rows[0])}x{len(rows)}")
    print("LUA_ROWS_BEGIN")
    for row in rows:
        print(f'        "{row}",')
    print("LUA_ROWS_END")


def main():
    (ROOT / "assets/lzc/map").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/lzc/map_sources").mkdir(parents=True, exist_ok=True)
    (ROOT / "output/terrain_model").mkdir(parents=True, exist_ok=True)
    rows73 = build_snow_ambush()
    rows74 = build_linghu()
    print_rows("m073", rows73)
    print_rows("m074", rows74)
    print(validate_image(ROOT / "assets/lzc/map/m073.png", (36 * CELL, 26 * CELL)))
    print(validate_image(ROOT / "assets/lzc/map/m074.png", (42 * CELL, 28 * CELL)))


if __name__ == "__main__":
    main()
