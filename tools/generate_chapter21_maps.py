"""Build chapter 21 maps from the Cao Cao Legend terrain material archive."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


WIDTH, HEIGHT, CELL = 19, 14, 80
SIZE = (WIDTH * CELL, HEIGHT * CELL)
ROOT = Path(__file__).resolve().parents[1]
MATERIAL_ROOT = ROOT / "tmp" / "map_materials"

MAPS = {
    "m034.png": (
        [
            "rrrrrrrrrrrrrrrrrrr",
            "rmmmFFFFgggFFFFmmmr",
            "rmmFgggggggggggFmmr",
            "rmFgggggggggggggFmr",
            "rFgggfffgffffggggFr",
            "rgggffffwfffffggggr",
            "rggffffffffffgggggr",
            "rggffffffffffgggggr",
            "rgggffffffffffggggr",
            "rFgggffffffggggggFr",
            "rmFgggggggggggggFmr",
            "rmmFggggeggggggFmmr",
            "rmmmFFFFgggFFFFmmmr",
            "rrrrrrrrrrrrrrrrrrr",
        ],
        False,
        "chapter15-ganshi-gpt2.png",
    ),
    "m035.png": (
        [
            "rrrrrrrrrrrrrrrrrrr",
            "rmmmFgggggggggFmmmr",
            "rmmFgggggeggggggFmr",
            "rmFggffffffffgggFmr",
            "rFggffffffffffgggFr",
            "~~~~ff~~~~~~~~ff~~~",
            "~~~~ff~~~~~~~~ff~~~",
            "rFggffffffffffgggFr",
            "rmFggffffffffgggFmr",
            "rmmFgggggggggggFmmr",
            "rmmmFgggggggggFmmmr",
            "rggggggggeggggggggr",
            "rgggggggggggggggggr",
            "rrrrrrrrrrrrrrrrrrr",
        ],
        False,
        "chapter15-ganshi-gpt2.png",
    ),
    "m036.png": (
        [
            "fffffffffGfffffffff",
            "ffWWWWWWWGWWWWWWWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiibiiCiiibiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffGiiiiiiiiiiiiiGff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWWWWWWWGWWWWWWWff",
            "fffffffffffffffffff",
            "ffffefffffffeffffff",
            "fffffffffffffffffff",
        ],
        True,
        "chapter17-bo-city-gpt2.png",
    ),
}


def material_directories() -> tuple[Path, Path]:
    terrain = next(
        path
        for path in MATERIAL_ROOT.iterdir()
        if len([item for item in path.glob("*") if item.suffix.lower() in {".png", ".jpg"}]) == 23
    )
    buildings = next(path for path in MATERIAL_ROOT.iterdir() if len(list(path.glob("*.png"))) == 52)
    return terrain, buildings


def texture(directory: Path, number: int, seed: int) -> Image.Image:
    source = Image.open(next(directory.glob(f"{number}.*"))).convert("RGB")
    if source.width < SIZE[0] or source.height < SIZE[1]:
        canvas = Image.new("RGB", SIZE)
        for y in range(0, SIZE[1], source.height):
            for x in range(0, SIZE[0], source.width):
                canvas.paste(source, (x, y))
        return canvas
    rng = random.Random(seed)
    left = rng.randrange(source.width - SIZE[0] + 1)
    top = rng.randrange(source.height - SIZE[1] + 1)
    return source.crop((left, top, left + SIZE[0], top + SIZE[1]))


def terrain_mask(rows: list[str], chars: set[str], blur: int = 9) -> Image.Image:
    small = Image.new("L", (WIDTH, HEIGHT), 0)
    pixels = small.load()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char in chars:
                pixels[x, y] = 255
    mask = small.resize(SIZE, Image.Resampling.NEAREST)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur else mask


def building(directory: Path, number: int, extent: int) -> Image.Image:
    sprite = Image.open(directory / f"{number}.png").convert("RGBA")
    ratio = extent / max(sprite.size)
    return sprite.resize(
        (max(1, int(sprite.width * ratio)), max(1, int(sprite.height * ratio))),
        Image.Resampling.NEAREST,
    )


def cover(source: Image.Image) -> Image.Image:
    ratio = max(SIZE[0] / source.width, SIZE[1] / source.height)
    resized = source.resize((int(source.width * ratio), int(source.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - SIZE[0]) // 2
    top = (resized.height - SIZE[1]) // 2
    return resized.crop((left, top, left + SIZE[0], top + SIZE[1]))


def add_natural_river(image: Image.Image, seed: int) -> Image.Image:
    """Blend a continuous creek into the painted terrain without tile borders."""
    rng = random.Random(seed)
    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)
    upper: list[tuple[int, int]] = []
    lower: list[tuple[int, int]] = []
    for x in range(-40, SIZE[0] + 41, 24):
        bend = 18 * math.sin(x / 175.0) + 8 * math.sin(x / 61.0)
        jitter = rng.randint(-3, 3)
        center = int(455 + bend + jitter)
        half_width = int(72 + 8 * math.sin(x / 103.0))
        upper.append((x, center - half_width))
        lower.append((x, center + half_width))
    draw.polygon(upper + list(reversed(lower)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(14))

    detail = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(0.72)
    water = ImageOps.colorize(detail, "#173f43", "#6f9d8c").convert("RGB")
    water = Image.blend(water, Image.new("RGB", SIZE, (42, 98, 94)), 0.28)
    result = Image.composite(water, image, mask)

    ripples = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ripple_draw = ImageDraw.Draw(ripples)
    for y in range(405, 520, 18):
        offset = rng.randint(-18, 18)
        for x in range(offset, SIZE[0], 110):
            length = rng.randint(38, 72)
            ripple_draw.arc((x, y, x + length, y + 12), 185, 350, fill=(198, 220, 196, 55), width=2)
    result = Image.alpha_composite(result.convert("RGBA"), ripples.filter(ImageFilter.GaussianBlur(1))).convert("RGB")

    ford_mask = Image.new("L", SIZE, 0)
    ford_draw = ImageDraw.Draw(ford_mask)
    for center_x in (int(4.5 * CELL), int(14.5 * CELL)):
        ford_draw.polygon(
            [
                (center_x - 62, 365), (center_x + 56, 365),
                (center_x + 42, 548), (center_x - 50, 548),
            ],
            fill=225,
        )
    ford_mask = ImageChops.multiply(ford_mask.filter(ImageFilter.GaussianBlur(8)), mask)
    sand = ImageOps.colorize(ImageOps.grayscale(image), "#4a4932", "#a39a66").convert("RGB")
    return Image.composite(sand, result, ford_mask)

def render(rows: list[str], destination: Path, seed: int, night: bool, source_name: str) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)
    terrain, buildings = material_directories()
    source_path = ROOT / "output" / "imagegen" / source_name
    image = cover(Image.open(source_path).convert("RGB"))
    if any("~" in row for row in rows):
        image = add_natural_river(image, seed)
    # The source maps already contain natural, blended barriers. Collision and
    # movement costs come from the matching Lua terrain table.

    icons = {"e": (34, 72), "b": (38, 72), "C": (29, 86), "G": (39, 72), "D": (33, 72), "c": (21, 72)}
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char not in icons:
                continue
            number, extent = icons[char]
            sprite = building(buildings, number, extent)
            left = x * CELL + (CELL - sprite.width) // 2
            top = y * CELL + (CELL - sprite.height) // 2 - (8 if char in "Ce" else 0)
            image.paste(sprite, (left, top), sprite)

    if night:
        image = Image.blend(image, Image.new("RGB", SIZE, (31, 42, 70)), 0.34)
        image = ImageEnhance.Contrast(image).enhance(1.12)
        glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        for x, y in ((6, 5), (12, 7), (9, 3)):
            center_x, center_y = x * CELL + CELL // 2, y * CELL + CELL // 2
            glow_draw.ellipse((center_x - 52, center_y - 52, center_x + 52, center_y + 52), fill=(255, 112, 34, 60))
            glow_draw.ellipse((center_x - 14, center_y - 18, center_x + 14, center_y + 18), fill=(255, 174, 56, 190))
        image = Image.alpha_composite(image.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(10))).convert("RGB")

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)


def main() -> None:
    for index, (filename, (rows, night, source_name)) in enumerate(MAPS.items()):
        destination = ROOT / "assets" / "lzc" / "map" / filename
        render(rows, destination, 2100 + index * 97, night, source_name)
        print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
