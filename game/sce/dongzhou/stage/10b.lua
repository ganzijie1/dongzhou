gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "XiongTong102", "DouBoBi102", "QuXia102", "DouDan102" }
gduel_enabled = true
gduels = {
    {
        attacker = "DouDan102", defender = "ShaoShi102", exp = 60, outcome = "kill",
        attacker_speech = "少师轻敌误国，还不快快下车受缚！",
        defender_speech = "楚兵深入随境，正好叫你有来无回！",
        result_speech = "两车交错，斗丹已抢入少师阵前！",
        text = "斗丹奋力破阵，将少师斩落车下，随军阵势随即崩溃。"
    }
}
gsites = {
    { id = "chu_camp", name = "楚军营寨", position = {3, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "sui_store", name = "随军辎重", position = {15, 3}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}
gstory = {
    chapter = "第十回·下",
    title = "楚熊通僭号称王 蔡侯乘间袭陈",
    battle_title = "青林破随",
    objective = "击溃随军，斗丹与少师相邻可触发史实斩杀",
    map_asset = "m012.png",
    intro = {
        { speaker = "旁白", text = "楚君熊通欲会诸侯于沈鹿，汉东诸国皆来，唯独随国缺席。熊通以此为由，亲率大军伐随。" },
        { speaker = "季梁", text = "楚人尚武而骄。应当修政爱民、避其锋芒，不可轻率出战。" },
        { speaker = "少师", text = "楚军远来疲惫，若只闭门议和，岂不叫诸侯耻笑？臣愿领兵迎敌！" },
        { speaker = "熊通", text = "随侯不用贤臣而信少师，正是破敌之机。斗伯比定策，屈瑕整军，斗丹居前破阵！" },
        { speaker = "斗丹", text = "少师若敢出战，我便在青林山下取他首级！" },
        { speaker = "军令", text = "四名楚国有姓名将领必须存活。山地增加移动消耗；斗丹与少师相邻时触发史实斩杀。" }
    },
    victory = {
        { speaker = "熊通", text = "少师已死，随军败退。传令止兵，准随侯遣使议和。" },
        { speaker = "季梁", text = "随国愿奉盟约。楚君若欲尊号，可由我国上请周天子。" },
        { speaker = "旁白", text = "周桓王拒绝给熊通王号。熊通便自称楚武王，从此楚国公开与周王室分庭抗礼。" },
        { speaker = "旁白", text = "同年，祝聃因背疽去世；郑庄公也病重而亡。祭足拥立世子忽，郑国继承之争由此展开。" },
        { speaker = "下回预告", text = "第十一回：宋庄公贪赂构兵，郑祭足杀婿逐主。" }
    },
    defeat = {
        { speaker = "熊通", text = "青林道路不利，先收兵回楚境。待随国政乱，再来问罪！" }
    }
}
gstage = {
    title_id = "BattleOfQinglin", turn_limit = 22,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "rrmmmFFFFFFFFFmmmrr",
            "rmmmFFFgggggFFFmmmr",
            "mmmFFFggfffggFFFmmm",
            "mmFFFggfffffgbFFFmm",
            "mFFFggffmmmfffggFFF",
            "FFFggfffmmmffffggFF",
            "FFggfffff~fffffggFF",
            "FFggffff~~~ffffggFF",
            "Fggfffff~ffffffgggF",
            "FgggfffffffggffffgF",
            "FfffggfffffgggffffF",
            "FfgeffffggfffffffFF",
            "FgggFFFFgggFFFFgggF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {3, 11}, hero = "XiongTong102" },
            { position = {5, 10}, hero = "DouBoBi102" },
            { position = {7, 11}, hero = "QuXia102" },
            { position = {6, 9}, hero = "DouDan102" },
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 520 }
}
function on_deploy(game)
    game:appoint_hero("XiongTong102", 1)
    game:appoint_hero("DouBoBi102", 1)
    game:appoint_hero("QuXia102", 1)
    game:appoint_hero("DouDan102", 1)
end
function on_begin(game)
    game:generate_unit("ChuGuard102", 1, Enum.force.own, {2, 10})
    game:generate_unit("ChuArcher102", 1, Enum.force.own, {4, 12})
    game:generate_unit("SuiHou102", 1, Enum.force.enemy, {15, 3})
    game:generate_unit("JiLiang102", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("ShaoShi102", 1, Enum.force.enemy, {12, 5})
    game:generate_unit("SuiGuard102", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("SuiGuard102", 1, Enum.force.enemy, {16, 5})
    game:generate_unit("SuiGuard102", 1, Enum.force.enemy, {14, 7})
    game:generate_unit("SuiArcher102", 1, Enum.force.enemy, {16, 7})
end
function on_update(game) end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end