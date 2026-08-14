rear_arrived = false
rear_leader_id = -1
danbo_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "DouZhang23" }
gduel_enabled = true
gduels = {
    {
        attacker = "DouZhang23", defender = "DanBo23", exp = 65, outcome = "retreat",
        attacker_speech = "聃伯，纯门已被前后截断，下马受缚还能保全郑军余众！",
        defender_speech = "楚军先退后返，又从背后包抄，果然早有诡计！",
        result_speech = "斗章以铁简击落聃伯，楚军将其缚上囚车。",
        text = "斗章回军突击，斗廉断其归路；聃伯力不能支，被斗章以铁简击倒俘获。"
    }
}

gsites = {
    { id = "chunmen_chu_camp", name = "楚军行营", position = {4, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "chunmen_zheng_camp", name = "郑军边营", position = {7, 2}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十三回·下",
    title = "卫懿公好鹤亡国 齐桓公兴兵伐楚",
    battle_title = "纯门反袭",
    objective = "斗章回师牵制郑军；第三回合或接近纯门时，斗廉从郑军背后出现，击退聃伯",
    map_asset = "m039.png",
    intro = {
        { speaker = "", text = "齐桓公救邢封卫，诸侯颂声遍及荆襄。楚成王不愿中原只知齐国，决意向北扩张。" },
        { speaker = "楚成王", text = "齐侯经营霸业近三十年，借尊王之名号令诸侯。楚国若再不北进，天下只知有齐！" },
        { speaker = "令尹子文", text = "郑居南北之间，是中原屏障。若不能使郑国屈服，楚军便无法与齐侯争衡。" },
        { speaker = "斗章", text = "臣愿率车二百乘伐郑。若郑国闻风请成，楚国威名自然越过汉水。" },
        { speaker = "", text = "郑国自纯门受兵后日夜戒备。郑文公命大夫聃伯率军守住边境，又向齐国告急。" },
        { speaker = "聃伯", text = "纯门山路狭窄，楚军若从正面来攻，必先在谷口暴露。各部不得离开边营追敌。" },
        { speaker = "", text = "斗章探知郑军已有准备，又听说齐军将至，担心失利，未交战便退回楚境。" },
        { speaker = "楚成王", text = "斗章临敌退兵，辱没楚国威名！斗廉带寡人佩剑前往军中，斩下他的首级！" },
        { speaker = "斗廉", text = "大王命我斩你，但兄弟并非没有生路。郑人见你退兵，戒备必松；立刻返身急袭便可赎罪。" },
        { speaker = "斗章", text = "弟领前队衔枚卧鼓，从谷道直扑郑营；兄长率后队绕山而行，待交战后截断聃伯退路。" },
        { speaker = "", text = "聃伯正在纯门点阅兵马，忽报一支不明军队从南面疾驰而来，只得仓促列阵。" },
        { speaker = "聃伯", text = "敌军去而复返，必是楚将斗章。前军守住谷道，弓手居高压阵，切不可被他冲散！" },
        { speaker = "斗章", text = "楚军先退是为诱敌松懈。各部沿中央谷道推进，将郑军注意力全部引向正面！" },
        { speaker = "军令", text = "斗章被击退则失败。斗廉在第三回合或斗章接近纯门后从右上方出现；斗章与聃伯相邻可触发俘将单挑。" }
    },
    events = {
        { id = "doulian_rear", trigger = "turn", turn = 3,
          speaker = "斗廉", text = "后队已经绕到郑军背后！封住北面山道，与斗章前后夹击！" },
        { id = "danbo_captured", trigger = "defeated", unit = "DanBo23",
          speaker = "斗章", text = "聃伯已经被俘，楚军不要贪功深入，立即整队班师！" }
    },
    victory = {
        { speaker = "斗廉", text = "郑军只顾抵挡前队，背后山道已经空了。楚军后队压下去，封住他们的归路！" },
        { speaker = "聃伯", text = "前有斗章，后有斗廉，纯门道路已断。郑军各自突围，不要全陷在谷中！" },
        { speaker = "", text = "聃伯力不能支，被斗章以铁简击倒，双手拿住。郑军折损大半，楚军却没有继续深入。" },
        { speaker = "斗廉", text = "此战只为替你免去死罪。郑国仍有准备，齐军也可能来援，不可因一次得手便侥幸长驱。" },
        { speaker = "", text = "斗章押聃伯回楚，楚成王准其赎罪，又添兵车二百乘，命斗廉、斗章再次伐郑。" },
        { speaker = "郑文公", text = "聃伯被俘，楚军又增兵再来。郑国愿向楚请成，以免百姓再受兵祸。" },
        { speaker = "孔叔", text = "齐国正为救郑谋划伐楚。受人之德却临阵弃齐，不祥；应当坚壁待援。" },
        { speaker = "管仲", text = "主公救燕、存鲁、城邢、封卫，恩德已加于诸侯。今日救郑，不如合诸侯直伐楚国。" },
        { speaker = "齐桓公", text = "楚国必有准备，如何出其不意？" },
        { speaker = "管仲", text = "蔡侯曾把蔡姬另嫁楚王，主公早欲问罪。可名为讨蔡，实则越蔡伐楚。" },
        { speaker = "", text = "齐桓公与江、黄二君秘密订盟，又请徐国袭取舒国，剪除楚国羽翼；季友也代表鲁国前来请从征伐。" },
        { speaker = "", text = "齐国遍约宋、鲁、陈、卫、郑、曹、许，约定次年正月会师上蔡，八国大军由此成形。" },
        { speaker = "竖貂", text = "臣愿先率一军潜行掠蔡，替诸侯扫清集结之地。" },
        { speaker = "", text = "竖貂攻蔡至夜，暗受蔡穆公金帛，又泄露先蔡后楚的军机。蔡侯惊惧，当夜弃城奔楚。" },
        { speaker = "", text = "齐桓公抵达上蔡，七路诸侯陆续会师。许穆公抱病先到，当夜病逝，齐侯为其停军发丧。" },
        { speaker = "", text = "八国之师南抵楚界，楚大夫屈完衣冠整肃，停车道左，奉楚成王之命质问齐军来意。" },
        { speaker = "屈完", text = "齐居北海，楚近南海，风马牛不相及。齐侯为何率八国车徒深入楚境？" },
        { speaker = "管仲", text = "齐国奉周室之命征讨不共王职者。楚国不贡包茅，周祭无以缩酒；昭王南征不返，也要问罪于楚！" },
        { speaker = "屈完", text = "包茅不入，楚国认罪补贡；昭王不返是胶舟之故，请问诸水滨。楚国不会承担无端罪名。" },
        { speaker = "", text = "管仲认为楚人未服，传令八军进至陉山，却不渡汉水。楚令尹斗子文已在汉南整军，只待联军渡河。" },
        { speaker = "下回预告", text = "第二十四回：屈完再入齐营，齐楚于召陵订盟；齐桓公随后大会诸侯于葵邱。" }
    },
    defeat = {
        { speaker = "斗章", text = "前队未能牵住郑军，兄长的后队也无法完成包抄。只能再次退回楚境请罪！" },
        { speaker = "", text = "斗章被击退，或斗廉到场后被击退，本关失败。" }
    }
}

gstage = {
    title_id = "ChunmenCounterRaid23", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrgggF",
            "rrrrrrggggrrrrggggF",
            "rrrFgggeggggrrgggFr",
            "rrFgggggggggrrgggFr",
            "rFggggrrrgggggggFrr",
            "FggggrrrrggggggFrrr",
            "gggggrrrrrggggFrrrr",
            "gggggggrrgggggFrrrr",
            "FggggrrrggggggFrrrr",
            "rFgggrrrrgggggggFrr",
            "rrgggggrrrgggggggFr",
            "rrrggggggggggggFrrr",
            "rrrgeggggggggggFrrrr",
            "rrrrFFFFFFFFFFFrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 12}, hero = "DouZhang23" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1900 }
}

function on_deploy(game)
    game:appoint_hero("DouZhang23", 1)
end

function on_begin(game)
    game:generate_unit("ChuGuard23", 1, Enum.force.own, {5, 11})
    game:generate_unit("ChuGuard23", 1, Enum.force.own, {6, 12})
    game:generate_unit("ChuArcher23", 1, Enum.force.own, {3, 11})

    danbo_id = game:generate_unit("DanBo23", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("ZhengGuard23", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("ZhengGuard23", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("ZhengArcher23", 1, Enum.force.enemy, {5, 2})
    game:generate_unit("ZhengArcher23", 1, Enum.force.enemy, {10, 2})
end

function on_update(game)
    if not rear_arrived and game:has_unit("DouLian23") then rear_arrived = true end
    if not rear_arrived
       and (game:get_turn_current() >= 3 or game:is_force_within(Enum.force.own, {8, 5}, 3)) then
        rear_arrived = true
        rear_leader_id = game:generate_unit("DouLian23", 1, Enum.force.own, {16, 3})
        game:generate_unit("ChuGuard23", 1, Enum.force.own, {15, 3})
        game:generate_unit("ChuGuard23", 1, Enum.force.own, {16, 2})
        game:generate_unit("ChuArcher23", 1, Enum.force.own, {15, 2})
        game:push_cmd_speak(rear_leader_id, "后队已绕至郑军背后！封住山道，与斗章前后夹攻！")
        game:push_cmd_speak(danbo_id, "右后方也是楚军！纯门归路已断，各部收缩阵线！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if not game:has_unit("DouZhang23") then return Enum.status.defeat end
    if rear_arrived and not game:has_unit("DouLian23") then return Enum.status.defeat end
    if not game:has_unit("DanBo23") then return Enum.status.victory end
    return Enum.status.undecided
end