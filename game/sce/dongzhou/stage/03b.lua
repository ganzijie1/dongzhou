gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengWuGong", "GongZiCheng3", "WeiWuGong", "QinXiangGong", "JinWenHou" }

gduel_enabled = false
gduels = {}

gsites = {
    { id = "zheng_field_camp", name = "郑军前营", position = {2, 11}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "hao_storehouse_retake", name = "镐京府库", position = {12, 4}, restore_hp = 10, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第三回·下",
    title = "犬戎主大闹镐京 周平王东迁洛邑",
    battle_title = "四国复镐",
    objective = "郑军先破夹击；第三、第五回合诸侯援军到场后，三面夜袭收复镐京",
    map_asset = "m024.png",
    intro = {
        { speaker = "", text = "犬戎攻破镐京，周幽王、伯服皆死于骊山。戎主搬空府库，却仍盘踞王城，纵兵饮酒劫掠。" },
        { speaker = "申侯", text = "我原只想纠正王慝、复立故太子，不料竟引得君亡国破。若犬戎再不退兵，我将成华夏罪人。" },
        { speaker = "", text = "申侯暗发三封密书：北召晋侯姬仇，东请卫侯姬和，西约秦君嬴开；又遣人赴郑国报丧。" },
        { speaker = "郑掘突", text = "父亲为保王驾，死于犬戎万箭之下。君父之仇不共戴天，我即刻发兵，不可迟疑！" },
        { speaker = "公子成", text = "我军星夜奔驰，兵疲马乏。应当深沟固垒，等诸侯会齐再合攻，这才是万全之策。" },
        { speaker = "郑掘突", text = "犬戎志骄意满，我以锐气击其懈怠，往无不克。若等诸侯兵集，反而慢了复仇之心！" },
        { speaker = "", text = "郑军直逼镐京。城上偃旗息鼓，四野寂静，犬戎早已在林后布下伏兵。" },
        { speaker = "军令", text = "郑掘突与公子成必须存活。靠近南门会触发犬戎夹击；卫、秦、晋援军将于第三、第五回合到场。" },
        { speaker = "军令", text = "城墙不可跨越，四座城门均可通行但不提供补给。待诸侯会师后击退犬戎全军，即可收复镐京。" }
    },
    victory = {
        { speaker = "", text = "卫、秦、晋三路兵马趁夜从东、南、北三面攻城，申侯在城内开门接应。犬戎阵脚顿乱。" },
        { speaker = "犬戎主", text = "西门尚有空隙，弃了金帛，随我突围！" },
        { speaker = "郑掘突", text = "我早已伏在西路。今日虽未能尽灭犬戎，也要叫你们知道华夏尚有人在！" },
        { speaker = "", text = "犬戎主得满也速收拾败兵接应，混战后向西逃去。镐京失而复得，天色也已大明。" },
        { speaker = "卫武公", text = "今日君亡国破，岂是饮酒庆功之时？国不可一日无君，应迎故太子宜臼回京，即正王位。" },
        { speaker = "郑掘突", text = "迎立太子一事，我愿亲赴申国，以成先父未竟之志。" },
        { speaker = "太子宜臼", text = "父王已死，我虽是废弃之人，今日即位，终究要负不孝之名于天下。" },
        { speaker = "郑掘突", text = "殿下当以社稷为重。镐京百姓正盼新君安定人心，请勿再迟疑。" },
        { speaker = "", text = "宜臼入镐京，见宫室残毁，凄然泪下。告庙即位，是为周平王。" },
        { speaker = "周平王", text = "镐京亡而复存，全赖诸侯勤王。卫侯进爵为公，晋侯加封河内，秦君列为诸侯。" },
        { speaker = "周平王", text = "郑伯友死于王事，赐谥为桓；世子掘突袭爵为伯，并入朝任卿士。" },
        { speaker = "", text = "不久，犬戎再犯周疆，岐、丰之地半为戎有。宫阙十不存五，府库空虚，平王动了迁都洛邑之念。" },
        { speaker = "周平王", text = "洛邑居天下之中，四方朝贡道里适均。犬戎又步步逼近，朕欲东迁，诸卿以为如何？" },
        { speaker = "卫武公", text = "镐京山河险固，沃野千里。洛邑四面受敌；若弃西京而迁洛，王室从此必然衰弱。" },
        { speaker = "周平王", text = "宫阙残毁、兵力单弱，犬戎侵夺不止。朕之东迁，实非得已。" },
        { speaker = "卫武公", text = "应当节用爱民、练兵复仇，而不是退避。今日退一尺，敌明日便进一尺，蚕食之忧不会止于岐丰。" },
        { speaker = "太宰咺", text = "府库已空，百姓畏戎如虎。若强留镐京，一旦戎骑再来，民心先溃；东迁才是通变之策。" },
        { speaker = "周平王", text = "申国也送来告急文书，自顾不暇。东迁之事，朕意已决。" },
        { speaker = "", text = "大宗伯奉七庙神主先行，秦襄公亲率甲兵护驾。百姓扶老携幼，随王车浩荡东去。西周至此而亡。" },
        { speaker = "下回预告", text = "第四回·上：秦襄公受封诸侯，率军西逐犬戎，争夺岐丰故地。" }
    },
    defeat = {
        { speaker = "郑掘突", text = "君父之仇未报，我怎能先倒在镐京城外……" },
        { speaker = "", text = "勤王诸侯失去主将，只得退兵。犬戎继续盘踞镐京，宗周再无收复之机。" }
    }
}

gstage = {
    title_id = "FourStatesRetakeHaojing",
    turn_limit = 22,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FgggggggggggggggggF",
            "FgggggggfffgggggggF",
            "FgggWWWWWGWWWWWgggF",
            "FgggWiiiiiiiiiWgggF",
            "FgggWiiiiiiibiWgggF",
            "FgggWihiiiiihiWgggF",
            "FgggGiiiiiiiiiGgggF",
            "FgggWiiiiiiiiiWgggF",
            "FgggWiiieiiiiiWgggF",
            "FgggWiiiiiiiiiWgggF",
            "FgggWWWWWGWWWWWgggF",
            "FgeffffffffffgggggF",
            "FgggggggffffggggggF",
            "FFFFFFFFFFFFFFFFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {2, 11}, hero = "ZhengWuGong" },
            { position = {3, 11}, hero = "GongZiCheng3" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 420 }
}

local ambush_revealed = false
local wei_arrived = false
local coalition_arrived = false

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("ZhengGuard31", 1, Enum.force.own, {1, 10})
    game:generate_unit("ZhengGuard31", 1, Enum.force.own, {4, 12})
    game:generate_unit("CoalitionArcher31", 1, Enum.force.own, {2, 12})

    game:generate_unit("QuanRongLord", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("ManYeSu41", 1, Enum.force.enemy, {12, 6})
    game:generate_unit("QuanRongWarrior", 1, Enum.force.enemy, {7, 6})
    game:generate_unit("QuanRongWarrior2", 1, Enum.force.enemy, {9, 7})
    game:generate_unit("QuanRongWarrior", 1, Enum.force.enemy, {11, 8})
    game:generate_unit("QuanRongArcher", 1, Enum.force.enemy, {7, 4})
    game:generate_unit("QuanRongArcher", 1, Enum.force.enemy, {11, 5})
end

local function reveal_ambush(game)
    if ambush_revealed then return end
    if game:get_turn_current() < 2 and not game:is_force_within(Enum.force.own, {9, 10}, 4) then return end
    ambush_revealed = true
    local bo_ding = game:generate_unit("BoDing41", 1, Enum.force.enemy, {6, 11})
    game:generate_unit("QuanRongWarrior", 1, Enum.force.enemy, {5, 12})
    game:generate_unit("QuanRongWarrior2", 1, Enum.force.enemy, {7, 12})
    game:generate_unit("QuanRongArcher", 1, Enum.force.enemy, {6, 13})
    game:push_cmd_speak(bo_ding, "郑军只顾攻城，后路已断！孛丁在此，休想全身而退！")
end

local function bring_wei_reinforcements(game)
    if wei_arrived or game:get_turn_current() < 3 then return end
    wei_arrived = true
    local wei = game:generate_unit("WeiWuGong", 1, Enum.force.own, {17, 6})
    game:generate_unit("WeiGuard31", 1, Enum.force.own, {17, 5})
    game:generate_unit("WeiGuard31", 1, Enum.force.own, {17, 7})
    game:push_cmd_speak(wei, "郑世子放心！卫军已到。先稳住阵脚，秦、晋两军转眼便至！")
end

local function bring_coalition_reinforcements(game)
    if coalition_arrived or game:get_turn_current() < 5 then return end
    coalition_arrived = true
    local qin = game:generate_unit("QinXiangGong", 1, Enum.force.own, {8, 0})
    game:generate_unit("JinWenHou", 1, Enum.force.own, {10, 0})
    game:generate_unit("JinGuard31", 1, Enum.force.own, {7, 1})
    game:generate_unit("CoalitionArcher31", 1, Enum.force.own, {11, 1})
    game:push_cmd_speak(qin, "今夜三更，东、南、北三面齐攻，独留西门。郑世子可预伏西路，截其退兵！")
end

function on_update(game)
    if not ambush_revealed and game:has_unit("BoDing41") then ambush_revealed = true end
    if not wei_arrived and game:has_unit("WeiWuGong") then wei_arrived = true end
    if not coalition_arrived and game:has_unit("JinWenHou") then coalition_arrived = true end
    reveal_ambush(game)
    bring_wei_reinforcements(game)
    bring_coalition_reinforcements(game)
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if not game:has_unit("ZhengWuGong") or not game:has_unit("GongZiCheng3") then
        return Enum.status.defeat
    end
    if wei_arrived and not game:has_unit("WeiWuGong") then return Enum.status.defeat end
    if coalition_arrived and (not game:has_unit("QinXiangGong") or not game:has_unit("JinWenHou")) then
        return Enum.status.defeat
    end
    if coalition_arrived and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
    return Enum.status.undecided
end