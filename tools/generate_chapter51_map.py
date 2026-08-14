from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WIDTH = 48
HEIGHT = 34


def build_rows():
    rows = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            border = min(x, WIDTH - 1 - x, y, HEIGHT - 1 - y)
            if 27 <= y <= 29 and x < 44:
                tile = "~"
            elif x >= 44 and 26 <= y <= 30:
                tile = "w"
            elif border <= 2 and y < 25 and (x * 2 + y * 3) % 5 < 2:
                tile = "F"
            elif y <= 6 and ((x <= 13) or (x >= 35)):
                tile = "F" if (x + y) % 4 else "m"
            elif (x <= 6 or x >= 41) and y <= 23 and (x + y * 2) % 5 == 0:
                tile = "m"
            elif 22 <= y <= 26:
                tile = "w" if (x + y) % 4 < 2 else "g"
            elif abs(y - (15 + (x // 13) % 2)) <= 1:
                tile = "w"
            else:
                tile = "g" if (x * 2 + y) % 7 < 2 else "f"
            row.append(tile)
        rows.append("".join(row))
    return rows


def main():
    rows = build_rows()
    deployments = [
        {"name": "ChuZhuangWang51", "force": 1, "position": [24, 25]},
        {"name": "GongZiCe51", "force": 1, "position": [39, 17]},
        {"name": "GongZiYingQi51", "force": 1, "position": [9, 17]},
        {"name": "PanWang51", "force": 1, "position": [37, 10]},
        {"name": "LeBo51", "force": 1, "position": [11, 10]},
        {"name": "YangYouJi51", "force": 1, "position": [19, 23]},
        {"name": "DouYueJiao40", "force": 3, "position": [24, 16]},
        {"name": "DouBenHuang51", "force": 3, "position": [26, 14]},
    ]
    source_name = "chapter51-qinghe-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (WIDTH * CELL, HEIGHT * CELL))
    image = natural.natural_overlay(image, rows)

    # Broken bridge stubs stop at the impassable river cells; no visual or logical crossing remains.
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = 24 * CELL + CELL // 2
    bank_north = 27 * CELL
    bank_south = 30 * CELL
    wood = (92, 69, 45, 210)
    edge = (44, 33, 25, 220)
    draw.polygon([(cx - 34, bank_north - 34), (cx + 34, bank_north - 34),
                  (cx + 25, bank_north + 18), (cx - 28, bank_north + 5)], fill=wood, outline=edge)
    draw.polygon([(cx - 28, bank_south - 6), (cx + 25, bank_south - 18),
                  (cx + 34, bank_south + 34), (cx - 34, bank_south + 34)], fill=wood, outline=edge)
    for dx in (-22, 0, 22):
        draw.line((cx + dx, bank_north - 32, cx + dx - 3, bank_north + 9), fill=edge, width=4)
        draw.line((cx + dx - 3, bank_south - 9, cx + dx, bank_south + 32), fill=edge, width=4)
    image = Image.alpha_composite(image, overlay)

    map_path = ROOT / "assets/lzc/map/m081.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m081.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": "output/imagegen/m081_prompt.txt",
        "grid": [WIDTH, HEIGHT], "cell_pixels": CELL, "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth river and broken bridge",
        "structure_regions": {}, "camp_icon_cells": [], "camp_cells": [], "fence_cells": [],
        "fence_geometry": "no fences in this battlefield", "wall_cells": [], "gates": [],
        "castle_cells": [], "supply_sites": [], "blocked_edges": [],
        "deployments": deployments,
        "mission": {
            "type": "qinghe_bridge_encirclement",
            "river_rows": [27, 29], "east_ford_columns": [44, 47],
            "broken_bridge_center": [24, 28], "broken_bridge_passable": False,
            "duel": {"attacker": "YangYouJi51", "defender": "DouYueJiao40", "outcome": "historical_death"},
            "DouBenHuang51": "escapes_to_Jin",
        },
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m081_ch51_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review = ROOT / "output/terrain_model/m081_ch51_review.png"
    common.review_image(image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()}, deployments, review)
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (WIDTH * CELL, HEIGHT * CELL) and max(stat.var) > 100
    print(f"m081: {WIDTH}x{HEIGHT}, pixels={image.size}, variance={[round(v, 2) for v in stat.var]}")


if __name__ == "__main__":
    main()
