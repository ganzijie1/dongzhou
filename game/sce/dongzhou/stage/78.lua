gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"LuDingGong78","JiSunSi78"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="lu_palace",name="鲁国宫府",position={29,11},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}},{id="jishi_manor",name="季氏府",position={20,22},restore_hp=20,restore_mp=10,rewards={}},{id="shusun_manor",name="叔孙氏府",position={38,22},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第七十八回",title="会夹谷孔子却齐 堕三都闻人伏法",battle_title="鲁国平叛",objective="先击破阳虎军，再守卫鲁宫击退公山不狃与叔孙辄。",map_asset="m124.png",
 intro={
  {speaker="",text="孔子摄相事随鲁定公会齐于夹谷，以礼制止齐国莱人劫盟，又迫齐归还侵鲁土地。齐国转而以女乐离间鲁政。"},
  {speaker="",text="鲁国先有阳虎专权。阳虎挟持季孙斯失败，遂集结叛军攻向国都南门，企图控制鲁君与三桓。"},
  {speaker="鲁定公",text="城墙不可跨越，叛军只能从南门进入。宫军守住门内街道，不能让阳虎接近王宫。"},
  {speaker="季孙斯",text="阳虎熟知鲁都门户，必会分兵冲击。先击退阳越与前锋，再围攻阳虎。"},
  {speaker="阳虎",text="季氏多年把持鲁政，我今日夺其家兵，另立国政。破南门，直取宫府！"},
  {speaker="军令",text="第一阶段击破阳虎军；第二阶段公山不狃、叔孙辄攻宫。鲁定公与季孙斯任一被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="鲁定公",text="南门是唯一通路，宫军依街巷迎击。"}
 },
 victory={
  {speaker="",text="阳越在南门中箭身亡，阳虎军溃败。阳虎先奔齐，后投晋国赵氏。"},
  {speaker="",text="数年后公山不狃与叔孙辄又据费邑起兵，直攻鲁宫。孔子指挥申句须、乐颀反击，叛军再败。"},
  {speaker="公山不狃",text="鲁国终究不容我等。叔孙辄向齐境退，我自往吴国求存。"},
  {speaker="",text="孔子建议堕毁三都，以削弱家臣叛乱根基。叔孙、季孙先后响应，孟孙氏却暗中阻止成邑被毁。"},
  {speaker="",text="齐国送来女乐与良马，鲁定公、季桓子沉迷观赏，多日不朝。孔子失望离鲁，开始周游列国。"},
  {speaker="军令",text="鲁国平叛完成，获得1900金币。下一关：携李之战。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("YangHu78",1,Enum.force.enemy,{28,37});game:generate_unit("YangYue78",1,Enum.force.enemy,{34,35});many(game,"LuGuard78",{{25,15},{32,15},{20,20},{38,20},{25,27},{32,27}},Enum.force.own);many(game,"LuRebel78",{{23,36},{26,38},{31,38},{37,36},{21,39},{40,39}},Enum.force.enemy);many(game,"LuRebelArcher78",{{24,40},{35,40},{20,35},{39,35}},Enum.force.enemy)
end
function on_update(game)
if phase==1 and not game:has_unit("YangHu78")and not game:has_unit("YangYue78")then phase=2;game:generate_unit("GongShanBuNiu78",1,Enum.force.enemy,{28,34});game:generate_unit("ShuSunZhe78",1,Enum.force.enemy,{29,34});many(game,"LuRebel78",{{18,31},{22,33},{35,33},{40,30}},Enum.force.enemy);many(game,"LuRebelArcher78",{{16,28},{42,28}},Enum.force.enemy);game:push_cmd_speak(0,"阳虎败逃后，公山不狃、叔孙辄又从费邑攻入南门！守住鲁宫！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("GongShanBuNiu78")and not game:has_unit("ShuSunZhe78")then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou78",turn_limit=32,map={blocked_edges={},size={58,42},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffg",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFfff",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggF",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFg",
        "fffgFfffggfffFggffffggFffggFfffggfffFggfffggfFffggFfffggff",
        "gffffggFffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfggfFffgg",
        "fFgffffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggffFf",
        "fffgFffffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFfffgFff",
        "gffFfggfffWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWFggffffgg",
        "fggfffFggfWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWfffFgffff",
        "FffggffffFWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWggfffgFff",
        "ggfFfggfFfWiiihhhhhhhhhiiiiiiCiiiiihhhhhhhhhhiiiWFfggfFfgg",
        "ffFgfffggfWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWffffggffF",
        "ffffgFfffgWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWggFfffggf",
        "ggffffggFfWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWffggfFffg",
        "ffFgfffFggWiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhhiiiWffffFgfff",
        "fFffggffffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffgFf",
        "ggffFfggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFggffffg",
        "ffggfffFggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffFgfff",
        "gFffggFfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFffggf",
        "FggfffggfFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggfFfg",
        "fffFgfffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFffffggff",
        "gffffgFfffWiiiiiiiiiCiiiiiiiiiiiiiiiiiCiiiiiiiiiWfggFfffgF",
        "FggffFfggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggffff",
        "fffggfffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffffFgff",
        "gfFffggfffWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWfggffffgF",
        "fggffFfggfWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWffFggffFf",
        "fffgFffffgWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWgFfffggff",
        "ggfffggFffWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWffggFffgg",
        "fFggfffggfWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWffffggfFf",
        "ffffFgfffFWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWgFffffFgf",
        "ggfFffggffWiiihhhhhhhhiiiiiiiiiiiiiihhhhhhhhhiiiWFfggffffg",
        "ffggffFfggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffFggfff",
        "FfffggfffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffFgf",
        "ggfFffggFfWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWFfggfFffg",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffF",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggf",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffg",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggff",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggff",
},file="map.bmp"},deploy={unselectables={{position={29,11},hero="LuDingGong78"},{position={22,17},hero="JiSunSi78"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=19000}}
