"""Build chapter 36's Linghu assault and Jiang palace-fire maps."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, CELL = 21, 15, 64
SIZE = (WIDTH * CELL, HEIGHT * CELL)
OUTPUT = ROOT / "output/imagegen"
MAP_ROOT = ROOT / "assets/lzc/map"
MANIFEST_ROOT = ROOT / "assets/lzc/map_sources"
REVIEW_ROOT = ROOT / "output/terrain_model"

LINGHU_PROMPT = """Use case: stylized-concept. Asset type: grid-free base environment for a Chinese historical turn-based tactical RPG battlefield. Primary request: the winter approach to ancient Linghu city beside the Yellow River, before any fortifications are composited. Scene: broad dry grassland and packed-earth roads, a clear south-to-north assault avenue, subtle frozen riverbank gravel on the lower-left edge, sparse leafless trees and low rocky hills only near outer corners, a large level open plateau reserved across the upper-center for a walled city overlay. Style: polished orthographic top-down late-1990s Chinese historical tactical RPG map, hand-painted pixel texture, natural soft terrain transitions, readable at 48 pixels per logical cell. Composition: landscape, no perspective horizon, no dominant object, generous continuous traversable ground. Constraints: absolutely no city walls, gates, buildings, camps, fences, tents, units, text, UI, labels, or visible grid lines; no square tile seams; no modern objects; no watermark."""

JIANG_PROMPT = """Use case: stylized-concept. Asset type: grid-free base environment for a Chinese historical turn-based tactical RPG battlefield. Primary request: the ground plane of ancient Jiang capital at night during a palace conspiracy, before structures are composited. Scene: broad dark stone-paved avenues mixed with compacted earth courtyards, muted winter grass at the outer edges, a straight southern approach road, a large level rectangular central-north area reserved for a palace wall overlay, scattered drainage channels and bare ornamental trees outside the reserved area. Style: polished orthographic top-down late-1990s Chinese historical tactical RPG map, hand-painted pixel texture, cool moonlit blue-gray palette with warm reflected firelight hints, natural transitions and clear movement surfaces readable at 48 pixels per cell. Composition: landscape, no perspective horizon, no dominant object. Constraints: absolutely no palace, walls, gates, houses, fires, camps, fences, tents, units, text, UI, labels, or visible grid lines; no square tile seams; no modern objects; no watermark."""


def cover(source: Image.Image) -> Image.Image:
    ratio = max(SIZE[0] / source.width, SIZE[1] / source.height)
    scaled = source.resize((round(source.width * ratio), round(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (scaled.width - SIZE[0]) // 2
    top = (scaled.height - SIZE[1]) // 2
    return scaled.crop((left, top, left + SIZE[0], top + SIZE[1]))


def linghu_rows() -> list[str]:
    grid = [["f" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            edge = min(x, WIDTH - 1 - x)
            if edge <= 1 and y < 11:
                grid[y][x] = "m"
            elif edge <= 3 and y < 10:
                grid[y][x] = "F"
            elif (x + 2 * y) % 7 < 2:
                grid[y][x] = "g"
    for x in range(4, 17):
        grid[1][x] = "W"
        grid[8][x] = "G" if x in {9, 10, 11} else "W"
    for y in range(2, 8):
        grid[y][4] = grid[y][16] = "W"
        for x in range(5, 16):
            grid[y][x] = "i"
    grid[3][6] = grid[3][14] = "h"
    grid[3][10] = "C"
    grid[6][6] = "b"
    return ["".join(row) for row in grid]


def jiang_rows() -> list[str]:
    grid = [["g" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(1, 14):
        for x in range(2, 19):
            grid[y][x] = "i"
    for y in range(HEIGHT):
        if y in {0, 14}:
            for x in range(WIDTH):
                grid[y][x] = "F" if 2 <= x <= 18 else "m"
        else:
            grid[y][0] = grid[y][20] = "F"
    for x in range(5, 16):
        grid[2][x] = "W"
        grid[9][x] = "G" if x in {9, 10, 11} else "W"
    for y in range(3, 9):
        grid[y][5] = grid[y][15] = "W"
    grid[4][10] = "C"
    for position in ((7, 5), (13, 5), (7, 7), (13, 7)):
        grid[position[1]][position[0]] = "h"
    grid[4][3] = grid[4][17] = "b"
    return ["".join(row) for row in grid]


def atlas_tile(source: Image.Image, x: int, y: int) -> Image.Image:
    tile = source.crop((x * 80, y * 80, (x + 1) * 80, (y + 1) * 80))
    return tile.resize((CELL, CELL), Image.Resampling.LANCZOS)


def paste_structures(image: Image.Image, rows: list[str], top: int, bottom: int, burning: bool) -> Image.Image:
    wall_source = Image.open(OUTPUT / "m010-real-walls-gpt2-aligned.png").convert("RGB")
    palace_source = Image.open(ROOT / "assets/lzc/map/m048.png").convert("RGB")
    residence = atlas_tile(palace_source, 9, 1)
    tiles = {
        "top": atlas_tile(wall_source, 5, 0), "bottom": atlas_tile(wall_source, 5, 4),
        "left": atlas_tile(wall_source, 4, 2), "right": atlas_tile(wall_source, 14, 2),
        "tl": atlas_tile(wall_source, 4, 0), "tr": atlas_tile(wall_source, 14, 0),
        "bl": atlas_tile(wall_source, 4, 4), "br": atlas_tile(wall_source, 14, 4),
        "gate": atlas_tile(wall_source, 9, 4), "castle": atlas_tile(wall_source, 9, 0),
        "storehouse": atlas_tile(wall_source, 6, 2), "residence": residence,
    }
    result = image.copy()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            tile = None
            if char == "W":
                if y == top:
                    tile = tiles["tl"] if x == 4 + (1 if burning else 0) else tiles["tr"] if x == 16 - (1 if burning else 0) else tiles["top"]
                elif y == bottom:
                    tile = tiles["bl"] if x == 4 + (1 if burning else 0) else tiles["br"] if x == 16 - (1 if burning else 0) else tiles["bottom"]
                else:
                    tile = tiles["left"] if x <= 5 else tiles["right"]
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

    if burning:
        flames = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(flames)
        for x, y in ((7, 5), (13, 5), (7, 7), (13, 7), (10, 4)):
            cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
            draw.ellipse((cx - 22, cy - 12, cx + 22, cy + 25), fill=(255, 95, 22, 80))
            draw.polygon([(cx - 14, cy + 17), (cx - 5, cy - 28), (cx + 3, cy - 8), (cx + 13, cy - 35), (cx + 18, cy + 18)], fill=(255, 112, 24, 225))
            draw.polygon([(cx - 6, cy + 15), (cx + 1, cy - 16), (cx + 9, cy + 15)], fill=(255, 224, 92, 240))
        result = Image.alpha_composite(result.convert("RGBA"), flames.filter(ImageFilter.GaussianBlur(0.7))).convert("RGB")
    return result


def render(name: str, source_name: str, rows: list[str], top: int, bottom: int, prompt: str, deployments: list[dict], gates: list[list[int]], sites: list[list[int]], burning: bool) -> None:
    image = cover(Image.open(OUTPUT / source_name).convert("RGB"))
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Color(image).enhance(0.94 if burning else 1.02)
    image = paste_structures(image, rows, top, bottom, burning)
    MAP_ROOT.mkdir(parents=True, exist_ok=True)
    destination = MAP_ROOT / f"{name}.png"
    image.save(destination, "PNG", compress_level=3)

    wall_cells = [[x, y] for y, row in enumerate(rows) for x, char in enumerate(row) if char == "W"]
    camp_cells = [[x, y] for y, row in enumerate(rows) for x, char in enumerate(row) if char == "e"]
    manifest = {
        "map": f"assets/lzc/map/{name}.png", "source_base": f"output/imagegen/{source_name}",
        "prompt_file": f"output/imagegen/{name}_prompt.txt", "grid": [WIDTH, HEIGHT], "cell_pixels": CELL,
        "terrain_rows": rows, "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [], "terrain_source": "manually reviewed source-of-truth matrix with aligned structure overlays",
        "structure_regions": {"fortification": [[4 + (1 if burning else 0), top], [16 - (1 if burning else 0), bottom]]},
        "camp_icon_cells": camp_cells, "camp_cells": camp_cells, "fence_cells": [],
        "fence_geometry": "none", "gates": [{"name": "south_gate", "cells": gates}],
        "supply_sites": sites, "blocked_edges": [], "deployments": deployments,
        "visual_grid_in_game": False, "prompt": prompt,
    }
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    (MANIFEST_ROOT / f"{name}_ch36_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / f"{name}_prompt.txt").write_text(prompt, encoding="utf-8")

    review = image.convert("RGBA")
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(WIDTH + 1): draw.line((x * CELL, 0, x * CELL, SIZE[1]), fill=(255, 255, 255, 120), width=1)
    for y in range(HEIGHT + 1): draw.line((0, y * CELL, SIZE[0], y * CELL), fill=(255, 255, 255, 120), width=1)
    for y, row in enumerate(rows):
        for x, char in enumerate(row): draw.text((x * CELL + 3, y * CELL + 2), f"{x},{y} {char}", fill=(255, 245, 180, 240))
    for item in deployments:
        x, y = item["position"]
        draw.ellipse((x * CELL + 18, y * CELL + 18, x * CELL + 46, y * CELL + 46), outline=(255, 50, 50, 255) if item["force"] == 3 else (60, 220, 255, 255), width=3)
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(review, overlay).save(REVIEW_ROOT / f"{name}_ch36_review.png")


def main() -> None:
    render("m059", "chapter36-linghu-base-gpt2.png", linghu_rows(), 1, 8, LINGHU_PROMPT,
           [{"name": "PiBao36", "force": 1, "position": [10, 12]}, {"name": "DengHun36", "force": 3, "position": [10, 3]}],
           [[9, 8], [10, 8], [11, 8]], [[10, 3], [6, 6], [9, 8], [10, 8], [11, 8]], False)
    render("m060", "chapter36-jiang-palace-base-gpt2.png", jiang_rows(), 2, 9, JIANG_PROMPT,
           [{"name": "ZhaoShuai27", "force": 1, "position": [9, 13]}, {"name": "LvSheng36", "force": 3, "position": [9, 6]}, {"name": "XiRui36", "force": 3, "position": [11, 6]}],
           [[9, 9], [10, 9], [11, 9]], [[10, 4], [3, 4], [17, 4], [9, 9], [10, 9], [11, 9]], True)
    print(MAP_ROOT / "m059.png", MAP_ROOT / "m060.png", SIZE)


if __name__ == "__main__":
    main()
