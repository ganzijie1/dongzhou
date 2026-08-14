gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "WangZiChengFu152", "DongGuoYa152" }
contact_dialogue_shown = false
qinzi_id = -1
gduel_enabled = false
gduels = {}
gsites = {
 { id = "qi_pursuit_camp", name = "齐军追击营", position = {2, 12}, restore_hp = 20, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } }
}
gstory = {
 chapter = "第十五回·下", title = "雍大夫计杀无知 鲁庄公乾时大战", battle_title = "汶阳断后",
 objective = "截住鲁军后队；击溃秦子、曹沫所部", map_asset = "m023.png",
 intro = {
  { speaker = "", text = "乾时战败后，管夷吾从后营接应鲁庄公，清点兵车已折损七成，只得连夜拔营。王子成父、东郭牙早已绕出鲁军之后，在汶阳退路列阵。" },
  { speaker = "曹沫", text = "主公与公子纠先走，我留在此处挡住东郭牙。只要辎重队冲过山口，鲁军尚能回国。" },
  { speaker = "秦子", text = "我接住王子成父。今日即便战死，也不能让齐军追上鲁侯。" },
  { speaker = "王子成父", text = "鲁军大败而逃，正应乘势截断后队。东郭牙攻左，我从右路合围。" },
  { speaker = "军令", text = "王子成父、东郭牙必须存活。击溃鲁军后队即可获胜；秦子按原著战死，曹沫、鲁庄公等按撤退处理。" }
 },
 victory = {
  { speaker = "", text = "秦子接战王子成父，最终战死。曹沫与东郭牙鏖战，左臂再中一刀，仍刺杀多人后突出重围。" },
  { speaker = "", text = "鲁庄公沿路射杀两名追兵，管夷吾命军士抛弃辎重甲兵，引齐军争夺，方才护住公子纠逃回鲁境。齐军追过汶水，夺取汶阳之田。" },
  { speaker = "鲍叔牙", text = "公子纠尚在鲁国，管夷吾、召忽仍为其辅佐。请以大军压境，命鲁国杀纠，并将管、召交齐处置。" },
  { speaker = "下回预告", text = "第十六回：鲁国将议处公子纠与管仲，曹刿也将请见鲁庄公。" }
 },
 defeat = { { speaker = "王子成父", text = "鲁军后队已经冲过汶水，今日截击未成，暂且收兵！" } }
}
gstage = {
 title_id = "WenyangRearGuard", turn_limit = 18,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF", "FFFgggggggggggggFFF", "FFgggffffffffffggFF", "FgggfffffffffffgggF",
  "FggfffffffggffffggF", "FggfffffgggggfffggF", "Fgggfffggfffggfffgg", "FFgggfffggfffgggffF",
  "FfffggfffggffffgggF", "FffffggfffggffffggF", "FggffffggfffggggggF", "FgggffffggfffgggggF",
  "FgeggggffffgggggggF", "FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {2, 12}, hero = "WangZiChengFu152" }, { position = {4, 11}, hero = "DongGuoYa152" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 680 }
}
function on_deploy(game)
 for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
 game:generate_unit("QiPursuer15", 1, Enum.force.own, {1, 11})
 game:generate_unit("QiPursuitArcher15", 1, Enum.force.own, {5, 12})
 game:generate_unit("LuZhuangGong152", 1, Enum.force.enemy, {14, 2})
 game:generate_unit("CaoMo152", 1, Enum.force.enemy, {10, 6})
 qinzi_id = game:generate_unit("QinZi152", 1, Enum.force.enemy, {9, 7})
 game:generate_unit("GuanYiWu152", 1, Enum.force.enemy, {12, 4})
 game:generate_unit("GongZiJiu152", 1, Enum.force.enemy, {13, 3})
 game:generate_unit("ZhaoHuQi152", 1, Enum.force.enemy, {11, 5})
 game:generate_unit("LuRearGuard15", 1, Enum.force.enemy, {8, 8})
 game:generate_unit("LuRearArcher15", 1, Enum.force.enemy, {11, 7})
end
function on_update(game)
 if contact_dialogue_shown or not game:is_force_within(Enum.force.own, {9, 7}, 4) then return end
 contact_dialogue_shown = true
 game:push_cmd_speak(qinzi_id, "王子成父在前！主公速行，秦子今日以死断后！")
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
