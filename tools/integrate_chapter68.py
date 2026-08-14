from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT = Path(__file__).resolve().parents[1]
TITLE = "贺虒祁师旷辨新声 散家财陈氏买齐国"

HEROES = '''
        ,{ id = "ChenWuYu68", class = "Strategist", stat = {95,88,98,96,94}, model = "Strategist-1-red" }
        ,{ id = "BaoGuo68", class = "Archer", stat = {92,95,93,94,92}, model = "archer-1-red" }
        ,{ id = "WangHei68", class = "Cavalry", stat = {91,96,89,93,91}, model = "cavalry-1-red" }
        ,{ id = "LuanShi68", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GaoQiang68", class = "Cavalry", stat = {90,94,87,91,88}, model = "cavalry-1-blue" }
        ,{ id = "ChenBaoGuard68", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChenBaoArcher68", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "LuanGaoGuard68", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "LuanGaoArcher68", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "QiCitizenGuard68", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "QiCitizenArcher68", class = "Archer", stat = {87,93,90,90,89}, model = "archer-1-red" }'''


def stage() -> str:
    data = json.loads((ROOT / "assets/lzc/map_sources/m117_ch68_manifest.json").read_text(encoding="utf-8"))
    intro = [
        ("", "楚灵王建成章华宫，偏爱细腰，宫人百官争相节食束带，甚至有人因求腰细而饿死。"),
        ("申无宇", "臣的阍人偷盗酒器后藏入王宫。若借王宫便能逃避主人之法，上下名分从此尽乱。"),
        ("楚灵王", "卿言有理。将盗贼交还依法处置，擅入王宫之罪也一并赦免。"),
        ("", "薳启疆以攻伐相威胁，邀鲁昭公游章华宫。楚灵王以高台、美童与乐舞夸示国力。"),
        ("薳启疆", "大屈宝弓为齐、晋、越三国所求。鲁国若收下此弓，便要准备抵御三国索取。"),
        ("鲁昭公", "寡人不知此弓如此贵重，岂敢接受？立即送还楚国。"),
        ("", "晋平公不听羊舌肸劝谏，也在曲沃汾水旁营建虒祁宫，耗费民力，召诸侯前来祝贺。"),
        ("卫灵公", "昨夜宿在濮水驿舍，水中隐约传来琴声。师涓已经记下，请在虒祁台奏给晋侯。"),
        ("师旷", "此为师延所作亡国之音《清商》。纣王沉迷其中而亡国，不宜再奏。"),
        ("晋平公", "寡人只爱新声。既有《清征》《清角》，今日一并奏来，纵死也不遗憾。"),
        ("", "《清征》奏响，玄鹤列队起舞；《清角》再奏，黑云狂风骤起，帘幕、屋瓦、廊柱尽被摧折，大雨淹没台阶。"),
        ("子产", "晋侯梦见的三足黄鳖名为‘能’，乃鲧神所化。补行祭祀可暂宽其心，但病根实在劳民营建宫室。"),
        ("师旷", "石不能言，是民怨使鬼神不安。晋侯与楚王皆以宫室耗竭百姓，其祸已经不远。"),
        ("", "齐国栾施、高彊嗜酒结党，与陈无宇、鲍国渐生嫌隙。受罚小竖谎称栾高次日将发动袭击。"),
        ("陈无宇", "谎言虽已查明，但高彊途中看见我率甲，必会生疑。不如趁栾、高醉饮无备，先发制人。"),
        ("", "陈、鲍家甲包围栾府。栾施、高彊突围至虎门，齐景公闭门自守，晏婴请命王黑助陈、鲍逐栾高。"),
        ("王黑", "君命已下。栾、高攻击寝门，罪不可赦；沿东门大道追击，不得让他们挟众据城。"),
        ("军令", "陈无宇、鲍国、王黑推进至东门大道，触发百姓助战并解除栾施、高彊保护；击退二人视为奔鲁。三名主将不得被击退。"),
    ]
    victory = [
        ("", "齐国百姓怨恨栾、高专政，纷纷攘臂助战。高彊醉意未醒，不能力战，栾施率先夺东门而出。"),
        ("", "王黑与陈、鲍两家追至东门再战，栾、高部众尽散，二人逃往鲁国。"),
        ("晏婴", "擅自兴兵、驱逐世卿，又独占其财，必受国人议论。不如把所得食邑家财全部归还公室。"),
        ("陈无宇", "无宇不敢自利。栾、高财产尽数登记献公，并召回被逐公子，资助无禄宗室与贫困孤寡。"),
        ("", "齐景公将高唐封给陈无宇。陈氏以大量借出、小量收回，贫者焚券，齐国民心由此逐渐归向陈氏。"),
        ("", "晏婴劝齐景公宽刑薄敛、与陈氏争取民心，景公不能采纳，陈氏取代齐国的根基由此形成。"),
        ("", "楚灵王因诸侯多往晋国祝贺而不赴章华宫，准备兴兵。伍举建议先讨伐弑父自立的蔡灵公；陈国继承之争也将爆发。"),
        ("军令", "东门逐栾高完成，获得1000金币。第六十八回结束。"),
    ]
    head = shared.stage_head(
        "", TITLE, "第六十八回", "东门逐栾高",
        "推进至东门大道，发动百姓助战后击退栾施、高彊。",
        "m117.png", intro,
        [("王黑", "奉齐侯之命，公徒加入陈、鲍两军！"), ("陈无宇", "国人皆来助战，沿东门大道追击栾、高！")],
        victory, "陈无宇、鲍国、王黑任一被击退，或超过二十四回合，失败。",
        ["ChenWuYu68", "BaoGuo68", "WangHei68"],
        '{{id="linzi_palace",name="临淄宫署",position={21,12},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}},{id="linzi_tiger",name="虎门官署",position={35,15},restore_hp=20,restore_mp=15,rewards={}},{id="east_market",name="东市府库",position={50,29},restore_hp=20,restore_mp=10,rewards={}}}',
    )
    rows = shared.terrain_block(data)
    return head + f'''local people_joined=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("LuanShi68",1,Enum.force.enemy,{{57,18}});game:generate_unit("GaoQiang68",1,Enum.force.enemy,{{57,23}});game:set_unit_invulnerable("LuanShi68",true);game:set_unit_invulnerable("GaoQiang68",true)
 many(game,"ChenBaoGuard68",{{{{40,16}},{{40,24}},{{44,14}},{{44,27}},{{47,19}}}},Enum.force.own);many(game,"ChenBaoArcher68",{{{{38,17}},{{38,23}},{{46,16}},{{46,25}}}},Enum.force.own)
 many(game,"LuanGaoGuard68",{{{{52,16}},{{52,20}},{{52,24}},{{56,15}},{{56,26}},{{60,18}},{{60,23}}}},Enum.force.enemy);many(game,"LuanGaoArcher68",{{{{50,18}},{{50,23}},{{55,13}},{{55,28}},{{59,16}},{{59,25}}}},Enum.force.enemy)
end
function on_update(game)
 if not people_joined and (game:is_unit_within("ChenWuYu68",{{56,20}},6)or game:is_unit_within("BaoGuo68",{{56,20}},6)or game:is_unit_within("WangHei68",{{56,20}},6))then people_joined=true;game:set_unit_invulnerable("LuanShi68",false);game:set_unit_invulnerable("GaoQiang68",false);many(game,"QiCitizenGuard68",{{{{53,14}},{{54,27}},{{58,14}},{{58,27}}}},Enum.force.own);many(game,"QiCitizenArcher68",{{{{55,16}},{{55,25}}}},Enum.force.own);game:push_cmd_speak(0,"齐国百姓怨恨栾、高，纷纷攘臂加入追击！二人已无法继续据众自保！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if people_joined and not game:has_unit("LuanShi68") and not game:has_unit("GaoQiang68")then return Enum.status.victory end return Enum.status.undecided end
gstage={{title_id="LinziEastGate68",turn_limit=24,map={{blocked_edges={{}},size={{72,44}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{{position={{43,17}},hero="ChenWuYu68"}},{{position={{43,24}},hero="BaoGuo68"}},{{position={{39,20}},hero="WangHei68"}}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money=10000}}}}
'''


def patch_all() -> None:
    (ROOT / "game/sce/dongzhou/stage/68.lua").write_text(stage(), encoding="utf-8")

    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    if 'id = "ChenWuYu68"' not in text:
        text = text.replace(
            '        ,{ id = "LiangHouseArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }    },',
            '        ,{ id = "LiangHouseArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }' + HEROES + '    },',
        )
    text = text.replace('"66e", "67a", "67b" }', '"66e", "67a", "67b", "68" }')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("STAGE_TABLE_VERSION = 11", "STAGE_TABLE_VERSION = 12")
    text = text.replace('"66a","66b","66c","66d","66e","67a","67b"\n)', '"66a","66b","66c","66d","66e","67a","67b","68"\n)')
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m117.png"]' not in text:
        block = '''
_LARGE_BATTLE_MAPS["m117.png"]=(72,44,48)
HERO_LABELS.update({"ChenWuYu68":"陈无宇","BaoGuo68":"鲍国","WangHei68":"王黑","LuanShi68":"栾施","GaoQiang68":"高彊","ChenBaoGuard68":"陈鲍家甲","ChenBaoArcher68":"陈鲍弓手","LuanGaoGuard68":"栾高家甲","LuanGaoArcher68":"栾高弓手","QiCitizenGuard68":"齐国义民","QiCitizenArcher68":"齐国义民弓手"})
HERO_BIOS.update({"ChenWuYu68":"齐国陈氏宗主，联合鲍国驱逐栾、高，献出所得财产并广施恩惠，奠定陈氏取齐基础。","BaoGuo68":"齐国鲍氏大夫，误信小竖告密后与陈无宇联兵，参与虎门、东门之战。","WangHei68":"齐国大夫，奉齐景公之命率公徒支援陈、鲍，在东门追逐栾施、高彊。","LuanShi68":"齐国栾氏大夫，嗜酒专政，与高彊结党；虎门兵败后从东门逃往鲁国。","GaoQiang68":"齐国高氏大夫，年轻嗜酒，与栾施共同攻打虎门，败后随栾氏奔鲁。"})
PORTRAIT_INDEX_BY_HERO.update({"ChenWuYu68":49,"BaoGuo68":35,"WangHei68":35,"LuanShi68":34,"GaoQiang68":35})
SPEAKER_PORTRAIT_INDEX.update({"申无宇":49,"楚灵王":8,"薳启疆":49,"鲁昭公":8,"卫灵公":8,"师涓":49,"师旷":49,"晋平公":8,"子产":49,"陈无宇":49,"鲍国":35,"王黑":35,"晏婴":49})
'''
        text = text.replace('\nif _original_name == "__main__":', block + '\nif _original_name == "__main__":')
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_all()
    print("chapter 68 integrated: stage 68")
