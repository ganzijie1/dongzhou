"""Regression checks for the reviewed 30x22 Queshan battlefield."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

from rl.mengde_env import MengdeEnv
from rl.save_system import read_slot
from tools.generate_queshan_large_map import (
    CAMPS,
    CAMP_GROUND,
    EAST_CAMP,
    FENCES,
    GATE_CELLS,
    HEIGHT,
    MAP_OUT,
    REVIEWED_TERRAIN_ROWS,
    SITES,
    SOUTH_CAMP,
    WIDTH,
    blocked_edges,
    terrain_layers,
    terrain_rows,
)
from tools.terrain_semantic_model import CHAR_NAMES, parse_stage


EXPECTED_POSITIONS = {
    ("ZhengShiZiHu8", 1): (15, 19),
    ("GaoQuMi8", 1): (14, 19),
    ("ZhuDan8", 1): (16, 19),
    ("GongZiYuan8", 1): (14, 18),
    ("GongSunDaiZhong8", 1): (16, 18),
    ("DaLiang8", 4): (25, 10),
    ("XiaoLiang8", 4): (20, 4),
}
EXPECTED_DUPLICATES = {
    ("BeiRongWarrior8", 4): {(24, 11), (26, 11), (19, 5), (21, 5)},
    ("BeiRongArcher8", 4): {(25, 11), (20, 5)},
}


def unit_positions(units: list[dict]) -> dict[tuple[str, int], set[tuple[int, int]]]:
    positions: dict[tuple[str, int], set[tuple[int, int]]] = {}
    for unit in units:
        key = (str(unit["name"]), int(unit["force"]))
        positions.setdefault(key, set()).add((int(unit["x"]), int(unit["y"])))
    return positions


def main() -> None:
    stage_path = Path("game/sce/dongzhou/stage/08.lua")
    stage = parse_stage(stage_path)
    assert stage is not None
    rows = stage["rows"]
    assert (stage["width"], stage["height"]) == (WIDTH, HEIGHT)
    assert rows == terrain_rows()
    assert all(len(row) == WIDTH for row in rows)
    assert all("W" not in row for row in rows)
    assert stage["asset"] == MAP_OUT
    assert Image.open(MAP_OUT).size == (WIDTH * 48, HEIGHT * 48)

    camps = {
        (x, y)
        for y, row in enumerate(rows)
        for x, terrain in enumerate(row)
        if terrain == "e"
    }
    fences = {
        (x, y)
        for y, row in enumerate(rows)
        for x, terrain in enumerate(row)
        if terrain == "P"
    }
    assert camps == CAMPS == SOUTH_CAMP | EAST_CAMP
    assert len(camps) == 10
    assert all(rows[y][x] == "w" for x, y in CAMP_GROUND)
    assert len(CAMP_GROUND) == 39
    assert fences == FENCES and len(fences) == 44
    assert GATE_CELLS == {(14, 16), (15, 16), (22, 10), (22, 11)}
    assert all(rows[y][x] != "P" for x, y in GATE_CELLS)
    assert SITES == CAMPS

    reviewed_layers = terrain_layers()
    assert reviewed_layers
    structure_cells = FENCES | CAMPS | CAMP_GROUND | GATE_CELLS
    assert not {
        tuple(layer["position"])
        for layer in reviewed_layers
    } & structure_cells

    # Common visual terrain must remain three-class across retraining.
    assert tuple(rows) == REVIEWED_TERRAIN_ROWS
    counts = {terrain: sum(row.count(terrain) for row in rows) for terrain in "fFm"}
    assert counts == {"f": 300, "F": 208, "m": 59}
    assert all(rows[y][x] == "F" for x, y in {(0, 0), (7, 0), (29, 0), (0, 20), (29, 21)})
    assert all(rows[y][x] == "m" for x, y in {(3, 0), (4, 4), (3, 9), (3, 18)})
    assert all(rows[y][x] == "f" for x, y in {(15, 5), (15, 15), (20, 18)})
    prediction = json.loads(
        Path("output/terrain_model/m008_large_v2_prediction.json").read_text(encoding="utf-8")
    )
    assert prediction["rows"] == rows
    assert prediction["common_accuracy"] == 1.0
    assert prediction["common_disagreements"] == []
    assert prediction["terrain_layers"] == reviewed_layers

    stage_text = stage_path.read_text(encoding="utf-8")
    encoded_edges = {
        ((int(ax), int(ay)), (int(bx), int(by)))
        for ax, ay, bx, by in re.findall(
            r"from\s*=\s*\{(\d+),\s*(\d+)\}\s*,\s*"
            r"to\s*=\s*\{(\d+),\s*(\d+)\}",
            stage_text,
        )
    }
    assert blocked_edges() == []
    assert encoded_edges == set()

    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 11")
        map_info = env.map_info()
        assert (int(map_info["width"]), int(map_info["height"])) == (WIDTH, HEIGHT)
        assert env.story_info()["map_asset"] == "m008-large-v2.png"
        terrain = list(map_info["terrain"])
        engine_layers = list(map_info["terrain_layers"])
        assert len(engine_layers) == WIDTH * HEIGHT
        expected_layers = {
            tuple(layer["position"]): layer
            for layer in reviewed_layers
        }
        for index, layer in enumerate(engine_layers):
            point = (index % WIDTH, index // WIDTH)
            if point in expected_layers:
                expected = expected_layers[point]
                assert layer["primary_terrain"] == CHAR_NAMES[expected["primary_terrain"]]
                assert layer["secondary_terrain"] == CHAR_NAMES[expected["secondary_terrain"]]
                assert int(layer["coverage"]) == int(expected["coverage"])
            else:
                assert layer["secondary_terrain"] is None
                assert int(layer["coverage"]) == 0
        assert all(
            engine_layers[y * WIDTH + x]["secondary_terrain"] is None
            and int(engine_layers[y * WIDTH + x]["coverage"]) == 0
            for x, y in structure_cells
        )
        engine_fences = {
            (index % WIDTH, index // WIDTH)
            for index, name in enumerate(terrain)
            if name == "Fence"
        }
        assert engine_fences == FENCES
        supply_positions = {
            (int(site["x"]), int(site["y"]))
            for site in env.supply_info()["sites"]
        }
        assert supply_positions == CAMPS
        assert all(terrain[y * WIDTH + x] == "Camp" for x, y in supply_positions)

        units = [unit for unit in env.unit_info() if not unit["dead"]]
        positions = unit_positions(units)
        for key, expected in EXPECTED_POSITIONS.items():
            assert positions[key] == {expected}, (key, positions[key])
        for key, expected in EXPECTED_DUPLICATES.items():
            assert positions[key] == expected, (key, positions[key])
        assert len(units) == 13
        assert all(unit["terrain"] not in {"Mountain", "Forest", "Fence", "Wall"} for unit in units)
        for unit in units:
            assert env.movement_range(int(unit["id"])).isdisjoint(FENCES), unit["name"]

        by_name = {unit["name"]: unit for unit in units}
        leader = by_name["ZhengShiZiHu8"]
        assert env.movement_path(int(leader["id"]), 15, 16) == [
            (15, 19), (15, 18), (15, 17), (15, 16),
        ]
        gao = by_name["GaoQuMi8"]
        assert env.movement_path(int(gao["id"]), 14, 16) == [
            (14, 19), (14, 18), (14, 17), (14, 16),
        ]

        da_liang = by_name["DaLiang8"]
        assert env.movement_path(int(da_liang["id"]), 22, 10) == [
            (25, 10), (24, 10), (23, 10), (22, 10),
        ]
        assert {(22, 9), (22, 12), (28, 10)}.isdisjoint(
            env.movement_range(int(da_liang["id"]))
        )

        payload = read_slot(1, Path("saves"))
        assert payload is not None and int(payload["battle"]["stage_index"]) == 11
        env.restore(payload["battle"])
        restored = [unit for unit in env.unit_info() if not unit["dead"]]
        restored_positions = unit_positions(restored)
        for key, expected in EXPECTED_POSITIONS.items():
            assert restored_positions[key] == {expected}, (key, restored_positions[key])
        for key, expected in EXPECTED_DUPLICATES.items():
            assert restored_positions[key] == expected, (key, restored_positions[key])
        width = int(env.map_info()["width"])
        restored_terrain = list(env.map_info()["terrain"])
        restored_layers = list(env.map_info()["terrain_layers"])
        assert restored_layers == engine_layers
        assert all(
            restored_terrain[int(unit["y"]) * width + int(unit["x"])]
            not in {"Mountain", "Forest", "Fence", "Wall"}
            for unit in restored
        )

        # Legacy stages without an explicit layer flag remain single-terrain maps.
        env._request("LOAD_STAGE 0")
        legacy_map = env.map_info()
        assert all(
            layer["secondary_terrain"] is None and int(layer["coverage"]) == 0
            for layer in legacy_map["terrain_layers"]
        )

    print(
        f"Queshan terrain ok: {len(reviewed_layers)} natural blends, "
        "structures single-label, slot 1 migrated"
    )


if __name__ == "__main__":
    main()