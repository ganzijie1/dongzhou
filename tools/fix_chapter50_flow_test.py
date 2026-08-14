from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/chapter50_test.py"
text = path.read_text(encoding="utf-8")
old = '''    assert 'not game:has_unit("TiMiMing50")' in c
    assert 'game:generate_unit("LingZhe50"' in c'''
new = '''    assert 'game:is_unit_within("ZhaoDun47", {12,13}, 1)' in c
    assert 'game:generate_unit("LingZhe50", 1, Enum.force.ally, {10,13})' in c'''
if old not in text:
    raise RuntimeError("Taoyuan test anchor missing")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Taoyuan regression aligned with gate-crossing sacrifice trigger.")
