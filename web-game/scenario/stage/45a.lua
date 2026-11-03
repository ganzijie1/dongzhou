ambush_triggered = false
ambush_spoken = false
capture_announced = {}

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "JinXiangGong45", "XianZhen27" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "LangTan45", defender = "BaoManZi44", exp = 100, outcome = "kill",
        attacker_speech = "秦将休走！崤山谷口便是你的绝路！",
        defender_speech = "晋人只会藏在山后么？待我夺马再战！",
        result_speech = "褒蛮子挣断束缚夺马，狼瞫挺戈追上，将其斩杀。",
        text = "原著明载褒蛮子被俘后挣断绳索，夺马欲逃，狼瞫追及斩之。"
    },
    {
        attacker = "XianZhen27", defender = "MengMingShi26", exp = 90, outcome = "capture",
        attacker_speech = "孟明视，秦军四面皆绝，下马受缚！",
        defender_speech = "千里袭人，今日果中晋军伏算。",
        result_speech = "孟明视力尽被俘。",
        text = "孟明视被晋军擒获，随后因文嬴说情获释。"
    }
}
gsites = {}

gstory = {
    chapter = "第四十五回·上",
    title = "晋襄公墨缞败秦 先元帅免胄殉翟",
    battle_title = "崤山伏击",
    objective = "秦军已进入崤山峡谷。触发四面伏兵后击退全部秦军；孟明视、西乞术、白乙丙被击退视为被俘，褒蛮子按原著阵亡。晋襄公、先轸及伏兵各部具名将领任一被击退则失败。",
    map_asset = "m068.png",
    intro = {
        { speaker = "", text = "晋文公下葬未久，秦军袭郑不成，转破滑国，载着子女玉帛向西返回。边报传到绛都，先轸请求趁秦军疲惫，在崤山设伏。" },
        { speaker = "晋襄公", text = "父丧未毕便兴兵，礼制可容么？秦国又曾助先君返国，寡人不愿轻忘旧恩。" },
        { speaker = "先轸", text = "秦越晋境千里袭人，回师又灭我同姓滑国。臣若不击，诸侯都会以为晋国新丧而可欺。请君墨染衰麻，暂以军礼统众。" },
        { speaker = "赵衰", text = "先元帅所言是。秦师载重而归，崤山道路险绝，此时不取，日后必成边患。" },
        { speaker = "", text = "晋襄公把白色丧服染黑，亲率中军驻在崤山外二十里。先轸将诸军分作四路，先行潜入山谷两侧。" },
        { speaker = "先轸", text = "先且居、屠击伏左山；胥婴、狐鞫居伏右山。狐射姑、韩子舆断西路，梁弘、莱驹封东口。见谷中红旗一展，同时杀出。" },
        { speaker = "狐射姑", text = "西面归路已经用巨木堵住。秦军若回头，只能在绝命岩下拥作一团。" },
        { speaker = "梁弘", text = "东口由我封锁。等秦军中军完全入谷，再断其后，不许一车一马漏出。" },
        { speaker = "", text = "秦军沿上天梯、堕马崖、绝命岩、落魂涧一路西行。山路越走越窄，车轴相击，人马疲惫。" },
        { speaker = "孟明视", text = "前路落木太多，山上又似有旗影。命褒蛮子先探谷口，西乞、白乙约束后队，不可让辎车堵死道路。" },
        { speaker = "褒蛮子", text = "区区山路，哪能困住秦国锐士？我先越过断木，有伏兵便将他挑下山来！" },
        { speaker = "莱驹", text = "此人气势凶悍，先放他深入。红旗未举，东口不可提前暴露。" },
        { speaker = "军令", text = "岩山不可跨越，只有中央连续峡谷可以通行。秦军已进入伏击区，行动后将触发四面伏兵；秦国三帅击退后按被俘结算。" }
    },
    events = {
        { id = "ambush_signal", trigger = "approach", position = {11, 14}, radius = 2, speaker = "先轸", text = "秦军前后都已进入崤山。举红旗，四路伏兵同时合围！" },
        { id = "fallen_logs", trigger = "approach", position = {7, 14}, radius = 2, speaker = "狐射姑", text = "西路巨木已经点燃硫黄，秦军不可再从原路退出！" }
    },
    victory = {
        { speaker = "", text = "四路晋军从山腰齐出，硫黄烈火沿断木燃起。秦军车马困在狭谷，首尾不能相救，全军覆没，没有一辆战车、一匹战马逃出崤山。" },
        { speaker = "", text = "孟明视、西乞术、白乙丙被押到晋襄公营前，统一按被俘处理。褒蛮子挣断绑缚、夺马欲走，被狼瞫追上斩杀。" },
        { speaker = "文嬴", text = "秦晋本是婚姻之国，先君又受秦君厚恩。三帅辱国已深，放他们回秦受戮，反能消解两国之怨。" },
        { speaker = "晋襄公", text = "母夫人所请，寡人不敢违。解去三人囚车，令其立即西归。" },
        { speaker = "先轸", text = "将士用命才擒得三名敌帅，一妇人几句话便纵虎归山！今日放走，异日必为晋患。" },
        { speaker = "", text = "先轸盛怒之下竟向襄公面前唾地，随即醒悟失礼。襄公反而承认自己未经元帅便放俘有错，不加治罪。" },
        { speaker = "阳处父", text = "三人离营未远，臣愿追到黄河。若不能擒回，也绝不让他们从容西渡。" },
        { speaker = "", text = "阳处父追到河岸，以赠送良马为名诱孟明视上岸。孟明视识破计谋，拜谢不受，登上公孙枝预备的渡船脱身。" },
        { speaker = "秦穆公", text = "孤违蹇叔、百里奚之言，才有崤山之败，罪不在三帅。你们休养整军，日后仍要雪耻。" },
        { speaker = "军令", text = "崤山伏击完成，获得6200金币。下一战转入箕城大谷，先且居诱白部胡深入后再发动伏兵。" }
    },
    defeat = {
        { speaker = "", text = "晋军伏击号令失序，秦军冲开一处谷口。崤山合围未成，只能保护新君退回中军。" }
    }
}

gstage = {
    title_id = "XiaoshanAmbush45", turn_limit = 24,
    map = { blocked_edges = {}, size = {44, 28}, terrain = {
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrmmmrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrmmmmrrrrrrrrrmmmmmmmmrr",
        "rrrrrrmmmrrrrrrrrrrmmmmmmmmmrrrrmmmmmFmmmmmm",
        "rrmmmmmmmmmmmrrrmmmmmmFmmmmmmmmmmmmFmFmmFmmm",
        "mmmmmmmmFmmmmmmmmmmmFmmFmFmmmmmmmFmFFmmmFmmF",
        "mmmFmmFmFmmFmmmmFmFmmmFmmmFmFmmFmFFmmmFmmmmF",
        "mFmmFmmmFFmFmmFmFmmmFmmmFmmmmFmFFmmmgwwmFmmm",
        "mmFmmmFmmmFmmmFmmmFmmwwgfmFmmmFmmmggwwgfgwFm",
        "FmmmFmwfgmmmFmmmFmmfwwfggwwgFmmmggfwwfggwwgf",
        "mmfgwwggfwwfgmFmgfgwwggfwwfggwwgfgwwggfwwfgg",
        "fggwwgfgwwggfwwfggwwgfgwwggfwwfggwwgfgwwggfw",
        "gfwwfggwwgfgwwggfwwfggwwgfgwwggfwwfggwwgfgww",
        "gwwggfwwfggwwgfgwwggfwwfggwwgfgwwggfwwfggwwg",
        "wwgfgwwggfwwfggwwgfgwwggfwwfggwwgfgwmmFfwwfg",
        "wfggwwgfgwwggfwwfggwwmmmFwggfwwfggmmFmmmFmgf",
        "ggfwwfFmmwgfgwwggfwmmmFmmmFmwwggmmFmFmFmmmFm",
        "fgmmFmmmFmmmFwgfFmmmFFmmFmmmFmmmFmFmFmmFmFmm",
        "mmFmmmmFmmFmmmFmmmFFmmFmFmmFmmFmFmFmmmmFmmFm",
        "FmFmmFmFmmFmFmmmmFmmFmmmmFmFmmFmFmmmmmmmmmFm",
        "FmmFmFmmmmFmmFmFmmFmmmmmmmmmFmFmmmmmrrrmmmmm",
        "mFmmmmmmmmmmmFmmmmmmmrrrrmmmmmmmmmrrrrrrrrmm",
        "mmmmmmrrrmmmmmmmmmmrrrrrrrrrmmmmrrrrrrrrrrrr",
        "mmrrrrrrrrrrrmmmrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {23, 18}, hero = "JinXiangGong45" },
        { position = {21, 18}, hero = "XianZhen27" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6200 }
}

local ambush_named = { "XianQieJu45", "TuJi45", "XuYing45", "HuJuJu45", "HuSheGu27", "HanZiYu45", "LiangHong45", "LaiJu45", "LangTan45" }
local qin_captives = {
    { "MengMingShi26", "孟明视" },
    { "XiQiShu26", "西乞术" },
    { "BaiYiBing26", "白乙丙" }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

local function spring_ambush(game)
    if ambush_triggered then return end
    ambush_triggered = true
    game:push_cmd_speak(0, "红旗已经举起！左、右两山与东西谷口同时出现晋军，秦军被截在崤山中央。")
    game:generate_unit("XianQieJu45", 1, Enum.force.own, {20, 7})
    game:generate_unit("TuJi45", 1, Enum.force.own, {22, 8})
    game:generate_unit("XuYing45", 1, Enum.force.own, {19, 18})
    game:generate_unit("HuJuJu45", 1, Enum.force.own, {24, 17})
    game:generate_unit("HuSheGu27", 1, Enum.force.own, {7, 12})
    game:generate_unit("HanZiYu45", 1, Enum.force.own, {8, 15})
    game:generate_unit("LiangHong45", 1, Enum.force.own, {37, 10})
    game:generate_unit("LaiJu45", 1, Enum.force.own, {36, 13})
    game:generate_unit("LangTan45", 1, Enum.force.own, {12, 11})
    generate_many(game, "JinGuard45", {{18,8},{24,9},{18,17},{25,16},{9,12},{9,16},{35,11},{35,14}}, Enum.force.own)
    generate_many(game, "JinArcher45", {{19,9},{23,9},{20,17},{24,16},{8,11},{10,15},{34,11},{34,14}}, Enum.force.own)
end

function on_begin(game)
    game:generate_unit("BaoManZi44", 1, Enum.force.enemy, {11,14})
    game:generate_unit("MengMingShi26", 1, Enum.force.enemy, {18,14})
    game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {22,12})
    game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {26,13})
    generate_many(game, "QinGuard45", {{13,13},{15,14},{17,13},{20,13},{23,13},{25,12},{28,13},{30,13}}, Enum.force.enemy)
    generate_many(game, "QinCavalry45", {{12,15},{16,15},{21,14},{27,14},{31,12}}, Enum.force.enemy)
    generate_many(game, "QinArcher45", {{14,12},{19,12},{24,14},{29,12},{32,12}}, Enum.force.enemy)
end

function on_update(game)
    if not ambush_triggered and (game:is_unit_within("BaoManZi44", {11,14}, 2) or not game:has_unit("BaoManZi44")) then
        spring_ambush(game)
    end
    for _, captive in ipairs(qin_captives) do
        local hero, label = captive[1], captive[2]
        if not capture_announced[hero] and not game:has_unit(hero) then
            capture_announced[hero] = true
            game:push_cmd_speak(0, label .. "力尽落马，已被晋军生擒，押往襄公中军。")
        end
    end
end

function on_victory(game) end
function on_defeat(game) end

local function qin_alive(game)
    return game:get_num_units_alive("BaoManZi44") + game:get_num_units_alive("MengMingShi26")
        + game:get_num_units_alive("XiQiShu26") + game:get_num_units_alive("BaiYiBing26")
        + game:get_num_units_alive("QinGuard45") + game:get_num_units_alive("QinCavalry45")
        + game:get_num_units_alive("QinArcher45")
end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_triggered then
        for _, hero in ipairs(ambush_named) do
            if not game:has_unit(hero) then return Enum.status.defeat end
        end
        if qin_alive(game) == 0 then return Enum.status.victory end
    end
    return Enum.status.undecided
end
