gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "LuHuanGong11", "ZhengLiGong11", "GongZiNi11", "YuanFan11", "QinZi11", "LiangZi11", "TanBo11", "JiHou11", "YingJi11" }
song_reinforcements_arrived = false
gduel_enabled = false
gduels = {}
gsites = {
    { id = "ji_camp", name = "纪国援军营寨", position = {3, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "qi_store", name = "齐军辎重", position = {15, 2}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}
gstory = {
    chapter = "第十一回·中", title = "宋庄公贪赂构兵 郑祭足杀婿逐主", battle_title = "纪城大战",
    objective = "援救纪国，击退齐、宋、卫、燕四国联军",
    map_asset = "m014.png",
    intro = {
        { speaker = "旁白", text = "齐僖公欲灭纪国，联合宋、卫、燕三国大举进兵。纪侯向鲁求救，鲁桓公又请郑厉公合兵来援。" },
        { speaker = "纪侯", text = "四国兵马压境，纪城危在旦夕。今日全仗鲁郑二君相救。" },
        { speaker = "公子溺", text = "齐将公子彭生骁勇，我先缠住他，秦子、梁子随后接应。" },
        { speaker = "原繁", text = "我与檀伯绕击齐营，嬴季可从城中出兵夹攻。" },
        { speaker = "军令", text = "九名具名将领必须存活。先稳住中央，再从两翼夹击；来迟的宋军将在第五回合入场。" }
    },
    victory = {
        { speaker = "旁白", text = "公子溺与公子彭生交锋渐落下风，秦子、梁子及时赶到。原繁、檀伯突入齐营，嬴季也开城夹击。" },
        { speaker = "嬴季", text = "燕军已经先退，卫军阵脚大乱，诸军乘势掩杀！" },
        { speaker = "旁白", text = "齐军大败，公子彭生中箭几死。来迟的宋军也被鲁郑联军击退，纪国暂时解围。" },
        { speaker = "下回预告", text = "第十一回·下：雍纠设宴谋害祭足，郑国东郊再起杀机。" }
    },
    defeat = { { speaker = "纪侯", text = "纪城外援军已溃，寡人只能闭城死守了！" } }
}
gstage = {
    title_id = "BattleOfJiCity", turn_limit = 26,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "FFFFFgggggggggFFFFF",
        "FggggfffffffffggggF",
        "FggffffffffffffbggF",
        "FggfffgggfffffffggF",
        "Fffffggg~~~~ffffggF",
        "Ffffffff~fffffffffF",
        "Fggfffff~fffffggggF",
        "Fggfffff~fffffggggF",
        "Fggffff~~~~ffffgggF",
        "FgggfffffffffffgggF",
        "FggfffffffffffffggF",
        "FggeffffffffffffggF",
        "FgggggggffggggggggF",
        "FFFFFFFFFFFFFFFFFFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {3, 11}, hero = "LuHuanGong11" }, { position = {5, 11}, hero = "ZhengLiGong11" },
        { position = {8, 10}, hero = "GongZiNi11" }, { position = {6, 9}, hero = "YuanFan11" },
        { position = {4, 10}, hero = "QinZi11" }, { position = {10, 10}, hero = "LiangZi11" },
        { position = {12, 9}, hero = "TanBo11" }, { position = {2, 9}, hero = "JiHou11" },
        { position = {3, 8}, hero = "YingJi11" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 620 }
}
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
    game:generate_unit("JiGuard11", 1, Enum.force.own, {1, 10})
    game:generate_unit("QiXiGong11", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("GongZiPengSheng11", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("YanBo11", 1, Enum.force.enemy, {15, 3})
    game:generate_unit("WeiHuiGong11", 1, Enum.force.enemy, {13, 3})

    game:generate_unit("QiGuard11", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("QiGuard11", 1, Enum.force.enemy, {11, 3})

    game:generate_unit("CoalitionArcher11", 1, Enum.force.enemy, {12, 5})
end
function on_update(game)
    if not song_reinforcements_arrived and game:has_unit("SongZhuangGong11") then
        song_reinforcements_arrived = true
    end
    if song_reinforcements_arrived or game:get_turn_current() < 5 then return end

    song_reinforcements_arrived = true
    local song_lord = game:generate_unit("SongZhuangGong11", 1, Enum.force.enemy, {5, 3})
    game:generate_unit("SongGuard11", 1, Enum.force.enemy, {4, 4})
    game:generate_unit("SongArcher11", 1, Enum.force.enemy, {6, 5})
    game:push_cmd_speak(song_lord, "宋军虽迟，今日仍要与齐卫燕合攻纪城！")
end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if song_reinforcements_arrived and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
