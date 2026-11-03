gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"FanYang61","WeiShu63","ZhaoWu59","XunWu62","HanQi62"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="gugong_main",name="固宫",position={57,16},restore_hp=30,restore_mp=20,rewards={{item="medicine",amount=1}}},{id="gugong_store",name="固宫武库",position={63,25},restore_hp=25,restore_mp=15,rewards={}},{id="wei_house",name="魏氏府库",position={18,12},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十三回·下／第六十四回开端",title="老祁奚力救羊舌 小范鞅智劫魏舒",battle_title="固宫保卫战",objective="护送魏舒进入固宫，依次击退督戎与栾乐。",map_asset="m104.png",
 intro={
  {speaker="",text="叔虎、箕遗、黄渊被擒后，范匄又拘捕羊舌赤、羊舌肸等人，晋都一夜震动。"},
  {speaker="",text="告老的祁奚连夜入都，以贤臣关系社稷为由劝范匄；晋平公终于赦免羊舌赤、羊舌肸。"},
  {speaker="",text="栾盈由曲沃出奔楚国。家臣辛俞坚持三世事栾，获晋平公放行，携辎重追随旧主。"},
  {speaker="",text="栾盈转奔齐国，齐庄公不顾晏婴反对收留他，又将州绰、邢蒯列入勇爵。"},
  {speaker="",text="齐庄公借送媵女为名，将栾盈藏入温车送到曲沃。胥午召集曲沃之甲二百二十乘，夜袭绛都。"},
  {speaker="辛俞",text="我从主是为尽私忠，却不能助主叛晋。此行必败，愿以一死相送。"},
  {speaker="",text="辛俞自刎而死。栾盈仍率督戎、殖绰、郭最、栾乐、栾鲂破南门而入，直抵绛城市口。"},
  {speaker="范鞅",text="主公已入固宫。魏舒车徒在北隅列阵，若让他接应栾盈，绛都内外皆失。"},
  {speaker="魏舒",text="栾氏旧有恩于我，曲沃兵已经入城。此刻究竟应迎栾氏，还是奉晋侯之命？"},
  {speaker="范鞅",text="奉君命，请魏伯同车入固宫！车徒立即转向东行，不得停留。"},
  {speaker="督戎",text="固宫南关归我独攻。待填平沟堑，谁敢出关与我双戟一战？"},
  {speaker="军令",text="先护送魏舒进入固宫；随后击退督戎，再击退发动北关火攻的栾乐。栾盈本关败退，不可被击退。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="范鞅",text="魏伯已奉君命进入固宫，诸卿同心守关！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="斐豹",text="督戎，今日只你我二人赌个死生！"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="栾乐",text="北关火起，轈车并进，今夜定要破宫！"}
 },
 victory={
  {speaker="",text="范鞅跃上魏舒之车，执剑牵其衣带，迫使车徒转向固宫。魏舒既入宫，只能与范氏共同守御。"},
  {speaker="",text="督戎连败解雍、解肃、牟刚、牟劲，晋军无人敢应。隶人斐豹请焚丹书换取出战。"},
  {speaker="斐豹",text="督君素喜独斗。引他越过短墙，我伏于树下，以五十二斤铜锤取其首级。"},
  {speaker="",text="督戎中计，被斐豹从背后一锤击杀。固宫南关守军随即出击，栾军大败。"},
  {speaker="",text="栾乐夜用轈车火攻北关，一度攻占外关；范鞅、荀吴内外夹击，栾乐翻车被斐豹杀死。"},
  {speaker="",text="殖绰奔卫，郭最奔秦；栾盈、栾鲂带残兵退回曲沃。魏舒念旧放行，赵武也没有追赶。"},
  {speaker="范匄",text="曲沃之甲尽随栾盈而归。范鞅、荀吴立即率军围城，不可再给齐军接应的机会。"},
  {speaker="军令",text="固宫保卫战完成，获得1200金币。下一关：曲沃灭栾。"}
 },
 defeat={{speaker="",text="范鞅、魏舒、赵武任一被击退，或超过三十回合，战役失败。"}}
}
local phase=1 local feibao_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("LuanYing62",1,Enum.force.enemy,{36,39});game:set_unit_invulnerable("LuanYing62",true);game:generate_unit("DuRong63",1,Enum.force.enemy,{38,43});game:set_unit_invulnerable("DuRong63",true);game:generate_unit("LuanLe63",1,Enum.force.enemy,{55,39});game:set_unit_invulnerable("LuanLe63",true);game:generate_unit("LuanFang63",1,Enum.force.enemy,{60,40});game:set_unit_invulnerable("LuanFang63",true);many(game,"LuanRebelGuard63",{{33,41},{36,43},{41,41},{31,36},{39,36},{49,38},{53,38},{59,38},{63,39}},Enum.force.enemy);many(game,"LuanRebelArcher63",{{30,39},{42,39},{51,41},{58,42},{64,41}},Enum.force.enemy);many(game,"JinGugongGuard63",{{53,33},{56,33},{59,33},{62,33},{53,10},{60,10}},Enum.force.own);many(game,"JinGugongArcher63",{{50,31},{65,31},{51,12},{64,12}},Enum.force.own)end
function on_update(game)
if phase==1 and game:is_unit_within("WeiShu63",{57,16},8)then phase=2;feibao_spawned=true;game:generate_unit("FeiBao63",1,Enum.force.own,{54,32});game:set_unit_invulnerable("DuRong63",false);game:push_cmd_speak(0,"魏舒已进入固宫。斐豹请战，督戎不再受保护！")end
if phase==2 and feibao_spawned and not game:has_unit("FeiBao63")then return end
if phase==2 and not game:has_unit("DuRong63")then phase=3;game:set_unit_invulnerable("LuanLe63",false);game:push_cmd_speak(0,"督戎已被斐豹击杀！栾乐转攻北关，火箭轈车一齐逼近。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if feibao_spawned and not game:has_unit("FeiBao63")then return Enum.status.defeat end if phase==3 and not game:has_unit("LuanLe63")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="GugongDefense63",turn_limit=30,map={blocked_edges={},size={74,52},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfffgFffff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggfFfggff",
        "gfWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWgg",
        "fgWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWff",
        "ffWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWgF",
        "gfWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWfg",
        "fFWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWff",
        "ffWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihWgF",
        "gfWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWWWWWWWWWWWGGWWWWWWWWWWWhiWFg",
        "fgWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "FfWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWgf",
        "ggWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWFg",
        "ffWiiiiiihiiiiiihiCiiiihiiiiiihiiiiiihiiiiiihWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "ffWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWiiiiiiiiiiiiiiiiiiiiiiWiiWgg",
        "ggWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWiiiiiiiiiiiiiiiiiiiiiiWihWff",
        "ffWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWiiiiiiiiiiiiiiiiiiiiiiWhiWff",
        "fFWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWiiiiiiiiiiiCiiiiiiiiiiWiiWgg",
        "ggWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWfF",
        "ffWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "gFWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihWiiiiiiiiiiiiiiiiiiiiiiWiiWgg",
        "FgWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "ffWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWiiiiiiiiiiiiiiiiiiiiiiWihWFf",
        "gfWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWiiiiiiiiiiiiiiiiiiiiiiWhiWfg",
        "FgWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "ffWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWgf",
        "gfWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWiiiiiiiiiiiiiiiiiCiiiiWiiWfg",
        "fgWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "ffWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWiiiiiiiiiiiiiiiiiiiiiiWiiWgF",
        "ggWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWiiiiiiiiiiiiiiiiiiiiiiWihWfg",
        "fFWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWiiiiiiiiiiiiiiiiiiiiiiWhiWff",
        "ffWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWgF",
        "ggWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWFf",
        "ffWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWiiiiiiiiiiiiiiiiiiiiiiWiiWff",
        "FfWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihWiiiiiiiiiiiiiiiiiiiiiiWiiWgg",
        "ggWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWiiiiiiiiiiiiiiiiiiiiiiWiiWFf",
        "ffWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWWWWWWWWWWWGGWWWWWWWWWWWihWff",
        "gfWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWgg",
        "fgWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWff",
        "ffWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWgf",
        "gFWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWfg",
        "fgWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWfF",
        "ffWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWgf",
        "gFWiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihWfg",
        "FgWiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiWff",
        "ffWiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiWFf",
        "ggWihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiWfg",
        "FfWhiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiWff",
        "ffWiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiWgg",
        "ggWiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiihiiiiiiWff",
        "ffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWff",
        "ffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgF",
        "ggffffgFffffggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFggffff",
},file="map.bmp"},deploy={unselectables={{position={17,12},hero="FanYang61"},{position={19,12},hero="WeiShu63"},{position={54,31},hero="ZhaoWu59"},{position={60,31},hero="XunWu62"},{position={57,12},hero="HanQi62"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=12000}}
