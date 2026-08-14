xu_surrendered = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChongEr27", "ZhaoShuai27", "HuYan27", "XianZhen27" }
gevents_enabled = true
gsites = {
    { id = "jin_camp_left", name = "晋军行营", position = {13, 20}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_right", name = "晋军行营", position = {18, 20}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "yingyang_palace_west", name = "颍阳城池", position = {14, 5}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "yingyang_palace", name = "颍阳城池", position = {16, 5}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "yingyang_palace_east", name = "颍阳城池", position = {18, 5}, restore_hp = 25, restore_mp = 15, rewards = {} }
}

gstory = {
    chapter = "第四十三回·上",
    title = "智宁俞假鸩复卫 老烛武缒城说秦",
    battle_title = "九国围许",
    objective = "突破颍阳南门，击退许国全部普通守军，迫使许僖公请降。许僖公必须保留性命；晋文公、赵衰、狐偃、先轸任一被击退则失败。",
    map_asset = "m065.png",
    intro = {
        { speaker = "", text = "河阳朝王之后，晋文公命先蔑护送卫成公归周，又密令医衍途中下鸩。宁俞早已看破杀机，重金嘱咐医衍减轻药性，再借神灵示警之名解救卫侯。卫国复位之争暂由鲁僖公、臧孙辰向周王与晋侯申理。" },
        { speaker = "晋文公", text = "许国既不践河阳之会，便是轻王命、慢诸侯。传檄齐、宋、鲁、蔡、陈、秦、莒、邾，同向颍阳问罪。" },
        { speaker = "赵衰", text = "九国之师虽盛，也须申明只讨不朝之罪，不可纵兵扰民。许侯若面缚衔璧而降，当保其宗社。" },
        { speaker = "", text = "郑文公随军未久便托故先归，并暗中向楚国告急。楚成王新败于城濮，不肯再发一卒，颍阳因此失去唯一外援。诸侯军分列四面，晋军在南门外扎下中军行营。" },
        { speaker = "秦穆公", text = "秦晋既约相救，寡人今日亲至许城。只是攻城宜留退路，莫使许人因绝望而死守。" },
        { speaker = "曹共公", text = "寡人从前以无礼得罪晋侯，赖卜人郭偃之言才获归国。今日愿率曹军从征，以功赎过。" },
        { speaker = "晋文公", text = "旧怨已经了结。曹侯复位后能知盟约，便与诸侯并肩列阵。先轸，南门交给你；赵衰、狐偃总摄诸军。" },
        { speaker = "先轸", text = "颍阳城墙连续，除南门两格通道外不可跨越。弓手先压住门内两翼，甲士夺门后向内街展开，不要把部队堵在狭道上。" },
        { speaker = "许僖公", text = "楚国的救兵为何还不见踪影？城中粮少，九国环攻，若南门再失，许国宗庙难保。" },
        { speaker = "许国守将", text = "君上尚在，臣等便守住南门与宫城。即便不能退敌，也要让诸侯知道许人并非不战而降。" },
        { speaker = "军令", text = "击退许国普通守军即可触发许僖公衔璧请降。许僖公生命降至零会原地满血恢复，不能以斩首结束本关。" }
    },
    events = {
        { id = "south_gate", trigger = "approach", position = {15, 14}, radius = 2, speaker = "先轸", text = "南门已在眼前。两格门道可以通行，左右连续城墙都不可跨越；甲士让开射线，不要挡住后方弓手。" },
        { id = "palace", trigger = "approach", position = {16, 7}, radius = 2, speaker = "许僖公", text = "晋军已经攻入内城！楚援终究不至，继续抵抗只会害尽颍阳百姓。" }
    },
    victory = {
        { speaker = "", text = "许国守军退尽，许僖公解去冠服，面缚衔璧出宫请罪。晋文公受璧后立即松绑，命诸军退出民居，只留使者重申朝王与会盟之约。" },
        { speaker = "许僖公", text = "寡人失期于河阳，自知有罪。今日愿奉王命、守盟约，只求诸侯勿伤许国百姓。" },
        { speaker = "晋文公", text = "知罪能改，许国仍守其社稷。诸军解围，不得取一民之财。" },
        { speaker = "", text = "围许既解，秦穆公与晋文公约定两国有警互相救援。晋侯随后得报：郑国表面从征，暗中又与楚国往来，遂生伐郑之意。赵衰以连年用兵为由，请休整一年。" },
        { speaker = "", text = "与此同时，宁俞继续经营卫成公复位。他借孔达联络周歂、冶廑，杀死阻挠归国的元咺一党；卫成公终于重返国都。元咺奔晋申冤，卫国君臣之狱仍留待诸侯裁断。" },
        { speaker = "军令", text = "九国围许完成，获得4800金币。下一关为夜缒说秦：只控制烛之武避开晋军警戒前往秦营，不进行战斗。" }
    },
    defeat = {
        { speaker = "", text = "晋军主将受创，诸侯阵势动摇；颍阳守军乘机封闭南门，问罪之师只能暂退。" }
    }
}

gstage = {
    title_id = "NineStatesBesiegeXu43", turn_limit = 30,
    map = { blocked_edges = {}, size = {32, 24}, terrain = {
        "mmfffFgFffffFgFfffgFfFffggFfFfgg",
        "FfFfggfFfFggffFfFgfffFgFffffFmmf",
        "ffmgFfffWWWWWWWWWWWWWWWWfFggffFf",
        "mgffffggWiiiiiiiiiiiiiiWggffffgm",
        "ffffggffWiiiiiiiiiiiiiiWffffgmff",
        "fmmgffffWiiiiiCiCiCiiiiWffggffff",
        "ggffffggWiiiiiiiiiiiiiiWggffffmm",
        "ffffggffWiiiiiiiiiiiiiiWffffggff",
        "mmggffffWiiiiiiiiiiiiiiWffggffff",
        "ggffffggWiiiiiiiiiiiiiiWggfffmmg",
        "ffmfggffWiiiiiiiiiiiiiiWffffggff",
        "mfggffffWiiiiiiiiiiiiiiWffggfffm",
        "ggffffggWiiiiiiiiiiiiiiWggfffmgg",
        "fmmfggffWiiiiiiiiiiiiiiWffffggff",
        "ffggffffWWWWWWWGGWWWWWWWffggffmm",
        "ggffffggffffggffffggffffggffffgg",
        "mmffggffffggffffggffffggffffggff",
        "ffggffffggPPPPPgfPPPPPffffggfmmf",
        "ggmfffggffPfggffffggfPffggffffgg",
        "mfffggffffPgffffggfffPggffffggfm",
        "ffggffffggPffeggffefgPffffggfmff",
        "FmmffFgFffPfFgFfffgFfPffggFfFfgg",
        "FfFfggfFfFPgffFfFgfffPgFffffFgmm",
        "ffFgFfffgFPPPPPPPPPPPPfFfFggffFf"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {15, 20}, hero = "ChongEr27" },
        { position = {13, 21}, hero = "ZhaoShuai27" },
        { position = {17, 21}, hero = "HuYan27" },
        { position = {19, 21}, hero = "XianZhen27" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4800 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("JinGuard43", 1, Enum.force.own, {12, 19})
    game:generate_unit("JinGuard43", 1, Enum.force.own, {18, 19})
    game:generate_unit("JinArcher43", 1, Enum.force.own, {16, 19})
    game:generate_unit("QinMuGong29", 1, Enum.force.ally, {5, 16})
    game:generate_unit("CaoGongGong39", 1, Enum.force.ally, {26, 16})
    game:generate_unit("GongSunGu33", 1, Enum.force.ally, {27, 12})
    game:generate_unit("GuoGuiFu40", 1, Enum.force.ally, {5, 12})
    game:generate_unit("XuXiGong43", 1, Enum.force.enemy, {16, 5})
    game:set_unit_invulnerable("XuXiGong43", true)
    for _, p in ipairs({{15,14},{16,14},{12,11},{20,11},{14,8},{18,8}}) do
        game:generate_unit("XuGuard43", 1, Enum.force.enemy, p)
    end
    for _, p in ipairs({{11,9},{21,9},{15,7},{17,7}}) do
        game:generate_unit("XuArcher43", 1, Enum.force.enemy, p)
    end
end

function xu_defenders_alive(game)
    return game:get_num_units_alive("XuGuard43") + game:get_num_units_alive("XuArcher43")
end

function on_update(game)
    if not xu_surrendered and xu_defenders_alive(game) == 0 then
        xu_surrendered = true
        game:push_cmd_speak(0, "许军已经放下兵器。许僖公面缚衔璧出宫，颍阳之围到此为止。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if xu_surrendered then return Enum.status.victory end
    return Enum.status.undecided
end
