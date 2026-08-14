"""Regression checks for chapter-three Quanrong reinforcement rules."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def alive_count(env: MengdeEnv, name: str) -> int:
    return sum(not unit["dead"] and unit["name"] == name for unit in env.unit_info())


def defeat(snapshot: dict, name: str, *, count: int = 1) -> None:
    defeated = 0
    for unit in snapshot["units"]:
        if unit.get("name") == name and int(unit["hp"]) > 0:
            unit["hp"] = 0
            defeated += 1
            if defeated == count:
                return
    raise AssertionError((name, count, defeated))


def advance_one_turn(env: MengdeEnv) -> None:
    start_turn = int(env.snapshot()["turn_current"])
    for _ in range(100):
        if int(env.snapshot()["turn_current"]) > start_turn:
            return
        actions = env.list_actions()
        assert actions
        action = next((item for item in actions if int(item["type"]) == 0), actions[0])
        _, _, terminated, truncated, _ = env.step(int(action["index"]))
        assert not terminated and not truncated
    raise AssertionError("turn did not advance")


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True, max_episode_actions=500) as env:
        env.reset()
        env._request("LOAD_STAGE 2")
        assert alive_count(env, "QuanRongLeftWarrior") == 3
        assert alive_count(env, "QuanRongRightWarrior") == 3

        snapshot = env.snapshot()
        defeat(snapshot, "QuanRongLeftWarrior")
        defeat(snapshot, "BoDing41")
        env.restore(snapshot)
        advance_one_turn(env)
        assert alive_count(env, "QuanRongLeftWarrior") == 3
        assert alive_count(env, "QuanRongRightWarrior") == 3
        assert alive_count(env, "BoDing41") == 0
        assert alive_count(env, "ManYeSu41") == 1

        env._request("LOAD_STAGE 2")
        snapshot = env.snapshot()
        defeat(snapshot, "QuanRongLord")
        defeat(snapshot, "QuanRongWarrior", count=6)
        env.restore(snapshot)
        action = next(item for item in env.list_actions() if int(item["type"]) == 0)
        env.step(int(action["index"]))
        assert alive_count(env, "QuanRongLord") == 0
        assert sum(
            alive_count(env, name)
            for name in ("QuanRongWarrior", "QuanRongWarrior2", "QuanRongArcher")
        ) == 10
        assert alive_count(env, "QuanRongLord") == 0

    print("Quanrong reinforcements ok: flank troops return next turn; named generals stay withdrawn")


if __name__ == "__main__":
    main()