from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT = Path(__file__).resolve().parents[1]

HEROES = '''
        ,{ id = "HanQi62", class = "Strategist", stat = {95,90,99,96,95}, model = "Strategist-1-red" }
        ,{ id = "WeiJiang62", class = "Cavalry", stat = {93,96,92,94,93}, model = "cavalry-1-red" }
        ,{ id = "ZhouChuo62", class = "Cavalry", stat = {90,96,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "LuanYing62", class = "Cavalry", stat = {91,95,90,93,91}, model = "cavalry-1-red" }
        ,{ id = "QiLingGong62", class = "Lord", stat = {91,89,88,89,86}, model = "lord-1-blue" }
        ,{ id = "XiGuiFu62", class = "Cavalry", stat = {91,95,90,92,90}, model = "cavalry-1-blue" }
        ,{ id = "ZhiChuo62", class = "Cavalry", stat = {90,96,88,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GuoZui62", class = "Cavalry", stat = {89,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "CuiZhu62", class = "Strategist", stat = {94,87,98,95,92}, model = "Strategist-1-blue" }
        ,{ id = "QingFeng62", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "QiCoalitionGuard62", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-blue" }
        ,{ id = "QiCoalitionArcher62", class = "Archer", stat = {88,94,92,91,90}, model = "archer-1-blue" }
        ,{ id = "JinCoalitionGuard62", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher62", class = "Archer", stat = {88,94,92,91,90}, model = "archer-1-red" }
        ,{ id = "QiZhuangGong62", class = "Lord", stat = {94,95,91,94,92}, model = "lord-1-red" }
        ,{ id = "GongLou62", class = "Infantry", stat = {87,90,90,89,91}, model = "infantry-1-red" }
        ,{ id = "SuShaWei62", class = "Cavalry", stat = {90,94,86,90,87}, model = "cavalry-1-blue" }
        ,{ id = "GaotangGuard62", class = "Infantry", stat = {88,93,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "GaotangArcher62", class = "Archer", stat = {87,92,89,90,88}, model = "archer-1-blue" }
        ,{ id = "ShuHu62", class = "Cavalry", stat = {89,94,85,90,87}, model = "cavalry-1-blue" }
        ,{ id = "JiYi62", class = "Infantry", stat = {88,93,84,89,87}, model = "infantry-1-blue" }
        ,{ id = "HuangYuan62", class = "Cavalry", stat = {88,93,85,89,87}, model = "cavalry-1-blue" }
        ,{ id = "XunWu62", class = "Cavalry", stat = {92,95,93,93,92}, model = "cavalry-1-red" }
        ,{ id = "JinArrestGuard62", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }'''


def manifest(mid: str, suffix: str) -> dict:
    return json.loads((ROOT / f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))


def head(chapter, title, battle, objective, asset, intro, victory, defeat, commanders, sites, events):
    return shared.stage_head("", title, chapter, battle, objective, asset, intro, events, victory, defeat, commanders, sites)


def stage_a() -> str:
    d = manifest("m101", "ch62a")
    intro = [
        ("", "卫献公奔齐以后，齐灵公自恃国强，欲争诸侯之长；晋悼公卒，晋平公新立，诸卿决定以大军伐齐。"),
        ("", "晋会鲁、宋、卫、郑、曹、莒、邾、滕、薛、杞、小邾等国，合为十二国之师，兵锋直指齐境。"),
        ("荀偃", "齐军在防门掘沟拒守。先夺沟西阵地，再填出通路，全军不得分散涉险。"),
        ("士匄", "防门一破，析归父必退平阴；平阴若失，齐军会沿石门狭道撤向临淄。"),
        ("赵武", "此役不以弑君为功。齐灵公守临淄，列国只焚外郭、围城示威，不攻宫城。"),
        ("韩起", "十二国旗号虽多，军令只出中军。盟军守住两翼，我军连续推进三个战区。"),
        ("析归父", "防门深沟尚在，晋军纵有千乘，也休想整阵渡过。弓手压住填沟之处！"),
        ("殖绰", "若平阴不守，我与郭最退到石门。那里山道狭窄，追兵未必能展开。"),
        ("齐灵公", "寡人据临淄坚城，诸侯远来，粮尽自退。崔杼、庆封整顿外郭，不可擅出。"),
        ("军令", "击退析归父，穿过平阴；在石门击退并俘获殖绰、郭最；最后抵达临淄西门，坚持围城六回合。"),
    ]
    victory = [
        ("", "诸侯军越过防门，平阴齐军败退。析归父失守关隘，齐境再无完整的野战防线。"),
        ("", "殖绰、郭最据石门拒战，周绰率锐士追及，将二人击败俘获，押入晋军。"),
        ("荀偃", "临淄城墙坚固，不必强攻宫城。分兵焚毁外郭积聚，使齐国知惧即可。"),
        ("", "联军围临淄六日，火光照城。郑国急报国内有变，诸侯军遂停止攻城，班师回国。"),
        ("", "荀偃出师前梦见先父责己，回军后果然病重而卒；殖绰、郭最后来乘隙逃归齐国。"),
        ("", "同年楚军出师遇大雪，冻死者众；师旷听南风不竞，断言楚军无功，晋国北方暂安。"),
        ("", "齐灵公不久病危，崔杼迎故太子光为齐庄公；高厚及荣子、公子牙皆死于内乱。"),
        ("军令", "十二国伐齐完成，获得1500金币。下一关：高唐平叛。"),
    ]
    text = head("第六十二回·上", "诸侯同心围齐国 晋臣合力逐栾盈", "十二国伐齐", "突破防门、石门追俘，围临淄六回合后撤军。", "m101.png", intro, victory,
                "荀偃、士匄、赵武任一被击退，或超过四十回合，战役失败。", ["XunYan58", "ShiGai60", "ZhaoWu59"],
                '{{id="pingyin",name="平阴城",position={42,20},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="linzi_palace",name="临淄城",position={76,13},restore_hp=25,restore_mp=20,rewards={}},{id="linzi_store",name="临淄武库",position={78,30},restore_hp=20,restore_mp=10,rewards={}}}',
                [("析归父", "填沟处失守，全军退往平阴！"), ("周绰", "石门追兵已至，殖绰、郭最还不下马受缚！"), ("荀偃", "围城第六日，郑国有急，诸侯军依令撤退。")])
    rows = shared.terrain_block(d)
    return text + f'''local phase=1 local siege_turn=-1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("HanQi62",1);game:appoint_hero("WeiJiang62",1);game:appoint_hero("ZhouChuo62",1);game:appoint_hero("LuanYing62",1)end
function on_begin(game)
game:generate_unit("XiGuiFu62",1,Enum.force.enemy,{{31,28}});game:generate_unit("ZhiChuo62",1,Enum.force.enemy,{{61,25}});game:generate_unit("GuoZui62",1,Enum.force.enemy,{{61,28}});game:set_unit_invulnerable("ZhiChuo62",true);game:set_unit_invulnerable("GuoZui62",true)
game:generate_unit("QiLingGong62",1,Enum.force.enemy,{{76,13}});game:set_unit_invulnerable("QiLingGong62",true);game:generate_unit("CuiZhu62",1,Enum.force.enemy,{{71,23}});game:generate_unit("QingFeng62",1,Enum.force.enemy,{{72,28}})
many(game,"QiCoalitionGuard62",{{{{22,23}},{{22,27}},{{22,31}},{{30,24}},{{30,26}},{{30,30}},{{37,23}},{{37,27}},{{46,22}},{{46,28}},{{57,23}},{{57,30}},{{70,20}},{{70,26}},{{74,34}},{{80,33}}}},Enum.force.enemy)
many(game,"QiCoalitionArcher62",{{{{23,20}},{{23,34}},{{32,23}},{{32,33}},{{40,18}},{{44,31}},{{58,20}},{{59,32}},{{73,18}},{{75,37}}}},Enum.force.enemy)
many(game,"JinCoalitionGuard62",{{{{7,27}},{{7,30}},{{14,23}},{{14,33}}}},Enum.force.own);many(game,"JinCoalitionArcher62",{{{{9,21}},{{9,37}},{{16,25}},{{16,31}}}},Enum.force.own)
end
function on_update(game)
if phase==1 and not game:has_unit("XiGuiFu62")then phase=2;game:push_cmd_speak(0,"防门已破，析归父退走！诸军穿过平阴，继续向石门追击。");game:set_unit_invulnerable("ZhiChuo62",false);game:set_unit_invulnerable("GuoZui62",false)end
if phase==2 and not game:has_unit("ZhiChuo62") and not game:has_unit("GuoZui62")then phase=3;game:push_cmd_speak(0,"殖绰、郭最已在石门被俘。中军向临淄西门推进，不可攻击齐侯宫城。");end
if phase==3 and game:is_unit_within("XunYan58",{{68,24}},3)then phase=4;siege_turn=game:get_turn_current();game:push_cmd_speak(0,"临淄合围。自本回合起围城六日，焚外郭而不攻宫城。");end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==4 and game:get_turn_current()>=siege_turn+6 then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="QiCampaign62",turn_limit=40,map={{blocked_edges={{}},size={{86,56}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{12,25}},hero="XunYan58"}},{{position={{10,28}},hero="ShiGai60"}},{{position={{12,31}},hero="ZhaoWu59"}},{{position={{8,24}},hero="HanQi62"}},{{position={{8,32}},hero="WeiJiang62"}},{{position={{15,28}},hero="ZhouChuo62"}},{{position={{10,35}},hero="LuanYing62"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=15000}}}}
'''


def stage_b() -> str:
    d = manifest("m102", "ch62b")
    intro = [
        ("", "齐庄公即位后，肃沙卫据高唐反叛。齐军围攻一个多月，城墙坚固，始终不能攻入。"),
        ("齐庄公", "高唐久攻不下，强攻只会损兵。谁能在城中寻得内应，打开一处缺口？"),
        ("", "高唐工匠公娄暗中登上东北城角，以灯火为号，垂下绳索接引齐军。"),
        ("殖绰", "我与郭最从东北角缒城。主力仍在南门列阵，莫让肃沙卫察觉真正突破处。"),
        ("郭最", "入城后先夺东北城角，再直取肃沙卫。得手便开南门，接应庄公大军。"),
        ("公娄", "绳索已系牢。城角守军换班只有片刻，两位将军速下，不可点火。"),
        ("肃沙卫", "高唐粮足城坚，齐军围上数月也无用。东北角只留少数巡兵即可。"),
        ("军令", "殖绰或郭最抵达东北绳索格后解除肃沙卫保护；击退肃沙卫即完成夜袭。"),
    ]
    victory = [
        ("", "殖绰、郭最循绳登上高唐东北城角，击散守卒，公娄立即引二人直趋城中。"),
        ("肃沙卫", "东北角为何有喊杀声？快调南门守军回城，堵住通往府署的街道！"),
        ("", "肃沙卫被擒，南门随即打开。齐庄公率军入城，高唐一个多月的叛乱就此平定。"),
        ("齐庄公", "公娄冒险为内应，殖绰、郭最先登破城，皆当记功。肃沙卫按叛臣治罪。"),
        ("", "肃沙卫被处死。齐庄公由此稳住君位，齐国暂与晋国在澶渊讲和。"),
        ("军令", "高唐平叛完成，获得900金币。下一关：叔虎府之围。"),
    ]
    text = head("第六十二回·中", "诸侯同心围齐国 晋臣合力逐栾盈", "高唐平叛", "利用东北城角绳索潜入高唐，击退肃沙卫。", "m102.png", intro, victory,
                "齐庄公、殖绰、郭最任一被击退，或超过二十八回合，战役失败。", ["QiZhuangGong62", "ZhiChuo62", "GuoZui62"],
                '{{id="gaotang_palace",name="高唐府署",position={29,11},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="gaotang_store",name="高唐武库",position={39,18},restore_hp=20,restore_mp=10,rewards={}}}',
                [("公娄", "东北城角灯号已明，绳索垂下！"), ("郭最", "城角已破，转身开南门！")])
    rows = shared.terrain_block(d)
    return text + f'''local rope_open=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("GongLou62",1,Enum.force.ally,{{46,8}});game:generate_unit("SuShaWei62",1,Enum.force.enemy,{{29,11}});game:set_unit_invulnerable("SuShaWei62",true);many(game,"GaotangGuard62",{{{{45,7}},{{45,10}},{{42,14}},{{35,16}},{{30,22}},{{24,16}},{{20,25}},{{29,32}},{{31,32}}}},Enum.force.enemy);many(game,"GaotangArcher62",{{{{43,9}},{{40,12}},{{34,20}},{{22,20}},{{27,30}},{{33,30}}}},Enum.force.enemy)end
function on_update(game)if not rope_open and (game:is_unit_within("ZhiChuo62",{{48,7}},2) or game:is_unit_within("GuoZui62",{{48,7}},2))then rope_open=true;game:set_unit_invulnerable("SuShaWei62",false);game:push_cmd_speak(0,"公娄垂下绳索，东北城角已被夺取！肃沙卫可以被击退。")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if rope_open and not game:has_unit("SuShaWei62")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="GaotangNightBreach62",turn_limit=28,map={{blocked_edges={{}},size={{58,42}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{23,38}},hero="QiZhuangGong62"}},{{position={{51,7}},hero="ZhiChuo62"}},{{position={{52,9}},hero="GuoZui62"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=9000}}}}
'''


def stage_c() -> str:
    d = manifest("m103", "ch62c")
    intro = [
        ("", "晋平公即位后，栾盈因家势强盛遭范匄忌惮。范宣子听信栾祁之言，诬称栾盈谋乱。"),
        ("", "栾盈出奔楚国，其党叔虎、箕遗、黄渊仍在晋都。范匄命范鞅先围叔虎宅第。"),
        ("范鞅", "叔虎闭门拒捕，府墙不可翻越。封住南门，先晓谕投降；若仍拒命，再焚门进兵。"),
        ("叔虎", "范氏罗织罪名，今日不过仗势灭族。谁敢入门，我便以石木相拒！"),
        ("", "告密者张铿来到墙下劝降，叔虎以大石击杀张铿。范鞅遂下令纵火烧门。"),
        ("箕遗", "南门火起，守宅已无意义。与叔虎并骑冲出，尚可杀开一条路。"),
        ("黄渊", "我从东路接应。只要三人中有一人出城，便可把栾氏受诬之事传到诸侯。"),
        ("军令", "范鞅接近南门后触发焚门。第三回合荀吴由东路赶到；击退三人均视为被俘。"),
    ]
    victory = [
        ("", "南门被火烧开，叔虎、箕遗冲出府门，范氏弓手齐发，将二人射伤擒住。"),
        ("荀吴", "黄渊企图从东路接应，已被我军截住。三名栾氏党羽全部在押。"),
        ("范鞅", "押回朝堂听审，不得在街市私杀。栾氏其余家众逐一登记，不许趁乱劫掠。"),
        ("", "叔虎、箕遗、黄渊后来皆被处死；羊舌赤、羊舌肸也受牵连，幸得祁奚力救。"),
        ("", "栾盈远奔楚国，晋国内部的范栾之争并未结束，更大的祸乱已经埋下。"),
        ("军令", "叔虎府围捕完成，获得800金币。第六十二回剧情完成。"),
    ]
    text = head("第六十二回·下／第六十三回开端", "诸侯同心围齐国 晋臣合力逐栾盈", "叔虎府之围", "焚开南门，击退并俘获叔虎、箕遗、黄渊。", "m103.png", intro, victory,
                "范鞅被击退，或荀吴登场后被击退，或超过二十二回合，战役失败。", ["FanYang61"],
                '{{id="shuhu_hall",name="叔虎府正堂",position={25,11},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}}}',
                [("叔虎", "张铿卖主求荣，休想以空言骗我开门！"), ("范鞅", "张铿已死，纵火焚门，弓手列阵擒人！"), ("荀吴", "东路已封，黄渊不得接近叔虎府。")])
    rows = shared.terrain_block(d)
    return text + f'''local gate_burned=false local xunwu_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("FanYang61",1)end
function on_begin(game)game:generate_unit("ShuHu62",1,Enum.force.enemy,{{24,18}});game:generate_unit("JiYi62",1,Enum.force.enemy,{{28,18}});game:generate_unit("HuangYuan62",1,Enum.force.enemy,{{42,18}});game:set_unit_invulnerable("ShuHu62",true);game:set_unit_invulnerable("JiYi62",true);many(game,"JinArrestGuard62",{{{{20,32}},{{23,33}},{{27,33}},{{30,32}}}},Enum.force.own)end
function on_update(game)
if not gate_burned and game:is_unit_within("FanYang61",{{25,28}},3)then gate_burned=true;game:set_unit_invulnerable("ShuHu62",false);game:set_unit_invulnerable("JiYi62",false);game:push_cmd_speak(0,"叔虎击杀劝降者，范鞅下令焚开南门！叔虎、箕遗突围。")end
if not xunwu_spawned and game:get_turn_current()>=3 then xunwu_spawned=true;game:generate_unit("XunWu62",1,Enum.force.own,{{47,18}});many(game,"JinArrestGuard62",{{{{46,16}},{{46,20}}}},Enum.force.own);game:push_cmd_speak(0,"荀吴从东路赶到，截断黄渊接应路线。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("FanYang61")then return Enum.status.defeat end if xunwu_spawned and not game:has_unit("XunWu62")then return Enum.status.defeat end if not game:has_unit("ShuHu62") and not game:has_unit("JiYi62") and not game:has_unit("HuangYuan62")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="ShuHuManor62",turn_limit=22,map={{blocked_edges={{}},size={{50,36}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{24,32}},hero="FanYang61"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=8000}}}}
'''


def patch_all() -> None:
    for sid, text in (("62a", stage_a()), ("62b", stage_b()), ("62c", stage_c())):
        (ROOT / f"game/sce/dongzhou/stage/{sid}.lua").write_text(text, encoding="utf-8")

    p = ROOT / "game/sce/dongzhou/config.lua"; t = p.read_text(encoding="utf-8")
    if 'id = "HanQi62"' not in t:
        t = t.replace('        ,{ id = "SunArcher61", class = "Archer", stat = {86,91,87,89,87}, model = "archer-1-blue" }    },', '        ,{ id = "SunArcher61", class = "Archer", stat = {86,91,87,89,87}, model = "archer-1-blue" }' + HEROES + '    },')
    t = t.replace('"61a", "61b", "61c" }', '"61a", "61b", "61c", "62a", "62b", "62c" }')
    p.write_text(t, encoding="utf-8")

    p = ROOT / "rl/save_system.py"; t = p.read_text(encoding="utf-8")
    t = t.replace("STAGE_TABLE_VERSION = 5", "STAGE_TABLE_VERSION = 6")
    t = t.replace('"61a","61b","61c"\n)', '"61a","61b","61c","62a","62b","62c"\n)')
    p.write_text(t, encoding="utf-8")

    p = ROOT / "rl/play_gui.py"; t = p.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m101.png"]' not in t:
        block = '''
_LARGE_BATTLE_MAPS["m101.png"]=(86,56,48)
_LARGE_BATTLE_MAPS["m102.png"]=(58,42,48)
_LARGE_BATTLE_MAPS["m103.png"]=(50,36,48)
HERO_LABELS.update({"HanQi62":"韩起","WeiJiang62":"魏绛","ZhouChuo62":"周绰","LuanYing62":"栾盈","QiLingGong62":"齐灵公","XiGuiFu62":"析归父","ZhiChuo62":"殖绰","GuoZui62":"郭最","CuiZhu62":"崔杼","QingFeng62":"庆封","QiCoalitionGuard62":"齐军甲士","QiCoalitionArcher62":"齐军弓手","JinCoalitionGuard62":"晋盟甲士","JinCoalitionArcher62":"晋盟弓手","QiZhuangGong62":"齐庄公","GongLou62":"公娄","SuShaWei62":"肃沙卫","GaotangGuard62":"高唐守军","GaotangArcher62":"高唐弓手","ShuHu62":"叔虎","JiYi62":"箕遗","HuangYuan62":"黄渊","XunWu62":"荀吴","JinArrestGuard62":"晋国甲士"})
HERO_BIOS.update({"HanQi62":"晋国正卿韩起，参与伐齐与诸侯会盟，后来执掌晋政。","WeiJiang62":"晋国名将魏绛，辅佐晋悼公和晋平公，主张和戎以安诸夏。","ZhouChuo62":"晋国勇士，伐齐时追至石门，击败并俘获殖绰、郭最。","LuanYing62":"晋国栾氏之主，受范氏构陷出奔楚国，后来返晋作乱。","QiLingGong62":"齐国君主，恃强与晋争霸，遭十二国联军围攻临淄。","XiGuiFu62":"齐国将领，率军据防门沟壕抵御晋国联军。","ZhiChuo62":"齐国勇将，石门战败被俘，后逃归齐国，又参与高唐夜袭。","GuoZui62":"齐国勇将，与殖绰同守石门被俘，后从高唐东北城角先登入城。","CuiZhu62":"齐国权臣，迎立齐庄公，后来专擅齐国国政。","QingFeng62":"齐国大夫，与崔杼共同迎立齐庄公。","QiZhuangGong62":"齐国君主光，平定高唐肃沙卫之乱，稳定新政。","GongLou62":"高唐工匠，为齐军内应，夜间从东北城角垂绳接引。","SuShaWei62":"齐国叛臣，据高唐坚守一月有余，城破后被处死。","ShuHu62":"晋国栾氏党羽，遭范鞅包围府第，突围被俘后处死。","JiYi62":"晋国栾氏党羽，与叔虎一同冲出府门，被射伤擒获。","HuangYuan62":"晋国栾氏党羽，企图接应叔虎，被荀吴截获。","XunWu62":"晋国大夫，中行氏将领，叔虎府之变中截获黄渊。"})
PORTRAIT_INDEX_BY_HERO.update({"HanQi62":49,"WeiJiang62":35,"ZhouChuo62":38,"LuanYing62":34,"QiLingGong62":8,"XiGuiFu62":34,"ZhiChuo62":35,"GuoZui62":38,"CuiZhu62":49,"QingFeng62":34,"QiZhuangGong62":7,"GongLou62":25,"SuShaWei62":34,"ShuHu62":35,"JiYi62":25,"HuangYuan62":38,"XunWu62":35})
SPEAKER_PORTRAIT_INDEX.update({"荀偃":35,"士匄":35,"赵武":35,"韩起":49,"析归父":34,"殖绰":35,"郭最":38,"齐灵公":8,"齐庄公":7,"公娄":25,"肃沙卫":34,"范鞅":35,"叔虎":35,"箕遗":25,"黄渊":38,"荀吴":35})
HISTORICAL_DEATH_HEROES.update({"SuShaWei62","ShuHu62","JiYi62","HuangYuan62"})
'''
        t = t.replace('\nif _original_name == "__main__":', block + '\nif _original_name == "__main__":')
    p.write_text(t, encoding="utf-8")


if __name__ == "__main__":
    patch_all(); print("chapter 62 integrated: 62a, 62b, 62c")
