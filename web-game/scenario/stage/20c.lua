gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ShenSheng20", "ZhaoSu20", "BiWan20" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "di_fort_20", name = "狄寨", position = {3, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "huo_castle_20", name = "霍国城池", position = {15, 2}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "huo_gate_20", name = "霍城南门", position = {15, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "wei_castle_20b", name = "魏国城池", position = {9, 6}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "wei_fort_20b", name = "魏国营门", position = {9, 8}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "jin_lower_camp_20", name = "晋国下军行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 2 }, { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十回·三",
    title = "申生将下军灭三国",
    battle_title = "狄霍魏之战",
    objective = "分兵夺取狄寨、霍城与魏邑，击败三国守军",
    map_asset = "m032.png",
    intro = {
        { speaker = "", text = "晋献公建立上、下二军，自领上军，以世子申生统领下军，赵夙、毕万随军出征。" },
        { speaker = "晋献公", text = "狄、霍、魏三国扼守北境道路，时常彼此接应。下军须同时压住三处据点，不可让其合兵。" },
        { speaker = "申生", text = "儿臣领命。赵夙攻西北狄寨，毕万取东北霍城，我率中军进逼魏邑。" },
        { speaker = "赵夙", text = "狄寨以木栅围护，中央鹿砦是唯一入口。臣先用弓手压制，再令步卒开路。" },
        { speaker = "毕万", text = "霍城有石墙南门，不可翻越。我部沿东路直抵城下，夺门之后守住内街。" },
        { speaker = "申生", text = "魏邑居中，若先败便会使两翼孤立。我军必须保持联络，不可只顾一处追击。" },
        { speaker = "狄首", text = "晋军分成三路，正是兵力空虚。守住寨门，待霍、魏从两侧夹击！" },
        { speaker = "霍君", text = "霍城石墙坚固。晋军若攻狄寨，我便出兵袭其后路；若来攻城，则据门射击。" },
        { speaker = "魏君", text = "魏邑虽小，却位居三军中央。诸军向我靠拢，共同抵挡申生。" },
        { speaker = "赵夙", text = "敌军想互相救援，正须切断三条道路。每夺下一处，立即留下兵力守住入口。" },
        { speaker = "毕万", text = "下军初建，此战关系世子威望。各部依号令推进，不得争功乱序。" },
        { speaker = "军令", text = "申生、赵夙、毕万必须存活。栅栏、城墙和水域不可通行，从各处入口击败三国全部守军。" }
    },
    victory = {
        { speaker = "申生", text = "三处据点都已平定。收拢降卒、封存府库，不得惊扰当地百姓。" },
        { speaker = "赵夙", text = "狄寨已降，北境西路从此畅通。臣请留少量守军修整道路。" },
        { speaker = "毕万", text = "霍、魏相继失守，三国不能再彼此呼应。下军可以班师复命。" },
        { speaker = "", text = "晋军灭狄、霍、魏三国。晋献公把狄地赐给赵夙、魏地赐给毕万，二族由此开始兴盛。" },
        { speaker = "晋献公", text = "世子统军有方，赵夙、毕万皆有战功。按功赐邑，使天下知道晋国赏罚分明。" },
        { speaker = "", text = "申生功名愈高，骊姬反而愈加忌惮。她继续在绛都经营党羽，等待离间父子的机会。" },
        { speaker = "", text = "与此同时，南方楚国也发生内乱。熊恽杀兄即位，是为楚成王，以叔父子元为令尹。" },
        { speaker = "", text = "子元仰慕文夫人息妫，又在宫旁大建馆舍歌舞。文夫人斥其不思征伐，子元遂率六百乘攻郑。" },
        { speaker = "叔詹", text = "子元求胜心切，反而最怕失败。大开城门、照常行市，再使甲士暗伏，他必疑有诡计。" },
        { speaker = "", text = "子元见郑城空门整肃，又闻齐、宋、鲁援军将至，连夜留下空营撤退。郑国不战而解围。" },
        { speaker = "下关提示", text = "第二十回·四：子元回楚后图谋更急，斗谷於菟将率甲士入宫靖难。" }
    },
    defeat = {
        { speaker = "申生", text = "三路军势被敌军分割，继续进攻只会被逐一击破。下军暂退南营重新集结。" },
        { speaker = "", text = "狄、霍、魏仍能互相支援，晋国北境未能平定。" }
    }
}

gstage = {
    title_id = "JinConquersThreeStates20", turn_limit = 24,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FPPPPPgggggggWWWWWF",
            "FPiiiPgggggggWiCiWF",
            "FPiiiPgggggggWiiiWF",
            "FPPDPPgggggggWWGWWF",
            "FgggggPPPPPPPgggggF",
            "FgggggPiiCiiPgggggF",
            "FgggggPiiiiiPgggggF",
            "FgggggPPPDPPPgggggF",
            "FgggggggggggggggggF",
            "F~~~~gggggggggggggF",
            "FgggggggggggggggggF",
            "FggggggggeggggggggF",
            "FFFFFFFFFFFFFFFFFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "ShenSheng20" },
            { position = {6, 11}, hero = "ZhaoSu20" },
            { position = {12, 11}, hero = "BiWan20" },
            { position = {8, 11}, hero = "JinGuard202" },
            { position = {10, 11}, hero = "JinArcher202" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1450 }
}

function on_deploy(game)
    game:appoint_hero("ShenSheng20", 1)
    game:appoint_hero("ZhaoSu20", 1)
    game:appoint_hero("BiWan20", 1)
    game:appoint_hero("JinGuard202", 1)
    game:appoint_hero("JinArcher202", 1)
end

function on_begin(game)
    game:generate_unit("DiChief20", 1, Enum.force.enemy, {3, 2})
    game:generate_unit("DiGuard20", 1, Enum.force.enemy, {2, 3})
    game:generate_unit("DiArcher20", 1, Enum.force.enemy, {4, 3})
    game:generate_unit("HuoLord20", 1, Enum.force.enemy, {15, 2})
    game:generate_unit("HuoGuard20", 1, Enum.force.enemy, {14, 3})
    game:generate_unit("HuoArcher20", 1, Enum.force.enemy, {16, 3})
    game:generate_unit("WeiLord20", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("WeiGuard202", 1, Enum.force.enemy, {8, 7})
    game:generate_unit("WeiArcher202", 1, Enum.force.enemy, {10, 7})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end