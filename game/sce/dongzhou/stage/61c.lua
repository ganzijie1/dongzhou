gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"WeiXianGong61","GongSunDing61"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="wei_palace",name="卫国宫城",position={12,12},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}
gstory={chapter="第六十一回·下／第六十二回开端",title="晋悼公驾楚会萧鱼 孙林父因歌逐献公",battle_title="卫侯出奔",objective="保护卫献公击退尹公佗并抵达齐境。",map_asset="m100.png",
 intro={
  {speaker="",text="卫献公轻慢孙林父、宁殖，又借《巧言》讥刺孙氏。孙林父在戚邑聚集家甲，迎立公孙剽之谋渐成。"},
  {speaker="孙林父",text="卫侯已经明言猜忌孙氏，再坐等下去必受其祸。整顿家甲，攻入国都。"},
  {speaker="",text="孙蒯、孙嘉率兵击散二百余宫甲。卫献公只剩十余人，由神射手公孙丁护送，从东门奔齐。"},
  {speaker="卫献公",text="前有河泽，后有追兵。寡人若能抵达齐境，尚可等待复国之日。"},
  {speaker="公孙丁",text="臣负责断后。主公沿东门大道前进，不要停在追兵射程之内。"},
  {speaker="",text="庾公差追到后认出授业恩师公孙丁，去掉箭镞，四箭只中车身，以全师恩与主命。"},
  {speaker="尹公佗",text="庾公差顾念师门，我与公孙丁却隔了一层。若无功而返，如何回复孙氏？"},
  {speaker="公孙丁",text="射艺传承不可忘本。你若仍要追来，我只能以你的箭还射于你。"},
  {speaker="军令",text="护送卫献公沿东门大道抵达齐境。尹公佗出现后必须击退，公孙丁与卫献公不得被击退。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="庾公差",text="四箭去镞，只射车身，不伤吾师与卫侯！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="尹公佗",text="师恩为轻，主命为重，我再来追取卫侯！"}
 },
 victory={
  {speaker="",text="尹公佗一箭射来，公孙丁伸手接住，搭回弓弦，一箭贯其左臂，再发一箭将其射死。"},
  {speaker="",text="卫献公之弟公子鱄冒死赶来从驾，君臣进入齐境。齐灵公把卫献公安置在莱城。"},
  {speaker="卫献公",text="若非公孙丁神射，寡人已经死在河泽。今日奔亡，实由轻慢大臣、自取其祸。"},
  {speaker="",text="孙林父与宁殖迎公孙剽即位，是为卫殇公。晋悼公认为卫衎无道，没有出兵讨伐。"},
  {speaker="",text="齐灵公见晋侯无意干涉卫国内乱，开始图谋争霸；晋悼公却已病重。"},
  {speaker="军令",text="卫侯出奔完成，获得1100金币。第六十一回结束。"}
 },
 defeat={{speaker="",text="卫献公或公孙丁被击退，本关失败。"}}
}
local second_wave=false local yin_spawned=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("GongZiZhuan61",1)end
function on_begin(game)game:generate_unit("SunKuai61",1,Enum.force.enemy,{12,25});game:generate_unit("SunJia61",1,Enum.force.enemy,{15,27});many(game,"WeiPalaceGuard61",{{16,16},{17,18},{18,20}},Enum.force.own);many(game,"SunPursuer61",{{11,23},{16,24},{18,27},{20,25}},Enum.force.enemy);many(game,"SunArcher61",{{10,27},{17,29}},Enum.force.enemy)end
function on_update(game)if not second_wave and game:is_unit_within("WeiXianGong61",{35,18},3)then second_wave=true;game:push_cmd_speak(0,"庾公差去镞发箭，四箭只中车身，随后依师礼退兵。")end if second_wave and not yin_spawned and game:is_unit_within("WeiXianGong61",{46,18},3)then yin_spawned=true;game:generate_unit("YinGongTuo61",1,Enum.force.enemy,{50,18});many(game,"SunPursuer61",{{49,16},{49,20},{52,17},{52,21}},Enum.force.enemy);game:generate_unit("GongZiZhuan61",1,Enum.force.ally,{54,20});game:push_cmd_speak(0,"尹公佗再次追来！公子鱄也从齐境方向赶来接应！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if yin_spawned and not game:has_unit("YinGongTuo61") and game:is_unit_within("WeiXianGong61",{62,18},1)then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="WeiExileEscape61",turn_limit=28,map={blocked_edges={},size={64,38},terrain={
        "FgfffFggffffggFffggffffFggwgggwggwwggwgggwggwwggwgggwggwwggwgggw",
        "ffggffffFgffffggfFfggfFfwwggwgggwggwwggwgggwggwwggwgggwggwwggwgg",
        "gfFfggffffgFffffFgfffggfggwwggwgggwggwwggwgggwggwwggwgggwggwwggw",
        "fggffFggffFfggffffgFfffggwggwwggwgggwggwwggwgggwggwwggwgggwggwwg",
        "fffgFfffggfffFggffffggFfgggwggwwggwgggwggwwggwgggwggwwggwgggwggw",
        "gffWWWWWWWWWWWWWWWWWWWWggwgggwggwwggwgggwggwwggwgggwggwwggwgggwg",
        "fFgWiiiiiiiiiiiiiiiiiiWfwggwgggwggwwggwgggwggwwggwgggwggwwggwggg",
        "fffWiiiiiiiiiiiiiiiiiiWfgwwggwgggwggwwggwgggwggwwggwgggwggwwggwg",
        "gffWiiiiiiiiiiiiiiiiiiWgwggwwggwgggwggwwggwgggwggwwggwgggwggwwgg",
        "fggWiiiiiiiiiiiiiiiiiiWfggwggwwggwgggwggwwggwgggwggwwggwgggwggww",
        "FffWiiiiiiiiiiiiiiiiiiWFwgggwggwwggwgggwggwwggwgggwggwwggwgggwgg",
        "ggfWiiiiiiiiiiiiiiiiiiWgggwgggwggwwggwgggwggwwggwgggwggwwggwgggw",
        "ffFWiiiiiiiiCiiiiiiiiiWfwwggwgggwggwwggwgggwggwwggwgggwggwwggwgg",
        "fffWiiiiiiiiiiiiiiiiiiWfggwwggwgggwggwwggwgggwggwwggwgggwggwwggw",
        "ggfWiiiiiiiiiiiiiiiiiiWggwggwwggwgggwggwwggwgggwggwwggwgggwggwwg",
        "ffFWiiiiiiiiiiiiiiiiiiWfgggwggwwggwgggwggwwggwgggwggwwggwgggwggw",
        "fFfWiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffffffff",
        "ggfWiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffffffff",
        "ffgWiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffffffff",
        "gFfWiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffffffff",
        "FggWiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffffffff",
        "fffWiiiiiiiiiiiiiiiiiiWfwgggwggwwggwgggwggwwggwgggwggwwggwgggwgg",
        "gffWiiiiiiiiiiiiiiiiiiWgggwgggwggwwggwgggwggwwggwgggwggwwggwgggw",
        "FggWiiiiiiiiiiiiiiiiiiWFwwggwgggwggwwggwgggwggwwggwgggwggwwggwgg",
        "fffWiiiiiiiiiiiiiiiiiiWfggwwggwgggwggwwggwgggwggwwggwgggwggwwggw",
        "gfFWiiiiiiiiiiiiiiiiiiWggwggwwggwgggwggwwggwgggwggwwggwgggwggwwg",
        "fggWiiiiiiiiiiiiiiiiiiWfgggwggwwggwgggwggwwggwgggwggwwggwgggwggw",
        "fffWiiiiiiiiiiiiiiiiiiWfgwgggwggwwggwgggwggwwggwgggwggwwggwgggwg",
        "ggfWiiiiiiiiiiiiiiiiiiWgwggwgggwggwwggwgggwggwwggwgggwggwwggwggg",
        "fFgWiiiiiiiiiiiiiiiiiiWfgwwggwgggwggwwggwgggwggwwggwgggwggwwggwg",
        "fffWiiiiiiiiiiiiiiiiiiWfwggwwggwgggwggwwggwgggwggwwggwgggwggwwgg",
        "ggfWWWWWWWWWWWWWWWWWWWWgggwggwwggwgggwggwwggwgggwggwwggwgggwggww",
        "ffggffFfggfffggFfffgFfffwgggwggwwggwgggwggwwggwgggwggwwggwgggwgg",
        "FfffggfffFggffFggffffggFggwgggwggwwggwgggwggwwggwgggwggwwggwgggw",
        "ggfFffggFfffggfffFgffffgwwggwgggwggwwggwgggwggwwggwgggwggwwggwgg",
        "ffFgffffggfFffggfffgFfffggwwggwgggwggwwggwgggwggwwggwgggwggwwggw",
        "gfffgFffffggffFfggfFfggfgwggwwggwgggwggwwggwgggwggwwggwgggwggwwg",
        "fggfffggFfffgFffffggffFggggwggwwggwgggwggwwggwgggwggwwggwgggwggw",
},file="map.bmp"},deploy={unselectables={{position={18,17},hero="WeiXianGong61"},{position={19,19},hero="GongSunDing61"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=11000}}
