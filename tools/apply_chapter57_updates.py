import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main():
    manifest = json.loads((ROOT / "assets/lzc/map_sources/m091_ch57_manifest.json").read_text(encoding="utf-8"))
    rows = "\n" + "\n".join(f'        "{row}",' for row in manifest["terrain_rows"]) + "\n    "
    replace_once(ROOT / "game/sce/dongzhou/stage/57.lua", " __ROWS__ ", rows)

    config = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "PalaceDoctor57", class = "Strategist", stat = {76, 66, 92, 90, 88}, model = "Strategist-1-red" }
        ,{ id = "PalaceSearchGuard57", class = "Infantry", stat = {88, 93, 82, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "PalaceSearchArcher57", class = "Archer", stat = {86, 91, 86, 89, 87}, model = "archer-1-blue" }
'''
    replace_once(config, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(config, '"55a", "55b", "56a", "56b" }', '"55a", "55b", "56a", "56b", "57" }')

    gui = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m091.png"] = (48, 32, 48)
HERO_LABELS.update({"PalaceDoctor57":"医者","PalaceSearchGuard57":"宫中搜卒","PalaceSearchArcher57":"宫中弓卫"})
HERO_BIOS.update({
    "PalaceDoctor57":"韩厥亲信，乔装医者，以药囊藏匿赵武穿越宫门搜查线，将赵氏孤儿安全送出宫城。",
    "PalaceSearchGuard57":"奉屠岸贾之命搜查宫城的晋国甲士；被击退按撤退处理，不计作史实阵亡。",
    "PalaceSearchArcher57":"封锁宫中大道与东门的晋国弓卫；被击退按撤退处理，不计作史实阵亡。",
})
PORTRAIT_INDEX_BY_HERO.update({"PalaceDoctor57":45})
SPEAKER_PORTRAIT_INDEX.update({
    "国佐":49,"郤克":37,"季孙行父":42,"孙良夫":35,"夏姬":12,"屈巫":45,"楚共王":8,
    "屠岸贾":45,"韩厥":42,"赵朔":35,"赵庄姬":12,"公孙杵臼":31,"程婴":49,"医者":45,
})

'''
    replace_once(gui, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')

    prior = ROOT / "rl/chapter56_test.py"
    replace_once(prior, 'assert \'"55a", "55b", "56a", "56b" }\'in c',
                 'assert \'"55a", "55b", "56a", "56b", "57" }\'in c')
    print("Chapter 57 integrated.")


if __name__ == "__main__":
    main()
