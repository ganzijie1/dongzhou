"""Build chapter 34's Suiyang and Hong River maps from GPT Image 2 sources."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    ("chapter34-suiyang-defense-gpt2.png", "m056.png", 1.12, 1.10, 1.02),
    ("chapter34-hong-river-gpt2.png", "m057.png", 1.10, 1.08, 1.02),
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
