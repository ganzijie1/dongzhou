"""Build a labelled preview atlas from Face.e5."""

from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image, ImageDraw

from e5_archive import E5Archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=80)
    args = parser.parse_args()

    faces = E5Archive(args.root / "E5" / "Face.e5")
    cell, columns = 136, 8
    rows = (args.count + columns - 1) // columns
    atlas = Image.new("RGB", (columns * cell, rows * cell), (36, 39, 42))
    draw = ImageDraw.Draw(atlas)
    for slot, index in enumerate(range(args.start, min(args.start + args.count, len(faces.entries)))):
        x, y = slot % columns * cell, slot // columns * cell
        try:
            face = Image.open(io.BytesIO(faces.read(index))).convert("RGB")
            face.thumbnail((cell - 8, cell - 24), Image.Resampling.LANCZOS)
            atlas.paste(face, (x + (cell - face.width) // 2, y + 18))
        except (OSError, ValueError) as error:
            draw.text((x + 4, y + 24), str(error), fill=(230, 100, 100))
        draw.text((x + 4, y + 3), str(index), fill=(255, 255, 255))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
