gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengLiGong19", "BinXuWu19" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "li_castle", name = "栎城城池", position = {8, 1}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "li_storehouse", name = "栎城府库", position = {9, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "li_south_gate", name = "栎城南门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "qi_camp_19", name = "齐军行营", position = {4, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "li_exile_camp", name = "郑厉公行营", position = {14, 11}, restore_hp = 20, restore_mp = 15, rewards = {} }
}

gstory = {
    chapter = "第十九回·上",
    title = "擒傅瑕厉公复国",
    battle_title = "栎城复郑",
    objective = "郑厉公与宾须无由南门击破郑军，生擒傅瑕，为复国打开道路",
    map_asset = "m028.png",
    intro = {
        { speaker = "", text = "北杏会盟与遂邑问罪之后，齐桓公声望渐隆。管仲却指出，周室东迁以来，郑国久为中原强国，若不能使郑归齐，霸业仍无根基。" },
        { speaker = "管夷吾", text = "郑国内乱多年，祭足已死，子仪在位而人心未定。公子突流寓栎城，正可借此机会使郑国归附。" },
        { speaker = "齐桓公", text = "公子突昔日曾居郑君之位，如今可还愿复国？寡人愿遣一军相助。" },
        { speaker = "郑厉公", text = "寡人在外十九年，未尝一日忘记宗庙。若齐侯相援，郑国复定之后，必不负齐。" },
        { speaker = "", text = "齐桓公命宾须无率军来到栎城，与郑厉公会合。郑都闻讯，派大夫傅瑕领兵阻截。" },
        { speaker = "宾须无", text = "傅瑕远来拒敌，背后又无坚城可恃。先截住他的退路，再迫其在南门外决战。" },
        { speaker = "傅瑕", text = "子仪为郑君已久，公子突不过是流亡之人。齐军擅入郑境，今日休想越过栎城！" },
        { speaker = "郑厉公", text = "傅瑕，你既知郑国久乱，更该明白百姓盼的是安定。何苦替根基不稳的子仪死战？" },
        { speaker = "傅瑕", text = "战场之上，只凭兵刃说话。你若真有复国之志，先破我阵再谈！" },
        { speaker = "", text = "栎城北倚低山，外墙完整，只有南门可供大军进入。傅瑕把步卒列在门前，弓手登上内街两侧。" },
        { speaker = "宾须无", text = "敌军想借窄门消耗我军。弓手先压住门内，步卒不要挤成一团；一旦开路，便直取傅瑕。" },
        { speaker = "郑厉公", text = "傅瑕须留下性命。此人熟悉郑都虚实，也许正是打开国门的钥匙。" },
        { speaker = "齐军甲士", text = "南门道路已经探明，左右城墙不可跨越。请主公下令进兵！" },
        { speaker = "傅瑕", text = "守住栎城！只要拖到郑都援军赶来，齐军孤军深入，自会退去。" },
        { speaker = "军令", text = "郑厉公、宾须无必须存活。城墙不可通行，由中央南门攻入，击败傅瑕及全部守军。" }
    },
    victory = {
        { speaker = "傅瑕", text = "阵势已破，我今日落在你们手里，要杀便杀！" },
        { speaker = "郑厉公", text = "寡人不杀你。若你能助我返回郑都，既往之罪可以赦免，国政也可托付于你。" },
        { speaker = "傅瑕", text = "公子既肯信我，傅瑕愿先入都城。三日之内，必开城相迎。" },
        { speaker = "宾须无", text = "此人兵败便改投新主，未必可信。主公不可毫无防备。" },
        { speaker = "郑厉公", text = "我当然知道。但郑都守备、宫门轮值尽在他心中，眼下只能借他的手破局。" },
        { speaker = "", text = "傅瑕回到郑都，暗中联络旧部，趁夜杀死子仪及其二子，随后打开城门迎接郑厉公。" },
        { speaker = "郑厉公", text = "寡人流亡十九年，今日终于重入宗庙。先安抚百姓，不得纵兵扰民。" },
        { speaker = "傅瑕", text = "臣已兑现约定，请主公也依前言，把国政交给臣下。" },
        { speaker = "郑厉公", text = "你侍奉子仪，却因一己生死弑君迎我。这样反复无常的人，寡人岂能再托以国政？" },
        { speaker = "", text = "郑厉公下令诛杀傅瑕，以申明臣节。大夫原繁因曾拥立厉公又不能终始，惭愧自尽。" },
        { speaker = "宾须无", text = "郑国虽复，朝中旧怨仍深。主公当宽待无罪之人，才能使国势真正安定。" },
        { speaker = "郑厉公", text = "将军之言甚是。请回报齐侯，郑国愿奉王命，与齐同盟。" },
        { speaker = "", text = "郑厉公复位后，齐桓公又准备大会诸侯。此时周王室内部却因园圃与权位之争，酿成更大的祸乱。" },
        { speaker = "", text = "蔿国、边伯、石速、詹父、子禽五大夫拥立王子颓。周惠王兵败出奔，辗转来到郑国栎城。" },
        { speaker = "周惠王", text = "王子颓据成周、僭用天子礼乐。郑伯若能扶寡人复位，王室必不忘郑国之功。" },
        { speaker = "郑厉公", text = "臣既蒙先王册命，岂能坐视逆臣窃国？请大王暂驻栎城，臣即联络西虢公共讨子颓。" },
        { speaker = "下关提示", text = "第十九回·下：郑厉公与西虢公将分兵攻入成周，迎周惠王复位。" }
    },
    defeat = {
        { speaker = "宾须无", text = "栎城守军据门死战，我军阵形已经散乱。先护送郑厉公撤回营中！" },
        { speaker = "", text = "若失去齐国援军，郑厉公的复国之路还将遥遥无期。" }
    }
}

gstage = {
    title_id = "LiCityRestoration", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "mmmWWWWWWWWWWWmmmmm",
            "mmmWiiiiCiiiiWmmmmm",
            "mmmWiiihihiiiWmmmmm",
            "mmmWiiiiibiiiWmmmmm",
            "mmmWWWWWWGWWWWmmmmm",
            "ggggggggggggggggggg",
            "ggggggggggggggggggg",
            "gggggFFFgggFFFggggg",
            "gggggFFFgggFFFggggg",
            "ggggggggggggggggggg",
            "ggggggggggggggggggg",
            "ggggegggggggggegggg",
            "ggggggggggggggggggg",
            "ggggggggggggggggggg"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {14, 11}, hero = "ZhengLiGong19" },
            { position = {4, 11}, hero = "BinXuWu19" },
            { position = {3, 12}, hero = "QiGuard19" },
            { position = {6, 12}, hero = "QiArcher19" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1150 }
}

function on_deploy(game)
    game:appoint_hero("ZhengLiGong19", 1)
    game:appoint_hero("BinXuWu19", 1)
    game:appoint_hero("QiGuard19", 1)
    game:appoint_hero("QiArcher19", 1)
end

function on_begin(game)
    game:generate_unit("FuXia19", 1, Enum.force.enemy, {8, 1})
    game:generate_unit("ZhengGuard19", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("ZhengGuard19", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("ZhengGuard19", 1, Enum.force.enemy, {8, 5})
    game:generate_unit("ZhengGuard19", 1, Enum.force.enemy, {10, 5})
    game:generate_unit("ZhengArcher19", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("ZhengArcher19", 1, Enum.force.enemy, {10, 3})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end