gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "GongZiLu5", "GaoQuMi" }

gsites = {
    {
        id = "zheng_east_gate", name = "郑国东门", position = {4, 7},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "coalition_outpost", name = "联军前哨", position = {15, 5},
        restore_hp = 10, restore_mp = 0,
        rewards = { { item = "medicine", amount = 1 } }
    }
}

gstory = {
    chapter = "第五回",
    title = "宠虢公周郑交质 助卫逆鲁宋兴兵",
    battle_title = "东门诱敌",
    objective = "击退联军前锋，完成诱敌后撤",
    map_asset = "m005.jpg",
    intro = {
        { speaker = "旁白", text = "共叔段死后，其子公孙滑借卫兵攻取廪延。郑庄公先修书说明原委，卫桓公知是助逆，急令撤军。" },
        { speaker = "高渠弥", text = "卫军虽退，公孙滑仍占廪延。臣愿领兵夺回城邑，使叛乱再无余波。" },
        { speaker = "旁白", text = "高渠弥击走公孙滑，郑、卫暂且言和。此后周平王欲分政于虢公忌父，引起郑庄公猜忌。" },
        { speaker = "周平王", text = "朕命太子狐入质于郑，郑国也遣世子忽居周，以释君臣之间的疑心。" },
        { speaker = "旁白", text = "天子与诸侯互换人质，君臣名分自此愈发衰微。平王死后，太子狐悲恸而亡，其子林继位，是为周桓王。" },
        { speaker = "周桓王", text = "郑伯久专王政，又曾留先太子为质。朕将政事交给虢公，不再受郑国挟制。" },
        { speaker = "郑庄公", text = "我郑氏两代辅周，今日却被弃如敝履。祭足可往温、洛之间取麦禾，试看周王如何处置。" },
        { speaker = "旁白", text = "祭足割取温地麦禾、成周稻谷，周桓王却隐忍未发。郑庄公随后与齐僖公在石门结盟，世子忽又辞去齐国婚事。" },
        { speaker = "旁白", text = "卫国公子州吁一向暴戾好武，与石厚合谋刺杀卫桓公，篡得君位。为立威服众，他决定发兵攻郑。" },
        { speaker = "州吁", text = "郑、齐已有石门之盟，单凭卫国难以取胜。可重赂宋、鲁，再约陈、蔡，五国合兵围郑！" },
        { speaker = "旁白", text = "宋殇公因公子冯寄居郑国而应允出兵；鲁公子翚贪受重赂，也私自率军来会。五国联军围住郑国东门。" },
        { speaker = "郑庄公", text = "州吁新行篡逆，只想借战功压服卫人。宋、鲁、陈、蔡各怀心思，绝无久战之志。" },
        { speaker = "郑庄公", text = "先送公子冯往长葛，引宋军移营；公子吕再出东门挑战，击乱前锋后佯败而回。州吁得了虚名，自会退兵。" },
        { speaker = "公子吕", text = "臣领步骑出城搦战。待联军前锋阵脚动摇，便依号令退回东门。" },
        { speaker = "军令", text = "从郑国东门出击，击退地图上的卫国及诸侯联军前锋；不要恋战追入联军本阵。" }
    },
    victory = {
        { speaker = "公子吕", text = "联军前锋已乱！依主公号令，鸣金收兵，退回东门！" },
        { speaker = "旁白", text = "宋军听闻公子冯移往长葛，果然转营追去；陈、蔡、鲁三军本无战意，也开始准备撤兵。" },
        { speaker = "州吁", text = "郑军既已退去，我军也算得胜。卫国新政未稳，不必再在郑境久留。" },
        { speaker = "旁白", text = "五国联军很快散去。州吁虽以战胜自夸，卫国百姓仍不归心，反而愈加怨恨其弑君自立。" },
        { speaker = "石厚", text = "民心不服，君位难安。不如请教我父石碏，求一条安定卫国之策。" },
        { speaker = "石碏", text = "州吁、石厚弑君作乱，天理难容。欲安卫国，唯有大义灭亲。" },
        { speaker = "下回预告", text = "第六回：卫石碏大义灭亲，郑庄公假命伐宋。" }
    },
    defeat = {
        { speaker = "公子吕", text = "联军人数众多，我军阵形已乱。先退入东门，再依主公之计出战！" },
        { speaker = "旁白", text = "诱敌之计尚未完成，郑军必须重新整顿部署。" }
    }
}

gstage = {
    title_id = "ZhengEastGateFeint",
    turn_limit = 18,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FggWffffffffffffffF",
            "FggWffffffffffffffF",
            "FggWffffFFFFFFFfffF",
            "FggWffffFFFFFFFfffF",
            "FggWfffffffffffbffF",
            "FggWffffffffffffffF",
            "FggeefffffffffffffF",
            "FggWfffffffFffffffF",
            "FggWfffffffFffffffF",
            "FggWffffffffffffffF",
            "FggWffffffffffffffF",
            "FgggggggggggggggggF",
            "FFFFFFFFFFFFFFFFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 7}, hero = "GongZiLu5" },
            { position = {5, 6}, hero = "GaoQuMi" },
            { position = {5, 8}, hero = "ZhengEastGuard" },
            { position = {6, 7}, hero = "ZhengEastArcher" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 300 }
}

function on_deploy(game)
    game:appoint_hero("GongZiLu5", 1)
    game:appoint_hero("GaoQuMi", 1)
    game:appoint_hero("ZhengEastGuard", 1)
    game:appoint_hero("ZhengEastArcher", 1)
end

function on_begin(game)
    game:generate_unit("ZhouXu5", 1, Enum.force.enemy, {15, 5})
    game:generate_unit("ShiHou5", 1, Enum.force.enemy, {16, 4})
    game:generate_unit("WeiVanguard", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("WeiVanguard", 1, Enum.force.enemy, {14, 6})
    game:generate_unit("CoalitionGuard", 1, Enum.force.enemy, {13, 7})
    game:generate_unit("CoalitionGuard", 1, Enum.force.enemy, {16, 8})
    game:generate_unit("CoalitionGuard", 1, Enum.force.enemy, {14, 10})
    game:generate_unit("CoalitionGuard", 1, Enum.force.enemy, {17, 6})
end

function on_update(game) end

function on_victory(game)
end

function on_defeat(game)
end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then
        return Enum.status.defeat
    end
    if game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
