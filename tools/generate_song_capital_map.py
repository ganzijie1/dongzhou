"""Build the Song capital coup map from a project-local GPT Image 2 city base."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def main() -> None:
    source = ROOT / "output" / "imagegen" / "chapter14-wei-city-gpt2.png"
    image = cover(Image.open(source).convert("RGB"))
    image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(0.93)
    image = ImageEnhance.Contrast(image).enhance(1.10)
    image = ImageEnhance.Brightness(image).enhance(0.98)
    destination = ROOT / "assets" / "lzc" / "map" / "song-capital-coup.png"
    image.save(destination, "PNG", compress_level=3)
    assert Image.open(destination).size == SIZE
    assert destination.stat().st_size > 1_000_000
    print(destination, destination.stat().st_size, hashlib.sha256(destination.read_bytes()).hexdigest()[:12])


if __name__ == "__main__":
    main()
