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


def reachable(rows: list[str], start: tuple[int, int], goal: tuple[int, int]) -> bool:
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            px, py = point
            if point not in seen and 0 <= py < len(rows) and 0 <= px < len(rows[0]) and rows[py][px] not in BLOCKED:
                seen.add(point)
                queue.append(point)
    return False


def main() -> None:
    stage_path = ROOT / "game/sce/dongzhou/stage/70.lua"
    manifest_path = ROOT / "assets/lzc/map_sources/m119_ch70_manifest.json"
    stage = stage_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = stage_rows(stage)
    walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    sites = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "C"}

    assert manifest["grid"] == [68, 46]
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (68 * 48, 46 * 48)
    assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
    assert sites == {tuple(cell) for cell in manifest["castle_cells"]}
    assert sites == {tuple(cell) for cell in manifest["supply_sites"]}
    assert gates.isdisjoint(walls)
    assert all(rows[y][x] == "G" for x, y in gates)
    assert manifest["fence_cells"] == [] and manifest["camp_cells"] == []
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit

    assert reachable(rows, (61, 20), (52, 20))
    assert reachable(rows, (52, 20), (24, 10))
    assert reachable(rows, (52, 21), (39, 23))
    assert all(not reachable(rows, (61, 20), wall) for wall in walls)

    assert 'battle_title="郢都兵变"' in stage
    assert 'game:generate_unit("CaiWei69",1,Enum.force.ally,{50,20})' in stage
    assert 'game:set_unit_invulnerable("CaiWei69",true)' in stage
    assert 'not game:has_unit("ChuPalaceGuard70")' in stage
    assert 'not game:has_unit("ChuPalaceArcher70")' in stage
    assert 'game:set_unit_invulnerable(h,false)' in stage
    assert 'game:generate_unit("WeiPi70"' not in stage
    assert 'not game:has_unit("ShiZiLu70")' in stage
    assert 'not game:has_unit("GongZiBa70")' in stage
    assert "乾溪" in stage and "楚灵王" in stage and "自缢" in stage
    assert "平丘" in stage and "四千乘" in stage and "三十万" in stage
    assert "击退楚灵王" not in stage
    assert stage.count("{speaker=") >= 40

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-3:] == ("68", "69", "70")
    assert STAGE_TABLE_VERSION == 14
    assert '"68", "69", "70"' in config
    for hero in (
        "ZiGan70", "ZiXi70", "XiaNie70", "XuWuMou70", "DouChengRan70",
        "WeiPi70", "ShiZiLu70", "GongZiBa70", "ChenCaiGuard70",
        "ChenCaiArcher70", "ChuPalaceGuard70", "ChuPalaceArcher70",
    ):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui
    assert '_LARGE_BATTLE_MAPS["m119.png"]=(68,46,48)' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        env._restart_process(CURRENT_DONGZHOU_STAGES.index("70"))
        assert env.story_info()["map_asset"] == "m119.png"
        active = [unit for unit in env.unit_info() if not unit["dead"]]
        assert len(active) >= 32
        assert not any(unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for unit in active)

    print("chapter 70 ok: Ying coup, historical Qianxi collapse, Pingqiu epilogue, map contract, heroes, and save table")


if __name__ == "__main__":
    main()
