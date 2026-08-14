gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"FanYang61"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="qin_center",name="秦军中营",position={50,18},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="qin_rear",name="秦军后营",position={53,23},restore_hp=25,restore_mp=15,rewards={}}}
gstory={chapter="第六十一回·中",title="晋悼公驾楚会萧鱼 孙林父因歌逐献公",battle_title="棫林突秦",objective="栾鍼阵亡后，保护范鞅撤回泾水西岸。",map_asset="m099.png",
 intro={
  {speaker="",text="楚共王去世后，吴王诸樊遣公子党伐楚，养由基一箭射杀公子党，吴军败退。"},
  {speaker="",text="晋悼公决定报秦救郑之怨，命荀偃率晋军及十二国诸侯伐秦。秦景公在泾水上游投毒，联军渡河受阻。"},
  {speaker="公子蟜",text="既然从晋出兵，岂能临河观望？郑军先渡泾水，卫军随后跟上！"},
  {speaker="荀偃",text="诸军鸡鸣驾车，视我马首所向而行。"},
  {speaker="栾黡",text="军旅进退岂能只说看马首？我的马首要向东，魏绛随我班师！"},
  {speaker="荀偃",text="号令不明是我的过错。下军既退，诸侯无心再战，全军撤回。"},
  {speaker="栾鍼",text="此行本为报秦，若人人无功而返，只会再添国耻。范鞅，你可愿与我突入秦阵？"},
  {speaker="范鞅",text="愿随将军。但秦营有四百乘，击破前阵后不可恋战，须留一人把消息带回。"},
  {speaker="军令",text="栾鍼、范鞅从西侧渡口突入秦营。栾鍼按原著战死后，范鞅撤回西岸即完成关卡。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="栾鍼",text="联军虽退，我二人仍要让秦军知道晋国有人！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="范鞅",text="栾将军已经战死，向西岸撤退！"}
 },
 victory={
  {speaker="",text="栾鍼连杀秦军十余人，嬴詹大军赶到，将二人重重包围。栾鍼身中七箭，力尽而死。"},
  {speaker="范鞅",text="秦军势大，继续死战只会让栾将军的消息无人带回。范鞅脱甲单车，冲出包围！"},
  {speaker="",text="范鞅独自回营，栾黡误以为他诱弟送死，拔戈追杀。范匄命范鞅暂奔秦国。"},
  {speaker="秦景公",text="范鞅能识晋国贤才，也能预见栾氏兴亡，可留作客卿。秦晋积怨至此，应当重新通聘。"},
  {speaker="",text="秦景公遣庶长武聘晋，请复范鞅之位。晋悼公同意，秦晋自此通和。"},
  {speaker="军令",text="棫林突秦完成，获得900金币。下一关：卫侯出奔。"}
 },
 defeat={{speaker="",text="范鞅被秦军击退，本关失败。"}}
}
local luan_fallen=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("FanYang61",1);game:appoint_hero("LuanZhen58",1)end
function on_begin(game)game:generate_unit("QinJingGong61",1,Enum.force.enemy,{50,18});game:set_unit_invulnerable("QinJingGong61",true);game:generate_unit("YingZhan61",1,Enum.force.enemy,{53,23});game:generate_unit("GongZiWuDi61",1,Enum.force.enemy,{44,20});many(game,"QinYulinGuard61",{{45,17},{45,22},{48,14},{51,14},{55,16},{55,25},{49,27},{44,25}},Enum.force.enemy);many(game,"QinYulinArcher61",{{47,11},{54,12},{56,20},{51,28}},Enum.force.enemy)end
function on_update(game)if not luan_fallen and not game:has_unit("LuanZhen58")then luan_fallen=true;game:push_cmd_speak(0,"栾鍼身中七箭，力尽战死！范鞅立即向西渡过泾水！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("FanYang61")then return Enum.status.defeat end if luan_fallen and game:is_unit_within("FanYang61",{16,19},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="YulinCharge61",turn_limit=24,map={blocked_edges={},size={62,40},terrain={
        "FgfffFggffffggFffgg~~~~~~fffFggfffggfFffggffffFgfffFgffffggfFf",
        "ffggffffFgffffggfFf~~~~~~ggffffFgfffggffFfggfFffggfffgFffffggf",
        "gfFfggffffgFffffFgf~~~~~~FfggffffgFfffgFffffggffFfggfffggFfffg",
        "fggffFggffFfggffffg~~~~~~fffFggffFfggfffggFfffggfffFggffFggfff",
        "fffgFfffggfffFggfff~~~~~~ggFfffggfffFggfffggfFffggFfffggfffFgf",
        "gffffggFffggffffFgf~~~~~~ffggfFffggffffFgfffFgffffggfFffggfffg",
        "fFgffffggfFfggfFffg~~~~~~gfffggffFfggfFffggfffgFffffggffFfggfF",
        "fffgFffffFgfffggffF~~~~~~fgFfffgFffffggffFfggfffggFfffgFffffgg",
        "gffFfggffffgFfffggf~~~~~~fFfggfffggFfffggfPPPPPPPPPPPPPPPPPfff",
        "fggfffFggffffggFffg~~~~~~gfffFggfffggfFffgPFfffggfffFgffffPgfF",
        "FffggffffFgfffFggff~~~~~~fggffffFgfffFgfffPggfFffggfffgFffPfFg",
        "ggfFfggfFffggffffFg~~~~~~fFfggfFffggfffgFfPffggffFfggfFfggPfff",
        "ffFgfffggffFfggffff~~~~~~FffffggffFfggfffgPFfffgFffffggffFPgff",
        "ffffgFfffggfffFggff~~~~~~fggFfffggfffFggffPggffffggFfffggfPfFg",
        "ggffffggFffggFfffgg~~~~~~fffggfFffggFfffggPffFgffffggfFffgPFff",
        "ffFgfffFggfffggfFff~~~~~~FgfffFgffffggfFffPgfffgFffffFgfffPggf",
        "fFffggffffFgfffggff~~~~~~ffggfffgFffffggffPfggfFfggffffgFfPffg",
        "ggffFfggffffgFfffgFvvvvvvffFfggfffggFfffgFPfffggffFggffffgPFff",
        "ffggfffFggffFfggfffvvvvvvggfffFggffFggffffPgFfffggeffFgfffPggf",
        "gFffggFfffggfffFggfvvvvvvffggFfffggfffFgffffggfFffggFffggfPffF",
        "FggfffggfFffggffffFvvvvvvffffggfFffggfffgFffffFgffffggfFfgPfff",
        "fffFgfffggffFfggfFf~~~~~~gFffffggffFfggfFfPgffffgFffffggffPggf",
        "gffffgFfffgFffffggf~~~~~~ffggFfffgFffffggfPFggffffggFfffgFPffg",
        "FggffFfggfffggFfffg~~~~~~gffFggffffggFfffgPfffFgfffFgeffffPgFf",
        "fffggfffFggfffggfFf~~~~~~fggfffFgffffggfFfPggFffggffffFgffPfgg",
        "gfFffggffffFgfffFgf~~~~~~FffggfffgFffffFgfPffggfFfggffffgFPfff",
        "fggffFfggfFffggfffg~~~~~~gffFfggfFfggffffgPffffggffFggffFfPgff",
        "fffgFffffggffFfggff~~~~~~fgFffffggffFggfffPggFfffgFfffggffPFgg",
        "ggfffggFfffggfffFgg~~~~~~fffggFfffggfffFgfPfFggffffggFffggPfff",
        "fFggfffggfFffggFfff~~~~~~gffffggfFffggFffgPffffFgffffggfFfPgfF",
        "ffffFgfffFgffffggfF~~~~~~fgFffffFgffffggfFPggffffgFffffFgfPfgg",
        "ggfFffggfffgFffffgg~~~~~~fFfggffffgFffffggPPPPPPPPPPPPPPPPPfff",
        "ffggffFfggfffggFfff~~~~~~ggffFggffffggFfffgFfffggfffFggffffggF",
        "FfffggfffFggffFggff~~~~~~ffggfffFgfffFggffffggFffggffffFgfffFg",
        "ggfFffggFfffggfffFg~~~~~~fFffggFffggffffFgffffggfFfggfFffggfff",
        "ffFgffffggfFffggfff~~~~~~FgffffggfFfggffffgFffffFgfffggffFfggf",
        "gfffgFffffggffFfggf~~~~~~ffgFffffggffFggffFfggffffgFfffggfffFg",
        "fggfffggFfffgFffffg~~~~~~ffffggFfffgFfffggfffFggffffggFffggFff",
        "ffFggffFggffffggFff~~~~~~FgfffFggffffggFffggffffFgfffFggfffggf",
        "gFfffggfffFgffffggf~~~~~~ffggffffFgffffggfFfggfFffggffffFgfffg",
},file="map.bmp"},deploy={unselectables={{position={31,18},hero="LuanZhen58"},{position={31,21},hero="FanYang61"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=9000}}
