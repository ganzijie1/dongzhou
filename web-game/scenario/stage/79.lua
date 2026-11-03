gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"GouJian79","LingGuFu79","FanLi79"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="yue_camp",name="越军营寨",position={9,29},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="wu_camp",name="吴军营寨",position={51,11},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第七十九回",title="归女乐黎弥阻孔子 栖会稽文种通宰嚭",battle_title="携李之战",objective="击破吴军前锋，灵姑浮接近阖闾触发负伤撤退。",map_asset="m125.png",
 intro={
  {speaker="",text="越王允常去世，勾践即位。吴王阖闾乘丧伐越，伍员虽谏丧国不宜轻敌，吴军仍进至携李。"},
  {speaker="勾践",text="吴军强盛，正面久战不利。先以敢死队三次冲击，扰乱其心，再由全军从河湾反击。"},
  {speaker="范蠡",text="吴军主力在东北林地，阖闾居中。灵姑浮若能突入王旗，可迫吴军全线撤退。"},
  {speaker="灵姑浮",text="我只认吴王大纛。若能以戈伤他，越国今日便可保全。"},
  {speaker="伍子胥",text="越兵阵前自刎，是要乱我军心。大王不可前出，应保持阵形等待其气衰。"},
  {speaker="军令",text="击破吴军前锋，使灵姑浮接近阖闾触发史实负伤撤退。勾践、范蠡、灵姑浮任一被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="灵姑浮",text="我将直取吴王大纛。"}
 },
 victory={
  {speaker="",text="越国敢死队在阵前自刎，吴军惊愕。越军乘势冲锋，灵姑浮以戈击中阖闾足趾。"},
  {speaker="吴王阖闾",text="我伤势难支，立即退兵。夫差务必记住，是越王勾践使我至此！"},
  {speaker="",text="吴军退至陉地，阖闾伤重去世，专毅也因护主负伤而亡。夫差即位，日夜命人提醒父仇。"},
  {speaker="吴王夫差",text="三年之内若不能报越，我何以立于吴国！伍员整军，伯嚭治粮，准备再战。"},
  {speaker="军令",text="携李之战完成，获得2100金币。下一关：夫椒会稽。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("WuHelu79",1,Enum.force.enemy,{51,11});game:set_unit_invulnerable("WuHelu79",true);game:generate_unit("WuZiXu79",1,Enum.force.enemy,{46,15});game:generate_unit("ZhuanYi79",1,Enum.force.enemy,{42,18});many(game,"YueGuard79",{{6,25},{8,32},{12,24},{15,31},{18,28}},Enum.force.own);many(game,"YueArcher79",{{5,29},{12,35},{17,24}},Enum.force.own);many(game,"WuGuard79",{{38,16},{41,12},{44,9},{47,11},{48,18},{52,16},{55,13},{57,9}},Enum.force.enemy);many(game,"WuArcher79",{{40,9},{44,19},{50,8},{55,17}},Enum.force.enemy)
end
function on_update(game)
if phase==1 and game:is_unit_within("LingGuFu79",{51,11},1)then phase=2;game:set_unit_invulnerable("WuHelu79",false);game:push_cmd_speak(0,"灵姑浮突至王旗，以戈击中阖闾足趾！击退阖闾，吴军便会撤退！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("WuHelu79")then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou79",turn_limit=28,map={blocked_edges={},size={62,42},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFf",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggf",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFfffmwwmwwmwwmwwmwwmffg",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFwwmwwmwwmwwmwwmwfff",
        "fffgFfffggfffFggffffggvvvvvvvvvggfffFggfffgwmwwmwwmwwmwwmwwFgf",
        "gffffggFffggffffFgfffFvvvvvvvvvffggffffFgffmwwmwwmwwmwwmwwmffg",
        "fFgffffggfFfggfFffggffvvvvvvvvvffFfggfFffggwwmwwmwwmwwmwwmwgfF",
        "fffgFffffFgfffggffFfggvvvvvvvvvgFffffggffFfwmwwmwwmwwmwwmwwfgg",
        "gffFfggffffgFfffggfffFgvvvvvvvvvfggFfffggffmwwmwwmwwmwwmwwmfff",
        "fggfffFggffffggFffggFffvvvvvvvvvfffggfFffggwwmwwmwwmwwmwwmwgfF",
        "FffggffffFgfffFggfffggfvvvvvvvvvFgfffFgffffwmwwmwwmwwmwwmwwfFg",
        "ggfFfggfFffggffffFgfffgvvvvvvvvvffggfffgFffmwwmwwmwCmwwmwwmfff",
        "ffFgfffggffFfggffffgFfffvvvvvvvvvfFfggfffggwwmwwmwwmwwmwwmwgff",
        "ffffgFfffggfffFggffFfggfvvvvvvvvvgfffFggffFwmwwmwwmwwmwwmwwfFg",
        "ggffffggFffggFfffggfffFgvvvvvvvvvfggFfffggfffFgffffggfFffggFff",
        "ffFgfffFggfffggfFffggfffvvvvvvvvvfffggfFffggfffgFffffFgffffggf",
        "fFffggffffFgfffggffFfggfFvvvvvvvvvffffggffFfggfFfggffffgFffffg",
        "ggffFfggffffgFfffgFffffggvvvvvvvvvggFfffgFffffggffFggffffggFff",
        "ffggfffFggffFfggfffggFfffvvvvvvvvvfFggffffggFfffggfffFgfffFggf",
        "gFffggFfffggfffFggfffggfFvvvvvvvvvgfffFgffffggfFffggFffggffffF",
        "FggfffggfFffggffffFgfffFgfvvvvvvvvvggfffgFffffFgffffggfFfggfff",
        "fffFgfffggffFfggfFffggfffgvvvvvvvvvFfggfFfggffffgFffffggffFggf",
        "gffffgFfffgFffffggffFfggffvvvvvvvvvffffggffFggffffggFfffgFfffg",
        "FggffFfggfffggFfffggfffFggvvvvvvvvvggFfffggfffFgfffFggffffggFf",
        "fffggfffFggfffggfFffggFfffgvvvvvvvvvfggfFffggFffggffffFgffffgg",
        "gfFffggffffFgfffFgffffggfFfvvvvvvvvvfffFgffffggfFfggffffgFffff",
        "fggffFfggfFffggfffgFffffggfvvvvvvvvvgffffgFffffggffFggffFfggff",
        "fffgFffffggffFfggfffggFfffgvvvvvvvvvFggffffggFfffgFfffggfffFgg",
        "ggfffggFfffggfffFggffFggffffvvvvvvvvvffFgfffFggffffggFffggffff",
        "fFggfffggCFffggFfffggfffFgffvvvvvvvvvgFffggffffFgffffggfFfggfF",
        "ffffFgfffFgffffggfFffggfffgFvvvvvvvvvfggfFfggffffgFffffFgfffgg",
        "ggfFffggfffgFffffggffFfggfFfvvvvvvvvvfffggffFggffFfggffffgFfff",
        "ffggffFfggfffggFfffgFffffggffvvvvvvvvvFfffgFfffggfffFggffffggF",
        "FfffggfffFggffFggffffggFfffggvvvvvvvvvggffffggFffggffffFgfffFg",
        "ggfFffggFfffggfffFgffffggfFffvvvvvvvvvffFgffffggfFfggfFffggfff",
        "ffFgffffggfFffggfffgFffffFgffvvvvvvvvvffffgFffffFgfffggffFfggf",
        "gfffgFffffggffFfggfFfggffffgFfvvvvvvvvvgffFfggffffgFfffggfffFg",
        "fggfffggFfffgFffffggffFggffffgvvvvvvvvvfggfffFggffffggFffggFff",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggf",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFgfffg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggffFfgg",
},file="map.bmp"},deploy={unselectables={{position={9,29},hero="GouJian79"},{position={14,26},hero="LingGuFu79"},{position={11,33},hero="FanLi79"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=21000}}
