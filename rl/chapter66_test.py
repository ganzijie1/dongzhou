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


def terrain_rows(stage_text: str) -> list[str]:
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage_text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))


def reachable(matrix: list[str], start: tuple[int, int], goals: set[tuple[int, int]]) -> bool:
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            px, py = point
            if (
                point not in seen
                and 0 <= py < len(matrix)
                and 0 <= px < len(matrix[0])
                and matrix[py][px] not in BLOCKED
            ):
                seen.add(point)
                queue.append(point)
    return False


def contract(map_id: str, suffix: str, stage_id: str, grid: list[int]) -> dict:
    stage_path = ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua"
    manifest_path = ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json"
    stage = stage_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = terrain_rows(stage)

    assert manifest["grid"] == grid
    assert rows == manifest["terrain_rows"]
    assert Image.open(ROOT / manifest["map"]).size == (grid[0] * 48, grid[1] * 48)
    assert {(x, y) for y, row in enumerate(rows) for x, code in enumerate(row) if code == "W"} == {
        tuple(point) for point in manifest.get("wall_cells", [])
    }
    assert {(x, y) for y, row in enumerate(rows) for x, code in enumerate(row) if code == "P"} == {
        tuple(point) for point in manifest.get("fence_cells", [])
    }
    for unit in manifest["deployments"]:
        x, y = unit["position"]
        assert rows[y][x] not in BLOCKED, unit
    return manifest


def main() -> None:
    yu = contract("m111", "ch66a", "66a", [56, 40])
    ning = contract("m112", "ch66b", "66b", [50, 38])
    cui = contract("m108", "ch66c", "66c", [50, 38])
    shuju = contract("m113", "ch66d", "66d", [68, 46])
    jize = contract("m114", "ch66e", "66e", [60, 42])

    assert reachable(yu["terrain_rows"], (44, 20), {(41, 19), (41, 20)})
    assert reachable(ning["terrain_rows"], (25, 35), {(24, 32), (25, 32)})
    assert reachable(cui["terrain_rows"], (24, 31), {(24, 17), (25, 17)})
    assert reachable(shuju["terrain_rows"], (21, 21), {(47, 22), (47, 23)})
    assert reachable(jize["terrain_rows"], (13, 22), {(42, 20)})

    gate_cells = {tuple(p) for gate in shuju["gates"] for p in gate["cells"]}
    assert gate_cells.isdisjoint(
        {tuple(p) for p in shuju["fence_cells"]}
    )
    assert {tuple(p) for p in shuju["camp_cells"]} == {(56, 16), (57, 29)}

    texts = {
        sid: (ROOT / f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8")
        for sid in ("66a", "66b", "66c", "66d", "66e")
    }
    checks = {
        "66a": ("圉村伏殖绰", 'game:is_unit_within("ZhiChuo62",{41,19},1)'),
        "66b": ("宁府诛喜", 'not game:has_unit("NingXi65")'),
        "66c": ("崔氏覆灭", 'not game:has_unit("CuiJiang65")'),
        "66d": ("舒鸠之战", 'set_unit_invulnerable("ShuJiuLord66",false)'),
        "66e": ("棘泽擒将", 'not game:has_unit("HuangJie66")'),
    }
    for sid, (title, mechanic) in checks.items():
        assert f'battle_title="{title}"' in texts[sid]
        assert mechanic in texts[sid]
        assert 'speaker="旁白"' not in texts[sid]
        assert texts[sid].count("speaker=") >= 8

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    start = CURRENT_DONGZHOU_STAGES.index("65a")
    assert CURRENT_DONGZHOU_STAGES[start:start + 8] == ("65a", "65b", "65c", "66a", "66b", "66c", "66d", "66e")
    assert STAGE_TABLE_VERSION >= 10
    assert '"66e", "67a"' in config
    for hero in (
        "GongSunMianYu66",
        "LuPuBie66",
        "QuJian66",
        "ZiJiang66",
        "XiHuan66",
        "QuHuYong66",
        "ShuJiuLord66",
        "ChuanFengShu66",
        "GongZiWei66",
        "HuangJie66",
    ):
        assert config.count(f'id = "{hero}"') == 1
        assert f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for sid, asset in (
            ("66a", "m111.png"),
            ("66b", "m112.png"),
            ("66c", "m108.png"),
            ("66d", "m113.png"),
            ("66e", "m114.png"),
        ):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid))
            assert env.story_info()["map_asset"] == asset
            assert not any(
                unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}
                for unit in env.unit_info()
                if not unit["dead"]
            )

    print("chapter 66 ok: five battles, terrain contracts, phases, heroes, and save table")


if __name__ == "__main__":
    main()
