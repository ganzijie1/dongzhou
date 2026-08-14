from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re

from PIL import Image

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED = {"r", "W", "~", "P"}


def lua_rows(text: str) -> list[str]:
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))


def reachable(rows: list[str], start: tuple[int, int], goals: set[tuple[int, int]]) -> bool:
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            px, py = point
            if point not in seen and 0 <= py < len(rows) and 0 <= px < len(rows[0]) and rows[py][px] not in BLOCKED:
                seen.add(point)
                queue.append(point)
    return False


def test_contract(map_id: str, suffix: str, expected_grid: list[int]) -> dict:
    stage_id = "59a" if suffix == "ch59a" else "59b"
    stage = (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    rows = manifest["terrain_rows"]
    assert manifest["grid"] == expected_grid
    assert len(rows) == expected_grid[1] and all(len(row) == expected_grid[0] for row in rows)
    assert lua_rows(stage) == rows
    assert Image.open(ROOT / manifest["map"]).size == tuple(value * 48 for value in expected_grid)
    assert manifest["visual_grid_in_game"] is False
    assert manifest["fence_cells"] == [] and manifest["blocked_edges"] == []
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit
    prediction = json.loads((ROOT / f"output/terrain_model/{map_id}_{suffix}_prediction.json").read_text(encoding="utf-8"))
    assert prediction["auto_apply"] is False
    return manifest


def main() -> None:
    taiyin = test_contract("m093", "ch59a", [52, 34])
    manor = test_contract("m094", "ch59b", [48, 32])
    rows = manor["terrain_rows"]
    walls = {tuple(p) for p in manor["wall_cells"]}
    matrix_walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    assert walls == matrix_walls
    gates = {tuple(p) for item in manor["gates"] for p in item["cells"]}
    assert gates == {(24, 27), (25, 27)} and all(rows[y][x] == "G" for x, y in gates)
    assert reachable(rows, (21, 29), gates) and reachable(rows, (30, 16), gates)
    assert manor["supply_sites"] == [[30, 16]]

    stage_a = (ROOT / "game/sce/dongzhou/stage/59a.lua").read_text(encoding="utf-8")
    stage_b = (ROOT / "game/sce/dongzhou/stage/59b.lua").read_text(encoding="utf-8")
    assert 'battle_title="太阴山之变"' in stage_a
    assert 'battle_title="赵氏复仇"' in stage_b
    assert 'set_unit_invulnerable("JinLiGong58",true)' in stage_a
    assert 'not game:has_unit("XuTong59")' in stage_a
    assert 'king_captured then return Enum.status.victory' in stage_a
    assert 'set_unit_invulnerable("TuAnGu50",true)' in stage_b
    assert 'set_unit_invulnerable("TuAnGu50",false)' in stage_b
    assert stage_b.index('is_unit_within("ZhaoWu59"') < stage_b.index('not game:has_unit("TuAnGu50")')
    assert stage_a.count('{speaker=') >= 23 and stage_b.count('{speaker=') >= 23
    for text in (stage_a, stage_b):
        assert 'speaker="旁白"' not in text
        assert "gally_hold_position=true" in text

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-10:] == ("57", "58", "59a", "59b", "60a", "60b", "60c", "61a", "61b", "61c")
    assert CURRENT_DONGZHOU_STAGES.index("58") == 93
    assert STAGE_TABLE_VERSION == 5
    assert '"57", "58", "59a", "59b", "60a", "60b", "60c", "61a", "61b", "61c" }' in config
    for hero in ("XuTong59", "YiYangWu59", "QingFeiTui59", "ChengHua59", "ZhaoWu59", "ChengYing59"):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui
    assert '_LARGE_BATTLE_MAPS["m093.png"] = (52, 34, 48)' in gui
    assert '_LARGE_BATTLE_MAPS["m094.png"] = (48, 32, 48)' in gui

    with MengdeEnv(EXE, scenario="dongzhou", interactive=True) as env:
        env.reset()
        env._request(f"LOAD_STAGE {CURRENT_DONGZHOU_STAGES.index('59a')}")
        assert env.story_info()["map_asset"] == "m093.png"
        assert not any(unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for unit in env.unit_info() if not unit["dead"])
        env._request(f"LOAD_STAGE {CURRENT_DONGZHOU_STAGES.index('59b')}")
        assert env.story_info()["map_asset"] == "m094.png"
        units = [unit for unit in env.unit_info() if not unit["dead"]]
        assert not any(unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for unit in units)
        zhao = next(unit for unit in units if unit["name"] == "ZhaoWu59")
        assert env.movement_path(int(zhao["id"]), 24, 27)
        assert not env.movement_path(int(zhao["id"]), 23, 27)

    print("chapter 59 ok: Taiyin coup, Zhao restoration, two distinct maps, barriers, story, and save table")


if __name__ == "__main__":
    main()
