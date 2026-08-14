gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QiHuanGong18", "GuanYiWu18" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "wei_castle_20", name = "卫国城池", position = {8, 1}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wei_storehouse_20", name = "卫国府库", position = {8, 2}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "wei_gate_20", name = "卫城南门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "qi_camp_20", name = "齐军行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十回·一",
    title = "齐侯奉命讨卫",
    battle_title = "方伯伐卫",
    objective = "奉周惠王之命击败卫懿公，突破南门并控制卫城",
    map_asset = "m030.png",
    intro = {
        { speaker = "", text = "郑文公见齐国声势日盛，主动请盟。齐桓公复会宋、鲁、陈、郑诸侯于幽，列国由此愈加归心。" },
        { speaker = "鲍叔牙", text = "明主贤臣，虽乐不忘其忧。主公不可忘出奔，管仲不可忘槛囚，宁戚不可忘饭牛。" },
        { speaker = "齐桓公", text = "寡人与诸大夫若能常记困厄之日，齐国社稷才可长久。" },
        { speaker = "", text = "周惠王遣召伯廖册齐桓公为方伯，许其专征伐，并命齐国追究卫朔当年援立王子颓之罪。" },
        { speaker = "召伯廖", text = "卫朔助逆犯顺，王室怀恨十年。今赐齐侯方伯之权，请代天子申明国法。" },
        { speaker = "管夷吾", text = "卫惠公虽已去世，王命不可不行；但罪不及无辜，先陈兵问罪，不可纵军掠民。" },
        { speaker = "", text = "齐桓公亲率车徒压向卫境。卫懿公不问来由，急令守军出城迎战。" },
        { speaker = "卫懿公", text = "父君旧事与寡人何干？齐军越境而来，若不迎敌，卫国颜面何存！" },
        { speaker = "公子开方", text = "齐军号令严整，兵力又盛。请父君固守城门，切勿在平原与其决战。" },
        { speaker = "王子成父", text = "卫军阵形仓促。臣率骑兵压住南门，步卒随后推进，弓手清除门内守军。" },
        { speaker = "齐桓公", text = "只问卫侯抗命之罪，不杀降卒。卫懿公与开方若肯服王命，留其性命。" },
        { speaker = "卫懿公", text = "守住南门！齐军虽强，城墙却不能飞越，只要拖住道路便有转机。" },
        { speaker = "管夷吾", text = "敌军以城门为中心结阵。不要拥挤在门前，先用远射迫其分散，再集中破门。" },
        { speaker = "鲍叔牙", text = "王命与军纪同样重要。入城之后封存府库，不得擅取卫人财物。" },
        { speaker = "军令", text = "齐桓公、管夷吾必须存活。城墙不可通行，由南门攻入，击败卫懿公及全部卫军。" }
    },
    victory = {
        { speaker = "卫懿公", text = "卫军已败。先君之罪既由齐侯奉王命追讨，寡人愿献金帛请和。" },
        { speaker = "齐桓公", text = "先王之制，罪不及子孙。卫国既肯遵命，寡人不再多求。" },
        { speaker = "公子开方", text = "齐侯威德行于天下，臣愿舍卫国储位，留在齐国执鞭侍从。" },
        { speaker = "管夷吾", text = "舍父母邦国而求宠于外，此人未必可托心腹。主公宜察其行，不可只听其言。" },
        { speaker = "", text = "齐桓公却认为开方爱己，拜为大夫。开方又献言卫侯少女之美，卫国遂将少卫姬送入齐宫。" },
        { speaker = "", text = "齐军班师后，中原诸侯暂安。故事转向晋国：曲沃武公并翼受封，其子诡诸即位，是为晋献公。" },
        { speaker = "晋献公", text = "桓叔、庄伯旧族盘踞国中，终是后患。士蔿可设法离散其党，尽除乱根。" },
        { speaker = "", text = "士蔿诱杀桓庄之族，又扩建绛都。晋献公整顿国政后，把目光投向西方骊戎。" },
        { speaker = "下关提示", text = "第二十回·二：晋献公将出兵骊戎，骊姬也将由此进入晋宫。" }
    },
    defeat = {
        { speaker = "管夷吾", text = "卫军据城反击，我军不宜在王命之师初战便徒增伤亡。先退回行营整顿。" },
        { speaker = "", text = "齐军未能申明王命，方伯威信受到诸侯质疑。" }
    }
}

gstage = {
    title_id = "QiPunishesWei20", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "gggWWWWWWWWWWWggggg",
            "gggWiiiiCiiiiWggggg",
            "gggWiiiibiiiiWggggg",
            "gggWiiiiiiiiiWggggg",
            "gggWWWWWWGWWWWggggg",
            "fffffffffffffffffff",
            "fffffffffffffffffff",
            "fffffFFFfffFFFfffff",
            "fffffffffffffffffff",
            "fffffffffffffffffff",
            "fffffffffffffffffff",
            "fffffffffffffffffff",
            "fffffffffefffffffff",
            "fffffffffffffffffff"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "QiHuanGong18" },
            { position = {8, 11}, hero = "GuanYiWu18" },
            { position = {10, 11}, hero = "BaoShuYa18" },
            { position = {7, 12}, hero = "WangZiChengFu18" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1300 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong18", 1)
    game:appoint_hero("GuanYiWu18", 1)
    game:appoint_hero("BaoShuYa18", 1)
    game:appoint_hero("WangZiChengFu18", 1)
end

function on_begin(game)
    game:generate_unit("WeiYiGong20", 1, Enum.force.enemy, {8, 1})
    game:generate_unit("WeiKaiFang20", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("WeiGuard20", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("WeiGuard20", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("WeiGuard20", 1, Enum.force.enemy, {8, 5})
    game:generate_unit("WeiGuard20", 1, Enum.force.enemy, {10, 5})
    game:generate_unit("WeiArcher20", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("WeiArcher20", 1, Enum.force.enemy, {11, 3})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end