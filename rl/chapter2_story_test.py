"""Regression checks for the complete chapter-two interlude."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.play_gui import story_entries


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, scenario="dongzhou", interactive=True) as env:
        env.reset()
        env._request("LOAD_STAGE 1")
        story = env.story_info()
        intro = list(story["intro"])
        frames = story_entries(intro, "点击进入下一回")

        assert story["chapter"] == "第二回"
        assert story["story_only"] is True
        assert len(intro) >= 50, len(intro)
        assert len(frames) == len(intro), (len(frames), len(intro))
        assert intro[0]["speaker"] == "旁白"
        assert "宣王" in intro[0]["text"]
        assert intro[-1]["speaker"] == "下回预告"
        assert "第三回" in intro[-1]["text"]

    print(f"chapter two story ok: {len(frames)} frontend frames from beginning to preview")


if __name__ == "__main__":
    main()