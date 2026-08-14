from __future__ import annotations
import json
from pathlib import Path
import integrate_chapter60 as shared
ROOT=Path(__file__).resolve().parents[1]
HEROES='''
        ,{ id = "GongSunMianYu66", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-red" }
        ,{ id = "LuPuBie66", class = "Strategist", stat = {93,88,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "QuJian66", class = "Strategist", stat = {94,88,98,95,93}, model = "Strategist-1-red" }
        ,{ id = "ZiJiang66", class = "Cavalry", stat = {91,95,90,92,90}, model = "cavalry-1-red" }
        ,{ id = "XiHuan66", class = "Strategist", stat = {90,87,96,92,90}, model = "Strategist-1-red" }
        ,{ id = "QuHuYong66", class = "Strategist", stat = {93,86,97,94,91}, model = "Strategist-1-blue" }
        ,{ id = "ShuJiuLord66", class = "Lord", stat = {87,86,89,88,86}, model = "lord-1-blue" }
        ,{ id = "ChuanFengShu66", class = "Cavalry", stat = {91,96,87,92,90}, model = "cavalry-1-red" }
        ,{ id = "GongZiWei66", class = "Cavalry", stat = {92,95,93,93,91}, model = "cavalry-1-red" }
        ,{ id = "HuangJie66", class = "Cavalry", stat = {89,94,87,90,88}, model = "cavalry-1-blue" }
        ,{ id = "SunAmbusher66", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-red" }
        ,{ id = "WeiRaider66", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "NingGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }
        ,{ id = "CuiGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "ChuShujuGuard66", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChuShujuArcher66", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "WuReliefGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "WuReliefArcher66", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "ZhengGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }'''
def data(mid,suffix):return json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
def head(chapter,battle,objective,asset,intro,victory,defeat,commanders,sites,events):return shared.stage_head("","杀宁喜子鱄出奔 戮崔杼庆封独相",chapter,battle,objective,asset,intro,events,victory,defeat,commanders,sites)
def many_lua():return 'local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end\n'

def stage_a():
 d=data("m111","ch66a");intro=[("","殖绰率卫国千人袭杀茅氏三百晋卒。孙林父命孙蒯、雍鉏回击，二人忌惮殖绰勇力，决定设伏。"),("雍鉏","我只带百人诈败，把殖绰引往圉村；将军在土山下掘坑覆草，以言语激他驱车上山。"),("孙蒯","殖绰若带全军，不可力敌；他恃勇轻追，进入村口两格陷坑后弓弩齐发。"),("殖绰","擒得孙蒯，便如擒半个孙林父。区区土山，驱车直上！"),("军令","雍鉏诱殖绰进入圉村陷坑，解除其保护后击退。孙蒯、雍鉏任一被击退均失败。")];victory=[("","殖绰轻车追至圉村，被孙蒯辱骂激怒，驱车上坡时马车陷入覆草深坑。"),("","孙氏伏弩齐发，殖绰死于坑中。孙蒯斩其首级，杀散卫军，却向晋国隐瞒胜讯。"),("","晋平公因三百戍卒被杀而囚卫献公；晏婴、羊舌肸力谏，献公与宁喜献女乐后获释。"),("军令","圉村伏殖绰完成，获得800金币。下一关：宁府诛喜。")]
 text=head("第六十六回·上","圉村伏殖绰","诱殖绰进入陷坑并击退。","m111.png",intro,victory,"孙蒯或雍鉏被击退，或超过二十回合，失败。",["SunKuai61","YongChu65"],"{}",[("雍鉏","殖绰已追入林道，继续向圉村诱敌！"),("孙蒯","坑上覆草已破，弓弩齐发！")]);rows=shared.terrain_block(d)
 return text+many_lua()+f'''local trapped=false
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("ZhiChuo62",1,Enum.force.enemy,{{17,20}});game:set_unit_invulnerable("ZhiChuo62",true);many(game,"WeiRaider66",{{{{14,16}},{{14,19}},{{14,23}},{{18,16}},{{18,24}}}},Enum.force.enemy);many(game,"SunAmbusher66",{{{{43,15}},{{45,19}},{{44,23}},{{39,15}},{{39,24}}}},Enum.force.own)end
function on_update(game)if not trapped and game:is_unit_within("ZhiChuo62",{{41,19}},1)then trapped=true;game:set_unit_invulnerable("ZhiChuo62",false);game:push_cmd_speak(0,"殖绰车马坠入陷坑，伏弩齐发！")end end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if trapped and not game:has_unit("ZhiChuo62")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="YuVillageTrap66",turn_limit=20,map={{blocked_edges={{}},size={{56,40}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{46,17}},hero="SunKuai61"}},{{position={{31,22}},hero="YongChu65"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=8000}}}}
'''

def stage_b():
 d=data("m112","ch66b");intro=[("","宋国向戌倡导晋楚弭兵。宁喜不经卫献公便遣石恶赴会，自称政权归宁氏，引起献公不满。"),("","公孙无地、公孙臣先攻宁府，误触伏机，一死一擒；宁喜将无地鞭杀。"),("公孙免馀","宁氏开门处理俘虏，正是乘门而入之机。先截右宰谷，再围宁喜于堂柱。"),("宁喜","我迎故君复位，卫国政事本应归我。何人敢趁春宴犯宁氏？"),("军令","攻入宁府，击退右宰谷与宁喜。公孙免馀被击退即失败。")];victory=[("","右宰谷夜车来问，刚入门便被公孙免馀截杀。宁喜绕堂柱逃走，身中两剑而死。"),("","卫献公陈宁喜、右宰谷尸于朝。公子鱄因自认失信，携妻子出奔晋国，终身不再入卫。"),("","献公任太叔仪执政，卫国暂安；石恶因闻宁喜被杀，不敢归卫而留在晋国。"),("军令","宁府诛喜完成，获得700金币。下一关：崔氏覆灭。")]
 text=head("第六十六回·中一","宁府诛喜","攻入宁府，击退右宰谷与宁喜。","m112.png",intro,victory,"公孙免馀被击退或超过十八回合，失败。",["GongSunMianYu66"],'{{id="ning_hall",name="宁氏正堂",position={25,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="ning_store",name="宁氏府库",position={17,23},restore_hp=20,restore_mp=10,rewards={}}}',[("公孙免馀","宁府门启，随我突入！"),("宁喜","绕柱结阵，挡住来兵！")]);rows=shared.terrain_block(d)
 return text+many_lua()+f'''function on_deploy(game)game:appoint_hero("GongSunMianYu66",1)end
function on_begin(game)game:generate_unit("NingXi65",1,Enum.force.enemy,{{25,10}});game:generate_unit("YouZaiGu65",1,Enum.force.enemy,{{17,23}});many(game,"NingGuard66",{{{{22,29}},{{26,29}},{{30,29}},{{20,24}},{{28,24}},{{22,18}},{{27,18}}}},Enum.force.enemy);many(game,"QingGuard66",{{{{20,34}},{{24,34}},{{28,34}},{{32,34}}}},Enum.force.own)end function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("GongSunMianYu66")then return Enum.status.defeat end if not game:has_unit("NingXi65") and not game:has_unit("YouZaiGu65")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="NingManorCoup66",turn_limit=18,map={{blocked_edges={{}},size={{50,38}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{24,35}},hero="GongSunMianYu66"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=7000}}}}
'''

def stage_c():
 d=data("m108","ch66c");intro=[("","崔杼许立幼子崔明，崔成、崔疆不满东郭偃、棠无咎把持宗邑，转向庆封求援。"),("","庆封赠甲百具，使二人先杀东郭偃、棠无咎，又暗令卢蒲嫳带家甲进入崔府。"),("卢蒲嫳","我奉左相之命而来。开门之后先封住内院，崔成、崔疆一个也不能走。"),("崔疆","庆氏兵马或许是来助我除掉崔明。开门纳军，不必防备。"),("军令","击退崔成、崔疆。庆封、卢蒲嫳任一被击退均失败。")];victory=[("","崔成、崔疆开门纳入庆氏甲兵，卢蒲嫳当场翻脸，将二人斩首并抄毁家产。"),("","棠姜自缢。崔杼回府见家门尽毁，自知被庆封出卖，也在内室自缢。"),("","崔明盗取父母尸身合葬后奔鲁，庆封以讨弑君者为名，独相齐景公。"),("军令","崔氏覆灭完成，获得700金币。下一关：舒鸠之战。")]
 text=head("第六十六回·中二","崔氏覆灭","击退崔成、崔疆，控制崔氏府。","m108.png",intro,victory,"庆封或卢蒲嫳被击退，或超过十八回合，失败。",["QingFeng62","LuPuBie66"],'{{id="cui_inner",name="崔氏内宅",position={24,9},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="cui_store",name="崔氏府库",position={15,24},restore_hp=20,restore_mp=10,rewards={}}}',[("卢蒲嫳","崔氏开门，甲士尽入！"),("崔成","庆氏不是援军，立即封锁内院！")]);rows=shared.terrain_block(d)
 return text+many_lua()+f'''function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("CuiCheng65",1,Enum.force.enemy,{{20,15}});game:generate_unit("CuiJiang65",1,Enum.force.enemy,{{29,15}});many(game,"CuiGuard66",{{{{18,13}},{{23,13}},{{27,13}},{{32,13}},{{20,20}},{{29,20}}}},Enum.force.enemy);many(game,"QingGuard66",{{{{20,28}},{{24,29}},{{28,29}},{{32,28}}}},Enum.force.own)end function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if not game:has_unit("CuiCheng65") and not game:has_unit("CuiJiang65")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="CuiClanCollapse66",turn_limit=18,map={{blocked_edges={{}},size={{50,38}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{19,29}},hero="QingFeng62"}},{{position={{24,30}},hero="LuPuBie66"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=7000}}}}
'''

def stage_d():
 d=data("m113","ch66d");intro=[("","吴王馀祭诱舒鸠叛楚，楚令尹屈建率军讨伐。老将养由基坚持为先锋，在离城迎击吴国救兵。"),("","养由基追击过深，被吴国铁叶车与江南射手四面围住，死于万箭之下。"),("屈建","养叔已死，不可再凭勇力。子疆诈败引夷昧至栭山，楚军伏于栖山林中。"),("子疆","吴军离开水路又远离营壁，待其全军进入山口，我回军反击。"),("军令","在栭山击退夷昧、屈狐庸，再攻入舒鸠西门并击退舒鸠君。三名楚将不得被击退。")];victory=[("","夷昧误认楚军逃遁，倾营追至栭山。子疆回军，屈建伏兵四起，将吴军围住。"),("","屈狐庸奋力救出夷昧，吴国援军败归。楚军乘势攻入舒鸠，灭其国。"),("","次年楚秦联军伐吴受阻，转兵侵郑；棘泽阵前又发生争夺俘虏之事。"),("军令","舒鸠之战完成，获得1100金币。下一关：棘泽擒将。")]
 text=head("第六十六回·中三","舒鸠之战","击退吴国救军并攻取舒鸠。","m113.png",intro,victory,"屈建、子疆、息桓任一被击退，或超过二十八回合，失败。",["QuJian66","ZiJiang66","XiHuan66"],'{{id="shuju_center",name="舒鸠中营",position={56,16},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="shuju_store",name="舒鸠后营",position={57,29},restore_hp=20,restore_mp=10,rewards={}}}',[("子疆","吴军已入栭山，伏兵起！"),("屈建","吴援败退，转攻舒鸠西门！")]);rows=shared.terrain_block(d)
 return text+many_lua()+f'''local relief_down=false
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("YiMei60",1,Enum.force.enemy,{{34,20}});game:generate_unit("QuHuYong66",1,Enum.force.enemy,{{38,24}});game:generate_unit("ShuJiuLord66",1,Enum.force.enemy,{{56,16}});game:set_unit_invulnerable("ShuJiuLord66",true);many(game,"WuReliefGuard66",{{{{31,17}},{{31,22}},{{34,25}},{{38,19}},{{41,22}}}},Enum.force.enemy);many(game,"WuReliefArcher66",{{{{33,15}},{{36,27}},{{40,17}},{{42,25}}}},Enum.force.enemy);many(game,"ChuShujuGuard66",{{{{12,17}},{{12,23}},{{16,18}},{{16,26}}}},Enum.force.own);many(game,"ChuShujuArcher66",{{{{10,20}},{{18,16}},{{19,27}}}},Enum.force.own)end
function on_update(game)if not relief_down and not game:has_unit("YiMei60") and not game:has_unit("QuHuYong66")then relief_down=true;game:set_unit_invulnerable("ShuJiuLord66",false);game:push_cmd_speak(0,"吴国救军已退，舒鸠西门失去外援！")end end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if relief_down and not game:has_unit("ShuJiuLord66")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="ShujuCampaign66",turn_limit=28,map={{blocked_edges={{}},size={{68,46}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{14,20}},hero="QuJian66"}},{{position={{17,24}},hero="ZiJiang66"}},{{position={{21,21}},hero="XiHuan66"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=11000}}}}
'''

def stage_e():
 d=data("m114","ch66e");intro=[("","楚秦伐吴无功，楚军回师侵郑。大夫穿封戍在棘泽迎战郑军，王子围随军争功。"),("穿封戍","皇颉在前阵。我亲自冲车截住他，王子围守住侧翼即可。"),("公子围","俘获敌将是全军首功。谁先把皇颉押到中军，功劳便归谁。"),("皇颉","楚军两路逼近，郑军结阵后撤，不可陷在浅泽中央。"),("军令","击退皇颉即视为俘获。穿封戍、公子围任一被击退均失败。")];victory=[("","穿封戍在阵中擒住皇颉，公子围却抢先向楚康王报功，称俘虏为自己所得。"),("","伯州犁审问皇颉时上下指手，暗示应奉承王子围。皇颉遂称自己败于王子围。"),("","穿封戍愤怒拔戈追逐公子围。楚康王最终将功劳平分，留下“上下其手”的典故。"),("","吴王馀祭后来伐越，醉卧馀皇大舟，被守船越俘夺刀刺死；其弟夷昧继位，任季札通聘列国。"),("军令","棘泽擒将完成，获得700金币。第六十六回结束。")]
 text=head("第六十六回·下","棘泽擒将","击退并俘获郑将皇颉。","m114.png",intro,victory,"穿封戍或公子围被击退，或超过十八回合，失败。",["ChuanFengShu66","GongZiWei66"],"{}",[("穿封戍","皇颉阵脚已乱，随我截住他的战车！"),("公子围","拿住郑将，立即送往中军！")]);rows=shared.terrain_block(d)
 return text+many_lua()+f'''function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("HuangJie66",1,Enum.force.enemy,{{45,21}});many(game,"ZhengGuard66",{{{{42,17}},{{42,21}},{{42,25}},{{47,17}},{{47,25}},{{50,20}},{{50,23}}}},Enum.force.enemy);many(game,"ChuShujuGuard66",{{{{12,17}},{{12,23}},{{17,18}},{{17,25}}}},Enum.force.own)end function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if not game:has_unit("HuangJie66")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="JizeCapture66",turn_limit=18,map={{blocked_edges={{}},size={{60,42}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{14,20}},hero="ChuanFengShu66"}},{{position={{18,23}},hero="GongZiWei66"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=7000}}}}
'''

def patch_all():
 for sid,text in (("66a",stage_a()),("66b",stage_b()),("66c",stage_c()),("66d",stage_d()),("66e",stage_e())):(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").write_text(text,encoding="utf-8")
 p=ROOT/"game/sce/dongzhou/config.lua";t=p.read_text(encoding="utf-8")
 if 'id = "GongSunMianYu66"' not in t:t=t.replace('        ,{ id = "NingHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }    },','        ,{ id = "NingHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }'+HEROES+'    },')
 t=t.replace('"65a", "65b", "65c" }','"65a", "65b", "65c", "66a", "66b", "66c", "66d", "66e" }');p.write_text(t,encoding="utf-8")
 p=ROOT/"rl/save_system.py";t=p.read_text(encoding="utf-8").replace('STAGE_TABLE_VERSION = 9','STAGE_TABLE_VERSION = 10').replace('"65a","65b","65c"\n)','"65a","65b","65c","66a","66b","66c","66d","66e"\n)');p.write_text(t,encoding="utf-8")
 p=ROOT/"rl/play_gui.py";t=p.read_text(encoding="utf-8")
 if '_LARGE_BATTLE_MAPS["m111.png"]' not in t:
  block='''
_LARGE_BATTLE_MAPS["m111.png"]=(56,40,48)
_LARGE_BATTLE_MAPS["m112.png"]=(50,38,48)
_LARGE_BATTLE_MAPS["m113.png"]=(68,46,48)
_LARGE_BATTLE_MAPS["m114.png"]=(60,42,48)
HERO_LABELS.update({"GongSunMianYu66":"公孙免馀","LuPuBie66":"卢蒲嫳","QuJian66":"屈建","ZiJiang66":"子疆","XiHuan66":"息桓","QuHuYong66":"屈狐庸","ShuJiuLord66":"舒鸠君","ChuanFengShu66":"穿封戍","GongZiWei66":"公子围","HuangJie66":"皇颉","SunAmbusher66":"孙氏伏弩","WeiRaider66":"卫国袭兵","NingGuard66":"宁氏家甲","QingGuard66":"庆氏家甲","CuiGuard66":"崔氏家甲","ChuShujuGuard66":"楚军甲士","ChuShujuArcher66":"楚军弓手","WuReliefGuard66":"吴国援兵","WuReliefArcher66":"吴国弓手","ZhengGuard66":"郑军甲士"})
HERO_BIOS.update({"GongSunMianYu66":"卫国大夫，趁宁府开门率家甲攻入，杀右宰谷、宁喜。","LuPuBie66":"庆封家臣，诱崔成、崔疆开门后将二人斩首，助庆氏独掌齐政。","QuJian66":"楚国令尹，舒鸠之战设伏栭山，击退吴国援军并灭舒鸠。","ZiJiang66":"楚国将领，奉屈建之命诈败诱吴军进入栭山伏击圈。","XiHuan66":"楚国大夫，随养由基出征舒鸠，收拾败军参与后续伏击。","QuHuYong66":"吴国相国，率兵救援舒鸠，在栭山救出夷昧后败退。","ShuJiuLord66":"舒鸠国君，受吴国诱使叛楚，吴援失败后亡国。","ChuanFengShu66":"楚国县尹，棘泽阵前亲手俘获郑将皇颉，却被公子围争功。","GongZiWei66":"楚康王之弟，棘泽之战与穿封戍争夺擒将之功。","HuangJie66":"郑国将领，棘泽兵败被穿封戍擒获，后在伯州犁暗示下改口。"})
PORTRAIT_INDEX_BY_HERO.update({"GongSunMianYu66":35,"LuPuBie66":49,"QuJian66":49,"ZiJiang66":35,"XiHuan66":49,"QuHuYong66":49,"ShuJiuLord66":8,"ChuanFengShu66":35,"GongZiWei66":38,"HuangJie66":34})
SPEAKER_PORTRAIT_INDEX.update({"雍鉏":25,"孙蒯":35,"殖绰":35,"公孙免馀":35,"宁喜":49,"卢蒲嫳":49,"崔成":34,"屈建":49,"子疆":35,"穿封戍":35,"公子围":38,"皇颉":34})
HISTORICAL_DEATH_HEROES.update({"ZhiChuo62","NingXi65","YouZaiGu65","CuiCheng65","CuiJiang65","TangWuJiu65","DongGuoYan65","CuiZhu62"})
'''
  t=t.replace('\nif _original_name == "__main__":',block+'\nif _original_name == "__main__":')
 p.write_text(t,encoding="utf-8")
if __name__=="__main__":patch_all();print("chapter 66 integrated: 66a-66e")
