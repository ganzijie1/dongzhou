from __future__ import annotations
import json
from pathlib import Path
import integrate_chapter60 as shared

ROOT=Path(__file__).resolve().parents[1]
HEROES='''
        ,{ id = "TangWuJiu65", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "CuiCheng65", class = "Cavalry", stat = {88,93,85,90,87}, model = "cavalry-1-red" }
        ,{ id = "CuiJiang65", class = "Cavalry", stat = {89,94,85,90,88}, model = "cavalry-1-red" }
        ,{ id = "DongGuoYan65", class = "Strategist", stat = {91,84,96,92,90}, model = "Strategist-1-red" }
        ,{ id = "JiaJu65", class = "Cavalry", stat = {89,95,84,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ZhouChuoQi65", class = "Cavalry", stat = {91,97,86,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GongSunAo65", class = "Infantry", stat = {90,96,84,91,89}, model = "infantry-1-blue" }
        ,{ id = "LouYan65", class = "Infantry", stat = {88,94,83,89,87}, model = "infantry-1-blue" }
        ,{ id = "CuiAmbusher65", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "QiBraveGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "NiuChen65", class = "Archer", stat = {90,96,89,92,90}, model = "archer-1-red" }
        ,{ id = "ChaoGuard65", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "WuGateGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "WuGateArcher65", class = "Archer", stat = {88,94,90,91,89}, model = "archer-1-blue" }
        ,{ id = "NingXi65", class = "Strategist", stat = {93,87,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "YouZaiGu65", class = "Strategist", stat = {91,84,96,92,91}, model = "Strategist-1-red" }
        ,{ id = "BeiGongYi65", class = "Cavalry", stat = {90,94,88,91,89}, model = "cavalry-1-red" }
        ,{ id = "SunXiang65", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ChuDai65", class = "Archer", stat = {90,96,88,92,90}, model = "archer-1-blue" }
        ,{ id = "YongChu65", class = "Infantry", stat = {89,94,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "WeiShangGong65", class = "Lord", stat = {88,90,86,88,85}, model = "lord-1-blue" }
        ,{ id = "TaiZiJiao65", class = "Cavalry", stat = {87,92,83,88,86}, model = "cavalry-1-blue" }
        ,{ id = "SunHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "SunHouseArcher65", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "NingHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }'''

def data(mid,suffix):return json.loads((ROOT/f"assets/lzc/map_sources/{mid}_{suffix}_manifest.json").read_text(encoding="utf-8"))
def head(chapter,title,battle,objective,asset,intro,victory,defeat,commanders,sites,events):return shared.stage_head("",title,chapter,battle,objective,asset,intro,events,victory,defeat,commanders,sites)

def stage_a():
    d=data("m108","ch65a")
    intro=[("","莒黎比公入临淄朝齐，齐庄公在北郭设宴。崔杼诈称有病，诱使庄公宴后到崔府问疾。"),("","齐庄公私通棠姜已久，以为崔杼病重，便带贾举、州绰、公孙敖、偻堙等勇士前往。"),("东郭偃","州绰等人留在外舍饮酒，先盗走兵器；府内鸣钟后，门外伏甲同时发动。"),("棠无咎","内室左右已伏甲百人。庄公入楼后封闭后门，以钟声为号，不许任何人越墙。"),("齐庄公","寡人愿与崔相立盟，甚至到太庙自尽谢罪，只求放开一条生路。"),("棠无咎","我等只奉命捉拿淫贼，不知有君。花台与墙头均有弓手，休想逃走。"),("州绰","我受齐侯知遇，今日纵无兵器，也不能苟活而事新主。"),("军令","击退齐庄公及贾举、州绰、公孙敖、偻堙。崔氏四名具名角色任一被击退均失败。")]
    victory=[("","齐庄公破后户登楼，又跳上花台欲翻墙，被棠无咎射中左股，坠墙后遭伏甲刺杀。"),("","贾举入中门时被绊索绊倒，崔疆将其击杀；公孙敖奋力折断崔成手臂，最终也被长戈刺死。"),("","偻堙被州绰误投车石打断一足，旋即战死；州绰不肯降服，以头撞墙自尽。"),("","邴师、封具、铎父、襄尹等勇爵之士先后殉死，王何奔莒，卢蒲癸奔晋。"),("","晏婴伏在庄公尸身上痛哭三踊。崔杼不敢杀贤，随后迎公子杵臼为齐景公。"),("","太史伯与两名弟弟因直书“崔杼弑其君光”相继被杀，第三弟仍不改书，崔杼终于退让。"),("军令","崔府之变完成，获得900金币。下一关：巢门伏射。")]
    text=head("第六十五回·上","弑齐光崔庆专权 纳卫衎甯喜擅政","崔府之变","击退齐庄公及随行勇士，控制崔氏府第。","m108.png",intro,victory,"棠无咎、崔成、崔疆、东郭偃任一被击退，或超过二十二回合，失败。",["TangWuJiu65","CuiCheng65","CuiJiang65","DongGuoYan65"],
              '{{id="cui_inner",name="崔氏内宅",position={24,9},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="cui_store",name="崔氏府库",position={15,24},restore_hp=20,restore_mp=10,rewards={}}}',[("棠无咎","钟声已响，封锁后户与花台！"),("齐庄公","寡人知罪，愿与崔相面盟！"),("州绰","兵器虽失，州绰尚有一命可报君恩！")])
    rows=shared.terrain_block(d);targets='{"QiZhuangGong62","JiaJu65","ZhouChuoQi65","GongSunAo65","LouYan65"}'
    return text+f'''local targets={targets}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("QiZhuangGong62",1,Enum.force.enemy,{{24,22}});game:generate_unit("JiaJu65",1,Enum.force.enemy,{{25,20}});game:generate_unit("ZhouChuoQi65",1,Enum.force.enemy,{{22,29}});game:generate_unit("GongSunAo65",1,Enum.force.enemy,{{27,29}});game:generate_unit("LouYan65",1,Enum.force.enemy,{{30,28}});many(game,"CuiAmbusher65",{{{{18,13}},{{22,13}},{{27,13}},{{31,13}},{{18,19}},{{21,20}},{{28,20}},{{32,19}}}},Enum.force.own);many(game,"QiBraveGuard65",{{{{20,25}},{{24,26}},{{28,25}},{{24,29}}}},Enum.force.enemy)end
function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end for _,h in ipairs(targets)do if game:has_unit(h)then return Enum.status.undecided end end return Enum.status.victory end
gstage={{title_id="CuiManorRegicide65",turn_limit=22,map={{blocked_edges={{}},size={{50,38}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{24,9}},hero="TangWuJiu65"}},{{position={{20,15}},hero="CuiCheng65"}},{{position={{29,15}},hero="CuiJiang65"}},{{position={{15,24}},hero="DongGuoYan65"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=9000}}}}
'''

def stage_b():
    d=data("m109","ch65b")
    intro=[("","齐庄公死后，晋平公原欲会诸侯伐齐；崔杼、庆封归还朝歌并献宗器，晋齐重新讲和。"),("","同年吴王诸樊率军伐楚，行至巢邑，亲自逼近城门督战。"),("牛臣","吴王恃勇近门。我藏在门外短墙之后，待他进入两格射程再发箭。"),("吴王诸樊","小小巢门，岂能挡我吴军？步卒压住两翼，寡人亲到门下察看虚实。"),("军令","牛臣依托短墙射击吴王诸樊。牛臣被击退即失败，击退诸樊完成本关。")]
    victory=[("","诸樊逼近巢门时，牛臣从短墙后突然发箭，正中吴王。吴军抢回主君，随即停止攻城。"),("","诸樊伤重而死。吴国群臣遵从寿梦遗命，不立其子，而立弟馀祭为王。"),("吴王馀祭","兄弟四人依次传位，最终应当传给季札。若人人寿终，季札已老，故我也不敢恋位。"),("军令","巢门伏射完成，获得600金币。下一关：帝丘复君。")]
    text=head("第六十五回·中","弑齐光崔庆专权 纳卫衎甯喜擅政","巢门伏射","依托短墙击退吴王诸樊。","m109.png",intro,victory,"牛臣被击退或超过十八回合，本关失败。",["NiuChen65"],
              '{{id="chao_city",name="巢城",position={43,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}',[("牛臣","吴王已近短墙，弓手屏息，待我先发！"),("吴王诸樊","攻开巢门，今日不必扎营！")])
    rows=shared.terrain_block(d)
    return text+f'''local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("ZhuFan60",1,Enum.force.enemy,{{22,17}});many(game,"ChaoGuard65",{{{{31,14}},{{31,18}},{{31,22}}}},Enum.force.own);many(game,"WuGateGuard65",{{{{17,14}},{{17,18}},{{17,22}},{{21,14}},{{21,21}}}},Enum.force.enemy);many(game,"WuGateArcher65",{{{{14,16}},{{14,20}},{{19,11}},{{19,25}}}},Enum.force.enemy)end
function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("NiuChen65")then return Enum.status.defeat end if not game:has_unit("ZhuFan60")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="ChaoGateAmbush65",turn_limit=18,map={{blocked_edges={{}},size={{52,36}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{30,16}},hero="NiuChen65"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=6000}}}}
'''

def stage_c():
    d=data("m110","ch65c")
    intro=[("","卫献公衎被逐多年。宁殖临终命其子宁喜迎故君复位，以洗去宁氏参与逐君的污名。"),("","献公据夷仪，许诺复国后政事尽归宁喜。公子鱄为双方作证，宁喜遂开始联络石恶、北宫遗等人。"),("右宰谷","献公言语仍如旧日，未必守约；但孙嘉出使、孙林父与孙蒯皆在戚邑，如今只有孙襄守帝丘。"),("宁喜","父命不可违。先攻孙氏府，夺其家甲；若一次不成，夜间趁孙襄伤重再攻。"),("褚带","孙氏府墙坚厚，家甲千人。弓手轮番守楼，宁氏休想靠一次冲锋破门。"),("公孙丁","孙襄若出门追击，我可在街口以箭截住。他一倒，孙氏家甲必乱。"),("卫殇公","寡人在位十三年并无失德。宁喜若敢擅废君主，便是真正的叛臣。"),("军令","先击退孙襄；随后夜破孙氏府，击退褚带；最后进入卫宫，击退卫殇公与世子角。雍鉏按原著逃往戚邑。")]
    victory=[("","右宰谷初攻孙府不利，孙襄出门追击，被公孙丁一箭射中胸口，回府后伤重而死。"),("","宁喜三更再攻，孙氏家甲因无主而溃散。雍鉏越后墙逃往戚邑，褚带被乱军杀死。"),("","宁喜持孙襄首级入宫，逼卫殇公退位。殇公与世子角反抗失败，最终都被杀死。"),("","卫献公三日赶回帝丘复位，允许太叔仪为殇公治丧，并任宁喜独相卫国。"),("","孙林父以戚邑附晋，故意把三百晋国守卒置于茅氏，企图借卫军袭晋激怒晋国。"),("","宁喜没有识破其计，命殖绰率千人袭击茅氏；战斗胜负留待下一回。"),("军令","帝丘复君完成，获得1200金币。第六十五回结束。")]
    text=head("第六十五回·下","弑齐光崔庆专权 纳卫衎甯喜擅政","帝丘复君","攻破孙氏府与卫宫，迎卫献公复位。","m110.png",intro,victory,"宁喜、右宰谷、北宫遗、公孙丁任一被击退，或超过三十回合，失败。",["NingXi65","YouZaiGu65","BeiGongYi65","GongSunDing61"],
              '{{id="sun_hall",name="孙氏正堂",position={16,13},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="sun_store",name="孙氏府库",position={23,29},restore_hp=20,restore_mp=10,rewards={}},{id="wei_palace",name="卫国宫城",position={56,13},restore_hp=25,restore_mp=20,rewards={}}}',[("公孙丁","孙襄追出府门，正是放箭之时！"),("宁喜","孙襄已死，三更再攻孙府！"),("卫殇公","宁喜擅杀世臣，寡人宁死不受废位之辱！")])
    rows=shared.terrain_block(d)
    return text+f'''local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("SunXiang65",1,Enum.force.enemy,{{27,21}});game:generate_unit("ChuDai65",1,Enum.force.enemy,{{23,29}});game:set_unit_invulnerable("ChuDai65",true);game:generate_unit("YongChu65",1,Enum.force.enemy,{{16,13}});game:set_unit_invulnerable("YongChu65",true);game:generate_unit("WeiShangGong65",1,Enum.force.enemy,{{56,13}});game:set_unit_invulnerable("WeiShangGong65",true);game:generate_unit("TaiZiJiao65",1,Enum.force.enemy,{{58,18}});game:set_unit_invulnerable("TaiZiJiao65",true);many(game,"SunHouseGuard65",{{{{26,18}},{{26,24}},{{20,20}},{{20,25}},{{14,19}},{{14,25}}}},Enum.force.enemy);many(game,"SunHouseArcher65",{{{{25,16}},{{25,27}},{{18,16}},{{18,30}}}},Enum.force.enemy);many(game,"NingHouseGuard65",{{{{33,18}},{{33,21}},{{33,25}},{{37,18}},{{37,26}}}},Enum.force.own)end
function on_update(game)if phase==1 and not game:has_unit("SunXiang65")then phase=2;game:set_unit_invulnerable("ChuDai65",false);game:push_cmd_speak(0,"孙襄中箭身亡，孙氏家甲已经动摇。三更再攻内门，击退褚带！")end if phase==2 and not game:has_unit("ChuDai65")then phase=3;game:set_unit_invulnerable("WeiShangGong65",false);game:set_unit_invulnerable("TaiZiJiao65",false);game:push_cmd_speak(0,"孙府已破，雍鉏越墙逃往戚邑。宁氏诸军转向卫宫，迫使殇公退位！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==3 and not game:has_unit("WeiShangGong65") and not game:has_unit("TaiZiJiao65")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="DiqiuRestoration65",turn_limit=30,map={{blocked_edges={{}},size={{70,48}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{35,19}},hero="NingXi65"}},{{position={{35,23}},hero="YouZaiGu65"}},{{position={{38,20}},hero="BeiGongYi65"}},{{position={{38,24}},hero="GongSunDing61"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=12000}}}}
'''

def patch_all():
    for sid,text in (("65a",stage_a()),("65b",stage_b()),("65c",stage_c())):(ROOT/f"game/sce/dongzhou/stage/{sid}.lua").write_text(text,encoding="utf-8")
    p=ROOT/"game/sce/dongzhou/config.lua";t=p.read_text(encoding="utf-8")
    if 'id = "TangWuJiu65"' not in t:t=t.replace('        ,{ id = "JuArcher64", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }    },','        ,{ id = "JuArcher64", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }'+HEROES+'    },')
    t=t.replace('"64a", "64b" }','"64a", "64b", "65a", "65b", "65c" }');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/save_system.py";t=p.read_text(encoding="utf-8").replace('STAGE_TABLE_VERSION = 8','STAGE_TABLE_VERSION = 9').replace('"64a","64b"\n)','"64a","64b","65a","65b","65c"\n)');p.write_text(t,encoding="utf-8")
    p=ROOT/"rl/play_gui.py";t=p.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m108.png"]' not in t:
        block='''
_LARGE_BATTLE_MAPS["m108.png"]=(50,38,48)
_LARGE_BATTLE_MAPS["m109.png"]=(52,36,48)
_LARGE_BATTLE_MAPS["m110.png"]=(70,48,48)
HERO_LABELS.update({"TangWuJiu65":"棠无咎","CuiCheng65":"崔成","CuiJiang65":"崔疆","DongGuoYan65":"东郭偃","JiaJu65":"贾举","ZhouChuoQi65":"州绰","GongSunAo65":"公孙敖","LouYan65":"偻堙","CuiAmbusher65":"崔氏伏甲","QiBraveGuard65":"齐国勇士","NiuChen65":"牛臣","ChaoGuard65":"巢城守军","WuGateGuard65":"吴军甲士","WuGateArcher65":"吴军弓手","NingXi65":"宁喜","YouZaiGu65":"右宰谷","BeiGongYi65":"北宫遗","SunXiang65":"孙襄","ChuDai65":"褚带","YongChu65":"雍鉏","WeiShangGong65":"卫殇公","TaiZiJiao65":"世子角","SunHouseGuard65":"孙氏家甲","SunHouseArcher65":"孙氏弓手","NingHouseGuard65":"宁氏家甲"})
HERO_BIOS.update({"TangWuJiu65":"崔杼继室之子，奉命伏甲崔府，射杀越墙逃走的齐庄公。","CuiCheng65":"崔杼长子，参与崔府伏击，遭公孙敖奋力折断手臂。","CuiJiang65":"崔杼之子，在崔府中门击杀贾举，又以长戈刺死公孙敖。","DongGuoYan65":"崔杼家臣，负责在府门外稳住齐国勇士并暗中夺走兵器。","JiaJu65":"齐庄公勇爵之士，随君入崔府，中伏被杀。","ZhouChuoQi65":"齐庄公勇爵之首，崔府之变中不肯投降，以头触墙殉君。","GongSunAo65":"齐国勇士，崔府中拔系马柱死战，最终被崔疆刺杀。","LouYan65":"齐国勇爵之士，崔府之变中受伤后战死。","NiuChen65":"楚国巢邑守将，藏身短墙之后发箭，射杀攻门的吴王诸樊。","NingXi65":"卫国宁氏大夫，奉父遗命迎献公复位，诛孙襄、废卫殇公后专政。","YouZaiGu65":"卫国右宰，参与攻打孙氏府与迎复卫献公。","BeiGongYi65":"卫国大夫，协助宁喜夜攻孙氏府并发动复位之变。","SunXiang65":"孙林父之子，守孙氏府时中公孙丁一箭，伤重而死。","ChuDai65":"孙氏家将，善射守府，孙襄死后被宁氏乱军杀死。","YongChu65":"孙氏家将，孙府失守后越后墙逃往戚邑。","WeiShangGong65":"卫国君主剽，在位十三年，宁喜迎献公复位时被废杀。","TaiZiJiao65":"卫殇公世子，持剑救父，被公孙丁击杀。"})
PORTRAIT_INDEX_BY_HERO.update({"TangWuJiu65":25,"CuiCheng65":34,"CuiJiang65":38,"DongGuoYan65":49,"JiaJu65":34,"ZhouChuoQi65":35,"GongSunAo65":25,"LouYan65":38,"NiuChen65":33,"NingXi65":49,"YouZaiGu65":49,"BeiGongYi65":35,"SunXiang65":34,"ChuDai65":33,"YongChu65":25,"WeiShangGong65":7,"TaiZiJiao65":38})
SPEAKER_PORTRAIT_INDEX.update({"棠无咎":25,"东郭偃":49,"齐庄公":7,"州绰":35,"牛臣":33,"吴王诸樊":7,"吴王馀祭":7,"宁喜":49,"右宰谷":49,"褚带":33,"公孙丁":33,"卫殇公":7})
HISTORICAL_DEATH_HEROES.update({"QiZhuangGong62","JiaJu65","ZhouChuoQi65","GongSunAo65","LouYan65","ZhuFan60","SunXiang65","ChuDai65","WeiShangGong65","TaiZiJiao65"})
'''
        t=t.replace('\nif _original_name == "__main__":',block+'\nif _original_name == "__main__":')
    p.write_text(t,encoding="utf-8")

if __name__=="__main__":patch_all();print("chapter 65 integrated: 65a, 65b, 65c")
