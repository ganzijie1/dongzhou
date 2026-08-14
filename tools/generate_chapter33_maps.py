"""Build chapter 33's Qi-camp and Meng-alliance maps from GPT Image 2 sources."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    ("chapter33-qi-camp-night-gpt2.png", "m054.png", 1.30, 1.12, 1.04),
    ("chapter33-meng-ambush-gpt2.png", "m055.png", 1.04, 1.10, 0.98),
)


def main() -> None:
    for source_name, destination_name, brightness, contrast, color in MAPS:
        source = ROOT / "output/imagegen" / source_name
        image = cover(Image.open(source).convert("RGB"))
        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        image = ImageEnhance.Color(image).enhance(color)
        destination = ROOT / "assets/lzc/map" / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "PNG", compress_level=3)
        assert Image.open(destination).size == SIZE
        print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
