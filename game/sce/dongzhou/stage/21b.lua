gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong18", "GuanYiWu18", "WangZiChengFu18", "HuErBan21" }
gduel_enabled = false
gduels = {}
ridge_reinforced = false

gsites = {
    { id = "tuanzishan_enemy_camp", name = "团子山戎营", position = {9, 2}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "beier_qi_camp", name = "卑耳溪齐营", position = {9, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十一回·二",
    title = "管夷吾智辨俞儿 齐桓公兵定孤竹",
    battle_title = "卑耳溪争渡",
    objective = "由左侧浅滩和右侧竹筏分路渡过卑耳溪，击退黄花并夺取团子山",
    map_asset = "m035.png",
    intro = {
        { speaker = "", text = "齐军离开令支，前方顽山连路、怪石嵯峨，草木封住车道。管夷吾命军士纵火清除荆棘，再凿山开路。" },
        { speaker = "齐桓公", text = "北地山险，连戎人都要下马。大军带着战车翻越群岭，恐怕人马先自疲敝。" },
        { speaker = "管夷吾", text = "劳其形者疲其神，悦其神者忘其形。让军士同唱上山、下山之歌，自能齐力推车。" },
        { speaker = "", text = "车徒唱和前行，越过数重山头，忽遇两面石壁夹住一条狭径，大车尽数壅塞。" },
        { speaker = "齐桓公", text = "此处只容单骑，若有伏兵，我军进退都无道路。仲父可有办法？" },
        { speaker = "", text = "山凹中忽有一物，朱衣玄冠、赤足如童，向齐桓公拱揖后抠起衣襟，朝石壁间疾驰而去。" },
        { speaker = "管夷吾", text = "此乃北方登山之神俞儿。它以右手抠衣，是示意前方有水，而且右深左浅，应当向左寻找渡口。" },
        { speaker = "", text = "探马回报：卑耳溪右侧深逾一丈，竹筏全被孤竹收走；向左三里却有浅滩，水只没膝。" },
        { speaker = "虎儿斑", text = "末将愿先从左侧浅滩涉水，夺下对岸高地，为大军立住阵脚。" },
        { speaker = "管夷吾", text = "孤军先渡容易被截断。王子成父、高黑走右路乘筏为正兵；虎儿斑、宾须无走左路涉水为奇兵。" },
        { speaker = "王子成父", text = "右路水深，但竹筏可以载兵。弓手先压住北岸，骑兵登陆后直取黄花中军。" },
        { speaker = "黄花", text = "齐军竟真能越过顽山！密卢、速买守住团子山，我率五千兵先把渡河之敌赶回水中！" },
        { speaker = "密卢", text = "团子山是东进要路。只要黄花拖住溪口，我军便能从岭后包抄齐军。" },
        { speaker = "速买", text = "齐军分路渡水，正是各个击破的机会。骑兵藏在山后，等他们登岸再冲。" },
        { speaker = "齐桓公", text = "两路军都以团子山为会合点。先登岸者稳住阵势，不可贪功深入。" },
        { speaker = "军令", text = "深水与岩山不可进入。左侧浅滩、右侧筏道均可通行；接近北岸后，密卢与速买的援军才会出现。" }
    },
    victory = {
        { speaker = "王子成父", text = "右路已经登岸！高黑虽不能胜黄花，我军主力赶到后，黄花阵脚终于松动。" },
        { speaker = "虎儿斑", text = "左路浅滩畅通，无终骑兵已先占团子山。山戎想从岭后包抄，反被我们截住了。" },
        { speaker = "黄花", text = "两路齐军同时合围，再战只会全军覆没。先退回无棣城，请国主增兵！" },
        { speaker = "密卢", text = "团子山已经失守，只能退往马鞭山。黄花竟敢轻视我等，此仇以后再算。" },
        { speaker = "", text = "黄花弃马翻山逃脱，密卢与速买也退向马鞭山。齐军在团子山合营，准备继续进兵。" },
        { speaker = "", text = "孤竹相国兀律古献计，建议空出无棣城，再派人诈降，把齐军诱入北方旱海迷谷。" },
        { speaker = "黄花", text = "若要齐侯相信诈降，必须先献密卢首级。我愿亲自去马鞭山取他性命，再作向导。" },
        { speaker = "", text = "黄花突斩密卢。速买愤怒交战，兵败后投奔虎儿斑，却被虎儿斑斩杀，令支君臣至此俱亡。" },
        { speaker = "管夷吾", text = "黄花来降得太过凑巧，所言孤竹国主逃往砂碛借兵，也未必可信。追击不可失去联络。" },
        { speaker = "齐桓公", text = "无棣果然是一座空城。先留燕军守城，其余各军追击，但沿途必须留下标记。" },
        { speaker = "", text = "黄花引高黑先行，渐渐与后军失去联系。齐军则在暮色中踏入白沙惨雾笼罩的旱海。" },
        { speaker = "下关提示", text = "第二十一回·三：齐军将凭老马走出迷谷，回攻无棣城，并以城内举火、三门佯攻完成合围。" }
    },
    defeat = {
        { speaker = "管夷吾", text = "两路渡河军互相失去呼应，黄花正沿河岸逐队击破。立即退回南岸重整竹筏。" },
        { speaker = "", text = "齐军争渡失利，无法继续深入孤竹。" }
    }
}

gstage = {
    title_id = "BeierCreekCrossing21", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrrrrr",
            "rmmmFgggggggggFmmmr",
            "rmmFgggggeggggggFmr",
            "rmFggffffffffgggFmr",
            "rFggffffffffffgggFr",
            "~~~~ff~~~~~~~~ff~~~",
            "~~~~ff~~~~~~~~ff~~~",
            "rFggffffffffffgggFr",
            "rmFggffffffffgggFmr",
            "rmmFgggggggggggFmmr",
            "rmmmFgggggggggFmmmr",
            "rggggggggeggggggggr",
            "rgggggggggggggggggr",
            "rrrrrrrrrrrrrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 11}, hero = "QiHuanGong18" },
            { position = {8, 12}, hero = "GuanYiWu18" },
            { position = {11, 12}, hero = "WangZiChengFu18" },
            { position = {6, 12}, hero = "HuErBan21" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1550 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong18", 1)
    game:appoint_hero("GuanYiWu18", 1)
    game:appoint_hero("WangZiChengFu18", 1)
    game:appoint_hero("HuErBan21", 1)
end

function on_begin(game)
    game:generate_unit("QiGuard21", 1, Enum.force.own, {5, 11})
    game:generate_unit("QiArcher21", 1, Enum.force.own, {13, 11})
    game:generate_unit("HuangHua21", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("GuzhuArcher21", 1, Enum.force.enemy, {5, 4})
    game:generate_unit("GuzhuArcher21", 1, Enum.force.enemy, {13, 4})
end

function on_update(game)
    if not ridge_reinforced and game:has_unit("MiLu21") then ridge_reinforced = true end
    if ridge_reinforced or not game:is_force_within(Enum.force.own, {9, 7}, 4) then return end
    ridge_reinforced = true
    local milu = game:generate_unit("MiLu21", 1, Enum.force.enemy, {4, 2})
    game:generate_unit("SuMai21", 1, Enum.force.enemy, {14, 2})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {3, 3})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {15, 3})
    game:push_cmd_speak(milu, "齐军正在登岸！从团子山两侧冲下去，把他们重新赶进溪水！")
    game:push_cmd_speak(3, "密卢果然来援。无终骑兵守住浅滩出口，绝不让两翼合拢！")
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ridge_reinforced and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
