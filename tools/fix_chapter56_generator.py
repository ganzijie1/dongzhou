from pathlib import Path
p=Path(__file__).with_name("generate_chapter56_maps.py")
s=p.read_text(encoding="utf-8")
old='common.draw_fences(im,f,bounds,g)'
if old not in s: raise RuntimeError("chapter56 fence call anchor missing")
p.write_text(s.replace(old,'common.draw_fences(im,f,bounds)',1),encoding="utf-8")
print("chapter56 fence renderer call corrected")
