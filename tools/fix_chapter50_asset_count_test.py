from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/chapter50_test.py"
text = path.read_text(encoding="utf-8")
old = "assert len(files) == 32"
if old not in text:
    raise RuntimeError("asset count anchor missing")
path.write_text(text.replace(old, "assert len(files) == 36", 1), encoding="utf-8")
print("Ling Ao regression now covers all 36 runtime animation files.")
