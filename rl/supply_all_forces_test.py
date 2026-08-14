"""Regression checks for restorative sites across every battle force."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def verify_recovery(
    env: MengdeEnv,
    *,
    previous_force: int,
    target_name: str,
    site: tuple[int, int],
    restore_hp: int,
    restore_mp: int,
) -> None:
    env._request("LOAD_STAGE 2")
    snapshot = env.snapshot()
    snapshot["current_force"] = previous_force
    for unit in snapshot["units"]:
        unit["done"] = True

    target = next(unit for unit in snapshot["units"] if unit["name"] == target_name)
    target["x"], target["y"] = site
    target["hp"], target["mp"] = 1, 0

    actor = next(
        unit for unit in snapshot["units"]
        if int(unit["force"]) == previous_force and unit["name"] != target_name
    )
    actor["done"] = False
    env.restore(snapshot)

    wait = next(
        action for action in env.list_actions()
        if int(action["unit"]) == int(actor["id"]) and int(action["type"]) == 0
    )
    env.step(int(wait["index"]))

    recovered = next(unit for unit in env.unit_info() if unit["name"] == target_name)
    expected_hp = 1 + int(recovered["max_hp"]) * restore_hp // 100
    assert int(recovered["hp"]) == expected_hp, (
        target_name, recovered, expected_hp, env.notices()
    )
    assert int(recovered["mp"]) == int(recovered["max_mp"]) * restore_mp // 100


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        verify_recovery(
            env,
            previous_force=4,
            target_name="ZhengHuanGong",
            site=(9, 7),
            restore_hp=20,
            restore_mp=10,
        )
        verify_recovery(
            env,
            previous_force=1,
            target_name="ZhouYouWang",
            site=(9, 0),
            restore_hp=25,
            restore_mp=10,
        )
        verify_recovery(
            env,
            previous_force=2,
            target_name="BoDing41",
            site=(2, 11),
            restore_hp=20,
            restore_mp=10,
        )

    print("supply recovery ok: own, ally, and enemy forces recover at turn start")


if __name__ == "__main__":
    main()
