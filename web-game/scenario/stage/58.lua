local xiongfa_captured=false
local king_wounded=false
local wei_fallen=false
local wei_fallen_turn=0
local chu_retreat=false
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"JinLiGong58","LuanShu58","ShiXie58","HanJue48","WeiQi54","LuanZhen58","XiZhi58","XiQi58","XunYan58"}
local required_commanders={"JinLiGong58","LuanShu58","ShiXie58","HanJue48","LuanZhen58","XiZhi58","XiQi58","XunYan58"}
gduel_enabled=false gevents_enabled=true gduels={}
gsites={
 {id="jin_west_camp_58",name="晋军上军行营",position={20,9},restore_hp=20,restore_mp=12,rewards={{item="medicine",amount=1}}},
 {id="jin_center_camp_58",name="晋军中军行营",position={32,9},restore_hp=20,restore_mp=12,rewards={{item="spirit_powder",amount=1}}},
 {id="jin_east_camp_58",name="晋军下军行营",position={44,9},restore_hp=20,restore_mp=12,rewards={}},
 {id="chu_west_camp_58",name="楚军左军行营",position={20,36},restore_hp=20,restore_mp=12,rewards={}},
 {id="chu_center_camp_58",name="楚军中军行营",position={32,36},restore_hp=20,restore_mp=12,rewards={}},
 {id="chu_east_camp_58",name="楚军右军行营",position={44,36},restore_hp=20,restore_mp=12,rewards={}}
}
gstory={chapter="第五十八回",title="说秦伯魏相迎医 报魏锜养叔献艺",battle_title="鄢陵交锋",
 objective="击退楚王之子熊茷，按原著视为生擒；随后令魏锜接近楚共王触发射伤左眼。养由基参战后，魏锜被击退按史实阵亡；再坚持至下一回合，触发子反醉酒、楚军连夜撤营，完整结束鄢陵之战。除魏锜外，我方具名将领被击退即失败；楚共王不可被击退。",
 map_asset="m092.png",
 intro={
  {speaker="",text="晋景公梦见蓬头巨鬼闯入宫门，控诉赵氏无罪，醒后吐血不起。群臣召桑门大巫入宫问疾。"},
  {speaker="桑门大巫",text="此鬼是先世有功之臣，子孙遭祸最惨者。怨气已深，不是祭祀可以禳解的。"},
  {speaker="晋景公",text="莫非赵氏之祖？寡人此病还有多少时日？"},
  {speaker="屠岸贾",text="这巫者本是赵盾门客，故意借鬼神替赵氏诉冤，主公不可轻信。"},
  {speaker="桑门大巫",text="臣冒死直言，君侯恐怕不能尝到今年的新麦。"},
  {speaker="",text="景公病势日重，晋国医生都不识病症。魏锜之子魏相请求赴秦，延请名医高缓。"},
  {speaker="魏相",text="医者有活人之心，邻国有恤患之义。秦晋虽有旧怨，我也要说服秦伯遣医。"},
  {speaker="秦桓公",text="晋国屡败秦师，今日怎有脸来借我秦国名医？"},
  {speaker="魏相",text="秦晋交恶，曲直并不尽在晋国。若因旧怨见死不救，既负邻国之义，也负医者之心。"},
  {speaker="秦桓公",text="大夫以正言责寡人，寡人岂敢不听。高缓即刻随你入晋。"},
  {speaker="",text="高缓到达新绛，为景公诊脉，断言病在肓上膏下，针灸药石都无法触及。"},
  {speaker="高缓",text="此病已经不可施治。君侯梦见二竖藏于膏肓，正与臣诊断相合。"},
  {speaker="晋景公",text="真是良医。虽不能治，寡人仍当厚礼送归。"},
  {speaker="",text="新麦献入宫中，屠岸贾先杀桑门大巫。景公尚未尝粥，忽然腹痛，坠厕而死。"},
  {speaker="",text="世子州蒲即位，是为晋厉公。宋国华元来晋吊丧，又劝栾书与楚国弭兵休战。"},
  {speaker="华元",text="晋楚连年争锋，宋郑夹在南北之间，百姓无岁不受兵灾。何不订盟息民？"},
  {speaker="栾书",text="楚国反复，盟约未必可信。但若子重肯主其事，晋国可以遣使相商。"},
  {speaker="栾鍼",text="楚令尹问晋国用兵有何长处，我只答两个字：整、暇。人乱我整，人忙我暇。"},
  {speaker="",text="晋士燮与楚公子罢盟于宋国西门。公子侧不满未参与盟议，旋即劝楚共王毁盟伐郑。"},
  {speaker="公子侧",text="诸侯惟利是从，盟书不过一纸。郑国既肯归楚，便该出兵保它。"},
  {speaker="",text="郑国再次背晋从楚。晋厉公不听伯宗抑制三郤之谏，反杀伯宗，随后尽起六军伐郑。"},
  {speaker="士燮",text="国君年少骄纵，国内权臣争势。此战若胜，外患虽息，内乱恐怕更近。"},
  {speaker="郤至",text="郑国朝晋暮楚，不出兵惩戒，诸侯只会更加轻视晋国。"},
  {speaker="",text="楚共王率公子侧、公子婴齐、公子壬夫疾驰救郑。两军在鄢陵相遇，各自下寨。"},
  {speaker="",text="六月晦日，楚军趁天色未明逼近晋营。晋军营内井灶遍布，一时难以展开阵列。"},
  {speaker="栾书",text="楚军已经压营列阵，我军无处成列。诸将可有破局之策？"},
  {speaker="士匄",text="削平灶土，以木板掩井，军士携带干粮净水。营内列阵后再决开营门，楚军奈何不得。"},
  {speaker="士燮",text="竖子休得妄言！兵家胜负关系国运，岂容十六岁童子在中军摇唇？"},
  {speaker="栾书",text="此童子之智胜过老将。依计平灶填井，三军从三处营门同时出阵。"},
  {speaker="潘党",text="我能七札俱穿，军中还有谁敢与我较射？"},
  {speaker="养由基",text="穿甲是力，百步穿杨才是巧。你标三叶，我按次序三箭贯之。"},
  {speaker="",text="养由基三箭依次穿叶，又一箭从潘党箭尾送出旧箭而自占其孔，潘党方才心服。"},
  {speaker="晋厉公",text="平灶填井已经完成。中军由正门出阵，上下两军分走左右门，今日与楚决战！"},
  {speaker="军令",text="先击退前队熊茷，再让魏锜接近楚共王。营寨可为双方补给，围栏不可跨越，三处营门均可通行。"}
 },
 events={
  {id="capture_xiongfa",trigger="defeat",speaker="栾书",text="熊茷已经被擒，以囚车列于阵前，引楚王亲自来救。"},
  {id="wei_shoots_king",trigger="approach",position={32,36},radius=3,speaker="魏锜",text="魏锜撇开工尹襄，张弓射中楚共王左眼！"},
  {id="yang_revenge",trigger="defeat",speaker="养由基",text="一箭已报君王之仇，军中自此称养由基为养一箭。"},
  {id="chu_night_retreat",trigger="next_turn",speaker="楚共王",text="子反醉不能起，鲁卫援军又到。全军连夜拔营，由养由基率弓弩断后。"}
 },
 victory={
  {speaker="",text="魏锜追射楚共王，箭中左眼。潘党力战护王回车，楚军一度阵脚大乱。"},
  {speaker="楚共王",text="养叔，射寡人的正是绿袍虬髯者。寡人只给你两支箭，为我报仇！"},
  {speaker="养由基",text="杀魏锜，一箭足矣。余下一箭，臣仍缴还大王。"},
  {speaker="",text="养由基一箭射中魏锜项下。栾书夺回尸首，晋军因神射阻截，不敢继续紧追。"},
  {speaker="栾鍼",text="昔日我以整暇二字回答子重。今日混战未见其整，各退未见其暇，请以酒犒其从者。"},
  {speaker="公子婴齐",text="晋国少年尚记前言。此酒我饮了，来日阵前再当面答谢。"},
  {speaker="苗贲皇",text="整顿车乘，补充士卒，秣马厉兵，明日饱食决战，何必畏楚？"},
  {speaker="",text="楚王负伤回营，公子侧请求休战一日，准备次日雪耻。小竖穀阳却把美酒谎称椒汤，接连献给公子侧。"},
  {speaker="公子侧",text="好椒汤！竖子爱我！再斟一瓯来。"},
  {speaker="",text="公子侧饮至大醉，倒卧不起。楚王得知晋军鸡鸣出战、鲁卫援军已到，十余次派人召他都无法唤醒。"},
  {speaker="公子婴齐",text="晋兵势盛，本就难以必胜。如今司马醉不能起，不如连夜班师，免受更大挫败。"},
  {speaker="楚共王",text="把子反缚在车上随军撤走。养叔率三百弓弩手断后，不可让晋军追及。"},
  {speaker="",text="黎明时晋军开营索战，只见楚营空幕。栾书欲追，士燮认为郑国已有严备，力劝收兵。"},
  {speaker="士燮",text="楚军虽退，养由基仍在后方。郑国各处严兵固守，追击无益，可以唱凯回师了。"},
  {speaker="",text="公子侧行五十里方才酒醒，得知因自己醉酒导致全军撤退，羞愤大哭。公子婴齐又以子玉兵败自尽之事相责。"},
  {speaker="公子侧",text="先大夫子玉兵败尚且自裁。我身为司马醉误军机，还有何面目再立楚军之上？"},
  {speaker="",text="公子侧最终自缢而死。至此鄢陵之战完整结束，晋军获胜，楚国退兵。"},
  {speaker="军令",text="鄢陵之战完成，获得1500金币。熊茷按被俘处理，魏锜、公子侧按原著阵亡，其余被击退角色按撤退处理。"}
 },
 defeat={{speaker="",text="晋军具名主将被击退，营内阵列崩溃，楚军乘势压入中军。"}}
}
gstage={title_id="BattleOfYanling58",turn_limit=32,map={blocked_edges={},size={64,44},terrain={
        "FFfffffFFffffgFFffffgFFfffggFFfffgfFFffggfFFffgffFFfggffFFfgfffF",
        "ffffFFgffffFFfffffFFfffffFFffffgFFffffgFFfffggFFfffgfFFffggfFFff",
        "fFFfgfffFFggfffFFgffffFFgffffFFfffffFFfffffFFffffgFFffffgFFfffgg",
        "ffggfffPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPffffFFf",
        "fgFffffPgfffffgfffffggfffffgfffffggfffffgfffffggfffffgffPffggfff",
        "FfffffgPffffggfffffgfffffggfffffgfffffggfffffgfffffggfffPfgfffFF",
        "ffffggfPfffgfffffggfffffgfffffggfffffgfffffggfffffgfffffPgfffffg",
        "FFfgfffPfggfffffgfffffggfffffgfffffggfffffgfffffggfffffgPffffggF",
        "fggffffPgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfPfffgFff",
        "gFFfffgPfffffgfffffgefffffgfffffegfffffgffffeggfffffgfffPfggffff",
        "fffffgfPfffggfffffgfffffggfffffgfffffggfffffgfffffggffffPgfffFFg",
        "ffFggffPffgfffffggfffffgfffffggfffffgfffffggfffffgfffffgPfffffgf",
        "FfgffffPggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfPfffggFF",
        "ggfffffPfffffggfffffgfffffggfffffgfffffggfffffgfffffggffPffgffff",
        "FFfffggPffffgfffffggfffffgfffffggfffffgfffffggfffffgffffPggffffF",
        "ffffgffPPPPPPPfffPPPPPPPPPPPPPPfffPPPPPPPPPPPPPffgPPPPPPPffffFgg",
        "fFFgfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgff",
        "fgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggFFf",
        "gfFfffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffff",
        "FfffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggffffFF",
        "fffgfffffggfffffgfffffggffffwwwwwwwwwfffffgfffffggfffffgfffffggf",
        "FFgfffffgfffffggfffffgfffffwwwwwwwwwwwffggfffffgfffffggfffffgffF",
        "gfffffggfffffgfffffggfffffwwwwwwwwwwwwwgfffffggfffffgfffffggfFff",
        "fFFffgfffffggfffffgfffffggwwwwwwwwwwwwwfffffgfffffggfffffgfffffg",
        "fffggfffffgfffffggfffffgffwwwwwwwwwwwwwfffggfffffgfffffggffffFFf",
        "ffFfffffggfffffgfffffggfffwwwwwwwwwwwwwffgfffffggfffffgfffffggff",
        "FgfffffgfffffggfffffgfffffwwwwwwwwwwwwwggfffffgfffffggfffffgffFF",
        "fffffggfffffgfffffggfffffgfwwwwwwwwwwwgfffffggfffffgfffffggfffff",
        "FFffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffgF",
        "ffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffFff",
        "fFFffffggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfff",
        "gfffffgPPPPPPPfffPPPPPPPPPPPPPPfgfPPPPPPPPPPPPPfffPPPPPPPfgffFFf",
        "ffFfggfPfffgfffffggfffffgfffffggfffffgfffffggfffffgfffffPgfffffg",
        "FffgfffPfggfffffgfffffggfffffgfffffggfffffgfffffggfffffgPffffgFF",
        "fggffffPgfffffggfffffgfffffggfffffgfffffggfffffgfffffggfPfffgfff",
        "FFffffgPfffffgfffffggfffffgfffffggfffffgfffffggfffffgfffPfggfffF",
        "fffffgfPfffggfffffgfefffggfffffgeffffggfffffefffffggffffPgfffFfg",
        "fFFggffPffgfffffggfffffgfffffggfffffgfffffggfffffgfffffgPfffffgf",
        "ffgffffPggfffffgfffffggfffffgfffffggfffffgfffffggfffffgfPfffgFFf",
        "ggFffffPfffffggfffffgfffffggfffffgfffffggfffffgfffffggffPffgffff",
        "FffffggPffffgfffffggfffffgfffffggfffffgfffffggfffffgffffPggfffFF",
        "fffFFffPffFFfffffFFffffgFFffffgFFfffggFFfffgfFFffggfFFffPffFFfgg",
        "FFggfffPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPFfffgfF",
        "fgffFFfggffFFfgfffFFggfffFFgffffFFgffffFFfffffFFfffffFFffffgFFff",
    },file="map.bmp"},deploy={unselectables={
 {position={32,9},hero="JinLiGong58"},{position={29,10},hero="LuanShu58"},{position={35,10},hero="ShiXie58"},{position={45,11},hero="HanJue48"},{position={21,11},hero="WeiQi54"},{position={39,12},hero="LuanZhen58"},{position={18,12},hero="XiZhi58"},{position={15,10},hero="XiQi58"},{position={48,10},hero="XunYan58"}
},num_required_selectables=0,selectables={}},rewards={equipments={},money=15000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:set_unit_invulnerable("WeiQi54",true)
 game:generate_unit("ChuGongWang58",1,Enum.force.enemy,{32,36});game:set_unit_invulnerable("ChuGongWang58",true)
 game:generate_unit("GongZiCe51",1,Enum.force.enemy,{29,37});game:generate_unit("GongZiYingQi51",1,Enum.force.enemy,{18,36});game:generate_unit("GongZiRenFu58",1,Enum.force.enemy,{46,36})
 game:generate_unit("XiongFa58",1,Enum.force.enemy,{32,29});game:generate_unit("YangYouJi51",1,Enum.force.enemy,{36,34});game:set_unit_invulnerable("YangYouJi51",true)
 game:generate_unit("PanDang58",1,Enum.force.enemy,{42,34});game:generate_unit("GongYinXiang58",1,Enum.force.enemy,{24,34})
 many(game,"JinYanlingGuard58",{{14,13},{16,13},{27,13},{30,13},{34,13},{37,13},{47,13},{49,13}},Enum.force.own)
 many(game,"JinYanlingArcher58",{{12,11},{24,11},{41,11},{52,11}},Enum.force.own)
 many(game,"ChuYanlingGuard58",{{13,33},{16,33},{27,33},{30,33},{34,33},{37,33},{48,33},{51,33}},Enum.force.enemy)
 many(game,"ChuYanlingCavalry58",{{15,29},{20,30},{27,29},{37,29},{44,30},{49,29}},Enum.force.enemy)
 many(game,"ChuYanlingArcher58",{{11,35},{22,35},{40,35},{52,35}},Enum.force.enemy)
end
function on_update(game)
 if not xiongfa_captured and not game:has_unit("XiongFa58")then xiongfa_captured=true;game:push_cmd_speak(0,"熊茷已经被击退，按原著视为生擒。晋军把囚车列于阵前，引楚王来救！")end
 if xiongfa_captured and not king_wounded and game:is_unit_within("WeiQi54",{32,36},3)then king_wounded=true;game:set_unit_invulnerable("WeiQi54",false);game:push_cmd_speak(0,"魏锜撇开工尹襄，一箭射中楚共王左眼！养由基已经锁定魏锜，保护其他晋将并让史实事件完成。")end
 if king_wounded and not wei_fallen and not game:has_unit("WeiQi54")then wei_fallen=true;wei_fallen_turn=game:get_turn_current();game:push_cmd_speak(0,"养由基一箭射中魏锜项下。魏锜按原著阵亡，晋军抢回尸首！楚军声称明日再战，继续保持阵列。")end
 if wei_fallen and not chu_retreat and game:get_turn_current()>=wei_fallen_turn+1 then chu_retreat=true;game:push_cmd_speak(0,"子反醉卧不起，楚共王已连夜拔营，由养由基率三百弓弩断后。晋军黎明发现楚营已空，鄢陵之战结束！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(required_commanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if chu_retreat then return Enum.status.victory end
 return Enum.status.undecided
end