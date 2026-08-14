ambush_triggered = false

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
        "FFfgfFFmfgFFgfmFFfgfFFffgFFgmfFFwffFFfff",
        "gfFFffgFFgmfFFfgfFFffgFFmffFFfgmFFfwfFFw",
        "FfgfFFmfgFFgfmFFfgfFFffgFFgmfFFfffFFffwF",
        "fFFffgffgmfgffgfmgffgffmffgffgmffwfffFff",
        "fgffgmfgffgfmgffgffmffgffgmfgffgwmffwfFF",
        "FFffgffgmfgPPPPPPPPPPPPPPPPPPmfgfffwmffw",
        "gfFgmfgffgfPgffgffgffgffgffgPfgfffwffFFm",
        "FffgffgffgfPgffgffgffgffgffgPfgffwfmfwfF",
        "fFFmfgffgffPffgffgffgffgffgfPgffwfffwFmf",
        "ffgffgffgffPffgefgffgffeffgfPgffffmwffFF",
        "FFmfgffgffgPfgffgffgffgffgffPffgffwffmwf",
        "fgFfgmfgffgPfgffgffgffgffgffPffgfwfffFFf",
        "FmfgffgffgfPgffgffgffgffgffgPfgfwfffmffF",
        "gFFgmfgffgffgffgffgffgffgffgffgffffwfFfm",
        "mfgffgffgffgffgffgfegffgffgffgffffwmffFF",
        "FFgmfgffgffPffgffgffgffgffgfPgfffwfffwmf",
        "fgFfgffgffgPfgffgffgffgffgffPffgwfmfwFFf",
        "FgmfgffgffgPfgffgffgffgffgffPffgfffwfmfF",
        "gFFgfmgffgfPgffgffgffgffgffgPfgfffwffFwf",
        "gmfgffgffgfPgffeffgffgfegffgPfgffwffmwFF",
        "FFgfmgffgffPffgffgffgffgffgfPgffwfffwffm",
        "mfFffgffgffPffgffgffgffgffgfPgfffffmfFFw",
        "FgfmgffgffmPPPPPPPPPPPPPPPPPPffmffwfffmF",
        "fFFfgfmgffgffmffgffgmfgffgfmgffgfwmffFff",
        "gfmgffgffmffgffgmfgffgfmgffgffmfwfffwmFF",
        "FFfgfFFffgFFmffFFfgmFFffgFFgffFFfmfFFffw",
        "fmFFfgfFFffgFFgmfFFfgfFFffgFFmffFFwfmFFf",
        "FfgfFFffgFFmffFFfgmFFffgFFgffFFfmwFFfwfF",
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
    game:generate_unit("GongZiJian48", 1, Enum.force.enemy, {36,14})
    game:generate_unit("GongZiPang48", 1, Enum.force.enemy, {35,12})
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
