escape_spoken = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhouXiangWang29", "JianShiFu38", "ZuoYanFu38" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "wangcheng_palace", name = "王城宫城", position = {11, 4}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wangcheng_store", name = "王城宝物库", position = {6, 6}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "wangcheng_gate_left", name = "王城南门", position = {10, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wangcheng_gate_center", name = "王城南门", position = {11, 9}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wangcheng_gate_right", name = "王城南门", position = {12, 9}, restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第三十八回·上",
    title = "周襄王避乱居郑 晋文公守信降原",
    battle_title = "王城突围",
    objective = "护送周襄王到达东南出口（21,14）。周襄王、简师父、左鄢父任一被击退即失败；富辰与王师友军在南门坚守牵制。",
    map_asset = "m061.png",
    intro = {
        { speaker = "", text = "周襄王听小东告发太叔带与隗后的私情，持剑奔向中宫，却想到太叔武艺高强，又怕在不明罪状时杀弟招致不孝之名。" },
        { speaker = "周襄王", text = "先查清实据，再废隗后、逐太叔。若此刻仓促动剑，反会让逆臣借口生乱。" },
        { speaker = "", text = "太叔带得知小东已经告发，连夜逃出宫门。次日宫人对质招认，襄王把隗后贬入冷宫。" },
        { speaker = "", text = "颓叔、桃子担心当初借翟伐郑、迎立隗后之事牵连自己，追上太叔带，一同逃往翟国。" },
        { speaker = "颓叔", text = "只要对翟君说周王忘恩辱后，再请五千兵拥立太叔，王城便可一举夺取。" },
        { speaker = "", text = "翟君信以为真，派大将赤丁率步骑五千，赤风子为先锋，奉太叔带伐周。" },
        { speaker = "", text = "周使谭伯前往军中说明太叔内乱之罪，却被赤丁杀害。翟军随即直逼王城。" },
        { speaker = "", text = "原伯贯、毛卫率王师车阵出城。赤风子诈败，将原伯贯引入翠云山伏击，原伯贯被擒。" },
        { speaker = "", text = "当夜翟军劈开车营锁链，以芦苇纵火。毛卫突围时被太叔带刺死，王师大败，王城陷入重围。" },
        { speaker = "周襄王", text = "朕早不听富辰之谏，借翟攻郑又娶翟女，今日果然自取其祸。" },
        { speaker = "周公孔", text = "百官家属尚能聚为一军，可以背城决战，不应轻弃社稷。" },
        { speaker = "富辰", text = "翟兵方锐，王应暂时出巡。郑、卫、陈之中，郑国最适合奉迎天子。" },
        { speaker = "周襄王", text = "朕曾借翟兵伐郑，郑国难道不会怨恨吗？" },
        { speaker = "富辰", text = "郑国正想证明自己仍尊王室。大王此时入郑，他们必以奉迎天子洗去旧怨。" },
        { speaker = "简师父", text = "臣随王前往郑境，再从氾地告难于秦晋。只要勤王书送出，太叔不能长久。" },
        { speaker = "左鄢父", text = "东南道路尚未完全封锁。王驾一出南门，沿大道向东，不可恋战。" },
        { speaker = "富辰", text = "臣率子弟亲党数百人从南门直冲翟营，牵住赤丁主力。大王趁乱离城！" },
        { speaker = "", text = "富辰尽召子弟亲党，说明忠义，列阵于南门。翟骑已经越过城外大道。" },
        { speaker = "赤丁", text = "周王已经无兵可用！堵住东南道路，擒住襄王便可迎太叔入城。" },
        { speaker = "军令", text = "城墙不可跨越，南门三格可通行并补给。周襄王必须到达东南出口；富辰是坚守友军，不计入我方阵亡失败条件。" }
    },
    events = {
        { id = "south_gate_breakout", trigger = "approach", position = {11, 9}, radius = 2, speaker = "富辰", text = "臣等向正南突击吸住翟军，大王从门外转向东南，不要停留！" },
        { id = "escape_road", trigger = "approach", position = {19, 13}, radius = 2, speaker = "简师父", text = "前方已是通往郑境的大路。再走两格便可脱离翟军追击！" }
    },
    victory = {
        { speaker = "", text = "富辰率族人与翟军反复冲杀，为襄王争得出城时间。襄王与简师父、左鄢父终于沿东南大道脱离王城。" },
        { speaker = "", text = "富辰身负重伤仍拒绝投降，力战而死；随他出战的子弟亲党三百余人也大多阵亡。" },
        { speaker = "", text = "太叔带进入王城，释放隗后并自立为王，却因国人不服而移居温城，把王城政务留给周公、召公。" },
        { speaker = "", text = "襄王抵达郑国氾地竹川，借宿农民封氏草堂。封氏兄弟同耕共食、奉养后母，使襄王感慨自己反受母弟之害。" },
        { speaker = "周襄王", text = "农家兄弟尚能和睦，朕贵为天子却被亲弟逐出王城，实在有愧。" },
        { speaker = "左鄢父", text = "周公也曾遭遇骨肉之变。大王不必自伤，应立即把王难告知诸侯。" },
        { speaker = "", text = "襄王亲自写下告难书，分送齐、宋、陈、郑、卫，又命简师父告晋、左鄢父告秦。" },
        { speaker = "", text = "郑文公听说襄王驻跸氾地，立即修建馆舍、亲自供应器具饮食。鲁、宋等国也遣使问安。" },
        { speaker = "", text = "简师父来到晋国。狐偃劝晋文公纳王讨逆，以尊王之义开启霸业。" },
        { speaker = "狐偃", text = "若晋国迟疑，秦国必会迎回天子，勤王大义便归于秦。主公应立即整军。" },
        { speaker = "", text = "郭偃占得大吉之兆。晋文公分左右二军：赵衰、魏犨统左军，郤溱、颠颉统右军，狐偃、栾枝居中策应。" },
        { speaker = "", text = "秦穆公也率兵抵达河上。晋文公派胥臣说明晋军已有成算，请秦军不必远涉。" },
        { speaker = "秦穆公", text = "晋侯新立，正需勤王之功安定国内。既然晋军已有准备，寡人愿让此功于晋。" },
        { speaker = "", text = "晋军进屯阳樊：左军前往氾地迎接襄王，右军直指太叔带所在的温城。" },
        { speaker = "军令", text = "王城突围完成，获得4200金币。下一战转入温原合并地图：先讨伐温城，再自动播放三日降原剧情。" }
    },
    defeat = {
        { speaker = "", text = "周襄王未能穿过翟军封锁，勤王书无法送出，王室复位失去机会。" }
    }
}

gstage = {
    title_id = "WangchengEscape38", turn_limit = 14,
    map = { blocked_edges = {}, size = {23, 16}, terrain = {
        "mmffffffggffffffggfffmm",
        "mmffWWWWWWWWWWWWWWWffmm",
        "mmffWiiiiiiiiiiiiiWfgmm",
        "mmggWiiiiiiiiiiiiiWgfmm",
        "mmffWihiiiiCiiiihiWffmm",
        "mmffWiiiiiiiiiiiiiWffmm",
        "mmffWibiiiiiiiiiiiWfgmm",
        "mmggWiiiiiiiiiiiiiWgfmm",
        "mmffWiiiiiiiiiiiiiWffmm",
        "mmffWWWWWWGGGWWWWWWffmm",
        "mmffggffffffggffffffgmm",
        "FFggffffffggffffffggfFF",
        "FFffffffggffffffggfffFF",
        "FFffffggffffffggfffffFF",
        "FFffggffffffggffffffgFF",
        "FFggffffffggffffffggfFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {11, 4}, hero = "ZhouXiangWang29" },
        { position = {10, 5}, hero = "JianShiFu38" },
        { position = {12, 5}, hero = "ZuoYanFu38" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 4200 }
}

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("FuChen38", 1, Enum.force.ally, {11, 9})
    game:generate_unit("RoyalGuard29", 1, Enum.force.ally, {10, 8})
    game:generate_unit("RoyalGuard29", 1, Enum.force.ally, {12, 8})
    game:generate_unit("RoyalArcher29", 1, Enum.force.ally, {9, 8})
    game:generate_unit("RoyalArcher29", 1, Enum.force.ally, {13, 8})
    game:generate_unit("ChiDing38", 1, Enum.force.enemy, {11, 12})
    game:generate_unit("ChiFengZi38", 1, Enum.force.enemy, {14, 12})
    game:generate_unit("DiGuard38", 1, Enum.force.enemy, {9, 11})
    game:generate_unit("DiGuard38", 1, Enum.force.enemy, {11, 11})
    game:generate_unit("DiGuard38", 1, Enum.force.enemy, {13, 11})
    game:generate_unit("DiCavalry38", 1, Enum.force.enemy, {7, 12})
    game:generate_unit("DiCavalry38", 1, Enum.force.enemy, {16, 13})
    game:generate_unit("DiArcher38", 1, Enum.force.enemy, {8, 13})
    game:generate_unit("DiArcher38", 1, Enum.force.enemy, {14, 13})
end

function on_update(game)
    if not escape_spoken and game:is_unit_within("ZhouXiangWang29", {19, 13}, 2) then
        escape_spoken = true
        game:push_cmd_speak(0, "郑境已近！护送周襄王继续前往东南出口，不必回头恋战。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:is_unit_within("ZhouXiangWang29", {21, 14}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
