gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "HuaDu81" }
gsites = {
    { id = "mutineer_camp", name = "华督兵营", position = {1, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "song_armory", name = "宋都武库", position = {14, 2}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "song_palace", name = "宋都宫城", position = {9, 0}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "song_palace_gate_inner", name = "宋都宫门内", position = {9, 3}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "song_palace_gate", name = "宋都宫门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "kong_residence", name = "孔府", position = {5, 2}, restore_hp = 15, restore_mp = 5, rewards = {} }
}
gstory = {
    chapter = "第八回·上",
    title = "华督弄权杀二孔 郑忽救齐破北戎",
    battle_title = "宋都兵变",
    objective = "攻破孔父嘉府邸与宫门，消灭宋国守军",
    map_asset = "song-capital-coup.png",
    intro = {
        { speaker = "旁白", text = "宋殇公连年用兵，百姓困苦。太宰华督觊觎孔父嘉之妻，便将军民怨气全都推到孔父嘉身上。" },
        { speaker = "华督", text = "诸军听着：国家七年十一战，都是孔父嘉逼迫君上。今日除掉奸臣，便可休兵！" },
        { speaker = "孔父嘉", text = "华督以私欲煽动乱兵，哪有半分为国之心？守住府门，速报君上！" },
        { speaker = "宋殇公", text = "孔父嘉乃先君托孤重臣。华督敢在国都作乱，禁军随寡人平叛！" },
        { speaker = "军令", text = "华督必须存活。城墙不可跨越，从府门与宫门推进，击溃孔父嘉、宋殇公及守军。" }
    },
    victory = {
        { speaker = "华督", text = "宫门已破，宋国再无人能阻我！" },
        { speaker = "旁白", text = "孔父嘉被乱兵杀害，宋殇公赶来救援，也死于兵变。华督强娶孔妻，孔妻不从，登楼自尽。" },
        { speaker = "旁白", text = "华督迎回在郑国避难的公子冯，立为宋庄公，并重赂齐、鲁、郑、陈诸国求得承认。" },
        { speaker = "下回预告", text = "第八回·下：郑忽救齐，鹊山伏击北戎。" }
    },
    defeat = {
        { speaker = "华督", text = "禁军已经合围，先退出宫城，另寻机会！" }
    }
}
gstage = {
    title_id = "SongCapitalCoup", turn_limit = 18,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "iiiiiiiiiCiiiiiiiii",
            "iiiiiiiiiiiiiiiiiii",
            "iiiiihiiiiiiiibiiii",
            "WWWWWWWWWGWWWWWWWWW",
            "WWWWWWWWWGWWWWWWWWW",
            "mmmfffffffffffffmmm",
            "mmmfffffffffffffmmm",
            "mmmfffffffffffffmmm",
            "mmmfffffffffffffmmm",
            "mmmfffffffffffffmmm",
            "mmmfffffffffffffmmm",
            "eeefffffffffffffeee",
            "eeefffffffffffffeee",
            "eeefffffffffffffeee"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {1, 12}, hero = "HuaDu81" },
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 360 }
}
function on_deploy(game) game:appoint_hero("HuaDu81", 1) end
function on_begin(game)
    game:generate_unit("SongMutineer81", 1, Enum.force.own, {3, 11})
    game:generate_unit("SongMutineer82", 1, Enum.force.own, {3, 13})
    game:generate_unit("SongMutineerArcher81", 1, Enum.force.own, {3, 12})
    game:generate_unit("KongFuJia81", 1, Enum.force.enemy, {5, 2})
    game:generate_unit("SongShangGong81", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("SongPalaceGuard81", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("SongPalaceGuard81", 1, Enum.force.enemy, {11, 2})
    game:generate_unit("SongPalaceGuard81", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("SongPalaceArcher81", 1, Enum.force.enemy, {4, 1})
    game:generate_unit("SongPalaceArcher81", 1, Enum.force.enemy, {13, 1})
end
function on_update(game) end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end