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
    stage = (ROOT / "game/sce/dongzhou/stage/81.lua").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m127_ch81_manifest.json").read_text(encoding="utf-8"))
    rows = stage_rows(stage)
    walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
    gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
    sites = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "C"}

    assert manifest["grid"] == [60, 42]
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (60 * 48, 42 * 48)
    assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
    assert gates == {(38, 10), (38, 11), (38, 30), (38, 31)}
    assert all(rows[y][x] == "G" for x, y in gates)
    assert sites == {(49, 10), (49, 31)}
    assert {tuple(cell) for cell in manifest["supply_sites"]} == sites | gates
    assert manifest["fence_cells"] == manifest["camp_cells"] == []
    assert len(manifest["deployments"]) == 42
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit

    assert reachable(rows, (10, 19), (49, 10))
    assert reachable(rows, (10, 23), (49, 31))
    assert reachable(rows, (49, 31), (1, 38))
    assert all(not reachable(rows, (10, 19), wall) for wall in walls)

    assert 'battle_title="临淄高国之乱"' in stage
    assert 'game:set_unit_invulnerable("GuoXia81",true)' in stage
    assert 'game:push_cmd_move(guoxia_id,{1,38})' in stage
    assert 'not game:has_unit("GaoZhang81")' in stage
    assert 'not game:has_unit("GuoXia81")' not in stage
    assert "西施" in stage and "蒸熟" in stage and "南林处女" in stage and "陈音" in stage
    assert "子贡" in stage and "陈恒" in stage and "晋定公" in stage and "第八十二回" in stage
    assert stage.count("{speaker=") >= 39

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert CURRENT_DONGZHOU_STAGES[-3:] == ("79", "80", "81")
    assert STAGE_TABLE_VERSION == 16
    assert '"79", "80", "81"' in config
    for hero in (
        "ChenQi81", "BaoMu81", "GaoZhang81", "GuoXia81", "QiClanGuard81", "QiClanArcher81",
        "GaoHouseGuard81", "GaoHouseArcher81", "GuoHouseGuard81", "GuoHouseArcher81",
        "GongZiYangSheng81", "XiShi81", "YueNv81", "ChenYin81", "ChenHeng81", "ZiGong81",
    ):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui or f"'{hero}'" in gui
    assert '_LARGE_BATTLE_MAPS["m127.png"]=(60,42,48)' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        env._restart_process(CURRENT_DONGZHOU_STAGES.index("81"))
        assert env.story_info()["map_asset"] == "m127.png"
        active = [unit for unit in env.unit_info() if not unit["dead"]]
        assert len(active) == 42
        assert not any(unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for unit in active)

    print("chapter 81 ok: Linzi coup, historical Guo retreat, full narrative, map contract, heroes, saves, and runtime")


if __name__ == "__main__":
    main()
