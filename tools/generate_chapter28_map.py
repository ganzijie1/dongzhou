"""Build chapter 28's Jiang capital coup map from a local GPT Image 2 base."""

from __future__ import annotations

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def main() -> None:
    source = ROOT / "output/imagegen/chapter14-gufen-palace-gpt2.png"
    image = cover(Image.open(source).convert("RGB"))
    image = ImageOps.mirror(image)
    scaled = image.resize(
        (round(SIZE[0] * 1.06), round(SIZE[1] * 1.06)),
        Image.Resampling.LANCZOS,
    )
    left = (scaled.width - SIZE[0]) // 2
    top = max(0, (scaled.height - SIZE[1]) // 2 - 24)
    image = scaled.crop((left, top, left + SIZE[0], top + SIZE[1]))
    image = ImageEnhance.Color(image).enhance(0.94)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = ImageEnhance.Brightness(image).enhance(0.98)
    destination = ROOT / "assets/lzc/map/m048.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    assert Image.open(destination).size == SIZE
    print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
