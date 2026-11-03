counterattack_spoken = false
gate_spoken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = {
    "GongZiZhao32", "CuiYao32", "SongXiangGong33", "GongZiDang33",
    "GongSunGu33", "HuaYuShi33", "GaoHu33"
}
gduel_enabled = false
gduels = {}
gsites = {
    { id = "linzi_north_gate", name = "临淄城门", position = {10, 0},
      restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "song_left_camp", name = "宋军左营", position = {3, 11},
      restore_hp = 20, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "song_center_camp", name = "宋军中营", position = {9, 11},
      restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "song_right_camp", name = "宋军右营", position = {15, 11},
      restore_hp = 20, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第三十三回·上",
    title = "宋公伐齐纳子昭 楚人伏兵劫盟主",
    battle_title = "齐郊夜战",
    objective = "击退公子元、公子潘、公子商人后，护送公子昭本人进入北侧城门（10，0）；七名我方有名角色任一被击退则失败",
    map_asset = "m054.png",
    intro = {
        { speaker = "", text = "易牙率军出城抵挡宋、卫、曹、邾四国，高虎趁竖刁留守临淄，在城楼设下伏兵，以商议军情为名将他请来饮酒。" },
        { speaker = "高虎", text = "宋公合诸侯送世子到齐，城外众寡不敌。老夫今日要借你一件东西，才能救齐国之难。" },
        { speaker = "竖刁", text = "老大夫有何差遣，竖刁惟命是听。" },
        { speaker = "高虎", text = "只借你项上人头，向世子与宋公谢罪！壮士还不动手！" },
        { speaker = "", text = "伏兵从壁后冲出，擒住竖刁斩首。高虎大开城门，号召国人出迎公子昭，响应者超过千人。" },
        { speaker = "", text = "公子无亏得知竖刁被杀，乘小车仗剑出宫，想召集丁壮抵抗。昔日被害官员的家属在东门将他围住杀死。" },
        { speaker = "", text = "易牙军中听说无亏、竖刁俱死，士卒纷纷倒戈。易牙只带数名心腹连夜逃往鲁国，高虎接收其军，迎接公子昭。" },
        { speaker = "公子昭", text = "奸臣已除，诸侯也已经退兵。请高、国二老整备法驾，我当入城为父君治丧。" },
        { speaker = "", text = "公子元、公子潘、公子商人不肯奉迎，联合无亏旧党与竖刁余部据守临淄各门。高虎只得护送公子昭再次退往宋国。" },
        { speaker = "宋襄公", text = "是寡人班师太早，才让三公子重新闭城。此次独出四百乘，定要把世子送入临淄。" },
        { speaker = "公子目夷", text = "三公子党羽虽多，却各怀私心。只要稳住营寨，等他们出城决战，便可分割击破。" },
        { speaker = "", text = "宋军抵达齐郊，三公子担心攻城惊动百姓，决定趁宋军立营未稳，于当夜突然打开城门劫寨。" },
        { speaker = "公子商人", text = "先集中四家兵众击破公子荡前营，再趁夜色冲击宋国中军。胜则逐昭，不胜便各自退路。" },
        { speaker = "公子元", text = "此战以替无亏复仇为名。诸军从中央道路突进，不要在林地分散。" },
        { speaker = "公子潘", text = "宋军营火就在南面。弓手射住营门，步骑一齐压上，今夜不能让他们重新列阵！" },
        { speaker = "公子荡", text = "前营遭到夜袭，先向中军收缩，不可让齐军包围。公孙固、华御事正从左右来援！" },
        { speaker = "公孙固", text = "我率中军从正面接住三公子，华御事与高虎分攻两翼。公子昭留在后阵，等敌军退散再入城。" },
        { speaker = "高虎", text = "城门在北面中央，整段城墙都不可跨越。击退三公子之后，必须由公子昭本人走入城门。" },
        { speaker = "军令", text = "先击退公子元、公子潘、公子商人，再护送公子昭本人到（10，0）。城墙不可通行，城门与宋军三处营寨可回复体力和策略值。" }
    },
    events = {
        { id = "song_counterattack", trigger = "approach", position = {9, 7}, radius = 2,
          speaker = "公孙固", text = "前营已经稳住！中军向北反击，弓手保持两格射界，不要被前排堵住！" },
        { id = "linzi_gate", trigger = "defeated", unit = "GongZiYuan33",
          speaker = "高虎", text = "公子元已经败退，齐军阵势开始动摇。继续击退潘与商人，再迎世子入城！" }
    },
    victory = {
        { speaker = "公子元", text = "四家兵众各为其主，根本不能统一号令。宋军已经合围，我先往卫国避难！" },
        { speaker = "公子潘", text = "元已经逃走，城门也来不及关闭。收拢残兵退回府中，暂且向世子请罪。" },
        { speaker = "公子商人", text = "此战败在众心不一。留得性命，日后齐国朝局仍有我们的机会。" },
        { speaker = "", text = "宋军反击至天明，三公子党羽溃散。公子元逃往卫国，潘与商人退入城中，宋军紧随其后进入临淄。" },
        { speaker = "崔夭", text = "当日我开东门送世子出逃，今日再为世子执辔入城。齐国宗庙终于没有断绝。" },
        { speaker = "", text = "国懿仲聚集百官，与高虎拥立公子昭即位，是为齐孝公。孝公封崔夭为大夫，厚赏宋军。" },
        { speaker = "齐孝公", text = "无亏、竖刁虽死，齐国不能再因诸公子互相残杀。只诛易牙、竖刁首乱之党，其余一概赦免。" },
        { speaker = "高虎", text = "宽赦可以暂安宗室。公子潘与商人仍有党羽，主公今后不可再让宫中私门左右国政。" },
        { speaker = "", text = "鲁僖公发兵来救无亏，途中听说齐孝公已经即位，只得撤军。从此鲁、齐之间产生嫌隙。" },
        { speaker = "", text = "当年八月，齐国安葬桓公于牛首堈，并将晏蛾儿附葬。宫中又强迫数百内侍宫人殉葬。" },
        { speaker = "宋襄公", text = "寡人以一国之兵平定齐乱、拥立世子，此功足以号召诸侯，继承齐桓公的霸业。" },
        { speaker = "公子目夷", text = "纳昭是守信义，诸侯敬服的是这份信义。若把一时之功当作称霸根基，反会走得太急。" },
        { speaker = "", text = "宋襄公先约滕、曹、邾、鄫等小国会盟。滕君迟到被拘，鄫君晚到两日，宋公竟听从公子荡，以鄫君祭祀睢水。" },
        { speaker = "公子目夷", text = "祭祀本为人祈福，杀人求福，神也不会享用。用残暴威吓诸侯，只会使他们恐惧而背离宋国。" },
        { speaker = "", text = "东夷并未因此来朝。滕君重赂获释，曹君也因宋公残虐离会，宋襄公震怒，命公子荡率军伐曹。" },
        { speaker = "", text = "宋军围曹三个月不能取胜。郑文公率先朝楚，又约鲁、齐、陈、蔡与楚成王结盟，宋襄公只得召军撤退。" },
        { speaker = "公子荡", text = "大国之中以齐、楚最强。齐国新乱未定，若先以厚礼求楚王帮助召集诸侯，宋国仍可借势主盟。" },
        { speaker = "公子目夷", text = "诸侯本来畏服楚国，楚王怎会把盟主之权交给宋国？向楚借势，恐怕反受楚国操纵。" },
        { speaker = "", text = "宋襄公不听，派公子荡赴楚。楚成王约宋、齐在鹿上会面，宋公又自负有恩于齐，轻慢齐孝公而先请楚王署名。" },
        { speaker = "楚成王", text = "宋公既想借楚国召集诸侯，明年秋八月便在盂地会盟。寡人自会带陈、蔡、郑等国赴会。" },
        { speaker = "", text = "楚成王回国后接受成得臣之计，暗选千名勇士操演，准备在盂地把宋襄公劫为俘虏。" },
        { speaker = "下关提示", text = "第三十三回·下：盂地会盟时楚军将突然露甲。公子目夷必须按宋襄公嘱托突围回国。" }
    },
    defeat = {
        { speaker = "高虎", text = "宋军中营被冲散，公子昭再度失去援军。临淄诸门仍在三公子手中。" },
        { speaker = "", text = "公子昭、崔夭、宋襄公、公子荡、公孙固、华御事或高虎被击退，本关失败。" }
    }
}

gstage = {
    title_id = "BattleQiCamp33", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "WWWWWWWWWWGWWWWWWWW",
            "FFgggggggffggggggFF",
            "FggggggggffgggggggF",
            "FggggggggffgggggggF",
            "gggggggggffgggggggg",
            "ggggggggwffwggggggg",
            "ggggggggwffwggggggg",
            "ggggggggwffwggggggg",
            "gggggggggffgggggggg",
            "gggfffffffffffffggg",
            "gggffffffffffgggggg",
            "gggefffffefffffeggg",
            "gggfffffffffffffggg",
            "gggggggggffgggggggg"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "GongZiZhao32" },
            { position = {10, 12}, hero = "CuiYao32" },
            { position = {9, 11}, hero = "SongXiangGong33" },
            { position = {9, 9}, hero = "GongZiDang33" },
            { position = {6, 11}, hero = "GongSunGu33" },
            { position = {12, 11}, hero = "HuaYuShi33" },
            { position = {10, 10}, hero = "GaoHu33" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 4400 }
}

function on_deploy(game)
    game:appoint_hero("GongZiZhao32", 1)
    game:appoint_hero("CuiYao32", 1)
    game:appoint_hero("SongXiangGong33", 1)
    game:appoint_hero("GongZiDang33", 1)
    game:appoint_hero("GongSunGu33", 1)
    game:appoint_hero("HuaYuShi33", 1)
    game:appoint_hero("GaoHu33", 1)
end

function on_begin(game)
    game:generate_unit("SongGuard33", 1, Enum.force.own, {3, 11})
    game:generate_unit("SongGuard33", 1, Enum.force.own, {15, 11})
    game:generate_unit("SongArcher33", 1, Enum.force.own, {7, 12})
    game:generate_unit("SongArcher33", 1, Enum.force.own, {13, 12})
    game:generate_unit("GongZiYuan33", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("GongZiPan33", 1, Enum.force.enemy, {5, 4})
    game:generate_unit("GongZiShangRen33", 1, Enum.force.enemy, {14, 4})
    game:generate_unit("QiClanGuard33", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("QiClanGuard33", 1, Enum.force.enemy, {11, 4})
    game:generate_unit("QiClanGuard33", 1, Enum.force.enemy, {6, 5})
    game:generate_unit("QiClanGuard33", 1, Enum.force.enemy, {13, 5})
    game:generate_unit("QiClanArcher33", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("QiClanArcher33", 1, Enum.force.enemy, {12, 3})
end

function on_update(game)
    if not counterattack_spoken and game:is_force_within(Enum.force.own, {9, 7}, 2) then
        counterattack_spoken = true
        game:push_cmd_speak(0, "宋军中军已经接战！公孙固正面推进，华御事与高虎从两翼夹击！")
    end
    if not gate_spoken
       and not game:has_unit("GongZiYuan33")
       and not game:has_unit("GongZiPan33")
       and not game:has_unit("GongZiShangRen33") then
        gate_spoken = true
        game:push_cmd_speak(0, "三公子均已败退！请公子昭本人沿中央道路进入北侧城门！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("GongZiYuan33")
       and not game:has_unit("GongZiPan33")
       and not game:has_unit("GongZiShangRen33")
       and game:is_unit_within("GongZiZhao32", {10, 0}, 0) then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
