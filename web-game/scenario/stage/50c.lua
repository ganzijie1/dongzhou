dog_defeated = false
ti_fallen = false
ling_zhe_arrived = false

gally_hold_position = true
gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoDun47" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十回·下",
    title = "东门遂援立子倭 赵宣子桃园强谏",
    battle_title = "桃园脱险",
    objective = "护送赵盾从桃园宫墙西门突围并到达西侧出口（1,13）。灵獒必须先被击退；提弥明按原著留下断后并阵亡，之后灵辄出现接应。赵盾被击退则失败，晋灵公与屠岸贾不可被击退。",
    map_asset = "m080.png",
    intro = {
        { speaker = "", text = "晋灵公成年后荒淫暴虐，重税营建，在绛州城内修桃园与绛霄楼，宠任善于逢迎的屠岸贾。" },
        { speaker = "晋灵公", text = "弹鸟有什么意思？今日与屠卿各执弹弓，以园外百姓为目标，中眼者胜！" },
        { speaker = "", text = "弹丸如雨落入人群，百姓有人破头、伤眼、落齿。晋灵公在高台俯视奔逃惨状，反而大笑。" },
        { speaker = "", text = "晋灵公又豢养一头赤色猛犬灵獒，由獒奴牵随左右，稍有过失便纵犬咬人。" },
        { speaker = "", text = "一次晋灵公嫌熊掌没有煮熟，以铜斗杀死宰夫，又将尸体支解装入竹笼，命内侍弃于野外。" },
        { speaker = "赵盾", text = "主上视人命如草芥，国家危亡只在旦夕。我与士会若再沉默，晋国便无人敢进忠言。" },
        { speaker = "士会", text = "让我先谏。若主上不听，相国再继续进言，不能让忠谏一次便断绝。" },
        { speaker = "", text = "晋灵公见士会便抢先声称知错。次日却免朝前往桃园，赵盾只得拦在园门强谏。" },
        { speaker = "赵盾", text = "有道之君以快乐百姓，无道之君只求自身享乐。纵犬弹人、支解膳夫，桀纣之祸将及君身！" },
        { speaker = "晋灵公", text = "相国暂退，容寡人今日最后游玩一次，明日早朝再依你的话改革。" },
        { speaker = "屠岸贾", text = "车驾既到桃园，岂能空返？相国挡住园门，反使国君在百姓面前失去威严。" },
        { speaker = "", text = "赵盾无奈让路。屠岸贾随即向晋灵公献计，派刺客鉏麑在五更潜入赵府。" },
        { speaker = "鉏麑", text = "赵盾端坐待朝、不忘恭敬，是百姓之主。杀他不忠，弃君命不信，我只能以死两全。" },
        { speaker = "", text = "鉏麑在赵府门前触槐自尽，临死高声示警。赵盾明知有变，仍按礼入朝。" },
        { speaker = "", text = "屠岸贾又在宫宴后壁埋伏甲士，准备诱使赵盾解剑，再诬称他拔剑弑君。" },
        { speaker = "提弥明", text = "臣侍君宴，礼不过三爵！相国不可在酒后解剑，立即起身离席！" },
        { speaker = "", text = "赵盾醒悟离席。屠岸贾命獒奴放出灵獒追咬紫袍者，宫墙后的伏兵也一齐冲出。" },
        { speaker = "提弥明", text = "相国快走！我先折断恶犬之颈，再挡住伏甲。只要赵氏还有人接应，晋国便仍有希望。" },
        { speaker = "军令", text = "西侧宫墙连续不可跨越，只有两格西门G可通行。先击退灵獒；提弥明阵亡后灵辄倒戈接应，赵盾本人必须到达（1,13）。" }
    },
    events = {
        { id = "ling_ao_defeated", trigger = "unit_defeated", unit = "LingAo50", speaker = "提弥明", text = "恶犬已死！相国立即穿过西门，我留下抵挡伏甲！" },
        { id = "ling_zhe_rescue", trigger = "unit_defeated", unit = "TiMiMing50", speaker = "灵辄", text = "相国莫怕！我是翳桑饿人灵辄，今日混在公徒之中，正为报昔日一饭之恩！" }
    },
    victory = {
        { speaker = "", text = "提弥明双手折断灵獒之颈，以身体护住赵盾，独自迎战宫中伏甲。" },
        { speaker = "", text = "赵盾退出宫门后，提弥明寡不敌众，遍体受伤，最终力尽而死。" },
        { speaker = "灵辄", text = "相国还记得翳桑那个饿了三日、却仍想把饭留给母亲的人吗？我便是灵辄。" },
        { speaker = "", text = "五年前赵盾曾救济灵辄与其母。灵辄如今身在伏兵之中，念旧恩倒戈，背负赵盾冲出朝门。" },
        { speaker = "赵盾", text = "一饭之恩，你竟以性命相报。随我同车离城，赵氏绝不会亏待义士！" },
        { speaker = "", text = "灵辄不愿受报，转身隐入人群。赵朔率赵府家丁驾车赶到，伏甲见人多势众，不敢再追。" },
        { speaker = "赵朔", text = "父亲不能再回府了。西门道路尚未封锁，我们先离开绛州，再决定投奔翟国还是秦国。" },
        { speaker = "赵盾", text = "晋君既要杀我，此刻只能出奔。家国后事暂托诸卿，待局势有变再作打算。" },
        { speaker = "", text = "赵盾父子同出西门向西而去。晋国正卿被迫流亡，灵公与赵氏的冲突已无法挽回。" },
        { speaker = "军令", text = "桃园脱险完成，获得800金币。提弥明与灵獒按原著记入阵亡；晋灵公、屠岸贾和其余伏甲均保留后续出场。" }
    },
    defeat = {{ speaker = "", text = "赵盾未能穿过桃园西门，宫中伏甲将他围住，晋国赵氏遭受重创。" }}
}

gstage = {
    title_id = "TaoyuanEscape50", turn_limit = 18,
    map = { blocked_edges = {}, size = {38,26}, terrain = {
        "FFffFFggFFffFFffFFggFFffFFffFFggFFffFF",
        "gfFFfgFFffFFgfFFfgFFffFFgfFFfgFFffFFgf",
        "FFffFFffFFggFFffFFffFFggFFffFFffFFggFF",
        "ffFggffffggfWWWWWWWWWWWWWWWWWWWWWWWWff",
        "FFggffffggffWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "fgFffffggfffWiiiiiiiiiiiiiiiiiiiiiiWfg",
        "FFffffggffffWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "gfFffggffffgWiiiiiiiiiiiiiiiiiiiiiiWgf",
        "FFffggffffggWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "ffFggffffggfWiiiiiiiiiiiiiiiiiiiiiiWff",
        "FFggffffggffWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "wwFwwwwwwwwwWiiiiiiiiiiiiiiiiiiiiiiWww",
        "FFwwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiiiWFF",
        "wwFwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiiiWww",
        "FFffggffffggWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "ffFggffffggfWiiiiiiiiiiiiiiiiiiiiiiWff",
        "FFggffffggffWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "fgFffffggfffWiiiiiiiiiiiiiiiiiiiiiiWfg",
        "FFffffggffffWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "gfFffggffffgWiiiiiiiiiiiiiiiiiiiiiiWgf",
        "FFffggffffggWiiiiiiiiiiiiiiiiiiiiiiWFF",
        "ffFggffffggfWiiiiiiiiiiiiiiiiiiiiiiWff",
        "FFggffffggffWWWWWWWWWWWWWWWWWWWWWWWWFF",
        "fgFFffFFgfFFfgFFffFFgfFFfgFFffFFgfFFfg",
        "FFffFFggFFffFFffFFggFFffFFffFFggFFffFF",
        "gfFFfgFFffFFgfFFfgFFffFFgfFFfgFFffFFgf",
    }, file = "map.bmp" },
    deploy = { unselectables = {{ position = {29,12}, hero = "ZhaoDun47" }}, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 8000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game) game:appoint_hero("ZhaoDun47", 1) end
function on_begin(game)
    game:generate_unit("TiMiMing50", 1, Enum.force.own, {27,13})
    game:generate_unit("JinLingGong50", 1, Enum.force.enemy, {31,7})
    game:generate_unit("TuAnGu50", 1, Enum.force.enemy, {29,7})
    game:generate_unit("LingAo50", 1, Enum.force.enemy, {24,12})
    for _, hero in ipairs({"JinLingGong50", "TuAnGu50"}) do game:set_unit_invulnerable(hero, true) end
    many(game, "PalaceGuard50", {{22,8},{22,11},{22,14},{22,17},{26,6},{26,19},{31,10},{31,16},{34,12}}, Enum.force.enemy)
    many(game, "PalaceArcher50", {{19,7},{19,18},{24,6},{24,19},{28,9},{28,17},{33,9},{33,17}}, Enum.force.enemy)
end
function on_update(game)
    if not dog_defeated and not game:has_unit("LingAo50") then
        dog_defeated = true
        game:push_cmd_speak(0, "提弥明已经折断灵獒之颈。赵盾立即向西门撤离，提弥明留下抵挡宫中伏甲。")
        many(game, "PalaceGuard50", {{17,10},{17,12},{17,14},{17,16}}, Enum.force.enemy)
    end
    if dog_defeated and not ti_fallen and game:is_unit_within("ZhaoDun47", {12,13}, 1) then
        ti_fallen = true
        game:generate_unit("LingZhe50", 1, Enum.force.ally, {10,13})
        ling_zhe_arrived = true
        game:push_cmd_speak(0, "赵盾已经穿过西门，提弥明转身留下断后。灵辄从伏甲中倒戈，在门外接应赵盾。")
    end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if dog_defeated and ti_fallen and game:is_unit_within("ZhaoDun47", {1,13}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
