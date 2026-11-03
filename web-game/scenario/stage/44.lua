west_breached = false
south_breached = false
east_breached = false
palace_taken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "MengMingShi26", "XiQiShu26", "BaiYiBing26", "BaoManZi44" }
gevents_enabled = true
gsites = {
    { id = "hua_palace_west", name = "滑国宫城", position = {14, 5}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "hua_palace_center", name = "滑国宫城", position = {16, 5}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "hua_palace_east", name = "滑国宫城", position = {18, 5}, restore_hp = 25, restore_mp = 15, rewards = {} }
}

gstory = {
    chapter = "第四十四回",
    title = "叔詹据鼎抗晋侯 弦高假命犒秦军",
    battle_title = "三更袭滑",
    objective = "孟明视、西乞术、白乙丙分别突破滑国南、西、东三门；三门均告突破后，任一秦军有名将领进入宫城一格范围即胜。十二回合内未夺宫城，或任一我方有名将领被击退则失败。",
    map_asset = "m067.png",
    intro = {
        { speaker = "", text = "秦穆公与郑国私盟退兵，狐偃请率偏师追击。晋文公念及流亡时秦国扶立之恩，又顾念甥舅婚姻，拒绝趁秦军归心追杀，只留下半军继续围郑。" },
        { speaker = "晋文公", text = "若无秦君，寡人不能返国。子玉无礼，寡人尚退避三舍报德，岂能今日反袭秦师？即使秦军尽退，晋国也能独自围郑。" },
        { speaker = "", text = "烛之武建议迎回受宠于晋的公子兰，请晋国议和。石申父携重宝入晋营，晋文公提出两项条件：立公子兰为世子，并交出执政叔詹听罪。" },
        { speaker = "郑文公", text = "立兰为世子可以保社稷；叔詹却是寡人的股肱。晋侯索他入营，分明有意烹杀，孤怎忍心相送？" },
        { speaker = "叔詹", text = "主忧则臣辱，主辱则臣死。若舍一臣能救百姓、安社稷，臣不往才是不忠。请君送臣出城。" },
        { speaker = "", text = "叔詹来到晋营，晋文公命人架起鼎镬。叔詹据住鼎耳，从料事为智、尽心为忠、临难为勇、杀身为仁四端自陈，反问晋国是否真要烹杀仁智忠勇俱全之臣。" },
        { speaker = "叔詹", text = "臣曾预言晋公子归国必霸，也劝郑君终身事晋。今日自请就死以救一城。自今以后，天下事君者都以叔詹为戒罢！" },
        { speaker = "晋文公", text = "寡人只是试子，子真烈士。撤去鼎镬，厚礼相待；召公子兰回来，以世子礼送入郑城，晋军就此解围。" },
        { speaker = "", text = "公子兰被立为世子后，秦晋嫌隙渐深。魏犨旧伤复发而死，狐毛、狐偃也相继去世；胥臣举荐郤缺，晋文公不以其父郤芮之罪废其才，又扩三军为五军。" },
        { speaker = "郤缺", text = "臣不过冀野农夫，君侯不以先父之罪加戮，已经是宽宥。若蒙任用，愿以敬慎报国。" },
        { speaker = "", text = "楚成王畏惧晋国军政完备，派斗章求和。郑文公去世，公子兰即位为郑穆公；不久晋文公也病逝，世子继位为晋襄公。出殡时棺柩如牛鸣，郭偃卜得西方将有秦兵来犯。" },
        { speaker = "先轸", text = "西方来鼠，越我垣墙，一击三伤，所指必是秦国。先君棺柩有声，是在警告我们提防秦师。" },
        { speaker = "", text = "驻守郑国北门的杞子、逢孙、杨孙因郑国重新服晋而不满，密报秦穆公，称自己掌握北门钥匙，可作内应灭郑。秦穆公不听蹇叔、百里奚反复劝阻，命孟明视、西乞术、白乙丙率三千精兵、三百乘车秘密东进。" },
        { speaker = "蹇叔", text = "千里劳师，郑国一旦闻讯必有准备；所得只是俘获，失去的却是信、仁、智。此行郑不足虑，可虑者晋，崤山险阻尤其不可不防。" },
        { speaker = "秦穆公", text = "晋文公已死，郑国新君立足未稳，天下还有谁能阻秦？兵贵神速，老臣不必再以迂阔之言阻挠。" },
        { speaker = "", text = "秦军经过周都北门，只免胄而不卷甲束兵，三百乘争相超车。少年王孙满断言其轻而无礼，必将自取败辱。郑国商人弦高在黎阳津得知秦军来意，立即遣人飞报郑国，自己带二十头肥牛迎向秦军。" },
        { speaker = "弦高", text = "寡君早知三位将军远行辛劳，特命下臣远迎犒师。郑国处强国之间，日夜警备，不敢有一刻安寝，请诸位体谅。" },
        { speaker = "孟明视", text = "郑君既已知道我军出发日期，偷袭再无可能。强攻城坚，久围又无后援；附近滑国毫无准备，转取滑城，至少不使大军空手回秦。" },
        { speaker = "西乞术", text = "三更时分兵分三路。末将取西门，白乙取东门，主帅与褒蛮子夺南门；三门同时发难，不给滑军合围机会。" },
        { speaker = "白乙丙", text = "父亲密简所忧本是晋国，我们却先攻无备的滑国。既然主帅决意进兵，只能速战速决，天亮前撤出城池。" },
        { speaker = "滑君", text = "秦军不是东行援郑的吗，怎么突然围住滑城？快闭三门，集中弓手守住内街，宫中车马随时准备向翟地撤离！" },
        { speaker = "军令", text = "连续城墙不可跨越。西乞术突破西门，孟明视突破南门，白乙丙突破东门；三路都进入城内后，再由任一有名将领接近宫城。滑君不可击杀，生命归零会原地恢复。" }
    },
    events = {
        { id = "west_gate", trigger = "approach", position = {6, 9}, radius = 1, speaker = "西乞术", text = "西门守军仓促列阵。甲士先夺两格门道，弓手随后压住内街。" },
        { id = "south_gate", trigger = "approach", position = {15, 15}, radius = 1, speaker = "孟明视", text = "南门是中军主攻方向。褒蛮子随我冲门，不许守军闭合门道！" },
        { id = "east_gate", trigger = "approach", position = {25, 9}, radius = 1, speaker = "白乙丙", text = "东门已经接战。这里城墙连续，只能从两格门道正面突破。" },
        { id = "palace", trigger = "approach", position = {16, 5}, radius = 2, speaker = "滑君", text = "三门尽失，秦军已经逼近宫城。备车北走，立即逃往翟地！" }
    },
    victory = {
        { speaker = "", text = "秦军三路同时进入滑城，宫城防线迅速瓦解。滑君乘夜向北逃往翟地，滑国自此不能复国。" },
        { speaker = "孟明视", text = "郑国虽未得，滑城已经攻破。收拢诸军与缴获，天明即向西撤退，不要在此等待晋国援兵。" },
        { speaker = "", text = "秦军在滑城掳取子女玉帛，随后西归。滑地失去国君，后来被卫国吞并；弦高假命犒军虽救郑国，却使毫无准备的滑国承受灭国之祸。" },
        { speaker = "", text = "郑穆公收到弦高密报后查探北门客馆，果然发现杞子等人厉兵秣马、只等秦军献门。烛之武带束帛登门，含蓄点破密谋。" },
        { speaker = "烛之武", text = "诸位久戍郑国，郑国供给已经困乏。听闻将军整顿车马，想必有归意；孟明正在周、滑之间，何不前去会合？" },
        { speaker = "", text = "杞子知道谋泄，逃往齐国；逢孙、杨孙逃往宋国。北门秦卒失去主帅一度聚众，佚之狐发给行粮、分批引导回乡，没有再起战斗。" },
        { speaker = "军令", text = "第44回完成，获得5200金币。三帅仍将面对蹇叔预言中的崤山险阻。" }
    },
    defeat = {
        { speaker = "", text = "东方渐白，滑军已经从三门互相增援。秦军失去夜袭先机，只得放弃滑城向西撤退。" }
    }
}

gstage = {
    title_id = "NightRaidOnHua44", turn_limit = 12,
    map = { blocked_edges = {}, size = {32, 24}, terrain = {
        "mmfffFgFffffFgFfffgFfFffggFfFfgg",
        "FfFfggfFfFggffFfFgfffFgFffffFmmf",
        "ffmgFfWWWWWWWWWWWWWWWWWWWWggffFf",
        "mgffffWiiiiiiiiiiiiiiiiiiWffffgm",
        "ffffggWiiiiiiiiiiiiiiiiiiWffgmff",
        "fmmgffWiiiiiiiCiCiCiiiiiiWggffff",
        "ggffffWiiiiiiiiiiiiiiiiiiWffffmm",
        "ffffggWiiiiiiiiiiiiiiiiiiWffggff",
        "mmggffWiiiiiiiiiiiiiiiiiiWggffff",
        "ggffffGiiiiiiiiiiiiiiiiiiGfffmmg",
        "ffmfggGiiiiiiiiiiiiiiiiiiGffggff",
        "mfggffWiiiiiiiiiiiiiiiiiiWggfffm",
        "ggffffWiiiiiiiiiiiiiiiiiiWfffmgg",
        "fmmfggWiiiiiiiiiiiiiiiiiiWffggff",
        "ffggffWiiiiiiiiiiiiiiiiiiWggffmm",
        "ggffffWWWWWWWWWGGWWWWWWWWWffffgg",
        "mmffggffffggffffggffffggffffggff",
        "ffggffffggffffggffffggffffggfmmf",
        "ggmfffggffffggffffggffffggffffgg",
        "mfffggffffggffffggffffggffffggfm",
        "ffggffffggffffggffffggffffggfmff",
        "FmmffFgFffffFgFfffgFfFffggFfFfgg",
        "FfFfggfFfFggffFfFgfffFgFffffFgmm",
        "ffFgFfffgFfFffggFfFfggfFfFggffFf"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {15, 21}, hero = "MengMingShi26" },
        { position = {4, 18}, hero = "XiQiShu26" },
        { position = {27, 18}, hero = "BaiYiBing26" },
        { position = {14, 20}, hero = "BaoManZi44" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 5200 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("QinGuard44", 1, Enum.force.own, {5, 19})
    game:generate_unit("QinArcher44", 1, Enum.force.own, {3, 19})
    game:generate_unit("QinGuard44", 1, Enum.force.own, {16, 20})
    game:generate_unit("QinArcher44", 1, Enum.force.own, {17, 21})
    game:generate_unit("QinGuard44", 1, Enum.force.own, {26, 19})
    game:generate_unit("QinArcher44", 1, Enum.force.own, {28, 19})
    game:generate_unit("HuaGong44", 1, Enum.force.enemy, {16, 5})
    game:set_unit_invulnerable("HuaGong44", true)
    for _, p in ipairs({{6,9},{6,10},{25,9},{25,10},{15,15},{16,15},{11,11},{21,11}}) do
        game:generate_unit("HuaGuard44", 1, Enum.force.enemy, p)
    end
    for _, p in ipairs({{9,8},{23,8},{13,7},{19,7}}) do
        game:generate_unit("HuaArcher44", 1, Enum.force.enemy, p)
    end
end

function named_qin_near_palace(game)
    return game:is_unit_within("MengMingShi26", {16, 5}, 1)
        or game:is_unit_within("XiQiShu26", {16, 5}, 1)
        or game:is_unit_within("BaiYiBing26", {16, 5}, 1)
        or game:is_unit_within("BaoManZi44", {16, 5}, 1)
end

function on_update(game)
    if not west_breached and game:is_unit_within("XiQiShu26", {8, 9}, 2) then
        west_breached = true
        game:push_cmd_speak(0, "西乞术已经越过西门，西路秦军进入滑城。")
    end
    if not south_breached and game:is_unit_within("MengMingShi26", {15, 13}, 2) then
        south_breached = true
        game:push_cmd_speak(0, "孟明视已经突破南门，中军沿南北大街向宫城推进。")
    end
    if not east_breached and game:is_unit_within("BaiYiBing26", {23, 9}, 2) then
        east_breached = true
        game:push_cmd_speak(0, "白乙丙已经越过东门，东路秦军进入滑城。")
    end
    if west_breached and south_breached and east_breached and named_qin_near_palace(game) then
        palace_taken = true
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if palace_taken then return Enum.status.victory end
    return Enum.status.undecided
end
