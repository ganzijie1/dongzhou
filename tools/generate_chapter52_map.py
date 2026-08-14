from pathlib import Path
import json

from PIL import Image, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural


ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WIDTH = 46
HEIGHT = 30


def build_rows():
    rows = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            border = min(x, WIDTH - 1 - x, y, HEIGHT - 1 - y)
            flank_road = abs(y - (5 + x // 5)) <= 1 and x <= 24
            battle_road = abs(y - (18 - x // 10)) <= 1 and 12 <= x <= 43
            if flank_road or battle_road:
                tile = "w" if (x + y) % 3 else "f"
            elif border <= 1 and (x * 3 + y * 5) % 4 != 0:
                tile = "F"
            elif x <= 12 and 8 <= y <= 24 and (x + y * 2) % 5 < 3:
                tile = "F"
            elif 13 <= x <= 22 and 20 <= y <= 27 and (x * 2 + y) % 4 < 2:
                tile = "F"
            elif 25 <= x <= 31 and 3 <= y <= 9 and (x + y) % 3 == 0:
                tile = "m"
            elif (x * 2 + y * 3) % 11 < 2:
                tile = "g"
            else:
                tile = "f"
            row.append(tile)
        rows.append("".join(row))
    return rows


def main():
    rows = build_rows()
    deployments = [
        {"name": "XiQue45", "force": 1, "position": [6, 5]},
        {"name": "ZhengXiangGong52", "force": 2, "position": [41, 16]},
        {"name": "GongZiQuJi52", "force": 2, "position": [39, 14]},
        {"name": "ChuZhuangWang51", "force": 3, "position": [27, 17]},
    ]
    source_name = "chapter52-liufen-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (WIDTH * CELL, HEIGHT * CELL))
    image = natural.natural_overlay(image, rows)
    map_path = ROOT / "assets/lzc/map/m082.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)

    manifest = {
        "map": "assets/lzc/map/m082.png",
        "source_base": f"output/imagegen/{source_name}",
        "prompt_file": "output/imagegen/m082_prompt.txt",
        "grid": [WIDTH, HEIGHT],
        "cell_pixels": CELL,
        "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [],
        "terrain_source": "GPT Image 2 natural base plus reviewed programmatic source-of-truth natural terrain",
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
            "type": "liufen_relief_flank_attack",
            "surprise_trigger": [20, 11],
            "surprise_radius": 3,
            "historical_survivors": ["ChuZhuangWang51", "ZhengXiangGong52", "GongZiQuJi52"],
        },
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m082_ch52_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review = ROOT / "output/terrain_model/m082_ch52_review.png"
    common.review_image(image, rows, {"walls": set(), "fences": set(), "gates": set(), "sites": set()}, deployments, review)
    prediction = {
        "map": "assets/lzc/map/m082.png",
        "grid": [WIDTH, HEIGHT],
        "backend": "reviewed-natural-contract-with-dinov3-evidence-slot",
        "threshold": 0.72,
        "auto_apply": False,
        "review_required": [],
        "note": "Natural classifier evidence cannot overwrite the reviewed Lua terrain rows.",
    }
    (ROOT / "output/terrain_model/m082_ch52_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (WIDTH * CELL, HEIGHT * CELL) and max(stat.var) > 100
    print(f"m082: {WIDTH}x{HEIGHT}, pixels={image.size}, variance={[round(v, 2) for v in stat.var]}")


if __name__ == "__main__":
    main()
