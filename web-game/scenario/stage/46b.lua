charge_started = false
qin_retreat = false
retreat_announced = {}

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "XianQieJu45", "ZhaoShuai27", "HuJuJu45", "LangTan45" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第四十六回·中",
    title = "楚商臣宫中弑父 秦穆公崤谷封尸",
    battle_title = "彭衙之战",
    objective = "先由狼瞫进入秦军前阵（23，14）两格范围，触发私属百余人冲阵；随后把秦军普通部队压至三人以内。孟明视、西乞术、白乙丙均可击退，结局统一为撤退；我方具名将领任一被击退则失败。",
    map_asset = "m071.png",
    intro = {
        { speaker = "", text = "先轸安葬后，许、蔡两国因晋文公去世重新依附楚国。晋襄公任阳处父为大将伐许侵蔡，楚成王命斗勃、成大心率军救援。" },
        { speaker = "", text = "晋楚两军隔泜水相持两月。岁末晋粮将尽，阳处父提出一方退舍、让另一方渡水决战。成大心担心晋军半渡而击，劝斗勃先退三十里。" },
        { speaker = "阳处父", text = "楚军既退，便宣称斗勃畏晋而走。岁暮天寒，我军立即班师，不必真的渡水。" },
        { speaker = "", text = "斗勃两日后才发现晋军已远去。太子商臣趁机诬陷斗勃受贿避战，楚成王误信谗言，赐剑令斗勃自尽。成大心申明原委，成王由此开始疑惧商臣。" },
        { speaker = "", text = "楚成王偏爱少子职，意图废长立幼。商臣听到传闻后，依太傅潘崇之计故意怠慢王妹江芈，从她怒骂中确认父王确有废立之意。" },
        { speaker = "潘崇", text = "太子若不能屈身事弟，也不能逃亡他国，只有先行大事，才能转祸为福。" },
        { speaker = "", text = "商臣夜半调集宫甲包围王宫。楚成王请求吃完熊掌再死，被潘崇识破拖延求救之意，只得以冠带自缢；江芈悔恨泄密，也随之自尽。" },
        { speaker = "", text = "商臣即位为楚穆王，重用潘崇。斗宜申、仲归谋弑新王失败，被斗越椒擒杀；公子职出逃，也在郊外被追杀。" },
        { speaker = "赵衰", text = "楚成王尚可用礼义劝诫，商臣连父亲都不爱，日后必将祸及诸侯。" },
        { speaker = "", text = "次年春，孟明视请求伐晋雪耻，秦穆公准其与西乞术、白乙丙率四百乘东进。晋襄公命先且居为将，赵衰为副，狐鞫居为车右，向西迎敌。" },
        { speaker = "先且居", text = "与其等秦军进入晋境，不如主动西行。大军直抵彭衙，在边境展开阵势。" },
        { speaker = "狼瞫", text = "先元帅曾以我无勇而罢黜。今日我不求录功，只求率私属先犯秦阵，洗去旧耻。" },
        { speaker = "孟明视", text = "晋军主力尚远，前方只有百余私属。稳住车阵，先挫其锐气，再迎先且居中军。" },
        { speaker = "军令", text = "狼瞫必须先到彭衙中央触发冲阵，晋军主力才能全面推进。秦国三帅均可正常击退，退出战场后统一按撤退处理，不计为历史阵亡。" }
    },
    events = {
        { id = "langtan_charge", trigger = "approach", position = {23,14}, radius = 2, speaker = "狼瞫", text = "鲜伯与诸位私属随我直犯秦阵！今日只论勇烈，不计生还！" },
        { id = "qin_line_breaks", trigger = "enemy_count", count = 3, speaker = "先且居", text = "秦军前阵已乱，全军压上，迫使三帅西退！" }
    },
    victory = {
        { speaker = "", text = "狼瞫与鲜伯率百余人直冲秦阵，所向披靡。白乙丙奋力反击，鲜伯战死；狼瞫身被数创仍不后退。" },
        { speaker = "先且居", text = "秦阵已经被狼瞫打乱。诸军全面掩杀，不可让孟明重新整队！" },
        { speaker = "", text = "晋军乘势推进，孟明视、西乞术、白乙丙不能抵挡，率残军西走。三帅均按撤退处理。" },
        { speaker = "", text = "先且居从乱军中救出狼瞫。狼瞫遍体是伤，呕血一斗有余，次日去世。晋襄公以上大夫之礼葬于西郭，命群臣送葬。" },
        { speaker = "先且居", text = "彭衙今日之胜，全是狼瞫首先破阵之功，与臣无关。请君厚葬勇士，以励后来。" },
        { speaker = "", text = "孟明视回秦自认必死，秦穆公仍亲自郊迎，把战败责任归于自己。孟明于是散尽家财抚恤阵亡之家，日夜训练军士。" },
        { speaker = "", text = "当年冬天，晋襄公又命先且居联合宋大夫公子成、陈大夫辕选、郑大夫公子归生攻秦，夺取汪、彭衙二邑。郭偃所卜一击三伤至此应验。" },
        { speaker = "秦穆公", text = "孟明不是怯懦，只是雪耻之时尚未到。寡人仍以国政相托，任由他补卒搜乘。" },
        { speaker = "军令", text = "彭衙之战完成，获得6000金币。下一关秦穆公亲征王官，孟明焚舟后攻城。" }
    },
    defeat = {
        { speaker = "", text = "狼瞫的冲阵未能撼动秦军，我方具名将领先受重创，先且居只能撤回晋境。" }
    }
}

gstage = {
    title_id = "PengyaBattle46", turn_limit = 22,
    map = { blocked_edges = {}, size = {42, 28}, terrain = {
        "rFFFFrFFFFrFFFFrFFFFrFFFFrFFFFrFFFFrFFFFrF",
        "FFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFF",
        "FmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFm",
        "FFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFF",
        "FrmFFgwwFgfgFwwgFgfgFwfgFgfwFgfgFgwwFgFFFr",
        "rFFFwwFgggFwwgFgggFwggFggwFgggFgwwFgggFFrF",
        "FFFmFfgfFwwfFfgfFwgfFfgwFfgfFfwwFfgfFwmFFF",
        "FmFFggFwwgggggwwgggggwwgggggwwgggggwwgFFFm",
        "FFFFFwwgfgfgwwfgfgfwwgfgfgwwfgfgfwwgFgFmFF",
        "FrmFwgFgggwwgggggwwgggggwwgggggwwgggggFFFr",
        "rFFFFfgfwwgfgfgwwfgfgfwwgfgfgwwfgfgfFwFFrF",
        "FFFmggFwgggggwwgggggwwgggggwwgggggwwggmFFF",
        "FmFFFwfgfgfwwgfgfgwwfgfgfwwgfgfgwwfgFgFFFm",
        "FFFFggFggwwgggggwwgggggwwgggggwwgggggwFmFF",
        "FrmFFfgwwfgfgfwwgfgfgwwfgfgfwwgfgfgwFfFFFr",
        "rFFFgwFgggggwwgggggwwgggggwwgggggwwgggFFrF",
        "FFFmFgfgfgwwfgfgfwwgfgfgwwfgfgfwwgfgFgmFFF",
        "FmFFggFgwwgggggwwgggggwwgggggwwgggggwwFFFm",
        "FFFFFfwwgfgfgwwfgfgfwwgfgfgwwfgfgfwwFfFmFF",
        "FrmFwwFggggwwgggggwwgggggwwgggggwwggggFFFr",
        "rFFFFgfgfwwgfgfgwwfgfgfwwgfgfgwwfgfgFwFFrF",
        "FFFmggFwwgFgggFwggFggwFgggFgwwFgggFwwgmFFF",
        "FmFFFwwfFfgfFwgfFfgwFfgfFfwwFfgfFwwfFfFFFm",
        "FFFFwgFgggFwggFggwFgggFgwwFgggFwwgFgggFmFF",
        "FrmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFr",
        "rFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFrF",
        "FFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFF",
        "FmFrFFmFrFFmFrFFmFrFFmFrFFmFrFFmFrFFmFrFFm"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {7,14}, hero = "XianQieJu45" },
        { position = {5,16}, hero = "ZhaoShuai27" },
        { position = {6,12}, hero = "HuJuJu45" },
        { position = {10,14}, hero = "LangTan45" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6000 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_begin(game)
    game:generate_unit("MengMingShi26", 1, Enum.force.enemy, {35,14})
    game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {34,11})
    game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {34,17})
    generate_many(game, "QinPengyaGuard46", {{29,9},{31,10},{33,12},{30,13},{32,15},{31,18},{29,19}}, Enum.force.enemy)
    generate_many(game, "QinPengyaCavalry46", {{27,10},{29,12},{30,16},{28,18},{36,10},{37,14},{36,18}}, Enum.force.enemy)
    generate_many(game, "QinPengyaArcher46", {{32,8},{35,9},{37,11},{37,17},{35,19},{32,20}}, Enum.force.enemy)
    generate_many(game, "JinGuard46", {{6,13},{8,12},{8,16},{10,17}}, Enum.force.own)
    generate_many(game, "JinArcher46", {{5,11},{5,18},{9,10},{9,18}}, Enum.force.own)
end

local function qin_regular_alive(game)
    return game:get_num_units_alive("QinPengyaGuard46") + game:get_num_units_alive("QinPengyaCavalry46")
        + game:get_num_units_alive("QinPengyaArcher46")
end

function on_update(game)
    if not charge_started and game:is_unit_within("LangTan45", {23,14}, 2) then
        charge_started = true
        game:push_cmd_speak(0, "狼瞫与鲜伯率百余私属直犯秦阵，秦军前列开始动摇！晋军主力可以全面推进。")
        game:generate_unit("XianBo46", 1, Enum.force.ally, {22,15})
        generate_many(game, "JinRetainer46", {{21,12},{21,13},{21,15},{21,16}}, Enum.force.ally)
    end
    local qin_named = {
        { "MengMingShi26", "孟明视" },
        { "XiQiShu26", "西乞术" },
        { "BaiYiBing26", "白乙丙" }
    }
    for _, item in ipairs(qin_named) do
        if not retreat_announced[item[1]] and not game:has_unit(item[1]) then
            retreat_announced[item[1]] = true
            game:push_cmd_speak(0, item[2] .. "已被击退，率领身边残兵退出彭衙战场。")
        end
    end
    if charge_started and not qin_retreat and qin_regular_alive(game) <= 3
        and not game:has_unit("MengMingShi26") and not game:has_unit("XiQiShu26")
        and not game:has_unit("BaiYiBing26") then
        qin_retreat = true
        game:push_cmd_speak(0, "秦国三帅都已退出战场，剩余车阵向西溃退。狼瞫伤重倒下，晋军停止追击。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if qin_retreat then return Enum.status.victory end
    return Enum.status.undecided
end
