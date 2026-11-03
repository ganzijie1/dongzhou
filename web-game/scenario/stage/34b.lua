crossing_spoken = false
chu_formed = false
retreat_spoken = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "SongXiangGong33", "GongSunGu33", "LePuYi34", "HuaXiuLao34", "XiangZiShou34" }
gduel_enabled = false
gduels = {}
gsites = {
    { id = "chu_left_camp_hong", name = "楚军左营", position = {7, 1}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "chu_center_camp_hong", name = "楚军中营", position = {9, 1}, restore_hp = 20, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } },
    { id = "chu_right_camp_hong", name = "楚军右营", position = {11, 1}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "song_camp_hong", name = "宋军本营", position = {9, 11}, restore_hp = 20, restore_mp = 10, rewards = { { item = "medicine", amount = 2 } } }
}

gstory = {
    chapter = "第三十四回·下",
    title = "宋襄公假仁失众 齐姜氏乘醉遣夫",
    battle_title = "泓水败阵",
    objective = "第三回合楚军完成渡河列阵后，护送负伤的宋襄公本人到南侧出口（9，13）；五名我方有名角色任一被击退则失败",
    map_asset = "m057.png",
    intro = {
        { speaker = "", text = "宋襄公倾国伐郑，命公子目夷辅佐世子王臣守国，亲率公孙固、乐仆伊、华秀老、公子荡、向訾守出征。" },
        { speaker = "郑文公", text = "宋军因亳都会盟之怨来犯，郑国难以独力抵挡。立刻向楚王告急，请楚军救援。" },
        { speaker = "成得臣", text = "救郑不如伐宋。宋军主力远在郑境，楚军直捣宋国，宋公必然疲于回救；以逸待劳，胜负已定。" },
        { speaker = "楚成王", text = "郑国事楚甚恭。子玉统军伐宋，斗勃为副，寡人留后接应，务必挫败宋公的霸业妄想。" },
        { speaker = "", text = "宋襄公得知楚军入境，匆忙从郑国撤兵，兼程回国，在泓水南岸列营迎战。楚军则屯于北岸。" },
        { speaker = "公孙固", text = "楚军本为救郑而来。我军既已离郑，只须谢罪退兵，楚国便会撤回，实在不该在泓水决战。" },
        { speaker = "宋襄公", text = "齐桓公曾兴兵伐楚，寡人若见楚军而避战，如何继承霸业？我军甲兵虽少，仁义却胜过楚人。" },
        { speaker = "公孙固", text = "宋军甲不如楚坚、兵不如楚利、人不如楚强。主公以空名赌国运，臣只能竭力保全宗庙。" },
        { speaker = "乐仆伊", text = "司马已经多次劝谏。既然战书约定十一月朔日交战，各军必须提前布阵，防止楚军过河冲击。" },
        { speaker = "华秀老", text = "泓水横在中央，只有中间浅滩可以通行。若趁楚军半渡攻击，确实能以全军压制其半。" },
        { speaker = "宋襄公", text = "辂车大旗写着“仁义”二字。堂堂之阵，岂有攻击半渡之师的道理？等楚军全部渡河。" },
        { speaker = "公子荡", text = "臣随主公中军冲阵。无论此战成败，宋国公族都不能让楚人夺走主君旗号。" },
        { speaker = "向訾守", text = "门官亲兵已经集结在主公周围。楚军一旦成阵，我们护住辂车，公孙司马在外接应。" },
        { speaker = "斗勃", text = "宋公专务迂阔，不知用兵。早渡晚渡都没有差别，前军沿中央浅滩从容过河。" },
        { speaker = "成得臣", text = "宋军果然不攻击半渡之兵。各部全部过河后再展开阵势，弓手居后，车骑留出冲击通道。" },
        { speaker = "公孙固", text = "楚军过河后仍未成列，最后还有一次进攻机会。主公若再等待，宋军便只能设法突围。" },
        { speaker = "宋襄公", text = "未成列而鼓之，同样有损万世仁义。等楚军堂堂列阵，寡人再亲自擂鼓出战！" },
        { speaker = "成得臣", text = "宋公已经两次错失战机。列阵后打开中军缺口，只放他的辂车深入，再从四面合围。" },
        { speaker = "军令", text = "泓水两行水域不可通行，中央三格浅滩是唯一渡口。第三回合楚军列阵后，护送宋襄公本人撤到（9，13）。" }
    },
    events = {
        { id = "hong_crossing", trigger = "approach", position = {9, 4}, radius = 2, speaker = "公孙固", text = "楚军正在通过浅滩！主公仍不准攻击，各部保持阵形，准备承受完成列阵后的冲击。" },
        { id = "chu_battle_line", trigger = "turn", turn = 3, speaker = "成得臣", text = "楚军已经渡河成列！中军开门诱宋公深入，左右两翼随后合围！" },
        { id = "song_retreat", trigger = "approach", position = {9, 11}, radius = 2, speaker = "公孙固", text = "主公右股中箭，已经不能步战！不要再争仁义大旗，立即护送主公退回本营！" }
    },
    victory = {
        { speaker = "", text = "楚军列阵后，宋襄公擂鼓进攻。成得臣故意打开阵门，只放宋国中军深入，随后从四面包围。" },
        { speaker = "斗勃", text = "公孙固想要入阵救主，先过我这一关！楚军各部继续合围宋公辂车。" },
        { speaker = "公孙固", text = "乐仆伊牵制斗勃，华秀老接住追兵。向訾守，立刻带我去主公所在之处！" },
        { speaker = "向訾守", text = "门官亲兵已经人人带伤，仍在死战。主公身中数创，右股中箭，公子荡也倒在车下。" },
        { speaker = "公子荡", text = "司马快扶主公离开……仁义大旗可以丢，宋国的君主不能再落入楚人手中。" },
        { speaker = "", text = "公子荡伤中要害，当场阵亡。公孙固以身遮护宋襄公，向訾守率门官断后，奋力杀出楚阵。" },
        { speaker = "宋襄公", text = "寡人不忍重伤敌人，也不愿擒拿白发老者。以仁义行师，何错之有？" },
        { speaker = "公孙固", text = "门官已经无一生还，宋国甲车十丧八九。百姓讥怨的不是仁义，而是主公不肯审时用兵。" },
        { speaker = "", text = "楚军乘胜追击，宋军丢弃辎重器械。公孙固连夜护送宋襄公回国，乐仆伊、华秀老等各自撤退。" },
        { speaker = "", text = "成得臣向屯在柯泽的楚成王献捷。郑文公与夫人文芈赴营劳军，又邀请楚王入郑都享宴。" },
        { speaker = "叔詹", text = "楚王受九献大礼，却在酒后失去礼法。礼而无别，终非有德之主。" },
        { speaker = "", text = "另一边，重耳已在齐国居住七年，沉溺于齐姜和宴饮。狐偃、赵衰等人在桑阴商议劫公子离齐。" },
        { speaker = "齐姜", text = "公子若贪图眼前安乐，便会错过返回晋国的天命。今晚我将设宴灌醉公子，你们连夜载他出城。" },
        { speaker = "狐偃", text = "夫人割舍夫妻之情以成全公子大业，此德千古罕有。车马、兵器、干粮都已在郊外备妥。" },
        { speaker = "", text = "齐姜将重耳灌醉，狐偃、魏犨、颠颉连席抬上车，与赵衰等人在城外会合，连夜离开齐国。" },
        { speaker = "重耳", text = "未得晋国，先失齐国！子犯竟敢不告而劫我出城，拿戈来，我先与你算账！" },
        { speaker = "下回预告", text = "第三十五回：重耳一行将继续流亡宋、郑、楚诸国；宋襄公箭伤恶化，宋国霸业也将走到尽头。" }
    },
    defeat = {
        { speaker = "公孙固", text = "宋军退路被楚军截断，主公再次落入敌手。泓水之败将直接危及宋国宗庙。" },
        { speaker = "", text = "宋襄公、公孙固、乐仆伊、华秀老或向訾守被击退，本关失败。" }
    }
}

gstage = {
    title_id = "BattleHongRiver34", turn_limit = 12,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "rrFFFgggeeeegggFFrr",
        "rFFFgggeegeeegggFFr",
        "FggggggggffgggggggF",
        "~~~~~~~~fff~~~~~~~~",
        "~~~~~~~~fff~~~~~~~~",
        "FggggggggffgggggggF",
        "FggggggggffgggggggF",
        "gggggggggffgggggggg",
        "gggggggggffgggggggg",
        "FggggggggffgggggggF",
        "FggggggggffgggggggF",
        "ggggggggeeeeggggggg",
        "FggggggggffgggggggF",
        "FFFggggggffggggggFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {9, 10}, hero = "SongXiangGong33" },
        { position = {8, 9}, hero = "GongSunGu33" },
        { position = {6, 9}, hero = "LePuYi34" },
        { position = {12, 9}, hero = "HuaXiuLao34" },
        { position = {10, 9}, hero = "XiangZiShou34" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 3000 }
}

function on_deploy(game)
    game:appoint_hero("SongXiangGong33", 1)
    game:appoint_hero("GongSunGu33", 1)
    game:appoint_hero("LePuYi34", 1)
    game:appoint_hero("HuaXiuLao34", 1)
    game:appoint_hero("XiangZiShou34", 1)
end

function on_begin(game)
    game:generate_unit("GongZiDang33", 1, Enum.force.ally, {9, 8})
    game:generate_unit("SongGuard33", 1, Enum.force.ally, {8, 8})
    game:generate_unit("SongGuard33", 1, Enum.force.ally, {10, 8})
    game:generate_unit("SongArcher33", 1, Enum.force.ally, {7, 10})
    game:generate_unit("SongArcher33", 1, Enum.force.ally, {11, 10})
    game:generate_unit("ChengDeChen33", 1, Enum.force.enemy, {9, 0})
    game:generate_unit("DouBo33", 1, Enum.force.enemy, {7, 1})
    game:generate_unit("LuChen34", 1, Enum.force.enemy, {11, 1})
    game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {12, 2})
    game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {8, 2})
    game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {10, 2})
end

function on_update(game)
    if not crossing_spoken and game:is_force_within(Enum.force.enemy, {9, 4}, 1) then
        crossing_spoken = true
        game:push_cmd_speak(0, "楚军正在中央浅滩渡过泓水；宋襄公严令不得攻击半渡之师。")
    end
    if not chu_formed and game:get_turn_current() >= 3 then
        chu_formed = true
        game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {7, 5})
        game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {11, 5})
        game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {9, 5})
        game:push_cmd_speak(0, "第三回合，楚军全部渡河成列；宋襄公深入敌阵负伤，胜利目标变为护送他撤到南侧出口。")
    end
    if not retreat_spoken and game:get_turn_current() >= 3 and game:is_unit_within("SongXiangGong33", {9, 11}, 2) then
        retreat_spoken = true
        game:push_cmd_speak(0, "公孙固护住负伤的宋襄公，正沿南侧道路撤退；只有宋襄公本人到达出口才算脱险。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_turn_current() >= 3 and game:is_unit_within("SongXiangGong33", {9, 13}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
