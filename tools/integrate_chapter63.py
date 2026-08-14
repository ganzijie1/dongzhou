from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT=Path(__file__).resolve().parents[1]

HEROES='''
        ,{ id = "WeiShu63", class = "Cavalry", stat = {93,94,94,94,92}, model = "cavalry-1-red" }
        ,{ id = "DuRong63", class = "Infantry", stat = {91,99,82,93,91}, model = "infantry-1-blue" }
        ,{ id = "LuanLe63", class = "Archer", stat = {90,98,87,93,90}, model = "archer-1-blue" }
        ,{ id = "LuanFang63", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "LuanRong63", class = "Infantry", stat = {87,92,84,89,86}, model = "infantry-1-blue" }
        ,{ id = "XuWu63", class = "Strategist", stat = {89,81,94,91,89}, model = "Strategist-1-blue" }
        ,{ id = "FeiBao63", class = "Infantry", stat = {90,97,87,92,91}, model = "infantry-1-red" }
        ,{ id = "XieYong63", class = "Infantry", stat = {87,93,84,89,87}, model = "infantry-1-red" }
        ,{ id = "XieSu63", class = "Infantry", stat = {87,93,84,89,87}, model = "infantry-1-red" }
        ,{ id = "MuGang63", class = "Infantry", stat = {88,95,83,90,88}, model = "infantry-1-red" }
        ,{ id = "MuJin63", class = "Infantry", stat = {88,95,83,90,88}, model = "infantry-1-red" }
        ,{ id = "LuanRebelGuard63", class = "Infantry", stat = {89,94,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "LuanRebelArcher63", class = "Archer", stat = {88,94,90,91,89}, model = "archer-1-blue" }
        ,{ id = "JinGugongGuard63", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "JinGugongArcher63", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "QuwoGuard63", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QuwoArcher63", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }'''


def data(mid,suffix):return json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
def head(chapter,title,battle,objective,asset,intro,victory,defeat,commanders,sites,events):
    return shared.stage_head("",title,chapter,battle,objective,asset,intro,events,victory,defeat,commanders,sites)


def stage_a():
    d=data("m104","ch63a")
    intro=[
        ("","叔虎、箕遗、黄渊被擒后，范匄又拘捕羊舌赤、羊舌肸等人，晋都一夜震动。"),
        ("","告老的祁奚连夜入都，以贤臣关系社稷为由劝范匄；晋平公终于赦免羊舌赤、羊舌肸。"),
        ("","栾盈由曲沃出奔楚国。家臣辛俞坚持三世事栾，获晋平公放行，携辎重追随旧主。"),
        ("","栾盈转奔齐国，齐庄公不顾晏婴反对收留他，又将州绰、邢蒯列入勇爵。"),
        ("","齐庄公借送媵女为名，将栾盈藏入温车送到曲沃。胥午召集曲沃之甲二百二十乘，夜袭绛都。"),
        ("辛俞","我从主是为尽私忠，却不能助主叛晋。此行必败，愿以一死相送。"),
        ("","辛俞自刎而死。栾盈仍率督戎、殖绰、郭最、栾乐、栾鲂破南门而入，直抵绛城市口。"),
        ("范鞅","主公已入固宫。魏舒车徒在北隅列阵，若让他接应栾盈，绛都内外皆失。"),
        ("魏舒","栾氏旧有恩于我，曲沃兵已经入城。此刻究竟应迎栾氏，还是奉晋侯之命？"),
        ("范鞅","奉君命，请魏伯同车入固宫！车徒立即转向东行，不得停留。"),
        ("督戎","固宫南关归我独攻。待填平沟堑，谁敢出关与我双戟一战？"),
        ("军令","先护送魏舒进入固宫；随后击退督戎，再击退发动北关火攻的栾乐。栾盈本关败退，不可被击退。"),
    ]
    victory=[
        ("","范鞅跃上魏舒之车，执剑牵其衣带，迫使车徒转向固宫。魏舒既入宫，只能与范氏共同守御。"),
        ("","督戎连败解雍、解肃、牟刚、牟劲，晋军无人敢应。隶人斐豹请焚丹书换取出战。"),
        ("斐豹","督君素喜独斗。引他越过短墙，我伏于树下，以五十二斤铜锤取其首级。"),
        ("","督戎中计，被斐豹从背后一锤击杀。固宫南关守军随即出击，栾军大败。"),
        ("","栾乐夜用轈车火攻北关，一度攻占外关；范鞅、荀吴内外夹击，栾乐翻车被斐豹杀死。"),
        ("","殖绰奔卫，郭最奔秦；栾盈、栾鲂带残兵退回曲沃。魏舒念旧放行，赵武也没有追赶。"),
        ("范匄","曲沃之甲尽随栾盈而归。范鞅、荀吴立即率军围城，不可再给齐军接应的机会。"),
        ("军令","固宫保卫战完成，获得1200金币。下一关：曲沃灭栾。"),
    ]
    text=head("第六十三回·下／第六十四回开端","老祁奚力救羊舌 小范鞅智劫魏舒","固宫保卫战","护送魏舒进入固宫，依次击退督戎与栾乐。","m104.png",intro,victory,
              "范鞅、魏舒、赵武任一被击退，或超过三十回合，战役失败。",["FanYang61","WeiShu63","ZhaoWu59","XunWu62","HanQi62"],
              '{{id="gugong_main",name="固宫",position={57,16},restore_hp=30,restore_mp=20,rewards={{item="medicine",amount=1}}},{id="gugong_store",name="固宫武库",position={63,25},restore_hp=25,restore_mp=15,rewards={}},{id="wei_house",name="魏氏府库",position={18,12},restore_hp=20,restore_mp=10,rewards={}}}',
              [("范鞅","魏伯已奉君命进入固宫，诸卿同心守关！"),("斐豹","督戎，今日只你我二人赌个死生！"),("栾乐","北关火起，轈车并进，今夜定要破宫！")])
    rows=shared.terrain_block(d)
    return text+f'''local phase=1 local feibao_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("LuanYing62",1,Enum.force.enemy,{{36,39}});game:set_unit_invulnerable("LuanYing62",true);game:generate_unit("DuRong63",1,Enum.force.enemy,{{38,43}});game:set_unit_invulnerable("DuRong63",true);game:generate_unit("LuanLe63",1,Enum.force.enemy,{{55,39}});game:set_unit_invulnerable("LuanLe63",true);game:generate_unit("LuanFang63",1,Enum.force.enemy,{{60,40}});game:set_unit_invulnerable("LuanFang63",true);many(game,"LuanRebelGuard63",{{{{33,41}},{{36,43}},{{41,41}},{{31,36}},{{39,36}},{{49,38}},{{53,38}},{{59,38}},{{63,39}}}},Enum.force.enemy);many(game,"LuanRebelArcher63",{{{{30,39}},{{42,39}},{{51,41}},{{58,42}},{{64,41}}}},Enum.force.enemy);many(game,"JinGugongGuard63",{{{{53,33}},{{56,33}},{{59,33}},{{62,33}},{{53,10}},{{60,10}}}},Enum.force.own);many(game,"JinGugongArcher63",{{{{50,31}},{{65,31}},{{51,12}},{{64,12}}}},Enum.force.own)end
function on_update(game)
if phase==1 and game:is_unit_within("WeiShu63",{{57,16}},8)then phase=2;feibao_spawned=true;game:generate_unit("FeiBao63",1,Enum.force.own,{{54,32}});game:set_unit_invulnerable("DuRong63",false);game:push_cmd_speak(0,"魏舒已进入固宫。斐豹请战，督戎不再受保护！")end
if phase==2 and feibao_spawned and not game:has_unit("FeiBao63")then return end
if phase==2 and not game:has_unit("DuRong63")then phase=3;game:set_unit_invulnerable("LuanLe63",false);game:push_cmd_speak(0,"督戎已被斐豹击杀！栾乐转攻北关，火箭轈车一齐逼近。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if feibao_spawned and not game:has_unit("FeiBao63")then return Enum.status.defeat end if phase==3 and not game:has_unit("LuanLe63")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="GugongDefense63",turn_limit=30,map={{blocked_edges={{}},size={{74,52}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{17,12}},hero="FanYang61"}},{{position={{19,12}},hero="WeiShu63"}},{{position={{54,31}},hero="ZhaoWu59"}},{{position={{60,31}},hero="XunWu62"}},{{position={{57,12}},hero="HanQi62"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=12000}}}}
'''


def stage_b():
    d=data("m105","ch63b")
    intro=[
        ("","固宫之战失败后，栾盈、栾鲂带曲沃残兵退回城中。范鞅、荀吴率三百乘围城。"),
        ("范鞅","栾氏爪牙已尽，但曲沃城墙连续坚固。封住东门、南门，先断城中补给。"),
        ("荀吴","胥午经营曲沃多年，城中仍有弓手与甲士。两路同时施压，不让守军集中一门。"),
        ("栾盈","我悔不用辛俞忠言，才到今日。但栾氏宗祀尚在，绝不能束手就擒。"),
        ("胥午","我曾受栾氏厚恩。曲沃若破，惟有伏剑以谢故主，不会出城求生。"),
        ("栾鲂","城破后我从南墙缒城突围，若能留下栾氏一脉，也不算全军俱没。"),
        ("军令","击退胥午、栾荣后解除栾盈保护；击退栾盈即视为被俘。栾鲂不可被击退，按剧情突围。"),
    ]
    victory=[
        ("","曲沃被围一个多月，守军死伤过半。晋军从东、南两门同时攻入，城内再无完整防线。"),
        ("","胥午见大势已去，伏剑自尽。栾盈、栾荣被范鞅所部擒获，栾鲂乘夜缒城奔宋。"),
        ("栾盈","我悔不用辛俞之言，以私怨犯君，终使栾氏数世功业毁于一旦。"),
        ("","范鞅担心晋平公临时宽赦，夜使人缢杀栾盈，并处死栾荣，栾氏自此灭族。"),
        ("","晋平公焚毁丹书，释放因旧案没官为奴者；斐豹因击杀督戎被任为中军牙将。"),
        ("","范匄随后告老，赵武接掌晋国政事。齐庄公出兵接应栾盈，闻其失败后转兵撤退。"),
        ("军令","曲沃灭栾完成，获得1300金币。第六十三回战役结束。"),
    ]
    text=head("第六十三回·终／第六十四回上","老祁奚力救羊舌 小范鞅智劫魏舒","曲沃灭栾","攻破曲沃，击退胥午、栾荣并俘获栾盈。","m105.png",intro,victory,
              "范鞅或荀吴被击退，或超过三十二回合，战役失败。",["FanYang61","XunWu62"],
              '{{id="quwo_hall",name="曲沃栾氏宗堂",position={28,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="quwo_west_store",name="曲沃西库",position={18,21},restore_hp=20,restore_mp=10,rewards={}},{id="quwo_east_store",name="曲沃东库",position={38,21},restore_hp=20,restore_mp=10,rewards={}}}',
              [("胥午","城亡之日，便是胥午报答栾氏之时。"),("栾鲂","兄长保重，我从南墙突围，为栾氏留下一线。"),("范鞅","栾盈已经就擒，曲沃各军放下兵器！")])
    rows=shared.terrain_block(d)
    return text+f'''local leaders_down=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("LuanYing62",1,Enum.force.enemy,{{28,10}});game:set_unit_invulnerable("LuanYing62",true);game:generate_unit("XuWu63",1,Enum.force.enemy,{{18,21}});game:generate_unit("LuanRong63",1,Enum.force.enemy,{{38,21}});game:generate_unit("LuanFang63",1,Enum.force.enemy,{{28,29}});game:set_unit_invulnerable("LuanFang63",true);many(game,"QuwoGuard63",{{{{46,16}},{{46,21}},{{29,32}},{{26,32}},{{22,27}},{{34,27}},{{20,17}},{{36,17}},{{26,13}},{{31,13}}}},Enum.force.enemy);many(game,"QuwoArcher63",{{{{44,14}},{{44,23}},{{23,30}},{{33,30}},{{16,16}},{{40,16}},{{24,11}},{{32,11}}}},Enum.force.enemy);many(game,"JinGugongGuard63",{{{{52,15}},{{52,18}},{{52,22}},{{52,25}}}},Enum.force.own);many(game,"JinGugongArcher63",{{{{55,17}},{{55,23}}}},Enum.force.own)end
function on_update(game)if not leaders_down and not game:has_unit("XuWu63") and not game:has_unit("LuanRong63")then leaders_down=true;game:set_unit_invulnerable("LuanYing62",false);game:push_cmd_speak(0,"胥午伏剑，栾荣被擒。栾鲂已经缒城逃往宋国，合兵进取栾盈！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if leaders_down and not game:has_unit("LuanYing62")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="QuwoLastSiege63",turn_limit=32,map={{blocked_edges={{}},size={{58,42}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{53,17}},hero="FanYang61"}},{{position={{53,21}},hero="XunWu62"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=13000}}}}
'''


def patch_all():
    for sid,text in (("63a",stage_a()),("63b",stage_b())):(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").write_text(text,encoding="utf-8")
    p=ROOT/"game/sce/dongzhou/config.lua";t=p.read_text(encoding="utf-8")
    if 'id = "WeiShu63"' not in t:t=t.replace('        ,{ id = "JinArrestGuard62", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }    },','        ,{ id = "JinArrestGuard62", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }'+HEROES+'    },')
    t=t.replace('"62a", "62b", "62c" }','"62a", "62b", "62c", "63a", "63b" }');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/save_system.py";t=p.read_text(encoding="utf-8").replace('STAGE_TABLE_VERSION = 6','STAGE_TABLE_VERSION = 7').replace('"62a","62b","62c"\n)','"62a","62b","62c","63a","63b"\n)');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/play_gui.py";t=p.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m104.png"]' not in t:
        block='''
_LARGE_BATTLE_MAPS["m104.png"]=(74,52,48)
_LARGE_BATTLE_MAPS["m105.png"]=(58,42,48)
HERO_LABELS.update({"WeiShu63":"魏舒","DuRong63":"督戎","LuanLe63":"栾乐","LuanFang63":"栾鲂","LuanRong63":"栾荣","XuWu63":"胥午","FeiBao63":"斐豹","XieYong63":"解雍","XieSu63":"解肃","MuGang63":"牟刚","MuJin63":"牟劲","LuanRebelGuard63":"栾氏甲士","LuanRebelArcher63":"栾氏弓手","JinGugongGuard63":"固宫甲士","JinGugongArcher63":"固宫弓手","QuwoGuard63":"曲沃甲士","QuwoArcher63":"曲沃弓手"})
HERO_BIOS.update({"WeiShu63":"晋国魏氏大夫，原欲接应栾盈，被范鞅挟持入固宫后参与平乱。","DuRong63":"栾盈麾下第一勇士，使双戟攻固宫，连败晋将，最终中斐豹伏击而死。","LuanLe63":"栾氏善射猛将，北关火攻一度得手，追射范鞅时翻车被杀。","LuanFang63":"栾氏将领，护栾盈退回曲沃，城破后缒城逃往宋国。","LuanRong63":"栾氏族人，曲沃城破后与栾盈一同被擒处死。","XuWu63":"曲沃守臣，受栾氏旧恩，助栾盈起兵，城破后伏剑自尽。","FeiBao63":"晋国隶人，以免除丹书罪籍为请，设计击杀勇士督戎，升为牙将。","XieYong63":"赵武部将，与弟解肃出战督戎，重伤而死。","XieSu63":"赵武部将，督戎阵前折枪后逃归固宫。","MuGang63":"荀吴部下勇士，与解肃等合战督戎。","MuJin63":"荀吴部下勇士，合战督戎时战死。"})
PORTRAIT_INDEX_BY_HERO.update({"WeiShu63":35,"DuRong63":25,"LuanLe63":33,"LuanFang63":34,"LuanRong63":25,"XuWu63":49,"FeiBao63":25,"XieYong63":25,"XieSu63":38,"MuGang63":25,"MuJin63":38})
SPEAKER_PORTRAIT_INDEX.update({"魏舒":35,"督戎":25,"栾乐":33,"栾鲂":34,"栾盈":34,"胥午":49,"斐豹":25,"辛俞":49})
HISTORICAL_DEATH_HEROES.update({"DuRong63","LuanLe63","LuanYing62","LuanRong63","XuWu63","XieYong63","MuJin63"})
'''
        t=t.replace('\nif _original_name == "__main__":',block+'\nif _original_name == "__main__":')
    p.write_text(t,encoding="utf-8")


if __name__=="__main__":patch_all();print("chapter 63 integrated: 63a, 63b")
