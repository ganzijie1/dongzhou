raid_started = false
qin_retreat = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoDun47", "XianKe47", "XunLinFu47", "XianDu47" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {
    { id = "qin_camp_northwest", name = "秦军行营", position = {11,9}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_camp_northeast", name = "秦军行营", position = {19,9}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_camp_command", name = "公子雍中军帐", position = {15,14}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "qin_camp_southwest", name = "秦军行营", position = {11,18}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_camp_southeast", name = "秦军行营", position = {19,18}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十七回·下",
    title = "弄玉吹箫双跨凤 赵盾背秦立灵公",
    battle_title = "令狐夜袭",
    objective = "晋军从秦营东门潜入，击杀公子雍并把秦军普通部队压至四人以内。秦营围栏整格不可跨越，东西两处各有两格营门；白乙丙、先蔑、士会依原著只能撤退，不可被击杀。我方四名具名将领任一被击退则失败。",
    map_asset = "m074.png",
    intro = {
        { speaker = "", text = "晋襄公去世后，太子夷皋年仅七岁。赵盾认为秦狄交侵、国事多难，不宜立幼主，主张迎回在秦国任亚卿的公子雍。" },
        { speaker = "赵盾", text = "公子雍年长好善，母亲杜祁有贤德；秦国又大而近。迎他为君，既能安定内政，也可修复秦晋旧好。" },
        { speaker = "狐射姑", text = "公子乐之母曾受文公宠爱，他本人正在陈国。陈与晋素来和睦，朝发夕至，比去秦国迎雍稳妥。" },
        { speaker = "赵盾", text = "陈小而远，不能为援；秦大而近，足以释怨。此事已定，命先蔑为正使、士会为副使入秦迎雍。" },
        { speaker = "荀林父", text = "夫人与太子都在国内，却向外国另迎新君，此事恐怕反复。士伯最好托病辞行，免得有去无回。" },
        { speaker = "先蔑", text = "国政尽在赵氏，怎会有变？既受迎君之命，我必把公子雍安然送回。" },
        { speaker = "", text = "狐射姑暗中派人赴陈迎公子乐。赵盾获知后，命门客公孙杵臼率家丁百人在郫地伏杀公子乐。" },
        { speaker = "", text = "狐射姑报复赵盾，指使弟弟狐鞫居杀死阳处父。赵盾依法诛狐鞫居，狐射姑逃往翟国，晋国军权尽归赵盾。" },
        { speaker = "秦康公", text = "先君曾两次安定晋国国君。如今晋人又迎公子雍，秦晋世代之好可以重修。白乙丙率车四百乘护送，不得有失。" },
        { speaker = "公子雍", text = "晋国卿士既以国君之礼来迎，我当返回故国安定社稷。此行仰仗康公与白乙将军护送。" },
        { speaker = "", text = "秦军渡过黄河，在令狐扎下大营。因为误以为前方晋军是来迎接公子雍，营中毫无戒备。" },
        { speaker = "", text = "与此同时，襄夫人穆嬴每日抱太子夷皋到朝堂哭诉，又到赵氏叩头，责问赵盾为何抛弃先君嫡子。" },
        { speaker = "穆嬴", text = "先君临终把夷皋托付给你，言语尚在耳边。若弃嫡子而另立外人，我母子只有一死！" },
        { speaker = "郤缺", text = "今日舍幼立长，等太子长成必生内乱。迎雍使者虽已出发，也应先立夷皋，再设法阻止秦军。" },
        { speaker = "", text = "赵盾与群臣畏惧穆嬴及其党羽，终于改立夷皋，是为晋灵公。边谍随即报告：秦军护送公子雍已经抵达河下。" },
        { speaker = "赵盾", text = "若迎公子雍，秦军便是宾客；如今既不接受，他们就是敌军。再派使者解释只会授人口实，不如抢先出兵。" },
        { speaker = "", text = "箕郑父留守绛都辅佐灵公。赵盾将中军，先克为副；荀林父统上军，先都统下军，三军屯于廑阴。" },
        { speaker = "先蔑", text = "迎公子雍本是赵孟主张，如今为何又立太子、发兵拒我？我受命迎雍，便认雍为主，绝不能背弃前言。" },
        { speaker = "荀林父", text = "我早劝你不要入秦。你终究是晋臣，若肯留下，赵孟未必追究。" },
        { speaker = "先蔑", text = "若贪恋故乡富贵而背弃所迎之君，何以立身？我回秦营，与公子雍共进退。" },
        { speaker = "赵盾", text = "先蔑不肯留下，明日秦军必然进逼。全军秣马饱食，衔枚潜行，三更从东门突入秦营，不给他们披甲结阵的机会。" },
        { speaker = "先克", text = "中军直取公子雍中军帐；我封锁东门内侧。荀伯压北翼，先都压南翼，得手后一路追至刳首。" },
        { speaker = "白乙丙", text = "晋军应当是来迎新君的，不必过分戒备。营门留两队值夜，其余军士解甲休息，明早再入晋境。" },
        { speaker = "军令", text = "从右侧开阔地接近秦营东门（25，13）与（25，14）。围栏格不可跨越；突入后优先击杀公子雍并压缩普通秦军，三名原著生还者不列入歼灭条件。" }
    },
    events = {
        { id = "east_gate_raid", trigger = "approach", position = {25,13}, radius = 2, speaker = "赵盾", text = "已到秦营东门！鼓角齐鸣，三军一同杀入，不给秦兵披甲上马的时间！" },
        { id = "central_tent", trigger = "approach", position = {15,14}, radius = 2, speaker = "公子雍", text = "晋军竟以迎君为名诱我至此，又乘夜袭营！护卫中军，向西门突围！" },
        { id = "west_pursuit", trigger = "approach", position = {6,13}, radius = 2, speaker = "白乙丙", text = "公子雍已陷乱军，秦阵无法再整。先蔑、士会随我从西门突围，退向黄河！" }
    },
    victory = {
        { speaker = "", text = "三更时分，晋军衔枚疾进，从秦营东门突然杀入。秦军在睡梦中惊醒，马不及披甲，人不及操戈，营内四处奔散。" },
        { speaker = "", text = "公子雍死于乱军之中。白乙丙死战打开西门通路，护送先蔑、士会冲出营寨，晋军一路追至刳首。" },
        { speaker = "先蔑", text = "赵孟可以背我，我不能背秦。公子雍既死，我也无颜再归晋国，愿留在秦国承受后果。" },
        { speaker = "士会", text = "我与士伯同受使命，他既奔秦，我不能独自回国求富贵。今日起与他同为秦臣。" },
        { speaker = "", text = "秦康公接纳先蔑与士会，拜二人为大夫。荀林父念同僚之义，请赵盾把两家妻子、财物完整送往秦国。" },
        { speaker = "赵盾", text = "从前贾季出奔，我也送还其家。先蔑、士会虽与我道路不同，家眷无罪，照数送往秦国，不得侵扰。" },
        { speaker = "", text = "此战晋军各部都有俘获，唯有先克部将蒯得贪进，反被秦军夺去五辆战车。先克欲依军法斩首，众将求情后改夺田禄。" },
        { speaker = "", text = "箕郑父、士谷、梁益耳对赵盾专权日益不满，暗中商议趁秦晋相持发动内乱。新的祸患已经埋下。" },
        { speaker = "军令", text = "令狐夜袭完成，获得7600金币。公子雍依原著阵亡；白乙丙、先蔑、士会撤退并在后续剧情继续登场。第47回完成。" }
    },
    defeat = {
        { speaker = "", text = "夜袭未能迅速突破秦营，晋军具名将领先被击退。秦军披甲结阵，公子雍在护送下继续向绛都推进。" }
    }
}

gstage = {
    title_id = "LinghuNightRaid47", turn_limit = 24,
    map = { blocked_edges = {}, size = {42, 28}, terrain = {
        "wwwwmFmfmgFfmfmFmfmfFgmfmFmgmfFfmgmFmfmgFf",
        "wwwwffgFfgffFffgfFgffgFfgffFffgfFgffgFfgff",
        "wwwwFmfmgFfmfmFmfmfFgmfmFmgmfFfmgmFmfmgFfm",
        "wwwwfgffgffgffgffgffgffgffgffgffgffgffgffF",
        "wwwwmfPPPPPPPPPPPPPPPPPPPPmfmfmgmfmfmgmfmf",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgffFf",
        "wwwwffPffgffgffgffgffgffgPfgffgffgffgffgff",
        "wwwwffPffgffgffgffgffgffgPfgffgffgffgffFff",
        "wwwwfgPfgffgffgffgffgffgfPgffgffgffgffgffF",
        "wwwwfgPfgffeffgffgfegffgfPgffgffgffgffgffg",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgffFf",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgffgf",
        "wwwwffPffgffgffgffgffgffgPfgffgffgffgffFff",
        "wwwwffgffgffgffgffgffgffgffgffgffgffgffgfF",
        "wwwwfgffgffgffgefgffgffgffgffgffgffgffgffg",
        "wwwwfgPfgffgffgffgffgffgfPgffgffgffgffgfFg",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgffgf",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgfFgf",
        "wwwwffPffgfegffgffgefgffgPfgffgffgffgffgfF",
        "wwwwffPffgffgffgffgffgffgPfgffgffgffgffgff",
        "wwwwfgPfgffgffgffgffgffgfPgffgffgffgffgfFg",
        "wwwwfgPfgffgffgffgffgffgfPgffgffgffgffgffg",
        "wwwwgfPgffgffgffgffgffgffPffgffgffgffgfFgf",
        "wwwwgfPPPPPPPPPPPPPPPPPPPPffgffgffgffgffgF",
        "wwwwffgffgffgffgffgffgffgffgffgffgffgffgff",
        "wwwwfFgffgFfgffFffgfFgffgFfgffFffgfFgffgFf",
        "wwwwfgfFgffgFfgffFffgfFgffgFfgffFffgfFgffg",
        "wwwwFgffgFfgffFffgfFgffgFfgffFffgfFgffgFfg"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {35,13}, hero = "ZhaoDun47" },
        { position = {35,16}, hero = "XianKe47" },
        { position = {38,12}, hero = "XunLinFu47" },
        { position = {38,17}, hero = "XianDu47" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 7600 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("GongZiYong47", 1, Enum.force.enemy, {15,14})
    game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {11,9})
    game:generate_unit("XianMie47", 1, Enum.force.enemy, {19,9})
    game:generate_unit("ShiHui47", 1, Enum.force.enemy, {19,18})
    game:set_unit_invulnerable("BaiYiBing26", true)
    game:set_unit_invulnerable("XianMie47", true)
    game:set_unit_invulnerable("ShiHui47", true)
    generate_many(game, "QinGuard47", {{25,13},{25,14},{14,12},{16,12},{14,16},{16,16},{9,12},{21,12}}, Enum.force.enemy)
    generate_many(game, "QinCavalry47", {{8,8},{22,8},{8,19},{22,19},{12,14},{18,14}}, Enum.force.enemy)
    generate_many(game, "QinArcher47", {{10,7},{20,7},{10,20},{20,20},{13,10},{17,18}}, Enum.force.enemy)
    generate_many(game, "JinGuard47", {{33,12},{33,14},{33,16},{36,11},{36,18}}, Enum.force.own)
    generate_many(game, "JinCavalry47", {{37,14},{37,16},{40,13},{40,17}}, Enum.force.own)
    generate_many(game, "JinArcher47", {{34,10},{34,19},{39,11},{39,18}}, Enum.force.own)
end

local function qin_regular_alive(game)
    return game:get_num_units_alive("QinGuard47") + game:get_num_units_alive("QinCavalry47")
        + game:get_num_units_alive("QinArcher47")
end

function on_update(game)
    if not raid_started and (game:is_unit_within("ZhaoDun47", {25,13}, 2)
        or game:is_unit_within("XianKe47", {25,14}, 2)) then
        raid_started = true
        game:push_cmd_speak(0, "晋军已经冲入秦营东门！秦军仓促惊醒，无法在营门内及时完成整队。")
    end
    if raid_started and not qin_retreat and not game:has_unit("GongZiYong47") and qin_regular_alive(game) <= 4 then
        qin_retreat = true
        game:push_cmd_speak(0, "公子雍已死，白乙丙护着先蔑、士会从西门突围。晋军追至刳首后收兵。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if qin_retreat then return Enum.status.victory end
    return Enum.status.undecided
end
