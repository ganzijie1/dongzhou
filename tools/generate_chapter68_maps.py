from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as structures
import generate_chapter60_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def build_linzi_east_gate() -> None:
    width, height = 72, 44
    rows = common.natural_rows(width, height)
    bounds = (5, 3, 62, 40)
    gates = {(62, 20), (62, 21)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(21, 12), (35, 15), (50, 29)}
    decor = {(13, 10), (29, 10), (45, 11), (55, 15), (16, 28), (29, 32), (41, 29), (55, 33)}

    for y in range(4, 40):
        for x in range(6, 62):
            rows[y][x] = "i" if (x * 3 + y * 5) % 10 else "h"
    for x0, y0, x1, y1 in ((12, 7, 28, 17), (31, 9, 42, 20), (45, 9, 58, 19), (12, 25, 26, 35), (37, 25, 58, 36)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                rows[y][x] = "h"
    for x, y in decor:
        rows[y][x] = "h"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter50-daji-base-gpt2.png"
    image = common.base_image(source, width, height, rows)
    tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(tint).rectangle(
        (6 * CELL, 4 * CELL, 62 * CELL, 40 * CELL), fill=(123, 105, 82, 82)
    )
    image = Image.alpha_composite(image, tint.filter(ImageFilter.GaussianBlur(7)))
    structures.draw_walls(image, walls, bounds)
    structures.draw_castles(image, sites | decor)

    deployments = [
        {"name": "ChenWuYu68", "force": 1, "position": [43, 17]},
        {"name": "BaoGuo68", "force": 1, "position": [43, 24]},
        {"name": "WangHei68", "force": 1, "position": [39, 20]},
        {"name": "LuanShi68", "force": 3, "position": [57, 18]},
        {"name": "GaoQiang68", "force": 3, "position": [57, 23]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: large Mengde capital pursuit map\n"
        "Primary request: the eastern wards of Linzi, a broad avenue from the palace district to a two-cell east gate, "
        "with room outside the wall for fleeing clan troops.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic.\n"
        "Constraints: no units, text, UI or visible grid; continuous walls, east gate and buildings are separate overlays.\n"
    )
    common.save_map(
        "m117", "ch68", image, rows, source, prompt, walls, gates, sites, deployments,
        {
            "linzi_east_wards": [[5, 3], [62, 40]],
            "tiger_gate_route": [[31, 14], [61, 27]],
            "urban_wards": [[12, 7], [58, 36]],
            "east_gate": [[62, 20], [62, 21]],
        },
        {
            "type": "linzi_four_clans",
            "gate_name": "linzi_east_gate",
            "retreat": ["LuanShi68", "GaoQiang68"],
            "ally_trigger": [56, 20],
        },
    )


if __name__ == "__main__":
    build_linzi_east_gate()
    print("chapter 68 map generated: m117 72x44")
