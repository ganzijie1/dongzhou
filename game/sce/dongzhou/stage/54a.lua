assault_started = false
gsupply_enabled = false
gitems = {{ id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 }}
gcommanders = { "ChuZhuangWang51", "GongZiYingQi51", "GongZiCe51", "LeBo51", "YangYouJi51" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}
gstory = {
 chapter = "第五十四回·上", title = "荀林父纵属亡师 孟侏儒托优悟主", battle_title = "邲之战",
 objective = "楚军进入晋中军周围触发总攻，击溃晋中军甲士并击退荀罃，将其生擒。荀林父、士会不可被击退；我方具名将领被击退则失败。",
 map_asset = "m085.png",
 intro = {
  { speaker = "", text = "晋景公命荀林父统中军、先谷为副，士会统上军、赵朔统下军，出车六百乘救郑。" },
  { speaker = "", text = "晋军抵达黄河时郑国已经降楚。士会认为救援已迟、交战无名，建议全军班师。" },
  { speaker = "士会", text = "楚军已经退郑，此时追战没有名义。保存六百乘，等待再举才是上策。" },
  { speaker = "先谷", text = "今日畏楚而退，小国今后依靠谁？我愿独自渡河迎敌！" },
  { speaker = "", text = "先谷不听帅令，赵同、赵括率本部相随。韩厥警告荀林父，副将覆没，主帅必独负其罪。" },
  { speaker = "韩厥", text = "事已至此，只能三军同进。胜则有功，败也由六卿共同承担。" },
  { speaker = "", text = "荀林父被迫全军渡河，在敖、鄗二山之间扎营。郑襄公同时劝晋楚交战，准备择强而从。" },
  { speaker = "栾书", text = "郑国反复无常，今日劝晋击楚，转身也会向楚军递送同样的话。" },
  { speaker = "", text = "孙叔敖主张先求和。蔡鸠居到晋营，却被先谷、赵氏兄弟和赵旃接连羞辱。" },
  { speaker = "先谷", text = "回去告诉楚王，晋军定要杀得楚师片甲不回！" },
  { speaker = "", text = "楚庄王大怒，乐伯请以单车挑战晋营，许伯御车、摄叔为车右。" },
  { speaker = "乐伯", text = "我左射马、右射人，射错便算输！" },
  { speaker = "", text = "乐伯左右连发，马与追兵应弦而倒，最后射杀麋鹿赠给紧追的鲍癸。" },
  { speaker = "鲍癸", text = "楚将既有箭术又知礼数，我若再追，反显晋人无礼。" },
  { speaker = "", text = "魏锜假称赴楚求和，实际请战，回营又诬称楚王拒和。赵旃则趁夜混入楚营。" },
  { speaker = "士会", text = "魏锜赵旃心怀怨望，必然激怒楚军。元帅若仍不设防，三军都将受害。" },
  { speaker = "", text = "士会命郤克、巩朔、韩穿在敖山前设伏，保护上军。赵旃败露后弃车逃入万松林。" },
  { speaker = "潘党", text = "北方尘头大起，像是晋国大军来救赵旃！" },
  { speaker = "孙叔敖", text = "尘头不高，并非全军。宁可我迫人，不使人迫我，应立刻击其中军。" },
  { speaker = "楚庄王", text = "公子婴齐攻上军，公子侧攻下军，寡人亲率中军直击荀林父！" },
  { speaker = "军令", text = "楚军三路推进。楚庄王进入（29，18）周围七格发动总攻；击溃晋中军甲士并击退荀罃。" }
 },
 events = {{ id = "bi_assault", trigger = "approach", position = {29,18}, radius = 7, speaker = "楚庄王", text = "援桴击鼓！三军同时进击！" }},
 victory = {
  { speaker = "", text = "楚王亲自击鼓，三军突然压向晋营。晋军全无准备，中军顷刻四散。" },
  { speaker = "", text = "荀罃率軘车迎赵旃，却撞上熊负羁，左骖中箭倒地，荀罃被楚军生擒。" },
  { speaker = "荀林父", text = "中军已经不能再战！各部向黄河撤退，先求渡河！" },
  { speaker = "", text = "士会上军早有准备，在敖山七寨相互呼应，全军未损一人，楚军不敢深追。" },
  { speaker = "", text = "晋中、下军争渡黄河，三十余舟倾覆。先谷竟命人砍断攀船士卒的手指。" },
  { speaker = "", text = "荀首听说儿子荀罃被俘，决定重新登岸，以楚国贵族换回儿子。" },
  { speaker = "军令", text = "邲之战完成，获得1300金币。荀罃为被俘而非死亡；下一关转入河口反击。" }
 }, defeat = {{ speaker = "", text = "楚军具名将领被击退，晋军稳住中军，邲地总攻失败。" }}
}
gstage = { title_id = "BattleOfBi54", turn_limit = 30, map = { blocked_edges = {}, size = {58,36}, terrain = {
        "FffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfg",
        "FfFgfFgFffFfFgfFgFffFfFgfFgFffFfFgfFgFffFfFgfFgFffFfFgfFgF",
        "ffFfFffFfFffFfFffFfFffFfFffFfFffFfFffFfFffFfFffFfFffFfFffF",
        "fFfffgffgffffffgffgffffffgffgffffffgffgffffffgffgffffffgFf",
        "fFffgffffffgffgffffffgffgffffffgffgffffffgffgffffffgffgfFf",
        "FffffmmrmmmrmmmrmgffgffffffgffgffffffgffgffffffgffgffffFfg",
        "FfFgfmrmmmrmmmrmmffffffgffgffffffgffgffffffgffgffffffgfFgF",
        "ffFffrmmmrmmmrmmmffgffgffffffgffgffffffgffgffffffgffgffffF",
        "fFfffmmmrmmmrmmmrfgffffffgffgffffffgffgffffffgffgffffffgFf",
        "fFffgmmrmmmrmmmrmffffgffgffffffgffgffffffgffgffffffgffgfFf",
        "FffffmrmmmrmmmrmmgffgffffffgffgffffffgffgffffffgffgffffFfg",
        "FfFgfrmmmrmmmrmmmffffffgffgffffffgffgffffffgffgffffffgfFgF",
        "ffFffmmmrmmmrmmmrffgffgffffffgffgffffffgffgffffffgffgffffF",
        "fFfffgffgffffffgffgffffffgffgffffffgffgffffffgffgffffffgFf",
        "fFffgffffffgffgffffffgffgffffffgffgffffffgffgwwwwwwwwwwwww",
        "Fffffffgffgffffffgffgffffffgffwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "FfFgffgffffffgfwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwffffgffgffffF",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwfffffgffgffffffgffgffffffgFf",
        "wwwwwwwwwwwwwwwffffffgffgffffffgffgffffffgffgffffffgffgfFf",
        "FfmmrmmmrmmmfffffgffgffffffgffgffffffgffgffffffgffgffffFfg",
        "FfmrmmmrmmmrfgffgffffffgffgffffffgffgffffffgffgffffffgfFgF",
        "ffrmmmrmmmrmgffffffgffgffffffgffgffffffgffgffffffgffgffffF",
        "fFmmmrmmmrmmfffgffgffffffgffgffffffgffgffffffgffgffffffgFf",
        "fFmmrmmmrmmmffgffffffgffgffffffgffgffffffgffgffffffgffgfFf",
        "FfmrmmmrmmmrfffffgffgffffffgffgffffffgffgffffffgffgffffFfg",
        "FfrmmmrmmmrmfgffgffffffgffgffffffgffgffffffgffgffffffgfFgF",
        "ffmmmrmmmrmmgffffffgffgffffffgffgffffffgffgffffffgffgffffF",
        "fFmmrmmmrmmmfffgffgffffffgffgffffffgffgffffffgffgffffffgFf",
        "fFmrmmmrmmmrffgffffffgffgffffffgffgffffffgffgffffffgffgfFf",
        "FfrmmmrmmmrmfffffgffgffffffgffgffffffgffgffffffgffgffffFfg",
        "FfFgffgffffffgffgffffffgffgffffffgffgffffffgffgffffffgfFgF",
        "ffFffffffgffgffffffgffgffffffgffgffffffgffgffffffgffgffffF",
        "fFffFgFfgFfFffFgFfgFfFffFgFfgFfFffFgFfgFfFffFgFfgFfFffFgFf",
        "fFfFgfFfFffFfFgfFfFffFfFgfFfFffFfFgfFfFffFfFgfFfFffFfFgfFf",
        "FffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfgFfFffFfFfg",
    }, file = "map.bmp" }, deploy = { unselectables = {
 { position = {48,18}, hero = "ChuZhuangWang51" }, { position = {47,9}, hero = "GongZiYingQi51" }, { position = {47,27}, hero = "GongZiCe51" }, { position = {45,14}, hero = "LeBo51" }, { position = {45,22}, hero = "YangYouJi51" }
}, num_required_selectables = 0, selectables = {} }, rewards = { equipments = {}, money = 13000 } }
local function many(game,h,p,f) for _,v in ipairs(p) do game:generate_unit(h,1,f,v) end end
function on_deploy(game) for _,h in ipairs(gcommanders) do game:appoint_hero(h,1) end end
function on_begin(game)
 game:generate_unit("XunLinFu47",1,Enum.force.enemy,{25,18}); game:set_unit_invulnerable("XunLinFu47",true)
 game:generate_unit("ShiHui47",1,Enum.force.enemy,{20,8}); game:set_unit_invulnerable("ShiHui47",true)
 game:generate_unit("XunYing54",1,Enum.force.enemy,{18,15})
 many(game,"ChuBiGuard54",{{43,16},{43,20},{46,16},{46,20},{42,8},{42,26}},Enum.force.own)
 many(game,"ChuBiCavalry54",{{50,12},{50,24},{53,9},{53,27}},Enum.force.own)
 many(game,"ChuBiArcher54",{{44,6},{44,30},{51,16},{51,20}},Enum.force.own)
 many(game,"JinCenterGuard54",{{22,15},{22,18},{22,21},{26,15},{26,21},{29,17},{29,20}},Enum.force.enemy)
 many(game,"JinCenterCavalry54",{{18,19},{20,23},{27,13},{31,15},{31,22}},Enum.force.enemy)
 many(game,"JinCenterArcher54",{{19,13},{24,13},{24,23},{28,19},{32,17}},Enum.force.enemy)
end
function on_update(game) if not assault_started and game:is_unit_within("ChuZhuangWang51",{29,18},7) then assault_started=true; game:push_cmd_speak(0,"楚王亲鼓，中军总攻开始！") end end
function on_victory(game) end function on_defeat(game) end
function end_condition(game) if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end if assault_started and not game:has_unit("JinCenterGuard54") and not game:has_unit("XunYing54") then return Enum.status.victory end return Enum.status.undecided end
