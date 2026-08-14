"""Build chapter 32's Linzi night escape map from its GPT Image 2 source."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def main() -> None:
    source = ROOT / "output/imagegen/chapter32-linzi-night-gpt2.png"
    image = cover(Image.open(source).convert("RGB"))
    image = ImageEnhance.Brightness(image).enhance(1.34)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = ImageEnhance.Color(image).enhance(1.05)
    destination = ROOT / "assets/lzc/map/m053.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    assert Image.open(destination).size == SIZE
    print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
