"""Regression checks for proximity ambushes and delayed reinforcements."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def move_snapshot_unit(snapshot: dict, unit_id: int, position: tuple[int, int]) -> None:
    unit = next(unit for unit in snapshot["units"] if int(unit["id"]) == unit_id)
    unit["x"], unit["y"] = position


def wait_with_unit(env: MengdeEnv, unit_id: int) -> None:
    action = next(
        action for action in env.list_actions()
        if int(action["unit"]) == unit_id and int(action["type"]) == 0
    )
    env.step(int(action["index"]))


def unit_id(env: MengdeEnv, name: str) -> int:
    return int(next(unit for unit in env.unit_info() if unit["name"] == name)["id"])


def force_counts(env: MengdeEnv) -> tuple[int, int]:
    units = [unit for unit in env.unit_info() if not unit["dead"]]
    return (
        sum(int(unit["force"]) == 1 for unit in units),
        sum(int(unit["force"]) == 4 for unit in units),
    )


def trigger_by_position(
    env: MengdeEnv,
    stage_index: int,
    moving_name: str,
    moving_position: tuple[int, int],
    waiting_name: str,
    expected_delta: tuple[int, int],
) -> None:
    env._request(f"LOAD_STAGE {stage_index}")
    snapshot = env.snapshot()
    move_snapshot_unit(snapshot, unit_id(env, moving_name), moving_position)
    env.restore(snapshot)
    before = force_counts(env)
    wait_with_unit(env, unit_id(env, waiting_name))
    after = force_counts(env)
    assert (after[0] - before[0], after[1] - before[1]) == expected_delta, (
        stage_index, before, after
    )


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env.reset()
        trigger_by_position(env, 11, "DaLiang8", (4, 8), "GongSunDaiZhong8", (2, 0))
        trigger_by_position(env, 13, "ChenEscort101", (8, 9), "CaiJi101", (4, 0))
        trigger_by_position(env, 15, "LuHuanGong11", (10, 4), "LuHuanGong11", (0, 3))

        env._request("LOAD_STAGE 16")
        snapshot = env.snapshot()
        snapshot["turn_current"] = 5
        env.restore(snapshot)
        before = force_counts(env)
        wait_with_unit(env, unit_id(env, "LuHuanGong11"))
        after = force_counts(env)
        assert (after[0] - before[0], after[1] - before[1]) == (0, 3), (before, after)

        trigger_by_position(env, 17, "JiZu11", (12, 3), "JiZu11", (2, 5))

        env._request("LOAD_STAGE 18")
        snapshot = env.snapshot()
        snapshot["turn_current"] = 3
        env.restore(snapshot)
        before = force_counts(env)
        wait_with_unit(env, unit_id(env, "JiZu11"))
        after = force_counts(env)
        assert (after[0] - before[0], after[1] - before[1]) == (0, 2), (before, after)

        trigger_by_position(env, 19, "ZhengZhaoGong12", (11, 7), "GaoQuMi12", (3, 0))
        trigger_by_position(env, 21, "ZiWei13", (9, 8), "QiXiangGong13", (5, 0))

        env._request("LOAD_STAGE 22")
        snapshot = env.snapshot()
        snapshot["turn_current"] = 3
        env.restore(snapshot)
        before = force_counts(env)
        wait_with_unit(env, unit_id(env, "QiXiangGong14"))
        after = force_counts(env)
        assert (after[0] - before[0], after[1] - before[1]) == (0, 3), (before, after)

        trigger_by_position(env, 23, "LianCheng14", (9, 8), "LianCheng14", (0, 1))
        trigger_by_position(env, 24, "LuZhuangGong15", (9, 8), "QiHuanGong15", (4, 0))

    print("scripted spawns ok: 8 proximity ambushes, 3 delayed reinforcements")


if __name__ == "__main__":
    main()
