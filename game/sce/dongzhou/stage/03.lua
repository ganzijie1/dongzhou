gsupply_enabled = true
gally_hold_position = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengHuanGong" }

gsites = {
    {
        id = "you_king_city_w", name = "王城", position = {9, 0},
        restore_hp = 25, restore_mp = 10, rewards = {}
    },
    {
        id = "you_king_city_e", name = "王城", position = {10, 0},
        restore_hp = 25, restore_mp = 10, rewards = {}
    },
    { id = "you_king_camp_w", name = "王城西营", position = {8, 0}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "you_king_camp_e", name = "王城东营", position = {11, 0}, restore_hp = 20, restore_mp = 10, rewards = {} },
    {
        id = "shen_camp", name = "申军营寨", position = {2, 11},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "hao_storehouse", name = "镐京府库", position = {16, 1},
        restore_hp = 10, restore_mp = 10,
        rewards = {
            { item = "medicine", amount = 1 },
            { item = "spirit_powder", amount = 1 }
        }
    },
    { id = "zheng_middle_camp", name = "郑军中营", position = {9, 7}, restore_hp = 20, restore_mp = 10, rewards = {} }
    ,{ id = "zheng_storehouse", name = "郑军府库", position = {10, 7}, restore_hp = 10, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第三回",
    title = "犬戎主大闹镐京 周平王东迁洛邑",
    battle_title = "镐京陷落",
    objective = "护送周幽王坚守十回合；犬戎主接触或击退幽王也会触发结局",
    map_asset = "m000.jpg",
    intro = {
        { speaker = "申侯", text = "幽王废嫡立庶，又发兵伐申。我虽借犬戎之兵，但只为扶立故太子，绝不能任其屠戮中国。" },
        { speaker = "犬戎主", text = "申侯许我镐京府库任取。儿郎们围住王城，从南门杀进去！" },
        { speaker = "周幽王", text = "速举骊山烽火，召诸侯勤王！" },
        { speaker = "虢石父", text = "烽烟已经升起，却仍不见一军来救。" },
        { speaker = "郑桓公", text = "华夏有君臣之义。臣虽兵少，也当守住王驾，绝不容犬戎横行王城！" },
        { speaker = "军令", text = "郑桓公部由我军控制，幽王部为友军，申侯与犬戎为敌军。守满十回合可获两份金疮药。" },
        { speaker = "军令", text = "犬戎主接触周幽王，或周幽王被击退，会立即触发幽王被俘剧情过关，但没有坚守奖励。" },
        { speaker = "军令", text = "犬戎部初始十一人；存活少于五人时，将从南方补充至十一人。" }
    },
    victory = {
        { speaker = "郑桓公", text = "王驾先走！臣守住此处，纵然万箭加身，也不能让犬戎轻易得逞。" },
        { speaker = "犬戎主", text = "周王已经落入我手。镐京府库、宫室金帛，尽归犬戎！" },
        { speaker = "申侯", text = "我本欲纠正王慝、复立宜臼，不料犬戎竟弑君焚城。引戎入华，实为我一生之罪。" },
        { speaker = "旁白", text = "郑桓公力战死于骊山，周幽王与伯服被犬戎所杀。犬戎盘踞镐京，华夏诸侯随后起兵勤王。" }
    },
    defeat = {
        { speaker = "郑桓公", text = "臣未能护住王驾，也未能守住华夏衣冠……" },
        { speaker = "旁白", text = "郑桓公过早败退，王师无人约束，犬戎迅速席卷镐京。" }
    }
}

gstage = {
    title_id = "HaoJingFalls",
    turn_limit = 12,
    map = {
        blocked_edges = {},
        size = {19, 16},
        terrain = {
            "WFFFFiiieCCeFFFFFFW",
            "WgggFhhhihhhFgggbFW",
            "WgggFiiiiiiiFggeeeW",
            "WWWWWWWWWGGWWWWWWWW",
            "WgggWfffffffffWgggW",
            "WgggWfffffffffWgggW",
            "WgggGfffffffffGgggW",
            "WgggWffffebfffWgggW",
            "WgggWfffffffffWgggW",
            "WWWWWWWWWGGWWWWWWWW",
            "WfffffffffffffffffW",
            "WgeeffffffffffffggW",
            "WWWWWWWWWGGWWWWWWWW",
            "FggggggfffffggggggF",
            "FggggggfffffggggggF",
            "FFFFFFFFFFFFFFFFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 7}, hero = "ZhengHuanGong" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = {
        equipments = {},
        money = 300,
        has_conditional_items = true,
        conditional_items = {
            { id = "medicine", amount = 2, condition = "held_ten_turns" }
        }
    }
}

held_ten_turns = false
capture_triggered = false
local RONG_GENERIC_TARGET = 10
local FLANK_TARGET = 3
local reinforcement_generation = 0
local left_reinforce_turn = nil
local right_reinforce_turn = nil
local reinforcement_slots = {
    {1, 14}, {3, 14}, {5, 14}, {7, 14}, {9, 14}, {11, 14}, {13, 14}, {15, 14}, {17, 14},
    {2, 13}, {4, 13}, {6, 13}, {8, 13}, {10, 13}, {12, 13}, {14, 13}, {16, 13},
    {3, 12}, {5, 12}, {7, 12}, {9, 12}, {11, 12}, {13, 12}, {15, 12}
}
local left_reinforcement_slots = {
    {1, 5}, {2, 6}, {2, 8}, {3, 5}, {3, 7}, {1, 8}
}
local right_reinforcement_slots = {
    {17, 5}, {16, 6}, {16, 8}, {15, 5}, {15, 7}, {17, 8}
}

local function rong_alive(game)
    return game:get_num_units_alive("QuanRongWarrior")
        + game:get_num_units_alive("QuanRongWarrior2")
        + game:get_num_units_alive("QuanRongArcher")
end

local function spawn_rong_reinforcements(game)
    local alive = rong_alive(game)
    if alive >= 5 then return end
    local missing = RONG_GENERIC_TARGET - alive
    if missing <= 0 then return end

    reinforcement_generation = reinforcement_generation + 1
    local slot_index = 1
    local function spawn(hero)
        while slot_index <= #reinforcement_slots do
            local position = reinforcement_slots[slot_index]
            slot_index = slot_index + 1
            if game:is_cell_vacant(position) then
                local unit_id = game:generate_unit(hero, 1, Enum.force.enemy, position)
                game:set_unit_direction(unit_id, 3)
                return true
            end
        end
        return false
    end


    local next_warrior = reinforcement_generation % 3
    while missing > 0 do
        local hero = next_warrior == 0 and "QuanRongWarrior"
            or (next_warrior == 1 and "QuanRongWarrior2" or "QuanRongArcher")
        if not spawn(hero) then return end
        next_warrior = (next_warrior + 1) % 3
        missing = missing - 1
    end
end

local function fill_flank(game, hero, slots, direction)
    local missing = FLANK_TARGET - game:get_num_units_alive(hero)
    if missing <= 0 then return true end
    for _, position in ipairs(slots) do
        if missing <= 0 then break end
        if game:is_cell_vacant(position) then
            local unit_id = game:generate_unit(hero, 1, Enum.force.enemy, position)
            game:set_unit_direction(unit_id, direction)
            missing = missing - 1
        end
    end
    return missing <= 0
end

local function update_flank_reinforcements(game)
    local turn = game:get_turn_current()
    local left_alive = game:get_num_units_alive("QuanRongLeftWarrior")
    local right_alive = game:get_num_units_alive("QuanRongRightWarrior")

    if left_alive < FLANK_TARGET and left_reinforce_turn == nil then
        left_reinforce_turn = turn + 1
    end
    if right_alive < FLANK_TARGET and right_reinforce_turn == nil then
        right_reinforce_turn = turn + 1
    end

    if left_reinforce_turn ~= nil and turn >= left_reinforce_turn then
        if fill_flank(game, "QuanRongLeftWarrior", left_reinforcement_slots, 2) then
            left_reinforce_turn = nil
        else
            left_reinforce_turn = turn + 1
        end
    end
    if right_reinforce_turn ~= nil and turn >= right_reinforce_turn then
        if fill_flank(game, "QuanRongRightWarrior", right_reinforcement_slots, 1) then
            right_reinforce_turn = nil
        else
            right_reinforce_turn = turn + 1
        end
    end
end

function on_deploy(game)
    game:appoint_hero("ZhengHuanGong", 1)
end

local function generate_facing(game, hero, position, direction)
    local unit_id = game:generate_unit(hero, 1, Enum.force.enemy, position)
    game:set_unit_direction(unit_id, direction)
    return unit_id
end

function on_begin(game)
    game:generate_unit("RoyalGuard", 1, Enum.force.ally, {4, 6})
    game:generate_unit("RoyalGuard", 1, Enum.force.ally, {15, 6})
    game:generate_unit("RoyalGuard", 1, Enum.force.ally, {9, 12})
    game:generate_unit("RoyalGuard", 1, Enum.force.ally, {10, 12})
    game:generate_unit("RoyalGuard", 1, Enum.force.ally, {10, 7})

    game:generate_unit("ZhouYouWang", 1, Enum.force.ally, {9, 0})
    game:generate_unit("GuoShiFu", 1, Enum.force.ally, {10, 0})

    generate_facing(game, "BoDing41", {1, 7}, 2)
    generate_facing(game, "QuanRongLeftWarrior", {1, 5}, 2)
    generate_facing(game, "QuanRongLeftWarrior", {2, 6}, 2)
    generate_facing(game, "QuanRongLeftWarrior", {2, 8}, 2)

    generate_facing(game, "ManYeSu41", {17, 7}, 1)
    generate_facing(game, "QuanRongRightWarrior", {17, 5}, 1)
    generate_facing(game, "QuanRongRightWarrior", {16, 6}, 1)
    generate_facing(game, "QuanRongRightWarrior", {16, 8}, 1)

    generate_facing(game, "ShenHou", {2, 14}, 3)
    generate_facing(game, "QuanRongLord", {9, 14}, 3)
    generate_facing(game, "QuanRongWarrior", {4, 13}, 3)
    generate_facing(game, "QuanRongWarrior", {6, 13}, 3)
    generate_facing(game, "QuanRongWarrior", {8, 13}, 3)
    generate_facing(game, "QuanRongWarrior", {10, 13}, 3)
    generate_facing(game, "QuanRongWarrior", {12, 13}, 3)
    generate_facing(game, "QuanRongWarrior", {14, 13}, 3)
    generate_facing(game, "QuanRongArcher", {5, 14}, 3)
    generate_facing(game, "QuanRongArcher", {7, 14}, 3)
    generate_facing(game, "QuanRongArcher", {11, 14}, 3)
    generate_facing(game, "QuanRongArcher", {13, 14}, 3)
end

function on_update(game)
    spawn_rong_reinforcements(game)
    update_flank_reinforcements(game)
    if game:get_turn_current() > 10 then
        held_ten_turns = true
    end
    if not game:has_unit("ZhouYouWang")
       or game:are_units_within("QuanRongLord", "ZhouYouWang", 1) then
        capture_triggered = true
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_turn_current() > 10 then
        held_ten_turns = true
        return Enum.status.victory
    end
    if capture_triggered or not game:has_unit("ZhouYouWang")
       or game:are_units_within("QuanRongLord", "ZhouYouWang", 1) then
        capture_triggered = true
        return Enum.status.victory
    end
    if game:get_num_commanders_alive() < #gcommanders then
        return Enum.status.defeat
    end
    return Enum.status.undecided
end
