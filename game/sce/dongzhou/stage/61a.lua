gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"GongSunXia61","ZiChan61","GongSunChai61"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="west_palace",name="郑国西宫",position={24,10},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="west_store",name="西宫武库",position={16,18},restore_hp=20,restore_mp=10,rewards={}}, {id="east_store",name="东侧府库",position={34,18},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十一回·上",title="晋悼公驾楚会萧鱼 孙林父因歌逐献公",battle_title="郑宫平乱",objective="诛灭尉止党羽，平定郑国西宫内乱。",map_asset="m098.png",
 intro={
  {speaker="",text="偪阳破城后，晋悼公三次分军临郑，以轮番出师疲敝楚军。第一次驻牛首时，郑国西宫忽生内乱。"},
  {speaker="",text="尉止纠集司臣、侯晋等人，杀公子騑、公子发、公孙辄，退据北宫，企图控制郑国朝政。"},
  {speaker="公孙夏",text="父亲公子騑死于乱党，我当率家甲攻贼，为父报仇，也保郑国宗庙。"},
  {speaker="子产",text="国中虽乱，不能借外兵平事。家甲只击乱党，不得侵扰城中百姓。"},
  {speaker="公孙虿",text="我从东街策应。尉止若退入北宫，三路同时合围，不给其逃亡机会。"},
  {speaker="智罃",text="郑国内乱本可乘隙攻取，但乘人之危不义。晋军缓攻，听郑人自行定乱。"},
  {speaker="栾黡",text="若此时攻城，郑必不能战。元帅既以信义为先，下军遵令列阵，不入城。"},
  {speaker="军令",text="率三支家甲从南门进入西宫，击退尉止、司臣、侯晋等乱党。三名我方将领任一被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="公孙夏",text="乱党退入北宫，三路合围！"}
 },
 victory={
  {speaker="",text="公孙夏率家甲攻入北宫，公孙虿从侧翼夹击。尉止一党溃散，首恶尽被诛灭。"},
  {speaker="子产",text="内乱已经平定。收拢兵甲，安抚百姓，迎立公子嘉主持国政。"},
  {speaker="",text="智罃接受郑国求和，晋军退去；楚公子贞随后到来，郑国又与楚盟。这是三驾服楚的第一驾。"},
  {speaker="",text="次年晋军第二次围郑，向戌屯东门、孙林父屯北鄙、赵武营西郊、智罃扬兵南门。郑简公在毫城北与晋盟。"},
  {speaker="",text="郑国为迫使晋楚分出强弱，又诱楚国伐宋。晋悼公会合十二国第三次临郑，驻军萧鱼。"},
  {speaker="晋悼公",text="郑若真心归晋，俘虏尽数释放，虎牢戍兵也可撤去。以诚信相待，不再逼其反覆。"},
  {speaker="",text="郑简公感泣盟晋，献乐器车甲。悼公赏魏绛、智罃，郑国自此二十四年不再叛晋。"},
  {speaker="军令",text="郑宫平乱完成，获得1200金币。下一关：棫林突秦。"}
 },
 defeat={{speaker="",text="三名郑国具名将领被击退，家甲失去统领，本关失败。"}}
}
local rebels={"WeiZhi61","SiChen61","HouJin61"}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("WeiZhi61",1,Enum.force.enemy,{24,10});game:generate_unit("SiChen61",1,Enum.force.enemy,{16,18});game:generate_unit("HouJin61",1,Enum.force.enemy,{34,18});many(game,"ZhengHouseGuard61",{{19,30},{23,31},{27,31},{31,30}},Enum.force.own);many(game,"ZhengRebel61",{{24,25},{25,25},{14,22},{35,22},{20,15},{29,15},{22,9},{27,9}},Enum.force.enemy);many(game,"ZhengRebelArcher61",{{12,18},{38,18},{19,12},{30,12}},Enum.force.enemy)end
function on_update(game)end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end for _,h in ipairs(rebels)do if game:has_unit(h)then return Enum.status.undecided end end return Enum.status.victory end
gstage={title_id="ZhengPalaceRevolt61",turn_limit=24,map={blocked_edges={},size={50,34},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffgg",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFf",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggff",
        "fffgFfffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWggfFffgg",
        "gffffggFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFgffff",
        "fFgffffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffgFff",
        "fffgFfffWiiiiiiiiihhhhhhhhhhhhhhiiiiiiiiiWfggfffgg",
        "gffFfggfWiiiiiiiiihhhhhhhhhhhhhhiiiiiiiiiWffFggffF",
        "fggfffFgWiiiiiiiiihhhhhhhhhhhhhhiiiiiiiiiWgFfffggf",
        "FffggfffWiiiiiiiiihhhhhhChhhhhhhiiiiiiiiiWfggfFffg",
        "ggfFfggfWiiiiiiiiihhhhhhhhhhhhhhiiiiiiiiiWfffggffF",
        "ffFgfffgWiiiiiiiiihhhhhhhhhhhhhhiiiiiiiiiWgFfffgFf",
        "ffffgFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFggffffg",
        "ggffffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffFgfff",
        "ffFgfffFWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWggfffgFf",
        "fFffggffWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWFfggfFfg",
        "ggffFfggWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWffffggff",
        "ffggfffFWiiihhhhChhhiiiiiiiiiiihhhChhhhiiWggFfffgg",
        "gFffggFfWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWffggfFff",
        "FggfffggWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWffffFgff",
        "fffFgfffWiiihhhhhhhhiiiiiiiiiiihhhhhhhhiiWggffffgF",
        "gffffgFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFggffff",
        "FggffFfgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffFgff",
        "fffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFffgg",
        "gfFffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggfFf",
        "fggffFfgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFffffggf",
        "fffgFfffWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWfggFfffg",
        "ggfffggFfffggfffFggffFggffffggFfffggfffFgfffFggfff",
        "fFggfffggfFffggFfffggfffFgffffggfFffggFffggffffFgf",
        "ffffFgfffFgffffggfFffggfffgFffffFgffffggfFfggffffg",
        "ggfFffggfffgFffffggffFfggfFfggffffgFffffggffFggffF",
        "ffggffFfggfffggFfffgFffffggffFggffffggFfffgFfffggf",
        "FfffggfffFggffFggffffggFfffggfffFgfffFggffffggFffg",
},file="map.bmp"},deploy={unselectables={{position={21,30},hero="GongSunXia61"},{position={25,30},hero="ZiChan61"},{position={29,30},hero="GongSunChai61"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=12000}}
