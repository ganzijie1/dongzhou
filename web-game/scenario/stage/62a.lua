gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"XunYan58","ShiGai60","ZhaoWu59"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="pingyin",name="平阴城",position={42,20},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="linzi_palace",name="临淄城",position={76,13},restore_hp=25,restore_mp=20,rewards={}},{id="linzi_store",name="临淄武库",position={78,30},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十二回·上",title="诸侯同心围齐国 晋臣合力逐栾盈",battle_title="十二国伐齐",objective="突破防门、石门追俘，围临淄六回合后撤军。",map_asset="m101.png",
 intro={
  {speaker="",text="卫献公奔齐以后，齐灵公自恃国强，欲争诸侯之长；晋悼公卒，晋平公新立，诸卿决定以大军伐齐。"},
  {speaker="",text="晋会鲁、宋、卫、郑、曹、莒、邾、滕、薛、杞、小邾等国，合为十二国之师，兵锋直指齐境。"},
  {speaker="荀偃",text="齐军在防门掘沟拒守。先夺沟西阵地，再填出通路，全军不得分散涉险。"},
  {speaker="士匄",text="防门一破，析归父必退平阴；平阴若失，齐军会沿石门狭道撤向临淄。"},
  {speaker="赵武",text="此役不以弑君为功。齐灵公守临淄，列国只焚外郭、围城示威，不攻宫城。"},
  {speaker="韩起",text="十二国旗号虽多，军令只出中军。盟军守住两翼，我军连续推进三个战区。"},
  {speaker="析归父",text="防门深沟尚在，晋军纵有千乘，也休想整阵渡过。弓手压住填沟之处！"},
  {speaker="殖绰",text="若平阴不守，我与郭最退到石门。那里山道狭窄，追兵未必能展开。"},
  {speaker="齐灵公",text="寡人据临淄坚城，诸侯远来，粮尽自退。崔杼、庆封整顿外郭，不可擅出。"},
  {speaker="军令",text="击退析归父，穿过平阴；在石门击退并俘获殖绰、郭最；最后抵达临淄西门，坚持围城六回合。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="析归父",text="填沟处失守，全军退往平阴！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="周绰",text="石门追兵已至，殖绰、郭最还不下马受缚！"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="荀偃",text="围城第六日，郑国有急，诸侯军依令撤退。"}
 },
 victory={
  {speaker="",text="诸侯军越过防门，平阴齐军败退。析归父失守关隘，齐境再无完整的野战防线。"},
  {speaker="",text="殖绰、郭最据石门拒战，周绰率锐士追及，将二人击败俘获，押入晋军。"},
  {speaker="荀偃",text="临淄城墙坚固，不必强攻宫城。分兵焚毁外郭积聚，使齐国知惧即可。"},
  {speaker="",text="联军围临淄六日，火光照城。郑国急报国内有变，诸侯军遂停止攻城，班师回国。"},
  {speaker="",text="荀偃出师前梦见先父责己，回军后果然病重而卒；殖绰、郭最后来乘隙逃归齐国。"},
  {speaker="",text="同年楚军出师遇大雪，冻死者众；师旷听南风不竞，断言楚军无功，晋国北方暂安。"},
  {speaker="",text="齐灵公不久病危，崔杼迎故太子光为齐庄公；高厚及荣子、公子牙皆死于内乱。"},
  {speaker="军令",text="十二国伐齐完成，获得1500金币。下一关：高唐平叛。"}
 },
 defeat={{speaker="",text="荀偃、士匄、赵武任一被击退，或超过四十回合，战役失败。"}}
}
local phase=1 local siege_turn=-1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("HanQi62",1);game:appoint_hero("WeiJiang62",1);game:appoint_hero("ZhouChuo62",1);game:appoint_hero("LuanYing62",1)end
function on_begin(game)
game:generate_unit("XiGuiFu62",1,Enum.force.enemy,{31,28});game:generate_unit("ZhiChuo62",1,Enum.force.enemy,{61,25});game:generate_unit("GuoZui62",1,Enum.force.enemy,{61,28});game:set_unit_invulnerable("ZhiChuo62",true);game:set_unit_invulnerable("GuoZui62",true)
game:generate_unit("QiLingGong62",1,Enum.force.enemy,{76,13});game:set_unit_invulnerable("QiLingGong62",true);game:generate_unit("CuiZhu62",1,Enum.force.enemy,{71,23});game:generate_unit("QingFeng62",1,Enum.force.enemy,{72,28})
many(game,"QiCoalitionGuard62",{{22,23},{22,27},{22,31},{30,24},{30,26},{30,30},{37,23},{37,27},{46,22},{46,28},{57,23},{57,30},{70,20},{70,26},{74,34},{80,33}},Enum.force.enemy)
many(game,"QiCoalitionArcher62",{{23,20},{23,34},{32,23},{32,33},{40,18},{44,31},{58,20},{59,32},{73,18},{75,37}},Enum.force.enemy)
many(game,"JinCoalitionGuard62",{{7,27},{7,30},{14,23},{14,33}},Enum.force.own);many(game,"JinCoalitionArcher62",{{9,21},{9,37},{16,25},{16,31}},Enum.force.own)
end
function on_update(game)
if phase==1 and not game:has_unit("XiGuiFu62")then phase=2;game:push_cmd_speak(0,"防门已破，析归父退走！诸军穿过平阴，继续向石门追击。");game:set_unit_invulnerable("ZhiChuo62",false);game:set_unit_invulnerable("GuoZui62",false)end
if phase==2 and not game:has_unit("ZhiChuo62") and not game:has_unit("GuoZui62")then phase=3;game:push_cmd_speak(0,"殖绰、郭最已在石门被俘。中军向临淄西门推进，不可攻击齐侯宫城。");end
if phase==3 and game:is_unit_within("XunYan58",{68,24},3)then phase=4;siege_turn=game:get_turn_current();game:push_cmd_speak(0,"临淄合围。自本回合起围城六日，焚外郭而不攻宫城。");end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==4 and game:get_turn_current()>=siege_turn+6 then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="QiCampaign62",turn_limit=40,map={blocked_edges={},size={86,56},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfffgFffffFgffffggfFfg",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggfFfggffffgFffffggff",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffggffFggffffggFfffgF",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFggffffggFfffggfffFgfffFggffff",
        "fffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffggFfffggfffFgffffggfFffggFffggffffFgff",
        "gffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFfmmmmmmmmmmffFWWWWWWWWWWWWWWWWWF",
        "fFgffffggfFfggfFffggffffF~~~~ggffFfggfFffggfffgFffffggfmmmmmmmmmmfffWiiiiiiiiiiiiiiiWf",
        "fffgFffffFgfffggffFfggfff~~~~ffgFffffggffFfggfffggFfffgmmmmmmmmmmggfWiiiiiiiiiiiiiiiWf",
        "gffFfggffffgFfffggfffFggf~~~~gfffggFfffggfffFggffFggfffmmmmmmmmmmffFWiiiiiiiiiiiiiiiWg",
        "fggfffFggffffggFffggFfffg~~~~FggfffggfFffggFfffggfffFgfmmmmmmmmmmgFfWiiiiiiiiiiiiiiiWf",
        "FffggffffFgfffFggfffggfFf~~~~fffFgfffFgffffggfFffggfffgmmmmmmmmmmfggWiiiiiiiiiiiiiiiWf",
        "ggfFfggfFffggffffFgfffggf~~~~gfFffggfffgFffffggffFfggfFmmmmmmmmmmfffWiiiiiiiiiiiiiiiWg",
        "ffFgfffggffFfggffffgFfffg~~~~fggffFfggfffggFfffgFffffggmmmmmmmmmmgFfWiiiiiiiiiiiiiiiWf",
        "ffffgFfffggfffFggffFfggff~~~~fffggfffFggffFggffffggFfffmmmmmmmmmmFggWiiiiiiiCiiiiiiiWf",
        "ggffffggFffggFfffggfffFgg~~~~gfFffWWWWWWWWWWWWWWWWfggfFmmmmmmmmmmfffWiiiiiiiiiiiiiiiWg",
        "ffFgfffFggfffggfFffggffff~~~~fFgffWiiiiiiiiiiiiiiWfffFgmmmmmmmmmmgffWiiiiiiiiiiiiiiiWF",
        "fFffggffffFgfffggffFfggfF~~~~fffgFWiiiiiiiiiiiiiiWgffffmmmmmmmmmmFggWiiiiiiiiiiiiiiiWf",
        "ggffFfggffffgFfffgFffffgg~~~~ggfffWiiiiiiiiiiiiiiWFggffmmmmmmmmmmfffWiiiiiiiiiiiiiiiWg",
        "ffggfffFggffFfggfffggFfff~~~~fFggfWiiiiiiiiiiiiiiWfffFgmmmmmmmmmmggFWiiiiiiiiiiiiiiiWf",
        "gFffggFfffggfffFggfffggfF~~~~FfffgWiiiiiiiiiiiiiiWggFffmmmmmmmmmmffgWiiiiiiiiiiiiiiiWg",
        "FggfffggfFffggffffFgfffFg~~~~ggfFfWiiiiiiiCiiiiiiWffggfmmmmmmmmmmfffWiiiiiiiiiiiiiiiWf",
        "fffFgfffggffFfggfFffggfff~~~~ffggfWiiiiiiiiiiiiiiWffffgmmmmmmmmmmggfWiiiiiiiiiiiiiiiWf",
        "gffffgFfffgFffffggffFfggf~~~~FfffgWiiiiiiiiiiiiiiWggFffmmmmmmmmmmfFgWiiiiiiiiiiiiiiiWg",
        "FggffFfggfffggFfffggfffFg~~~~ggfffWiiiiiiiiiiiiiiWfFggfmmmmmmmmmmfffWiiiiiiiiiiiiiiiWf",
        "fffggfffFggfffggfFffggFff~~~~ffFgfGiiiiiiiiiiiiiiGffffffffffffffffffGiiiiiiiiiiiiiiiWf",
        "gfFffggffffFgfffFgffffggf~~~~gfffgGiiiiiiiiiiiiiiGggfffffffffffffffgGiiiiiiiiiiiiiiiWF",
        "fggffFfggfFffggfffgFffffg~~~~fggfFWiiiiiiiiiiiiiiWfFgfffffffffffffffWiiiiiiiiiiiiiiiWf",
        "fffgFffffggffFfggfffggFffvvvvfffggWiiiiiiiiiiiiiiWFffffffffffffffffgWiiiiiiiiiiiiiiiWf",
        "ggfffggFfffggfffFggffFggfvvvvgFfffWiiiiiiiiiiiiiiWfggffffffffffffffFWiiiiiiiiiiiiiiiWF",
        "fFggfffggfFffggFfffggfffFvvvvfggfFWiiiiiiiiiiiiiiWfffggmmmmmmmmmmgffWiiiiiiiiiiiiiiiWf",
        "ffffFgfffFgffffggfFffggff~~~~fffFgWiiiiiiiiiiiiiiWFffffmmmmmmmmmmfggWiiiiiiiiiCiiiiiWf",
        "ggfFffggfffgFffffggffFfgg~~~~gffffWiiiiiiiiiiiiiiWfggffmmmmmmmmmmffFWiiiiiiiiiiiiiiiWg",
        "ffggffFfggfffggFfffgFffff~~~~FggffWiiiiiiiiiiiiiiWffFggmmmmmmmmmmgFfWiiiiiiiiiiiiiiiWf",
        "FfffggfffFggffFggffffggFf~~~~fffFgWiiiiiiiiiiiiiiWgffffmmmmmmmmmmfggWiiiiiiiiiiiiiiiWf",
        "ggfFffggFfffggfffFgffffgg~~~~ggFffWiiiiiiiiiiiiiiWfggfFmmmmmmmmmmfffWiiiiiiiiiiiiiiiWg",
        "ffFgffffggfFffggfffgFffff~~~~ffggfWWWWWWWWWWWWWWWWfffggmmmmmmmmmmgFfWiiiiiiiiiiiiiiiWf",
        "gfffgFffffggffFfggfFfggff~~~~ffffggffFggffFfggffffgFfffmmmmmmmmmmFfgWiiiiiiiiiiiiiiiWg",
        "fggfffggFfffgFffffggffFgg~~~~ggFfffgFfffggfffFggffffggFmmmmmmmmmmfffWiiiiiiiiiiiiiiiWf",
        "ffFggffFggffffggFfffggfff~~~~fFggffffggFffggffffFgfffFgmmmmmmmmmmggfWiiiiiiiiiiiiiiiWF",
        "gFfffggfffFgffffggfFffggF~~~~ffffFgffffggfFfggfFffggfffmmmmmmmmmmFfgWiiiiiiiiiiiiiiiWg",
        "fggfFffggfffgFffffFgffffg~~~~ggffffgFffffFgfffggffFfggfmmmmmmmmmmfffWiiiiiiiiiiiiiiiWf",
        "fffggffFfggfFfggffffgFfff~~~~fFggffFfggffffgFfffggfffFgmmmmmmmmmmggFWiiiiiiiiiiiiiiiWf",
        "gFfffgFffffggffFggffffggF~~~~FfffggfffFggffffggFffggFffmmmmmmmmmmffgWiiiiiiiiiiiiiiiWg",
        "FggffffggFfffggfffFgfffFg~~~~fggFffggffffFgfffFggfffggfmmmmmmmmmmgffWiiiiiiiiiiiiiiiWf",
        "fffFgffffggfFffggFffggfff~~~~fffggfFfggfFffggffffFgfffgmmmmmmmmmmfggWiiiiiiiiiiiiiiiWf",
        "ggfffgFffffFgffffggfFfggf~~~~FffffFgfffggffFfggffffgFffmmmmmmmmmmfFfWWWWWWWWWWWWWWWWWg",
        "FfggfFfggffffgFffffggffFg~~~~fggffffgFfffggfffFggffFfggmmmmmmmmmmgfffFggffFggffffggFff",
        "ffffggffFggffffggFfffgFff~~~~ffFggffffggFffggFfffggfffFmmmmmmmmmmfggFfffggfffFgffffggf",
        "ggFfffggfffFgfffFggffffgg~~~~gffffFgfffFggfffggfFffggffmmmmmmmmmmfffggfFffggfffgFffffF",
        "ffggfFffggFffggffffFgffff~~~~fggfFffggffffFgfffggffFfggmmmmmmmmmmFffffggffFfggfFfggfff",
        "ffffFgffffggfFfggffffgFff~~~~fffggffFfggffffgFfffgFffffmmmmmmmmmmfggFfffgFffffggffFggf",
        "ggffffgFffffggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFggffffggFfffggfffF",
        "fFggffffggFfffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffggFfffggfffFgffffggfFffggFf",
        "gfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfffgFffffFgffffgg",
        "fggFffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggfFfggffffgFffff",
        "fffggfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffggffFggffffggFf",
},file="map.bmp"},deploy={unselectables={{position={12,25},hero="XunYan58"},{position={10,28},hero="ShiGai60"},{position={12,31},hero="ZhaoWu59"},{position={8,24},hero="HanQi62"},{position={8,32},hero="WeiJiang62"},{position={15,28},hero="ZhouChuo62"},{position={10,35},hero="LuanYing62"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=15000}}
