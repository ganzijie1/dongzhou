from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFilter, ImageStat

import generate_chapter43_maps as common
import generate_chapter47_maps as natural

ROOT = Path(__file__).resolve().parents[1]
CELL = 48
WIDTH, HEIGHT = 64, 44


def perimeter(bounds):
    return common.rectangle_perimeter(*bounds)


def base_rows():
    rows = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            edge = min(x, WIDTH - 1 - x, y, HEIGHT - 1 - y)
            if edge <= 2 and (x + y * 3) % 7 in (0, 1):
                tile = "F"
            elif (x * 2 + y * 3) % 13 in (0, 1, 2):
                tile = "g"
            else:
                tile = "f"
            row.append(tile)
        rows.append(row)
    # The bog that catches Duke Li's chariot is passable wasteland with extra movement cost.
    for y in range(20, 28):
        for x in range(26, 39):
            if ((x - 32) / 7) ** 2 + ((y - 24) / 5) ** 2 <= 1:
                rows[y][x] = "w"
    return rows


def draw_camp_ground(image, bounds):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = bounds
    draw.rounded_rectangle(
        (x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL),
        radius=34, fill=(121, 98, 65, 52)
    )
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(10)))


def draw_bog(image, bog_cells):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x, y in bog_cells:
        draw.ellipse((x * CELL - 8, y * CELL + 7, (x + 1) * CELL + 8, (y + 1) * CELL - 4),
                     fill=(72, 67, 50, 62))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(8)))


def main():
    rows = base_rows()
    jin_bounds = (7, 3, 56, 15)
    chu_bounds = (7, 31, 56, 42)
    jin_gates = {(x, 15) for x in (14, 15, 16, 31, 32, 33, 47, 48, 49)}
    chu_gates = {(x, 31) for x in (14, 15, 16, 31, 32, 33, 47, 48, 49)}
    gates = jin_gates | chu_gates
    fences = (perimeter(jin_bounds) - jin_gates) | (perimeter(chu_bounds) - chu_gates)
    camps = {(20, 9), (32, 9), (44, 9), (20, 36), (32, 36), (44, 36)}
    bog = {(x, y) for y, row in enumerate(rows) for x, tile in enumerate(row) if tile == "w"}
    for x, y in fences:
        rows[y][x] = "P"
    for x, y in camps:
        rows[y][x] = "e"

    deployments = [
        {"name":"JinLiGong58","force":1,"position":[32,9]},
        {"name":"LuanShu58","force":1,"position":[29,10]},
        {"name":"ShiXie58","force":1,"position":[35,10]},
        {"name":"HanJue48","force":1,"position":[45,11]},
        {"name":"WeiQi54","force":1,"position":[21,11]},
        {"name":"LuanZhen58","force":1,"position":[39,12]},
        {"name":"XiZhi58","force":1,"position":[18,12]},
        {"name":"XiQi58","force":1,"position":[15,10]},
        {"name":"XunYan58","force":1,"position":[48,10]},
        {"name":"ChuGongWang58","force":3,"position":[32,36]},
        {"name":"GongZiCe51","force":3,"position":[29,37]},
        {"name":"GongZiYingQi51","force":3,"position":[18,36]},
        {"name":"GongZiRenFu58","force":3,"position":[46,36]},
        {"name":"XiongFa58","force":3,"position":[32,29]},
        {"name":"YangYouJi51","force":3,"position":[36,34]},
        {"name":"PanDang58","force":3,"position":[42,34]},
        {"name":"GongYinXiang58","force":3,"position":[24,34]},
    ]

    source_name = "chapter56-an-base-gpt2.png"
    source = Image.open(ROOT / "output/imagegen" / source_name).convert("RGB")
    image = natural.cover_resize(source, (WIDTH * CELL, HEIGHT * CELL))
    image = natural.natural_overlay(image, rows)
    draw_camp_ground(image, jin_bounds)
    draw_camp_ground(image, chu_bounds)
    draw_bog(image, bog)
    common.draw_fences(image, fences & perimeter(jin_bounds), jin_bounds)
    common.draw_fences(image, fences & perimeter(chu_bounds), chu_bounds)
    common.draw_sites(image, camps)

    map_path = ROOT / "assets/lzc/map/m092.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(map_path, "PNG", compress_level=3)
    prompt_path = ROOT / "output/imagegen/m092_prompt.txt"
    prompt_path.write_text(
        "Use case: historical-scene\nAsset type: Mengde tactical battle-map base\n"
        "Primary request: broad Yanling battlefield with northern and southern level camp clearings, open central battle line, and a dark shallow bog.\n"
        "Style: classic Chinese tactical-RPG painted terrain, orthographic, natural transitions.\n"
        "Constraints: no structures, camps, fences, walls, units, text, UI, or visible grid; structures are separate overlays.\n",
        encoding="utf-8"
    )
    manifest = {
        "map":"assets/lzc/map/m092.png",
        "source_base":f"output/imagegen/{source_name}",
        "prompt_file":"output/imagegen/m092_prompt.txt",
        "grid":[WIDTH,HEIGHT], "cell_pixels":CELL,
        "terrain_rows":["".join(row) for row in rows],
        "terrain_protocol":{"version":2,"blendable":["f","g","F","w","m"],"structure_mixing":False},
        "terrain_layers":[],
        "terrain_source":"recomposed GPT Image 2 natural base plus reviewed programmatic Yanling geometry",
        "structure_regions":{"jin_camp":[[7,3],[56,15]],"chu_camp":[[7,31],[56,42]],"central_bog":[[26,20],[38,27]]},
        "camp_icon_cells":[list(c) for c in sorted(camps)],
        "camp_cells":[list(c) for c in sorted(camps)],
        "fence_cells":[list(c) for c in sorted(fences)],
        "fence_geometry":"impassable cell center-axis; corners use two half-axis segments",
        "wall_cells":[],
        "gates":[
            {"name":"jin_west_gate","cells":[[14,15],[15,15],[16,15]]},
            {"name":"jin_center_gate","cells":[[31,15],[32,15],[33,15]]},
            {"name":"jin_east_gate","cells":[[47,15],[48,15],[49,15]]},
            {"name":"chu_west_gate","cells":[[14,31],[15,31],[16,31]]},
            {"name":"chu_center_gate","cells":[[31,31],[32,31],[33,31]]},
            {"name":"chu_east_gate","cells":[[47,31],[48,31],[49,31]]},
        ],
        "castle_cells":[], "supply_sites":[list(c) for c in sorted(camps)], "blocked_edges":[],
        "deployments":deployments,
        "mission":{"type":"battle_of_yanling_phase_one","capture":"XiongFa58","wound":"ChuGongWang58","historical_death":"WeiQi54"},
        "visual_grid_in_game":False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m092_ch58_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review = ROOT / "output/terrain_model/m092_ch58_review.png"
    common.review_image(image, rows, {"walls":set(),"fences":fences,"gates":gates,"sites":camps}, deployments, review)
    prediction = {
        "map":manifest["map"], "grid":manifest["grid"],
        "backend":"reviewed-contract-with-dinov3-evidence-slot", "threshold":0.72,
        "auto_apply":False, "review_required":[],
        "note":"Classifier evidence cannot overwrite reviewed fences, gates, camps, bog, deployments, or Lua terrain."
    }
    (ROOT / "output/terrain_model/m092_ch58_prediction.json").write_text(
        json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    stat = ImageStat.Stat(image.convert("RGB"))
    assert image.size == (WIDTH * CELL, HEIGHT * CELL) and max(stat.var) > 100
    print(f"m092: {WIDTH}x{HEIGHT}, pixels={image.size}, fences={len(fences)}, gates={len(gates)}, camps={len(camps)}")


if __name__ == "__main__":
    main()