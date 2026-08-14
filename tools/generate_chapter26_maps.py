"""Build chapter 26 western campaign maps from existing GPT Image 2 bases."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    (ROOT / "output/imagegen/chapter20-li-rong-gpt2.png", "m044.png", True, 0.96, 1.09, 1.02),
    (ROOT / "assets/lzc/map/m035.png", "m045.png", False, 0.88, 1.12, 0.94),
)


def render(
    source: Path, destination_name: str, mirror: bool,
    color: float, contrast: float, brightness: float,
) -> Path:
    image = cover(Image.open(source).convert("RGB"))
    if mirror:
        image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    destination = ROOT / "assets" / "lzc" / "map" / destination_name
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
