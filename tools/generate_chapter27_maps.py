"""Build chapter 27 Pu city and Caisang maps from local GPT Image 2 bases."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from tools.generate_chapter21_maps import ROOT, SIZE, cover


MAPS = (
    ("chapter19-luoyi-gpt2.png", "m046.png", True, 0.98, 1.10, 0.98, 1.02),
    ("chapter23-chunmen-gpt2.png", "m047.png", True, 0.96, 1.08, 1.02, 1.07),
)


def render(
    source_name: str,
    destination_name: str,
    mirror: bool,
    color: float,
    contrast: float,
    brightness: float,
    zoom: float,
) -> Path:
    image = cover(Image.open(ROOT / "output/imagegen" / source_name).convert("RGB"))
    if mirror:
        image = ImageOps.mirror(image)
    if zoom != 1.0:
        scaled = image.resize(
            (round(SIZE[0] * zoom), round(SIZE[1] * zoom)),
            Image.Resampling.LANCZOS,
        )
        left = (scaled.width - SIZE[0]) // 2
        top = (scaled.height - SIZE[1]) // 2
        image = scaled.crop((left, top, left + SIZE[0], top + SIZE[1]))
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    destination = ROOT / "assets/lzc/map" / destination_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    return destination


def main() -> None:
    outputs = [render(*spec) for spec in MAPS]
    assert all(Image.open(path).size == SIZE for path in outputs)
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in outputs}) == 2
    for path in outputs:
        print(path, path.stat().st_size)


if __name__ == "__main__":
    main()
