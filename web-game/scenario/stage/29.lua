qi_arrived = false
south_gate_spoken = false
west_gate_spoken = false
rong_lord_id = -1

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QinMuGong29", "BailiXi29", "JinHuiGong29", "XiRui29" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "royal_palace", name = "周王城", position = {9, 2}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "spirit_powder", amount = 1 } } },
    { id = "west_gate", name = "王城西门", position = {2, 5}, restore_hp = 15, restore_mp = 10,
      rewards = {} },
    { id = "south_gate_west", name = "王城南门", position = {9, 8}, restore_hp = 15, restore_mp = 10,
      rewards = {} },
    { id = "south_gate_east", name = "王城南门", position = {10, 8}, restore_hp = 15, restore_mp = 10,
      rewards = {} },
    { id = "qin_relief_camp", name = "秦军行营", position = {4, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "jin_relief_camp", name = "晋军行营", position = {14, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十九回",
    title = "晋惠公大诛群臣 管夷吾病榻论相",
    battle_title = "王城勤王",
    objective = "保护周襄王、周公孔、召伯廖，击退伊洛戎主；四名初始我方将领及第三回合到场的管仲必须存活",
    map_asset = "m049.png",
    intro = {
        { speaker = "", text = "晋惠公即位后既不割河西五城给秦国，也不兑现许给里克、丕郑父的封田，反而重用吕饴甥、郤芮等亲信。" },
        { speaker = "里克", text = "新君因我等迎立才得入绛，却把田地与旧约一概抛开。若连秦国都敢欺骗，晋国早晚要受其祸。" },
        { speaker = "郤芮", text = "里克本想迎立重耳，如今又怨望失田。丕郑父正在秦国，此二人若内外相应，君位必有危险。" },
        { speaker = "晋惠公", text = "里克有迎立之功，寡人以什么名义治他？" },
        { speaker = "郤芮", text = "他弑奚齐、卓子，又杀顾命大臣荀息。私劳不能掩公罪，请君赐其自裁。" },
        { speaker = "", text = "郤芮到里克府中宣命。里克怒斥欲加之罪何患无辞，随后拔剑自刎。祁举、共华、贾华、骓遄等旧臣皆有怨言。" },
        { speaker = "", text = "晋惠公依贾君所请，为申生改葬曲沃，谥为共世子。狐突祭墓后梦见申生成为乔山之主，预言夷吾将受天罚。" },
        { speaker = "丕郑父", text = "里克已死，我若畏罪不入绛都，反而坐实与秦国合谋。只能照常复命，再寻找保全众人的办法。" },
        { speaker = "", text = "秦使冷至带着厚礼和退还的地券来到晋国，请吕饴甥、郤芮赴秦会谈。二人怀疑这是丕郑父诱杀他们的计策。" },
        { speaker = "吕饴甥", text = "丕郑父深夜召集祁举、共华等旧臣，必有异谋。让屠岸夷假装惧罪投靠，先取得他们的手书。" },
        { speaker = "屠岸夷", text = "只要能免去弑卓子的旧罪，我愿依计行事。请二位教我怎样取信丕郑父。" },
        { speaker = "", text = "屠岸夷咬指出血立誓，骗得丕郑父等十人署名迎立重耳的手书，随即把密信交给郤芮。" },
        { speaker = "", text = "次日早朝，晋惠公以手书为证，将丕郑父、祁举、贾华、骓遄等八人押出斩首；共华主动入朝领死，也被处斩。" },
        { speaker = "", text = "丕豹逃往秦国，劝秦穆公趁晋国人心不服出兵。蹇叔、百里奚认为师出无名且没有内应，穆公没有采纳。" },
        { speaker = "", text = "同年，周王子带结交伊洛之戎，诱其进攻京师，自己准备在城内接应。戎军突然包围王城。" },
        { speaker = "周襄王", text = "叔带身为王弟却引戎攻周。立即向诸侯告急，周公孔、召伯廖率王师固守各门！" },
        { speaker = "周公孔", text = "王城四周城墙完整，戎军只能从西门与两格南门进入。王师留在城内坚守，不得擅自追出。" },
        { speaker = "召伯廖", text = "南门外戎兵最多，弓手正在压制门道。只要诸侯援军从后冲击，围城阵势便会松动。" },
        { speaker = "秦穆公", text = "王室有难，秦国不能坐视。井伯随我从西南行营推进，先击破围攻西门的戎骑。" },
        { speaker = "百里奚", text = "勤王是公义，不可借机报复晋国。秦晋两军分列道路两侧，给弓手留出射界，再合击戎主。" },
        { speaker = "晋惠公", text = "晋国虽与秦有旧约之争，今日也应先救天子。郤芮整顿东南行营，与秦军同时北进。" },
        { speaker = "郤芮", text = "戎军背靠南门堵路，正面近战若聚成一团，后方射手便无法输出。各队轮换让开中央道路。" },
        { speaker = "伊洛戎主", text = "王子带说城内自会响应，周兵不足为惧！分兵围住西门和南门，先挡住秦晋援军。" },
        { speaker = "", text = "齐桓公也命管仲率兵勤王。齐军路程较远，将在第三回合从东南方向抵达战场。" },
        { speaker = "军令", text = "城墙不可跨越，西门和两格南门可以通行并补给。第三回合管仲率齐军到场；击退伊洛戎主即可迫使戎兵撤围。" }
    },
    events = {
        { id = "south_gate", trigger = "approach", position = {9, 8}, radius = 2,
          speaker = "召伯廖", text = "诸侯援军已到南门！王师守住门内，让秦晋前后夹击戎军！" },
        { id = "west_gate", trigger = "approach", position = {2, 5}, radius = 2,
          speaker = "周公孔", text = "西门外的秦军已经接近。守军不必出城，只需压住企图回身堵门的戎骑！" },
        { id = "qi_relief", trigger = "turn", turn = 3,
          speaker = "管仲", text = "齐国奉天子急诏前来勤王！戎军退路已松，齐兵从东南列阵夹击。" }
    },
    victory = {
        { speaker = "伊洛戎主", text = "秦、晋、齐三路兵马都已到达，王城内又没有人开门接应。继续围攻只会腹背受敌，撤军！" },
        { speaker = "周襄王", text = "诸侯勤王及时，京师得以保全。各军不得追入戎地，先救治城外百姓。" },
        { speaker = "", text = "伊洛之戎焚掠东门后撤走。晋惠公与秦穆公在王城外相见，因背弃割地之约而面有惭色。" },
        { speaker = "秦穆公", text = "今日同为勤王而来，秦晋私怨不可夹杂其中。寡人不会趁晋军疲惫夜袭。" },
        { speaker = "", text = "穆姬又写信责备晋惠公污辱贾君、不纳群公子。惠公更加猜疑秦国，急忙率军返回晋国。" },
        { speaker = "丕豹", text = "晋军仓促班师，正可夜袭！若擒夷吾，重立晋君就在今日。" },
        { speaker = "秦穆公", text = "勤王之师不可转眼变成私斗之兵。即使晋侯有负于秦，也不能在天子城下失义。" },
        { speaker = "", text = "齐国援军到达时戎围已经解除。管仲派人责问戎主，戎主辩称是甘叔召他们进攻京师。" },
        { speaker = "周襄王", text = "王子带引戎犯阙，罪不可赦。逐出王城，削去党羽！" },
        { speaker = "", text = "王子带逃往齐国。伊洛戎主派人入周谢罪求和，周襄王念及边境百姓，准其退兵。" },
        { speaker = "", text = "周襄王追念管仲早年平定王位、如今又有和戎之劳，设大宴并以上卿之礼相待。" },
        { speaker = "管仲", text = "齐国尚有国氏、高氏二位上卿，臣不敢越次受礼。请以周礼下卿之位相待。" },
        { speaker = "", text = "当年冬天，管仲病势沉重。齐桓公亲自来到病榻前，询问身后由谁主持国政。" },
        { speaker = "齐桓公", text = "仲父若有不测，寡人准备把国政托付鲍叔牙，是否合适？" },
        { speaker = "管仲", text = "鲍叔牙是君子，却善恶过于分明。见人一恶便终身不忘，不适合统摄百官。" },
        { speaker = "齐桓公", text = "那么公孙隰朋如何？" },
        { speaker = "管仲", text = "隰朋不耻下问，居家不忘公门，可以任用。只是臣死之后，他恐怕也不能长久。" },
        { speaker = "齐桓公", text = "易牙烹子供寡人食用，竖刁自宫，开方舍弃卫国储位，他们难道还不可信？" },
        { speaker = "管仲", text = "易牙连亲子都能忍心烹杀，何况君主；竖刁连身体都能残害，何况君主。" },
        { speaker = "管仲", text = "开方久居齐国，父母去世也不奔丧。他舍弃千乘之国，所图必然超过千乘。三人都不可亲近。" },
        { speaker = "齐桓公", text = "这三人侍奉寡人多年，仲父从前为何不明言？" },
        { speaker = "管仲", text = "臣在时如同堤防，可以约束他们迎合君意；堤防将去，横流必至。君侯务必远离三人。" },
        { speaker = "", text = "齐桓公默然离开病榻。晋国的清洗、周室的戎患与齐国的权力交接，都为此后更大的动荡埋下伏笔。" },
        { speaker = "下回预告", text = "第三十回：管仲病逝后齐国内政渐乱，秦晋之间也将因饥荒、背约与韩原之战彻底决裂。" }
    },
    defeat = {
        { speaker = "周公孔", text = "王城守军已经失去主心，戎兵正从城门涌入。天子必须立即撤离！" },
        { speaker = "", text = "周襄王、周公孔、召伯廖，或任一我方有名将领被击退，本关失败。" }
    }
}

gstage = {
    title_id = "RelieveRoyalCity29", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "~~FFFFFgggggFFFFFFF",
            "~~WWWWWWWWWWWWWWWFF",
            "~gWiiiiiiCiiiiiiWgg",
            "~gWiihiiiiiiihiiWgg",
            "~gWiiiiiiiiiiiiiWgg",
            "~gGiiiiiiiiiiiiiWgg",
            "~gWiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWWWWWWWGGWWWWWWgg",
            "gggggggggffgggggggg",
            "gggggggggffgggggggg",
            "ggggeggggffgggegggg",
            "gggggggggffgggggggg",
            "FFFggggggffgggggFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 11}, hero = "QinMuGong29" },
            { position = {3, 12}, hero = "BailiXi29" },
            { position = {14, 11}, hero = "JinHuiGong29" },
            { position = {15, 12}, hero = "XiRui29" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3800 }
}

function on_deploy(game)
    game:appoint_hero("QinMuGong29", 1)
    game:appoint_hero("BailiXi29", 1)
    game:appoint_hero("JinHuiGong29", 1)
    game:appoint_hero("XiRui29", 1)
end

function on_begin(game)
    game:generate_unit("QinGuard29", 1, Enum.force.own, {5, 12})
    game:generate_unit("QinArcher29", 1, Enum.force.own, {2, 12})
    game:generate_unit("JinGuard29", 1, Enum.force.own, {13, 12})
    game:generate_unit("JinArcher29", 1, Enum.force.own, {16, 12})

    game:generate_unit("ZhouXiangWang29", 1, Enum.force.ally, {9, 2})
    game:generate_unit("ZhouGongKong29", 1, Enum.force.ally, {7, 6})
    game:generate_unit("ShaoBoLiao29", 1, Enum.force.ally, {12, 6})
    game:generate_unit("RoyalGuard29", 1, Enum.force.ally, {8, 7})
    game:generate_unit("RoyalGuard29", 1, Enum.force.ally, {11, 7})
    game:generate_unit("RoyalArcher29", 1, Enum.force.ally, {9, 7})
    game:generate_unit("RoyalArcher29", 1, Enum.force.ally, {10, 7})

    rong_lord_id = game:generate_unit("YiLuoRongLord29", 1, Enum.force.enemy, {9, 10})
    game:generate_unit("YiLuoRongGuard29", 1, Enum.force.enemy, {7, 9})
    game:generate_unit("YiLuoRongGuard29", 1, Enum.force.enemy, {12, 9})
    game:generate_unit("YiLuoRongCavalry29", 1, Enum.force.enemy, {1, 7})
    game:generate_unit("YiLuoRongCavalry29", 1, Enum.force.enemy, {17, 7})
    game:generate_unit("YiLuoRongCavalry29", 1, Enum.force.enemy, {6, 10})
    game:generate_unit("YiLuoRongCavalry29", 1, Enum.force.enemy, {13, 10})
    game:generate_unit("YiLuoRongArcher29", 1, Enum.force.enemy, {4, 9})
    game:generate_unit("YiLuoRongArcher29", 1, Enum.force.enemy, {14, 9})
    game:generate_unit("YiLuoRongArcher29", 1, Enum.force.enemy, {8, 10})
    game:generate_unit("YiLuoRongArcher29", 1, Enum.force.enemy, {11, 10})
end

function on_update(game)
    if not south_gate_spoken and game:is_force_within(Enum.force.own, {9, 8}, 2) then
        south_gate_spoken = true
        game:push_cmd_speak(rong_lord_id, "援军已经逼近南门！近战堵住道路，弓手从两翼集中射击！")
        game:push_cmd_speak(0, "南门为两格通道，前队不要堵死后方射手与骑兵的进路！")
    end
    if not west_gate_spoken and game:is_force_within(Enum.force.own, {2, 5}, 2) then
        west_gate_spoken = true
        game:push_cmd_speak(0, "西门已与秦军接通。王师继续坚守城内，秦军从外侧攻击戎军后队！")
    end
    if not qi_arrived and game:get_turn_current() >= 3 then
        qi_arrived = true
        game:generate_unit("GuanYiWu29", 1, Enum.force.own, {18, 11})
        game:generate_unit("QiGuard29", 1, Enum.force.own, {18, 10})
        game:generate_unit("QiArcher29", 1, Enum.force.own, {18, 12})
        game:push_cmd_speak(0, "第三回合，管仲率齐国援军从东南抵达战场！")
        game:push_cmd_speak(rong_lord_id, "齐兵也来了？王子带为何还不开门接应！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("ZhouXiangWang29")
       or not game:has_unit("ZhouGongKong29")
       or not game:has_unit("ShaoBoLiao29") then
        return Enum.status.defeat
    end
    if qi_arrived and not game:has_unit("GuanYiWu29") then return Enum.status.defeat end
    if not game:has_unit("YiLuoRongLord29") then return Enum.status.victory end
    return Enum.status.undecided
end
