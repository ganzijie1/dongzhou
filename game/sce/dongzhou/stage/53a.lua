gally_hold_position = true
gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChuZhuangWang51", "GongZiYingQi51", "GongZiCe51", "QuWu53" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十三回·上",
    title = "楚庄王纳谏复陈 晋景公出师救郑",
    battle_title = "株林讨逆",
    objective = "楚庄王率军由西门进入夏氏宅院，击退夏征舒并将其生擒。宅墙是不可跨越的连续W地形，双格西门为可通行G。夏征舒被击退先视为被俘，战后才按原著车裂；任一我方具名将领被击退则失败。",
    map_asset = "m083.png",
    intro = {
        { speaker = "", text = "泄冶见陈灵公、孔宁、仪行父在朝堂上以夏姬贴身衣物相互戏谑，整衣持笏，再次进入朝门进谏。" },
        { speaker = "泄冶", text = "君臣以敬为本，男女以别为礼。如今朝堂秽语公行，敬与别都已荡然，这是亡国之道！" },
        { speaker = "陈灵公", text = "卿不必再说，寡人已经知道羞愧，今后自当悔改。" },
        { speaker = "", text = "泄冶出门又当面斥责孔宁、仪行父：臣子不但不能掩盖君过，反而诱导国君并四处宣扬，何以为天下表率。" },
        { speaker = "孔宁", text = "泄冶一日不闭口，主公便不能再往株林。要让他永不进言，只有使他再也开不了口。" },
        { speaker = "仪行父", text = "死人自然无口。请主公传旨诛杀泄冶，往后株林之游便无人阻挠。" },
        { speaker = "", text = "陈灵公不肯亲自下令，却默许二人自行处置。孔宁、仪行父重金收买刺客，在泄冶入朝途中将他杀害。" },
        { speaker = "", text = "国人都以为刺杀出自陈侯旨意。泄冶死后，君臣三人更加肆无忌惮，《株林》之诗也在陈国流传。" },
        { speaker = "", text = "夏征舒渐渐长成，身材魁伟，勇力过人而善射。陈灵公为讨好夏姬，让他承袭父职，担任陈国司马。" },
        { speaker = "夏姬", text = "这是陈侯赐予你的官爵。你只管尽忠国事，不必因家中流言分心。" },
        { speaker = "", text = "一日陈灵公与孔宁、仪行父再到株林，夏征舒设宴款待。三人酒后竟以征舒生父为题，当面作恶毒笑谈。" },
        { speaker = "陈灵公", text = "征舒身形高大，倒有几分像仪大夫，莫非是你所生？" },
        { speaker = "仪行父", text = "他两眼炯炯更像主公，还是主公所生才对。" },
        { speaker = "", text = "夏征舒在屏风后听得清楚，怒不可遏。他锁住内室，命亲兵包围夏府，亲自披甲持弓杀入前院。" },
        { speaker = "夏征舒", text = "围住前后门户，一个也不许走！今日要拿的不是国君，而是辱我父母、坏我家门的淫贼！" },
        { speaker = "", text = "陈灵公奔向东侧马厩，先避过一箭，却在退出马厩时被夏征舒第二箭射中心口，当场身亡。" },
        { speaker = "", text = "孔宁、仪行父趁夏征舒追赶陈侯，从西侧射圃的狗洞逃出，连家也不敢回，赤身奔往楚国。" },
        { speaker = "", text = "夏征舒拥兵入城，谎称陈侯暴病而亡，立世子午为陈成公。成公心中怨恨，却无力制伏掌兵的夏征舒。" },
        { speaker = "", text = "楚国原本派使者约陈侯赴辰陵会盟，途中听闻陈乱而返。孔宁、仪行父也到郢都，只说夏征舒弑君，不提自己诱君之罪。" },
        { speaker = "屈巫", text = "夏征舒弑君，陈国又无力自讨。大王应当出兵陈国，诛其首恶，以正诸侯之法。" },
        { speaker = "孙叔敖", text = "征舒之罪确实当讨。但大军入陈须明示只诛一人，不可借机扰害无罪百姓。" },
        { speaker = "楚庄王", text = "传檄陈国：罪有专归，其余臣民安居勿扰。楚军所过秋毫无犯，只取夏征舒。" },
        { speaker = "", text = "陈国百姓早已归罪夏征舒，无心为他守城。楚军一路安抚居民，直入陈都，如行无人之境。" },
        { speaker = "辕颇", text = "楚王为陈国讨罪，并非灭国。夏征舒已经逃往株林，请大王以臣为向导，尽快包围夏氏。" },
        { speaker = "楚庄王", text = "公子婴齐留一部守住陈都，其余诸军随寡人赶往株林。不可让征舒携母逃入郑境。" },
        { speaker = "夏征舒", text = "楚军来得太快，宅院已被包围。亲兵守住西门，我去收拾家财，寻找机会护送母亲突围。" },
        { speaker = "军令", text = "从西侧进军，清除宅门守军后进入夏氏宅院，击退夏征舒。墙格W不可进入，双格西门G可通行；夏征舒被击退即被俘。" }
    },
    events = {
        { id = "zhulin_gate", trigger = "approach", position = {25,14}, radius = 3, speaker = "屈巫", text = "西门就在前方。两翼封住院墙，主力由门内直取夏征舒，不许伤害宅中无关之人！" }
    },
    victory = {
        { speaker = "", text = "楚军封住株林各条道路，夏征舒未能逃离宅院，被楚军生擒，囚入后车。" },
        { speaker = "楚庄王", text = "将征舒押回陈都栗门，明正其弑君之罪。其他家人不得妄加杀害。" },
        { speaker = "", text = "楚军又在园中找到夏姬。楚庄王一度想纳她入后宫，屈巫立即以讨罪不可终于贪色相劝。" },
        { speaker = "屈巫", text = "大王兴兵是为讨逆，起于义而终于色，便会使天下怀疑出兵本意。霸主不应如此。" },
        { speaker = "楚庄王", text = "子灵之言有理。寡人既称吊民伐罪，便不能夺人妻女。放夏姬自择去处。" },
        { speaker = "", text = "公子侧继而请求娶夏姬，屈巫又称她屡次招致家国祸乱。楚庄王最终将夏姬赐给新近丧偶的连尹襄老。" },
        { speaker = "", text = "楚庄王在栗门将夏征舒车裂，随后收取陈国版图，暂置为楚县，任公子婴齐为陈公。" },
        { speaker = "军令", text = "株林讨逆完成，获得800金币。夏征舒按原著死亡；下一关转入申叔时劝谏、复封陈国以及楚军围郑。" }
    },
    defeat = {{ speaker = "", text = "楚军具名将领在株林宅门前被击退，夏征舒趁乱逃往郑国，讨逆失败。" }}
}

gstage = {
    title_id = "CaptureAtZhulin53", turn_limit = 22,
    map = { blocked_edges = {}, size = {46,30}, terrain = {
        "gFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfF",
        "FFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFF",
        "fFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfF",
        "FFgffgffgffgffgffgffgffgffgffgffgffgffgffgfFFF",
        "fFFFfgFfFffFfFgffgffgffgffgffgffgffgffgffgfFgF",
        "FFfFfFffFfFffFfffffffffffWWWWWWWWWWWWWWWWWWWFF",
        "FFFfgFfFffFfFgffgffgffgffWiiiiiiiiiiiiiiiiiWfF",
        "FFFfFffFfFgfFgffgffgffgffWiiiiiiiiiiiiiiiiiWFF",
        "fFFfFfFffFfFfffffffffffffWiiiiiiiiiiiiiiiiiWfF",
        "FFfFffFfFgfFgFfgffgffgffgWiiiiiiiiiiiiiiiiiWFF",
        "FFFFfFgfFgFfgFfgffgffgffgWiiiiiiiiiiiiiiiiiWfF",
        "FFFffFfFffFfFffffffffffffWiiiiiiiiiiiiiiiiiWFF",
        "fFFfFgfFgFfgFfgffgffgffgfWiiiiiiiiiiiiiiiiiWgF",
        "wwwwwwwwwwwwwwgffgffgffgfWiiiiiiiiiiiiiiiiiWFF",
        "wwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiWww",
        "wwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiWww",
        "FFFfgFfFffFfFgwwwwwwwwwwwWiiiiiiiiiiiiiiiiiWww",
        "FFFfFffFfFffFffffffffffffWiiiiiiiiiiiiiiiiiWFF",
        "gFFgFfFffFfFgffgffgffgffgWiiiiiiiiiiiiiiiiiWfF",
        "FFfFffFfFgfFgFfgffgffgffgWiiiiiiiiiiiiiiiiiWFF",
        "FFFFfFffFfFffFfffffffffffWiiiiiiiiiiiiiiiiiWfF",
        "FFFffFfFgfFgFfgffgffgffgfWiiiiiiiiiiiiiiiiiWFF",
        "fFFfFgfFgFfgFfgffgffgffgfWiiiiiiiiiiiiiiiiiWgF",
        "FFffFfFffFfFfffffffffffffWiiiiiiiiiiiiiiiiiWFF",
        "fFFFgfFgFfgFfFffgffgffgffWiiiiiiiiiiiiiiiiiWfF",
        "FFfFgFfgFfFffFffgffgffgffWWWWWWWWWWWWWWWWWWWFF",
        "fFFffffffffffffffffffffffffffffffffffffffffFfF",
        "FFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFF",
        "gFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfFFFgFFFfFFFfF",
        "FFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFFfFFF",
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {7,15}, hero = "ChuZhuangWang51" },
        { position = {9,13}, hero = "GongZiYingQi51" },
        { position = {9,17}, hero = "GongZiCe51" },
        { position = {6,12}, hero = "QuWu53" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 8000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
    game:generate_unit("XiaZhengShu53", 1, Enum.force.enemy, {36,15})
    many(game, "ChuExpeditionGuard53", {{5,14},{5,16},{8,11},{8,19},{11,12},{11,18}}, Enum.force.own)
    many(game, "ChuExpeditionCavalry53", {{4,10},{4,20},{10,9},{10,21}}, Enum.force.own)
    many(game, "ChuExpeditionArcher53", {{3,13},{3,17},{12,10},{12,20}}, Enum.force.own)
    many(game, "XiaHouseGuard53", {{26,13},{26,16},{29,11},{29,19},{33,13},{33,17},{38,12},{38,18}}, Enum.force.enemy)
    many(game, "XiaHouseArcher53", {{28,8},{28,22},{34,10},{34,20},{40,14},{40,16}}, Enum.force.enemy)
end
function on_update(game) end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("XiaZhengShu53") then return Enum.status.victory end
    return Enum.status.undecided
end
