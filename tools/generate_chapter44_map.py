from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as common


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, CELL = 32, 24, 48
CITY_BOUNDS = (6, 2, 25, 15)
WEST_GATE = {(6, 9), (6, 10)}
EAST_GATE = {(25, 9), (25, 10)}
SOUTH_GATE = {(15, 15), (16, 15)}
GATES = WEST_GATE | EAST_GATE | SOUTH_GATE
WALLS = common.rectangle_perimeter(*CITY_BOUNDS) - GATES
INTERIOR = {(x, y) for y in range(3, 15) for x in range(7, 25)}
CASTLES = {(14, 5), (16, 5), (18, 5)}


def terrain_rows():
    rows = common.base_rows(WIDTH, HEIGHT)
    for x, y in INTERIOR:
        rows[y][x] = "i"
    for x, y in WALLS:
        rows[y][x] = "W"
    for x, y in GATES:
        rows[y][x] = "G"
    for x, y in CASTLES:
        rows[y][x] = "C"
    return ["".join(row) for row in rows]


def deployments():
    return [
        {"name": "MengMingShi26", "force": 1, "position": [15, 21]},
        {"name": "XiQiShu26", "force": 1, "position": [4, 18]},
        {"name": "BaiYiBing26", "force": 1, "position": [27, 18]},
        {"name": "BaoManZi44", "force": 1, "position": [14, 20]},
        {"name": "QinGuard44", "force": 1, "position": [5, 19]},
        {"name": "QinArcher44", "force": 1, "position": [3, 19]},
        {"name": "QinGuard44", "force": 1, "position": [16, 20]},
        {"name": "QinArcher44", "force": 1, "position": [17, 21]},
        {"name": "QinGuard44", "force": 1, "position": [26, 19]},
        {"name": "QinArcher44", "force": 1, "position": [28, 19]},
        {"name": "HuaGong44", "force": 3, "position": [16, 5]},
        {"name": "HuaGuard44", "force": 3, "position": [6, 9]},
        {"name": "HuaGuard44", "force": 3, "position": [6, 10]},
        {"name": "HuaGuard44", "force": 3, "position": [25, 9]},
        {"name": "HuaGuard44", "force": 3, "position": [25, 10]},
        {"name": "HuaGuard44", "force": 3, "position": [15, 15]},
        {"name": "HuaGuard44", "force": 3, "position": [16, 15]},
        {"name": "HuaGuard44", "force": 3, "position": [11, 11]},
        {"name": "HuaGuard44", "force": 3, "position": [21, 11]},
        {"name": "HuaArcher44", "force": 3, "position": [9, 8]},
        {"name": "HuaArcher44", "force": 3, "position": [23, 8]},
        {"name": "HuaArcher44", "force": 3, "position": [13, 7]},
        {"name": "HuaArcher44", "force": 3, "position": [19, 7]},
    ]


def main():
    rows = terrain_rows()
    units = deployments()
    source = Image.open(ROOT / "output/imagegen/chapter44-hua-base-gpt2.png").convert("RGB")
    image = source.resize((WIDTH * CELL, HEIGHT * CELL), Image.Resampling.LANCZOS).convert("RGBA")
    tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(tint)
    draw.rectangle((7 * CELL, 3 * CELL, 25 * CELL, 15 * CELL), fill=(80, 86, 98, 76))
    image = Image.alpha_composite(image, tint.filter(ImageFilter.GaussianBlur(7)))
    common.draw_walls(image, WALLS, CITY_BOUNDS)
    common.draw_castles(image, CASTLES)

    map_path = ROOT / "assets/lzc/map/m067.png"
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m067.png",
        "source_base": "output/imagegen/chapter44-hua-base-gpt2.png",
        "prompt_file": "output/imagegen/m067_prompt.txt",
        "grid": [WIDTH, HEIGHT], "cell_pixels": CELL, "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 moonlit natural base plus programmatic source-of-truth city structures",
        "structure_regions": {"hua_city": [[6, 2], [25, 15]]},
        "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "wall_cells": [list(c) for c in sorted(WALLS)],
        "gates": [
            {"name": "hua_west_gate", "cells": [list(c) for c in sorted(WEST_GATE)]},
            {"name": "hua_south_gate", "cells": [list(c) for c in sorted(SOUTH_GATE)]},
            {"name": "hua_east_gate", "cells": [list(c) for c in sorted(EAST_GATE)]},
        ],
        "castle_cells": [list(c) for c in sorted(CASTLES)],
        "supply_sites": [list(c) for c in sorted(CASTLES)],
        "blocked_edges": [], "deployments": units,
        "mission": {"type": "three_route_night_assault", "turn_limit": 10,
                    "goal": "any_named_qin_commander_reaches_hua_palace", "hua_lord_outcome": "retreat_to_di"},
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m067_ch44_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(
        image, rows, {"walls": WALLS, "fences": set(), "gates": GATES, "sites": CASTLES}, units,
        ROOT / "output/terrain_model/m067_ch44_review.png",
    )
    print(f"m067: {WIDTH}x{HEIGHT}, deployments={len(units)}")


if __name__ == "__main__":
    main()
