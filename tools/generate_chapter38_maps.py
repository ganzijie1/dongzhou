"""Build chapter 38's Wangcheng escape and combined Wen-Yuan maps."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/imagegen"
MAP_ROOT = ROOT / "assets/lzc/map"
MANIFEST_ROOT = ROOT / "assets/lzc/map_sources"
REVIEW_ROOT = ROOT / "output/terrain_model"
CELL = 64

WANGCHENG_PROMPT = """Use case: stylized-concept. Asset type: grid-free base environment for a Chinese historical turn-based tactical RPG battlefield. Primary request: ancient Zhou royal capital outskirts during a civil-war evacuation, before any city structures are composited. Scene: broad packed-earth roads and muted spring grass, a large level rectangular plateau reserved in the upper-center for a walled royal city overlay, a clear winding escape road leading from that plateau toward the southeast edge, scattered low forest and rocky foothills only along outer borders, open maneuver ground outside the future south gate. Style: polished orthographic top-down late-1990s Chinese historical tactical RPG map, hand-painted pixel texture, natural soft terrain transitions, readable at 64 pixels per logical cell. Composition: landscape, no horizon, generous continuous traversable route to the southeast. Constraints: absolutely no walls, gates, buildings, camps, fences, tents, units, fire, text, UI, labels, or visible grid lines; no tile seams; no modern objects; no watermark."""

WEN_PROMPT = """Use case: stylized-concept. Asset type: grid-free base environment for a Chinese historical turn-based tactical RPG battlefield. Primary request: ancient Wen city and its surrounding basin during a spring punitive campaign, before fortifications are composited. Scene: broad dry-grass basin with compacted earth roads, two separated level reserved areas across the upper half for two walled towns, straight southern approaches with open cavalry ground, shallow gullies and sparse orchards near outer flanks, low foothills only at far corners. Style: polished orthographic top-down late-1990s Chinese historical tactical RPG map, hand-painted pixel texture, natural transitions, readable at 64 pixels per logical cell. Constraints: no walls, gates, buildings, camps, fences, tents, units, fire, text, UI, labels, grid lines, tile seams, modern objects, or watermark."""


def cover(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    ratio = max(size[0] / source.width, size[1] / source.height)
    scaled = source.resize((round(source.width * ratio), round(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (scaled.width - size[0]) // 2
    top = (scaled.height - size[1]) // 2
    return scaled.crop((left, top, left + size[0], top + size[1]))


def city(grid: list[list[str]], left: int, right: int, top: int, bottom: int,
         gate_xs: set[int], castle: tuple[int, int], closed: bool = False) -> None:
    for x in range(left, right + 1):
        grid[top][x] = "W"
        grid[bottom][x] = "W" if closed or x not in gate_xs else "G"
    for y in range(top + 1, bottom):
        grid[y][left] = grid[y][right] = "W"
        for x in range(left + 1, right):
            grid[y][x] = "i"
    grid[castle[1]][castle[0]] = "C"
    grid[top + 3][left + 2] = "h"
    grid[top + 3][right - 2] = "h"
    grid[top + 5][left + 2] = "b"


def wangcheng_rows() -> list[str]:
    width, height = 23, 16
    grid = [["f" for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if x <= 1 or x >= 21:
                grid[y][x] = "m" if y < 11 else "F"
            elif (x + 2 * y) % 8 < 2:
                grid[y][x] = "g"
    city(grid, 4, 18, 1, 9, {10, 11, 12}, (11, 4))
    return ["".join(row) for row in grid]


def wen_yuan_rows() -> list[str]:
    width, height = 27, 17
    grid = [["f" for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if x in {0, 26}:
                grid[y][x] = "m"
            elif x in {1, 25} and y > 10:
                grid[y][x] = "F"
            elif (2 * x + y) % 9 < 2:
                grid[y][x] = "g"
    city(grid, 1, 11, 1, 9, {5, 6, 7}, (6, 4))
    city(grid, 15, 25, 1, 9, {19, 20, 21}, (20, 4), closed=True)
    return ["".join(row) for row in grid]


def atlas_tile(source: Image.Image, x: int, y: int) -> Image.Image:
    return source.crop((x * 80, y * 80, (x + 1) * 80, (y + 1) * 80)).resize(
        (CELL, CELL), Image.Resampling.LANCZOS
    )


def structures(image: Image.Image, rows: list[str], cities: list[dict]) -> Image.Image:
    source = Image.open(OUTPUT / "m010-real-walls-gpt2-aligned.png").convert("RGB")
    palace = Image.open(ROOT / "assets/lzc/map/m048.png").convert("RGB")
    tiles = {
        "top": atlas_tile(source, 5, 0), "bottom": atlas_tile(source, 5, 4),
        "left": atlas_tile(source, 4, 2), "right": atlas_tile(source, 14, 2),
        "tl": atlas_tile(source, 4, 0), "tr": atlas_tile(source, 14, 0),
        "bl": atlas_tile(source, 4, 4), "br": atlas_tile(source, 14, 4),
        "gate": atlas_tile(source, 9, 4), "castle": atlas_tile(source, 9, 0),
        "storehouse": atlas_tile(source, 6, 2), "residence": atlas_tile(palace, 9, 1),
    }
    result = image.copy()
    city_by_cell = {}
    for spec in cities:
        for y in range(spec["top"], spec["bottom"] + 1):
            for x in range(spec["left"], spec["right"] + 1):
                city_by_cell[(x, y)] = spec
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            spec = city_by_cell.get((x, y))
            tile = None
            if char == "W" and spec is not None:
                if y == spec["top"]:
                    tile = tiles["tl"] if x == spec["left"] else tiles["tr"] if x == spec["right"] else tiles["top"]
                elif y == spec["bottom"]:
                    if spec.get("closed_gate") and x in spec["closed_gate"]:
                        tile = tiles["gate"].copy()
                        draw = ImageDraw.Draw(tile)
                        draw.rectangle((8, 28, CELL - 8, CELL - 8), fill=(74, 48, 31), outline=(35, 24, 18), width=3)
                    else:
                        tile = tiles["bl"] if x == spec["left"] else tiles["br"] if x == spec["right"] else tiles["bottom"]
                else:
                    tile = tiles["left"] if x == spec["left"] else tiles["right"]
            elif char == "G":
                tile = tiles["gate"]
            elif char == "C":
                tile = tiles["castle"]
            elif char == "b":
                tile = tiles["storehouse"]
            elif char == "h":
                tile = tiles["residence"]
            if tile is not None:
                result.paste(tile, (x * CELL, y * CELL))
    return result


def render(name: str, source_name: str, rows: list[str], prompt: str, cities: list[dict],
           gates: list[dict], sites: list[list[int]], deployments: list[dict]) -> None:
    width, height = len(rows[0]), len(rows)
    size = width * CELL, height * CELL
    image = ImageEnhance.Contrast(cover(Image.open(OUTPUT / source_name).convert("RGB"), size)).enhance(1.07)
    image = structures(image, rows, cities)
    MAP_ROOT.mkdir(parents=True, exist_ok=True)
    image.save(MAP_ROOT / f"{name}.png", "PNG", compress_level=3)

    walls = [[x, y] for y, row in enumerate(rows) for x, char in enumerate(row) if char == "W"]
    manifest = {
        "map": f"assets/lzc/map/{name}.png", "source_base": f"output/imagegen/{source_name}",
        "prompt_file": f"output/imagegen/{name}_prompt.txt", "grid": [width, height], "cell_pixels": CELL,
        "terrain_rows": rows, "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [], "terrain_source": "manually reviewed source-of-truth matrix with aligned structures",
        "structure_regions": {item["name"]: [[item["left"], item["top"]], [item["right"], item["bottom"]]] for item in cities},
        "camp_icon_cells": [], "camp_cells": [], "fence_cells": [], "fence_geometry": "none",
        "wall_cells": walls, "gates": gates, "supply_sites": sites, "blocked_edges": [],
        "deployments": deployments, "visual_grid_in_game": False, "prompt": prompt,
    }
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    (MANIFEST_ROOT / f"{name}_ch38_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUTPUT / f"{name}_prompt.txt").write_text(prompt, encoding="utf-8")

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(width + 1):
        draw.line((x * CELL, 0, x * CELL, size[1]), fill=(255, 255, 255, 110), width=1)
    for y in range(height + 1):
        draw.line((0, y * CELL, size[0], y * CELL), fill=(255, 255, 255, 110), width=1)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            draw.text((x * CELL + 3, y * CELL + 2), f"{x},{y} {char}", fill=(255, 245, 180, 240))
    for item in deployments:
        x, y = item["position"]
        color = (255, 60, 60, 255) if item["force"] == 3 else (60, 220, 255, 255)
        draw.ellipse((x * CELL + 18, y * CELL + 18, x * CELL + 46, y * CELL + 46), outline=color, width=3)
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image.convert("RGBA"), overlay).save(REVIEW_ROOT / f"{name}_ch38_review.png")


def main() -> None:
    wangcheng = [{"name": "wangcheng", "left": 4, "right": 18, "top": 1, "bottom": 9}]
    render(
        "m061", "chapter38-wangcheng-base-gpt2.png", wangcheng_rows(), WANGCHENG_PROMPT, wangcheng,
        [{"name": "south_gate", "cells": [[10, 9], [11, 9], [12, 9]]}],
        [[11, 4], [6, 6], [10, 9], [11, 9], [12, 9]],
        [{"name": "ZhouXiangWang38", "force": 1, "position": [11, 4]}, {"name": "ChiDing38", "force": 3, "position": [11, 12]}],
    )
    cities = [
        {"name": "wen_city", "left": 1, "right": 11, "top": 1, "bottom": 9},
        {"name": "yuan_city", "left": 15, "right": 25, "top": 1, "bottom": 9, "closed_gate": {19, 20, 21}},
    ]
    render(
        "m062", "chapter38-wen-base-gpt2.png", wen_yuan_rows(), WEN_PROMPT, cities,
        [{"name": "wen_south_gate", "cells": [[5, 9], [6, 9], [7, 9]]}],
        [[6, 4], [3, 6], [5, 9], [6, 9], [7, 9], [20, 4], [17, 6]],
        [
            {"name": "WeiChou27", "force": 1, "position": [7, 14]},
            {"name": "TaiShuDai38", "force": 3, "position": [6, 4]},
            {"name": "WeiHou38", "force": 3, "position": [4, 4]},
            {"name": "YuanBoGuan38", "force": 3, "position": [20, 4]},
            {"name": "YuanGuard38", "force": 3, "position": [18, 5]},
            {"name": "YuanGuard38", "force": 3, "position": [22, 5]},
            {"name": "YuanGuard38", "force": 3, "position": [19, 8]},
            {"name": "YuanGuard38", "force": 3, "position": [21, 8]},
            {"name": "YuanArcher38", "force": 3, "position": [17, 7]},
            {"name": "YuanArcher38", "force": 3, "position": [23, 7]},
        ],
    )


if __name__ == "__main__":
    main()
