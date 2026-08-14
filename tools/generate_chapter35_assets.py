"""Generate chapter 35's Yunmeng map and local beast art fallback."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/lzc/map_sources/m058_ch35_manifest.json"
MAP_OUT = ROOT / "assets/lzc/map/m058.png"
REVIEW_OUT = ROOT / "output/terrain_model/m058_ch35_review.png"
PORTRAIT_ROOT = ROOT / "rl/assets/portraits"
ANIM_ROOT = ROOT / "rl/assets/unit_anim"


def cover(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    ratio = max(size[0] / source.width, size[1] / source.height)
    scaled = source.resize(
        (round(source.width * ratio), round(source.height * ratio)),
        Image.Resampling.LANCZOS,
    )
    left = (scaled.width - size[0]) // 2
    top = (scaled.height - size[1]) // 2
    return scaled.crop((left, top, left + size[0], top + size[1]))


def class_mask(rows: list[str], chars: set[str], cell: int, blur: int = 18) -> Image.Image:
    width, height = len(rows[0]), len(rows)
    small = Image.new("L", (width, height), 0)
    pixels = small.load()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            pixels[x, y] = 255 if char in chars else 0
    mask = small.resize((width * cell, height * cell), Image.Resampling.NEAREST)
    return mask.filter(ImageFilter.GaussianBlur(blur)) if blur else mask


def generate_map(manifest: dict) -> None:
    width, height = manifest["grid"]
    cell = int(manifest["cell_pixels"])
    rows = list(manifest["terrain_rows"])
    size = (width * cell, height * cell)
    assert len(rows) == height and all(len(row) == width for row in rows)

    source = ROOT / manifest["source_base"]
    base = ImageOps.mirror(cover(Image.open(source).convert("RGB"), size))
    base = ImageEnhance.Color(base).enhance(0.82)
    base = ImageEnhance.Contrast(base).enhance(1.08)

    grass_detail = ImageEnhance.Contrast(ImageOps.grayscale(base)).enhance(0.78)
    grass = ImageOps.colorize(grass_detail, "#364a31", "#9cac70")
    flat = ImageEnhance.Brightness(base).enhance(1.12)
    flat = Image.blend(flat, Image.new("RGB", size, "#9a9565"), 0.16)
    forest = ImageEnhance.Contrast(base).enhance(1.18)
    forest = Image.blend(forest, Image.new("RGB", size, "#315638"), 0.38)
    mountain = ImageOps.colorize(
        ImageEnhance.Contrast(ImageOps.grayscale(base)).enhance(1.28),
        "#3e4639",
        "#9a977a",
    )
    water = ImageOps.colorize(ImageOps.grayscale(base), "#153c58", "#68a9bd")
    water = Image.blend(water, Image.new("RGB", size, "#2f7898"), 0.42)

    image = grass
    image = Image.composite(flat, image, class_mask(rows, {"f"}, cell))
    image = Image.composite(forest, image, class_mask(rows, {"F"}, cell))
    image = Image.composite(mountain, image, class_mask(rows, {"m"}, cell))
    image = Image.composite(water, image, class_mask(rows, {"~"}, cell, 11))

    rng = random.Random(35058)
    forest_detail = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(forest_detail)
    for _ in range(430):
        x, y = rng.randrange(size[0]), rng.randrange(size[1])
        if rows[min(height - 1, y // cell)][min(width - 1, x // cell)] != "F":
            continue
        radius = rng.randrange(5, 13)
        color = rng.choice(((25, 65, 35, 54), (65, 98, 48, 48), (18, 48, 31, 44)))
        draw.ellipse((x - radius, y - radius // 2, x + radius, y + radius // 2), fill=color)
    image = Image.alpha_composite(image.convert("RGBA"), forest_detail.filter(ImageFilter.GaussianBlur(2)))

    ridge = Image.new("RGBA", size, (0, 0, 0, 0))
    ridge_draw = ImageDraw.Draw(ridge)
    for y in range(height):
        for x in range(width):
            if rows[y][x] != "m":
                continue
            cx, cy = x * cell + cell // 2, y * cell + cell // 2
            peak = cy - rng.randrange(10, 19)
            ridge_draw.polygon(
                [(cx - 25, cy + 15), (cx, peak), (cx + 25, cy + 15)],
                fill=(71, 77, 62, 46),
            )
            ridge_draw.line((cx, peak, cx + 12, cy + 8), fill=(205, 199, 161, 45), width=2)
    ridge.putalpha(Image.composite(ridge.getchannel("A"), Image.new("L", size), class_mask(rows, {"m"}, cell, 6)))
    image = Image.alpha_composite(image, ridge.filter(ImageFilter.GaussianBlur(1)))

    ripples = Image.new("RGBA", size, (0, 0, 0, 0))
    ripple_draw = ImageDraw.Draw(ripples)
    for y in range(5 * cell + 12, 9 * cell, 15):
        for x in range(9 * cell + rng.randrange(4, 18), 14 * cell, 70):
            ripple_draw.arc((x, y, x + 38, y + 9), 190, 350, fill=(195, 220, 198, 80), width=2)
    ripples.putalpha(Image.composite(ripples.getchannel("A"), Image.new("L", size), class_mask(rows, {"~"}, cell, 3)))
    image = Image.alpha_composite(image, ripples.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")
    image = ImageEnhance.Sharpness(image).enhance(1.08)

    MAP_OUT.parent.mkdir(parents=True, exist_ok=True)

    image.save(MAP_OUT, "PNG", compress_level=3)

    review = image.convert("RGBA")
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    review_draw = ImageDraw.Draw(overlay)
    for x in range(width + 1):
        review_draw.line((x * cell, 0, x * cell, size[1]), fill=(255, 255, 255, 115), width=1)
    for y in range(height + 1):
        review_draw.line((0, y * cell, size[0], y * cell), fill=(255, 255, 255, 115), width=1)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            review_draw.text((x * cell + 3, y * cell + 2), f"{x},{y} {char}", fill=(255, 245, 190, 235))
    REVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(review, overlay).save(REVIEW_OUT, "PNG")


def portrait(kind: str, destination: Path) -> None:
    size = 320
    image = Image.new("RGB", (size, size), "#273128" if kind == "bear" else "#263638")
    glow = Image.new("L", (size, size), 0)
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((35, 25, 285, 300), fill=210)
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    backdrop = Image.new("RGB", (size, size), "#6b7552" if kind == "bear" else "#6a8177")
    image = Image.composite(backdrop, image, glow)
    draw = ImageDraw.Draw(image)
    if kind == "bear":
        draw.ellipse((61, 44, 259, 278), fill="#28251e", outline="#b29a68", width=4)
        draw.ellipse((48, 38, 111, 104), fill="#26231c", outline="#9d865c", width=4)
        draw.ellipse((209, 38, 272, 104), fill="#26231c", outline="#9d865c", width=4)
        draw.ellipse((92, 89, 228, 260), fill="#3a3327")
        draw.ellipse((106, 155, 218, 265), fill="#7b684b")
        draw.ellipse((126, 124, 143, 143), fill="#d7b95f")
        draw.ellipse((180, 124, 197, 143), fill="#d7b95f")
        draw.ellipse((131, 130, 139, 141), fill="#11120f")
        draw.ellipse((184, 130, 192, 141), fill="#11120f")
        draw.ellipse((143, 181, 181, 207), fill="#171713")
        draw.arc((126, 185, 199, 238), 15, 165, fill="#d6c295", width=4)
        draw.line((105, 107, 144, 175), fill="#ad8e6b", width=5)
    else:
        draw.ellipse((50, 62, 267, 270), fill="#202726", outline="#b4b9a8", width=4)
        draw.ellipse((82, 81, 235, 244), fill="#d7d7c8")
        draw.polygon([(83, 103), (119, 54), (144, 105)], fill="#1e2423")
        draw.polygon([(177, 104), (208, 52), (238, 112)], fill="#1e2423")
        draw.ellipse((106, 120, 132, 145), fill="#1a1d1c")
        draw.ellipse((180, 120, 206, 145), fill="#1a1d1c")
        draw.ellipse((113, 128, 124, 142), fill="#d7b95f")
        draw.ellipse((187, 128, 198, 142), fill="#d7b95f")
        draw.polygon([(138, 147), (190, 146), (207, 258), (166, 285), (129, 245)], fill="#363f3c")
        draw.ellipse((151, 242, 181, 267), fill="#171a19")
        for x, y in ((81, 176), (222, 183), (105, 224), (214, 230)):
            draw.ellipse((x - 13, y - 9, x + 13, y + 9), fill="#303938")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.resize((256, 256), Image.Resampling.LANCZOS).save(destination, "PNG")


def beast_frame(kind: str, direction: str, phase: int = 0, state: str = "walk") -> Image.Image:
    scale = 4
    image = Image.new("RGBA", (64 * scale, 64 * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    bob = (phase % 2) * 2
    fallen = state == "weak"
    attack = state == "attack"
    hit = state == "hit"
    if fallen:
        body = (8, 38, 57, 56)
        head = (42, 34, 62, 53)
    elif direction in {"left", "right"}:
        body = (12, 23 + bob, 52, 51 + bob)
        head = (4 if direction == "left" else 43, 20 + bob, 25 if direction == "left" else 63, 43 + bob)
    else:
        body = (15, 19 + bob, 49, 52 + bob)
        head = (18, 10 + bob, 47, 37 + bob)
    body_color = "#302a20" if kind == "bear" else "#d3d0bb"
    dark = "#181a16" if kind == "bear" else "#232a28"
    outline = "#171713"
    draw.ellipse(tuple(v * scale for v in body), fill=body_color, outline=outline, width=2 * scale)
    draw.ellipse(tuple(v * scale for v in head), fill=dark, outline=outline, width=2 * scale)
    if not fallen:
        leg_y = (48 + bob) * scale
        for x in (19, 39):
            step = (phase * 3 if x == 19 else (1 - phase) * 3) * scale
            draw.rounded_rectangle((x * scale, leg_y - step, (x + 8) * scale, 58 * scale), radius=3 * scale, fill=dark)
    if kind == "bear":
        if direction != "up" and not fallen:
            eye_y = (24 + bob) * scale
            eye_x = 14 if direction == "left" else 50 if direction == "right" else 27
            draw.ellipse((eye_x * scale, eye_y, (eye_x + 3) * scale, eye_y + 3 * scale), fill="#e2bd58")
        if attack and not fallen:
            claw_x = 2 if direction == "left" else 54 if direction == "right" else 48
            draw.line((claw_x * scale, 30 * scale, (claw_x + (-8 if direction == "left" else 8)) * scale, 41 * scale), fill="#dfd4b3", width=2 * scale)
    else:
        draw.rectangle((18 * scale, 22 * scale, 46 * scale, 32 * scale), fill=dark)
        if direction != "up" and not fallen:
            snout_x = 4 if direction == "left" else 50 if direction == "right" else 27
            snout_y = 31 + bob
            draw.rounded_rectangle((snout_x * scale, snout_y * scale, (snout_x + 10) * scale, (snout_y + 18) * scale), radius=4 * scale, fill="#4b5651")
            draw.ellipse(((snout_x + 2) * scale, (snout_y + 14) * scale, (snout_x + 8) * scale, (snout_y + 18) * scale), fill="#151817")
    if hit:
        red = Image.new("RGBA", image.size, (180, 42, 35, 70))
        image = Image.alpha_composite(image, red)
    return image.resize((64, 64), Image.Resampling.NEAREST)


def animation(kind: str) -> None:
    root = ANIM_ROOT / kind
    root.mkdir(parents=True, exist_ok=True)
    for direction in ("down", "up", "left"):
        for phase in range(2):
            beast_frame(kind, direction, phase).save(root / f"{direction}_{phase}.png")
        beast_frame(kind, direction, 0, "idle").save(root / f"stand_{direction}.png")
        for phase in range(4):
            beast_frame(kind, direction, phase % 2, "attack").save(root / f"attack_{direction}_{phase}.png")
        beast_frame(kind, direction, 0, "hit").save(root / f"hit_{direction}.png")
    beast_frame(kind, "down", 0, "hit").save(root / "hit_failed.png")
    beast_frame(kind, "down", 0, "idle").save(root / "hit_recover.png")
    beast_frame(kind, "left", 0, "weak").save(root / "weak_0.png")
    beast_frame(kind, "left", 1, "weak").save(root / "weak_1.png")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    generate_map(manifest)




    print(MAP_OUT, Image.open(MAP_OUT).size)
    print(REVIEW_OUT)
    print("Chapter 35 creature art is installed separately from reviewed GPT Image 2 outputs.")




if __name__ == "__main__":
    main()
