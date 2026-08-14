"""Build chapter 24 city battle maps from existing GPT Image 2 bases."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    ("chapter17-bo-city-gpt2.png", "m040.png", True, 0.88, 1.10),
    ("chapter18-sui-city-gpt2.png", "m041.png", False, 1.05, 1.06),
)


def render(
    source_name: str, destination_name: str, mirror: bool,
    color: float, contrast: float,
) -> Path:
    source = ROOT / "output" / "imagegen" / source_name
    image = cover(Image.open(source).convert("RGB"))
    if mirror:
        image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    destination = ROOT / "assets" / "lzc" / "map" / destination_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    return destination


def main() -> None:
    outputs = [render(*spec) for spec in MAPS]
    assert all(Image.open(path).size == SIZE for path in outputs)
    hashes = {hashlib.sha256(path.read_bytes()).digest() for path in outputs}
    assert len(hashes) == len(outputs)
    for path in outputs:
        print(path, path.stat().st_size)


if __name__ == "__main__":
    main()