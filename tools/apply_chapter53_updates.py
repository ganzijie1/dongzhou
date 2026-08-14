import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def rows(name):
    data = json.loads((ROOT / "assets/lzc/map_sources" / name).read_text(encoding="utf-8"))
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE_53A = r'''gally_hold_position = true
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
__ROWS__
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
'''


STAGE_53B = r'''huangmen_cleared = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChuZhuangWang51", "GongZiYingQi51", "GongZiCe51", "LeBo51" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十三回·下",
    title = "楚庄王纳谏复陈 晋景公出师救郑",
    battle_title = "皇门破郑",
    objective = "楚军清除皇门守军后，由乐伯穿过双格皇门进入城内坐标（31，16）周围两格，触发郑襄公牵羊请降。连续城墙均为不可通行W，皇门为可通行G。郑襄公、公子去疾不可被击退；任一我方具名将领被击退则失败。",
    map_asset = "m084.png",
    intro = {
        { speaker = "", text = "楚庄王灭陈后，出使齐国归来的申叔时没有称贺。庄王遣人责问，他请求入见，以“蹊田夺牛”设喻。" },
        { speaker = "申叔时", text = "有人牵牛踩坏田禾，田主因怒夺走整头牛。践田固然有罪，夺牛却远远过分，大王将如何断案？" },
        { speaker = "楚庄王", text = "应当薄责牵牛者，再归还其牛。损伤几行田禾，不足以夺走别人赖以为生的牛。" },
        { speaker = "申叔时", text = "夏征舒有弑君之罪，大王诛其身足矣；如今却兼取陈国，这与蹊田夺牛有什么区别？" },
        { speaker = "楚庄王", text = "善哉！寡人明于断狱，却险些昧于断国。立即迎回陈君，将版图归还陈国。" },
        { speaker = "", text = "陈大夫辕颇在归途中遇到从晋国返回的陈成公，迎他复位。公子婴齐交还陈国版图，率楚军归国。" },
        { speaker = "", text = "孔宁归陈不久，患狂疾投水而死；仪行父也在噩梦之后暴病身亡。陈国株林旧党至此相继凋零。" },
        { speaker = "", text = "公子婴齐因陈公之封被撤，请求申吕之田作为补偿。屈巫以那是楚国北方御晋赋税来源为由阻止。" },
        { speaker = "", text = "楚庄王见陈国已经归附，而郑国仍追随晋国，决定倾三军两广之众再伐郑。孙叔敖认为非大军不能成事。" },
        { speaker = "唐狡", text = "郑国不值得劳动全军开路。请给臣百人先行一日，扫清道路，为大军准备宿营之地。" },
        { speaker = "", text = "唐狡率百人一路力战，所当者破。楚军直抵郑郊，楚庄王才知道这位先锋正是绝缨会上被宽赦的人。" },
        { speaker = "唐狡", text = "绝缨会牵美人衣袖者就是臣。大王不追究死罪，臣今日舍命报恩，不能再以此求取赏赐。" },
        { speaker = "", text = "唐狡当夜离营而去，不知所终。楚军攻破郊关，在郑都四面筑起长围，连续攻打十七日。" },
        { speaker = "", text = "郑襄公依仗晋国必来救援，不肯讲和。郑军伤亡日增，城东北角终于崩塌数十丈。" },
        { speaker = "楚庄王", text = "城中哭声震地。传令全军后退十里，让郑人知道楚军既有威，也愿意施德。" },
        { speaker = "公子婴齐", text = "城墙已经崩陷，正可一鼓而入，为何反而退兵？" },
        { speaker = "楚庄王", text = "郑国只知我威，未知我德。暂退观察其是否请降，再决定进退。" },
        { speaker = "", text = "郑襄公误以为晋国援军已经来到，立即发动百姓抢修城墙，男女都登城巡守，仍无请降之意。" },
        { speaker = "", text = "楚庄王再次合围。郑都又坚守近三个月，城内粮箭耗尽，军民再无力支撑。" },
        { speaker = "乐伯", text = "皇门守军已经疲惫。臣愿率锐士先登，劈开城门，为三军打通入城道路！" },
        { speaker = "楚庄王", text = "准你从皇门进攻。城破之后不许抢掠，不许侵害百姓，违令者军法从事。" },
        { speaker = "郑襄公", text = "晋援迟迟不至，城中已经不能再守。若皇门被破，只能肉袒牵羊，保全郑国宗祀。" },
        { speaker = "公子去疾", text = "臣陪君上守在城内。楚军若肯存郑，臣愿留在楚营为质，使两国盟约有所凭信。" },
        { speaker = "军令", text = "清除皇门守军后，让乐伯穿过双格皇门，到达城内（31，16）周围两格。城墙W不可跨越；郑国两名具名角色不可被击退。" }
    },
    events = {
        { id = "huangmen_gate", trigger = "approach", position = {28,16}, radius = 3, speaker = "乐伯", text = "皇门就在眼前！盾兵压住城头弓手，随我劈开门路，楚军不得四散抢掠！" }
    },
    victory = {
        { speaker = "", text = "乐伯率锐士从皇门先登，楚军随即打开城门。三军依照庄王军令整队入城，没有抢掠百姓。" },
        { speaker = "", text = "郑襄公肉袒牵羊，在大路上迎接楚庄王，请求保留郑国宗庙，甘愿降为附庸。" },
        { speaker = "郑襄公", text = "孤不能服事大国，使君王劳师至此。郑国存亡死生，唯大王之命；只求不绝先君祭祀。" },
        { speaker = "公子婴齐", text = "郑国力尽才降，赦免之后仍会再叛。不如就此灭郑，免得将来重复用兵。" },
        { speaker = "楚庄王", text = "若申叔时在此，又要用蹊田夺牛讥我。传令退军三十里，接受郑国盟约。" },
        { speaker = "", text = "郑襄公亲至楚营谢罪请盟，并留下弟弟公子去疾为质。楚军北行，驻扎在郔地。" },
        { speaker = "", text = "斥候来报：晋景公任命荀林父为主将、先谷为副，出动战车六百乘救郑，已经渡过黄河。" },
        { speaker = "孙叔敖", text = "郑国既已归附，楚军也连续作战疲惫。再与晋国争胜没有必要，不如完整撤军。" },
        { speaker = "伍参", text = "楚军一见晋师便退，郑国必以为楚不如晋。晋军号令不一，看似强大，实际上可以击败。" },
        { speaker = "", text = "楚庄王让众将把主战或主退写在掌中。虞邱、襄老等少数人主退，公子婴齐、公子侧、乐伯、养由基等二十余人主战。" },
        { speaker = "楚庄王", text = "老臣之见与令尹相同，原本应当撤军。但若就此把郑国重新让给晋国，楚国三月之战便全无意义。" },
        { speaker = "伍参", text = "荀林父初掌中军，先谷刚愎，各卿族又各行其意。大王亲统一国之师，何必畏惧号令不一的晋军？" },
        { speaker = "楚庄王", text = "寡人虽不善将兵，也不至于在晋国诸臣之下。通知孙叔敖，全军车辕改向北方，进抵管城待敌！" },
        { speaker = "", text = "楚军连夜转向北进，晋国六百乘也正向郑境推进。两国主力即将在邲地相遇，胜负留待下回。" },
        { speaker = "军令", text = "皇门破郑完成，获得1200金币。郑襄公、公子去疾均按史实存活；下一回将进入晋楚主力决战。" }
    },
    defeat = {{ speaker = "", text = "楚军具名将领在皇门总攻中被击退，郑军稳住城防，围城战功亏一篑。" }}
}

gstage = {
    title_id = "BreachHuangmen53", turn_limit = 28,
    map = { blocked_edges = {}, size = {52,34}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {8,17}, hero = "ChuZhuangWang51" },
        { position = {12,11}, hero = "GongZiYingQi51" },
        { position = {12,23}, hero = "GongZiCe51" },
        { position = {20,16}, hero = "LeBo51" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 12000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
    game:generate_unit("ZhengXiangGong52", 1, Enum.force.enemy, {44,16})
    game:generate_unit("GongZiQuJi52", 1, Enum.force.enemy, {42,18})
    game:set_unit_invulnerable("ZhengXiangGong52", true)
    game:set_unit_invulnerable("GongZiQuJi52", true)
    many(game, "ChuSiegeGuard53", {{7,14},{7,20},{10,14},{10,20},{14,13},{14,21},{18,13},{18,20}}, Enum.force.own)
    many(game, "ChuSiegeCavalry53", {{5,11},{5,23},{11,9},{11,25},{17,10},{17,24}}, Enum.force.own)
    many(game, "ChuSiegeArcher53", {{8,10},{8,24},{15,11},{15,23},{21,12},{21,21}}, Enum.force.own)
    many(game, "ZhengHuangmenGuard53", {{27,15},{27,18},{29,15},{29,18},{31,16},{31,17}}, Enum.force.enemy)
    many(game, "ZhengCityGuard53", {{34,12},{34,21},{38,10},{38,23},{42,12},{42,22},{46,14},{46,20}}, Enum.force.enemy)
    many(game, "ZhengCityArcher53", {{30,10},{30,23},{35,15},{35,18},{40,14},{40,20},{47,11},{47,24}}, Enum.force.enemy)
end
function on_update(game)
    if not huangmen_cleared and not game:has_unit("ZhengHuangmenGuard53") then
        huangmen_cleared = true
        game:push_cmd_speak(0, "皇门守军已经被击溃！乐伯立即穿过城门进入城内，迫使郑襄公请降。")
    end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if huangmen_cleared and game:is_unit_within("LeBo51", {31,16}, 2) then return Enum.status.victory end
    return Enum.status.undecided
end
'''


def write_stages():
    (ROOT / "game/sce/dongzhou/stage/53a.lua").write_text(
        STAGE_53A.replace("__ROWS__", rows("m083_ch53a_manifest.json")), encoding="utf-8")
    (ROOT / "game/sce/dongzhou/stage/53b.lua").write_text(
        STAGE_53B.replace("__ROWS__", rows("m084_ch53b_manifest.json")), encoding="utf-8")


def update_config():
    path = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "QuWu53", class = "Strategist", stat = {93, 88, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "XiaZhengShu53", class = "Archer", stat = {88, 96, 84, 90, 88}, model = "archer-1-blue" }
        ,{ id = "ChuExpeditionGuard53", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-red" }
        ,{ id = "ChuExpeditionCavalry53", class = "Cavalry", stat = {88, 94, 84, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "ChuExpeditionArcher53", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-red" }
        ,{ id = "XiaHouseGuard53", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "XiaHouseArcher53", class = "Archer", stat = {83, 91, 84, 86, 84}, model = "archer-1-blue" }
        ,{ id = "ChuSiegeGuard53", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-red" }
        ,{ id = "ChuSiegeCavalry53", class = "Cavalry", stat = {89, 95, 85, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "ChuSiegeArcher53", class = "Archer", stat = {86, 93, 88, 90, 88}, model = "archer-1-red" }
        ,{ id = "ZhengHuangmenGuard53", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "ZhengCityGuard53", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "ZhengCityArcher53", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(path, '"50c", "51", "52" }', '"50c", "51", "52", "53a", "53b" }')


def update_gui():
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m083.png"] = (46, 30, 48)
_LARGE_BATTLE_MAPS["m084.png"] = (52, 34, 48)

HERO_LABELS.update({
    "QuWu53": "屈巫", "XiaZhengShu53": "夏征舒",
    "ChuExpeditionGuard53": "楚国甲士", "ChuExpeditionCavalry53": "楚国骑兵", "ChuExpeditionArcher53": "楚国弓手",
    "XiaHouseGuard53": "夏氏家兵", "XiaHouseArcher53": "夏氏弓手",
    "ChuSiegeGuard53": "楚军攻城卒", "ChuSiegeCavalry53": "楚军游骑", "ChuSiegeArcher53": "楚军强弓",
    "ZhengHuangmenGuard53": "皇门守卒", "ZhengCityGuard53": "郑都守军", "ZhengCityArcher53": "郑都弓手",
})
HERO_BIOS.update({
    "QuWu53": "楚国公族大夫，字子灵，文武兼备。伐陈时劝楚庄王不可纳夏姬，后来受封申公。",
    "XiaZhengShu53": "陈国司马，夏御叔与夏姬之子，勇力善射。因陈灵公在株林辱及父母，射杀灵公，后被楚军擒获车裂。",
})
PORTRAIT_INDEX_BY_HERO.update({"QuWu53": 45, "XiaZhengShu53": 24})
SPEAKER_PORTRAIT_INDEX.update({
    "陈灵公": 9, "孔宁": 38, "仪行父": 31, "泄冶": 49, "夏征舒": 24, "夏姬": 12,
    "屈巫": 45, "孙叔敖": 45, "楚庄王": 8, "辕颇": 42, "申叔时": 49,
    "唐狡": 35, "乐伯": 34, "公子婴齐": 35, "郑襄公": 7, "公子去疾": 45, "伍参": 31,
})
HISTORICAL_DEATH_HEROES.add("XiaZhengShu53")

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_prior_test():
    path = ROOT / "rl/chapter52_test.py"
    replace_once(path, 'assert \'"50b", "50c", "51", "52" }\' in config',
                 'assert \'"50b", "50c", "51", "52", "53a", "53b" }\' in config')


def main():
    write_stages(); update_config(); update_gui(); update_prior_test()
    print("Chapter 53 stages, config, GUI metadata, and prior regression anchor updated.")


if __name__ == "__main__":
    main()
