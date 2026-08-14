gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengLiGong19", "XiGuoGong19" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "chengzhou_palace", name = "成周王城", position = {9, 2}, restore_hp = 25, restore_mp = 20, rewards = {} },
    { id = "chengzhou_storehouse", name = "王城府库", position = {11, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "chengzhou_west_gate", name = "成周西门", position = {2, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "chengzhou_south_gate", name = "成周南门", position = {9, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "zheng_camp_19", name = "郑军行营", position = {4, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "guo_camp_19", name = "虢军行营", position = {14, 12}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第十九回·下",
    title = "杀子颓惠王复位",
    battle_title = "成周反正",
    objective = "郑、虢联军分由西门与南门攻入成周，击败王子颓及五大夫，迎周惠王还都",
    map_asset = "m029.png",
    intro = {
        { speaker = "", text = "周惠王即位后，收取蔿国等大夫的园圃，引起五大夫怨恨。蔿国、边伯、石速、詹父、子禽遂暗中拥戴王子颓。" },
        { speaker = "王子颓", text = "惠王薄待旧臣，天怒人怨。诸公共扶寡人入王城，事成之后，爵土皆有加封。" },
        { speaker = "", text = "五大夫第一次举兵失败，逃往温地，又联合卫国与南燕之师卷土重来，终于攻入成周。" },
        { speaker = "", text = "王子颓僭居王位，以天子礼乐宴饮，尤其喜爱养牛，日夜令乐工奏舞。周惠王被迫出奔郑国。" },
        { speaker = "周惠王", text = "逆臣据有宗庙宝器，诸侯却多在观望。郑伯若能复我王位，便是再造周室。" },
        { speaker = "郑厉公", text = "臣曾久居栎城，深知流亡之苦。今日必奉大王还都，绝不使王子颓久据成周。" },
        { speaker = "", text = "郑厉公先派师叔入周探听虚实，又邀西虢公会师。两国约定分攻成周西、南两门。" },
        { speaker = "师叔", text = "王子颓把精兵集中在王城内街，五大夫各守一处。南门正面兵多，西门守备稍弱。" },
        { speaker = "西虢公", text = "虢军由西门突入，牵住边伯、石速；郑军攻南门直取王子颓。两路一旦会合，逆党无处可逃。" },
        { speaker = "郑厉公", text = "先迎天子，不争首功。各军入城后严守军纪，不得惊扰周民、毁坏宗庙。" },
        { speaker = "蔿国", text = "郑伯不过刚刚复国，竟敢插手王室废立。守住两门，等卫、燕援兵来到，胜负自明！" },
        { speaker = "边伯", text = "西门外已有虢军旗号。把弓手调到内街，步卒据门，不可让两路敌军会合。" },
        { speaker = "王子颓", text = "寡人已受百官朝贺，便是真正的天子。今日谁能斩郑伯、虢公，封邑千户！" },
        { speaker = "周惠王", text = "郑、虢将士若平定叛乱，寡人必在太庙论功。诸军奋勇，收复成周！" },
        { speaker = "军令", text = "郑厉公、西虢公必须存活。城墙不可通行，从西门、南门攻入，击败王子颓和全部叛军。" }
    },
    victory = {
        { speaker = "西虢公", text = "西门已经攻破！虢军沿内街向王城推进，与郑军会合！" },
        { speaker = "郑厉公", text = "南门也已在我军手中。关闭外门，不许王子颓与五大夫逃出成周。" },
        { speaker = "王子颓", text = "卫、燕援军为何还不到？寡人的百官、礼乐，难道今日便要尽数失去？" },
        { speaker = "蔿国", text = "大势已去。只是我们既已拥立新王，今日也只能死守到底。" },
        { speaker = "", text = "郑、虢两军在王城前合击，王子颓与蔿国、边伯、石速、詹父、子禽皆死于乱军之中。" },
        { speaker = "周惠王", text = "宗庙与宝器终于收复。郑伯、西虢公扶危定倾，其功应告于列祖列宗。" },
        { speaker = "郑厉公", text = "臣只求王室安定、号令重行。成周百姓久经兵乱，请大王先减征赋、抚恤死伤。" },
        { speaker = "西虢公", text = "五大夫旧党尚散在城中，臣愿留下整顿门禁，清查兵器，却不牵连无辜家属。" },
        { speaker = "", text = "周惠王重登王位，在太庙赏赐郑厉公与西虢公。郑国因两度迎王，声势再振。" },
        { speaker = "周惠王", text = "赐郑伯虎牢以东之地，赐虢公酒泉之邑。二卿世守王畿，勿使今日之乱再起。" },
        { speaker = "师叔", text = "主公复国未久便定王室，诸侯再不敢轻视郑国。只是国中旧臣仍须慢慢安抚。" },
        { speaker = "郑厉公", text = "寡人十九年流亡，见过太多人因一时得势便忘却根本。此后更应慎刑、守信。" },
        { speaker = "", text = "齐桓公得知郑、虢平定子颓之乱，遣使向周惠王称贺，也借机继续召集列国会盟。" },
        { speaker = "", text = "然而诸侯之间的旧怨并未消散。齐、鲁、宋、郑的盟约与婚姻仍不断牵动中原局势。" },
        { speaker = "下回预告", text = "第二十回：齐桓公继续经营诸侯之盟，中原各国又将因礼法与利害再起波澜。" }
    },
    defeat = {
        { speaker = "西虢公", text = "两路兵马未能会合，叛军正从内街反扑。先护送天子撤出战场！" },
        { speaker = "", text = "郑、虢联军败退，王子颓仍据成周，周惠王复位无期。" }
    }
}

gstage = {
    title_id = "ChengzhouRestoration", turn_limit = 24,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "ggggFFFFFFFFFFFgggg",
            "ggWWWWWWWWWWWWWWWgg",
            "ggWiiiiiiCiiiiiiWgg",
            "ggWiiihiiiibiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggGiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWWWWWWWGWWWWWWWgg",
            "ggggggggggggggggggg",
            "~gggggggggggggggggg",
            "~~ggggggggggggggggg",
            "ggggegggggggggegggg",
            "ggggggggggggggggggg"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 12}, hero = "ZhengLiGong19" },
            { position = {14, 12}, hero = "XiGuoGong19" },
            { position = {5, 11}, hero = "ShiShu19" },
            { position = {6, 12}, hero = "ZhengGuard192" },
            { position = {13, 11}, hero = "GuoGuard19" },
            { position = {15, 11}, hero = "GuoArcher19" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1250 }
}

function on_deploy(game)
    game:appoint_hero("ZhengLiGong19", 1)
    game:appoint_hero("XiGuoGong19", 1)
    game:appoint_hero("ShiShu19", 1)
    game:appoint_hero("ZhengGuard192", 1)
    game:appoint_hero("GuoGuard19", 1)
    game:appoint_hero("GuoArcher19", 1)
end

function on_begin(game)
    game:generate_unit("ZhouHuiWang19", 1, Enum.force.ally, {9, 12})
    game:generate_unit("WangZiTui19", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("WeiGuo19", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("BianBo19", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("ShiSu19", 1, Enum.force.enemy, {6, 5})
    game:generate_unit("ZhanFu19", 1, Enum.force.enemy, {12, 5})
    game:generate_unit("ZiQin19", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("RoyalRebelGuard19", 1, Enum.force.enemy, {4, 4})
    game:generate_unit("RoyalRebelGuard19", 1, Enum.force.enemy, {14, 4})
    game:generate_unit("RoyalRebelGuard19", 1, Enum.force.enemy, {9, 8})
    game:generate_unit("RoyalRebelArcher19", 1, Enum.force.enemy, {5, 7})
    game:generate_unit("RoyalRebelArcher19", 1, Enum.force.enemy, {13, 7})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end