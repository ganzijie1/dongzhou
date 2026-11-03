gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong18", "GuanYiWu18", "WangZiChengFu18", "HuErBan21" }
gduel_enabled = false
gduels = {}
ambush_revealed = false
sumai_id = -1

gsites = {
    { id = "fulong_qi_camp", name = "伏龙山车营", position = {9, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十一回·一",
    title = "管夷吾智辨俞儿 齐桓公兵定孤竹",
    battle_title = "伏龙山破伏",
    objective = "护住齐桓公、管夷吾、王子成父与虎儿斑，诱出并击退密卢、速买的山谷伏兵",
    map_asset = "m034.png",
    intro = {
        { speaker = "", text = "山戎盘踞令支，凭险不贡，见齐国称霸中原，便以万骑侵入燕境，企图截断燕国通齐之路。" },
        { speaker = "燕庄公", text = "山戎围掠二月，边邑子女多被掳走。燕军独力难支，只得求救于齐侯。" },
        { speaker = "齐桓公", text = "南有楚、北有戎、西有狄，都是诸夏之患。燕国既来告急，齐国不能坐视。" },
        { speaker = "管夷吾", text = "只解燕围而退，山戎得志后还会再来。应当乘其未稳，深入令支，彻底平定北患。" },
        { speaker = "", text = "齐军渡过济水，燕庄公请当前锋。齐桓公念燕军久困，只令燕军押后助势。" },
        { speaker = "燕庄公", text = "无终虽是戎种，却不依附山戎。臣愿请其出兵，并为大军引路。" },
        { speaker = "", text = "无终大将虎儿斑率骑兵来会。齐桓公厚加赏赐，命他引军进入北地山道。" },
        { speaker = "虎儿斑", text = "末将熟悉山势，愿为前锋。若遇山戎，定以铁瓜锤开路！" },
        { speaker = "", text = "速买只带百余骑迎战，略战数合便佯败入林。虎儿斑追入山谷，四面呼哨齐起，前后队顿时被截断。" },
        { speaker = "速买", text = "齐人远来疲惫，无终骑兵又贪功冒进。封住谷口，把虎儿斑生擒献给密卢！" },
        { speaker = "虎儿斑", text = "中计又如何！无终男儿随我结阵死战，绝不能让山戎越过此处！" },
        { speaker = "王子成父", text = "虎儿斑尚在谷中苦战。我率骑兵从正面破围，弓手压住两侧林口！" },
        { speaker = "", text = "齐军救出虎儿斑后，在伏龙山结成车城。密卢与速买再次设伏，故意下马叫骂，想引齐军离营。" },
        { speaker = "管夷吾", text = "山戎惯用伏兵。先以车营挡住冲击，待其伏兵暴露，王子成父与虎儿斑再分路反包围。" },
        { speaker = "齐桓公", text = "胜负是兵家常事。虎儿斑不必惭愧，今日正可借山戎之血洗去前耻。" },
        { speaker = "军令", text = "山地与森林增加移动消耗，岩山不可跨越。齐军进入谷口后，密卢伏兵才会出现；所有有名我军将领必须存活。" }
    },
    victory = {
        { speaker = "虎儿斑", text = "山戎伏兵已乱！末将今日总算报了谷中受困之耻。" },
        { speaker = "王子成父", text = "左、右两路已经合围。速买的骑兵丢下马匹，正向黄台山方向败退。" },
        { speaker = "密卢", text = "齐军远来竟还如此整肃。退守黄台谷口，断掉他们取水的濡水！" },
        { speaker = "速买", text = "再用木石塞住山路，多掘坑堑。只要齐军缺水缺粮，迟早自行溃散。" },
        { speaker = "", text = "山戎退后，果然堵塞黄台山大路，又筑坝断流。伏龙山二十余里无泉，齐军饮水渐绝。" },
        { speaker = "公孙隰朋", text = "蚁冬居山阳、夏居山阴。如今正值冬月，应在向阳山腰寻找蚁穴，再向下掘水。" },
        { speaker = "", text = "军士依言掘得清泉，全军欢声雷动。齐桓公称隰朋为圣，遂将此泉命名为圣泉。" },
        { speaker = "管夷吾", text = "有水便不怕坚守。令宾须无绕芝麻岭抄后，正面则以土囊填坑、空车探路，同时攻入黄台谷口。" },
        { speaker = "", text = "六日之后，齐军正面搬开木石，宾须无又从西路杀到。密卢、速买无心恋战，弃营东逃。" },
        { speaker = "齐桓公", text = "不许杀害投降的令支百姓，先救回燕国被掳人口，再清点山戎遗下的牛羊器械。" },
        { speaker = "", text = "降人告知密卢必投孤竹。齐桓公决定继续东进，讨伐包庇山戎的孤竹国。" },
        { speaker = "下关提示", text = "第二十一回·二：齐军将翻越顽山、寻找卑耳溪浅滩，分左右两路渡水争夺团子山。" }
    },
    defeat = {
        { speaker = "管夷吾", text = "车营已经被冲开，山戎伏骑正截断各部。先护送君侯退出谷口，再作计较。" },
        { speaker = "", text = "齐军未能破除伏龙山伏兵，北伐被迫中止。" }
    }
}

gstage = {
    title_id = "FulongValleyAmbush21", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrrrrr",
            "rmmmFFFFgggFFFFmmmr",
            "rmmFgggggggggggFmmr",
            "rmFgggggggggggggFmr",
            "rFgggfffgffffggggFr",
            "rgggffffwfffffggggr",
            "rggffffffffffgggggr",
            "rggffffffffffgggggr",
            "rgggffffffffffggggr",
            "rFgggffffffggggggFr",
            "rmFgggggggggggggFmr",
            "rmmFggggeggggggFmmr",
            "rmmmFFFFgggFFFFmmmr",
            "rrrrrrrrrrrrrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 11}, hero = "QiHuanGong18" },
            { position = {8, 11}, hero = "GuanYiWu18" },
            { position = {10, 11}, hero = "WangZiChengFu18" },
            { position = {9, 10}, hero = "HuErBan21" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1450 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong18", 1)
    game:appoint_hero("GuanYiWu18", 1)
    game:appoint_hero("WangZiChengFu18", 1)
    game:appoint_hero("HuErBan21", 1)
end

function on_begin(game)
    game:generate_unit("QiGuard21", 1, Enum.force.own, {7, 12})
    game:generate_unit("QiArcher21", 1, Enum.force.own, {11, 12})
    sumai_id = game:generate_unit("SuMai21", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {8, 4})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {10, 4})
    game:generate_unit("ShanRongArcher21", 1, Enum.force.enemy, {9, 2})
end

function on_update(game)
    if not ambush_revealed and game:has_unit("MiLu21") then ambush_revealed = true end
    if ambush_revealed or not game:is_force_within(Enum.force.own, {9, 7}, 3) then return end
    ambush_revealed = true
    local milu = game:generate_unit("MiLu21", 1, Enum.force.enemy, {3, 6})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {2, 7})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {4, 8})
    game:generate_unit("ShanRongArcher21", 1, Enum.force.enemy, {3, 9})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {16, 6})
    game:generate_unit("ShanRongCavalry21", 1, Enum.force.enemy, {14, 8})
    game:generate_unit("ShanRongArcher21", 1, Enum.force.enemy, {15, 9})
    game:push_cmd_speak(milu, "齐军已经进入谷心！两翼伏骑尽出，截断他们的退路！")
    game:push_cmd_speak(2, "伏兵果然现身。左军随我迎击密卢，虎儿斑守住车营！")
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end
