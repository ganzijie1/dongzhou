"""Build the large Queshan map from a clean terrain base plus aligned overlays.

The terrain matrix is the source of truth. Center-axis fences own complete
impassable cells; gates are created by omitting fence cells from the ring.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output" / "imagegen" / "queshan-large-base-gpt2.png"
MAP_OUT = ROOT / "assets" / "lzc" / "map" / "m008-large-v2.png"
REVIEW_OUT = ROOT / "output" / "terrain_model" / "m008_large_v2_review.png"
MANIFEST_OUT = ROOT / "output" / "terrain_model" / "m008_large_v2_manifest.json"
FENCE_H_OUT = ROOT / "assets" / "lzc" / "terrain" / "fence-queshan-horizontal.png"
FENCE_V_OUT = ROOT / "assets" / "lzc" / "terrain" / "fence-queshan-vertical.png"
CAMP_TILE = ROOT / "assets" / "lzc" / "map_sources" / "changshao" / "camp.png"

WIDTH, HEIGHT, CELL = 30, 22, 48
NATURAL_TERRAINS = {"f", "g", "F", "w", "m"}
RIGHT_BOTTOM_MOUNTAIN_START = {18: 26, 19: 24, 20: 22, 21: 20}
REVIEWED_TERRAIN_ROWS = (
    "FFFmFFFFFFFFFFFFFFFFFFFFFFFmFF",
    "FFFmmFFFffffFFFFFFFFFFFFFFFFmF",
    "FFFmmmFFFffffFfFFFFFFFFFFFFFmF",
    "FmFmmmmffffffffffFFffFFFFFFFFF",
    "mFmmmmmFFffffffffffffFfffffFmF",
    "FmmmmmmFfffffffffffffffffffFmF",
    "mFmmmmmfFfffffffffffffffffffmF",
    "mmFmmmfFffffffffffffffPPPPPPPF",
    "mFmmFfFfffffffffffffffPwwwwwPm",
    "mFFmFFffffffffffffffffPwewewPF",
    "FmFmFffffffffffffffffffwwewwPF",
    "FFmFmffffffffffffffffffwwwwwPF",
    "FmmFFfffffffffffffffffPwewewPF",
    "FFmmFFffffffffffffffffPPPPPPPF",
    "FFFFFfffffffffffffffffffffFffF",
    "FFFFFffffffffffffffffffffffFFF",
    "FFFFfffffffPPPffPPPfffffFffFFF",
    "FFFfFFfffffPwwwwwwPffffffffFFF",
    "FmFmmffffffPwewwwePffffffffffF",
    "FFmFfmfffffPwwwewwPffFfffffffF",
    "FFFFFFFFFFfPwewwwePFFFFFFFFFFF",
    "FFFFFFFFFFFPPPPPPPPFFFFFFFFFFF",
)
SOUTH_ENCLOSURE = {(x, y) for y in range(17, 21) for x in range(12, 18)}
EAST_ENCLOSURE = {(x, y) for y in range(8, 13) for x in range(23, 28)}
SOUTH_CAMP = {(15, 19), (13, 18), (17, 18), (13, 20), (17, 20)}
EAST_CAMP = {(25, 10), (24, 9), (26, 9), (24, 12), (26, 12)}
CAMPS = SOUTH_CAMP | EAST_CAMP
CAMP_GROUND = (SOUTH_ENCLOSURE | EAST_ENCLOSURE) - CAMPS
SITES = set(CAMPS)
SOUTH_GATE_CELLS = {(14, 16), (15, 16)}
EAST_GATE_CELLS = {(22, 10), (22, 11)}
GATE_CELLS = SOUTH_GATE_CELLS | EAST_GATE_CELLS
SOUTH_FENCE = (
    {(x, 16) for x in range(11, 19)}
    | {(x, 21) for x in range(11, 19)}
    | {(11, y) for y in range(17, 21)}
    | {(18, y) for y in range(17, 21)}
) - SOUTH_GATE_CELLS
EAST_FENCE = (
    {(x, 7) for x in range(22, 29)}
    | {(x, 13) for x in range(22, 29)}
    | {(22, y) for y in range(8, 13)}
    | {(28, y) for y in range(8, 13)}
) - EAST_GATE_CELLS
FENCES = SOUTH_FENCE | EAST_FENCE
CORNER_DIRECTIONS = {
    (11, 16): {"right", "down"}, (18, 16): {"left", "down"},
    (11, 21): {"right", "up"}, (18, 21): {"left", "up"},
    (22, 7): {"right", "down"}, (28, 7): {"left", "down"},
    (22, 13): {"right", "up"}, (28, 13): {"left", "up"},
}


def terrain_rows() -> list[str]:
    assert len(REVIEWED_TERRAIN_ROWS) == HEIGHT
    assert all(len(row) == WIDTH for row in REVIEWED_TERRAIN_ROWS)
    cells = [list(row) for row in REVIEWED_TERRAIN_ROWS]

    for x, y in CAMP_GROUND:
        cells[y][x] = "w"
    for x, y in CAMPS:
        cells[y][x] = "e"
    for x, y in FENCES:
        cells[y][x] = "P"
    return ["".join(row) for row in cells]

def terrain_layers() -> list[dict]:
    """Reviewed natural-terrain boundary cells using secondary coverage 0..255."""
    rows = terrain_rows()
    structures = FENCES | CAMPS | CAMP_GROUND | GATE_CELLS
    layers: dict[tuple[int, int], dict] = {}

    def add(x: int, y: int, secondary: str, coverage: int) -> None:
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or (x, y) in structures:
            return
        primary = rows[y][x]
        assert primary in NATURAL_TERRAINS
        assert secondary in NATURAL_TERRAINS and secondary != primary
        assert 1 <= coverage <= 255
        layers[(x, y)] = {
            "position": [x, y],
            "primary_terrain": primary,
            "secondary_terrain": secondary,
            "coverage": coverage,
        }

    # Full-map review found interleaved forest, exposed ridge, and open ground.
    # Store a secondary class only at their visible four-neighbor transitions.
    common = {"f", "F", "m"}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            primary = rows[y][x]
            if primary not in common:
                continue
            neighbors = [
                rows[ny][nx]
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT
                and rows[ny][nx] in common and rows[ny][nx] != primary
            ]
            if neighbors:
                secondary = max(
                    sorted(set(neighbors)),
                    key=lambda value: (neighbors.count(value), value),
                )
                add(x, y, secondary, 72)

    return [layers[key] for key in sorted(layers, key=lambda p: (p[1], p[0]))]


def blocked_edges() -> list[tuple[tuple[int, int], tuple[int, int]]]:
    # Cell-centered fences use terrain collision, not edge collision.
    return []


def cover_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_ratio = size[0] / size[1]
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    else:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize(size, Image.Resampling.LANCZOS)


def rounded_camp_ground(image: Image.Image, cells: set[tuple[int, int]]) -> None:
    min_x = min(x for x, _ in cells) * CELL
    max_x = (max(x for x, _ in cells) + 1) * CELL
    min_y = min(y for _, y in cells) * CELL
    max_y = (max(y for _, y in cells) + 1) * CELL
    pad = 7
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((min_x + pad, min_y + pad, max_x - pad, max_y - pad), 18, fill=205)
    mask = mask.filter(ImageFilter.GaussianBlur(9))
    rng = random.Random(min_x * 97 + min_y)
    ground = Image.new("RGB", image.size, (116, 101, 65))
    noise = Image.new("L", image.size, 0)
    noise_pixels = noise.load()
    for y in range(max(0, min_y - 16), min(image.height, max_y + 16)):
        for x in range(max(0, min_x - 16), min(image.width, max_x + 16)):
            noise_pixels[x, y] = rng.randrange(18, 57)
    tint = Image.new("RGB", image.size, (150, 132, 84))
    ground = Image.composite(tint, ground, noise)
    image.paste(ground, (0, 0), mask)


def make_fence_sprites() -> tuple[Image.Image, Image.Image]:
    scale = 4
    sprite = Image.new("RGBA", (CELL * scale, 16 * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    wood_dark = (65, 43, 25, 255)
    wood = (119, 79, 42, 255)
    wood_light = (167, 119, 65, 255)
    shadow = (28, 23, 18, 100)
    draw.rounded_rectangle((3 * scale, 11 * scale, 45 * scale, 15 * scale), 2 * scale, fill=shadow)
    for px in (5, 24, 43):
        draw.polygon([
            (px * scale, 1 * scale), ((px + 3) * scale, 5 * scale),
            ((px + 3) * scale, 14 * scale), ((px - 3) * scale, 14 * scale),
            ((px - 3) * scale, 5 * scale),
        ], fill=wood_dark)
        draw.polygon([
            (px * scale, 2 * scale), ((px + 2) * scale, 5 * scale),
            ((px + 1) * scale, 13 * scale), ((px - 1) * scale, 13 * scale),
            ((px - 1) * scale, 5 * scale),
        ], fill=wood)
        draw.line(((px - 1) * scale, 5 * scale, px * scale, 12 * scale), fill=wood_light, width=scale)
    for py in (6, 10):
        draw.rounded_rectangle((2 * scale, (py - 1) * scale, 46 * scale, (py + 2) * scale), scale, fill=wood_dark)
        draw.line((3 * scale, py * scale, 45 * scale, py * scale), fill=wood_light, width=scale)
    horizontal = sprite.resize((CELL, 16), Image.Resampling.LANCZOS)
    vertical = horizontal.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    FENCE_H_OUT.parent.mkdir(parents=True, exist_ok=True)
    horizontal.save(FENCE_H_OUT)
    vertical.save(FENCE_V_OUT)
    return horizontal, vertical


def paste_centered(image: Image.Image, sprite: Image.Image, center: tuple[int, int]) -> None:
    image.alpha_composite(sprite, (center[0] - sprite.width // 2, center[1] - sprite.height // 2))


def draw_fence_cell(
    image: Image.Image,
    x: int,
    y: int,
    horizontal: Image.Image,
    vertical: Image.Image,
) -> None:
    center = (x * CELL + CELL // 2, y * CELL + CELL // 2)
    directions = CORNER_DIRECTIONS.get((x, y))
    if directions is None:
        if y in {7, 13, 16, 21}:
            paste_centered(image, horizontal, center)
        else:
            paste_centered(image, vertical, center)
        return

    corner = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    h_top = (CELL - horizontal.height) // 2
    v_left = (CELL - vertical.width) // 2
    if "left" in directions:
        corner.alpha_composite(horizontal.crop((0, 0, CELL // 2 + 1, horizontal.height)), (0, h_top))
    if "right" in directions:
        corner.alpha_composite(
            horizontal.crop((CELL // 2 - 1, 0, CELL, horizontal.height)),
            (CELL // 2 - 1, h_top),
        )
    if "up" in directions:
        corner.alpha_composite(vertical.crop((0, 0, vertical.width, CELL // 2 + 1)), (v_left, 0))
    if "down" in directions:
        corner.alpha_composite(
            vertical.crop((0, CELL // 2 - 1, vertical.width, CELL)),
            (v_left, CELL // 2 - 1),
        )
    paste_centered(image, corner, center)


def draw_camps_and_fences(image: Image.Image) -> None:
    for camp in (SOUTH_ENCLOSURE, EAST_ENCLOSURE):
        rounded_camp_ground(image, camp)
    image_rgba = image.convert("RGBA")

    camp = Image.open(CAMP_TILE).convert("RGBA")
    camp = ImageEnhance.Contrast(camp).enhance(1.08)
    large = camp.resize((66, 66), Image.Resampling.LANCZOS)
    small = camp.resize((44, 44), Image.Resampling.LANCZOS)
    for x, y in ((15, 19), (25, 10)):
        paste_centered(image_rgba, large, (x * CELL + CELL // 2, y * CELL + CELL // 2))
    for x, y in ((13, 18), (17, 18), (13, 20), (17, 20), (24, 9), (26, 9), (24, 12), (26, 12)):
        paste_centered(image_rgba, small, (x * CELL + CELL // 2, y * CELL + CELL // 2))

    fence_h, fence_v = make_fence_sprites()
    for x, y in sorted(FENCES, key=lambda cell: (cell[1], cell[0])):
        draw_fence_cell(image_rgba, x, y, fence_h, fence_v)
    image.paste(image_rgba.convert("RGB"))


def draw_review(image: Image.Image, rows: list[str]) -> None:
    review = image.convert("RGBA")
    overlay = Image.new("RGBA", review.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            left, top = x * CELL, y * CELL
            draw.rectangle((left, top, left + CELL - 1, top + CELL - 1), outline=(255, 238, 105, 165), width=1)
            label = f"{x},{y} {terrain}"
            draw.text((left + 2, top + 2), label, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 220))
    for x, y in FENCES:
        left, top = x * CELL, y * CELL
        draw.rectangle(
            (left + 2, top + 2, left + CELL - 3, top + CELL - 3),
            outline=(255, 45, 45, 255),
            width=4,
        )
    for x, y in GATE_CELLS:
        left, top = x * CELL, y * CELL
        draw.rectangle(
            (left + 2, top + 2, left + CELL - 3, top + CELL - 3),
            outline=(55, 255, 105, 255),
            width=4,
        )
    Image.alpha_composite(review, overlay).convert("RGB").save(REVIEW_OUT, quality=94)


def main() -> None:
    if not BASE.is_file():
        raise FileNotFoundError(f"Missing GPT Image base: {BASE}")
    rows = terrain_rows()
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)
    assert {(x, y) for y, row in enumerate(rows) for x, value in enumerate(row) if value == "P"} == FENCES
    image = cover_resize(Image.open(BASE).convert("RGB"), (WIDTH * CELL, HEIGHT * CELL))
    image = ImageEnhance.Color(image).enhance(0.92)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    draw_camps_and_fences(image)
    MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(MAP_OUT, "PNG", compress_level=6)
    draw_review(image, rows)
    manifest = {
        "map": str(MAP_OUT.relative_to(ROOT)),
        "source_base": str(BASE.relative_to(ROOT)),
        "grid": [WIDTH, HEIGHT],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {
            "version": 2,
            "primary_field": "primary_terrain",
            "secondary_field": "secondary_terrain",
            "secondary_coverage_range": [0, 255],
            "blendable_terrain": sorted(NATURAL_TERRAINS),
            "structure_cells_are_excluded": True,
        },
        "terrain_layers": terrain_layers(),
        "terrain_source": "manually reviewed programmatic source of truth",
        "structure_regions": {
            "south_camp": sorted([list(cell) for cell in SOUTH_ENCLOSURE], key=lambda p: (p[1], p[0])),
            "east_camp": sorted([list(cell) for cell in EAST_ENCLOSURE], key=lambda p: (p[1], p[0])),
        },
        "camp_cells": sorted([list(cell) for cell in CAMPS], key=lambda p: (p[1], p[0])),
        "camp_icon_cells": sorted([list(cell) for cell in CAMPS], key=lambda p: (p[1], p[0])),
        "supply_sites": sorted([list(site) for site in SITES], key=lambda p: (p[1], p[0])),
        "blocked_edges": [],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [
            {
                "name": "south_north_gate",
                "cells": sorted([list(cell) for cell in SOUTH_GATE_CELLS]),
            },
            {
                "name": "east_west_gate",
                "cells": sorted([list(cell) for cell in EAST_GATE_CELLS]),
            },
        ],
        "deployments": [
            {"name": "ZhengShiZiHu8", "force": 1, "position": [15, 19]},
            {"name": "GaoQuMi8", "force": 1, "position": [14, 19]},
            {"name": "ZhuDan8", "force": 1, "position": [16, 19]},
            {"name": "GongZiYuan8", "force": 1, "position": [14, 18]},
            {"name": "GongSunDaiZhong8", "force": 1, "position": [16, 18]},
            {"name": "DaLiang8", "force": 4, "position": [25, 10]},
            {"name": "BeiRongWarrior8", "force": 4, "position": [24, 11]},
            {"name": "BeiRongWarrior8", "force": 4, "position": [26, 11]},
            {"name": "BeiRongArcher8", "force": 4, "position": [25, 11]},
            {"name": "XiaoLiang8", "force": 4, "position": [20, 4]},
            {"name": "BeiRongWarrior8", "force": 4, "position": [19, 5]},
            {"name": "BeiRongWarrior8", "force": 4, "position": [21, 5]},
            {"name": "BeiRongArcher8", "force": 4, "position": [20, 5]},
        ],
        "visual_grid_in_game": False,
        "fence_cells": sorted([list(cell) for cell in FENCES], key=lambda p: (p[1], p[0])),
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(rows))
    print(f"map={MAP_OUT} size={image.size} fence_cells={len(FENCES)} gates={len(GATE_CELLS)}")


if __name__ == "__main__":
    main()
