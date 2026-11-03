gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhengZhuangGong72", "GaoQuMi72", "XiaShuYing72", "QiXiGong72", "LuYinGong72" }
gsites = {
    { id = "allied_camp", name = "三国联营", position = {8, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "xu_store", name = "许都府库", position = {9, 2}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 2 } } },
    { id = "xu_gate", name = "许都城门", position = {9, 4}, restore_hp = 20, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第七回·下",
    title = "公孙阏争车射考叔 公子翚献谄贼隐公",
    battle_title = "许都夺城",
    objective = "突破许都城门，击溃许庄公守军",
    map_asset = "m010-camp-v2.png",
    intro = {
        { speaker = "旁白", text = "郑军大破戴城以后，齐、鲁与郑三国转兵攻许。第三日，颍考叔率先登城，举起郑伯大旗。" },
        { speaker = "旁白", text = "公孙阏因争车旧怨，暗中一箭射中颍考叔后心。颍考叔坠城而死，凶手混在军中，无人看清。" },
        { speaker = "瑕叔盈", text = "颍将军虽死，军旗不可倒！我来执旗，诸军随我登城！" },
        { speaker = "郑庄公", text = "先取城门，不得扰害百姓。许君若退，留其宗祀，不可赶尽杀绝。" },
        { speaker = "许庄公", text = "城头已经失守，仍要护住宗庙。百里，带守军守住最后一道门！" },
        { speaker = "军令", text = "五名有姓名将领必须存活。城墙不可通行，须从城门突破；击溃许军。" }
    },
    victory = {
        { speaker = "瑕叔盈", text = "城门已开，三国军旗都登上许都城头！" },
        { speaker = "旁白", text = "许庄公出奔卫国，百里护送许叔退守东偏。郑庄公没有吞并许国，只令许叔奉祀先君。" },
        { speaker = "郑庄公", text = "天子尚不能令诸侯，郑国又怎能长据许地？留许叔在此，也好让后人知道我并非贪土。" },
        { speaker = "旁白", text = "班师后，庄公查问颍考叔之死，却始终没有找到放暗箭的人。公孙阏心中惶惧，不久暴死。" },
        { speaker = "旁白", text = "与此同时，鲁公子翚向公子轨进谗，派人弑杀鲁隐公，拥立公子轨为鲁桓公，自己出任太宰。" },
        { speaker = "下回预告", text = "第八回·上：华督煽动兵变，宋都宫门染血。" }
    },
    defeat = {
        { speaker = "郑庄公", text = "登城军已经被截断，先退回联营，整顿云梯再攻！" }
    }
}
gstage = {
    title_id = "SiegeOfXu", turn_limit = 24,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFFFWWWWWWWWWFFFFF",
            "FFFFFWffffffffWFFFF",
            "FFFFFWfffbffffWFFFF",
            "FFFFFWffffffffWFFFF",
            "FFFFFWWWWGWWWWWFFFF",
            "FggggffffffffffgggF",
            "FgggffffggffffffggF",
            "FggffffggggffffffgF",
            "Ffffffgggggffffffff",
            "FffffggfffffggffffF",
            "FfffggfffffffggfffF",
            "FffggfffefffffggffF",
            "FggggfffffffffggggF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {8, 11}, hero = "ZhengZhuangGong72" },
            { position = {6, 10}, hero = "GaoQuMi72" },
            { position = {9, 9}, hero = "XiaShuYing72" },
            { position = {4, 11}, hero = "QiXiGong72" },
            { position = {12, 11}, hero = "LuYinGong72" },
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 420 }
}
function on_deploy(game)
    game:appoint_hero("ZhengZhuangGong72", 1)
    game:appoint_hero("GaoQuMi72", 1)
    game:appoint_hero("XiaShuYing72", 1)
    game:appoint_hero("QiXiGong72", 1)
    game:appoint_hero("LuYinGong72", 1)
end
function on_begin(game)
    game:generate_unit("AlliedGuard72", 1, Enum.force.own, {7, 12})
    game:generate_unit("AlliedArcher72", 1, Enum.force.own, {10, 12})
    game:generate_unit("XuZhuangGong72", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("BaiLi72", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("XuGuard72", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("XuGuard72", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("XuGuard72", 1, Enum.force.enemy, {10, 3})
    game:generate_unit("XuArcher72", 1, Enum.force.enemy, {8, 1})
    game:generate_unit("XuArcher72", 1, Enum.force.enemy, {10, 1})
end
function on_update(game) end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end