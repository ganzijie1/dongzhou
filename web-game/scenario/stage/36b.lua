relief_arrived = false
palace_spoken = false
lv_spoken = false
xi_spoken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "HuMao27", "ZhaoShuai27", "WeiChou27", "LuanZhi36" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "jiang_palace", name = "绛宫城池", position = {10, 4}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "jiang_left_store", name = "西侧宝物库", position = {3, 4}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "jiang_right_store", name = "东侧宝物库", position = {17, 4}, restore_hp = 15, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } },
    { id = "jiang_gate_left", name = "绛宫南门", position = {9, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "jiang_gate_center", name = "绛宫南门", position = {10, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "jiang_gate_right", name = "绛宫南门", position = {11, 9}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第三十六回·下",
    title = "晋吕郤夜焚公宫 秦穆公再平晋乱",
    battle_title = "绛宫火变",
    objective = "击退吕省、郤芮，平定宫火。狐毛、赵衰、魏犨、栾枝任一被击退即失败；第3回合晋国族兵从两侧赶到。",
    map_asset = "m060.png",
    intro = {
        { speaker = "", text = "晋文公即位后按功行赏，又宽赦旧怨。吕省、郤芮却自知反复无常，日夜担心被追究。" },
        { speaker = "吕省", text = "狐偃、赵衰等人尽居要职，朝廷再无我等立足之地。与其坐待受刑，不如先下手。" },
        { speaker = "郤芮", text = "勃鞮曾两次追杀重耳，与他仇怨最深。约他同谋，夜焚公宫，事情必成。" },
        { speaker = "", text = "二人找到勃鞮，约定纵火之夜内外夹击。勃鞮表面答应，转身便求见晋文公。" },
        { speaker = "", text = "晋文公想到勃鞮曾斩断自己的衣袖，又曾奉惠公之命追至狄境，起初拒绝相见。" },
        { speaker = "勃鞮", text = "齐桓公不记斩带钩之仇而用管仲，方能称霸。臣昔日各为其主，今日却是为新君告急。" },
        { speaker = "晋文公", text = "他说得有理。若仍拘泥旧怨，如何收拢晋国人心？传勃鞮入见。" },
        { speaker = "", text = "勃鞮说明吕省、郤芮的纵火计划。文公听从狐偃安排，秘密离宫，渡河暂避秦国。" },
        { speaker = "狐偃", text = "主公先离开绛都，臣随行护卫。狐毛、赵衰、魏犨与栾枝留下联络诸族，火起即救宫平乱。" },
        { speaker = "", text = "当夜，吕省、郤芮伏兵四起，火把飞入宫垣。宫门、廊庑同时燃烧，烈焰映红绛都。" },
        { speaker = "吕省", text = "四面封住宫门！重耳若冲出火场，立即格杀；若不出来，就让他葬身火海！" },
        { speaker = "郤芮", text = "先占南门，不许城中族兵接近。弓手守住两翼，近兵随我攻入宫内。" },
        { speaker = "赵衰", text = "主公已经离宫，贼军尚不知情。我们先保护宫城补给点，再从正门截断叛军。" },
        { speaker = "魏犨", text = "火势虽大，真正的宫墙仍不可跨越。正南三格门道能通行，莫被两侧假缺口诱开。" },
        { speaker = "栾枝", text = "栾、郤等族并非人人从逆。我已发出急报，只要撑到第三回合，两侧援军便会赶来。" },
        { speaker = "狐毛", text = "吕省、郤芮必须击退，其余胁从尽量招降。平乱之后还要保存晋国元气。" },
        { speaker = "", text = "宫内火光持续燃烧，但城池、宝物库与南门补给格仍可恢复体力。结构地形均按矩阵判定。" },
        { speaker = "军令", text = "击退吕省、郤芮。第3回合左右两侧各有晋国族兵增援；四名我方有名将领任一被击退即失败。" }
    },
    events = {
        { id = "palace_fire", trigger = "approach", position = {10, 4}, radius = 4, speaker = "赵衰", text = "宫中无人回应，说明主公已安全离开。诸军专心截断叛军退路！" },
        { id = "lv_retreats", trigger = "defeated", unit = "LvSheng36", speaker = "吕省", text = "重耳竟不在宫中！今夜之谋已经泄露，快向河岸撤退！" },
        { id = "xi_retreats", trigger = "defeated", unit = "XiRui36", speaker = "郤芮", text = "各族援兵都到了，再战无益。先逃出绛都，再图后计！" }
    },
    victory = {
        { speaker = "", text = "吕省、郤芮见晋国诸族兵马赶来，纵火之谋又未能伤到文公，只得各自逃离绛都。" },
        { speaker = "赵衰", text = "宫火已经控制，百姓与库藏损失不大。二贼虽逃，却再无军队可用。" },
        { speaker = "", text = "晋文公从秦国传来命令，不急于公开搜捕，而让勃鞮继续与吕省、郤芮联络。" },
        { speaker = "勃鞮", text = "二贼如今走投无路，只要假称秦国愿意相助，他们一定会到王城投奔。" },
        { speaker = "", text = "勃鞮见到吕省、郤芮，谎称晋文公已死在宫火中，秦穆公准备另立晋君，请二人赴王城商议。" },
        { speaker = "吕省", text = "若秦君肯立新君，我们仍有拥立之功。晋国群臣即使不服，也不能违抗秦师。" },
        { speaker = "郤芮", text = "只怕勃鞮有诈。但绛都已无容身之处，唯有借秦国翻盘。" },
        { speaker = "", text = "二人来到王城，被引入馆舍。秦穆公设宴相待，屏风后却早已坐着晋文公。" },
        { speaker = "秦穆公", text = "你们说晋侯死于宫火，寡人却有一位故人，正想当面听听二位如何解释。" },
        { speaker = "晋文公", text = "寡人赦免旧罪，你们反而焚烧公宫、扰乱百姓。今日还有何言？" },
        { speaker = "", text = "屏风撤去，吕省、郤芮面无人色。秦兵将二人拿下，依谋逆之罪在王城伏诛。" },
        { speaker = "秦穆公", text = "晋国两度生乱，皆因君臣相疑、刑赏失当。贤婿回国之后，当以此为戒。" },
        { speaker = "晋文公", text = "蒙秦君再平晋乱。寡人将修明政事、整顿军旅，不负诸侯与晋人的期望。" },
        { speaker = "", text = "吕、郤之乱平定，晋文公的君位自此稳固。流亡旧臣与国内诸族也逐渐合为一体。" },
        { speaker = "军令", text = "绛宫火变平定，获得4800金币。第36回结束；以下进入第37回完整过场，本回不设置战斗关卡。" },
        { speaker = "", text = "第三十七回　介子推守志焚绵上　太叔带怙宠入宫中" },
        { speaker = "", text = "晋文公追恨吕省、郤芮，原想尽诛其党。赵衰劝他改惠公、怀公严刻之政，以宽大安定人心，文公于是颁行大赦。" },
        { speaker = "", text = "吕郤余党人数众多，虽见赦令仍疑惧不安，国内流言并未立即停止。" },
        { speaker = "", text = "一日清晨，小吏头须叩宫门求见。文公想起他当年盗取库藏，使自己流亡途中缺乏行资，命守门人拒绝。" },
        { speaker = "头须", text = "主公能容纳两度追杀自己的勃鞮，因而免去焚宫之难，今日为何独不能容我？臣有安定晋国的办法。" },
        { speaker = "晋文公", text = "勃鞮尚且可以各为其主，头须之罪又何必永记？方才是寡人的过失，立即召他进来。" },
        { speaker = "头须", text = "臣盗取主公财物，国人尽知。主公若巡城时仍以臣驾车，吕郤余党见连我都被宽恕，自然相信赦令并非虚言。" },
        { speaker = "", text = "晋文公依计巡城，命头须御车。众人见状，都说盗库之人尚且复用，其他人更无须担忧，流言从此平息。" },
        { speaker = "", text = "头须又禀告，文公早年留在蒲城的一子一女并未死于兵乱，多年来一直由他托付遂氏抚养。" },
        { speaker = "晋文公", text = "寡人一直以为他们早遭兵刃。若非你今日说明，我几乎要背负不慈之名！" },
        { speaker = "", text = "文公厚赏遂氏，迎回儿女，立儿子驩为太子，将女儿伯姬嫁给赵衰，称为赵姬，并仍让头须掌管库藏。" },
        { speaker = "", text = "翟君送季隗归晋，齐孝公也送齐姜回国。怀嬴敬佩二人的贤德，主动请求让出夫人之位。" },
        { speaker = "", text = "宫中重新排序，以齐姜为夫人，季隗次之，怀嬴再次。三人不以先后争宠，文公内宫由此安定。" },
        { speaker = "赵姬", text = "叔隗先嫁赵氏，又有赵盾这样的贤子。若因我后来受宠便弃旧迎新，岂不是把不贤之名留给我？" },
        { speaker = "赵衰", text = "主公把女儿赐给我，我若再迎叔隗，恐怕有负君恩。" },
        { speaker = "赵姬", text = "长幼先后不可颠倒。请迎叔隗母子回国，立叔隗为正室、赵盾为嫡子；我居偏房才合礼法。" },
        { speaker = "", text = "晋文公赞叹女儿贤德，命人迎回叔隗与赵盾。十七岁的赵盾通诗书、精射御，赵衰尤其器重。" },
        { speaker = "", text = "安顿家室之后，晋文公大会群臣，按从亡、送款、迎降分为三等，再依德、才、功劳高下授予封赏。" },
        { speaker = "", text = "赵衰、狐偃列从亡首功；狐毛、胥臣、魏犨、狐射姑、先轸、颠颉依次受赏。栾枝、郤溱等国内响应者也各得封赐。" },
        { speaker = "壶叔", text = "臣从蒲城起便侍奉左右，奔走四方，足踵俱裂。如今封赏从亡诸臣，为何没有臣的名字？" },
        { speaker = "晋文公", text = "导我以仁义者受上赏，辅我谋议而不辱诸侯者次之，冒锋镝护卫者又次之。奔走劳苦也会受赏，只是次序未到。" },
        { speaker = "", text = "壶叔惭愧退下。文公随后遍赏车夫、仆隶，人人感悦；魏犨、颠颉却因武功排在文臣之后而略有怨言。" },
        { speaker = "", text = "只有介子推没有出席。他见狐偃渡河时提及功劳，认为众臣争称己功是贪取天意，便托病在家，织履奉母。" },
        { speaker = "介子推母", text = "你随君十九年，又曾割股救他。如今国门有诏，遗漏功劳者可以自言，何不入朝求一份俸禄？" },
        { speaker = "介子推", text = "惠公、怀公失德，天命归于主公。诸臣却争说是自己的功劳，我正以此为耻，宁可终身织履。" },
        { speaker = "介子推母", text = "你既愿作廉士，我也愿作廉士之母。我们离开市井，到绵上深山隐居，不再搅入功名之争。" },
        { speaker = "", text = "介子推背着母亲进入绵山，结庐深谷。邻人解张知道内情，担心他的功绩埋没，夜里在朝门悬书讽谏。" },
        { speaker = "", text = "书中以龙蛇为喻：重耳如龙失所，群臣如蛇相随；饥饿时一蛇割股，龙归深渊后众蛇有穴，唯独割股之蛇流落荒野。" },
        { speaker = "晋文公", text = "这是说介子推！寡人流亡卫国时无食，正是他割股相救。遍赏群臣却独忘了他，过错全在寡人。" },
        { speaker = "解张", text = "悬书是臣代写的。子推并无求赏之心，已经背母隐入绵上深谷，请主公亲自寻找。" },
        { speaker = "", text = "晋文公任命解张为下大夫，立即以他为前导来到绵山。山中峰峦重叠、林木深密，数日寻访仍不见踪迹。" },
        { speaker = "绵山农夫", text = "数日前有人看见一名男子背着老妇，在山脚汲水歇息，随后又背母上山，至今不知去了哪里。" },
        { speaker = "晋文公", text = "子推极孝。若从山前山后举火逼近，他必定背母出来；只须控制火路，不可伤人。" },
        { speaker = "魏犨", text = "从亡诸臣人人有功，子推却隐居使君侯久候。待他避火出来，臣定要当面羞他。" },
        { speaker = "", text = "军士环山放火，恰遇风势猛烈，延烧数里，三日方息。介子推始终没有出山。" },
        { speaker = "", text = "众人在一株枯柳下找到介子推母子的遗骨。二人相抱而亡，没有留下求赏或怨恨之言。" },
        { speaker = "晋文公", text = "寡人本想表彰忠臣，反因躁急害死子推母子。改绵山为介山，环山之田作为祠田，永志寡人之过。" },
        { speaker = "", text = "晋人思念介子推，不忍在他焚身之日举火，逐渐形成清明前禁火冷食的寒食习俗。" },
        { speaker = "", text = "文公此后更谨慎治国，举善任能、省刑薄敛、通商礼宾、救济贫弱，晋国很快安定强盛。" },
        { speaker = "", text = "周襄王派太宰周公孔和内使叔兴赐予晋文公侯伯之命。叔兴回朝断言晋侯必将成为诸侯霸主。" },
        { speaker = "", text = "与此同时，郑文公因滑国亲卫而不亲郑，命公子士泄、堵俞弥出兵伐滑。滑国一度求和，郑军退后却仍旧依附卫国。" },
        { speaker = "", text = "卫文公向周室求援。周襄王派游孙伯、伯服赴郑调解，郑文公却把两名王臣拘在边境，等攻破滑国才肯释放。" },
        { speaker = "周襄王", text = "郑国屡次轻慢王命，如今竟敢拘押天子使臣，朕一定要问罪！谁能替王室讨伐郑国？" },
        { speaker = "富辰", text = "郑虽无道，终究是周室同姓。翟人并非我族，借异族之力攻打宗亲，只见其害，未见其利。" },
        { speaker = "颓叔", text = "郑国依仗楚国，王师单独出兵未必能胜。翟人尚未失礼，借其兵诛逆正可重振王威。" },
        { speaker = "", text = "襄王听从颓叔、桃子，命二人向翟国借兵。翟军假称出猎，突然进入郑境，攻破栎城并派兵驻守。" },
        { speaker = "", text = "襄王认为翟国有功，又逢中宫新丧，便想迎娶翟君之女后叔隗，以婚姻巩固关系。" },
        { speaker = "富辰", text = "酬劳翟国可以，天子却不应因一时之功立翟女为后。翟人兼恃军功与姻亲，日后必有窥伺王室之心。" },
        { speaker = "", text = "周襄王没有听从，迎后叔隗入宫，令她主持中宫。隗后自幼驰马射猎，进入深宫后十分不适。" },
        { speaker = "隗后", text = "妾在翟国常随父亲出猎，如今久居宫中，四肢都要僵了。请大王举行大狩，让妾也看看周人的骑射。" },
        { speaker = "", text = "襄王为取悦隗后，在北邙山大集车徒，规定以猎获数量赏车。王子王孙与将士竞相驰射。" },
        { speaker = "", text = "襄王庶弟太叔带猎获超过三十只，夺得头筹。隗后见他仪表出众、骑射娴熟，屡次向襄王称赞。" },
        { speaker = "隗后", text = "天色尚早，妾也想亲自驰射一围。请大王选善骑的同姓宗室保护妾下场。" },
        { speaker = "太叔带", text = "臣愿随行护卫王后。" },
        { speaker = "", text = "隗后与太叔带并马绕过山腰，彼此夸赞骑术。隗后暗示太叔次日到太后宫中问安，两人就此私下约定。" },
        { speaker = "", text = "次日太叔带入宫，在惠后侧室与隗后私会。宫人受了贿赂，又畏惧太叔权势，无人敢向襄王告发。" },
        { speaker = "", text = "太叔带出入渐渐肆无忌惮，甚至连夜留在宫中。把守宫门的内侍都猜测襄王之后或将由太叔继位，更不敢阻拦。" },
        { speaker = "", text = "宫婢小东善于音律。一夜酒宴，太叔令她吹箫，醉后又想强行亲近。小东惧怕隗后，挣脱衣服逃走。" },
        { speaker = "小东", text = "大王救命！太叔带此刻仍在中宫，他与隗后早已私通，方才又拔剑追杀奴婢！" },
        { speaker = "周襄王", text = "太叔带欺朕至此！取剑来，朕亲自到中宫问个明白！" },
        { speaker = "", text = "襄王持剑直奔中宫，太叔带的性命与周室下一场大乱，就留待第38回继续。" }
    },
    defeat = {
        { speaker = "", text = "救火诸将被叛军击溃，宫城与百姓陷入更大混乱，晋文公无法安全返回绛都。" }
    }
}

gstage = {
    title_id = "JiangPalaceFire36", turn_limit = 12,
    map = { blocked_edges = {}, size = {21, 15}, terrain = {
        "mmFFFFFFFFFFFFFFFFFmm",
        "FgiiiiiiiiiiiiiiiiigF",
        "FgiiiWWWWWWWWWWWiiigF",
        "FgiiiWiiiiiiiiiWiiigF",
        "FgibiWiiiiCiiiiWibigF",
        "FgiiiWihiiiiihiWiiigF",
        "FgiiiWiiiiiiiiiWiiigF",
        "FgiiiWihiiiiihiWiiigF",
        "FgiiiWiiiiiiiiiWiiigF",
        "FgiiiWWWWGGGWWWWiiigF",
        "FgiiiiiiiiiiiiiiiiigF",
        "FgiiiiiiiiiiiiiiiiigF",
        "FgiiiiiiiiiiiiiiiiigF",
        "FgiiiiiiiiiiiiiiiiigF",
        "mmFFFFFFFFFFFFFFFFFmm"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {8, 13}, hero = "HuMao27" },
        { position = {9, 13}, hero = "ZhaoShuai27" },
        { position = {10, 13}, hero = "WeiChou27" },
        { position = {11, 13}, hero = "LuanZhi36" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4800 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("JinGuard29", 1, Enum.force.own, {8, 12})
    game:generate_unit("JinArcher29", 1, Enum.force.own, {11, 12})
    game:generate_unit("LvSheng36", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("XiRui36", 1, Enum.force.enemy, {11, 6})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {9, 9})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {11, 9})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {8, 8})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {12, 8})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {8, 10})
    game:generate_unit("RebelGuard36", 1, Enum.force.enemy, {12, 10})
    game:generate_unit("RebelArcher36", 1, Enum.force.enemy, {7, 8})
    game:generate_unit("RebelArcher36", 1, Enum.force.enemy, {13, 8})
end

function on_update(game)
    if game:has_unit("JinClanGuard36") and game:get_turn_current() >= 3 then
        relief_arrived = true
    end
    if not relief_arrived and game:get_turn_current() >= 3 then
        relief_arrived = true
        local relief_id = game:generate_unit("JinClanGuard36", 1, Enum.force.own, {1, 7})
        game:generate_unit("JinClanArcher36", 1, Enum.force.own, {19, 7})
        game:generate_unit("JinClanGuard36", 1, Enum.force.own, {1, 8})
        game:generate_unit("JinClanArcher36", 1, Enum.force.own, {19, 8})
        game:push_cmd_speak(relief_id, "栾氏、郤氏忠于晋侯的族兵已经赶到！从两翼夹击纵火叛军！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("LvSheng36") and not game:has_unit("XiRui36") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
