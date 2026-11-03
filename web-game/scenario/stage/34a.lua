siege_spoken = false
final_assault_arrived = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "GongZiMuYi33", "GongSunGu33" }
gduel_enabled = false
gduels = {}
gsites = {
    { id = "suiyang_palace", name = "睢阳城池", position = {9, 1}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "suiyang_south_gate", name = "睢阳南门", position = {9, 7}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "chu_left_camp", name = "楚军左营", position = {4, 11}, restore_hp = 20, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
    { id = "chu_center_camp", name = "楚军中营", position = {9, 11}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "chu_right_camp", name = "楚军右营", position = {14, 11}, restore_hp = 20, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第三十四回·上",
    title = "宋襄公假仁失众 齐姜氏乘醉遣夫",
    battle_title = "睢阳守城",
    objective = "公子目夷、公孙固坚守到第四回合，或提前击退成得臣与斗勃；两名我方有名角色任一被击退则失败",
    map_asset = "m056.png",
    intro = {
        { speaker = "", text = "楚成王在盂地擒住宋襄公，掠尽宋国馆舍中的犒军礼物、粮粟与车乘，又迫使陈、蔡、郑、许、曹诸侯留在原地。" },
        { speaker = "楚成王", text = "宋公伐齐擅立、拘滕、杀鄫、围曹，又以亡国余力妄图称霸。六罪俱在，寡人今日便踏破睢阳！" },
        { speaker = "宋襄公", text = "寡人一心继承齐桓公霸业，却落到阶下受辱。今日之祸，皆因没有听子鱼之言。" },
        { speaker = "", text = "楚军号称千乘，实有五百乘。楚成王带着宋襄公拔营东进，列国诸侯畏惧楚威，无人敢替宋国求情。" },
        { speaker = "公子目夷", text = "主公被楚军挟持，敌兵旦夕便到。宋国不可无主，我暂摄国政，只为号令三军、保全社稷。" },
        { speaker = "公孙固", text = "公子摄位，赏罚方能严明。城墙各段不得留隙，南门只开一条通道，弓手登城，步卒守门。" },
        { speaker = "宋军守将", text = "城内道路与民居都已清理。王臣暂居城池，甲士分守城门，楚军若强攻，只能从南门正面推进。" },
        { speaker = "世子王臣", text = "叔父只管主持军务。父君身陷楚营，王臣虽不能出战，也愿与睢阳百姓共守此城。" },
        { speaker = "", text = "公子目夷告于太庙，暂居南面摄政。睢阳铃柝严明，各路城门封闭，城上矢石、滚木准备齐全。" },
        { speaker = "斗勃", text = "宋君正在我军手中！早早献土纳降，尚可保全旧君性命；若敢顽抗，城破之日玉石俱焚。" },
        { speaker = "公孙固", text = "国人已经立新君主持社稷。旧君被执，已辱社稷，归与不归惟楚所命；要宋国投降，万无可能！" },
        { speaker = "成得臣", text = "宋人竟用另立新君破我挟持之计。前军压住南门，弓手两格外齐射，近战兵不得堵住射路。" },
        { speaker = "楚成王", text = "区区宋城也敢拒命！成得臣、斗勃轮番攻门，今日不惜兵力，也要把这座城拿下来。" },
        { speaker = "公子目夷", text = "楚军势盛却远道而来。守住三日，使其攻城无功，楚王自然明白宋公这个俘虏换不来宋国。" },
        { speaker = "公孙固", text = "城门地形能够恢复体力，但城墙绝不可跨越。受伤者轮换退到城内，弓手始终保持射界。" },
        { speaker = "华御事", text = "楚军三个营寨也能补给，不能贸然出城追击。我们的目标是守住，不是争一时斩获。" },
        { speaker = "宋军守卒", text = "主君虽被俘，睢阳仍有公子目夷和诸位将军。城在人在，决不向楚军献门！" },
        { speaker = "楚军弓手", text = "步卒先压城门两侧，让出中路射线。宋军缩在门后，正可用弓箭不断消耗。" },
        { speaker = "军令", text = "坚守至第四回合或击退成得臣、斗勃即可过关。城墙不可通行；睢阳城池、南门和三座营寨对驻留者均有恢复效果。" }
    },
    events = {
        { id = "suiyang_siege", trigger = "approach", position = {9, 7}, radius = 2, speaker = "公孙固", text = "楚军已经逼近南门！步卒稳住门内，弓手隔墙齐射，不准任何人擅自追出城外！" },
        { id = "third_day_assault", trigger = "turn", turn = 3, speaker = "成得臣", text = "已经连攻两日，宋人仍不动摇。第三日增派甲士与弓手压向南门，作最后一次强攻！" }
    },
    victory = {
        { speaker = "公孙固", text = "楚军连攻三日，折损众多，始终不能越过睢阳城墙。各门仍在我军手中。" },
        { speaker = "公子目夷", text = "不可出城追击。楚王已经明白宋国不会因一名俘虏屈服，主公反而有了获释的机会。" },
        { speaker = "楚成王", text = "宋人既然不用旧君，杀掉宋公又有何益？攻城不克，再退兵释人，寡人的威名何在？" },
        { speaker = "成得臣", text = "杀宋公如杀匹夫，既不能得宋，又徒取天下怨恨。不如移师亳都，以俘获震慑鲁国。" },
        { speaker = "", text = "楚军退出宋境，转屯亳都。宜申奉命携带战利品前往曲阜，邀请鲁僖公赴会共同审断宋襄公。" },
        { speaker = "鲁僖公", text = "楚王恃强袭执上公，有威无德。鲁宋同受葵丘之盟，若坐视不救，必被天下人耻笑。" },
        { speaker = "仲遂", text = "臣先私见成得臣，请他从中转圜。只要诸侯共同要求释宋，楚王便可借此收买人心。" },
        { speaker = "郑文公", text = "楚王若能释放宋公，诸侯愿尊楚为盟主。请在亳郊重筑盟坛，歃血同赦宋罪。" },
        { speaker = "", text = "楚成王释放宋襄公，并在亳郊受诸侯推戴主盟。宋襄公含羞受歃，敢怒而不敢言。" },
        { speaker = "宋襄公", text = "听说子鱼已经即位，寡人还有何面目返回睢阳？不如暂奔卫国避让。" },
        { speaker = "公子目夷", text = "臣摄位只是替主公守国。国仍是主公之国，法驾已经备齐，请主公回朝，臣退回臣列。" },
        { speaker = "", text = "宋襄公复位后仍不甘受辱，又怨郑文公率先尊楚为盟主。次年郑君朝楚，宋公遂倾国伐郑。" },
        { speaker = "公子目夷", text = "楚郑正相亲睦，伐郑必招楚军。主公若仍以霸名用兵，恐怕下一次再无人能以守城之计解围。" },
        { speaker = "宋襄公", text = "郑伯助楚辱宋，此仇不可不报。寡人亲率中军，公孙固随行，子鱼辅佐世子守国。" },
        { speaker = "下关提示", text = "第三十四回·下：宋军从郑国回师，在泓水南岸迎战楚军。必须面对宋襄公坚持等待楚军渡河列阵造成的败局。" }
    },
    defeat = {
        { speaker = "公子目夷", text = "南门防线已经崩溃，楚军涌入城内。宋国既失主君又失都城，再无人能够维系社稷。" },
        { speaker = "", text = "公子目夷或公孙固被击退，本关失败。" }
    }
}

gstage = {
    title_id = "DefenseSuiyang34", turn_limit = 8,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "mmmWWWWWWWWWWWWWmmm",
        "mmmWiiiiiCiiiiiWmmm",
        "mmmWiiiiiiiiiiiWmmm",
        "mmmWhhiiiiiiihhWmmm",
        "mmmWiiiiiiiiiiiWmmm",
        "mmmWiiiiiiiiiiiWmmm",
        "mmmWiiiiiiiiiiiWmmm",
        "mmmWWWWWWGWWWWWWmmm",
        "FgggggggggggggggggF",
        "FgggggggggggggggggF",
        "gggggggggffgggggggg",
        "ggggeggggeggggegggg",
        "gggggggggffgggggggg",
        "FFFggggggffggggggFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {9, 1}, hero = "GongZiMuYi33" },
        { position = {9, 6}, hero = "GongSunGu33" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 3600 }
}

function on_deploy(game)
    game:appoint_hero("GongZiMuYi33", 1)
    game:appoint_hero("GongSunGu33", 1)
end

function on_begin(game)
    game:generate_unit("SongPrinceChen34", 1, Enum.force.ally, {10, 1})
    game:generate_unit("SongGuard33", 1, Enum.force.ally, {8, 6})
    game:generate_unit("SongGuard33", 1, Enum.force.ally, {10, 6})
    game:generate_unit("SongArcher33", 1, Enum.force.ally, {6, 5})
    game:generate_unit("SongArcher33", 1, Enum.force.ally, {12, 5})
    game:generate_unit("ChuChengWang33", 1, Enum.force.enemy, {9, 11})
    game:generate_unit("ChengDeChen33", 1, Enum.force.enemy, {8, 9})
    game:generate_unit("DouBo33", 1, Enum.force.enemy, {10, 9})
    game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {5, 9})
    game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {13, 9})
    game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {6, 10})
    game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {12, 10})
end

function on_update(game)
    if not siege_spoken and game:is_force_within(Enum.force.enemy, {9, 7}, 2) then
        siege_spoken = true
        game:push_cmd_speak(0, "楚军已进入南门射程！友军坚守不移动，我军依托城门和城内道路反击！")
    end
    if not final_assault_arrived and game:get_turn_current() >= 3 then
        final_assault_arrived = true
        game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {3, 9})
        game:generate_unit("ChuGuard34", 1, Enum.force.enemy, {15, 9})
        game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {7, 10})
        game:generate_unit("ChuArcher34", 1, Enum.force.enemy, {11, 10})
        game:push_cmd_speak(0, "第三回合，楚军最后一批攻城兵赶到；守住本回合，楚军便会因伤亡过大而退兵。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("ChengDeChen33") and not game:has_unit("DouBo33") then return Enum.status.victory end
    if game:get_turn_current() >= 4 then return Enum.status.victory end
    return Enum.status.undecided
end
