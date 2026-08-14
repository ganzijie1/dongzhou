"""Build a labelled preview atlas from Pmap.e5 and Spalet.e5."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image, ImageDraw

from e5_archive import E5Archive


def decode_sprite(payload: bytes, palette: bytes) -> Image.Image:
    if len(payload) < 16:
        raise ValueError("Pmap entry is too short")
    header = struct.unpack_from("<8H", payload)
    width, height = header[4], header[5]
    pixels = payload[16:]
    if width <= 0 or height <= 0 or width * height > len(pixels):
        raise ValueError(f"unsupported Pmap dimensions {width}x{height}")
    image = Image.frombytes("P", (width, height), pixels[:width * height])
    image.putpalette(palette)
    image.info["transparency"] = 255
    return image.convert("RGBA")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=80)
    parser.add_argument("--palette", type=int, default=0)
    args = parser.parse_args()

    pmap = E5Archive(args.root / "E5" / "Pmap.e5")
    palettes = E5Archive(args.root / "E5" / "Spalet.e5")
    palette = palettes.read(args.palette)
    cell = 128
    columns = 8
    rows = (args.count + columns - 1) // columns
    atlas = Image.new("RGB", (columns * cell, rows * cell), (36, 39, 42))
    draw = ImageDraw.Draw(atlas)
    for slot, index in enumerate(range(args.start, min(args.start + args.count, len(pmap.entries)))):
        x, y = slot % columns * cell, slot // columns * cell
        try:
            sprite = decode_sprite(pmap.read(index), palette)
            sprite.thumbnail((cell - 8, cell - 24), Image.Resampling.NEAREST)
            atlas.paste(sprite, (x + (cell - sprite.width) // 2, y + 18), sprite)
        except ValueError as error:
            draw.text((x + 4, y + 24), str(error), fill=(230, 100, 100))
        draw.text((x + 4, y + 3), str(index), fill=(255, 255, 255))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
