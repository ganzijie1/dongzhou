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
STAGES = {
    "71": ("m120", "ch71", (52, 38)),
    "72": ("m121", "ch72", (64, 36)),
    "73": ("m122", "ch73", (72, 44)),
    "75": ("m123", "ch75_77", (92, 64)),
    "78": ("m124", "ch78", (58, 42)),
    "79": ("m125", "ch79", (62, 42)),
    "80": ("m126", "ch80", (70, 50)),
}


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
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    first_stage = CURRENT_DONGZHOU_STAGES.index("71")
    assert CURRENT_DONGZHOU_STAGES[first_stage:first_stage + len(STAGES)] == tuple(STAGES)
    assert CURRENT_DONGZHOU_STAGES[first_stage + len(STAGES)] == "81"
    assert STAGE_TABLE_VERSION >= 15
    assert '"71", "72", "73", "75", "78", "79", "80"' in config
    assert "第七十四回" in (ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8")
    assert "第七十五至七十七回" in (ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8")

    for stage_id, (map_id, suffix, size) in STAGES.items():
        stage = (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))
        rows = stage_rows(stage)
        assert "endend" not in stage and "undecidedend" not in stage
        assert manifest["grid"] == list(size)
        assert rows == manifest["terrain_rows"]
        assert Image.open(ROOT / manifest["map"]).size == (size[0] * 48, size[1] * 48)
        expected_map_registration = f'_LARGE_BATTLE_MAPS["{map_id}.png"]={size + (48,)}'.replace(" ", "")
        assert expected_map_registration in gui.replace(" ", "")
        walls = {(x, y) for y, row in enumerate(rows) for x, cell in enumerate(row) if cell == "W"}
        gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
        assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
        assert gates.isdisjoint(walls)
        for unit in manifest["deployments"]:
            x, y = unit["position"]
            assert rows[y][x] not in BLOCKED, unit

    rows72 = stage_rows((ROOT / "game/sce/dongzhou/stage/72.lua").read_text(encoding="utf-8"))
    assert reachable(rows72, (31, 32), (32, 1))
    rows75 = stage_rows((ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8"))
    assert reachable(rows75, (83, 29), (15, 48))
    assert reachable(rows75, (15, 48), (88, 8))

    expected_heroes = ("TianKaiJiang71", "WuYuan72", "JiGuang73", "SunWu75", "LuDingGong78", "GouJian79", "FuChai80")
    for hero in expected_heroes:
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui or f"'{hero}'" in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for stage_id, (map_id, _, _) in STAGES.items():
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(stage_id))
            assert env.story_info()["map_asset"] == f"{map_id}.png"
            active = [unit for unit in env.unit_info() if not unit["dead"]]
            assert active, stage_id
            illegal = [unit for unit in active if unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}]
            assert not illegal, (stage_id, [(unit.get("hero"), unit.get("position"), unit.get("terrain")) for unit in illegal])

    print("chapters 71-80 ok: seven battle maps, merged 74-77 narrative, terrain contracts, saves, and runtime launches")


if __name__ == "__main__":
    main()
