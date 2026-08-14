"""Regression checks for the upper-city/lower-field Song capital battle map."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageStat

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 10")
        story = env.story_info()
        assert (story["chapter"], story["battle_title"], story["map_asset"]) == (
            "第八回·上", "宋都兵变", "song-capital-coup.png"
        )
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        terrain = list(map_info["terrain"])
        assert (width, height) == (19, 14)
        assert terrain.count("Flatland") == 117
        assert terrain.count("Mountain") == 36
        assert terrain.count("Camp") == 18
        assert terrain.count("Forest") == 0
        assert terrain.count("Wall") == 36
        assert all(
            terrain[y * width + x] == ("Gate" if x == 9 else "Wall")
            for y in (3, 4) for x in range(width)
        )
        assert all(
            terrain[y * width + x] == (
                "Camp" if y >= 11 and (x < 3 or x > 15)
                else "Mountain" if x < 3 or x > 15
                else "Flatland"
            ) for y in range(5, 14) for x in range(width)
        )

        units = [unit for unit in env.unit_info() if not unit["dead"]]
        assert units and all(
            unit["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"}
            for unit in units
        )
        supplies = {(int(site["x"]), int(site["y"])) for site in env.supply_info()["sites"]}
        assert supplies == {(1, 12), (14, 2), (9, 0), (9, 3), (9, 4), (5, 2)}

    image = Image.open("assets/lzc/map/song-capital-coup.png").convert("RGB")
    assert image.size == (1520, 1120)
    assert all(value > 20 for value in ImageStat.Stat(image).stddev)
    gui_source = Path("rl/play_gui.py").read_text(encoding="utf-8")
    assert '"SongMutineerArcher81": 17' in gui_source
    print("song capital ok: upper city, continuous wall gate, central plain, side mountains, corner camps, supplies, and deployment")


if __name__ == "__main__":
    main()
