gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QiHuanGong15", "BaoShuYa15", "YongLin15", "WangZiChengFu15", "DongGuoYa15", "NingYue15", "ZhongSunJiu15" }
qi_ambush_revealed = false
pursuit_phase = false
qinzi_fallen = false
gduel_enabled = false
gduels = {}
gsites = {
 { id = "qi_ganshi_camp", name = "齐军行营", position = {2, 2}, restore_hp = 20, restore_mp = 15, rewards = { { item = "medicine", amount = 1 } } },
 { id = "lu_ganshi_camp", name = "鲁军行营", position = {9, 12}, restore_hp = 15, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } }
}
gstory = {
 chapter = "第十五回", title = "雍大夫计杀无知 鲁庄公乾时大战", battle_title = "乾时之战",
 objective = "诱鲁军进入乾时中央发动两翼伏兵；击破鲁军前队后直接进入汶阳追击，最终击退断后的秦子。齐军七名具名将领任一被击退均失败。", map_asset = "m022.png",
 intro = {
  { speaker = "", text = "管夷吾与鲍叔牙相交多年，各自辅佐公子纠与公子小白。齐襄公遇弑后，小白奔莒，公子纠随管夷吾、召忽奔鲁。公孙无知即位仅一月，雍廪联合高傒、东郭牙设谋：雍廪在朝堂刺死无知，高傒则闭门诛杀连称、管至父。" },
  { speaker = "", text = "齐国遣使迎公子纠，鲁庄公率三百乘护送。管夷吾先驰即墨追上小白，一箭射中带钩；小白咬舌吐血诈死，改服疾驰，反而先入临淄即位，是为齐桓公。" },
  { speaker = "鲍叔牙", text = "鲁兵不肯退，必在乾时驻营。雍廪出阵诈败，宁越、仲孙湫伏于两翼；王子成父、东郭牙绕至鲁军之后。" },
  { speaker = "齐桓公", text = "寡人亲领中军。待鲁军深入，伏兵齐出，不许鲁庄公再扶公子纠争位。" },
  { speaker = "鲁庄公", text = "小白既未中箭而死，我军更不能空手回鲁。先破齐军，再送公子纠入临淄。" },
  { speaker = "管夷吾", text = "小白初立，人心未定，应当急攻。但齐军若示弱退走，切不可追得太深。" },
  { speaker = "军令", text = "七名齐军具名将领必须存活。鲁军接近乾时中央后伏兵出现；击破前队后不离开战场，立即转入汶阳追击，击退秦子才完成整场乾时之战。" }
 },
 victory = {
  { speaker = "", text = "雍廪诈败诱敌，曹沫追入重围。宁越、仲孙湫两路伏兵齐起，鲍叔牙中军如墙推进，鲁军三面受敌而溃。" },
  { speaker = "", text = "曹沫身中两箭仍杀出重围。秦子倒下鲁侯黄旗，梁子反将绣旗立于自己车上引开追兵，最终被宁越俘获，斩于军前。鲁庄公微服逃回后营。" },
  { speaker = "鲍叔牙", text = "王子成父、东郭牙已绕到鲁军退路。鲁侯虽逃出乾时，后队仍在我军掌握之中。" },
  { speaker = "", text = "鲁军连夜拔营。王子成父、东郭牙从两翼追上汶阳退路，秦子与曹沫回身断后。" },
  { speaker = "秦子", text = "主公与公子纠先走！我接住王子成父，今日即便战死，也不能让齐军追上鲁侯。" },
  { speaker = "", text = "秦子迎战王子成父，最终阵亡。曹沫左臂再中一刀，仍杀出重围；管夷吾命军士抛弃辎重，护住鲁侯和公子纠退回鲁境。" },
  { speaker = "", text = "齐军追过汶水，夺取汶阳之田。鲍叔牙随后请以大军压境，迫使鲁国交出公子纠与管、召二人。" },
  { speaker = "军令", text = "完整乾时之战完成，获得1580金币。梁子、秦子按原著阵亡，其余鲁军具名角色按撤退处理。" }
 },
 defeat = { { speaker = "齐桓公", text = "伏兵未能合围，鲁军已冲向临淄。速收拢中军再作抵挡！" } }
}
gstage = {
 title_id = "BattleOfGanshi", turn_limit = 22,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF", "FFFgggggggggggggFFF", "FFegggfffffffggggFF", "FFgggfffffffffgggFF",
  "FgggfffffffffffgggF", "FggffffwwwwwffffggF", "FggfffwwfffwwfffggF", "FggfffffffffffffggF",
  "FgggfffffffffffgggF", "FFgggfffffffffgggFF", "FFgggfffffffffgggFF", "FggggfffffffffggggF",
  "FggggggggeggggggggF", "FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {2, 2}, hero = "QiHuanGong15" }, { position = {4, 3}, hero = "BaoShuYa15" },
  { position = {9, 5}, hero = "YongLin15" }, { position = {14, 3}, hero = "WangZiChengFu15" },
  { position = {16, 2}, hero = "DongGuoYa15" }, { position = {3, 5}, hero = "NingYue15" },
  { position = {15, 5}, hero = "ZhongSunJiu15" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 1580 }
}
function on_deploy(game)
 for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
 game:generate_unit("LuZhuangGong15", 1, Enum.force.enemy, {9, 12})
 game:generate_unit("CaoMo15", 1, Enum.force.enemy, {8, 10})
 game:generate_unit("QinZi15", 1, Enum.force.enemy, {6, 11})
 game:generate_unit("LiangZi15", 1, Enum.force.enemy, {12, 11})
 game:generate_unit("GongZiJiu15", 1, Enum.force.enemy, {10, 11})
 game:generate_unit("GuanYiWu15", 1, Enum.force.enemy, {7, 12})
 game:generate_unit("ZhaoHuQi15", 1, Enum.force.enemy, {11, 12})
 game:generate_unit("LuGuard15", 1, Enum.force.enemy, {5, 11})
 game:generate_unit("LuArcher15", 1, Enum.force.enemy, {13, 11})
 for _,hero in ipairs({"LuZhuangGong15","CaoMo15","GongZiJiu15","GuanYiWu15","ZhaoHuQi15","QinZi15"}) do game:set_unit_invulnerable(hero,true) end
end
function on_update(game)
 if not qi_ambush_revealed and game:has_unit("QiAmbusher15") then qi_ambush_revealed = true end
 if not qi_ambush_revealed and game:is_force_within(Enum.force.enemy, {9, 7}, 3) then
  qi_ambush_revealed = true
  local guard = game:generate_unit("QiAmbusher15", 1, Enum.force.own, {5, 7})
  game:generate_unit("QiAmbusher15", 1, Enum.force.own, {13, 7})
  game:generate_unit("QiAmbushArcher15", 1, Enum.force.own, {3, 8})
  game:generate_unit("QiAmbushArcher15", 1, Enum.force.own, {15, 8})
  game:push_cmd_speak(guard, "鲁军已入乾时！两翼伏兵齐出，截断中军退路！")
 end
 if qi_ambush_revealed and not pursuit_phase and not game:has_unit("LiangZi15")
    and game:get_num_units_alive("LuGuard15") == 0 and game:get_num_units_alive("LuArcher15") == 0 then
  pursuit_phase = true
  game:set_unit_invulnerable("QinZi15", false)
  game:generate_unit("QiPursuer15", 1, Enum.force.own, {6, 10})
  game:generate_unit("QiPursuitArcher15", 1, Enum.force.own, {12, 10})
  game:generate_unit("LuRearGuard15", 1, Enum.force.enemy, {8, 9})
  game:generate_unit("LuRearArcher15", 1, Enum.force.enemy, {10, 9})
  game:push_cmd_speak(0, "鲁军前队已经崩溃，战斗直接转入汶阳追击！秦子回身断后，击退秦子完成整场战役。")
 end
 if pursuit_phase and not qinzi_fallen and not game:has_unit("QinZi15") then
  qinzi_fallen = true
  game:push_cmd_speak(0, "秦子战死，曹沫护送鲁侯退过汶水。齐军夺取汶阳，乾时之战结束！")
 end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if qinzi_fallen then return Enum.status.victory end
 return Enum.status.undecided
end
