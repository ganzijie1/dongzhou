gsupply_enabled = true
gitems = {
 { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
 { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "LuHuanGong13" }
gduel_enabled = false
gduels = {}
gsites = {}

gstory = {
 chapter = "第十三回·上", title = "鲁桓公夫妇如齐 郑子亹君臣为戮", battle_title = "牛山车变",
 objective = "观看鲁桓公夫妇如齐及牛山车变", map_asset = "m018.png", story_only = true,
 intro = {
  { speaker = "", text = "齐襄公见祭足来聘，本欲报聘郑国，忽闻高渠弥弑昭公而立子亹，已有问罪之意；恰逢鲁桓公奉周王之命携文姜来齐议婚，便暂将郑事搁下，亲至泺水迎候。" },
  { speaker = "申繻", text = "女子出嫁，各有家室。夫人父母俱亡，此行并非归宁之礼；鲁以秉礼为国，君侯不可纵其越境。" },
  { speaker = "鲁桓公", text = "寡人已经答允夫人同行，又奉王命议婚，不必再谏。" },
  { speaker = "", text = "抵达临淄后，齐襄公将文姜迎入宫中，暗设密室私宴。鲁桓公察觉兄妹越礼，与文姜争问，文姜抵赖不认；齐襄公得知事情败露，强邀鲁侯游牛山饯行。" },
  { speaker = "齐襄公", text = "彭生，席散后由你护送鲁侯回馆。车出国门，便替寡人除了后患。" },
  { speaker = "公子彭生", text = "昔日战场一箭之辱，臣至今未忘。鲁侯醉后，车中之事无人能够看见。" },
  { speaker = "", text = "牛山宴罢，鲁桓公酩酊大醉。彭生与其同车，行至城外，以铁臂拉折鲁侯肋骨，鲁侯血流满车而死。齐襄公佯作悲恸，将罪责尽推给彭生，又当着鲁使将彭生斩首灭口。" },
  { speaker = "施伯", text = "鲁弱齐强，此等暧昧之事又不可张扬。眼下不宜兴兵，只可迫齐国诛彭生谢罪，先迎灵柩、立世子，重整朝纲。" },
  { speaker = "", text = "世子同即位，是为鲁庄公。施伯又献策为先君请命、迎回文姜，并将王姬馆舍筑在郊外，使庄公以居丧为由不亲自主婚。文姜羞归鲁宫，最终留居齐鲁边境的祝丘馆舍。" },
  { speaker = "", text = "其间周公黑肩欲乘王姬出嫁，弑周庄王而立王子克。大夫辛伯告发其谋，庄王诛黑肩、逐王子克，王子克逃往燕国。" },
  { speaker = "齐襄公", text = "国人仍议寡人无道。郑国弑君立庶，正可借讨逆之名服众。传书子亹，约在首止会盟，不必兴师远征。" },
  { speaker = "下回预告", text = "第十三回·下：子亹与高渠弥赴首止会盟，齐襄公已命死士环列盟坛。" }
 },
 victory = {}, defeat = {}
}

gstage = {
 title_id = "NiushanCarriageMurder", turn_limit = 99,
 map = { blocked_edges = {}, size = {19, 14}, terrain = {
  "FFFFFFFFFFFFFFFFFFF","FggggggfffffggggggF","FggggggfffffggggggF","FggggggfffffggggggF",
  "FgggggfffffffgggggF","FgggggfffffffgggggF","FgggggfffffffgggggF","FgggggfffffffgggggF",
  "FgggggfffffffgggggF","FggggggfffffggggggF","FggggggfffffggggggF","FggggggfffffggggggF",
  "FggggggfffffggggggF","FFFFFFFFFFFFFFFFFFF"
 }, file = "map.bmp" },
 deploy = { unselectables = { { position = {8, 8}, hero = "LuHuanGong13" } }, num_required_selectables = 0, selectables = {} },
 rewards = { equipments = {}, money = 0 }
}
function on_deploy(game) game:appoint_hero("LuHuanGong13", 1) end
function on_begin(game)
 game:generate_unit("WenJiang13", 1, Enum.force.ally, {10, 8})
 game:generate_unit("GongZiPengSheng13", 1, Enum.force.enemy, {9, 5})
end
function on_update(game) end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game) return Enum.status.undecided end
