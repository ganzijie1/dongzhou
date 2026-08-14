from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT, CELL = 64, 42, 32

CAMP_INTERIOR = {(x, y) for y in range(2, 15) for x in range(21, 43)}
CAMP_CELLS = {(26, 5), (32, 5), (38, 5), (26, 11), (32, 11), (38, 11)}
CAMP_GATE = {(30, 15), (31, 15), (32, 15), (33, 15)}
CAMP_FENCES = (
    {(x, 1) for x in range(20, 44)}
    | {(x, 15) for x in range(20, 44)}
    | {(20, y) for y in range(2, 15)}
    | {(43, y) for y in range(2, 15)}
) - CAMP_GATE
CAMP_CORNERS = {
    (20, 1): {"right", "down"}, (43, 1): {"left", "down"},
    (20, 15): {"right", "up"}, (43, 15): {"left", "up"},
}
KONGSANG_GATE = {(9, 32), (10, 32)}
KONGSANG_WALLS = (
    {(x, y) for x in range(5, 16) for y in (32, 40)}
    | {(x, y) for y in range(33, 40) for x in (5, 15)}
) - KONGSANG_GATE
KONGSANG_INTERIOR = {(x, y) for y in range(33, 40) for x in range(6, 15)}
KONGSANG_CASTLES = {(8, 37), (10, 37), (12, 37)}


def terrain_rows():
    rows = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            terrain = "g" if (x + 2 * y) % 5 in (0, 1) else "f"
            if x <= 13 and y <= 11 and x + y <= 19:
                terrain = "m" if x <= 4 and y <= 7 else "F"
            if x <= 10 and y >= 31 and x + (41 - y) <= 14:
                terrain = "m" if x <= 3 else "F"
            if x >= 59 and y >= 26 and x + y >= 93:
                terrain = "~"
            elif x >= 55 and y >= 24 and x + y >= 87:
                terrain = "w"
            if (x, y) in KONGSANG_WALLS:
                terrain = "W"
            elif (x, y) in KONGSANG_CASTLES:
                terrain = "C"
            elif (x, y) in KONGSANG_INTERIOR:
                terrain = "i"
            elif (x, y) in KONGSANG_GATE:
                terrain = "G"
            elif (x, y) in CAMP_FENCES:
                terrain = "P"
            elif (x, y) in CAMP_CELLS:
                terrain = "e"
            row.append(terrain)
        rows.append("".join(row))
    return rows
def deployments():
    own = {
        "ChongEr27": (32, 5), "ZhaoShuai27": (29, 7), "QiMan40": (32, 8),
        "XianZhen27": (35, 7), "HuMao27": (10, 8), "HuYan27": (14, 8),
        "LuanZhi36": (47, 8), "XuChen27": (51, 8),
    }
    allied_named = {
        "XiaoZiYin40": (11, 12), "BaiYiBing30": (14, 12),
        "GuoGuiFu40": (49, 12), "CuiYao32": (52, 12), "GongSunGu33": (28, 12),
    }
    enemy_named = {
        "DouYiShen40": (8, 26), "ShiGui40": (10, 28), "BaiChou40": (14, 28),
        "DouBo33": (50, 26), "YuanXuan40": (46, 28), "GongZiYin40": (54, 28),
        "ChengDeChen33": (32, 30), "ChengDaXin40": (28, 29), "DouYueJiao40": (36, 29),
    }
    left = ([("ChuGuard40#L", (x, 24)) for x in (8, 12, 16, 20, 24, 28)] +
            [("ChuCavalry40#L", (x, 25)) for x in (10, 14, 18, 22, 26)] +
            [("ChuArcher40#L", (x, 26)) for x in (12, 20, 28)])
    right = ([("ChenGuard40#R" if i % 2 == 0 else "CaiGuard40#R", (x, 26))
              for i, x in enumerate((14, 22, 30, 38, 46, 54))] +
             [("ChenCavalry40#R" if i % 2 == 0 else "CaiCavalry40#R", (x, 27))
              for i, x in enumerate((16, 24, 32, 40, 48))] +
             [("ChenArcher40#R", (26, 27)), ("CaiArcher40#R", (42, 27))])
    center = ([("ChuGuard40#C", (x, 24)) for x in (32, 36, 40, 44, 48, 52)] +
              [("ChuCavalry40#C", (x, 25)) for x in (30, 34, 38, 42, 46)] +
              [("ChuArcher40#C", (x, 26)) for x in (36, 44, 52)])
    own_generic = [
        ("JinGuard39#01", (27, 9)), ("JinGuard39#02", (37, 9)),
        ("JinArcher39#01", (24, 11)),
    ]
    allied_generic = [
        ("QinGuard36#01", (10, 14)), ("QinGuard36#02", (12, 14)),
        ("QiGuard30#01", (50, 14)), ("QiGuard30#02", (52, 14)),
        ("SongGuard33#01", (36, 12)), ("SongGuard33#02", (40, 12)),
    ]
    result = [{"name": n, "force": 1, "position": list(p)} for n, p in own.items()]
    result += [{"name": n, "force": 1, "position": list(p)} for n, p in own_generic]
    result += [{"name": n, "force": 2, "position": list(p)} for n, p in allied_named.items()]
    result += [{"name": n, "force": 2, "position": list(p)} for n, p in allied_generic]
    result += [{"name": n, "force": 3, "position": list(p)} for n, p in enemy_named.items()]
    for index, (name, pos) in enumerate(left + right + center, 1):
        result.append({"name": f"{name}{index:02d}", "force": 3, "position": list(pos)})
    return result
def paste_centered(image, sprite, center):
    image.alpha_composite(sprite, (center[0] - sprite.width // 2, center[1] - sprite.height // 2))

def draw_camp(image):
    tinted = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = Image.new("L", image.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((21 * CELL, 2 * CELL, 43 * CELL, 15 * CELL), radius=24, fill=118)
    mask = mask.filter(ImageFilter.GaussianBlur(12))
    tinted.paste((118, 101, 69, 62), (0, 0, image.width, image.height), mask)
    canvas = Image.alpha_composite(image.convert("RGBA"), tinted)

    camp = Image.open(ROOT / "assets/lzc/map_sources/changshao/camp.png").convert("RGBA")
    camp = ImageEnhance.Contrast(camp).enhance(1.08).resize((30, 30), Image.Resampling.LANCZOS)
    for x, y in sorted(CAMP_CELLS):
        paste_centered(canvas, camp, (x * CELL + CELL // 2, y * CELL + CELL // 2))

    horizontal = Image.open(ROOT / "assets/lzc/terrain/fence-queshan-horizontal.png").convert("RGBA")
    vertical = Image.open(ROOT / "assets/lzc/terrain/fence-queshan-vertical.png").convert("RGBA")
    horizontal = horizontal.resize((CELL, 12), Image.Resampling.LANCZOS)
    vertical = vertical.resize((12, CELL), Image.Resampling.LANCZOS)
    for x, y in sorted(CAMP_FENCES):
        center = (x * CELL + CELL // 2, y * CELL + CELL // 2)
        directions = CAMP_CORNERS.get((x, y))
        if directions is None:
            paste_centered(canvas, horizontal if y in (1, 11) else vertical, center)
            continue
        corner = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        htop = (CELL - horizontal.height) // 2
        vleft = (CELL - vertical.width) // 2
        if "left" in directions:
            corner.alpha_composite(horizontal.crop((0, 0, CELL // 2 + 1, horizontal.height)), (0, htop))
        if "right" in directions:
            corner.alpha_composite(horizontal.crop((CELL // 2 - 1, 0, CELL, horizontal.height)), (CELL // 2 - 1, htop))
        if "up" in directions:
            corner.alpha_composite(vertical.crop((0, 0, vertical.width, CELL // 2 + 1)), (vleft, 0))
        if "down" in directions:
            corner.alpha_composite(vertical.crop((0, CELL // 2 - 1, vertical.width, CELL)), (vleft, CELL // 2 - 1))
        paste_centered(canvas, corner, center)
    return canvas.convert("RGB")


def draw_kongsang_city(image):
    canvas = image.convert("RGBA")
    tint = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(tint)
    draw.rectangle((5 * CELL, 32 * CELL, 16 * CELL, 41 * CELL), fill=(92, 82, 68, 90))
    canvas = Image.alpha_composite(canvas, tint)

    wall_source = Image.open(ROOT / "assets/lzc/map_sources/haojing/wall-strip.png").convert("RGBA")
    horizontal = wall_source.crop((0, 0, 48, 48)).resize((CELL, CELL), Image.Resampling.LANCZOS)
    vertical = horizontal.rotate(90, expand=False)
    for x, y in sorted(KONGSANG_WALLS):
        sprite = horizontal if y in (32, 40) else vertical
        paste_centered(canvas, sprite, (x * CELL + CELL // 2, y * CELL + CELL // 2))

    building_files = ["building-25.png", "building-37.png", "building-47.png"]
    for (x, y), filename in zip(sorted(KONGSANG_CASTLES), building_files):
        building = Image.open(ROOT / "assets/lzc/map_sources/haojing" / filename).convert("RGBA")
        building = building.resize((CELL + 8, CELL + 8), Image.Resampling.LANCZOS)
        paste_centered(canvas, building, (x * CELL + CELL // 2, y * CELL + CELL // 2))
    return canvas.convert("RGB")


def main():
    rows = terrain_rows()
    source = Image.open(ROOT / "output/imagegen/chapter40-chengpu-base-gpt2.png").convert("RGB")
    image = source.resize((WIDTH * CELL, HEIGHT * CELL), Image.Resampling.LANCZOS)
    image = draw_camp(image)
    image = draw_kongsang_city(image)
    map_path = ROOT / "assets/lzc/map/m064.png"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(map_path, "PNG", compress_level=3)
    manifest = {
        "map": "assets/lzc/map/m064.png",
        "source_base": "output/imagegen/chapter40-chengpu-base-gpt2.png",
        "prompt_file": "output/imagegen/m064_prompt.txt",
        "grid": [WIDTH, HEIGHT], "cell_pixels": CELL, "terrain_rows": rows,
        "terrain_protocol": {"version": 2, "blendable": ["f", "g", "F", "w", "m"], "structure_mixing": False},
        "terrain_layers": [], "terrain_source": "manually reviewed natural terrain plus programmatic camp structures",
        "structure_regions": {"jin_main_camp": [[20, 1], [43, 15]], "kongsang_city": [[5, 32], [15, 40]]},
        "camp_icon_cells": [list(cell) for cell in sorted(CAMP_CELLS)],
        "camp_cells": [list(cell) for cell in sorted(CAMP_CELLS)],
        "fence_cells": [list(cell) for cell in sorted(CAMP_FENCES)],
        "fence_geometry": "impassable cell center-axis; corners use two half-axis segments",
        "wall_cells": [list(cell) for cell in sorted(KONGSANG_WALLS)],
        "gates": [{"name": "jin_south_gate", "cells": [list(cell) for cell in sorted(CAMP_GATE)]}, {"name": "kongsang_north_gate", "cells": [list(cell) for cell in sorted(KONGSANG_GATE)]}],
        "castle_cells": [list(cell) for cell in sorted(KONGSANG_CASTLES)],
        "supply_sites": [list(cell) for cell in sorted(CAMP_CELLS | KONGSANG_CASTLES)],
        "blocked_edges": [],
        "delayed_deployments": [
            {"trigger": "all_non_kongsang_enemies_defeated", "heroes": ["ChengDeChen33", "ChengDaXin40", "DouYueJiao40", "DouYiShen40", "DouBo33"], "destination_region": "kongsang_city"},
            {"trigger": "ChengDeChen33_within_3_of_10_35", "hero": "WeiChou27", "position": [17, 34], "force": 1},
        ],
        "phase_rules": {
            "battle_title": "城濮之战",
            "initial_enemy_direction": "north",
            "protected_at_kongsang": ["ChengDeChen33"],
            "wei_chou_defeat": "stage_defeat",
            "ceasefire_after_turns": 5,
        },
        "deployments": deployments(),
        "visual_grid_in_game": False,
    }
    manifest_path = ROOT / "assets/lzc/map_sources/m064_ch40_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(WIDTH + 1):
        draw.line((x * CELL, 0, x * CELL, HEIGHT * CELL), fill=(255, 255, 255, 100), width=1)
    for y in range(HEIGHT + 1):
        draw.line((0, y * CELL, WIDTH * CELL, y * CELL), fill=(255, 255, 255, 100), width=1)
    for y, row in enumerate(rows):
        for x, terrain in enumerate(row):
            draw.text((x * CELL + 3, y * CELL + 2), f"{x},{y} {terrain}", fill=(255, 245, 180, 240))
    for x, y in CAMP_FENCES:
        draw.rectangle((x * CELL + 2, y * CELL + 2, (x + 1) * CELL - 3, (y + 1) * CELL - 3), outline=(255, 55, 55, 255), width=4)
    for x, y in CAMP_GATE:
        draw.rectangle((x * CELL + 2, y * CELL + 2, (x + 1) * CELL - 3, (y + 1) * CELL - 3), outline=(55, 255, 105, 255), width=4)
    for x, y in CAMP_CELLS:
        draw.rectangle((x * CELL + 5, y * CELL + 5, (x + 1) * CELL - 6, (y + 1) * CELL - 6), outline=(255, 220, 55, 255), width=3)
    for item in deployments():
        x, y = item["position"]
        color = (255, 80, 80, 255) if item["force"] == 3 else (70, 220, 255, 255)
        draw.ellipse((x * CELL + 18, y * CELL + 18, x * CELL + 46, y * CELL + 46), outline=color, width=3)
    review_path = ROOT / "output/terrain_model/m064_ch40_review.png"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image.convert("RGBA"), overlay).save(review_path)
    print("\n".join(rows))

if __name__ == "__main__":
    main()
