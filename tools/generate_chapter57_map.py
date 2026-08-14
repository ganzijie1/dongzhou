from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def build_rows(width, height, walls, gates, halls):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if border <= 2 and (x + y * 3) % 6 in (0, 1):
                terrain = "F"
            elif (x * 2 + y) % 11 in (0, 1):
                terrain = "g"
            else:
                terrain = "f"
            row.append(terrain)
        rows.append(row)

    for y in range(4, 28):
        for x in range(5, 39):
            rows[y][x] = "i"
    for x in range(5, 46):
        rows[15][x] = "w"
        rows[16][x] = "w"
    for y in range(6, 27):
        rows[y][23] = "w"
        rows[y][24] = "w"
    for x, y in halls:
        rows[y][x] = "h"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    return ["".join(row) for row in rows]


def draw_halls(image, hall_groups):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x0, y0, x1, y1 in hall_groups:
        left, top = x0 * CELL + 5, y0 * CELL + 8
        right, bottom = (x1 + 1) * CELL - 5, (y1 + 1) * CELL - 5
        draw.rectangle((left, top + 13, right, bottom), fill=(126, 101, 69, 235), outline=(70, 57, 43, 255), width=3)
        roof = [(left - 8, top + 15), ((left + right) // 2, top - 8), (right + 8, top + 15)]
        draw.polygon(roof, fill=(73, 82, 77, 250), outline=(39, 45, 43, 255))
        for px in range(left + 17, right - 8, 28):
            draw.line((px, top + 16, px, bottom - 2), fill=(91, 65, 47, 170), width=2)
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(0.35)))


def main():
    width, height = 48, 32
    palace_bounds = (4, 3, 39, 28)
    gates = {(39, 15), (39, 16)}
    walls = common.rectangle_perimeter(*palace_bounds) - gates
    hall_groups = [(8, 7, 14, 10), (18, 6, 29, 10), (8, 21, 14, 24), (28, 20, 35, 24)]
    halls = {(x, y) for x0, y0, x1, y1 in hall_groups for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
    rows = build_rows(width, height, walls, gates, halls)
    deployments = [
        {"name": "PalaceDoctor57", "force": 1, "position": [10, 16]},
        {"name": "HanJue48", "force": 1, "position": [44, 16]},
        {"name": "TuAnGu50", "force": 3, "position": [34, 13]},
        {"name": "PalaceSearchGuard57", "force": 3, "position": [31, 15]},
        {"name": "PalaceSearchGuard57", "force": 3, "position": [31, 18]},
        {"name": "PalaceSearchGuard57", "force": 3, "position": [26, 13]},
        {"name": "PalaceSearchGuard57", "force": 3, "position": [26, 19]},
    ]

    source_name = "chapter50-taoyuan-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (width * CELL, height * CELL))
    image = natural.natural_overlay(image, rows)
    courtyard = Image.new("RGBA", image.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(courtyard)
    cd.rectangle((5 * CELL, 4 * CELL, 39 * CELL, 28 * CELL), fill=(123, 111, 91, 55))
    image = Image.alpha_composite(image, courtyard.filter(ImageFilter.GaussianBlur(7)))
    draw_halls(image, hall_groups)
    common.draw_walls(image, walls, palace_bounds)

    map_path = ROOT / "assets/lzc/map/m091.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m091.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": "output/imagegen/m091_prompt.txt",
        "grid": [width, height],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "i"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "reused GPT Image 2 palace ground base plus reviewed programmatic source-of-truth palace geometry",
        "structure_regions": {"xinjiang_palace": [[4, 3], [39, 28]], "palace_halls": hall_groups},
        "camp_icon_cells": [],
        "camp_cells": [],
        "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [list(c) for c in sorted(walls)],
        "gates": [{"name": "xinjiang_palace_east_gate", "cells": [list(c) for c in sorted(gates)]}],
        "castle_cells": [],
        "supply_sites": [],
        "blocked_edges": [],
        "deployments": deployments,
        "mission": {
            "type": "palace_orphan_escort",
            "carrier": "PalaceDoctor57",
            "escort": "HanJue48",
            "escape": [44, 15],
            "only_exit": "xinjiang_palace_east_gate",
            "named_enemy_invulnerable": ["TuAnGu50"],
        },
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m091_ch57_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": walls, "fences": set(), "gates": gates, "sites": set()}, deployments,
                        ROOT / "output/terrain_model/m091_ch57_review.png")
    prediction = {
        "map": manifest["map"], "grid": manifest["grid"],
        "backend": "reviewed-contract-with-dinov3-evidence-slot", "threshold": 0.72,
        "auto_apply": False, "review_required": [],
        "note": "Classifier evidence cannot overwrite reviewed palace walls, gates, halls, or Lua terrain."
    }
    (ROOT / "output/terrain_model/m091_ch57_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (width * CELL, height * CELL) and max(stat.var) > 100
    print(f"m091: {width}x{height}, pixels={image.size}, walls={len(walls)}, gates={len(gates)}")


if __name__ == "__main__":
    main()
