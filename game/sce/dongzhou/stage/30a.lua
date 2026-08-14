river_spoken = false
target_spoken = false

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QiHuanGong30", "BaoShuYa30", "WangZiChengFu30", "QiHou30" }
gduel_enabled = false
gduels = {}
gsites = {
    { id = "yuanling", name = "缘陵新城", position = {3, 2}, restore_hp = 25, restore_mp = 15,
      rewards = { { item = "spirit_powder", amount = 1 } } },
    { id = "south_camp_gate", name = "诸侯营门", position = {9, 10}, restore_hp = 15, restore_mp = 5,
      rewards = {} },
    { id = "south_camp", name = "诸侯行营", position = {9, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第三十回·上",
    title = "秦晋大战龙门山 穆姬登台要大赦",
    battle_title = "缘陵救杞",
    objective = "击退淮夷主并护送杞侯进入缘陵新城（3，2）；四名有名角色任一被击退则失败",
    map_asset = "m050.png",
    intro = {
        { speaker = "", text = "管仲病中劝齐桓公远离易牙、竖刁、开方，举荐公孙隰朋。第二天他已不能言语，当夜病逝。" },
        { speaker = "齐桓公", text = "仲父去世，如同上天折断寡人一臂。以国礼厚葬，采邑交给他的后人，世代为齐国大夫。" },
        { speaker = "鲍叔牙", text = "管仲不因私交荐我，正是我当初力荐他的原因。若让我专掌刑法，易牙等人早已无处容身。" },
        { speaker = "", text = "公孙隰朋继任不足一月便病逝。齐桓公只得请鲍叔牙主持国政。" },
        { speaker = "鲍叔牙", text = "君侯若一定要用臣，必须先罢斥易牙、竖刁、开方，不许三人再入朝。" },
        { speaker = "齐桓公", text = "仲父临终也是这样告诫。寡人立即逐退三人，仍按旧政治理齐国。" },
        { speaker = "", text = "不久淮夷进犯杞国。齐桓公会合宋、鲁、陈、卫、郑、许、曹七国诸侯，亲自救援。" },
        { speaker = "杞侯", text = "淮夷沿河逼近旧都，城中百姓已经难以久守。请盟主护送宗庙与民众迁往缘陵。" },
        { speaker = "齐桓公", text = "救杞不能只击退一股敌兵，还要使百姓有可守之城。王子成父护住杞侯，向西北缘陵推进。" },
        { speaker = "鲍叔牙", text = "北部河汊不可涉越，中央道路和浅滩才是迁徙通道。先清除沿路淮夷，再护送车队。" },
        { speaker = "王子成父", text = "南营栅栏不可跨越，只能从北侧营门出发。步卒先过门，弓手随后，不要堵住杞侯车驾。" },
        { speaker = "淮夷主", text = "杞人弃城迁走，正好在河道间截住他们！弓手控制中央道路，步卒从两侧林中合围。" },
        { speaker = "杞侯", text = "宗庙器物可以再置，百姓性命不可复得。若遇伏兵，先让老弱车队退到齐军阵后。" },
        { speaker = "齐桓公", text = "诸侯从齐之令，正因我们仍守管仲旧政。此战不得劫掠，也不得追杀放下兵器的淮夷。" },
        { speaker = "鲍叔牙", text = "缘陵新城在西北聚落。击退淮夷主后，杞侯本人进入城池格才算完成迁都。" },
        { speaker = "军令", text = "河流与营地栅栏不可跨越，诸侯营门可以通行和补给。击退淮夷主，并让杞侯到达（3，2）。" }
    },
    events = {
        { id = "river_crossing", trigger = "approach", position = {9, 7}, radius = 2,
          speaker = "鲍叔牙", text = "河汊在此收窄，保持中央道路畅通，先让杞侯车驾通过！" },
        { id = "yuanling_target", trigger = "approach", position = {3, 2}, radius = 2,
          speaker = "杞侯", text = "缘陵城就在前面。只要清除淮夷主力，杞国百姓便可在此安居。" }
    },
    victory = {
        { speaker = "淮夷主", text = "七国诸侯都在齐军旗下，中央道路也已失守。继续阻拦迁都只会全军覆没，撤回淮上！" },
        { speaker = "杞侯", text = "宗庙与百姓都已抵达缘陵。杞国虽失旧都，今日总算重新有了立足之地。" },
        { speaker = "齐桓公", text = "修筑城垣、安置流民所需粮木由诸侯分担。诸军完成迁徙后依次返国。" },
        { speaker = "", text = "诸侯仍服从齐国号令，正因为鲍叔牙没有改变管仲留下的政令。" },
        { speaker = "", text = "另一边，晋惠公即位后连年歉收，第五年又逢大荒，只得派庆郑携宝玉向秦国求粮。" },
        { speaker = "秦穆公", text = "负约的是晋君，挨饿的是晋国百姓。寡人不能因夷吾无信，把灾祸转嫁给百姓。" },
        { speaker = "百里奚", text = "丰歉流转，各国都可能遭灾。救邻是常理，也为秦国留下将来求援的余地。" },
        { speaker = "", text = "秦国沿渭水运送数万斛粮食直达河、汾、雍、绛，船只首尾相连，史称泛舟之役。" },
        { speaker = "", text = "次年秦国遭灾，晋国却获丰收。秦穆公派冷至向晋国购粮，晋惠公起初准备答应。" },
        { speaker = "郤芮", text = "若承认泛舟是秦国恩德，更应先偿还扶立与割地大恩。既然大恩不报，小恩也不必报。" },
        { speaker = "庆郑", text = "幸灾是不仁，背施是不义。不仁不义，晋国靠什么守住疆土？" },
        { speaker = "虢射", text = "秦国去年不趁晋饥攻取土地，是他们愚蠢。如今秦饥，正可联合梁国反攻秦境。" },
        { speaker = "", text = "晋惠公拒绝售粮，吕饴甥、郤芮还让冷至转告秦君：想吃晋粟，只管用兵来取。" },
        { speaker = "秦穆公", text = "夷吾受秦三次大恩而无一报，如今反要联梁伐秦。传令三军先发制人，直取晋国！" },
        { speaker = "百里奚", text = "梁国空城多而百姓怨，不能真正助晋。应先声讨晋侯背德，击破晋军后再处理梁国。" },
        { speaker = "下关提示", text = "第三十回·下：秦穆公亲率三军进入韩原，白乙丙与屠岸夷、秦军与晋惠公将在龙门山决战。" }
    },
    defeat = {
        { speaker = "王子成父", text = "迁徙队伍被淮夷截断，杞侯无法抵达缘陵。先退回诸侯行营重新整队。" },
        { speaker = "", text = "齐桓公、鲍叔牙、王子成父或杞侯被击退，本关失败。" }
    }
}

gstage = {
    title_id = "RelieveQiYuanling30", turn_limit = 20,
    map = { blocked_edges = {}, size = {19, 14}, terrain = {
        "rrrFFFFF~~~~~FFFrrr",
        "rFhhhhFF~~~~~FhhhFr",
        "rFhChhFF~~~~~FhhhFr",
        "rFhhhhgg~~~ggFhhhFr",
        "rFFFgggg~~~ggFFFFFr",
        "rFFgggggg~gggggFFFr",
        "rFggggggg~ggggggFFr",
        "rFgggggfffggggggFFr",
        "rFFggggfffffggggFFr",
        "rFFFgggfffffgggFFFr",
        "FFFFFPPPPGPPPPFFFFF",
        "FFFFFPiiiiiiiPFFFFF",
        "FFFFFPiiieiiiPFFFFF",
        "FFFFFPPPPPPPPPFFFFF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {8, 12}, hero = "QiHuanGong30" },
        { position = {10, 12}, hero = "BaoShuYa30" },
        { position = {8, 11}, hero = "WangZiChengFu30" },
        { position = {9, 11}, hero = "QiHou30" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 3600 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong30", 1)
    game:appoint_hero("BaoShuYa30", 1)
    game:appoint_hero("WangZiChengFu30", 1)
    game:appoint_hero("QiHou30", 1)
end

function on_begin(game)
    game:generate_unit("QiGuard30", 1, Enum.force.own, {10, 11})
    game:generate_unit("QiArcher30", 1, Enum.force.own, {9, 12})
    game:generate_unit("HuaiYiLord30", 1, Enum.force.enemy, {15, 2})
    game:generate_unit("HuaiYiGuard30", 1, Enum.force.enemy, {13, 4})
    game:generate_unit("HuaiYiGuard30", 1, Enum.force.enemy, {15, 5})
    game:generate_unit("HuaiYiGuard30", 1, Enum.force.enemy, {6, 6})
    game:generate_unit("HuaiYiGuard30", 1, Enum.force.enemy, {12, 7})
    game:generate_unit("HuaiYiArcher30", 1, Enum.force.enemy, {14, 3})
    game:generate_unit("HuaiYiArcher30", 1, Enum.force.enemy, {11, 6})
    game:generate_unit("HuaiYiArcher30", 1, Enum.force.enemy, {6, 8})
    game:generate_unit("HuaiYiCavalry30", 1, Enum.force.enemy, {4, 7})
    game:generate_unit("HuaiYiCavalry30", 1, Enum.force.enemy, {14, 7})
end

function on_update(game)
    if not river_spoken and game:is_unit_within("QiHou30", {9, 7}, 2) then
        river_spoken = true
        game:push_cmd_speak(0, "杞侯车驾接近中央渡路，前队让开通道，弓手压制两岸！")
    end
    if not target_spoken and game:is_unit_within("QiHou30", {3, 2}, 2) then
        target_spoken = true
        game:push_cmd_speak(0, "缘陵已到，击退淮夷主后让杞侯进入城池格！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("HuaiYiLord30") and game:is_unit_within("QiHou30", {3, 2}, 0) then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
