from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, ImageStat

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, STAGE_TABLE_VERSION
from tools.chapters82_108_data import STAGES, STAGE_IDS, all_new_heroes


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
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    sources = {int(row["ordinal"]): row for row in json.loads(
        (ROOT / "assets/lzc/chapter_sources/dongzhou_82_108.json").read_text(encoding="utf-8")
    )}
    assert CURRENT_DONGZHOU_STAGES[-len(STAGE_IDS):] == tuple(STAGE_IDS)
    assert STAGE_TABLE_VERSION == 17
    assert len(STAGES) == 28 and len({spec["map"] for spec in STAGES}) == 28
    all_stage_text = ""
    map_hashes: set[str] = set()

    for spec in STAGES:
        stage_path = ROOT / f"game/sce/dongzhou/stage/{spec['id']}.lua"
        manifest_path = ROOT / f"assets/lzc/map_sources/{spec['map']}_ch{spec['id']}_manifest.json"
        stage = stage_path.read_text(encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows = stage_rows(stage)
        all_stage_text += stage
        width, height = manifest["grid"]
        assert len(rows) == height and all(len(row) == width for row in rows), spec["id"]
        assert rows == manifest["terrain_rows"]
        map_path = ROOT / manifest["map"]
        image = Image.open(map_path).convert("RGB")
        assert image.size == (width * 48, height * 48)
        assert max(ImageStat.Stat(image).var) > 80
        assert len(image.getcolors(maxcolors=10_000_000) or []) > 100
        map_hashes.add(hashlib.sha256(map_path.read_bytes()).hexdigest())
        if "fortified_city" in manifest["structure_regions"]:
            (x0, y0), (x1, y1) = manifest["structure_regions"]["fortified_city"]
            crop = image.crop((x0 * 48, y0 * 48, (x1 + 1) * 48, (y1 + 1) * 48))
            assert max(ImageStat.Stat(crop).var) > 80, spec["id"]
        walls = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "W"}
        camps = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain == "e"}
        gates = {tuple(cell) for gate in manifest["gates"] for cell in gate["cells"]}
        restorative = {(x, y) for y, row in enumerate(rows) for x, terrain in enumerate(row) if terrain in {"e", "G", "D", "C"}}
        assert walls == {tuple(cell) for cell in manifest["wall_cells"]}
        assert camps == {tuple(cell) for cell in manifest["camp_cells"]} == {tuple(cell) for cell in manifest["camp_icon_cells"]}
        assert gates.isdisjoint(walls) and all(rows[y][x] == "G" for x, y in gates)
        assert restorative == {tuple(cell) for cell in manifest["supply_sites"]}
        assert manifest["fence_cells"] == [] and manifest["blocked_edges"] == []
        assert len(manifest["deployments"]) == len(spec["own"]) + 25
        for unit in manifest["deployments"]:
            x, y = unit["position"]
            assert rows[y][x] not in BLOCKED, (spec["id"], unit)
        mission = manifest["mission"]
        start = tuple(mission["own_positions"][0])
        enemy = tuple(mission["enemy_position"])
        assert reachable(rows, start, enemy), spec["id"]
        assert reachable(rows, enemy, tuple(mission["retreat_exit"])), spec["id"]
        assert f'battle_title="{spec["battle"]}"' in stage
        assert stage.count("{speaker=") >= 18, spec["id"]
        if spec["outcome"] == "retreat":
            assert f'game:set_unit_invulnerable("{spec["enemy"][0]}",true)' in stage
            assert "game:push_cmd_move(enemy_unit" in stage
        else:
            assert f'not game:has_unit("{spec["enemy"][0]}")' in stage

    assert len(map_hashes) == len(STAGES)
    for chapter in range(82, 109):
        title = re.sub(r"^第[^回]+回", "", sources[chapter]["title"])
        assert title in all_stage_text, (chapter, title)
    for hero_id, _, _, _, _, _ in all_new_heroes():
        assert config.count(f'id = "{hero_id}"') == 1, hero_id
        assert f'"{hero_id}"' in gui or f"'{hero_id}'" in gui
    for spec in STAGES:
        manifest = json.loads((ROOT / f"assets/lzc/map_sources/{spec['map']}_ch{spec['id']}_manifest.json").read_text(encoding="utf-8"))
        size = tuple(manifest["grid"] + [48])
        assert f"'{spec['map']}.png': {size}" in gui

    with MengdeEnv(EXE, scenario="dongzhou", max_units=999, interactive=True) as env:
        env.reset()
        for spec in STAGES:
            env._restart_process(CURRENT_DONGZHOU_STAGES.index(spec["id"]))
            assert env.story_info()["map_asset"] == f"{spec['map']}.png"
            active = [unit for unit in env.unit_info() if not unit["dead"]]
            assert len(active) == len(spec["own"]) + 25, (spec["id"], len(active))
            illegal = [unit for unit in active if unit["terrain"] in {"Wall", "RockyMountain", "Water", "Fence"}]
            assert not illegal, (spec["id"], [(unit.get("hero"), unit.get("position"), unit.get("terrain")) for unit in illegal])

    print("chapters 82-108 ok: 28 stages, source-complete narrative, map contracts, outcomes, saves, and runtime launches")


if __name__ == "__main__":
    main()
