from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT = Path(__file__).resolve().parents[1]
TITLE = "卢蒲癸计逐庆封 楚灵王大合诸侯"

HEROES = '''
        ,{ id = "LuPuGui67", class = "Cavalry", stat = {94,96,94,95,93}, model = "cavalry-1-red" }
        ,{ id = "GaoChai67", class = "Strategist", stat = {93,86,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "LuanZao67", class = "Strategist", stat = {92,87,96,93,91}, model = "Strategist-1-red" }
        ,{ id = "QingShe67", class = "Cavalry", stat = {92,98,88,94,91}, model = "cavalry-1-blue" }
        ,{ id = "QingSi67", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "QingYi67", class = "Cavalry", stat = {88,93,86,90,87}, model = "cavalry-1-blue" }
        ,{ id = "GongSunHei67", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-red" }
        ,{ id = "SiDai67", class = "Cavalry", stat = {90,95,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "YinDuan67", class = "Infantry", stat = {91,94,90,92,90}, model = "infantry-1-red" }
        ,{ id = "LiangXiao67", class = "Cavalry", stat = {93,96,94,94,91}, model = "cavalry-1-blue" }
        ,{ id = "QiCoalitionGuard67", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "QiCoalitionArcher67", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "QingTempleGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingCounterGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingCounterArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "ZhengGateGuard67", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ZhengGateArcher67", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "LiangHouseGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "LiangHouseArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }'''


def manifest(map_id: str, suffix: str) -> dict:
    return json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))


def head(chapter: str, battle: str, objective: str, asset: str, intro, victory, defeat, commanders, sites, events):
    return shared.stage_head("", TITLE, chapter, battle, objective, asset, intro, events, victory, defeat, commanders, sites)


def many_lua() -> str:
    return 'local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end\n'


def stage_a() -> str:
    data = manifest("m115", "ch67a")
    intro = [
        ("", "周灵王太子晋早逝，传说缑岭跨鹤升仙。灵王随后崩逝，次子贵即位，是为周景王；楚康王也在同年去世。"),
        ("", "齐相庆封独掌国政后日益荒淫，把政事交给儿子庆舍，自己长期住在卢蒲嫳家中。"),
        ("卢蒲嫳", "庆氏以为我只图酒色，却不知庄公之仇未雪。召我兄卢蒲癸回齐，才有内应。"),
        ("卢蒲癸", "我已让庆舍召回王何，又取得他的信任。高、栾、陈、鲍四族从外包围，卢蒲氏从内下手。"),
        ("", "齐景公御膳以鸭代鸡，高虿、栾灶以为庆氏刻减公膳，由此与庆舍公开结怨。"),
        ("高虿", "庆封与崔杼同弑庄公。崔氏已灭，庆氏尚在，今日正可为先君报仇。"),
        ("", "庆封率庆嗣、庆遗赴东莱田猎。陈无宇渡河后拆桥凿舟，断绝庆封归路。"),
        ("庆姜", "我故意警告庆舍不可参加尝祭，他刚愎自用，反而必定亲自入太庙。"),
        ("庆舍", "高虿、栾灶不过禽兽，即便真有伏兵，我一人也足以寝处之。"),
        ("军令", "第一阶段在太庙击退庆舍；第二阶段守住临淄西门，击退回援的庆封、庆嗣、庆遗。卢蒲癸、高虿、栾灶不得被击退。"),
    ]
    victory = [
        ("", "卢蒲癸从背后刺入庆舍胁下，王何以戈击断其左肩。庆舍投出俎壶，王何当场战死。"),
        ("", "庆舍抱住庙柱奋力摇撼，最终伤重而死。卢蒲癸随即杀庆绳，四姓甲士尽灭庆氏在城中的党羽。"),
        ("", "庆封闻讯反攻临淄西门，城中防守严密，部卒不断逃散。庆封与庆嗣、庆遗败走，转奔鲁国。"),
        ("晏婴", "诸臣为安社稷而诛庆氏，并非犯上。君上回宫，勿使城中再生混乱。"),
        ("", "鲁国迫于齐国压力不敢收留庆封，庆封又奔吴国。吴王夷昧将朱方封给他，庆氏表面更富，祸患却尚未结束。"),
        ("", "齐国发掘崔杼之柩陈尸于市，卢蒲嫳、卢蒲癸被放逐北燕。陈无宇不取庆氏财物，反而将木材施给百姓。"),
        ("军令", "太庙诛庆完成，获得1200金币。下一关：郑门讨伯有。"),
    ]
    text = head(
        "第六十七回·上", "太庙诛庆", "先诛庆舍，再击退从西门反攻的庆封父子。", "m115.png",
        intro, victory, "卢蒲癸、高虿、栾灶任一被击退，或超过二十八回合，失败。",
        ["LuPuGui67", "GaoChai67", "LuanZao67"],
        '{{id="qi_temple",name="齐国太庙",position={34,11},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="qi_palace",name="临淄宫署",position={48,14},restore_hp=20,restore_mp=15,rewards={}}}',
        [("卢蒲癸", "庙门已闭，四姓甲士一同动手！"), ("庆封", "庆舍已死，随我攻破西门夺回临淄！")],
    )
    rows = shared.terrain_block(data)
    return text + many_lua() + f'''local phase=1
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("LuPuBie66",1,Enum.force.ally,{{25,15}});game:generate_unit("QingShe67",1,Enum.force.enemy,{{34,11}})
 many(game,"QiCoalitionGuard67",{{{{27,15}},{{31,18}},{{38,18}},{{42,15}}}},Enum.force.own);many(game,"QiCoalitionArcher67",{{{{26,12}},{{42,12}}}},Enum.force.own)
 many(game,"QingTempleGuard67",{{{{31,9}},{{37,9}},{{30,12}},{{38,12}},{{33,16}},{{36,16}}}},Enum.force.enemy)
end
function on_update(game)
 if phase==1 and not game:has_unit("QingShe67")then phase=2;game:generate_unit("QingFeng62",1,Enum.force.enemy,{{3,20}});game:generate_unit("QingSi67",1,Enum.force.enemy,{{3,16}});game:generate_unit("QingYi67",1,Enum.force.enemy,{{3,25}});many(game,"QingCounterGuard67",{{{{1,18}},{{1,23}},{{4,18}},{{4,23}},{{6,16}},{{6,25}}}},Enum.force.enemy);many(game,"QingCounterArcher67",{{{{2,14}},{{2,27}},{{5,19}},{{5,22}}}},Enum.force.enemy);game:push_cmd_speak(0,"庆舍已死，王何也被俎壶击中身亡！庆封父子正在反攻临淄西门！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("QingFeng62") and not game:has_unit("QingSi67") and not game:has_unit("QingYi67")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="QiTempleCoup67",turn_limit=28,map={{blocked_edges={{}},size={{68,44}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{32,14}},hero="LuPuGui67"}},{{position={{29,16}},hero="GaoChai67"}},{{position={{38,16}},hero="LuanZao67"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=12000}}}}
'''


def stage_b() -> str:
    data = manifest("m116", "ch67b")
    intro = [
        ("", "齐国庆氏败亡后，高氏、栾氏相继专政。高竖据卢邑自保，闾邱婴许立高氏之后，兵乱未扩大成大战。"),
        ("", "郑国上卿良霄字伯有，奢侈嗜酒，常在地下酒室通宵饮宴，家臣有事也不得入见。"),
        ("公孙黑", "我与公孙楚争娶徐吾犯之妹，又被良霄强令出使楚国。既不肯见我，我便烧他的府第。"),
        ("", "公孙黑联合印段包围良府并纵火。良霄醉中被家臣扶上车，逃往雍梁。"),
        ("良霄", "国氏、罕氏没有参与拒绝良氏的盟约，他们必会助我。召集家甲，从郑国北门杀回去！"),
        ("驷带", "良霄误判国、罕两家态度。公孙黑命我与印段守住北门，不许叛军进入城中。"),
        ("印段", "家甲在前，弓手随后。先击破良氏随从，再围良霄，不可让他借夜色退回雍梁。"),
        ("公孙黑", "我留在城内坚守，不会主动出门。驷带、印段率军迎击。"),
        ("良霄", "我仍是郑国上卿。挡我归城者，皆是乱臣！"),
        ("军令", "击退全部良氏家甲与弓手，解除良霄保护后将其击退。驷带、印段任一被击退均失败。"),
    ]
    victory = [
        ("", "良霄在北门外战败，逃入屠羊之肆，被追兵杀死，随行家臣也全部战死。"),
        ("子产", "兄弟相攻，国之不幸。即便良霄有罪，也应收敛他与家臣的尸身，以礼安葬。"),
        ("", "罕虎拒绝执政，推举子产。子产整顿田制、乡伍与服章，抑制奢侈，又铸刑书、保留乡校议政。"),
        ("", "公孙黑继续乱政，最终被子产依法处死。郑人后来传说良霄为厉，子产为良氏立后，流言才平息。"),
        ("", "蔡世子般弑父自立；宋宫大火，伯姬因傅母未到而不肯下堂，最终葬身火海。晋国只救宋灾而不讨蔡乱，霸业由此衰落。"),
        ("", "虢地会盟时，楚公子围僭用国君仪仗。子产不许楚军带兵入郑，公子围只能卸下弓矢完成迎亲。"),
        ("", "公子围归楚后勒死郏敖，又杀幕、平夏，自立为楚灵王；随后向晋国索取诸侯会盟与婚姻，列国不敢违抗。"),
        ("军令", "郑门讨伯有完成，获得900金币。第六十七回结束。"),
    ]
    text = head(
        "第六十七回·下", "郑门讨伯有", "守住郑国北门，击破良氏家甲并击退良霄。", "m116.png",
        intro, victory, "驷带、印段任一被击退，或超过二十二回合，失败。",
        ["SiDai67", "YinDuan67"],
        '{{id="zheng_west",name="郑城西署",position={18,28},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}},{id="zheng_palace",name="郑国宫署",position={30,30},restore_hp=25,restore_mp=15,rewards={}},{id="zheng_east",name="郑城东署",position={43,28},restore_hp=20,restore_mp=10,rewards={}}}',
        [("驷带", "良氏家甲已经逼近北门，列阵迎敌！"), ("良霄", "家甲尽失也挡不住我，随我冲入郑城！")],
    )
    rows = shared.terrain_block(data)
    return text + many_lua() + f'''local liang_exposed=false
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("GongSunHei67",1,Enum.force.ally,{{30,25}});game:generate_unit("LiangXiao67",1,Enum.force.enemy,{{30,7}});game:set_unit_invulnerable("LiangXiao67",true)
 many(game,"ZhengGateGuard67",{{{{24,20}},{{28,20}},{{33,20}},{{37,20}},{{26,24}},{{35,24}}}},Enum.force.own);many(game,"ZhengGateArcher67",{{{{22,22}},{{39,22}},{{28,26}},{{33,26}}}},Enum.force.own)
 many(game,"LiangHouseGuard67",{{{{25,8}},{{28,10}},{{33,10}},{{36,8}},{{23,12}},{{38,12}},{{27,14}},{{34,14}}}},Enum.force.enemy);many(game,"LiangHouseArcher67",{{{{24,6}},{{36,6}},{{25,15}},{{37,15}}}},Enum.force.enemy)
end
function on_update(game)
 if not liang_exposed and not game:has_unit("LiangHouseGuard67") and not game:has_unit("LiangHouseArcher67")then liang_exposed=true;game:set_unit_invulnerable("LiangXiao67",false);game:push_cmd_speak(0,"良氏家甲已经全灭！良霄败势已成，截住他通往屠羊肆的退路！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if liang_exposed and not game:has_unit("LiangXiao67")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="BoyouRebellion67",turn_limit=22,map={{blocked_edges={{}},size={{62,42}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{27,21}},hero="SiDai67"}},{{position={{34,21}},hero="YinDuan67"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=9000}}}}
'''


def patch_all() -> None:
    for stage_id, text in (("67a", stage_a()), ("67b", stage_b())):
        (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").write_text(text, encoding="utf-8")

    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    if 'id = "LuPuGui67"' not in text:
        text = text.replace(
            '        ,{ id = "ZhengGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }    },',
            '        ,{ id = "ZhengGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }' + HEROES + '    },',
        )
    text = text.replace('"66c", "66d", "66e" }', '"66c", "66d", "66e", "67a", "67b" }')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("STAGE_TABLE_VERSION = 10", "STAGE_TABLE_VERSION = 11")
    text = text.replace('"66a","66b","66c","66d","66e"\n)', '"66a","66b","66c","66d","66e","67a","67b"\n)')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m115.png"]' not in text:
        block = '''
_LARGE_BATTLE_MAPS["m115.png"]=(68,44,48)
_LARGE_BATTLE_MAPS["m116.png"]=(62,42,48)
HERO_LABELS.update({"LuPuGui67":"卢蒲癸","GaoChai67":"高虿","LuanZao67":"栾灶","QingShe67":"庆舍","QingSi67":"庆嗣","QingYi67":"庆遗","GongSunHei67":"公孙黑","SiDai67":"驷带","YinDuan67":"印段","LiangXiao67":"良霄","QiCoalitionGuard67":"齐国四姓甲士","QiCoalitionArcher67":"齐国四姓弓手","QingTempleGuard67":"庆氏庙卫","QingCounterGuard67":"庆氏回援甲士","QingCounterArcher67":"庆氏回援弓手","ZhengGateGuard67":"郑国门卫","ZhengGateArcher67":"郑国守城弓手","LiangHouseGuard67":"良氏家甲","LiangHouseArcher67":"良氏弓手"})
HERO_BIOS.update({"LuPuGui67":"齐国勇士，为报齐庄公之仇潜入庆氏，太庙尝祭时从背后刺杀庆舍。","GaoChai67":"齐国大夫，字子尾，联合栾、陈、鲍诸族围攻太庙，驱逐庆封。","LuanZao67":"齐国大夫，字子雅，与高虿共同反对庆氏专政，参与太庙之变。","QingShe67":"庆封之子，力大勇猛而刚愎，太庙尝祭时被卢蒲癸、王何合击而死。","QingSi67":"庆封族人，随庆封赴东莱田猎，临淄事变后参与西门反攻。","QingYi67":"庆封族人，随庆封出猎并参与西门反攻，失败后随庆氏逃亡。","GongSunHei67":"郑国大夫，与良霄冲突并焚毁良府，后来继续乱政，被子产依法处死。","SiDai67":"公孙黑之侄，奉命与印段守卫郑国北门，击败返攻的良霄。","YinDuan67":"郑国大夫，与驷带共同率勇士在北门迎击良氏家甲。","LiangXiao67":"郑国上卿，字伯有，奢侈嗜酒；良府被焚后返攻北门，战败被杀。"})
PORTRAIT_INDEX_BY_HERO.update({"LuPuGui67":35,"GaoChai67":49,"LuanZao67":49,"QingShe67":34,"QingSi67":35,"QingYi67":34,"GongSunHei67":35,"SiDai67":35,"YinDuan67":34,"LiangXiao67":49})
SPEAKER_PORTRAIT_INDEX.update({"卢蒲癸":35,"卢蒲嫳":49,"高虿":49,"庆姜":27,"庆舍":34,"庆封":38,"晏婴":49,"公孙黑":35,"良霄":49,"驷带":35,"印段":34,"子产":49})
HISTORICAL_DEATH_HEROES.update({"QingShe67","LiangXiao67"})
'''
        text = text.replace('\nif _original_name == "__main__":', block + '\nif _original_name == "__main__":')
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_all()
    print("chapter 67 integrated: 67a-67b")
