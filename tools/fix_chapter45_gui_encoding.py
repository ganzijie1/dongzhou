from pathlib import Path


path = Path(r"C:\mengde\rl\play_gui.py")
text = path.read_text(encoding="utf-8")
start_marker = '_LARGE_BATTLE_MAPS["m068.png"] = (44, 28, 48)'
end_marker = 'if _original_name == "__main__":'
start = text.index(start_marker)
end = text.index(end_marker, start)

block = '''_LARGE_BATTLE_MAPS["m068.png"] = (44, 28, 48)
_LARGE_BATTLE_MAPS["m069.png"] = (36, 26, 48)

HERO_LABELS.update({
    "JinXiangGong45": "晋襄公", "XianQieJu45": "先且居", "TuJi45": "屠击",
    "XuYing45": "胥婴", "HuJuJu45": "狐鞫居", "HanZiYu45": "韩子舆",
    "LiangHong45": "梁弘", "LaiJu45": "莱驹", "LangTan45": "狼瞫",
    "LuanDun45": "栾盾", "XiQue45": "郤缺", "BaiBuHu45": "白部胡",
    "JinGuard45": "晋军甲士", "JinArcher45": "晋军弓手",
    "QinGuard45": "秦军甲士", "QinCavalry45": "秦军骑兵", "QinArcher45": "秦军弓手",
    "DiCavalry45": "翟军骑兵", "DiArcher45": "翟军射手",
})
HERO_BIOS.update({
    "JinXiangGong45": "晋文公之子。即位后墨染丧服亲征，在崤山全歼秦军；能容先轸面斥之失，继续委以军政。",
    "XianQieJu45": "先轸之子，晋国将领。崤山伏左山截击秦军，箕城之战又担任先锋，诈败诱白部胡进入大谷。",
    "TuJi45": "晋国将领。崤山战与先且居率左翼伏兵，见红旗后从山腰突击秦军。",
    "XuYing45": "晋国将领。崤山战与狐鞫居率右翼伏兵，截断秦军侧面通路。",
    "HuJuJu45": "晋国狐氏将领。崤山伏击负责右翼，后又参加箕城御翟，协助封锁大谷退路。",
    "HanZiYu45": "晋国将领。崤山战随狐射姑伏于西口，以弓军和断木封住秦军归路。",
    "LiangHong45": "晋国将领。崤山伏于东口，待秦军全部入谷后封闭后路。",
    "LaiJu45": "晋国勇将。崤山东口遇褒蛮子，依伏击号令暂时放其深入，随后参加合围。",
    "LangTan45": "晋国勇士。崤山斩杀挣缚夺马的褒蛮子；箕城战不因先锋被换而怀怨，以战死证明勇烈。",
    "LuanDun45": "晋国将领。箕城御翟时伏于大谷左翼，待白部胡深入后出击。",
    "XiQue45": "晋国郤氏贤将。箕城战伏于大谷右翼，一箭射杀白部胡，后成为晋国重要卿士。",
    "BaiBuHu45": "白部翟首领，越箕城侵晋，追击先且居进入大谷，被郤缺一箭射中面门而死。",
    "JinGuard45": "参加崤山伏击与箕城御翟的晋国甲士。",
    "JinArcher45": "埋伏在山腰、林缘，负责封锁谷道的晋军弓手。",
    "QinGuard45": "随秦国三帅袭郑、破滑后携带缴获西归的秦军甲士。",
    "QinCavalry45": "困在崤山狭谷、首尾不能相救的秦军骑兵。",
    "QinArcher45": "随秦军辎重队进入崤山的弓手。",
    "DiCavalry45": "跟随白部胡越过箕城、追入大谷的翟军骑兵。",
    "DiArcher45": "跟随白部胡侵晋的翟军射手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "JinXiangGong45": 6, "XianQieJu45": 24, "TuJi45": 49, "XuYing45": 35,
    "HuJuJu45": 25, "HanZiYu45": 17, "LiangHong45": 34, "LaiJu45": 20,
    "LangTan45": 13, "LuanDun45": 45, "XiQue45": 37, "BaiBuHu45": 7,
})
SPEAKER_PORTRAIT_INDEX.update({
    "晋襄公": 6, "先且居": 24, "屠击": 49, "胥婴": 35, "狐鞫居": 25,
    "韩子舆": 17, "梁弘": 34, "莱驹": 20, "狼瞫": 13, "栾盾": 45,
    "郤缺": 37, "白部胡": 7, "文嬴": 18, "阳处父": 35, "白屯": 7,
})
HISTORICAL_DEATH_HEROES.update({"BaoManZi44", "BaiBuHu45", "XianZhen27"})

'''

updated = text[:start] + block + text[end:]
path.write_text(updated, encoding="utf-8", newline="")
print("Rewrote chapter45 GUI block as UTF-8.")
