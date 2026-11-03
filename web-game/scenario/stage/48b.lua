sortie_started = false
rescue_started = false
rescue_turn = 0
qin_retreat = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoDun47", "XunLinFu47", "XiQue45", "YuPian48", "LuanDun45", "XuJia48", "ZhaoChuan48", "HanJue48" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "qin_northwest", name = "秦军行营", position = {11,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_northeast", name = "秦军行营", position = {18,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_command", name = "秦军中军帐", position = {14,15}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "qin_southwest", name = "秦军行营", position = {11,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_southeast", name = "秦军行营", position = {18,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_northwest", name = "晋军行营", position = {42,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_northeast", name = "晋军行营", position = {49,10}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_command", name = "晋军中军帐", position = {46,15}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "jin_southwest", name = "晋军行营", position = {42,21}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "jin_southeast", name = "晋军行营", position = {49,21}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十八回·下",
    title = "刺先克五将乱晋 召士会寿馀绐秦",
    battle_title = "河曲之战",
    objective = "坚守晋营，令赵穿从东营出击至河曲中央，引出秦军后由任一晋军具名将领与他相邻完成接应；赵穿返回晋营中军七格范围并坚持三个回合，秦军即于夜间撤退。秦康公、西乞术、白乙丙、士会依原著均不可阵亡。我方任一具名将领被击退则失败。",
    map_asset = "m076.png",
    intro = {
        { speaker = "", text = "令狐之败五年后，秦康公仍以晋军夜袭、公子雍被杀为耻，亲率大军渡河，攻取晋国羁马。" },
        { speaker = "秦康公", text = "晋人背盟袭营，又害公子雍。今日进至河曲，正要让赵盾偿还令狐旧债。" },
        { speaker = "赵盾", text = "秦师远来，锋锐正盛。荀林父将中军，郤缺佐之；臾骈将上军，栾盾佐之；胥甲将下军，赵穿佐之。" },
        { speaker = "", text = "晋军列阵时，赵盾的车右擅自驰入队列。韩厥依军法将他斩首，然后向主帅请罪。" },
        { speaker = "韩厥", text = "军令不避贵近。主帅车右乱阵，臣已按法处置；若有罪，请连臣一并治罪。" },
        { speaker = "赵盾", text = "执法不阿，正是军中所需。车右虽亲近，坏阵便当死；韩厥无罪，反当记功。" },
        { speaker = "臾骈", text = "秦军渡河而来，求战心切。我军深沟高垒，不与争锋，待其粮尽气衰再动。" },
        { speaker = "赵盾", text = "就依臾骈之计。各军守营，不得擅出；秦人挑战辱骂，也只当没有听见。" },
        { speaker = "士会", text = "晋军众将多能守令，唯赵穿勇而少谋，受不得激。集中兵力挑战下军，他必定出阵。" },
        { speaker = "秦康公", text = "若能引赵穿离营，再围而歼之，晋军必来救援。那时由局部交锋撕开全阵。" },
        { speaker = "赵穿", text = "秦人在营外日夜辱骂，我身为下军之佐，岂能躲在围栏后面看他们逞威！" },
        { speaker = "胥甲", text = "主帅已有坚壁之令。你若孤军深入，秦军左右一合，我下军也会被拖出营去。" },
        { speaker = "赵穿", text = "畏敌才会失去军心。我只领本部冲到河曲中央，击退挑战者便回，不必诸军相助。" },
        { speaker = "荀林父", text = "赵穿若真出营，不能坐视他被围。中、上两军随时准备开门接应，但不可追入秦营。" },
        { speaker = "郤缺", text = "救人而不乱阵才是关键。接到赵穿后立刻退回东营，以营门和弓弩挡住秦军。" },
        { speaker = "军令", text = "东西两座大营的围栏均不可跨越，四座营门各为两格通道。赵穿到达河曲中央才算出战；友军与他相邻后，护送他返回东营中军附近。" }
    },
    events = {
        { id = "zhao_chuan_sortie", trigger = "approach", position = {30,15}, radius = 2, speaker = "赵穿", text = "秦军休得猖狂！赵穿已经出营，来与我在河曲决一胜负！" },
        { id = "jin_rescue", trigger = "adjacent", speaker = "荀林父", text = "诸军已经接应赵穿，边战边退，回到晋营后坚守三回合！" }
    },
    victory = {
        { speaker = "", text = "赵穿擅自出战，晋国三军被迫出营接应。双方鏖战至暮，各有损伤，仍未分胜负。" },
        { speaker = "秦康公", text = "晋人不肯决战，明日再遣使下书。若他们仍避战，便从河曲渡口逼近其垒。" },
        { speaker = "臾骈", text = "秦使辞强而神色不定，说明他们也怕久驻。今夜可在河岸设伏，待秦军半渡而击。" },
        { speaker = "", text = "赵穿、胥甲不满臾骈得计，暗中把半渡邀击的谋划泄露给秦军。秦康公当夜拔营，晋军追之不及。" },
        { speaker = "赵盾", text = "泄漏军谋使秦师得脱，胥甲难逃军法。河曲虽未大败，却错过了结束秦患的机会。" },
        { speaker = "", text = "又过五年，赵盾思念留秦的士会，召集六卿商议迎回之法。魏寿馀自请诈降秦国。" },
        { speaker = "寿馀", text = "臣佯称与魏邑争讼、叛晋归秦，再献魏地。秦君若要辨认城邑，必会派熟知晋事的士会同行。" },
        { speaker = "韩厥", text = "寿馀逃出国境，我照约捕其妻子，使秦国相信他确已反晋。戏必须做足，才瞒得过士会。" },
        { speaker = "", text = "寿馀入秦献魏，秦康公果然命士会前往受地。绕朝看破其中有诈，把马鞭赠给士会送行。" },
        { speaker = "绕朝", text = "使事若成，晋国得一良臣，秦国失一智士。此鞭赠你，过河以后，莫忘今日故人。" },
        { speaker = "士会", text = "君命与故国都不可轻负。既已走到河边，前路如何，只能由我自己承担。" },
        { speaker = "", text = "寿馀与士会登舟渡河，晋国接应之军已在东岸等候。秦晋数年的离合，至此又翻开新局。" },
        { speaker = "军令", text = "河曲之战完成，获得6800金币。秦、晋具名将领均按原著保留；士会归晋作为后续剧情承接。" }
    },
    defeat = {
        { speaker = "", text = "晋军具名将领在接应途中被击退，三军阵势崩散。河曲坚壁之策宣告失败。" }
    }
}

gstage = {
    title_id = "BattleOfHequ48", turn_limit = 28,
    map = { blocked_edges = {}, size = {54, 32}, terrain = {
        "~~~~~wwwmfFFggfFFfggFFffmFFfffFFmffFFgffFFggfFFfmgFFff",
        "~~~~~wwwFFggfFFfggFFfmgFFfffFFfffFFgfmFFggfFFmggFFffgF",
        "~~~~~wwwggmFFfggFFmfgFFfffFFfffFFgmfFFggfFFfggFFffmFFf",
        "~~~~~wwwffffggfmffggfffmggffffgmffffggfmffggfffmggffff",
        "~~~~~wwwffggmfffggffmfggffffmgffffggmfffggffmfggffffFF",
        "~~~~~wwwgmffffggfmffggfffmggffffgmffffggfmffggfffmgFff",
        "~~~~~wwwPPPPPPPPPPPPPPffggffffggffffggfPPPPPPPPPPPPPPF",
        "~~~~~wwwPfggffffggfffPggffffggffffggfffPggffffggfffFPg",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffmfggPf",
        "~~~~~wwwPfffggffffggfPffggffffggffffggfPffggffffggffPF",
        "~~~~~wwwPfggefffgefffPggffffggffffggfffPggfeffggefmFPg",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffffggPF",
        "~~~~~wwwPfffggffffggfPffggffffggffffggfPffggffffggfFPf",
        "~~~~~wwwPfggffffggfffPggffffggffffggfffPggffffggfmffPg",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffffggPF",
        "~~~~~wwwffffggefffggffffggffffggffffggffffggffefggfFff",
        "~~~~~wwwffggffffggffffggffffggffffggffffggffffggmfffgF",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffffgFPm",
        "~~~~~wwwPfffggffffggfPffggffffggffffggfPffggffffggmfPf",
        "~~~~~wwwPfggffffggfffPggffffggffffggfffPggffffggffffPF",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffffgFPf",
        "~~~~~wwwPfffegfffeggfPffggffffggffffggfPffgeffffemffPF",
        "~~~~~wwwPfggffffggfffPggffffggffffggfffPggffffggfffFPg",
        "~~~~~wwwPgffffggffffgPffffggffffggffffgPffffggffffgmPf",
        "~~~~~wwwPfffggffffggfPffggffffggffffggfPffggffffmgffPF",
        "~~~~~wwwPPPPPPPPPPPPPPggffffggffffggfffPPPPPPPPPPPPPPm",
        "~~~~~wwwggmfffggffmfggffffmgffffggmfffggffmfggffffmgfF",
        "~~~~~wwwffffggfmffggfffmggffffgmffffggfmffggfffmggfFFf",
        "~~~~~wwwffggmfffggffmfggffffmgffffggmfffggffmfggffffmg",
        "~~~~~wwwFmffFFggfFFfggFFfmgFFfffFFfffFFgfmFFggfFFmggFF",
        "~~~~~wwwffFFggmFFfggFFmfgFFfffFFfffFFgmfFFggfFFfggFFff",
        "~~~~~wwwFFgmfFFfggFFffgFFffmFFfffFFmffFFggfFFfggFFfmgF",
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {46,15}, hero = "ZhaoDun47" },
        { position = {43,10}, hero = "XunLinFu47" },
        { position = {48,10}, hero = "XiQue45" },
        { position = {43,21}, hero = "YuPian48" },
        { position = {48,21}, hero = "LuanDun45" },
        { position = {45,18}, hero = "XuJia48" },
        { position = {39,15}, hero = "ZhaoChuan48" },
        { position = {50,15}, hero = "HanJue48" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6800 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("QinKangGong48", 1, Enum.force.enemy, {14,15})
    game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {12,10})
    game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {17,10})
    game:generate_unit("ShiHui47", 1, Enum.force.enemy, {17,21})
    for _, hero in ipairs({"QinKangGong48", "XiQiShu26", "BaiYiBing26", "ShiHui47"}) do
        game:set_unit_invulnerable(hero, true)
    end
    generate_many(game, "QinGuard48", {{10,8},{14,8},{18,8},{10,13},{18,13},{10,18},{18,18},{10,23},{14,23},{18,23}}, Enum.force.enemy)
    generate_many(game, "QinCavalry48", {{12,9},{16,9},{11,15},{17,15},{12,22},{16,22}}, Enum.force.enemy)
    generate_many(game, "QinArcher48", {{9,11},{19,11},{9,20},{19,20},{20,14},{20,17}}, Enum.force.enemy)
    generate_many(game, "JinGuard48", {{41,8},{45,8},{49,8},{41,12},{49,12},{41,19},{49,19},{41,23},{45,23},{49,23}}, Enum.force.own)
    generate_many(game, "JinCavalry48", {{43,9},{47,9},{42,14},{48,14},{43,22},{47,22}}, Enum.force.own)
    generate_many(game, "JinArcher48", {{40,10},{50,10},{40,21},{50,21},{40,14},{40,17}}, Enum.force.own)
end

local function jin_has_reached_zhao(game)
    for _, hero in ipairs({"ZhaoDun47", "XunLinFu47", "XiQue45", "YuPian48", "LuanDun45", "XuJia48", "HanJue48"}) do
        if game:are_units_within(hero, "ZhaoChuan48", 1) then return true end
    end
    return false
end

function on_update(game)
    if not sortie_started and game:is_unit_within("ZhaoChuan48", {30,15}, 2) then
        sortie_started = true
        game:push_cmd_speak(0, "赵穿不听坚壁军令，已经冲到河曲中央。秦军两翼合拢，晋国三军必须出营接应。")
        generate_many(game, "QinCavalry48", {{24,12},{24,19},{27,14},{27,17}}, Enum.force.enemy)
        generate_many(game, "QinArcher48", {{22,10},{22,21},{25,15}}, Enum.force.enemy)
    end
    if sortie_started and not rescue_started and jin_has_reached_zhao(game) then
        rescue_started = true
        rescue_turn = game:get_turn_current()
        game:push_cmd_speak(0, "晋军已经接到赵穿！不要追入秦营，护送他退回东侧晋营，依托营门再守三回合。")
    end
    if rescue_started and not qin_retreat and game:get_turn_current() >= rescue_turn + 3
        and game:is_unit_within("ZhaoChuan48", {46,15}, 7) then
        qin_retreat = true
        game:push_cmd_speak(0, "秦军察觉晋军准备在河岸设伏，连夜拔营西撤。河曲之战就此结束。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if qin_retreat then return Enum.status.victory end
    return Enum.status.undecided
end
