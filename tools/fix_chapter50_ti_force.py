from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


for relative in ("tools/apply_chapter50_updates.py", "game/sce/dongzhou/stage/50c.lua"):
    replace(
        ROOT / relative,
        'game:generate_unit("TiMiMing50", 1, Enum.force.ally, {27,13})',
        'game:generate_unit("TiMiMing50", 1, Enum.force.own, {27,13})',
    )

print("Ti Mi Ming is player-controlled so the historical sacrifice is reachable and explicit.")
