from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT = Path(__file__).resolve().parents[1]
TITLE = "杀三兄楚平王即位 劫齐鲁晋昭公寻盟"

HEROES = '''
        ,{ id = "ZiGan70", class = "Lord", stat = {93,91,92,91,90}, model = "lord-1-red" }
        ,{ id = "ZiXi70", class = "Strategist", stat = {92,85,96,93,92}, model = "Strategist-1-red" }
        ,{ id = "XiaNie70", class = "Cavalry", stat = {91,95,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "XuWuMou70", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "DouChengRan70", class = "Strategist", stat = {93,88,96,94,92}, model = "Strategist-1-red" }
        ,{ id = "WeiPi70", class = "Strategist", stat = {92,85,94,92,90}, model = "Strategist-1-blue" }
        ,{ id = "ShiZiLu70", class = "Lord", stat = {89,90,86,88,86}, model = "lord-1-blue" }
        ,{ id = "GongZiBa70", class = "Infantry", stat = {88,92,84,89,86}, model = "infantry-1-blue" }
        ,{ id = "ChenCaiGuard70", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChenCaiArcher70", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "ChuPalaceGuard70", class = "Infantry", stat = {89,94,88,91,90}, model = "infantry-1-blue" }
        ,{ id = "ChuPalaceArcher70", class = "Archer", stat = {88,93,91,91,89}, model = "archer-1-blue" }'''


def build_stage() -> str:
    data = json.loads((ROOT / "assets/lzc/map_sources/m119_ch70_manifest.json").read_text(encoding="utf-8"))
    intro = [
        ("", "楚灵王灭陈、蔡，又迁许、胡、沈、道、房、申六国百姓于荆山，自以为天下可取，欲先灭徐国再攻吴国。"),
        ("郑丹", "徐国远在东北，又有吴国为援。大王久驻乾溪，三军冻馁，国中若有内变，恐怕首尾不能相顾。"),
        ("楚灵王", "穿封戍守陈，弃疾守蔡，伍举与太子守郢，皆是楚人。寡人所向必克，何须多虑！"),
        ("", "楚王从冬至春仍留乾溪射猎筑台。蔡人朝吴与家宰观从见国内空虚，谋借公子弃疾之名召回子干、子皙。"),
        ("观从", "子干在晋，子皙在郑。假称蔡公愿以陈蔡之师迎二公子返楚，先将人召来，再迫蔡公举兵。"),
        ("朝吴", "灵王弑兄杀侄，三位公子皆不服。陈蔡百姓思复宗祀，蔡洧、斗成然又能内应，此时不举，再无机会。"),
        ("", "子干、子皙来到蔡郊，才知蔡公弃疾并未下令。朝吴歃血立盟，把弃疾的名字列在盟书首位，又发动蔡人围住蔡公府。"),
        ("公子弃疾", "你等把我逼上虎背。既然人心已齐，便合陈蔡之众进取郢都；但不得劫掠百姓。"),
        ("夏啮", "陈公病重不起，陈人却没有忘记亡国之恨。夏啮率陈国义众前来，与蔡军同复宗祀。"),
        ("须务牟", "愿为先锋，乘郢都无备直取东门。只要城门一开，先控制王宫，不让薳罢奉世子禄逃走。"),
        ("", "蔡洧遣心腹出城送款，斗成然在郊外迎接。郢都百姓痛恨灵王暴政，听闻蔡公到来，无人愿为王室死战。"),
        ("蔡洧", "东门已经打开。城中守军仍不知乾溪虚实，诸军直取宫门，我与斗成然在内接应。"),
        ("子干", "先君郏敖之仇，今日当报；但楚国宗社不可尽毁，宫中降者皆免其罪。"),
        ("子皙", "薳罢若奉世子据宫顽抗，先清外围甲士，再入宫擒拿世子禄与公子罢。"),
        ("军令", "从东门攻入郢都，清除宫门卫队后击退世子禄和公子罢；薳罢将按史实自刎。公子弃疾、子干、子皙、朝吴、夏啮、须务牟任一被击退则失败。"),
    ]
    victory = [
        ("", "蔡洧开门纳军，郢都百姓没有抵抗。薳罢不能进入王宫，回家自刎；世子禄、公子罢在宫中被杀。"),
        ("公子弃疾", "长幼不可废。请子干兄即楚王位，以子皙为令尹，弃疾暂领司马，先安定国人。"),
        ("", "朝吴令观从赶赴乾溪，宣告新王命令：先归者复其田里，后归者劓鼻，协助楚灵王者罪及三族。"),
        ("观从", "郢都已破，世子禄与公子罢皆死。乾溪士卒若立即归家，田宅一概恢复；迟疑者依法治罪！"),
        ("", "乾溪楚军冻饿已久，听令后一时散去大半。楚灵王拔寨西返，沿途士卒不断逃亡，到訾梁时只剩百人。"),
        ("楚灵王", "寡人杀人之子多矣，人杀寡人之子，又何足怪。诸侯无人爱我，出奔求师不过自取其辱。"),
        ("", "楚灵王弃冠服于岸柳，独自在釐泽流离。涓人畴不敢献食，申亥念父命将他迎入棘村，灵王当夜自缢。"),
        ("申亥", "先父申无宇两次获王赦免，命我在王有难时舍命相从。如今只能亲自殡殓，以报旧恩。"),
        ("", "公子弃疾追至訾梁未得灵王尸首。朝吴又让小卒诈称楚王大军返郢，斗成然回城附和。"),
        ("斗成然", "蔡公兵败，楚王已经入城！新王若落在灵王手中，必受申地蔡侯、齐庆封一般的酷刑。"),
        ("", "子皙先拔剑自刎，子干也仓促自尽。弃疾整军返回郢都，国人才知前后消息皆是朝吴之计。"),
        ("", "公子弃疾即位，改名熊居，是为楚平王。昔年楚共王祷神，当璧而拜者为君的预言至此应验。"),
        ("", "国人尚未知灵王已死，平王先令观从以冠服伪作尸首安定众心；三年后申亥告知真墓，才将灵王正式改葬。"),
        ("楚平王", "灵王以吞并失人心，寡人应反其所为。访求陈、蔡之后，复立陈世子偃师之子吴与蔡世子有之子庐。"),
        ("朝吴", "陈蔡宗祀既复，臣愿随蔡平公归国。六国迁民也应各还故土，楚库中的重器财宝一并归还。"),
        ("", "楚平王复陈、蔡，归还六国故土。陈蔡义军各从其主，百姓欢声如雷。"),
        ("", "司马督围徐无功，闻灵王已死便解围班师；吴公子光在豫章邀击，俘获三百乘楚军并夺取州来。"),
        ("", "晋昭公想重振霸业，征齐景公入晋。宴席投壶时，齐侯说若投中便与晋国代兴，晋臣大怒。"),
        ("晏婴", "盟无常主，惟有德者居之。晋若有德，谁敢不服；若无德，吴楚也会相继而起，岂止齐国？"),
        ("", "晋昭公大阅四千乘、三十万甲士，邀十二国诸侯会于平丘，又请周卿士刘挚监临。"),
        ("羊舌肸", "楚虔无信，自取陨灭。晋国愿效践土故事镇抚诸夏；若齐侯拒盟，四千乘愿到城下请罪。"),
        ("齐景公", "大国既以盟礼不可废，齐国不敢自外。今日姑且受歃，日后仍要看晋国能否以德服人。"),
        ("", "晋国扣留鲁卿季孙意如，又在劝说后释放。诸侯看出晋国徒恃兵威而谋略不足，晋国从此不能再主盟。"),
        ("军令", "郢都兵变完成，获得1800金币。第七十回结束。"),
    ]
    head = shared.stage_head(
        "70", TITLE, "第七十回", "郢都兵变",
        "从东门攻入郢都，清除宫门卫队后击退世子禄和公子罢。薳罢自尽，楚灵王按史实从乾溪溃逃。",
        "m119.png", intro,
        [
            ("蔡洧", "郢都东门已开，国人愿迎蔡公。直取宫门，不得扰民！"),
            ("朝吴", "宫门卫队已经瓦解，薳罢不能入宫而自尽，世子禄、公子罢再无屏障！"),
            ("观从", "乾溪归田令已经传遍楚军，灵王部众正在自行离营。"),
        ],
        victory,
        "六名我方具名将领任一被击退，或二十六回合内未能控制楚宫，本关失败。",
        ["GongZiQiJi69", "ZiGan70", "ZiXi70", "ChaoWu69", "XiaNie70", "XuWuMou70"],
        '{{id="ying_palace",name="郢都王宫",position={24,10},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}},{id="ying_west_office",name="郢都西府",position={16,23},restore_hp=20,restore_mp=10,rewards={}},{id="ying_east_office",name="郢都东府",position={39,23},restore_hp=20,restore_mp=10,rewards={}}}',
    )
    terrain = shared.terrain_block(data)
    return head + f'''local palace_open=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("CaiWei69",1,Enum.force.ally,{{50,20}});game:set_unit_invulnerable("CaiWei69",true)
 game:generate_unit("DouChengRan70",1,Enum.force.ally,{{50,21}});game:set_unit_invulnerable("DouChengRan70",true)
 game:generate_unit("ShiZiLu70",1,Enum.force.enemy,{{16,23}});game:generate_unit("GongZiBa70",1,Enum.force.enemy,{{39,23}})
 for _,h in ipairs({{"ShiZiLu70","GongZiBa70"}})do game:set_unit_invulnerable(h,true)end
 many(game,"ChenCaiGuard70",{{{{56,19}},{{56,22}},{{59,16}},{{59,25}}}},Enum.force.own);many(game,"ChenCaiArcher70",{{{{55,17}},{{55,24}},{{61,15}},{{61,26}}}},Enum.force.own)
 many(game,"ChuPalaceGuard70",{{{{48,18}},{{48,23}},{{43,20}},{{43,21}},{{38,17}},{{38,26}},{{29,18}},{{29,24}}}},Enum.force.enemy)
 many(game,"ChuPalaceArcher70",{{{{46,16}},{{46,25}},{{34,18}},{{34,23}},{{22,16}},{{22,27}}}},Enum.force.enemy)
end
function on_update(game)
 if not palace_open and not game:has_unit("ChuPalaceGuard70") and not game:has_unit("ChuPalaceArcher70")then palace_open=true;for _,h in ipairs({{"ShiZiLu70","GongZiBa70"}})do game:set_unit_invulnerable(h,false)end;game:push_cmd_speak(0,"宫门卫队已经瓦解！薳罢无法进入王宫而自刎，世子禄与公子罢失去保护，控制宫署！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if palace_open and not game:has_unit("ShiZiLu70")and not game:has_unit("GongZiBa70")then return Enum.status.victory end
 return Enum.status.undecided
end
gstage={{title_id="YingCoup70",turn_limit=26,map={{blocked_edges={{}},size={{68,46}},terrain={{
{terrain}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{61,20}},hero="GongZiQiJi69"}},{{position={{62,18}},hero="ZiGan70"}},{{position={{62,23}},hero="ZiXi70"}},{{position={{58,17}},hero="ChaoWu69"}},{{position={{58,25}},hero="XiaNie70"}},{{position={{64,21}},hero="XuWuMou70"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=18000}}}}
'''


def patch_all() -> None:
    (ROOT / "game/sce/dongzhou/stage/70.lua").write_text(build_stage(), encoding="utf-8")

    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    if 'id = "ZiGan70"' not in text:
        text = text.replace(
            '        ,{ id = "CaiArcher69", class = "Archer", stat = {88,93,91,91,90}, model = "archer-1-blue" }    },',
            '        ,{ id = "CaiArcher69", class = "Archer", stat = {88,93,91,91,90}, model = "archer-1-blue" }' + HEROES + '    },',
        )
    text = text.replace('"67b", "68", "69" }', '"67b", "68", "69", "70" }')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("STAGE_TABLE_VERSION = 13", "STAGE_TABLE_VERSION = 14")
    text = text.replace('"67a","67b","68","69"\n)', '"67a","67b","68","69","70"\n)')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m119.png"]' not in text:
        block = '''
_LARGE_BATTLE_MAPS["m119.png"]=(68,46,48)
HERO_LABELS.update({"ZiGan70":"子干","ZiXi70":"子皙","XiaNie70":"夏啮","XuWuMou70":"须务牟","DouChengRan70":"斗成然","WeiPi70":"薳罢","ShiZiLu70":"世子禄","GongZiBa70":"公子罢","ChenCaiGuard70":"陈蔡义军","ChenCaiArcher70":"陈蔡弓手","ChuPalaceGuard70":"楚宫甲士","ChuPalaceArcher70":"楚宫弓手"})
HERO_BIOS.update({"ZiGan70":"楚共王之子、楚灵王之弟，流亡晋国后被迎回郢都即位，旋因诈报灵王返城而自尽。","ZiXi70":"楚共王之子，流亡郑国。随子干返楚任令尹，误信灵王归来，先于兄长自刎。","XiaNie70":"陈国夏征舒后裔，响应复陈之举，率陈人协助公子弃疾袭取郢都。","XuWuMou70":"公子弃疾家臣，担任陈蔡联军先锋，率精甲先行突入郢都。","DouChengRan70":"楚国郊尹，与公子弃疾交好，郢都兵变时为内应，后参与诈报并迎立楚平王。","WeiPi70":"楚灵王所任令尹，郢都失守时欲奉世子禄出奔，不能进入王宫，最终自刎。","ShiZiLu70":"楚灵王太子，奉命留守郢都。公子弃疾联军入宫后被杀。","GongZiBa70":"楚灵王之子，郢都兵变中与世子禄一同守宫，被公子弃疾军杀死。"})
PORTRAIT_INDEX_BY_HERO.update({"ZiGan70":7,"ZiXi70":49,"XiaNie70":35,"XuWuMou70":25,"DouChengRan70":49,"WeiPi70":42,"ShiZiLu70":8,"GongZiBa70":34})
SPEAKER_PORTRAIT_INDEX.update({"郑丹":49,"观从":49,"朝吴":42,"公子弃疾":7,"夏啮":35,"须务牟":25,"蔡洧":35,"子干":7,"子皙":49,"斗成然":49,"楚平王":7,"申亥":35,"楚灵王":8,"晏婴":49,"羊舌肸":49,"齐景公":8})
HISTORICAL_DEATH_HEROES.update({"ShiZiLu70","GongZiBa70"})
'''
        text = text.replace('\nif _original_name == "__main__":', block + '\nif _original_name == "__main__":')
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_all()
    print("chapter 70 integrated: stage 70")
