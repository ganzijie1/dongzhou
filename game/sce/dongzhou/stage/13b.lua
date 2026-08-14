gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "QiXiangGong13", "WangZiChengFu13", "GuanZhiFu13" }
ambush_revealed = false
ziwei_id = -1
gaoqm_id = -1
gduel_enabled = false
gduels = {}
gsites = {
 { id = "west_qi_camp", name = "齐军西行营", position = {3, 3}, restore_hp = 20, restore_mp = 10, rewards = { { item = "medicine", amount = 1 } } },
 { id = "east_qi_camp", name = "齐军东行营", position = {15, 3}, restore_hp = 20, restore_mp = 10, rewards = { { item = "spirit_powder", amount = 1 } } }
}
gstory = {
 chapter = "第十三回·下", title = "鲁桓公夫妇如齐 郑子亹君臣为戮", battle_title = "首止诛逆",
 objective = "待郑使团进入盟坛，合围子亹与高渠弥", map_asset = "m019.png",
 intro = {
  { speaker = "", text = "齐襄公欲借诛郑国弑君之罪压下国内议论，假意致书子亹，约在首止相会为盟。子亹以为得齐国支持便可安稳君位，决定亲自赴会。" },
  { speaker = "祭足", text = "昭公有功于齐，齐侯又勇悍难测。大国忽然折节下交，必有奸谋。臣染病不能随行，请主公慎之。" },
  { speaker = "原繁", text = "若此行果然有变，郑国之后当立何人？" },
  { speaker = "祭足", text = "公子仪有君人之相。子亹若不听劝，君臣恐怕都要受戮。" },
  { speaker = "子亹", text = "齐侯既肯与寡人会盟，郑国便安如泰山。高渠弥随驾，祭足既病，就不必勉强。" },
  { speaker = "高渠弥", text = "臣会严整随从、护卫盟坛。齐侯若问昭公之事，自有臣代为应答。" },
  { speaker = "齐襄公", text = "王子成父守西营，管至父守东营。郑使团越过南路进入盟坛，再命百余死士从四面现身。" },
  { speaker = "军令", text = "齐襄公、王子成父、管至父必须存活。郑军接近盟坛后我方伏兵才会出现；击败子亹与高渠弥即可获胜。" }
 },
 victory = {
  { speaker = "", text = "齐军死士一拥而上，子亹被乱刃斩杀。高渠弥被押回临淄，车裂于南门；齐襄公遣使告郑，称已代郑国诛灭逆臣庶孽。" },
  { speaker = "原繁", text = "祭足所料无一不中，我实在不及。如今郑国不可无君，当速定嗣位之人。" },
  { speaker = "祭足", text = "厉公出亡，不可再辱宗庙。迎公子仪于陈，以叔詹、原繁辅政，先安百姓、修备边境。" },
  { speaker = "", text = "公子仪即位后，将国政委于祭足，遣使修好齐、陈，又向楚国纳贡。郑厉公暂时无隙可乘，郑国由此稍安。" },
  { speaker = "下回预告", text = "第十四回：卫侯朔抗王入国，齐襄公出猎遇鬼。" }
 },
 defeat = { { speaker = "齐襄公", text = "郑使团已经冲出首止，今日不能成事。诸军收拢死士，休要留下把柄！" } }
}
gstage = {
 title_id = "ShouzhiAllianceExecution", turn_limit = 18,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF","FFgggggfffffgggggFF","FggggggfffffggggggF","FggegggfffffgggeggF",
  "FggggggfffffggggggF","FfffffffffffffffffF","FfffffffffffffffffF","FggggggfffffggggggF",
  "FgggggggfffgggggggF","FgggggggfffgggggggF","FgggggggfffgggggggF","FgggggggfffgggggggF",
  "FgggggggfffgggggggF","FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = {
  { position = {9, 4}, hero = "QiXiangGong13" }, { position = {3, 3}, hero = "WangZiChengFu13" },
  { position = {15, 3}, hero = "GuanZhiFu13" }
 }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 720 }
}
function on_deploy(game)
 for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end
function on_begin(game)
 ziwei_id = game:generate_unit("ZiWei13", 1, Enum.force.enemy, {9, 11})
 gaoqm_id = game:generate_unit("GaoQuMi13", 1, Enum.force.enemy, {8, 12})
 game:generate_unit("ZhengEscort13", 1, Enum.force.enemy, {7, 11})
 game:generate_unit("ZhengEscort13", 1, Enum.force.enemy, {10, 12})
 game:generate_unit("ZhengArcher13", 1, Enum.force.enemy, {11, 11})
end
function on_update(game)
 if not ambush_revealed and game:has_unit("QiDeadman13") then ambush_revealed = true end
 if ambush_revealed or not game:is_force_within(Enum.force.enemy, {9, 6}, 3) then return end
 ambush_revealed = true
 local deadman = game:generate_unit("QiDeadman13", 1, Enum.force.own, {7, 6})
 game:generate_unit("QiDeadman13", 1, Enum.force.own, {11, 6})
 game:generate_unit("QiDeadman13", 1, Enum.force.own, {7, 8})
 game:generate_unit("QiDeadman13", 1, Enum.force.own, {11, 8})
 game:generate_unit("QiArcher13", 1, Enum.force.own, {9, 2})
 game:push_cmd_speak(deadman, "奉齐侯命问郑君：先君昭公，因何而亡？")
 game:push_cmd_speak(ziwei_id, "先君偶染寒疾，又受盗贼惊扰，故而暴亡。此事与寡人无涉！")
 game:push_cmd_speak(gaoqm_id, "齐侯设伏相欺！护住主公，先冲出南路再说！")
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
 if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
 if ambush_revealed and game:get_num_enemies_alive() == 0 then return Enum.status.victory end
 return Enum.status.undecided
end
