gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "CaiJi101" }
ambush_revealed = false
gduel_enabled = true
gduels = {
    {
        attacker = "CaiJi101", defender = "ChenGongZiTuo101", exp = 55, outcome = "kill",
        attacker_speech = "公子佗，你弑兄夺位，今日还想从围场脱身？",
        defender_speech = "区区猎人也敢拦我车驾，陈军给我冲开道路！",
        result_speech = "伏兵四起，公子佗已被蔡季截住！",
        text = "蔡季纵兵合围，将公子佗斩于猎场。"
    }
}
gsites = {
    { id = "hunter_camp", name = "猎人伏营", position = {3, 9}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "chen_supply", name = "陈国行营", position = {15, 4}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}
gstory = {
    chapter = "第十回·上",
    title = "楚熊通僭号称王 蔡侯乘间袭陈",
    battle_title = "猎场伏蔡",
    objective = "围住公子佗车驾，蔡季与其相邻可触发史实斩杀",
    map_asset = "m011-camp.png",
    intro = {
        { speaker = "旁白", text = "陈桓公死后，弟公子佗杀太子免而自立。蔡侯欲替陈国除乱，命蔡季将十队兵士扮作猎人，埋伏在围场道路两侧。" },
        { speaker = "蔡季", text = "各队只驱逐禽兽，不要先露兵器。等公子佗车驾进入林间，再一齐封住退路。" },
        { speaker = "公子佗", text = "今日围猎，谁先射得猛兽，寡人重赏！" },
        { speaker = "军令", text = "蔡季必须存活。利用树林掩护接近公子佗；蔡季与公子佗相邻时可触发史实斩杀。" }
    },
    victory = {
        { speaker = "旁白", text = "公子佗被擒后当场斩首。蔡人迎立陈桓公之子公子跃，是为陈厉公，陈国乱局暂息。" },
        { speaker = "下回预告", text = "第十回·下：熊通伐随，青林山两军决战。" }
    },
    defeat = {
        { speaker = "蔡季", text = "车驾已经冲出围场，伏兵不可再追，立即撤回蔡境！" }
    }
}
gstage = {
    title_id = "CaiHuntingAmbush", turn_limit = 16,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FFFFFgggFFFFgggFFFF",
            "FFFFgggggFFggggFFFF",
            "FFFggffffggffffgFFF",
            "FFggfffffffffffeFFF",
            "FggffffgggfffffffFF",
            "FggfffgggggfffffffF",
            "FffffggfffggfffffgF",
            "FfffggfffffggffffgF",
            "FffegffffffffffffgF",
            "FffgggfffffgggffffF",
            "FggggFFFFFgggggFFFF",
            "FFFFF~~FFFFFgggFFFF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {3, 9}, hero = "CaiJi101" },
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 400 }
}
function on_deploy(game) game:appoint_hero("CaiJi101", 1) end
function on_begin(game)
    
    game:generate_unit("ChenGongZiTuo101", 1, Enum.force.enemy, {15, 4})
    game:generate_unit("ChenEscort101", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("ChenEscort101", 1, Enum.force.enemy, {16, 5})
    game:generate_unit("ChenEscort101", 1, Enum.force.enemy, {13, 6})
    game:generate_unit("ChenArcher101", 1, Enum.force.enemy, {16, 7})
end
function on_update(game)
    if not ambush_revealed and game:has_unit("CaiHunter101") then
        ambush_revealed = true
    end
    if ambush_revealed then return end
    if not game:is_force_within(Enum.force.enemy, {6, 9}, 6) then return end

    ambush_revealed = true
    local hunter = game:generate_unit("CaiHunter101", 1, Enum.force.own, {2, 8})
    game:generate_unit("CaiHunter102", 1, Enum.force.own, {4, 8})
    game:generate_unit("CaiHunterArcher101", 1, Enum.force.own, {6, 10})
    game:generate_unit("CaiHunter103", 1, Enum.force.own, {7, 11})
    game:push_cmd_speak(hunter, "车驾已入围场，猎人伏兵封住退路！")
end

function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end