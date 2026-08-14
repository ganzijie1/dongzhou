"""Build chapter 30's Yuanling relief and Hanyuan battle maps."""

from __future__ import annotations

import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def yuanling() -> Image.Image:
    image = cover(Image.open(ROOT / "output/imagegen/chapter20-three-states-gpt2.png").convert("RGB"))
    image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(1.04)
    image = ImageEnhance.Contrast(image).enhance(1.10)
    return image


def hanyuan() -> Image.Image:
    image = cover(Image.open(ROOT / "output/imagegen/chapter15-ganshi-gpt2.png").convert("RGB"))
    image = ImageEnhance.Color(image).enhance(0.92)
    image = ImageEnhance.Contrast(image).enhance(1.12)

    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)
    rng = random.Random(3030)
    points = []
    cx, cy = 12.0 * 80, 7.4 * 80
    for index in range(28):
        angle = index * 6.283185307179586 / 28
        radius_x = 145 + rng.randint(-24, 24)
        radius_y = 105 + rng.randint(-18, 18)
        points.append((cx + radius_x * __import__("math").cos(angle), cy + radius_y * __import__("math").sin(angle)))
    draw.polygon(points, fill=225)
    mask = mask.filter(ImageFilter.GaussianBlur(16))
    gray = ImageOps.grayscale(image)
    mud = ImageOps.colorize(gray, "#40382b", "#857557").convert("RGB")
    image = Image.composite(mud, image, mask)

    detail = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    detail_draw = ImageDraw.Draw(detail)
    for _ in range(28):
        x = rng.randint(835, 1085)
        y = rng.randint(500, 700)
        detail_draw.ellipse((x, y, x + rng.randint(20, 52), y + rng.randint(5, 14)), fill=(45, 37, 27, 75))
    return Image.alpha_composite(image.convert("RGBA"), detail.filter(ImageFilter.GaussianBlur(2))).convert("RGB")


def main() -> None:
    outputs = (("m050.png", yuanling()), ("m051.png", hanyuan()))
    for name, image in outputs:
        destination = ROOT / "assets/lzc/map" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "PNG", compress_level=3)
        assert Image.open(destination).size == SIZE
        print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
