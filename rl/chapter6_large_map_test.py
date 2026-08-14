"""Regression checks for chapter six's native-sized scrolling battlefield."""

from __future__ import annotations

import os
from collections import deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rl.mengde_env import MengdeEnv


IMPASSABLE = {"RockyMountain", "Wall", "Water", "Fence"}


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 7")
        map_info = env.map_info()
        width = int(map_info["width"])
        height = int(map_info["height"])
        terrain = list(map_info["terrain"])
        assert (width, height) == (26, 28)
        assert terrain.count("Water") == 67
        assert all(terrain[y * width + x] != "Camp" for x, y in ((14, 7), (15, 7), (14, 8), (15, 8), (16, 8)))
        assert all(terrain[y * width + x] == "Camp" for x, y in ((19, 6), (20, 6), (19, 7), (20, 7)))

        unit_list = [unit for unit in env.unit_info() if not unit["dead"]]
        units = {unit["name"]: unit for unit in unit_list}
        assert len(unit_list) == 14
        assert all(unit["terrain"] not in IMPASSABLE for unit in unit_list)
        assert all(units[name]["terrain"] == "Camp" for name in (
            "YingKaoShu6", "GongZiLu6", "GaoQuMi6", "LuGongZiHui6"
        ))
        assert {
            (int(units[name]["x"]), int(units[name]["y"]))
            for name in ("YingKaoShu6", "GongZiLu6", "GaoQuMi6", "LuGongZiHui6")
        } == {(19, 6), (20, 6), (19, 7), (20, 7)}
        assert (int(units["GongZiLu6"]["x"]), int(units["GongZiLu6"]["y"])) == (19, 7)
        assert (int(units["LuGongZiHui6"]["x"]), int(units["LuGongZiHui6"]["y"])) == (20, 7)
        assert units["GaoQuMi6"]["class"] == "Infantry"
        assert units["LuGongZiHui6"]["class"] == "Cavalry"
        assert units["GaoCityCommander6"]["terrain"] == "Castle"
        assert int(units["GaoCityCommander6"]["force"]) == 4
        assert units["GaoCityCommander6"]["class"] == "Lord"
        assert (int(units["GaoCityCommander6"]["x"]), int(units["GaoCityCommander6"]["y"])) == (20, 25)
        assert any(unit["name"] == "SongDefender" and (int(unit["x"]), int(unit["y"])) == (20, 22) for unit in unit_list)
        assert any(unit["name"] == "SongDefender" and (int(unit["x"]), int(unit["y"])) == (14, 25) for unit in unit_list)

        # Both painted bridges remain passable while their adjacent river is blocked.
        assert all(terrain[y * width + x] != "Water" for y in range(14, 17) for x in (19, 20))
        assert terrain[16 * width + 18] == "Water"
        assert terrain[16 * width + 21] == "Water"
        assert all(terrain[y * width + x] != "Water" for y in (20, 21) for x in (5, 6))
        assert terrain[20 * width + 4] == "Water"
        assert terrain[20 * width + 7] == "Water"

        # Four northern camps use impassable palisades with open inward entrances.
        assert all(terrain[3 * width + x] == "Fence" for x in (*range(12, 16), *range(22, 26)))
        assert all(terrain[y * width + x] == "Fence" for y in range(4, 7) for x in (12, 25))
        assert all(terrain[y * width + x] == "Fence" for y in range(8, 10) for x in (12, 25))
        assert all(terrain[10 * width + x] == "Fence" for x in (*range(12, 16), *range(22, 26)))
        assert all(terrain[y * width + x] != "Fence" for x, y in ((16, 5), (21, 5), (16, 9), (21, 9)))
        fence_cells = {
            (x, y) for y in range(height) for x in range(width)
            if terrain[y * width + x] == "Fence"
        }
        for unit in unit_list:
            if int(unit["force"]) == 1:
                assert not (set(env.movement_range(int(unit["id"]))) & fence_cells)
        stage_source = Path("game/sce/dongzhou/stage/06.lua").read_text(encoding="utf-8")
        assert stage_source.count("{ from =") == 39
        assert all(terrain[22 * width + x] == ("Gate" if x == 20 else "Wall") for x in range(14, 26))
        assert all(terrain[y * width + 14] == ("Gate" if y == 25 else "Wall") for y in range(22, 28))

        start = (int(units["YingKaoShu6"]["x"]), int(units["YingKaoShu6"]["y"]))
        goal = (20, 22)
        queue = deque([start])
        visited = {start}
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if not (0 <= nx < width and 0 <= ny < height) or (nx, ny) in visited:
                    continue
                if terrain[ny * width + nx] in IMPASSABLE:
                    continue
                visited.add((nx, ny))
                queue.append((nx, ny))
        assert goal in visited

    pygame.init()
    pygame.display.set_mode((1280, 756))
    import rl.play_gui as gui

    source = gui.load_battle_map(Path("assets/lzc"), "m006.jpg")
    assert source.get_size() == (1248, 1344)
    assert gui.BOARD_LIMIT == (1248, 1344)
    fitted = gui.fit_battle_map(source, 26, 28, 48)
    assert fitted.get_size() == source.get_size()
    original_mouse_position = pygame.mouse.get_pos
    try:
        pygame.mouse.get_pos = lambda: (970, 715)
        gui._scroll_large_battle_map()
        assert gui._battle_camera["x"] > 0 and gui._battle_camera["y"] > 0
    finally:
        pygame.mouse.get_pos = original_mouse_position
        pygame.quit()

    print("chapter 6 large map ok: native pixels, scrolling camera, river barriers, bridges, and deployment")


if __name__ == "__main__":
    main()