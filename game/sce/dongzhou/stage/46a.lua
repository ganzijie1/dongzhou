baitun_released = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "XianQieJu45", "HuSheGu27", "XiQue45", "LuanDun45", "HuJuJu45" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第四十六回·上",
    title = "楚商臣宫中弑父 秦穆公崤谷封尸",
    battle_title = "大谷之战",
    objective = "击退翟军普通部队至四人以内，再由狐射姑接近白暾触发旧恩对话并放其退走。白暾不可击杀；先且居、狐射姑、郤缺、栾盾、狐鞫居任一被击退则失败。",
    map_asset = "m070.png",
    intro = {
        { speaker = "", text = "白部胡战死后，败兵把消息报给其弟白暾。白暾早知晋国不可轻犯，却仍要迎回兄长遗骸，遂派使者提出以先轸遗体交换白部胡尸首。" },
        { speaker = "先且居", text = "父帅遗表已经说明死志，但尸身尚在翟营。我愿亲自前往交换，诸将不必劝阻。" },
        { speaker = "郤缺", text = "白暾肯送还遗体，未必肯安然退兵。左右两翼仍按大谷旧阵布置，交换完成后立即归阵。" },
        { speaker = "栾盾", text = "我守左翼，郤缺守右翼。翟骑若趁交接冲击中军，便从两侧包围。" },
        { speaker = "狐鞫居", text = "中军车阵已经连成一线，普通骑兵不能正面穿透。白暾若强攻，只会折损更多部众。" },
        { speaker = "", text = "次日两军列阵。先且居身穿素服独自出迎，白暾拔去先轸遗体上的箭翎，以香水洗净，又脱下锦袍包裹，送还晋军。" },
        { speaker = "白暾", text = "我送来的是一具完整遗体，你们却只还兄长一颗首级。晋人如此欺我，怎能罢休！" },
        { speaker = "先且居", text = "白部胡全尸仍在大谷乱军之中。若要寻回，便自行去认；晋军没有替侵境之敌收尸的义务。" },
        { speaker = "", text = "白暾勃然大怒，挥动开山大斧，命翟骑冲向晋军。晋军以战车屯列如墙，连续挡住数次突击。" },
        { speaker = "狐射姑", text = "白暾既然执意再战，我从中军出阵迎他。两翼保持阵形，先削去随从，莫伤白暾性命。" },
        { speaker = "军令", text = "车阵由晋军战车单位构成，并非城墙地形；敌军可在击退战车后突破。先把翟军普通部队压至四人以内，再让狐射姑与白暾相邻。" }
    },
    events = {
        { id = "chariot_line", trigger = "approach", position = {14,13}, radius = 2, speaker = "先且居", text = "车阵不得散开！甲士守住间隙，弓手从车后压住翟骑。" },
        { id = "baitun_pursuit", trigger = "approach", position = {30,13}, radius = 2, speaker = "狐射姑", text = "白暾已经脱离本阵，我追上去问清他的身份。" }
    },
    victory = {
        { speaker = "", text = "郤缺、栾盾从左右合围，翟军抵挡不住，纷纷向东北退走。狐射姑认定白暾，紧随马后追赶。" },
        { speaker = "白暾", text = "将军面善，莫非贾季？你父子在翟国十二年，我国相待不薄。今日留情，异日自有相报之时。" },
        { speaker = "狐射姑", text = "正是贾季。念及旧日收留之恩，我放你一条生路。立即带兵回翟，不得再侵晋境。" },
        { speaker = "", text = "狐射姑拨马返回，白暾连夜撤军。白部胡无子，白暾为兄发丧，继任翟君。" },
        { speaker = "", text = "晋军迎先轸遗体归国。晋襄公亲自入殓，读完遗表后拜先且居为中军元帅；先轸双目至此才安然闭合。" },
        { speaker = "晋襄公", text = "郤缺射杀白部胡，恢复冀地食邑；胥臣荐贤有功，以先茅之县为赏。诸将功罪分明，晋军方能长久。" },
        { speaker = "军令", text = "大谷之战完成，获得4800金币。下一关为彭衙之战；泜水对峙与楚国宫变将在战前过场完整展开。" }
    },
    defeat = {
        { speaker = "", text = "晋军车阵被提前冲散，具名将领受创，先轸遗体也无法安全送回绛都。" }
    }
}

gstage = {
    title_id = "DaguBattle46", turn_limit = 18,
    map = { blocked_edges = {}, size = {38, 26}, terrain = {
        "rrrrrrmmFmmmFmmmFmmmFmmmFmmmFmmmrrrrrr",
        "rrrrrrmmmFmmmFmmmFmmmFmmmFmmmFmmrrrrrr",
        "mmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmm",
        "mmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmm",
        "FmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFm",
        "FFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFF",
        "mFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmF",
        "FmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFm",
        "fgfgwwfgfgwwfgfgwwfgfgwwfgfgwwfgfgwwfg",
        "gggwwggggwwggggwwggggwwggggwwggggwwggg",
        "gfwwgfgfwwgfgfwwgfgfwwgfgfwwgfgfwwgfgf",
        "gwwggggwwggggwwggggwwggggwwggggwwggggw",
        "wwfgfgwwfgfgwwfgfgwwfgfgwwfgfgwwfgfgww",
        "wggggwwggggwwggggwwggggwwggggwwggggwwg",
        "gfgfwwgfgfwwgfgfwwgfgfwwgfgfwwgfgfwwgf",
        "gggwwggggwwggggwwggggwwggggwwggggwwggg",
        "fgwwfgfgwwfgfgwwfgfgwwfgfgwwfgfgwwfgfg",
        "gwwggggwwggggwwggggwwggggwwggggwwggggw",
        "mFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmF",
        "FmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFm",
        "FFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFFmFF",
        "mFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmF",
        "mmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmm",
        "mmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmmmFmm",
        "rrrrrrmmFmmmFmmmFmmmFmmmFmmmFmmmrrrrrr",
        "rrrrrrmmmFmmmFmmmFmmmFmmmFmmmFmmrrrrrr"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {7,13}, hero = "XianQieJu45" },
        { position = {8,11}, hero = "HuSheGu27" },
        { position = {8,15}, hero = "XiQue45" },
        { position = {6,10}, hero = "LuanDun45" },
        { position = {6,16}, hero = "HuJuJu45" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4800 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_begin(game)
    game:generate_unit("BaiTun46", 1, Enum.force.enemy, {30,13})
    game:set_unit_invulnerable("BaiTun46", true)
    generate_many(game, "JinChariot46", {{13,9},{13,11},{13,13},{13,15},{13,17}}, Enum.force.own)
    generate_many(game, "JinGuard46", {{11,10},{11,12},{11,14},{11,16}}, Enum.force.own)
    generate_many(game, "JinArcher46", {{9,10},{9,12},{9,14},{9,16}}, Enum.force.own)
    generate_many(game, "DiCavalry46", {{24,9},{26,10},{28,11},{25,13},{28,15},{26,16},{24,17}}, Enum.force.enemy)
    generate_many(game, "DiArcher46", {{29,9},{30,11},{30,15},{29,17}}, Enum.force.enemy)
end

local function di_remnants(game)
    return game:get_num_units_alive("DiCavalry46") + game:get_num_units_alive("DiArcher46")
end

function on_update(game)
    if not baitun_released and di_remnants(game) <= 4 and game:are_units_within("HuSheGu27", "BaiTun46", 1) then
        baitun_released = true
        game:push_cmd_speak(0, "白暾认出狐射姑就是昔日居翟的贾季。狐射姑念及旧恩，放他带领残部退回翟国。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if baitun_released then return Enum.status.victory end
    return Enum.status.undecided
end
