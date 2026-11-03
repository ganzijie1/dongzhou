gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"WuYuan72","GongZiSheng72"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="zhao_post",name="昭关驿舍",position={44,8},restore_hp=20,restore_mp=15,rewards={{item="spirit_powder",amount=1}}}}
gstory={chapter="第七十二回",title="棠公尚捐躯奔父难 伍子胥微服过昭关",battle_title="昭关脱逃",objective="护送伍员、公子胜穿过昭关并抵达北方出口。",map_asset="m121.png",
 intro={
  {speaker="",text="伍奢与伍尚在郢都被杀，太子建先逃宋国，后因宋国内乱转入郑国。晋人令太子建为内应，太子建谋泄被郑定公处死。"},
  {speaker="伍员",text="父兄与太子皆死，公子胜是伍氏和太子唯一血脉。我必须带他穿过昭关，东投吴国。"},
  {speaker="",text="楚国沿途悬挂伍员画像。伍员困在东皋公家中七日，一夜须发尽白。东皋公请来相貌相似的皇甫讷。"},
  {speaker="黄甫讷",text="我穿你的衣服先过关，引守军追赶。你换上我的衣冠、白发遮面，趁乱带公子胜通过。"},
  {speaker="公子胜",text="关外还有大江。只要到了吴境，父仇与伍氏之仇终有报答之日。"},
  {speaker="军令",text="护送伍员与公子胜穿过双格关门并抵达北方出口。不要恋战；任一人被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="皇甫讷",text="我先引开守军，伍员趁乱从双格关门通过。"}
 },
 victory={
  {speaker="",text="皇甫讷故意露形奔走，关吏追错了人。伍员白发换装，带公子胜从另一列车马中通过昭关。"},
  {speaker="伍员",text="昭关已过，前面却是长江。楚军追骑将至，若没有舟楫仍难脱身。"},
  {speaker="",text="一名渔父驾小舟接伍员渡江，又拒绝百金宝剑。为断绝伍员疑心，渔父覆舟自沉。"},
  {speaker="",text="伍员一路乞食吹箫来到吴市。公子光听说楚国逃臣有大才，遣人暗中相访。"},
  {speaker="公子光",text="楚平王与囊瓦乱政，吴国正可西向。先生若能为我筹吴国之事，我也愿助先生报父兄之仇。"},
  {speaker="军令",text="昭关脱逃完成，获得1400金币。下一关：鸡父之战。"}
 },
 defeat={{speaker="",text="具名我军将领被击退，或未能完成关卡目标，本关失败。"}}
}
local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
game:generate_unit("HuangFuNe72",1,Enum.force.ally,{25,20});game:generate_unit("ZhaoGuanCaptain72",1,Enum.force.enemy,{31,13});many(game,"ZhaoGuard72",{{27,13},{36,13}},Enum.force.enemy);many(game,"ZhaoArcher72",{{23,14},{41,14}},Enum.force.enemy)
end
function on_update(game)
if phase==1 and game:is_unit_within("WuYuan72",{31,15},2)then phase=2;game:push_cmd_speak(0,"皇甫讷已引走关吏，伍员白发换装，立即穿关！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if game:is_unit_within("WuYuan72",{32,1},1)and game:is_unit_within("GongZiSheng72",{32,1},2)then return Enum.status.victory end return Enum.status.undecided
end
gstage={title_id="Dongzhou72",turn_limit=26,map={blocked_edges={},size={64,36},terrain={
        "mmmmmmmmmmmmmmmmmgggfggggfggggfggggfggggfggggfgfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmggfggggfggggfggggfggggfggggfggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgfggggfggggfggggfggggfggggfgggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmggggfggggfggggfggggfggggfggggffmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgggfggggfggggfggggfggggfggggfgfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmggfggggfggggfggggfggggfggggfggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmggggfggggfggggfggggfggggfgCggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmgggfggggfggggfggggfggggfggggfgmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmggfggggfggggfggggfggggfggggfggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmgfggggfggggfggggfggggfggggfgggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmggggfggggfggggfggggfggggfggggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggfggggfggggfggggfggggfggggfggmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWgmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmffggggfggggfggggfggggfggggfggggmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggfmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfgggfggggfggggfggggfggggfggggfgmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggfggggfggggfggggfggggfggggfggmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfgfggggfggggfggggfggggfggggfgggmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmggfggggfggggfggggfggggfggggfggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgfggggfggggfggggfggggfggggfgggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmggggfggggfggggfggggfggggfggggffmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmgvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmgggfggggfggggfggggfggggfggggfgmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmggfggggfggggfggggfggggfggggfggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmgfggggfggggfggggfggggfggggfgggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfggggfggggfggggfggggfggggfggggmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmggggfggggfggggfggggfggggfggggfmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmgggfggggfggggfggggfggggfggggfgmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmfgfggggfggggfggggfggggfggggfgggmmmmmmmmmmmmmmm",
},file="map.bmp"},deploy={unselectables={{position={31,32},hero="WuYuan72"},{position={34,32},hero="GongZiSheng72"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=14000}}
