from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_config_alignment():
    config = (ROOT / "game/sce/dongzhou/config.lua").read_text(encoding="utf-8")
    terrain_block = re.search(r"terrains\s*=\s*\{(.*?)\n    \},\n    terrain_movecost", config, re.S).group(1)
    terrains = re.findall(r'id = "([^"]+)", char = "([^"]+)"', terrain_block)
    move_block = re.search(r"terrain_movecost\s*=\s*\{(.*?)\n    \},\n    terrain_effect", config, re.S).group(1)
    effect_block = re.search(r"terrain_effect\s*=\s*\{(.*?)\n    \},\n    magics", config, re.S).group(1)
    costs = re.findall(r"\{([^{}]+)\}", move_block)
    effects = re.findall(r"\{([^{}]+)\}", effect_block)
    assert len(terrains) == len(costs) == len(effects)
    lookup = {name: [int(x.strip()) for x in costs[i].split(",")] for i, (name, _) in enumerate(terrains)}
    chars = dict(terrains)
    assert chars["Snow"] == "s" and chars["ShallowRiver"] == "v" and chars["Water"] == "~"
    assert max(lookup["Snow"]) < 255
    assert max(lookup["ShallowRiver"]) < 255 and min(lookup["ShallowRiver"]) >= 2
    assert all(value == 255 for value in lookup["Water"])
    gui = (ROOT / "rl/play_gui.py").read_text(encoding="utf-8")
    for text in ('"Snow": "雪地"', '"ShallowRiver": "小河"', '"Water": "大河"'):
        assert text in gui


if __name__ == "__main__":
    test_config_alignment()
    print("snow and shallow-river terrain checks passed")
