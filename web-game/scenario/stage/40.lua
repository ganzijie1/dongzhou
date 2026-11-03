left_flank_spoken = false
right_flank_spoken = false
center_spoken = false
kongsang_phase = false
wei_chou_arrived = false
ceasefire_issued = false
kongsang_started_turn = 0
wei_chou_id = -1
kongsang_heroes = {"ChengDeChen33", "ChengDaXin40", "DouYueJiao40", "DouYiShen40", "DouBo33"}
kongsang_ids = {}

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = {
    "ChongEr27", "HuMao27", "HuYan27", "ZhaoShuai27",
    "XuChen27", "XianZhen27", "LuanZhi36", "QiMan40"
}
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "XuChen27", defender = "GongZiYin40", exp = 100, outcome = "kill",
        attacker_speech = "陈蔡争功冒进，虎皮车阵已冲乱你们的战马。公子印，还不受死！",
        defender_speech = "几张虎皮也敢乱我蔡军？稳住车驾，与胥臣决一死战！",
        result_speech = "蔡军战马惊惶回奔，胥臣乘乱突入，一斧将公子印劈于车下。",
        text = "胥臣依原著以虎皮蒙马之计击破陈蔡前队，斩杀公子印。"
    },
    {
        attacker = "BaiYiBing30", defender = "DouBo33", exp = 100, outcome = "retreat",
        attacker_speech = "楚右师已经自乱，斗勃休走，看我白乙丙这一箭！",
        defender_speech = "秦将也来助晋？待我重整息师，再与你交锋！",
        result_speech = "白乙丙一箭射中斗勃面颊，斗勃带箭突围，楚右师随即崩溃。",
        text = "白乙丙依原著射伤斗勃，斗勃负伤撤退。"
    }
}
gsites = {
    { id = "jin_camp_northwest", name = "晋军行营", position = {26, 5}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_command", name = "晋军中军帐", position = {32, 5}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_northeast", name = "晋军行营", position = {38, 5}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_southwest", name = "晋军行营", position = {26, 11}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_south", name = "晋军行营", position = {32, 11}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_camp_southeast", name = "晋军行营", position = {38, 11}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "kongsang_west", name = "空桑城", position = {8, 37}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "kongsang_center", name = "空桑城", position = {10, 37}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "kongsang_east", name = "空桑城", position = {12, 37}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十、四十一回",
    title = "先轸诡谋激子玉 连谷城子玉自杀",
    battle_title = "城濮之战",
    objective = "击溃楚军全部普通部队，迫使成得臣等五将撤往左下空桑；成得臣接近空桑后魏犨才率军出现，坚持五回合等候晋文公止战令。魏犨或八名晋军有名将领任一被击退则失败",
    map_asset = "m064.png",
    intro = {
        { speaker = "", text = "曹城攻破后，晋文公先处理魏犨、颠颉违令焚烧僖负羁之家的军案。赵衰奉密旨探视重伤的魏犨，魏犨束胸出见，勉强跳跃以示尚能效命。" },
        { speaker = "魏犨", text = "臣知违令当死。若主公尚肯留我残生，必以死力报国，不敢因伤自逸。" },
        { speaker = "", text = "颠颉被荀林父押到军门，仍以介子推焚死之事强辩。晋文公大怒，依军法将颠颉斩首，以其首祭僖负羁。" },
        { speaker = "晋文公", text = "颠颉主谋纵火、违令擅刑，虽有十九年从亡之功也不能赦。魏犨革去右戎之职，留待立功赎罪。" },
        { speaker = "", text = "魏犨之职由舟之侨接替。三军见从亡旧臣一死一革，才真正明白军法无私，从此号令更加严整。" },
        { speaker = "", text = "楚成王围宋至睢阳，听说卫国告急，亲率一部救卫；行至半途又闻晋军已破曹擒君，惊叹晋军用兵神速。" },
        { speaker = "楚成王", text = "晋侯流亡十九年，备尝险阻而得国，非寻常之主。令子玉撤宋围归国，不可轻与晋军争锋。" },
        { speaker = "", text = "成得臣自恃宋城旦夕可下，不肯班师，只请若战败甘受军法。楚王准其暂留，却再三告诫可和则和。" },
        { speaker = "", text = "宋成公见楚军昼夜攻城，再遣门尹般、华秀老缒城而出，携宝玉重器清册赶赴晋营求救。" },
        { speaker = "门尹般", text = "宋国存亡只在旦夕。寡君愿献宗器，请晋侯哀怜，速进兵解睢阳之围。" },
        { speaker = "先轸", text = "晋国若只因受赂救宋，名义不足。可让宋把重器分献齐秦，请两国向楚说情，再借曹卫之地激怒子玉。" },
        { speaker = "", text = "门尹般赴秦，华秀老赴齐。齐昭公遣崔夭、秦穆公遣公子縶向成得臣请和；晋国同时把曹卫近宋的田地割给宋国。" },
        { speaker = "成得臣", text = "宋人倚晋侵吞曹卫，却让齐秦来劝我退兵，岂有此理！两国使者请回，此事绝不答应。" },
        { speaker = "", text = "齐秦使者受辱而返，晋文公在中途迎入营中盛宴款待，陈说楚将骄横。齐秦于是各自发兵，与晋国共同救宋。" },
        { speaker = "", text = "楚将宛春又到晋营，提出晋国复曹卫、楚国解宋围，彼此罢兵。狐偃当面斥责，先轸却看出这是子玉归德于楚、归怨于晋的计策。" },
        { speaker = "先轸", text = "宛春之请不可听，也不可不听。私许曹卫以离其党，再拘宛春激怒子玉，宋围自然不攻自解。" },
        { speaker = "栾枝", text = "楚吞小国、辱大邦，正是中原之耻。主公若要图霸，不能只顾昔日私惠而失天下大义。" },
        { speaker = "", text = "晋文公命栾枝拘押宛春，送往五鹿交郤步扬看守；又分别许诺曹共公、卫成公复国，诱使两国写信与楚绝交。" },
        { speaker = "", text = "成得臣先闻宛春被拘，又收到曹卫绝楚书信，怒不可遏，立即撤去宋围，集结陈、蔡、郑、许诸军寻找晋军决战。" },
        { speaker = "斗越椒", text = "楚王曾戒不可轻战，齐秦又已助晋。元帅若一定要战，至少请增派兵将，不可只凭一时之怒。" },
        { speaker = "", text = "楚王不情愿地只拨西广千人，成大心又召集宗族兵六百。成得臣分成中、左、右三军，雨骤风驰直逼晋营。" },
        { speaker = "狐偃", text = "主公昔日受楚王礼遇，曾许交兵中原时退避三舍。今日必须践约，退九十里至城濮；楚若仍追，曲便在楚。" },
        { speaker = "", text = "晋军连退三舍，在城濮安营。齐将国归父、崔夭，秦将小子憖、白乙丙以及宋司马公孙固先后率军会合。" },
        { speaker = "", text = "成得臣见晋军退却，以为对方胆怯，强令楚军追至城濮，凭山阻泽下寨。晋文公夜梦与楚王搏斗不胜，狐偃却解释为楚将伏地请罪的吉兆。" },
        { speaker = "晋文公", text = "寡人退避三舍，已经报答楚王旧恩。子玉若仍逼战，明日便以三军与之一决。" },
        { speaker = "", text = "先轸复阅晋军七百乘，在有莘之墟分派三军。上军联秦攻楚左师，下军联齐攻楚右师，中军暂守阵门。" },
        { speaker = "先轸", text = "陈蔡前队怯战，胥臣以虎皮蒙马冲其车阵；栾枝曳柴扬尘假装败走。楚军两翼一乱，中军便可横击切断。" },
        { speaker = "胥臣", text = "虎皮车阵已经备好。待陈蔡战车追近，突然放车冲出，敌马必受惊回奔，反冲楚军右师。" },
        { speaker = "栾枝", text = "下军先退，车后曳柴扬起尘土；狐氏大旗也装作败走，引斗宜申与郑许军脱离本阵。" },
        { speaker = "祁瞒", text = "中军奉命坚守，不论成大心如何叫阵都不得出击。先轸元帅从侧翼横冲时，我会守住大旗不动。" },
        { speaker = "军令", text = "先击溃楚、陈、蔡、郑、许普通部队，迫使成得臣等将退往空桑。成得臣接近空桑后魏犨才率军出现，坚持五回合等候止战令；魏犨被击退则失败。" }
    },
    events = {
        { id = "tiger_carts", trigger = "approach", position = {27, 17}, radius = 3,
          speaker = "胥臣", text = "陈蔡车阵已经追近！放虎皮车，惊乱敌马，随后直取公子印！" },
        { id = "dust_feint", trigger = "approach", position = {7, 17}, radius = 3,
          speaker = "栾枝", text = "曳柴扬尘，假作全军北奔！待斗宜申深入，狐氏回军夹击！" },
        { id = "center_hold", trigger = "approach", position = {32, 18}, radius = 3,
          speaker = "先轸", text = "中军不可争一时之功。祁瞒守住阵门，我军先断楚军左右两翼！" }
    },
    victory = {
        { speaker = "", text = "晋军上下两军合围，中军荀林父、先蔑赶到接战。斗越椒射落晋军大旗，成得臣乘势突进，先轸、郤溱、栾枝、胥臣、狐毛、狐偃随即从四面压上。" },
        { speaker = "成得臣", text = "左右两军已经溃散，中军不可再陷重围。鸣金收军，由大心与越椒护住退路！" },
        { speaker = "", text = "成大心率宗兵六百死战，斗越椒往返冲阵救出楚军。晋文公命各军逐出宋、卫之境便止，不可穷追伤害楚王旧恩。" },
        { speaker = "", text = "国归父、小子憖乘虚夺取楚国大寨，粮草辎重尽归晋、齐、秦联军。成得臣只得绕过有莘山，沿睢水退向空桑。" },
        { speaker = "魏犨", text = "楚军残部已到空桑！我虽负伤，仍可挡住子玉、子西与斗越椒。诸军列阵，不许他们冲回大寨！" },
        { speaker = "", text = "魏犨独战斗越椒、斗宜申、斗勃三将。双方相持至第五回合，晋军使者飞马赶到，传达文公止战之令。" },
        { speaker = "晋军使者", text = "先元帅奉主公之命：放楚将生还本国，以报楚王昔日款待之德。魏将军立即停战，让开归路！" },
        { speaker = "魏犨", text = "既是君命，今日饶你们去。楚军速离空桑，若再回头犯阵，魏犨仍以军法相待！" },
        { speaker = "", text = "成得臣回到连谷，见中军尚存六七，申、息左右军却十不存一，便与斗宜申、斗勃自囚，请成大心赴申城向楚王请罪。" },
        { speaker = "楚成王", text = "子玉出征前自言不胜甘受军令。楚法兵败者死，诸将应当自裁，不可再污斧锧。" },
        { speaker = "成得臣", text = "纵使大王赦我，我又有何面目见申、息父老？大心收好残军，父今日以一死谢国。" },
        { speaker = "", text = "成得臣北向再拜，在连谷拔剑自刎。蒍贾劝蔿吕臣以楚王旧赐免死牌求情，赦令赶到时，成得臣已经死去半日。" },
        { speaker = "", text = "斗宜申悬梁时因身体沉重扯断白绫，斗勃因要收殓子玉、子西也没有自尽，二人后来都获赦。楚成王闻子玉已死，悔恨不已。" },
        { speaker = "", text = "楚王拜蔿吕臣为令尹，成大心、成嘉为大夫。令尹子文临终告诫斗般椒：斗越椒有熊虎之状、豺狼之声，将来若执政，斗氏宗族必有大祸。" },
        { speaker = "", text = "晋文公在楚寨用遗粮休军三日，齐、秦、宋诸军辞归。先轸将祁瞒押至军前，奏明他违令出战、扰乱中军之罪。" },
        { speaker = "晋文公", text = "若非上下两军先胜，楚中军岂能击溃？军令不可因侥幸获胜而废。" },
        { speaker = "", text = "赵衰依军法斩祁瞒示众。晋军班师至南河时舟船不足，先轸以厚赏募船，百姓争相应募，大军迅速渡过黄河。" },
        { speaker = "", text = "郑文公遣子人九请成。赵衰劝晋侯暂息师旅，晋文公准许郑国归附，并命狐毛、狐偃先往践土修筑王宫。" },
        { speaker = "王子虎", text = "天子闻晋侯伐楚得胜、少安中国，将亲驾劳军。请晋侯五月在践土候驾，率诸侯共行朝礼。" },
        { speaker = "", text = "周襄王驾临践土，晋文公献楚俘、车马与器械。天子册命晋侯为方伯，赐彤弓玄矢与虎贲三百人，许其专征王慝。" },
        { speaker = "周襄王", text = "齐桓公去世后荆楚复强，叔父仗义翦伐、尊奖王室。今日册为盟主，望合诸侯修盟会之政。" },
        { speaker = "", text = "晋文公登践土盟坛执牛耳，齐、秦、宋、卫、郑、曹等诸侯歃血修盟。城濮一战至此结束，晋国正式继齐而主盟中原。" },
        { speaker = "下回预告", text = "第四十二回：周襄王河阳受觐，卫元咺将在公馆与卫成公对狱，叔武之死也将引发新的冤案。" }
    },
    defeat = {
        { speaker = "先轸", text = "我军一翼过早崩溃，楚军中军已经乘势压上。先退回有莘重整三军，不可让君侯陷入重围。" },
        { speaker = "", text = "八名晋军有名将领任一被击退，本关失败。" }
    }
}

gstage = {
    title_id = "BattleOfChengpu40", turn_limit = 50,
    map = { blocked_edges = {}, size = {64, 42}, terrain = {
        "mmmmmFFFFFFFFFfggfffggfffggfffggfffggfffggfffggfffggfffggfffggff",
        "mmmmmFFFFFFFFFgfffggPPPPPPPPPPPPPPPPPPPPPPPPgfffggfffggfffggfffg",
        "mmmmmFFFFFFFFFffggffPggfffggfffggfffggfffggPffggfffggfffggfffggf",
        "mmmmmFFFFFFFFFggfffgPfffggfffggfffggfffggffPggfffggfffggfffggfff",
        "mmmmmFFFFFFFFFfffggfPfggfffggfffggfffggfffgPfffggfffggfffggfffgg",
        "mmmmmFFFFFFFFFfggfffPgfffgefffggeffggfefggfPfggfffggfffggfffggff",
        "mmmmmFFFFFFFFFgfffggPffggfffggfffggfffggfffPgfffggfffggfffggfffg",
        "mmmmmFFFFFFFFfffggffPggfffggfffggfffggfffggPffggfffggfffggfffggf",
        "FFFFFFFFFFFFffggfffgPfffggfffggfffggfffggffPggfffggfffggfffggfff",
        "FFFFFFFFFFFfggfffggfPfggfffggfffggfffggfffgPfffggfffggfffggfffgg",
        "FFFFFFFFFFggfffggfffPgfffggfffggfffggfffggfPfggfffggfffggfffggff",
        "FFFFFFFFFgfffggfffggPffggfefggffeggfffegfffPgfffggfffggfffggfffg",
        "fggfffggfffggfffggffPggfffggfffggfffggfffggPffggfffggfffggfffggf",
        "gfffggfffggfffggfffgPfffggfffggfffggfffggffPggfffggfffggfffggfff",
        "ffggfffggfffggfffggfPfggfffggfffggfffggfffgPfffggfffggfffggfffgg",
        "ggfffggfffggfffggfffPPPPPPPPPPggffPPPPPPPPPPfggfffggfffggfffggff",
        "fffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffg",
        "fggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggf",
        "gfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfff",
        "ffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffgg",
        "ggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggff",
        "fffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffg",
        "fggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggf",
        "gfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfff",
        "ffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffgw",
        "ggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggww",
        "fffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfwww",
        "fggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggffwwww",
        "gfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffwwwww",
        "ffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffgwwwwww",
        "ggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggwwwwww~",
        "mmmmFfffggfffggfffggfffggfffggfffggfffggfffggfffggfffggfwwwwww~~",
        "mmmmFWWWWGGWWWWWggfffggfffggfffggfffggfffggfffggfffggffwwwwww~~~",
        "mmmmFWiiiiiiiiiWfffggfffggfffggfffggfffggfffggfffggfffgwwwww~~~~",
        "mmmmFWiiiiiiiiiWfggfffggfffggfffggfffggfffggfffggfffggfwwww~~~~~",
        "mmmmFWiiiiiiiiiWgfffggfffggfffggfffggfffggfffggfffggfffwwww~~~~~",
        "mmmmFWiiiiiiiiiWffggfffggfffggfffggfffggfffggfffggfffggwwww~~~~~",
        "mmmmFWiiCiCiCiiWggfffggfffggfffggfffggfffggfffggfffggffwwww~~~~~",
        "mmmmFWiiiiiiiiiWfffggfffggfffggfffggfffggfffggfffggfffgwwww~~~~~",
        "mmmmFWiiiiiiiiiWfggfffggfffggfffggfffggfffggfffggfffggfwwww~~~~~",
        "mmmmFWWWWWWWWWWWgfffggfffggfffggfffggfffggfffggfffggfffwwww~~~~~",
        "mmmmFFFFFFFffggfffggfffggfffggfffggfffggfffggfffggfffggwwww~~~~~"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {32, 5}, hero = "ChongEr27" },
        { position = {29, 7}, hero = "ZhaoShuai27" },
        { position = {32, 8}, hero = "QiMan40" },
        { position = {35, 7}, hero = "XianZhen27" },
        { position = {10, 8}, hero = "HuMao27" },
        { position = {14, 8}, hero = "HuYan27" },
        { position = {47, 8}, hero = "LuanZhi36" },
        { position = {51, 8}, hero = "XuChen27" }
    }, num_required_selectables = 0, selectables = {} },    rewards = { equipments = {}, money = 7200 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

local kongsang_retreat_positions = {
    {10, 35}, {7, 35}, {12, 35}, {8, 36}, {11, 36}
}

local kongsang_reentry_positions = {
    {24, 34}, {22, 35}, {26, 35}, {23, 36}, {25, 36}
}

local function count_living_kongsang_heroes(game)
    local count = 0
    for _, hero in ipairs(kongsang_heroes) do
        if game:has_unit(hero) then count = count + 1 end
    end
    return count
end

local function begin_kongsang_retreat(game)
    kongsang_phase = true
    for index, hero in ipairs(kongsang_heroes) do
        if not game:has_unit(hero) then
            kongsang_ids[hero] = game:generate_unit(
                hero, 1, Enum.force.enemy, kongsang_reentry_positions[index]
            )
        end
    end
    game:set_unit_invulnerable("ChengDeChen33", true)
    for index, hero in ipairs(kongsang_heroes) do
        game:push_cmd_move(kongsang_ids[hero], kongsang_retreat_positions[index])
    end
    game:push_cmd_speak(kongsang_ids["ChengDeChen33"], "中军已失，诸将随我撤往空桑！尚存者立即退兵，先前负伤者也重新归队护持退路！")
end

local function bring_wei_chou_to_kongsang(game)
    wei_chou_arrived = true
    kongsang_started_turn = game:get_turn_current()
    wei_chou_id = game:generate_unit("WeiChou27", 1, Enum.force.own, {17, 34})
    generate_many(game, "JinGuard39", {{18, 33}, {18, 35}, {17, 36}}, Enum.force.own)
    game:push_cmd_speak(wei_chou_id, "成得臣已近空桑！魏犨奉命在此截住楚军，诸军列阵，不可让子玉冲回大寨！")
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    generate_many(game, "JinGuard39", {{27, 9}, {37, 9}}, Enum.force.own)
    generate_many(game, "JinArcher39", {{24, 11}}, Enum.force.own)

    game:generate_unit("XiaoZiYin40", 1, Enum.force.ally, {11, 12})
    game:generate_unit("BaiYiBing30", 1, Enum.force.ally, {14, 12})
    game:generate_unit("GuoGuiFu40", 1, Enum.force.ally, {49, 12})
    game:generate_unit("CuiYao32", 1, Enum.force.ally, {52, 12})
    game:generate_unit("GongSunGu33", 1, Enum.force.ally, {28, 12})
    generate_many(game, "QinGuard36", {{10, 14}, {12, 14}}, Enum.force.ally)
    generate_many(game, "QiGuard30", {{50, 14}, {52, 14}}, Enum.force.ally)
    generate_many(game, "SongGuard33", {{36, 12}, {40, 12}}, Enum.force.ally)

    kongsang_ids["DouYiShen40"] = game:generate_unit("DouYiShen40", 1, Enum.force.enemy, {8, 26})
    game:generate_unit("ShiGui40", 1, Enum.force.enemy, {10, 28})
    game:generate_unit("BaiChou40", 1, Enum.force.enemy, {14, 28})
    kongsang_ids["DouBo33"] = game:generate_unit("DouBo33", 1, Enum.force.enemy, {50, 26})
    game:generate_unit("YuanXuan40", 1, Enum.force.enemy, {46, 28})
    game:generate_unit("GongZiYin40", 1, Enum.force.enemy, {54, 28})
    kongsang_ids["ChengDeChen33"] = game:generate_unit("ChengDeChen33", 1, Enum.force.enemy, {32, 30})
    kongsang_ids["ChengDaXin40"] = game:generate_unit("ChengDaXin40", 1, Enum.force.enemy, {28, 29})
    kongsang_ids["DouYueJiao40"] = game:generate_unit("DouYueJiao40", 1, Enum.force.enemy, {36, 29})

    generate_many(game, "ChuGuard40", {
        {8, 24}, {12, 24}, {16, 24}, {20, 24}, {24, 24}, {28, 24},
        {32, 24}, {36, 24}, {40, 24}, {44, 24}, {48, 24}, {52, 24}
    }, Enum.force.enemy)
    generate_many(game, "ChuCavalry40", {
        {10, 25}, {14, 25}, {18, 25}, {22, 25}, {26, 25},
        {30, 25}, {34, 25}, {38, 25}, {42, 25}, {46, 25}
    }, Enum.force.enemy)
    generate_many(game, "ChuArcher40", {
        {12, 26}, {20, 26}, {28, 26}, {36, 26}, {44, 26}, {52, 26}
    }, Enum.force.enemy)

    generate_many(game, "ChenGuard40", {{14, 26}, {30, 26}, {46, 26}}, Enum.force.enemy)
    generate_many(game, "CaiGuard40", {{22, 26}, {38, 26}, {54, 26}}, Enum.force.enemy)
    generate_many(game, "ChenCavalry40", {{16, 27}, {32, 27}, {48, 27}}, Enum.force.enemy)
    generate_many(game, "CaiCavalry40", {{24, 27}, {40, 27}}, Enum.force.enemy)
    game:generate_unit("ChenArcher40", 1, Enum.force.enemy, {26, 27})
    game:generate_unit("CaiArcher40", 1, Enum.force.enemy, {42, 27})
    game:set_force_direction(Enum.force.enemy, 3)
end
function on_update(game)
    -- Native save restoration reloads Lua globals. Reconstruct the phase from
    -- battlefield facts before evaluating spawn triggers.
    if not kongsang_phase
       and game:get_num_enemies_alive() <= #kongsang_heroes
       and game:is_unit_within("ChengDeChen33", {10, 35}, 3) then
        kongsang_phase = true
        game:set_unit_invulnerable("ChengDeChen33", true)
    end
    if kongsang_phase and not wei_chou_arrived and game:has_unit("WeiChou27") then
        wei_chou_arrived = true
        kongsang_started_turn = game:get_turn_current()
    end    if not left_flank_spoken and game:is_force_within(Enum.force.own, {12, 23}, 4) then
        left_flank_spoken = true
        game:push_cmd_speak(0, "狐氏上军已逼近楚左师，栾枝的曳柴疑兵开始扬尘诱敌！")
    end
    if not right_flank_spoken and game:is_force_within(Enum.force.own, {50, 23}, 4) then
        right_flank_spoken = true
        game:push_cmd_speak(0, "胥臣部接近陈蔡前队，虎皮战车即将突入敌阵！")
    end
    if not center_spoken and game:is_force_within(Enum.force.own, {32, 23}, 4) then
        center_spoken = true
        game:push_cmd_speak(0, "楚中军尚未动摇，先击破左右两军，不可直接冲击成得臣本阵！")
    end
    if not kongsang_phase
       and game:get_num_enemies_alive() == count_living_kongsang_heroes(game) then
        begin_kongsang_retreat(game)
    end
    if kongsang_phase and not wei_chou_arrived
       and game:is_unit_within("ChengDeChen33", {10, 35}, 3) then
        bring_wei_chou_to_kongsang(game)
    end
    if kongsang_phase and not ceasefire_issued then
        game:set_unit_invulnerable("ChengDeChen33", true)
    end
    if wei_chou_arrived and not ceasefire_issued
       and game:get_turn_current() >= kongsang_started_turn + 5 then
        ceasefire_issued = true
        game:set_unit_invulnerable("ChengDeChen33", false)
        game:push_cmd_speak(0, "主公有令：城濮已胜，以报楚王旧恩，不得再追杀成得臣。魏犨立即止战，让开归路！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if wei_chou_arrived and not game:has_unit("WeiChou27") then return Enum.status.defeat end
    if ceasefire_issued then return Enum.status.victory end
    return Enum.status.undecided
end
