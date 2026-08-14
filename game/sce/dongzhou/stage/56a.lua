relief_arrived=false
gsupply_enabled=false gitems={{id="medicine",name="恢复用药",hp=120,mp=0,price=120,initial=2}}
gcommanders={"SunLiangFu56"} gduel_enabled=false gevents_enabled=true gduels={} gsites={}
gstory={chapter="第五十六回·上",title="萧夫人登台笑客 逢丑父易服免君",battle_title="新筑夜袭",
 objective="孙良夫进入齐军空营后遭国佐、高固合围。坚持到第三回合，石稷与仲叔于奚从东面赶到；随后让孙良夫抵达东侧出口（45，16）即可突围。孙良夫被击退则失败。",map_asset="m089.png",
 intro={
  {speaker="",text="郤雍依靠察言观色捕盗，三日之内便被数十名群盗合攻杀死。荀林父忧愤成疾，也随之去世。"},
  {speaker="羊舌职",text="察见渊鱼者不祥。以一人之智压制群盗，终究敌不过群盗合力。弭盗应当教化人心，而非只求多捕。"},
  {speaker="",text="晋景公依羊舌职建议重用士会。士会删除苛刻捕盗条令，尊崇善人、推行教化，晋国盗患自然消散。"},
  {speaker="",text="士会受周天子赐黻冕，担任中军元帅兼太傅，改封于范，成为范氏始祖。"},
  {speaker="",text="晋国为了恢复霸业，派郤克出使鲁、齐。鲁国季孙行父、卫国孙良夫、曹国公子首也先后来到齐国。"},
  {speaker="",text="齐顷公见四位使者分别眇、秃、跛、驼，竟挑选相同缺陷的御者驾车，让母亲萧夫人在崇台观看取笑。"},
  {speaker="国佐",text="朝聘是国家大礼，宾主应以敬相待，不能拿使臣身体缺陷取乐。"},
  {speaker="",text="齐顷公不听。台上妇女笑声传到车下，四国使臣确认受到刻意羞辱，当夜歃血相盟，誓言伐齐。"},
  {speaker="郤克",text="我等好意修聘，反被齐国供妇人观笑。若不报此仇，非丈夫也！"},
  {speaker="",text="鲁宣公病逝，季孙氏拥立十三岁的鲁成公，驱逐东门氏。楚庄王也在旅途中病逝，十岁的楚共王即位。"},
  {speaker="",text="齐顷公得知鲁晋谋齐，先发兵攻破鲁国龙邑，为宠臣卢蒲就魁之死屠杀城北军民，随后回军迎击卫国。"},
  {speaker="石稷",text="我军原想乘齐军在鲁国时侵境，如今齐侯已经回师，不可轻敌。不如暂让归路，等待晋鲁合兵。"},
  {speaker="孙良夫",text="齐侯辱我跛足，今日仇人在前，怎能不战？今夜直劫齐营！"},
  {speaker="",text="齐军早有防备，故意留下空营。孙良夫率中军冲入营门后，国佐、高固从左右包围，齐侯亲率大军掩至。"},
  {speaker="军令",text="从空营东门寻找突围路线，坚持三回合等待石稷与仲叔于奚援军；援军到达后让孙良夫抵达（45，16）。"}
 },events={{id="empty_camp",trigger="approach",position={23,16},radius=3,speaker="孙良夫",text="营中无人，这是空营！全军转向东门，准备突围！"}},
 victory={
  {speaker="",text="孙良夫冲出空营时被国佐、高固夹击，幸得宁相、向禽两队车兵接应，且战且退。"},
  {speaker="石稷",text="元帅只管前行，我率本部断后。不要与齐军纠缠！"},
  {speaker="",text="石稷挡住追兵，仲叔于奚又率新筑百余乘赶到。齐侯担心深入卫境后兵力不继，鸣金收军。"},
  {speaker="孙良夫",text="我本欲报齐，反为所败，无颜回国。暂驻新筑，我亲往晋国请兵，生缚齐君方雪此耻！"},
  {speaker="",text="孙良夫与鲁国臧孙许在晋国共同请师。郤克主张发八百乘，晋景公终于同意联军伐齐。"},
  {speaker="军令",text="新筑夜袭完成，获得700金币。齐卫具名将领均按撤退处理；下一关进入鞌之战。"}
 },defeat={{speaker="",text="孙良夫在齐军空营内被击退，卫军失去主将，无法撤回新筑。"}}}
gstage={title_id="NightRaidAtXinzhu56",turn_limit=18,map={blocked_edges={},size={48,32},terrain={
        "FFffFFffFFffFFffFFffFFffFFffFFffFFffFFmmFFmmFFmm",
        "gfFFgfFFgfFFgfFFgfFFgfFFgfFFgfFFgfFFgfFFmmFFmmFF",
        "FFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFmmFFmmFFmm",
        "ffFgfffgfffgfffgfffgfffgfffgfffgfffgffmmmmmmmmFF",
        "FFgfffgfffgfffgfffgfffgfffgfffgfffgfffmmmmmmmFmm",
        "ffFfffgfffgfffgfffgfffgfffgfffgfffgfffmmmmmmmmFF",
        "FFfffgfffgfffgfffgfffgfffgfffgfffgfffgmmmmmmmFmm",
        "fgFffgfffgfffgPPPPPPPPPPPPPPPPPPPgfffgmmmmmmmmFF",
        "FFffgfffgfffgfPfgfffgfffgfffgfffPfffgfmmmmmmmFmm",
        "gfFfgfffgfffgfPfgfffgfffgfffgfffPfffgfffgfffgfFF",
        "FFfgfffgfffgffPgfffgfffgfffgfffgPffgfffgfffgfFfg",
        "ffFgfffgfffgffPgfffgfffgfffgfffgPffgfffgfffgffFF",
        "FFgfffgfffgfffPfffgfffgfffgfffgfPfgfffgfffgffFgf",
        "ffFfffgfffgfffPfffgfffgfffgfffgfPfgfffgfffgfffFF",
        "FFfffgfffgfffgPffgfffgfffgfffgffPgfffgfffgfffFff",
        "wwwwwwwwwwwwwwPwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwPwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwPwwwwwwwwwwwwwwwwwPwwwwwwwwwwwwwww",
        "FFfgfffgfffgffPgfffgfffgfffgfffgPffgfffgfffgfFfg",
        "ffFgfffgfffgffPgfffgfffgfffgfffgPffgfffgfffgffFF",
        "FFgfffgfffgfffPfffgfffgfffgfffgfPfgfffgfffgffFgf",
        "ffFfffgfffgfffPfffgfffgfffgfffgfPfgfffgfffgfffFF",
        "FFfffgfffgfffgPffgfffgfffgfffgffPgfffgfffgfffFff",
        "fgFffgfffgfffgPffgfffgfffgfffgffPgfffgfffgfffgFF",
        "FFffgfffgfffgfPfgfffgfffgfffgfffPfffgfffgfffgFff",
        "gfFfgfffgfffgfPPPPPPPPPPPPPPPPPPPfffgfffgfffgfFF",
        "FFfgfffgfffgfffgfffgfffgfffgfffgfffgfffgfffgfFfg",
        "ffFgfffgfffgfffgfffgfffgfffgfffgfffgfffgfffgffFF",
        "FFgfffgfffgfffgfffgfffgfffgfffgfffgfffgfffgffFgf",
        "ffFFffFFffFFffFFffFFffFFffFFffFFffFFffFFffFFffFF",
        "FFffFFffFFffFFffFFffFFffFFffFFffFFffFFffFFffFFff",
        "fgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFFfgFF",
    },file="map.bmp"},deploy={unselectables={{position={23,16},hero="SunLiangFu56"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=7000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("SunLiangFu56",1)end
function on_begin(game)
 game:generate_unit("GuoZuo56",1,Enum.force.enemy,{10,12});game:generate_unit("GaoGu56",1,Enum.force.enemy,{10,21});game:set_unit_invulnerable("GuoZuo56",true);game:set_unit_invulnerable("GaoGu56",true)
 many(game,"WeiRaidGuard56",{{20,14},{20,18},{23,13},{23,19},{26,14},{26,18}},Enum.force.own)
 many(game,"QiAmbushGuard56",{{12,10},{12,22},{9,15},{9,18},{17,5},{17,27}},Enum.force.enemy)
 many(game,"QiAmbushCavalry56",{{7,8},{7,24},{15,9},{15,23}},Enum.force.enemy)
end
function on_update(game)if not relief_arrived and game:get_turn_current()>=3 then relief_arrived=true;game:generate_unit("ShiJi56",1,Enum.force.ally,{42,13});game:generate_unit("ZhongShuYuXi56",1,Enum.force.ally,{42,19});many(game,"WeiReliefGuard56",{{40,11},{40,21},{44,14},{44,18}},Enum.force.ally);game:push_cmd_speak(0,"石稷与仲叔于奚援军抵达东面，孙良夫立即突围！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if game:get_num_commanders_alive()<#gcommanders then return Enum.status.defeat end if relief_arrived and game:is_unit_within("SunLiangFu56",{45,16},1)then return Enum.status.victory end return Enum.status.undecided end
