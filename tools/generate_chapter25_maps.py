"""Build chapter 25 pass and city maps from existing GPT Image 2 bases."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    ("chapter19-li-city-gpt2.png", "m042.png", True, 0.92, 1.08, 0.98),
    ("m010-real-walls-gpt2-aligned.png", "m043.png", False, 1.06, 1.04, 0.96),
)


def render(
    source_name: str, destination_name: str, mirror: bool,
    color: float, contrast: float, brightness: float,
) -> Path:
    source = ROOT / "output" / "imagegen" / source_name
    image = cover(Image.open(source).convert("RGB"))
    if mirror:
        image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    destination = ROOT / "assets" / "lzc" / "map" / destination_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    return destination


def main() -> None:
    outputs = [render(*spec) for spec in MAPS]
    assert all(Image.open(path).size == SIZE for path in outputs)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in outputs}) == len(outputs)
    for path in outputs:
        print(path, path.stat().st_size)


if __name__ == "__main__":
    main()
