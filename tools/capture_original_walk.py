"""Capture a short original-game movement sequence from a selected destination."""

from __future__ import annotations

import argparse
import ctypes
import time
from ctypes import wintypes
from pathlib import Path

from mss import mss
from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle", type=int, required=True)
    parser.add_argument("--x", type=int, required=True, help="client destination x")
    parser.add_argument("--y", type=int, required=True, help="client destination y")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=2.5)
    args = parser.parse_args()

    user32 = ctypes.windll.user32
    user32.ShowWindow(args.handle, 9)
    user32.SetForegroundWindow(args.handle)
    time.sleep(0.4)
    rect = wintypes.RECT()
    user32.GetWindowRect(args.handle, ctypes.byref(rect))
    client_origin = wintypes.POINT(0, 0)
    user32.ClientToScreen(args.handle, ctypes.byref(client_origin))
    user32.SetCursorPos(client_origin.x + args.x, client_origin.y + args.y)
    lparam = (args.y << 16) | args.x
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    frames: list[tuple[bytes, tuple[int, int]]] = []
    mouse_state = 0
    with mss() as capture:
        while time.perf_counter() - started < args.seconds:
            elapsed = time.perf_counter() - started
            if mouse_state == 0 and elapsed >= 0.20:
                user32.PostMessageW(args.handle, 0x0200, 0, lparam)
                user32.PostMessageW(args.handle, 0x0201, 1, lparam)
                mouse_state = 1
            elif mouse_state == 1 and elapsed >= 0.23:
                user32.PostMessageW(args.handle, 0x0202, 0, lparam)
                mouse_state = 2
            rect = wintypes.RECT()
            if not user32.GetWindowRect(args.handle, ctypes.byref(rect)):
                break
            shot = capture.grab(
                {
                    "left": rect.left,
                    "top": rect.top,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top,
                }
            )
            frames.append((bytes(shot.bgra), shot.size))
    for frame, (pixels, size) in enumerate(frames):
        image = Image.frombytes("RGB", size, pixels, "raw", "BGRX")
        image.save(args.output / f"frame_{frame:03d}.png")
    print(f"captured {len(frames)} frames")


if __name__ == "__main__":
    main()
