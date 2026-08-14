import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def replace_once(path, old, new):
    path = Path(path); text = path.read_text(encoding="utf-8")
    if old not in text: raise RuntimeError(f"anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def inject_rows(stage, manifest):
    data = json.loads((ROOT / "assets/lzc/map_sources" / manifest).read_text(encoding="utf-8"))
    value = "\n" + "\n".join(f'        "{row}",' for row in data["terrain_rows"]) + "\n    "
    replace_once(ROOT / "game/sce/dongzhou/stage" / stage, " __ROWS__ ", value)

def main():
    inject_rows("54a.lua", "m085_ch54a_manifest.json"); inject_rows("54b.lua", "m086_ch54b_manifest.json")
    config = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "XunYing54", class = "Cavalry", stat = {87, 92, 91, 90, 89}, model = "cavalry-1-blue" }
        ,{ id = "XunShou54", class = "Archer", stat = {91, 96, 92, 94, 92}, model = "archer-1-red" }
        ,{ id = "WeiQi54", class = "Cavalry", stat = {87, 93, 84, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "XiangLao54", class = "Cavalry", stat = {88, 93, 86, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "GongZiGuChen54", class = "Cavalry", stat = {87, 92, 87, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "ChuBiGuard54", class = "Infantry", stat = {89, 94, 87, 91, 89}, model = "infantry-1-red" }
        ,{ id = "ChuBiCavalry54", class = "Cavalry", stat = {90, 95, 86, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "ChuBiArcher54", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-red" }
        ,{ id = "JinCenterGuard54", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "JinCenterCavalry54", class = "Cavalry", stat = {89, 94, 85, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "JinCenterArcher54", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-blue" }
        ,{ id = "XunFamilyGuard54", class = "Infantry", stat = {87, 93, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinReturnArcher54", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-red" }
        ,{ id = "ChuSalvageGuard54", class = "Infantry", stat = {86, 91, 84, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "ChuSalvageCavalry54", class = "Cavalry", stat = {87, 92, 84, 89, 87}, model = "cavalry-1-blue" }
'''
    replace_once(config, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(config, '"52", "53a", "53b" }', '"52", "53a", "53b", "54a", "54b" }')
    gui = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m085.png"] = (58, 36, 48)
_LARGE_BATTLE_MAPS["m086.png"] = (52, 34, 48)
HERO_LABELS.update({"XunYing54":"荀罃","XunShou54":"荀首","WeiQi54":"魏锜","XiangLao54":"襄老","GongZiGuChen54":"公子谷臣","ChuBiGuard54":"楚中军甲士","ChuBiCavalry54":"楚中军战骑","ChuBiArcher54":"楚中军强弓","JinCenterGuard54":"晋中军甲士","JinCenterCavalry54":"晋中军战骑","JinCenterArcher54":"晋中军弓手","XunFamilyGuard54":"荀氏家兵","JinReturnArcher54":"晋军弓手","ChuSalvageGuard54":"楚军收车卒","ChuSalvageCavalry54":"楚军巡骑"})
HERO_BIOS.update({"XunYing54":"晋国荀氏将领，荀首之子。邲之战被熊负羁生擒，后由父亲以楚国俘虏交换归晋。","XunShou54":"晋国下军大夫，善射。邲战败退后为救子折返楚军，射杀襄老并生擒谷臣。","WeiQi54":"晋国将领。邲战前擅自赴楚挑战，败退时协助荀首生擒公子谷臣。","XiangLao54":"楚国连尹。邲战后收取晋军遗车，被折返的荀首一箭射杀。","GongZiGuChen54":"楚国王族将领。救援襄老时被射伤右腕、魏锜生擒，后用于交换荀罃。"})
PORTRAIT_INDEX_BY_HERO.update({"XunYing54":35,"XunShou54":37,"WeiQi54":33,"XiangLao54":34,"GongZiGuChen54":38})
SPEAKER_PORTRAIT_INDEX.update({"荀林父":37,"士会":31,"先谷":35,"韩厥":45,"栾书":42,"乐伯":34,"鲍癸":38,"孙叔敖":45,"潘党":33,"楚庄王":8,"荀首":37,"魏锜":33,"孙安":31})
HISTORICAL_DEATH_HEROES.add("XiangLao54")

'''
    replace_once(gui, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')
    prior = ROOT / "rl/chapter53_test.py"
    replace_once(prior, 'assert \'"50c", "51", "52", "53a", "53b" }\' in config', 'assert \'"50c", "51", "52", "53a", "53b", "54a", "54b" }\' in config')
    print("Chapter 54 integrated.")

if __name__ == "__main__": main()
