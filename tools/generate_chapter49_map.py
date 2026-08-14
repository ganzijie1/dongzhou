from pathlib import Path
import json

from PIL import Image, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as prior


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WIDTH = 44
HEIGHT = 30


def terrain_rows():
    rows = []
    for y in range(HEIGHT):
        row = []
        road_center = 14 + (1 if 9 <= y <= 18 else 0)
        for x in range(WIDTH):
            border = min(x, WIDTH - 1 - x, y, HEIGHT - 1 - y)
            road_y = 14 + (1 if 12 <= x <= 29 else 0) - (1 if x >= 36 else 0)
            if abs(y - road_y) <= 1:
                tile = "w"
            elif border <= 2 and (x * 3 + y * 2) % 5 < 3:
                tile = "F"
            elif (y <= 7 and 5 <= x <= 15) or (y >= 23 and 27 <= x <= 39):
                tile = "F" if (x + y) % 4 else "m"
            elif (y <= 5 and x >= 31) or (y >= 25 and x <= 10):
                tile = "m" if (x * 2 + y) % 3 else "F"
            elif (x + y * 2) % 7 < 2:
                tile = "g"
            else:
                tile = "f"
            row.append(tile)
        rows.append("".join(row))
    return rows


def main():
    rows = terrain_rows()
    deployments = [
        {"name": "SongZhaoGong49", "force": 3, "position": [9, 14]},
        {"name": "DangYiZhu49", "force": 3, "position": [11, 14]},
        {"name": "HuaOu49", "force": 1, "position": [36, 13]},
    ]
    source_name = "chapter49-mengzhu-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = prior.cover_resize(source, (WIDTH * CELL, HEIGHT * CELL))
    image = prior.natural_overlay(image, rows)

    map_path = ROOT / "assets/lzc/map/m077.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)

    manifest = {
        "map": "assets/lzc/map/m077.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": "output/imagegen/m077_prompt.txt",
        "grid": [WIDTH, HEIGHT],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {
            "version": 2,
            "blendable": ["f", "g", "F", "w", "m"],
            "structure_mixing": False,
        },
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth terrain",
        "structure_regions": {},
        "camp_icon_cells": [],
        "camp_cells": [],
        "fence_cells": [],
        "fence_geometry": "no fences in this battlefield",
        "wall_cells": [],
        "gates": [],
        "castle_cells": [],
        "supply_sites": [],
        "blocked_edges": [],
        "deployments": deployments,
        "mission": {
            "type": "mengzhu_pursuit",
            "pursuit_direction": "east_to_west",
            "first_target": "DangYiZhu49",
            "protected_target": "SongZhaoGong49",
            "protection_release": "DangYiZhu49 defeated",
            "named_outcomes": {
                "DangYiZhu49": "historical_death",
                "SongZhaoGong49": "historical_death",
                "HuaOu49": "must_survive_battle",
            },
        },
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m077_ch49_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    review_path = ROOT / "output/terrain_model/m077_ch49_review.png"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    common.review_image(
        image,
        rows,
        {"walls": set(), "fences": set(), "gates": set(), "sites": set()},
        deployments,
        review_path,
    )
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (WIDTH * CELL, HEIGHT * CELL)
    assert max(stat.var) > 100
    print(f"m077: {WIDTH}x{HEIGHT}, pixels={image.size}, variance={[round(v, 2) for v in stat.var]}")


if __name__ == "__main__":
    main()
