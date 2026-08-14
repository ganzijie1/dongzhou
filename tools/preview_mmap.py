"""Create labeled contact sheets for an E5 image archive."""

from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image, ImageDraw

from e5_archive import E5Archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=64)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    archive = E5Archive(args.archive)
    tile = (200, 142)
    columns = 4
    end = min(len(archive.entries), args.start + args.count)
    rows = (end - args.start + columns - 1) // columns
    sheet = Image.new("RGB", (tile[0] * columns, tile[1] * rows), "black")
    draw = ImageDraw.Draw(sheet)
    for slot, index in enumerate(range(args.start, end)):
        with Image.open(io.BytesIO(archive.read(index))) as source:
            image = source.convert("RGB")
        image.thumbnail((tile[0], tile[1] - 22))
        x = slot % columns * tile[0]
        y = slot // columns * tile[1]
        sheet.paste(image, (x, y + 22))
        draw.text((x + 5, y + 4), str(index), fill="white")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)


if __name__ == "__main__":
    main()
