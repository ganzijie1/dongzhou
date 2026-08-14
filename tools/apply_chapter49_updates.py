import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def terrain_rows() -> str:
    data = json.loads(
        (ROOT / "assets/lzc/map_sources/m077_ch49_manifest.json").read_text(encoding="utf-8")
    )
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE = r'''pursuit_engaged = false
protector_fallen = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "HuaOu49" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第四十九回",
    title = "公子鲍厚施买国 齐懿公竹池遇变",
    battle_title = "孟诸之变",
    objective = "华耦率追兵沿林道追上宋昭公。荡意诸护主期间，宋昭公不可被击退；先击退荡意诸，再击退宋昭公方可过关。史载二人皆死于孟诸，其他昭公近卫被击退均按撤退处理。华耦被击退则失败。",
    map_asset = "m077.png",
    intro = {
        { speaker = "", text = "士会随寿馀渡过黄河，赵朔早已在东岸接应。秦国若派追兵，晋国三军便准备隔河压阵。" },
        { speaker = "赵朔", text = "范叔回国，晋国便重新得到一位能安邦定国的大夫。荀林父、郤缺已列军河上，秦人不敢轻追。" },
        { speaker = "士会", text = "我离晋多年，今日重踏故土，既愧且喜。秦君待我有礼，这份旧情也不能忘记。" },
        { speaker = "", text = "秦康公得知士会已去，非但没有加罪，反将他的妻子儿女送还晋国。秦晋由此暂息兵戈。" },
        { speaker = "", text = "不久周顷王崩，匡王即位；楚穆王亦死，太子侣继位，是为楚庄王。中原与南方都换了新主。" },
        { speaker = "", text = "晋国在新城大会诸侯，蔡国不肯赴会。郤缺奉命伐蔡，蔡侯畏惧请和，晋军随即收兵。" },
        { speaker = "郤缺", text = "蔡既认罪，便不必多杀士卒。会盟所求是服从号令，不是借机灭国。" },
        { speaker = "", text = "齐昭公去世，世子舍继位。公子商人家财雄厚，长期赈济贫民，又供养死士，暗中收买国人。" },
        { speaker = "公子商人", text = "国人受我恩惠，群臣也多与我交好。齐国君位既已动摇，岂能让一个幼主久居其上？" },
        { speaker = "", text = "公子商人杀死世子舍，又欺骗公子元辞让君位，最终自立为君，是为齐懿公。" },
        { speaker = "公子元", text = "你既掌握宫门和甲士，何必还用虚言试我？这君位我不敢受，也不愿受。" },
        { speaker = "", text = "齐懿公囚禁昭姬。周王派单伯护送昭姬回国，懿公却连单伯一并扣押，并发兵侵鲁。" },
        { speaker = "鲁文公", text = "齐国拘王使、侵我境，已失诸侯之礼。应请晋国召集诸侯，共问齐君之罪。" },
        { speaker = "", text = "诸侯会于扈地，本欲讨齐；齐懿公以重礼遍赂卿大夫，又放回昭姬和单伯，诸侯终于散去。" },
        { speaker = "", text = "宋昭公在位十年，疏远宗族，宠信小人。襄夫人与公子鲍素有私情，渐渐生出改立之心。" },
        { speaker = "襄夫人", text = "昭公无道，宋人怨他；公子鲍厚待百姓，国人归心。若要安定宗社，正应立贤。" },
        { speaker = "", text = "公子鲍效法齐国公子商人，散尽财货，遇到饥年更开仓赈粮。宋国百姓都盼望他执政。" },
        { speaker = "公子鲍", text = "百姓若无粮，我守着府库又有何用？先让老弱活过荒年，其他事情以后再说。" },
        { speaker = "", text = "宋昭公先前在朝堂杀公子卬、公孙钟离，荡意诸逃到鲁国。后来他赦免荡意诸，召其回宋。" },
        { speaker = "荡意诸", text = "君上待宗族刻薄，宫中又有异谋。如今忽然出猎孟诸，恐怕不是游乐，而是送身入险。" },
        { speaker = "宋昭公", text = "寡人身为宋君，难道连孟诸都去不得？国中再多怨言，也无人敢在道路上弑君。" },
        { speaker = "", text = "昭公出城后，襄夫人将华元、公孙友扣在宫中，公子须关闭城门，断绝昭公归路。" },
        { speaker = "公子须", text = "城门已经封闭，华元、公孙友也不能出宫。华耦可立即召集国人，追向孟诸。" },
        { speaker = "华耦", text = "昭公失德，宋人苦之已久。愿奉公子鲍为君者，随我出城追击，不可让昭公逃往别国！" },
        { speaker = "", text = "昭公听说追兵已近，有人劝他逃亡。昭公却把随身宝物分给从者，命众人各自求生。" },
        { speaker = "宋昭公", text = "做一国之君而逃亡他国，还不如死在宋地。你们拿走这些财物，不必再陪寡人送命。" },
        { speaker = "荡意诸", text = "臣曾因惧祸而逃，如今蒙君召回，岂能再次背主？追兵若来，先从臣的尸体上过去。" },
        { speaker = "军令", text = "沿孟诸林道由东向西追击。荡意诸存活时宋昭公受护卫锁定；先击退荡意诸，再击退宋昭公。华耦不得被击退。" }
    },
    events = {
        { id = "mengzhu_contact", trigger = "approach", position = {9,14}, radius = 7, speaker = "荡意诸", text = "华耦已经追到孟诸！诸位若要伤害君上，先来与我一战！" },
        { id = "protector_falls", trigger = "unit_defeated", unit = "DangYiZhu49", speaker = "宋昭公", text = "荡意诸为寡人战死，最后一位忠臣也不在了。华耦，来取寡人的性命吧。" }
    },
    victory = {
        { speaker = "", text = "荡意诸始终挡在昭公之前，身受数创仍不退让，最终死于孟诸林道。" },
        { speaker = "华耦", text = "荡意诸忠勇可敬，但宋国今日必须改立新君。众军越过他的尸身，围住昭公！" },
        { speaker = "", text = "宋昭公无路可走，终于被追兵杀死。史载孟诸之变，昭公与荡意诸同日遇害。" },
        { speaker = "", text = "公子鲍继位，是为宋文公。文公任命荡意诸之子荡虺为司城，以表彰其父忠义。" },
        { speaker = "宋文公", text = "荡意诸虽为先君而死，其忠不可废。今日厚恤其家，正是要让宋人知道忠臣有后。" },
        { speaker = "", text = "华耦回城复命后，因心疾突然去世。宋文公改任公子须为司城，稳定宋国朝局。" },
        { speaker = "", text = "晋、卫、陈、郑四国随后联合伐宋，声称要为宋昭公讨罪。宋国正面临新君即位后的第一场危机。" },
        { speaker = "华元", text = "诸侯兴师是为名分，并非真想灭宋。以厚礼结纳晋军主帅，或可免去城下之战。" },
        { speaker = "", text = "华元以财货贿赂荀林父。荀林父接受宋国解释，承认宋文公，四国联军遂退。" },
        { speaker = "郑穆公", text = "出师本为讨弑君之罪，如今受赂便退，晋国号令还有什么公义可言？" },
        { speaker = "", text = "郑穆公因此不服晋国，转而亲近楚国。宋国内乱虽止，中原诸侯的阵线却再次分裂。" },
        { speaker = "", text = "齐懿公即位后愈发暴虐。他掘出邴歜父亲的尸体断足，又夺走阎职之妻，二人都怀恨在心。" },
        { speaker = "邴歜", text = "辱及亡父，此仇不共戴天。齐君明日到申池游乐，正是我们报仇的机会。" },
        { speaker = "阎职", text = "他夺我妻室，我也不愿再忍。等他酒醉入浴，遣散侍从，你我便一同动手。" },
        { speaker = "", text = "齐懿公到申池竹林饮酒，酒醉后入浴。邴歜、阎职支开从者，将懿公杀死在池边。" },
        { speaker = "", text = "二人欲拥立公子元，齐国大臣却另立公子元之子为君，是为齐惠公；邴歜、阎职逃往楚国。" },
        { speaker = "", text = "鲁国方面，公孙敖先后娶莒国姐妹戴己、声己，又因莒女私奔离鲁，家门与国政纠缠不清。" },
        { speaker = "", text = "公孙敖晚年思归，襄仲仲遂为他请命。季孙行父主张不得轻赦逃臣，鲁文公只准归还其尸。" },
        { speaker = "", text = "公孙敖终究未能生还鲁国。其子文伯、惠叔的继嗣之争，也为三桓日后专政增添新的裂痕。" },
        { speaker = "", text = "鲁文公病重，嫡庶诸子争位。仲遂倾向公子俀，叔孙得臣与季孙行父则各怀打算。" },
        { speaker = "仲遂", text = "国君一旦去世，鲁国储位必起大争。谁先得到齐国支持，谁便能在国内掌握主动。" },
        { speaker = "", text = "第四十九回至此结束。齐、宋两国相继弑君，鲁国继承之争又将爆发，诸侯礼法已进一步崩坏。" },
        { speaker = "军令", text = "孟诸之变完成，获得700金币。荡意诸与宋昭公按原著记入阵亡；其他昭公近卫统一按撤退处理。" }
    },
    defeat = {
        { speaker = "", text = "华耦在追击中被击退，拥立公子鲍的部众失去指挥。昭公得以脱离孟诸，政变宣告失败。" }
    }
}

gstage = {
    title_id = "MengzhuIncident49", turn_limit = 22,
    map = { blocked_edges = {}, size = {44, 30}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {36,13}, hero = "HuaOu49" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 7000 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    game:appoint_hero("HuaOu49", 1)
end

function on_begin(game)
    game:generate_unit("SongZhaoGong49", 1, Enum.force.enemy, {9,14})
    game:generate_unit("DangYiZhu49", 1, Enum.force.enemy, {11,14})
    game:set_unit_invulnerable("SongZhaoGong49", true)
    generate_many(game, "RoyalRetainer49", {{7,12},{7,16},{10,11},{10,17},{13,13},{13,15}}, Enum.force.enemy)
    generate_many(game, "RoyalArcher49", {{8,10},{8,18},{14,11},{14,17}}, Enum.force.enemy)
    generate_many(game, "SongCoupGuard49", {{34,11},{34,15},{37,10},{37,16},{39,13}}, Enum.force.own)
    generate_many(game, "SongCoupCavalry49", {{35,12},{35,14},{38,12},{38,14}}, Enum.force.own)
    generate_many(game, "SongCoupArcher49", {{39,10},{39,16},{41,12},{41,14}}, Enum.force.own)
end

function on_update(game)
    if not pursuit_engaged and game:is_unit_within("HuaOu49", {9,14}, 7) then
        pursuit_engaged = true
        game:push_cmd_speak(0, "华耦追兵已进入孟诸西段。荡意诸挡在昭公身前；先击退荡意诸，才能解除宋昭公的护卫锁定。")
    end
    if not protector_fallen and not game:has_unit("DangYiZhu49") then
        protector_fallen = true
        game:set_unit_invulnerable("SongZhaoGong49", false)
        game:push_cmd_speak(0, "荡意诸已经阵亡，宋昭公失去最后的护卫，现在可以被击退。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if protector_fallen and not game:has_unit("SongZhaoGong49") then return Enum.status.victory end
    return Enum.status.undecided
end
'''


def write_stage() -> None:
    stage = STAGE.replace("__ROWS__", terrain_rows())
    (ROOT / "game/sce/dongzhou/stage/49.lua").write_text(stage, encoding="utf-8")


def update_config() -> None:
    path = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "HuaOu49", class = "Cavalry", stat = {88, 92, 82, 89, 86}, model = "cavalry-1-red" }
        ,{ id = "SongZhaoGong49", class = "Lord", stat = {84, 82, 78, 80, 76}, model = "lord-1-blue" }
        ,{ id = "DangYiZhu49", class = "Infantry", stat = {90, 94, 78, 92, 88}, model = "infantry-1-blue" }
        ,{ id = "SongCoupGuard49", class = "Infantry", stat = {84, 89, 80, 85, 83}, model = "infantry-1-red" }
        ,{ id = "SongCoupCavalry49", class = "Cavalry", stat = {85, 91, 80, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "SongCoupArcher49", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "RoyalRetainer49", class = "Infantry", stat = {83, 88, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "RoyalArcher49", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(path, '"47a", "47b", "48a", "48b" }', '"47a", "47b", "48a", "48b", "49" }')


def update_gui() -> None:
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m077.png"] = (44, 30, 48)

HERO_LABELS.update({
    "HuaOu49": "华耦", "SongZhaoGong49": "宋昭公", "DangYiZhu49": "荡意诸",
    "SongCoupGuard49": "拥鲍甲士", "SongCoupCavalry49": "拥鲍骑兵", "SongCoupArcher49": "拥鲍弓手",
    "RoyalRetainer49": "昭公近卫", "RoyalArcher49": "昭公弓手",
})
HERO_BIOS.update({
    "HuaOu49": "宋国司马华耦。宋昭公出猎孟诸时，奉襄夫人与公子鲍之命召集国人追击；事成回城后突发心疾而死。",
    "SongZhaoGong49": "宋国国君，名杵臼。疏远宗族而失去国人支持，出猎孟诸时遭华耦追杀，与忠臣荡意诸一同遇害。",
    "DangYiZhu49": "宋国大夫。曾避祸奔鲁，获宋昭公赦免后归国；孟诸之变中拒绝逃生，独自护主直至战死。",
    "SongCoupGuard49": "受公子鲍恩惠、随华耦追击宋昭公的宋国甲士。",
    "SongCoupCavalry49": "沿孟诸林道追赶宋昭公车驾的拥鲍骑兵。",
    "SongCoupArcher49": "随华耦封锁孟诸林间退路的拥鲍弓手。",
    "RoyalRetainer49": "随宋昭公出猎孟诸的近卫，昭公命其带走财物自行逃生。",
    "RoyalArcher49": "保护宋昭公车驾、在孟诸抵挡追兵的弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "HuaOu49": 34, "SongZhaoGong49": 7, "DangYiZhu49": 25,
})
SPEAKER_PORTRAIT_INDEX.update({
    "赵朔": 37, "士会": 31, "郤缺": 42, "公子商人": 7, "公子元": 18,
    "鲁文公": 7, "襄夫人": 12, "公子鲍": 18, "荡意诸": 25, "宋昭公": 7,
    "公子须": 35, "华耦": 34, "宋文公": 18, "华元": 49, "郑穆公": 7,
    "邴歜": 38, "阎职": 39, "仲遂": 45,
})
HISTORICAL_DEATH_HEROES.update({"DangYiZhu49", "SongZhaoGong49"})

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_prior_test() -> None:
    path = ROOT / "rl/chapter48_test.py"
    replace_once(
        path,
        'assert \'"47a", "47b", "48a", "48b" }\' in config',
        'assert \'"47a", "47b", "48a", "48b", "49" }\' in config',
    )


def main() -> None:
    write_stage()
    update_config()
    update_gui()
    update_prior_test()
    print("Chapter 49 stage, config, GUI metadata, and chapter 48 regression anchor updated.")


if __name__ == "__main__":
    main()
