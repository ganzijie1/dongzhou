from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def build_rows(width, height, mode):
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            border = min(x, width - 1 - x, y, height - 1 - y)
            if mode == "bi":
                if (5 <= x <= 16 and 5 <= y <= 12) or (2 <= x <= 11 and 20 <= y <= 30):
                    tile = "m" if (x + y) % 4 else "r"
                elif abs(y - (18 - x // 15)) <= 1:
                    tile = "w"
                elif border <= 2 and (x * 2 + y) % 5 < 2:
                    tile = "F"
                else:
                    tile = "g" if (x * 3 + y * 2) % 10 < 2 else "f"
            else:
                if 4 <= y <= 6 and x < width - 5:
                    tile = "~"
                elif 4 <= y <= 6 and x >= width - 5:
                    tile = "w"
                elif 7 <= y <= 10:
                    tile = "w" if (x + y) % 3 else "g"
                elif (x <= 10 and y >= 22) or (x >= 38 and y >= 24):
                    tile = "m" if (x + y) % 5 else "F"
                elif abs(y - (20 - x // 8)) <= 1:
                    tile = "w"
                elif border <= 1 and (x + y * 2) % 4 < 2:
                    tile = "F"
                else:
                    tile = "g" if (x * 2 + y) % 9 < 2 else "f"
            row.append(tile)
        rows.append(row)
    return rows


def render(source_name, rows):
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (len(rows[0]) * CELL, len(rows) * CELL))
    image = natural.natural_overlay(image, rows)
    return image


def river_overlay(image, width):
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 4 * CELL, (width - 5) * CELL, 7 * CELL), fill=(58, 103, 111, 125))
    for y in (4 * CELL + 14, 5 * CELL + 22, 6 * CELL + 18):
        draw.line((0, y, (width - 5) * CELL, y + 8), fill=(168, 197, 190, 65), width=4)


def save(map_id, suffix, source, prompt, image, rows, deployments, mission):
    data = {
        "map": f"assets/lzc/map/{map_id}.png", "source_base": f"output/imagegen/{source}",
        "prompt_file": f"output/imagegen/{prompt}", "grid": [len(rows[0]), len(rows)], "cell_pixels": CELL,
        "terrain_rows": ["".join(row) for row in rows],
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [], "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [], "castle_cells": [],
        "supply_sites": [], "blocked_edges": [], "deployments": deployments, "mission": mission, "visual_grid_in_game": False,
    }
    path = ROOT / "assets/lzc/map" / f"{map_id}.png"; image.convert("RGB").save(path, "PNG", compress_level=3)
    (ROOT / "assets/lzc/map_sources" / f"{map_id}_{suffix}_manifest.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    common.review_image(image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()}, deployments,
                        ROOT / "output/terrain_model" / f"{map_id}_{suffix}_review.png")
    prediction = {"map": data["map"], "grid": data["grid"], "backend": "reviewed-contract-with-dinov3-evidence-slot",
                  "threshold": 0.72, "auto_apply": False, "review_required": [],
                  "note": "Classifier evidence cannot overwrite reviewed river, rocky barrier, or Lua terrain rows."}
    (ROOT / "output/terrain_model" / f"{map_id}_{suffix}_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    stat = ImageStat.Stat(image.convert("RGB")); assert image.size == (len(rows[0]) * CELL, len(rows) * CELL) and max(stat.var) > 100
    print(map_id, data["grid"], image.size, [round(v, 2) for v in stat.var])


def build_bi():
    width, height = 58, 36; rows = build_rows(width, height, "bi")
    deployments = [
        {"name": "ChuZhuangWang51", "force": 1, "position": [48, 18]},
        {"name": "GongZiYingQi51", "force": 1, "position": [47, 9]},
        {"name": "GongZiCe51", "force": 1, "position": [47, 27]},
        {"name": "XunLinFu47", "force": 3, "position": [25, 18]},
        {"name": "XunYing54", "force": 3, "position": [18, 15]},
    ]
    source = "chapter54-bi-base-gpt2.png"; image = render(source, rows)
    save("m085", "ch54a", source, "m085_prompt.txt", image, rows, deployments, {
        "type": "battle_of_bi_main_assault", "victory": "break Jin center and capture XunYing54",
        "historical_survivors": ["XunLinFu47", "ShiHui47"], "captured": "XunYing54",
    })


def build_river():
    width, height = 52, 34; rows = build_rows(width, height, "river")
    deployments = [
        {"name": "XunShou54", "force": 1, "position": [44, 9]},
        {"name": "WeiQi54", "force": 1, "position": [46, 11]},
        {"name": "XiangLao54", "force": 3, "position": [24, 20]},
        {"name": "GongZiGuChen54", "force": 3, "position": [27, 22]},
    ]
    source = "chapter54-river-retreat-base-gpt2.png"; image = render(source, rows); river_overlay(image, width)
    save("m086", "ch54b", source, "m086_prompt.txt", image, rows, deployments, {
        "type": "xun_shou_counterattack", "river_rows": [4, 6], "northeast_ford_columns": [47, 51],
        "duel_outcomes": {"XiangLao54": "historical_death", "GongZiGuChen54": "captured_alive"},
        "escape": [48, 8],
    })


def main():
    for path in (ROOT / "assets/lzc/map", ROOT / "assets/lzc/map_sources", ROOT / "output/terrain_model"):
        path.mkdir(parents=True, exist_ok=True)
    build_bi(); build_river()


if __name__ == "__main__": main()
