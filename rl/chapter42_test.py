"""Regression checks for chapter 42's story-only Heyang audience and trial."""

from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    stage = (root / "game/sce/dongzhou/stage/42.lua").read_text(encoding="utf-8")
    config = (root / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    gui = (root / "rl/play_gui.py").read_text(encoding="utf-8")

    assert '"39", "40", "42"' in config
    assert "story_only = true" in stage
    assert "\u65c1\u767d" not in stage
    assert all(term in stage for term in (
        "\u5143\u89d2", "\u53d4\u6b66", "\u6b47\u72ac", "\u4e09\u884c",
        "\u6cb3\u9633", "\u516c\u9986", "\u58eb\u8363", "\u937c\u5e84\u5b50", "\u516c\u5b50\u7455",
    ))
    assert all(name in gui for name in (
        r'"\u536b\u6210\u516c"', r'"\u5143\u54ba"', r'"\u53d4\u6b66"',
        r'"\u5b81\u4fde"', r'"\u738b\u5b50\u864e"',
    ))

    with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
        env._request("LOAD_STAGE 65")
        story = env.story_info()
        assert story["chapter"] == "\u7b2c\u56db\u5341\u4e8c\u56de"
        assert story["title"] == "\u5468\u8944\u738b\u6cb3\u9633\u53d7\u89d0 \u536b\u5143\u54ba\u516c\u9986\u5bf9\u72f1"
        assert story["battle_title"] == "\u6cb3\u9633\u53d7\u89d0"
        assert story["story_only"] is True
        assert story["map_asset"] == "m049.png"
        assert len(story["intro"]) >= 60
        assert not story["victory"] and not story["defeat"]
        assert all(entry["speaker"] != "\u65c1\u767d" for entry in story["intro"])

    print("chapter 42 ok: full story-only Heyang audience, Shuwu case, and hall trial")


if __name__ == "__main__":
    main()
