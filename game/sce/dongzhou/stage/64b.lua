gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"HuaZhou64","QiLiang64","XiHouZhong64"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="qieyu_city",name="且于城",position={59,12},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}
gstory={chapter="第六十四回·下",title="曲沃城栾盈灭族 且于门杞梁死战",battle_title="且于门死战",objective="击退莒郊军，架盾越过火沟并抵达且于门。",map_asset="m107.png",
 intro={
  {speaker="",text="齐庄公回到齐境后转而袭莒，留下王孙挥统大军，自领三千精锐与勇爵诸士秘密进军。"},
  {speaker="",text="华周、杞梁不满两人只得一乘，却仍奉君命出征；小卒隰侯重慕其勇义，自愿同车。"},
  {speaker="华周",text="我与杞梁只用一车先行。隰侯重掌鼓，鼓声不停，我二人便不会退后。"},
  {speaker="杞梁",text="母亲教我：生而无义，死而无名，虽居勇爵也只为人所笑。今日当尽将士之责。"},
  {speaker="",text="三人在莒郊遇黎比公率三百甲士巡查。华周、杞梁跳车持戟，冲阵杀伤近半。"},
  {speaker="莒黎比公",text="二位勇名果然不虚。若肯罢战，我愿分莒国土地与你们共同享有。"},
  {speaker="华周",text="弃国归敌是不忠，受命半途而废是不信。我们只知深入破敌，不受封赏诱惑。"},
  {speaker="",text="黎比公败退且于门，在狭道挖沟灸炭，又命百名善射者伏于门旁。"},
  {speaker="隰侯重",text="我以盾伏在火炭之上，为二位铺出两步通路。只要你们越沟，我死亦有名。"},
  {speaker="军令",text="先击退莒黎比公；隰侯重抵达火沟后开启双格盾桥；华周、杞梁击退城门守将并抵达且于门即过关。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="莒黎比公",text="退守且于门，掘火沟，令百名弓手夹门伏射！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="隰侯重",text="盾桥已成，二位将军踏我背上越沟！"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="杞梁",text="既过火沟，便只向城门，不再回头！"}
 },
 victory={
  {speaker="",text="隰侯重伏盾于炭火之上，华周、杞梁踏盾越沟。回首时，他已被烈火烧死。"},
  {speaker="华周",text="此人勇义与我相同，却先我而死。我哭的不是畏死，而是痛惜同道。"},
  {speaker="",text="二人逼近且于门，百名弓手从门旁齐射。杞梁身受重伤，仍持戟杀敌，最终战死。"},
  {speaker="",text="华周身中数十箭，力尽被擒。莒黎比公将他载回城中，齐军主力随后也未能立刻破门。"},
  {speaker="齐庄公",text="三人单车深入，忠勇足以传世。撤回大军，厚恤杞梁、隰侯重之家。"},
  {speaker="",text="杞梁之妻后来闻夫战死，悲恸迎丧；其故事在后世不断流传演变。"},
  {speaker="军令",text="且于门死战完成，获得1000金币。第六十四回结束。"}
 },
 defeat={{speaker="",text="华周、杞梁、隰侯重任一在完成目标前被击退，或超过二十八回合，战役失败。"}}
}
local field_broken=false local bridge_ready=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("JuLiBiGong64",1,Enum.force.enemy,{29,23});game:generate_unit("JuGateCaptain64",1,Enum.force.enemy,{52,22});game:set_unit_invulnerable("JuGateCaptain64",true);many(game,"JuGuard64",{{23,18},{23,22},{23,26},{27,17},{27,27},{33,19},{33,25},{49,19},{49,26},{55,20},{55,25}},Enum.force.enemy);many(game,"JuArcher64",{{25,15},{25,30},{31,16},{31,29},{50,17},{50,28},{54,18},{54,27},{57,21},{57,24}},Enum.force.enemy)end
function on_update(game)
if not field_broken and not game:has_unit("JuLiBiGong64")then field_broken=true;game:push_cmd_speak(0,"黎比公退入且于门，火沟已经点燃。隰侯重立即前往盾桥位置！")end
if field_broken and not bridge_ready and game:is_unit_within("XiHouZhong64",{46,22},1)then bridge_ready=true;game:set_unit_invulnerable("JuGateCaptain64",false);game:push_cmd_speak(0,"隰侯重伏盾于炭火，双格通路已经打开！华周、杞梁越沟夺门！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if bridge_ready and not game:has_unit("JuGateCaptain64") and game:is_unit_within("HuaZhou64",{52,22},2) and game:is_unit_within("QiLiang64",{52,23},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="QieyuLastStand64",turn_limit=28,map={blocked_edges={},size={68,46},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffggfff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffFfggf",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFffffg",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggffFggffffggFff",
        "fffgFfffggfffFggffffggFffggFfffggfffFgmmmmmmmmmmmmmfffggfffFgffffggf",
        "gffffggFffggffffFgfffFggfffggfFffggfffmmmmmmmmmmmmmgWWWWWWWWWWWWWWWF",
        "fFgffffggfFfggfFffggffffFgfffggffFfggfmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "fffgFffffFgfffggffFfggffffgFfffgFffffgmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "gffFfggffffgFfffggfffFggffFfggfffggFffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWF",
        "fggfffFggffffggFffggFfffggfffFggfffggfmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "FffggffffFgfffFggfffggfFffggffffFgfffFmmmmmmmmmmmmmfWiiiiiiiiiiiiiWg",
        "ggfFfggfFffggffffFgfffggffFfggfFffggffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWf",
        "ffFgfffggffFfggffffgFfffgFffffggffFfggmmmmmmmmmmmmmfWiiiiiiCiiiiiiWf",
        "ffffgFfffggfffFggffFfggfffggFfffggfffFmmmmmmmmmmmmmFWiiiiiiiiiiiiiWg",
        "ggffffggFffggFfffggfffFggfffggfFffggFfmmmmmmmmmmmmmgWiiiiiiiiiiiiiWf",
        "ffFgfffFggfffggfFffggffffFgfffFgffffggmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "fFffggffffFgfffggffFfggfFffggfffgFffffmmmmmmmmmmmmmfWiiiiiiiiiiiiiWg",
        "ggffFfggffffgFfffgFffffggffFfggfffggFfmmmmmmmmmmmmmgWiiiiiiiiiiiiiWf",
        "ffggfffFggffFfggfffggFfffggfffFggfffffffffffff~fffffWiiiiiiiiiiiiiWF",
        "gFffggFfffggfffFggfffggfFffggFfffggfffffffffff~fffffWiiiiiiiiiiiiiWg",
        "FggfffggfFffggffffFgfffFgffffggfFfffffffffffff~fffffWiiiiiiiiiiiiiWf",
        "fffFgfffggffFfggfFffggfffgFffffggfffffffffffff~fffffWiiiiiiiiiiiiiWf",
        "gffffgFfffgFffffggffFfggfffggFfffgFfffffffffffGfffffGiiiiiiiiiiiiiWg",
        "FggffFfggfffggFfffggfffFggffFggfffffffffffffffGfffffGiiiiiiiiiiiiiWf",
        "fffggfffFggfffggfFffggFfffggfffFgfffffffffffff~fffffWiiiiiiiiiiiiiWf",
        "gfFffggffffFgfffFgffffggfFffggfffgFfffffffffff~fffffWiiiiiiiiiiiiiWg",
        "fggffFfggfFffggfffgFffffggffFfggfFffffffffffff~fffffWiiiiiiiiiiiiiWf",
        "fffgFffffggffFfggfffggFfffgFffffggffffffffffff~fffffWiiiiiiiiiiiiiWg",
        "ggfffggFfffggfffFggffFggffffggFfffggffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWF",
        "fFggfffggfFffggFfffggfffFgffffggfFffggmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "ffffFgfffFgffffggfFffggfffgFffffFgffffmmmmmmmmmmmmmfWiiiiiiiiiiiiiWg",
        "ggfFffggfffgFffffggffFfggfFfggffffgFffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWF",
        "ffggffFfggfffggFfffgFffffggffFggffffggmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "FfffggfffFggffFggffffggFfffggfffFgfffFmmmmmmmmmmmmmfWiiiiiiiiiiiiiWg",
        "ggfFffggFfffggfffFgffffggfFffggFffggffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWf",
        "ffFgffffggfFffggfffgFffffFgffffggfFfggmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "gfffgFffffggffFfggfFfggffffgFffffggffFmmmmmmmmmmmmmFWiiiiiiiiiiiiiWg",
        "fggfffggFfffgFffffggffFggffffggFfffgFfmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "ffFggffFggffffggFfffggfffFgfffFggffffgmmmmmmmmmmmmmfWiiiiiiiiiiiiiWf",
        "gFfffggfffFgffffggfFffggFffggffffFgfffmmmmmmmmmmmmmgWiiiiiiiiiiiiiWg",
        "fggfFffggfffgFffffFgffffggfFfggffffgFfmmmmmmmmmmmmmfWWWWWWWWWWWWWWWf",
        "fffggffFfggfFfggffffgFffffggffFggffFfgmmmmmmmmmmmmmffFggffFfggfffggF",
        "gFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffggFfffggfffFggfffg",
        "FggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgff",
        "fffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffgg",
        "ggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFf",
},file="map.bmp"},deploy={unselectables={{position={12,21},hero="HuaZhou64"},{position={12,24},hero="QiLiang64"},{position={10,23},hero="XiHouZhong64"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=10000}}
