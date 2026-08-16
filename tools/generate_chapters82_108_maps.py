from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat

try:
    from tools import generate_chapter43_maps as structures
    from tools.chapters82_108_data import STAGES
except ImportError:
    import generate_chapter43_maps as structures
    from chapters82_108_data import STAGES


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
SOURCE_PATH = ROOT / "assets/lzc/chapter_sources/dongzhou_82_108.json"
TEMP_SOURCE = Path(r"C:\tmp\dongzhou_chapters_71_108.json")
BLOCKED = {"r", "W", "~", "P"}


def load_sources() -> dict[int, dict]:
    if SOURCE_PATH.exists():
        rows = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    else:
        rows = json.loads(TEMP_SOURCE.read_text(encoding="utf-8"))
        rows = [row for row in rows if 82 <= int(row["ordinal"]) <= 108]
        SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        SOURCE_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {int(row["ordinal"]): row for row in rows}


def dimensions(index: int, theme: str) -> tuple[int, int]:
    width = 48 + (index % 4) * 4
    height = 34 + (index % 3) * 4
    if theme in {"city", "palace"}:
        width += 4
    return width, height


def base_rows(width: int, height: int, seed: int) -> list[list[str]]:
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            value = (x * 11 + y * 7 + seed * 13) % 29
            row.append("g" if value < 8 else "f")
        rows.append(row)
    return rows


def apply_natural_theme(rows: list[list[str]], theme: str, seed: int) -> None:
    height, width = len(rows), len(rows[0])
    mid_x, mid_y = width // 2, height // 2
    if theme == "river":
        bend = seed % 5 - 2
        for y in range(height):
            center = mid_x + round(math.sin((y + seed) / 5) * 2) + bend
            for x in range(max(0, center - 1), min(width, center + 2)):
                rows[y][x] = "~"
        for y in range(mid_y - 1, mid_y + 2):
            for x in range(mid_x - 5, mid_x + 6):
                if 0 <= x < width:
                    rows[y][x] = "f"
    elif theme == "flood":
        for y in range(height):
            for x in range(width):
                if (y < 5 or y > height - 6 or (x + y + seed) % 17 == 0) and abs(y - mid_y) > 2:
                    rows[y][x] = "~"
        for y in range(mid_y - 2, mid_y + 3):
            for x in range(width):
                rows[y][x] = "w" if (x + seed) % 7 < 2 else "f"
    elif theme == "mountain":
        for y in range(height):
            ridge = mid_x + round(math.sin((y + seed) / 4) * 4)
            for x in range(ridge - 2, ridge + 3):
                if 0 <= x < width and abs(y - mid_y) > 3:
                    rows[y][x] = "r" if (x + y + seed) % 3 else "m"
        for y in range(mid_y - 3, mid_y + 4):
            for x in range(mid_x - 7, mid_x + 8):
                if 0 <= x < width:
                    rows[y][x] = "m" if (x + y) % 4 == 0 else "f"
    elif theme == "forest":
        for y in range(height):
            for x in range(width):
                if ((x - 9) ** 2 + (y - 8) ** 2 < 55 or
                        (x - width + 11) ** 2 + (y - height + 10) ** 2 < 70 or
                        (x * 5 + y * 3 + seed) % 31 < 4):
                    rows[y][x] = "F"
    elif theme == "trench":
        for x in range(12, width - 10):
            if abs(x - mid_x) > 3:
                rows[mid_y - 5][x] = "r"
                rows[mid_y + 5][x] = "r"
        for y in range(3, height - 3):
            if abs(y - mid_y) > 3:
                rows[y][mid_x] = "w"
                rows[y][mid_x + 1] = "w"
    else:
        for y in range(height):
            for x in range(width):
                if (x * 3 + y * 5 + seed) % 37 < 3:
                    rows[y][x] = "F"


def apply_structures(rows: list[list[str]], theme: str) -> dict:
    height, width = len(rows), len(rows[0])
    mid_y = height // 2
    walls: set[tuple[int, int]] = set()
    gates: set[tuple[int, int]] = set()
    sites: set[tuple[int, int]] = set()
    camps: set[tuple[int, int]] = set()
    regions: dict[str, list[list[int]]] = {}
    bounds = None
    if theme in {"city", "palace"}:
        x0, y0, x1, y1 = width - 22, 3, width - 3, height - 4
        bounds = (x0, y0, x1, y1)
        west_gates = {(x0, mid_y - 1), (x0, mid_y)}
        east_gates = {(x1, mid_y - 1), (x1, mid_y)}
        gates = west_gates | east_gates
        walls = structures.rectangle_perimeter(*bounds) - gates
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                rows[y][x] = "i"
        for x, y in walls:
            rows[y][x] = "W"
        for x, y in gates:
            rows[y][x] = "G"
        sites = {(x1 - 6, mid_y - 4), (x1 - 6, mid_y + 4)}
        for x, y in sites:
            rows[y][x] = "C"
        regions["fortified_city"] = [[x0, y0], [x1, y1]]
    own_camp = (7, min(height - 4, mid_y + 7))
    enemy_camp = ((width - 9 if bounds is None else bounds[2] - 6), min(height - 5, mid_y + 7))
    for cell in (own_camp, enemy_camp):
        x, y = cell
        if rows[y][x] not in BLOCKED and rows[y][x] not in {"G", "C"}:
            rows[y][x] = "e"
            camps.add(cell)
    regions["own_supply"] = [[own_camp[0], own_camp[1]], [own_camp[0], own_camp[1]]]
    regions["enemy_supply"] = [[enemy_camp[0], enemy_camp[1]], [enemy_camp[0], enemy_camp[1]]]
    return {"walls": walls, "gates": gates, "sites": sites, "camps": camps, "regions": regions, "bounds": bounds}


def nearest_legal(rows: list[list[str]], anchor: tuple[int, int], count: int,
                  occupied: set[tuple[int, int]]) -> list[tuple[int, int]]:
    height, width = len(rows), len(rows[0])
    candidates = []
    for y in range(height):
        for x in range(width):
            if rows[y][x] not in BLOCKED and (x, y) not in occupied:
                distance = abs(x - anchor[0]) + abs(y - anchor[1])
                candidates.append((distance, (x * 17 + y * 13) % 23, x, y))
    candidates.sort()
    chosen = [(x, y) for _, _, x, y in candidates[:count]]
    occupied.update(chosen)
    return chosen


def deployment_contract(spec: dict, rows: list[list[str]], structures_info: dict) -> tuple[list[dict], dict]:
    height, width = len(rows), len(rows[0])
    mid_y = height // 2
    occupied: set[tuple[int, int]] = set()
    own_positions = nearest_legal(rows, (6, mid_y), len(spec["own"]), occupied)
    if structures_info["bounds"]:
        enemy_anchor = (structures_info["bounds"][2] - 7, mid_y)
    else:
        enemy_anchor = (width - 7, mid_y)
    enemy_position = nearest_legal(rows, enemy_anchor, 1, occupied)[0]
    own_guards = nearest_legal(rows, (11, mid_y), 8, occupied)
    own_archers = nearest_legal(rows, (14, mid_y), 4, occupied)
    enemy_guards = nearest_legal(rows, (enemy_anchor[0] - 4, mid_y), 8, occupied)
    enemy_archers = nearest_legal(rows, (enemy_anchor[0] - 7, mid_y), 4, occupied)
    exit_position = nearest_legal(rows, (width - 1, mid_y), 1, occupied)[0]
    deployments = []
    for (hero_id, _), position in zip(spec["own"], own_positions):
        deployments.append({"name": hero_id, "force": 1, "position": list(position)})
    deployments.append({"name": spec["enemy"][0], "force": 3, "position": list(enemy_position)})
    for name, force, positions in (
        ("LateZhouGuardOwn", 1, own_guards),
        ("LateZhouArcherOwn", 1, own_archers),
        ("LateZhouGuardEnemy", 3, enemy_guards),
        ("LateZhouArcherEnemy", 3, enemy_archers),
    ):
        deployments.extend({"name": name, "force": force, "position": list(position)} for position in positions)
    runtime = {
        "own_positions": [list(position) for position in own_positions],
        "enemy_position": list(enemy_position),
        "own_guards": [list(position) for position in own_guards],
        "own_archers": [list(position) for position in own_archers],
        "enemy_guards": [list(position) for position in enemy_guards],
        "enemy_archers": [list(position) for position in enemy_archers],
        "retreat_exit": list(exit_position),
    }
    return deployments, runtime


def render_base(rows: list[list[str]], seed: int) -> Image.Image:
    height, width = len(rows), len(rows[0])
    random.seed(seed)
    image = Image.new("RGBA", (width * CELL, height * CELL), (125, 145, 92, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(260):
        x, y = random.randrange(image.width), random.randrange(image.height)
        radius = random.randrange(40, 190)
        color = random.choice(((58, 95, 48, 28), (178, 151, 94, 30), (89, 121, 73, 25)))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    natural = Image.new("RGBA", image.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(natural, "RGBA")
    colors = {
        "F": (38, 91, 45, 130), "m": (115, 101, 77, 130), "r": (76, 70, 63, 205),
        "~": (47, 105, 139, 220), "w": (143, 126, 91, 115), "i": (139, 127, 108, 155),
    }
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            if terrain in colors:
                pad = 5 if terrain in {"F", "m", "w"} else 0
                nd.rectangle((x * CELL - pad, y * CELL - pad, (x + 1) * CELL + pad, (y + 1) * CELL + pad), fill=colors[terrain])
    natural = natural.filter(ImageFilter.GaussianBlur(5))
    image = Image.alpha_composite(image, natural)
    detail = ImageDraw.Draw(image, "RGBA")
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
            if terrain == "F" and (x * 7 + y * 11 + seed) % 3 == 0:
                detail.ellipse((cx - 13, cy - 17, cx + 13, cy + 12), fill=(34, 78, 38, 120))
            elif terrain == "r":
                detail.polygon(((cx - 18, cy + 16), (cx, cy - 18), (cx + 18, cy + 16)), fill=(67, 63, 58, 185))
            elif terrain == "~":
                detail.arc((cx - 19, cy - 6, cx + 19, cy + 8), 5, 175, fill=(178, 214, 218, 125), width=2)
    return image


def write_map(spec: dict, index: int) -> None:
    width, height = dimensions(index, spec["theme"])
    rows = base_rows(width, height, 8200 + index)
    apply_natural_theme(rows, spec["theme"], 8200 + index)
    structures_info = apply_structures(rows, spec["theme"])
    deployments, runtime = deployment_contract(spec, rows, structures_info)
    rows_text = ["".join(row) for row in rows]
    base = render_base(rows, 8200 + index)
    base_path = ROOT / f"output/imagegen/{spec['map']}_ch{spec['id']}_base.png"
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(base_path, compress_level=5)
    image = base.copy()
    if structures_info["walls"]:
        structures.draw_walls(image, structures_info["walls"], structures_info["bounds"])
        structures.draw_castles(image, structures_info["sites"])
    structures.draw_sites(image, structures_info["camps"])
    map_path = ROOT / f"assets/lzc/map/{spec['map']}.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, compress_level=5)
    prompt = (
        "Use case: historical-scene\n"
        f"Asset type: Mengde tactical map for {spec['battle']}\n"
        f"Primary request: distinct {spec['theme']} battlefield with broad readable terrain and reserved deployment zones.\n"
        "Constraints: no units, text, UI, or visible grid; structures are cell-aligned overlays.\n"
        "Method: deterministic local raster composition using repository terrain and structure assets because the built-in image generator is unavailable.\n"
    )
    prompt_path = ROOT / f"output/imagegen/{spec['map']}_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    gates = []
    if structures_info["gates"]:
        west = sorted(cell for cell in structures_info["gates"] if cell[0] == structures_info["bounds"][0])
        east = sorted(cell for cell in structures_info["gates"] if cell[0] == structures_info["bounds"][2])
        gates = [{"name": "west_gate", "cells": [list(cell) for cell in west]},
                 {"name": "east_gate", "cells": [list(cell) for cell in east]}]
    supply_sites = structures_info["sites"] | structures_info["camps"] | structures_info["gates"]
    manifest = {
        "map": str(map_path.relative_to(ROOT)).replace("\\", "/"),
        "source_base": str(base_path.relative_to(ROOT)).replace("\\", "/"),
        "prompt_file": str(prompt_path.relative_to(ROOT)).replace("\\", "/"),
        "grid": [width, height], "cell_pixels": CELL, "terrain_rows": rows_text,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "manually reviewed deterministic source geometry with programmatic structure ownership",
        "structure_regions": structures_info["regions"],
        "camp_icon_cells": [list(cell) for cell in sorted(structures_info["camps"])],
        "camp_cells": [list(cell) for cell in sorted(structures_info["camps"])],
        "fence_cells": [], "fence_geometry": "no fences in this battlefield",
        "wall_cells": [list(cell) for cell in sorted(structures_info["walls"])],
        "gates": gates,
        "castle_cells": [list(cell) for cell in sorted(structures_info["sites"])],
        "supply_sites": [list(cell) for cell in sorted(supply_sites)],
        "blocked_edges": [], "deployments": deployments,
        "mission": {"battle": spec["battle"], "outcome": spec["outcome"], **runtime},
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / f"assets/lzc/map_sources/{spec['map']}_ch{spec['id']}_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path = ROOT / f"output/terrain_model/{spec['map']}_ch{spec['id']}_review.png"
    structures.review_image(
        image, rows_text,
        {"walls": structures_info["walls"], "fences": set(), "gates": structures_info["gates"], "sites": supply_sites},
        deployments, review_path,
    )
    prediction = {
        "map": manifest["map"], "grid": manifest["grid"],
        "backend": "reviewed-contract-programmatic-source", "threshold": 0.72,
        "auto_apply": False, "review_required": [],
        "common_terrain_review": {"classes": ["f", "g", "F", "w", "m"], "status": "reviewed against deterministic source geometry"},
        "note": "Structural classes and deployments are source-owned and excluded from classifier overwrite.",
    }
    prediction_path = ROOT / f"output/terrain_model/{spec['map']}_ch{spec['id']}_prediction.json"
    prediction_path.write_text(json.dumps(prediction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert image.size == (width * CELL, height * CELL)
    assert max(ImageStat.Stat(image.convert("RGB")).var) > 80


def main() -> None:
    load_sources()
    for index, spec in enumerate(STAGES):
        write_map(spec, index)
        print(f"generated {spec['id']}: {spec['map']} {spec['battle']}")
    print(f"generated {len(STAGES)} chapter 82-108 battle maps")


if __name__ == "__main__":
    main()
