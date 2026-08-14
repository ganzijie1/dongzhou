gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "DouGuWuTu20", "DouBan20", "DouLian20" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "chu_palace_20", name = "楚王宫", position = {9, 1}, restore_hp = 25, restore_mp = 20, rewards = {} },
    { id = "chu_storehouse_20", name = "楚宫府库", position = {14, 5}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "chu_south_gate_20", name = "楚宫南门", position = {9, 12}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第二十回·四",
    title = "楚成王平乱相子文",
    battle_title = "楚宫靖难",
    objective = "斗谷於菟率甲入宫，解救斗廉并诛杀图谋篡位的子元",
    map_asset = "m033.png",
    intro = {
        { speaker = "", text = "子元伐郑无功，留下空营连夜撤回楚国，却对文夫人谎称全胜。" },
        { speaker = "文夫人", text = "若真歼敌成功，应告太庙、示国人，与未亡人何干？令尹不必以虚名相媚。" },
        { speaker = "", text = "楚成王也因子元不战而还而不悦。子元内心不安，篡位和逼迫文夫人的念头反而更急。" },
        { speaker = "子元", text = "楚国军政都在我手。只要先使文夫人顺从，年幼的楚王又能奈我何？" },
        { speaker = "", text = "文夫人小恙，子元借问安进入王宫，竟把卧具搬入宫中，三日不出；数百家甲环列宫外。" },
        { speaker = "斗廉", text = "令尹虽是先王之弟，终究也是人臣。王宫岂是你梳洗寝处之地？立即退出！" },
        { speaker = "子元", text = "这是我家宫室，楚国之政也在我掌握。你一个射师，竟敢当面教训我？" },
        { speaker = "", text = "子元命家甲锁住斗廉，拘在宫廊。文夫人暗遣侍人向斗谷於菟求救。" },
        { speaker = "文夫人", text = "子元挟兵入宫，斗廉已经被拘。若再迟疑，楚国宗庙便要落入逆臣之手。" },
        { speaker = "斗谷於菟", text = "臣立即密奏楚王，约斗梧、斗御疆与斗班半夜入宫。此战只诛首恶，不扰宫人。" },
        { speaker = "楚成王", text = "子元擅兵逼宫，已非叔父而是逆臣。准你调集甲士，先救母后与斗廉。" },
        { speaker = "斗班", text = "我率前队从南门进入，直取子元寝处。斗梧、斗御疆分守走廊，防止家甲合围。" },
        { speaker = "斗谷於菟", text = "宫墙与内墙不可跨越，必须沿门廊推进。各部保持联络，不要在庭院中分散。" },
        { speaker = "子元家甲", text = "令尹有命，封锁南门与两处廊门！擅入王宫者一律格杀！" },
        { speaker = "斗廉", text = "我被拘在东廊，尚能牵制一部分守兵。诸位不必顾虑我，先控制宫门。" },
        { speaker = "子元", text = "斗氏小儿也敢称靖难？待我斩了斗班，再去与楚王理论！" },
        { speaker = "斗班", text = "我等不是作乱，正是来诛作乱之人。子元，今日休想逃出王宫！" },
        { speaker = "军令", text = "斗谷於菟、斗班、斗廉必须存活。宫墙不可通行，沿庭院和廊门击败子元及全部家甲。" }
    },
    victory = {
        { speaker = "子元", text = "楚国兵权明明尽在我手，怎么一夜之间，宫门内外全都反了？" },
        { speaker = "斗班", text = "不是楚人反你，是你挟兵逼宫、自绝于楚！" },
        { speaker = "", text = "子元持剑突围，与斗班交战。斗御疆、斗梧随后赶到，子元夺门欲走，被斗班一剑斩杀。" },
        { speaker = "斗谷於菟", text = "首恶已除。立即解开斗廉枷锁，安抚宫人；子元家甲放下武器者免死。" },
        { speaker = "斗廉", text = "宫禁已经肃清。请先向文夫人问安，再由大王公布子元罪状。" },
        { speaker = "楚成王", text = "榜示子元挟兵逼宫之罪，削灭其家。诸军不得借机牵连无罪族人。" },
        { speaker = "", text = "子元之乱平定，楚成王欲任斗廉为令尹。斗廉自称才力不足，推举斗谷於菟。" },
        { speaker = "斗廉", text = "齐国有管仲、宁戚，国富兵强。楚国若要整顿政事、抗衡中原，非斗谷於菟不可。" },
        { speaker = "楚成王", text = "谷於菟幼时有虎乳之异，今又平定宫乱。自此尊称子文，拜为楚国令尹。" },
        { speaker = "子文", text = "国家之祸多由君弱臣强。臣愿先令斗氏归还半数采邑，再整军、任贤、充实公府。" },
        { speaker = "", text = "子文迁楚都于郢，任用屈完等贤臣，楚国由此大治。齐桓公听闻后，开始警惕南方强楚。" },
        { speaker = "管夷吾", text = "楚地广兵强，今又有子文治政，不可仓促深入。应先广施威德、安定北方戎患。" },
        { speaker = "", text = "齐桓公依管仲之计，迫使小国鄣不战而降。正在谋划南方时，燕国使者忽然赶到临淄求援。" },
        { speaker = "燕使", text = "山戎大举入燕，边城接连失守。请齐侯念同盟之义，速发大军救援！" },
        { speaker = "齐桓公", text = "欲图南方，必先定北戎。传令整军，寡人将亲自救燕。" },
        { speaker = "下回预告", text = "第二十一回：管夷吾智辨俞儿，齐桓公将深入北地平定孤竹与山戎。" }
    },
    defeat = {
        { speaker = "斗谷於菟", text = "家甲控制了宫中廊门，继续强攻会危及文夫人。先退出庭院重新集结。" },
        { speaker = "", text = "子元仍挟兵据宫，楚成王与文夫人陷入危局。" }
    }
}

gstage = {
    title_id = "ChuPalaceCoup20", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "WWWWWWWWWWWWWWWWWWW",
            "WiiiiiiiiCiiiiiiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiWWiWWiWWiWWiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiihiiiiiiiibiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiWWiWWiWWiWWiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WiiiiiiiiiiiiiiiiiW",
            "WWWWWWWWWGWWWWWWWWW",
            "ggggggggggggggggggg"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {8, 10}, hero = "DouGuWuTu20" },
            { position = {10, 10}, hero = "DouBan20" },
            { position = {7, 9}, hero = "DouLian20" },
            { position = {11, 9}, hero = "DouYuJiang20" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1500 }
}

function on_deploy(game)
    game:appoint_hero("DouGuWuTu20", 1)
    game:appoint_hero("DouBan20", 1)
    game:appoint_hero("DouLian20", 1)
    game:appoint_hero("DouYuJiang20", 1)
end

function on_begin(game)
    game:generate_unit("ZiYuan20", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("ZiYuanGuard20", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("ZiYuanGuard20", 1, Enum.force.enemy, {11, 2})
    game:generate_unit("ZiYuanGuard20", 1, Enum.force.enemy, {6, 4})
    game:generate_unit("ZiYuanGuard20", 1, Enum.force.enemy, {12, 4})
    game:generate_unit("ZiYuanGuard20", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("ZiYuanArcher20", 1, Enum.force.enemy, {5, 5})
    game:generate_unit("ZiYuanArcher20", 1, Enum.force.enemy, {13, 5})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end