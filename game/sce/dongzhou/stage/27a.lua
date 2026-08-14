rear_gate_spoken = false
bodi_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChongEr27", "HuMao27", "HuYan27" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "jin_siege_camp_west", name = "晋军西营", position = {4, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "jin_siege_camp_east", name = "晋军东营", position = {14, 11}, restore_hp = 20, restore_mp = 10,
      rewards = {} }
}

gstory = {
    chapter = "第二十七回·上",
    title = "骊姬巧计杀申生 献公临终嘱荀息",
    battle_title = "蒲城突围",
    objective = "护送重耳本人到达东侧出口（18，5）；重耳、狐毛、狐偃任一被击退则失败",
    map_asset = "m046.png",
    intro = {
        { speaker = "", text = "骊姬与优施先拉拢荀息，让他担任奚齐的师傅，又设法使里克远离朝政，晋国储位之争愈发险恶。" },
        { speaker = "骊姬", text = "世子申生仁孝而有军功，若只在君侯面前进谗，群臣必定不服。须让罪证看起来出自他自己。" },
        { speaker = "", text = "骊姬先以蜂蜜涂发，在花园招引蜜蜂，又故意让申生持衣袖驱赶，使晋献公远望时误以为世子调戏庶母。" },
        { speaker = "晋献公", text = "寡人亲眼所见，岂还能错？申生竟敢在宫苑无礼，实在辜负寡人多年信任。" },
        { speaker = "", text = "申生奉命在曲沃祭祀母亲齐姜，将祭肉和酒送回绛都。骊姬暗中投毒，试给犬与小臣，二者当场毙命。" },
        { speaker = "骊姬", text = "毒物由曲沃送来，除了世子还有谁能下手？他既想杀妾，下一步自然便是弑君夺位。" },
        { speaker = "", text = "献公震怒，命东关五为主将、梁五为副将，率二百乘进逼曲沃。申生既不肯自辩，也不肯逃亡。" },
        { speaker = "申生", text = "父君年老，没有骊姬便寝食不安。我若申辩，使父君知道受骗，反而会令他余生痛苦。" },
        { speaker = "", text = "申生在新城自缢。门客杜原款欲向献公说明真相，却被梁五拘杀。骊姬随后又诬称重耳、夷吾参与毒谋。" },
        { speaker = "重耳", text = "兄长宁可受死也不愿伤父君之心，如今骊姬仍不肯罢手。蒲城虽有城墙，守军却远少于晋国中军。" },
        { speaker = "狐毛", text = "献公已经派寺人勃鞮率军来蒲。南门外两营相接，正面突围只会陷入包围。" },
        { speaker = "狐偃", text = "府后东墙外有一条旧道。墙脚虽窄，却能绕开南门围军；先让公子离开，我们再随后接应。" },
        { speaker = "勃鞮", text = "君侯有命，缉拿重耳回绛都问罪！蒲人若敢阻挡，一律以同谋论处！" },
        { speaker = "重耳", text = "父君之命，我本不敢违。但骊姬已经害死申生，此去绛都绝无分辩机会。我不能坐以待毙。" },
        { speaker = "狐毛", text = "城墙不可跨越，南门又有重兵。沿城内道路向东，穿过后墙暗口，再直奔地图东侧出口。" },
        { speaker = "狐偃", text = "勃鞮骑兵行动迅速，弓手又能隔两格封路。步卒先护住两侧，让重耳本人持续向出口移动。" },
        { speaker = "勃鞮", text = "堵住南门与东侧旧道！重耳若想越墙，就把他连人带衣一同留下！" },
        { speaker = "军令", text = "只有重耳本人进入（18，5）才算过关，狐毛或狐偃先到不会触发胜利。三名有名角色必须全部存活。" }
    },
    events = {
        { id = "rear_gate", trigger = "approach", position = {16, 5}, radius = 2,
          speaker = "狐偃", text = "后墙暗口就在前面！重耳先走，我和兄长挡住追兵。" }
    },
    victory = {
        { speaker = "勃鞮", text = "重耳已经攀出东墙！快追，绝不能让他逃到翟国！" },
        { speaker = "", text = "勃鞮追到墙边，挥戈斩断重耳衣袖。重耳落地后不敢停留，沿旧道向北疾走。" },
        { speaker = "狐偃", text = "公子已经脱险。蒲城守不住了，不必与晋军死战，诸人分路撤退，到翟国会合。" },
        { speaker = "重耳", text = "兄长含冤而死，今日我又被父君追杀。此后流亡在外，也绝不能忘记晋国百姓。" },
        { speaker = "", text = "重耳进入翟境，赵衰、胥臣、魏犨、狐射姑、颠颉、介子推、先轸等人先后赶来追随。" },
        { speaker = "赵衰", text = "公子能在危急中保全性命，便还有澄清国乱的一日。眼下先借翟军之力守住采桑道路。" },
        { speaker = "", text = "与此同时，晋献公又派贾华攻屈。夷吾与郤芮、吕饴甥、虢射弃城奔梁，贾华故意迟追，使其得以脱身。" },
        { speaker = "夷吾", text = "重耳去了翟国，我便前往梁国。只要离开晋境，日后仍有回国争位的机会。" },
        { speaker = "", text = "勃鞮回报重耳已逃，随即请求继续追击。晋军整队北上，直逼翟国采桑。" },
        { speaker = "下关提示", text = "第二十七回·下：重耳与翟军在采桑抵挡勃鞮，坚持十回合或击退勃鞮即可过关。" }
    },
    defeat = {
        { speaker = "狐偃", text = "公子未能冲出蒲城，追兵已经封死东侧旧道。晋国的内乱再无人能够挽回。" },
        { speaker = "", text = "重耳、狐毛或狐偃被击退，本关失败。" }
    }
}

gstage = {
    title_id = "EscapePuCity27", turn_limit = 16,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "ggggggggggggggggg~~",
            "gWWWWWWWfWWWWWWWWg~",
            "gWiiiiiiiiiiiiiiWg~",
            "gWiiiiiihiiiiiiiWg~",
            "gWiiiiiiiiiiiiiiWg~",
            "gWiiiiiiiiiiiiiifgg",
            "gWiiiiiiiiiiiiiiWgg",
            "gWiiiiiiiiiiiiiiWgg",
            "gWWWWWWWfWWWWWWWWgg",
            "ggggfffffwffffggggg",
            "gggfffffwfffffggggg",
            "ggggeffffwffffegggg",
            "gggfffffwfffffggggg",
            "gggggggggwggggggggg"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 3}, hero = "ChongEr27" },
            { position = {7, 4}, hero = "HuMao27" },
            { position = {11, 4}, hero = "HuYan27" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3000 }
}

function on_deploy(game)
    game:appoint_hero("ChongEr27", 1)
    game:appoint_hero("HuMao27", 1)
    game:appoint_hero("HuYan27", 1)
end

function on_begin(game)
    game:generate_unit("PuGuard27", 1, Enum.force.own, {8, 5})
    game:generate_unit("PuGuard27", 1, Enum.force.own, {10, 5})
    bodi_id = game:generate_unit("BoDi27", 1, Enum.force.enemy, {9, 10})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {8, 9})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {10, 9})
    game:generate_unit("JinGuard27", 1, Enum.force.enemy, {18, 6})
    game:generate_unit("JinCavalry27", 1, Enum.force.enemy, {6, 10})
    game:generate_unit("JinCavalry27", 1, Enum.force.enemy, {12, 10})
    game:generate_unit("JinArcher27", 1, Enum.force.enemy, {7, 11})
    game:generate_unit("JinArcher27", 1, Enum.force.enemy, {11, 11})
end

function on_update(game)
    if not rear_gate_spoken and game:is_unit_within("ChongEr27", {16, 5}, 2) then
        rear_gate_spoken = true
        game:push_cmd_speak(0, "后墙暗口已到！重耳本人继续向东侧出口撤离，其他人留后阻敌！")
        game:push_cmd_speak(bodi_id, "重耳就在东墙！骑兵绕到旧道，弓手封锁出口！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:is_unit_within("ChongEr27", {18, 5}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
