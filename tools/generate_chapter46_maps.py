from pathlib import Path
import json
import math

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def natural_rows(width, height, mode):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            if mode == "dagu":
                edge = min(y, height - 1 - y)
                if edge <= 1 and (x < 6 or x > width - 7):
                    tile = "r"
                elif edge <= 4:
                    tile = "m" if (x + y * 3) % 4 else "F"
                elif edge <= 7:
                    tile = "F" if (x * 2 + y) % 3 else "m"
                else:
                    tile = "w" if (x + y) % 6 < 2 else ("g" if (x * 2 + y) % 4 else "f")
            else:
                border = min(x, width - 1 - x, y, height - 1 - y)
                if border <= 1 and ((x + y) % 5 == 0):
                    tile = "r"
                elif border <= 3:
                    tile = "m" if (x * 3 + y) % 5 == 0 else "F"
                elif border <= 6 and (x + y * 2) % 4 == 0:
                    tile = "F"
                else:
                    tile = "w" if (x + y * 2) % 7 < 2 else ("g" if (x * 2 + y) % 4 else "f")
            row.append(tile)
        rows.append("".join(row))
    return rows


def wangguan_rows():
    width, height = 36, 28
    rows = [list(row) for row in natural_rows(width, height, "plain")]
    bounds = (7, 2, 28, 17)
    gates = {(16, 17), (17, 17), (18, 17)}
    walls = common.rectangle_perimeter(*bounds) - gates
    interior = {(x, y) for y in range(3, 17) for x in range(8, 28)}
    castle = {(17, 5)}
    stores = {(11, 7), (24, 7)}
    for x, y in interior:
        rows[y][x] = "i"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in castle:
        rows[y][x] = "C"
    for x, y in stores:
        rows[y][x] = "b"
    return ["".join(row) for row in rows], bounds, walls, gates, castle, stores


def apply_natural_overlay(source, rows):
    width, height = len(rows[0]), len(rows)
    image = source.resize((width * CELL, height * CELL), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    colors = {"r": (58, 52, 46, 76), "m": (91, 76, 57, 38),
              "F": (30, 76, 40, 38), "w": (129, 104, 69, 27), "i": (104, 92, 76, 66)}
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            if tile in colors:
                draw.rectangle((x * CELL - 5, y * CELL - 5,
                                (x + 1) * CELL + 5, (y + 1) * CELL + 5), fill=colors[tile])
    return Image.alpha_composite(image, mask.filter(ImageFilter.GaussianBlur(15)))


def manifest_base(map_id, source_name, prompt_name, rows, deployments, mission):
    return {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": f"output/imagegen/{prompt_name}",
        "grid": [len(rows[0]), len(rows)],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed source-of-truth terrain masks",
        "structure_regions": {},
        "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [], "gates": [], "castle_cells": [], "supply_sites": [],
        "blocked_edges": [], "deployments": deployments, "mission": mission,
        "visual_grid_in_game": False,
    }


def write_natural(map_id, source_name, prompt_name, rows, deployments, mission):
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = apply_natural_overlay(source, rows)
    image.convert("RGB").save(ROOT / "assets/lzc/map" / f"{map_id}.png", "PNG", compress_level=3)
    manifest = manifest_base(map_id, source_name, prompt_name, rows, deployments, mission)
    (ROOT / "assets/lzc/map_sources" / f"{map_id}_ch46_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()},
                        deployments, ROOT / "output/terrain_model" / f"{map_id}_ch46_review.png")
    return image


def build_dagu():
    rows = natural_rows(38, 26, "dagu")
    deployments = [
        {"name": "XianQieJu45", "force": 1, "position": [7, 13]},
        {"name": "HuSheGu27", "force": 1, "position": [8, 11]},
        {"name": "XiQue45", "force": 1, "position": [8, 15]},
        {"name": "LuanDun45", "force": 1, "position": [6, 10]},
        {"name": "HuJuJu45", "force": 1, "position": [6, 16]},
        {"name": "BaiTun46", "force": 3, "position": [30, 13]},
    ]
    write_natural("m070", "chapter46-dagu-exchange-base-gpt2.png", "m070_prompt.txt", rows, deployments,
                  {"type": "corpse_exchange_then_battle", "boss_outcome": "released_by_hu_shegu"})
    return rows


def build_pengya():
    rows = natural_rows(42, 28, "plain")
    deployments = [
        {"name": "XianQieJu45", "force": 1, "position": [7, 14]},
        {"name": "ZhaoShuai27", "force": 1, "position": [5, 16]},
        {"name": "HuJuJu45", "force": 1, "position": [6, 12]},
        {"name": "LangTan45", "force": 1, "position": [10, 14]},
        {"name": "MengMingShi26", "force": 3, "position": [35, 14]},
        {"name": "XiQiShu26", "force": 3, "position": [34, 11]},
        {"name": "BaiYiBing26", "force": 3, "position": [34, 17]},
        {"name": "XianBo46", "force": 2, "position": [22, 15], "arrival": "langtan_charge"},
    ]
    write_natural("m071", "chapter46-pengya-base-gpt2.png", "m071_prompt.txt", rows, deployments,
                  {"type": "vanguard_charge", "trigger": [23, 14], "qin_named_outcome": "retreat",
                   "lang_tan_outcome": "scripted_death_after_victory"})
    return rows


def build_wangguan():
    rows, bounds, walls, gates, castle, stores = wangguan_rows()
    deployments = [
        {"name": "QinMuGong29", "force": 1, "position": [17, 24]},
        {"name": "MengMingShi26", "force": 1, "position": [17, 21]},
        {"name": "XiQiShu26", "force": 1, "position": [14, 23]},
        {"name": "BaiYiBing26", "force": 1, "position": [20, 23]},
        {"name": "YouYu26", "force": 1, "position": [19, 25]},
        {"name": "WangguanCommander46", "force": 3, "position": [17, 5]},
    ]
    source = Image.open(ROOT / "output/imagegen/chapter46-wangguan-base-gpt2.png").convert("RGB")
    image = apply_natural_overlay(source, rows)
    common.draw_walls(image, walls, bounds)
    common.draw_castles(image, castle)
    common.draw_sites(image, stores)
    image.convert("RGB").save(ROOT / "assets/lzc/map/m072.png", "PNG", compress_level=3)
    manifest = manifest_base("m072", "chapter46-wangguan-base-gpt2.png", "m072_prompt.txt", rows, deployments,
                             {"type": "wangguan_siege", "goal": "occupy_castle", "postlude": "xiaoshan_burial"})
    manifest.update({
        "terrain_source": "GPT Image 2 natural base plus programmatic source-of-truth Wangguan structures",
        "structure_regions": {"wangguan_city": [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]},
        "wall_cells": [list(c) for c in sorted(walls)],
        "gates": [{"name": "wangguan_south_gate", "cells": [list(c) for c in sorted(gates)]}],
        "castle_cells": [list(c) for c in sorted(castle)],
        "camp_icon_cells": [], "camp_cells": [],
        "supply_sites": [list(c) for c in sorted(castle | stores)],
    })
    (ROOT / "assets/lzc/map_sources/m072_ch46_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": walls, "fences": set(), "gates": gates,
                                      "sites": castle | stores}, deployments,
                        ROOT / "output/terrain_model/m072_ch46_review.png")
    return rows


def print_rows(map_id, rows):
    print(f"{map_id}: {len(rows[0])}x{len(rows)}, native={len(rows[0]) * CELL}x{len(rows) * CELL}")
    print("LUA_ROWS_BEGIN")
    for row in rows:
        print(f'        "{row}",')
    print("LUA_ROWS_END")


def main():
    print_rows("m070", build_dagu())
    print_rows("m071", build_pengya())
    print_rows("m072", build_wangguan())


if __name__ == "__main__":
    main()
