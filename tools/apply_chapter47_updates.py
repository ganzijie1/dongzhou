from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_config():
    path = ROOT / "game/sce/dongzhou/config.lua"
    hero_block = '''        ,{ id = "ShuSunDeChen47", class = "Lord", stat = {86, 90, 88, 88, 86}, model = "lord-1-red" }
        ,{ id = "FuFuZhongSheng47", class = "Strategist", stat = {82, 88, 94, 92, 90}, model = "Strategist-1-red" }
        ,{ id = "QiaoRu47", class = "Infantry", stat = {92, 98, 70, 90, 86}, model = "infantry-1-blue" }
        ,{ id = "LuGuard47", class = "Infantry", stat = {83, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "LuArcher47", class = "Archer", stat = {81, 86, 84, 84, 82}, model = "archer-1-red" }
        ,{ id = "DiGuard47", class = "Infantry", stat = {83, 89, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "DiCavalry47", class = "Cavalry", stat = {85, 91, 78, 85, 83}, model = "cavalry-1-blue" }
        ,{ id = "DiArcher47", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-blue" }
        ,{ id = "ZhaoDun47", class = "Strategist", stat = {92, 88, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "XianKe47", class = "Cavalry", stat = {86, 92, 84, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "XunLinFu47", class = "Cavalry", stat = {88, 90, 94, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "XianDu47", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "GongZiYong47", class = "Lord", stat = {88, 86, 90, 88, 86}, model = "lord-1-blue" }
        ,{ id = "XianMie47", class = "Strategist", stat = {84, 82, 92, 90, 88}, model = "Strategist-1-blue" }
        ,{ id = "ShiHui47", class = "Strategist", stat = {90, 86, 98, 96, 94}, model = "Strategist-1-blue" }
        ,{ id = "JinGuard47", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-red" }
        ,{ id = "JinCavalry47", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinArcher47", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "QinGuard47", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "QinCavalry47", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "QinArcher47", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", hero_block + "    },\n    equipments = {},")
    replace_once(path, '"46a", "46b", "46c" }', '"46a", "46b", "46c", "47a", "47b" }')


def update_gui():
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m073.png"] = (36, 26, 48)
_LARGE_BATTLE_MAPS["m074.png"] = (42, 28, 48)

HERO_LABELS.update({
    "ShuSunDeChen47": "叔孙得臣", "FuFuZhongSheng47": "富父终甥", "QiaoRu47": "侨如",
    "LuGuard47": "鲁军甲士", "LuArcher47": "鲁军弓手",
    "DiGuard47": "翟军甲士", "DiCavalry47": "翟军骑兵", "DiArcher47": "翟军射手",
    "ZhaoDun47": "赵盾", "XianKe47": "先克", "XunLinFu47": "荀林父", "XianDu47": "先都",
    "GongZiYong47": "公子雍", "XianMie47": "先蔑", "ShiHui47": "士会",
    "JinGuard47": "晋军甲士", "JinCavalry47": "晋军骑兵", "JinArcher47": "晋军弓手",
    "QinGuard47": "秦军甲士", "QinCavalry47": "秦军骑兵", "QinArcher47": "秦军弓手",
})
HERO_BIOS.update({
    "ShuSunDeChen47": "鲁国卿大夫。长翟侨如侵鲁时统兵迎战，采纳富父终甥的雪夜陷坑之计，杀散翟军并载回侨如巨尸。",
    "FuFuZhongSheng47": "鲁国大夫。预判夜间降雪，以草蓐浮土掩盖陷坑，诈败诱侨如追赶，待其坠坑后持戈刺喉。",
    "QiaoRu47": "翟国长人，身高一丈五尺，力举千钧，人称长翟。受白暾之命侵鲁，追敌时坠入雪坑，被富父终甥刺死。",
    "ZhaoDun47": "赵衰之子，晋国正卿。先迎公子雍，后迫于穆嬴改立夷皋，并率晋军夜袭令狐秦营。",
    "XianKe47": "先且居之子，晋军将领。令狐之战担任赵盾中军副将，后因部将蒯得贪进失车而依法处分。",
    "XunLinFu47": "晋国将领。曾预言迎雍之事将变；令狐之战独领上军，战后又为先蔑、士会送还家眷财物。",
    "XianDu47": "晋国将领，先蔑族人。令狐之战独领下军参与夜袭，后因不满赵盾专权而卷入晋国内乱。",
    "GongZiYong47": "晋文公庶子，母为贤德的杜祁，在秦任亚卿。被晋卿迎立又遭背弃，最终死于令狐夜袭乱军。",
    "XianMie47": "晋国下军元帅，字士伯。奉命入秦迎公子雍，赵盾改立灵公后仍不肯背弃使命，战后留秦为臣。",
    "ShiHui47": "晋国大夫，又称随会、士季。随先蔑迎公子雍，令狐兵败后与先蔑一同留秦，后来成为晋国名臣。",
    "LuGuard47": "埋伏在雪地陷坑两侧、等候长翟深入的鲁国甲士。",
    "LuArcher47": "依托雪原林缘封锁翟军退路的鲁军弓手。",
    "DiGuard47": "随长翟侨如侵入鲁境的翟军甲士。",
    "DiCavalry47": "追击富父终甥诱敌部队的翟军骑兵。",
    "DiArcher47": "在雪夜为侨如前队提供远射掩护的翟军射手。",
    "JinGuard47": "衔枚潜行、从东门突入令狐秦营的晋军甲士。",
    "JinCavalry47": "负责冲散秦营车阵并向刳首追击的晋军骑兵。",
    "JinArcher47": "在营门与外围压制仓促迎战秦军的晋军弓手。",
    "QinGuard47": "护送公子雍返晋、夜宿令狐营寨的秦军甲士。",
    "QinCavalry47": "秦康公拨给公子雍的车骑护卫，遭晋军三更突袭。",
    "QinArcher47": "令狐营中来不及完成列阵的秦军弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ShuSunDeChen47": 24, "FuFuZhongSheng47": 49, "QiaoRu47": 34,
    "ZhaoDun47": 42, "XianKe47": 35, "XunLinFu47": 37, "XianDu47": 25,
    "GongZiYong47": 7, "XianMie47": 40, "ShiHui47": 31,
})
SPEAKER_PORTRAIT_INDEX.update({
    "弄玉": 18, "萧史": 31, "秦康公": 7, "臾骈": 49, "狐射姑": 45,
    "叔孙得臣": 24, "富父终甥": 49, "侨如": 34, "赵盾": 42,
    "先克": 35, "荀林父": 37, "先都": 25, "公子雍": 7,
    "先蔑": 40, "士会": 31, "穆嬴": 18,
})
HISTORICAL_DEATH_HEROES.update({"QiaoRu47", "GongZiYong47"})

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def main():
    update_config()
    update_gui()
    print("Chapter 47 config and GUI registration updated.")


if __name__ == "__main__":
    main()
