"""Regression check for restoring after a speculative terminal branch."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def main() -> None:
    with MengdeEnv(
        EXECUTABLE, scenario="dongzhou", max_episode_actions=40,
        interactive=True,
    ) as env:
        env.reset(seed=2026)
        root = env.snapshot()
        terminal_branch = deepcopy(root)
        for unit in terminal_branch["units"]:
            if int(unit["force"]) == 1 and unit["name"] in {"DuBo", "ZuoRu"}:
                unit["hp"] = 0
        terminal_branch["current_force"] = 4
        env.restore(terminal_branch, restart_process=False)
        wait = next(action for action in env.list_actions() if int(action["type"]) == 0)
        _, _, terminated, _, info = env.step(int(wait["index"]))
        assert terminated and int(info["status"]) == 4

        env.restore(root, restart_process=False)
        assert env.list_actions(), "restored root must reopen legal actions"
        assert int(env.snapshot()["current_force"]) == int(root["current_force"])

    print("in-process restore reopens battle after speculative terminal branch")


if __name__ == "__main__":
    main()
