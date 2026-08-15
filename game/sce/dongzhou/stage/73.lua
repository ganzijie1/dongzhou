gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"JiGuang73","GongZiGai73"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="wu_north_camp",name="吴军北营",position={12,11},restore_hp=20,restore_mp=10,rewards={}},{id="wu_south_camp",name="吴军南营",position={14,33},restore_hp=20,restore_mp=10,rewards={}},{id="hu_camp",name="胡军大营",position={58,11},restore_hp=20,restore_mp=10,rewards={}},{id="shen_camp",name="沈军大营",position={57,33},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第七十三回",title="伍员吹箫乞吴市 专诸进炙刺王僚",battle_title="鸡父之战",objective="击破夏啮前锋，再合围胡、沈两君与魏越。",map_asset="m122.png",
 intro={
  {speaker="",text="楚国率陈、蔡、胡、沈、顿、许等国攻吴。吴王僚命公子光迎战鸡父，伍员献疲兵分击之策。"},
  {speaker="公子光",text="楚属七国号令不一。先用三千罪卒冲阵扰乱其前军，再分兵击胡、沈，最后合攻楚军。"},
  {speaker="公子盖余",text="我从北路包抄胡、沈两君。主军击夏啮时，我部不必恋战，只要断其归路。"},
  {speaker="夏啮",text="吴军以罪人当先，不过乌合之众。陈军先击破他们，诸国随后推进！"},
  {speaker="魏越",text="诸军营垒分散，若陈军先败，后军恐怕各自奔逃。"},
  {speaker="军令",text="先击退夏啮及陈军前锋，随后合围胡、沈两君并击破魏越。两名吴军主将被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="公子光",text="罪卒扰乱前军后，全军分击诸侯营垒。"}
 },
 victory={
  {speaker="",text="三千罪卒反复冲击，陈军阵形散乱。公子光乘势斩夏啮，吴军两翼又擒胡、沈两君。"},
  {speaker="",text="许、蔡、顿军见两君被俘，各自逃散。魏越收兵不及，自知回楚必获罪，最终自尽。"},
  {speaker="伍员",text="鸡父一胜，楚东境门户已开。但大王若仍在，公子光终究不能专行伐楚大计。"},
  {speaker="",text="伍员向公子光推荐勇士专诸。专诸把匕首藏入炙鱼腹中，在宴席刺杀吴王僚，自己也被卫士杀死。"},
  {speaker="公子光",text="专诸以身成事，其子当世袭卿位。自今日起我即吴王阖闾，任伍员、孙武整军，准备西破强楚。"},
  {speaker="",text="王僚之子庆忌逃到艾城聚众。要离断臂杀妻以取信庆忌，最终在舟中刺死庆忌，自己亦伏剑而死。"},
  {speaker="军令",text="鸡父之战完成，获得1800金币。下一关：柏举之战。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("XiaNie73",1,Enum.force.enemy,{48,13});game:generate_unit("WeiYue73",1,Enum.force.enemy,{57,31});game:generate_unit("HuGong73",1,Enum.force.enemy,{58,11});game:generate_unit("ShenGong73",1,Enum.force.enemy,{57,33});many(game,"WuGuard73",{{5,18},{6,24},{10,18},{11,27},{14,21},{15,25}},Enum.force.own);many(game,"WuArcher73",{{4,21},{9,29},{16,18}},Enum.force.own);many(game,"CoalitionGuard73",{{43,11},{46,16},{50,10},{52,15},{53,28},{55,35},{61,27},{62,34},{60,8},{63,13}},Enum.force.enemy);many(game,"CoalitionArcher73",{{45,9},{50,18},{54,30},{61,32},{63,10}},Enum.force.enemy)
end
function on_update(game)
if phase==1 and not game:has_unit("XiaNie73")then phase=2;game:push_cmd_speak(0,"夏啮已死，陈军前锋崩溃！公子盖余从北路合围胡、沈两军！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if not game:has_unit("XiaNie73")and not game:has_unit("WeiYue73")and not game:has_unit("HuGong73")and not game:has_unit("ShenGong73")then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou73",turn_limit=30,map={blocked_edges={},size={72,44},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfffgFff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggfFfgg",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffggffF",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFggffffggFfffggf",
        "fffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffggFfffggfffFgffffggfFffg",
        "gffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfffgFffffFgfff",
        "fFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggfFfggffffgFf",
        "fffgFffffFgfffggffFfggffffgFfvvvvvvvfggffFfggfffggFfffgFffffggffFggffffg",
        "gffFfggffffgFfffggfffFggffFfgvvvvvvvfffggfffFggffFggffffggFfffggfffFgfff",
        "wwgfffwwgfffwwgFffwwFfffwwfffvwwvvvvwwFffgwwfffgwwffFgwwffggwwffggwwfggf",
        "FffggffffFgfffFggfffggfFffggfvvvvvvvfFgffffggfFffggfffgFffffFgffffggfFfg",
        "ggfFfggfFffgCffffFgfffggffFfgvvvvvvvfffgFffffggffFfggfFfggCfffgFffffggff",
        "ffFgfffggffFfggffffgFfffgFffffvvvvvvvgfffggFfffgFffffggffFggffffggFfffgF",
        "ffffgFfffggfffFggffFfggfffggFfvvvvvvvFggffFggffffggFfffggfffFgfffFggffff",
        "ggffffggFffggFfffggfffFggfffggvvvvvvvfffggfffFgffffggfFffggFffggffffFgff",
        "ffFgfffFggfffggfFffggffffFgfffvvvvvvvgfFffggfffgFffffFgffffggfFfggffffgF",
        "fFffggffffFgfffggffFfggfFffggfvvvvvvvfggffFfggfFfggffffgFffffggffFggffFf",
        "ggffFfggffffgFfffgFffffggffFfggvvvvvvvffgFffffggffFggffffggFfffgFfffggff",
        "ffggfffFggffFfggfffggFfffggfffFvvvvvvvffffggFfffggfffFgfffFggffffggFffgg",
        "gFffggFfffggfffFggfffggfFffggFfvvvvvvvFgffffggfFffggFffggffffFgffffggfFf",
        "FggfffggfFffggffffFgfffFgffffggvvvvvvvffgFffffFgffffggfFfggffffgFffffFgf",
        "fffFgfffggffFfggfFffggfffgFffffvvvvvvvgfFfggffffgFffffggffFggffFfggffffg",
        "gffffgFfffgFffffggffFfggfffggFffvvvvvvvggffFggffffggFfffgFfffggfffFggfff",
        "FggffFfggfffggFfffggfffFggffFggfvvvvvvvffggfffFgfffFggffffggFffggffffFgf",
        "fffggfffFggfffggfFffggFfffggfffFvvvvvvvfFffggFffggffffFgffffggfFfggfFffg",
        "gfFffggffffFgfffFgffffggfFffggffvvvvvvvFgffffggfFfggffffgFffffFgfffggffF",
        "fggffFfggfFffggfffgFffffggffFfggvvvvvvvffgFffffggffFggffFfggffffgFfffggf",
        "fffgFffffggffFfggfffggFfffgFffffgvvvvvvvfffggFfffgFfffggfffFggffffggFffg",
        "ggfffggFfffggfffFggffFggffffggFffvvvvvvvgfffFggffffggFffggffffFgfffFggff",
        "fFggfffggfFffggFfffggfffFgffffggfvvvvvvvfggffffFgffffggfFfggfFffggffffFg",
        "ffffFgfffFgffffggfFffggfffgFffffFvvvvvvvfFfggffffgFffffFgfffggffFfggffff",
        "ggfFffggfffgFffffggffFfggfFfggfffvvvvvvvggffFggffFfggffffgFfffggfffFggff",
        "ffggffFfggfffggFfffgFffffggffFggffvvvvvvvfgFfffggfffFggffffggFffggFfffgg",
        "FfffggfffFggffCggffffggFfffggfffFgvvvvvvvfffggFffggffffFgCffFggfffggfFff",
        "wwfFffwwFfffwwfffFwwfffgwwFffgwwffvvwwvvvgwwffggwwfggfwwfggfwwfFgfwwggff",
        "ffFgffffggfFffggfffgFffffFgffffggfvvvvvvvfgFffffFgfffggffFfggffffgFfffgF",
        "gfffgFffffggffFfggfFfggffffgFffffgvvvvvvvfFfggffffgFfffggfffFggffFfggfff",
        "fggfffggFfffgFffffggffFggffffggFfffvvvvvvvfffFggffffggFffggFfffggfffFggf",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffffF",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFf",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggf",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggffFfggfffggFfffg",
        "gFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffggFfffggfffFggfffggfFf",
        "FggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgf",
},file="map.bmp"},deploy={unselectables={{position={8,21},hero="JiGuang73"},{position={10,24},hero="GongZiGai73"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=18000}}
