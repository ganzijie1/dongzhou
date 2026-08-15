gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"GouJian79","FanLi79","WenZhong79"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="yue_field_camp",name="越军残营",position={8,25},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}},{id="huiji_castle",name="会稽城池",position={58,23},restore_hp=30,restore_mp=20,rewards={{item="spirit_powder",amount=1}}}}
gstory={chapter="第八十回",title="夫差违谏释越 勾践竭力事吴",battle_title="夫椒会稽",objective="护送勾践、范蠡、文种进入会稽并坚守至第十二回合。",map_asset="m126.png",
 intro={
  {speaker="",text="夫差整军三年，在夫椒大败越军。勾践仅余五千甲士，退守会稽山城。"},
  {speaker="勾践",text="今日不是争胜之时。范蠡护军沿浅水撤向会稽，文种设法向吴国求和。"},
  {speaker="范蠡",text="河中深水不可过。穿过西门进入会稽后据山坚守，等文种说服伯嚭。"},
  {speaker="文种",text="吴太宰伯嚭贪财，可以重赂；夫差想北上争霸，也未必愿在山中消耗兵力。"},
  {speaker="伍子胥",text="越王困兽犹斗，此时不灭，日后必为吴患。大王万不可因小利释勾践！"},
  {speaker="吴王夫差",text="越国愿为臣妾，勾践又亲入吴服役。只要他确有诚意，寡人可以留其宗祀。"},
  {speaker="军令",text="护送勾践、范蠡、文种进入会稽城池并守到第十二回合。任一具名将领被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="文种",text="只要守住会稽，我便能以重赂说服伯嚭。"}
 },
 victory={
  {speaker="",text="文种重赂伯嚭，夫差接受越国请降。勾践入吴为臣，亲自尝粪问疾，终于骗得夫差信任。"},
  {speaker="伍子胥",text="飞鸟在青云之上，尚有矰缴之忧；潜鱼在深渊之下，尚有钓网之患。越王不可放归！"},
  {speaker="",text="夫差不听，三年后放勾践归越。勾践卧薪尝胆，与百姓同劳，范蠡练兵，文种治国。"},
  {speaker="勾践",text="越国今日不与吴争锋。十年生聚、十年教训，待吴国北上空虚，再报会稽之耻。"},
  {speaker="",text="孔子周游至卫、曹、宋、陈、蔡之间，屡遭困厄；与此同时，吴越两国的兴亡也进入新的阶段。"},
  {speaker="军令",text="夫椒会稽完成，获得2200金币。第八十回结束。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("FuChai80",1,Enum.force.enemy,{20,21});game:generate_unit("WuZiXu79",1,Enum.force.enemy,{18,27});many(game,"YueGuard79",{{5,21},{5,28},{8,18},{9,32},{13,20},{14,30}},Enum.force.own);many(game,"YueArcher79",{{4,24},{7,34},{14,24}},Enum.force.own);many(game,"WuGuard79",{{16,18},{16,23},{16,31},{20,16},{21,26},{22,33},{29,18},{30,29}},Enum.force.enemy);many(game,"WuArcher79",{{18,14},{23,20},{23,30},{30,24}},Enum.force.enemy)
end
function on_update(game)
if phase==1 and game:is_unit_within("GouJian79",{58,23},2)and game:is_unit_within("FanLi79",{58,23},4)and game:is_unit_within("WenZhong79",{58,23},4)then phase=2;game:push_cmd_speak(0,"越王与二大夫已进入会稽。依山坚守到第十二回合，等待文种议和！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and game:get_turn_current()>=12 then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou80",turn_limit=26,map={blocked_edges={},size={70,50},terrain={
        "FgfffFggffffggFffggffffFg~vvvv~vvvv~vvffggffffFgfffFgffffggfFffggfffgF",
        "ffggffffFgffffggfFfggfFffvvvv~vvvv~vvvffFfggfFffggfffgFffffggffFfggfFf",
        "gfFfggffffgFffffFgfffggffvvv~vvvv~vvvvgFffffggffFfggfffggFfffgFffffggf",
        "fggffFggffFfggffffgFfffggvv~vvvv~vvvv~ffggFfffggfffFggffFggffffggFfffg",
        "fffgFfffggfffFggffffggFffv~vvvv~vvvv~vgfffggfFffrmmmrmmmrmmmrmmmrmmmFf",
        "gffffggFffggffffFgfffFggf~vvvv~vvvv~vvfFgfffFgffmmmrmmmrmmmrmmmrmmmrgf",
        "fFgffffggfFfggfFffggffffFvvvv~vvvv~vvvFffggfffgFmmrmmmrmmmrmmmrmmmrmfg",
        "fffgFffffFgfffggffFfggfffvvv~vvvv~vvvvgffFfggfffmrmmmrmmmrmmmrmmmrmmff",
        "gffFfggffffgFfffggfffFggfvv~vvvv~vvvv~fggfffFggfrmmmrmmmrmmmrmmmrmmmgf",
        "fggfffFggffffggFffggFfffgv~vvvv~vvvv~vFffggFfffgmmmrmmmrmmmrmmmrmmmrfg",
        "FffggffffFgfffFggfffggfFf~vvvv~vvvv~vvgffffggfFfmmrmmmrmmmrmmmrmmmrmfF",
        "ggfFfggfFffggffffFgfffggfvvvv~vvvv~vvvfgFffffggfmrmmmrmmmrmmmrmmmrmmgg",
        "ffFgfffggffFfggffffgFfffgvvv~vvvv~vvvvfffggFfffgrWWWWWWWWWWWWWWWWWWmff",
        "ffffgFfffggfffFggffFfggffvv~vvvv~vvvv~ggffFggfffmWiiiiiiiiiiiiiiiiWrff",
        "ggffffggFffggFfffggfffFggv~vvvv~vvvv~vffggfffFgfmWiiiiiiiiiiiiiiiiWmFg",
        "ffFgfffFggfffggfFffggffff~vvvv~vvvv~vvfFffggfffgmWiiiiiiiiiiiiiiiiWmff",
        "fFffggffffFgfffggffFfggfFvvvv~vvvv~vvvggffFfggfFrWiiiiiiiiiiiiiiiiWmff",
        "ggffFfggffffgFfffgFffffggvvv~vvvv~vvvvffgFffffggmWiiiiiiiiiiiiiiiiWrgg",
        "ffggfffFggffFfggfffggFfffvv~vvvv~vvvv~ffffggFfffmWiiiiiiiiiiiiiiiiWmff",
        "gFffggFfffggfffFggfffggfFv~vvvv~vvvv~vFgffffggfFmWiiiiiiiiiiiiiiiiWmgf",
        "FggfffggfFffggffffFgfffFg~vvvv~vvvv~vvffgFffffFgrWiiiiiiiiiiiiiiiiWmfF",
        "fffFgfffggffFfggfFffggfffvvvv~vvvv~vvvgfFfggffffmWiiiiiiiiiiiiiiiiWrff",
        "gffffgFfffgFffffggffFfggfvvv~vvvv~vvvvfggffFggffmWiiiiiiiiiiiiiiiiWmgf",
        "FggffFfggfffggFfffggfffFgvv~vvvv~vvvv~fffggfffFgmGiiiiiiiiCiiiiiiiWmfF",
        "fffggfffFggfffggfFffggFffv~vvvv~vvvv~vgfFffggFffrGiiiiiiiiiiiiiiiiWmFf",
        "gfFffggfCffFgfffFgffffggf~vvvv~vvvv~vvfFgffffggfmWiiiiiiiiiiiiiiiiWrgf",
        "fggffFfggfFffggfffgFffffgvvvv~vvvv~vvvfffgFffffgmWiiiiiiiiiiiiiiiiWmfg",
        "fffgFffffggffFfggfffggFffvvv~vvvv~vvvvgffffggFffmWiiiiiiiiiiiiiiiiWmFf",
        "ggfffggFfffggfffFggffFggfvv~vvvv~vvvv~fFgfffFggfrWiiiiiiiiiiiiiiiiWmgg",
        "fFggfffggfFffggFfffggfffFv~vvvv~vvvv~vFffggffffFmWiiiiiiiiiiiiiiiiWrff",
        "ffffFgfffFgffffggfFffggff~vvvv~vvvv~vvggfFfggfffmWiiiiiiiiiiiiiiiiWmff",
        "ggfFffggfffgFffffggffFfggvvvv~vvvv~vvvffggffFggfmWiiiiiiiiiiiiiiiiWmgg",
        "ffggffFfggfffggFfffgFffffvvv~vvvv~vvvvFfffgFfffgrWiiiiiiiiiiiiiiiiWmff",
        "FfffggfffFggffFggffffggFfvv~vvvv~vvvv~ggffffggFfmWiiiiiiiiiiiiiiiiWrfF",
        "ggfFffggFfffggfffFgffffggv~vvvv~vvvv~vffFgffffggmWiiiiiiiiiiiiiiiiWmgg",
        "ffFgffffggfFffggfffgFffff~vvvv~vvvv~vvffffgFffffmWiiiiiiiiiiiiiiiiWmff",
        "gfffgFffffggffFfggfFfggffvvvv~vvvv~vvvggffFfggffrWWWWWWWWWWWWWWWWWWmgf",
        "fggfffggFfffgFffffggffFggvvv~vvvv~vvvvffggfffFggmmmrmmmrmmmrmmmrmmmrFg",
        "ffFggffFggffffggFfffggfffvv~vvvv~vvvv~gFffggffffmmrmmmrmmmrmmmrmmmrmff",
        "gFfffggfffFgffffggfFffggFv~vvvv~vvvv~vfggfFfggfFmrmmmrmmmrmmmrmmmrmmgf",
        "fggfFffggfffgFffffFgffffg~vvvv~vvvv~vvfffFgfffggrmmmrmmmrmmmrmmmrmmmfg",
        "fffggffFfggfFfggffffgFfffvvvv~vvvv~vvvgffffgFfffmmmrmmmrmmmrmmmrmmmrff",
        "gFfffgFffffggffFggffffggFvvv~vvvv~vvvvFggffffggFmmrmmmrmmmrmmmrmmmrmgf",
        "FggffffggFfffggfffFgfffFgvv~vvvv~vvvv~fffFgfffFgmrmmmrmmmrmmmrmmmrmmfF",
        "fffFgffffggfFffggFffggfffv~vvvv~vvvv~vgfFffggfffrmmmrmmmrmmmrmmmrmmmff",
        "ggfffgFffffFgffffggfFfggf~vvvv~vvvv~vvfggffFfggfmmmrmmmrmmmrmmmrmmmrgg",
        "FfggfFfggffffgFffffggffFgvvvv~vvvv~vvvfffggfffFggffFfggfffggFfffggfffF",
        "ffffggffFggffffggFfffgFffvvv~vvvv~vvvvggFffggFfffggfffFggfffggfFffggFf",
        "ggFfffggfffFgfffFggffffggvv~vvvv~vvvv~fFggfffggfFffggffffFgfffFgffffgg",
        "ffggfFffggFffggffffFgffffv~vvvv~vvvv~vffffFgfffggffFfggfFffggfffgFffff",
},file="map.bmp"},deploy={unselectables={{position={8,25},hero="GouJian79"},{position={10,28},hero="FanLi79"},{position={10,22},hero="WenZhong79"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=22000}}
