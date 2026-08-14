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
    rows: list[list[str]] = []
    for y in range(height):
        row = []
        for x in range(width):
            value = (x * 5 + y * 7) % 19
            row.append("F" if value < 3 else "g" if value < 8 else "f")
        rows.append(row)
    return rows


def save_map(map_id: str, suffix: str, image: Image.Image, rows: list[list[str]],
             source: str, prompt: str, structures_data: dict, deployments: list[dict],
             mission: dict) -> None:
    width, height = len(rows[0]), len(rows)
    row_strings = ["".join(row) for row in rows]
    assert all(len(row) == width for row in row_strings)
    for unit in deployments:
        x, y = unit["position"]
        assert 0 <= x < width and 0 <= y < height
        assert rows[y][x] not in BLOCKED, unit

    map_path = ROOT / f"assets/lzc/map/{map_id}.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    prompt_path = ROOT / f"output/imagegen/{map_id}_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    walls = set(structures_data.get("walls", set()))
    gates = set(structures_data.get("gates", set()))
    sites = set(structures_data.get("sites", set()))
    manifest = {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{map_id}_prompt.txt",
        "grid": [width, height], "cell_pixels": CELL,
        "terrain_rows": row_strings,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "recomposed saved GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry",
        "structure_regions": structures_data.get("regions", {}),
        "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [list(p) for p in sorted(walls)],
        "gates": [{"name": structures_data.get("gate_name", "passage"), "cells": [list(p) for p in sorted(gates)]}] if gates else [],
        "castle_cells": [list(p) for p in sorted(sites)],
        "supply_sites": [list(p) for p in sorted(sites)],
        "blocked_edges": [], "deployments": deployments,
        "mission": mission, "visual_grid_in_game": False,
    }
    manifest_path = ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review = ROOT / f"output/terrain_model/{map_id}_{suffix}_review.png"
    structures.review_image(image, rows, {"walls": walls, "fences": set(), "gates": gates, "sites": sites}, deployments, review)
    prediction = {
        "map": manifest["map"], "grid": manifest["grid"],
        "backend": "reviewed-contract-with-dinov3-evidence-slot", "threshold": 0.72,
        "auto_apply": False, "review_required": [],
        "note": "Visual predictions cannot overwrite reviewed barriers, passages, sites, or deployments.",
    }
    (ROOT / f"output/terrain_model/{map_id}_{suffix}_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    assert image.size == (width * CELL, height * CELL)
    assert max(ImageStat.Stat(image.convert("RGB")).var) > 100


def build_taiyin() -> None:
    width, height = 52, 34
    rows = natural_rows(width, height)
    # Rocky mountain masses own whole cells; the central diagonal road remains broad and passable.
    for y in range(height):
        center = 12 + y * 25 // (height - 1)
        for x in range(width):
            distance = abs(x - center)
            if distance >= 12 and (x < 13 or x > 38):
                rows[y][x] = "r"
            elif distance >= 8:
                rows[y][x] = "m"
            elif distance <= 3:
                rows[y][x] = "w"

    source = "chapter56-xinzhu-base-gpt2.png"
    base = Image.open(ROOT / "output/imagegen" / source).convert("RGB")
    image = natural.cover_resize(base, (width * CELL, height * CELL))
    image = natural.natural_overlay(image, rows)
    road = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(road)
    points = [((12 + y * 25 // (height - 1)) * CELL + CELL // 2, y * CELL + CELL // 2) for y in range(height)]
    draw.line(points, fill=(142, 119, 80, 125), width=CELL * 7, joint="curve")
    image = Image.alpha_composite(image, road.filter(ImageFilter.GaussianBlur(8)))
    deployments = [
        {"name": "LuanShu58", "force": 1, "position": [12, 8]},
        {"name": "XunYan58", "force": 1, "position": [35, 25]},
        {"name": "JinLiGong58", "force": 3, "position": [25, 17]},
        {"name": "XuTong59", "force": 3, "position": [23, 15]},
        {"name": "ChengHua59", "force": 2, "position": [29, 21]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: Mengde tactical battle-map base\n"
        "Primary request: broad Taiyin mountain valley with a diagonal seven-cell-wide carriage road and wooded ambush slopes.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\n"
        "Constraints: no buildings, walls, units, text, UI, or visible grid.\n"
    )
    save_map("m093", "ch59a", image, rows, source, prompt,
             {"walls": set(), "gates": set(), "sites": set(), "regions": {"taiyin_road": [[8, 0], [42, 33]]}},
             deployments, {"type": "taiyin_coup", "capture": "JinLiGong58", "defeat_first": "XuTong59"})


def build_tu_estate() -> None:
    width, height = 48, 32
    rows = natural_rows(width, height)
    bounds = (12, 5, 39, 27)
    gates = {(24, 27), (25, 27)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    halls = {(x, y) for y in range(9, 14) for x in range(27, 35)}
    sites = {(30, 16)}
    for y in range(6, 27):
        for x in range(13, 39):
            rows[y][x] = "i"
    for x, y in halls:
        rows[y][x] = "h"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter50-taoyuan-base-gpt2.png"
    base = Image.open(ROOT / "output/imagegen" / source).convert("RGB")
    image = natural.cover_resize(base, (width * CELL, height * CELL))
    image = natural.natural_overlay(image, rows)
    courtyard = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(courtyard).rectangle((13 * CELL, 6 * CELL, 39 * CELL, 27 * CELL), fill=(130, 111, 83, 70))
    image = Image.alpha_composite(image, courtyard.filter(ImageFilter.GaussianBlur(7)))
    # Draw one continuous manor block and one continuous wall ring.
    hall_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(hall_layer)
    draw.rectangle((27 * CELL + 5, 9 * CELL + 8, 35 * CELL - 5, 14 * CELL - 5), fill=(121, 91, 63, 235), outline=(62, 47, 37, 255), width=4)
    draw.polygon([(27 * CELL - 6, 9 * CELL + 16), (31 * CELL, 8 * CELL + 20), (35 * CELL + 6, 9 * CELL + 16)], fill=(69, 76, 71, 250), outline=(35, 40, 38, 255))
    image = Image.alpha_composite(image, hall_layer.filter(ImageFilter.GaussianBlur(0.4)))
    structures.draw_walls(image, walls, bounds)
    structures.draw_sites(image, sites)
    deployments = [
        {"name": "HanJue48", "force": 1, "position": [21, 29]},
        {"name": "ZhaoWu59", "force": 1, "position": [28, 29]},
        {"name": "ChengYing59", "force": 2, "position": [30, 16]},
        {"name": "TuAnGu50", "force": 3, "position": [31, 11]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: Mengde tactical battle-map base\n"
        "Primary request: level ground reserved for a large Jin noble estate with a broad southern approach.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\n"
        "Constraints: no buildings, walls, gates, units, text, UI, or visible grid; estate structures are separate overlays.\n"
    )
    save_map("m094", "ch59b", image, rows, source, prompt,
             {"walls": walls, "gates": gates, "sites": sites, "gate_name": "tu_estate_south_gate",
              "regions": {"tu_estate": [[12, 5], [39, 27]], "main_hall": [[27, 9], [34, 13]]}},
             deployments, {"type": "zhao_restoration", "unlock_by": "ZhaoWu59", "historical_death": "TuAnGu50"})


if __name__ == "__main__":
    build_taiyin()
    build_tu_estate()
    print("chapter 59 maps generated: m093 52x34, m094 48x32")
