gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "JiZu11", "FuXia12" }
coalition_reinforcements_arrived = false
gduel_enabled = false
gduels = {}
gsites = {
 { id = "zheng_store", name = "郑军辎重", position = {3, 11}, restore_hp = 20, restore_mp = 15, rewards = { { item = "medicine", amount = 1 } } },
 { id = "coalition_camp", name = "四国联营", position = {15, 2}, restore_hp = 15, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } }
}
gstory = {
 chapter = "第十二回·上", title = "卫宣公筑台纳媳 高渠弥乘间易君", battle_title = "大陵拒敌",
 objective = "守住大陵，击退宋、鲁、蔡、卫四国联军", map_asset = "m016.png",
 intro = {
  { speaker = "旁白", text = "卫宣公为急子聘齐女，却贪其美色，筑新台自纳为宣姜。宣姜生寿、朔二子，公子朔又屡进谗言，欲除急子。" },
  { speaker = "旁白", text = "宣公命急子持白旄赴齐，暗令死士伏于莘野。公子寿得知阴谋，灌醉急子，夺旄代行，甘愿替兄赴死。" },
  { speaker = "公子寿", text = "兄长奉命无可逃避，便由我先行。若父侯见我因谗而死，或能醒悟。" },
  { speaker = "旁白", text = "死士误杀公子寿。急子醒后追至，见弟首级，宁愿同死，也不肯独生，兄弟二人遂一同遇害。" },
  { speaker = "旁白", text = "公子朔继位，是为卫惠公。其后郑昭公复位，卫惠公护送昭公归郑，却因未获答谢转而怨郑。" },
  { speaker = "宋庄公", text = "郑厉公许诺补足旧赂。鲁、蔡、卫既肯出兵，四国便合攻郑国，送厉公复位！" },
  { speaker = "祭足", text = "四国兵多，却各怀盘算。傅瑕守住大陵要道，我率中军随机应变，绝不可轻离阵地。" },
  { speaker = "傅瑕", text = "大陵水道狭窄，正可分割诸侯兵马。只要两翼不失，敌军虽众也难并力。" },
  { speaker = "军令", text = "祭足、傅瑕必须存活。宋军后队将在第三回合到场；击退四国全部兵马即可获胜。" }
 },
 victory = {
  { speaker = "傅瑕", text = "四国轮番进攻，彼此不能相顾。宋军已退，余军阵脚也乱了！" },
  { speaker = "旁白", text = "祭足与傅瑕守住大陵，四国联军久攻无功，只得各自引兵退去。" },
  { speaker = "旁白", text = "卫惠公归途中得知公子泄、公子职与宁跪拥立黔牟，便逃往齐国。齐襄公暂缓伐卫，将宣姜另嫁公子硕，以维系齐卫关系。" },
  { speaker = "祭足", text = "郑厉公仍据栎城，宋国又肯助他。我要亲赴齐鲁结好，为郑国另寻外援。" },
  { speaker = "下一回预告", text = "第十二回·下：祭足离郑出使，高渠弥趁郑昭公冬祭，在郊道布下伏兵。" }
 },
 defeat = { { speaker = "祭足", text = "大陵防线已破，郑国门户洞开。先收拢残军，再图后计！" } }
}
gstage = {
 title_id = "DefenseOfDaling", turn_limit = 24,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF","FggggggggffgggggggF","FggffffffffffffeggF","FggfffffffffffffggF",
  "FgggfffffffffffgggF","Fgggffff~~~~ffffggF","Fggggfffff~fffffggF","Fggggfffff~fffffggF",
  "Ffffffffff~fffffffF","Fggffff~~~~gggffffF","FggfffffffgggfffggF","FggbffffffffffffggF",
  "FggggfffffffffggggF","FFFFFgggggggggFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {3, 11}, hero = "JiZu11" }, { position = {5, 10}, hero = "FuXia12" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 680 }
}
function on_deploy(game)
 game:appoint_hero("JiZu11", 1)
 game:appoint_hero("FuXia12", 1)
end
function on_begin(game)
 game:generate_unit("AlliedGuard11", 1, Enum.force.own, {2, 10})
 game:generate_unit("AlliedArcher11", 1, Enum.force.own, {6, 11})
 game:generate_unit("SongZhuangGong11", 1, Enum.force.enemy, {15, 2})
 game:generate_unit("LuHuanGong11", 1, Enum.force.enemy, {13, 3})
 game:generate_unit("CaiJi101", 1, Enum.force.enemy, {16, 4})
 game:generate_unit("WeiHuiGong11", 1, Enum.force.enemy, {11, 3})
 game:generate_unit("SongGuard11", 1, Enum.force.enemy, {14, 4})
 game:generate_unit("QiGuard11", 1, Enum.force.enemy, {12, 5})
 game:generate_unit("CoalitionArcher11", 1, Enum.force.enemy, {16, 6})
end
function on_update(game)
 if not coalition_reinforcements_arrived and game:has_unit("SongArcher11") then coalition_reinforcements_arrived = true end
 if coalition_reinforcements_arrived or game:get_turn_current() < 3 then return end
 coalition_reinforcements_arrived = true
 local rear_guard = game:generate_unit("SongGuard11", 1, Enum.force.enemy, {16, 1})
 game:generate_unit("SongArcher11", 1, Enum.force.enemy, {17, 2})
 game:push_cmd_speak(rear_guard, "宋军后队已至！诸军并力压过大陵水道！")
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if coalition_reinforcements_arrived and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
