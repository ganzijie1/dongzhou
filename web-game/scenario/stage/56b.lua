encirclement=false
gsupply_enabled=false gitems={{id="medicine",name="恢复用药",hp=120,mp=0,price=120,initial=2}}
gcommanders={"XiKe56","HanJue48","JiSunXingFu56","SunLiangFu56"} gduel_enabled=false gevents_enabled=true gduels={} gsites={}
gstory={chapter="第五十六回·下",title="萧夫人登台笑客 逢丑父易服免君",battle_title="鞌之战",
 objective="击破齐中军战车后，韩厥抵达华不注山南侧（42，23）周围四格触发合围；随后击退逢丑父，判定误擒齐侯并获胜。齐顷公不可被击退；我方具名将领被击退则失败。",map_asset="m090.png",
 intro={
  {speaker="",text="晋景公准郤克发兵八百乘，士燮统上军、栾书统下军、韩厥任司马，鲁卫曹军在新筑会合。"},
  {speaker="",text="齐顷公得知联军将至，亲选五百乘，三日三夜驰行五百余里，在鞌地扎营。"},
  {speaker="高固",text="齐晋从未正面交兵，请让我单车探营，看看晋军究竟有多少勇士。"},
  {speaker="",text="高固闯入晋垒，以巨石击倒晋将，又跳上对方战车把人和车一同带回齐营，自称出卖余勇。"},
  {speaker="齐顷公",text="晋军虽多，能战者少。明日寡人亲乘金舆冲阵，弓手随马足所向齐射！"},
  {speaker="",text="国佐率齐右军挡鲁，高固率左军挡卫曹。齐侯亲率中军，以箭雨直冲晋阵。"},
  {speaker="",text="御者解张手肘连中两箭，鲜血染轮；郤克也被射中左胁，血流到鞋，鼓声一度放缓。"},
  {speaker="解张",text="中军旗鼓是三军耳目。伤还未死，便必须继续前进，不能让鼓声停下！"},
  {speaker="郤克",text="援枹击鼓！我军尚能战，诸军随中军压上！"},
  {speaker="",text="郤克负伤继续击鼓，解张冒箭驱车，郑丘缓持笠护主。晋军以为中军得胜，争先冲击，齐军开始败退。"},
  {speaker="韩厥",text="元帅暂歇，我去追齐侯金舆！各军封住华不注山道路，不可让齐君脱身。"},
  {speaker="逢丑父",text="主公快把锦袍绣甲给我，换穿车右衣服。若有不测，臣愿代君受患。"},
  {speaker="军令",text="先击破齐中军战车，再让韩厥接近华不注山南侧触发包围。击退逢丑父即可，不得击退齐顷公。"}
 },events={{id="huabuzhu_encircle",trigger="approach",position={42,23},radius=4,speaker="韩厥",text="金舆就在山前！五路合围，生擒齐侯！"}},
 victory={
  {speaker="",text="逢丑父与齐顷公换衣，齐侯假扮车右。韩厥追到马首，把穿锦袍者认作齐侯。"},
  {speaker="韩厥",text="寡君不能拒绝鲁卫请求，命我军问罪上国。请君侯屈驾晋营！"},
  {speaker="",text="逢丑父假称口渴，命换装的齐侯到华泉取水，又故意嫌浑要求重取。齐侯借机绕山逃走。"},
  {speaker="",text="韩厥把逢丑父献给郤克，才发现并非齐侯。郤克原想以欺军罪处斩，听见丑父临刑呼喊后将其释放。"},
  {speaker="逢丑父",text="我为君主免除危难，今日却要因此被杀。此后天下再不会有代君受患的臣子了！"},
  {speaker="郤克",text="尽忠于君本是义行，杀你不祥。解开绑缚，让后车载你同行。"},
  {speaker="",text="齐顷公逃回本营后又三次乘轻车进入晋阵寻找丑父，国佐、高固劝他退守临淄等待楚援。"},
  {speaker="",text="晋鲁卫曹联军长驱进入齐境，烧毁关隘，直逼临淄。齐国如何求和，留待下一回分解。"},
  {speaker="军令",text="鞌之战完成，获得1400金币。齐顷公与逢丑父均存活，逢丑父按被俘后释放处理。"}
 },defeat={{speaker="",text="联军具名将领在鞌地被击退，齐军箭阵压垮晋中军。"}}}
gstage={title_id="BattleOfAn56",turn_limit=30,map={blocked_edges={},size={60,38},terrain={
        "FFfffFFffgFFfffFFfggFFfffFFggfFFfffFFgffFFfffFFfffFFffgFFfff",
        "ffFFfffFFfffFFffgFFfffFFfggFFfffFFggfFFfffFFgffFFfffFFfffFFf",
        "FfffFFgffFFfffFFfffFFffgFFfffFFfggFFfffFFggfFFfffFFgffFFfffF",
        "fFFggfffffffggfffffffggfffffffggfffffffggfffffffggfffffffFgf",
        "fggfffffffggfffffffggfffffffggffffffrrmmmrrmmmrrmmfffffggfFF",
        "FFffffffggfffffffggfffffffggfffffffgrmmmrrmmmrrmmmfffggfffff",
        "ffFfffggfffffffggfffffffggfffffffggfmmmrrmmmrrmmmrfggffffFFf",
        "FfffggfffffffggfffffffggfffffffggfffmmrrmmmrrmmmrrgfffffffgF",
        "fFFgfffffffggfffffffggfffffffggfffffmrrmmmrrmmmrrmffffffgFff",
        "ggfffffffggfffffffggfffffffggfffffffrrmmmrrmmmrrmmffffggffFF",
        "FFfffffggfffffffggfffffffggfffffffggrmmmrrmmmrrmmmffggffffff",
        "ffFffggfffffffggfffffffggfffffffggffmmmrrmmmrrmmmrggfffffFFg",
        "FffggfffffffggfffffffggfffffffggffffmmrrmmmrrmmmrrfffffffggF",
        "fFFfffffffggfffffffggfffffffggffffffmrrmmmrrmmmrrmfffffggFff",
        "gfffffffggfffffffggfffffffggfffffffgrrmmmrrmmmrrmmfffggfffFF",
        "FFffffggfffffffggfffffffggfffffffggfrmmmrrmmmrrmmmfggfffwwww",
        "ffFfggfffffffggfffffffggfffffffggfffmmmrrmmmrrmmmrwwwwwwwwww",
        "Ffggfffffffggfffffffggffffffwwwwwwwwmmrrmmmrrmmmrrwwwwwwwwww",
        "gFFffffffggfffwwwwwwwwwwwwwwwwwwwwwwmrrmmmrrmmmrrmwwwwwwfFff",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrmmmrrmmmrrmmffggffffFF",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwffffggffrmmmrrmmmrrmmmggfffffffg",
        "wwwwwwwwwwwwwwfffffffggfffffffggfffffffggfwwwwwfggfffffffFFf",
        "FggfffffffggfffffffggfffffffggfffffffggfffwwwwwgfffffffggffF",
        "gFFfffffggfffffffggfffffffggfffffffggfffffwwwwwffffffggffFff",
        "ffffffggfffffffggfffffffggfffffffggfffffffwwwwwffffggfffffFF",
        "FFffggfffffffggfffffffggfffffffggfffffffggfffffffggfffffffgg",
        "ffFgfffffffggfffffffggfffffffggfffffffggfffffffggfffffffgFFf",
        "FgfffffffggfffffffggfffffffggfffffffggfffffffggfffffffggfffF",
        "fFFffffggfffffffggfffffffggfffffffggfffffffggfffffffggfffFff",
        "FfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFF",
        "FFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgF",
        "fFFFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFFF",
        "FfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFF",
        "FFFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFFFf",
        "fFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFgFfFfFfFfFgFfFfFfFFF",
        "FFgFfFFFfFFFgFfFFFfFFFfFfFFFfFFFfFfFFFgFFFfFfFFFgFFFfFfFFFfF",
        "FgFFFfFFFgFfFFFfFFFgFfFFFfFFFfFfFFFfFFFfFfFFFgFFFfFfFFFgFFFf",
        "FfFfFFFgFFFfFfFFFgFFFfFfFFFfFFFfFfFFFfFFFfFgFFFfFFFfFgFFFfFF",
    },file="map.bmp"},deploy={unselectables={{position={10,19},hero="XiKe56"},{position={12,16},hero="HanJue48"},{position={8,14},hero="JiSunXingFu56"},{position={8,24},hero="SunLiangFu56"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=14000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("QiQingGong56",1,Enum.force.enemy,{48,19});game:generate_unit("FengChouFu56",1,Enum.force.enemy,{46,21});game:generate_unit("GuoZuo56",1,Enum.force.enemy,{50,12});game:generate_unit("GaoGu56",1,Enum.force.enemy,{50,27});game:set_unit_invulnerable("QiQingGong56",true);game:set_unit_invulnerable("GuoZuo56",true);game:set_unit_invulnerable("GaoGu56",true)
 many(game,"JinCoalitionGuard56",{{9,17},{9,21},{13,18},{13,22},{16,16},{16,24},{19,18},{19,22}},Enum.force.own)
 many(game,"JinCoalitionArcher56",{{7,11},{7,27},{14,13},{14,26},{20,14},{20,26}},Enum.force.own)
 many(game,"QiCenterChariot56",{{35,16},{39,19},{39,22},{43,15},{43,23},{47,16},{47,23}},Enum.force.enemy)
 many(game,"QiArcher56",{{41,12},{41,26},{45,13},{45,25},{51,16},{51,22}},Enum.force.enemy)
end
function on_update(game)if not encirclement and not game:has_unit("QiCenterChariot56")and game:is_unit_within("HanJue48",{42,23},4)then encirclement=true;game:push_cmd_speak(0,"韩厥已经合围金舆，击退穿锦袍的逢丑父！")end end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if game:get_num_commanders_alive()<#gcommanders then return Enum.status.defeat end if encirclement and not game:has_unit("FengChouFu56")then return Enum.status.victory end return Enum.status.undecided end
