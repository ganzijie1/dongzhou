yu_returned = false
yu_gong_id = -1
bailixi_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "LiKe25", "XunXi25" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "yu_castle", name = "虞国城池", position = {9, 0}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "yu_storehouse", name = "虞国府库", position = {6, 2}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "yu_south_gate", name = "虞都南门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "jin_hidden_camp", name = "晋军伏营", position = {15, 10}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十五回·下",
    title = "智荀息假途灭虢 穷百里饲牛拜相",
    battle_title = "箕山袭虞",
    objective = "里克、荀息从南门攻入虞都并占领最上方城池；二人任一被击退则失败",
    map_asset = "m043.png",
    intro = {
        { speaker = "", text = "灭虢之后，里克托病驻军城外一个多月。虞公不断馈送药物，丝毫没有察觉晋军已经逼近国都。" },
        { speaker = "晋献公", text = "寡人此来只说接应伐虢之师。虞公贪图与晋国结好，必会亲自出城相迎。" },
        { speaker = "荀息", text = "请主公再约虞公到箕山较猎。只要他带走城中甲兵、坚车良马，里克便可从南门夺城。" },
        { speaker = "虞公", text = "晋侯亲来相谢，正合寡人之愿。明日尽出精甲良马，让晋人看看虞国军威！" },
        { speaker = "宫之奇", text = "臣已经携族远去，虞国再无人敢进逆耳之言。唇既亡，齿寒之日就在眼前。" },
        { speaker = "百里奚", text = "君上既决意出猎，臣只能随行。若真有变故，还望主公立即回城，不可再贪围猎胜负。" },
        { speaker = "", text = "虞公倾城出动，从辰时猎到申时。虞都忽然火起，晋献公仍劝他再打一围，以拖延回军。" },
        { speaker = "里克", text = "城中精兵都在箕山，守军并不知道晋虞已经反目。先夺南门，再沿城内道路直取北面城池。" },
        { speaker = "荀息", text = "虞公会在第四回合返回。我们不是来屠城，只需控制城池和府库，守军放下兵器便准其归家。" },
        { speaker = "虞都守将", text = "晋军不是还驻在虢境吗？南门外为何出现大队甲士！立即关闭城门，向箕山告急！" },
        { speaker = "里克", text = "城门已经来不及关闭。前队直取门楼，弓手随后进入；城墙不可跨越，不要在两翼徒耗兵力。" },
        { speaker = "军令", text = "击退虞都守将后，让任一我军单位进入最上方城池即可胜利。第四回合虞公与百里奚从南方回军。" }
    },
    events = {
        { id = "yu_return", trigger = "turn", turn = 4,
          speaker = "虞公", text = "城楼上已经换成晋军旗号！全军立即回城，夺回南门！" },
        { id = "yu_castle_taken", trigger = "occupy", position = {9, 0},
          speaker = "里克", text = "虞国城池已经控制，府库与百姓俱安。各军停止追击，等待晋侯处置虞公。" }
    },
    victory = {
        { speaker = "里克", text = "虞都已在晋军掌握之中。前蒙君假我以道，今再假我以国，敬谢明赐！" },
        { speaker = "虞公", text = "悔不听宫之奇之谏！百里奚，当日他劝我拒绝借道，你为何一言不发？" },
        { speaker = "百里奚", text = "君不肯听宫之奇，又怎会听我？臣不言，正是为了留身随君直到今日。" },
        { speaker = "舟之侨", text = "主公弃虢失策在前，如今进退无路，不如归晋。晋侯或许仍会保全君位与性命。" },
        { speaker = "晋献公", text = "寡人此来，只为取回璧马的价值。虞君暂居后车，百里奚若愿相随，也不必阻拦。" },
        { speaker = "荀息", text = "臣的计策已经完成。如今请把璧还入府库，把马牵回马厩；晋国两件至宝果然只是暂寄。" },
        { speaker = "", text = "百里奚不肯抛弃虞公，随他一同入晋。有人劝其离开，他答道：受禄既久，正该在亡国时尽忠。" },
        { speaker = "", text = "百里奚本是虞国人，字井伯。早年家贫，妻子杜氏杀掉家中唯一母鸡，又拆门闩烧火为他饯行。" },
        { speaker = "杜氏", text = "男子志在四方，怎能守着妻子坐困？你尽管出游求仕，我自会设法养活孩子。" },
        { speaker = "", text = "百里奚先到齐国，穷困乞食于铚，结识蹇叔；又曾为周王子颓养牛，因蹇叔识其无能而及时离开。" },
        { speaker = "蹇叔", text = "王子颓志大才疏，身边尽是谗谄之人，迟早会因非分之想败亡。不可轻易把自己托付给他。" },
        { speaker = "", text = "二人后来同到虞国。蹇叔访友宫之奇，宫之奇荐百里奚为中大夫；蹇叔却认为虞公见小自用。" },
        { speaker = "百里奚", text = "我久困贫贱，如鱼困在陆地，急需一勺水救命。明知虞公不足与有为，也只能暂且出仕。" },
        { speaker = "", text = "虞国灭亡后，晋国把百里奚作为陪嫁臣仆送往秦国。百里奚不堪受辱，途中逃走，经宋境转往楚国。" },
        { speaker = "", text = "宛地猎人怀疑他是奸细，将其捆缚。百里奚自称善于养牛，猎人试用之后，牛群果然日益肥壮。" },
        { speaker = "楚成王", text = "使牲畜按时饮食、爱惜其力，使心与牛合一。这道理不只可用于牛，也可以用来养马。" },
        { speaker = "", text = "楚王不知道百里奚的真正才干，只让他到南海牧马。秦穆公得知晋国陪嫁名册缺少此人，便询问公孙枝。" },
        { speaker = "公孙枝", text = "百里奚知虞公不可谏而不谏，是智；亡国后随主入晋而不肯臣晋，是忠。他有经世之才。" },
        { speaker = "秦穆公", text = "若以重金向楚国求贤，楚王必会察觉他的价值而留下。怎样才能让百里奚归秦？" },
        { speaker = "公孙枝", text = "只说他是逃亡的陪嫁奴仆，用五张黑羊皮贱价赎回。楚国不知其贤，才会放人。" },
        { speaker = "", text = "楚王果然以囚车交人。百里奚看出秦君求他的本意，毫不忧惧；进入秦境后，公孙枝先解其囚再迎入朝。" },
        { speaker = "秦穆公", text = "先生已经七十岁，可惜太老了。" },
        { speaker = "百里奚", text = "若要追鸟搏兽，臣确实老了；若要坐而谋划国事，臣还年轻。姜尚八十遇文王，臣还早了十年。" },
        { speaker = "秦穆公", text = "秦国介于戎狄，不参与中原会盟。先生有何良策，使秦国不落在诸侯之后？" },
        { speaker = "百里奚", text = "雍岐是周室兴起之地。秦国可先以德抚、以力征，兼并西戎，聚其地与民，再据山川之险临中原。" },
        { speaker = "", text = "秦穆公与百里奚连续交谈三日，言无不合，感叹自己得到井伯如同齐桓公得到管仲。" },
        { speaker = "秦穆公", text = "从今日起，拜先生为上卿，总理秦国国政。五张羊皮赎来的不是奴仆，而是秦国霸业！" },
        { speaker = "", text = "秦人因此称百里奚为“五羖大夫”。百里奚却辞让上卿之位，准备推荐一位旧友代替自己。" },
        { speaker = "下回预告", text = "第二十六回：百里奚举荐蹇叔，又将在秦国重逢失散多年的妻子杜氏。" }
    },
    defeat = {
        { speaker = "里克", text = "虞公已经带着精兵回到城下，南门仍未突破。奇袭变成强攻，假道之计功亏一篑。" },
        { speaker = "", text = "里克或荀息被击退，本关失败。" }
    }
}

gstage = {
    title_id = "SurpriseYuCapital25", turn_limit = 16,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "mmmmWWWWWCWWWWWmmmm",
            "mmmmWiiiiiiiiiWmmmm",
            "mmmmWibiiiiiiiWmmmm",
            "mmmmWiiiiiiiiiWmmmm",
            "mmmmWWWWWGWWWWWmmmm",
            "mmmgggfffwfffgggmmm",
            "mmgggffffwffffgggmm",
            "mgggFFFFfwfFFFFgggm",
            "mggggffffwffffggggm",
            "mggggffffwffffggggm",
            "mggggffffwfffffgegm",
            "mmgggffffwffffgggmm",
            "mmmgggfffwfffgggmmm",
            "mmmmgggggfffgggmmmm"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {15, 10}, hero = "LiKe25" },
            { position = {16, 10}, hero = "XunXi25" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2700 }
}

function on_deploy(game)
    game:appoint_hero("LiKe25", 1)
    game:appoint_hero("XunXi25", 1)
end

function on_begin(game)
    game:generate_unit("JinGuard25", 1, Enum.force.own, {15, 9})
    game:generate_unit("JinGuard25", 1, Enum.force.own, {16, 9})
    game:generate_unit("JinArcher25", 1, Enum.force.own, {14, 10})
    game:generate_unit("YuCapitalCaptain25", 1, Enum.force.enemy, {9, 0})
    game:generate_unit("YuGuard25", 1, Enum.force.enemy, {8, 3})
    game:generate_unit("YuGuard25", 1, Enum.force.enemy, {10, 3})
    game:generate_unit("YuGuard25", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("YuArcher25", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("YuArcher25", 1, Enum.force.enemy, {11, 2})
end

function on_update(game)
    if not yu_returned and game:get_turn_current() >= 4 then
        yu_returned = true
        yu_gong_id = game:generate_unit("YuGong25", 1, Enum.force.enemy, {8, 13})
        bailixi_id = game:generate_unit("BailiXi25", 1, Enum.force.enemy, {10, 13})
        game:generate_unit("YuGuard25", 1, Enum.force.enemy, {7, 12})
        game:generate_unit("YuGuard25", 1, Enum.force.enemy, {11, 12})
        game:generate_unit("YuArcher25", 1, Enum.force.enemy, {9, 12})
        game:push_cmd_speak(yu_gong_id, "城中火起，城楼上又换成晋军旗号！各部随我夺回南门！")
        game:push_cmd_speak(bailixi_id, "晋军已经控制城门。主公不可挤在中央道路，弓手先压制门内，再寻退路！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("YuCapitalCaptain25")
       and game:is_force_within(Enum.force.own, {9, 0}, 0) then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
