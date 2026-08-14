from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as structures
import generate_chapter60_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def build_shangcai() -> None:
    width, height = 64, 46
    rows = common.natural_rows(width, height)
    bounds = (9, 3, 54, 37)
    north_gate = {(31, 3), (32, 3)}
    south_gate = {(31, 37), (32, 37)}
    gates = north_gate | south_gate
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(31, 9), (21, 18), (42, 18)}
    decor = {
        (15, 9), (20, 11), (23, 8), (40, 9), (45, 11), (49, 8),
        (15, 26), (20, 29), (23, 25), (40, 26), (45, 29), (49, 25),
        (27, 18), (36, 18), (27, 27), (36, 27),
    }
    residences = (
        (13, 7, 24, 13), (39, 7, 50, 13),
        (13, 23, 24, 31), (39, 23, 50, 31),
    )

    for y in range(4, 37):
        for x in range(10, 54):
            rows[y][x] = "i"
    for x0, y0, x1, y1 in residences:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                rows[y][x] = "h"
    for y in range(4, 38):
        rows[y][30] = "i"
        rows[y][31] = "i"
        rows[y][32] = "i"
        rows[y][33] = "i"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter55-suiyang-base-gpt2.png"
    image = common.base_image(source, width, height, rows)
    city_tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(city_tint).rectangle(
        (10 * CELL, 4 * CELL, 54 * CELL, 37 * CELL), fill=(126, 106, 78, 82)
    )
    image = Image.alpha_composite(image, city_tint.filter(ImageFilter.GaussianBlur(7)))
    structures.draw_walls(image, walls, bounds)
    structures.draw_castles(image, sites | decor)

    deployments = [
        {"name": "GongZiQiJi69", "force": 1, "position": [31, 42]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [25, 41]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [28, 42]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [35, 42]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [38, 41]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [23, 43]},
        {"name": "ChuSiegeGuard69", "force": 1, "position": [40, 43]},
        {"name": "ChuSiegeArcher69", "force": 1, "position": [27, 44]},
        {"name": "ChuSiegeArcher69", "force": 1, "position": [31, 44]},
        {"name": "ChuSiegeArcher69", "force": 1, "position": [32, 44]},
        {"name": "ChuSiegeArcher69", "force": 1, "position": [36, 44]},
        {"name": "CaiShiZiYou69", "force": 3, "position": [31, 9]},
        {"name": "GongSunGuiSheng69", "force": 3, "position": [21, 18]},
        {"name": "ChaoWu69", "force": 3, "position": [42, 18]},
        {"name": "CaiGuard69", "force": 3, "position": [31, 36]},
        {"name": "CaiGuard69", "force": 3, "position": [32, 36]},
        {"name": "CaiGuard69", "force": 3, "position": [26, 32]},
        {"name": "CaiGuard69", "force": 3, "position": [37, 32]},
        {"name": "CaiGuard69", "force": 3, "position": [18, 28]},
        {"name": "CaiGuard69", "force": 3, "position": [45, 28]},
        {"name": "CaiGuard69", "force": 3, "position": [26, 14]},
        {"name": "CaiGuard69", "force": 3, "position": [37, 14]},
        {"name": "CaiGuard69", "force": 3, "position": [31, 5]},
        {"name": "CaiGuard69", "force": 3, "position": [32, 5]},
        {"name": "CaiArcher69", "force": 3, "position": [28, 34]},
        {"name": "CaiArcher69", "force": 3, "position": [35, 34]},
        {"name": "CaiArcher69", "force": 3, "position": [17, 25]},
        {"name": "CaiArcher69", "force": 3, "position": [46, 25]},
        {"name": "CaiArcher69", "force": 3, "position": [27, 12]},
        {"name": "CaiArcher69", "force": 3, "position": [36, 12]},
        {"name": "CaiArcher69", "force": 3, "position": [29, 7]},
        {"name": "CaiArcher69", "force": 3, "position": [34, 7]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: large Mengde siege battle map\n"
        "Primary request: broad natural approaches around the fortified Cai capital, with a long north-south avenue, "
        "dense wards, and ample southern deployment ground for a prolonged Chu siege.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\n"
        "Constraints: no units, text, UI or visible grid; continuous walls, gates and buildings are separate overlays.\n"
    )
    common.save_map(
        "m118", "ch69", image, rows, source, prompt, walls, gates, sites, deployments,
        {
            "shangcai_city": [[9, 3], [54, 37]],
            "north_gate": [[31, 3], [32, 3]],
            "south_gate": [[31, 37], [32, 37]],
            "central_avenue": [[30, 3], [33, 37]],
            "residential_wards": [[13, 7], [50, 31]],
            "southern_chu_lines": [[20, 39], [43, 45]],
        },
        {
            "type": "merged_chen_cai_campaign",
            "gate_name": "shangcai_north_and_south_gates",
            "active_gate": "south_gate",
            "messenger_escape_turn": 3,
            "parley_turn": 6,
            "final_assault_turn": 8,
            "capture": ["CaiShiZiYou69"],
        },
    )


if __name__ == "__main__":
    build_shangcai()
    print("chapter 69 map generated: m118 64x46")
