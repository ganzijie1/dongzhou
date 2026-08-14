"""Launch LZC and capture one original battle walk without focus interruptions."""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

from mss import mss
from PIL import Image


USER32 = ctypes.windll.user32


def find_window(pid: int, timeout: float = 10.0) -> int:
    found = 0
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def callback(handle: int, _param: int) -> bool:
        nonlocal found
        owner = wintypes.DWORD()
        USER32.GetWindowThreadProcessId(handle, ctypes.byref(owner))
        rect = wintypes.RECT()
        USER32.GetWindowRect(handle, ctypes.byref(rect))
        if (
            owner.value == pid
            and USER32.IsWindowVisible(handle)
            and rect.right - rect.left >= 600
            and rect.bottom - rect.top >= 400
            and USER32.GetWindowTextLengthW(handle) > 0
        ):
            found = handle
            return False
        return True

    callback_fn = callback_type(callback)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        USER32.EnumWindows(callback_fn, 0)
        if found:
            return found
        time.sleep(0.05)
    raise RuntimeError("LZC window did not appear")


def click_client(handle: int, x: int, y: int) -> None:
    point = wintypes.POINT(0, 0)
    USER32.ClientToScreen(handle, ctypes.byref(point))
    USER32.SetCursorPos(point.x + x, point.y + y)
    lparam = (y << 16) | x
    USER32.PostMessageW(handle, 0x0200, 0, lparam)
    USER32.PostMessageW(handle, 0x0201, 1, lparam)
    USER32.PostMessageW(handle, 0x0202, 0, lparam)


def physical_click_client(handle: int, x: int, y: int) -> None:
    point = wintypes.POINT(0, 0)
    USER32.ClientToScreen(handle, ctypes.byref(point))
    USER32.SetCursorPos(point.x + x, point.y + y)
    time.sleep(0.10)
    USER32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.08)
    USER32.mouse_event(0x0004, 0, 0, 0, 0)


def post_click_client(handle: int, x: int, y: int) -> None:
    lparam = (y << 16) | x
    USER32.PostMessageW(handle, 0x0201, 1, lparam)
    time.sleep(0.10)
    USER32.PostMessageW(handle, 0x0202, 0, lparam)


def frame_rect(handle: int) -> dict[str, int]:
    rect = wintypes.RECT()
    if not USER32.GetWindowRect(handle, ctypes.byref(rect)):
        raise RuntimeError("LZC window disappeared")
    return {
        "left": rect.left,
        "top": rect.top,
        "width": rect.right - rect.left,
        "height": rect.bottom - rect.top,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    environment = os.environ.copy()
    environment["__COMPAT_LAYER"] = "WIN7RTM"
    process = subprocess.Popen([str(args.game)], cwd=args.game.parent, env=environment)
    handle = find_window(process.pid)
    USER32.SetForegroundWindow(handle)
    time.sleep(0.8)

    # Existing battle save: second main-menu button.
    post_click_client(handle, 520, 220)
    time.sleep(4.0)

    # Initial battle view: select the red player unit, then move the cursor away.
    click_client(handle, 502, 239)
    USER32.SetCursorPos(960, 540)
    time.sleep(0.5)

    args.output.mkdir(parents=True, exist_ok=True)
    frames: list[tuple[bytes, tuple[int, int]]] = []
    started = time.perf_counter()
    clicked = False
    with mss() as capture:
        while time.perf_counter() - started < 1.5:
            elapsed = time.perf_counter() - started
            if not clicked and elapsed >= 0.20:
                # One tile to the right of the centered selected unit.
                click_client(handle, 359, 239)
                clicked = True
            shot = capture.grab(frame_rect(handle))
            frames.append((bytes(shot.bgra), shot.size))
    for index, (pixels, size) in enumerate(frames):
        Image.frombytes("RGB", size, pixels, "raw", "BGRX").save(
            args.output / f"frame_{index:03d}.png"
        )
    print(f"pid={process.pid} handle={handle} frames={len(frames)}")


if __name__ == "__main__":
    main()
