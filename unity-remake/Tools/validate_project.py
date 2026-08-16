from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unity-remake"
SCRIPT = PROJECT / "Assets/Scripts/DongJiaoBattle.cs"
SOURCE_STAGE = ROOT / "game/sce/dongzhou/stage/01.lua"


def rows_from_csharp(text: str) -> list[str]:
    block = re.search(r"Terrain\s*=\s*\{(.*?)\};", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))


def rows_from_lua(text: str) -> list[str]:
    block = re.search(r"terrain\s*=\s*\{(.*?)\}\s*,\s*file", text, re.S)
    assert block
    return re.findall(r'"([fgFwmrW~cbeGDPihCsv]+)"', block.group(1))


def main() -> None:
    manifest = json.loads((PROJECT / "Packages/manifest.json").read_text(encoding="utf-8"))
    assert "com.unity.test-framework" in manifest["dependencies"]
    script = SCRIPT.read_text(encoding="utf-8")
    rows = rows_from_csharp(script)
    assert rows == rows_from_lua(SOURCE_STAGE.read_text(encoding="utf-8"))
    assert len(rows) == 14 and all(len(row) == 19 for row in rows)
    assert "RuntimeInitializeOnLoadMethod" in script
    for feature in ("BuildReachable", "EnemyTurn", "UseMedicine", "ClaimSupply", "duelTriggered", "DrawStoryModal"):
        assert feature in script
    source_map = ROOT / "assets/lzc/map/m007-camp-v5.png"
    unity_map = PROJECT / "Assets/Resources/EastHunt.png"
    assert hashlib.sha256(source_map.read_bytes()).digest() == hashlib.sha256(unity_map.read_bytes()).digest()
    assert Image.open(unity_map).size == (1536, 1152)
    scene_guid = re.search(r"guid: ([0-9a-f]{32})", (PROJECT / "Assets/Scenes/DongJiao.unity.meta").read_text()).group(1)
    assert scene_guid in (PROJECT / "ProjectSettings/EditorBuildSettings.asset").read_text()
    print("unity remake contract ok: source terrain, map, scene, gameplay systems, tests, and build settings")


if __name__ == "__main__":
    main()
