"""Verify the native mengde RL protocol without training a model."""

from __future__ import annotations

import argparse
from pathlib import Path

from rl.mengde_env import MengdeEnv


DEFAULT_EXECUTABLES = (
    Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe"),
    Path("build/rl-vcpkg/game/src/rl/Debug/mengde_rl.exe"),
    Path("build/game/src/rl/Release/mengde_rl.exe"),
    Path("build/game/src/rl/mengde_rl"),
)


def find_executable(value: Path | None) -> Path:
    if value is not None:
        return value
    for candidate in DEFAULT_EXECUTABLES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("mengde_rl not found; pass --executable with its build path")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--steps", type=int, default=3)
    args = parser.parse_args()

    executable = find_executable(args.executable)
    with MengdeEnv(executable, scenario=args.scenario) as env:
        observation, info = env.reset()
        print(
            f"RESET ok: observation={observation.shape}, "
            f"legal_actions={info['action_count']}"
        )
        for step in range(1, args.steps + 1):
            actions = env.list_actions()
            if not actions:
                raise RuntimeError("native environment returned no legal actions")
            selected = 0
            observation, reward, terminated, truncated, info = env.step(selected)
            print(
                f"STEP {step} ok: action={selected}, reward={reward:.3f}, "
                f"legal_actions={info['action_count']}, done={terminated or truncated}"
            )
            if terminated or truncated:
                break
    print("mengde RL smoke test passed")


if __name__ == "__main__":
    main()
