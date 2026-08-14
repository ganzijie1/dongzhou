gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"ZhuFan60","YiMei60"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="jiuzi_castle",name="鸠兹城池",position={55,20},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}}}
gstory={chapter="第六十回·中",title="吴国伐楚丧邓廖",battle_title="采石水战",objective="以夷昧诱邓廖进入采石浅滩，触发余祭伏兵；击退邓廖后，诸樊接近鸠兹城池完成收复。诸樊或夷昧被击退则失败。",map_asset="m096.png",
 intro={
  {speaker="",text="楚国连年与吴国争夺东境。令尹子重死后，公子婴齐继任令尹，命司马尹齐取鸠兹，再遣邓廖率舟师深入吴境。"},
  {speaker="尹齐",text="鸠兹已下，吴军新败。邓廖率组甲三百、被练三千，乘胜东进。"},
  {speaker="邓廖",text="吴人不习大阵，只要沿水道追击，必能直抵其腹地。"},
  {speaker="",text="吴王寿梦病重，世子诸樊代掌军政。他命弟余祭设伏采石，又令弟夷昧领少量舟师诱敌。"},
  {speaker="",text="楚军组甲披重铠、被练穿练袍，水上正面列阵极为强悍；吴军因此避其锋锐，只在曲折浅滩设伏。"},
  {speaker="诸樊",text="邓廖锐气正盛，不可正面争锋。夷昧且战且退，把楚舟引入采石浅水。"},
  {speaker="夷昧",text="我只保留一条退路。楚军若追入浅滩，余祭便从后方截断深水航道。"},
  {speaker="余祭",text="伏舟藏在芦苇之后，等邓廖进入采石中央再起。过早现身，只会把他惊走。"},
  {speaker="军令",text="夷昧诱使邓廖进入采石范围，余祭伏兵才会出现。浅河可通行，深水不可跨越。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="余祭",text="楚舟已经进入采石，伏军从芦苇后尽出，截断归路！"}
 },
 victory={
  {speaker="",text="余祭伏舟齐出，吴军前后夹击。邓廖舟阵大乱，三千被练几乎尽失，邓廖被吴军生擒。"},
  {speaker="邓廖",text="败军之将，唯有一死。我受楚国厚恩，绝不降吴。"},
  {speaker="",text="邓廖不屈而死。诸樊乘胜反攻鸠兹，尹齐不能抵挡，弃城退回楚境。"},
  {speaker="",text="尹齐自愧丧师失地，归国后忧愤成疾而死。吴国经此一战，声势大振。"},
  {speaker="",text="晋悼公闻吴楚相攻，决定趁楚东顾之际，再会诸侯伐郑。诸军随后转向偪阳。"},
  {speaker="军令",text="采石水战完成，获得1300金币。下一关：偪阳之战。"}
 },
 defeat={{speaker="",text="诸樊或夷昧被击退，诱敌与反攻失去统领，本关失败。"}}
}
local ambush=false
local deng_down=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end game:appoint_hero("YuJi60",1)end
function on_begin(game)
 game:generate_unit("DengLiao60",1,Enum.force.enemy,{34,20});game:generate_unit("YinQi60",1,Enum.force.enemy,{55,20});game:set_unit_invulnerable("YinQi60",true)
 many(game,"WuMarine60",{{11,7},{15,10},{20,12},{22,16}},Enum.force.own);many(game,"WuArcher60",{{10,11},{18,9}},Enum.force.own)
 many(game,"ChuMarine60",{{30,18},{32,22},{35,17},{36,23},{40,18},{42,22},{50,18},{52,23}},Enum.force.enemy)
 many(game,"ChuRiverArcher60",{{33,16},{38,21},{44,19},{53,17},{56,23}},Enum.force.enemy)
end
function on_update(game)
 if not ambush and game:is_unit_within("DengLiao60",{28,20},2)then ambush=true;game:generate_unit("YuJi60",1,Enum.force.own,{40,25});many(game,"WuMarine60",{{38,27},{42,26},{44,24}},Enum.force.own);many(game,"WuArcher60",{{39,28},{45,25}},Enum.force.own);game:push_cmd_speak(0,"余祭伏舟尽出！前军回身夹击，截住邓廖退路！")end
 if ambush and not deng_down and not game:has_unit("DengLiao60")then deng_down=true;game:push_cmd_speak(0,"邓廖被吴军生擒，拒绝投降而死。诸樊立即向东反攻鸠兹！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if ambush and not game:has_unit("YuJi60")then return Enum.status.defeat end if deng_down and game:is_unit_within("ZhuFan60",{55,20},2)then return Enum.status.victory end return Enum.status.undecided end
gstage={title_id="CaishiBattle60",turn_limit=28,map={blocked_edges={},size={62,40},terrain={
        "~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~WWWWWWWWWWWWWW~",
        "~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~WiiiiiiiiiiiiW~",
        "~~~~~~~~~fffffgggvvvvvvvvvvvvvvgvvvvgvvvvgvf~~~WiiiiiiiiiiiiW~",
        "~~~~~~~~~~fffffgggvvvvvvvvvvvvgvvvvgvvvvgvvff~~WiiiiiiiiiiiiW~",
        "~~~~~~~~~~fffffgggvvvvvvvvvvvgvvvvgvvvvgvvvff~~WiiiiiiiiiiiiW~",
        "~~~~~~~~~~~fffffgggvvvvvvvvvgvvvvgvvvvgvvvvfff~WiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~fffffgggvvvvvvvvvvvvgvvvvgvvvvgffffWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~fffffgggvvvvvvvvvvvgvvvvgvvvvgvffffGiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~fffffgggvvvvvvvvvgvvvvgvvvvgvvffffGiiiiiiiCiiiiW~",
        "~~~~~~~~~~~~~fffffgggvvvvvvvvgvvvvgvvvvgvvvffffWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~fffffgggvvvvvvgvvvvgvvvvgvvvvgfffWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~fffffgggvvvvvvvvvgvvvvgvvvvgggffWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~fffffgggvvvvvvvvgvvvvgvvvvgvggffWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~~fffffgggvvvvvvgvvvvgvvvvgvvgggfWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~~~fffffgggvvvvgvvvvgvvvvgvvvvgggWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggWiiiiiiiiiiiiW~",
        "~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvggWWWWWWWWWWWWWW~",
        "~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~~~fffffgggvvvvvvvvvvvvvvvvvvvgggfffff~~",
    },file="map.bmp"},deploy={unselectables={{position={18,12},hero="ZhuFan60"},{position={24,20},hero="YiMei60"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=13000}}
