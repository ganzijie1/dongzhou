gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "JiZu11", "QiangChu11", "GongZiE11" }
enemy_ambush_revealed = false
own_ambush_revealed = false
yongjiu_id = -1
gduel_enabled = true
gduels = {
    {
        attacker = "QiangChu11", defender = "YongJiu11", exp = 60, outcome = "kill",
        attacker_speech = "毒酒已经败露，雍纠还不束手！",
        defender_speech = "伏兵何在？快替我拿下祭足！",
        result_speech = "公子阏已破伏兵，雍纠无人可救！",
        text = "强鉏率勇士擒住雍纠，祭足下令将其斩首示众。"
    }
}
gsites = {
    { id = "jizu_camp", name = "祭氏家兵营", position = {3, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "banquet_store", name = "东郊宴亭", position = {14, 3}, restore_hp = 15, restore_mp = 20,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}
gstory = {
    chapter = "第十一回·下", title = "宋庄公贪赂构兵 郑祭足杀婿逐主", battle_title = "东郊反杀",
    objective = "击破伏兵，强鉏与雍纠相邻可触发擒杀事件",
    map_asset = "m015.png",
    intro = {
        { speaker = "旁白", text = "郑厉公怨祭足专政，暗使雍纠在东郊设宴，以毒酒谋害岳父。雍纠之妻祭氏闻知内情，急告父亲。" },
        { speaker = "祭足", text = "女儿以父为亲，已将毒谋尽数告知。强鉏带勇士随我赴宴，公子阏率百名家兵埋伏在外。" },
        { speaker = "雍纠", text = "岳父请满饮此杯，今日只叙翁婿之情。" },
        { speaker = "祭足", text = "这杯酒还是洒在地上，看它究竟藏了什么！" },
        { speaker = "公子阏", text = "毒酒变色，伏兵也已现身。家兵随我杀入园中！" },
        { speaker = "军令", text = "祭足、强鉏、公子阏必须存活。击破伏兵，强鉏接近雍纠时触发史实处决。" }
    },
    victory = {
        { speaker = "祭足", text = "雍纠伏诛。郑突既要杀我，我便不能再容他在位。" },
        { speaker = "旁白", text = "郑厉公闻变逃往蔡国。祭足迎回公子忽，重新立为郑君，是为郑昭公。" },
        { speaker = "旁白", text = "宋庄公贪赂而构兵，郑厉公谋杀权臣而失国，诸侯间的旧怨又添新仇。" },
        { speaker = "下回预告", text = "第十二回：待续。" }
    },
    defeat = { { speaker = "祭足", text = "家兵未能接应，东郊宴亭已经落入雍纠伏兵之手！" } }
}
gstage = {
    title_id = "EasternSuburbCounterplot", turn_limit = 16,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "FFFFFFFFFFFFFFFFFFF",
        "FgggggggggggggggggF",
        "FgggffffffffffggggF",
        "FggffffffffffbggggF",
        "FggfffgggggffffgggF",
        "FffffggfffggffffffF",
        "FfffggfffffggfffffF",
        "FfffggfffffggfffffF",
        "FffffggfffggffffffF",
        "FgggffffffffffggggF",
        "FggfffffffffffffggF",
        "FggeffffffffffffggF",
        "FgggggggffggggggggF",
        "FFFFFFFFFFFFFFFFFFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {3, 11}, hero = "JiZu11" }, { position = {5, 10}, hero = "QiangChu11" },
        { position = {7, 11}, hero = "GongZiE11" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 500 }
}
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)


    yongjiu_id = game:generate_unit("YongJiu11", 1, Enum.force.enemy, {14, 3})
    
end
function on_update(game)
    if not enemy_ambush_revealed and game:has_unit("ZhengAmbusher11") then
        enemy_ambush_revealed = true
    end
    if not own_ambush_revealed and game:has_unit("JiClanGuard11") then
        own_ambush_revealed = true
    end
    if not enemy_ambush_revealed and game:is_force_within(Enum.force.own, {14, 3}, 4) then
        enemy_ambush_revealed = true
        game:generate_unit("ZhengAmbusher11", 1, Enum.force.enemy, {11, 4})
        game:generate_unit("ZhengAmbusher11", 1, Enum.force.enemy, {13, 5})
        game:generate_unit("ZhengAmbusher11", 1, Enum.force.enemy, {15, 5})
        game:generate_unit("ZhengAmbusher11", 1, Enum.force.enemy, {12, 7})
        game:generate_unit("ZhengAmbushArcher11", 1, Enum.force.enemy, {15, 7})
        game:push_cmd_speak(yongjiu_id, "祭足已入宴亭，伏兵立即动手！")
    end

    if enemy_ambush_revealed and not own_ambush_revealed
       and game:is_force_within(Enum.force.enemy, {9, 8}, 7) then
        own_ambush_revealed = true
        local family_guard = game:generate_unit("JiClanGuard11", 1, Enum.force.own, {2, 10})
        game:generate_unit("JiClanArcher11", 1, Enum.force.own, {6, 12})
        game:push_cmd_speak(family_guard, "雍纠伏兵已现，祭氏家兵随公子阏反击！")
    end
end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    local required = #gcommanders
    if game:get_num_commanders_alive() < required then return Enum.status.defeat end
    if enemy_ambush_revealed and own_ambush_revealed
       and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
