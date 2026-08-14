import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"W", "P", "~"}


def manifest(name):
    return json.loads((ROOT / "assets/lzc/map_sources" / name).read_text(encoding="utf-8"))


def check_manifest(data):
    width, height = data["grid"]
    rows = data["terrain_rows"]
    assert len(rows) == height
    assert all(len(row) == width for row in rows)
    assert not (set(map(tuple, data["wall_cells"])) & set(map(tuple, sum((g["cells"] for g in data["gates"]), []))))
    assert not (set(map(tuple, data["fence_cells"])) & set(map(tuple, sum((g["cells"] for g in data["gates"]), []))))
    occupied = set()
    for unit in data["deployments"]:
        pos = tuple(unit["position"])
        assert pos not in occupied, pos
        occupied.add(pos)
        x, y = pos
        assert rows[y][x] not in BLOCKED, (unit["name"], pos, rows[y][x])


def stage_rows(stage):
    text = (ROOT / "game/sce/dongzhou/stage" / stage).read_text(encoding="utf-8")
    size_match = re.search(r"size\s*=\s*\{(\d+),\s*(\d+)\}", text)
    terrain_match = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert size_match and terrain_match
    width, height = map(int, size_match.groups())
    rows = re.findall(r'"([A-Za-z~]+)"', terrain_match.group(1))
    assert len(rows) == height, (stage, len(rows), height)
    assert all(len(row) == width for row in rows), (stage, [len(row) for row in rows], width)
    return rows


def main():
    m65 = manifest("m065_ch43a_manifest.json")
    m66 = manifest("m066_ch43b_manifest.json")
    check_manifest(m65)
    check_manifest(m66)
    assert stage_rows("43a.lua") == m65["terrain_rows"]
    assert stage_rows("43b.lua") == m66["terrain_rows"]
    assert all(m65["terrain_rows"][y][x] == "W" for x, y in m65["wall_cells"])
    assert all(m66["terrain_rows"][y][x] == "W" for x, y in m66["wall_cells"])
    assert all(m65["terrain_rows"][y][x] == "P" for x, y in m65["fence_cells"])
    assert all(m66["terrain_rows"][y][x] == "P" for x, y in m66["fence_cells"])
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    assert '"42", "43a", "43b"' in config
    assert config.count('id = "ZhuZhiWu43"') == 1
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    assert '_LARGE_BATTLE_MAPS["m065.png"] = (32, 24, 48)' in gui
    assert '_LARGE_BATTLE_MAPS["m066.png"] = (36, 26, 48)' in gui
    print("chapter43 validation passed")


if __name__ == "__main__":
    main()
