from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def base_rows(width, height, mode):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if mode == "zhulin":
                road = abs(y - (14 + (x // 14) % 2)) <= 1
                if road:
                    tile = "w"
                elif border <= 2 and (x + y * 2) % 4 != 0:
                    tile = "F"
                elif x <= 13 and 4 <= y <= 25 and (x * 2 + y) % 5 < 2:
                    tile = "F"
                else:
                    tile = "g" if (x * 3 + y) % 9 < 2 else "f"
            else:
                road = abs(y - 16) <= 1 and 3 <= x <= 27
                if road:
                    tile = "w"
                elif border <= 2 and (x * 2 + y * 3) % 5 < 2:
                    tile = "F"
                elif y <= 6 and x <= 18 and (x + y) % 4 == 0:
                    tile = "m"
                else:
                    tile = "g" if (x + y * 2) % 8 < 2 else "f"
            row.append(tile)
        rows.append(row)
    return rows


def place(rows, cells, terrain):
    for x, y in cells:
        rows[y][x] = terrain


def render(source_name, rows):
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (len(rows[0]) * CELL, len(rows) * CELL))
    return natural.natural_overlay(image, rows)


def manifest(map_id, source, prompt, rows, deployments, mission):
    return {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{prompt}",
        "grid": [len(rows[0]), len(rows)], "cell_pixels": CELL,
        "terrain_rows": ["".join(row) for row in rows],
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth structure geometry",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [],
        "castle_cells": [], "supply_sites": [], "blocked_edges": [],
        "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }


def draw_manor(image, walls, bounds, gates):
    common.draw_walls(image, walls, bounds)
    draw = ImageDraw.Draw(image, "RGBA")
    x0, y0, x1, y1 = bounds
    for x, y, w, h in ((x0 + 5, y0 + 4, 5, 3), (x0 + 12, y0 + 4, 4, 3), (x0 + 8, y0 + 9, 6, 3)):
        px0, py0 = x * CELL + 5, y * CELL + 8
        px1, py1 = (x + w) * CELL - 5, (y + h) * CELL - 6
        draw.rectangle((px0, py0 + 18, px1, py1), fill=(151, 121, 82, 205), outline=(80, 61, 43, 225), width=3)
        draw.polygon(((px0 - 9, py0 + 20), ((px0 + px1) // 2, py0 - 10), (px1 + 9, py0 + 20)),
                     fill=(74, 75, 67, 225), outline=(47, 47, 43, 235))
    for gx, gy in gates:
        draw.rectangle((gx * CELL + 4, gy * CELL + 18, (gx + 1) * CELL - 4, (gy + 1) * CELL - 6),
                       fill=(116, 91, 60, 180))


def save(map_id, suffix, image, rows, data, structures):
    map_path = ROOT / "assets/lzc/map" / f"{map_id}.png"
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    manifest_path = ROOT / "assets/lzc/map_sources" / f"{map_id}_{suffix}_manifest.json"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, structures, data["deployments"], ROOT / "output/terrain_model" / f"{map_id}_{suffix}_review.png")
    prediction = {"map": data["map"], "grid": data["grid"], "backend": "reviewed-contract-with-dinov3-evidence-slot",
                  "threshold": 0.72, "auto_apply": False, "review_required": [],
                  "note": "Classifier evidence cannot overwrite reviewed structure or Lua terrain rows."}
    (ROOT / "output/terrain_model" / f"{map_id}_{suffix}_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (len(rows[0]) * CELL, len(rows) * CELL) and max(stat.var) > 100
    print(map_id, data["grid"], image.size, [round(v, 2) for v in stat.var])


def build_zhulin():
    width, height = 46, 30
    bounds = (25, 5, 43, 25)
    gates = {(25, 14), (25, 15)}
    walls = common.rectangle_perimeter(*bounds) - gates
    interior = {(x, y) for y in range(6, 25) for x in range(26, 43)}
    rows = base_rows(width, height, "zhulin")
    place(rows, interior, "i"); place(rows, walls, "W"); place(rows, gates, "G")
    deployments = [
        {"name": "ChuZhuangWang51", "force": 1, "position": [7, 15]},
        {"name": "GongZiYingQi51", "force": 1, "position": [9, 13]},
        {"name": "GongZiCe51", "force": 1, "position": [9, 17]},
        {"name": "QuWu53", "force": 1, "position": [6, 12]},
        {"name": "XiaZhengShu53", "force": 3, "position": [36, 15]},
    ]
    source = "chapter53-zhulin-base-gpt2.png"
    image = render(source, rows); draw_manor(image, walls, bounds, gates)
    data = manifest("m083", source, "m083_prompt.txt", rows, deployments, {
        "type": "capture_xia_zhengshu_at_zhulin", "target": "XiaZhengShu53", "outcome": "captured_then_executed",
    })
    data.update({"structure_regions": {"xia_manor": [[25, 5], [43, 25]]},
                 "wall_cells": [list(c) for c in sorted(walls)],
                 "gates": [{"name": "zhulin_west_gate", "cells": [list(c) for c in sorted(gates)]}]})
    save("m083", "ch53a", image, rows, data, {"walls": walls, "fences": set(), "gates": gates, "sites": set()})


def build_zheng():
    width, height = 52, 34
    bounds = (28, 3, 50, 31)
    gates = {(28, 16), (28, 17)}
    walls = common.rectangle_perimeter(*bounds) - gates
    interior = {(x, y) for y in range(4, 31) for x in range(29, 50)}
    rows = base_rows(width, height, "zheng")
    place(rows, interior, "i"); place(rows, walls, "W"); place(rows, gates, "G")
    deployments = [
        {"name": "ChuZhuangWang51", "force": 1, "position": [8, 17]},
        {"name": "LeBo51", "force": 1, "position": [20, 16]},
        {"name": "GongZiYingQi51", "force": 1, "position": [12, 11]},
        {"name": "GongZiCe51", "force": 1, "position": [12, 23]},
        {"name": "ZhengXiangGong52", "force": 3, "position": [44, 16]},
        {"name": "GongZiQuJi52", "force": 3, "position": [42, 18]},
    ]
    source = "chapter53-zheng-siege-base-gpt2.png"
    image = render(source, rows); common.draw_walls(image, walls, bounds)
    data = manifest("m084", source, "m084_prompt.txt", rows, deployments, {
        "type": "huangmen_breach_after_zheng_siege", "gate": [[28, 16], [28, 17]],
        "victory": "LeBo51 enters city after gate defenders are cleared", "zheng_outcome": "surrenders_not_destroyed",
    })
    data.update({"structure_regions": {"zheng_capital": [[28, 3], [50, 31]]},
                 "wall_cells": [list(c) for c in sorted(walls)],
                 "gates": [{"name": "huangmen_west_gate", "cells": [list(c) for c in sorted(gates)]}]})
    save("m084", "ch53b", image, rows, data, {"walls": walls, "fences": set(), "gates": gates, "sites": set()})


def main():
    for path in (ROOT / "assets/lzc/map", ROOT / "assets/lzc/map_sources", ROOT / "output/terrain_model"):
        path.mkdir(parents=True, exist_ok=True)
    build_zhulin(); build_zheng()


if __name__ == "__main__":
    main()
