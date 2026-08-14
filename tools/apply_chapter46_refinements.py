from pathlib import Path


root = Path(r"C:\mengde")
stage = root / "game/sce/dongzhou/stage/46a.lua"
text = stage.read_text(encoding="utf-8")
old = 'di_remnants(game) <= 4 and game:is_unit_within("HuSheGu27", {30,13}, 1)'
new = 'di_remnants(game) <= 4 and game:are_units_within("HuSheGu27", "BaiTun46", 1)'
assert text.count(old) == 1
text = text.replace(old, new, 1)
stage.write_text(text, encoding="utf-8", newline="")
print("Updated Dagu pursuit to unit-to-unit adjacency.")
