"""Regression checks for chapter thirty-seven's cutscene-only adaptation."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def main() -> None:
    config = Path("game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    stages = next(line for line in config.splitlines() if "stages = {" in line)
    assert '"36a", "36b"' in stages
    assert '"37"' not in stages
    assert not Path("game/sce/dongzhou/stage/37.lua").exists()

    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 60")
        story = env.story_info()
        victory = story["victory"]
        text = "\n".join(entry["text"] for entry in victory)
        assert len(victory) == 76
        assert "第三十七回　介子推守志焚绵上　太叔带怙宠入宫中" in text
        assert "头须御车" in text
        assert "立儿子驩为太子" in text
        assert "立叔隗为正室、赵盾为嫡子" in text
        assert "改绵山为介山" in text
        assert "寒食习俗" in text
        assert "攻破栎城" in text
        assert "北邙山大集车徒" in text
        assert "就留待第38回继续" in text
        speakers = {entry["speaker"] for entry in victory}
        assert {"头须", "晋文公", "介子推", "解张", "周襄王", "富辰", "隗后", "太叔带", "小东"} <= speakers

    print("chapter 37 ok: dense cutscene, no forced battle/map, and chapter 38 handoff")


if __name__ == "__main__":
    main()
