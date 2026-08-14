gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"JinDaoGong60","HanJue48","XunYan58","LuanYan60"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="pengcheng_palace",name="彭城官署",position={26,9},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="pengcheng_west",name="彭城西库",position={18,17},restore_hp=20,restore_mp=10,rewards={}},{id="pengcheng_east",name="彭城东库",position={35,17},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十回·上",title="合晋楚彭城大战",battle_title="彭城复宋",objective="扫清南门楚军，接近城门触发百姓开门，再生擒鱼石等五名叛臣。晋悼公、韩厥、荀偃或栾黡被击退则失败。",map_asset="m095.png",
 intro={
  {speaker="",text="楚共王欲扰乱晋国新政，采用公子壬夫之策，资助鱼石、向为人、鳞朱、向带、鱼府五名宋国逃臣伐宋。"},
  {speaker="",text="楚郑联军攻取彭城，留下三百乘战车与五名逃臣守城。宋将老佐围城，先败鱼石，却因深入楚国援军而战死。"},
  {speaker="晋悼公",text="彭城若久据于楚，宋国必危。会合宋、鲁、卫、曹诸军，围城而不扰百姓。"},
  {speaker="韩厥",text="五名逃臣凭城固守，城中百姓却不愿随他们叛宋。先扫清城门外楚军，再逼近南门。"},
  {speaker="向戌",text="我备有临冲楼车，可隔城晓谕父老：开门者免罪，唯执五人为诛。"},
  {speaker="仲孙蔑",text="鲁军守住东侧，卫曹诸军封锁西路；晋军主攻南门，不可让楚援再入城。"},
  {speaker="",text="彭城父老早怨鱼石等人挟楚自重，只因楚兵守门，不敢响应。"},
  {speaker="鱼石",text="城中有三百乘楚车，诸侯虽众，未必能破彭城。违令开门者斩！"},
  {speaker="栾黡",text="连续城墙不可跨越。清除南门守军后，主力接近城门，由向戌登楼车劝降。"},
  {speaker="军令",text="先击退彭城南门守军并接近城门，触发百姓开门；再击退鱼石等五人，按原著视为生擒。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="向戌",text="城中父老听着：开门归宋者免罪，只执鱼石五人！"}
 },
 victory={
  {speaker="",text="向戌乘楼车临城晓谕，彭城百姓连夜缒人相约。次日城门大开，守卒倒戈，鱼石等五人束手被擒。"},
  {speaker="晋悼公",text="五人为宋国叛臣，应交宋国依法处置。楚军余众放下兵甲者，不再追杀。"},
  {speaker="",text="鱼石、向为人、鳞朱、向带、鱼府被宋国处死，彭城复归于宋。诸侯因此更加信服晋悼公。"},
  {speaker="",text="悼公随后在虎牢筑城，令魏绛执掌军法。郑国惧晋而归盟，楚国又遣兵争郑，郑国数次反覆。"},
  {speaker="魏绛",text="军令贵在必行。即使诸侯车马挡道，也不得坏我行列；但执法之后，罪责由我一人承担。"},
  {speaker="",text="悼公不但没有杀魏绛，反而命他辅佐戎事。郑国终于坚定从晋，中原形势暂时安定。"},
  {speaker="军令",text="彭城复宋完成，获得1400金币。下一关：采石水战。"}
 },
 defeat={{speaker="",text="晋军主将被击退，或未能收复彭城，本关失败。"}}
}
local gate_open=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
local rebels={"YuShi60","XiangWeiRen60","LinZhu60","XiangDai60","YuFu60"}
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("XiangShu60",1,Enum.force.ally,{20,31});game:generate_unit("ZhongSunMie60",1,Enum.force.ally,{33,31})
 game:generate_unit("YuShi60",1,Enum.force.enemy,{26,9});game:generate_unit("XiangWeiRen60",1,Enum.force.enemy,{18,17});game:generate_unit("LinZhu60",1,Enum.force.enemy,{35,17});game:generate_unit("XiangDai60",1,Enum.force.enemy,{22,22});game:generate_unit("YuFu60",1,Enum.force.enemy,{31,22})
 for _,h in ipairs(rebels)do game:set_unit_invulnerable(h,true)end
 many(game,"JinCoalitionGuard60",{{20,34},{25,35},{28,35},{33,34}},Enum.force.own);many(game,"JinCoalitionArcher60",{{18,33},{35,33}},Enum.force.own)
 many(game,"SongCoalitionGuard60",{{13,30},{16,32},{38,32},{41,30}},Enum.force.ally)
 many(game,"PengchengGuard60",{{25,26},{28,26},{23,24},{30,24},{16,14},{38,14},{20,8},{33,8}},Enum.force.enemy)
 many(game,"PengchengArcher60",{{19,23},{34,23},{14,12},{40,12},{24,6},{29,6}},Enum.force.enemy)
end
function on_update(game)
 if not gate_open and not game:has_unit("PengchengGuard60") and not game:has_unit("PengchengArcher60") and (game:is_unit_within("JinDaoGong60",{26,27},3)or game:is_unit_within("HanJue48",{26,27},3)or game:is_unit_within("XunYan58",{26,27},3)or game:is_unit_within("LuanYan60",{26,27},3))then gate_open=true;for _,h in ipairs(rebels)do game:set_unit_invulnerable(h,false)end;game:push_cmd_speak(0,"向戌登临冲楼车晓谕全城，彭城百姓已经打开南门！生擒鱼石等五人！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if gate_open then for _,h in ipairs(rebels)do if game:has_unit(h)then return Enum.status.undecided end end return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="PengchengRecapture60",turn_limit=30,map={blocked_edges={},size={54,38},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgf",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffg",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggff",
        "fggffFggfWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfggfffFgg",
        "fffgFfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFffggFfff",
        "gffffggFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffffggfF",
        "fFgffffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfgFffffgg",
        "fffgFffffWiiihhhhhhhhiiiiiiiiiiihhhhhhhhhiiiWfffggFfff",
        "gffFfggffWiiihhhhhhhhiiiiiiiiiiihhhhhhhhhiiiWggffFggff",
        "fggfffFggWiiihhhhhhhhiiiiiCiiiiihhhhhhhhhiiiWffggfffFg",
        "FffggffffWiiihhhhhhhhiiiiiiiiiiihhhhhhhhhiiiWfFffggfff",
        "ggfFfggfFWiiihhhhhhhhiiiiiiiiiiihhhhhhhhhiiiWggffFfggf",
        "ffFgfffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffgFffffg",
        "ffffgFfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggFff",
        "ggffffggFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFgffffggf",
        "ffFgfffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffgFffffF",
        "fFffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfFfggfff",
        "ggffFfggfWiiiiiiiiCiiiiiiiiiiiiiiiiCiiiiiiiiWfggffFggf",
        "ffggfffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggfffF",
        "gFffggFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfFffggFf",
        "FggfffggfWiiiiihhhhhhhiiiiiiiiiiihhhhhhhiiiiWfFgffffgg",
        "fffFgfffgWiiiiihhhhhhhiiiiiiiiiiihhhhhhhiiiiWfffgFffff",
        "gffffgFffWiiiiihhhhhhhiiiiiiiiiiihhhhhhhiiiiWgffffggFf",
        "FggffFfggWiiiiihhhhhhhiiiiiiiiiiihhhhhhhiiiiWfFgfffFgg",
        "fffggfffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFffggffff",
        "gfFffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggfFfggff",
        "fggffFfggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggffFgg",
        "fffgFffffWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWFfffgFfff",
        "ggfffggFfffggfffFggffFggffffggFfffggfffFgfffFggffffggF",
        "fFggfffggfFffggFfffggfffFgffffggfFffggFffggffffFgffffg",
        "ffffFgfffFgffffggfFffggfffgFffffFgffffggfFfggffffgFfff",
        "ggfFffggfffgFffffggffFfggfFfggffffgFffffggffFggffFfggf",
        "ffggffFfggfffggFfffgFffffggffFggffffggFfffgFfffggfffFg",
        "FfffggfffFggffFggffffggFfffggfffFgfffFggffffggFffggfff",
        "ggfFffggFfffggfffFgffffggfFffggFffggffffFgffffggfFfggf",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffg",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFff",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffgg",
    },file="map.bmp"},deploy={unselectables={{position={24,33},hero="JinDaoGong60"},{position={28,33},hero="HanJue48"},{position={22,35},hero="XunYan58"},{position={30,35},hero="LuanYan60"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=14000}}
