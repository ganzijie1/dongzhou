gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"SiDai67","YinDuan67"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="zheng_west",name="郑城西署",position={18,28},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}},{id="zheng_palace",name="郑国宫署",position={30,30},restore_hp=25,restore_mp=15,rewards={}},{id="zheng_east",name="郑城东署",position={43,28},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十七回·下",title="卢蒲癸计逐庆封 楚灵王大合诸侯",battle_title="郑门讨伯有",objective="守住郑国北门，击破良氏家甲并击退良霄。",map_asset="m116.png",
 intro={
  {speaker="",text="齐国庆氏败亡后，高氏、栾氏相继专政。高竖据卢邑自保，闾邱婴许立高氏之后，兵乱未扩大成大战。"},
  {speaker="",text="郑国上卿良霄字伯有，奢侈嗜酒，常在地下酒室通宵饮宴，家臣有事也不得入见。"},
  {speaker="公孙黑",text="我与公孙楚争娶徐吾犯之妹，又被良霄强令出使楚国。既不肯见我，我便烧他的府第。"},
  {speaker="",text="公孙黑联合印段包围良府并纵火。良霄醉中被家臣扶上车，逃往雍梁。"},
  {speaker="良霄",text="国氏、罕氏没有参与拒绝良氏的盟约，他们必会助我。召集家甲，从郑国北门杀回去！"},
  {speaker="驷带",text="良霄误判国、罕两家态度。公孙黑命我与印段守住北门，不许叛军进入城中。"},
  {speaker="印段",text="家甲在前，弓手随后。先击破良氏随从，再围良霄，不可让他借夜色退回雍梁。"},
  {speaker="公孙黑",text="我留在城内坚守，不会主动出门。驷带、印段率军迎击。"},
  {speaker="良霄",text="我仍是郑国上卿。挡我归城者，皆是乱臣！"},
  {speaker="军令",text="击退全部良氏家甲与弓手，解除良霄保护后将其击退。驷带、印段任一被击退均失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="驷带",text="良氏家甲已经逼近北门，列阵迎敌！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="良霄",text="家甲尽失也挡不住我，随我冲入郑城！"}
 },
 victory={
  {speaker="",text="良霄在北门外战败，逃入屠羊之肆，被追兵杀死，随行家臣也全部战死。"},
  {speaker="子产",text="兄弟相攻，国之不幸。即便良霄有罪，也应收敛他与家臣的尸身，以礼安葬。"},
  {speaker="",text="罕虎拒绝执政，推举子产。子产整顿田制、乡伍与服章，抑制奢侈，又铸刑书、保留乡校议政。"},
  {speaker="",text="公孙黑继续乱政，最终被子产依法处死。郑人后来传说良霄为厉，子产为良氏立后，流言才平息。"},
  {speaker="",text="蔡世子般弑父自立；宋宫大火，伯姬因傅母未到而不肯下堂，最终葬身火海。晋国只救宋灾而不讨蔡乱，霸业由此衰落。"},
  {speaker="",text="虢地会盟时，楚公子围僭用国君仪仗。子产不许楚军带兵入郑，公子围只能卸下弓矢完成迎亲。"},
  {speaker="",text="公子围归楚后勒死郏敖，又杀幕、平夏，自立为楚灵王；随后向晋国索取诸侯会盟与婚姻，列国不敢违抗。"},
  {speaker="军令",text="郑门讨伯有完成，获得900金币。第六十七回结束。"}
 },
 defeat={{speaker="",text="驷带、印段任一被击退，或超过二十二回合，失败。"}}
}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
local liang_exposed=false
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("GongSunHei67",1,Enum.force.ally,{30,25});game:generate_unit("LiangXiao67",1,Enum.force.enemy,{30,7});game:set_unit_invulnerable("LiangXiao67",true)
 many(game,"ZhengGateGuard67",{{24,20},{28,20},{33,20},{37,20},{26,24},{35,24}},Enum.force.own);many(game,"ZhengGateArcher67",{{22,22},{39,22},{28,26},{33,26}},Enum.force.own)
 many(game,"LiangHouseGuard67",{{25,8},{28,10},{33,10},{36,8},{23,12},{38,12},{27,14},{34,14}},Enum.force.enemy);many(game,"LiangHouseArcher67",{{24,6},{36,6},{25,15},{37,15}},Enum.force.enemy)
end
function on_update(game)
 if not liang_exposed and not game:has_unit("LiangHouseGuard67") and not game:has_unit("LiangHouseArcher67")then liang_exposed=true;game:set_unit_invulnerable("LiangXiao67",false);game:push_cmd_speak(0,"良氏家甲已经全灭！良霄败势已成，截住他通往屠羊肆的退路！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if liang_exposed and not game:has_unit("LiangXiao67")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="BoyouRebellion67",turn_limit=22,map={blocked_edges={},size={62,42},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFf",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggf",
        "gfFfggffffgFffffFgfffffgffffgffffgffffgfffffggffFfggfffggFfffg",
        "fggffFggffFfggffffgFffgffffgffffgffffgffffgfffggfffFggffFggfff",
        "fffgFfffggfffFggfffffgffffgffffgffffgffffgfgfFffggFfffggfffFgf",
        "gffffggFffggffffFgffgffffgffffgffffgffffgfffFgffffggfFffggfffg",
        "fFgffffggfFfggfFffggffffgffffgffffgffffgffffffgFffffggffFfggfF",
        "fffgFffffFgfffggffFffffgffffgffffgffffgffffggfffggFfffgFffffgg",
        "gffFfggffffgFfffggffffgffffgffffgffffgffffgfFggffFggffffggFfff",
        "fggfffFggffffggFffggfgffffgffffgffffgffffgfFfffggfffFgffffggfF",
        "FffggffffFgfffFggfffgffffgffffgffffgffffgffggfFffggfffgFffffFg",
        "ggfFfggfFffggffffFgfffffgffffgffffgffffgfffffggffFfggfFfggffff",
        "ffFgfffggffFfggffffgfffgffffgffffgffffgffffFfffgFffffggffFggff",
        "ffffgFfffggfffFggffFffgffffgffffgffffgffffgggffffggFfffggfffFg",
        "ggffffggFffggFfffggffgffffgffffgffffgffffgfffFgffffggfFffggFff",
        "ffFgfffFggfffggfFffggffffgffffgffffgffffgffgfffgFffffFgffffggf",
        "fFffggffffFgfffggffFffffgffffgffffgffffgffffggfFfggffffgFffffg",
        "ggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffggffFggffffggFff",
        "ffggffWWWWWWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWWWWWWffFggf",
        "gFffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffffF",
        "FggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggfff",
        "fffFgfWihiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihiWffFggf",
        "gffffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFfffg",
        "FggffFWiiiiihiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiihiiiiiWffggFf",
        "fffggfWhiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihiiWffffgg",
        "gfFffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFffff",
        "fggffFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggff",
        "fffgFfWiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihWfffFgg",
        "ggfffgWiiiiiiiiiiiCiiiiiiiiiiiiiiiiiiiiiiiiCiiiiiiiiiiiWggffff",
        "fFggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggfF",
        "ffffFgWihiihiihiihiihiihiihiihCihiihiihiihiihiihiihiihiWgfffgg",
        "ggfFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfgFfff",
        "ffggffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggF",
        "FfffggWhiihiihiihiihhihiihiihiihiihiihiihiihiihiihiihiiWgfffFg",
        "ggfFffWiiiiiiihiiiiiiiiiiihiiiiiiiiiiihiiiiiiiihiiiiiiiWfggfff",
        "ffFgffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFfggf",
        "gfffgFWiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihiihWgfffFg",
        "fggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggFff",
        "ffFggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfffggf",
        "gFfffgWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWFgfffg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFff",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggffFfgg",
},file="map.bmp"},deploy={unselectables={{position={27,21},hero="SiDai67"},{position={34,21},hero="YinDuan67"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=9000}}
