import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def terrain_rows():
    data = json.loads((ROOT / "assets/lzc/map_sources/m081_ch51_manifest.json").read_text(encoding="utf-8"))
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE = r'''ambush_started = false
bridge_closed = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChuZhuangWang51", "GongZiCe51", "GongZiYingQi51", "PanWang51", "LeBo51", "YangYouJi51" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "YangYouJi51", defender = "DouYueJiao40", exp = 100, outcome = "kill",
        attacker_speech = "令尹三箭已尽。若养由基还要三箭才能中你，便只能算初学射术；我只发一矢！",
        defender_speech = "无名小校也敢夸口？我让你三箭，看你如何射中本令尹！",
        result_speech = "养由基先以虚弦诱斗越椒左右躲闪，趁其身形未定，一箭贯脑。",
        text = "养由基隔清河与斗越椒较射，一箭射杀叛军主将。"
    }
}
gsites = {}

gstory = {
    chapter = "第五十一回",
    title = "责赵盾董狐直笔 诛斗椒绝缨大会",
    battle_title = "清河桥之战",
    objective = "楚军伏兵由东西两翼夹击饥疲的斗氏叛军。清河中央断桥不可通行，只有最东侧浅滩可以绕行；养由基与斗越椒相邻可触发史实箭术单挑，一箭击杀。斗越椒被击退即可取胜，斗贲皇按原著逃往晋国。任一我方具名将领被击退则失败。",
    map_asset = "m081.png",
    intro = {
        { speaker = "", text = "赵盾父子出绛城后暂住首阳山。赵穿请求叔父不要越过国境，许诺数日内必有消息。" },
        { speaker = "赵穿", text = "叔父暂居首阳，莫急着投秦或奔翟。我回绛城设法除掉昏君，再迎你主持国政。" },
        { speaker = "", text = "赵穿假意向晋灵公请罪，又献计搜选民间美女，让屠岸贾离开桃园奔走郊外。" },
        { speaker = "", text = "随后赵穿挑选二百甲士充当桃园宿卫，约定二更毁门入园，以挥袖为号刺杀晋侯。" },
        { speaker = "晋灵公", text = "甲士忽然登台做什么？赵穿，立即传令让他们退下，不得惊扰寡人饮宴！" },
        { speaker = "赵穿", text = "众人都想见相国赵盾，请主公召他回朝。主公既不肯答应，他们只好自己讨取公道。" },
        { speaker = "", text = "赵穿挥袖，二百甲士一拥而上，将晋灵公刺死在绛霄楼。近侍畏惧暴君已久，无人出手相救。" },
        { speaker = "", text = "赵穿约束军士，不许妄杀他人，随即赶往首阳山迎回赵盾。百姓因长期受苦，也无人归罪赵穿。" },
        { speaker = "", text = "赵盾回绛后伏尸痛哭，为晋灵公殡殓，并与士会议立成年国君，以免重蹈改立幼主的覆辙。" },
        { speaker = "士会", text = "文公之子黑臀年长，现任职于周。迎他回晋，足以稳定社稷。" },
        { speaker = "", text = "赵穿奉命迎公子黑臀。黑臀即位，是为晋成公，继续任赵盾执掌国政，又将女儿庄姬嫁给赵朔。" },
        { speaker = "赵盾", text = "赵同、赵括、赵婴均已成人，臣愿把嫡位归还诸弟，共同辅佐新君。" },
        { speaker = "", text = "赵盾没有追究屠岸贾，也不许赵穿借机报复。屠岸贾表面谨慎侍奉赵氏，暗中却仍怀怨恨。" },
        { speaker = "", text = "太史董狐在史简上直书：赵盾弑其君夷皋于桃园。赵盾见后大惊，亲自到史馆质问。" },
        { speaker = "赵盾", text = "弑君之日我已出奔河东，离绛城二百余里。太史为何把赵穿之罪记在我名下？" },
        { speaker = "董狐", text = "你身为相国，出亡未越国境，回来又不讨弑君之贼。此事若非你主谋，天下谁会相信？" },
        { speaker = "赵盾", text = "史臣之权重于卿相。只恨我未能及时越境，又未依法讨赵穿，从此难免万世恶名。" },
        { speaker = "", text = "赵穿自恃迎立之功求正卿，赵盾为避私议不许。赵穿愤恨成疾，背疽发作而死。" },
        { speaker = "", text = "周匡王去世，弟瑜即位，是为周定王。次年楚庄王率军攻陆浑之戎，又陈兵雒水边界。" },
        { speaker = "楚庄王", text = "大禹所铸九鼎如今在雒阳，不知形制大小、轻重多少？寡人愿听王孙大夫说明。" },
        { speaker = "王孙满", text = "国家传承在德不在鼎。有德则鼎虽小亦重，无德则鼎虽大亦轻；周德未尽，鼎不可问。" },
        { speaker = "", text = "楚庄王惭愧退兵。此时令尹斗越椒因权力被分而怨恨，趁楚王出征陆浑发动叛乱。" },
        { speaker = "", text = "斗越椒逼迫族人从乱，斗克拒绝后被杀；越椒又突袭杀死司马蒍贾，屯兵蒸野截断楚王归路。" },
        { speaker = "苏从", text = "大王愿赦免令尹擅杀司马之罪，甚至可遣王子为质。只要放下兵器，若敖氏仍可保全。" },
        { speaker = "斗越椒", text = "我耻于只做令尹，不需要赦免！楚王若有本事，便亲自领兵来战。" },
        { speaker = "", text = "第一次交锋，斗越椒两箭逼退楚王，楚军上下都畏惧他的神射。庄王只得退到皇浒扎营。" },
        { speaker = "楚庄王", text = "越椒偷出的透骨风神箭只有两支，方才已经用尽。明日我军不必再怕，按计诱他追击。" },
        { speaker = "公子侧", text = "臣与公子婴齐分伏东西两翼。潘尪故意让路，引越椒日夜兼程追向青山。" },
        { speaker = "公子婴齐", text = "叛军一日一夜奔行二百余里，又忍饥追赶。等他们停车做饭，两军同时合击。" },
        { speaker = "", text = "楚军次日诈退，斗越椒果然命士卒不擒楚王不得吃饭。叛军饥疲不堪，仍追过清河桥。" },
        { speaker = "熊负羁", text = "楚王尚未到达青山。令尹军士又饥又累，不如先停车造饭，吃饱再战。" },
        { speaker = "", text = "斗越椒中计停车，公子侧、公子婴齐两翼伏兵突然杀出。叛军不能再战，向南退回清河。" },
        { speaker = "楚庄王", text = "清河桥已经拆断，寡人率军伏在两岸。封住东侧浅滩，不让叛军重新渡河！" },
        { speaker = "乐伯", text = "斗越椒退路已绝！养由基随我到河口，若能以箭术破其威名，斗氏全军必溃。" },
        { speaker = "养由基", text = "臣愿与越椒隔河较射。他若三箭不能伤我，臣只需一箭便取其性命。" },
        { speaker = "军令", text = "东西两翼合围斗氏叛军。清河三行水域不可通行，中段断桥不能通过，东侧四列浅滩可绕行。养由基与斗越椒相邻触发史实单挑。" }
    },
    events = {
        { id = "qinghe_encirclement", trigger = "approach", position = {24,16}, radius = 8, speaker = "楚庄王", text = "叛军已经进入青山合围圈！东西两翼同时出击，把斗越椒逼向断桥！" },
        { id = "duel_ready", trigger = "adjacent", speaker = "养由基", text = "斗越椒就在河口。让我与他较射，破掉叛军最后的胆气！" }
    },
    victory = {
        { speaker = "", text = "斗越椒连发三箭，养由基或拨、或蹲、或张口衔镞，三箭都未能伤他。" },
        { speaker = "养由基", text = "该我还射了！若需要三箭才能中你，便是初学；养由基只发一矢。" },
        { speaker = "", text = "养由基先两次虚拉弓弦，诱得斗越椒左右躲闪；第三次突然发箭，一箭贯穿其脑。" },
        { speaker = "", text = "斗氏军见主将阵亡，饥疲之下四散奔逃。公子侧、公子婴齐分路追击，楚军取得全胜。" },
        { speaker = "", text = "斗越椒之子斗贲皇逃往晋国，后来被晋国任为大夫，食邑于苗，因此又称苗贲皇。" },
        { speaker = "", text = "楚庄王回郢都诛灭从乱的若敖氏宗族；斗克黄出使归来，明知获罪仍主动复命请囚。" },
        { speaker = "斗克黄", text = "祖父子文早已预言越椒将灭若敖氏。臣既属逆族，又违先祖告诫，今日受死本是应分。" },
        { speaker = "楚庄王", text = "子文治楚有大功，斗克黄又不逃刑，是忠臣。赦免其罪，恢复官职，改名斗生。" },
        { speaker = "", text = "楚庄王厚赏养由基，让他统领亲军、担任车右，又令虞邱暂掌国政。" },
        { speaker = "", text = "庄王在渐台大会群臣，夜间怪风吹灭烛火。宠姬许姬被人牵袖，只扯下对方冠缨。" },
        { speaker = "许姬", text = "妾已取得无礼者冠缨，请大王立即点灯查验，以正君臣男女之礼。" },
        { speaker = "楚庄王", text = "今日原为尽欢，不可因酒后失态伤害国士。命所有人都摘去冠缨，再点烛饮酒！" },
        { speaker = "", text = "百官全部绝缨，冒犯许姬者身份不再可查。此宴后来被称为绝缨会。" },
        { speaker = "", text = "樊姬又提醒庄王：虞邱虽贤，却长期未举荐贤才，想以一人智慧掩尽楚国人才。" },
        { speaker = "虞邱", text = "臣智确实不及樊夫人。请大王容臣遍访群臣，为楚国另寻足以任相的人才。" },
        { speaker = "", text = "斗生举荐避难梦泽的蒍敖。蒍敖幼时见两头蛇，因怕后来者受害，将蛇杀死掩埋。" },
        { speaker = "蒍敖之母", text = "你见不祥却先想到保护别人，一念之善，上天必会保佑；你不仅不会死，将来还会得福。" },
        { speaker = "", text = "虞邱与斗生奉命到梦泽迎蒍敖入朝。蒍敖字孙叔，日后将以孙叔敖之名辅佐楚庄王。" },
        { speaker = "军令", text = "清河桥之战完成，获得900金币。斗越椒按原著记入阵亡，斗贲皇撤往晋国；其余未明确死亡的具名角色统一按撤退处理。" }
    },
    defeat = {{ speaker = "", text = "楚军具名将领在合围中被击退，斗越椒冲破青山伏兵，清河设伏失败。" }}
}

gstage = {
    title_id = "BattleOfQingheBridge51", turn_limit = 26,
    map = { blocked_edges = {}, size = {48,34}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {24,25}, hero = "ChuZhuangWang51" },
        { position = {39,17}, hero = "GongZiCe51" },
        { position = {9,17}, hero = "GongZiYingQi51" },
        { position = {37,10}, hero = "PanWang51" },
        { position = {11,10}, hero = "LeBo51" },
        { position = {19,23}, hero = "YangYouJi51" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 9000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
    game:generate_unit("DouYueJiao40", 1, Enum.force.enemy, {24,16})
    game:generate_unit("DouBenHuang51", 1, Enum.force.enemy, {26,14})
    game:set_unit_invulnerable("DouBenHuang51", true)
    many(game, "ChuRoyalGuard51", {{21,24},{23,24},{25,24},{27,24},{20,22},{28,22}}, Enum.force.own)
    many(game, "ChuRoyalArcher51", {{18,25},{30,25},{21,21},{27,21}}, Enum.force.own)
    many(game, "ChuAmbushGuard51", {{5,13},{7,15},{9,13},{39,13},{41,15},{43,13}}, Enum.force.own)
    many(game, "ChuAmbushCavalry51", {{6,10},{10,9},{38,9},{42,10}}, Enum.force.own)
    many(game, "ChuAmbushArcher51", {{4,17},{8,19},{40,19},{44,17}}, Enum.force.own)
    many(game, "RuoAoGuard51", {{20,11},{22,12},{24,11},{26,12},{28,11},{19,15},{29,15},{20,19},{24,20},{28,19}}, Enum.force.enemy)
    many(game, "RuoAoCavalry51", {{21,8},{25,8},{29,9},{18,13},{30,13},{22,18},{26,18}}, Enum.force.enemy)
    many(game, "RuoAoArcher51", {{17,10},{31,10},{18,17},{30,17},{21,20},{27,20}}, Enum.force.enemy)
end
function on_update(game)
    if not ambush_started and (game:is_unit_within("GongZiCe51", {24,16}, 8)
        or game:is_unit_within("GongZiYingQi51", {24,16}, 8)) then
        ambush_started = true
        game:push_cmd_speak(0, "东西两翼伏兵已经合围！斗氏军饥疲不堪，正向清河断桥方向退却。")
    end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("DouYueJiao40") then return Enum.status.victory end
    return Enum.status.undecided
end
'''


def write_stage():
    (ROOT / "game/sce/dongzhou/stage/51.lua").write_text(STAGE.replace("__ROWS__", terrain_rows()), encoding="utf-8")


def update_config():
    path = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "ChuZhuangWang51", class = "King", stat = {94, 92, 96, 96, 94}, model = "lord-1-red" }
        ,{ id = "GongZiCe51", class = "Strategist", stat = {92, 88, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "GongZiYingQi51", class = "Cavalry", stat = {91, 94, 88, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "PanWang51", class = "Cavalry", stat = {88, 92, 84, 89, 86}, model = "cavalry-1-red" }
        ,{ id = "LeBo51", class = "Cavalry", stat = {88, 94, 82, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "YangYouJi51", class = "Archer", stat = {94, 99, 90, 96, 94}, model = "archer-1-red" }
        ,{ id = "DouBenHuang51", class = "Cavalry", stat = {90, 94, 90, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "ChuRoyalGuard51", class = "Infantry", stat = {86, 91, 84, 87, 85}, model = "infantry-1-red" }
        ,{ id = "ChuRoyalArcher51", class = "Archer", stat = {84, 90, 86, 87, 85}, model = "archer-1-red" }
        ,{ id = "ChuAmbushGuard51", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ChuAmbushCavalry51", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-red" }
        ,{ id = "ChuAmbushArcher51", class = "Archer", stat = {83, 89, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "RuoAoGuard51", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "RuoAoCavalry51", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-blue" }
        ,{ id = "RuoAoArcher51", class = "Archer", stat = {84, 90, 86, 87, 85}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(path, '"49", "50a", "50b", "50c" }', '"49", "50a", "50b", "50c", "51" }')


def update_gui():
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m081.png"] = (48, 34, 48)

HERO_LABELS.update({
    "ChuZhuangWang51": "楚庄王", "GongZiCe51": "公子侧", "GongZiYingQi51": "公子婴齐",
    "PanWang51": "潘尪", "LeBo51": "乐伯", "YangYouJi51": "养由基", "DouBenHuang51": "斗贲皇",
    "ChuRoyalGuard51": "楚王亲卫", "ChuRoyalArcher51": "楚王弓手",
    "ChuAmbushGuard51": "楚军伏兵", "ChuAmbushCavalry51": "楚军伏骑", "ChuAmbushArcher51": "楚军伏弓",
    "RuoAoGuard51": "若敖甲士", "RuoAoCavalry51": "若敖骑兵", "RuoAoArcher51": "若敖弓手",
})
HERO_BIOS.update({
    "ChuZhuangWang51": "楚国君王熊侣。即位后整顿朝政，平定斗越椒叛乱，任用孙叔敖，逐渐奠定楚国霸业。",
    "GongZiCe51": "楚国王族名将，字子反。清河桥之战与公子婴齐分率两翼伏兵，合围饥疲的斗氏叛军。",
    "GongZiYingQi51": "楚国王族名将，字子重。斗越椒叛乱时统率一翼伏军，协助楚庄王截断清河退路。",
    "PanWang51": "楚国将领。初战与斗旗交锋，诈退阶段故意为斗越椒让路，将叛军继续引向青山伏击圈。",
    "LeBo51": "楚国大将。清河桥南阻截斗越椒，并接受部将养由基请战，以箭术决定叛军主将生死。",
    "YangYouJi51": "楚国神射手，字叔。清河桥隔河与斗越椒较射，避过三箭后仅发一矢便贯脑杀敌。",
    "DouBenHuang51": "斗越椒之子。清河兵败后逃往晋国，被任为大夫，食邑于苗，后称苗贲皇。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ChuZhuangWang51": 8, "GongZiCe51": 49, "GongZiYingQi51": 35,
    "PanWang51": 33, "LeBo51": 34, "YangYouJi51": 24, "DouBenHuang51": 38,
})
SPEAKER_PORTRAIT_INDEX.update({
    "赵穿": 35, "晋灵公": 7, "士会": 31, "赵盾": 42, "董狐": 49,
    "楚庄王": 8, "王孙满": 45, "苏从": 42, "斗越椒": 34, "公子侧": 49,
    "公子婴齐": 35, "熊负羁": 25, "乐伯": 34, "养由基": 24, "斗克黄": 31,
    "许姬": 12, "虞邱": 45, "蒍敖之母": 12,
})
HISTORICAL_DEATH_HEROES.add("DouYueJiao40")

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_prior_test():
    path = ROOT / "rl/chapter50_test.py"
    replace_once(path, 'assert \'"48a", "48b", "49", "50a", "50b", "50c" }\' in config',
                 'assert \'"48a", "48b", "49", "50a", "50b", "50c", "51" }\' in config')


def main():
    write_stage()
    update_config()
    update_gui()
    update_prior_test()
    print("Chapter 51 stage, config, GUI metadata, and prior regression anchor updated.")


if __name__ == "__main__":
    main()
