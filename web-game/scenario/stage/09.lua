gsupply_enabled = true

gduel_enabled = true
gduels = {
    {
        attacker = "ZhuDan9", defender = "ZhouHuanWang9", exp = 55,
        outcome = "retreat",
        attacker_speech = "天王车驾在前，祝聃只射其肩，不伤性命！",
        defender_speech = "郑军无礼，竟敢向王驾放箭！",
        result_speech = "周王中箭退军，主公已经鸣金，诸军不可追赶！",
        text = "祝聃一箭射中周桓王左肩，虢公林父护住王驾退出战场。"
    }
}

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = {
    "ZhengZhuangGong9", "GaoQuMi9", "ZhuDan9",
    "JiZu9", "ManBo9", "ZhengGongZiYuan9"
}

gsites = {
    {
        id = "zheng_central_camp", name = "郑军中军营寨", position = {9, 11},
        restore_hp = 20, restore_mp = 15,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "xuge_storehouse", name = "繻葛军需库", position = {16, 7},
        restore_hp = 25, restore_mp = 10,
        rewards = {
            { item = "medicine", amount = 1 },
            { item = "spirit_powder", amount = 1 }
        }
    }
}

gstory = {
    chapter = "第九回",
    title = "齐侯送文姜婚鲁 祝聃射周王中肩",
    battle_title = "繻葛之战",
    objective = "击溃陈军、蔡卫联军与周王中军，迫使王师退兵",
    map_asset = "m002.jpg",
    intro = {
        { speaker = "旁白", text = "齐僖公次女文姜才貌出众。世子忽辞婚后，她郁郁成疾；鲁桓公遣公子翚求婚，齐侯终于应允。" },
        { speaker = "鲁桓公", text = "齐鲁世好，寡人愿以重礼迎娶文姜，使两国永结婚盟。" },
        { speaker = "齐僖公", text = "鲁侯礼数周全，寡人亲送文姜至讙邑，再交由鲁国车驾迎归。" },
        { speaker = "旁白", text = "文姜嫁入鲁国，齐鲁关系愈加亲密。与此同时，周王室与郑国积怨已经到了不可收拾的地步。" },
        { speaker = "周桓王", text = "郑寤生假命伐宋，又五年不朝。若不亲征，诸侯都将轻慢王室！" },
        { speaker = "虢公林父", text = "郑国累世勤王，骤然夺其政柄，难免生怨。请先下诏责问，不宜轻动六军。" },
        { speaker = "周桓王", text = "朕与寤生势不两立！召蔡、卫、陈三国发兵，朕亲统中军问罪。" },
        { speaker = "旁白", text = "周桓王自领中军；虢公林父统蔡、卫为右军；周公黑肩统陈军为左军，三路兵马会于繻葛。" },
        { speaker = "祭足", text = "天子亲征，名分在王。不如遣使谢罪，免使郑国背上抗王之名。" },
        { speaker = "郑庄公", text = "王室夺我卿士之政，又加兵郑境。若不挫其锋锐，郑国宗社难保。" },
        { speaker = "公子元", text = "王师分为三军，我军也分左右二拒。先破军心不稳的陈师，再冲蔡卫，最后合击王卒。" },
        { speaker = "高渠弥", text = "臣请布鱼丽阵：战车列前，甲士填补车阵空隙，层层相接，有进无退。" },
        { speaker = "曼伯", text = "臣率右拒直取陈军。陈国新遭篡乱，士卒无心为王室死战。" },
        { speaker = "祭足", text = "臣率左拒迎击蔡、卫。只待中军大旆挥动，两翼一齐进兵。" },
        { speaker = "祝聃", text = "若王师中军亲自压上，我以强弓射其车盖，先夺军心。" },
        { speaker = "军令", text = "保持六名具名将领存活，击溃王师三军。祝聃击败周桓王时会触发射王中肩对白。" }
    },
    victory = {
        { speaker = "曼伯", text = "陈军果然无心恋战，左军已经自行奔散，连周兵阵脚也被冲乱！" },
        { speaker = "祭足", text = "蔡、卫望见陈军先败，各自逃命。虢公林父虽能约束后队，也只能缓缓退兵。" },
        { speaker = "高渠弥", text = "鱼丽阵步步推进，王师中军左右失援，已经不能成列！" },
        { speaker = "旁白", text = "郑军三路合击，周王亲自断后。祝聃认准绣盖，一箭射中桓王左肩。" },
        { speaker = "祝聃", text = "周王已经中箭，臣愿追上前去，擒住王驾！" },
        { speaker = "郑庄公", text = "今日出兵只为保全社稷，怎敢凌辱天子？立即鸣金，不得追赶。" },
        { speaker = "祭足", text = "主公既已立威，臣愿携牛羊粮草前往王营问安，使天下知道郑国并无弑君之心。" },
        { speaker = "周桓王", text = "今日败军，是朕用人不明。郑伯既遣使谢罪，王师就此退回洛邑。" },
        { speaker = "旁白", text = "繻葛一战后，周王室再难以天子之兵压服郑国，王权由此更加衰微。" },
        { speaker = "下回预告", text = "第十回：楚熊通僭号称王，蔡侯乘乱袭陈。" }
    },
    defeat = {
        { speaker = "郑庄公", text = "鱼丽阵已经被王师冲散，今日先退守郑境，再图后计！" },
        { speaker = "旁白", text = "郑军三路不能相应，王师乘势推进，繻葛战局转为不利。" }
    }
}

gstage = {
    title_id = "BattleOfXuge",
    turn_limit = 24,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FgggggfffffgggggggF",
            "FgggfffffffffffgggF",
            "FggffwwfffwwffggggF",
            "FggffwwfffwwfffgggF",
            "FggffffffffffffgggF",
            "FffffgggfffgggffffF",
            "FfffggfffffffggfffF",
            "FfffgffffffffgggbfF",
            "FfffgggfffffgggfffF",
            "FgggfffffffffffgggF",
            "FggfffffffffffffggF",
            "FggggffffeffffggggF",
            "FgggggggffggggggggF",
            "FgggggggggggggggggF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 11}, hero = "ZhengZhuangGong9" },
            { position = {8, 10}, hero = "GaoQuMi9" },
            { position = {10, 10}, hero = "ZhuDan9" },
            { position = {5, 10}, hero = "JiZu9" },
            { position = {13, 10}, hero = "ManBo9" },
            { position = {9, 9}, hero = "ZhengGongZiYuan9" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 480 }
}

function on_deploy(game)
    game:appoint_hero("ZhengZhuangGong9", 1)
    game:appoint_hero("GaoQuMi9", 1)
    game:appoint_hero("ZhuDan9", 1)
    game:appoint_hero("JiZu9", 1)
    game:appoint_hero("ManBo9", 1)
    game:appoint_hero("ZhengGongZiYuan9", 1)
end

function on_begin(game)
    game:generate_unit("ZhouHuanWang9", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("GuoGongLinFu9", 1, Enum.force.enemy, {14, 3})
    game:generate_unit("ZhouGongHeiJian9", 1, Enum.force.enemy, {4, 3})
    game:generate_unit("BoYuanZhu9", 1, Enum.force.enemy, {3, 4})
    game:generate_unit("ChenSoldier9", 1, Enum.force.enemy, {2, 3})
    game:generate_unit("ChenSoldier9", 1, Enum.force.enemy, {5, 4})
    game:generate_unit("ChenSoldier9", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("CaiWeiSoldier9", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("CaiWeiSoldier9", 1, Enum.force.enemy, {15, 4})
    game:generate_unit("CaiWeiSoldier9", 1, Enum.force.enemy, {16, 3})
    game:generate_unit("RoyalGuard9", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("RoyalGuard9", 1, Enum.force.enemy, {10, 3})
end

function on_update(game) end

function on_victory(game)
end

function on_defeat(game)
end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then
        return Enum.status.defeat
    end
    if game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end