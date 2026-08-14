from pathlib import Path


path = Path(__file__).resolve().parents[1] / "rl/chapter50_test.py"
text = path.read_text(encoding="utf-8")
old = 'alpha = Counter(image.getchannel("A").getdata())'
new = 'alpha = Counter(image.getchannel("A").get_flattened_data())'
if old not in text:
    raise RuntimeError("Pillow API anchor missing")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Chapter 50 asset test updated to the current Pillow pixel API.")
