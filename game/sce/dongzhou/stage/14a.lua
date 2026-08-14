gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QiXiangGong14", "WeiHuiGong14", "LuZhuangGong14", "SongMinGong14", "ChenXuanGong14", "CaiAiHou14" }
royal_reinforcements_arrived = false
gduel_enabled = false
gduels = {}
gsites = {
 { id = "wei_gate", name = "卫城城门", position = {9, 4}, restore_hp = 15, restore_mp = 10, rewards = {} },
 { id = "coalition_camp", name = "五国联营", position = {9, 12}, restore_hp = 20, restore_mp = 15, rewards = { { item = "medicine", amount = 1 } } }
}
gstory = {
 chapter = "第十四回·上", title = "卫侯朔抗王入国 齐襄公出猎遇鬼", battle_title = "卫城破围",
 objective = "攻破卫城；第三回合周将子突率王师来援", map_asset = "m020.png",
 intro = {
  { speaker = "", text = "王姬病逝后，齐襄公愈发频繁往来禚地。齐军乘势攻取郱、鄑、郚三邑，纪侯不愿屈服，托国于弟嬴季后出奔，纪国由此灭亡。楚武王熊通再征随国，途中病卒；斗祈、屈重秘不发丧，迫随侯议和后才班师。" },
  { speaker = "卫惠公", text = "寡人出奔多年，公子黔牟僭居君位。今日得齐、鲁、宋、陈、蔡五国相助，必当重入卫都。" },
  { speaker = "齐襄公", text = "诸侯分兵围城，齐军先登。拿下城门，便迎卫侯朔复位。" },
  { speaker = "公子黔牟", text = "朔得罪先君而出奔，如今借外兵返国，我等唯有守城待王师。" },
  { speaker = "宁跪", text = "周天子已命子突率二百乘救卫。只要守住三日，局势尚有转机。" },
  { speaker = "子突", text = "诸侯擅自废立，是蔑视王命。我虽兵少，也要亲赴卫城解围。" },
  { speaker = "军令", text = "六名具名诸侯必须存活。城墙不可跨越，只能从城门攻入；第三回合子突率王师战车抵达后，歼灭全部守军即可获胜。" }
 },
 victory = {
  { speaker = "", text = "齐军首先登城，诸侯联军随即打开城门。子突力战杀敌数十，王师溃败后自刎而死。公子泄、公子职被齐军处死，宁跪逃往秦国。" },
  { speaker = "齐襄公", text = "黔牟毕竟是先君之子，放他回周。今日迎卫侯朔入国，诸侯各自班师。" },
  { speaker = "卫惠公", text = "寡人复位，全赖诸侯之力。卫国自此当谨事齐国。" },
  { speaker = "", text = "卫侯朔复位后，齐襄公命连称、管至父戍守葵丘，约定次年瓜熟时派人替换。" },
  { speaker = "下回预告", text = "第十四回·下：葵丘守将久戍不代，姑棼离宫将起兵变。" }
 },
 defeat = { { speaker = "齐襄公", text = "王师已破我军侧翼。诸侯暂且退兵，另图入卫之策！" } }
}
gstage = {
 title_id = "CoalitionRestoresWeiShuo", turn_limit = 22,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FgggggggggggggggggF", "FgggggggfffgggggggF", "FgggbggfffffbgggggF", "FggggggfffffggggggF",
  "WWWWWWWWWGWWWWWWWWW", "FggggggfffffggggggF", "FgggfffffffffffgggF", "FggfffffffffffffggF",
  "FgggggfffffffgggggF", "FggggffffffffffgggF", "FgggfffffffffffgggF", "FggggggfffffggggggF",
  "FggggggggeggggggggF", "FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {5, 11}, hero = "QiXiangGong14" }, { position = {7, 12}, hero = "WeiHuiGong14" },
  { position = {3, 12}, hero = "LuZhuangGong14" }, { position = {11, 12}, hero = "SongMinGong14" },
  { position = {13, 11}, hero = "ChenXuanGong14" }, { position = {15, 12}, hero = "CaiAiHou14" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 820 }
}
function on_deploy(game)
 for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
 game:generate_unit("CoalitionGuard14", 1, Enum.force.own, {8, 11})
 game:generate_unit("CoalitionArcher14", 1, Enum.force.own, {10, 11})
 game:generate_unit("QianMou14", 1, Enum.force.enemy, {9, 1})
 game:generate_unit("GongZiXie14", 1, Enum.force.enemy, {6, 2})
 game:generate_unit("GongZiZhi14", 1, Enum.force.enemy, {12, 2})
 game:generate_unit("NingGui14", 1, Enum.force.enemy, {9, 3})
 game:generate_unit("WeiGuard14", 1, Enum.force.enemy, {5, 3})
 game:generate_unit("WeiGuard14", 1, Enum.force.enemy, {13, 3})
 game:generate_unit("WeiArcher14", 1, Enum.force.enemy, {4, 2})
 game:generate_unit("WeiArcher14", 1, Enum.force.enemy, {14, 2})
end
function on_update(game)
 if not royal_reinforcements_arrived and game:has_unit("ZiTu14") then royal_reinforcements_arrived = true end
 if royal_reinforcements_arrived or game:get_turn_current() < 3 then return end
 royal_reinforcements_arrived = true
 local zitu = game:generate_unit("ZiTu14", 1, Enum.force.enemy, {2, 8})
 game:generate_unit("RoyalChariot14", 1, Enum.force.enemy, {1, 9})
 game:generate_unit("RoyalChariot14", 1, Enum.force.enemy, {3, 9})
 game:push_cmd_speak(zitu, "王命在此！二百乘随我冲阵，救出卫君黔牟！")
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if royal_reinforcements_arrived and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
