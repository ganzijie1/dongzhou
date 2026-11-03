ambush_triggered = false
xianzhen_sacrificed = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "XianZhen27", "XianQieJu45", "HuSheGu27", "HuJuJu45" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "XiQue45", defender = "BaiBuHu45", exp = 100, outcome = "kill",
        attacker_speech = "白部胡已入大谷，且看郤缺一箭破敌！",
        defender_speech = "晋军不过佯退，冲开两翼便是箕城！",
        result_speech = "郤缺一箭正中白部胡面门，翟军主帅坠马而死。",
        text = "原著明载郤缺射中白部胡面门，将其杀死。"
    }
}
gsites = {}

gstory = {
    chapter = "第四十五回·下",
    title = "晋襄公墨缞败秦 先元帅免胄殉翟",
    battle_title = "箕城御翟",
    objective = "先且居诱白部胡进入大谷中央，触发郤缺、栾盾两翼伏兵；击退白部胡并把翟军残部压至两人以内，触发先轸免胄殉翟剧情。任一我方具名将领在事件前被击退则失败。",
    map_asset = "m069.png",
    intro = {
        { speaker = "", text = "崤山战后，先轸因晋襄公擅自释放秦国三帅而盛怒失礼，虽获宽赦，心中始终惭愧。不久白部胡率翟兵越过箕城侵入晋境。" },
        { speaker = "晋襄公", text = "北境急报，白部胡已经逼近箕城。仍请先元帅统军御敌，寡人绝不因前事疑你。" },
        { speaker = "先轸", text = "臣受君知遇，更当以死报国。白部胡锐气正盛，不可在箕城下硬拒，应把他引入大谷再合围。" },
        { speaker = "狼瞫", text = "末将愿为先锋，戴罪冲阵。崤山斩褒蛮子之后，军中无人敢说我怯战。" },
        { speaker = "先轸", text = "此战诱敌需要沉稳，不在一人逞勇。先锋仍用先且居，你暂随中军。" },
        { speaker = "", text = "狼瞫的友人劝他趁机刺杀先轸以雪弃用之耻。狼瞫断然拒绝，称以下犯上不能成名，宁愿死在敌阵证明勇气。" },
        { speaker = "先且居", text = "我在谷口接战，只许败、不许胜。白部胡追到中央三格范围，左右伏兵再出现。" },
        { speaker = "栾盾", text = "左翼已经藏入林后，翟骑没有进入大谷之前绝不露旗。" },
        { speaker = "郤缺", text = "右翼弓手沿林缘散开。我会盯住白部胡，他一进入射程，先取主帅。" },
        { speaker = "狐射姑", text = "我与狐鞫居在后路策应。伏兵一起，便切断翟军向北退出山谷的道路。" },
        { speaker = "白部胡", text = "晋军先锋人数不多，正向南退走。全军追入谷中，先擒此将，再取箕城！" },
        { speaker = "军令", text = "先且居先向大谷中央后撤诱敌。白部胡进入（18，13）三格范围后，两翼伏兵才会刷新；两侧树林增加移动消耗，角落岩山不可通行。" }
    },
    events = {
        { id = "dagu_ambush", trigger = "approach", position = {18,13}, radius = 3, speaker = "先且居", text = "白部胡已经越过谷心！两翼举旗，封住北面归路！" },
        { id = "xianzhen_last_charge", trigger = "enemy_count", count = 2, speaker = "先轸", text = "白部胡已死，翟军将溃。臣今日愿以此身洗去失礼之愧。" }
    },
    victory = {
        { speaker = "", text = "白部胡追入大谷，栾盾、郤缺从左右林间杀出。郤缺一箭射中白部胡面门，翟军失去主帅，余众四散。" },
        { speaker = "", text = "战局已定，先轸写好捷报交给先且居，忽然单骑冲入残余翟阵。众将赶来接应时，他又卸下盔甲，坦然承受乱箭。" },
        { speaker = "先轸", text = "臣曾对国君失礼，虽蒙不罪，心不能安。今日以身殉国，愿后世只记晋军不可轻侮。" },
        { speaker = "", text = "翟军弓手万箭齐发，先轸中箭如猬，仍立马不倒。晋军夺回遗体，全军为元帅举哀。" },
        { speaker = "", text = "白暾见先轸如此刚烈，感叹中华自有大贤，下令残部不得毁伤尸身，随后退回北地。" },
        { speaker = "晋襄公", text = "先元帅以死报国，寡人痛失柱石。厚葬先轸，录用其子先且居，使继掌晋军。" },
        { speaker = "军令", text = "箕城御翟完成，获得5600金币。先轸按原著在本关殉国；先且居继承晋军统帅职责。" }
    },
    defeat = {
        { speaker = "", text = "诱敌尚未完成，晋军具名将领先遭重创。大谷两翼无法同时合围，只得退守箕城。" }
    }
}

gstage = {
    title_id = "JiCityDefendsDi45", turn_limit = 20,
    map = { blocked_edges = {}, size = {36, 26}, terrain = {
        "rrrFFmmFmgggfgggfgggfgggfgggmFmFFrrr",
        "rrrFmFFFFgfgggfgggfgggfgggfgFFFFFrrr",
        "rrrmFFFmFmggfgggfgggfgggfgggFmFFFrrr",
        "rrrFFFFFFFfgggfgggfgggfgggfgFFFFmrrr",
        "rrrFFFmFmFggfgggfgggfgggfgggmFmmFrrr",
        "mFFFFmFFFFfgggfgggfgggfgggfgFFFFFFFm",
        "FFFFmFFmFmggfgggfgggfgggfgggFmFFFFmF",
        "FFFmFFFFFFfgggfgggfgggfgggfgFFFFFmFF",
        "FFmFFFFFmFggfgggfgggfgggfgggmFmFmFFF",
        "FmFFFFmFFFfgggfgggfgggfgggfgFFFmFFFF",
        "mFFFFmFmFmggfgggfgggfgggfggmFmmFFFFm",
        "FFFFmFFFFFfgggfgggfgggfgggfFFFFFFFmF",
        "FFFmFFmFmgggfgggfgggfgggfggFmFFFFmFF",
        "FFmFFFFFFgfgggfgggfgggfgggFFFFFFmFFF",
        "FmFFFmFmfgggfgggfgggfgggfgFmFFFmFFFF",
        "mFFFFFFFggfgggfgggfgggfgggFFFFmFFFFm",
        "FFFFmFmFfgggfgggfgggfgggfgmFmmFFFFmF",
        "FFFmFFFFggfgggfgggfgggfgggFFFFFFFmFF",
        "FFmFFmFmfgggfgggfgggfgggfgFmFFFFmFFF",
        "FmFFFFFFggfgggfgggfgggfgggFFFFFmFFFF",
        "mFFFFFmFfgggfgggfgggfgggfgmFmFmFFFFm",
        "FFFFmFFFggfgggfgggfgggfgggFFFmFFFFmF",
        "rrrmFmFmfgggfgggfgggfgggfgFmFFFFFrrr",
        "rrrFFFFFggfgggfgggfgggfgggFFFFFFmrrr",
        "rrrFFFmFmgggfgggfgggfgggfggFmFFmFrrr",
        "rrrFFmFFFgfgggfgggfgggfgggfFFFmFFrrr"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {18,22}, hero = "XianZhen27" },
        { position = {18,17}, hero = "XianQieJu45" },
        { position = {15,21}, hero = "HuSheGu27" },
        { position = {21,21}, hero = "HuJuJu45" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 5600 }
}

local ambush_named = { "LuanDun45", "XiQue45" }

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

local function spring_dagu_ambush(game)
    if ambush_triggered then return end
    ambush_triggered = true
    game:push_cmd_speak(0, "白部胡已经深入大谷，左右林中晋军同时杀出，北面退路也被截断！")
    game:generate_unit("LuanDun45", 1, Enum.force.own, {9,13})
    game:generate_unit("XiQue45", 1, Enum.force.own, {27,13})
    generate_many(game, "JinGuard45", {{10,11},{10,15},{25,11},{25,15}}, Enum.force.own)
    generate_many(game, "JinArcher45", {{9,12},{9,14},{26,12},{26,14}}, Enum.force.own)
end

function on_begin(game)
    game:generate_unit("BaiBuHu45", 1, Enum.force.enemy, {18,4})
    generate_many(game, "DiCavalry45", {{15,5},{17,6},{19,6},{21,5},{14,7},{22,7}}, Enum.force.enemy)
    generate_many(game, "DiArcher45", {{16,3},{20,3},{13,5},{23,5}}, Enum.force.enemy)
    generate_many(game, "JinGuard45", {{16,19},{20,19}}, Enum.force.own)
end

local function di_remnants(game)
    return game:get_num_units_alive("DiCavalry45") + game:get_num_units_alive("DiArcher45")
end

function on_update(game)
    if not ambush_triggered and (game:is_unit_within("BaiBuHu45", {18,13}, 3) or not game:has_unit("BaiBuHu45")) then
        spring_dagu_ambush(game)
    end
    if ambush_triggered and not xianzhen_sacrificed and not game:has_unit("BaiBuHu45") and di_remnants(game) <= 2 then
        xianzhen_sacrificed = true
        game:push_cmd_speak(0, "白部胡已死，翟军残部将溃。先轸写下捷报，忽然单骑冲入敌阵。")
        game:push_cmd_speak(0, "先轸卸去盔甲，任翟军乱箭射来，以死洗去此前对国君失礼之愧。")
        game:push_cmd_speak(0, "先元帅殉国！晋军收回遗体，白暾也叹服其忠烈，下令残部退走。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_triggered and not xianzhen_sacrificed then
        for _, hero in ipairs(ambush_named) do
            if not game:has_unit(hero) then return Enum.status.defeat end
        end
    end
    if xianzhen_sacrificed then return Enum.status.victory end
    return Enum.status.undecided
end
