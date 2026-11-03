gate_spoken = false
denghun_spoken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "PiBao36", "ChongEr27", "GongZiZhi30", "HuYan27", "ZhaoShuai27", "WeiChou27" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "PiBao36", defender = "DengHun36", exp = 80, outcome = "kill",
        attacker_speech = "丕豹奉秦君之命为公子开路，邓惛还不下城！",
        defender_speech = "令狐尚有甲兵，岂容亡公子入晋！",
        result_speech = "丕豹先登突阵，邓惛被擒斩首，令狐守军顿失号令。",
        text = "原著明载丕豹攻破令狐，获将邓惛而斩之。"
    }
}
gsites = {
    { id = "linghu_castle", name = "令狐城池", position = {10, 3}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "linghu_treasure", name = "令狐宝物库", position = {6, 6}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "linghu_gate_left", name = "令狐南门", position = {9, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "linghu_gate_center", name = "令狐南门", position = {10, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "linghu_gate_right", name = "令狐南门", position = {11, 8}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第三十六回·上",
    title = "晋吕郤夜焚公宫 秦穆公再平晋乱",
    battle_title = "令狐破城",
    objective = "击退邓惛后，由重耳占领北城城池。丕豹、重耳、公子絷、狐偃、赵衰、魏犨任一被击退即失败。",
    map_asset = "m059.png",
    intro = {
        { speaker = "", text = "狐毛、狐偃得知父亲狐突因拒绝召回二子而被晋怀公杀害，伏地痛哭。重耳也为老臣守义而死悲恸不已。" },
        { speaker = "狐偃", text = "父亲以死全忠，正是催促我们迎公子归晋。若仍迟疑，反使忠魂无所归依。" },
        { speaker = "", text = "晋大夫栾盾暗遣家人求见，说明吕省、郤芮专权失众，国内已有多人愿作内应。" },
        { speaker = "栾盾", text = "怀公猜忌群臣，百姓怨苦。公子若有秦师相助，晋人必开门相迎。" },
        { speaker = "重耳", text = "我流亡十九年，不敢以私怨残害晋民。入境之后，军士不得侵掠，违者军法从事。" },
        { speaker = "", text = "秦穆公命公子絷率兵护送重耳，又以丕豹为先锋，公孙枝等整备舟师，直指黄河。" },
        { speaker = "公子絷", text = "令狐是入晋门户。邓惛若闭城拒守，须迅速破之，不能让吕省、郤芮从容集兵。" },
        { speaker = "丕豹", text = "臣父丕郑死于晋乱，今日愿先登令狐，为公子扫清归国之路。" },
        { speaker = "", text = "行至黄河岸边，狐偃捧出重耳流亡以来的旧器，佯言渡河后便当辞去。" },
        { speaker = "狐偃", text = "臣多年以谲诈冒犯公子，今日大事将成，请从此告退。" },
        { speaker = "重耳", text = "若返晋之后忘记诸君的劳苦，河神在上，必厌弃此身！" },
        { speaker = "", text = "狐偃听罢，将旧器投入河中。群臣皆拜，君臣猜疑至此尽释。" },
        { speaker = "", text = "秦晋联军渡过黄河，先取郇地。令狐守将邓惛拒绝归附，关闭南门，列弓手于城上。" },
        { speaker = "邓惛", text = "怀公有命，敢迎重耳者族诛！令狐军民各守城垣，不得擅开城门。" },
        { speaker = "赵衰", text = "城墙不可跨越，南面三格门道是唯一正路。弓手会压住狭道，须先清其两翼。" },
        { speaker = "魏犨", text = "等先锋破门，我便直冲城中。只要邓惛一败，守兵自会瓦解。" },
        { speaker = "公子絷", text = "秦军只助公子靖乱，不争晋地。诸军听令，保护重耳入城，不得抢掠民舍。" },
        { speaker = "军令", text = "攻入令狐，击退邓惛；随后让重耳走到北部城池格。城墙为不可通行地形，南门可通行并可补给。" }
    },
    events = {
        { id = "linghu_gate", trigger = "approach", position = {10, 8}, radius = 2, speaker = "丕豹", text = "门道虽窄，左右城墙却无缺口。弓手压制城头，步骑依次入门！" },
        { id = "denghun_falls", trigger = "defeated", unit = "DengHun36", speaker = "令狐守军", text = "邓将军已败，吕省、郤芮又不见援军，何必再为怀公送死！" }
    },
    victory = {
        { speaker = "", text = "丕豹率众先登，攻破令狐，擒获邓惛。依军令将邓惛斩首，其余降卒尽数赦免。" },
        { speaker = "重耳", text = "今日所诛只在首恶。令狐百姓仍安居如故，秦晋军士不得扰民。" },
        { speaker = "", text = "桑泉、臼衰两邑闻令狐已破，相继开门归附。重耳声势大振，晋国旧臣纷纷响应。" },
        { speaker = "", text = "吕省、郤芮见怀公众叛亲离，转而杀死怀公，遣人迎接重耳，企图掩盖旧罪。" },
        { speaker = "狐偃", text = "二人反复无常，不可尽信。但国人望公子已久，可先入曲沃，再定君位。" },
        { speaker = "", text = "重耳抵达曲沃，朝见祖庙。群臣拥立，是为晋文公。" },
        { speaker = "晋文公", text = "流亡十九年方归宗国，当修政安民、赏功赦罪，不使晋国再陷骨肉相残。" },
        { speaker = "", text = "晋怀公逃至高梁，最终被杀。晋国表面平定，吕省、郤芮却因畏惧追究旧恶而暗怀异心。" },
        { speaker = "吕省", text = "重耳亲信皆从亡旧臣，我们即使献城，也难免日后被清算。" },
        { speaker = "郤芮", text = "不如约勃鞮夜焚公宫，趁乱除去重耳。只要火起，宫内外便无法相救。" },
        { speaker = "", text = "二人秘密聚集死士，约定纵火日期，却不知道勃鞮已将密谋记在心中。" },
        { speaker = "勃鞮", text = "我曾奉献公、惠公之命追杀重耳，那是各为其主。如今吕郤谋反，我不能坐视晋国再乱。" },
        { speaker = "", text = "绛都夜色渐深，宫墙外已有可疑兵卒聚集。勃鞮请求入宫面见文公，警报将至。" },
        { speaker = "军令", text = "令狐已定，获得4500金币。下一战转入绛宫火变，需保护救援主将并击退吕省、郤芮。" }
    },
    defeat = {
        { speaker = "", text = "秦晋联军主将受创，令狐守军趁门道狭窄发动反击，重耳返国之路被迫中断。" }
    }
}

gstage = {
    title_id = "LinghuSiege36", turn_limit = 20,
    map = { blocked_edges = {}, size = {21, 15}, terrain = {
        "mmFFfffggfffffggfFFmm",
        "mmFFWWWWWWWWWWWWWFFmm",
        "mmFFWiiiiiiiiiiiWFFmm",
        "mmFFWihiiiCiiihiWFFmm",
        "mmFFWiiiiiiiiiiiWFFmm",
        "mmFFWiiiiiiiiiiiWFFmm",
        "mmFFWibiiiiiiiiiWFFmm",
        "mmFFWiiiiiiiiiiiWFFmm",
        "mmFFWWWWWGGGWWWWWFFmm",
        "mmFFgfffffggfffffFFmm",
        "mmgfffffggfffffggffmm",
        "gfffffggfffffggfffffg",
        "ffffggfffffggfffffggf",
        "ffggfffffggfffffggfff",
        "ggfffffggfffffggfffff"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {10, 12}, hero = "PiBao36" },
        { position = {9, 13}, hero = "ChongEr27" },
        { position = {8, 13}, hero = "GongZiZhi30" },
        { position = {10, 13}, hero = "HuYan27" },
        { position = {11, 13}, hero = "ZhaoShuai27" },
        { position = {12, 13}, hero = "WeiChou27" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4500 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("QinGuard36", 1, Enum.force.own, {7, 12})
    game:generate_unit("QinGuard36", 1, Enum.force.own, {13, 12})
    game:generate_unit("QinArcher36", 1, Enum.force.own, {8, 12})
    game:generate_unit("QinArcher36", 1, Enum.force.own, {12, 12})
    game:generate_unit("DengHun36", 1, Enum.force.enemy, {10, 3})
    game:generate_unit("LinghuGuard36", 1, Enum.force.enemy, {10, 8})
    game:generate_unit("LinghuGuard36", 1, Enum.force.enemy, {9, 7})
    game:generate_unit("LinghuGuard36", 1, Enum.force.enemy, {11, 7})
    game:generate_unit("LinghuGuard36", 1, Enum.force.enemy, {6, 5})
    game:generate_unit("LinghuGuard36", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("LinghuArcher36", 1, Enum.force.enemy, {7, 7})
    game:generate_unit("LinghuArcher36", 1, Enum.force.enemy, {13, 7})
    game:generate_unit("LinghuArcher36", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("LinghuArcher36", 1, Enum.force.enemy, {13, 4})
end

function on_update(game)
    if not denghun_spoken and not game:has_unit("DengHun36") then
        denghun_spoken = true
        game:push_cmd_speak(0, "邓惛已败，令狐守军号令大乱！护送重耳进入北城城池。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("DengHun36") and game:is_unit_within("ChongEr27", {10, 3}, 0) then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
