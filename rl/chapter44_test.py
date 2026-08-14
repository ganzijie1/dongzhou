import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"W", "P", "~"}


def main():
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m067_ch44_manifest.json").read_text(encoding="utf-8"))
    stage = (ROOT / "game/sce/dongzhou/stage/44.lua").read_text(encoding="utf-8")
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")

    width, height = manifest["grid"]
    rows = manifest["terrain_rows"]
    assert (width, height) == (32, 24)
    assert len(rows) == height and all(len(row) == width for row in rows)
    assert manifest["camp_cells"] == manifest["camp_icon_cells"] == []
    assert manifest["fence_cells"] == []
    wall_cells = set(map(tuple, manifest["wall_cells"]))
    gate_cells = set(map(tuple, sum((gate["cells"] for gate in manifest["gates"]), [])))
    assert not wall_cells & gate_cells
    assert all(rows[y][x] == "W" for x, y in wall_cells)
    assert all(rows[y][x] == "G" for x, y in gate_cells)

    occupied = set()
    for unit in manifest["deployments"]:
        pos = tuple(unit["position"])
        assert pos not in occupied
        occupied.add(pos)
        x, y = pos
        assert rows[y][x] not in BLOCKED, (unit["name"], pos, rows[y][x])

    size = re.search(r"size\s*=\s*\{(\d+),\s*(\d+)\}", stage)
    terrain = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", stage, re.S)
    stage_rows = re.findall(r'"([A-Za-z~]+)"', terrain.group(1))
    assert tuple(map(int, size.groups())) == (width, height)
    assert stage_rows == rows
    assert all(name in stage for name in ("孟明视", "西乞术", "白乙丙", "弦高", "叔詹", "郤缺"))
    assert "旁白" not in stage
    assert '"43a", "43b", "44"' in config
    assert config.count('id = "BaoManZi44"') == 1
    assert '_LARGE_BATTLE_MAPS["m067.png"] = (32, 24, 48)' in gui
    assert (ROOT / "assets/lzc/map/m067.png").is_file()
    print("chapter44 validation passed")


if __name__ == "__main__":
    main()
