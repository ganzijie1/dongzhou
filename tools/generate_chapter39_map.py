"""Build chapter 39's four-gate Cao capital battle map."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/imagegen"
MAP_ROOT = ROOT / "assets/lzc/map"
MANIFEST_ROOT = ROOT / "assets/lzc/map_sources"
REVIEW_ROOT = ROOT / "output/terrain_model"
CELL = 64
WIDTH, HEIGHT = 25, 19

PROMPT = """Use case: stylized-concept. Asset type: grid-free natural base environment for a Mengde / Ekgd Chinese historical tactical RPG battle map. Primary request: the rural outskirts around ancient Cao capital before any fortifications are composited. Scene/backdrop: broad spring grassland and compacted earth roads; a large completely level rectangular reserved area centered in the upper-middle for one sizeable walled city; four broad road approaches aligned from north, south, east, and west toward that reserved area; an old ancestral cemetery grove outside the future west wall; open military assembly ground outside every future gate; low forest belts and rocky foothills only around the far outer border. Style/medium: polished orthographic top-down late-1990s Chinese historical tactical RPG map, hand-painted pixel texture, natural soft terrain transitions, readable at 64 pixels per logical cell. Composition/framing: full-canvas landscape, no horizon, no visible grid. Constraints: absolutely no walls, gates, buildings, city structures, camps, fences, tombstones, units, carts, flags, fire, corpses, text, UI, labels, grid lines, tile seams, modern objects, or watermark. Keep the central reserved rectangle obstacle-free and keep all four road approaches continuous."""

CITY = {"left": 4, "right": 20, "top": 3, "bottom": 14}
NORTH_GATE = {(11, 3), (12, 3), (13, 3)}
SOUTH_GATE = {(11, 14), (12, 14), (13, 14)}
WEST_GATE = {(4, 7), (4, 8), (4, 9)}
EAST_GATE = {(20, 7), (20, 8), (20, 9)}
GATE_CELLS = NORTH_GATE | SOUTH_GATE | WEST_GATE | EAST_GATE

def cover(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    ratio = max(size[0] / source.width, size[1] / source.height)
    scaled = source.resize((round(source.width * ratio), round(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (scaled.width - size[0]) // 2
    top = (scaled.height - size[1]) // 2
    return scaled.crop((left, top, left + size[0], top + size[1]))

def terrain_rows() -> list[str]:
    grid = [["f" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x in {0, WIDTH - 1} or y in {0, HEIGHT - 1}:
                grid[y][x] = "m"
            elif x in {1, WIDTH - 2} or y in {1, HEIGHT - 2}:
                grid[y][x] = "F" if (x + y) % 3 else "m"
            elif (2 * x + y) % 9 < 2:
                grid[y][x] = "g"
    for y in range(CITY["top"], CITY["bottom"] + 1):
        for x in range(CITY["left"], CITY["right"] + 1):
            boundary = x in {CITY["left"], CITY["right"]} or y in {CITY["top"], CITY["bottom"]}
            grid[y][x] = "W" if boundary else "i"
    for x, y in GATE_CELLS:
        grid[y][x] = "G"
    grid[6][12] = "C"
    grid[5][7] = "h"
    grid[5][17] = "h"
    grid[11][7] = "b"
    grid[11][17] = "h"
    return ["".join(row) for row in grid]

def atlas_tile(source: Image.Image, x: int, y: int) -> Image.Image:
    return source.crop((x * 80, y * 80, (x + 1) * 80, (y + 1) * 80)).resize((CELL, CELL), Image.Resampling.LANCZOS)

def soften_city_ground(image: Image.Image) -> Image.Image:
    result = image.copy()
    box = ((CITY["left"] + 1) * CELL, (CITY["top"] + 1) * CELL, CITY["right"] * CELL, CITY["bottom"] * CELL)
    crop = result.crop(box)
    warm = Image.new("RGB", crop.size, (143, 127, 82))
    paved = Image.blend(ImageEnhance.Color(crop).enhance(0.55), warm, 0.34)
    paved = ImageEnhance.Contrast(paved).enhance(1.08)
    mask = Image.new("L", crop.size, 230).filter(ImageFilter.GaussianBlur(10))
    result.paste(paved, box, mask)
    return result

def add_structures(image: Image.Image, rows: list[str]) -> Image.Image:
    wall_source = Image.open(OUTPUT / "m010-real-walls-gpt2-aligned.png").convert("RGB")
    residence_source = Image.open(ROOT / "assets/lzc/map/m048.png").convert("RGB")
    tiles = {
        "top": atlas_tile(wall_source, 5, 0), "bottom": atlas_tile(wall_source, 5, 4),
        "left": atlas_tile(wall_source, 4, 2), "right": atlas_tile(wall_source, 14, 2),
        "tl": atlas_tile(wall_source, 4, 0), "tr": atlas_tile(wall_source, 14, 0),
        "bl": atlas_tile(wall_source, 4, 4), "br": atlas_tile(wall_source, 14, 4),
        "gate": atlas_tile(wall_source, 9, 4), "castle": atlas_tile(wall_source, 9, 0),
        "storehouse": atlas_tile(wall_source, 6, 2), "residence": atlas_tile(residence_source, 9, 1),
    }
    result = soften_city_ground(image)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            tile = None
            if char == "W":
                if y == CITY["top"]:
                    tile = tiles["tl"] if x == CITY["left"] else tiles["tr"] if x == CITY["right"] else tiles["top"]
                elif y == CITY["bottom"]:
                    tile = tiles["bl"] if x == CITY["left"] else tiles["br"] if x == CITY["right"] else tiles["bottom"]
                else:
                    tile = tiles["left"] if x == CITY["left"] else tiles["right"]
            elif char == "G":
                if y == CITY["top"]:
                    tile = tiles["gate"].rotate(180)
                elif y == CITY["bottom"]:
                    tile = tiles["gate"]
                elif x == CITY["left"]:
                    tile = tiles["gate"].rotate(90)
                else:
                    tile = tiles["gate"].rotate(270)
            elif char == "C":
                tile = tiles["castle"]
            elif char == "b":
                tile = tiles["storehouse"]
            elif char == "h":
                tile = tiles["residence"]
            if tile is not None:
                result.paste(tile, (x * CELL, y * CELL))
    draw = ImageDraw.Draw(result)
    for x, y in ((1, 7), (2, 8), (1, 10), (2, 11), (3, 12)):
        cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
        draw.rounded_rectangle((cx - 8, cy - 15, cx + 8, cy + 15), 3, fill=(108, 105, 84), outline=(67, 67, 57), width=2)
        draw.line((cx - 12, cy + 15, cx + 12, cy + 15), fill=(65, 64, 52), width=3)
    return result

def deployments() -> list[dict]:
    own = {
        "HuMao27": (10, 1), "HuYan27": (12, 1),
        "DianJie27": (1, 7), "ZhaoShuai27": (1, 9),
        "LuanZhi36": (23, 8), "XuChen27": (23, 9),
        "XianZhen27": (11, 16), "WeiChou27": (13, 16), "ChongEr27": (12, 17),
        "JinGuard39#N": (8, 1), "JinArcher39#N": (14, 1),
        "JinGuard39#W": (2, 8), "JinArcher39#E": (22, 8),
        "JinGuard39#S": (10, 16), "JinArcher39#S": (14, 16),
    }
    enemy = {
        "CaoGongGong39": (12, 6), "YuLang39": (12, 10),
        "CaoGateGuard39#N": (12, 3), "CaoGateGuard39#S": (12, 14),
        "CaoGateGuard39#W": (4, 8), "CaoGateGuard39#E": (20, 8),
        "CaoArcher39#N1": (10, 4), "CaoArcher39#N2": (14, 4),
        "CaoArcher39#S1": (10, 13), "CaoArcher39#S2": (14, 13),
        "CaoArcher39#W1": (5, 6), "CaoArcher39#W2": (5, 10),
        "CaoArcher39#E1": (19, 6), "CaoArcher39#E2": (19, 10),
    }
    result = [{"name": name, "force": 1, "position": list(pos)} for name, pos in own.items()]
    result += [{"name": name, "force": 3, "position": list(pos)} for name, pos in enemy.items()]
    result.append({"name": "XiFuJi39", "force": 2, "position": [7, 5]})
    return result

def main() -> None:
    rows = terrain_rows()
    size = WIDTH * CELL, HEIGHT * CELL
    source = Image.open(OUTPUT / "chapter39-cao-base-gpt2.png").convert("RGB")
    image = ImageEnhance.Contrast(cover(source, size)).enhance(1.06)
    image = add_structures(image, rows)
    MAP_ROOT.mkdir(parents=True, exist_ok=True)
    image.save(MAP_ROOT / "m063.png", "PNG", compress_level=3)

    wall_cells = [[x, y] for y, row in enumerate(rows) for x, char in enumerate(row) if char == "W"]
    gates = [
        {"name": "north_gate", "cells": [list(cell) for cell in sorted(NORTH_GATE)]},
        {"name": "south_gate", "cells": [list(cell) for cell in sorted(SOUTH_GATE)]},
        {"name": "west_gate", "cells": [list(cell) for cell in sorted(WEST_GATE)]},
        {"name": "east_gate", "cells": [list(cell) for cell in sorted(EAST_GATE)]},
    ]
    supply_sites = [list(cell) for cell in sorted(GATE_CELLS)] + [[12, 6], [7, 11]]
    manifest = {
        "map": "assets/lzc/map/m063.png", "source_base": "output/imagegen/chapter39-cao-base-gpt2.png",
        "prompt_file": "output/imagegen/m063_prompt.txt", "grid": [WIDTH, HEIGHT], "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [], "terrain_source": "manually reviewed programmatic source of truth with aligned structures",
        "structure_regions": {"cao_city": [[CITY["left"], CITY["top"]], [CITY["right"], CITY["bottom"]]]},
        "camp_icon_cells": [], "camp_cells": [], "fence_cells": [], "fence_geometry": "none",
        "wall_cells": wall_cells, "gates": gates, "supply_sites": supply_sites,
        "blocked_edges": [], "deployments": deployments(), "visual_grid_in_game": False, "prompt": PROMPT,
    }
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    (MANIFEST_ROOT / "m063_ch39_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "m063_prompt.txt").write_text(PROMPT, encoding="utf-8")

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(WIDTH + 1):
        draw.line((x * CELL, 0, x * CELL, size[1]), fill=(255, 255, 255, 105), width=1)
    for y in range(HEIGHT + 1):
        draw.line((0, y * CELL, size[0], y * CELL), fill=(255, 255, 255, 105), width=1)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            draw.text((x * CELL + 3, y * CELL + 2), f"{x},{y} {char}", fill=(255, 245, 180, 240))
    for item in deployments():
        x, y = item["position"]
        color = (255, 70, 70, 255) if item["force"] == 3 else (255, 220, 70, 255) if item["force"] == 2 else (70, 220, 255, 255)
        draw.ellipse((x * CELL + 18, y * CELL + 18, x * CELL + 46, y * CELL + 46), outline=color, width=3)
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image.convert("RGBA"), overlay).save(REVIEW_ROOT / "m063_ch39_review.png")

if __name__ == "__main__":
    main()
