"""Build chapter 31's Di escape map from a local GPT Image 2 source."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def main() -> None:
    image = cover(Image.open(ROOT / "output/imagegen/chapter15-wenyang-gpt2.png").convert("RGB"))
    image = ImageEnhance.Color(image).enhance(0.96)
    image = ImageEnhance.Contrast(image).enhance(1.13)
    image = ImageEnhance.Brightness(image).enhance(1.02)
    destination = ROOT / "assets/lzc/map/m052.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    assert Image.open(destination).size == SIZE
    print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
