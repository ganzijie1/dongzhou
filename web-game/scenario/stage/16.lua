gsupply_enabled = true
gown_hold_until_turn = 3

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "LuZhuangGong16", "CaoGui16" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "lu_changshao_camp", name = "鲁军行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "qi_changshao_camp", name = "齐军行营", position = {9, 1}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第十六回",
    title = "释槛囚鲍叔荐仲 战长勺曹刿败齐",
    battle_title = "长勺鼓阵",
    objective = "前两回合坚守不动，待齐军三鼓气竭后反击，击退鲍叔牙所部",
    map_asset = "m025.png",
    intro = {
        { speaker = "", text = "汶阳战后，齐兵压境。鲍叔牙致书鲁国，索要公子纠、召忽与管夷吾三人。" },
        { speaker = "鲁庄公", text = "先前不听施伯之言，以致乾时兵败。如今杀纠与保全公子纠，哪一种对鲁国更有利？" },
        { speaker = "施伯", text = "小白初立便能用人，又在乾时败我。公子纠远不能及；齐军压境，不如杀纠求和。" },
        { speaker = "", text = "鲁庄公命公子偃袭杀公子纠，又将召忽、管夷吾拘入鲁庭，准备装入槛车交齐。" },
        { speaker = "召忽", text = "为子死孝，为臣死忠，这是本分。我岂能受桎梏之辱！" },
        { speaker = "", text = "召忽以头触柱而死。管夷吾却束身入槛，决意生还齐国，为公子纠申明冤屈。" },
        { speaker = "施伯", text = "管仲面有生气，必有内援。此人若为齐国所用，齐必称霸；主公不如杀之，只交尸首。" },
        { speaker = "公孙隰朋", text = "管夷吾曾射中寡君带钩，寡君恨之切骨，定要亲手杀他。若交尸首，反不能泄恨。" },
        { speaker = "", text = "鲁庄公信以为真，将管仲槛送齐国。管仲恐鲁君反悔，作《黄鹄》之歌教役夫边走边唱，槛车一日兼行两日路程。" },
        { speaker = "鲁庄公", text = "施伯所虑不无道理，速命公子偃追回槛车！" },
        { speaker = "", text = "追兵赶到时，槛车已出鲁境。管仲抵达堂阜，鲍叔牙早已在那里等候。" },
        { speaker = "鲍叔牙", text = "仲幸无恙！成大事者不恤小耻，立大功者不拘小谅。齐君志大识高，正是你施展王佐之才的明主。" },
        { speaker = "管夷吾", text = "我与召忽同事公子纠，既不能奉他即位，又不能死难，如今反事仇人，臣节岂非有亏？" },
        { speaker = "鲍叔牙", text = "守匹夫小节于天下无益。你若辅佐齐君，安百姓、尊王室、成霸业，才不负平生所学。" },
        { speaker = "齐桓公", text = "管夷吾那一箭险些取我性命，箭痕至今尚在。寡人恨不得食其肉，如何还能用他？" },
        { speaker = "鲍叔牙", text = "人臣各为其主。射钩之时，他只知公子纠；主公若用他，他便能替主公射取天下！" },
        { speaker = "", text = "齐桓公终于释去私仇，斋戒更衣，亲自郊迎管仲，与他同车入朝。临淄百姓观者如堵。" },
        { speaker = "鲍叔牙", text = "臣谨慎守法，足以做具臣，却不足以治天下。宽惠百姓、执掌国柄、布信四方、整军敢战，我有五处不如管仲。" },
        { speaker = "管夷吾", text = "礼义廉耻，国之四维；四维不张，国乃灭亡。欲使民，必先爱民，省刑薄税，使士农工商各安其业。" },
        { speaker = "管夷吾", text = "兵贵精不贵多。以乡里编伍寄寓军令，使同伍之人祭祀同福、死丧同恤，夜战闻声不乱，昼战相识不散。" },
        { speaker = "管夷吾", text = "周室未衰，邻国未附，不可急于征伐。应当尊周亲邻、察诸侯之隙，再图方伯之业。" },
        { speaker = "", text = "桓公与管仲连谈三日三夜，拜其为相国，尊称仲父；隰朋、宁越、王子成父、宾须无、东郭牙也各任其职。" },
        { speaker = "鲁庄公", text = "悔不听施伯之言，竟把天下奇才送还齐国！立即整顿车乘，伐齐报乾时之仇！" },
        { speaker = "管夷吾", text = "齐国军政尚未整顿，此时不宜出兵。请主公先修内政，切勿轻战。" },
        { speaker = "齐桓公", text = "鲁国先扶公子纠争位，如今又兴兵犯境。寡人不能一再退让，命鲍叔牙率军直取长勺！" },
        { speaker = "施伯", text = "齐军势盛，臣荐东平曹刿。此人从未出仕，却有将相之才，足以抵御鲍叔牙。" },
        { speaker = "曹刿", text = "肉食者鄙，未能远谋。大王若能取信于民、察明小大之狱，百姓便肯用命，此战可以一战。" },
        { speaker = "鲁庄公", text = "先生与寡人同乘一车，军中进退，全听先生决断！" },
        { speaker = "军令", text = "鲁庄公、曹刿必须存活。第一、第二回合只能待机坚守；第三回合解除限制，击退齐军即可获胜。" },
        { speaker = "军令", text = "山地会增加移动消耗。不要急追齐军，先稳住阵形，等曹刿判断齐军三鼓气竭再全面反击。" }
    },
    victory = {
        { speaker = "鲍叔牙", text = "鲁军两次不应鼓，果然怯战。传令第三次擂鼓，冲散他们！" },
        { speaker = "曹刿", text = "齐军一鼓作气，再而衰，三而竭；如今彼竭我盈，正是反击之时！" },
        { speaker = "", text = "鲁军第一次擂响战鼓，整齐杀出。齐兵本以为鲁军不敢交战，猝不及防，顿时大败。" },
        { speaker = "鲁庄公", text = "齐军阵脚已乱，乘胜追击，不可让鲍叔牙从容退走！" },
        { speaker = "曹刿", text = "大国用兵难以测度，恐怕留有伏兵。请主公暂缓，容臣察看车辙与旗势。" },
        { speaker = "", text = "曹刿下车察看齐军车辙，又登车扶轼远望，见其辙乱旗靡，方才断定不是诱敌。" },
        { speaker = "曹刿", text = "齐军车辙已乱，军旗也东倒西歪，确是败退。如今可以追了！" },
        { speaker = "", text = "鲁军追出三十余里，缴获辎重甲兵无数。长勺之战，齐军因轻敌三鼓而败。" },
        { speaker = "鲁庄公", text = "寡人今日才知，临阵勇气与追敌判断，皆有时机。先生之谋，鲁国当永不忘。" },
        { speaker = "下回预告", text = "第十七回：齐国虽败于长勺，管仲仍将整顿国政；宋国也将再起内乱。" }
    },
    defeat = {
        { speaker = "曹刿", text = "齐军锐气未衰，我军阵形却先乱了。长勺今日不可再守！" },
        { speaker = "", text = "鲁军未能熬过齐军前两鼓，长勺防线被突破，鲁庄公只得退回曲阜。" }
    }
}

gstage = {
    title_id = "BattleOfChangshao",
    turn_limit = 18,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF",
            "FFggggggwewggggggFF",
            "FggggfffwwwfffggggF",
            "FgmmmfffwwwffffgggF",
            "FmmmmfffwwwffffgggF",
            "FmmmmfffwwwfffggggF",
            "FgmmmfffwwwfffmmmmF",
            "FgmmffffwwwfffmmmmF",
            "FggggfffwwwffmmmmmF",
            "FgggffffwwwffmmmmmF",
            "FggggfffwwwfffmmmgF",
            "FggggfffwwwfffgmmgF",
            "FFggggggwewggggggFF",
            "FFFFFFFFFFFFFFFFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {9, 11}, hero = "LuZhuangGong16" },
            { position = {8, 11}, hero = "CaoGui16" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 960 }
}

local second_drum_shown = false
local third_drum_shown = false
local bao_id = -1

function on_deploy(game)
    game:appoint_hero("LuZhuangGong16", 1)
    game:appoint_hero("CaoGui16", 1)
end

function on_begin(game)
    game:generate_unit("LuGuard16", 1, Enum.force.own, {6, 11})
    game:generate_unit("LuGuard16", 1, Enum.force.own, {12, 11})
    game:generate_unit("LuGuard16", 1, Enum.force.own, {7, 12})
    game:generate_unit("LuArcher16", 1, Enum.force.own, {10, 12})
    game:generate_unit("LuArcher16", 1, Enum.force.own, {11, 11})

    bao_id = game:generate_unit("BaoShuYa16", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("QiVanguard16", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("QiVanguard16", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("QiGuard16", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("QiGuard16", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("QiGuard16", 1, Enum.force.enemy, {11, 4})
    game:generate_unit("QiArcher16", 1, Enum.force.enemy, {5, 3})
    game:generate_unit("QiArcher16", 1, Enum.force.enemy, {13, 3})

    game:push_cmd_speak(bao_id, "齐军第一次擂鼓！先破鲁军中阵者，重赏！")
    game:push_cmd_speak(1, "齐师方锐，宜静以待之。鲁军各守本位，不得喧哗出阵！")
end

function on_update(game)
    local turn = game:get_turn_current()
    if not second_drum_shown and turn >= 2 then
        second_drum_shown = true
        game:push_cmd_speak(bao_id, "鲁军不敢应战，再擂一通鼓，继续压住他们！")
        game:push_cmd_speak(1, "齐军锐气已衰一层，仍不可动。再等一鼓。")
    end
    if not third_drum_shown and turn >= 3 then
        third_drum_shown = true
        game:push_cmd_speak(bao_id, "第三次擂鼓！鲁军必走，全军向前！")
        game:push_cmd_speak(1, "彼竭我盈，反击就在此刻！擂响鲁军第一通战鼓！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:get_turn_current() >= 3 and game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end