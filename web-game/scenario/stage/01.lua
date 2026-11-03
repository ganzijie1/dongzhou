gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "DuBo", "ZuoRu" }

gduel_enabled = true
gduels = {
    {
        attacker = "DuBo", defender = "ZhouXuanWang", exp = 50,
        outcome = "retreat",
        attacker_speech = "大王执意杀臣，臣今日便以此身再进一谏！",
        defender_speech = "杜伯抗命犯驾，寡人岂能容你！",
        result_speech = "宣王负伤退入后阵，王师一时失去号令！",
        text = "杜伯奋力逼近王驾，周宣王被击伤，在护卫簇拥下撤出战场。"
    }
}

gsites = {
    {
        id = "left_watchtower", name = "西南角楼", position = {1, 10},
        restore_hp = 15, restore_mp = 0,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "left_storehouse", name = "西南宝物库", position = {5, 12},
        restore_hp = 10, restore_mp = 10,
        rewards = {
            { item = "medicine", amount = 1 },
            { item = "spirit_powder", amount = 1 }
        }
    },
    {
        id = "right_watchtower", name = "东南角楼", position = {14, 11},
        restore_hp = 15, restore_mp = 0,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "right_camp", name = "东南营寨", position = {15, 9},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "royal_storehouse", name = "王师宝物库", position = {17, 0},
        restore_hp = 20, restore_mp = 15,
        rewards = { { item = "medicine", amount = 2 } }
    },
}

gstory = {
    chapter = "第一回",
    title = "周宣王闻谣轻杀 杜大夫化厉鸣冤",
    battle_title = "东郊索命",
    objective = "击破周宣王车驾护军",
    map_asset = "m007-camp-v5.png",
    intro = {
        { speaker = "旁白", text = "周厉王失道，国人逐之；共和十四年后，太子静即位，是为周宣王。" },
        { speaker = "旁白", text = "宣王任用召虎、方叔、尹吉甫等贤臣，征淮夷、伐猃狁，一时中兴。" },
        { speaker = "旁白", text = "三十九年，宣王征姜戎败于千亩，王师伤亡惨重，王心自此多疑。" },
        { speaker = "旁白", text = "有童谣说：月将升，日将没；檿弧箕箙，几亡周国。" },
        { speaker = "周宣王", text = "市井孩童唱的是何等妖言？速召百官入朝解说！" },
        { speaker = "伯阳父", text = "月属阴、日属阳。阴盛阳衰，恐有女子乱周；檿弧箕箙，是桑木弓与箕草箭袋。" },
        { speaker = "旁白", text = "昔年龙漦藏于王府，宫女误触而孕，四十年方产下一女。宫人惧罪，将婴儿弃于清水河。" },
        { speaker = "周宣王", text = "传旨天下：严禁制造贩卖檿弧箕箙，见者即拿；并搜捕宫中弃女。" },
        { speaker = "旁白", text = "一对乡民夫妇不知禁令，携桑弓箕袋入城叫卖。官差不问缘由，竟将妇人当街杀死。" },
        { speaker = "乡民", text = "我妻无辜惨死，此城不可久留！" },
        { speaker = "旁白", text = "乡民逃至河边，见群鸟覆护一名女婴，便将她抱走，一路投奔褒城。" },
        { speaker = "旁白", text = "此女后来入宫，便是褒姒；而此刻，宣王仍以为妖孽已经绝迹。" },
        { speaker = "旁白", text = "多年后，宣王梦见绝美女子大笑，取下宗庙牌位捆成一束，扬长而去。" },
        { speaker = "周宣王", text = "那弃女至今无踪，司市官杜伯办事不力，推出斩首！" },
        { speaker = "杜伯", text = "臣奉命搜访多年，并无踪迹。无罪而杀臣，何以服天下？" },
        { speaker = "左儒", text = "杜伯无罪。王若必杀忠臣，臣愿以死相谏！" },
        { speaker = "周宣王", text = "君叫臣死，臣不得不死。再敢多言，与杜伯同罪！" },
        { speaker = "旁白", text = "杜伯含冤伏诛。左儒痛哭收尸，回家后自刎而死。" },
        { speaker = "杜伯", text = "若死者无知，此事便休；若死者有知，三年之内，必使王知妄杀之报。" },
        { speaker = "旁白", text = "三年后，宣王率百官东郊游猎。旌旗蔽日，车马雷动。" },
        { speaker = "周宣王", text = "今日围猎，众卿随寡人尽兴而归！" },
        { speaker = "尹吉甫", text = "前方忽起怪风，王驾暂缓！臣似见一辆白马素车迎面而来。" },
        { speaker = "左儒", text = "昏王可还记得无罪而死的杜大夫？今日东郊，正是鸣冤之时！" },
        { speaker = "杜伯", text = "赤弓在手，白矢已发。周王，偿还你滥杀忠良的血债吧！" },
        { speaker = "军令", text = "操纵杜伯、左儒冲破王师护卫。杜伯与周宣王相邻可触发单挑；击伤宣王后，王师将混乱两回合。" }
    },
    victory = {
        { speaker = "杜伯", text = "周王，白矢在此！" },
        { speaker = "旁白", text = "一声弓响，赤光掠过。宣王中箭伏于车中，百官惊散。" },
        { speaker = "尹吉甫", text = "护住王驾，速返镐京！今日所见，任何人不得泄露！" },
        { speaker = "旁白", text = "宣王负伤撤回镐京，东郊王师随即退散。那名被抱往褒城的女婴，也正一步步走近周室。" }
    },
    defeat = {
        { speaker = "左儒", text = "王师势众，今日未能使沉冤昭雪……" },
        { speaker = "旁白", text = "白马素车隐入风中。东郊围猎仍在继续，杜伯之冤却不会就此消散。" }
    }
}

gstage = {
    title_id = "DongJiaoRevenge",
    turn_limit = 18,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFrrmmmmrrFFPweebe",
            "FFFrrmmmmrrFFPeeeee",
            "FFFrrmmmmrrFgPfeeee",
            "wFFrrrrFFFrFgwPPPwP",
            "wwwFFFrrrrrFFwwFFFF",
            "wwwggrmmmmrFFwwwFFF",
            "wwwgrrmmmmrFFwwwFFF",
            "wwwgrrmmmmrFFwwwFFF",
            "wwwgrrmmmmrFFwwwFFF",
            "wwwwgrrrrrrFFwweFFF",
            "wcwggggggggggwwwFFF",
            "~~wwwwwwwwwwwwcFFFF",
            "g~~~~bwwwwwwwwwFFFF",
            "FFF~~wwwwwwwwwwFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {2, 6}, hero = "DuBo" },
            { position = {2, 8}, hero = "ZuoRu" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 240 }
}

function on_deploy(game)
    game:appoint_hero("DuBo", 1)
    game:appoint_hero("ZuoRu", 1)
end

function on_begin(game)
    game:generate_unit("ZhouXuanWang", 1, Enum.force.enemy, {16, 1})
    game:generate_unit("YinJiFu", 1, Enum.force.enemy, {15, 1})
    game:generate_unit("ZhaoHu", 1, Enum.force.enemy, {17, 1})
    game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {12, 1})
    game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {15, 2})
    game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {17, 2})
    game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {17, 3})
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
