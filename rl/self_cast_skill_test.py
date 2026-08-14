"""Regression test for friendly skills targeting their caster."""

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 0")
        env.reset()
        before = next(unit for unit in env.unit_info() if unit["name"] == "ZuoRu")
        action = next(
            candidate for candidate in env.list_actions()
            if candidate.get("skill") == "buff_dex"
            and candidate.get("target") == before["id"]
            and candidate["x"] == before["x"]
            and candidate["y"] == before["y"]
        )
        env.step(action["index"])
        after = next(unit for unit in env.unit_info() if unit["name"] == "ZuoRu")
        assert after["mp"] == before["mp"] - 6
        assert after["dex"] > before["dex"]
        assert after["done"] is True

        enemy_skills = [
            candidate for candidate in env.list_actions()
            if candidate.get("skill") == "fire_0"
            and candidate.get("target") == candidate.get("unit")
        ]
        assert not enemy_skills

    print("self-cast skill ok: friendly buff targets caster; enemy skill cannot")


if __name__ == "__main__":
    main()
