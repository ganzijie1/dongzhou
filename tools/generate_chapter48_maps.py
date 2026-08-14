from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageStat

import generate_chapter43_maps as structures
import generate_chapter47_maps as prior


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def natural_rows(width, height, mode):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if mode == "zheng":
                if border <= 2 and (x + y * 3) % 5 < 2:
                    tile = "F"
                elif border <= 5 and (x * 2 + y) % 7 == 0:
                    tile = "m"
                elif x >= width - 8:
                    tile = "w" if (x + y) % 4 == 0 else "f"
                else:
                    tile = "g" if (x * 2 + y) % 6 < 2 else "f"
            else:
                if x <= 4:
                    tile = "~"
                elif x <= 7:
                    tile = "w"
                elif border <= 2 and (x + y * 2) % 5 < 2:
                    tile = "F"
                elif border <= 5 and (x * 3 + y) % 8 == 0:
                    tile = "m"
                else:
                    tile = "g" if (x + y * 2) % 6 < 2 else "f"
            row.append(tile)
        rows.append(row)
    return rows


def place(rows, cells, terrain):
    for x, y in cells:
        rows[y][x] = terrain


def manifest_base(map_id, source, prompt, rows, deployments, mission):
    return {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{prompt}",
        "grid": [len(rows[0]), len(rows)], "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth structures",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [],
        "castle_cells": [], "supply_sites": [], "blocked_edges": [],
        "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }


def render_base(source_name, rows, night=False):
    width, height = len(rows[0]), len(rows)
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = prior.cover_resize(source, (width * CELL, height * CELL))
    return prior.natural_overlay(image, rows, night=night)


def build_zheng_decoy():
    map_id, width, height = "m075", 40, 28
    bounds = (11, 5, 28, 22)
    west_gates = {(11, 13), (11, 14)}
    east_gates = {(28, 13), (28, 14)}
    gates = west_gates | east_gates
    fences = structures.rectangle_perimeter(*bounds) - gates
    camps = {(15, 9), (23, 9), (19, 14), (15, 19), (23, 19)}
    rows = natural_rows(width, height, "zheng")
    place(rows, fences, "P")
    place(rows, camps, "e")
    rows = ["".join(row) for row in rows]
    deployments = [
        {"name": "DouYueJiao48", "force": 1, "position": [18, 3]},
        {"name": "WeiJia48", "force": 1, "position": [18, 25]},
        {"name": "StrawDecoy48", "force": 2, "position": [19, 14]},
        {"name": "GongZiJian48", "force": 3, "position": [36, 14]},
        {"name": "GongZiPang48", "force": 3, "position": [35, 12]},
        {"name": "YueEr48", "force": 3, "position": [35, 16]},
    ]
    source_name = "chapter48-zheng-decoy-base-gpt2.png"
    image = render_base(source_name, rows, night=True)
    structures.draw_fences(image, fences, bounds)
    structures.draw_sites(image, camps)
    image.convert("RGB").save(ROOT / "assets/lzc/map/m075.png", "PNG", compress_level=3)
    manifest = manifest_base(map_id, source_name, "m075_prompt.txt", rows, deployments, {
        "type": "empty_camp_double_ambush", "trigger_center": [19, 14], "trigger_radius": 2,
        "named_zheng_outcome": "captured_then_released", "ambush_wings": [[18, 3], [18, 25]],
    })
    manifest.update({
        "structure_regions": {"chu_decoy_camp": [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]},
        "camp_icon_cells": [list(c) for c in sorted(camps)], "camp_cells": [list(c) for c in sorted(camps)],
        "fence_cells": [list(c) for c in sorted(fences)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [{"name": "chu_west_gate", "cells": [list(c) for c in sorted(west_gates)]},
                  {"name": "chu_east_gate", "cells": [list(c) for c in sorted(east_gates)]}],
        "supply_sites": [list(c) for c in sorted(camps)],
    })
    (ROOT / "assets/lzc/map_sources/m075_ch48a_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    structures.review_image(image, rows, {"walls": set(), "fences": fences, "gates": gates, "sites": camps},
                            deployments, ROOT / "output/terrain_model/m075_ch48a_review.png")
    return rows


def build_hequ():
    map_id, width, height = "m076", 54, 32
    qin_bounds = (8, 6, 21, 25)
    qin_west = {(8, 15), (8, 16)}
    qin_east = {(21, 15), (21, 16)}
    qin_gates = qin_west | qin_east
    qin_fences = structures.rectangle_perimeter(*qin_bounds) - qin_gates
    jin_bounds = (39, 6, 52, 25)
    jin_west = {(39, 15), (39, 16)}
    jin_east = {(52, 15), (52, 16)}
    jin_gates = jin_west | jin_east
    jin_fences = structures.rectangle_perimeter(*jin_bounds) - jin_gates
    fences = qin_fences | jin_fences
    gates = qin_gates | jin_gates
    qin_camps = {(12, 10), (17, 10), (14, 15), (12, 21), (17, 21)}
    jin_camps = {(43, 10), (48, 10), (46, 15), (43, 21), (48, 21)}
    camps = qin_camps | jin_camps
    rows = natural_rows(width, height, "hequ")
    place(rows, fences, "P")
    place(rows, camps, "e")
    rows = ["".join(row) for row in rows]
    deployments = [
        {"name": "QinKangGong48", "force": 3, "position": [14, 15]},
        {"name": "XiQiShu26", "force": 3, "position": [12, 10]},
        {"name": "BaiYiBing26", "force": 3, "position": [17, 10]},
        {"name": "ShiHui47", "force": 3, "position": [17, 21]},
        {"name": "ZhaoDun47", "force": 1, "position": [46, 15]},
        {"name": "XunLinFu47", "force": 1, "position": [43, 10]},
        {"name": "XiQue45", "force": 1, "position": [48, 10]},
        {"name": "YuPian48", "force": 1, "position": [43, 21]},
        {"name": "LuanDun45", "force": 1, "position": [48, 21]},
        {"name": "XuJia48", "force": 1, "position": [45, 18]},
        {"name": "ZhaoChuan48", "force": 1, "position": [39, 15]},
        {"name": "HanJue48", "force": 1, "position": [50, 15]},
    ]
    source_name = "chapter48-hequ-base-gpt2.png"
    image = render_base(source_name, rows)
    structures.draw_fences(image, qin_fences, qin_bounds)
    structures.draw_fences(image, jin_fences, jin_bounds)
    structures.draw_sites(image, camps)
    image.convert("RGB").save(ROOT / "assets/lzc/map/m076.png", "PNG", compress_level=3)
    manifest = manifest_base(map_id, source_name, "m076_prompt.txt", rows, deployments, {
        "type": "hequ_standoff_and_rescue", "river_columns": [0, 4],
        "zhao_chuan_sortie": [30, 15], "jin_rescue": "named_officer_adjacency",
        "victory": "zhao_chuan_returns_to_jin_camp_after_three_turns", "named_qin_outcome": "night_retreat",
    })
    manifest.update({
        "structure_regions": {
            "qin_camp": [[qin_bounds[0], qin_bounds[1]], [qin_bounds[2], qin_bounds[3]]],
            "jin_camp": [[jin_bounds[0], jin_bounds[1]], [jin_bounds[2], jin_bounds[3]]],
        },
        "camp_icon_cells": [list(c) for c in sorted(camps)], "camp_cells": [list(c) for c in sorted(camps)],
        "fence_cells": [list(c) for c in sorted(fences)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [
            {"name": "qin_west_gate", "cells": [list(c) for c in sorted(qin_west)]},
            {"name": "qin_east_gate", "cells": [list(c) for c in sorted(qin_east)]},
            {"name": "jin_west_gate", "cells": [list(c) for c in sorted(jin_west)]},
            {"name": "jin_east_gate", "cells": [list(c) for c in sorted(jin_east)]},
        ],
        "supply_sites": [list(c) for c in sorted(camps)],
    })
    (ROOT / "assets/lzc/map_sources/m076_ch48b_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    structures.review_image(image, rows, {"walls": set(), "fences": fences, "gates": gates, "sites": camps},
                            deployments, ROOT / "output/terrain_model/m076_ch48b_review.png")
    return rows


def print_rows(map_id, rows):
    print(f"{map_id}: {len(rows[0])}x{len(rows)}")
    print("LUA_ROWS_BEGIN")
    for row in rows:
        print(f'        "{row}",')
    print("LUA_ROWS_END")


def validate(path, size):
    image = Image.open(path).convert("RGB")
    stat = ImageStat.Stat(image)
    assert image.size == size and max(stat.var) > 100
    return [round(value, 2) for value in stat.var]


def main():
    (ROOT / "assets/lzc/map").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/lzc/map_sources").mkdir(parents=True, exist_ok=True)
    (ROOT / "output/terrain_model").mkdir(parents=True, exist_ok=True)
    rows75 = build_zheng_decoy()
    rows76 = build_hequ()
    print_rows("m075", rows75)
    print_rows("m076", rows76)
    print("m075 variance", validate(ROOT / "assets/lzc/map/m075.png", (40 * CELL, 28 * CELL)))
    print("m076 variance", validate(ROOT / "assets/lzc/map/m076.png", (54 * CELL, 32 * CELL)))


if __name__ == "__main__":
    main()
