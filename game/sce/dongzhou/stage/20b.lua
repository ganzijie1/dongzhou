gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "JinXianGong20", "ShenSheng20" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "li_rong_camp_20", name = "骊戎大营", position = {9, 2}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "li_rong_entrance_20", name = "骊戎营门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "jin_camp_20", name = "晋军行营", position = {15, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十回·二",
    title = "晋献公违卜立骊姬",
    battle_title = "骊山问戎",
    objective = "突破骊戎营门，击败骊戎主及其守军，迫使骊戎请和",
    map_asset = "m031.png",
    intro = {
        { speaker = "", text = "晋献公继位后诛除桓庄之族，又命士蔿扩建绛都，晋国兵权逐渐集中于国君。" },
        { speaker = "晋献公", text = "西方骊戎屡扰边境，若任其占据山道，绛都终日不得安宁。寡人将亲率上军问罪。" },
        { speaker = "申生", text = "骊山道路狭窄，戎营又设在高地。儿臣愿率下军先夺营门，为父君开路。" },
        { speaker = "里克", text = "骊戎善守山地，不可沿峡道挤作一团。应使弓手压住栅栏，再由步卒夺取入口。" },
        { speaker = "", text = "晋军进入骊山，骊戎主聚集部众，在北面高地立木栅拒守。" },
        { speaker = "骊戎主", text = "晋军远来山中，粮道绵长。我军只需守住营门，待其疲惫便可反击。" },
        { speaker = "晋献公", text = "骊戎若肯臣服，寡人可以止兵；若仍阻塞道路，今日便平其营寨。" },
        { speaker = "骊戎主", text = "戎人只信弓马，不信空言。晋侯想进我营，先问过山中健儿！" },
        { speaker = "申生", text = "父君居中督阵，儿臣从东侧坡地接近营门。赵氏甲士守住峡口，防止戎骑迂回。" },
        { speaker = "晋军弓手", text = "木栅连成一线，只有中央营门可通过。山石与栅栏均不可跨越。" },
        { speaker = "里克", text = "骊戎主身边弓手较多。先引出门前步卒，再集中攻击主帐，不可分兵追逐。" },
        { speaker = "晋献公", text = "降者免死，百姓不取。此战是为安定边境，不是纵兵掠夺。" },
        { speaker = "骊戎主", text = "各部守住高台！晋军若在山道停滞，便从两侧以箭雨夹击。" },
        { speaker = "申生", text = "晋军将士，随我夺门！击破戎营之后立即整队，不得争抢财物。" },
        { speaker = "军令", text = "晋献公、申生必须存活。栅栏和岩山不可通行，由中央营门进入，击败全部骊戎军。" }
    },
    victory = {
        { speaker = "骊戎主", text = "营门已破，再战只会使部族尽灭。骊戎愿请和，向晋侯献上贡礼。" },
        { speaker = "晋献公", text = "骊戎既服，寡人准其保留部众。此后须开放山道，不得再犯晋境。" },
        { speaker = "", text = "骊戎主献上长女骊姬与次女少姬。晋献公见骊姬美貌聪慧，宠爱无比。" },
        { speaker = "骊姬", text = "妾身既入晋宫，愿尽心侍奉君侯。军国之事虽非妇人所掌，若蒙问及，也不敢隐瞒。" },
        { speaker = "", text = "骊姬生奚齐，少姬生卓子。晋献公欲立骊姬为夫人，命太卜郭偃灼龟。" },
        { speaker = "郭偃", text = "龟兆言专宠将使美恶倒置，香草不能压过臭草，祸乱十年仍有余臭。此事不吉。" },
        { speaker = "晋献公", text = "再以蓍草占筮。若两法不同，寡人自取吉兆。" },
        { speaker = "史苏", text = "卦辞并非赞成再立夫人。礼无二嫡，主公若违龟从筮，晋国必生内乱。" },
        { speaker = "", text = "晋献公不听劝告，仍立骊姬为夫人。骊姬表面推辞废立，暗中却与优施、梁五、东关五谋划。" },
        { speaker = "优施", text = "申生、重耳、夷吾三位公子都在君侯身边，夺嗣之计难行。须以守边为名，使他们各居外邑。" },
        { speaker = "", text = "梁五、东关五劝献公令申生居曲沃、重耳居蒲、夷吾居屈。三公子由此远离绛都。" },
        { speaker = "士蔿", text = "一国三公，嫡庶长幼已乱。今日筑下的城，数年之后恐怕便是彼此相攻的壁垒。" },
        { speaker = "", text = "晋献公新建二军，自将上军，令申生统领下军，并准备继续向狄、霍、魏三国用兵。" },
        { speaker = "申生", text = "儿臣虽远居曲沃，仍当奉父君军令。赵夙、毕万可随下军出征，扫清北境。" },
        { speaker = "下关提示", text = "第二十回·三：申生将率赵夙、毕万进攻狄、霍、魏三国。" }
    },
    defeat = {
        { speaker = "申生", text = "山道被戎军截断，继续强攻只会使队伍失去照应。请父君暂退峡口。" },
        { speaker = "", text = "晋军未能打通骊山道路，骊戎仍控制西部边境。" }
    }
}

gstage = {
    title_id = "JinCampaignLiRong20", turn_limit = 20,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrmmmmmmmmmrrrrr",
            "mmmmmPPPPPPPPPmmmmm",
            "mmmmmPiiieiiiPmmmmm",
            "mmmmmPiiiiiiiPmmmmm",
            "mmmmmPPPPDPPPPmmmmm",
            "mmmwwwwwwwwwwwmmmmm",
            "mmmwwwwwwwwwwwmmmmm",
            "mmmwwwrrwwwrrwwmmmmm",
            "wwwwwwwwwwwwwwwwwww",
            "wwwwwwwwwwwwwwwwwww",
            "wwwwwwwwwwwwwwwwwww",
            "wwwwwwwwwwwwwwwwwww",
            "wwwwwwwwwwwwwwwewww",
            "wwwwwwwwwwwwwwwwwww"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {15, 12}, hero = "JinXianGong20" },
            { position = {14, 11}, hero = "ShenSheng20" },
            { position = {16, 11}, hero = "JinGuard20" },
            { position = {13, 12}, hero = "JinArcher20" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1350 }
}

function on_deploy(game)
    game:appoint_hero("JinXianGong20", 1)
    game:appoint_hero("ShenSheng20", 1)
    game:appoint_hero("JinGuard20", 1)
    game:appoint_hero("JinArcher20", 1)
end

function on_begin(game)
    game:generate_unit("LiRongLord20", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("LiRongGuard20", 1, Enum.force.enemy, {7, 2})
    game:generate_unit("LiRongGuard20", 1, Enum.force.enemy, {11, 2})
    game:generate_unit("LiRongGuard20", 1, Enum.force.enemy, {8, 5})
    game:generate_unit("LiRongGuard20", 1, Enum.force.enemy, {10, 5})
    game:generate_unit("LiRongArcher20", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("LiRongArcher20", 1, Enum.force.enemy, {11, 3})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end