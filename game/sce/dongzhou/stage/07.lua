gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengZhuangGong7", "YingKaoShu7", "GaoQuMi7", "GongSunE7" }

gduel_enabled = true
gduels = {
    {
        attacker = "GongSunE7", defender = "YouZaiChou7", exp = 45,
        attacker_speech = "右宰丑，三国犯我郑境，今日还不下马受缚！",
        defender_speech = "无名小将，也敢在我阵前夸口！",
        result_speech = "卫军主将已死，乘势踏破敌营！",
        text = "公孙阏与右宰丑交锋，只一合便将右宰丑刺于车下！"
    }
}

gsites = {
    {
        id = "dai_storehouse", name = "戴城宝物库", position = {13, 2},
        restore_hp = 25, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "dai_castle", name = "戴城内城", position = {9, 1},
        restore_hp = 25, restore_mp = 15,
        rewards = {}
    },
    {
        id = "dai_south_gate", name = "戴城南门", position = {9, 4},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "spirit_powder", amount = 1 } }
    }
}

gstory = {
    chapter = "第七回·上",
    title = "公孙阏争车射考叔 公子翚献谄贼隐公",
    battle_title = "戴城夜袭",
    objective = "夜袭宋、卫、蔡三营，击败全部联军",
    map_asset = "m027.png",
    intro = {
        { speaker = "旁白", text = "郑军攻取郜、防二城之际，世子忽急报宋、卫联军袭入郑境。郑庄公当即向齐、鲁辞行班师。" },
        { speaker = "夷仲年", text = "三国刚刚盟誓共患相恤，郑国有警，齐军愿随郑伯回援。" },
        { speaker = "郑庄公", text = "二邑已足惩宋，齐、鲁不必久劳。郜、防两邑都赠鲁国，权作会师之谢。" },
        { speaker = "旁白", text = "郑庄公行至中途，又得文书：宋、卫没有攻下郑境，已会合蔡军转而围攻戴国。" },
        { speaker = "郑庄公", text = "孔父嘉不知兵，右宰丑又自恃勇力。三军客地扎营，正好一举收取。" },
        { speaker = "公子吕", text = "臣先打出援戴旗号，在城外虚设营寨。主公可藏在戎车之中，随戴军一同入城。" },
        { speaker = "戴君", text = "宋、卫、蔡围城日久，军民疲惫。郑国肯来相救，快开城迎公子吕入内！" },
        { speaker = "旁白", text = "戴城门户一开，郑庄公立刻逐走戴君，兼并戴国军队。城头顷刻插满郑旗。" },
        { speaker = "孔父嘉", text = "郑伯假救戴而夺戴，欺人太甚！明日列阵决战，我必与郑国分个胜负。" },
        { speaker = "右宰丑", text = "郑庄公最善用兵，恐有后计。宋、卫、蔡三营应彼此照应，不可相隔太远。" },
        { speaker = "郑庄公", text = "他们虽有三军，却各守一营。今夜分兵四路，衔枚卧鼓，以火光诱其来回奔走。" },
        { speaker = "高渠弥", text = "臣趁孔父嘉出营救援之际夺取宋军中营，截断三军联络。" },
        { speaker = "颍考叔", text = "臣从左路突击宋军，若遇孔父嘉，定叫他弃车而逃。" },
        { speaker = "公孙阏", text = "右宰丑由我对付。卫军今日既来犯郑，休想全身返回。" },
        { speaker = "军令", text = "从戴城出击，依次袭破宋、卫、蔡三处营寨；所有有名将领必须存活。" }
    },
    victory = {
        { speaker = "高渠弥", text = "宋军中营已被我军夺下，三国兵马彼此冲撞，再也不能成阵！" },
        { speaker = "颍考叔", text = "孔父嘉已经弃车步逃，只带二十余人冲出包围。" },
        { speaker = "公孙阏", text = "右宰丑阵亡，卫军尽数溃散。宋、卫、蔡三军车徒辎重都归我军。" },
        { speaker = "旁白", text = "郑庄公既得戴城，又兼并三国之师，满载而归。席间颍考叔却劝他不可自比奉王命的方伯。" },
        { speaker = "颍考叔", text = "主公假称王命伐宋，蔡、卫反助宋，郕、许又不应征。若要服众，当先问罪郕、许。" },
        { speaker = "郑庄公", text = "郕邻齐国，许邻郑国。先助齐伐郕，再请齐、鲁同来伐许，方能各得其利。" },
        { speaker = "旁白", text = "公子吕助齐攻郕，兵临国都后郕国请和；归途中公子吕染病去世。齐、鲁、郑随即约定会师伐许。" },
        { speaker = "下回预告", text = "第七回·下：三国攻许，颍考叔中箭，瑕叔盈接旗夺城。" }
    },    defeat = {
        { speaker = "郑庄公", text = "夜袭已失先机，三国联军正在重新结阵。立即退回戴城！" },
        { speaker = "旁白", text = "有名将领折损或戴城夜袭失败，郑军必须重新部署四路疑兵。" }
    }
}

gstage = {
    title_id = "DaiNightRaid",
    turn_limit = 18,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "mmmmWWWWWWWWWWWWmmm",
            "mmmmWiiiiCiiiiiWmmm",
            "mmmmWiiiiiiiibiWmmm",
            "mmmmWiiiiiiiiiiWmmm",
            "mmmmWWWWWGWWWWWWmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmgeggggwggggegmmm",
            "mmmggggggwggggggmmm"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 1}, hero = "ZhengZhuangGong7" },
            { position = {7, 2}, hero = "YingKaoShu7" },
            { position = {11, 2}, hero = "GaoQuMi7" },
            { position = {9, 3}, hero = "GongSunE7" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 420 }
}

function on_deploy(game)
    game:appoint_hero("ZhengZhuangGong7", 1)
    game:appoint_hero("YingKaoShu7", 1)
    game:appoint_hero("GaoQuMi7", 1)
    game:appoint_hero("GongSunE7", 1)
end

function on_begin(game)
    game:generate_unit("YouZaiChou7", 1, Enum.force.enemy, {14, 12})
    game:generate_unit("SongGuard7", 1, Enum.force.enemy, {8, 10})
    game:generate_unit("SongGuard7", 1, Enum.force.enemy, {10, 10})
    game:generate_unit("WeiGuard7", 1, Enum.force.enemy, {13, 11})
    game:generate_unit("WeiGuard7", 1, Enum.force.enemy, {15, 11})
    game:generate_unit("CaiArcher7", 1, Enum.force.enemy, {4, 12})
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

