from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageEnhance, ImageStat

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
            if mode == "daji":
                road = 13 + (x // 12) % 2
                if abs(y - road) <= 1:
                    tile = "w"
                elif border <= 2 and (x * 2 + y) % 4 < 2:
                    tile = "F"
                elif border <= 5 and (x + y * 3) % 9 == 0:
                    tile = "m"
                else:
                    tile = "g" if (x + y * 2) % 6 < 2 else "f"
            elif mode == "jiao":
                if border <= 2 and (x + y * 3) % 6 < 2:
                    tile = "F"
                elif y <= 4 and x >= 25 and (x + y) % 4 == 0:
                    tile = "m"
                elif abs(y - 14) <= 1:
                    tile = "w"
                else:
                    tile = "g" if (x * 2 + y) % 7 < 2 else "f"
            else:
                if border <= 2 and (x + y * 2) % 4 < 2:
                    tile = "F"
                elif abs(y - 12) <= 1:
                    tile = "w"
                else:
                    tile = "g" if (x + y) % 6 < 2 else "f"
            row.append(tile)
        rows.append(row)
    return rows


def place(rows, cells, terrain):
    for x, y in cells:
        rows[y][x] = terrain


def manifest(map_id, source, prompt, rows, deployments, mission):
    return {
        "map": f"assets/lzc/map/{map_id}.png",
        "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{prompt}",
        "grid": [len(rows[0]), len(rows)],
        "cell_pixels": CELL,
        "terrain_rows": ["".join(r) if isinstance(r, list) else r for r in rows],
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [],
        "castle_cells": [], "supply_sites": [], "blocked_edges": [],
        "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }


def render(source_name, rows):
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (len(rows[0]) * CELL, len(rows) * CELL))
    return natural.natural_overlay(image, rows)


def save(map_id, image, rows, data, structures):
    map_path = ROOT / "assets/lzc/map" / f"{map_id}.png"
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    manifest_path = ROOT / "assets/lzc/map_sources" / data.pop("manifest_name")
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, structures, data["deployments"], ROOT / "output/terrain_model" / f"{map_id}_ch50_review.png")
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (len(rows[0]) * CELL, len(rows) * CELL) and max(stat.var) > 100
    print(map_id, data["grid"], image.size, [round(v, 2) for v in stat.var])


def build_daji():
    width, height = 42, 28
    rows = base_rows(width, height, "daji")
    deployments = [
        {"name": "GongZiGuiSheng50", "force": 1, "position": [34, 13]},
        {"name": "HuaYuan50", "force": 3, "position": [8, 14]},
    ]
    source = "chapter50-daji-base-gpt2.png"
    image = render(source, rows)
    data = manifest("m078", source, "m078_prompt.txt", rows, deployments, {
        "type": "battle_of_daji", "target": "HuaYuan50", "target_outcome": "captured_not_killed",
    })
    data["manifest_name"] = "m078_ch50a_manifest.json"
    save("m078", image, rows, data, {"walls": set(), "fences": set(), "gates": set(), "sites": set()})


def build_jiao():
    width, height = 46, 30
    bounds = (2, 5, 15, 24)
    gates = {(15, 14), (15, 15)}
    walls = common.rectangle_perimeter(*bounds) - gates
    interior = {(x, y) for y in range(6, 24) for x in range(3, 15)}
    rows = base_rows(width, height, "jiao")
    place(rows, interior, "i")
    place(rows, walls, "W")
    place(rows, gates, "G")
    deployments = [
        {"name": "ZhaoChuan48", "force": 1, "position": [39, 14]},
        {"name": "QinSiegeCaptain50", "force": 3, "position": [22, 14]},
        {"name": "JiaoDefender50", "force": 2, "position": [12, 14]},
    ]
    source = "chapter50-jiao-base-gpt2.png"
    image = render(source, rows)
    common.draw_walls(image, walls, bounds)
    data = manifest("m079", source, "m079_prompt.txt", rows, deployments, {
        "type": "relief_of_jiao", "relief_gate": [15, 14], "hold_turns": 3,
        "qin_outcome": "withdraws_after_relief",
    })
    data.update({
        "manifest_name": "m079_ch50b_manifest.json",
        "structure_regions": {"jiao_city": [[2, 5], [15, 24]]},
        "wall_cells": [list(c) for c in sorted(walls)],
        "gates": [{"name": "jiao_east_gate", "cells": [list(c) for c in sorted(gates)]}],
    })
    save("m079", image, rows, data, {"walls": walls, "fences": set(), "gates": gates, "sites": set()})


def build_taoyuan():
    width, height = 38, 26
    bounds = (12, 3, 35, 22)
    gates = {(12, 12), (12, 13)}
    walls = common.rectangle_perimeter(*bounds) - gates
    interior = {(x, y) for y in range(4, 22) for x in range(13, 35)}
    rows = base_rows(width, height, "taoyuan")
    place(rows, interior, "i")
    place(rows, walls, "W")
    place(rows, gates, "G")
    deployments = [
        {"name": "ZhaoDun47", "force": 1, "position": [29, 12]},
        {"name": "TiMiMing50", "force": 1, "position": [27, 13]},
        {"name": "JinLingGong50", "force": 3, "position": [31, 7]},
        {"name": "TuAnGu50", "force": 3, "position": [29, 7]},
        {"name": "LingAo50", "force": 3, "position": [24, 12]},
    ]
    source = "chapter50-taoyuan-base-gpt2.png"
    image = render(source, rows)
    common.draw_walls(image, walls, bounds)
    # Darken the open western avenue slightly so the escape route reads without a visible grid.
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle((0, 11 * CELL, 13 * CELL, 15 * CELL), radius=40, fill=(94, 76, 58, 24))
    image = Image.alpha_composite(image, shade)
    data = manifest("m080", source, "m080_prompt.txt", rows, deployments, {
        "type": "taoyuan_escape", "first_target": "LingAo50", "escape": [1, 13],
        "TiMiMing50": "historical_sacrifice", "ZhaoDun47": "must_escape",
    })
    data.update({
        "manifest_name": "m080_ch50c_manifest.json",
        "structure_regions": {"taoyuan_palace": [[12, 3], [35, 22]]},
        "wall_cells": [list(c) for c in sorted(walls)],
        "gates": [{"name": "taoyuan_west_gate", "cells": [list(c) for c in sorted(gates)]}],
    })
    save("m080", image, rows, data, {"walls": walls, "fences": set(), "gates": gates, "sites": set()})


def main():
    for path in (ROOT / "assets/lzc/map", ROOT / "assets/lzc/map_sources", ROOT / "output/terrain_model"):
        path.mkdir(parents=True, exist_ok=True)
    build_daji()
    build_jiao()
    build_taoyuan()


if __name__ == "__main__":
    main()
