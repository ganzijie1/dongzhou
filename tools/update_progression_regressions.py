from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(relative, old, new):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing: {relative}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "rl/chapter45_test.py",
    '    assert \', "44", "45a", "45b" }\' in config',
    '    assert \'"44", "45a", "45b", "46a"\' in config',
)
replace_once(
    "rl/chapter46_test.py",
    '    assert \', "45a", "45b", "46a", "46b", "46c" }\' in config',
    '    assert \'"45a", "45b", "46a", "46b", "46c", "47a"\' in config',
)
print("Updated chapter progression regressions to use local sequence anchors.")
