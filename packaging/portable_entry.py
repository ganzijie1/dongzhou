"""PyInstaller entry point for the portable Windows distribution."""

from __future__ import annotations

import ctypes
import os
import sys
import traceback
from pathlib import Path


def _report_unhandled(error_type, error, error_traceback):
    log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Ekgd" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "startup-error.log"
    details = "".join(traceback.format_exception(error_type, error, error_traceback))
    log_path.write_text(details, encoding="utf-8")
    ctypes.windll.user32.MessageBoxW(
        None,
        f"游戏启动失败，错误日志已保存到：\n{log_path}",
        "东周列国志 MOD",
        0x10,
    )


sys.excepthook = _report_unhandled

# Explicit imports let PyInstaller see dependencies used by the preserved GUI payload.
import gymnasium  # noqa: E402,F401
import numpy  # noqa: E402,F401
import pygame  # noqa: E402,F401
from rl import mengde_env, runtime_policy, save_system, smoke_test  # noqa: E402,F401
from tools import e5_archive  # noqa: E402,F401
from rl import play_gui  # noqa: E402


if __name__ == "__main__":
    if "--scenario" not in sys.argv:
        sys.argv.extend(["--scenario", "dongzhou"])
    play_gui.main()