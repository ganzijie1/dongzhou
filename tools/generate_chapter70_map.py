from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as structures
import generate_chapter60_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def build_ying_coup() -> None:
    width, height = 68, 46
    rows = common.natural_rows(width, height)
    bounds = (7, 4, 52, 37)
    east_gate = {(52, 20), (52, 21)}
    south_gate = {(29, 37), (30, 37)}
    gates = east_gate | south_gate
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(24, 10), (16, 23), (39, 23)}

    for y in range(5, 37):
        for x in range(8, 52):
            rows[y][x] = "i"
    for x0, y0, x1, y1 in (
        (11, 8, 19, 15), (31, 8, 43, 15),
        (11, 27, 20, 33), (34, 27, 46, 33),
    ):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                rows[y][x] = "h"
    for x in range(8, 53):
        rows[20][x] = "i"
        rows[21][x] = "i"
    for y in range(5, 38):
        rows[y][28] = "i"
        rows[y][29] = "i"
        rows[y][30] = "i"
        rows[y][31] = "i"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter36-jiang-palace-base-gpt2.png"
    image = common.base_image(source, width, height, rows)
    city_tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(city_tint).rectangle(
        (8 * CELL, 5 * CELL, 52 * CELL, 37 * CELL), fill=(126, 103, 78, 82)
    )
    image = Image.alpha_composite(image, city_tint.filter(ImageFilter.GaussianBlur(8)))
    structures.draw_walls(image, walls, bounds)
    structures.draw_castles(image, sites | {(13, 12), (38, 12), (14, 30), (42, 30)})

    deployments = [
        {"name": "GongZiQiJi69", "force": 1, "position": [61, 20]},
        {"name": "ZiGan70", "force": 1, "position": [62, 18]},
        {"name": "ZiXi70", "force": 1, "position": [62, 23]},
        {"name": "ChaoWu69", "force": 1, "position": [58, 17]},
        {"name": "XiaNie70", "force": 1, "position": [58, 25]},
        {"name": "XuWuMou70", "force": 1, "position": [64, 21]},
        {"name": "ChenCaiGuard70", "force": 1, "position": [56, 19]},
        {"name": "ChenCaiGuard70", "force": 1, "position": [56, 22]},
        {"name": "ChenCaiGuard70", "force": 1, "position": [59, 16]},
        {"name": "ChenCaiGuard70", "force": 1, "position": [59, 25]},
        {"name": "ChenCaiArcher70", "force": 1, "position": [55, 17]},
        {"name": "ChenCaiArcher70", "force": 1, "position": [55, 24]},
        {"name": "ChenCaiArcher70", "force": 1, "position": [61, 15]},
        {"name": "ChenCaiArcher70", "force": 1, "position": [61, 26]},
        {"name": "CaiWei69", "force": 2, "position": [50, 20]},
        {"name": "DouChengRan70", "force": 2, "position": [50, 21]},
        {"name": "WeiPi70", "force": 3, "position": [24, 10]},
        {"name": "ShiZiLu70", "force": 3, "position": [16, 23]},
        {"name": "GongZiBa70", "force": 3, "position": [39, 23]},
        {"name": "ChuPalaceGuard70", "force": 3, "position": [48, 18]},
        {"name": "ChuPalaceGuard70", "force": 3, "position": [48, 23]},
        {"name": "ChuPalaceGuard70", "force": 3, "position": [43, 20]},
        {"name": "ChuPalaceGuard70", "force": 3, "position": [43, 21]},
        {"name": "ChuPalaceArcher70", "force": 3, "position": [46, 16]},
        {"name": "ChuPalaceArcher70", "force": 3, "position": [46, 25]},
        {"name": "ChuPalaceArcher70", "force": 3, "position": [34, 18]},
        {"name": "ChuPalaceArcher70", "force": 3, "position": [34, 23]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: large Mengde palace-coup battle map\n"
        "Primary request: broad eastern approach leading through a two-cell gate into a continuous-walled "
        "Ying capital, with a central avenue, palace compound, government residences, and open deployment ground.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\n"
        "Constraints: no units, text, UI, or visible grid; walls, gates, buildings, and supply sites are separate overlays.\n"
    )
    common.save_map(
        "m119", "ch70", image, rows, source, prompt, walls, gates, sites, deployments,
        {
            "ying_city": [[7, 4], [52, 37]],
            "east_gate": [[52, 20], [52, 21]],
            "south_gate": [[29, 37], [30, 37]],
            "palace_avenue": [[8, 20], [52, 21]],
            "eastern_rebel_assembly": [[55, 15], [66, 27]],
        },
        {
            "type": "ying_capital_coup",
            "gate_name": "ying_east_and_south_gates",
            "active_gate": "east_gate",
            "gate_openers": ["CaiWei69", "DouChengRan70"],
            "palace_targets": ["ShiZiLu70", "GongZiBa70"],
            "historical_outcome": "qianxi_army_disperses_without_killing_chu_ling_wang",
        },
    )


if __name__ == "__main__":
    build_ying_coup()
    print("chapter 70 map generated: m119 68x46")
