gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"FanYang61"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="shuhu_hall",name="叔虎府正堂",position={25,11},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}}}
gstory={chapter="第六十二回·下／第六十三回开端",title="诸侯同心围齐国 晋臣合力逐栾盈",battle_title="叔虎府之围",objective="焚开南门，击退并俘获叔虎、箕遗、黄渊。",map_asset="m103.png",
 intro={
  {speaker="",text="晋平公即位后，栾盈因家势强盛遭范匄忌惮。范宣子听信栾祁之言，诬称栾盈谋乱。"},
  {speaker="",text="栾盈出奔楚国，其党叔虎、箕遗、黄渊仍在晋都。范匄命范鞅先围叔虎宅第。"},
  {speaker="范鞅",text="叔虎闭门拒捕，府墙不可翻越。封住南门，先晓谕投降；若仍拒命，再焚门进兵。"},
  {speaker="叔虎",text="范氏罗织罪名，今日不过仗势灭族。谁敢入门，我便以石木相拒！"},
  {speaker="",text="告密者张铿来到墙下劝降，叔虎以大石击杀张铿。范鞅遂下令纵火烧门。"},
  {speaker="箕遗",text="南门火起，守宅已无意义。与叔虎并骑冲出，尚可杀开一条路。"},
  {speaker="黄渊",text="我从东路接应。只要三人中有一人出城，便可把栾氏受诬之事传到诸侯。"},
  {speaker="军令",text="范鞅接近南门后触发焚门。第三回合荀吴由东路赶到；击退三人均视为被俘。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="叔虎",text="张铿卖主求荣，休想以空言骗我开门！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="范鞅",text="张铿已死，纵火焚门，弓手列阵擒人！"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="荀吴",text="东路已封，黄渊不得接近叔虎府。"}
 },
 victory={
  {speaker="",text="南门被火烧开，叔虎、箕遗冲出府门，范氏弓手齐发，将二人射伤擒住。"},
  {speaker="荀吴",text="黄渊企图从东路接应，已被我军截住。三名栾氏党羽全部在押。"},
  {speaker="范鞅",text="押回朝堂听审，不得在街市私杀。栾氏其余家众逐一登记，不许趁乱劫掠。"},
  {speaker="",text="叔虎、箕遗、黄渊后来皆被处死；羊舌赤、羊舌肸也受牵连，幸得祁奚力救。"},
  {speaker="",text="栾盈远奔楚国，晋国内部的范栾之争并未结束，更大的祸乱已经埋下。"},
  {speaker="军令",text="叔虎府围捕完成，获得800金币。第六十二回剧情完成。"}
 },
 defeat={{speaker="",text="范鞅被击退，或荀吴登场后被击退，或超过二十二回合，战役失败。"}}
}
local gate_burned=false local xunwu_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("FanYang61",1)end
function on_begin(game)game:generate_unit("ShuHu62",1,Enum.force.enemy,{24,18});game:generate_unit("JiYi62",1,Enum.force.enemy,{28,18});game:generate_unit("HuangYuan62",1,Enum.force.enemy,{42,18});game:set_unit_invulnerable("ShuHu62",true);game:set_unit_invulnerable("JiYi62",true);many(game,"JinArrestGuard62",{{20,32},{23,33},{27,33},{30,32}},Enum.force.own)end
function on_update(game)
if not gate_burned and game:is_unit_within("FanYang61",{25,28},3)then gate_burned=true;game:set_unit_invulnerable("ShuHu62",false);game:set_unit_invulnerable("JiYi62",false);game:push_cmd_speak(0,"叔虎击杀劝降者，范鞅下令焚开南门！叔虎、箕遗突围。")end
if not xunwu_spawned and game:get_turn_current()>=3 then xunwu_spawned=true;game:generate_unit("XunWu62",1,Enum.force.own,{47,18});many(game,"JinArrestGuard62",{{46,16},{46,20}},Enum.force.own);game:push_cmd_speak(0,"荀吴从东路赶到，截断黄渊接应路线。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if not game:has_unit("FanYang61")then return Enum.status.defeat end if xunwu_spawned and not game:has_unit("XunWu62")then return Enum.status.defeat end if not game:has_unit("ShuHu62") and not game:has_unit("JiYi62") and not game:has_unit("HuangYuan62")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="ShuHuManor62",turn_limit=22,map={blocked_edges={},size={50,36},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffgg",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFf",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggff",
        "fffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffgg",
        "gffffggFffggfWWWWWWWWWWWWWWWWWWWWWWWWWWFgfffFgffff",
        "fFgffffggfFfgWiiiiiiiiiiiiiiiiiiiiiiiiWffggfffgFff",
        "fffgFffffFgffWiiiiiiiiiiiiiiiiiiiiiiiiWffFfggfffgg",
        "gffFfggffffgFWiiiiiiiiiiiiiiiiiiiiiiiiWggfffFggffF",
        "fggfffFggffffWiiiiiiiiiiiiiiiiiiiiiiiiWffggFfffggf",
        "FffggffffFgffWiiiiiiiiiiiiiiiiiiiiiiiiWffffggfFffg",
        "ggfFfggfFffggWiiiiiiiiiiiCiiiiiiiiiiiiWgFffffggffF",
        "ffFgfffggffFfWiiiiiiiiiiiiiiiiiiiiiiiiWffggFfffgFf",
        "ffffgFfffggffWiiiiiiiiiiiiiiiiiiiiiiiiWgffFggffffg",
        "ggffffggFffggWiiiiiiiiiiiiiiiiiiiiiiiiWfggfffFgfff",
        "ffFgfffFggfffWiiiiiiiiiiiiiiiiiiiiiiiiWFffggfffgFf",
        "fFffggffffFgfWiiiiiiiiiiiiiiiiiiiiiiiiWgffFfggfFfg",
        "ggffFfggffffgWiiiiiiiiiiiiiiiiiiiiiiiiWfgFffffggff",
        "ffggfffFggffFWiiiiiiiiiiiiiiiiiiiiiiiiWfffggFfffgg",
        "gFffggFfffggfWiiiiiiiiiiiiiiiiiiiiiiiiWgffffggfFff",
        "FggfffggfFffgWiiiiiiiiiiiiiiiiiiiiiiiiWfgFffffFgff",
        "fffFgfffggffFWiiiiiiiiiiiiiiiiiiiiiiiiWfFfggffffgF",
        "gffffgFfffgFfWiiiiiiiiiiiiiiiiiiiiiiiiWggffFggffff",
        "FggffFfggfffgWiiiiiiiiiiiiiiiiiiiiiiiiWffggfffFgff",
        "fffggfffFggffWiiiiiiiiiiiiiiiiiiiiiiiiWfFffggFffgg",
        "gfFffggffffFgWiiiiiiiiiiiiiiiiiiiiiiiiWFgffffggfFf",
        "fggffFfggfFffWiiiiiiiiiiiiiiiiiiiiiiiiWffgFffffggf",
        "fffgFffffggffWiiiiiiiiiiiiiiiiiiiiiiiiWffffggFfffg",
        "ggfffggFfffggWWWWWWWWWWWWGGWWWWWWWWWWWWFgfffFggfff",
        "fFggfffggfFffggFfffggfffFgffffggfFffggFffggffffFgf",
        "ffffFgfffFgffffggfFffggfffgFffffFgffffggfFfggffffg",
        "ggfFffggfffgFffffggffFfggfFfggffffgFffffggffFggffF",
        "ffggffFfggfffggFfffgFffffggffFggffffggFfffgFfffggf",
        "FfffggfffFggffFggffffggFfffggfffFgfffFggffffggFffg",
        "ggfFffggFfffggfffFgffffggfFffggFffggffffFgffffggfF",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFg",
},file="map.bmp"},deploy={unselectables={{position={24,32},hero="FanYang61"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=8000}}
