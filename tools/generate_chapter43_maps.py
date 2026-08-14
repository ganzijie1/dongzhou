from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WALL_SRC = ROOT / "assets/lzc/map_sources/haojing/wall-strip.png"
CAMP_SRC = ROOT / "assets/lzc/map_sources/changshao/camp.png"
FENCE_H_SRC = ROOT / "assets/lzc/terrain/fence-queshan-horizontal.png"
FENCE_V_SRC = ROOT / "assets/lzc/terrain/fence-queshan-vertical.png"


def rectangle_perimeter(x0, y0, x1, y1):
    return ({(x, y0) for x in range(x0, x1 + 1)} |
            {(x, y1) for x in range(x0, x1 + 1)} |
            {(x0, y) for y in range(y0, y1 + 1)} |
            {(x1, y) for y in range(y0, y1 + 1)})


def paste_centered(image, sprite, cell):
    cx, cy = cell[0] * CELL + CELL // 2, cell[1] * CELL + CELL // 2
    image.alpha_composite(sprite, (cx - sprite.width // 2, cy - sprite.height // 2))


def base_rows(width, height):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            terrain = "g" if (x + y * 2) % 6 in (0, 1) else "f"
            if y <= 2 or y >= height - 3:
                if (x * 3 + y) % 7 in (0, 1):
                    terrain = "F"
            if x <= 2 or x >= width - 3:
                if (x + y * 3) % 8 in (0, 1):
                    terrain = "m"
            row.append(terrain)
        rows.append(row)
    return rows


def draw_walls(canvas, walls, bounds):
    source = Image.open(WALL_SRC).convert("RGBA")
    horizontal = source.crop((0, 0, 48, 48)).resize((CELL, CELL), Image.Resampling.LANCZOS)
    vertical = horizontal.rotate(90, expand=False)
    x0, y0, x1, y1 = bounds
    for cell in sorted(walls):
        x, y = cell
        sprite = horizontal if y in (y0, y1) else vertical
        paste_centered(canvas, sprite, cell)


def draw_fences(canvas, fences, bounds):
    horizontal = Image.open(FENCE_H_SRC).convert("RGBA").resize((CELL, 18), Image.Resampling.LANCZOS)
    vertical = Image.open(FENCE_V_SRC).convert("RGBA").resize((18, CELL), Image.Resampling.LANCZOS)
    x0, y0, x1, y1 = bounds
    for cell in sorted(fences):
        x, y = cell
        sprite = horizontal if y in (y0, y1) else vertical
        paste_centered(canvas, sprite, cell)


def draw_sites(canvas, sites):
    camp = Image.open(CAMP_SRC).convert("RGBA")
    camp = ImageEnhance.Contrast(camp).enhance(1.08).resize((44, 44), Image.Resampling.LANCZOS)
    for cell in sorted(sites):
        paste_centered(canvas, camp, cell)


def draw_castles(canvas, castles):
    names = ["building-25.png", "building-37.png", "building-47.png"]
    for index, cell in enumerate(sorted(castles)):
        sprite = Image.open(ROOT / "assets/lzc/map_sources/haojing" / names[index % len(names)]).convert("RGBA")
        sprite = sprite.resize((56, 56), Image.Resampling.LANCZOS)
        paste_centered(canvas, sprite, cell)


def review_image(image, rows, structures, deployments, output):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    height, width = len(rows), len(rows[0])
    for x in range(width + 1):
        draw.line((x * CELL, 0, x * CELL, height * CELL), fill=(255, 255, 255, 80))
    for y in range(height + 1):
        draw.line((0, y * CELL, width * CELL, y * CELL), fill=(255, 255, 255, 80))
    colors = {"walls": (255, 55, 55, 255), "fences": (255, 120, 30, 255),
              "gates": (55, 255, 105, 255), "sites": (255, 220, 55, 255)}
    for key, cells in structures.items():
        for x, y in cells:
            draw.rectangle((x * CELL + 3, y * CELL + 3, (x + 1) * CELL - 4, (y + 1) * CELL - 4),
                           outline=colors[key], width=4)
    for item in deployments:
        x, y = item["position"]
        color = (255, 70, 70, 255) if item["force"] == 3 else (60, 220, 255, 255)
        draw.ellipse((x * CELL + 12, y * CELL + 12, (x + 1) * CELL - 12, (y + 1) * CELL - 12),
                     outline=color, width=4)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image.convert("RGBA"), overlay).save(output)


def build_map_65():
    width, height = 32, 24
    city_bounds = (8, 2, 23, 14)
    city_gates = {(15, 14), (16, 14)}
    walls = rectangle_perimeter(*city_bounds) - city_gates
    interior = {(x, y) for y in range(3, 14) for x in range(9, 23)}
    castles = {(14, 5), (16, 5), (18, 5)}
    camp_bounds = (10, 17, 21, 23)
    camp_gates = {(15, 17), (16, 17)}
    fences = rectangle_perimeter(*camp_bounds) - camp_gates
    camp_sites = {(13, 20), (18, 20)}
    rows = base_rows(width, height)
    for x, y in interior:
        rows[y][x] = "i"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in city_gates:
        rows[y][x] = "G"
    for x, y in castles:
        rows[y][x] = "C"
    for x, y in fences:
        rows[y][x] = "P"
    for x, y in camp_sites:
        rows[y][x] = "e"
    rows = ["".join(row) for row in rows]

    deployments = [
        {"name": "ChongEr27", "force": 1, "position": [15, 20]},
        {"name": "ZhaoShuai27", "force": 1, "position": [13, 21]},
        {"name": "HuYan27", "force": 1, "position": [17, 21]},
        {"name": "XianZhen27", "force": 1, "position": [19, 21]},
        {"name": "JinGuard43", "force": 1, "position": [12, 19]},
        {"name": "JinGuard43", "force": 1, "position": [18, 19]},
        {"name": "JinArcher43", "force": 1, "position": [16, 19]},
        {"name": "QinMuGong29", "force": 2, "position": [5, 16]},
        {"name": "CaoGongGong39", "force": 2, "position": [26, 16]},
        {"name": "GongSunGu33", "force": 2, "position": [27, 12]},
        {"name": "GuoGuiFu40", "force": 2, "position": [5, 12]},
        {"name": "XuXiGong43", "force": 3, "position": [16, 5]},
        {"name": "XuGuard43", "force": 3, "position": [15, 14]},
        {"name": "XuGuard43", "force": 3, "position": [16, 14]},
        {"name": "XuGuard43", "force": 3, "position": [12, 11]},
        {"name": "XuGuard43", "force": 3, "position": [20, 11]},
        {"name": "XuGuard43", "force": 3, "position": [14, 8]},
        {"name": "XuGuard43", "force": 3, "position": [18, 8]},
        {"name": "XuArcher43", "force": 3, "position": [11, 9]},
        {"name": "XuArcher43", "force": 3, "position": [21, 9]},
        {"name": "XuArcher43", "force": 3, "position": [15, 7]},
        {"name": "XuArcher43", "force": 3, "position": [17, 7]},
    ]

    source = Image.open(ROOT / "output/imagegen/chapter43-yingyang-base-gpt2.png").convert("RGB")
    image = source.resize((width * CELL, height * CELL), Image.Resampling.LANCZOS).convert("RGBA")
    tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tint)
    td.rectangle((9 * CELL, 3 * CELL, 23 * CELL, 14 * CELL), fill=(104, 90, 72, 76))
    image = Image.alpha_composite(image, tint.filter(ImageFilter.GaussianBlur(6)))
    draw_walls(image, walls, city_bounds)
    draw_castles(image, castles)
    draw_fences(image, fences, camp_bounds)
    draw_sites(image, camp_sites)
    output = ROOT / "assets/lzc/map/m065.png"
    image.convert("RGB").save(output, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m065.png", "source_base": "output/imagegen/chapter43-yingyang-base-gpt2.png",
        "prompt_file": "output/imagegen/m065_prompt.txt", "grid": [width, height], "cell_pixels": CELL,
        "terrain_rows": rows, "terrain_source": "GPT Image 2 natural base plus programmatic source-of-truth structures",
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "m"], "structure_mixing": False},
        "terrain_layers": [], "structure_regions": {"yingyang_city": [[8, 2], [23, 14]], "jin_camp": [[10, 17], [21, 23]]},
        "wall_cells": [list(c) for c in sorted(walls)], "fence_cells": [list(c) for c in sorted(fences)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [{"name": "yingyang_south_gate", "cells": [list(c) for c in sorted(city_gates)]},
                  {"name": "jin_north_gate", "cells": [list(c) for c in sorted(camp_gates)]}],
        "camp_icon_cells": [list(c) for c in sorted(camp_sites)], "camp_cells": [list(c) for c in sorted(camp_sites)],
        "castle_cells": [list(c) for c in sorted(castles)], "supply_sites": [list(c) for c in sorted(camp_sites | castles)],
        "blocked_edges": [], "deployments": deployments, "visual_grid_in_game": False,
    }
    path = ROOT / "assets/lzc/map_sources/m065_ch43a_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_image(image, rows, {"walls": walls, "fences": fences, "gates": city_gates | camp_gates, "sites": camp_sites | castles}, deployments,
                 ROOT / "output/terrain_model/m065_ch43a_review.png")
    return rows, deployments


def build_map_66():
    width, height = 36, 26
    city_bounds = (10, 4, 25, 20)
    city_gates = {(10, 11), (10, 12), (25, 11), (25, 12)}
    walls = rectangle_perimeter(*city_bounds) - city_gates
    interior = {(x, y) for y in range(5, 20) for x in range(11, 25)}
    castles = {(16, 7), (18, 7), (20, 7)}
    west_bounds = (1, 8, 8, 18)
    west_gates = {(8, 12), (8, 13)}
    east_bounds = (27, 8, 34, 18)
    east_gates = {(27, 12), (27, 13)}
    west_fences = rectangle_perimeter(*west_bounds) - west_gates
    east_fences = rectangle_perimeter(*east_bounds) - east_gates
    fences = west_fences | east_fences
    camp_sites = {(4, 11), (4, 15), (31, 11), (31, 15)}
    rows = base_rows(width, height)
    for x, y in interior:
        rows[y][x] = "i"
    for x, y in walls:
        rows[y][x] = "W"
    for x, y in city_gates:
        rows[y][x] = "G"
    for x, y in castles:
        rows[y][x] = "C"
    for x, y in fences:
        rows[y][x] = "P"
    for x, y in camp_sites:
        rows[y][x] = "e"
    rows = ["".join(row) for row in rows]

    deployments = [
        {"name": "ZhuZhiWu43", "force": 1, "position": [23, 12]},
        {"name": "ZhengWenGong43", "force": 2, "position": [18, 7]},
        {"name": "ShuZhan43", "force": 2, "position": [16, 9]},
        {"name": "YiZhiHu43", "force": 2, "position": [20, 9]},
        {"name": "QinMuGong29", "force": 2, "position": [31, 11]},
        {"name": "BailiXi29", "force": 2, "position": [31, 15]},
        {"name": "QinGuard43", "force": 2, "position": [29, 10]},
        {"name": "QinGuard43", "force": 2, "position": [29, 16]},
        {"name": "JinPatrol43", "force": 2, "position": [26, 8]},
        {"name": "JinPatrol43", "force": 2, "position": [26, 16]},
        {"name": "JinPatrol43", "force": 2, "position": [30, 21]},
        {"name": "JinPatrol43", "force": 2, "position": [30, 3]},
        {"name": "ChongEr27", "force": 2, "position": [4, 11]},
        {"name": "HuYan27", "force": 2, "position": [4, 15]},
    ]

    source = Image.open(ROOT / "output/imagegen/chapter43-zheng-base-gpt2.png").convert("RGB")
    image = source.resize((width * CELL, height * CELL), Image.Resampling.LANCZOS).convert("RGBA")
    tint = Image.new("RGBA", image.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tint)
    td.rectangle((11 * CELL, 5 * CELL, 25 * CELL, 20 * CELL), fill=(82, 88, 96, 72))
    image = Image.alpha_composite(image, tint.filter(ImageFilter.GaussianBlur(6)))
    draw_walls(image, walls, city_bounds)
    draw_castles(image, castles)
    draw_fences(image, west_fences, west_bounds)
    draw_fences(image, east_fences, east_bounds)
    draw_sites(image, camp_sites)
    output = ROOT / "assets/lzc/map/m066.png"
    image.convert("RGB").save(output, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m066.png", "source_base": "output/imagegen/chapter43-zheng-base-gpt2.png",
        "prompt_file": "output/imagegen/m066_prompt.txt", "grid": [width, height], "cell_pixels": CELL,
        "terrain_rows": rows, "terrain_source": "GPT Image 2 natural base plus programmatic source-of-truth structures",
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "m"], "structure_mixing": False},
        "terrain_layers": [], "structure_regions": {"zheng_city": [[10, 4], [25, 20]], "jin_camp": [[1, 8], [8, 18]], "qin_camp": [[27, 8], [34, 18]]},
        "wall_cells": [list(c) for c in sorted(walls)], "fence_cells": [list(c) for c in sorted(fences)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "gates": [{"name": "zheng_west_gate", "cells": [[10, 11], [10, 12]]},
                  {"name": "zheng_east_gate", "cells": [[25, 11], [25, 12]]},
                  {"name": "jin_east_gate", "cells": [list(c) for c in sorted(west_gates)]},
                  {"name": "qin_west_gate", "cells": [list(c) for c in sorted(east_gates)]}],
        "camp_icon_cells": [list(c) for c in sorted(camp_sites)], "camp_cells": [list(c) for c in sorted(camp_sites)],
        "castle_cells": [list(c) for c in sorted(castles)], "supply_sites": [list(c) for c in sorted(camp_sites | castles)],
        "blocked_edges": [], "deployments": deployments,
        "mission": {"type": "stealth_diplomacy", "combat_allowed": False, "player": "ZhuZhiWu43", "goal": [31, 11],
                    "checkpoints": [[25, 12], [28, 13], [30, 12]], "detection_radius": 2},
        "visual_grid_in_game": False,
    }
    path = ROOT / "assets/lzc/map_sources/m066_ch43b_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_image(image, rows, {"walls": walls, "fences": fences, "gates": city_gates | west_gates | east_gates, "sites": camp_sites | castles}, deployments,
                 ROOT / "output/terrain_model/m066_ch43b_review.png")
    return rows, deployments


def main():
    ROOT.joinpath("assets/lzc/map").mkdir(parents=True, exist_ok=True)
    ROOT.joinpath("assets/lzc/map_sources").mkdir(parents=True, exist_ok=True)
    rows65, dep65 = build_map_65()
    rows66, dep66 = build_map_66()
    print(f"m065: {len(rows65[0])}x{len(rows65)}, deployments={len(dep65)}")
    print(f"m066: {len(rows66[0])}x{len(rows66)}, deployments={len(dep66)}")


if __name__ == "__main__":
    main()
