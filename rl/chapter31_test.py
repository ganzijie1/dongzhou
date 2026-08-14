"""Regression checks for chapter thirty-one's Di escape battle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
IMPASSABLE = {"Wall", "RockyMountain", "Water", "Fence"}


def living(env: MengdeEnv) -> list[dict]:
    return [unit for unit in env.unit_info() if not unit["dead"]]


def wait_once(env: MengdeEnv) -> tuple:
    action = next(item for item in env.list_actions() if int(item["type"]) == 0)
    return env.step(int(action["index"]))


def main() -> None:
    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 52")
        story = env.story_info()
        assert story["chapter"] == "第三十一回"
        assert story["title"] == "晋惠公怒杀庆郑 介子推割股啖君"
        assert story["battle_title"] == "翟国脱险"
        assert story["map_asset"] == "m052.png"
        assert len(story["intro"]) == 19
        assert len(story["victory"]) == 24

        info = env.map_info()
        assert (int(info["width"]), int(info["height"])) == (19, 14)
        terrain = list(info["terrain"])
        units = living(env)
        assert len(units) == 10
        assert all(unit["terrain"] not in IMPASSABLE for unit in units)
        names = {unit["name"] for unit in units}
        assert {
            "ChongEr27", "HuMao27", "HuYan27", "ZhaoShuai27", "XuChen27",
            "WeiChou27", "HuSheGu27", "DianJie27", "JieZiTui27", "XianZhen27",
        } == names
        assert "BoDi27" not in names
        assert terrain[12 * 19 + 2] == "Grass"
        assert terrain[1 * 19 + 17] == "Forest"

        turn_three = env.snapshot()
        turn_three["turn_current"] = 3
        env.restore(turn_three)
        wait_once(env)
        pursuers = [
            unit for unit in living(env)
            if unit["name"] in {"BoDi27", "Assassin31", "AssassinArcher31"}
        ]
        assert len(pursuers) == 4
        assert all(unit["terrain"] not in IMPASSABLE for unit in pursuers)
        assert sum(unit["name"] == "Assassin31" for unit in pursuers) == 2

        # A companion reaching the exit must not substitute for Chong Er.
        env._request("LOAD_STAGE 52")
        companion_exit = env.snapshot()
        next(unit for unit in companion_exit["units"] if unit["name"] == "HuYan27").update(
            {"x": 17, "y": 1}
        )
        env.restore(companion_exit)
        _, _, terminated, _, _ = wait_once(env)
        assert not terminated

        # Only Chong Er at the northeast exit completes the battle.
        env._request("LOAD_STAGE 52")
        escaped = env.snapshot()
        next(unit for unit in escaped["units"] if unit["name"] == "ChongEr27").update(
            {"x": 17, "y": 1}
        )
        env.restore(escaped)
        _, _, terminated, truncated, result = wait_once(env)
        assert terminated and not truncated and int(result["status"]) == 3

    map_path = Path("assets/lzc/map/m052.png")
    assert map_path.stat().st_size > 1_000_000
    old_maps = [Path("assets/lzc/map/m050.png"), Path("assets/lzc/map/m051.png")]
    hashes = {hashlib.sha256(path.read_bytes()).digest() for path in [*old_maps, map_path]}
    assert len(hashes) == 3

    prediction = json.loads(
        Path("output/terrain_model/m052_ch31_prediction.json").read_text(encoding="utf-8")
    )
    assert prediction["grid"] == [19, 14]
    assert prediction["feature_backend"] == "dinov3-directional-v2"
    assert prediction["fence_review_required"] == []
    print("chapter 31 ok: Di escape, delayed pursuit, Chong Er-only exit, terrain, story, and UI data")


if __name__ == "__main__":
    main()
