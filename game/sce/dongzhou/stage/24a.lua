gate_exchange_spoken = false
zheng_wen_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong24", "GuanYiWu24", "BaoShuYa24", "WangZiChengFu24" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "xinmi_west_gate", name = "新密西门", position = {5, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "xinmi_east_gate", name = "新密东门", position = {13, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "xinmi_south_gate", name = "新密南门", position = {9, 7}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "xinmi_storehouse", name = "新密府库", position = {6, 3}, restore_hp = 15, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "allied_field_camp", name = "诸侯行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十四回·上",
    title = "盟召陵礼款楚大夫 会葵邱义戴周天子",
    battle_title = "新密围城",
    objective = "齐国诸侯军突破新密南门守备；齐桓公、管仲、鲍叔牙、王子成父被击退则失败",
    map_asset = "m040.png",
    intro = {
        { speaker = "", text = "屈完再入齐营，承认楚国久缺包茅之贡，请齐侯退军一舍，楚国便恢复向周室进贡。" },
        { speaker = "齐桓公", text = "楚国若肯修旧职，使寡人可以向天子复命，齐国何必再求一战？八军退三十里，驻于召陵。" },
        { speaker = "楚成王", text = "齐军拔寨后退，分明是畏惧楚国。既然如此，包茅之贡也可以不必再提。" },
        { speaker = "令尹子文", text = "八国之君尚不肯失信于匹夫，大王岂能使屈完失信于八国国君？此贡不可反悔。" },
        { speaker = "", text = "楚王命屈完携金帛八车、菁茅一车前往召陵。齐桓公则令七国军队各列一方，齐军独当楚国方向。" },
        { speaker = "齐桓公", text = "大夫请看，中原八国甲兵连营数十里。寡人以此众作战，何患不胜；以此众攻城，何患不克？" },
        { speaker = "屈完", text = "君侯以德安抚诸侯，天下自然归服；若只恃兵众，楚有方城为城、汉水为池，百万之师也未必有用。" },
        { speaker = "管仲", text = "屈大夫言中要害。楚国既肯供贡，齐国当以礼相待，不可把尊王之师变成逞强之兵。" },
        { speaker = "", text = "次日召陵筑坛，齐桓公主盟，管仲司盟，屈完代表楚王与八国同立载书，自此世通盟好。" },
        { speaker = "管仲", text = "郑国聃伯仍被拘在楚营，请大夫释放归郑；蔡侯先前得罪齐国，也可借此一并讲和。" },
        { speaker = "屈完", text = "两件事楚国都答应。菁茅将由我亲自送往洛邑，使天下知道楚国并非有意绝周。" },
        { speaker = "鲍叔牙", text = "楚国僭王才是大罪，仲父为何只责问包茅，不迫使楚王削去王号？" },
        { speaker = "管仲", text = "若强令楚国革号，势必开战，南北数年不得安宁。以包茅使其服罪复贡，胜过兵连祸结。" },
        { speaker = "", text = "联军班师途中，陈大夫辕涛涂想把粮役转嫁徐、莒，反被申侯揭破。齐侯一度拘捕涛涂，又以虎牢赏申侯。" },
        { speaker = "", text = "屈完如约向周惠王献上菁茅。隰朋随后入周告捷，却发现惠王宠爱次子叔带，已有废世子郑之意。" },
        { speaker = "公孙隰朋", text = "王见世子时神色仓皇，又让叔带并肩而出。周室嫡庶将乱，盟主不可坐视。" },
        { speaker = "管仲", text = "请世子出会诸侯。诸侯一旦共同承认储君名分，惠王即使偏爱叔带，也难再行废立。" },
        { speaker = "", text = "八国会于首止，共戴世子郑。周惠王却密令郑文公逃盟、联楚扶立叔带，郑伯不听孔叔劝谏，悄然归国。" },
        { speaker = "齐桓公", text = "郑伯受齐国救援却逃离首止，还暗通楚国。诸侯随寡人进至新密，必须使郑国重守盟信！" },
        { speaker = "管仲", text = "围城只为问罪，不可杀伤郑君与城中百姓。攻破南门守备、显出诸侯军威，便可等待郑国答复。" },
        { speaker = "郑文公", text = "城门不可轻开。孔叔守内城，申侯联络楚国；只要楚军牵制诸侯，新密之围自然可解。" },
        { speaker = "孔叔", text = "臣仍以为背齐不义，但今日受命守城，先保百姓。弓手居墙内，不得出门追击。" },
        { speaker = "王子成父", text = "城墙完整不可跨越，东西门也有守兵。主力集中南门，用弓手压制门内，再由步骑破阵。" },
        { speaker = "军令", text = "城墙无法通行，只能从三座城门进入。消灭南门校尉与两名门内守军即可触发楚军围许急报并过关。" }
    },
    victory = {
        { speaker = "新密守门校尉", text = "南门守备已经被突破！收起吊桥后的拒马，内军退守街巷，不要让百姓卷入混战！" },
        { speaker = "齐桓公", text = "诸军止步，不得入户。传话郑伯：寡人要的是他回归盟约，不是毁掉郑国宗庙。" },
        { speaker = "许国使者", text = "楚成王亲率大军围攻许城！许国新君僖公守城告急，请盟主立即发兵救援！" },
        { speaker = "管仲", text = "楚军攻许正是为新密解围。许穆公病死伐楚军中，许国事齐最勤，不能坐视其后人被围。" },
        { speaker = "齐桓公", text = "留下书信责郑，诸侯军立即转向许城。郑国若以此自称得救，只会更显背盟之失。" },
        { speaker = "", text = "申侯从楚国回到郑国，把诸侯解围全归作自己的功劳；郑文公却因虎牢之赏过厚，没有再加封爵。" },
        { speaker = "申侯", text = "若非我联楚攻许，齐侯怎肯撤去新密之围？主公今日无赏，未免薄待有功之臣。" },
        { speaker = "孔叔", text = "齐军因救许而退，并非畏郑。申侯反复挑动齐楚，只会让兵祸再次落到郑国。" },
        { speaker = "下关提示", text = "第二十四回·下：齐国诸侯军转援许城，击退楚王围城之师；胜利后接宁母、洮与葵邱会盟。" }
    },
    defeat = {
        { speaker = "管仲", text = "问罪之师若连盟主与诸将都不能保全，郑国只会更加倒向楚国。先退回行营重整！" },
        { speaker = "", text = "齐桓公、管仲、鲍叔牙或王子成父被击退，本关失败。" }
    }
}

gstage = {
    title_id = "XinmiSiege24", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FggggWWWWWWWWWggggF",
            "FggggWiiiiiiiWggggF",
            "FggggWbihihiiWggggF",
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
            { position = {8, 11}, hero = "QiHuanGong24" },
            { position = {9, 11}, hero = "GuanYiWu24" },
            { position = {10, 11}, hero = "BaoShuYa24" },
            { position = {11, 11}, hero = "WangZiChengFu24" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2100 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong24", 1)
    game:appoint_hero("GuanYiWu24", 1)
    game:appoint_hero("BaoShuYa24", 1)
    game:appoint_hero("WangZiChengFu24", 1)
end

function on_begin(game)
    game:generate_unit("CoalitionGuard24", 1, Enum.force.own, {7, 12})
    game:generate_unit("CoalitionGuard24", 1, Enum.force.own, {11, 12})
    game:generate_unit("CoalitionArcher24", 1, Enum.force.own, {6, 11})
    game:generate_unit("CoalitionArcher24", 1, Enum.force.own, {12, 11})
    zheng_wen_id = game:generate_unit("ZhengWenGong24", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("KongShu24", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("ShenHou24", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("XinmiGateCaptain24", 1, Enum.force.enemy, {9, 7})
    game:generate_unit("ZhengGateGuard24", 1, Enum.force.enemy, {8, 6})
    game:generate_unit("ZhengGateGuard24", 1, Enum.force.enemy, {10, 6})
    game:generate_unit("ZhengArcher24", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("ZhengArcher24", 1, Enum.force.enemy, {11, 4})
end

function on_update(game)
    if not gate_exchange_spoken and game:is_force_within(Enum.force.own, {9, 7}, 2) then
        gate_exchange_spoken = true
        game:push_cmd_speak(0, "南门就在眼前！弓手压住城头，步卒依次推进，不得越门劫掠！")
        game:push_cmd_speak(zheng_wen_id, "齐侯果然只攻南门守备。各军退守城内，等待楚国围许的消息！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("XinmiGateCaptain24") and not game:has_unit("ZhengGateGuard24") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end