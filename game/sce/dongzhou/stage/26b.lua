xirong_clash_spoken = false
chiban_id = -1
youyu_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "MengMingShi26", "XiQiShu26", "BaiYiBing26", "YouYu26" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "xirong_camp", name = "西戎王帐", position = {9, 1}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "qin_west_camp", name = "秦军西征行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十六回·下",
    title = "歌扊扅百里认妻 获陈宝穆公证梦",
    battle_title = "西戎归秦",
    objective = "三帅与繇余击伤西戎主赤斑，迫使诸戎归降；四名将领任一被击退则失败",
    map_asset = "m045.png",
    intro = {
        { speaker = "", text = "秦穆公厚待繇余，与其同席共食，又令蹇叔、百里奚轮流陪伴，逐一询问西戎地形和兵势。" },
        { speaker = "内史廖", text = "臣已把六名女乐献给赤斑。戎主日夜宴饮，政事荒废；如今又怀疑繇余迟归是心向秦国。" },
        { speaker = "繇余", text = "我苦谏赤斑停止宴乐，他反而疑我有二心。既然西戎不能用贤，我愿在秦国施展所学。" },
        { speaker = "秦穆公", text = "先生熟知西部诸戎，请任亚卿，与二相同理国政，并为三帅规划此次进军路线。" },
        { speaker = "百里奚", text = "此战目的在于收服诸戎，不是屠灭部落。赤斑受伤或主帐失守，便应准其投降。" },
        { speaker = "蹇叔", text = "三戒不可忘：不贪远功，不因挑衅而忿，不求一日尽灭诸戎。稳步推进，恩威并用。" },
        { speaker = "繇余", text = "赤斑把主帐设在北面高地，左右山路看似险要，中央谷道却能容纳步弓交替前进。" },
        { speaker = "孟明视", text = "西乞术领步卒在中央稳阵，白乙丙用弓手压住坡口；我率骑兵寻找侧面开阔地。" },
        { speaker = "西乞术", text = "前排近战接敌后不要堵在弓手两格射程内。若后队无法输出，立即侧移让出直线。" },
        { speaker = "白乙丙", text = "敌军若在山口聚集，弓手优先攻击主帐附近守军，不要把箭浪费在无法突破的岩山上。" },
        { speaker = "赤斑", text = "繇余背弃西戎，还把山川道路尽告秦人！诸部守住王帐，绝不能向秦国低头！" },
        { speaker = "军令", text = "岩山不可跨越，山地会增加移动消耗。击退赤斑即触发归降剧情，赤斑不会战死。" }
    },
    events = {
        { id = "xirong_clash", trigger = "approach", position = {9, 4}, radius = 3,
          speaker = "繇余", text = "前面就是西戎主帐的南口。不要攀越岩山，步弓沿谷道轮换推进！" },
        { id = "chiban_yields", trigger = "defeated", unit = "ChiBan26",
          speaker = "赤斑", text = "王帐已破，再战只会让诸部覆灭。西戎愿纳土称臣，请秦军停止进攻！" }
    },
    victory = {
        { speaker = "赤斑", text = "繇余把西戎山川虚实尽告秦军，我已无路可守。愿率本部归秦，诸军停止交战！" },
        { speaker = "孟明视", text = "秦军停手，收起兵刃。归降各部仍居原地，不夺牛羊，不迁百姓。" },
        { speaker = "繇余", text = "主公若早日停止女乐、重新亲贤，何至于此？如今既已归秦，仍应安抚部众。" },
        { speaker = "", text = "赤斑是诸戎领袖。各部听说他归秦，无不震惧，相继纳土称臣，秦国西境由此大为扩展。" },
        { speaker = "秦穆公", text = "三帅临阵有方，繇余献策熟悉道路，二相又能约束军纪。此次西征诸臣皆有重赏！" },
        { speaker = "", text = "穆公大宴群臣，轮番饮酒，回宫后忽然闭目不醒。世子罂与群臣惊惧，太医却诊得脉息如常。" },
        { speaker = "内史廖", text = "这不是疾病，而是尸厥异梦。不可惊动，也不必祈祷，只需守候主公自行醒来。" },
        { speaker = "", text = "世子罂在床边守了五日，穆公才汗出如雨而醒，却以为只是顷刻之间。" },
        { speaker = "秦穆公", text = "梦中宝夫人奉上帝之命引我登天，玉殿王者赐酒，又两次宣旨：任好听命，你将平定晋国之乱。" },
        { speaker = "内史廖", text = "晋侯宠骊姬而疏太子，国内恐怕将乱。天命主公平乱，是秦国之福。宝夫人或与陈仓旧事有关。" },
        { speaker = "", text = "内史廖取出秦文公时旧简：陈仓人曾掘得食死人脑的怪物，又遇一雌一雄两只野雉之精。" },
        { speaker = "内史廖", text = "旧言得雄者王、得雌者霸。陈仓正在太白山西，请主公到两山之间出猎，以验证梦兆。" },
        { speaker = "", text = "次日穆公出猎太白山，猎人网住一只玉色雉鸡。雉鸡随即化成石鸡，色泽光彩不减。" },
        { speaker = "秦穆公", text = "这正是梦中的宝夫人！用兰汤沐浴、锦衾覆盖，盛入玉匣，在陈仓山建立祠庙。" },
        { speaker = "", text = "宝夫人祠建成后，陈仓山改名宝鸡山。每逢祭日，山上鸡鸣传出三里，间或有赤光雷声。" },
        { speaker = "", text = "百里奚一家团聚、蹇叔入秦、三帅平戎、繇余归附，使秦国从西陲诸侯逐渐具备争衡中原的实力。" },
        { speaker = "下回预告", text = "第二十七回：骊姬再设毒计陷害申生，晋献公临终又把奚齐托付给荀息。" }
    },
    defeat = {
        { speaker = "繇余", text = "谷道推进失去章法，赤斑重新召集诸戎。秦军只能退出山口，等待再次进兵。" },
        { speaker = "", text = "孟明视、西乞术、白乙丙或繇余被击退，本关失败。" }
    }
}

gstage = {
    title_id = "WesternRongSubmission26", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrrrrr",
            "rrrrgggggegggggrrrr",
            "rrrgggFFFgFFFgggrrr",
            "rrgggmmmmwmmmmgggrr",
            "rgggmmmggwggmmmgggr",
            "gggmmmgggwgggmmmggg",
            "ggmmmmgggwgggmmmmgg",
            "ggmmmmgggwgggmmmmgg",
            "gggmmmgggwgggmmmggg",
            "rgggmmmggwggmmmgggr",
            "rrgggmmmmwmmmmgggrr",
            "rrrgggFFFgFFFgggrrr",
            "rrrrgggggegggggrrrr",
            "rrrrrrrrgggrrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {7, 12}, hero = "MengMingShi26" },
            { position = {8, 12}, hero = "XiQiShu26" },
            { position = {10, 12}, hero = "BaiYiBing26" },
            { position = {11, 12}, hero = "YouYu26" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3000 }
}

function on_deploy(game)
    game:appoint_hero("MengMingShi26", 1)
    game:appoint_hero("XiQiShu26", 1)
    game:appoint_hero("BaiYiBing26", 1)
    game:appoint_hero("YouYu26", 1)
end

function on_begin(game)
    game:generate_unit("QinGuard26", 1, Enum.force.own, {6, 11})
    game:generate_unit("QinGuard26", 1, Enum.force.own, {12, 11})
    game:generate_unit("QinArcher26", 1, Enum.force.own, {9, 11})
    chiban_id = game:generate_unit("ChiBan26", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("XiRongGuard26", 1, Enum.force.enemy, {8, 2})
    game:generate_unit("XiRongGuard26", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("XiRongCavalry26", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("XiRongCavalry26", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("XiRongArcher26", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("XiRongArcher26", 1, Enum.force.enemy, {10, 3})
end

function on_update(game)
    if not xirong_clash_spoken and game:is_force_within(Enum.force.own, {9, 4}, 3) then
        xirong_clash_spoken = true
        game:push_cmd_speak(0, "主帐南口已到！岩山不可通行，步卒让出弓手射界，沿谷道交替推进！")
        game:push_cmd_speak(chiban_id, "守住王帐！只要挡住中央谷道，秦军骑兵便无法展开！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("ChiBan26") then return Enum.status.victory end
    return Enum.status.undecided
end
