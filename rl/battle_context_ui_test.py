"""Regression checks for the map-side battle command and inspection UI."""

from __future__ import annotations

import os
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import rl.play_gui as gui


def fonts() -> dict[str, pygame.font.Font]:
    return {
        "heading": pygame.font.SysFont("Microsoft YaHei", 28),
        "title": pygame.font.SysFont("Microsoft YaHei", 22),
        "body": pygame.font.SysFont("Microsoft YaHei", 18),
        "small": pygame.font.SysFont("Microsoft YaHei", 15),
        "tiny": pygame.font.SysFont("Microsoft YaHei", 12),
    }


def detail(unit_id: int, force: int, *, done: bool = False) -> dict:
    return {
        "id": unit_id, "name": "YingKaoShu6" if force == 1 else "SongDefender",
        "class": "Strategist" if force == 1 else "Infantry", "force": force,
        "done": done, "dead": False, "x": 15, "y": 4, "level": 1, "exp": 0,
        "hp": 100, "max_hp": 100, "mp": 20, "max_mp": 20,
        "atk": 80, "def": 72, "int": 86, "dex": 75, "mor": 78,
        "terrain": "Camp", "terrain_effect": 105, "move_cost": 1,
        "skills": ([{"id": "fire_0", "mp": 8, "power": 55, "target_enemy": True}]
                   if force == 1 else []),
    }


def draw_args(screen, font_map, selected, destination, unit_details):
    inventory = {
        "medicine": {"count": 2},
        "spirit_powder": {"count": 1},
    }
    return [
        screen, font_map, None, {"current_force": 1}, [], selected, destination, None,
        pygame.Surface((1248, 1344)), pygame.Surface((1248, 1344), pygame.SRCALPHA), [],
        [pygame.Surface((112, 112)) for _ in range(64)], {}, {}, unit_details,
        None, "AI", [], None, None, None, {}, set(), "Battle", "Objective",
        inventory, [], 0,
    ]


def click(rect: pygame.Rect) -> list[pygame.event.Event]:
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": rect.center}))
    return gui._context_event_get()


def board_click(position, terrain, unit_details, *, button=1):
    selected_unit = None
    target_mode = None
    action_animation = None
    preview_move = None
    destination = None

    def reset_selection():
        return None

    pygame.event.clear()
    pygame.event.post(pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": button, "pos": position}
    ))
    return gui._context_event_get()


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(gui.SCREEN_SIZE)
    font_map = fonts()
    original_draw = gui._original_draw
    original_present = pygame.display.flip
    original_overlay = gui.draw_overlay
    present_calls = []
    pygame.display.flip = lambda: present_calls.append("present")
    gui._original_draw = lambda *args, **kwargs: pygame.display.flip()
    try:
        own = detail(7, 1)
        args = draw_args(screen, font_map, 7, None, [own])
        gui.draw(*args)
        assert present_calls == ["present"]
        assert screen.get_size() == gui.SCREEN_SIZE
        assert tuple(screen.get_at((978, 400))[:3]) == (13, 15, 17)
        assert tuple(screen.get_at((990, 400))[:3]) == (24, 27, 30)
        assert not gui._context_menu_active
        assert gui._context_view_mode is None
        assert gui.BATTLE_SAVE_BUTTON.x >= 984
        assert gui.BATTLE_LOAD_BUTTON.x >= 984
        assert gui._terrain_at_screen_position(["Flatland"] * (26 * 28), (30, 46)) == "Flatland"
        terrain = ["Flatland"] * (19 * 14)
        empty_position = (
            gui.BOARD_ORIGIN[0] + 2 * gui._active_cell + 4,
            gui.BOARD_ORIGIN[1] + 3 * gui._active_cell + 4,
        )
        translated = board_click(empty_position, terrain, [])
        assert len(translated) == 1
        assert gui._context_selected_cell == (2, 3)
        empty_args = draw_args(screen, font_map, None, None, [])
        empty_args[10] = terrain
        gui.draw(*empty_args)
        highlight = (
            gui.BOARD_ORIGIN[0] + 2 * gui._active_cell + 1,
            gui.BOARD_ORIGIN[1] + 3 * gui._active_cell + 1,
        )
        assert tuple(screen.get_at(highlight)[:3]) == tuple(gui.COLORS["accent"])
        assert board_click(empty_position, terrain, [], button=3) == []
        assert gui._context_selected_cell is None
        translated = click(gui.BATTLE_LOAD_BUTTON)
        assert len(translated) == 1 and translated[0].pos == gui.BATTLE_SAVE_BUTTON.center
        assert gui._battle_load_requested is True
        gui._battle_load_requested = False

        cancelled = []
        frame = SimpleNamespace(f_locals={
            "selected_unit": 7, "destination": None, "target_mode": None,
            "action_animation": None, "preview_move": None,
            "unit_details": [own], "reset_selection": lambda: cancelled.append(True),
        })
        selected_position = (
            15 * gui._active_cell + gui.BOARD_ORIGIN[0] + 1,
            4 * gui._active_cell + gui.BOARD_ORIGIN[1] + 1,
        )
        assert gui._click_hits_selected_unit(frame, selected_position)
        assert gui._cancel_selection_from_frame(frame)
        assert cancelled == [True]
        frame.f_locals["target_mode"] = "fire_0"
        assert not gui._click_hits_selected_unit(frame, selected_position)

        args[6] = (15, 4)
        gui.draw(*args)
        assert gui._context_menu_active
        assert all(rect.x >= 20 for rect in (
            gui.STATUS_BUTTON, gui.ITEM_BUTTON, gui.ATTACK_BUTTON, gui.WAIT_BUTTON,
            gui.SKILL_BUTTON,
        ))

        assert click(gui.STATUS_BUTTON) == []
        assert gui._context_view_mode == "status"
        gui.draw(*args)
        assert gui.CONTEXT_CLOSE_BUTTON.x > 0
        assert click(gui.CONTEXT_CLOSE_BUTTON) == []
        assert gui._context_view_mode is None

        assert click(gui.ITEM_BUTTON) == []
        assert gui._context_view_mode == "items"
        gui.draw(*args)
        assert gui.HP_ITEM_BUTTON.x > 0 and gui.MP_ITEM_BUTTON.x > 0
        assert click(gui.ITEM_BACK_BUTTON) == []
        assert gui._context_view_mode is None

        assert click(gui.SKILL_BUTTON) == []
        assert gui._context_view_mode == "skills"
        gui.draw(*args)
        assert gui.SKILL_OPTION_BUTTONS[0].x > 0
        translated = click(gui.SKILL_OPTION_BUTTONS[0])
        assert len(translated) == 1
        assert translated[0].pos == (gui.PANEL_X + 8, 520)
        assert gui._context_view_mode is None

        enemy = detail(9, 4)
        enemy_args = draw_args(screen, font_map, 9, None, [enemy])
        gui.draw(*enemy_args)
        assert gui._context_view_mode == "status"
        assert not gui._context_menu_active

        legacy_overlay_calls = []
        gui.draw_overlay = lambda *args, **kwargs: legacy_overlay_calls.append("legacy")
        gui._original_draw = lambda *args, **kwargs: (gui.draw_overlay(), pygame.display.flip())
        story_args = draw_args(screen, font_map, None, None, [own])
        story_args[18] = {"speaker": "旁白", "text": "完整宽度对话测试"}
        gui.draw(*story_args)
        assert screen.get_size() == gui.SCREEN_SIZE
        assert gui.SCREEN_SIZE == (1280, 756)
        assert gui.STORY_DIALOG_RECT.right == 952
        assert legacy_overlay_calls == []
        assert tuple(screen.get_at(gui.STORY_DIALOG_RECT.topleft)[:3]) == (130, 114, 75)
        assert tuple(screen.get_at((978, 400))[:3]) == (13, 15, 17)
        assert tuple(screen.get_at((990, 400))[:3]) == (24, 27, 30)
    finally:
        gui._original_draw = original_draw
        gui.draw_overlay = original_overlay
        pygame.display.flip = original_present
        pygame.quit()

    print("battle context UI ok: docked story, terrain hover, in-battle load, commands, status, items, skills, and selection cancel")


if __name__ == "__main__":
    main()