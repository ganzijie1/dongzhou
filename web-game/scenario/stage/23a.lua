ambush_revealed = false
last_stand_spoken = false
ambush_leader_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "WeiYiGong23", "QuKong23", "YuBo23", "HuangYi23", "KongYingQi23" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "yingze_wei_camp", name = "卫军行营", position = {9, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "yingze_di_camp", name = "北狄前营", position = {9, 1}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十三回·上",
    title = "卫懿公好鹤亡国 齐桓公兴兵伐楚",
    battle_title = "荥泽死守",
    objective = "卫懿公、渠孔、于伯、黄夷、孔婴齐坚守六回合；任一人提前被击退即失败",
    map_asset = "m038.png",
    intro = {
        { speaker = "", text = "卫懿公在位九年，怠慢国政，唯独酷爱仙鹤。宫苑中养鹤数百，凡献鹤者皆得重赏。" },
        { speaker = "", text = "懿公给群鹤排定品位，上者食大夫俸，次者食士俸；出游时更以大轩载鹤在前，号称“鹤将军”。" },
        { speaker = "石祁子", text = "百姓饥寒，军府空虚，主公却厚敛鹤粮。臣与宁速屡次进谏，愿君早日回心。" },
        { speaker = "卫懿公", text = "鹤性高洁，正可彰显卫国气象。二卿不必再以小民怨言扫寡人游兴。" },
        { speaker = "", text = "公子毁见卫国必乱，托故前往齐国。卫人怨恨懿公失政，人心已暗中归附公子毁。" },
        { speaker = "", text = "北狄主瞍瞒听闻齐国远征山戎，认为中原轻视北狄，先破邢国，随即移兵攻卫。" },
        { speaker = "卫国百姓", text = "君上既给仙鹤爵禄，就让鹤将军替卫国御狄！我们空腹耕作，为何还要替鹤操兵？" },
        { speaker = "卫懿公", text = "寡人知罪了！立即放散群鹤，减去苑囿费用，只求国人同心守卫社稷。" },
        { speaker = "石祁子", text = "今日才悔悟，只怕已经太晚。狄兵连报已至荥泽，请主公向齐国求援。" },
        { speaker = "卫懿公", text = "卫国从未向齐修聘谢罪，齐侯未必肯救。寡人亲自出战，以一死谢过百姓！" },
        { speaker = "宁速", text = "臣愿代君出战，请主公留守国都。国中还需有人主持，万不可轻身赴险。" },
        { speaker = "卫懿公", text = "石祁子执玉玦代理国政，宁速持矢专任守御。若此战不胜，寡人绝不生还！" },
        { speaker = "", text = "懿公命渠孔为将，于伯为副，黄夷当前锋，孔婴齐殿后。士卒一路低唱，军心离散。" },
        { speaker = "卫军士卒", text = "鹤食禄，民力耕；鹤乘轩，民操兵。狄锋锐不可当，今日出征九死一生！" },
        { speaker = "渠孔", text = "前方狄军不过千余，左右奔走，全无行伍。传令擂鼓推进，一举踏破其前营！" },
        { speaker = "于伯", text = "荥泽两侧芦苇深密，敌骑故意散乱，恐怕是在诱我深入。中军不可离开大旆！" },
        { speaker = "瞍瞒", text = "卫军果然沿大道追来。各部隐入左右水泽，待其中军过半，再截断前后！" },
        { speaker = "军令", text = "这是一场历史死守战。五名有姓名将领必须坚持六回合；狄军伏兵会在卫军深入或第三回合出现。" }
    },
    events = {
        { id = "yingze_ambush", trigger = "approach", position = {9, 5}, radius = 3,
          speaker = "渠孔", text = "左右芦苇同时响起胡哨，狄军伏兵已经截断前后！" },
        { id = "yingze_last_stand", trigger = "turn", turn = 6,
          speaker = "卫懿公", text = "不要偃去大旆！孤宁愿死在旗前，以谢卫国百姓！" }
    },
    victory = {
        { speaker = "渠孔", text = "事急了！请主公偃去大旆，换上士卒衣甲下车，或许还能冲出包围！" },
        { speaker = "卫懿公", text = "若诸军肯救，以大旆为识；若无人肯救，去掉旗帜又有什么用？孤宁一死谢百姓！" },
        { speaker = "", text = "卫军前后队先后崩溃。黄夷战死，孔婴齐自刎，于伯中箭坠车，卫懿公与渠孔亦没于乱军。" },
        { speaker = "", text = "狄军攻入卫城。宁速与石祁子护送宫眷、公子申和史籍东走，宋桓公派兵备舟接应，遗民才得渡河。" },
        { speaker = "弘演", text = "主公尸骸已不可辨，只有肝脏尚存。既无人收殓，臣便以自己的身体作为棺椁！" },
        { speaker = "", text = "弘演剖腹纳入懿公之肝而死。从者依言暂葬，等待卫国新君迎回忠臣遗骨。" },
        { speaker = "", text = "石祁子、宁速在漕邑清点遗民，仅余七百二十人；又从共、滕二邑抽丁，扶立公子申为卫戴公。" },
        { speaker = "", text = "戴公在位数日病逝。宁速前往齐国迎公子毁，齐桓公赠车马、祭服、牲畜和门材，并遣公子无亏护送。" },
        { speaker = "卫文公", text = "先君失国，百姓流离。寡人当布衣蔬食，早起夜息，与遗民一同重建卫国。" },
        { speaker = "管仲", text = "留三千甲士久戍漕邑终非长策。不如合诸侯筑城，一劳永逸，也使狄人不敢再窥卫境。" },
        { speaker = "", text = "邢国再次告急。管仲主张等待狄军攻疲后再救，齐、宋、曹三军屯于聂北两月，邢国终被攻破。" },
        { speaker = "齐桓公", text = "寡人救援不早，使邢侯与百姓流离，罪在寡人。立即进军驱逐狄人，重建邢国！" },
        { speaker = "", text = "瞍瞒掳掠已足，放火北退。齐桓公命诸侯扑灭火势，在夷仪筑城、立宗庙，使邢侯叔颜复国。" },
        { speaker = "", text = "诸侯随后移师楚邱，为卫文公筑城封卫。齐桓公至此存鲁、存邢、存卫，霸业声望达到顶峰。" },
        { speaker = "楚成王", text = "齐侯救邢封卫，以尊王之名尽收诸侯之心。当今天下只有齐而没有楚，寡人以此为耻！" },
        { speaker = "令尹子文", text = "郑国居南北之间，是中原屏障。大王若要与齐争衡，必须先使郑国屈服。" },
        { speaker = "下关提示", text = "第二十三回·下：斗章先退后进，斗廉绕后夹击，楚军于纯门俘获郑将聃伯。" }
    },
    defeat = {
        { speaker = "卫懿公", text = "寡人尚未尽力赎罪，中军大旆已经倒下。卫国再无人能挡狄骑！" },
        { speaker = "", text = "五名有姓名将领若在第六回合前被击退，卫军阵线会过早崩溃，本关失败。" }
    }
}

gstage = {
    title_id = "YingzeLastStand23", turn_limit = 8,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFFFFgggggggggFFFFF",
            "FFggg~~~wew~~~gggFF",
            "Fggg~~~~www~~~~gggF",
            "Fgg~~~~FwwwF~~~~ggF",
            "Fgg~~~FFwwwFF~~~ggF",
            "Fggg~FggwwwggF~gggF",
            "FgggggggwwwgggggggF",
            "Fggg~FggwwwggF~gggF",
            "Fgg~~~FFwwwFF~~~ggF",
            "Fgg~~~~FwwwF~~~~ggF",
            "Fggg~~~~www~~~~gggF",
            "FFggg~~~www~~~gggFF",
            "FFggggggwewggggggFF",
            "FFFFFgggggggggFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "WeiYiGong23" },
            { position = {8, 11}, hero = "QuKong23" },
            { position = {10, 11}, hero = "YuBo23" },
            { position = {7, 12}, hero = "HuangYi23" },
            { position = {11, 12}, hero = "KongYingQi23" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1800 }
}

function on_deploy(game)
    game:appoint_hero("WeiYiGong23", 1)
    game:appoint_hero("QuKong23", 1)
    game:appoint_hero("YuBo23", 1)
    game:appoint_hero("HuangYi23", 1)
    game:appoint_hero("KongYingQi23", 1)
end

function on_begin(game)
    game:generate_unit("WeiGuard23", 1, Enum.force.own, {6, 12})
    game:generate_unit("WeiGuard23", 1, Enum.force.own, {12, 12})
    game:generate_unit("WeiArcher23", 1, Enum.force.own, {8, 10})
    game:generate_unit("WeiArcher23", 1, Enum.force.own, {10, 10})

    game:generate_unit("SouMan23", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("DiCavalry23", 1, Enum.force.enemy, {8, 2})
    game:generate_unit("DiCavalry23", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("DiArcher23", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("DiArcher23", 1, Enum.force.enemy, {10, 3})
end

function on_update(game)
    if not ambush_revealed and game:has_unit("DiAmbusher23") then ambush_revealed = true end
    if not ambush_revealed
       and (game:get_turn_current() >= 3 or game:is_force_within(Enum.force.own, {9, 5}, 3)) then
        ambush_revealed = true
        ambush_leader_id = game:generate_unit("DiAmbusher23", 1, Enum.force.enemy, {2, 5})
        game:generate_unit("DiAmbusher23", 1, Enum.force.enemy, {2, 7})
        game:generate_unit("DiArcher23", 1, Enum.force.enemy, {3, 6})
        game:generate_unit("DiAmbusher23", 1, Enum.force.enemy, {16, 5})
        game:generate_unit("DiAmbusher23", 1, Enum.force.enemy, {15, 7})
        game:generate_unit("DiArcher23", 1, Enum.force.enemy, {16, 8})
        game:push_cmd_speak(ambush_leader_id, "胡哨齐起！截断卫军前后，不要让中军退回大道！")
        game:push_cmd_speak(0, "果然中了伏兵！诸军向大旆靠拢，先保住中军阵脚！")
    end
    if not last_stand_spoken and game:get_turn_current() >= 6 then
        last_stand_spoken = true
        game:push_cmd_speak(0, "不要偃旗！孤就在大旆之下，与卫国将士共同受死！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_turn_current() > 6 then return Enum.status.victory end
    return Enum.status.undecided
end