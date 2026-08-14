gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "LianCheng14", "GuanZhiFu14" }
turenfei_revealed = false
gduel_enabled = true
gduels = {
 { attacker = "LianCheng14", defender = "TuRenFei14", exp = 35, outcome = "kill", attacker_speech = "徒人费，你果然还在护主！", defender_speech = "主君虽曾鞭我，我仍是齐臣。逆贼受死！", result_speech = "连称甲坚刃利，徒人费力战不支而死。", text = "徒人费突击连称，未能破甲，反被连称斩杀。" },
 { attacker = "LianCheng14", defender = "ShiZhiFenRu14", exp = 45, outcome = "kill", attacker_speech = "石之纷如，还不让开宫门！", defender_speech = "乱臣休想踏入寝宫半步！", result_speech = "石之纷如鏖战十余合，失足倒地，被连称杀死。", text = "石之纷如与连称交锋十余合，失足被杀。" },
 { attacker = "LianCheng14", defender = "MengYang14", exp = 25, outcome = "kill", attacker_speech = "床上之人便是齐侯，纳命来！", defender_speech = "孟阳受主君厚恩，今日以身代死！", result_speech = "孟阳身着君服，代齐襄公死于榻上。", text = "孟阳假扮齐襄公，被连称误杀于寝榻。" },
 { attacker = "LianCheng14", defender = "QiXiangGong142", exp = 55, outcome = "kill", attacker_speech = "只剩一只履，齐侯还想藏到何处？", defender_speech = "寡人悔不该拒绝瓜时代戍之约！", result_speech = "连称循遗履搜到门后，杀死齐襄公。", text = "齐襄公藏于门后，因遗履暴露踪迹，被连称杀死。" }
}
gsites = {
 { id = "gufen_gate", name = "姑棼宫门", position = {9, 6}, restore_hp = 15, restore_mp = 10, rewards = {} },
 { id = "rebel_camp", name = "葵丘行营", position = {9, 12}, restore_hp = 20, restore_mp = 15, rewards = { { item = "medicine", amount = 1 } } }
}
gstory = {
 chapter = "第十四回·下", title = "卫侯朔抗王入国 齐襄公出猎遇鬼", battle_title = "姑棼宫变",
 objective = "攻入姑棼离宫；连称相邻史实人物可触发单挑", map_asset = "m021.png",
 intro = {
  { speaker = "齐襄公", text = "连称、管至父守葵丘，待明年瓜熟，自有他人来代。" },
  { speaker = "", text = "次年瓜熟，齐襄公却拒绝换防。连称、管至父久戍生怨，转与公孙无知及宫中连妃联络，约定趁国君出猎时起事。" },
  { speaker = "管至父", text = "主君失信在先。公孙无知素有怨望，连妃又能通报宫中虚实，此事可以发动。" },
  { speaker = "", text = "齐襄公在贝丘出猎，遇见一头大豕，自称看见已死的彭生。齐侯惊惧坠车伤足，连夜退到姑棼离宫。" },
  { speaker = "孟阳", text = "臣愿穿上君服卧于寝榻，引乱兵来杀。主君可暂藏门后，等待援军。" },
  { speaker = "连称", text = "离宫守备空虚，破门后直取寝殿。谁先找到齐侯，便是首功。" },
  { speaker = "军令", text = "连称、管至父必须存活。接近宫门后徒人费才会现身；城墙不可跨越。连称与徒人费、石之纷如、孟阳、齐襄公相邻时均有史实单挑。" }
 },
 victory = {
  { speaker = "", text = "徒人费、石之纷如先后战死，孟阳代君死于寝榻。连称发现齐襄公遗落的一只履，最终在门后搜出齐侯，将其杀死。" },
  { speaker = "公孙无知", text = "齐侯既死，国中不可一日无主。诸位拥我即位，连称、管至父仍掌军政。" },
  { speaker = "管至父", text = "鲍叔牙、管夷吾等人尚在外地，须尽快安定临淄，免得诸公子回国争位。" },
  { speaker = "下回预告", text = "第十五回：齐国新君无知即位，国内反对势力暗中聚集。" }
 },
 defeat = { { speaker = "管至父", text = "宫门守军已经合围，今日事败，速退回葵丘！" } }
}
gstage = {
 title_id = "GufenPalaceCoup", turn_limit = 18,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF", "FFgggbgggggbgggggFF", "FggggggfffffggggggF", "FggggggfffffggggggF",
  "FggggggfffffggggggF", "FggggggfffffggggggF", "WWWWWWWWWGWWWWWWWWW", "FggggggfffffggggggF",
  "FgggggfffffffgggggF", "FggggffffffffffgggF", "FgggfffffffffffgggF", "FggggggfffffggggggF",
  "FggggggggeggggggggF", "FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {8, 12}, hero = "LianCheng14" }, { position = {10, 12}, hero = "GuanZhiFu14" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 760 }
}
function on_deploy(game)
 for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
 game:generate_unit("KuikouGuard14", 1, Enum.force.own, {7, 11})
 game:generate_unit("RebelArcher14", 1, Enum.force.own, {11, 11})
 game:generate_unit("QiXiangGong142", 1, Enum.force.enemy, {9, 1})
 game:generate_unit("MengYang14", 1, Enum.force.enemy, {8, 2})
 game:generate_unit("ShiZhiFenRu14", 1, Enum.force.enemy, {9, 5})
 game:generate_unit("QiPalaceGuard14", 1, Enum.force.enemy, {6, 4})
 game:generate_unit("QiPalaceGuard14", 1, Enum.force.enemy, {12, 4})
 game:generate_unit("QiPalaceArcher14", 1, Enum.force.enemy, {5, 3})
 game:generate_unit("QiPalaceArcher14", 1, Enum.force.enemy, {13, 3})
end
function on_update(game)
 if not turenfei_revealed and game:has_unit("TuRenFei14") then turenfei_revealed = true end
 if turenfei_revealed or not game:is_force_within(Enum.force.own, {9, 7}, 3) then return end
 turenfei_revealed = true
 local fei = game:generate_unit("TuRenFei14", 1, Enum.force.enemy, {8, 7})
 game:push_cmd_speak(fei, "我假意归附只为先来报信。乱臣若要进宫，先过我这一关！")
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if turenfei_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
