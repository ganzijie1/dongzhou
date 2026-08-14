from __future__ import annotations

from collections import deque
import json
import re
from pathlib import Path

from PIL import Image

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED = {"r", "W", "~", "P"}


def stage_rows(text: str) -> list[str]:
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


def contract(map_id: str, suffix: str, stage_id: str, grid: list[int]) -> dict:
    stage = (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    rows = stage_rows(stage)
    walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    sites = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "C"}

    assert manifest["grid"] == grid
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (grid[0] * 48, grid[1] * 48)
    assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
    assert sites == {tuple(cell) for cell in manifest["castle_cells"]}
    assert sites == {tuple(cell) for cell in manifest["supply_sites"]}
    assert gates.isdisjoint(walls)
    assert all(rows[y][x] == "G" for x, y in gates)
    assert manifest["fence_cells"] == [] and manifest["camp_cells"] == []
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit
    return manifest


def main() -> None:
    qi = contract("m115", "ch67a", "67a", [68, 44])
    zheng = contract("m116", "ch67b", "67b", [62, 42])
    qi_gate = {(7, 20), (7, 21)}
    zheng_gate = {(30, 18), (31, 18)}

    assert reachable(qi["terrain_rows"], (3, 20), qi_gate)
    assert reachable(qi["terrain_rows"], (32, 14), qi_gate)
    assert reachable(zheng["terrain_rows"], (30, 7), zheng_gate)
    assert reachable(zheng["terrain_rows"], (27, 21), zheng_gate)

    a = (ROOT / "game/sce/dongzhou/stage/67a.lua").read_text(encoding="utf-8")
    b = (ROOT / "game/sce/dongzhou/stage/67b.lua").read_text(encoding="utf-8")
    assert 'battle_title="太庙诛庆"' in a
    assert 'phase==1 and not game:has_unit("QingShe67")' in a
    assert 'game:generate_unit("QingFeng62"' in a
    assert 'not game:has_unit("QingSi67") and not game:has_unit("QingYi67")' in a
    assert 'battle_title="郑门讨伯有"' in b
    assert 'game:set_unit_invulnerable("LiangXiao67",true)' in b
    assert 'not game:has_unit("LiangHouseGuard67") and not game:has_unit("LiangHouseArcher67")' in b
    assert 'game:set_unit_invulnerable("LiangXiao67",false)' in b
    for text in (a, b):
        assert 'speaker="旁白"' not in text
        assert text.count("speaker=") >= 15

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    start = CURRENT_DONGZHOU_STAGES.index("66c")
    assert CURRENT_DONGZHOU_STAGES[start:start + 5] == ("66c", "66d", "66e", "67a", "67b")
    assert CURRENT_DONGZHOU_STAGES[CURRENT_DONGZHOU_STAGES.index("67a"):CURRENT_DONGZHOU_STAGES.index("67a") + 2] == ("67a", "67b")
    assert STAGE_TABLE_VERSION >= 11
    assert '"67b", "68"' in config
    assert config.count('id = "QingFeng62"') == 1
    for hero in (
        "LuPuGui67", "GaoChai67", "LuanZao67", "QingShe67", "QingSi67", "QingYi67",
        "GongSunHei67", "SiDai67", "YinDuan67", "LiangXiao67",
    ):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for stage_id, asset in (("67a", "m115.png"), ("67b", "m116.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(stage_id))
            assert env.story_info()["map_asset"] == asset
            assert not any(
                unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}
                for unit in env.unit_info()
                if not unit["dead"]
            )

    print("chapter 67 ok: merged temple/west-gate battle, Boyou rebellion, maps, heroes, and save table")


if __name__ == "__main__":
    main()
