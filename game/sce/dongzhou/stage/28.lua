east_market_spoken = false
court_gate_spoken = false
liangwu_spoken = false
dongguan_id = -1
liangwu_id = -1
xunxi_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "LiKe28", "PiZhengFu28", "TuAnYi28", "ZhuiTuan28", "GongHua28" }
gduel_enabled = true
gduels = {
    {
        attacker = "TuAnYi28", defender = "DongGuanWu28", exp = 65, outcome = "kill",
        attacker_speech = "东关五，我来禀报围攻里府之事，请近前听令！",
        defender_speech = "里克已成瓮中之鳖。你若能取其首级，本将保你升爵！",
        result_speech = "屠岸夷猝然扼住东关五颈项，一臂发力，将其折颈掷于东市。",
        text = "屠岸夷依骓遄之计佯受甲兵，在东市反戈，亲手折颈杀死东关五。"
    },
    {
        attacker = "LiKe28", defender = "LiangWu28", exp = 70, outcome = "kill",
        attacker_speech = "梁五，申生之冤、奚齐之乱，今日一并清算！",
        defender_speech = "晋国宫门尚在我手，里克逆党休想再进一步！",
        result_speech = "梁五欲自刎不成，被屠岸夷擒住；里克挥刀将其斩为两段。",
        text = "梁五逃往朝堂途中被擒，里克依原著记载亲手将其斩杀。"
    },
    {
        attacker = "TuAnYi28", defender = "XunXi28", exp = 75, outcome = "kill",
        attacker_speech = "荀息，卓子已伏诛，你还要守这道乱命吗？",
        defender_speech = "我受先君托孤，虽知无益，也不能食言。今日惟有以死践诺！",
        result_speech = "荀息拔剑冲向里克，屠岸夷从侧面截住，将其斩于朝阶。",
        text = "荀息护卓子于朝堂，最后拔剑死战，被屠岸夷斩杀。"
    }
}
gsites = {}

gstory = {
    chapter = "第二十八回",
    title = "里克两弑孤主 穆公一平晋乱",
    battle_title = "绛都宫变",
    objective = "击杀东关五、梁五、荀息；五名我方有名将领任一被击退则失败",
    map_asset = "m048.png",
    intro = {
        { speaker = "", text = "晋献公死后，荀息依遗命拥立奚齐。狐突托病不朝，里克与丕郑父则到荀息府中劝他改立长公子。" },
        { speaker = "里克", text = "重耳、夷吾俱在国外，奚齐又是骊姬所生。如今国人怨愤，凭什么让一个孺子服众？" },
        { speaker = "荀息", text = "先君托奚齐于我，奚齐便是我的君主。力不能保，我也只有一死谢罪，绝不改口。" },
        { speaker = "丕郑父", text = "死无益于晋国。你若执意守骊姬母子，我等也只能各成其志。" },
        { speaker = "", text = "里克派力士混入丧次，在苫块旁刺死奚齐；优施挺剑救主，也被一同杀死。荀息转而拥立九岁的卓子。" },
        { speaker = "梁五", text = "奚齐之死必是里克、丕郑父主谋！趁其党羽尚未聚集，立即调兵讨伐！" },
        { speaker = "荀息", text = "里、丕根深党固，七舆大夫半出其门。贸然进攻若败，卓子之位便再无可守。" },
        { speaker = "", text = "梁五与东关五不听，准备在送葬之日设伏杀里克。东关五把三百甲士交给客将屠岸夷。" },
        { speaker = "屠岸夷", text = "骓大夫，梁五要我围攻里克。若我照办，便是替骊姬党羽残害晋国老臣。" },
        { speaker = "骓遄", text = "你可先佯装答应，拿到兵权后反戈杀东关五。我与里克迎立重耳，自会保你富贵与清名。" },
        { speaker = "屠岸夷", text = "我愿割鸡为盟。东市见到东关五时，我先近身制住他，再号召三百甲士倒戈。" },
        { speaker = "", text = "送葬之日，里克称病留在府中。屠岸夷假意包围里府，又派人向墓地报告变乱，诱使梁五等分兵。" },
        { speaker = "东关五", text = "诸大夫都去送葬，只有里克不出。今日正是天赐良机，三百甲士随我先到东市！" },
        { speaker = "里克", text = "屠岸夷反戈之后，东市守军会动摇。丕郑父、骓遄、共华各率家甲会合，沿中央道路攻朝门。" },
        { speaker = "丕郑父", text = "宫墙不可跨越，只有中间两格朝门可通行。弓手压住门内，步卒与骑兵依次进入。" },
        { speaker = "共华", text = "臣的家甲已从西路赶来。东关五一死便立即向朝门推进，不给梁五转移卓子的时间。" },
        { speaker = "梁五", text = "东市若有变，所有宫卫退入朝门。荀卿护住卓子，我带兵在门内截杀里克！" },
        { speaker = "荀息", text = "我受先君遗命，今日即使宫门失守，也要护卓子到底。宫卫不得擅自退散。" },
        { speaker = "屠岸夷", text = "东关五就在东市近前。我先依约动手，诸位看见晋军旗号转向，便一齐向北推进。" },
        { speaker = "军令", text = "屠岸夷对东关五、里克对梁五、屠岸夷对荀息相邻时会触发原著单挑并直接击杀目标。" }
    },
    events = {
        { id = "east_market_turn", trigger = "defeated", unit = "DongGuanWu28",
          speaker = "屠岸夷", text = "东关五已死！愿为申生伸冤、迎立重耳者，随我转旗攻入朝门！" },
        { id = "court_gate", trigger = "approach", position = {9, 7}, radius = 2,
          speaker = "里克", text = "朝门就在前面。宫墙不可翻越，各部从两格门道依次进入！" },
        { id = "liang_falls", trigger = "defeated", unit = "LiangWu28",
          speaker = "里克", text = "梁五已经伏诛。荀息仍在北面朝堂护着卓子，继续推进！" }
    },
    victory = {
        { speaker = "里克", text = "东关五、梁五俱死，宫卫已经散去。荀息，你还要为了卓子与满朝公卿为敌吗？" },
        { speaker = "荀息", text = "我既以忠信许先君，怎能因成败改口？今日不能保卓子，唯有以死继之。" },
        { speaker = "", text = "卓子被屠岸夷夺下掷死，荀息拔剑来斗，也被斩于阶前。骊姬逃入后园，投水而死。" },
        { speaker = "", text = "里克尽灭梁五、东关五与优施之族，召集百官，主张迎立年长且贤的公子重耳。" },
        { speaker = "丕郑父", text = "迎立重耳须有狐突同意。狐氏父子深得国人信任，缺其名号，翟国的公子未必肯来。" },
        { speaker = "", text = "狐突以两个儿子都随重耳流亡为由，不肯在迎立文书署名。屠岸夷带着群臣表章前往翟国。" },
        { speaker = "重耳", text = "表章上没有狐突之名，晋国内部必未安定。二孺子刚死，其党羽尚在，我不能乘丧贪国。" },
        { speaker = "狐偃", text = "此时入晋，既有乘乱之名，又可能受制于迎立诸臣。天若保佑公子，何患将来无国？" },
        { speaker = "", text = "重耳拒绝返国。里克无奈，改派梁繇靡与屠岸夷前往梁国迎接夷吾。" },
        { speaker = "夷吾", text = "重耳自己放弃国位，正是上天把晋国交给我。只是里克等人迎我，必然有所求。" },
        { speaker = "郤芮", text = "先以汾阳、负葵之田厚赂里克和丕郑父，再借强秦之兵护送入国，方能确保万无一失。" },
        { speaker = "", text = "夷吾分别许给里克、丕郑父大片田地，又派使者向秦穆公献出河西五城，以换取秦军护送。" },
        { speaker = "秦穆公", text = "重耳、夷吾都称贤公子。先派公子絷分别吊唁，观察二人言行，再决定纳谁为君。" },
        { speaker = "", text = "重耳受吊时只为父丧痛哭，拒谈国位；夷吾却喜形于色，又向公子絷赠送黄金白玉。" },
        { speaker = "公子絷", text = "若为晋国择君，重耳远胜夷吾；若只求置君之名与秦国之利，夷吾反而更容易控制。" },
        { speaker = "秦穆公", text = "此言使寡人豁然。命公孙枝率三百乘护送夷吾，借此平定晋乱。" },
        { speaker = "", text = "穆姬又写信要求夷吾善待贾君、召回无罪诸公子。齐桓公与周惠王也遣军会合，共同护送。" },
        { speaker = "", text = "秦、周、齐三军抵达晋境，狐突率群臣备法驾迎接。夷吾进入绛都即位，是为晋惠公。" },
        { speaker = "晋惠公", text = "立子圉为世子，任狐突、虢射、吕饴甥、郤芮等为大夫。晋国自今日重新定君。" },
        { speaker = "", text = "国人一向仰慕重耳，见最终即位的是夷吾，大多失望。公孙枝则留在晋国，索取先前许诺的河西五城。" },
        { speaker = "里克", text = "新君若一即位便背弃强邻，秦国必怒。既然亲口许地，就应兑现。" },
        { speaker = "吕饴甥", text = "当初国非君有，才以他人之地求援；如今晋国已定，何必真的割让先君疆土？" },
        { speaker = "", text = "晋惠公拒绝割地，也不肯兑现许给里克、丕郑父的封田，只派丕郑父带国书赴秦谢罪。" },
        { speaker = "丕郑父", text = "夷吾失信于秦，又负晋臣。我将向秦君揭明吕、郤之谋，请秦国改纳重耳。" },
        { speaker = "下回预告", text = "第二十九回：晋惠公将清洗迎立旧臣，管仲也将在病榻上为齐国论定继任之相。" }
    },
    defeat = {
        { speaker = "里克", text = "东市倒戈未能成功，梁五已经封锁朝门。各家甲兵被分割，本次举事失败。" },
        { speaker = "", text = "里克、丕郑父、屠岸夷、骓遄或共华被击退，本关失败。" }
    }
}

gstage = {
    title_id = "JiangCapitalCoup28", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFFFFgggggggggFFFFF",
            "FFFFgggiiihiiigFFFF",
            "FFFgggiiiiiiigggFFF",
            "FFFgggiiiiiiigggFFF",
            "FFggggiiiiiiiggggFF",
            "FgggggiiiiiiigggggF",
            "WWWWWWWWffWWWWWWWWW",
            "FFgggffffwffffgggFF",
            "FgggfffffwfffffgggF",
            "FggffffggwggffffggF",
            "FggffffggwggffffggF",
            "FgggfffffwfffffgggF",
            "FFgggffffwffffgggFF",
            "FFFggggggwggggggFFF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 12}, hero = "LiKe28" },
            { position = {7, 12}, hero = "PiZhengFu28" },
            { position = {12, 9}, hero = "TuAnYi28" },
            { position = {5, 11}, hero = "ZhuiTuan28" },
            { position = {3, 10}, hero = "GongHua28" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3600 }
}

function on_deploy(game)
    game:appoint_hero("LiKe28", 1)
    game:appoint_hero("PiZhengFu28", 1)
    game:appoint_hero("TuAnYi28", 1)
    game:appoint_hero("ZhuiTuan28", 1)
    game:appoint_hero("GongHua28", 1)
end

function on_begin(game)
    game:generate_unit("CoupGuard28", 1, Enum.force.own, {8, 11})
    game:generate_unit("CoupGuard28", 1, Enum.force.own, {10, 11})
    game:generate_unit("CoupArcher28", 1, Enum.force.own, {6, 10})
    game:generate_unit("CoupArcher28", 1, Enum.force.own, {4, 10})

    dongguan_id = game:generate_unit("DongGuanWu28", 1, Enum.force.enemy, {13, 9})
    liangwu_id = game:generate_unit("LiangWu28", 1, Enum.force.enemy, {9, 3})
    xunxi_id = game:generate_unit("XunXi28", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("PalaceGuard28", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("PalaceGuard28", 1, Enum.force.enemy, {11, 2})
    game:generate_unit("PalaceGuard28", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("PalaceGuard28", 1, Enum.force.enemy, {11, 4})
    game:generate_unit("PalaceArcher28", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("PalaceArcher28", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("DongshiGuard28", 1, Enum.force.enemy, {14, 10})
    game:generate_unit("DongshiGuard28", 1, Enum.force.enemy, {15, 9})
    game:generate_unit("DongshiArcher28", 1, Enum.force.enemy, {16, 10})
end

function on_update(game)
    if not east_market_spoken and not game:has_unit("DongGuanWu28") then
        east_market_spoken = true
        game:push_cmd_speak(0, "东关五已死，东市甲士纷纷倒戈！各部转向中央朝门！")
    end
    if not court_gate_spoken and game:is_force_within(Enum.force.own, {9, 7}, 2) then
        court_gate_spoken = true
        game:push_cmd_speak(liangwu_id, "关闭朝门已经来不及了！步卒堵住两格通道，弓手从门内齐射！")
        game:push_cmd_speak(0, "宫墙无法跨越，从两格朝门轮换进兵，不要让前排堵死后队！")
    end
    if not liangwu_spoken and not game:has_unit("LiangWu28") then
        liangwu_spoken = true
        game:push_cmd_speak(xunxi_id, "梁五也已伏诛。荀息今日唯有守住卓子，以死践先君之命！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("DongGuanWu28")
       and not game:has_unit("LiangWu28")
       and not game:has_unit("XunXi28") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
