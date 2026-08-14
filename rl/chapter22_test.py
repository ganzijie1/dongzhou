"""Regression checks for chapter twenty-two and the Menglao duel."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 36")
        assert env.next_stage() is not None
        story = env.story_info()
        assert story["chapter"] == "第二十二回"
        assert story["title"] == "公子友两定鲁君 齐皇子独对委蛇"
        assert story["battle_title"] == "郦地退莒"
        assert story["map_asset"] == "m037.png"
        assert len(story["intro"]) == 17
        assert len(story["victory"]) == 14
        duel = story["duels"][0]
        assert (duel["attacker"], duel["defender"], duel["outcome"], duel["exp"]) == (
            "JiYou22", "YingNa22", "kill", 70
        )
        assert "孟劳" in duel["text"]

        map_info = env.map_info()
        assert (int(map_info["width"]), int(map_info["height"])) == (19, 14)
        units = {unit["name"]: unit for unit in env.unit_info() if not unit["dead"]}
        assert (units["JiYou22"]["x"], units["JiYou22"]["y"], units["JiYou22"]["terrain"]) == (4, 11, "Camp")
        assert (units["YingNa22"]["x"], units["YingNa22"]["y"], units["YingNa22"]["terrain"]) == (14, 2, "Camp")
        assert all(unit["terrain"] not in {"Wall", "RockyMountain", "Water", "Fence"} for unit in units.values())

        snapshot = env.snapshot()
        for unit in snapshot["units"]:
            if unit["name"] == "JiYou22":
                unit["x"], unit["y"] = 13, 2
        env.restore(snapshot)
        units = {unit["name"]: unit for unit in env.unit_info()}
        _, reward, terminated, truncated, info = env.resolve_duel(
            int(units["JiYou22"]["id"]), int(units["YingNa22"]["id"])
        )
        assert reward >= 2.0
        assert terminated and not truncated and int(info["status"]) == 3
        assert next(unit for unit in env.unit_info() if unit["name"] == "YingNa22")["dead"]

    map_path = Path("assets/lzc/map/m037.png")
    assert map_path.stat().st_size > 1_000_000
    print("chapter 22 ok: dense story, Li battlefield, valid deployment, and Menglao duel victory")


if __name__ == "__main__":
    main()