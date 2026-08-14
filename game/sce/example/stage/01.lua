gstage = {
    title_id = "Stage1",
    turn_limit = 20,
    map = {
        blocked_edges = {},
        size = {19, 16},
        terrain = {
            "WffffWWffffffWWffff",
            "WffWffffffffffffWff",
            "WfffffffWffWfffffff",
            "WWWWWWWWWffWWWWWWWW",
            "WFFFWffWffffWffWggg",
            "WFFFWffffffffffWggg",
            "WFFFffWWWffWWWffgfg",
            "WFFFWffffffffffWggg",
            "WFFFWffWffffWffWggf",
            "WWWWWWWWWffWWWWWWWW",
            "Wffffffffffffffffff",
            "WffffWffffffffWffff",
            "WWWWWWWWWffWWWWWWWW",
            "fffffffffffffffffff",
            "fffffffffffffffffff",
            "fffffffffffffffffff"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {17, 5}, hero = "CaoCao" },
            { position = {17, 6}, hero = "ZhangLiao" },
            { position = {16, 6}, hero = "XunYu" },
            { position = {17, 7}, hero = "DianWei" }
        },
        num_required_selectables = 0,
        selectables = {
            { position = {16, 7} },
--            { position = {5, 3} }
        }
    },
    rewards = { -- NYI
        equipments = {
            { id = "short_sword", amount = 1 }
        },
        money = 1000
    }
}


function on_deploy(game)
    game:appoint_hero("CaoCao", 80)
    game:appoint_hero("ZhangLiao", 4)
    game:appoint_hero("DianWei", 25)
    game:appoint_hero("ManChong", 20)
    game:appoint_hero("XiahouDun", 23)
    game:appoint_hero("XunYu", 33)
    game:obtain_equipment("short_sword", 10)
    game:obtain_equipment("heaven_sword", 1)
end


function on_begin(game)
    -- Enemies
    game:generate_unit("Bandit", 18, Enum.force.enemy, {8, 1})
    game:generate_unit("Bandit", 18, Enum.force.enemy, {9, 1})
    game:generate_unit("Bandit", 20, Enum.force.enemy, {10, 1})
    game:generate_unit("Bandit", 20, Enum.force.enemy, {11, 1})
    game:generate_unit("Bandit", 22, Enum.force.enemy, {8, 7})
    game:generate_unit("Bandit", 22, Enum.force.enemy, {11, 7})
end


function on_update(game) end

function on_victory(game)
    game:push_cmd_speak(0, "So long, losers!")
--    game:push_cmd_move(0, {0, 9})
--    game:push_cmd_move(1, {0, 10})
end


function on_defeat(game)
    print("<<<< ON_DEFEAT >>>>")
end


function end_condition(game)
    if game:get_num_owns_alive() == 0 then
        return Enum.status.defeat
    end
    if game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
