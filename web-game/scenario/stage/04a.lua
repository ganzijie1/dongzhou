gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QinXiangGong" }
gsites = {
    { id = "qin_camp", name = "秦军营寨", position = {3, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "rong_store", name = "犬戎辎重", position = {15, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}
gstory = {
    chapter = "第四回·上",
    title = "秦文公郊天应梦 郑庄公掘地见母",
    battle_title = "岐丰逐戎",
    objective = "击破伯丁、满也速与犬戎余部，夺回岐丰故地",
    map_asset = "m009.png",
    intro = {
        { speaker = "", text = "周平王迁都洛邑，秦襄公亲率甲兵护送王驾。临别之际，平王召襄公入朝，议论西土归属。" },
        { speaker = "周平王", text = "秦先祖伯益、非子，世代为王室牧马守边。卿此次护驾有功，朕当使秦正式列于诸侯。" },
        { speaker = "秦襄公", text = "臣世居西垂，受犬戎侵逼已久。今岐、丰尽陷敌手，若徒有封爵而无疆土，何以屏藩王室？" },
        { speaker = "周平王", text = "岐、丰本是周室故地，如今为犬戎所据。卿若能驱逐犬戎，所收之地，朕一概赐秦，永作西藩。" },
        { speaker = "", text = "襄公拜受王命，回国后修整车马、清点甲兵，又遣斥候沿渭水探查犬戎营垒。" },
        { speaker = "秦军斥候", text = "伯丁守住东侧山口，满也速屯兵谷中，犬戎主则在后方辎重营压阵。山路狭窄，两翼尽是岩山。" },
        { speaker = "秦襄公", text = "犬戎以为据险便可久守，却不知我秦人世居西陲，最熟山川。先夺谷口，再断其归路。" },
        { speaker = "秦军先锋", text = "末将愿率步卒正面结阵，吸引伯丁；弓手登上缓坡，压住谷内援军。" },
        { speaker = "秦襄公", text = "岐丰本是周室旧土。今日秦军向西，既为天子复土，也为秦国开疆。" },
        { speaker = "伯丁", text = "周人已经弃城东逃，凭你秦国也想夺回关中？" },
        { speaker = "满也速", text = "守住山口，等秦军陷在谷地，再从两翼围杀！" },
        { speaker = "犬戎主", text = "秦军若退，便沿渭水追杀；秦军若进，就让岐山成为他们的葬身之地！" },
        { speaker = "秦襄公", text = "传令各部稳步推进，不可争功冒入绝地。今日一战，要让秦旗重新立在岐丰！" },
        { speaker = "军令", text = "秦襄公必须存活。山地会增加移动消耗，岩山不可通行；击溃犬戎全军。" }
    },
    victory = {
        { speaker = "秦襄公", text = "犬戎阵势已破，乘势收复岐、丰！" },
        { speaker = "伯丁", text = "秦人竟能穿过山谷……岐丰守不住了！" },
        { speaker = "满也速", text = "主公快向西撤，我等已经无力再战！" },
        { speaker = "", text = "伯丁、满也速战死，犬戎主率残部逃往西荒。秦军乘胜收复岐、丰，沿途周民纷纷携粮迎接。" },
        { speaker = "秦军先锋", text = "旧城虽已残破，田野尚可耕种。只要迁民筑城，不出数年，这里便能成为秦国腹地。" },
        { speaker = "秦襄公", text = "今日所得，不只是一战之胜。秦自此有土有民，当世代守住西陲，不负天子所命。" },
        { speaker = "", text = "秦国由此据有关中故地，正式跻身诸侯。襄公凯旋不久去世，太子继位，是为秦文公。" },
        { speaker = "", text = "文公营建城邑、收聚遗民，又梦见黄蛇自天而降。群臣以为是上帝显兆，劝其郊祭白帝。" },
        { speaker = "秦文公", text = "秦既受命于西土，便当立坛郊天、修明政令，使军民知有所守。" },
        { speaker = "", text = "秦文公设鄜畤、祭白帝，秦国根基日益稳固。与此同时，郑国宫门之内，一场兄弟之争正在酝酿。" }
    },
    defeat = {
        { speaker = "秦襄公", text = "山口未开，秦军不能再损。退回营寨，来日再战！" }
    }
}
gstage = {
    title_id = "QinExpelsRong", turn_limit = 20,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "rrrmmmFFFgggFFFmmmm",
            "rrmmmFFFFgggFFFFmmm",
            "rmmmFFFfffggFFFFmmr",
            "mmmFFFffffgggFFbmmr",
            "mmFFFffggfffFFmmmmr",
            "mFFFffggggfffFFmmmr",
            "FFFfffggggffffFFmmr",
            "FFFffggfffggfffFFmr",
            "FFfffggffffggfffFmr",
            "FFffgggfffffggfffFr",
            "FfffggfffffffggfffF",
            "FfgefffffggfffffffF",
            "FgggffffffgggfffffF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {3, 11}, hero = "QinXiangGong" },
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 320 }
}
function on_deploy(game) game:appoint_hero("QinXiangGong", 1) end
function on_begin(game)
    game:generate_unit("QinVanguard41", 1, Enum.force.own, {2, 10})
    game:generate_unit("QinVanguard42", 1, Enum.force.own, {4, 10})
    game:generate_unit("QinArcher41", 1, Enum.force.own, {5, 11})
    game:generate_unit("QuanRongLord41", 1, Enum.force.enemy, {15, 3})
    game:generate_unit("BoDing41", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("ManYeSu41", 1, Enum.force.enemy, {16, 5})
    game:generate_unit("RongWarrior41", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("RongWarrior41", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("RongWarrior41", 1, Enum.force.enemy, {17, 4})
    game:generate_unit("RongArcher41", 1, Enum.force.enemy, {15, 6})
end
function on_update(game) end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end