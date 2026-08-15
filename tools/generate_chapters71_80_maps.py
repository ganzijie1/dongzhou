from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import generate_chapter43_maps as structures
import generate_chapter60_maps as common


ROOT = Path(__file__).resolve().parents[1]
CELL = 48


def fill(rows, bounds, terrain):
    x0, y0, x1, y1 = bounds
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            rows[y][x] = terrain


def tint(image, bounds, color):
    x0, y0, x1, y1 = bounds
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle((x0 * CELL, y0 * CELL, (x1 + 1) * CELL, (y1 + 1) * CELL), fill=color)
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(7)))


def finish(map_id, suffix, source, rows, walls, gates, sites, deployments, regions, mission, prompt, wall_bounds=None):
    image = common.base_image(source, len(rows[0]), len(rows), rows)
    if any(cell == "i" for row in rows for cell in row):
        image = tint(image, (0, 0, len(rows[0]) - 1, len(rows) - 1), (118, 101, 77, 28))
    if walls:
        structures.draw_walls(image, walls, wall_bounds or (0, 0, len(rows[0]) - 1, len(rows) - 1))
    if sites:
        structures.draw_castles(image, sites)
    common.save_map(map_id, suffix, image, rows, source, prompt, walls, gates, sites, deployments, regions, mission)


def build_pusui():
    width, height = 52, 38
    rows = common.natural_rows(width, height)
    for y in range(height):
        for x in range(width):
            if abs(y - (8 + x // 3)) <= 1:
                rows[y][x] = "v"
    bounds = (33, 7, 48, 24)
    gates = {(33, 15), (33, 16)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(43, 14)}
    fill(rows, (34, 8, 47, 23), "i")
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "TianKaiJiang71", "force": 1, "position": [7, 29]},
        {"name": "GuYeZi71", "force": 1, "position": [10, 31]},
        {"name": "YingShuang71", "force": 3, "position": [28, 17]},
        {"name": "XuJun71", "force": 3, "position": [43, 14]},
    ]
    finish("m120", "ch71", "chapter46-pengya-base-gpt2.png", rows, walls, gates, sites, deployments,
           {"pusui_frontier": [[0, 0], [32, 37]], "xu_fort": [[33, 7], [48, 24]], "river": [[0, 7], [51, 27]]},
           {"type": "pusui_campaign", "gate_name": "xu_west_gate", "historical_duel": ["TianKaiJiang71", "YingShuang71"]},
           "Use case: historical-scene\nAsset type: broad Pusui frontier battle map\nPrimary request: winding shallow river, open cavalry ground, and a continuous-walled Xu fort.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n", bounds)


def build_zhaoguan():
    width, height = 64, 36
    rows = [["m" if x < 18 or x > 47 else "f" for x in range(width)] for _ in range(height)]
    for y in range(height):
        center = 17 + (y // 7) % 3
        for x in range(center, center + 30):
            rows[y][x] = "g" if (x + y) % 5 else "f"
    wall_y = 15
    gates = {(31, wall_y), (32, wall_y)}
    walls = {(x, wall_y) for x in range(18, 48)} - gates
    sites = {(44, 8)}
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    for y in range(25, 29):
        for x in range(18, 48): rows[y][x] = "v"
    deployments = [
        {"name": "WuYuan72", "force": 1, "position": [31, 32]},
        {"name": "GongZiSheng72", "force": 1, "position": [34, 32]},
        {"name": "HuangFuNe72", "force": 2, "position": [25, 20]},
        {"name": "ZhaoGuanCaptain72", "force": 3, "position": [31, 13]},
    ]
    finish("m121", "ch72", "chapter47-linghu-night-base-gpt2.png", rows, walls, gates, sites, deployments,
           {"south_approach": [[18, 16], [47, 35]], "zhao_pass": [[18, 15], [47, 15]], "north_escape": [[18, 0], [47, 14]]},
           {"type": "zhaoguan_escape", "gate_name": "zhao_pass_two_cell_gate", "escape_cell": [32, 1]},
           "Use case: historical-scene\nAsset type: long Zhaoguan escape map\nPrimary request: narrow mountain corridor, continuous pass wall, two-cell gate, river ford and northern escape road.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n")


def build_jifu():
    width, height = 72, 44
    rows = common.natural_rows(width, height)
    for y in range(7, 38):
        center = 35 + (y - 22) // 5
        for x in range(center - 3, center + 4): rows[y][x] = "v"
    for x in range(width):
        if x % 6 < 2:
            rows[9][x] = "w"
            rows[34][x] = "w"
    sites = {(12, 11), (58, 11), (14, 33), (57, 33)}
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "JiGuang73", "force": 1, "position": [8, 21]},
        {"name": "GongZiGai73", "force": 1, "position": [10, 24]},
        {"name": "XiaNie73", "force": 3, "position": [48, 13]},
        {"name": "WeiYue73", "force": 3, "position": [57, 31]},
        {"name": "HuGong73", "force": 3, "position": [58, 11]},
        {"name": "ShenGong73", "force": 3, "position": [57, 33]},
    ]
    finish("m122", "ch73", "chapter54-river-retreat-base-gpt2.png", rows, set(), set(), sites, deployments,
           {"wu_west": [[0, 9], [28, 35]], "jifu_river": [[31, 7], [40, 37]], "coalition_camps": [[44, 5], [68, 38]]},
           {"type": "jifu_multi_army", "condemned_vanguard": True, "encirclement_targets": ["HuGong73", "ShenGong73"]},
           "Use case: historical-scene\nAsset type: wide Jifu multi-army battlefield\nPrimary request: broken river corridor, four coalition camps, woods and open maneuver lanes.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n")


def build_boju():
    width, height = 92, 64
    rows = common.natural_rows(width, height)
    for y in range(height):
        center = 46 + int(7 * ((y % 18) - 9) / 9)
        for x in range(center - 5, center + 6): rows[y][x] = "~"
        for x in range(center - 7, center + 8):
            if rows[y][x] != "~": rows[y][x] = "v"
    for y in range(18, 23):
        for x in range(34, 59): rows[y][x] = "v"
    for x in range(10, 30):
        for y in range(6, 16): rows[y][x] = "m" if (x + y) % 3 else "r"
    bounds = (4, 39, 27, 59)
    gates = {(27, 48), (27, 49)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(15, 48), (70, 12), (74, 50)}
    fill(rows, (5, 40, 26, 58), "i")
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "WuHelu79", "force": 1, "position": [83, 29]},
        {"name": "WuYuan72", "force": 1, "position": [82, 33]},
        {"name": "SunWu75", "force": 1, "position": [86, 31]},
        {"name": "FuGai75", "force": 1, "position": [80, 36]},
        {"name": "NangWa75", "force": 3, "position": [60, 30]},
        {"name": "ShenYinShu75", "force": 3, "position": [56, 37]},
        {"name": "TangHou75", "force": 3, "position": [70, 12]},
    ]
    finish("m123", "ch75_77", "chapter40-chengpu-base-gpt2.png", rows, walls, gates, sites, deployments,
           {"xiaobie_dabie": [[8, 5], [31, 18]], "han_river": [[36, 0], [60, 63]], "boju": [[53, 20], [82, 43]], "ying_city": [[4, 39], [27, 59]], "junxiang": [[65, 45], [87, 59]]},
           {"type": "boju_merged_campaign", "gate_name": "ying_east_gate", "phases": ["han_river", "xiaobie_dabie", "boju", "ying", "qin_relief_junxiang"]},
           "Use case: historical-scene\nAsset type: enormous merged Boju campaign map\nPrimary request: Han River, Xiao/Dabie mountains, Boju plain, continuous-walled Ying capital and Junxiang relief front.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n", bounds)


def build_lu_rebellion():
    width, height = 58, 42
    rows = common.natural_rows(width, height)
    bounds = (10, 5, 48, 34)
    gates = {(28, 34), (29, 34)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(29, 11), (20, 22), (38, 22)}
    fill(rows, (11, 6, 47, 33), "i")
    for x0, y0, x1, y1 in ((14, 8, 22, 15), (35, 8, 44, 15), (14, 25, 21, 31), (36, 25, 44, 31)): fill(rows, (x0, y0, x1, y1), "h")
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "LuDingGong78", "force": 1, "position": [29, 11]},
        {"name": "JiSunSi78", "force": 1, "position": [22, 17]},
        {"name": "YangHu78", "force": 3, "position": [28, 37]},
        {"name": "YangYue78", "force": 3, "position": [34, 35]},
    ]
    finish("m124", "ch78", "chapter36-jiang-palace-base-gpt2.png", rows, walls, gates, sites, deployments,
           {"lu_capital": [[10, 5], [48, 34]], "south_gate": [[28, 34], [29, 34]], "palace": [[25, 8], [33, 14]]},
           {"type": "lu_rebellion_two_phase", "gate_name": "lu_south_gate", "phases": ["yang_hu", "gongshan_buniu"]},
           "Use case: historical-scene\nAsset type: Lu capital rebellion map\nPrimary request: continuous-walled capital, broad southern gate, palace road and three noble compounds.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n", bounds)


def build_xieli():
    width, height = 62, 42
    rows = common.natural_rows(width, height)
    for y in range(4, 38):
        center = 30 + (y - 20) // 4
        for x in range(center - 4, center + 5): rows[y][x] = "v"
    for y in range(2, 14):
        for x in range(43, 59): rows[y][x] = "w" if (x + y) % 3 else "m"
    sites = {(9, 29), (51, 11)}
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "GouJian79", "force": 1, "position": [9, 29]},
        {"name": "LingGuFu79", "force": 1, "position": [14, 26]},
        {"name": "FanLi79", "force": 1, "position": [11, 33]},
        {"name": "WuHelu79", "force": 3, "position": [51, 11]},
        {"name": "WuZiXu79", "force": 3, "position": [46, 15]},
        {"name": "ZhuanYi79", "force": 3, "position": [42, 18]},
    ]
    finish("m125", "ch79", "chapter54-bi-base-gpt2.png", rows, set(), set(), sites, deployments,
           {"yue_southwest": [[2, 20], [23, 38]], "xieli_river": [[24, 3], [39, 39]], "wu_northeast": [[40, 2], [60, 21]]},
           {"type": "xieli_counterattack", "historical_duel": ["LingGuFu79", "WuHelu79"], "withdrawal": "wu_king_wounded"},
           "Use case: historical-scene\nAsset type: Xieli river battle map\nPrimary request: marshy river bend, Yue southwest camp, wooded Wu approach and open counterattack lanes.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n")


def build_fujiao_huiji():
    width, height = 70, 50
    rows = common.natural_rows(width, height)
    for y in range(height):
        for x in range(25, 38): rows[y][x] = "v" if (x + y) % 5 else "~"
    for y in range(4, 46):
        for x in range(48, 68): rows[y][x] = "m" if (x + y) % 4 else "r"
    bounds = (49, 12, 66, 36)
    gates = {(49, 23), (49, 24)}
    walls = structures.rectangle_perimeter(*bounds) - gates
    sites = {(58, 23), (8, 25)}
    fill(rows, (50, 13, 65, 35), "i")
    for x, y in walls: rows[y][x] = "W"
    for x, y in gates: rows[y][x] = "G"
    for x, y in sites: rows[y][x] = "C"
    deployments = [
        {"name": "GouJian79", "force": 1, "position": [8, 25]},
        {"name": "FanLi79", "force": 1, "position": [10, 28]},
        {"name": "WenZhong79", "force": 1, "position": [10, 22]},
        {"name": "FuChai80", "force": 3, "position": [20, 21]},
        {"name": "WuZiXu79", "force": 3, "position": [18, 27]},
    ]
    finish("m126", "ch80", "chapter38-wen-base-gpt2.png", rows, walls, gates, sites, deployments,
           {"fujiao_plain": [[0, 8], [24, 42]], "lake_crossing": [[25, 0], [38, 49]], "huiji_mountain": [[48, 3], [69, 47]], "huiji_city": [[49, 12], [66, 36]]},
           {"type": "fujiao_huiji_survival", "gate_name": "huiji_west_gate", "escape_cell": [58, 23], "deadline": 12},
           "Use case: historical-scene\nAsset type: merged Fujiao and Huiji retreat map\nPrimary request: western battlefield, broad water crossing, steep Huiji mountains and a continuous-walled mountain city.\nStyle: classic Chinese tactical-RPG painted terrain, no grid or units.\n", bounds)


def main():
    build_pusui(); build_zhaoguan(); build_jifu(); build_boju(); build_lu_rebellion(); build_xieli(); build_fujiao_huiji()
    print("chapters 71-80 maps generated: m120-m126")


if __name__ == "__main__":
    main()
