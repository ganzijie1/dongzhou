from pathlib import Path
p=Path(__file__).with_name("fix_chapter56_an_deployment.py")
p.write_text('''from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "game/sce/dongzhou/stage/56b.lua"
s = p.read_text(encoding="utf-8")
old = "{{39,16},{39,19},{39,22}"
new = "{{35,16},{39,19},{39,22}"
if old in s:
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
elif new not in s:
    raise RuntimeError("chapter56 An deployment anchor missing")
print("chapter56 An deployment is on passable ground")
''', encoding="utf-8")
print("chapter56 deployment fixer normalized")
