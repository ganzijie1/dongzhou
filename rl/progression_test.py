"""Verify named Dongzhou commanders retain progression across absent stages."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable


def set_progress(snapshot: dict, name: str, level: int, exp: int) -> None:
    for unit in snapshot["units"]:
        if unit["name"] == name:
            unit["level"] = level
            unit["exp"] = exp
            return
    raise AssertionError(f"unit not found: {name}")


def assert_progress(snapshot: dict, name: str, level: int, exp: int) -> None:
    for unit in snapshot["units"]:
        if unit["name"] == name:
            actual = (int(unit["level"]), int(unit["exp"]))
            assert actual == (level, exp), (name, actual)
            return
    raise AssertionError(f"unit not found: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    args = parser.parse_args()

    executable = find_executable(args.executable)
    with MengdeEnv(executable, scenario="dongzhou") as env:
        env._request("LOAD_STAGE 12")
        chapter_nine = env.snapshot()
        for unit in chapter_nine["units"]:
            if int(unit["force"]) == 1:
                unit["level"] = 6
                unit["exp"] = 0
        set_progress(chapter_nine, "JiZu9", 6, 37)
        set_progress(chapter_nine, "GaoQuMi9", 2, 54)
        env.restore(chapter_nine)

        for _ in range(5):
            assert env.next_stage() is not None
        chapter_eleven = env.snapshot()
        assert_progress(chapter_eleven, "JiZu11", 6, 37)
        gao_history = chapter_eleven["commander_progress"]["GaoQuMi"]
        assert (gao_history["level"], gao_history["exp"]) == (2, 54)
        assert env.training_options() == []

        env.restore(chapter_eleven)
        assert env.next_stage() is not None
        before_chapter_twelve_b = env.snapshot()

        two_stage_gap = copy.deepcopy(before_chapter_twelve_b)
        two_stage_gap["commander_progress"]["GaoQuMi"]["last_stage"] = 17
        env.restore(two_stage_gap)
        assert env.next_stage() is not None
        assert env.training_options() == []

        three_stage_gap = copy.deepcopy(before_chapter_twelve_b)
        three_stage_gap["commander_progress"]["GaoQuMi"]["last_stage"] = 16
        env.restore(three_stage_gap)
        assert env.next_stage() is not None
        chapter_twelve_b = env.snapshot()
        assert_progress(chapter_twelve_b, "GaoQuMi12", 2, 54)
        candidates = env.training_options()
        assert len(candidates) == 1, candidates
        candidate = candidates[0]
        assert candidate["hero_id"] == "GaoQuMi12"
        target = int(candidate["target_level"])
        penalty = int(candidate["penalty"])
        assert target > 2 and penalty == (target - 2 + 1) // 2

        result = env.train_commander("GaoQuMi12")
        assert (result["level"], result["training_penalty"]) == (target, penalty)
        trained_snapshot = env.snapshot()
        assert_progress(trained_snapshot, "GaoQuMi12", target, 54)
        assert trained_snapshot["commander_progress"]["GaoQuMi"][
            "training_penalty"
        ] == penalty
        trained_unit = next(
            unit for unit in env.unit_info() if unit["name"] == "GaoQuMi12"
        )

        normal_snapshot = copy.deepcopy(trained_snapshot)
        normal_snapshot["commander_progress"]["GaoQuMi"]["training_penalty"] = 0
        env.restore(normal_snapshot)
        normal_unit = next(
            unit for unit in env.unit_info() if unit["name"] == "GaoQuMi12"
        )
        for stat in ("atk", "def", "dex", "int", "mor"):
            assert int(normal_unit[stat]) - int(trained_unit[stat]) == penalty

        env.restore(trained_snapshot)
        reloaded = env.snapshot()["commander_progress"]["GaoQuMi"]
        assert (reloaded["level"], reloaded["training_penalty"]) == (
            target,
            penalty,
        )

    print("commander progression ok: inheritance, optional catch-up, penalty, and reload")


if __name__ == "__main__":
    main()
