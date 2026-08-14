wen_cleared = false
yuan_phase_start_turn = -1
yuan_second_day_spoken = false
yuan_third_day_spoken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChongEr27", "ZhaoShuai27", "WeiChou27", "XiZhen38", "LuanZhi36" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "WeiChou27", defender = "TaiShuDai38", exp = 100, outcome = "kill",
        attacker_speech = "逆贼太叔带，还想夺门逃往翟国吗！",
        defender_speech = "放孤出城，异日必有厚报！",
        result_speech = "魏犨跃上太叔车乘，一刀将太叔带斩杀。",
        text = "原著明载太叔带仗剑夺门，被魏犨追及并一刀斩之。"
    }
}
gsites = {
    { id = "wen_castle", name = "温城城池", position = {6, 4}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wen_store", name = "温城宝物库", position = {3, 6}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "wen_gate_left", name = "温城南门", position = {5, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wen_gate_center", name = "温城南门", position = {6, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wen_gate_right", name = "温城南门", position = {7, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "yuan_castle", name = "原城城池", position = {20, 4}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "yuan_store", name = "原城宝物库", position = {17, 6}, restore_hp = 15, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第三十八回·下",
    title = "周襄王避乱居郑 晋文公守信降原",
    battle_title = "温原勤王",
    objective = "全灭温城敌军后，晋军自动移至原城南侧；原城守军闭门不出。围城三回合，原城守军被击退后会在城内补回；约期届满自动撤围。",
    map_asset = "m062.png",
    intro = {
        { speaker = "", text = "晋文公接受勤王之请，命赵衰、魏犨统左军迎接襄王，郤溱、颠颉统右军围攻温城，自己与狐偃、栾枝居中策应。" },
        { speaker = "", text = "秦穆公本已率军到河上，见晋军决意独任勤王，便让出功业，派公子絷问劳襄王后班师。" },
        { speaker = "", text = "赵衰顺利把周襄王从氾地迎回王城。周公、召公开门奉迎，天子重新临朝。" },
        { speaker = "", text = "温城百姓听说襄王复位，群起攻杀颓叔、桃子，打开南门迎接晋军。" },
        { speaker = "郤溱", text = "温人已经归顺，太叔带只剩宫中亲兵。诸军不得扰民，只取首恶。" },
        { speaker = "", text = "太叔带携隗后登车，企图夺门逃往翟国。守门军士关闭外门，不肯放行。" },
        { speaker = "太叔带", text = "孤已在温城为王，挡路者死！只要冲出南门，翟国仍有五千援兵。" },
        { speaker = "隗后", text = "晋军已经进城，不能再迟疑。太叔快杀开道路！" },
        { speaker = "魏犨", text = "温城南门已经畅通，太叔就在城池附近。若与他相邻，我会按原著触发单挑斩杀。" },
        { speaker = "晋文公", text = "太叔逐兄乱周，罪在不赦；但温城军民已开门归顺，不可滥杀。" },
        { speaker = "赵衰", text = "左侧温城三格门道可以通行。右侧原城已有原伯贯守军，关闭城门；温城平定后才进入围原阶段。" },
        { speaker = "", text = "原伯贯退守原城，担心晋军夺邑，闭门安抚百姓。原城守军不出战，也不会跨图支援温城。" },
        { speaker = "栾枝", text = "先把温城首恶解决。原城之事要靠主公守信取民心，不可提前攻击。" },
        { speaker = "郤溱", text = "两城之间道路开阔，但右城门按连续城墙处理，不可通行。那里只是后续剧情场景。" },
        { speaker = "", text = "太叔亲兵依托温城城池、民居和宝物库负隅顽抗，弓手列于内街两翼。" },
        { speaker = "太叔带", text = "魏犨不过晋国匹夫，谁敢阻我出城！" },
        { speaker = "魏犨", text = "等我追到车前，看你还能往哪里逃。" },
        { speaker = "军令", text = "全灭温城敌军后，晋军主力自动移至原城南侧。原城守军闭门不出且会持续补员；围原三回合后依约撤兵。" }
    },
    events = {
        { id = "wen_gate", trigger = "approach", position = {6, 9}, radius = 2, speaker = "温城百姓", text = "南门已经为晋军打开！请只诛太叔与隗后，不要伤害城中百姓。" },
        { id = "taishu_falls", trigger = "defeated", unit = "TaiShuDai38", speaker = "隗后", text = "太叔已死，翟军也不在城中，我还能逃到哪里？" },
        { id = "weihou_falls", trigger = "defeated", unit = "WeiHou38", speaker = "晋军", text = "温城首恶已除！停止追击普通守卒，准备向天子报捷。" }
    },
    victory = {
        { speaker = "", text = "太叔带仗剑夺门，被魏犨追上车乘，一刀斩杀。隗后随后被晋军弓手围住，中箭身亡。" },
        { speaker = "郤溱", text = "本应把二人送交天子明正典刑，如今既已伏诛，只能据实奏报。" },
        { speaker = "", text = "晋军把二人葬于神农涧旁，安抚温城百姓，向阳樊中军报捷。" },
        { speaker = "", text = "晋文公亲至王城朝见襄王。襄王设酒犒赏，又赐金帛，文公辞谢不受。" },
        { speaker = "晋文公", text = "臣不敢受私赐，只愿死后得用天子隧葬之礼。" },
        { speaker = "周襄王", text = "先王礼制不可因私劳更改。叔父勤王大功，朕另以温、原、阳樊、攒茅四邑增封。" },
        { speaker = "", text = "王城百姓争相观看晋侯，感叹齐桓公仿佛重新出现。晋文公随后派诸将分别接收四邑。" },
        { speaker = "", text = "阳樊守臣苍葛不愿王畿百姓受晋兵威胁，率民登城。魏犨听其陈词，没有强攻，飞报文公。" },
        { speaker = "晋文公", text = "四邑是天子所赐，寡人不敢拒命；愿归周者可以迁走，愿留者归晋，绝不强迫。" },
        { speaker = "", text = "苍葛让百姓自行选择，愿归周者大半迁往轵村。魏犨和平接收阳樊疆界。" },
        { speaker = "", text = "随后晋文公与赵衰来到右侧原城。原伯贯谎称晋军已经屠戮阳樊百姓，原人因此闭门誓守。" },
        { speaker = "赵衰", text = "原人不服，是因为不信晋国。主公若能示信，不必攻城也能使他们归附。" },
        { speaker = "晋文公", text = "全军只带三日粮。三日不能使原城归服，立即解围退兵，绝不多留一日。" },
        { speaker = "", text = "原城关闭城门，守军始终没有出击；晋军也依令围而不攻。双方相持到第三日。" },
        { speaker = "", text = "第三日夜半，原民缒城来报：他们已查明阳樊百姓并未被杀，约定次日晚间开门献城。" },
        { speaker = "晋军司粮", text = "原民明晚就会献门，只需多留一天便能得城；粮食也可从阳樊补充。" },
        { speaker = "晋文公", text = "信是国家的宝物，也是百姓所依。约定三日，今日已满；为得一城而失信，百姓今后凭什么相信寡人？" },
        { speaker = "", text = "天明，晋文公真的解除原城之围。原城百姓见他宁可失城也不失信，纷纷在城楼竖起降旗。" },
        { speaker = "", text = "原民缒城追赶晋军，原伯贯无法阻止，只得开城出降。晋军行出三十里后收到降书。" },
        { speaker = "", text = "晋文公停住车马，单车进入原城。百姓夹道庆贺，原伯贯也被保留王朝卿士之礼，迁居河北。" },
        { speaker = "晋文公", text = "寡人以信得原，也要用可信之人守原。任赵衰为原大夫，兼领阳樊；郤溱守温，兼领攒茅。" },
        { speaker = "", text = "晋文公纳王示义、降原示信，自此奠定称霸诸侯的根基。" },
        { speaker = "军令", text = "第38回完成，获得6000金币。温城为实际战斗；原城守军闭城不出击，围原三回合后自动撤围并触发追降剧情。" }
    },
    defeat = {
        { speaker = "", text = "晋军主将受创，太叔带趁乱逃出温城，勤王之功未能完成。" }
    }
}

gstage = {
    title_id = "WenYuanCampaign38", turn_limit = 30,
    map = { blocked_edges = {}, size = {27, 17}, terrain = {
        "mffffgfffgffffgfffgffffgffm",
        "mWWWWWWWWWWWfgfWWWWWWWWWWWm",
        "mWiiiiiiiiiWfgfWiiiiiiiiiWm",
        "mWiiiiiiiiiWgffWiiiiiiiiiWm",
        "mWihiiCiihiWgffWihiiCiihiWm",
        "mWiiiiiiiiiWfffWiiiiiiiiiWm",
        "mWibiiiiiiiWfffWibiiiiiiiWm",
        "mWiiiiiiiiiWfffWiiiiiiiiiWm",
        "mWiiiiiiiiiWffgWiiiiiiiiiWm",
        "mWWWWGGGWWWWffgWWWWWWWWWWWm",
        "mfffgffffgfffgffffgfffgfffm",
        "mFffgfffgffffgfffgffffgffFm",
        "mFfgffffgfffgffffgfffgfffFm",
        "mFfgfffgffffgfffgffffgfffFm",
        "mFgffffgfffgffffgfffgffffFm",
        "mFgfffgffffgfffgffffgfffgFm",
        "mFffffgfffgffffgfffgffffgFm"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {7, 14}, hero = "ChongEr27" },
        { position = {8, 14}, hero = "ZhaoShuai27" },
        { position = {6, 14}, hero = "WeiChou27" },
        { position = {7, 15}, hero = "XiZhen38" },
        { position = {9, 15}, hero = "LuanZhi36" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6000 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("JinGuard38", 1, Enum.force.own, {5, 13})
    game:generate_unit("JinGuard38", 1, Enum.force.own, {9, 13})
    game:generate_unit("JinArcher38", 1, Enum.force.own, {6, 13})
    game:generate_unit("JinArcher38", 1, Enum.force.own, {8, 13})
    game:generate_unit("TaiShuDai38", 1, Enum.force.enemy, {6, 4})
    game:generate_unit("WeiHou38", 1, Enum.force.enemy, {4, 4})
    game:generate_unit("WenRebelGuard38", 1, Enum.force.enemy, {5, 9})
    game:generate_unit("WenRebelGuard38", 1, Enum.force.enemy, {6, 9})
    game:generate_unit("WenRebelGuard38", 1, Enum.force.enemy, {7, 9})
    game:generate_unit("WenRebelGuard38", 1, Enum.force.enemy, {5, 6})
    game:generate_unit("WenRebelGuard38", 1, Enum.force.enemy, {7, 6})
    game:generate_unit("WenRebelArcher38", 1, Enum.force.enemy, {3, 7})
    game:generate_unit("WenRebelArcher38", 1, Enum.force.enemy, {9, 7})
    game:generate_unit("YuanBoGuan38", 1, Enum.force.enemy, {20, 4})
    game:generate_unit("YuanGuard38", 1, Enum.force.enemy, {18, 5})
    game:generate_unit("YuanGuard38", 1, Enum.force.enemy, {22, 5})
    game:generate_unit("YuanGuard38", 1, Enum.force.enemy, {19, 8})
    game:generate_unit("YuanGuard38", 1, Enum.force.enemy, {21, 8})
    game:generate_unit("YuanArcher38", 1, Enum.force.enemy, {17, 7})
    game:generate_unit("YuanArcher38", 1, Enum.force.enemy, {23, 7})
end

function wen_enemies_alive(game)
    return game:has_unit("TaiShuDai38")
        or game:has_unit("WeiHou38")
        or game:has_unit("WenRebelGuard38")
        or game:has_unit("WenRebelArcher38")
end

local yuan_guard_origins = {{18, 5}, {22, 5}, {19, 8}, {21, 8}}
local yuan_archer_origins = {{17, 7}, {23, 7}}

local function spawn_yuan_defender_near(game, hero, origin)
    for radius = 0, 8 do
        for dx = -radius, radius do
            local dy = radius - math.abs(dx)
            for _, signed_dy in ipairs(dy == 0 and {0} or {-dy, dy}) do
                local x, y = origin[1] + dx, origin[2] + signed_dy
                if x >= 16 and x <= 24 and y >= 2 and y <= 8 then
                    local position = {x, y}
                    if game:is_cell_vacant(position) then
                        game:generate_unit(hero, 1, Enum.force.enemy, position)
                        return true
                    end
                end
            end
        end
    end
    return false
end

local function fill_yuan_defenders(game, hero, target, origins)
    local missing = target - game:get_num_units_alive(hero)
    for _, origin in ipairs(origins) do
        if missing <= 0 then return end
        if spawn_yuan_defender_near(game, hero, origin) then missing = missing - 1 end
    end
end

function replenish_yuan_defenders(game)
    if not game:has_unit("YuanBoGuan38") then
        spawn_yuan_defender_near(game, "YuanBoGuan38", {20, 4})
    end
    fill_yuan_defenders(game, "YuanGuard38", 4, yuan_guard_origins)
    fill_yuan_defenders(game, "YuanArcher38", 2, yuan_archer_origins)
end

function move_jin_main_force_to_yuan(game)
    local positions = {
        {17, 11}, {19, 11}, {20, 12}, {21, 11}, {23, 11},
        {18, 12}, {22, 12}, {19, 13}, {21, 13}
    }
    for index, position in ipairs(positions) do
        game:push_cmd_move(index - 1, position)
    end
end

function on_update(game)
    replenish_yuan_defenders(game)
    if not wen_cleared and not wen_enemies_alive(game) then
        wen_cleared = true
        move_jin_main_force_to_yuan(game)
        yuan_phase_start_turn = game:get_turn_current()
        game:push_cmd_speak(0, "温城敌军已全部肃清！晋军主力自动移至原城南侧，三日围原自本回合开始；原城守军闭门不出，并会持续补员。")
    elseif wen_cleared and not yuan_second_day_spoken
       and game:get_turn_current() >= yuan_phase_start_turn + 1 then
        yuan_second_day_spoken = true
        game:push_cmd_speak(0, "围原第二日：原城守军仍不出击，晋军维持包围，不得破城滥杀。")
    elseif wen_cleared and not yuan_third_day_spoken
       and game:get_turn_current() >= yuan_phase_start_turn + 2 then
        yuan_third_day_spoken = true
        game:push_cmd_speak(0, "围原第三日：原人尚未开门。各军整队，约期一满便依令撤围。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not wen_cleared then return Enum.status.undecided end
    if game:get_turn_current() >= yuan_phase_start_turn + 3 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
