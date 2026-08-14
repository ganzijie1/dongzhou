wildmen_arrived = false
mud_spoken = false
qin_lord_id = -1
jin_lord_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QinMuGong30", "BailiXi30", "XiQiShu30", "BaiYiBing30", "GongSunZhi30", "GongZiZhi30" }
gduel_enabled = true
gduels = {
    {
        attacker = "BaiYiBing30", defender = "TuAnYi30", exp = 80, outcome = "capture",
        attacker_speech = "屠岸夷，你仗铁枪冲阵，我白乙丙今日与你分个高下！",
        defender_speech = "我要与你独手拼个死活，叫旁人都不要相助！",
        result_speech = "二人恶战五十余合，弃车扭打滚入土窟，力尽仍不松手；秦军战后将屠岸夷擒下。",
        text = "白乙丙与屠岸夷按原著恶战至双双力竭，屠岸夷被俘后由秦穆公下令处斩。"
    },
    {
        attacker = "GongSunZhi30", defender = "JinHuiGong30", exp = 100, outcome = "capture",
        attacker_speech = "晋侯背秦三恩，今日龙门山下还不下车受缚！",
        defender_speech = "小驷陷入泥中，庆郑又不肯来救。家仆徒，挡住秦军！",
        result_speech = "小驷在泥泞中拔足不起，公孙枝击败护卫，将晋惠公连同车右一并俘获。",
        text = "晋惠公所乘小驷受惊陷泥，公孙枝率秦军合围，将其生擒。"
    }
}
gsites = {}

gstory = {
    chapter = "第三十回·下",
    title = "秦晋大战龙门山 穆姬登台要大赦",
    battle_title = "韩原大战",
    objective = "生擒晋惠公；六名秦国有名将领任一被击退则失败，白乙丙可与屠岸夷触发史实擒拿",
    map_asset = "m051.png",
    intro = {
        { speaker = "", text = "晋国拒绝向秦国售粮，还宣称秦君若想吃晋粟，只管用兵来取。秦穆公于是亲率四百乘伐晋。" },
        { speaker = "秦穆公", text = "留蹇叔、繇余辅佐太子守国，孟明视巡边镇抚诸戎。井伯与寡人居中，三军直取韩原。" },
        { speaker = "百里奚", text = "晋侯虽无道，吕、郤仍能整军。秦师数量较少，必须利用士气与地形分割晋军。" },
        { speaker = "公孙枝", text = "臣领右军，公子絷领左军。西乞术、白乙丙护卫中军，前后不得脱节。" },
        { speaker = "", text = "秦军渡过河东，连续三战三胜，长驱直入韩原。晋惠公调集六百乘亲自迎战。" },
        { speaker = "庆郑", text = "秦兵为君侯背德而来，最好的办法是认错割地。若一定出战，也不该乘不熟道路的郑国小驷。" },
        { speaker = "晋惠公", text = "寡人惯乘小驷，不必多言！郤步扬御车，家仆徒为车右，屠岸夷率先锋冲阵。" },
        { speaker = "韩简", text = "秦军虽少于晋军，斗气却十倍于我。君侯三受秦恩而无一报，秦军人人都有责负之心。" },
        { speaker = "秦穆公", text = "晋侯欲国，寡人纳之；欲粟，寡人给之；如今欲战，寡人岂敢拒命！" },
        { speaker = "百里奚", text = "晋军将作死战，君侯居中不可冒进。先让左右军接住冲击，再寻找晋侯车驾。" },
        { speaker = "屠岸夷", text = "秦军谁敢挡我！我以铁枪冲开中军，再从两翼接应晋侯合围！" },
        { speaker = "白乙丙", text = "屠岸夷由我来挡。此人勇而少谋，只要缠住他，晋军先锋便失去指挥。" },
        { speaker = "公孙枝", text = "地图中央偏右是泥泞，小驷不习战阵。若晋侯车驾进入泥地，我军立即两面合围。" },
        { speaker = "西乞术", text = "韩简、蛾晰会从左路夹攻。中军保持空隙，让后队能及时救援，不要被近战堵住。" },
        { speaker = "公子絷", text = "晋军将领大多随夷吾而来，击退按撤退处理。只有屠岸夷战后依原著罪行处斩。" },
        { speaker = "", text = "三百名曾误食秦穆公良马而受赦的岐山野人听说秦国出兵，正自发奔赴韩原报恩，将在第五回合到场。" },
        { speaker = "军令", text = "泥泞可以进入但移动消耗较高。白乙丙对屠岸夷、公孙枝对晋惠公相邻时触发史实擒拿；生擒晋惠公即胜。" }
    },
    events = {
        { id = "mud_trap", trigger = "approach", position = {12, 8}, radius = 2,
          speaker = "公孙枝", text = "前面泥泞松软，诱使晋侯小驷进入，再从左右合围车驾！" },
        { id = "wildmen_relief", trigger = "turn", turn = 5,
          speaker = "岐山野人", text = "勿伤吾恩主！昔日赐酒不杀之恩，今日正该以死相报！" }
    },
    victory = {
        { speaker = "晋惠公", text = "小驷拔足不起，庆郑又弃我而去。秦军已经围住车驾，寡人今日竟成俘虏！" },
        { speaker = "公孙枝", text = "晋侯已经受缚！各部停止追杀，收拢降卒，救治双方伤兵。" },
        { speaker = "", text = "韩简、梁繇靡赶来时，晋惠公及家仆徒、虢射、郤步扬都已被押回秦营，只得弃兵投降。" },
        { speaker = "", text = "第五回合赶到的岐山野人冲散围攻秦穆公的晋军，又救起被刺落车下的西乞术。" },
        { speaker = "秦穆公", text = "当年寡人只是不忍为几匹马杀人，今日诸位竟舍命来救。愿留仕秦国者，皆有爵禄。" },
        { speaker = "岐山野人", text = "我们只为报一时之恩，不求官爵金帛。恩主平安，众人便各回乡里。" },
        { speaker = "", text = "军士在土窟中找到白乙丙与屠岸夷，二人力尽气绝仍扭在一起。秦军将他们分开抬回大营。" },
        { speaker = "秦穆公", text = "白乙丙勇烈，立即用温车送回秦国医治。屠岸夷弑卓子、杀里克，今日依法处斩。" },
        { speaker = "", text = "屠岸夷被斩，白乙丙吐血数斗，半年后才恢复。秦军乘胜掩杀，晋军六百乘仅二三成逃脱。" },
        { speaker = "百里奚", text = "此战胜在秦军理直气壮，也胜在君侯昔日施恩于民。如今如何处置晋侯，更要慎重。" },
        { speaker = "公子絷", text = "夷吾背德，可用他祭告上帝，再迎立公子重耳。晋人必会感谢秦国废无道、立有道。" },
        { speaker = "公孙枝", text = "杀晋侯只会激起晋国世仇，重耳也未必肯乘弟死入国。不如迫其割五城、送世子为质后放还。" },
        { speaker = "秦穆公", text = "子桑所谋顾及数世。先把晋侯安置灵台山离宫，派千人看守，再议归国条件。" },
        { speaker = "", text = "秦军押送晋惠公回雍。穆姬得知兄长被俘，携太子披丧服登上后园高台，台下堆满柴薪。" },
        { speaker = "穆姬", text = "晋君早晨入秦，我便早晨自焚；晚上入秦，我便晚上自焚。若赦晋侯，也就是赦我。" },
        { speaker = "秦穆公", text = "夫人虽怨兄长无信，仍不忘骨肉与礼义。传话回宫，寡人不日便放晋侯归国。" },
        { speaker = "穆姬", text = "仁者虽怨不忘亲，虽怒不弃礼。晋侯若死于秦国，我这个妹妹也不能说全无罪过。" },
        { speaker = "", text = "穆姬离开高台返回宫中。晋惠公能否履行割地、送质的条件，将在下一回继续展开。" },
        { speaker = "下回预告", text = "第三十一回：晋惠公归国后将迁怒庆郑；流亡中的重耳也会因断粮接受介子推割股奉君。" }
    },
    defeat = {
        { speaker = "百里奚", text = "秦军阵线被晋军切断，君侯身边已无援兵。先退出韩原，不能让秦君反被晋军俘获。" },
        { speaker = "", text = "秦穆公、百里奚、西乞术、白乙丙、公孙枝或公子絷被击退，本关失败。" }
    }
}

gstage = {
    title_id = "BattleHanyuan30", turn_limit = 22,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "rrrFFFgggggggFFFrrr",
        "rrrFFgggggggggFFrrr",
        "rrFgggggfffgggggFrr",
        "rFFgggfffffffgggFFr",
        "FFgggffffwffffgggFF",
        "FgggfffffwfffffgggF",
        "gggffffggwwwwfffggg",
        "gggffffggwwwwfffggg",
        "FgggfffffwwwwffffgF",
        "FFgggffffwwwwfgggFF",
        "rFFgggfffffffgggFFr",
        "rrFgggggfffgggggFrr",
        "rrrFFgggggggggFFrrr",
        "rrrFFFgggggggFFFrrr"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {9, 12}, hero = "QinMuGong30" },
        { position = {8, 11}, hero = "BailiXi30" },
        { position = {7, 12}, hero = "XiQiShu30" },
        { position = {11, 12}, hero = "BaiYiBing30" },
        { position = {13, 11}, hero = "GongSunZhi30" },
        { position = {5, 11}, hero = "GongZiZhi30" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4500 }
}

function on_deploy(game)
    game:appoint_hero("QinMuGong30", 1)
    game:appoint_hero("BailiXi30", 1)
    game:appoint_hero("XiQiShu30", 1)
    game:appoint_hero("BaiYiBing30", 1)
    game:appoint_hero("GongSunZhi30", 1)
    game:appoint_hero("GongZiZhi30", 1)
end

function on_begin(game)
    game:generate_unit("QinGuard30", 1, Enum.force.own, {6, 11})
    game:generate_unit("QinGuard30", 1, Enum.force.own, {12, 11})
    game:generate_unit("QinArcher30", 1, Enum.force.own, {8, 12})
    game:generate_unit("QinArcher30", 1, Enum.force.own, {10, 12})
    jin_lord_id = game:generate_unit("JinHuiGong30", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("TuAnYi30", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("GuoShe30", 1, Enum.force.enemy, {14, 3})
    game:generate_unit("HanJian30", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("LiangYaoMi30", 1, Enum.force.enemy, {5, 4})
    game:generate_unit("JiaPuTu30", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("XiBuYang30", 1, Enum.force.enemy, {11, 3})
    game:generate_unit("JinGuard30", 1, Enum.force.enemy, {6, 4})
    game:generate_unit("JinGuard30", 1, Enum.force.enemy, {8, 4})
    game:generate_unit("JinGuard30", 1, Enum.force.enemy, {10, 4})
    game:generate_unit("JinGuard30", 1, Enum.force.enemy, {14, 4})
    game:generate_unit("JinCavalry30", 1, Enum.force.enemy, {4, 3})
    game:generate_unit("JinCavalry30", 1, Enum.force.enemy, {16, 3})
    game:generate_unit("JinArcher30", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("JinArcher30", 1, Enum.force.enemy, {15, 2})
end

function on_update(game)
    if not mud_spoken and game:is_force_within(Enum.force.enemy, {12, 8}, 2) then
        mud_spoken = true
        game:push_cmd_speak(jin_lord_id, "小驷脚下发滑，这片泥地不可久留！郤步扬，快把车驾转向！")
        game:push_cmd_speak(0, "晋侯车驾接近泥泞，公孙枝从东路包抄，准备触发擒拿！")
    end
    if not wildmen_arrived and game:get_turn_current() >= 5 then
        wildmen_arrived = true
        game:generate_unit("WildWarrior30", 1, Enum.force.own, {0, 8})
        game:generate_unit("WildWarrior30", 1, Enum.force.own, {0, 9})
        game:generate_unit("WildArcher30", 1, Enum.force.own, {1, 10})
        game:push_cmd_speak(0, "第五回合，三百岐山野人从西侧赶到，前来报答秦穆公赐酒不杀之恩！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("JinHuiGong30") then return Enum.status.victory end
    return Enum.status.undecided
end
