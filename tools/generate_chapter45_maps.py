from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def xiao_center(x):
    points = [(0, 15), (7, 13), (14, 15), (22, 12), (30, 14), (37, 11), (43, 13)]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return round(y0 + (y1 - y0) * t)
    return points[-1][1]


def xiaoshan_rows():
    width, height = 44, 28
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            d = abs(y - xiao_center(x))
            if d >= 10:
                tile = "r"
            elif d >= 8:
                tile = "m"
            elif d >= 6:
                tile = "F" if (x * 3 + y) % 5 < 2 else "m"
            elif d >= 4:
                tile = "m" if (x + y * 2) % 4 else "F"
            else:
                tile = "w" if (x + y) % 5 < 2 else ("g" if (x * 2 + y) % 3 else "f")
            row.append(tile)
        rows.append(row)
    return ["".join(row) for row in rows]


def dagu_rows():
    width, height = 36, 26
    rows = []
    for y in range(height):
        row = []
        valley_left = 9 + round(1.5 * math.sin(y / 4.0))
        valley_right = 26 + round(1.5 * math.sin((y + 3) / 4.5))
        for x in range(width):
            if (x < 3 or x > 32) and (y < 5 or y > 21):
                tile = "r"
            elif x < valley_left - 3 or x > valley_right + 3:
                tile = "m" if (x + y) % 5 == 0 else "F"
            elif x < valley_left or x > valley_right:
                tile = "F" if (x * 2 + y) % 4 else "m"
            else:
                tile = "g" if (x + y * 2) % 4 else "f"
            row.append(tile)
        rows.append("".join(row))
    return rows


def deployments_xiaoshan():
    return [
        {"name": "JinXiangGong45", "force": 1, "position": [23, 18]},
        {"name": "XianZhen27", "force": 1, "position": [21, 18]},
        {"name": "BaoManZi44", "force": 3, "position": [11, 14]},
        {"name": "MengMingShi26", "force": 3, "position": [18, 14]},
        {"name": "XiQiShu26", "force": 3, "position": [22, 12]},
        {"name": "BaiYiBing26", "force": 3, "position": [26, 13]},
    ]


def deployments_dagu():
    return [
        {"name": "XianZhen27", "force": 1, "position": [18, 22]},
        {"name": "XianQieJu45", "force": 1, "position": [18, 17]},
        {"name": "HuSheGu27", "force": 1, "position": [15, 21]},
        {"name": "HuJuJu45", "force": 1, "position": [21, 21]},
        {"name": "BaiBuHu45", "force": 3, "position": [18, 4]},
    ]


def terrain_overlay(source, rows):
    width, height = len(rows[0]), len(rows)
    image = source.resize((width * CELL, height * CELL), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    colors = {
        "r": (61, 54, 47, 74),
        "m": (91, 78, 58, 38),
        "F": (33, 79, 43, 40),
        "w": (124, 103, 68, 30),
    }
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            if tile in colors:
                pad = 5
                draw.rectangle((x * CELL - pad, y * CELL - pad,
                                (x + 1) * CELL + pad, (y + 1) * CELL + pad), fill=colors[tile])
    return Image.alpha_composite(image, mask.filter(ImageFilter.GaussianBlur(15)))


def write_map(map_id, stage_id, source_name, prompt_name, rows, deployments, mission):
    width, height = len(rows[0]), len(rows)
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = terrain_overlay(source, rows)
    map_path = ROOT / "assets/lzc/map" / f"{map_id}.png"
    image.convert("RGB").save(map_path, "PNG", compress_level=3)

    manifest = {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": f"output/imagegen/{prompt_name}",
        "grid": [width, height],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_source": "GPT Image 2 natural base plus source-of-truth broad terrain masks",
        "structure_regions": {},
        "camp_icon_cells": [],
        "camp_cells": [],
        "fence_cells": [],
        "fence_geometry": "no fences in this natural battlefield",
        "wall_cells": [],
        "gates": [],
        "castle_cells": [],
        "supply_sites": [],
        "blocked_edges": [],
        "deployments": deployments,
        "mission": mission,
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources" / f"{map_id}_ch45_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(
        image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()}, deployments,
        ROOT / "output/terrain_model" / f"{map_id}_ch45_review.png",
    )
    print(f"{map_id}: {width}x{height}, native={width * CELL}x{height * CELL}")
    print("LUA_ROWS_BEGIN")
    for row in rows:
        print(f'        "{row}",')
    print("LUA_ROWS_END")


def main():
    write_map(
        "m068", "45a", "chapter45-xiaoshan-base-gpt2.png", "m068_prompt.txt",
        xiaoshan_rows(), deployments_xiaoshan(),
        {"type": "four_sided_ambush", "trigger": [11, 14], "qin_named_outcome": "capture", "bao_manzi_outcome": "death"},
    )
    write_map(
        "m069", "45b", "chapter45-dagu-base-gpt2.png", "m069_prompt.txt",
        dagu_rows(), deployments_dagu(),
        {"type": "lure_into_valley", "trigger": [18, 13], "boss_outcome": "death", "xian_zhen_outcome": "scripted_death"},
    )


if __name__ == "__main__":
    main()
