"""Build the chapter 22 Li battlefield from an existing GPT Image 2 base."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from tools.generate_chapter21_maps import CELL, ROOT, SIZE, building, cover, material_directories


def curved_road_mask() -> Image.Image:
    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)
    points = [(-40, 1040), (220, 930), (480, 790), (760, 660), (1040, 450), (1320, 260), (1560, 120)]
    draw.line(points, fill=255, width=150, joint="curve")
    return mask.filter(ImageFilter.GaussianBlur(18))


def main() -> None:
    source = ROOT / "output" / "imagegen" / "chapter15-wenyang-gpt2.png"
    image = ImageOps.mirror(cover(Image.open(source).convert("RGB")))
    image = ImageEnhance.Color(image).enhance(0.84)
    image = ImageEnhance.Contrast(image).enhance(1.08)

    gray = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(0.82)
    earth = ImageOps.colorize(gray, "#403c27", "#a18e59").convert("RGB")
    road = Image.composite(earth, image, curved_road_mask())

    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for x, y in ((4, 11), (14, 2)):
        cx, cy = x * CELL + CELL // 2, y * CELL + CELL // 2
        shade_draw.ellipse((cx - 88, cy - 40, cx + 88, cy + 48), fill=(25, 20, 12, 48))
    road = Image.alpha_composite(road.convert("RGBA"), shade.filter(ImageFilter.GaussianBlur(12))).convert("RGB")

    _, buildings = material_directories()
    for x, y, number in ((4, 11, 34), (14, 2, 38)):
        sprite = building(buildings, number, 76)
        left = x * CELL + (CELL - sprite.width) // 2
        top = y * CELL + (CELL - sprite.height) // 2 - 5
        road.paste(sprite, (left, top), sprite)

    destination = ROOT / "assets" / "lzc" / "map" / "m037.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    road.save(destination, "PNG", compress_level=3)
    print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
