grass_triggered=false
gsupply_enabled=false gitems={{id="medicine",name="恢复用药",hp=120,mp=0,price=120,initial=2}}
gcommanders={"WeiKe55","WeiQi54"} gduel_enabled=false gevents_enabled=true gduels={} gsites={}
gstory={chapter="第五十五回·下",title="华元登床劫子反 老人结草亢杜回",battle_title="青草坡之战",
 objective="魏颗诱杜回进入青草坡中心（24，18）周围三格，触发老人结草后杜回才可被击退；击退杜回即生擒并按原著处斩。魏颗、魏锜被击退则失败。",map_asset="m088.png",
 intro={
  {speaker="",text="晋景公本欲救宋，却收到赤狄潞国密书。国相酆舒专权，逼潞君缢杀晋景公之妹伯姬。"},
  {speaker="",text="晋国命荀林父为大将、魏颗为副，出车三百乘伐潞。酆舒在曲梁战败逃往卫国，被卫君擒送晋军。"},
  {speaker="",text="晋军杀酆舒、灭潞国，又留下魏颗平定赤狄土地。秦桓公派勇将杜回来争夺潞地。"},
  {speaker="",text="杜回力能举千钧，手持一百二十斤开山大斧，带三百刀斧手步行冲阵，专砍车马与甲将。"},
  {speaker="魏颗",text="秦军不用战车，专从车轮马足间突入。晋军先闭营坚守，不可与杜回正面角力。"},
  {speaker="",text="杜回在营外挑战三日。魏锜率援军到来，不信杜回勇力，擅自出战，又被刀斧手击败。"},
  {speaker="魏锜",text="此人确实不是寻常勇士。若再正面接战，战车转折不便，仍会被他斩断马足。"},
  {speaker="",text="当夜魏颗梦中两次听到“青草坡”三字，决定由自己诱敌，命魏锜先到坡地两侧埋伏。"},
  {speaker="魏颗",text="拔营佯退，把杜回引到青草坡。伏兵只截其部众，不要急着围攻主将。"},
  {speaker="杜回",text="晋军已经胆破！三百刀斧手随我追击，不擒二魏誓不回秦！"},
  {speaker="军令",text="先诱杜回到（24，18）周围三格。触发结草前杜回不可被击退；触发后集中攻击将其生擒。"}
 },events={{id="grass_knot",trigger="approach",position={24,18},radius=3,speaker="魏颗",text="坡中老人正在挽结青草！杜回脚步已乱，伏兵合围！"}},
 victory={
  {speaker="",text="杜回进入坡心后忽然一步一跌，仿佛有人用青草缠住双足，百余斤大斧再也施展不开。"},
  {speaker="",text="魏颗、魏锜双车并进，两戟将杜回刺倒生擒。秦国刀斧手失去主将，四散奔逃。"},
  {speaker="杜回",text="我双足像被什么攀住，不能移动，这是天绝我命，并非力不如人！"},
  {speaker="",text="魏颗担心杜回绝力难制，当场将他处斩，解送稷山请功。"},
  {speaker="",text="当夜老人入梦，自称祖姬之父。魏颗当年遵父亲清醒时的遗命，将祖姬改嫁，没有以她殉葬。"},
  {speaker="老人",text="将军从治命、不从乱命，救我女儿一命。我在九泉结草相报，助你成此军功。"},
  {speaker="",text="晋景公封魏颗于令狐，铸景钟记功，又命士会攻灭甲氏、留吁、铎辰，赤狄土地尽归晋国。"},
  {speaker="",text="晋国随后遭遇饥荒与盗患。荀林父任用善察神色的郤雍捕盗，盗贼反而越来越多。"},
  {speaker="羊舌职",text="盗未捕尽，郤雍的死期却已近了。只凭神色逼迫市人，迟早会招来群盗合谋报复。"},
  {speaker="军令",text="青草坡之战完成，获得1000金币。杜回按原著被俘后处斩；第五十五回剧情完成。"}
 },defeat={{speaker="",text="魏颗或魏锜被击退，杜回冲破青草坡伏兵，晋军再次败退。"}}}
gstage={title_id="BattleOfQingcaoSlope55",turn_limit=22,map={blocked_edges={},size={48,32},terrain={
        "FFffwwgwwgwwgwffFFgfFFffFFffFFgfFFffFFffFFgfFFff",
        "fFFfwgwwgwwgwwFffFFffFFgfFFffFFffFFgfFFffFFffFFg",
        "ffFFgwwgwwgwwgFFgfFFffFFffFFgfFFffFFffFFgfFFffFF",
        "FffgwwgwwgwwgwfgfffffgfffffgfffffgfffffgfffffgfF",
        "FFgfwgwwgwwgwwgfffffgfffffgfffffgfffffgfffffgFff",
        "fFFfgwwgwwgwwgfffffgfffffgfffffgfffffgfffffgfFFf",
        "gfFfwwgwwgwwgwffffgfffffgfffffgfffffgfffffgfffFF",
        "FfffwgwwgwwgwwfffgfffffgfffffgfffffgfffffgfffffF",
        "FFffgwwgwwgwwgffgfffffgfffffgfffffgfffffgffffFgf",
        "fFFgwwgwwgwwgwfgfffffgfffffgfffffgfffffgfffffFFf",
        "ffFfffffgfffffgfffffgfffffgfffffgfffffgfffffgfFF",
        "FgfffffgfffffgfffffgfffffgfffffgfffffgfffffgfffF",
        "FFffffgfffffgfffffgfffffgfffffgfffffgfffffgffFff",
        "fFFffgfffffgfffffgfffffgfffffgfffffgffffwwwwwwww",
        "ffFfgfffffgfffffgfffffgfffffgfwwwwwwwwwwwwwwwwww",
        "Fffgfffffggggggggggggggggggggggggggggggwwwwwwwww",
        "FFgfffffgfgggggggggggggggggggggggggggggwffffgFff",
        "wwwwwwwwwwgggggggggggggggggggggggggggggffffgfFFf",
        "wwwwwwwwwwgggggggggggggggggggggggggggggfffgfffFF",
        "wwwwwwwwwwgggggggggggggggggggggggggggggffgfffffF",
        "FFffgfffffgggggggggggggggggggggggggggggfgffffFgf",
        "fFFgfffffgfffffgfffffgfffffgfffffgfffffgfffffFFf",
        "ffFfffffgfffffgfffffgfffffgfffffgfffffgfffffgfFF",
        "FgfffffgfffffgfffffgfffffgfffffgfffffgfffffgfffF",
        "FFffffgfffffgfffffgfffffgfffffgfffffgfffffgffFff",
        "FFFFfFffFfFgfFfFfgFfFffFfFffFgFffFfFffFfFgfFfFFg",
        "FfFfgFfFffFfFffFgFffFfFffFfFgfFfFfgFfFffFfFffFFF",
        "FfFgFffFfFffFfFgfFfFfgFfFffFfFffFgFffFfFffFfFgfF",
        "FFgfFfFfgFfFffFfFffFgFffFfFffFfFgfFfFfgFfFffFFFf",
        "fFFFfFFgFFFFfFFfFFFgfFFFfFFfFFFFfFFfFFFffFFFfFFf",
        "FfFFfFFFFfFFgFFFffFFFfFFgFFFFfFFfFFFgfFFFfFFfFFF",
        "FfFFFFfFFfFFFffFFFfFFfFFFFfFFgFFFffFFFfFFgFFFFfF",
    },file="map.bmp"},deploy={unselectables={{position={8,18},hero="WeiKe55"},{position={10,22},hero="WeiQi54"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=10000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("DuHui55",1,Enum.force.enemy,{39,17});game:set_unit_invulnerable("DuHui55",true)
 many(game,"JinAmbushGuard55",{{6,15},{6,21},{9,14},{9,24},{13,13},{13,25}},Enum.force.own)
 many(game,"JinAmbushArcher55",{{4,17},{4,23},{12,16},{12,22}},Enum.force.own)
 many(game,"QinAxeGuard55",{{36,14},{36,20},{39,14},{39,20},{42,15},{42,19}},Enum.force.enemy)
 many(game,"QinGuard55",{{34,17},{37,22},{41,12},{44,17}},Enum.force.enemy)
end
function on_update(game)if not grass_triggered and game:is_unit_within("DuHui55",{24,18},3)then grass_triggered=true;game:set_unit_invulnerable("DuHui55",false);game:push_cmd_speak(0,"老人结草绊住杜回，立即合围生擒！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if game:get_num_commanders_alive()<#gcommanders then return Enum.status.defeat end if grass_triggered and not game:has_unit("DuHui55")then return Enum.status.victory end return Enum.status.undecided end
