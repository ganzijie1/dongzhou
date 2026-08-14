gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"FanYang61","XunWu62"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="quwo_hall",name="曲沃栾氏宗堂",position={28,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="quwo_west_store",name="曲沃西库",position={18,21},restore_hp=20,restore_mp=10,rewards={}},{id="quwo_east_store",name="曲沃东库",position={38,21},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十三回·终／第六十四回上",title="老祁奚力救羊舌 小范鞅智劫魏舒",battle_title="曲沃灭栾",objective="攻破曲沃，击退胥午、栾荣并俘获栾盈。",map_asset="m105.png",
 intro={
  {speaker="",text="固宫之战失败后，栾盈、栾鲂带曲沃残兵退回城中。范鞅、荀吴率三百乘围城。"},
  {speaker="范鞅",text="栾氏爪牙已尽，但曲沃城墙连续坚固。封住东门、南门，先断城中补给。"},
  {speaker="荀吴",text="胥午经营曲沃多年，城中仍有弓手与甲士。两路同时施压，不让守军集中一门。"},
  {speaker="栾盈",text="我悔不用辛俞忠言，才到今日。但栾氏宗祀尚在，绝不能束手就擒。"},
  {speaker="胥午",text="我曾受栾氏厚恩。曲沃若破，惟有伏剑以谢故主，不会出城求生。"},
  {speaker="栾鲂",text="城破后我从南墙缒城突围，若能留下栾氏一脉，也不算全军俱没。"},
  {speaker="军令",text="击退胥午、栾荣后解除栾盈保护；击退栾盈即视为被俘。栾鲂不可被击退，按剧情突围。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="胥午",text="城亡之日，便是胥午报答栾氏之时。"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="栾鲂",text="兄长保重，我从南墙突围，为栾氏留下一线。"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="范鞅",text="栾盈已经就擒，曲沃各军放下兵器！"}
 },
 victory={
  {speaker="",text="曲沃被围一个多月，守军死伤过半。晋军从东、南两门同时攻入，城内再无完整防线。"},
  {speaker="",text="胥午见大势已去，伏剑自尽。栾盈、栾荣被范鞅所部擒获，栾鲂乘夜缒城奔宋。"},
  {speaker="栾盈",text="我悔不用辛俞之言，以私怨犯君，终使栾氏数世功业毁于一旦。"},
  {speaker="",text="范鞅担心晋平公临时宽赦，夜使人缢杀栾盈，并处死栾荣，栾氏自此灭族。"},
  {speaker="",text="晋平公焚毁丹书，释放因旧案没官为奴者；斐豹因击杀督戎被任为中军牙将。"},
  {speaker="",text="范匄随后告老，赵武接掌晋国政事。齐庄公出兵接应栾盈，闻其失败后转兵撤退。"},
  {speaker="军令",text="曲沃灭栾完成，获得1300金币。第六十三回战役结束。"}
 },
 defeat={{speaker="",text="范鞅或荀吴被击退，或超过三十二回合，战役失败。"}}
}
local leaders_down=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("LuanYing62",1,Enum.force.enemy,{28,10});game:set_unit_invulnerable("LuanYing62",true);game:generate_unit("XuWu63",1,Enum.force.enemy,{18,21});game:generate_unit("LuanRong63",1,Enum.force.enemy,{38,21});game:generate_unit("LuanFang63",1,Enum.force.enemy,{28,29});game:set_unit_invulnerable("LuanFang63",true);many(game,"QuwoGuard63",{{46,16},{46,21},{29,32},{26,32},{22,27},{34,27},{20,17},{36,17},{26,13},{31,13}},Enum.force.enemy);many(game,"QuwoArcher63",{{44,14},{44,23},{23,30},{33,30},{16,16},{40,16},{24,11},{32,11}},Enum.force.enemy);many(game,"JinGugongGuard63",{{52,15},{52,18},{52,22},{52,25}},Enum.force.own);many(game,"JinGugongArcher63",{{55,17},{55,23}},Enum.force.own)end
function on_update(game)if not leaders_down and not game:has_unit("XuWu63") and not game:has_unit("LuanRong63")then leaders_down=true;game:set_unit_invulnerable("LuanYing62",false);game:push_cmd_speak(0,"胥午伏剑，栾荣被擒。栾鲂已经缒城逃往宋国，合兵进取栾盈！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if leaders_down and not game:has_unit("LuanYing62")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="QuwoLastSiege63",turn_limit=32,map={blocked_edges={},size={58,42},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffg",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFfff",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggF",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFg",
        "fffgFfffgWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWgFfffggff",
        "gffffggFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggfFffgg",
        "fFgffffggWhiihiihiihiihiihiihiihiihiihiihiihiihiWfffggffFf",
        "fffgFffffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFfffgFff",
        "gffFfggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFggffffgg",
        "fggfffFggWiihiihiihiihiihiihiihiihiihiihiihiihiiWfffFgffff",
        "FffggffffWiiiiiiiiiiiiiiiiiiCiiiiiiiiiiiiiiiiiiiWggfffgFff",
        "ggfFfggfFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggfFfgg",
        "ffFgfffggWihiihiihiihiihiihiihiihiihiihiihiihiihWffffggffF",
        "ffffgFfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggFfffggf",
        "ggffffggFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggfFffg",
        "ffFgfffFgWhiihiihiihiihiihiihiihiihiihiihiihiihiWffffFgfff",
        "fFffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffgFf",
        "ggffFfggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFggffffg",
        "ffggfffFgWiihiihiihiihiihiihiihiihiihiihiihiihiiGgfffFgfff",
        "gFffggFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiGfggFffggf",
        "FggfffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggfFfg",
        "fffFgfffgWihiihiihCihiihiihiihiihiihiiCiihiihiihWFffffggff",
        "gffffgFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFfffgF",
        "FggffFfggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggffff",
        "fffggfffFWhiihiihiihiihiihiihiihiihiihiihiihiihiWgffffFgff",
        "gfFffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggffffgF",
        "fggffFfggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggffFf",
        "fffgFffffWiihiihiihiihiihiihiihiihiihiihiihiihiiWgFfffggff",
        "ggfffggFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFffgg",
        "fFggfffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggfFf",
        "ffffFgfffWihiihiihiihiihiihiihiihiihiihiihiihiihWgFffffFgf",
        "ggfFffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggffffg",
        "ffggffFfgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffFggfff",
        "FfffggfffWhiihiihiihiihiihiihiihiihiihiihiihiihiWggffffFgf",
        "ggfFffggFWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWFfggfFffg",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffF",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggf",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffg",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggff",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggff",
},file="map.bmp"},deploy={unselectables={{position={53,17},hero="FanYang61"},{position={53,21},hero="XunWu62"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=13000}}
