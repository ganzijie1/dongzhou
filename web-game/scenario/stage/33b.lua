ambush_spoken = false
escape_spoken = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "GongZiMuYi33" }
gduel_enabled = false
gduels = {}
gsites = {}

gstory = {
    chapter = "第三十三回·下",
    title = "宋公伐齐纳子昭 楚人伏兵劫盟主",
    battle_title = "盂地脱险",
    objective = "护送公子目夷本人到达南侧出口（9，13）；公子目夷被击退则失败；宋襄公留在盟坛按原著被楚军俘获",
    map_asset = "m055.png",
    intro = {
        { speaker = "", text = "鹿上会面之后，宋襄公自以为楚王已经同意帮助召集诸侯，回国时满面喜色。" },
        { speaker = "宋襄公", text = "楚王已经在征会文书上署名，陈、蔡、郑等诸侯都会赴盂地。此次盟会足以确立宋国霸业。" },
        { speaker = "公子目夷", text = "楚国强而难测。主公只得到楚王一句口头承诺，并未得到他的真心，盟会中必须防备欺诈。" },
        { speaker = "", text = "楚成王命成得臣、斗勃各选五百勇士，把甲胄兵器藏在礼服之内，预先操演劫盟之法。" },
        { speaker = "成得臣", text = "宋君好名而无实，又坚持衣裳之会不带兵车。盟坛之上只要红旗一举，便可将他生擒。" },
        { speaker = "子文", text = "既然答应会盟又暗中劫人，诸侯会说楚国无信。" },
        { speaker = "楚成王", text = "劫而后释，既可以示威，也可以示德。诸侯见宋国无能，自然会转而服从楚国。" },
        { speaker = "", text = "临行前，公子目夷再次请求带兵车赴会，或将百乘伏在三里之外接应，宋襄公都以守信为由拒绝。" },
        { speaker = "宋襄公", text = "既然约定衣裳之会，宋国若先带兵车，日后还有什么资格要求诸侯守信？你也随我同往。" },
        { speaker = "公子目夷", text = "臣随行可以，但请主公记住：若楚军忽然露甲，应先保全宋国，不可为了虚名留在坛上争辩。" },
        { speaker = "", text = "楚、陈、蔡、许、曹、郑六国之君按期到场，只有齐孝公与鲁僖公没有赴会。楚军侍从外表都穿着礼服。" },
        { speaker = "宋襄公", text = "寡人想恢复齐桓公的霸业，尊王安民、息兵罢战。诸君今日应推举一位盟主。" },
        { speaker = "楚成王", text = "有功论功，无功论爵。寡人虽是子爵，却已称王多年，宋公怎能列在王前？" },
        { speaker = "宋襄公", text = "楚国王号未经天子承认，不过是假王；宋为上公，天子尚以宾客相待，盟主自然应由寡人担任！" },
        { speaker = "成得臣", text = "诸侯是奉楚命而来，还是奉宋命而来？楚军听令，脱去礼服，举旗封锁盟坛！" },
        { speaker = "", text = "千名楚勇士露出重甲，从四周亭帐蜂拥上坛。成得臣、斗勃抓住宋襄公双袖，开始抢夺盟器玉帛。" },
        { speaker = "宋襄公", text = "寡人后悔不听子鱼之言！你速趁乱突围回宋，主持国防，不必顾念寡人！" },
        { speaker = "公子目夷", text = "主公既有此命，臣只能先保宋国。南侧道路尚未封死，随从护住两翼，立即突围！" },
        { speaker = "军令", text = "本关只要求公子目夷本人到达（9，13）。盟坛周围没有城墙和围栏；岩山不可通行，树林会增加移动消耗。宋襄公留在盟坛，其被击退按原著视为被俘。" }
    },
    events = {
        { id = "chu_ambush", trigger = "approach", position = {9, 6}, radius = 3,
          speaker = "成得臣", text = "红旗已举！封住东西两翼，生擒宋公，不要让公子目夷带人突围！" },
        { id = "south_escape", trigger = "approach", position = {9, 11}, radius = 2,
          speaker = "公子目夷", text = "南路就在前面！不要回坛争夺盟器，回到宋国整军才有机会救回主公！" }
    },
    victory = {
        { speaker = "公子目夷", text = "盂地已经被楚军控制。立即封闭宋国要道，召集兵车，等待主公被押往楚境的消息。" },
        { speaker = "宋襄公", text = "悔不听子鱼之言，以至今日被俘。你既已脱险，宋国尚不至于因寡人一人而亡。" },
        { speaker = "成得臣", text = "宋公已经在手，盟坛玉帛也尽归楚军。诸侯今日都看清谁才有主盟之力。" },
        { speaker = "楚成王", text = "押住宋公，收拢坛下伏兵。公子目夷虽逃，只要宋君仍在楚军手中，宋国便不敢轻动。" },
        { speaker = "", text = "楚军劫走宋襄公，并掠取会盟器物。陈、蔡、许、曹、郑诸侯惊惧离坛，盂地盟会彻底瓦解。" },
        { speaker = "", text = "公子目夷依宋襄公临别之命乘乱返回宋国。如何设法救回宋公，将在下一回继续展开。" },
        { speaker = "下回预告", text = "第三十四回：楚国将押宋襄公伐宋，公子目夷守城拒楚；鲁僖公出面求情后，宋楚又将在泓水交兵。" }
    },
    defeat = {
        { speaker = "公子目夷", text = "南路也被楚军截断。主公与宋国辅臣同时被俘，国内再无人能够主持防务。" },
        { speaker = "", text = "公子目夷被击退，本关失败。" }
    }
}

gstage = {
    title_id = "EscapeMeng33", turn_limit = 10,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrFFFgggggggggFFFrr",
            "rFFFgggggggggggFFFr",
            "FFggggggwwwggggggFF",
            "FggggggfffffggggggF",
            "ggggggfffffffgggggg",
            "ggggggffwwwffgggggg",
            "gggggfffwwwfffggggg",
            "gggggfffwwwfffggggg",
            "ggggggffwwwffgggggg",
            "FggggggfffffggggggF",
            "FFggggggwwgggggggFF",
            "rFggggggffgggggggFr",
            "rFFgggggffggggggFFr",
            "rrFFFgggffgggFFFFrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 7}, hero = "GongZiMuYi33" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2800 }
}

function on_deploy(game)
    game:appoint_hero("GongZiMuYi33", 1)
end

function on_begin(game)
    game:generate_unit("SongGuard33", 1, Enum.force.own, {8, 8})
    game:generate_unit("SongArcher33", 1, Enum.force.own, {10, 8})
    game:generate_unit("SongXiangGong33", 1, Enum.force.ally, {9, 6})
    game:generate_unit("ChuChengWang33", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("ChengDeChen33", 1, Enum.force.enemy, {6, 6})
    game:generate_unit("DouBo33", 1, Enum.force.enemy, {12, 6})
    game:generate_unit("ChuAmbusher33", 1, Enum.force.enemy, {5, 5})
    game:generate_unit("ChuAmbusher33", 1, Enum.force.enemy, {13, 5})
    game:generate_unit("ChuAmbusher33", 1, Enum.force.enemy, {5, 8})
    game:generate_unit("ChuAmbusher33", 1, Enum.force.enemy, {13, 8})
    game:generate_unit("ChuArcher33", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("ChuArcher33", 1, Enum.force.enemy, {11, 4})
end

function on_update(game)
    if not ambush_spoken and game:is_unit_within("GongZiMuYi33", {9, 6}, 3) then
        ambush_spoken = true
        game:push_cmd_speak(0, "楚军已经脱衣露甲！公子目夷按宋公嘱托向南突围，随从护住两翼！")
    end
    if not escape_spoken and game:is_unit_within("GongZiMuYi33", {9, 11}, 2) then
        escape_spoken = true
        game:push_cmd_speak(0, "南侧大道尚未封锁！只有公子目夷本人到达出口才算脱险！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:is_unit_within("GongZiMuYi33", {9, 13}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
