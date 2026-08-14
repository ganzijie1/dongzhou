from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT=Path(__file__).resolve().parents[1]
HEROES='''
        ,{ id = "WangSunHui64", class = "Cavalry", stat = {91,94,91,92,90}, model = "cavalry-1-red" }
        ,{ id = "ShenXianYu64", class = "Strategist", stat = {91,86,96,93,92}, model = "Strategist-1-red" }
        ,{ id = "YanMao64", class = "Cavalry", stat = {88,93,86,90,88}, model = "cavalry-1-red" }
        ,{ id = "ZhaoSheng64", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "ZhaoPursuer64", class = "Cavalry", stat = {89,94,85,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ZhaoArcher64", class = "Archer", stat = {88,93,90,90,89}, model = "archer-1-blue" }
        ,{ id = "QiRetreatGuard64", class = "Infantry", stat = {89,94,86,90,89}, model = "infantry-1-red" }
        ,{ id = "QiRetreatArcher64", class = "Archer", stat = {88,93,90,90,89}, model = "archer-1-red" }
        ,{ id = "HuaZhou64", class = "Infantry", stat = {91,98,85,92,91}, model = "infantry-1-red" }
        ,{ id = "QiLiang64", class = "Infantry", stat = {92,98,87,93,92}, model = "infantry-1-red" }
        ,{ id = "XiHouZhong64", class = "Infantry", stat = {89,96,84,90,90}, model = "infantry-1-red" }
        ,{ id = "JuLiBiGong64", class = "Lord", stat = {89,91,90,90,88}, model = "lord-1-blue" }
        ,{ id = "JuGateCaptain64", class = "Archer", stat = {89,95,90,91,89}, model = "archer-1-blue" }
        ,{ id = "JuGuard64", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "JuArcher64", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }'''


def data(mid,suffix):return json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
def head(chapter,title,battle,objective,asset,intro,victory,defeat,commanders,sites,events):return shared.stage_head("",title,chapter,battle,objective,asset,intro,events,victory,defeat,commanders,sites)


def stage_a():
    d=data("m106","ch64a")
    intro=[
        ("","栾盈袭晋时，齐庄公亲率大军为外援，先侵卫境，又北取朝歌，分兵经孟门、共山登太行。"),
        ("王孙挥","前军已经越过孟门。若栾盈控制绛都，我军便可从太行直下，内外夹击晋国。"),
        ("申鲜虞","曲沃急报：督戎、栾乐皆死，栾盈已经败退，晋国诸卿正集结大军。"),
        ("齐庄公","接应已无意义。全军沿少水撤回齐境，不可在山中与晋国主力纠缠。"),
        ("","齐军前队已经先发，邯郸大夫赵胜率本邑兵追来。齐庄公仓促撤退，只留晏氂断后。"),
        ("晏氂","主公先过少水，我守太行东口。只要中军退出，赵军便不能拖住全军。"),
        ("赵胜","齐军远来犯晋，如今仓皇退走。骑兵沿山道追击，弓手占住少水西岸。"),
        ("军令","护送齐庄公穿过太行山口与少水，到达东侧出口。晏氂为友军坚守后路，其退场不判我方失败。"),
    ]
    victory=[
        ("","齐庄公率中军越过少水，王孙挥、申鲜虞整顿前军，主力得以脱离晋国追兵。"),
        ("晏氂","中军已经走远，我军不必再退。列阵迎敌，为主公争取最后一段路程！"),
        ("","赵胜集中邯郸兵猛攻后队，晏氂兵败被杀。齐军虽失后将，仍成功退出晋境。"),
        ("齐庄公","栾盈已败，伐晋之志未成；平阴之役莒人曾欲袭齐，此仇尚未报。"),
        ("","齐庄公不肯立即回临淄，在国境整顿车乘，准备以精锐袭击莒国。"),
        ("军令","少水断后完成，获得800金币。下一关：且于门死战。"),
    ]
    text=head("第六十四回·中","曲沃城栾盈灭族 且于门杞梁死战","少水断后","护送齐庄公穿过太行与少水，从东侧撤出。","m106.png",intro,victory,
              "齐庄公、王孙挥、申鲜虞任一被击退，或超过二十四回合，战役失败。",["QiZhuangGong62","WangSunHui64","ShenXianYu64"],"{}",
              [("赵胜","邯郸骑兵已经追上，截住齐侯！"),("晏氂","主公只管东撤，后路由我来守！")])
    rows=shared.terrain_block(d)
    return text+f'''local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("YanMao64",1,Enum.force.ally,{{13,20}});game:generate_unit("ZhaoSheng64",1,Enum.force.enemy,{{6,20}});many(game,"ZhaoPursuer64",{{{{4,15}},{{4,18}},{{4,22}},{{4,25}},{{8,16}},{{8,24}}}},Enum.force.enemy);many(game,"ZhaoArcher64",{{{{2,18}},{{2,22}},{{7,13}},{{7,27}}}},Enum.force.enemy);many(game,"QiRetreatGuard64",{{{{17,17}},{{17,22}},{{21,20}}}},Enum.force.own);many(game,"QiRetreatArcher64",{{{{15,15}},{{15,25}}}},Enum.force.own)end
function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if game:is_unit_within("QiZhuangGong62",{{58,20}},1)then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="ShaoshuiRetreat64",turn_limit=24,map={{blocked_edges={{}},size={{60,40}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{19,19}},hero="QiZhuangGong62"}},{{position={{22,17}},hero="WangSunHui64"}},{{position={{22,22}},hero="ShenXianYu64"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=8000}}}}
'''


def stage_b():
    d=data("m107","ch64b")
    intro=[
        ("","齐庄公回到齐境后转而袭莒，留下王孙挥统大军，自领三千精锐与勇爵诸士秘密进军。"),
        ("","华周、杞梁不满两人只得一乘，却仍奉君命出征；小卒隰侯重慕其勇义，自愿同车。"),
        ("华周","我与杞梁只用一车先行。隰侯重掌鼓，鼓声不停，我二人便不会退后。"),
        ("杞梁","母亲教我：生而无义，死而无名，虽居勇爵也只为人所笑。今日当尽将士之责。"),
        ("","三人在莒郊遇黎比公率三百甲士巡查。华周、杞梁跳车持戟，冲阵杀伤近半。"),
        ("莒黎比公","二位勇名果然不虚。若肯罢战，我愿分莒国土地与你们共同享有。"),
        ("华周","弃国归敌是不忠，受命半途而废是不信。我们只知深入破敌，不受封赏诱惑。"),
        ("","黎比公败退且于门，在狭道挖沟灸炭，又命百名善射者伏于门旁。"),
        ("隰侯重","我以盾伏在火炭之上，为二位铺出两步通路。只要你们越沟，我死亦有名。"),
        ("军令","先击退莒黎比公；隰侯重抵达火沟后开启双格盾桥；华周、杞梁击退城门守将并抵达且于门即过关。"),
    ]
    victory=[
        ("","隰侯重伏盾于炭火之上，华周、杞梁踏盾越沟。回首时，他已被烈火烧死。"),
        ("华周","此人勇义与我相同，却先我而死。我哭的不是畏死，而是痛惜同道。"),
        ("","二人逼近且于门，百名弓手从门旁齐射。杞梁身受重伤，仍持戟杀敌，最终战死。"),
        ("","华周身中数十箭，力尽被擒。莒黎比公将他载回城中，齐军主力随后也未能立刻破门。"),
        ("齐庄公","三人单车深入，忠勇足以传世。撤回大军，厚恤杞梁、隰侯重之家。"),
        ("","杞梁之妻后来闻夫战死，悲恸迎丧；其故事在后世不断流传演变。"),
        ("军令","且于门死战完成，获得1000金币。第六十四回结束。"),
    ]
    text=head("第六十四回·下","曲沃城栾盈灭族 且于门杞梁死战","且于门死战","击退莒郊军，架盾越过火沟并抵达且于门。","m107.png",intro,victory,
              "华周、杞梁、隰侯重任一在完成目标前被击退，或超过二十八回合，战役失败。",["HuaZhou64","QiLiang64","XiHouZhong64"],
              '{{id="qieyu_city",name="且于城",position={59,12},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}',
              [("莒黎比公","退守且于门，掘火沟，令百名弓手夹门伏射！"),("隰侯重","盾桥已成，二位将军踏我背上越沟！"),("杞梁","既过火沟，便只向城门，不再回头！")])
    rows=shared.terrain_block(d)
    return text+f'''local field_broken=false local bridge_ready=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("JuLiBiGong64",1,Enum.force.enemy,{{29,23}});game:generate_unit("JuGateCaptain64",1,Enum.force.enemy,{{52,22}});game:set_unit_invulnerable("JuGateCaptain64",true);many(game,"JuGuard64",{{{{23,18}},{{23,22}},{{23,26}},{{27,17}},{{27,27}},{{33,19}},{{33,25}},{{49,19}},{{49,26}},{{55,20}},{{55,25}}}},Enum.force.enemy);many(game,"JuArcher64",{{{{25,15}},{{25,30}},{{31,16}},{{31,29}},{{50,17}},{{50,28}},{{54,18}},{{54,27}},{{57,21}},{{57,24}}}},Enum.force.enemy)end
function on_update(game)
if not field_broken and not game:has_unit("JuLiBiGong64")then field_broken=true;game:push_cmd_speak(0,"黎比公退入且于门，火沟已经点燃。隰侯重立即前往盾桥位置！")end
if field_broken and not bridge_ready and game:is_unit_within("XiHouZhong64",{{46,22}},1)then bridge_ready=true;game:set_unit_invulnerable("JuGateCaptain64",false);game:push_cmd_speak(0,"隰侯重伏盾于炭火，双格通路已经打开！华周、杞梁越沟夺门！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if bridge_ready and not game:has_unit("JuGateCaptain64") and game:is_unit_within("HuaZhou64",{{52,22}},2) and game:is_unit_within("QiLiang64",{{52,23}},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="QieyuLastStand64",turn_limit=28,map={{blocked_edges={{}},size={{68,46}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{12,21}},hero="HuaZhou64"}},{{position={{12,24}},hero="QiLiang64"}},{{position={{10,23}},hero="XiHouZhong64"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=10000}}}}
'''


def patch_all():
    for sid,text in (("64a",stage_a()),("64b",stage_b())):(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").write_text(text,encoding="utf-8")
    p=ROOT/"game/sce/dongzhou/config.lua";t=p.read_text(encoding="utf-8")
    if 'id = "WangSunHui64"' not in t:t=t.replace('        ,{ id = "QuwoArcher63", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }    },','        ,{ id = "QuwoArcher63", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }'+HEROES+'    },')
    t=t.replace('"63a", "63b" }','"63a", "63b", "64a", "64b" }');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/save_system.py";t=p.read_text(encoding="utf-8").replace('STAGE_TABLE_VERSION = 7','STAGE_TABLE_VERSION = 8').replace('"63a","63b"\n)','"63a","63b","64a","64b"\n)');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/play_gui.py";t=p.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m106.png"]' not in t:
        block='''
_LARGE_BATTLE_MAPS["m106.png"]=(60,40,48)
_LARGE_BATTLE_MAPS["m107.png"]=(68,46,48)
HERO_LABELS.update({"WangSunHui64":"王孙挥","ShenXianYu64":"申鲜虞","YanMao64":"晏氂","ZhaoSheng64":"赵胜","ZhaoPursuer64":"邯郸骑兵","ZhaoArcher64":"邯郸弓手","QiRetreatGuard64":"齐军甲士","QiRetreatArcher64":"齐军弓手","HuaZhou64":"华周","QiLiang64":"杞梁","XiHouZhong64":"隰侯重","JuLiBiGong64":"莒黎比公","JuGateCaptain64":"且于门将","JuGuard64":"莒国甲士","JuArcher64":"莒国弓手"})
HERO_BIOS.update({"WangSunHui64":"齐国大夫，齐庄公伐晋时统率前军，经孟门登太行。","ShenXianYu64":"齐国将领，随王孙挥统率伐晋前队。","YanMao64":"齐国将领，太行撤军时负责断后，兵败于赵胜而死。","ZhaoSheng64":"晋国邯郸大夫，起本邑之兵追击撤退齐军，斩杀晏氂。","HuaZhou64":"齐国勇士，与杞梁单车深入莒境，身中数十箭后被俘。","QiLiang64":"齐国勇士，且于门冒箭死战，重伤而亡，后世故事广为流传。","XiHouZhong64":"齐国小卒，慕华周、杞梁之勇，以盾伏火沟助二人越过，焚身而死。","JuLiBiGong64":"莒国君主，在莒郊率甲士迎战齐军，后退守且于门。","JuGateCaptain64":"莒国且于门守将，率弓手依托火沟夹门伏射。"})
PORTRAIT_INDEX_BY_HERO.update({"WangSunHui64":35,"ShenXianYu64":49,"YanMao64":34,"ZhaoSheng64":35,"HuaZhou64":25,"QiLiang64":38,"XiHouZhong64":25,"JuLiBiGong64":8,"JuGateCaptain64":33})
SPEAKER_PORTRAIT_INDEX.update({"王孙挥":35,"申鲜虞":49,"晏氂":34,"赵胜":35,"华周":25,"杞梁":38,"隰侯重":25,"莒黎比公":8,"齐庄公":7})
HISTORICAL_DEATH_HEROES.update({"YanMao64","QiLiang64","XiHouZhong64"})
'''
        t=t.replace('\nif _original_name == "__main__":',block+'\nif _original_name == "__main__":')
    p.write_text(t,encoding="utf-8")


if __name__=="__main__":patch_all();print("chapter 64 integrated: 64a, 64b")
