wangguan_taken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QinMuGong29", "MengMingShi26", "XiQiShu26", "BaiYiBing26", "YouYu26" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "wangguan_castle", name = "王官城池", position = {17,5}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wangguan_store_west", name = "王官宝物库", position = {11,7}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "wangguan_store_east", name = "王官宝物库", position = {24,7}, restore_hp = 15, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } },
    { id = "wangguan_gate_left", name = "王官南门", position = {16,17}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wangguan_gate_center", name = "王官南门", position = {17,17}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wangguan_gate_right", name = "王官南门", position = {18,17}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第四十六回·下",
    title = "楚商臣宫中弑父 秦穆公崤谷封尸",
    battle_title = "王官破城",
    objective = "突破王官南门，击退守将及全部普通守军，再由孟明视接近王官城池。连续城墙不可跨越，三格南门可通行并补给；秦穆公及秦国三帅、繇余任一被击退则失败。",
    map_asset = "m072.png",
    intro = {
        { speaker = "", text = "彭衙再败后，孟明视不再急于请战。他补足士卒战车，抚恤阵亡者家属，日夜以忠义训练三军。秦人多以为怯，只有穆公始终信任。" },
        { speaker = "秦穆公", text = "孟明终能报晋，只是时机未到。寡人三次败于晋，更不能因一时议论更换主将。" },
        { speaker = "", text = "次年夏五月，孟明视认为军队已经训练精熟，请秦穆公亲自督战。穆公选车五百乘，厚赠所有从军者家属。" },
        { speaker = "孟明视", text = "若此次仍不能雪耻，臣誓不生还。三军渡河后焚尽舟船，只能向前，不许再想退路。" },
        { speaker = "秦穆公", text = "屡败之后最缺的是士气。焚舟示必死，有进无退，此计可行。" },
        { speaker = "西乞术", text = "王官城墙连续，只有南门三格通道。步军先稳住门外，不能一拥而入堵住弓手射线。" },
        { speaker = "白乙丙", text = "弓军压制城头和门内两翼。孟明率前锋夺门后，我再把射线推进到内街。" },
        { speaker = "繇余", text = "晋国屡胜后必轻视秦军。王官孤城靠近边境，援兵未必敢来，破城后即可震动河东。" },
        { speaker = "王官守将", text = "秦军渡河焚舟，已经没有退路。关紧城门，依托连续城墙消耗他们，等待晋国援军。" },
        { speaker = "军令", text = "城墙整格不可跨越，三格南门是唯一通道并具有补给效果。先击退守军，再让孟明视接近北部王官城池结束战斗。" }
    },
    events = {
        { id = "south_gate", trigger = "approach", position = {17,17}, radius = 2, speaker = "孟明视", text = "南门就在前方。甲士分列左右，给白乙的弓手留下射线！" },
        { id = "inner_street", trigger = "approach", position = {17,12}, radius = 2, speaker = "西乞术", text = "秦军已经进入内街。沿南北大道推进，不要分散到城墙死角。" },
        { id = "castle", trigger = "approach", position = {17,5}, radius = 1, speaker = "王官守将", text = "晋国援军终究没有出现。王官已无法继续坚守，撤出北门！" }
    },
    victory = {
        { speaker = "", text = "孟明视率前锋突破王官南门，西乞术稳住内街，白乙丙以弓军压住两翼。守将见援军不至，率残部撤走，王官遂归秦军。" },
        { speaker = "", text = "消息传到绛州，晋襄公召集群臣。赵衰认为秦国倾国而来、君主亲征，困兽之斗不可硬挡；先且居也赞成四境坚守、不与交锋。" },
        { speaker = "晋襄公", text = "传谕各城只守不战，让秦军稍逞其志，以此结束连年兵祸。" },
        { speaker = "繇余", text = "晋军已经避让。主公可乘胜前往崤山，收葬当年死士遗骨，洗去全军旧耻。" },
        { speaker = "", text = "秦穆公自茅津渡河，屯兵东崤。晋国没有一人一骑迎战。秦军在堕马崖、绝命岩、落魂涧收集遗骨，以草铺衬，合葬山谷。" },
        { speaker = "秦穆公", text = "当年寡人不听蹇叔、百里奚哭谏，使三军葬身此地。今日亲自沥酒谢罪，愿死者英灵归土。" },
        { speaker = "", text = "孟明视、西乞术、白乙丙伏地痛哭，三军无不落泪。汪、彭衙二邑百姓也逐走晋国守将，重新归秦。" },
        { speaker = "", text = "秦穆公凯旋后升孟明视为亚卿，西乞术、白乙丙一并加封，改蒲津关为大庆关。西戎主赤班见秦势复振，率二十余国纳地朝秦。" },
        { speaker = "周襄王", text = "秦伯任好并国二十、称霸西戎，强盛不亚于晋国。虽不便同时册为侯伯，也当赐金鼓以示嘉奖。" },
        { speaker = "军令", text = "王官破城完成，获得6800金币。第46回全部剧情与关卡完成。" }
    },
    defeat = {
        { speaker = "", text = "秦军在王官南门受阻，具名将领先遭重创。焚舟之后无路可退，只能设法渡河收拢残军。" }
    }
}

gstage = {
    title_id = "WangguanSiege46", turn_limit = 28,
    map = { blocked_edges = {}, size = {36, 28}, terrain = {
        "rFFFFrFFFFrFFFFrFFFFrFFFFrFFFFrFFFFr",
        "FFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrF",
        "FmFFFFmWWWWWWWWWWWWWWWWWWWWWWFFmFFFF",
        "FFFFmFFWiiiiiiiiiiiiiiiiiiiiWmFFFFmF",
        "FrmFFgwWiiiiiiiiiiiiiiiiiiiiWgfgmFFF",
        "rFFFwwFWiiiiiiiiiCiiiiiiiiiiWgFgFFFr",
        "FFFmFfgWiiiiiiiiiiiiiiiiiiiiWfwwFmrF",
        "FmFFggFWiiibiiiiiiiiiiiibiiiWwFgFFFF",
        "FFFFFwwWiiiiiiiiiiiiiiiiiiiiWgfgFFmF",
        "FrmFwgFWiiiiiiiiiiiiiiiiiiiiWgFwmFFF",
        "rFFFFfgWiiiiiiiiiiiiiiiiiiiiWwwfFFFr",
        "FFFmggFWiiiiiiiiiiiiiiiiiiiiWgFgFmrF",
        "FmFFFwfWiiiiiiiiiiiiiiiiiiiiWgfgFFFF",
        "FFFFggFWiiiiiiiiiiiiiiiiiiiiWgFwFFmF",
        "FrmFFfgWiiiiiiiiiiiiiiiiiiiiWwgfmFFF",
        "rFFFgwFWiiiiiiiiiiiiiiiiiiiiWgFgFFFr",
        "FFFmFgfWiiiiiiiiiiiiiiiiiiiiWgfwFmrF",
        "FmFFggFWWWWWWWWWGGGWWWWWWWWWWwFgFFFF",
        "FFFFFfwwgfgfgwwfgfgfwwgfgfgwwfgfFFmF",
        "FrmFwwFggggwwgggggwwgggggwwgggFgmFFF",
        "rFFFFgfgfwwgfgfgwwfgfgfwwgfgfgwwFFFr",
        "FFFmggFwwgFgggFwggFggwFgggFgwwFgFmrF",
        "FmFFFwwfFfgfFwgfFfgwFfgfFfwwFfgfFFFF",
        "FFFFwgFgggFwggFggwFgggFgwwFgggFwFFmF",
        "FrmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFF",
        "rFFFFmFFFFmFFFFmFFFFmFFFFmFFFFmFFFFr",
        "FFFmrFFFmrFFFmrFFFmrFFFmrFFFmrFFFmrF",
        "FmFrFFmFrFFmFrFFmFrFFmFrFFmFrFFmFrFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {17,24}, hero = "QinMuGong29" },
        { position = {17,21}, hero = "MengMingShi26" },
        { position = {14,23}, hero = "XiQiShu26" },
        { position = {20,23}, hero = "BaiYiBing26" },
        { position = {19,25}, hero = "YouYu26" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6800 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_begin(game)
    game:generate_unit("WangguanCommander46", 1, Enum.force.enemy, {17,5})
    generate_many(game, "WangguanGuard46", {{16,17},{17,17},{18,17},{13,14},{21,14},{15,10},{19,10},{17,8}}, Enum.force.enemy)
    generate_many(game, "WangguanArcher46", {{13,16},{21,16},{11,12},{23,12},{14,7},{20,7}}, Enum.force.enemy)
    generate_many(game, "QinGuard46", {{15,21},{19,21},{13,22},{21,22}}, Enum.force.own)
    generate_many(game, "QinCavalry46", {{11,23},{23,23},{15,25},{21,25}}, Enum.force.own)
    generate_many(game, "QinArcher46", {{12,24},{22,24},{16,26},{20,26}}, Enum.force.own)
end

local function defenders_alive(game)
    return game:get_num_units_alive("WangguanCommander46") + game:get_num_units_alive("WangguanGuard46")
        + game:get_num_units_alive("WangguanArcher46")
end

function on_update(game)
    if not wangguan_taken and defenders_alive(game) == 0 and game:is_unit_within("MengMingShi26", {17,5}, 1) then
        wangguan_taken = true
        game:push_cmd_speak(0, "孟明视已经占领王官城池。晋军援兵没有出现，城中守军全部撤离。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if wangguan_taken then return Enum.status.victory end
    return Enum.status.undecided
end
