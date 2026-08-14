from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def update(path):
    text = path.read_text(encoding="utf-8")
    old = '''    if not ti_fallen and not game:has_unit("TiMiMing50") then
        ti_fallen = true
        game:generate_unit("LingZhe50", 1, Enum.force.ally, {15,13})
        ling_zhe_arrived = true
        game:push_cmd_speak(0, "提弥明力尽战死。灵辄从伏甲中倒戈，在西门外接应赵盾。")
    end'''
    new = '''    if dog_defeated and not ti_fallen and game:is_unit_within("ZhaoDun47", {12,13}, 1) then
        ti_fallen = true
        game:generate_unit("LingZhe50", 1, Enum.force.ally, {10,13})
        ling_zhe_arrived = true
        game:push_cmd_speak(0, "赵盾已经穿过西门，提弥明转身留下断后。灵辄从伏甲中倒戈，在门外接应赵盾。")
    end'''
    if old not in text:
        raise RuntimeError(f"Taoyuan flow anchor missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


update(ROOT / "tools/apply_chapter50_updates.py")
update(ROOT / "game/sce/dongzhou/stage/50c.lua")
print("Taoyuan sacrifice now triggers when Zhao Dun crosses the west gate after Ling Ao falls.")
