gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "GaoQuMi12" }
ambush_revealed = false
contact_dialogue_shown = false
zhao_id = -1
gduel_enabled = false
gduels = {}
gsites = {
 { id = "sacrifice_store", name = "冬祭行营", position = {5, 3}, restore_hp = 20, restore_mp = 15, rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
 { id = "ambusher_camp", name = "死士伏营", position = {15, 11}, restore_hp = 15, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } }
}
gstory = {
 chapter = "第十二回·下", title = "卫宣公筑台纳媳 高渠弥乘间易君", battle_title = "蒸祭伏杀",
 objective = "待郑昭公进入伏击圈，截断王驾退路", map_asset = "m017.png",
 intro = {
  { speaker = "旁白", text = "祭足从大陵归来，忧心郑厉公据栎为患，决定携礼出使齐鲁，为郑昭公结援。" },
  { speaker = "高渠弥", text = "祭足多智，留在国中我不敢动手。如今他远行，郑昭公冬祭出城，正是改立新君之机。" },
  { speaker = "公子亹", text = "昭公一向厌恶于你。此事若成，你我共掌国政；若败，便再无退路。" },
  { speaker = "高渠弥", text = "死士埋伏郊道两侧，只等王驾越过中央林地，再从三面合围。事后只称盗贼行凶。" },
  { speaker = "郑昭公", text = "冬蒸之祭不可失礼。祭足虽不在国中，高渠弥也应当守卫道路，为何迟迟不见？" },
  { speaker = "军令", text = "高渠弥必须存活。郑昭公接近中央伏击圈后，三队死士才会现身；击破王驾即可获胜。" }
 },
 victory = {
  { speaker = "郑昭公", text = "高渠弥……寡人早知你怀有异心，却终究未能先除后患。" },
  { speaker = "旁白", text = "死士突起，郑昭公死于冬祭归途。高渠弥托言盗贼所杀，随即拥立公子亹为郑君。" },
  { speaker = "公子亹", text = "召祭足回国，仍由他与高渠弥并执国政。眼下先稳住郑国，不可再生变乱。" },
  { speaker = "旁白", text = "郑昭公复位未满三年，便遭逆臣弑杀。祭足虽以智谋自全，郑国君位之争却远未结束。" },
  { speaker = "下一回预告", text = "第十三回：鲁桓公夫妇如齐，郑子亹与高渠弥也将赴齐会盟。" }
 },
 defeat = { { speaker = "高渠弥", text = "王驾已经冲出伏击圈。祭足若闻讯归国，我等再无动手机会！" } }
}
gstage = {
 title_id = "WinterSacrificeAmbush", turn_limit = 18,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF","FgggggggggggggggggF","FggggffffffffffgggF","FggggbffffffffffggF",
  "FgggffffgggggfffggF","FffffffggfffggffffF","FfffffggfffffggfffF","FfffffggfffffggfffF",
  "FffffffggfffggffffF","FggggffffffffffgggF","FggfffffffffffffggF","FggffffffffffffeggF",
  "FggggggggffgggggggF","FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {15, 11}, hero = "GaoQuMi12" }, { position = {14, 10}, hero = "ZhengAmbusher12" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 520 }
}
function on_deploy(game)
 game:appoint_hero("GaoQuMi12", 1)
 game:appoint_hero("ZhengAmbusher12", 1)
end
function on_begin(game)
 zhao_id = game:generate_unit("ZhengZhaoGong12", 1, Enum.force.enemy, {5, 3})
 game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {4, 4})
 game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {6, 4})
 game:generate_unit("RoyalGuard", 1, Enum.force.enemy, {5, 5})
 game:generate_unit("SongArcher11", 1, Enum.force.enemy, {7, 5})
end
function on_update(game)
 if not ambush_revealed and game:has_unit("ZhengAmbushArcher12") then ambush_revealed = true end
 if not ambush_revealed and game:is_force_within(Enum.force.enemy, {11, 8}, 5) then
  ambush_revealed = true
  local deadman = game:generate_unit("ZhengAmbusher12", 1, Enum.force.own, {11, 8})
  game:generate_unit("ZhengAmbusher12", 1, Enum.force.own, {13, 8})
  game:generate_unit("ZhengAmbushArcher12", 1, Enum.force.own, {12, 9})
  game:push_cmd_speak(deadman, "王驾已入伏击圈！封住北路，不许一人逃回新郑！")
 end
 if not contact_dialogue_shown and game:is_force_within(Enum.force.own, {5, 3}, 4) then
  contact_dialogue_shown = true
  game:push_cmd_speak(zhao_id, "沿路伏兵皆听高渠弥号令……原来今日盗贼之说，也是早已备好的！")
 end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if ambush_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
