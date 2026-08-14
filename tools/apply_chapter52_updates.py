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
    data = json.loads((ROOT / "assets/lzc/map_sources/m082_ch52_manifest.json").read_text(encoding="utf-8"))
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE = r'''surprise_started = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "XiQue45" }
gduel_enabled = true
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十二回",
    title = "公子宋尝鼋构逆 陈灵公衵服戏朝",
    battle_title = "柳棼救郑",
    objective = "郤缺率晋军沿西北柳林迂回，抵达楚军侧后坐标（20，11）附近触发奇袭。郑军坚守东面，不受玩家指挥。奇袭发动后击溃楚军步兵与弓手主线即可迫使楚庄王撤军。楚庄王、郑襄公与公子去疾按史实不可被击退；郤缺被击退则失败。",
    map_asset = "m082.png",
    intro = {
        { speaker = "", text = "郑国公子归生字子家，公子宋字子公，同为郑国执政重臣。一日二人入朝，公子宋的食指忽然自行跳动。" },
        { speaker = "公子宋", text = "从前食指如此，随后必能尝到异味。今日入朝，宫中大概又得了什么难得的珍馐。" },
        { speaker = "", text = "恰逢楚人献来一只大鼋，郑灵公命太官烹煮，准备分赐诸大夫。归生与公子宋相视而笑。" },
        { speaker = "郑灵公", text = "你二人为何见寡人的大鼎便发笑？莫非早已知道今日宴上有什么？" },
        { speaker = "公子归生", text = "子公今晨食指自动，断言必尝异味。方才见鼋，臣才知道他的预兆应在此物。" },
        { speaker = "", text = "郑灵公听后，故意遍赐群臣鼋羹，唯独不给公子宋，要看他的食指之兆如何应验。" },
        { speaker = "公子宋", text = "鼋羹由我预知，君上却用一碗汤羞辱臣。既然如此，臣便自己尝！" },
        { speaker = "", text = "公子宋走到君鼎前，以手指蘸取鼋羹入口，扬长而去。后世所谓“染指”，便由此而来。" },
        { speaker = "郑灵公", text = "臣子竟敢染指君鼎！寡人若不诛他，国法何在，君威何存？" },
        { speaker = "公子归生", text = "子公不过一时负气。臣愿劝他入朝谢罪，请君上暂息雷霆。" },
        { speaker = "", text = "次日公子宋照常入朝，全无请罪之意。郑灵公怒色愈盛，归生只得再去私下劝说。" },
        { speaker = "公子宋", text = "君上先以缺羹辱我，如今又欲杀我。与其坐等受戮，不如先下手为强。" },
        { speaker = "公子归生", text = "君臣名分不可犯。你若真有逆谋，我宁可将此事告知君上，也绝不与你同罪。" },
        { speaker = "", text = "公子宋暗中散布流言，声称归生与公子去疾将谋乱郑国，又以祸及家族相威胁，逼归生保持沉默。" },
        { speaker = "公子宋", text = "流言已经传遍国中。你若告发我，旁人只会说你为求脱罪而先发制人。如今你我已在一条船上。" },
        { speaker = "公子归生", text = "我既不能制止，又不敢揭发，从此难逃同谋之名。郑国之祸，竟由一鼎鼋羹而起。" },
        { speaker = "", text = "当年秋祭，郑灵公斋宿宫中。公子宋贿赂守门者，深夜潜入斋宫，以土囊压杀灵公，谎称国君暴卒。" },
        { speaker = "", text = "《春秋》记作“郑公子归生弑其君夷”，把罪责归于执政归生：身为正卿，知谋而不能讨，仍难辞其责。" },
        { speaker = "公子去疾", text = "灵公有八子，公子坚又居长。我若越次即位，只会使国人相信外间关于我参与逆谋的流言。" },
        { speaker = "", text = "公子去疾拒绝即位。诸大夫于是拥立公子坚，是为郑襄公。襄公一度想驱逐诸位兄弟，以绝后患。" },
        { speaker = "公子去疾", text = "公族如同树木枝叶。枝叶茂盛，根本才坚固；若尽逐兄弟，君上身边反而无人可倚。" },
        { speaker = "", text = "郑襄公采纳建议，使十一位兄弟都参与国政。公子宋则急忙向晋国求和，希望借晋国声势稳住自己的地位。" },
        { speaker = "", text = "次年，楚庄王以讨问弑君为名，派公子婴齐伐郑。晋国命荀林父来救，楚军转而攻陈，郑襄公遂在黑壤与晋结盟。" },
        { speaker = "", text = "周定王三年，赵盾去世，郤缺接掌晋国中军。陈国转与楚国讲和，晋成公便联合宋、卫、郑、曹讨陈。" },
        { speaker = "", text = "晋成公行军途中病逝，联军只得撤回。其子据即位，是为晋景公，郤缺继续主持晋国军政。" },
        { speaker = "", text = "同年，楚庄王再次亲自伐郑，军至柳棼。郑军正面受压，晋景公急命郤缺率军驰援。" },
        { speaker = "郑襄公", text = "楚军兵势强盛，正面已经被压在柳棼东境。郑军只求守住阵线，等待晋国援军从侧后破敌。" },
        { speaker = "公子去疾", text = "臣率郑军坚守不出。只要楚军的目光仍盯着正面，郤缺便有机会沿西北柳林绕到其侧后。" },
        { speaker = "郤缺", text = "楚军远来攻郑，阵势向东，西北柳林正是其视线死角。晋军不与中军硬撞，先断其步弓两线。" },
        { speaker = "军令", text = "晋军沿西北道路推进，郤缺进入（20，11）周围三格即发动奇袭。奇袭后击溃楚军步兵与弓手主线；郑军只会坚守攻击。" }
    },
    events = {
        { id = "liufen_flank", trigger = "approach", position = {20,11}, radius = 3, speaker = "郤缺", text = "楚军侧后就在眼前！步兵截断退路，弓手压住中军，骑兵从柳林间隙直插其阵！" }
    },
    victory = {
        { speaker = "", text = "晋军突然从西北柳林杀出，楚军步弓两线首尾不能相顾。郑军同时从正面鼓噪，楚军阵势迅速动摇。" },
        { speaker = "楚庄王", text = "郤缺不争正面，却从我军侧后下手。柳棼地势不利久战，传令收束各部，次第南撤。" },
        { speaker = "郤缺", text = "楚王已经退军，不可因追逐一时战果而误入伏地。整顿阵列，护送郑军收复柳棼。" },
        { speaker = "", text = "郤缺袭败楚师，郑国危局暂解。楚庄王与郑襄公、公子去疾均按史实存活，战场中的击退只作撤退处理。" },
        { speaker = "", text = "次年，楚军又来伐郑，驻扎在颍水北岸。此时公子归生忧惧成疾，终于病死。" },
        { speaker = "公子去疾", text = "灵公之死不能永远含糊。如今归生已亡，我要查清鼋宴以来的一切，让国人知道真正主谋是谁。" },
        { speaker = "", text = "公子去疾查明公子宋构逆始末，诛杀公子宋，陈尸示众，又剖开归生棺木、驱逐其族，以明执政不能纵逆。" },
        { speaker = "", text = "郑国随后遣使向楚国谢罪，请求罢兵。楚庄王接受郑国解释，并约陈、郑两国在辰陵会盟。" },
        { speaker = "", text = "故事转到陈国。陈灵公名平国，宠信孔宁、仪行父，三人沉溺游宴，朝政日渐荒废。" },
        { speaker = "", text = "陈国大夫泄冶为人刚直，多次忧虑君臣失仪，却始终未能使灵公远离佞臣。" },
        { speaker = "", text = "陈国公子少西之子夏御叔，娶郑穆公之女少妫为妻。少妫后来被称为夏姬，生子夏征舒。" },
        { speaker = "", text = "夏御叔早亡，夏姬居于株林。孔宁与仪行父先后与她私通，又向陈灵公夸耀株林游宴之乐。" },
        { speaker = "孔宁", text = "株林景致清幽，夏氏又善于设宴。主公若肯同行，远胜在宫中听那些拘谨的礼法。" },
        { speaker = "陈灵公", text = "寡人与二卿同游，何必事事避人耳目？明日便往株林，也看看你们称道的人物。" },
        { speaker = "", text = "陈灵公从此屡往株林，与孔宁、仪行父一同放纵。君臣甚至互赠夏姬的贴身衣物，以为戏谑。" },
        { speaker = "仪行父", text = "主公所获之物固然精巧，孔大夫所得也不遑多让。今日上朝，正好让彼此品评一番。" },
        { speaker = "", text = "三人在朝堂上公然以贴身衣物相互取笑，全无君臣礼度。群臣侧目，却无人敢当面进言。" },
        { speaker = "泄冶", text = "朝堂是议论国政之地，岂能成为君臣狎昵的笑场？若再无人劝止，陈国必因羞耻而招来祸乱。" },
        { speaker = "", text = "泄冶整理衣冠，决定当殿直谏。陈灵公能否听从忠言，孔宁、仪行父又将如何应对，要到下一回分解。" },
        { speaker = "军令", text = "柳棼救郑完成，获得1000金币。郤缺保留既有等级；楚庄王、郑襄公、公子去疾均未战死，其余本回未明确死亡的具名角色统一按撤退处理。" }
    },
    defeat = {{ speaker = "", text = "郤缺在柳棼侧击中被击退，晋国援军失去统率，郑国正面防线随之崩溃。" }}
}

gstage = {
    title_id = "BattleOfLiufen52", turn_limit = 25,
    map = { blocked_edges = {}, size = {46,30}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {6,5}, hero = "XiQue45" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 10000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end

function on_deploy(game)
    game:appoint_hero("XiQue45", 1)
end

function on_begin(game)
    game:generate_unit("ZhengXiangGong52", 1, Enum.force.ally, {41,16})
    game:generate_unit("GongZiQuJi52", 1, Enum.force.ally, {39,14})
    game:set_unit_invulnerable("ZhengXiangGong52", true)
    game:set_unit_invulnerable("GongZiQuJi52", true)
    many(game, "JinReliefGuard52", {{5,7},{7,7},{9,6},{8,4}}, Enum.force.own)
    many(game, "JinReliefCavalry52", {{4,4},{10,4},{7,2}}, Enum.force.own)
    many(game, "JinReliefArcher52", {{3,6},{10,7},{5,3}}, Enum.force.own)
    many(game, "ZhengGuard52", {{37,15},{38,17},{40,18},{42,18},{43,15}}, Enum.force.ally)
    many(game, "ZhengArcher52", {{38,13},{41,13},{43,17}}, Enum.force.ally)
    game:generate_unit("ChuZhuangWang51", 1, Enum.force.enemy, {27,17})
    game:set_unit_invulnerable("ChuZhuangWang51", true)
    many(game, "ChuLiufenGuard52", {{28,13},{30,14},{32,15},{34,16},{29,18},{31,19},{33,20},{35,18}}, Enum.force.enemy)
    many(game, "ChuLiufenCavalry52", {{24,14},{26,12},{25,19},{28,21},{36,13},{37,20}}, Enum.force.enemy)
    many(game, "ChuLiufenArcher52", {{26,16},{29,15},{31,17},{33,14},{34,19},{36,17}}, Enum.force.enemy)
end

function on_update(game)
    if not surprise_started and game:is_unit_within("XiQue45", {20,11}, 3) then
        surprise_started = true
        game:push_cmd_speak(0, "郤缺已经迂回到楚军侧后！晋军奇袭发动，击溃楚军步兵与弓手主线即可迫使楚王撤军。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if surprise_started and not game:has_unit("ChuLiufenGuard52") and not game:has_unit("ChuLiufenArcher52") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
'''


def write_stage():
    path = ROOT / "game/sce/dongzhou/stage/52.lua"
    path.write_text(STAGE.replace("__ROWS__", terrain_rows()), encoding="utf-8")


def update_config():
    path = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "ZhengXiangGong52", class = "Lord", stat = {89, 82, 91, 91, 90}, model = "lord-1-red" }
        ,{ id = "GongZiQuJi52", class = "Strategist", stat = {91, 86, 94, 92, 91}, model = "Strategist-1-red" }
        ,{ id = "JinReliefGuard52", class = "Infantry", stat = {86, 90, 84, 88, 86}, model = "infantry-1-red" }
        ,{ id = "JinReliefCavalry52", class = "Cavalry", stat = {87, 92, 83, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "JinReliefArcher52", class = "Archer", stat = {84, 90, 87, 88, 86}, model = "archer-1-red" }
        ,{ id = "ZhengGuard52", class = "Infantry", stat = {84, 88, 83, 86, 85}, model = "infantry-1-red" }
        ,{ id = "ZhengArcher52", class = "Archer", stat = {82, 88, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "ChuLiufenGuard52", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-blue" }
        ,{ id = "ChuLiufenCavalry52", class = "Cavalry", stat = {88, 94, 84, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "ChuLiufenArcher52", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(path, '"50b", "50c", "51" }', '"50b", "50c", "51", "52" }')


def update_gui():
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m082.png"] = (46, 30, 48)

HERO_LABELS.update({
    "ZhengXiangGong52": "郑襄公", "GongZiQuJi52": "公子去疾",
    "JinReliefGuard52": "晋军甲士", "JinReliefCavalry52": "晋军轻骑", "JinReliefArcher52": "晋军弓手",
    "ZhengGuard52": "郑军守卒", "ZhengArcher52": "郑军弓手",
    "ChuLiufenGuard52": "楚军甲士", "ChuLiufenCavalry52": "楚军骑兵", "ChuLiufenArcher52": "楚军弓手",
})
HERO_BIOS.update({
    "ZhengXiangGong52": "郑国国君，名坚。郑灵公遇弑后即位，任用诸位兄弟参与国政，在晋楚争霸之间维持郑国生存。",
    "GongZiQuJi52": "郑穆公之子，字子良。拒绝越次即位，劝郑襄公保全公族，后查明公子宋弑君之罪并加以诛讨。",
})
PORTRAIT_INDEX_BY_HERO.update({"ZhengXiangGong52": 7, "GongZiQuJi52": 45})
SPEAKER_PORTRAIT_INDEX.update({
    "公子宋": 34, "公子归生": 42, "郑灵公": 7, "公子去疾": 45, "郑襄公": 7,
    "郤缺": 37, "楚庄王": 8, "孔宁": 38, "陈灵公": 9, "仪行父": 31, "泄冶": 49,
})

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_prior_test():
    path = ROOT / "rl/chapter51_test.py"
    replace_once(path, 'assert \'"49", "50a", "50b", "50c", "51" }\' in config',
                 'assert \'"49", "50a", "50b", "50c", "51", "52" }\' in config')


def main():
    write_stage()
    update_config()
    update_gui()
    update_prior_test()
    print("Chapter 52 stage, config, GUI metadata, and prior regression anchor updated.")


if __name__ == "__main__":
    main()
