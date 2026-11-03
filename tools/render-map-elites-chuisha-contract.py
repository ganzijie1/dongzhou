"""Render the shipped MAP-Elites contract map and a labeled review image."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "web-game/scenario/map-elites-chuisha.archive.json"
OUTPUT = ROOT / "output/map-elites-chuisha"
CELL = 48
COLORS = {"f": "#7d8b58", "g": "#6f8756", "F": "#405d40", "w": "#887857", "m": "#625f50", "~": "#456f83", "v": "#77a8b1"}


def main() -> None:
    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    elite = max(archive["entries"], key=lambda entry: entry["quality"])
    rows = elite["rows"]
    width, height = archive["grid"]
    final = Image.new("RGB", (width * CELL, height * CELL), COLORS["f"])
    draw = ImageDraw.Draw(final)
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            draw.rectangle((x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL), fill=COLORS[terrain])
            if terrain in "~v":
                for offset in (14, 29):
                    draw.arc((x * CELL + 4, y * CELL + offset - 5, (x + 1) * CELL - 4, y * CELL + offset + 5), 190, 350, fill="#a3cad0", width=2)
            elif terrain == "F":
                draw.polygon(((x + 0.5) * CELL, y * CELL + 9, x * CELL + 13, (y + 1) * CELL - 11, (x + 1) * CELL - 13, (y + 1) * CELL - 11), fill="#294a34")
            elif terrain == "m":
                draw.polygon((x * CELL + 7, (y + 1) * CELL - 8, (x + 0.5) * CELL, y * CELL + 7, (x + 1) * CELL - 7, (y + 1) * CELL - 8), fill="#514f46")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    final.save(OUTPUT / "contract-map.png")
    review = final.copy()
    review_draw = ImageDraw.Draw(review, "RGBA")
    for x in range(width + 1): review_draw.line((x * CELL, 0, x * CELL, height * CELL), fill=(255, 246, 207, 100), width=1)
    for y in range(height + 1): review_draw.line((0, y * CELL, width * CELL, y * CELL), fill=(255, 246, 207, 100), width=1)
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            review_draw.text((x * CELL + 3, y * CELL + 2), f"{x},{y} {terrain}", fill=(255, 255, 255, 220))
    review.save(OUTPUT / "contract-review.png")


if __name__ == "__main__":
    main()
