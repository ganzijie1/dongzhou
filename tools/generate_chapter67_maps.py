from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as structures
import generate_chapter60_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def tint_city(image: Image.Image, bounds: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> Image.Image:
    x0, y0, x1, y1 = bounds
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle(
        (x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL), fill=color
    )
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(7)))


def build_qi_temple() -> None:
    width, height = 68, 44
    rows = common.natural_rows(width, height)
    bounds = (7, 3, 61, 40)
    gates = {(7, 20), (7, 21)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(34, 11), (48, 14)}
    decor = {(17, 10), (22, 15), (46, 10), (53, 17), (17, 28), (24, 33), (42, 29), (52, 33)}

    for y in range(4, 40):
        for x in range(8, 61):
            rows[y][x] = "i" if (x + y) % 8 else "h"
    for x0, y0, x1, y1 in ((27, 7, 41, 17), (43, 9, 54, 19), (14, 25, 25, 34), (37, 25, 53, 35)):
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

    source = "chapter38-wangcheng-base-gpt2.png"
    image = tint_city(common.base_image(source, width, height, rows), bounds, (118, 99, 79, 76))
    structures.draw_walls(image, walls, bounds)
    structures.draw_castles(image, sites | decor)
    deployments = [
        {"name": "LuPuGui67", "force": 1, "position": [32, 14]},
        {"name": "GaoChai67", "force": 1, "position": [29, 16]},
        {"name": "LuanZao67", "force": 1, "position": [38, 16]},
        {"name": "QingShe67", "force": 3, "position": [34, 11]},
        {"name": "QingFeng62", "force": 3, "position": [3, 20]},
        {"name": "QingSi67", "force": 3, "position": [3, 16]},
        {"name": "QingYi67", "force": 3, "position": [3, 25]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: large Mengde capital coup map\n"
        "Primary request: Linzi city with a spacious ancestral temple in the center and a broad western approach. "
        "Reserve a continuous city-wall perimeter and a two-cell west gate.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic.\n"
        "Constraints: no units, text, UI or visible grid; walls, gates and temple buildings are separate overlays.\n"
    )
    common.save_map(
        "m115", "ch67a", image, rows, source, prompt, walls, gates, sites, deployments,
        {"linzi_city": [[7, 3], [61, 40]], "taimiao": [[27, 7], [41, 17]], "urban_wards": [[14, 9], [54, 34]], "west_gate": [[7, 20], [7, 21]]},
        {"type": "qing_clan_collapse", "gate_name": "linzi_west_gate", "phases": ["temple_coup", "west_gate_counterattack"]},
    )


def build_zheng_north_gate() -> None:
    width, height = 62, 42
    rows = common.natural_rows(width, height)
    bounds = (6, 18, 55, 39)
    gates = {(30, 18), (31, 18)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(18, 28), (30, 30), (43, 28)}
    decor = {(12, 23), (20, 33), (26, 34), (38, 34), (49, 23), (14, 34), (47, 34)}

    for y in range(19, 39):
        for x in range(7, 55):
            rows[y][x] = "i" if (x * 3 + y) % 9 else "h"
    for y in range(2, 17):
        for x in range(20, 43):
            rows[y][x] = "f" if (x + y) % 5 else "g"
    for x, y in decor:
        rows[y][x] = "h"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in gates:
        rows[y][x] = "G"
    for x, y in sites:
        rows[y][x] = "C"

    source = "chapter53-zheng-siege-base-gpt2.png"
    image = tint_city(common.base_image(source, width, height, rows), bounds, (126, 107, 82, 72))
    structures.draw_walls(image, walls, bounds)
    structures.draw_castles(image, sites | decor)
    deployments = [
        {"name": "GongSunHei67", "force": 2, "position": [30, 25]},
        {"name": "SiDai67", "force": 1, "position": [27, 21]},
        {"name": "YinDuan67", "force": 1, "position": [34, 21]},
        {"name": "LiangXiao67", "force": 3, "position": [30, 7]},
    ]
    prompt = (
        "Use case: historical-scene\nAsset type: Mengde city-gate defense map\n"
        "Primary request: Zheng northern countryside leading to one two-cell north gate, with a continuous southern city wall and dense city interior.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic.\n"
        "Constraints: no units, text, UI or visible grid; walls, gate and city buildings are separate overlays.\n"
    )
    common.save_map(
        "m116", "ch67b", image, rows, source, prompt, walls, gates, sites, deployments,
        {"zheng_city": [[6, 18], [55, 39]], "north_gate": [[30, 18], [31, 18]], "urban_wards": [[10, 22], [51, 35]], "yongliang_route": [[20, 2], [42, 17]]},
        {"type": "boyou_rebellion", "gate_name": "zheng_north_gate", "historical_death": "LiangXiao67"},
    )


if __name__ == "__main__":
    build_qi_temple()
    build_zheng_north_gate()
    print("chapter 67 maps generated: m115 68x44, m116 62x42")
