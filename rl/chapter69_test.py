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


def main() -> None:
    stage_path = ROOT / "game/sce/dongzhou/stage/69.lua"
    manifest_path = ROOT / "assets/lzc/map_sources/m118_ch69_manifest.json"
    stage = stage_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = stage_rows(stage)
    walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    sites = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "C"}

    assert manifest["grid"] == [64, 46]
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (64 * 48, 46 * 48)
    assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
    assert sites == {tuple(cell) for cell in manifest["castle_cells"]}
    assert sites == {tuple(cell) for cell in manifest["supply_sites"]}
    assert gates.isdisjoint(walls)
    assert all(rows[y][x] == "G" for x, y in gates)
    assert manifest["fence_cells"] == [] and manifest["camp_cells"] == []
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit

    south_gate = {(31, 37), (32, 37)}
    north_gate = {(31, 3), (32, 3)}
    assert reachable(rows, (31, 42), south_gate)
    assert reachable(rows, (31, 9), south_gate)
    assert reachable(rows, (31, 9), north_gate)
    assert all(not reachable(rows, (31, 42), {wall}) for wall in walls)

    assert 'battle_title="蔡都围城"' in stage
    assert 'game:get_turn_current()' in stage
    assert 'turn>=3' in stage and 'turn>=6' in stage and 'turn>=8' in stage
    assert 'game:set_unit_invulnerable("CaiShiZiYou69",true)' in stage
    assert 'game:set_unit_invulnerable("CaiShiZiYou69",false)' in stage
    assert 'not game:has_unit("CaiGuard69")' in stage
    assert stage.count("{speaker=") >= 35
    assert 'speaker="旁白"' not in stage

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-2:] == ("68", "69")
    assert STAGE_TABLE_VERSION == 13
    assert '"67b", "68", "69"' in config
    for hero in (
        "ChuLingWang69", "WuJu69", "GongZiQiJi69", "CaiLingHou69",
        "CaiShiZiYou69", "GongSunGuiSheng69", "CaiWei69", "ChaoWu69",
        "ChuSiegeGuard69", "ChuSiegeArcher69", "CaiGuard69", "CaiArcher69",
    ):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        env._restart_process(CURRENT_DONGZHOU_STAGES.index("69"))
        assert env.story_info()["map_asset"] == "m118.png"
        active = [unit for unit in env.unit_info() if not unit["dead"]]
        assert len(active) >= 30
        assert not any(unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for unit in active)

    print("chapter 69 ok: merged Chen-Cai campaign, Shangcai siege, story, map contract, heroes, and save table")


if __name__ == "__main__":
    main()
