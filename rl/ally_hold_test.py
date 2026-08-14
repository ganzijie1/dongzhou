"""Regression checks for chapter-three allied hold-position orders."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def wait_for_zheng(env: MengdeEnv) -> None:
    zheng = next(unit for unit in env.unit_info() if unit["name"] == "ZhengHuanGong")
    action = next(
        item for item in env.list_actions()
        if int(item["unit"]) == int(zheng["id"]) and int(item["type"]) == 0
    )
    env.step(int(action["index"]))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env.reset()
        env._request("LOAD_STAGE 2")
        snapshot = env.snapshot()
        enemy = next(unit for unit in snapshot["units"] if unit.get("name") == "QuanRongLeftWarrior")
        enemy["x"], enemy["y"] = 5, 6
        env.restore(snapshot)
        wait_for_zheng(env)
        assert int(env.snapshot()["current_force"]) == 2
        details = {int(unit["id"]): unit for unit in env.unit_info()}
        actions = env.list_actions()
        assert actions
        for action in actions:
            actor = details[int(action["unit"])]
            assert int(actor["force"]) == 2
            assert (int(action["x"]), int(action["y"])) == (int(actor["x"]), int(actor["y"]))
        assert any(int(action["type"]) == 2 for action in actions)
        assert not any(int(action["type"]) == 1 for action in actions)

        env._request("LOAD_STAGE 2")
        snapshot = env.snapshot()
        next(unit for unit in snapshot["units"] if unit.get("name") == "GuoShiFu")["hp"] = 0
        env.restore(snapshot)
        zheng = next(unit for unit in env.unit_info() if unit["name"] == "ZhengHuanGong")
        wait = next(
            item for item in env.list_actions()
            if int(item["unit"]) == int(zheng["id"]) and int(item["type"]) == 0
        )
        _, _, terminated, _, info = env.step(int(wait["index"]))
        assert not terminated and int(info["status"]) != 4

        env._request("LOAD_STAGE 2")
        snapshot = env.snapshot()
        snapshot["current_force"] = 2
        next(unit for unit in snapshot["units"] if unit.get("name") == "ZhengHuanGong")["hp"] = 0
        env.restore(snapshot)
        wait = next(item for item in env.list_actions() if int(item["type"]) == 0)
        _, _, terminated, _, info = env.step(int(wait["index"]))
        assert terminated and int(info["status"]) == 4

    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=False) as env:
        env.reset()
        env._request("LOAD_STAGE 2")
        before = {
            int(unit["id"]): (int(unit["x"]), int(unit["y"]))
            for unit in env.unit_info() if int(unit["force"]) == 2
        }
        wait_for_zheng(env)
        after = {
            int(unit["id"]): (int(unit["x"]), int(unit["y"]))
            for unit in env.unit_info() if int(unit["force"]) == 2 and not unit["dead"]
        }
        assert after
        assert all(after[unit_id] == before[unit_id] for unit_id in after)

    print("allied hold order ok: only stationary attacks, skills, or waits; native AI does not move")


if __name__ == "__main__":
    main()