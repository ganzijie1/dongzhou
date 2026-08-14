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
    queue = deque([start]); seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            px, py = point
            if point not in seen and 0 <= py < len(rows) and 0 <= px < len(rows[0]) and rows[py][px] not in BLOCKED:
                seen.add(point); queue.append(point)
    return False


def contract(mid: str, suffix: str, sid: str, grid: list[int]) -> dict:
    stage = (ROOT / f"game/sce/dongzhou/stage/{sid}.lua").read_text(encoding="utf-8")
    data = json.loads((ROOT / f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    assert data["grid"] == grid and lua_rows(stage) == data["terrain_rows"]
    assert Image.open(ROOT / data["map"]).size == (grid[0] * 48, grid[1] * 48)
    for unit in data["deployments"]:
        x, y = unit["position"]
        assert data["terrain_rows"][y][x] not in BLOCKED, unit
    wall_matrix = {(x, y) for y, row in enumerate(data["terrain_rows"]) for x, value in enumerate(row) if value == "W"}
    assert wall_matrix == {tuple(p) for p in data["wall_cells"]}
    return data


def main() -> None:
    qi = contract("m101", "ch62a", "62a", [86, 56])
    gao = contract("m102", "ch62b", "62b", [58, 42])
    manor = contract("m103", "ch62c", "62c", [50, 36])

    assert reachable(qi["terrain_rows"], (12, 25), {(25, 27), (25, 28), (25, 29)})
    assert reachable(qi["terrain_rows"], (12, 25), {(68, 24), (68, 25)})
    assert reachable(gao["terrain_rows"], (51, 7), {(48, 7), (48, 8)})
    assert reachable(gao["terrain_rows"], (23, 38), {(29, 34), (30, 34)})
    assert reachable(manor["terrain_rows"], (24, 32), {(25, 28), (26, 28)})

    a = (ROOT / "game/sce/dongzhou/stage/62a.lua").read_text(encoding="utf-8")
    b = (ROOT / "game/sce/dongzhou/stage/62b.lua").read_text(encoding="utf-8")
    c = (ROOT / "game/sce/dongzhou/stage/62c.lua").read_text(encoding="utf-8")
    assert 'battle_title="十二国伐齐"' in a and 'siege_turn+6' in a and 'set_unit_invulnerable("QiLingGong62",true)' in a
    assert 'battle_title="高唐平叛"' in b and 'northeast_rope_breach' in json.dumps(gao, ensure_ascii=False)
    assert 'battle_title="叔虎府之围"' in c and 'game:get_turn_current()>=3' in c
    for text in (a, b, c):
        assert 'speaker="旁白"' not in text and text.count("{speaker=") >= 14

    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    start = CURRENT_DONGZHOU_STAGES.index("61a")
    assert CURRENT_DONGZHOU_STAGES[start:start + 6] == ("61a", "61b", "61c", "62a", "62b", "62c")
    assert STAGE_TABLE_VERSION >= 6 and '"62a", "62b", "62c", "63a"' in config
    for hero in ("HanQi62", "WeiJiang62", "QiLingGong62", "ZhiChuo62", "QiZhuangGong62", "SuShaWei62", "ShuHu62", "XunWu62"):
        assert config.count(f'id = "{hero}"') == 1 and f'"{hero}"' in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for sid, asset in (("62a", "m101.png"), ("62b", "m102.png"), ("62c", "m103.png")):
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(sid))
            assert env.story_info()["map_asset"] == asset
            assert not any(u["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"} for u in env.unit_info() if not u["dead"])
    print("chapter 62 ok: Qi campaign, Gaotang breach, Shu Hu manor, maps, events, and save table")


if __name__ == "__main__":
    main()
