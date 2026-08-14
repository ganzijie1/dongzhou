caisang_clash_spoken = false
recall_spoken = false
bodi_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = {
    "ChongEr27", "HuMao27", "HuYan27", "ZhaoShuai27", "XuChen27",
    "WeiChou27", "HuSheGu27", "DianJie27", "JieZiTui27", "XianZhen27"
}
gduel_enabled = false
gduels = {}
gsites = {}

gstory = {
    chapter = "第二十七回·下",
    title = "骊姬巧计杀申生 献公临终嘱荀息",
    battle_title = "采桑拒晋",
    objective = "重耳与九名有名随从坚持十回合，或提前击退勃鞮；任一有名角色被击退则失败",
    map_asset = "m047.png",
    intro = {
        { speaker = "", text = "重耳逃到翟国后，狐毛、狐偃与赵衰等人陆续会合。翟君允许他们暂居，并派兵守住通往国中的采桑道路。" },
        { speaker = "重耳", text = "诸位舍弃家业随我流亡，重耳无以为报。晋军若追到翟境，不可使翟国百姓因我遭受兵祸。" },
        { speaker = "赵衰", text = "勃鞮受骊姬党羽驱使，不拿到公子绝不会停手。采桑道路交错、林缘开阔，正可分层设防。" },
        { speaker = "狐毛", text = "中央大道最便于晋骑突进，两侧林地会增加移动消耗。步卒稳住路口，骑兵从空隙反击。" },
        { speaker = "狐偃", text = "晋军弓手射程两格。前排接敌后不要堵死后方道路，让狐射姑能够进入射位压制。" },
        { speaker = "魏犨", text = "流亡也要打出晋人的气势。我率骑兵守西路，谁敢越过林口便叫他退回去。" },
        { speaker = "狐射姑", text = "我在中军后方择高处放箭。只要前队留出直线，晋军近战便不能肆意聚集。" },
        { speaker = "胥臣", text = "十回合之内守住阵势即可，不必为了追击小卒离开主队。勃鞮若被击退，追军自然退去。" },
        { speaker = "颠颉", text = "我与介子推守住重耳两侧。晋军若绕行，就让他们在林间多耗脚程。" },
        { speaker = "介子推", text = "公子处境危急，仍先想到翟国百姓。能守住这条路，才不负翟君收留之恩。" },
        { speaker = "先轸", text = "晋军兵力虽多，却是远道追击。前五回合保持完整阵线，待其锐气下降再集中反击。" },
        { speaker = "勃鞮", text = "重耳就在采桑！献公有命，翟国若敢庇护罪人，便与蒲城同罪！" },
        { speaker = "重耳", text = "我与父君之间的是非自有天日可明。勃鞮，你越境兴兵，伤的是晋翟两国百姓。" },
        { speaker = "勃鞮", text = "我只奉君命，不听逃臣辩解。骑兵沿大道压进，弓手随后寻找射界，步卒不要堵住后队！" },
        { speaker = "翟军守将", text = "采桑是翟国土地。晋军再向前一步，我军便以入侵之敌相待！" },
        { speaker = "狐偃", text = "两军已经接近。所有有名随从必须存活，坚持十回合便会等到晋国召回军令。" },
        { speaker = "军令", text = "本关以防守为主：坚持十回合或击退勃鞮胜利。林地增加移动消耗，岩山不可通行。" }
    },
    events = {
        { id = "caisang_clash", trigger = "approach", position = {9, 7}, radius = 3,
          speaker = "勃鞮", text = "重耳一行已经进入射程！前队展开，不要挡住后方弓手道路！" },
        { id = "jin_recall", trigger = "turn", turn = 10,
          speaker = "晋军传令", text = "国中急报，主公召勃鞮立即班师，不得继续滞留翟境！" }
    },
    victory = {
        { speaker = "勃鞮", text = "采桑相持已久，翟军阵势不乱。如今国中又有急令，只能暂且退兵。" },
        { speaker = "重耳", text = "晋军退去，不可追杀。先安抚采桑百姓，再向翟君谢罪。" },
        { speaker = "赵衰", text = "此次能守住，不只靠翟军，也靠众人各安其位。公子从今日起已有可以共患难的班底。" },
        { speaker = "", text = "勃鞮与重耳一行在采桑相持两个多月。丕郑父进谏晋献公，指出兴兵追子只会加深国乱，献公终于召军回国。" },
        { speaker = "", text = "重耳留在翟国，夷吾则逃往梁国。晋国诸公子几乎全部被逐出境，朝中再无人能与奚齐争位。" },
        { speaker = "骊姬", text = "申生已死，重耳、夷吾又都在国外。如今群臣纵然不服，也找不到可以拥立的人。" },
        { speaker = "晋献公", text = "奚齐年幼，国事仍须有人辅佐。寡人已让荀息教导他，里克也应顾全晋国大局。" },
        { speaker = "荀息", text = "臣既受托为傅，必以忠贞守护公子。但储位骤变，国人心中未服，仍须谨慎安抚。" },
        { speaker = "", text = "晋献公册立奚齐为世子。不久他病势加重，自知不起，召荀息到榻前托付后事。" },
        { speaker = "晋献公", text = "奚齐尚幼，卓子更小。寡人把二子与晋国都托付给你，能否使他们安然继位？" },
        { speaker = "荀息", text = "臣竭尽股肱之力，继之以忠贞；若仍不能完成托付，便以死继之。" },
        { speaker = "晋献公", text = "得你此言，寡人可以闭目。梁五、东关五掌兵，骊姬处理宫中之事，你居中主持国政。" },
        { speaker = "", text = "晋献公在位二十六年而卒。骊姬命荀息为正卿，以梁五、东关五为将军，准备扶奚齐即位。" },
        { speaker = "里克", text = "晋国士民只知申生之贤，不知奚齐之德。献公尸骨未寒，宫门内外已经暗流汹涌。" },
        { speaker = "骊姬", text = "国君遗命分明，谁敢反对奚齐，便是违抗先君。宫门与军营都要严加防守。" },
        { speaker = "荀息", text = "我已向先君许下死诺，只能守住托孤之命。即使群臣来争，也没有退路。" },
        { speaker = "", text = "申生之死、诸公子出奔与献公托孤，使晋国进入更剧烈的权力争夺。重耳的长期流亡也由此开始。" },
        { speaker = "下回预告", text = "第二十八回：晋国内乱将围绕奚齐、卓子与诸公子继续发展。" }
    },
    defeat = {
        { speaker = "赵衰", text = "阵线已经被晋军切断，有名随从折损，重耳再无力量在翟国立足。" },
        { speaker = "", text = "重耳或任一有名随从被击退，本关失败。" }
    }
}

gstage = {
    title_id = "DefendCaisang27", turn_limit = 14,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrFFFgggggggFFFrrr",
            "rrrFFgggggggggFFrrr",
            "rrFgggggfffgggggFrr",
            "rFFgggfffffffgggFFr",
            "FFgggffffwffffgggFF",
            "FgggfffffwfffffgggF",
            "gggffffggwggffffggg",
            "gggffffggwggffffggg",
            "FgggfffffwfffffgggF",
            "FFgggffffwffffgggFF",
            "rFFgggfffffffgggFFr",
            "rrFgggggfffgggggFrr",
            "rrrFFgggggggggFFrrr",
            "rrrFFFgggggggFFFrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "ChongEr27" },
            { position = {7, 12}, hero = "HuMao27" },
            { position = {11, 12}, hero = "HuYan27" },
            { position = {8, 11}, hero = "ZhaoShuai27" },
            { position = {10, 11}, hero = "XuChen27" },
            { position = {5, 11}, hero = "WeiChou27" },
            { position = {13, 11}, hero = "HuSheGu27" },
            { position = {6, 12}, hero = "DianJie27" },
            { position = {12, 12}, hero = "JieZiTui27" },
            { position = {9, 10}, hero = "XianZhen27" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3400 }
}

function on_deploy(game)
    game:appoint_hero("ChongEr27", 1)
    game:appoint_hero("HuMao27", 1)
    game:appoint_hero("HuYan27", 1)
    game:appoint_hero("ZhaoShuai27", 1)
    game:appoint_hero("XuChen27", 1)
    game:appoint_hero("WeiChou27", 1)
    game:appoint_hero("HuSheGu27", 1)
    game:appoint_hero("DianJie27", 1)
    game:appoint_hero("JieZiTui27", 1)
    game:appoint_hero("XianZhen27", 1)
end

function on_begin(game)
    game:generate_unit("DiGuard27", 1, Enum.force.own, {4, 12})
    game:generate_unit("DiGuard27", 1, Enum.force.own, {14, 12})
    game:generate_unit("DiArcher27", 1, Enum.force.own, {9, 13})
    bodi_id = game:generate_unit("BoDi27", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {8, 2})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("JinCavalry27", 1, Enum.force.enemy, {4, 3})
    game:generate_unit("JinCavalry27", 1, Enum.force.enemy, {14, 3})
    game:generate_unit("JinArcher27", 1, Enum.force.enemy, {7, 1})
    game:generate_unit("JinArcher27", 1, Enum.force.enemy, {11, 1})
    game:generate_unit("JinArcher27", 1, Enum.force.enemy, {9, 3})
end

function on_update(game)
    if not caisang_clash_spoken and game:is_force_within(Enum.force.enemy, {9, 7}, 3) then
        caisang_clash_spoken = true
        game:push_cmd_speak(bodi_id, "采桑守军就在前面！近战前队不要堵住两格射界，让弓手先压低其兵力！")
        game:push_cmd_speak(0, "晋军开始展开。保持中央道路畅通，弓手与骑兵按次序反击！")
    end
    if not recall_spoken and game:get_turn_current() >= 10 then
        recall_spoken = true
        game:push_cmd_speak(bodi_id, "国中急令召我回军。各部脱离接触，不得再向翟境深入！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("BoDi27") then return Enum.status.victory end
    if game:get_turn_current() >= 10 then return Enum.status.victory end
    return Enum.status.undecided
end
