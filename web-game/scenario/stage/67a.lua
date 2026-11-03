gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"LuPuGui67","GaoChai67","LuanZao67"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="qi_temple",name="齐国太庙",position={34,11},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="qi_palace",name="临淄宫署",position={48,14},restore_hp=20,restore_mp=15,rewards={}}}
gstory={chapter="第六十七回·上",title="卢蒲癸计逐庆封 楚灵王大合诸侯",battle_title="太庙诛庆",objective="先诛庆舍，再击退从西门反攻的庆封父子。",map_asset="m115.png",
 intro={
  {speaker="",text="周灵王太子晋早逝，传说缑岭跨鹤升仙。灵王随后崩逝，次子贵即位，是为周景王；楚康王也在同年去世。"},
  {speaker="",text="齐相庆封独掌国政后日益荒淫，把政事交给儿子庆舍，自己长期住在卢蒲嫳家中。"},
  {speaker="卢蒲嫳",text="庆氏以为我只图酒色，却不知庄公之仇未雪。召我兄卢蒲癸回齐，才有内应。"},
  {speaker="卢蒲癸",text="我已让庆舍召回王何，又取得他的信任。高、栾、陈、鲍四族从外包围，卢蒲氏从内下手。"},
  {speaker="",text="齐景公御膳以鸭代鸡，高虿、栾灶以为庆氏刻减公膳，由此与庆舍公开结怨。"},
  {speaker="高虿",text="庆封与崔杼同弑庄公。崔氏已灭，庆氏尚在，今日正可为先君报仇。"},
  {speaker="",text="庆封率庆嗣、庆遗赴东莱田猎。陈无宇渡河后拆桥凿舟，断绝庆封归路。"},
  {speaker="庆姜",text="我故意警告庆舍不可参加尝祭，他刚愎自用，反而必定亲自入太庙。"},
  {speaker="庆舍",text="高虿、栾灶不过禽兽，即便真有伏兵，我一人也足以寝处之。"},
  {speaker="军令",text="第一阶段在太庙击退庆舍；第二阶段守住临淄西门，击退回援的庆封、庆嗣、庆遗。卢蒲癸、高虿、栾灶不得被击退。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="卢蒲癸",text="庙门已闭，四姓甲士一同动手！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="庆封",text="庆舍已死，随我攻破西门夺回临淄！"}
 },
 victory={
  {speaker="",text="卢蒲癸从背后刺入庆舍胁下，王何以戈击断其左肩。庆舍投出俎壶，王何当场战死。"},
  {speaker="",text="庆舍抱住庙柱奋力摇撼，最终伤重而死。卢蒲癸随即杀庆绳，四姓甲士尽灭庆氏在城中的党羽。"},
  {speaker="",text="庆封闻讯反攻临淄西门，城中防守严密，部卒不断逃散。庆封与庆嗣、庆遗败走，转奔鲁国。"},
  {speaker="晏婴",text="诸臣为安社稷而诛庆氏，并非犯上。君上回宫，勿使城中再生混乱。"},
  {speaker="",text="鲁国迫于齐国压力不敢收留庆封，庆封又奔吴国。吴王夷昧将朱方封给他，庆氏表面更富，祸患却尚未结束。"},
  {speaker="",text="齐国发掘崔杼之柩陈尸于市，卢蒲嫳、卢蒲癸被放逐北燕。陈无宇不取庆氏财物，反而将木材施给百姓。"},
  {speaker="军令",text="太庙诛庆完成，获得1200金币。下一关：郑门讨伯有。"}
 },
 defeat={{speaker="",text="卢蒲癸、高虿、栾灶任一被击退，或超过二十八回合，失败。"}}
}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
local phase=1
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("LuPuBie66",1,Enum.force.ally,{25,15});game:generate_unit("QingShe67",1,Enum.force.enemy,{34,11})
 many(game,"QiCoalitionGuard67",{{27,15},{31,18},{38,18},{42,15}},Enum.force.own);many(game,"QiCoalitionArcher67",{{26,12},{42,12}},Enum.force.own)
 many(game,"QingTempleGuard67",{{31,9},{37,9},{30,12},{38,12},{33,16},{36,16}},Enum.force.enemy)
end
function on_update(game)
 if phase==1 and not game:has_unit("QingShe67")then phase=2;game:generate_unit("QingFeng62",1,Enum.force.enemy,{3,20});game:generate_unit("QingSi67",1,Enum.force.enemy,{3,16});game:generate_unit("QingYi67",1,Enum.force.enemy,{3,25});many(game,"QingCounterGuard67",{{1,18},{1,23},{4,18},{4,23},{6,16},{6,25}},Enum.force.enemy);many(game,"QingCounterArcher67",{{2,14},{2,27},{5,19},{5,22}},Enum.force.enemy);game:push_cmd_speak(0,"庆舍已死，王何也被俎壶击中身亡！庆封父子正在反攻临淄西门！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("QingFeng62") and not game:has_unit("QingSi67") and not game:has_unit("QingYi67")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="QiTempleCoup67",turn_limit=28,map={blocked_edges={},size={68,44},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggf",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffg",
        "fggffFgWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfggFff",
        "fffgFffWiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihWfffggf",
        "gffffggWiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiWFffffF",
        "fFgffffWiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiWfggfff",
        "fffgFffWihiiiiiiihiiiiiiihihhhhhhhhhhhhhhhiiiiiiihiiiiiiihiiiWffFggf",
        "gffFfggWhiiiiiiihiiiiiiihiihhhhhhhhhhhhhhhiiiiiihiiiiiiihiiiiWggfffF",
        "fggfffFWiiiiiiihiiiiiiihiiihhhhhhhhhhhhhhhihhhhhhhhhhhhhiiiiiWffggFf",
        "FffggffWiiiiiihiihiiiihiiiihhhhhhhhhhhhhhhihhhhhhhhhhhhiiiiiiWffffgg",
        "ggfFfggWiiiiihiiiiiiihiiiiihhhhhhhChhhhhhhihhhhhhhhhhhhiiiiiiWgFffff",
        "ffFgfffWiiiihiiiiiiihiiiiiihhhhhhhhhhhhhhhihhhhhhhhhhhhiiiiihWffggFf",
        "ffffgFfWiiihiiiiiiihiiiiiiihhhhhhhhhhhhhhhihhhhhhhhhhhhiiiihiWfffFgg",
        "ggffffgWiihiiiiiiihiiiiiiihhhhhhhhhhhhhhhhhhhhhhChhhhhhiiihiiWggffff",
        "ffFgfffWihiiiiiiihiiiihiihihhhhhhhhhhhhhhhihhhhhhhhhhhhiihiiiWFfggff",
        "fFffggfWhiiiiiiihiiiiiiihiihhhhhhhhhhhhhhhihhhhhhhhhhhhihiiiiWgffFgg",
        "ggffFfgWiiiiiiihiiiiiiihiiihhhhhhhhhhhhhhhihhhhhhhhhhhhhiiiiiWfgFfff",
        "ffggfffWiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiihhhhhhhhhhhhiiiiiiWfffggF",
        "gFffggFWiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiihhhhhhhhhhhhiiiiiiWgffffg",
        "FggfffgGiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihWfgFfff",
        "fffFgffGiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiWfFfggf",
        "gffffgFWiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiWgfffFg",
        "FggffFfWihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiWfggfff",
        "fffggffWhiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiWfFfggf",
        "gfFffggWiiiiiihhhhhhhhhhhhiiiiihiiiiihhhhhhhhhhhhhhhhhihiiiiiWFgfffg",
        "fggffFfWiiiiiihhhhhhhhhhhhiiiihiiiiiihhhhhhhhhhhhhhhhhhiiiiiiWffgFff",
        "fffgFffWiiiiihhhhhhhhhhhhhiiihiiiiiiihhhhhhhhhhhhhhhhhiiiiiiiWffffgg",
        "ggfffggWiiiihihhhhhhhhhhhhiihiiiiiiihhhhhhhhhhhhhhhhhhiiiiiihWFgfffF",
        "fFggfffWiiihiihhhhhhhhhhhhihiiiiiiihihhhhhhhhhhhhhhhhhiiiiihiWffggff",
        "ffffFgfWiihiiihhhhhhhhhhhhhiiiiiiihiihhhhhhhhhhhhhhhhhiiiihiiWffFfgg",
        "ggfFffgWihiiiihhhhhhhhhhhhiiiiiiihiiihhhhhhhhhhhhhhhhhiiihiiiWggfffF",
        "ffggffFWhiiiiihhhhhhhhhhhhiiiiiihiiiihhhhhhhhhhhhhhhhhiihiiiiWffggFf",
        "FfffggfWiiiiiihhhhhhhhhhhhiiiiihiiiiihhhhhhhhhhhhhhhhhihiiiiiWgfffgg",
        "ggfFffgWiiiiiihhhhhhhhhhhhiiiihiiiiiihhhhhhhhhhhhhhhhhhiiiiiiWfFgfff",
        "ffFgfffWiiiiihiiiiiiihiiiiiiihiiiiiiihhhhhhhhhhhhhhhhhiiiiiiiWfffgFf",
        "gfffgFfWiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihWgffFfg",
        "fggfffgWiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiWfggfff",
        "ffFggffWiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiWFffggf",
        "gFfffggWihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiiiiihiiiWgffFfg",
        "fggfFffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfgFfff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggffFfggfffggF",
        "gFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffggFfffggfffFggfffg",
        "FggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgff",
},file="map.bmp"},deploy={unselectables={{position={32,14},hero="LuPuGui67"},{position={29,16},hero="GaoChai67"},{position={38,16},hero="LuanZao67"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=12000}}
