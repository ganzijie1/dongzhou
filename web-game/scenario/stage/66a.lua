gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"SunKuai61","YongChu65"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={}
gstory={chapter="第六十六回·上",title="杀宁喜子鱄出奔 戮崔杼庆封独相",battle_title="圉村伏殖绰",objective="诱殖绰进入陷坑并击退。",map_asset="m111.png",
 intro={
  {speaker="",text="殖绰率卫国千人袭杀茅氏三百晋卒。孙林父命孙蒯、雍鉏回击，二人忌惮殖绰勇力，决定设伏。"},
  {speaker="雍鉏",text="我只带百人诈败，把殖绰引往圉村；将军在土山下掘坑覆草，以言语激他驱车上山。"},
  {speaker="孙蒯",text="殖绰若带全军，不可力敌；他恃勇轻追，进入村口两格陷坑后弓弩齐发。"},
  {speaker="殖绰",text="擒得孙蒯，便如擒半个孙林父。区区土山，驱车直上！"},
  {speaker="军令",text="雍鉏诱殖绰进入圉村陷坑，解除其保护后击退。孙蒯、雍鉏任一被击退均失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="雍鉏",text="殖绰已追入林道，继续向圉村诱敌！"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="孙蒯",text="坑上覆草已破，弓弩齐发！"}
 },
 victory={
  {speaker="",text="殖绰轻车追至圉村，被孙蒯辱骂激怒，驱车上坡时马车陷入覆草深坑。"},
  {speaker="",text="孙氏伏弩齐发，殖绰死于坑中。孙蒯斩其首级，杀散卫军，却向晋国隐瞒胜讯。"},
  {speaker="",text="晋平公因三百戍卒被杀而囚卫献公；晏婴、羊舌肸力谏，献公与宁喜献女乐后获释。"},
  {speaker="军令",text="圉村伏殖绰完成，获得800金币。下一关：宁府诛喜。"}
 },
 defeat={{speaker="",text="孙蒯或雍鉏被击退，或超过二十回合，失败。"}}
}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
local trapped=false
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)game:generate_unit("ZhiChuo62",1,Enum.force.enemy,{17,20});game:set_unit_invulnerable("ZhiChuo62",true);many(game,"WeiRaider66",{{14,16},{14,19},{14,23},{18,16},{18,24}},Enum.force.enemy);many(game,"SunAmbusher66",{{43,15},{45,19},{44,23},{39,15},{39,24}},Enum.force.own)end
function on_update(game)if not trapped and game:is_unit_within("ZhiChuo62",{41,19},1)then trapped=true;game:set_unit_invulnerable("ZhiChuo62",false);game:push_cmd_speak(0,"殖绰车马坠入陷坑，伏弩齐发！")end end function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if trapped and not game:has_unit("ZhiChuo62")then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="YuVillageTrap66",turn_limit=20,map={blocked_edges={},size={56,40},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgfff",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFf",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffg",
        "fggffFggffFfggffffgFfffggfffFggffFfggfffggFfffggfffFggff",
        "fffgFfffggfffFggffffggFffggFfFFffFFfFFffFFfFFffFFfFFffgg",
        "gffffggFffggffffFgfffFggfffgFffFFfFFffFFfFFffFFfFFfffFff",
        "fFgffffggfFfggfFffggffffFgfffFFfFFffFFfFFffFFfFFffFFggff",
        "fffgFffffFgfffggffFfggffffgFFfFFffFFfFFffFFfFFffFFfFffgF",
        "gffFfggffffgFfffggfffFggffFfFFffFFfFFffFFfFFffFFfFFfffff",
        "fggfffFggffffggFffggFfffggffffFFfFFffFFfFFffFFfFFffFFgff",
        "FffggffffFgfffFggfffggfFffggFFfFFffFFfFFffFFfFFffFFfffgF",
        "ggfFfggfFffggffffFgfffggffFffFFffFFfFFffFFfFFffFFfFFgfFf",
        "ffFgfffggffFfggffffgFfffgFffFffFFfFFffFFfFFffFFfFFfffggf",
        "ffffgFfffggfffFggffFfggfffggfFFfFFffffffffffffffffFFfffg",
        "ggffffggFffggFfffggfffFggfffFfFFffFfffffffffffffFFfFgfFf",
        "ffFgfffFggfffggfFffggffffFgfFFffFFfffffffffffffffFFffFgf",
        "fFffggffffFgfffggffFfggfFffgffFFfFFfffffffffffffFffFfffg",
        "ggffFfggffffgFfffgFffffggffFFFfFFffffffffffffffffFFfgfff",
        "ffggfffFggffFfggfffggFfffggffFFffFFfffffffffffffFfFFfFgf",
        "gFffggFfffggfffFggfffggfFffgFffFFfFfffffffffffffFFffFffg",
        "FggfffggfFffggffffFgfffFgffffFFfFFffffffffffffffffFFggfF",
        "fffFgfffggffFfggfFffggfffgFfFfFFffFfffffffffffffFFfFffgg",
        "gffffgFfffgFffffggffFfggfffgFFffFFfffffffffffffffFFfFfff",
        "FggffFfggfffggFfffggfffFggffffFFfFFfffffffffffffFffFggff",
        "fffggfffFggfffggfFffggFfffggFFfFFffffffffffffffffFFfffFg",
        "gfFffggffffFgfffFgffffggfFfffFFffFFfffffffffffffFfFFffff",
        "fggffFfggfFffggfffgFffffggffFffFFfFfffffffffffffFFffggff",
        "fffgFffffggffFfggfffggFfffgFfFFfFFffFFfFFffFFfFFffFFffgg",
        "ggfffggFfffggfffFggffFggffffFfFFffFFfFFffFFfFFffFFfFgFff",
        "fFggfffggfFffggFfffggfffFgffFFffFFfFFffFFfFFffFFfFFffggf",
        "ffffFgfffFgffffggfFffggfffgFffFFfFFffFFfFFffFFfFFffFfffF",
        "ggfFffggfffgFffffggffFfggfFfFFfFFffFFfFFffFFfFFffFFfgfff",
        "ffggffFfggfffggFfffgFffffggffFFffFFfFFffFFfFFffFFfFFFggf",
        "FfffggfffFggffFggffffggFfffgFffFFfFFffFFfFFffFFfFFfffffF",
        "ggfFffggFfffggfffFgffffggfFffFFfFFffFFfFFffFFfFFffFFgfFf",
        "ffFgffffggfFffggfffgFffffFgfFfFFffFFfFFffFFfFFffFFfFfggf",
        "gfffgFffffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffg",
        "fggfffggFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFf",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFgg",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffff",
},file="map.bmp"},deploy={unselectables={{position={46,17},hero="SunKuai61"},{position={31,22},hero="YongChu65"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=8000}}
