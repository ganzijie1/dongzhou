gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong18", "GuanYiWu18" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "sui_castle", name = "遂邑城池", position = {9, 1}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "sui_storehouse", name = "遂邑府库", position = {13, 2}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "sui_south_gate", name = "遂邑南门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "qi_camp", name = "齐军行营", position = {4, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "song_camp", name = "宋军行营", position = {14, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第十八回",
    title = "曹沫手剑劫齐侯 桓公举火爵宁戚",
    battle_title = "遂邑问罪",
    objective = "齐宋联军由南门攻入遂邑，击败拒绝王命与北杏之会的遂国守军",
    map_asset = "m027.png",
    intro = {
        { speaker = "", text = "管仲为相三年，齐国减轻刑罚、整顿赋税，士农工商各安其业；又以乡里编伍练兵，府库与军备渐充。" },
        { speaker = "齐桓公", text = "寡人承仲父之教，更张国政。如今兵精粮足，百姓知礼义，可以召集诸侯、成就霸业了吗？" },
        { speaker = "管夷吾", text = "南有荆楚，西有秦晋，强国很多，却都只知逞强，不知尊奉周王。主公若先尊王室，诸侯自然信服。" },
        { speaker = "齐桓公", text = "周室东迁以来，号令不出王畿。寡人愿替天子安定列国，应当从何处着手？" },
        { speaker = "管夷吾", text = "宋国新平内乱，正需诸侯承认。可先请王命，会诸侯于北杏，以安宋国为名，建立盟主之信。" },
        { speaker = "", text = "齐桓公遣使入洛邑，请周釐王准许会盟。釐王见齐国愿尊王室，命使臣赐下王命。" },
        { speaker = "周使", text = "天子命齐侯抚恤诸侯、平定宋乱。列国当赴北杏，不得各怀私意、扰乱王政。" },
        { speaker = "", text = "齐国向宋、鲁、陈、蔡、卫、郑、曹、邾等国遍发盟书。宋桓公感激齐国相助，最先抵达北杏。" },
        { speaker = "宋桓公", text = "宋国内乱方定，承蒙齐侯召集诸侯加以抚定，御说愿奉王命，与齐国同盟。" },
        { speaker = "", text = "陈、蔡、邾等国随后到会。鲁庄公托病不至，卫、郑、曹也各有推辞；小国遂更是闭门拒绝使者。" },
        { speaker = "遂国君", text = "齐侯不过是诸侯之一，却假借王命号令天下。遂国城小兵少，也不能任他随意驱使！" },
        { speaker = "齐桓公", text = "大国观望，小国抗命。若第一次会盟便无人受罚，今后还有谁肯听从王命？" },
        { speaker = "管夷吾", text = "遂国近鲁而弱，拒盟最坚。先问罪于遂，既能申明王命，也可警告仍在观望的鲁国。" },
        { speaker = "鲍叔牙", text = "遂邑北面靠山，只有南门可供大军展开。臣率步卒推进，弓手压住城头，再由主公入城。" },
        { speaker = "宋桓公", text = "宋国新受诸侯之惠，此战愿出兵相助，以表同盟之诚。" },
        { speaker = "遂国君", text = "城墙坚固，齐宋联军再多，也只能挤在一座南门之外。各军守城，不得后退！" },
        { speaker = "管夷吾", text = "遂军把兵力都堆在门前，阵形看似严密。先用弓手迫其分散，再集中兵力夺门。" },
        { speaker = "军令", text = "齐桓公、管夷吾必须存活。城墙不可通行，从中央南门攻入遂邑；击败全部遂军即可获胜。" }
    },
    victory = {
        { speaker = "遂国君", text = "南门已经失守，再抵抗只会使百姓受害。开城停战，遂国愿受齐侯处置。" },
        { speaker = "齐桓公", text = "抗拒王命者必须受罚，但降卒与百姓不得杀害。封存府库，诸军不得入户劫掠。" },
        { speaker = "", text = "遂邑被攻破后，齐桓公留下守军。鲁庄公见北杏诸侯多已服齐，又失去遂国屏障，只得遣使求和。" },
        { speaker = "文姜", text = "齐鲁世为甥舅，既然齐国愿意议和，不妨暂献遂邑，待会盟时再设法索回失地。" },
        { speaker = "鲁庄公", text = "长勺虽胜，国力仍不足以连年拒齐。寡人愿在柯地与齐侯会盟，暂以遂邑为和议。" },
        { speaker = "曹沫", text = "臣三战失地，常以为耻。主公若赴柯地，请准臣随行；纵然一死，也要替鲁国取回疆土。" },
        { speaker = "", text = "柯地筑起盟坛，齐鲁两军分列坛下。齐桓公与鲁庄公登坛歃血，曹沫忽然拔出短剑，直逼齐侯。" },
        { speaker = "齐桓公", text = "曹将军在诸侯盟坛持剑相迫，究竟想要什么？" },
        { speaker = "曹沫", text = "齐强鲁弱，却屡夺鲁地。齐国边境距鲁都已经不远，主公难道还不明白寡君所忧吗？" },
        { speaker = "齐桓公", text = "寡人答应归还齐军所得的鲁国土地。盟誓既定，绝不反悔！" },
        { speaker = "", text = "曹沫掷剑下坛，北面回到臣位，神色与言辞一如平常。齐桓公回营后越想越怒，准备毁约诛杀曹沫。" },
        { speaker = "管夷吾", text = "贪图小利而在诸侯前失信，只会失去天下援助。主公若履行受胁之诺，反能使列国相信齐国重信。" },
        { speaker = "齐桓公", text = "仲父所言是。立即归还鲁国失地，不得追究曹沫。寡人宁可受一时之辱，也不能失信于天下。" },
        { speaker = "", text = "齐国如约归还汶阳等地。诸侯由此知道齐桓公守信，愿意归附齐国，霸业根基初成。" },
        { speaker = "", text = "其后桓公出行，夜间听见一名牧牛人叩角高歌，歌词感叹贤士生不逢时。桓公停车召见，问其姓名。" },
        { speaker = "宁戚", text = "臣是卫国人宁戚，家贫替商旅驾车牧牛。听闻齐侯礼贤，特来求取进身之路。" },
        { speaker = "齐桓公", text = "既有治国之言，何必等到明日查验乡里？传令举火设宴，今夜便授宁戚爵位！" },
        { speaker = "管夷吾", text = "疑人则不用，用人则不疑。主公不拘出身而取其才，天下贤士必将接踵而来。" },
        { speaker = "", text = "宁戚被任为大夫，与管仲、鲍叔牙等共同治齐。齐桓公尊王攘夷、会盟诸侯的道路由此展开。" },
        { speaker = "下回预告", text = "第十九回：郑厉公借傅瑕之手复国，周惠王将平定子颓之乱。" }
    },
    defeat = {
        { speaker = "鲍叔牙", text = "遂军依城固守，南门道路又窄。今日强攻无益，先退回行营重整阵形！" },
        { speaker = "", text = "齐国初次奉王命出兵便在遂邑受挫，北杏诸侯开始怀疑齐桓公能否主持盟会。" }
    }
}

gstage = {
    title_id = "PunitiveExpeditionAgainstSui", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
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
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 12}, hero = "QiHuanGong18" },
            { position = {5, 12}, hero = "GuanYiWu18" },
            { position = {3, 11}, hero = "BaoShuYa18" },
            { position = {6, 11}, hero = "WangZiChengFu18" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1080 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong18", 1)
    game:appoint_hero("GuanYiWu18", 1)
    game:appoint_hero("BaoShuYa18", 1)
    game:appoint_hero("WangZiChengFu18", 1)
end

function on_begin(game)
    game:generate_unit("QiGuard18", 1, Enum.force.own, {7, 12})
    game:generate_unit("QiArcher18", 1, Enum.force.own, {3, 12})
    game:generate_unit("SongHuanGong18", 1, Enum.force.ally, {14, 12})
    game:generate_unit("SongGuard18", 1, Enum.force.ally, {13, 11})
    game:generate_unit("SongArcher18", 1, Enum.force.ally, {15, 11})

    game:generate_unit("SuiLord18", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("SuiGuard18", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("SuiGuard18", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("SuiGuard18", 1, Enum.force.enemy, {12, 2})
    game:generate_unit("SuiArcher18", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("SuiArcher18", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("SuiGuard18", 1, Enum.force.enemy, {8, 5})
    game:generate_unit("SuiGuard18", 1, Enum.force.enemy, {10, 5})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end