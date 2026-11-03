gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong18", "GuanYiWu18", "WangZiChengFu18", "HuErBan21", "XiPeng21" }
gduel_enabled = true
gduels = {
    {
        attacker = "WangZiChengFu18", defender = "DaLiHe21", exp = 60, outcome = "capture",
        attacker_speech = "答里呵，北门正是仲父留给你的生路，也是擒你的罗网。下马受缚！",
        defender_speech = "齐军明明都在南、西、东三门，北门外怎会还有伏兵？",
        result_speech = "王子成父截断北门退路，生擒孤竹国主答里呵。",
        text = "王子成父依管仲部署伏于北门，待答里呵出城后将其生擒。"
    }
}
fire_started = false

gsites = {
    { id = "wudi_castle", name = "无棣城府", position = {9, 3}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wudi_north_gate", name = "无棣北门", position = {9, 1}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wudi_west_gate", name = "无棣西门", position = {2, 6}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wudi_east_gate", name = "无棣东门", position = {16, 6}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wudi_south_gate", name = "无棣南门", position = {9, 10}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wudi_west_storehouse", name = "无棣西库", position = {6, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "wudi_east_storehouse", name = "无棣东库", position = {13, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "wudi_south_camp", name = "齐军南营", position = {4, 12}, restore_hp = 20, restore_mp = 15, rewards = {} }
}

gstory = {
    chapter = "第二十一回·三",
    title = "管夷吾智辨俞儿 齐桓公兵定孤竹",
    battle_title = "无棣夜破",
    objective = "走出迷谷后围攻无棣城，配合城内举火，击杀黄花并生擒答里呵",
    map_asset = "m036.png",
    intro = {
        { speaker = "", text = "齐军追入旱海，风沙蔽月，方向尽失。军马中恶倒地，各队只能敲金击鼓互相召集。" },
        { speaker = "齐桓公", text = "四面都是白沙惨雾，来路已经辨不清。黄花果然是诈降诱敌！" },
        { speaker = "管夷吾", text = "臣听闻无终、山戎之马多来自漠北。可挑数匹老马纵在前方，随其所往寻找出谷道路。" },
        { speaker = "虎儿斑", text = "无终军中确有久走北地的老马。解开缰绳，让它们自己认路。" },
        { speaker = "", text = "老马委曲前行，终于带大军走出迷谷。齐军又与失散的公孙隰朋会合，立即回师无棣。" },
        { speaker = "", text = "沿途百姓正扶老携幼返回城中。管夷吾让虎儿斑挑选心腹，扮作百姓混入无棣，约定半夜举火。" },
        { speaker = "管夷吾", text = "竖貂攻南门，连挚攻西门，开方攻东门，只把北门空出来。王子成父与隰朋伏在北门外。" },
        { speaker = "王子成父", text = "敌军见三门受攻，必从北门突围。我就在北路等答里呵自投罗网。" },
        { speaker = "虎儿斑", text = "末将先带十余勇士混进城里。火起后直奔南门，砍开门闩接应主力。" },
        { speaker = "答里呵", text = "黄花说齐军已困死在旱海，为何他们又回到无棣？快命军民登城守望！" },
        { speaker = "兀律古", text = "百姓刚刚返城，门户混杂。应先搜捕奸细，再坚守四门，等待齐军粮尽。" },
        { speaker = "黄花", text = "臣诱敌虽未尽功，仍可守住南门。高黑已被我斩杀，今日再以齐军首级祭他！" },
        { speaker = "齐桓公", text = "高黑不屈而死，此仇必须讨还。但入城后不得滥杀百姓，只诛首恶。" },
        { speaker = "管夷吾", text = "不要挤在一门。三路佯攻牵制守军，等城内火起再同时压上，北门仍旧留空。" },
        { speaker = "公孙隰朋", text = "夜风转北，火势会向城中扩散。内应只点数处信火，不可焚毁民居。" },
        { speaker = "军令", text = "城墙不可跨越，四座城门可通行。第三回合或我军接近南门时触发城内举火；王子成父与答里呵相邻可触发生擒。" }
    },
    victory = {
        { speaker = "虎儿斑", text = "城内信火已起！南门门闩砍断，齐军可以入城了！" },
        { speaker = "黄花", text = "内外夹攻，南门已经守不住。护送国主从北门突围，我来断后！" },
        { speaker = "", text = "黄花在乱军中死战，力尽被杀。兀律古也死于城内混战，答里呵则奔向北门。" },
        { speaker = "王子成父", text = "北门伏兵合围，答里呵已经被擒。孤竹军放下兵器者，一概免死。" },
        { speaker = "齐桓公", text = "答里呵助山戎侵燕，又设迷谷毒计，罪不可赦。明正其罪，以警北方诸戎。" },
        { speaker = "", text = "齐桓公安抚无棣百姓，又命记录高黑不屈被害的忠节，准备回国后加以抚恤。" },
        { speaker = "燕庄公", text = "齐侯千里救燕，又平令支、孤竹，燕国宗社得保。新得土地，请由齐侯处置。" },
        { speaker = "齐桓公", text = "北陲若再立异族，日后仍会叛乱。令支、孤竹五百里之地都归燕国，使燕永为周室北藩。" },
        { speaker = "管夷吾", text = "无终出兵有功，可把小泉山下之田赐给无终，令各部知道助诸夏者必得厚报。" },
        { speaker = "虎儿斑", text = "无终得田，皆赖齐侯信义。往后北地若有警急，无终仍愿为齐国前驱。" },
        { speaker = "", text = "齐军休整五日后原路返回。鲍叔牙在葵兹关迎接，沿途粮运从未断绝。" },
        { speaker = "", text = "燕庄公送齐桓公越境五十余里。齐桓公为不失诸侯之礼，又把所经过的土地割给燕国。" },
        { speaker = "齐桓公", text = "北伐所得不归齐国一寸。寡人所求，是诸夏安定、贡道复通，而非乘危夺地。" },
        { speaker = "", text = "诸侯闻齐桓公救燕而不贪其地，无不畏齐之威、感齐之德，齐国霸业由此更盛。" },
        { speaker = "下回预告", text = "第二十二回：鲁国庆父接连作乱，季友两度扶立新君，并在郦地迎击索赂的莒军。" }
    },
    defeat = {
        { speaker = "管夷吾", text = "内应尚未打开城门，三路兵马却已失去呼应。先撤回十里外营寨，不能重蹈迷谷之险。" },
        { speaker = "", text = "齐军夜攻无棣失利，孤竹北患未能平定。" }
    }
}

gstage = {
    title_id = "WudiNightSiege21", turn_limit = 22,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "fffffffffffffffffff",
            "ffWWWWWWWGWWWWWWWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiibiiCiiibiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffGiiiiiiiiiiiiiGff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWiiiiiiiiiiiiiWff",
            "ffWWWWWWWGWWWWWWWff",
            "fffffffffffffffffff",
            "ffffefffffffeffffff",
            "fffffffffffffffffff"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 12}, hero = "QiHuanGong18" },
            { position = {6, 12}, hero = "GuanYiWu18" },
            { position = {9, 12}, hero = "WangZiChengFu18" },
            { position = {12, 12}, hero = "HuErBan21" },
            { position = {14, 12}, hero = "XiPeng21" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1800 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong18", 1)
    game:appoint_hero("GuanYiWu18", 1)
    game:appoint_hero("WangZiChengFu18", 1)
    game:appoint_hero("HuErBan21", 1)
    game:appoint_hero("XiPeng21", 1)
end

function on_begin(game)
    game:generate_unit("QiGuard21", 1, Enum.force.own, {7, 13})
    game:generate_unit("QiArcher21", 1, Enum.force.own, {11, 13})
    game:generate_unit("DaLiHe21", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("HuangHua21", 1, Enum.force.enemy, {9, 8})
    game:generate_unit("WuLvGu21", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {8, 9})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {10, 9})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {3, 6})
    game:generate_unit("GuzhuGuard21", 1, Enum.force.enemy, {15, 6})
    game:generate_unit("GuzhuArcher21", 1, Enum.force.enemy, {6, 5})
    game:generate_unit("GuzhuArcher21", 1, Enum.force.enemy, {12, 5})
end

function on_update(game)
    if not fire_started and game:has_unit("WuZhongWarrior21") then fire_started = true end
    if fire_started then return end
    if game:get_turn_current() < 3 and not game:is_force_within(Enum.force.own, {9, 10}, 2) then return end
    fire_started = true
    local infiltrator = game:generate_unit("WuZhongWarrior21", 1, Enum.force.own, {7, 9})
    game:generate_unit("WuZhongWarrior21", 1, Enum.force.own, {11, 9})
    game:generate_unit("WuZhongWarrior21", 1, Enum.force.own, {9, 7})
    game:push_cmd_speak(infiltrator, "城内信火已经点起！无终勇士立即夺门，接应齐军入城！")
    game:push_cmd_speak(3, "南门内应发动。正面各军同时推进，北门伏兵继续隐蔽！")
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if fire_started and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
