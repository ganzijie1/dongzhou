"""Capture a walk from an already-open LZC battle without launching the game."""

from __future__ import annotations

import argparse
import ctypes
import json
import threading
import time
from ctypes import wintypes
from pathlib import Path

from mss import mss
from PIL import Image


USER32 = ctypes.windll.user32
HWND_TOPMOST = -1
SW_RESTORE = 9
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def window_rect(handle: int) -> dict[str, int]:
    rect = wintypes.RECT()
    if not USER32.GetWindowRect(handle, ctypes.byref(rect)):
        raise RuntimeError(f"window {handle} is no longer available")
    return {
        "left": rect.left,
        "top": rect.top,
        "width": rect.right - rect.left,
        "height": rect.bottom - rect.top,
    }


def client_to_screen(handle: int, x: int, y: int) -> wintypes.POINT:
    point = wintypes.POINT(x, y)
    if not USER32.ClientToScreen(handle, ctypes.byref(point)):
        raise RuntimeError("failed to convert client coordinates")
    return point


def click_and_park(handle: int, x: int, y: int) -> tuple[int, int]:
    target = client_to_screen(handle, x, y)
    park = client_to_screen(handle, 300, 20)
    USER32.SetCursorPos(target.x, target.y)
    time.sleep(0.04)
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.025)
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    USER32.SetCursorPos(park.x, park.y)
    return target.x, target.y


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", type=int, required=True)
    parser.add_argument("--x", type=int, required=True)
    parser.add_argument("--y", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=1.5)
    args = parser.parse_args()

    handle = args.handle
    args.output.mkdir(parents=True, exist_ok=True)
    USER32.ShowWindow(handle, SW_RESTORE)
    USER32.SetWindowPos(
        handle,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE,
    )
    USER32.SetForegroundWindow(handle)
    time.sleep(0.15)

    frames: list[tuple[float, bytes, tuple[int, int]]] = []
    started = time.perf_counter()
    click_result: dict[str, float | tuple[int, int]] = {}

    def delayed_click() -> None:
        deadline = started + 0.12
        while time.perf_counter() < deadline:
            time.sleep(0.001)
        click_result["screen"] = click_and_park(handle, args.x, args.y)
        click_result["at"] = time.perf_counter() - started

    click_thread = threading.Thread(target=delayed_click, daemon=True)
    click_thread.start()
    with mss() as capture:
        while True:
            elapsed = time.perf_counter() - started
            shot = capture.grab(window_rect(handle))
            frames.append((time.perf_counter() - started, bytes(shot.bgra), shot.size))
            if elapsed >= args.seconds:
                break
    click_thread.join()

    for index, (_timestamp, pixels, size) in enumerate(frames):
        Image.frombytes("RGB", size, pixels, "raw", "BGRX").save(
            args.output / f"frame_{index:03d}.png"
        )
    metadata = {
        "handle": handle,
        "destination_client": [args.x, args.y],
        "destination_screen": list(click_result.get("screen", ())),
        "clicked_at_seconds": click_result.get("at"),
        "duration_seconds": frames[-1][0],
        "frame_count": len(frames),
        "timestamps": [timestamp for timestamp, _pixels, _size in frames],
    }
    (args.output / "capture.json").write_text(
        json.dumps(metadata, ensure_ascii=True, indent=2), encoding="ascii"
    )
    print(json.dumps(metadata))


if __name__ == "__main__":
    main()
