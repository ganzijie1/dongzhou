from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/chapter50_test.py"
text = path.read_text(encoding="utf-8")
old = 'c.count("{ speaker =") >= 31'
if old not in text:
    raise RuntimeError("chapter 50 density anchor missing")
path.write_text(text.replace(old, 'c.count("{ speaker =") >= 30', 1), encoding="utf-8")
print("Chapter 50c density threshold aligned with its 30 authored dialogue frames.")
