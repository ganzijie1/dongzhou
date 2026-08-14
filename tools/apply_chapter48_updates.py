import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def terrain_rows(manifest_name: str) -> str:
    data = json.loads((ROOT / "assets/lzc/map_sources" / manifest_name).read_text(encoding="utf-8"))
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE_48A = r'''ambush_triggered = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "DouYueJiao48", "WeiJia48" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "decoy_northwest", name = "楚军行营", position = {15,9}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "decoy_northeast", name = "楚军行营", position = {23,9}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "decoy_command", name = "空营中军帐", position = {19,14}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "decoy_southwest", name = "楚军行营", position = {15,19}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "decoy_southeast", name = "楚军行营", position = {23,19}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十八回·上",
    title = "刺先克五将乱晋 召士会寿馀绐秦",
    battle_title = "郑境诱营",
    objective = "诱使郑国三将从东门深入空营，在中军帐两格范围内触发伏兵；随后击退公子坚、公子庞、乐耳即视为生擒。营寨围栏不可跨越，东西两门各有两格通道。我方斗越椒或蔿贾被击退则失败。",
    map_asset = "m075.png",
    intro = {
        { speaker = "", text = "令狐夜袭之后，赵盾执晋国政权。先都、士谷、箕郑父、梁益耳、蒯得五人各怀旧怨，暗中结党，准备先除先克，再谋赵盾。" },
        { speaker = "先都", text = "赵盾专权，先克又倚中军副将之势逼迫同僚。若再迟疑，晋国再没有我等容身之处。" },
        { speaker = "箕郑父", text = "我掌军政而被他夺职；梁益耳、蒯得也因令狐失车获罪。五家合力，先克不足惧。" },
        { speaker = "", text = "先都派人趁先克在箕城无备，将他刺死。赵盾迅速查明主谋，把五将一并收捕。" },
        { speaker = "赵盾", text = "国有常刑，私怨不可坏军法。先都等五人谋乱杀卿，皆依法伏诛，不许再牵连家族。" },
        { speaker = "", text = "狐射姑在翟国听到消息，怨赵盾如夏日烈阳，又念旧主先蔑如冬日可爱，却终究无力回晋。" },
        { speaker = "狐射姑", text = "赵孟如夏日之日，人人畏其炎威；先蔑如冬日之日，人人怀其温厚。晋政自此尽归赵氏了。" },
        { speaker = "", text = "晋国内乱的消息传到郢都。楚穆王认为晋国暂时无暇南顾，命斗越椒、蔿贾率兵攻郑。" },
        { speaker = "楚穆王", text = "郑附晋而晋不能救，正可折其北盟。斗越椒主兵，蔿贾参谋，务必迫郑穆公低头。" },
        { speaker = "斗越椒", text = "郑军若守城不出，强攻徒损兵力。我在边境故意扎下一座空营，留草人旗帜诱他们来夺。" },
        { speaker = "蔿贾", text = "我军分伏南北，营内只留假将。郑兵贪功入门后，先封退路，再收紧两翼。" },
        { speaker = "", text = "郑穆公派公子坚、公子庞、乐耳领兵迎敌。三将远望楚营旗帜整齐，却不见巡逻军士。" },
        { speaker = "公子坚", text = "楚人弃营而走，正是夺取辎重的机会。若等主力赶到，首功便轮不到我们。" },
        { speaker = "乐耳", text = "营门洞开而鼓声不断，恐怕有诈。最好先遣小队探明，再让大军入内。" },
        { speaker = "公子庞", text = "楚军深入郑境，听闻我三路齐出，自然仓皇撤退。眼前空营岂可白白放过！" },
        { speaker = "蔿贾", text = "郑军果然争功。等三将都靠近中军帐再举火，不可惊散前锋。" },
        { speaker = "斗越椒", text = "北翼由我截住，南翼听你号令。要的是活捉三将，迫郑国服楚，不必滥杀。" },
        { speaker = "军令", text = "从南北两翼控制斗越椒、蔿贾。郑国任一具名将领进入中军帐两格范围，楚军伏兵才会出现；围栏整格阻挡，只能从东西营门通行。" }
    },
    events = {
        { id = "zheng_enters_decoy", trigger = "approach", position = {19,14}, radius = 2, speaker = "蔿贾", text = "三将已经深入空营，举火合围，先封住东门退路！" }
    },
    victory = {
        { speaker = "", text = "郑军深入空营后，楚军从南北两翼杀出，东门退路也被伏兵截断。公子坚、公子庞、乐耳先后力尽被俘。" },
        { speaker = "斗越椒", text = "绑缚三将，不得伤其性命。郑君若愿服楚，这三人便是议和的凭据。" },
        { speaker = "郑穆公", text = "晋国自顾不暇，郑国孤立无援。请归还三将，我愿遣使向楚谢罪，重新从楚。" },
        { speaker = "蔿贾", text = "大王所求是郑国归盟，不是多造仇怨。既已请服，三位将军即刻释放。" },
        { speaker = "", text = "楚军随后进逼陈国。陈公子朱与公子茷出战失利，陈共公也被迫向楚屈服。" },
        { speaker = "", text = "晋国救兵来到时，郑、陈已经降楚，只得退军。楚穆王在厥貉大会诸侯，声势大振。" },
        { speaker = "楚穆王", text = "郑、陈既服，蔡、许随盟，中原诸侯当知楚国号令。宋国若仍自矜，便以田猎试其诚意。" },
        { speaker = "", text = "诸侯会猎，宋臣未能按楚令驱兽，被申舟鞭责。南北之间的新一轮冲突由此埋下伏笔。" },
        { speaker = "军令", text = "郑境诱营完成，获得6500金币。三名郑将均按原著判定为被俘并释放，不记入阵亡名单；下一关转入河曲之战。" }
    },
    defeat = {
        { speaker = "", text = "诱营尚未合围，斗越椒或蔿贾已经被击退。楚军伏兵失去号令，只能撤出郑境。" }
    }
}

gstage = {
    title_id = "ZhengDecoyCamp48", turn_limit = 24,
    map = { blocked_edges = {}, size = {40, 28}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {18,3}, hero = "DouYueJiao48" },
        { position = {18,25}, hero = "WeiJia48" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6500 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("StrawDecoy48", 1, Enum.force.ally, {19,14})
    game:set_unit_invulnerable("StrawDecoy48", true)
    game:generate_unit("GongZiJian48", 1, Enum.force.enemy, {35,12})
    game:generate_unit("GongZiPang48", 1, Enum.force.enemy, {36,14})
    game:generate_unit("YueEr48", 1, Enum.force.enemy, {35,16})
    generate_many(game, "ZhengGuard48", {{32,10},{33,12},{33,16},{32,18},{30,13},{30,15}}, Enum.force.enemy)
    generate_many(game, "ZhengCavalry48", {{34,9},{36,11},{36,17},{34,19}}, Enum.force.enemy)
    generate_many(game, "ZhengArcher48", {{31,9},{31,19},{37,13},{37,15}}, Enum.force.enemy)
    generate_many(game, "ChuGuard48", {{15,3},{21,3},{15,24},{21,24}}, Enum.force.own)
    generate_many(game, "ChuArcher48", {{16,2},{20,2},{16,25},{20,25}}, Enum.force.own)
end

local function named_zheng_captured(game)
    return not game:has_unit("GongZiJian48") and not game:has_unit("GongZiPang48")
        and not game:has_unit("YueEr48")
end

function on_update(game)
    if not ambush_triggered and (game:is_unit_within("GongZiJian48", {19,14}, 2)
        or game:is_unit_within("GongZiPang48", {19,14}, 2)
        or game:is_unit_within("YueEr48", {19,14}, 2)) then
        ambush_triggered = true
        game:push_cmd_speak(0, "郑军三将已经进入空营！楚军南北两翼齐出，东门伏兵截断退路；具名郑将击退后按被俘处理。")
        generate_many(game, "ChuGuard48", {{29,11},{29,12},{29,16},{29,17},{24,4},{24,23}}, Enum.force.own)
        generate_many(game, "ChuCavalry48", {{31,11},{31,17},{25,5},{25,22}}, Enum.force.own)
        generate_many(game, "ChuArcher48", {{27,9},{27,19},{23,5},{23,22}}, Enum.force.own)
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_triggered and named_zheng_captured(game) then return Enum.status.victory end
    return Enum.status.undecided
end
'''


STAGE_48B = r'''sortie_started = false
rescue_started = false
rescue_turn = 0
qin_retreat = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoDun47", "XunLinFu47", "XiQue45", "YuPian48", "LuanDun45", "XuJia48", "ZhaoChuan48", "HanJue48" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "qin_northwest", name = "秦军行营", position = {11,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_northeast", name = "秦军行营", position = {18,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_command", name = "秦军中军帐", position = {14,15}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "qin_southwest", name = "秦军行营", position = {11,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_southeast", name = "秦军行营", position = {18,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_northwest", name = "晋军行营", position = {42,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_northeast", name = "晋军行营", position = {49,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_command", name = "晋军中军帐", position = {46,15}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "jin_southwest", name = "晋军行营", position = {42,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_southeast", name = "晋军行营", position = {49,21}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十八回·下",
    title = "刺先克五将乱晋 召士会寿馀绐秦",
    battle_title = "河曲之战",
    objective = "坚守晋营，令赵穿从东营出击至河曲中央，引出秦军后由任一晋军具名将领与他相邻完成接应；赵穿返回晋营中军七格范围并坚持三个回合，秦军即于夜间撤退。秦康公、西乞术、白乙丙、士会依原著均不可阵亡。我方任一具名将领被击退则失败。",
    map_asset = "m076.png",
    intro = {
        { speaker = "", text = "令狐之败五年后，秦康公仍以晋军夜袭、公子雍被杀为耻，亲率大军渡河，攻取晋国羁马。" },
        { speaker = "秦康公", text = "晋人背盟袭营，又害公子雍。今日进至河曲，正要让赵盾偿还令狐旧债。" },
        { speaker = "赵盾", text = "秦师远来，锋锐正盛。荀林父将中军，郤缺佐之；臾骈将上军，栾盾佐之；胥甲将下军，赵穿佐之。" },
        { speaker = "", text = "晋军列阵时，赵盾的车右擅自驰入队列。韩厥依军法将他斩首，然后向主帅请罪。" },
        { speaker = "韩厥", text = "军令不避贵近。主帅车右乱阵，臣已按法处置；若有罪，请连臣一并治罪。" },
        { speaker = "赵盾", text = "执法不阿，正是军中所需。车右虽亲近，坏阵便当死；韩厥无罪，反当记功。" },
        { speaker = "臾骈", text = "秦军渡河而来，求战心切。我军深沟高垒，不与争锋，待其粮尽气衰再动。" },
        { speaker = "赵盾", text = "就依臾骈之计。各军守营，不得擅出；秦人挑战辱骂，也只当没有听见。" },
        { speaker = "士会", text = "晋军众将多能守令，唯赵穿勇而少谋，受不得激。集中兵力挑战下军，他必定出阵。" },
        { speaker = "秦康公", text = "若能引赵穿离营，再围而歼之，晋军必来救援。那时由局部交锋撕开全阵。" },
        { speaker = "赵穿", text = "秦人在营外日夜辱骂，我身为下军之佐，岂能躲在围栏后面看他们逞威！" },
        { speaker = "胥甲", text = "主帅已有坚壁之令。你若孤军深入，秦军左右一合，我下军也会被拖出营去。" },
        { speaker = "赵穿", text = "畏敌才会失去军心。我只领本部冲到河曲中央，击退挑战者便回，不必诸军相助。" },
        { speaker = "荀林父", text = "赵穿若真出营，不能坐视他被围。中、上两军随时准备开门接应，但不可追入秦营。" },
        { speaker = "郤缺", text = "救人而不乱阵才是关键。接到赵穿后立刻退回东营，以营门和弓弩挡住秦军。" },
        { speaker = "军令", text = "东西两座大营的围栏均不可跨越，四座营门各为两格通道。赵穿到达河曲中央才算出战；友军与他相邻后，护送他返回东营中军附近。" }
    },
    events = {
        { id = "zhao_chuan_sortie", trigger = "approach", position = {30,15}, radius = 2, speaker = "赵穿", text = "秦军休得猖狂！赵穿已经出营，来与我在河曲决一胜负！" },
        { id = "jin_rescue", trigger = "adjacent", speaker = "荀林父", text = "诸军已经接应赵穿，边战边退，回到晋营后坚守三回合！" }
    },
    victory = {
        { speaker = "", text = "赵穿擅自出战，晋国三军被迫出营接应。双方鏖战至暮，各有损伤，仍未分胜负。" },
        { speaker = "秦康公", text = "晋人不肯决战，明日再遣使下书。若他们仍避战，便从河曲渡口逼近其垒。" },
        { speaker = "臾骈", text = "秦使辞强而神色不定，说明他们也怕久驻。今夜可在河岸设伏，待秦军半渡而击。" },
        { speaker = "", text = "赵穿、胥甲不满臾骈得计，暗中把半渡邀击的谋划泄露给秦军。秦康公当夜拔营，晋军追之不及。" },
        { speaker = "赵盾", text = "泄漏军谋使秦师得脱，胥甲难逃军法。河曲虽未大败，却错过了结束秦患的机会。" },
        { speaker = "", text = "又过五年，赵盾思念留秦的士会，召集六卿商议迎回之法。魏寿馀自请诈降秦国。" },
        { speaker = "寿馀", text = "臣佯称与魏邑争讼、叛晋归秦，再献魏地。秦君若要辨认城邑，必会派熟知晋事的士会同行。" },
        { speaker = "韩厥", text = "寿馀逃出国境，我照约捕其妻子，使秦国相信他确已反晋。戏必须做足，才瞒得过士会。" },
        { speaker = "", text = "寿馀入秦献魏，秦康公果然命士会前往受地。绕朝看破其中有诈，把马鞭赠给士会送行。" },
        { speaker = "绕朝", text = "使事若成，晋国得一良臣，秦国失一智士。此鞭赠你，过河以后，莫忘今日故人。" },
        { speaker = "士会", text = "君命与故国都不可轻负。既已走到河边，前路如何，只能由我自己承担。" },
        { speaker = "", text = "寿馀与士会登舟渡河，晋国接应之军已在东岸等候。秦晋数年的离合，至此又翻开新局。" },
        { speaker = "军令", text = "河曲之战完成，获得6800金币。秦、晋具名将领均按原著保留；士会归晋作为后续剧情承接。" }
    },
    defeat = {
        { speaker = "", text = "晋军具名将领在接应途中被击退，三军阵势崩散。河曲坚壁之策宣告失败。" }
    }
}

gstage = {
    title_id = "BattleOfHequ48", turn_limit = 28,
    map = { blocked_edges = {}, size = {54, 32}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {46,15}, hero = "ZhaoDun47" },
        { position = {44,11}, hero = "XunLinFu47" },
        { position = {47,11}, hero = "XiQue45" },
        { position = {44,19}, hero = "YuPian48" },
        { position = {47,19}, hero = "LuanDun45" },
        { position = {49,13}, hero = "XuJia48" },
        { position = {41,15}, hero = "ZhaoChuan48" },
        { position = {49,17}, hero = "HanJue48" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6800 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("QinKangGong48", 1, Enum.force.enemy, {14,15})
    game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {12,11})
    game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {17,11})
    game:generate_unit("ShiHui47", 1, Enum.force.enemy, {15,20})
    for _, hero in ipairs({"QinKangGong48", "XiQiShu26", "BaiYiBing26", "ShiHui47"}) do
        game:set_unit_invulnerable(hero, true)
    end
    generate_many(game, "QinGuard48", {{10,8},{14,8},{18,8},{10,13},{18,13},{10,18},{18,18},{10,23},{14,23},{18,23}}, Enum.force.enemy)
    generate_many(game, "QinCavalry48", {{12,9},{16,9},{11,15},{17,15},{12,22},{16,22}}, Enum.force.enemy)
    generate_many(game, "QinArcher48", {{9,11},{19,11},{9,20},{19,20},{20,14},{20,17}}, Enum.force.enemy)
    generate_many(game, "JinGuard48", {{41,8},{45,8},{49,8},{41,12},{49,12},{41,19},{49,19},{41,23},{45,23},{49,23}}, Enum.force.own)
    generate_many(game, "JinCavalry48", {{43,9},{47,9},{42,14},{48,14},{43,22},{47,22}}, Enum.force.own)
    generate_many(game, "JinArcher48", {{40,10},{50,10},{40,21},{50,21},{40,14},{40,17}}, Enum.force.own)
end

local function jin_has_reached_zhao(game)
    for _, hero in ipairs({"ZhaoDun47", "XunLinFu47", "XiQue45", "YuPian48", "LuanDun45", "XuJia48", "HanJue48"}) do
        if game:are_units_within(hero, "ZhaoChuan48", 1) then return true end
    end
    return false
end

function on_update(game)
    if not sortie_started and game:is_unit_within("ZhaoChuan48", {30,15}, 2) then
        sortie_started = true
        game:push_cmd_speak(0, "赵穿不听坚壁军令，已经冲到河曲中央。秦军两翼合拢，晋国三军必须出营接应。")
        generate_many(game, "QinCavalry48", {{24,12},{24,19},{27,14},{27,17}}, Enum.force.enemy)
        generate_many(game, "QinArcher48", {{22,10},{22,21},{25,15}}, Enum.force.enemy)
    end
    if sortie_started and not rescue_started and jin_has_reached_zhao(game) then
        rescue_started = true
        rescue_turn = game:get_turn_current()
        game:push_cmd_speak(0, "晋军已经接到赵穿！不要追入秦营，护送他退回东侧晋营，依托营门再守三回合。")
    end
    if rescue_started and not qin_retreat and game:get_turn_current() >= rescue_turn + 3
        and game:is_unit_within("ZhaoChuan48", {46,15}, 7) then
        qin_retreat = true
        game:push_cmd_speak(0, "秦军察觉晋军准备在河岸设伏，连夜拔营西撤。河曲之战就此结束。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if qin_retreat then return Enum.status.victory end
    return Enum.status.undecided
end
'''


def write_stages() -> None:
    stage_dir = ROOT / "game/sce/dongzhou/stage"
    (stage_dir / "48a.lua").write_text(
        STAGE_48A.replace("__ROWS__", terrain_rows("m075_ch48a_manifest.json")), encoding="utf-8"
    )
    (stage_dir / "48b.lua").write_text(
        STAGE_48B.replace("__ROWS__", terrain_rows("m076_ch48b_manifest.json")), encoding="utf-8"
    )


def update_config() -> None:
    path = ROOT / "game/sce/dongzhou/config.lua"
    hero_block = '''        ,{ id = "DouYueJiao48", class = "Cavalry", stat = {90, 96, 88, 90, 86}, model = "cavalry-1-red" }
        ,{ id = "WeiJia48", class = "Strategist", stat = {88, 82, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "StrawDecoy48", class = "Infantry", stat = {60, 60, 60, 60, 60}, model = "infantry-1-red" }
        ,{ id = "GongZiJian48", class = "Lord", stat = {85, 88, 84, 86, 84}, model = "lord-1-blue" }
        ,{ id = "GongZiPang48", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "YueEr48", class = "Archer", stat = {82, 88, 86, 85, 84}, model = "archer-1-blue" }
        ,{ id = "ChuGuard48", class = "Infantry", stat = {84, 90, 80, 85, 83}, model = "infantry-1-red" }
        ,{ id = "ChuCavalry48", class = "Cavalry", stat = {85, 91, 80, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "ChuArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "ZhengGuard48", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "ZhengCavalry48", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "ZhengArcher48", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "QinKangGong48", class = "Lord", stat = {88, 86, 92, 88, 86}, model = "lord-1-blue" }
        ,{ id = "YuPian48", class = "Strategist", stat = {86, 80, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "XuJia48", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ZhaoChuan48", class = "Cavalry", stat = {86, 94, 76, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "HanJue48", class = "Strategist", stat = {88, 88, 94, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "JinGuard48", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-red" }
        ,{ id = "JinCavalry48", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "QinGuard48", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "QinCavalry48", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "QinArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", hero_block + "    },\n    equipments = {},")
    replace_once(path, '"47a", "47b" }', '"47a", "47b", "48a", "48b" }')


def update_gui() -> None:
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m075.png"] = (40, 28, 48)
_LARGE_BATTLE_MAPS["m076.png"] = (54, 32, 48)

HERO_LABELS.update({
    "DouYueJiao48": "斗越椒", "WeiJia48": "蔿贾", "StrawDecoy48": "草人疑兵",
    "GongZiJian48": "公子坚", "GongZiPang48": "公子庞", "YueEr48": "乐耳",
    "ChuGuard48": "楚军甲士", "ChuCavalry48": "楚军骑兵", "ChuArcher48": "楚军弓手",
    "ZhengGuard48": "郑军甲士", "ZhengCavalry48": "郑军骑兵", "ZhengArcher48": "郑军弓手",
    "QinKangGong48": "秦康公", "YuPian48": "臾骈", "XuJia48": "胥甲",
    "ZhaoChuan48": "赵穿", "HanJue48": "韩厥",
    "JinGuard48": "晋军甲士", "JinCavalry48": "晋军骑兵", "JinArcher48": "晋军弓手",
    "QinGuard48": "秦军甲士", "QinCavalry48": "秦军骑兵", "QinArcher48": "秦军弓手",
})
HERO_BIOS.update({
    "DouYueJiao48": "楚国若敖氏名将，字伯棼。奉楚穆王命攻郑，以空营诱敌，配合蔿贾生擒郑国三将。",
    "WeiJia48": "楚国名臣，字伯嬴。善察人谋，辅佐斗越椒设空营伏兵，迫使郑、陈重新服楚。",
    "GongZiJian48": "郑国公子，奉郑穆公命迎击楚军，因争功深入空营，被楚军伏兵生擒后释放。",
    "GongZiPang48": "郑国将领，与公子坚、乐耳共同追入楚军空营，遭南北合围被俘，郑服楚后获释。",
    "YueEr48": "郑国将领，随公子坚迎战楚军，虽怀疑空营有诈，仍陷伏兵，后随二公子获释。",
    "QinKangGong48": "秦穆公之子。为报令狐之败率军攻晋，在河曲与晋军相持，识破半渡伏击后夜间撤军。",
    "YuPian48": "晋国上军主将，河曲之战主张坚壁不战；后从秦使神色中判断敌情，提出半渡而击。",
    "XuJia48": "晋国下军主将，河曲之战参与接应赵穿，后来因泄露臾骈的半渡伏击之谋而获罪。",
    "ZhaoChuan48": "晋国将领，赵夙之后。河曲之战不耐秦军挑战而擅自出营，迫使晋国三军共同接应。",
    "HanJue48": "晋国将领，执法严明。河曲列阵时斩赵盾乱阵车右而不避权贵，获得赵盾器重。",
    "StrawDecoy48": "楚军设置在空营中军帐内的草人假将，用旗鼓和假阵吸引郑军深入。",
    "ChuGuard48": "埋伏于空营南北两翼、负责封锁郑军退路的楚国甲士。",
    "ChuCavalry48": "在郑军进入空营后迅速合围东门的楚国骑兵。",
    "ChuArcher48": "依托营寨围栏压制郑军、以生擒三将为目标的楚军弓手。",
    "ZhengGuard48": "随郑国三将进入楚军空营的甲士。",
    "ZhengCavalry48": "争先追击楚军疑兵、陷入伏击的郑国骑兵。",
    "ZhengArcher48": "为郑国追击部队提供远射支援的弓手。",
    "JinGuard48": "河曲之战中依托东侧营寨坚守并接应赵穿的晋军甲士。",
    "JinCavalry48": "从晋营出击接应赵穿、随后掩护全军回营的晋军骑兵。",
    "JinArcher48": "驻守晋营门口、压制秦军追兵的晋军弓手。",
    "QinGuard48": "随秦康公进至河曲、负责守卫西侧大营的秦军甲士。",
    "QinCavalry48": "按照士会之计挑战赵穿并准备两翼合围的秦军骑兵。",
    "QinArcher48": "在河曲中央压制晋军接应部队的秦军弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "DouYueJiao48": 34, "WeiJia48": 49, "GongZiJian48": 7, "GongZiPang48": 35,
    "YueEr48": 24, "QinKangGong48": 7, "YuPian48": 45, "XuJia48": 25,
    "ZhaoChuan48": 35, "HanJue48": 42,
})
SPEAKER_PORTRAIT_INDEX.update({
    "先都": 25, "箕郑父": 45, "赵盾": 42, "狐射姑": 35, "楚穆王": 7,
    "斗越椒": 34, "蔿贾": 49, "郑穆公": 7, "公子坚": 7, "公子庞": 35,
    "乐耳": 24, "秦康公": 7, "臾骈": 45, "胥甲": 25, "赵穿": 35,
    "韩厥": 42, "荀林父": 37, "郤缺": 31, "士会": 31, "寿馀": 49, "绕朝": 40,
})

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_regression_anchor() -> None:
    path = ROOT / "rl/chapter47_test.py"
    replace_once(
        path,
        'assert \'"46a", "46b", "46c", "47a", "47b" }\' in config',
        'assert \'"46a", "46b", "46c", "47a", "47b", "48a", "48b" }\' in config',
    )


def main() -> None:
    write_stages()
    update_config()
    update_gui()
    update_regression_anchor()
    print("Chapter 48 stages, config, GUI metadata, and prior regression anchor updated.")


if __name__ == "__main__":
    main()
