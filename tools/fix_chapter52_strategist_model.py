from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for relative in ("tools/apply_chapter52_updates.py", "game/sce/dongzhou/config.lua"):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    old = 'id = "GongZiQuJi52", class = "Strategist", stat = {91, 86, 94, 92, 91}, model = "strategist-1-red"'
    new = 'id = "GongZiQuJi52", class = "Strategist", stat = {91, 86, 94, 92, 91}, model = "Strategist-1-red"'
    if old not in text:
        raise RuntimeError(f"anchor missing in {relative}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Chapter 52 strategist model corrected.")
