north_spoken = false
south_spoken = false
west_spoken = false
east_spoken = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = {
    "ChongEr27", "HuMao27", "HuYan27", "ZhaoShuai27", "XuChen27",
    "WeiChou27", "DianJie27", "XianZhen27", "LuanZhi36"
}
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "WeiChou27", defender = "CaoGongGong39", exp = 100, outcome = "capture",
        attacker_speech = "曹君昔日观骈胁、薄晋公子，今日四门皆破，还不下车受缚！",
        defender_speech = "寡人一时失察，竟使晋兵乘丧车而入。左右，护我退往宫城！",
        result_speech = "魏犨奋勇突阵，追及曹共公车驾，将其生擒送往晋文公帐前。",
        text = "魏犨按原著攻破曹宫，生擒曹共公。"
    },
    {
        attacker = "DianJie27", defender = "YuLang39", exp = 100, outcome = "kill",
        attacker_speech = "于朗献诈降之计，害我三百军士。今日城破，来偿命吧！",
        defender_speech = "兵不厌诈！你若有本事，先闯过我这口刀！",
        result_speech = "两人交锋未久，颠颉一刀斩于朗于马下，为陷阱中死去的晋军报仇。",
        text = "颠颉依原著斩杀于朗。"
    }
}
gsites = {
    { id = "north_gate_l", name = "曹城北门", position = {11, 3}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "north_gate_c", name = "曹城北门", position = {12, 3}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "north_gate_r", name = "曹城北门", position = {13, 3}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "south_gate_l", name = "曹城南门", position = {11, 14}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "south_gate_c", name = "曹城南门", position = {12, 14}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "south_gate_r", name = "曹城南门", position = {13, 14}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "west_gate_u", name = "曹城西门", position = {4, 7}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "west_gate_c", name = "曹城西门", position = {4, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "west_gate_d", name = "曹城西门", position = {4, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "east_gate_u", name = "曹城东门", position = {20, 7}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "east_gate_c", name = "曹城东门", position = {20, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "east_gate_d", name = "曹城东门", position = {20, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "cao_palace", name = "曹国宫城", position = {12, 6}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "xifu_store", name = "僖负羁宝物库", position = {7, 11}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第三十九回",
    title = "柳下惠授词却敌 晋文公伐卫破曹",
    battle_title = "丧车破曹",
    objective = "由四门攻入曹都，生擒曹共公并斩于朗；九名晋国有名将领及友军僖负羁任一被击退即失败",
    map_asset = "m063.png",
    intro = {
        { speaker = "", text = "齐桓公死后诸子争立，齐国霸业渐衰。齐孝公即位，听闻鲁国遭逢饥荒，欲乘虚发兵。鲁僖公召臧孙辰商议退敌之策。" },
        { speaker = "臧孙辰", text = "齐强鲁弱，交兵难胜。柳下惠素有贤名，又明晓齐鲁旧盟，若由他出面，或能不战而退齐师。" },
        { speaker = "", text = "柳下惠不肯亲往，却将一番说辞授予弟弟展喜。展喜赶到齐军境内，在齐孝公尚未入鲁之前迎住车驾。" },
        { speaker = "展喜", text = "昔周公、太公辅佐成王，世世子孙盟誓相安。齐若趁鲁饥而伐，便是先弃王命与祖盟，何以再号令诸侯？" },
        { speaker = "齐孝公", text = "寡人本欲问罪于鲁，既有先王旧盟，今日暂且班师。鲁国也该记得修好邻邦，不可自恃旧德。" },
        { speaker = "", text = "展喜一席话使齐军退去。鲁僖公仍忧齐国再来，遂向楚国求援。楚成王令成得臣联合陈、蔡伐齐，攻取阳谷，又转而围宋缗邑。" },
        { speaker = "楚成王", text = "子文多年劳苦，可仍总领令尹之职。齐宋皆未服楚，往后诸侯纷争尚多，正需老成之臣主持。" },
        { speaker = "子文", text = "臣年已长，子玉勇略足任军旅，愿让令尹之位。只是他性情刚强，君上用其才，也须有人时时规劝。" },
        { speaker = "蒍贾", text = "子玉治军严整，却好胜而少容。若统大军遇到晋国，只怕宁折不弯，终将误事。" },
        { speaker = "", text = "与此同时，晋文公整顿国政，命郤縠将中军、郤溱佐之，狐毛将上军、狐偃佐之，栾枝将下军、先轸佐之，编成三军。" },
        { speaker = "晋文公", text = "晋国受秦助而复国，又奉天子之命定周乱。如今诸侯观望，必须以明法练成三军，方能救宋而继齐桓公之业。" },
        { speaker = "", text = "晋军在被庐大阅，祁瞒违令使军旗折断，按军法斩首示众。号令既明，三军进退如一，诸侯始知晋国已有霸主气象。" },
        { speaker = "郤縠", text = "练兵既成，当从卫、曹借道南下救宋。若两国念旧怨拒绝，再分别问罪，不可让侧翼威胁粮道。" },
        { speaker = "", text = "晋国使者向卫国借道，卫成公因当年重耳过境时的旧怨一口拒绝。晋军于是绕道侵卫，进逼五鹿。" },
        { speaker = "先轸", text = "五鹿守军望见旗少，必以为我军势孤。可令每名士卒携一面旗，山谷遍插旌旗，先夺其胆。" },
        { speaker = "", text = "五鹿守军登城，只见晋旗漫山遍野，以为数万大军已到，竟弃城奔逃。晋军不战而取五鹿，卫国上下震动。" },
        { speaker = "", text = "大军进至敛盂，郤縠忽然病逝。晋文公悲悼老将，采纳赵衰之议，擢先轸为中军元帅，使栾枝佐之。" },
        { speaker = "赵衰", text = "先轸谋取五鹿，足见知兵；栾枝沉着宽和，可补其刚。二人合领中军，足以承郤縠未竟之志。" },
        { speaker = "", text = "晋军转而围曹。曹共公想起当年重耳过境时曾偷看骈胁，心中惧怕。大夫僖负羁劝他谢罪息兵，于朗却献诈降之计。" },
        { speaker = "僖负羁", text = "当年君上失礼于晋公子，臣妻曾劝臣赠璧馈食。今日晋侯得国而来，当还其邑、谢其罪，不可再用诡计激怒强邻。" },
        { speaker = "于朗", text = "晋军新到，正可假称请降，引一队人马入城。城门暗设陷坑伏兵，杀其先锋，挫其锐气，便有议和本钱。" },
        { speaker = "曹共公", text = "就依于朗之计。城头备下强弩，若晋军中伏，立刻闭门围杀；僖负羁不必再长他人志气。" },
        { speaker = "", text = "晋文公听闻曹国请降，命寺人勃鞮假扮国君，率三百士卒入城受降。于朗骤然发动机关，三百晋军尽陷坑中，勃鞮也被乱兵杀死。" },
        { speaker = "", text = "曹军把晋军尸首悬于城上示众。先轸料定曹人敬祖畏坟，故意扬言要掘尽曹国祖墓、焚烧尸骨，以迫其归还死者。" },
        { speaker = "先轸", text = "传令军中，明日遍掘曹墓，把棺椁堆到城前。曹人若肯交还我军遗体，便让他们自行用车送出。" },
        { speaker = "", text = "曹共公果然惶恐，第三日把晋军尸体装棺送还。到第四日，曹人仍把大量丧车停在四门之外，车马往来，门禁大乱。" },
        { speaker = "狐偃", text = "四门丧车阻塞，守卒彼此呼喝，正是同时夺门之机。狐毛攻北、先轸攻南、颠颉赵衰攻西、栾枝胥臣攻东。" },
        { speaker = "晋文公", text = "各军只夺城擒主，不许扰民。僖负羁当年以璧与食相助，特在他门前立表，军士不得侵犯其家。" },
        { speaker = "军令", text = "四路齐进：魏犨遇曹共公可触发生擒，颠颉遇于朗可触发史实斩杀；城墙不可跨越，只能从四座三格城门入城。" }
    },
    events = {
        { id = "north_gate", trigger = "approach", position = {12, 3}, radius = 1,
          speaker = "狐毛", text = "北门丧车尚未挪开，守卒彼此呼喝。举盾压上，先夺门洞再向宫城推进！" },
        { id = "south_gate", trigger = "approach", position = {12, 14}, radius = 1,
          speaker = "先轸", text = "南门已乱，弓手先压制城内两翼，步军随后通过，不要挤在门外。" },
        { id = "west_gate", trigger = "approach", position = {4, 8}, radius = 1,
          speaker = "颠颉", text = "于朗就在城中！西门一破，随我直取此贼，为勃鞮与三百军士偿命！" },
        { id = "east_gate", trigger = "approach", position = {20, 8}, radius = 1,
          speaker = "栾枝", text = "东门军听令，保持队列徐进。僖负羁宅第在城内西南，任何人不得误伤。" }
    },
    victory = {
        { speaker = "", text = "晋军从四门同时突入，曹军首尾不能相顾。魏犨追上曹共公车驾，将他生擒；颠颉在巷战中一刀斩杀于朗。" },
        { speaker = "魏犨", text = "曹君已经拿下！诸军停止追击，依君命封存府库，不得伤害城中百姓。" },
        { speaker = "颠颉", text = "于朗已伏诛，三百军士之仇终于得报。勃鞮虽曾与主公有隙，这次却替主公死在陷阱里。" },
        { speaker = "曹共公", text = "寡人昔日有眼无珠，今日又误用于朗，才至国破身擒。只求晋侯勿使曹国宗社断绝。" },
        { speaker = "晋文公", text = "你当年窥我骈胁，是无礼；今日诈降杀我军，是无信。暂且拘押，曹国大夫从于朗行恶者依罪处置。" },
        { speaker = "", text = "晋文公下令诛杀参与诈降的曹国大夫三百余人，却赦免曹共公，使曹国仍保宗祀。" },
        { speaker = "僖负羁", text = "臣不能劝止国君，又见同僚遭刑，实在无颜苟活。晋侯虽守旧恩，臣家也不敢求额外庇护。" },
        { speaker = "晋文公", text = "当年我流亡曹国，满城讥笑，只有僖负羁赠璧馈食。今日在其门前立表，不只是报恩，也是让三军知道信义不可忘。" },
        { speaker = "", text = "晋军奉令绕开僖负羁宅第。魏犨、颠颉却因宅中女眷貌美，酒后翻墙闯入，并纵火焚屋。" },
        { speaker = "魏犨", text = "火势怎么突然蔓延！颠颉先退出去，我去破墙救人！" },
        { speaker = "", text = "魏犨冲入烟火救人，被烧伤肋骨；僖负羁不愿独生，最终与家人一同死于浓烟。颠颉却先行逃走。" },
        { speaker = "狐偃", text = "主公明令保护僖氏，魏犨、颠颉仍敢违令纵火。若不严惩，今日被庐练兵所立的军法便成空话。" },
        { speaker = "先轸", text = "魏犨虽有擒曹之功，却不能抵消违令；颠颉临难先逃，更不可宽纵。请君侯按军法处置，以肃三军。" },
        { speaker = "晋文公", text = "功是功，罪是罪。先查明火起经过，医治魏犨，再议二人刑罚。僖负羁一家厚葬，曹人不得侵扰。" },
        { speaker = "", text = "曹都既破，晋军打开通往宋国的道路。卫、曹两国先后受挫，中原诸侯开始转而观望晋国号令。" },
        { speaker = "", text = "然而僖负羁之死使军中震动，魏犨与颠颉将受何等处分，晋文公又将如何救宋抗楚，留待下一回分解。" }
    },
    defeat = {
        { speaker = "先轸", text = "四门攻势失去统属，曹军已重新关闭门道。先收拢残军，再图破城。" },
        { speaker = "", text = "晋文公、狐毛、狐偃、赵衰、胥臣、魏犨、颠颉、先轸、栾枝或僖负羁被击退，本关失败。" }
    }
}

gstage = {
    title_id = "FuneralCartsBreakCao39", turn_limit = 26,
    map = { blocked_edges = {}, size = {25, 19}, terrain = {
        "mmmmmmmmmmmmmmmmmmmmmmmmm",
        "mFmFFmFFmFFmFFmFFmFFmFFmm",
        "mmffgfffgffffgfffgffffgFm",
        "mFfgWWWWWWWGGGWWWWWWWgfFm",
        "mFfgWiiiiiiiiiiiiiiiWgfmm",
        "mmgfWiihiiiiiiiiihiiWffFm",
        "mFgfWiiiiiiiCiiiiiiiWffFm",
        "mFffGiiiiiiiiiiiiiiiGffmm",
        "mmffGiiiiiiiiiiiiiiiGffFm",
        "mFffGiiiiiiiiiiiiiiiGffFm",
        "mFffWiiiiiiiiiiiiiiiWfgmm",
        "mmffWiibiiiiiiiiihiiWfgFm",
        "mFfgWiiiiiiiiiiiiiiiWgfFm",
        "mFfgWiiiiiiiiiiiiiiiWgfmm",
        "mmgfWWWWWWWGGGWWWWWWWffFm",
        "mFgfffgffffgfffgffffgffFm",
        "mFffffgfffgffffgfffgfffmm",
        "mmFFmFFmFFmFFmFFmFFmFFmFm",
        "mmmmmmmmmmmmmmmmmmmmmmmmm"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {10, 1}, hero = "HuMao27" },
        { position = {12, 1}, hero = "HuYan27" },
        { position = {1, 7}, hero = "DianJie27" },
        { position = {1, 9}, hero = "ZhaoShuai27" },
        { position = {23, 8}, hero = "LuanZhi36" },
        { position = {23, 9}, hero = "XuChen27" },
        { position = {11, 16}, hero = "XianZhen27" },
        { position = {13, 16}, hero = "WeiChou27" },
        { position = {12, 17}, hero = "ChongEr27" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6500 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("JinGuard39", 1, Enum.force.own, {8, 1})
    game:generate_unit("JinArcher39", 1, Enum.force.own, {14, 1})
    game:generate_unit("JinGuard39", 1, Enum.force.own, {2, 8})
    game:generate_unit("JinArcher39", 1, Enum.force.own, {22, 8})
    game:generate_unit("JinGuard39", 1, Enum.force.own, {10, 16})
    game:generate_unit("JinArcher39", 1, Enum.force.own, {14, 16})
    game:generate_unit("CaoGongGong39", 1, Enum.force.enemy, {12, 6})
    game:generate_unit("YuLang39", 1, Enum.force.enemy, {12, 10})
    game:generate_unit("CaoGateGuard39", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("CaoGateGuard39", 1, Enum.force.enemy, {12, 14})
    game:generate_unit("CaoGateGuard39", 1, Enum.force.enemy, {4, 8})
    game:generate_unit("CaoGateGuard39", 1, Enum.force.enemy, {20, 8})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {10, 4})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {14, 4})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {10, 13})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {14, 13})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {5, 6})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {5, 10})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {19, 6})
    game:generate_unit("CaoArcher39", 1, Enum.force.enemy, {19, 10})
    game:generate_unit("XiFuJi39", 1, Enum.force.ally, {7, 5})
end

function on_update(game)
    if not north_spoken and game:is_force_within(Enum.force.own, {12, 3}, 1) then
        north_spoken = true
        game:push_cmd_speak(0, "狐毛部已接近北门，丧车尚未清空，曹军无法及时合拢城门！")
    end
    if not south_spoken and game:is_force_within(Enum.force.own, {12, 14}, 1) then
        south_spoken = true
        game:push_cmd_speak(0, "先轸部抵达南门，四路破城之势已经形成！")
    end
    if not west_spoken and game:is_force_within(Enum.force.own, {4, 8}, 1) then
        west_spoken = true
        game:push_cmd_speak(0, "颠颉、赵衰从西门突入，于朗的退路即将被截断！")
    end
    if not east_spoken and game:is_force_within(Enum.force.own, {20, 8}, 1) then
        east_spoken = true
        game:push_cmd_speak(0, "栾枝、胥臣已夺东门，曹都守军开始动摇！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("XiFuJi39") then return Enum.status.defeat end
    if not game:has_unit("CaoGongGong39") and not game:has_unit("YuLang39") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
