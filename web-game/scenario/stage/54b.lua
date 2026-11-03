gsupply_enabled = false
gitems = {{ id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 }}
gcommanders = { "XunShou54", "WeiQi54" }
gduel_enabled = true
gevents_enabled = true
gduels = {{ attacker = "XunShou54", defender = "XiangLao54", exp = 100, outcome = "kill", attacker_speech = "我儿陷于楚军，今日以你父子换回荀罃！", defender_speech = "晋军已败，还敢回头送死！", result_speech = "荀首一箭贯穿襄老面颊，襄老坠车阵亡。", text = "荀首射杀连尹襄老。" }}
gsites = {}
gstory = {
 chapter = "第五十四回·下", title = "荀林父纵属亡师 孟侏儒托优悟主", battle_title = "河口夺俘",
 objective = "荀首、魏锜由东北渡口登岸，射杀襄老并击退公子谷臣，将其生擒；完成后让荀首返回（48，8）周围两格撤离。任一我方具名将领被击退则失败。",
 map_asset = "m086.png",
 intro = {
  { speaker = "", text = "晋军争渡黄河，船少兵多，岸上哭声震谷。荀首已经登舟，却得知儿子荀罃被熊负羁生擒。" },
  { speaker = "荀首", text = "我儿既陷楚营，我不能空手回国。救不回荀罃，也要擒一名楚国贵族作为交换。" },
  { speaker = "荀林父", text = "全军正在溃退，你带数百家兵返回楚阵，无异于自投死地。" },
  { speaker = "荀首", text = "楚军正收取遗车器械，必然疏于戒备。此时一股锐气，胜过方才号令不一的六百乘。" },
  { speaker = "魏锜", text = "荀罃与我素来交厚。我愿率本部相随，襄老、谷臣正可作为交换人质。" },
  { speaker = "", text = "荀氏平日爱护士卒，岸上和已登船的下军士卒纷纷相从，数百人重新登岸。" },
  { speaker = "", text = "连尹襄老正在清点晋军遗弃车仗，公子谷臣在旁接应，完全没料到败军会折返。" },
  { speaker = "军令", text = "使荀首与襄老相邻触发史实射杀，再击退公子谷臣判定为生擒，最后返回东北渡口。" }
 },
 events = {{ id = "counterattack", trigger = "approach", position = {28,20}, radius = 5, speaker = "荀首", text = "楚军阵势松散，先取襄老！" }},
 victory = {
  { speaker = "", text = "襄老毫无防备，被荀首一箭贯穿面颊，坠车阵亡。谷臣赶来救援，又被射中右腕。" },
  { speaker = "", text = "魏锜乘势击败谷臣，将他活捉上车，又载走襄老尸体，与荀首疾驰返回黄河。" },
  { speaker = "荀首", text = "有襄老尸体和谷臣在手，足以换回荀罃。楚师势强，不可继续恋战！" },
  { speaker = "", text = "楚军反应过来时，晋军小队已经撤到渡口。后来晋楚以谷臣、襄老尸体换回荀罃。" },
  { speaker = "", text = "楚庄王抵达邲城后拒绝穷追，也不许潘党堆积晋尸为京观，只命掩埋遗骨、祭祀河神。" },
  { speaker = "楚庄王", text = "晋国并非有罪之国，寡人只是侥幸取胜，何必以尸骨夸耀武功？" },
  { speaker = "", text = "荀林父回晋请罪。晋景公本欲斩他，群臣指出先谷违令才是败因，最终斩先谷而恢复林父官职。" },
  { speaker = "", text = "两年后孙叔敖病重，遗表劝楚王不可轻视晋国，应息兵安民，又嘱儿子孙安只受贫瘠寝邱。" },
  { speaker = "", text = "孙叔敖去世，楚庄王抚棺痛哭，以公子婴齐继任令尹。孙安遵父命辞官，砍柴度日。" },
  { speaker = "", text = "优孟模仿孙叔敖衣冠言行，在宫宴以歌讽谏：廉吏生前清白，死后子孙却衣食不足。" },
  { speaker = "楚庄王", text = "孙叔之功，寡人不敢忘！召孙安入朝，赐邑万家。" },
  { speaker = "孙安", text = "若大王念先父微劳，只求寝邱薄地足以衣食。" },
  { speaker = "", text = "楚王依言封寝邱。荀林父趁孙叔敖新丧出兵掠郑郊，却不围城，只以兵威迫郑求楚。" },
  { speaker = "", text = "郑襄公以公子张换公子去疾。楚王认为国信不在质子，将两人全部遣回郑国。" },
  { speaker = "军令", text = "河口夺俘完成，获得900金币。襄老阵亡，谷臣与荀罃均为被俘后交换。" }
 }, defeat = {{ speaker = "", text = "荀首或魏锜被击退，晋军未能取得交换荀罃的人质。" }}
}
gstage = { title_id = "RiverCounterattack54", turn_limit = 20, map = { blocked_edges = {}, size = {52,34}, terrain = {
        "FFffFFffFFffFFgfFFgfFFfgFFfgFFffFFffFFffFFffFFffFFgf",
        "gfFFgfFFfgFFfgFFffFFffFFffFFffFFffFFgfFFgfFFfgFFfgFF",
        "FFffgfffgffffgfffgffffgfffgffffgfffgffffgfffgffffgff",
        "fffgffffgfffgffffgfffgffffgfffgffffgfffgffffgfffgfFF",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~wwwww",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~wwwww",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~wwwww",
        "wwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgw",
        "wgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgww",
        "gwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwg",
        "wwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgwwgw",
        "ffffgfffgffffgfffgffffgfffgffffgfffgffffgfffgffffgFF",
        "FFfgffffgfffgffffgfffgffffgfffgffffgfffgffffgfffgfff",
        "fffgfffgffffgfffgffffgfffgffffgfffgffffgfffgffffwwww",
        "FFgffffgfffgffffgfffgffffgfffgffffgfffgfwwwwwwwwwwww",
        "ffgfffgffffgfffgffffgfffgffffgffwwwwwwwwwwwwwwwwwwww",
        "FFffffgfffgffffgfffgffffwwwwwwwwwwwwwwwwwwwwwwwwfffg",
        "fgfffgffffgfffgfwwwwwwwwwwwwwwwwwwwwwwwwfgffffgfffFF",
        "FFfffgffwwwwwwwwwwwwwwwwwwwwwwwwgfffgffffgfffgffffgf",
        "wwwwwwwwwwwwwwwwwwwwwwwwfffgfffgffffgfffgffffgfffgFF",
        "wwwwwwwwwwwwwwwwfgffffgfffgffffgfffgffffgfffgffffgff",
        "wwwwwwwwgfffgffffgfffgffffgfffgffffgfffgffffgfffgfFF",
        "mmmFmmmmFmmfgfffgffffgfffgffffgfffgffffgfffgffffgfff",
        "mmFmmmmFmmmgffffgfffgffffgfffgffffgfffgffffgfffgffFF",
        "mFmmmmFmmmmgfffgffffgfffgffffgfffgffffmmmFmmmmFmmmmF",
        "FmmmmFmmmmFffffgfffgffffgfffgffffgfffgmmFmmmmFmmmmFm",
        "mmmmFmmmmFmfffgffffgfffgffffgfffgffffgmFmmmmFmmmmFmm",
        "mmmFmmmmFmmfffgfffgffffgfffgffffgfffgfFmmmmFmmmmFmmm",
        "mmFmmmmFmmmffgffffgfffgffffgfffgffffgfmmmmFmmmmFmmmm",
        "mFmmmmFmmmmffgfffgffffgfffgffffgfffgffmmmFmmmmFmmmmF",
        "FmmmmFmmmmFfgffffgfffgffffgfffgffffgffmmFmmmmFmmmmFm",
        "mmmmFmmmmFmfgfffgffffgfffgffffgfffgfffmFmmmmFmmmmFmm",
        "mmmFmmmmFmmgFFffFFffFFffFFffFFffFFgfFFFmmmmFmmmmFmmm",
        "mmFmmmmFmmmFffFFffFFgfFFgfFFfgFFfgFFffmmmmFmmmmFmmmm",
    }, file = "map.bmp" }, deploy = { unselectables = {{ position = {44,9}, hero = "XunShou54" }, { position = {46,11}, hero = "WeiQi54" }}, num_required_selectables = 0, selectables = {} }, rewards = { equipments = {}, money = 9000 } }
local function many(game,h,p,f) for _,v in ipairs(p) do game:generate_unit(h,1,f,v) end end
function on_deploy(game) for _,h in ipairs(gcommanders) do game:appoint_hero(h,1) end end
function on_begin(game)
 game:generate_unit("XiangLao54",1,Enum.force.enemy,{24,20}); game:generate_unit("GongZiGuChen54",1,Enum.force.enemy,{27,22})
 many(game,"XunFamilyGuard54",{{43,11},{45,13},{47,13},{49,11}},Enum.force.own)
 many(game,"JinReturnArcher54",{{42,9},{46,9},{50,10}},Enum.force.own)
 many(game,"ChuSalvageGuard54",{{21,18},{22,22},{25,18},{27,19},{30,21},{31,24}},Enum.force.enemy)
 many(game,"ChuSalvageCavalry54",{{19,21},{24,24},{29,17},{33,22}},Enum.force.enemy)
end
function on_update(game) end function on_victory(game) end function on_defeat(game) end
function end_condition(game) if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end if not game:has_unit("XiangLao54") and not game:has_unit("GongZiGuChen54") and game:is_unit_within("XunShou54",{48,8},2) then return Enum.status.victory end return Enum.status.undecided end
