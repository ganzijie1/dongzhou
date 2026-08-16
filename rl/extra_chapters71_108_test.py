from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, ImageStat

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION
from tools.extra_chapters71_108_data import STAGES, all_new_heroes


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"
BLOCKED = {"r", "W", "~", "P"}
EXPECTED_SEGMENTS = (
    ("71", "72a", "72", "73", "73b", "74", "75", "76", "77", "78", "78b", "79", "80", "81"),
    ("82", "82b", "83a", "83", "84", "84b", "85", "86", "86b", "87"),
    ("100", "101", "101a", "102a"),
    ("106", "107a", "107", "108a", "108"),
)


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
    assert STAGE_TABLE_VERSION == 18
    for segment in EXPECTED_SEGMENTS:
        start = CURRENT_DONGZHOU_STAGES.index(segment[0])
        assert CURRENT_DONGZHOU_STAGES[start:start + len(segment)] == segment
    assert len(STAGES) == 14 and len({spec["map"] for spec in STAGES}) == 14

    map_hashes: set[str] = set()
    for spec in STAGES:
        stage_path = ROOT / f"game/sce/dongzhou/stage/{spec['id']}.lua"
        manifest_path = ROOT / f"assets/lzc/map_sources/{spec['map']}_ch{spec['id']}_manifest.json"
        stage = stage_path.read_text(encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows = stage_rows(stage)
        width, height = manifest["grid"]
        assert rows == manifest["terrain_rows"]
        assert len(rows) == height and all(len(row) == width for row in rows)
        image_path = ROOT / manifest["map"]
        image = Image.open(image_path).convert("RGB")
        assert image.size == (width * 48, height * 48)
        assert max(ImageStat.Stat(image).var) > 80
        assert len(image.getcolors(maxcolors=10_000_000) or []) > 100
        map_hashes.add(hashlib.sha256(image_path.read_bytes()).hexdigest())
        walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
        gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
        assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
        assert gates.isdisjoint(walls)
        assert {tuple(cell) for cell in manifest["supply_sites"]} == {
            (x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain in {"e", "G", "D", "C"}
        }
        for unit in manifest["deployments"]:
            x, y = unit["position"]
            assert rows[y][x] not in BLOCKED, (spec["id"], unit)
        mission = manifest["mission"]
        assert reachable(rows, tuple(mission["own_positions"][0]), tuple(mission["enemy_position"]))
        assert f'battle_title="{spec["battle"]}"' in stage
        assert spec["focus"] in stage
        assert stage.count("{speaker=") >= 18, spec["id"]
        if spec["outcome"] in {"retreat", "attempt"}:
            assert f'game:set_unit_invulnerable("{spec["enemy"][0]}",true)' in stage
        if spec["outcome"] == "attempt":
            assert f'game:is_unit_within("{spec["own"][0][0]}"' in stage
        elif spec["outcome"] == "retreat":
            assert "game:push_cmd_move(enemy_unit" in stage
        else:
            assert f'not game:has_unit("{spec["enemy"][0]}")' in stage

    assert len(map_hashes) == len(STAGES)
    for hero_id, _, _, _, _, _ in all_new_heroes():
        assert config.count(f'id = "{hero_id}"') == 1
        assert f"'{hero_id}'" in gui
    for spec in STAGES:
        manifest = json.loads((ROOT / f"assets/lzc/map_sources/{spec['map']}_ch{spec['id']}_manifest.json").read_text(encoding="utf-8"))
        assert f"'{spec['map']}.png': {tuple(manifest['grid'] + [48])}" in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for spec in STAGES:
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(spec["id"]))
            assert env.story_info()["map_asset"] == f"{spec['map']}.png"
            active = [unit for unit in env.unit_info() if not unit["dead"]]
            assert len(active) == len(spec["own"]) + 25, (spec["id"], len(active))
            assert not [unit for unit in active if unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}]

    print("supplemental chapters 71-108 ok: 14 split stages, maps, stories, progression, and runtime launches")


if __name__ == "__main__":
    main()
