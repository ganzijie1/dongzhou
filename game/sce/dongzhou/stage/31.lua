pursuers_arrived = false
fork_spoken = false
bodi_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = {
    "ChongEr27", "HuMao27", "HuYan27", "ZhaoShuai27", "XuChen27",
    "WeiChou27", "HuSheGu27", "DianJie27", "JieZiTui27", "XianZhen27"
}
gduel_enabled = false
gduels = {}
gsites = {}

gstory = {
    chapter = "第三十一回",
    title = "晋惠公怒杀庆郑 介子推割股啖君",
    battle_title = "翟国脱险",
    objective = "护送重耳本人到达东北出口（17，1）；第三回合勃鞮与刺客从西南追入；十名有名角色任一被击退则失败",
    map_asset = "m052.png",
    intro = {
        { speaker = "", text = "秦穆公接受晋国割让河西五城、送世子圉入秦为质的条件，将韩原被俘的晋惠公放归。夷吾回到晋国，仍把战败之耻迁怒于臣下。" },
        { speaker = "晋惠公", text = "韩原出兵之前，庆郑屡次以秦国三恩责备寡人；战阵崩溃时，他又不来救驾。如此不忠之臣，岂可再留？" },
        { speaker = "庆郑", text = "臣劝君报恩，是为晋国；臣不救无道，是明君臣大义。今日受刑，臣无所逃，也无所惧。" },
        { speaker = "蛾晰", text = "庆郑虽言语峻切，毕竟是晋国直臣。君侯若因一时之怒杀他，只会使群臣更不敢进谏。" },
        { speaker = "晋惠公", text = "寡人受辱于秦，正需整肃国政。将庆郑推出斩首，再有替他求情者一并治罪！" },
        { speaker = "", text = "庆郑拒绝出逃，从容受刑。晋惠公随后又想起仍在翟国的重耳，担心国人拥立兄长，密令寺人勃鞮带刺客赶往翟境。" },
        { speaker = "晋惠公", text = "重耳在翟多年，随从日众。你上次只斩断他的衣袖，这一次须秘密行事，不可再让他脱身。" },
        { speaker = "勃鞮", text = "臣熟悉蒲城旧党，也识得翟国道路。请君侯给我三日，定将重耳首级带回绛都。" },
        { speaker = "", text = "狐突从朝中得知密谋，立即遣人疾驰翟国。第一封警书刚到，重耳还舍不得离开已经生活十二年的翟国。" },
        { speaker = "重耳", text = "翟君厚待我，季隗又与我育有伯鯈、叔刘。只凭一封急信便弃家远行，恐怕是虚惊。" },
        { speaker = "狐偃", text = "舅父绝不会拿公子的性命开玩笑。夷吾既能杀里克、丕郑父和庆郑，也必容不下兄长。" },
        { speaker = "", text = "不久狐突第二封急信送到，说明勃鞮已经受命启程。重耳这才召集赵衰、狐毛、狐偃、介子推等人，决定连夜离开。" },
        { speaker = "季隗", text = "公子只管远行，不必挂念我与两个孩子。我今年二十五，再等二十五年；若仍不回来，我再嫁不迟。" },
        { speaker = "重耳", text = "我若得归晋国，必来迎你。眼下勃鞮追兵将至，众人轻装上路，不可惊动翟国百姓。" },
        { speaker = "赵衰", text = "东北岔路通往卫境。我们没有车马，须沿林间主路急行；进入密林会增加移动消耗。" },
        { speaker = "魏犨", text = "我与颠颉留在后队。勃鞮若追上来，我们只管阻截，不为恋战偏离公子。" },
        { speaker = "介子推", text = "此行仓促，最要紧的是保全公子。粮食财物都可舍弃，十名同行者却不可折损一人。" },
        { speaker = "狐偃", text = "前方道路分成三股，认准东北宽路。勃鞮第三回合便会追到西南入口，不要在岔路停留。" },
        { speaker = "军令", text = "只有重耳本人进入（17，1）才算胜利，其他人先到不会过关。第三回合追兵登场；树林消耗较高，岩山不可通行。" }
    },
    events = {
        { id = "bodi_pursuit", trigger = "turn", turn = 3,
          speaker = "勃鞮", text = "重耳刚离开翟境，足迹还新！刺客沿主路急追，弓手封住前方岔口！" },
        { id = "forest_fork", trigger = "approach", position = {10, 5}, radius = 2,
          speaker = "狐偃", text = "东北主路就在前面。重耳继续赶路，后队利用林缘迟滞追兵，不要回头恋战！" }
    },
    victory = {
        { speaker = "勃鞮", text = "又迟了一步！前方已是卫国道路，沿途关卡都不肯让晋军越境，只能回去复命。" },
        { speaker = "重耳", text = "我在翟国安居十二年，今日又成无家可归之人。诸位仍愿同行，这份情义重耳绝不敢忘。" },
        { speaker = "", text = "重耳一行进入卫国。卫文公嫌他是失国公子，不肯以礼相待，也没有供给车马粮食。" },
        { speaker = "卫文公", text = "晋国公子流亡多年，自家尚不能容他，卫国何必卷入兄弟之争？给些清水，让他们尽快出境。" },
        { speaker = "赵衰", text = "卫君拒绝接待，我们不可强求。齐桓公尚在临淄，若能到齐国，或许可以得到庇护。" },
        { speaker = "", text = "行至五鹿，众人断粮数日。重耳向田间农夫求食，农夫却捧起一块土坷垃放在他手中。" },
        { speaker = "重耳", text = "我等饥饿求食，你们却用泥土戏弄落难之人，难道以为我连惩戒之力也没有吗？" },
        { speaker = "狐偃", text = "有土便是得国之兆。百姓以土地奉公子，正应拜受，怎可因一时饥饿而发怒？" },
        { speaker = "", text = "重耳转怒为喜，向农夫再拜收下泥土。可泥土终究不能充饥，随从们采摘野菜，仍无法让公子下咽。" },
        { speaker = "介子推", text = "公子承担晋国宗庙之望，不能倒在荒野。我身上这块肉尚可救急，何必让众人知道来处。" },
        { speaker = "", text = "介子推走入山谷，从自己腿上割下一块肉，与野菜一同煮成羹汤。赵衰将汤送到重耳面前。" },
        { speaker = "赵衰", text = "刚得来一点肉食，公子先用这碗汤恢复体力。前方还有很长的路，不能再空腹赶路。" },
        { speaker = "重耳", text = "荒野之中从何得肉？若是夺取百姓牲畜，我宁可挨饿，也不能因自己流亡害人。" },
        { speaker = "赵衰", text = "这是介子推割下腿肉所煮。他怕公子不肯吃，才让我隐瞒。" },
        { speaker = "重耳", text = "介子推以身体救我，我若有重返晋国的一天，必当厚报这份恩德！" },
        { speaker = "介子推", text = "我只愿公子安然脱险，并非为了日后封赏。眼下应尽快赶到齐国，不要为我耽搁。" },
        { speaker = "", text = "一行人终于抵达齐国。齐桓公以诸侯之礼接待重耳，将宗女长卫姬嫁给他，又赠送良马二十乘。" },
        { speaker = "齐桓公", text = "公子历经患难而随从不散，可见将来必有作为。齐国愿供衣食车马，你先在临淄安心居住。" },
        { speaker = "长卫姬", text = "公子远来，齐国便是暂时的家。往日颠沛已经过去，不必时时担心追兵。" },
        { speaker = "", text = "重耳在齐渐渐安于富贵。与此同时，齐桓公思念易牙的调味、竖刁的侍奉与开方的恭顺，不顾管仲遗言，又将三人召回。" },
        { speaker = "鲍叔牙", text = "先君遗命不可违，三人本性也不会改变。主公重新亲近他们，齐国霸业必从宫中先坏。" },
        { speaker = "齐桓公", text = "寡人只是念及旧人，不至于让他们干预国政。叔牙不必为此忧虑。" },
        { speaker = "", text = "鲍叔牙忧愤成疾，不久去世。易牙、竖刁、开方重新把持宫廷，齐国的盛势开始由内而衰。" },
        { speaker = "下回预告", text = "第三十二回：齐桓公晚年将受三奸困厄，重耳的齐国岁月也将发生新的转折。" }
    },
    defeat = {
        { speaker = "狐偃", text = "追兵已经切断退路，有名随从折损。即使重耳独自逃出，也再无力量走完流亡之路。" },
        { speaker = "", text = "重耳或任一有名随从被击退，本关失败。" }
    }
}

gstage = {
    title_id = "EscapeDi31", turn_limit = 14,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "FFrFFFFFFFFFFFFFFFF",
            "FFFggggggggggfggFFF",
            "FFgggggggfgfFfggggF",
            "FgggfffffffffffgggF",
            "FggggffffffffffgggF",
            "FggggfffffffffffggF",
            "FggggfffffffffggggF",
            "FggggffffffffgggggF",
            "FgggggffffffggggggF",
            "FggggggffffggfggggF",
            "FggggfffffffffggggF",
            "FgggfgfgggggggggggF",
            "FggggggggggggggFggF",
            "FFFgFFFFFFFFFFFFrFrF"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {2, 12}, hero = "ChongEr27" },
            { position = {1, 11}, hero = "HuMao27" },
            { position = {3, 11}, hero = "HuYan27" },
            { position = {2, 10}, hero = "ZhaoShuai27" },
            { position = {4, 12}, hero = "XuChen27" },
            { position = {4, 11}, hero = "WeiChou27" },
            { position = {1, 12}, hero = "HuSheGu27" },
            { position = {3, 12}, hero = "DianJie27" },
            { position = {4, 10}, hero = "JieZiTui27" },
            { position = {5, 11}, hero = "XianZhen27" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 3800 }
}

function on_deploy(game)
    game:appoint_hero("ChongEr27", 1)
    game:appoint_hero("HuMao27", 1)
    game:appoint_hero("HuYan27", 1)
    game:appoint_hero("ZhaoShuai27", 1)
    game:appoint_hero("XuChen27", 1)
    game:appoint_hero("WeiChou27", 1)
    game:appoint_hero("HuSheGu27", 1)
    game:appoint_hero("DianJie27", 1)
    game:appoint_hero("JieZiTui27", 1)
    game:appoint_hero("XianZhen27", 1)
end

function on_begin(game) end

function on_update(game)
    if not pursuers_arrived and game:get_turn_current() >= 3 then
        pursuers_arrived = true
        bodi_id = game:generate_unit("BoDi27", 1, Enum.force.enemy, {0, 12})
        game:generate_unit("Assassin31", 1, Enum.force.enemy, {0, 11})
        game:generate_unit("Assassin31", 1, Enum.force.enemy, {1, 13})
        game:generate_unit("AssassinArcher31", 1, Enum.force.enemy, {2, 13})
        game:push_cmd_speak(bodi_id, "足迹尚新，重耳就在东北主路！刺客贴近追击，弓手寻找两格射界！")
        game:push_cmd_speak(0, "勃鞮追兵已从西南进入。重耳继续向东北出口撤离，后队不得恋战！")
    end
    if not fork_spoken and game:is_unit_within("ChongEr27", {10, 5}, 2) then
        fork_spoken = true
        game:push_cmd_speak(0, "东北宽路就在前面！只有重耳本人抵达出口才算脱险！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:is_unit_within("ChongEr27", {17, 1}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
