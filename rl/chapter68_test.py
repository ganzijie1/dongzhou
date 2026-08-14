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


def main() -> None:
    stage = (ROOT / "game/sce/dongzhou/stage/68.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m117_ch68_manifest.json").read_text(encoding="utf-8"))
    rows = stage_rows(stage)
    walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    sites = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "C"}

    assert manifest["grid"] == [72, 44]
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (72 * 48, 44 * 48)
    assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
    assert gates == {(62, 20), (62, 21)} and gates.isdisjoint(walls)
    assert all(rows[y][x] == "G" for x, y in gates)
    assert sites == {(21, 12), (35, 15), (50, 29)}
    assert sites == {tuple(cell) for cell in manifest["castle_cells"]}
    assert sites == {tuple(cell) for cell in manifest["supply_sites"]}
    assert manifest["fence_cells"] == [] and manifest["camp_cells"] == []
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit

    assert reachable(rows, (43, 17), gates)
    assert reachable(rows, (67, 20), gates)
    delayed = {(53, 14), (54, 27), (58, 14), (58, 27), (55, 16), (55, 25)}
    assert all(rows[y][x] not in BLOCKED for x, y in delayed)

    assert 'battle_title="东门逐栾高"' in stage
    assert 'game:set_unit_invulnerable("LuanShi68",true)' in stage
    assert 'game:is_unit_within("ChenWuYu68",{56,20},6)' in stage
    assert 'game:set_unit_invulnerable("LuanShi68",false)' in stage
    assert 'many(game,"QiCitizenGuard68"' in stage
    assert 'not game:has_unit("LuanShi68") and not game:has_unit("GaoQiang68")' in stage
    assert 'speaker="旁白"' not in stage and stage.count("speaker=") >= 24

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-3:] == ("67a", "67b", "68")
    assert STAGE_TABLE_VERSION == 12
    assert '"67a", "67b", "68" }' in config
    for hero in ("ChenWuYu68", "BaoGuo68", "WangHei68", "LuanShi68", "GaoQiang68"):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        env._restart_process(CURRENT_DONGZHOU_STAGES.index("68"))
        assert env.story_info()["map_asset"] == "m117.png"
        assert not any(
            unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}
            for unit in env.unit_info()
            if not unit["dead"]
        )

    print("chapter 68 ok: Linzi east-gate pursuit, ally trigger, map contract, heroes, and save table")


if __name__ == "__main__":
    main()
