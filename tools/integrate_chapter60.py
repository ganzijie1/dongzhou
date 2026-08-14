from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


HEROES = '''
        ,{ id = "JinDaoGong60", class = "Lord", stat = {95, 90, 98, 96, 95}, model = "lord-1-red" }
        ,{ id = "LuanYan60", class = "Cavalry", stat = {91, 95, 90, 93, 90}, model = "cavalry-1-red" }
        ,{ id = "XiangShu60", class = "Strategist", stat = {93, 87, 97, 94, 93}, model = "Strategist-1-red" }
        ,{ id = "ZhongSunMie60", class = "Strategist", stat = {92, 86, 96, 93, 92}, model = "Strategist-1-red" }
        ,{ id = "YuShi60", class = "Strategist", stat = {88, 84, 92, 89, 86}, model = "Strategist-1-blue" }
        ,{ id = "XiangWeiRen60", class = "Infantry", stat = {87, 91, 83, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "LinZhu60", class = "Archer", stat = {86, 90, 87, 88, 86}, model = "archer-1-blue" }
        ,{ id = "XiangDai60", class = "Cavalry", stat = {88, 92, 84, 89, 87}, model = "cavalry-1-blue" }
        ,{ id = "YuFu60", class = "Infantry", stat = {87, 91, 84, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "JinCoalitionGuard60", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher60", class = "Archer", stat = {86, 92, 89, 90, 88}, model = "archer-1-red" }
        ,{ id = "SongCoalitionGuard60", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-red" }
        ,{ id = "PengchengGuard60", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-blue" }
        ,{ id = "PengchengArcher60", class = "Archer", stat = {86, 92, 89, 90, 88}, model = "archer-1-blue" }
        ,{ id = "ZhuFan60", class = "Lord", stat = {92, 93, 90, 92, 91}, model = "lord-1-red" }
        ,{ id = "YiMei60", class = "Cavalry", stat = {89, 94, 85, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "YuJi60", class = "Cavalry", stat = {90, 95, 87, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "DengLiao60", class = "Cavalry", stat = {91, 96, 88, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "YinQi60", class = "Strategist", stat = {90, 88, 95, 92, 90}, model = "Strategist-1-blue" }
        ,{ id = "WuMarine60", class = "Infantry", stat = {87, 93, 84, 89, 88}, model = "infantry-1-red" }
        ,{ id = "WuArcher60", class = "Archer", stat = {86, 92, 88, 90, 88}, model = "archer-1-red" }
        ,{ id = "ChuMarine60", class = "Infantry", stat = {88, 94, 85, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "ChuRiverArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }
        ,{ id = "ShiGai60", class = "Cavalry", stat = {91, 95, 89, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "ShuLiangHe60", class = "Infantry", stat = {90, 97, 84, 91, 91}, model = "infantry-1-red" }
        ,{ id = "QinJinFu60", class = "Infantry", stat = {89, 95, 85, 90, 89}, model = "infantry-1-red" }
        ,{ id = "DiSiMi60", class = "Infantry", stat = {89, 95, 84, 90, 89}, model = "infantry-1-red" }
        ,{ id = "YunBan60", class = "Cavalry", stat = {91, 96, 88, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "BiYangLord60", class = "Lord", stat = {88, 87, 90, 89, 88}, model = "lord-1-blue" }
        ,{ id = "BiYangGuard60", class = "Infantry", stat = {88, 94, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "BiYangArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }'''


def manifest(map_id: str, suffix: str) -> dict:
    return json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))


def terrain_block(data: dict) -> str:
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


def stage_head(stage: str, title: str, chapter: str, battle_title: str, objective: str,
               map_asset: str, intro: list[tuple[str, str]], events: list[tuple[str, str]],
               victory: list[tuple[str, str]], defeat: str, commanders: list[str], sites: str = "{}") -> str:
    def rows(items: list[tuple[str, str]]) -> str:
        return ",\n  ".join('{speaker="%s",text="%s"}' % item for item in items)
    event_rows = ",\n  ".join('{id="story_event_%d",trigger="scripted",turn=0,hp_percent=0,speaker="%s",text="%s"}' % (index + 1, item[0], item[1]) for index, item in enumerate(events))
    return f'''gally_hold_position=true
gsupply_enabled=true
gitems={{{{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2}},{{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}}}
gcommanders={{{",".join('"'+x+'"' for x in commanders)}}}
gevents_enabled=true
gduel_enabled=false
gduels={{}}
gsites={sites}
gstory={{chapter="{chapter}",title="{title}",battle_title="{battle_title}",objective="{objective}",map_asset="{map_asset}",
 intro={{
  {rows(intro)}
 }},
 events={{
  {event_rows}
 }},
 victory={{
  {rows(victory)}
 }},
 defeat={{{{speaker="",text="{defeat}"}}}}
}}
'''


def build_60a() -> str:
    data = manifest("m095", "ch60a")
    intro = [
        ("", "楚共王欲扰乱晋国新政，采用公子壬夫之策，资助鱼石、向为人、鳞朱、向带、鱼府五名宋国逃臣伐宋。"),
        ("", "楚郑联军攻取彭城，留下三百乘战车与五名逃臣守城。宋将老佐围城，先败鱼石，却因深入楚国援军而战死。"),
        ("晋悼公", "彭城若久据于楚，宋国必危。会合宋、鲁、卫、曹诸军，围城而不扰百姓。"),
        ("韩厥", "五名逃臣凭城固守，城中百姓却不愿随他们叛宋。先扫清城门外楚军，再逼近南门。"),
        ("向戌", "我备有临冲楼车，可隔城晓谕父老：开门者免罪，唯执五人为诛。"),
        ("仲孙蔑", "鲁军守住东侧，卫曹诸军封锁西路；晋军主攻南门，不可让楚援再入城。"),
        ("", "彭城父老早怨鱼石等人挟楚自重，只因楚兵守门，不敢响应。"),
        ("鱼石", "城中有三百乘楚车，诸侯虽众，未必能破彭城。违令开门者斩！"),
        ("栾黡", "连续城墙不可跨越。清除南门守军后，主力接近城门，由向戌登楼车劝降。"),
        ("军令", "先击退彭城南门守军并接近城门，触发百姓开门；再击退鱼石等五人，按原著视为生擒。"),
    ]
    victory = [
        ("", "向戌乘楼车临城晓谕，彭城百姓连夜缒人相约。次日城门大开，守卒倒戈，鱼石等五人束手被擒。"),
        ("晋悼公", "五人为宋国叛臣，应交宋国依法处置。楚军余众放下兵甲者，不再追杀。"),
        ("", "鱼石、向为人、鳞朱、向带、鱼府被宋国处死，彭城复归于宋。诸侯因此更加信服晋悼公。"),
        ("", "悼公随后在虎牢筑城，令魏绛执掌军法。郑国惧晋而归盟，楚国又遣兵争郑，郑国数次反覆。"),
        ("魏绛", "军令贵在必行。即使诸侯车马挡道，也不得坏我行列；但执法之后，罪责由我一人承担。"),
        ("", "悼公不但没有杀魏绛，反而命他辅佐戎事。郑国终于坚定从晋，中原形势暂时安定。"),
        ("军令", "彭城复宋完成，获得1400金币。下一关：采石水战。"),
    ]
    head = stage_head("60a", "合晋楚彭城大战", "第六十回·上", "彭城复宋",
        "扫清南门楚军，接近城门触发百姓开门，再生擒鱼石等五名叛臣。晋悼公、韩厥、荀偃或栾黡被击退则失败。",
        "m095.png", intro, [("向戌", "城中父老听着：开门归宋者免罪，只执鱼石五人！")], victory,
        "晋军主将被击退，或未能收复彭城，本关失败。", ["JinDaoGong60", "HanJue48", "XunYan58", "LuanYan60"],
        '{{id="pengcheng_palace",name="彭城官署",position={26,9},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="pengcheng_west",name="彭城西库",position={18,17},restore_hp=20,restore_mp=10,rewards={}},{id="pengcheng_east",name="彭城东库",position={35,17},restore_hp=20,restore_mp=10,rewards={}}}')
    terrain = terrain_block(data)
    return head + f'''local gate_open=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
local rebels={{"YuShi60","XiangWeiRen60","LinZhu60","XiangDai60","YuFu60"}}
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("XiangShu60",1,Enum.force.ally,{{20,31}});game:generate_unit("ZhongSunMie60",1,Enum.force.ally,{{33,31}})
 game:generate_unit("YuShi60",1,Enum.force.enemy,{{26,9}});game:generate_unit("XiangWeiRen60",1,Enum.force.enemy,{{18,17}});game:generate_unit("LinZhu60",1,Enum.force.enemy,{{35,17}});game:generate_unit("XiangDai60",1,Enum.force.enemy,{{22,22}});game:generate_unit("YuFu60",1,Enum.force.enemy,{{31,22}})
 for _,h in ipairs(rebels)do game:set_unit_invulnerable(h,true)end
 many(game,"JinCoalitionGuard60",{{{{20,34}},{{25,35}},{{28,35}},{{33,34}}}},Enum.force.own);many(game,"JinCoalitionArcher60",{{{{18,33}},{{35,33}}}},Enum.force.own)
 many(game,"SongCoalitionGuard60",{{{{13,30}},{{16,32}},{{38,32}},{{41,30}}}},Enum.force.ally)
 many(game,"PengchengGuard60",{{{{25,26}},{{28,26}},{{23,24}},{{30,24}},{{16,14}},{{38,14}},{{20,8}},{{33,8}}}},Enum.force.enemy)
 many(game,"PengchengArcher60",{{{{19,23}},{{34,23}},{{14,12}},{{40,12}},{{24,6}},{{29,6}}}},Enum.force.enemy)
end
function on_update(game)
 if not gate_open and not game:has_unit("PengchengGuard60") and not game:has_unit("PengchengArcher60") and (game:is_unit_within("JinDaoGong60",{{26,27}},3)or game:is_unit_within("HanJue48",{{26,27}},3)or game:is_unit_within("XunYan58",{{26,27}},3)or game:is_unit_within("LuanYan60",{{26,27}},3))then gate_open=true;for _,h in ipairs(rebels)do game:set_unit_invulnerable(h,false)end;game:push_cmd_speak(0,"向戌登临冲楼车晓谕全城，彭城百姓已经打开南门！生擒鱼石等五人！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if gate_open then for _,h in ipairs(rebels)do if game:has_unit(h)then return Enum.status.undecided end end return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="PengchengRecapture60",turn_limit=30,map={{blocked_edges={{}},size={{54,38}},terrain={{
{terrain}
    }},file="map.bmp"}},deploy={{unselectables={{{{position={{24,33}},hero="JinDaoGong60"}},{{position={{28,33}},hero="HanJue48"}},{{position={{22,35}},hero="XunYan58"}},{{position={{30,35}},hero="LuanYan60"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=14000}}}}
'''


def build_60b() -> str:
    data = manifest("m096", "ch60b")
    intro = [
        ("", "楚国连年与吴国争夺东境。令尹子重死后，公子婴齐继任令尹，命司马尹齐取鸠兹，再遣邓廖率舟师深入吴境。"),
        ("尹齐", "鸠兹已下，吴军新败。邓廖率组甲三百、被练三千，乘胜东进。"),
        ("邓廖", "吴人不习大阵，只要沿水道追击，必能直抵其腹地。"),
        ("", "吴王寿梦病重，世子诸樊代掌军政。他命弟余祭设伏采石，又令弟夷昧领少量舟师诱敌。"),
        ("", "楚军组甲披重铠、被练穿练袍，水上正面列阵极为强悍；吴军因此避其锋锐，只在曲折浅滩设伏。"),
        ("诸樊", "邓廖锐气正盛，不可正面争锋。夷昧且战且退，把楚舟引入采石浅水。"),
        ("夷昧", "我只保留一条退路。楚军若追入浅滩，余祭便从后方截断深水航道。"),
        ("余祭", "伏舟藏在芦苇之后，等邓廖进入采石中央再起。过早现身，只会把他惊走。"),
        ("军令", "夷昧诱使邓廖进入采石范围，余祭伏兵才会出现。浅河可通行，深水不可跨越。"),
    ]
    victory = [
        ("", "余祭伏舟齐出，吴军前后夹击。邓廖舟阵大乱，三千被练几乎尽失，邓廖被吴军生擒。"),
        ("邓廖", "败军之将，唯有一死。我受楚国厚恩，绝不降吴。"),
        ("", "邓廖不屈而死。诸樊乘胜反攻鸠兹，尹齐不能抵挡，弃城退回楚境。"),
        ("", "尹齐自愧丧师失地，归国后忧愤成疾而死。吴国经此一战，声势大振。"),
        ("", "晋悼公闻吴楚相攻，决定趁楚东顾之际，再会诸侯伐郑。诸军随后转向偪阳。"),
        ("军令", "采石水战完成，获得1300金币。下一关：偪阳之战。"),
    ]
    head = stage_head("60b", "吴国伐楚丧邓廖", "第六十回·中", "采石水战",
        "以夷昧诱邓廖进入采石浅滩，触发余祭伏兵；击退邓廖后，诸樊接近鸠兹城池完成收复。诸樊或夷昧被击退则失败。",
        "m096.png", intro, [("余祭", "楚舟已经进入采石，伏军从芦苇后尽出，截断归路！")], victory,
        "诸樊或夷昧被击退，诱敌与反攻失去统领，本关失败。", ["ZhuFan60", "YiMei60"],
        '{{id="jiuzi_castle",name="鸠兹城池",position={55,20},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}}}')
    terrain = terrain_block(data)
    return head + f'''local ambush=false
local deng_down=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("YuJi60",1)end
function on_begin(game)
 game:generate_unit("DengLiao60",1,Enum.force.enemy,{{34,20}});game:generate_unit("YinQi60",1,Enum.force.enemy,{{55,20}});game:set_unit_invulnerable("YinQi60",true)
 many(game,"WuMarine60",{{{{11,7}},{{15,10}},{{20,12}},{{22,16}}}},Enum.force.own);many(game,"WuArcher60",{{{{10,11}},{{18,9}}}},Enum.force.own)
 many(game,"ChuMarine60",{{{{30,18}},{{32,22}},{{35,17}},{{36,23}},{{40,18}},{{42,22}},{{50,18}},{{52,23}}}},Enum.force.enemy)
 many(game,"ChuRiverArcher60",{{{{33,16}},{{38,21}},{{44,19}},{{53,17}},{{56,23}}}},Enum.force.enemy)
end
function on_update(game)
 if not ambush and game:is_unit_within("DengLiao60",{{28,20}},2)then ambush=true;game:generate_unit("YuJi60",1,Enum.force.own,{{40,25}});many(game,"WuMarine60",{{{{38,27}},{{42,26}},{{44,24}}}},Enum.force.own);many(game,"WuArcher60",{{{{39,28}},{{45,25}}}},Enum.force.own);game:push_cmd_speak(0,"余祭伏舟尽出！前军回身夹击，截住邓廖退路！")end
 if ambush and not deng_down and not game:has_unit("DengLiao60")then deng_down=true;game:push_cmd_speak(0,"邓廖被吴军生擒，拒绝投降而死。诸樊立即向东反攻鸠兹！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if ambush and not game:has_unit("YuJi60")then return Enum.status.defeat end if deng_down and game:is_unit_within("ZhuFan60",{{55,20}},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="CaishiBattle60",turn_limit=28,map={{blocked_edges={{}},size={{62,40}},terrain={{
{terrain}
    }},file="map.bmp"}},deploy={{unselectables={{{{position={{18,12}},hero="ZhuFan60"}},{{position={{24,20}},hero="YiMei60"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=13000}}}}
'''


def build_60c() -> str:
    data = manifest("m097", "ch60c")
    intro = [
        ("", "晋悼公会合鲁、宋、卫、曹、莒、邾、滕、薛等国，讨伐依楚的偪阳。偪阳虽小，城池却异常坚固。"),
        ("智罃", "围城二十四日仍未破，军粮将尽。诸军已有退意，但今日若退，天下必轻晋。"),
        ("荀偃", "请再给我与士匄七日。若不能克城，甘受军法。"),
        ("士匄", "我只给诸军六日。六日不下，先斩攻城不力者，再向元帅请罪。"),
        ("仲孙蔑", "鲁将秦堇父、狄虒弥愿先登。北门悬门危险，须有人托住闸板。"),
        ("叔梁纥", "悬门落下时由我举住。诸军只管穿门，不要停在闸下。"),
        ("秦堇父", "城墙不可越，只有北门可进。我和狄虒弥先攀门楼，夺取箭垛。"),
        ("云般", "偪阳虽小，也有死守之士。滚木礌石用尽，便在街巷接战。"),
        ("军令", "接近北门触发悬门事件。暴雨后进入五回合总攻阶段，五回合内击退云般；偪阳君不可直接击退。"),
    ]
    victory = [
        ("", "大雨过后积水渐退。荀偃、士匄督军总攻，秦堇父与狄虒弥先登城头，联军从北门蜂拥而入。"),
        ("", "偪阳箭石俱尽，云般率死士转入街巷。激战中云般阵亡，守军再无统领。"),
        ("偪阳君", "城中军民已经力竭，愿开府库、献城投降，只求保全百姓。"),
        ("智罃", "受降，不许劫掠。偪阳虽小，能守二十余日，其志可敬。"),
        ("", "联军最终只用五日完成最后总攻。悼公本欲把偪阳赐给宋国向戌，向戌辞让，改赐宋国公族。"),
        ("", "归师途中，诸侯又在虎牢会盟。晋悼公的威望达到极盛，中原各国莫敢违命。"),
        ("军令", "偪阳之战完成，获得1600金币。第六十回结束。"),
    ]
    head = stage_head("60c", "智荀偃力伐偪阳", "第六十回·下／第六十一回开端", "偪阳之战",
        "从北门攻入偪阳。悬门事件后坚持至暴雨退水，在五回合总攻期限内击退云般，迫使偪阳君投降。任一具名我军将领被击退则失败。",
        "m097.png", intro, [("叔梁纥", "悬门落下了！我来托住闸板，诸军迅速通过！"), ("士匄", "积水已退，偪阳箭石也将耗尽。五日之内必须破城！")], victory,
        "联军具名将领被击退，或暴雨退水后五回合仍未击退云般，本关失败。",
        ["XunYing54", "XunYan58", "ShiGai60", "ZhongSunMie60", "ShuLiangHe60", "QinJinFu60", "DiSiMi60"],
        '{{id="biyang_palace",name="偪阳城府",position={27,27},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="biyang_west_store",name="偪阳西库",position={17,18},restore_hp=20,restore_mp=10,rewards={}},{id="biyang_east_store",name="偪阳东库",position={38,18},restore_hp=20,restore_mp=10,rewards={}}}')
    terrain = terrain_block(data)
    return head + f'''local gate_event=false
local rain_started=false
local assault_turn=0
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("YunBan60",1,Enum.force.enemy,{{27,25}});game:set_unit_invulnerable("YunBan60",true);game:generate_unit("BiYangLord60",1,Enum.force.enemy,{{27,27}});game:set_unit_invulnerable("BiYangLord60",true)
 many(game,"JinCoalitionGuard60",{{{{17,3}},{{21,2}},{{26,2}},{{31,2}},{{36,3}},{{39,4}}}},Enum.force.own);many(game,"JinCoalitionArcher60",{{{{15,4}},{{41,3}}}},Enum.force.own)
 many(game,"BiYangGuard60",{{{{27,8}},{{28,8}},{{23,11}},{{32,11}},{{18,17}},{{37,17}},{{22,22}},{{33,22}},{{24,29}},{{31,29}}}},Enum.force.enemy)
 many(game,"BiYangArcher60",{{{{20,10}},{{35,10}},{{15,18}},{{40,18}},{{20,26}},{{35,26}}}},Enum.force.enemy)
end
function on_update(game)
 if not gate_event and (game:is_unit_within("QinJinFu60",{{27,7}},2)or game:is_unit_within("DiSiMi60",{{27,7}},2)or game:is_unit_within("ShuLiangHe60",{{27,7}},2))then gate_event=true;game:push_cmd_speak(0,"偪阳悬门突然落下！叔梁纥双手托住闸板，秦堇父、狄虒弥趁势穿门先登！")end
 if not rain_started and game:get_turn_current()>=6 then rain_started=true;assault_turn=game:get_turn_current();game:set_unit_invulnerable("YunBan60",false);game:push_cmd_speak(0,"连日暴雨已经退水，偪阳箭石耗尽！五回合总攻开始，击退云般迫其献城！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if rain_started and game:get_turn_current()>assault_turn+5 and game:has_unit("YunBan60")then return Enum.status.defeat end if rain_started and not game:has_unit("YunBan60")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="BiyangSiege60",turn_limit=28,map={{blocked_edges={{}},size={{56,42}},terrain={{
{terrain}
    }},file="map.bmp"}},deploy={{unselectables={{{{position={{24,3}},hero="XunYing54"}},{{position={{29,3}},hero="XunYan58"}},{{position={{19,4}},hero="ShiGai60"}},{{position={{34,4}},hero="ZhongSunMie60"}},{{position={{26,5}},hero="ShuLiangHe60"}},{{position={{22,5}},hero="QinJinFu60"}},{{position={{31,5}},hero="DiSiMi60"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=16000}}}}
'''


def patch_config() -> None:
    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    if 'id = "JinDaoGong60"' not in text:
        text = text.replace('        ,{ id = "TuHouseArcher59", class = "Archer", stat = {85, 92, 88, 89, 87}, model = "archer-1-blue" }    },',
                            '        ,{ id = "TuHouseArcher59", class = "Archer", stat = {85, 92, 88, 89, 87}, model = "archer-1-blue" }' + HEROES + '    },')
    text = text.replace('"57", "58", "59a", "59b" }', '"57", "58", "59a", "59b", "60a", "60b", "60c" }')
    path.write_text(text, encoding="utf-8")


def patch_save() -> None:
    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('STAGE_TABLE_VERSION = 3', 'STAGE_TABLE_VERSION = 4')
    text = text.replace('"57","58","59a","59b"\n)', '"57","58","59a","59b","60a","60b","60c"\n)')
    path.write_text(text, encoding="utf-8")


def patch_gui() -> None:
    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m095.png"]' in text:
        return
    block = '''

_LARGE_BATTLE_MAPS["m095.png"] = (54, 38, 48)
_LARGE_BATTLE_MAPS["m096.png"] = (62, 40, 48)
_LARGE_BATTLE_MAPS["m097.png"] = (56, 42, 48)
HERO_LABELS.update({
    "JinDaoGong60":"晋悼公","LuanYan60":"栾黡","XiangShu60":"向戌","ZhongSunMie60":"仲孙蔑",
    "YuShi60":"鱼石","XiangWeiRen60":"向为人","LinZhu60":"鳞朱","XiangDai60":"向带","YuFu60":"鱼府",
    "JinCoalitionGuard60":"晋国联军甲士","JinCoalitionArcher60":"晋国联军弓手","SongCoalitionGuard60":"宋国联军",
    "PengchengGuard60":"彭城楚军","PengchengArcher60":"彭城楚弓手","ZhuFan60":"诸樊","YiMei60":"夷昧","YuJi60":"余祭",
    "DengLiao60":"邓廖","YinQi60":"尹齐","WuMarine60":"吴国舟师","WuArcher60":"吴国弓手","ChuMarine60":"楚国舟师",
    "ChuRiverArcher60":"楚国舟弓手","ShiGai60":"士匄","ShuLiangHe60":"叔梁纥","QinJinFu60":"秦堇父","DiSiMi60":"狄虒弥",
    "YunBan60":"云般","BiYangLord60":"偪阳君","BiYangGuard60":"偪阳守军","BiYangArcher60":"偪阳弓手"
})
HERO_BIOS.update({
    "JinDaoGong60":"晋国君主周，整顿厉公乱政，任用韩厥、智罃、魏绛等人，多次会合诸侯，恢复晋国霸业。",
    "LuanYan60":"晋国卿大夫栾黡，栾书之子。晋悼公时期参与彭城、偪阳等诸侯会战。",
    "XiangShu60":"宋国大夫向戌。彭城被楚军占据后，以临冲楼车晓谕城中百姓，促使百姓开门擒拿五名叛臣。",
    "ZhongSunMie60":"鲁国正卿仲孙蔑，即孟献子。参与诸侯收复彭城及围攻偪阳，治政崇尚俭朴。",
    "YuShi60":"宋国逃臣鱼石，借楚军攻占彭城，与向为人等据城，后被城中百姓擒获并处死。",
    "XiangWeiRen60":"宋国逃臣向为人，随鱼石依附楚国并据守彭城，诸侯收复彭城后被擒。",
    "LinZhu60":"宋国逃臣鳞朱，依楚返宋据守彭城，最终与鱼石等一同被擒。",
    "XiangDai60":"宋国逃臣向带，参与据守彭城，城中百姓开门后被诸侯联军擒获。",
    "YuFu60":"宋国逃臣鱼府，借楚力据守彭城，城破后与其余四人一同伏法。",
    "ZhuFan60":"吴王寿梦长子诸樊。寿梦病重时主持军政，命夷昧诱敌、余祭伏击，在采石大破楚军。",
    "YiMei60":"吴王寿梦之子夷昧。采石之战率少量舟师诱使邓廖深入，为余祭伏兵创造夹击机会。",
    "YuJi60":"吴王寿梦之子余祭。率舟师埋伏采石，待邓廖深入后截断归路，协助吴军大破楚师。",
    "DengLiao60":"楚国将领，率组甲、被练深入吴境，在采石遭吴军伏击被俘，拒绝投降而死。",
    "YinQi60":"楚国司马尹齐，攻取鸠兹并遣邓廖深入吴境；邓廖败亡、鸠兹失守后忧愤成疾。",
    "ShiGai60":"晋国卿大夫士匄，范文子之子。偪阳久攻不克时请限期督战，最终率联军完成总攻。",
    "ShuLiangHe60":"鲁国勇士叔梁纥，孔子之父。偪阳攻城时力举落下的悬门，使诸侯军得以穿门入城。",
    "QinJinFu60":"鲁国将领秦堇父，偪阳攻城时与狄虒弥奋勇先登，率军突入城中。",
    "DiSiMi60":"鲁国勇士狄虒弥，偪阳之战随秦堇父攀城先登，在北门突破中建立战功。",
    "YunBan60":"偪阳守将云般。城中箭石耗尽后仍率死士巷战，最终战死，偪阳随即投降。",
    "BiYangLord60":"偪阳小国之君。守城二十余日后军民力竭，于云般战死后献城投降。"
})
PORTRAIT_INDEX_BY_HERO.update({"JinDaoGong60":7,"LuanYan60":35,"XiangShu60":49,"ZhongSunMie60":42,"YuShi60":45,"XiangWeiRen60":34,"LinZhu60":33,"XiangDai60":38,"YuFu60":25,"ZhuFan60":7,"YiMei60":35,"YuJi60":38,"DengLiao60":34,"YinQi60":45,"ShiGai60":35,"ShuLiangHe60":25,"QinJinFu60":33,"DiSiMi60":34,"YunBan60":38,"BiYangLord60":8})
SPEAKER_PORTRAIT_INDEX.update({"晋悼公":7,"向戌":49,"仲孙蔑":42,"鱼石":45,"栾黡":35,"尹齐":45,"邓廖":34,"诸樊":7,"夷昧":35,"余祭":38,"智罃":35,"荀偃":37,"士匄":35,"叔梁纥":25,"秦堇父":33,"云般":38,"偪阳君":8})
HISTORICAL_DEATH_HEROES.update({"YuShi60","XiangWeiRen60","LinZhu60","XiangDai60","YuFu60","DengLiao60","YinQi60","YunBan60"})
'''
    marker = '\nif _original_name == "__main__":'
    text = text.replace(marker, block + marker)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    (ROOT / "game/sce/dongzhou/stage/60a.lua").write_text(build_60a(), encoding="utf-8")
    (ROOT / "game/sce/dongzhou/stage/60b.lua").write_text(build_60b(), encoding="utf-8")
    (ROOT / "game/sce/dongzhou/stage/60c.lua").write_text(build_60c(), encoding="utf-8")
    patch_config(); patch_save(); patch_gui()
    print("chapter 60 integrated: 60a, 60b, 60c")


if __name__ == "__main__":
    main()
