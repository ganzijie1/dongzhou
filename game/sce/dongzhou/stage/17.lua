gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "SongHuanGong17", "XiaoShuDaXin17" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "song_restoration_camp", name = "宋军行营", position = {9, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "bo_storehouse", name = "亳城府库", position = {14, 3}, restore_hp = 15, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "bo_west_gate", name = "亳城西门", position = {5, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "bo_east_gate", name = "亳城东门", position = {13, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "bo_south_gate", name = "亳城南门", position = {9, 7}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第十七回",
    title = "宋国纳赂诛长万 楚王杯酒虏息妫",
    battle_title = "亳城平乱",
    objective = "萧叔大心与曹军内外夹攻，击破南宫牛、猛获与子游，迎公子御说归国",
    map_asset = "m026.png",
    intro = {
        { speaker = "", text = "长勺败后，齐桓公不肯罢兵，又邀宋国合攻鲁国。宋闵公命南宫长万为将、猛获为副，与齐师会于郎城。" },
        { speaker = "鲁庄公", text = "齐、宋两军互为犄角，南宫长万又有拔山举鼎之力，鲁国该如何抵挡？" },
        { speaker = "公子偃", text = "齐军号令严整，不可轻犯；宋军新到，营垒未固。臣愿以虎皮蒙马，夜袭宋营。" },
        { speaker = "", text = "百余匹蒙着虎皮的战马趁夜冲入宋营。宋军惊骇溃散，南宫长万肩中鲁庄公一箭，又被颛孙生刺伤左股，终于被擒。" },
        { speaker = "", text = "齐军见宋师已败，只得退兵。后来齐鲁通婚修好，鲁庄公释放南宫长万归宋。" },
        { speaker = "宋闵公", text = "寡人从前敬你是勇将，如今你不过是鲁国放回来的囚徒，哪里还配出使王庭？" },
        { speaker = "仇牧", text = "君臣之间当以礼相接。主公屡次以受俘之事羞辱长万，恐怕会激成祸乱。" },
        { speaker = "", text = "宋闵公不听劝告。蒙泽博局之上，他再次当众讥笑长万。长万酒后暴怒，一拳击杀闵公。" },
        { speaker = "仇牧", text = "弑君逆贼，天理不容！我虽年老，也要与你拼死！" },
        { speaker = "", text = "仇牧持笏来击，也死于长万之手；太宰华督起兵讨逆，途中同样被杀。长万拥立公子游，驱逐宋国诸公子。" },
        { speaker = "", text = "公子御说逃往亳邑，萧叔大心聚集戴、武、宣、穆、庄五族，又联合曹国援军前来救亳。" },
        { speaker = "萧叔大心", text = "南宫牛、猛获围城日久，军心已经松懈。城内宗族听见战鼓便会响应，我们从南门直取叛军中军。" },
        { speaker = "公子御说", text = "闵公虽失德，长万弑君立伪，罪不可赦。今日若能平乱，御说必与国人同守宋社。" },
        { speaker = "南宫牛", text = "五族不过乌合之众。守住两座城门，先杀萧叔，再回头扫平亳邑！" },
        { speaker = "猛获", text = "御说就在阵后，擒住他，宋国再无人敢与我们争位。" },
        { speaker = "军令", text = "公子御说、萧叔大心必须存活。城墙不可通行，只能由城门攻入；击溃叛军即可获胜。" }
    },
    victory = {
        { speaker = "萧叔大心", text = "城内已经举火响应！五族从内夹击，诸军一齐夺门！" },
        { speaker = "南宫牛", text = "城中怎么也反了？猛获，快护住子游！" },
        { speaker = "", text = "内外夹击之下，南宫牛战死，公子游被杀。猛获败逃卫国，南宫长万则抛下母亲，只身奔往陈国。" },
        { speaker = "公子御说", text = "逆党已平，先安抚城中百姓，收敛闵公、仇牧与华督遗骸，不得纵兵报复。" },
        { speaker = "", text = "萧叔大心奉御说即位，是为宋桓公。宋国重赂卫、陈两国，请其交出猛获与南宫长万。" },
        { speaker = "", text = "陈宣公命公子结诱长万饮下醇酒，待其大醉后以犀革裹身、牛筋捆缚，连夜送回宋国。长万与猛获皆被处死。" },
        { speaker = "", text = "南方的楚文王继承武王霸业，虎视汉阳。大夫鬻拳以兵谏阻止伐黄，虽获赦免，仍自断双足以明臣节。" },
        { speaker = "", text = "蔡哀侯与息侯同娶陈国女子。息妫途经蔡国时，蔡侯自恃是姐夫，接待轻薄，息侯闻讯后决意报复。" },
        { speaker = "息侯", text = "请楚王假意伐息，臣再向蔡国求救。蔡侯若来，楚军便可乘机将他擒住。" },
        { speaker = "楚文王", text = "此计既能折服蔡国，又可使息国归楚，正合寡人之意。" },
        { speaker = "", text = "蔡哀侯果然领兵救息，被楚军擒获。鬻拳劝楚王留其性命，楚王便在饯行宴上陈设女乐，释放蔡侯归国。" },
        { speaker = "蔡哀侯", text = "息妫容貌绝世，天下诸侯夫人无人能及。大王若见她，今日席中女乐便都不足观了。" },
        { speaker = "", text = "楚文王被说动，假称巡访来到息国，席间突然伏兵四起，息侯成为阶下之囚。" },
        { speaker = "息妫", text = "我一妇人事二夫，不能以死守节，尚有什么话可说？只求大王保全息侯性命。" },
        { speaker = "", text = "楚王纳息妫入宫，号为桃花夫人。她生下堵敖、成王，却数年不发一言；息侯也在故国覆亡后郁郁而终。" },
        { speaker = "下回预告", text = "第十八回：曹沫劫盟迫齐归田，管仲奉齐桓公之命整合诸侯。" }
    },
    defeat = {
        { speaker = "萧叔大心", text = "外军未能破门，城内宗族也遭到镇压。亳邑已不可久守，快护送公子撤退！" },
        { speaker = "", text = "宋国五族未能合军平乱，公子御说被迫再次流亡。" }
    }
}

gstage = {
    title_id = "BoCityRestoration", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FggggWWWWWWWWWggggF",
            "FggggWiiiiiiiWggggF",
            "FggggWiihihibWggggF",
            "FggggWiiiiiiiWggggF",
            "FggggGiiiiiiiGggggF",
            "FggggWiiiiiiiWggggF",
            "FggggWWWWGWWWWggggF",
            "FggggggggfggggggggF",
            "FgggfffffffgggggggF",
            "FggfffffffffffggggF",
            "FggggffffffffffgggF",
            "FggggggggeggggggggF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 11}, hero = "SongHuanGong17" },
            { position = {8, 11}, hero = "XiaoShuDaXin17" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1020 }
}

function on_deploy(game)
    game:appoint_hero("SongHuanGong17", 1)
    game:appoint_hero("XiaoShuDaXin17", 1)
end

function on_begin(game)
    game:generate_unit("SongClanGuard17", 1, Enum.force.own, {6, 10})
    game:generate_unit("SongClanGuard17", 1, Enum.force.own, {11, 10})
    game:generate_unit("SongArcher17", 1, Enum.force.own, {7, 12})
    game:generate_unit("CaoGuard17", 1, Enum.force.own, {10, 12})
    game:generate_unit("NanGongNiu17", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("MengHuo17", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("ZiYou17", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("RebelGuard17", 1, Enum.force.enemy, {6, 5})
    game:generate_unit("RebelGuard17", 1, Enum.force.enemy, {12, 5})
    game:generate_unit("RebelGuard17", 1, Enum.force.enemy, {8, 6})
    game:generate_unit("RebelArcher17", 1, Enum.force.enemy, {10, 6})
    game:generate_unit("RebelArcher17", 1, Enum.force.enemy, {14, 3})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end