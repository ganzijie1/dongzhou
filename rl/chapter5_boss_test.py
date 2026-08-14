"""Regression checks for the sixth battle's named enemy commanders."""

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 6")
        story = env.story_info()
        assert story["battle_title"] == "东门诱敌"

        units = [unit for unit in env.unit_info() if not unit["dead"]]
        assert all(int(unit["level"]) == 1 for unit in units)
        by_name = {}
        for unit in units:
            by_name.setdefault(unit["name"], []).append(unit)

        zhou_xu = by_name["ZhouXu5"][0]
        shi_hou = by_name["ShiHou5"][0]
        assert (zhou_xu["class"], int(zhou_xu["force"]), int(zhou_xu["x"]), int(zhou_xu["y"])) == (
            "Lord", 4, 15, 5
        )
        assert (shi_hou["class"], int(shi_hou["force"]), int(shi_hou["x"]), int(shi_hou["y"])) == (
            "Strategist", 4, 16, 4
        )
        assert len([unit for unit in units if int(unit["force"]) == 4]) == 8
        assert all(unit["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"} for unit in units)

    print("sixth battle ok: Zhou Xu and Shi Hou added as level-one named enemy commanders")


if __name__ == "__main__":
    main()