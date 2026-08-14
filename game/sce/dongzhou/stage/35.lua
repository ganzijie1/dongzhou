bear_defeated = false
mo_spawned = false

gally_hold_position = true
gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金创药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ChongEr27", "HuYan27", "ZhaoShuai27", "WeiChou27" }
gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "ChongEr27", defender = "HumanBear35", exp = 45, outcome = "kill",
        attacker_speech = "若我重耳终能返晋为君，此箭当贯人熊右掌！",
        defender_speech = "吼！",
        result_speech = "一箭正穿右掌，人熊扑地而死！",
        text = "重耳祝祷引弓，一箭贯穿人熊右掌，楚成王见之惊服。"
    },
    {
        attacker = "WeiChou27", defender = "MoBeast35", exp = 65, outcome = "capture",
        attacker_speech = "不用兵器，看我活捉此兽献于驾前！",
        defender_speech = "嗷！",
        result_speech = "魏犨扼住貘鼻，赵衰命军士以火熏之，怪兽终于伏地。",
        text = "魏犨飞身跨上貘背，双臂紧扼其颈，生擒怪兽。"
    }
}
gsites = {}

gstory = {
    chapter = "第三十五回",
    title = "晋重耳周游列国 秦怀嬴重婚公子",
    battle_title = "云梦围猎",
    objective = "先击退人熊；人熊倒下后貘从东北山谷出现，再将貘击退或由魏犨相邻触发生擒。重耳、狐偃、赵衰、魏犨任一被击退即失败。",
    map_asset = "m058.png",
    intro = {
        { speaker = "", text = "重耳被齐姜与狐偃等人灌醉载出临淄，醒后迁怒狐偃。赵衰、魏犨共同劝说，他终于收起安居齐国之念，继续周游列国。" },
        { speaker = "魏犨", text = "大丈夫当努力成名，声施后世。怎能留恋眼前妻室宴饮，忘了晋国仍在无道之君手中？" },
        { speaker = "重耳", text = "诸君舍弃骨肉乡里，随我奔走多年。既是众人公议，今后行止便听诸君安排。" },
        { speaker = "", text = "一行人先到曹国。曹共公不理朝政，听说重耳生有骈胁异相，竟微服闯入浴堂窥看，君臣无不愤怒。" },
        { speaker = "僖负羁", text = "晋公子贤名闻于天下，随从又皆豪杰。主君既不肯厚礼，我只能私下备食相赠，为曹国留下余地。" },
        { speaker = "重耳", text = "大夫使我不至于饥饿，已是厚恩。盘中白璧万万不能收；亡人若能返国，自会记得今日之情。" },
        { speaker = "", text = "重耳离曹入宋。宋襄公在泓水中箭，伤势未愈，仍命公孙固郊迎授馆，以国君之礼相待，并赠马二十乘。" },
        { speaker = "公孙固", text = "宋国新遭大败，主君病体沉重，实在无力助公子复国。若有大志，还须往楚、秦等大国求援。" },
        { speaker = "", text = "重耳离宋后，宋襄公箭疮恶化而死。临终嘱咐世子王臣重用公子目夷，若重耳得国，宋国当谦让事之。" },
        { speaker = "", text = "重耳到郑国，郑文公以他年老失势为由闭门不纳。上卿叔詹指出重耳有天命、人望、贤臣三助，郑伯仍不听。" },
        { speaker = "叔詹", text = "若不能尽礼，便该杀他，不能留下后患。如今既不礼又不杀，日后重耳得国，郑国必受其报。" },
        { speaker = "重耳", text = "郑门既闭，不必苦求。楚成王素有容人之量，我们径往楚国。" },
        { speaker = "", text = "楚成王果然以国君之礼接待重耳，设九献之享。重耳再三谦让，赵衰劝他顺应天命，君臣遂在楚国暂居。" },
        { speaker = "楚成王", text = "今日围猎云梦，寡人已连射一鹿一兔。晋公子身边文武英杰众多，也请一展身手。" },
        { speaker = "赵衰", text = "公子出亡十余年，小国轻慢，大国却以国君之礼相待，正是天命未绝。今日不可再辞。" },
        { speaker = "楚猎手", text = "西北苇泽冲出一头人熊，已经撞翻猎车，刀枪近不得身！" },
        { speaker = "重耳", text = "取弓来。若上天仍许我返晋，此箭便穿它右掌。" },
        { speaker = "军令", text = "穿过中央水泽两侧道路接近人熊。重耳与人熊相邻可触发射熊；人熊倒下后，貘会从东北山谷出现，魏犨与貘相邻可触发生擒。" }
    },
    events = {
        { id = "bear_approach", trigger = "approach", position = {16, 7}, radius = 3, speaker = "楚成王", text = "公子何不射之？若能一箭制住人熊，寡人便知晋国有人。" },
        { id = "mo_arrives", trigger = "defeated", unit = "HumanBear35", speaker = "楚猎手", text = "东北山谷又冲出怪兽，似熊非熊，嚼铁如泥，寻常刀箭全伤不得它！" }
    },
    victory = {
        { speaker = "赵衰", text = "此兽名貘，秉金气而生，皮肉如铁。惟鼻孔是虚窍，可用火气制伏。" },
        { speaker = "魏犨", text = "臣不用兵器，活捉此兽献于驾前！" },
        { speaker = "", text = "魏犨飞身跨上貘背，双臂扼颈，任它翻滚跳跃也不松手，终于牵至二君面前。赵衰命人用火熏鼻，怪兽随即伏地。" },
        { speaker = "楚成王", text = "公子能一箭穿熊掌，赵衰识异兽，魏犨又有生擒之勇。晋国诸杰文武俱备，楚国竟无一人能及！" },
        { speaker = "成得臣", text = "大王何必过誉晋臣？臣愿与魏犨比较武艺，看他是否真有万夫不当之勇。" },
        { speaker = "楚成王", text = "晋君臣是客，不可失礼。今日只论围猎，不必争强。" },
        { speaker = "楚成王", text = "公子若能返晋为君，何以报寡人今日相待之恩？" },
        { speaker = "重耳", text = "若不得已与楚兵相见于平原广泽，我愿先退避三舍，以报君王之德。" },
        { speaker = "成得臣", text = "重耳今日便敢预言与楚交兵，异日得国必成楚患。臣请杀之，至少也该留下狐偃、赵衰。" },
        { speaker = "楚成王", text = "重耳贤而从者皆国器，似有天助。留其臣不能为楚所用，只会以怨易德，此计不可。" },
        { speaker = "", text = "此时晋惠公病重，质于秦国的太子圉担心失位，抛下妻子怀嬴私逃回晋。秦穆公痛恨夷吾父子背义，派公孙枝赴楚迎接重耳。" },
        { speaker = "楚成王", text = "楚晋相隔遥远，秦晋却朝发夕至。秦君素贤，又与晋君交恶，这正是公子返国的机会。" },
        { speaker = "", text = "重耳抵达秦国，秦穆公郊迎授馆。穆姬恨太子圉无义，劝父亲把怀嬴改嫁重耳，以结秦晋之好。" },
        { speaker = "重耳", text = "怀嬴是子圉之妻，按叔侄名分便是侄妇。若为求秦援而娶她，恐怕有伤人伦。" },
        { speaker = "赵衰", text = "公子将夺子圉之国，何必独惜其妻？不能先结秦欢，又怎能借秦国之力成就大事？" },
        { speaker = "狐偃", text = "公子求入晋国，是想侍奉子圉，还是取代子圉？若欲代之，他本是仇敌，何必再问妻室名分。" },
        { speaker = "", text = "重耳终于答应婚事。秦穆公以怀嬴和四名宗女相嫁，秦晋援助由此确定。" },
        { speaker = "", text = "晋惠公病死，太子圉即位为晋怀公。他限令重耳随从三月内归国，否则诛杀亲族。狐突拒绝召回狐毛、狐偃，写下“子无二父，臣无二君”后从容受刑。" },
        { speaker = "下回预告", text = "第三十六回：晋吕郤夜焚公宫，秦穆公再平晋乱。秦国将正式发兵送重耳返晋。" }
    },
    defeat = {
        { speaker = "赵衰", text = "云梦水泽道路狭窄，猛兽冲散了围猎队。公子既受重伤，只能先退出楚境疗养。" },
        { speaker = "", text = "重耳、狐偃、赵衰或魏犨被击退，本关失败。" }
    }
}

gstage = {
    title_id = "YunmengHunt35", turn_limit = 12,
    map = { blocked_edges = {}, size = {23, 16}, terrain = {
        "FFFFFFFmmmmmmmmmFFFFFFF",
        "FFFFFFFmmmmmmmmmFFFFFFF",
        "FFFFFFgggmmmmmgggFFFFFF",
        "FFFFFggggfffffggggFFFFF",
        "FFFFgggfffffffffgggFFFF",
        "FFFgggffff~~~ffffgggFFF",
        "FFggggfff~~~~~fffggggFF",
        "Fggggffff~~~~~ffffggggF",
        "gggggfffff~~~fffffggggg",
        "gggggfffffffffffffggggg",
        "FggggfffffffffffffggggF",
        "FFgggfffffffffffgggmmFF",
        "FFFgggfffffffffgggmmmFF",
        "FFFFgggfffffffgggmmmmFF",
        "FFFFFgggfffffgggmmmmmFF",
        "FFFFFFFggfffggmmmmmmFFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {5, 12}, hero = "ChongEr27" },
        { position = {4, 13}, hero = "HuYan27" },
        { position = {6, 13}, hero = "ZhaoShuai27" },
        { position = {5, 14}, hero = "WeiChou27" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 3800 }
}

function on_deploy(game)
    game:appoint_hero("ChongEr27", 1)
    game:appoint_hero("HuYan27", 1)
    game:appoint_hero("ZhaoShuai27", 1)
    game:appoint_hero("WeiChou27", 1)
end

function on_begin(game)
    game:generate_unit("ChuChengWang33", 1, Enum.force.ally, {10, 12})
    game:generate_unit("ChuHunter35", 1, Enum.force.ally, {9, 13})
    game:generate_unit("ChuHunter35", 1, Enum.force.ally, {11, 13})
    game:generate_unit("HumanBear35", 1, Enum.force.enemy, {16, 7})
end

function on_update(game)
    if game:has_unit("MoBeast35") then
        mo_spawned = true
    end
    if not bear_defeated and not game:has_unit("HumanBear35") then
        bear_defeated = true
    end
    if bear_defeated and not mo_spawned then
        mo_spawned = true
        game:generate_unit("MoBeast35", 1, Enum.force.enemy, {19, 3})
        game:push_cmd_speak(0, "东北山谷传来怪吼，貘已经冲入围场！赵衰识得其弱点，魏犨正可上前生擒。")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if mo_spawned and not game:has_unit("MoBeast35") then return Enum.status.victory end
    return Enum.status.undecided
end