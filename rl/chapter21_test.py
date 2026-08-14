"""Regression checks for chapter twenty-one's three battles."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.save_system import CURRENT_DONGZHOU_STAGES, read_slot


EXPECTED = (
    ("第二十一回·一", "伏龙山破伏", "m034.png"),
    ("第二十一回·二", "卑耳溪争渡", "m035.png"),
    ("第二十一回·三", "无棣夜破", "m036.png"),
)
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 34")
        for offset, (chapter, battle, asset) in enumerate(EXPECTED):
            if offset:
                assert env.next_stage() is not None
            story = env.story_info()
            assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
                chapter, battle, asset
            )
            assert len(story["intro"]) >= 14
            assert len(story["victory"]) >= 10

            map_info = env.map_info()
            width = int(map_info["width"])
            terrain = list(map_info["terrain"])
            assert (width, len(terrain) // width) == (19, 14)
            units = [unit for unit in env.unit_info() if not unit["dead"]]
            assert units
            assert all(unit["terrain"] not in IMPASSABLE for unit in units)

            if offset == 0:
                names = {unit["name"] for unit in units}
                assert "MiLu21" not in names
                assert {"SuMai21", "ShanRongArcher21"} <= names
            elif offset == 1:
                for y in (5, 6):
                    assert all(
                        terrain[y * width + x] != "Water" for x in (4, 5, 14, 15)
                    )
                    assert terrain[y * width + 9] == "Water"
            else:
                assert all(
                    terrain[1 * width + x] == ("Gate" if x == 9 else "Wall")
                    for x in range(2, 17)
                )
                by_name = {unit["name"]: unit for unit in units}
                assert by_name["DaLiHe21"]["class"] == "Lord"
                assert by_name["WuLvGu21"]["class"] == "Strategist"
                assert by_name["HuangHua21"]["class"] == "Cavalry"

    maps = [Path(f"assets/lzc/map/m{number:03d}.png") for number in range(34, 37)]
    assert len({hashlib.sha256(path.read_bytes()).digest() for path in maps}) == 3
    assert all(path.stat().st_size > 1_000_000 for path in maps)

    save = read_slot(1)
    assert save is not None
    stage_index = int(save["battle"]["stage_index"])
    assert 0 <= stage_index < len(CURRENT_DONGZHOU_STAGES)
    stage_id = save["battle"].get("stage_id")
    if stage_id:
        assert CURRENT_DONGZHOU_STAGES[stage_index] == stage_id
    print("chapter 21 ok: three battles, dense story, distinct maps, terrain, roles, and eleventh-battle save")


if __name__ == "__main__":
    main()