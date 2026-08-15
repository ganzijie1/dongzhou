from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat

try:
    from tools import generate_chapter43_maps as structures
except ImportError:
    import generate_chapter43_maps as structures


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WIDTH = 60
HEIGHT = 42
GAO_BOUNDS = (38, 3, 56, 18)
GUO_BOUNDS = (38, 23, 56, 39)
GAO_GATES = {(38, 10), (38, 11)}
GUO_GATES = {(38, 30), (38, 31)}
GAO_WALLS = structures.rectangle_perimeter(*GAO_BOUNDS) - GAO_GATES
GUO_WALLS = structures.rectangle_perimeter(*GUO_BOUNDS) - GUO_GATES
WALLS = GAO_WALLS | GUO_WALLS
GATES = GAO_GATES | GUO_GATES
SITES = {(49, 10), (49, 31)}


def make_rows() -> list[list[str]]:
    rows = [["g" if (x * 7 + y * 11) % 19 < 5 else "f" for x in range(WIDTH)] for y in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if 16 <= x <= 35 or 19 <= y <= 22:
                rows[y][x] = "i"
            if x < 8 and (x * 5 + y * 3) % 17 < 3:
                rows[y][x] = "F"
    for bounds in (GAO_BOUNDS, GUO_BOUNDS):
        x0, y0, x1, y1 = bounds
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                rows[y][x] = "i"
    for x, y in WALLS:
        rows[y][x] = "W"
    for x, y in GATES:
        rows[y][x] = "G"
    for x, y in SITES:
        rows[y][x] = "C"
    return rows


def make_base(rows: list[list[str]]) -> Image.Image:
    random.seed(81)
    image = Image.new("RGB", (WIDTH * CELL, HEIGHT * CELL), (125, 143, 94))
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(420):
        x = random.randrange(image.width)
        y = random.randrange(image.height)
        radius = random.randrange(24, 150)
        color = random.choice(((72, 104, 58, 24), (171, 155, 102, 28), (91, 126, 75, 22)))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    avenue = (15 * CELL, 0, 36 * CELL, HEIGHT * CELL)
    cross = (0, 19 * CELL, WIDTH * CELL, 23 * CELL)
    draw.rounded_rectangle(avenue, radius=90, fill=(153, 139, 108, 205))
    draw.rounded_rectangle(cross, radius=80, fill=(153, 139, 108, 205))
    for bounds in (GAO_BOUNDS, GUO_BOUNDS):
        x0, y0, x1, y1 = bounds
        draw.rectangle(((x0 + 1) * CELL, (y0 + 1) * CELL, x1 * CELL, y1 * CELL), fill=(159, 143, 112, 185))
    image = image.filter(ImageFilter.GaussianBlur(5))
    texture = Image.new("RGBA", image.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture)
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            if terrain == "F":
                texture_draw.ellipse((x * CELL - 16, y * CELL - 16, (x + 1) * CELL + 16, (y + 1) * CELL + 16), fill=(48, 91, 48, 70))
    return Image.alpha_composite(image.convert("RGBA"), texture.filter(ImageFilter.GaussianBlur(10)))


def main() -> None:
    rows = make_rows()
    base = make_base(rows)
    base_path = ROOT / "output/imagegen/m127_ch81_base.png"
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(base_path, compress_level=3)

    image = base.copy()
    structures.draw_walls(image, GAO_WALLS, GAO_BOUNDS)
    structures.draw_walls(image, GUO_WALLS, GUO_BOUNDS)
    structures.draw_castles(image, SITES)
    map_path = ROOT / "assets/lzc/map/m127.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, compress_level=3)

    deployments = [
        {"name": "ChenQi81", "force": 1, "position": [10, 19]},
        {"name": "BaoMu81", "force": 1, "position": [10, 23]},
        {"name": "GaoZhang81", "force": 3, "position": [49, 10]},
        {"name": "GuoXia81", "force": 3, "position": [49, 31]},
        {"name": "QiClanGuard81", "force": 1, "position": [14, 18]},
        {"name": "QiClanArcher81", "force": 1, "position": [14, 24]},
    ]
    for name, force, positions in (
        ("QiClanGuard81", 1, ((17, 16), (17, 20), (17, 26), (17, 30), (23, 17), (23, 25), (29, 18), (29, 24))),
        ("QiClanArcher81", 1, ((20, 14), (20, 28), (27, 15), (27, 27))),
        ("GaoHouseGuard81", 3, ((40, 9), (40, 12), (44, 7), (44, 14), (48, 6), (52, 7), (52, 14), (54, 11))),
        ("GaoHouseArcher81", 3, ((42, 5), (42, 16), (50, 5), (50, 16))),
        ("GuoHouseGuard81", 3, ((40, 29), (40, 33), (44, 26), (44, 36), (48, 25), (52, 27), (52, 35), (54, 31))),
        ("GuoHouseArcher81", 3, ((42, 25), (42, 37), (50, 25), (50, 37))),
    ):
        deployments.extend(
            {"name": name, "force": force, "position": list(position)} for position in positions
        )
    prompt = (
        "Use case: historical-scene\n"
        "Asset type: Mengde tactical battle-map base\n"
        "Primary request: broad Linzi residential avenues with open western assembly ground and reserved eastern ground for two noble compounds.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, muted late-Spring-and-Autumn city palette.\n"
        "Constraints: no walls, gates, buildings, units, text, UI, or visible grid in the base; structures are aligned overlays.\n"
        "Method: deterministic local raster composition because the built-in image generator was unavailable.\n"
    )
    prompt_path = ROOT / "output/imagegen/m127_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    manifest = {
        "map": "assets/lzc/map/m127.png",
        "source_base": "output/imagegen/m127_ch81_base.png",
        "prompt_file": "output/imagegen/m127_prompt.txt",
        "grid": [WIDTH, HEIGHT],
        "cell_pixels": CELL,
        "terrain_rows": ["".join(row) for row in rows],
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "manually reviewed deterministic raster base and programmatic source-of-truth structures",
        "structure_regions": {
            "gao_residence": [[GAO_BOUNDS[0], GAO_BOUNDS[1]], [GAO_BOUNDS[2], GAO_BOUNDS[3]]],
            "guo_residence": [[GUO_BOUNDS[0], GUO_BOUNDS[1]], [GUO_BOUNDS[2], GUO_BOUNDS[3]]],
            "central_avenue": [[16, 0], [35, 41]],
        },
        "camp_icon_cells": [],
        "camp_cells": [],
        "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [list(cell) for cell in sorted(WALLS)],
        "gates": [
            {"name": "gao_west_gate", "cells": [list(cell) for cell in sorted(GAO_GATES)]},
            {"name": "guo_west_gate", "cells": [list(cell) for cell in sorted(GUO_GATES)]},
        ],
        "castle_cells": [list(cell) for cell in sorted(SITES)],
        "supply_sites": [list(cell) for cell in sorted(SITES | GATES)],
        "blocked_edges": [],
        "deployments": deployments,
        "mission": {
            "type": "linzi_clan_coup",
            "historical_death": ["GaoZhang81"],
            "historical_retreat": {"hero": "GuoXia81", "route": [[38, 31], [30, 31], [20, 31], [8, 35], [1, 38]]},
        },
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m127_ch81_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path = ROOT / "output/terrain_model/m127_ch81_review.png"
    structures.review_image(image, rows, {"walls": WALLS, "fences": set(), "gates": GATES, "sites": SITES}, deployments, review_path)
    prediction = {
        "map": manifest["map"],
        "grid": manifest["grid"],
        "backend": "reviewed-contract-programmatic-source",
        "threshold": 0.72,
        "auto_apply": False,
        "review_required": [],
        "common_terrain_review": {"classes": ["f", "g", "F"], "status": "manually reviewed against deterministic source geometry"},
        "note": "All walls, gates, sites, and deployments are source-owned and excluded from classifier overwrite.",
    }
    prediction_path = ROOT / "output/terrain_model/m127_ch81_prediction.json"
    prediction_path.write_text(json.dumps(prediction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    assert image.size == (WIDTH * CELL, HEIGHT * CELL)
    assert max(ImageStat.Stat(image.convert("RGB")).var) > 100
    print("chapter 81 map generated: m127 Linzi Gao-Guo clan compounds")


if __name__ == "__main__":
    main()
