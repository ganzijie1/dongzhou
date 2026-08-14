jiangrong_clash_spoken = false
wuli_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "MengMingShi26", "XiQiShu26", "BaiYiBing26" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "jiangrong_camp", name = "姜戎营地", position = {9, 1}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "qin_guazhou_camp", name = "秦军行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十六回·上",
    title = "歌扊扅百里认妻 获陈宝穆公证梦",
    battle_title = "瓜州逐戎",
    objective = "孟明视、西乞术、白乙丙击退姜戎主吾离；三帅任一被击退则失败",
    map_asset = "m044.png",
    intro = {
        { speaker = "", text = "秦穆公准备拜百里奚为上卿，百里奚却说自己的才智不及旧友蹇叔十分之一。" },
        { speaker = "百里奚", text = "我两次听从蹇叔之言，避过公子无知和王子颓之祸；一次不听而仕虞，几乎丧身。请速召他入秦。" },
        { speaker = "秦穆公", text = "寡人从未听说蹇叔之名，但既然井伯如此推重，便命公子絷携重礼前往宋国鸣鹿村。" },
        { speaker = "", text = "公子絷扮作商人，来到鸣鹿村。田间农夫所唱歌谣清逸高古，使他感叹蹇叔乡里也受贤者教化。" },
        { speaker = "公子絷", text = "百里奚有书托我拜访蹇先生。前方竹林左泉右石之间，可是先生草庐？" },
        { speaker = "", text = "蹇叔尚在石梁观泉，公子絷先遇到背负鹿蹄归来的蹇丙。二人谈论农桑武艺，公子絷暗暗称奇。" },
        { speaker = "蹇叔", text = "秦君既已得到井伯，一人足以治国。老夫用世之念早绝，愿退还礼币，仍在山林终老。" },
        { speaker = "公子絷", text = "先生若不去，井伯也会辞官回到鸣鹿。秦君求贤如枯苗望雨，还请成全故友的志向。" },
        { speaker = "", text = "蹇叔为了百里奚勉强答应，蹇丙也随父入秦。穆公亲自降阶迎接，询问秦国成就霸业之道。" },
        { speaker = "蹇叔", text = "德为根本，威用来辅佐。又要戒贪、戒忿、戒急；先抚雍渭百姓，再征服不服的诸戎。" },
        { speaker = "秦穆公", text = "先生为右庶长，井伯为左庶长，位皆上卿；蹇丙也拜为大夫。秦国教民立法，从此由二相同理。" },
        { speaker = "", text = "百里奚之妻杜氏早年因饥荒流落秦国，以替人浣衣为生；其子视字孟明，终日与乡人射猎角艺。" },
        { speaker = "", text = "杜氏听说秦相也叫百里奚，曾隔着车驾望见，却不敢相认。后来相府招浣衣妇，她才设法进入府中。" },
        { speaker = "杜氏", text = "老妾略懂琴歌，愿在相君堂下献曲。多年流离未曾开口，今日只唱一首旧事。" },
        { speaker = "杜氏", text = "百里奚，五羊皮！忆别时，烹伏雌，舂黄齑，炊扊扅。今日富贵忘我为？" },
        { speaker = "百里奚", text = "扊扅饯行之事只有我夫妻知道！你果然是杜氏。多年离乱，我何尝有一日忘记妻儿？" },
        { speaker = "", text = "夫妻相认，抱持大哭；孟明视也被召回，一家终于团聚。秦穆公赐粟千钟、金帛一车。" },
        { speaker = "秦穆公", text = "孟明视善于骑射，可与西乞术、白乙丙一同拜为大夫，号称三帅，专掌秦国征伐。" },
        { speaker = "孟明视", text = "父亲以治国之才受知，孩儿当以军功报答秦君。三帅虽初次同军，号令必须如一。" },
        { speaker = "", text = "姜戎主吾离骄横，多次越界侵掠秦地。二相主张先平近患，检验新军，再图更远的西戎。" },
        { speaker = "西乞术", text = "瓜州道路夹在山岭之间。步卒稳住中央，弓手留出射界，骑军再从开阔地追击吾离。" },
        { speaker = "白乙丙", text = "姜戎擅长山地袭扰，不要让全军挤在一条道路。敌人若收缩营地，先压弓手再攻主帐。" },
        { speaker = "吾离", text = "秦国刚任命三个年轻将领便敢来犯瓜州。待他们进入山道，姜戎骑兵一拥而下！" },
        { speaker = "军令", text = "击退吾离即可迫使姜戎全军败退；吾离按原著撤往晋国，不作战死处理。" }
    },
    events = {
        { id = "jiangrong_clash", trigger = "approach", position = {9, 4}, radius = 3,
          speaker = "吾离", text = "秦军已经穿过山口！骑兵沿两侧压下，弓手集中射击中央道路！" }
    },
    victory = {
        { speaker = "吾离", text = "秦国三军轮番进攻，姜戎营地已经守不住了。全军向东撤入晋境，暂避秦军锋芒！" },
        { speaker = "孟明视", text = "吾离已经越境逃往晋国，不必冒险深入追击。收拢降众，控制瓜州各处道路。" },
        { speaker = "西乞术", text = "瓜州已归秦国，附近部落若肯纳土，不得侵扰；仍持兵抵抗者才予缴械。" },
        { speaker = "白乙丙", text = "三帅初战能够取胜，全赖二相先整军政。将伤兵送入行营，清点后再向主公报捷。" },
        { speaker = "", text = "秦国尽有瓜州之地。西戎主赤斑见秦国日益强盛，派大夫繇余入秦，探察穆公为人与国力。" },
        { speaker = "繇余", text = "宫室苑囿若是役使鬼神，便劳神；若是役使百姓，便劳民。这样的壮丽并不足以夸耀。" },
        { speaker = "秦穆公", text = "戎夷没有礼乐法度，如何治理国家？" },
        { speaker = "繇余", text = "中原借礼乐粉饰、借法度督责，反生篡夺。戎人上下淳朴相待，不见治理痕迹，才是自然之治。" },
        { speaker = "百里奚", text = "繇余本是晋国不得志的贤者，如今为赤斑所用，确实会成为秦国大患。可请内史廖设法离间。" },
        { speaker = "内史廖", text = "向赤斑献女乐，使其怠政；再把繇余留秦一年，令戎主怀疑他有二心。贤臣被疏，西戎自然可取。" },
        { speaker = "", text = "赤斑沉迷女乐，繇余归国苦谏反被猜疑。秦穆公密使招贤，繇余终于弃戎入秦，献上攻取西戎之策。" },
        { speaker = "下关提示", text = "第二十六回·下：繇余熟知西戎山川，三帅沿其规划道路进军，击伤赤斑即可迫使诸戎归降。" }
    },
    defeat = {
        { speaker = "孟明视", text = "三帅初战便失去统一号令，瓜州诸部重新聚拢。只能退回秦境整军。" },
        { speaker = "", text = "孟明视、西乞术或白乙丙被击退，本关失败。" }
    }
}

gstage = {
    title_id = "GuazhouJiangRong26", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrgggggrrrrrrr",
            "rrrrrggggeggggrrrrr",
            "rrrgggmmmwmmmgggrrr",
            "rrgggmmmmwmmmmgggrr",
            "rgggmmmggwggmmmgggr",
            "gggmmmgggwgggmmmggg",
            "ggmmmmgggwgggmmmmgg",
            "ggmmmmgggwgggmmmmgg",
            "gggmmmgggwgggmmmggg",
            "rgggmmmggwggmmmgggr",
            "rrgggmmmmwmmmmgggrr",
            "rrrgggmmmwmmmgggrrr",
            "rrrrrggggeggggrrrrr",
            "rrrrrrrgggggrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {8, 12}, hero = "MengMingShi26" },
            { position = {9, 12}, hero = "XiQiShu26" },
            { position = {10, 12}, hero = "BaiYiBing26" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2600 }
}

function on_deploy(game)
    game:appoint_hero("MengMingShi26", 1)
    game:appoint_hero("XiQiShu26", 1)
    game:appoint_hero("BaiYiBing26", 1)
end

function on_begin(game)
    game:generate_unit("QinGuard26", 1, Enum.force.own, {7, 11})
    game:generate_unit("QinGuard26", 1, Enum.force.own, {11, 11})
    game:generate_unit("QinArcher26", 1, Enum.force.own, {9, 11})
    wuli_id = game:generate_unit("WuLi26", 1, Enum.force.enemy, {9, 1})
    game:generate_unit("JiangRongGuard26", 1, Enum.force.enemy, {8, 2})
    game:generate_unit("JiangRongGuard26", 1, Enum.force.enemy, {10, 2})
    game:generate_unit("JiangRongCavalry26", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("JiangRongCavalry26", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("JiangRongArcher26", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("JiangRongArcher26", 1, Enum.force.enemy, {10, 3})
end

function on_update(game)
    if not jiangrong_clash_spoken and game:is_force_within(Enum.force.own, {9, 4}, 3) then
        jiangrong_clash_spoken = true
        game:push_cmd_speak(wuli_id, "秦军已出山口！骑兵压两翼，弓手不要被前排堵住射界！")
        game:push_cmd_speak(0, "敌军主力就在北面营地！三帅保持相互支援，集中击退吾离！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("WuLi26") then return Enum.status.victory end
    return Enum.status.undecided
end
