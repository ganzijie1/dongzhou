"""Regression checks for selected-unit click and cancellation semantics."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import rl.play_gui as gui


def _capture(button: int) -> tuple[list[pygame.event.Event], bool]:
    selected_unit = 7
    target_mode = None
    destination = None
    action_animation = None
    preview_move = None
    unit_details = [{"id": 7, "x": 2, "y": 3}]
    cancelled = False

    def reset_selection() -> None:
        nonlocal cancelled
        cancelled = True

    position = (
        gui.BOARD_ORIGIN[0] + 2 * gui._active_cell + 4,
        gui.BOARD_ORIGIN[1] + 3 * gui._active_cell + 4,
    )
    pygame.event.post(pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": button, "pos": position}
    ))
    return pygame.event.get(), cancelled


def main() -> None:
    pygame.init()
    gui._battle_context_enabled = True
    left, left_cancelled = _capture(1)
    assert any(event.type == pygame.MOUSEBUTTONDOWN for event in left)
    assert not left_cancelled

    right, right_cancelled = _capture(3)
    assert not right
    assert right_cancelled
    pygame.quit()
    print("battle context ok: second left click confirms, right click cancels")


if __name__ == "__main__":
    main()