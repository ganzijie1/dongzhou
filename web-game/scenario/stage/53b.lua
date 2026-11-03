huangmen_cleared = false

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
        "FgfFmFffFgFfmFfFmgFfFffFgFffFfFfgFfFffFfFgfFfFffFgFf",
        "fFfmFfFmfFfFffFmFffFfFggFfFffFgFffFfFfgFfFffFfFgfFfF",
        "FfFfgFmFffFfFgmFfFmfFgFffFfFggFfFffFgFffFfFfgFfFffFf",
        "fFggfmfffmggfmfffmggffffffggWWWWWWWWWWWWWWWWWWWWWWWF",
        "mgFfmfffmgffmfffmgffffffggffWiiiiiiiiiiiiiiiiiiiiiWf",
        "FffmffgmfffmffgmffffffggffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFmfggmfffmfggmfffmfggffffffWiiiiiiiiiiiiiiiiiiiiiWF",
        "FfFgffffffggffffffggffffffggWiiiiiiiiiiiiiiiiiiiiiWg",
        "gFffffffggffffffggffffffggffWiiiiiiiiiiiiiiiiiiiiiWF",
        "ffFfffggffffffggffffffggffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "FfffggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFggffffffggffffffggffffffggWiiiiiiiiiiiiiiiiiiiiiWF",
        "FgFfffffggffffffggffffffggffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFffffggffffffggffffffggffffWiiiiiiiiiiiiiiiiiiiiiWF",
        "ffFfggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "FfgwwwwwwwwwwwwwwwwwwwwwwwwwWiiiiiiiiiiiiiiiiiiiiiWg",
        "gFfwwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiiWF",
        "FfFwwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiiWf",
        "fFffggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWF",
        "ffFgffffffggffffffggffffffggWiiiiiiiiiiiiiiiiiiiiiWg",
        "FgffffffggffffffggffffffggffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFffffggffffffggffffffggffffWiiiiiiiiiiiiiiiiiiiiiWF",
        "FfFfggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFggffffffggffffffggffffffggWiiiiiiiiiiiiiiiiiiiiiWF",
        "ggFfffffggffffffggffffffggffWiiiiiiiiiiiiiiiiiiiiiWf",
        "FfffffggffffffggffffffggffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFffggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWF",
        "FfFgffffffggffffffggffffffggWiiiiiiiiiiiiiiiiiiiiiWg",
        "gFffffffggffffffggffffffggffWiiiiiiiiiiiiiiiiiiiiiWF",
        "ffFfffggffffffggffffffggffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "FfffggffffffggffffffggffffffWiiiiiiiiiiiiiiiiiiiiiWf",
        "fFggFfFffFgFffFfFfgFfFffFfFgWWWWWWWWWWWWWWWWWWWWWWWF",
        "FgFffFfFggFfFffFgFffFfFfgFfFffFfFgfFfFffFgFffFfFggFf",
        "fFfFffFgFffFfFggFfFffFgFffFfFfgFfFffFfFgfFfFffFgFffF",
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
