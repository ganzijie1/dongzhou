gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "LuHuanGong11", "ZhengLiGong11", "GongZiNi11", "YuanFan11", "QinZi11", "LiangZi11", "TanBo11" }
song_ambush_revealed = false
gduel_enabled = true
gduels = {
    {
        attacker = "LiangZi11", defender = "MengHuo11", exp = 55, outcome = "retreat",
        attacker_speech = "猛获休走，看我这一箭！",
        defender_speech = "鲁军弓手，也敢挡我前锋？",
        result_speech = "猛获右臂中箭，已被公子溺与原繁合围擒住！",
        text = "梁子一箭射中猛获右臂，鲁郑两军乘势将其生擒。"
    }
}
gsites = {
    { id = "allied_camp", name = "鲁郑联营", position = {3, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "song_store", name = "宋军辎重", position = {15, 3}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "suiyang_gate", name = "睢阳城门", position = {8, 0}, restore_hp = 15, restore_mp = 10,
      rewards = {} }
}
gstory = {
    chapter = "第十一回·上", title = "宋庄公贪赂构兵 郑祭足杀婿逐主", battle_title = "鲁郑伐宋",
    objective = "攻破宋军城外阵势；梁子与猛获相邻可触发射臂擒将",
    map_asset = "m013.png",
    intro = {
        { speaker = "旁白", text = "宋庄公索取郑国迎立公子突的重赂，祭足不能尽数交付。宋国遂纠合诸侯侵郑，郑厉公转请鲁国出兵伐宋。" },
        { speaker = "鲁桓公", text = "宋人贪赂构兵，屡侵郑境。鲁军今日与郑军并进，直抵睢阳城下。" },
        { speaker = "郑厉公", text = "南宫长万勇冠宋军，猛获又为先锋，诸将不可轻敌。" },
        { speaker = "公子溺", text = "我与原繁先截猛获，秦子、梁子以弓弩接应，檀伯护住中军。" },
        { speaker = "军令", text = "七名具名将领必须存活。击溃宋军；梁子接近猛获时可触发史实事件。" }
    },
    victory = {
        { speaker = "梁子", text = "猛获右臂中箭，已被我军生擒！" },
        { speaker = "旁白", text = "南宫牛诈败诱敌，南宫长万又从西门设伏。两军鏖战至夜，各有将领被俘，最终交换俘虏而退。" },
        { speaker = "旁白", text = "宋国随后再约齐、卫、燕攻郑，郑国坚守不出。诸侯无功而返，齐国却转而筹划攻纪。" },
        { speaker = "下回预告", text = "第十一回·中：齐宋卫燕围攻纪国，鲁郑两军驰援纪城。" }
    },
    defeat = { { speaker = "鲁桓公", text = "宋军伏兵已出，先整军退回鲁境！" } }
}
gstage = {
    title_id = "LuZhengAttackSong", turn_limit = 22,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "WWWWWWWWGWWWWWWWWWW",
        "FgggggfffffgggggggF",
        "FgggfffffffffffgggF",
        "FggffffffffffffbggF",
        "FggffwwfffwwfffgggF",
        "FggffffffffffffgggF",
        "FffffgggfffgggffffF",
        "FfffggfffffffggfffF",
        "FfffgffffffffggfffF",
        "FfffgggfffffgggfffF",
        "FgggfffffffffffgggF",
        "FggeffffffffffffggF",
        "FgggggggffggggggggF",
        "FFFFFFFFFFFFFFFFFFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {3, 11}, hero = "LuHuanGong11" }, { position = {5, 11}, hero = "ZhengLiGong11" },
        { position = {4, 10}, hero = "GongZiNi11" }, { position = {6, 10}, hero = "YuanFan11" },
        { position = {2, 12}, hero = "QinZi11" }, { position = {7, 12}, hero = "LiangZi11" },
        { position = {8, 11}, hero = "TanBo11" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 560 }
}
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
    game:generate_unit("AlliedGuard11", 1, Enum.force.own, {1, 11})
    game:generate_unit("AlliedArcher11", 1, Enum.force.own, {9, 12})
    game:generate_unit("SongZhuangGong11", 1, Enum.force.enemy, {8, 1})
    
    game:generate_unit("MengHuo11", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("NangongNiu11", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("HuaDu11", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("SongGuard11", 1, Enum.force.enemy, {7, 4})
    
    game:generate_unit("SongArcher11", 1, Enum.force.enemy, {8, 0})
    
end
function on_update(game)
    if not song_ambush_revealed and game:has_unit("NangongChangWan11") then
        song_ambush_revealed = true
    end
    if song_ambush_revealed then return end
    if not game:is_force_within(Enum.force.own, {12, 4}, 4) then return end

    song_ambush_revealed = true
    local changwan = game:generate_unit("NangongChangWan11", 1, Enum.force.enemy, {11, 4})
    game:generate_unit("SongGuard11", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("SongArcher11", 1, Enum.force.enemy, {15, 3})
    game:push_cmd_speak(changwan, "鲁郑军已近西门，伏兵随我截断归路！")
end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if song_ambush_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
