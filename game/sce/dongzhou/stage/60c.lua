gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"XunYing54","XunYan58","ShiGai60","ZhongSunMie60","ShuLiangHe60","QinJinFu60","DiSiMi60"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="biyang_palace",name="偪阳城府",position={27,27},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="biyang_west_store",name="偪阳西库",position={17,18},restore_hp=20,restore_mp=10,rewards={}},{id="biyang_east_store",name="偪阳东库",position={38,18},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十回·下／第六十一回开端",title="智荀偃力伐偪阳",battle_title="偪阳之战",objective="从北门攻入偪阳。悬门事件后坚持至暴雨退水，在五回合总攻期限内击退云般，迫使偪阳君投降。任一具名我军将领被击退则失败。",map_asset="m097.png",
 intro={
  {speaker="",text="晋悼公会合鲁、宋、卫、曹、莒、邾、滕、薛等国，讨伐依楚的偪阳。偪阳虽小，城池却异常坚固。"},
  {speaker="智罃",text="围城二十四日仍未破，军粮将尽。诸军已有退意，但今日若退，天下必轻晋。"},
  {speaker="荀偃",text="请再给我与士匄七日。若不能克城，甘受军法。"},
  {speaker="士匄",text="我只给诸军六日。六日不下，先斩攻城不力者，再向元帅请罪。"},
  {speaker="仲孙蔑",text="鲁将秦堇父、狄虒弥愿先登。北门悬门危险，须有人托住闸板。"},
  {speaker="叔梁纥",text="悬门落下时由我举住。诸军只管穿门，不要停在闸下。"},
  {speaker="秦堇父",text="城墙不可越，只有北门可进。我和狄虒弥先攀门楼，夺取箭垛。"},
  {speaker="云般",text="偪阳虽小，也有死守之士。滚木礌石用尽，便在街巷接战。"},
  {speaker="军令",text="接近北门触发悬门事件。暴雨后进入五回合总攻阶段，五回合内击退云般；偪阳君不可直接击退。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="叔梁纥",text="悬门落下了！我来托住闸板，诸军迅速通过！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="士匄",text="积水已退，偪阳箭石也将耗尽。五日之内必须破城！"}
 },
 victory={
  {speaker="",text="大雨过后积水渐退。荀偃、士匄督军总攻，秦堇父与狄虒弥先登城头，联军从北门蜂拥而入。"},
  {speaker="",text="偪阳箭石俱尽，云般率死士转入街巷。激战中云般阵亡，守军再无统领。"},
  {speaker="偪阳君",text="城中军民已经力竭，愿开府库、献城投降，只求保全百姓。"},
  {speaker="智罃",text="受降，不许劫掠。偪阳虽小，能守二十余日，其志可敬。"},
  {speaker="",text="联军最终只用五日完成最后总攻。悼公本欲把偪阳赐给宋国向戌，向戌辞让，改赐宋国公族。"},
  {speaker="",text="归师途中，诸侯又在虎牢会盟。晋悼公的威望达到极盛，中原各国莫敢违命。"},
  {speaker="军令",text="偪阳之战完成，获得1600金币。第六十回结束。"}
 },
 defeat={{speaker="",text="联军具名将领被击退，或暴雨退水后五回合仍未击退云般，本关失败。"}}
}
local gate_event=false
local rain_started=false
local assault_turn=0
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("YunBan60",1,Enum.force.enemy,{27,25});game:set_unit_invulnerable("YunBan60",true);game:generate_unit("BiYangLord60",1,Enum.force.enemy,{27,27});game:set_unit_invulnerable("BiYangLord60",true)
 many(game,"JinCoalitionGuard60",{{17,3},{21,2},{26,2},{31,2},{36,3},{39,4}},Enum.force.own);many(game,"JinCoalitionArcher60",{{15,4},{41,3}},Enum.force.own)
 many(game,"BiYangGuard60",{{27,8},{28,8},{23,11},{32,11},{18,17},{37,17},{22,22},{33,22},{24,29},{31,29}},Enum.force.enemy)
 many(game,"BiYangArcher60",{{20,10},{35,10},{15,18},{40,18},{20,26},{35,26}},Enum.force.enemy)
end
function on_update(game)
 if not gate_event and (game:is_unit_within("QinJinFu60",{27,7},2)or game:is_unit_within("DiSiMi60",{27,7},2)or game:is_unit_within("ShuLiangHe60",{27,7},2))then gate_event=true;game:push_cmd_speak(0,"偪阳悬门突然落下！叔梁纥双手托住闸板，秦堇父、狄虒弥趁势穿门先登！")end
 if not rain_started and game:get_turn_current()>=6 then rain_started=true;assault_turn=game:get_turn_current();game:set_unit_invulnerable("YunBan60",false);game:push_cmd_speak(0,"连日暴雨已经退水，偪阳箭石耗尽！五回合总攻开始，击退云般迫其献城！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if rain_started and game:get_turn_current()>assault_turn+5 and game:has_unit("YunBan60")then return Enum.status.defeat end if rain_started and not game:has_unit("YunBan60")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="BiyangSiege60",turn_limit=28,map={blocked_edges={},size={56,42},terrain={
        "gwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwww",
        "wwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwg",
        "wwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgw",
        "wgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgww",
        "gwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwww",
        "wwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwg",
        "wwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgwwwgw",
        "fffgFfffWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWggFfffgF",
        "gffFfggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFggffff",
        "fggfffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffFgff",
        "FffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggfffgF",
        "ggfFfggfWiiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhiiiiWfFfggfFf",
        "ffFgfffgWiiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhiiiiWFffffggf",
        "ffffgFffWiiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhiiiiWfggFfffg",
        "ggffffggWiiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhiiiiWfffggfFf",
        "ffFgfffFWiiiihhhhhhhhhiiiiiiiiiiiihhhhhhhhhiiiiWFffffFgf",
        "fFffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggffffg",
        "ggffFfggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFggfff",
        "ffggfffFWiiiiiiiiCiiiiiiiiiiiiiiiiiiiiCiiiiiiiiWggfffFgf",
        "gFffggFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFffg",
        "FggfffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggfF",
        "fffFgfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFffffgg",
        "gffffgFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFfff",
        "FggffFfgWiiiiihhhhhhhhiiiiiiiiiiiihhhhhhhhiiiiiWfffFggff",
        "fffggfffWiiiiihhhhhhhhiiiiiiiiiiiihhhhhhhhiiiiiWggffffFg",
        "gfFffggfWiiiiihhhhhhhhiiiiiiiiiiiihhhhhhhhiiiiiWFfggffff",
        "fggffFfgWiiiiihhhhhhhhiiiiiiiiiiiihhhhhhhhiiiiiWgffFggff",
        "fffgFfffWiiiiihhhhhhhhiiiiiCiiiiiihhhhhhhhiiiiiWfgFfffgg",
        "ggfffggFWiiiiihhhhhhhhiiiiiiiiiiiihhhhhhhhiiiiiWfffggFff",
        "fFggfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffffggf",
        "ffffFgffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfgFffffF",
        "ggfFffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFfggfff",
        "ffggffFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffFggf",
        "FfffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggffffF",
        "ggfFffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFfggfFf",
        "ffFgffffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWFgfffggf",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffg",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFf",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFgg",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffff",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFgg",
    },file="map.bmp"},deploy={unselectables={{position={24,3},hero="XunYing54"},{position={29,3},hero="XunYan58"},{position={19,4},hero="ShiGai60"},{position={34,4},hero="ZhongSunMie60"},{position={26,5},hero="ShuLiangHe60"},{position={22,5},hero="QinJinFu60"},{position={31,5},hero="DiSiMi60"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=16000}}
