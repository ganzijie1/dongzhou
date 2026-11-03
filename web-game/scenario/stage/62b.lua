gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"QiZhuangGong62","ZhiChuo62","GuoZui62"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="gaotang_palace",name="高唐府署",position={29,11},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="gaotang_store",name="高唐武库",position={39,18},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十二回·中",title="诸侯同心围齐国 晋臣合力逐栾盈",battle_title="高唐平叛",objective="利用东北城角绳索潜入高唐，击退肃沙卫。",map_asset="m102.png",
 intro={
  {speaker="",text="齐庄公即位后，肃沙卫据高唐反叛。齐军围攻一个多月，城墙坚固，始终不能攻入。"},
  {speaker="齐庄公",text="高唐久攻不下，强攻只会损兵。谁能在城中寻得内应，打开一处缺口？"},
  {speaker="",text="高唐工匠公娄暗中登上东北城角，以灯火为号，垂下绳索接引齐军。"},
  {speaker="殖绰",text="我与郭最从东北角缒城。主力仍在南门列阵，莫让肃沙卫察觉真正突破处。"},
  {speaker="郭最",text="入城后先夺东北城角，再直取肃沙卫。得手便开南门，接应庄公大军。"},
  {speaker="公娄",text="绳索已系牢。城角守军换班只有片刻，两位将军速下，不可点火。"},
  {speaker="肃沙卫",text="高唐粮足城坚，齐军围上数月也无用。东北角只留少数巡兵即可。"},
  {speaker="军令",text="殖绰或郭最抵达东北绳索格后解除肃沙卫保护；击退肃沙卫即完成夜袭。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="公娄",text="东北城角灯号已明，绳索垂下！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="郭最",text="城角已破，转身开南门！"}
 },
 victory={
  {speaker="",text="殖绰、郭最循绳登上高唐东北城角，击散守卒，公娄立即引二人直趋城中。"},
  {speaker="肃沙卫",text="东北角为何有喊杀声？快调南门守军回城，堵住通往府署的街道！"},
  {speaker="",text="肃沙卫被擒，南门随即打开。齐庄公率军入城，高唐一个多月的叛乱就此平定。"},
  {speaker="齐庄公",text="公娄冒险为内应，殖绰、郭最先登破城，皆当记功。肃沙卫按叛臣治罪。"},
  {speaker="",text="肃沙卫被处死。齐庄公由此稳住君位，齐国暂与晋国在澶渊讲和。"},
  {speaker="军令",text="高唐平叛完成，获得900金币。下一关：叔虎府之围。"}
 },
 defeat={{speaker="",text="齐庄公、殖绰、郭最任一被击退，或超过二十八回合，战役失败。"}}
}
local rope_open=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("GongLou62",1,Enum.force.ally,{46,8});game:generate_unit("SuShaWei62",1,Enum.force.enemy,{29,11});game:set_unit_invulnerable("SuShaWei62",true);many(game,"GaotangGuard62",{{45,7},{45,10},{42,14},{35,16},{30,22},{24,16},{20,25},{29,32},{31,32}},Enum.force.enemy);many(game,"GaotangArcher62",{{43,9},{40,12},{34,20},{22,20},{27,30},{33,30}},Enum.force.enemy)end
function on_update(game)if not rope_open and (game:is_unit_within("ZhiChuo62",{48,7},2) or game:is_unit_within("GuoZui62",{48,7},2))then rope_open=true;game:set_unit_invulnerable("SuShaWei62",false);game:push_cmd_speak(0,"公娄垂下绳索，东北城角已被夺取！肃沙卫可以被击退。")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if rope_open and not game:has_unit("SuShaWei62")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="GaotangNightBreach62",turn_limit=28,map={blocked_edges={},size={58,42},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffg",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFfff",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggF",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFg",
        "fffgFfffggffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWgFfffggff",
        "gffffggFffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggfFffgg",
        "fFgffffggfFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggffFf",
        "fffgFffffFgfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiGgFfffgFff",
        "gffFfggffffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiGFggffffgg",
        "fggfffFggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffFgffff",
        "FffggffffFgfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggfffgFff",
        "ggfFfggfFffgWiiiiiiiiiiiiiiiiCiiiiiiiiiiiiiiiiiiWFfggfFfgg",
        "ffFgfffggffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggffF",
        "ffffgFfffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggFfffggf",
        "ggffffggFffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggfFffg",
        "ffFgfffFggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffFgfff",
        "fFffggffffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffgFf",
        "ggffFfggffffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFggffffg",
        "ffggfffFggffWiiiiiiiiiiiiiiiiiiiiiiiiiiCiiiiiiiiWgfffFgfff",
        "gFffggFfffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFffggf",
        "FggfffggfFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggfFfg",
        "fffFgfffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFffffggff",
        "gffffgFfffgFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFfffgF",
        "FggffFfggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggffff",
        "fffggfffFggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffffFgff",
        "gfFffggffffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggffffgF",
        "fggffFfggfFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggffFf",
        "fffgFffffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFfffggff",
        "ggfffggFfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFffgg",
        "fFggfffggfFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggfFf",
        "ffffFgfffFgfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFffffFgf",
        "ggfFffggfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggffffg",
        "ffggffFfggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffFggfff",
        "FfffggfffFggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffFgf",
        "ggfFffggFfffWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWFfggfFffg",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffF",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggf",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffg",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggff",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggff",
},file="map.bmp"},deploy={unselectables={{position={23,38},hero="QiZhuangGong62"},{position={51,7},hero="ZhiChuo62"},{position={52,9},hero="GuoZui62"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=9000}}
