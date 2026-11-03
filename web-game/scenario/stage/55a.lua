siege_started=false
siege_turn=0
peace_ready=false
gsupply_enabled=false
gitems={{id="medicine",name="恢复用药",hp=120,mp=0,price=120,initial=2}}
gcommanders={"ChuZhuangWang51","GongZiCe51","ShenShuShi55","ShenXi55"}
gduel_enabled=false gevents_enabled=true gduels={} gsites={}
gstory={
 chapter="第五十五回·上",title="华元登床劫子反 老人结草亢杜回",battle_title="睢阳围城",
 objective="击溃睢阳西门外守军后维持围城五回合，触发华元夜入子反土堙议和。连续城墙W不可通行，双格西门G可通行；华元、宋文公不可被击退，我方具名将领被击退则失败。",
 map_asset="m087.png",
 intro={
  {speaker="",text="楚庄王与群臣商议牵制晋国。公子侧建议攻打最依附晋国的宋国，使晋无暇再争郑。"},
  {speaker="公子婴齐",text="可遣使报聘齐国，故意不向宋国请假道。宋若杀使，楚国便有出兵之名。"},
  {speaker="",text="楚庄王命申无畏改名申舟出使。申舟知道宋人恨他，临行把儿子申犀托付给楚王。"},
  {speaker="申舟",text="为臣奉命而死本是分内，只求大王善待申犀。若我死于宋，他必请大王为父报仇。"},
  {speaker="",text="宋国关吏扣住申舟。华元认为楚使无文书过境是公然欺宋，主张将他处死。"},
  {speaker="华元",text="欺辱比受伐更可耻。楚国既存心挑衅，即使不杀此使，也迟早会来攻宋。"},
  {speaker="",text="申舟在宋廷痛骂宋君，华元命人割舌后杀死，并焚毁聘齐文书与礼物。"},
  {speaker="",text="楚庄王闻报投箸而起，立刻任公子侧为大将、申叔时为副，带申犀亲征宋国。"},
  {speaker="楚庄王",text="申舟以死奉命，寡人必守诺报仇。楼车四面逼城，迫宋国交出杀使之责！"},
  {speaker="",text="楚军围住睢阳，楼车与城墙等高。华元组织军民守城，又派乐婴齐奔晋告急。"},
  {speaker="",text="晋国伯宗认为邲败之后不能再与楚决战，只派解扬告诉宋人晋军将来，鼓励坚守。"},
  {speaker="",text="解扬在宋郊被楚军俘获。楚王逼他登楼车劝降，他却当着宋军高喊晋国大军即将来援。"},
  {speaker="解扬",text="我若对楚守信，便会对晋失信。请杀我，以证明楚国所求之信只在外国、不在臣子！"},
  {speaker="楚庄王",text="忠臣不惧死，说的正是你。放他回晋，不得加害。"},
  {speaker="",text="睢阳因解扬传话守备更坚。楚军自秋九月围到次年五月，双方相持九个月。"},
  {speaker="",text="城中粮尽，甚至易子而食、拾骨为炊，军民仍不肯投降；楚营也只剩七日粮食。"},
  {speaker="申犀",text="我父因大王之命而死，若今日退兵，岂不是失信于死者？"},
  {speaker="申叔时",text="宋人料定我军粮尽。可令士卒筑室耕田，五人攻城、五人耕作，假示长久围困。"},
  {speaker="",text="楚军沿城修建营房、轮流耕种。华元判断晋援不到、楚军又无退意，决定冒险夜入子反土堙。"},
  {speaker="军令",text="先击溃西门外宋军，再维持五回合围攻态势。不得跨越城墙或击退华元；进度完成自动触发夜间议和。"}
 },
 events={{id="suiyang_pressure",trigger="approach",position={29,17},radius=5,speaker="公子侧",text="西门守军已近！筑土堙观察城内，保持围攻，不可擅自抢掠。"}},
 victory={
  {speaker="",text="楚军持续施压五回合，城内外都已粮尽。华元夜间缒城而下，假扮谒者登上公子侧土堙。"},
  {speaker="",text="华元坐住公子侧双袖，以匕首相逼，坦言宋城已经易子而食、拾骨为炊，却绝不城下投降。"},
  {speaker="华元",text="国有已困之形，人有不困之志。楚军若退三十里，宋国愿结盟事楚。"},
  {speaker="公子侧",text="我也不欺你，楚营只剩七日粮。明日我奏请退军一舍，双方都不可失信。"},
  {speaker="",text="公子侧把实情报告楚王。庄王先怒其泄密，随后认为弱宋尚有不欺人之臣，大楚更不能反而无信。"},
  {speaker="楚庄王",text="退军三十里，与宋国结盟。申舟之仇以宋国服楚为报，不再使两国百姓相食。"},
  {speaker="",text="公子侧入城与宋文公歃血，华元送还申舟棺木并留楚为质。楚王厚葬申舟，使申犀继任大夫。"},
  {speaker="",text="华元后来与公子婴齐谈起晋楚弭兵，认为两强长期争战，终须有人居中缔结和平。"},
  {speaker="军令",text="睢阳围城完成，获得1100金币。宋国未灭，华元与公子侧均存活；下一关转入青草坡。"}
 },defeat={{speaker="",text="楚军具名将领被击退，围城攻势瓦解，无法迫使宋国议和。"}}
}
gstage={title_id="SiegeOfSuiyang55",turn_limit=26,map={blocked_edges={},size={54,36},terrain={
        "FFfffFFffgFFffgFFfgfFFfgfFFgffFFgffFFfffFFfffFFfffFFff",
        "gffFFfffFFfffFFfffFFffgFFffgFFfgfFFfgfFFgffFFgffFFfffF",
        "fFFfgfFFgffFFgffFFfffFFfffFFfffFFffgFFffgFFfgfFFfgfFFg",
        "FffgffffgfffgffffgfffgffffgfffgWWWWWWWWWWWWWWWWWWWWWWg",
        "ffFgfffgffffgfffgffffgfffgffffgWiiiiiiiiiiiiiiiiiiiiWF",
        "FFgffffgfffgffffgfffgffffgfffgfWiiiiiiiiiiiiiiiiiiiiWf",
        "ffgfffgffffgfffgffffgfffgffffgfWiiiiiiiiiiiiiiiiiiiiWF",
        "fFFfffgfffgffffgfffgffffgfffgffWiiiiiiiiiiiiiiiiiiiiWf",
        "FgfffgffffgfffgffffgfffgffffgffWiiiiiiiiiiiiiiiiiiiiWf",
        "gfFffgfffgffffgfffgffffgfffgfffWiiiiiiiiiiiiiiiiiiiiWF",
        "FFmmmmmmmmmmmmmmmmmmffgffffgfffWiiiiiiiiiiiiiiiiiiiiWf",
        "ffffgfffgffffgfffgffffgfffgffffWiiiiiiiiiiiiiiiiiiiiWF",
        "fFFgffffgfffgffffgfffgffffgfffgWiiiiiiiiiiiiiiiiiiiiWg",
        "FffgfffgffffgfffgffffgfffgffffgWiiiiiiiiiiiiiiiiiiiiWf",
        "ffFffffgfffgffffgfffgffffgfffgfWiiiiiiiiiiiiiiiiiiiiWF",
        "FFgfffgffffgfffgffffgfffgffffgfWiiiiiiiiiiiiiiiiiiiiWf",
        "fgffffgfffgffffgfffgffffgfffgffWiiiiiiiiiiiiiiiiiiiiWF",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiWf",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwGiiiiiiiiiiiiiiiiiiiiWf",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwWiiiiiiiiiiiiiiiiiiiiWF",
        "FFffgfffgffffgfffgffffgfffgffffWiiiiiiiiiiiiiiiiiiiiWg",
        "fffgffffgfffgffffgfffgffffgfffgWiiiiiiiiiiiiiiiiiiiiWF",
        "fFFgfffgffffgfffgffffgfffgffffgWiiiiiiiiiiiiiiiiiiiiWf",
        "FfgffffgfffgffffgfffgffffgfffgfWiiiiiiiiiiiiiiiiiiiiWf",
        "ffFfffgffffgfffgffffgfffgffffgfWiiiiiiiiiiiiiiiiiiiiWF",
        "FFffffgfffgffffgfffgffffgfffgffWiiiiiiiiiiiiiiiiiiiiWf",
        "mmmmmmmmmmmmmmmmmmmmfffgffffgffWiiiiiiiiiiiiiiiiiiiiWF",
        "gFFffgfffgffffgfffgffffgfffgfffWiiiiiiiiiiiiiiiiiiiiWf",
        "FfffgffffgfffgffffgfffgffffgfffWiiiiiiiiiiiiiiiiiiiiWf",
        "ffFfgfffgffffgfffgffffgfffgffffWiiiiiiiiiiiiiiiiiiiiWF",
        "FFfgffffgfffgffffgfffgffffgfffgWiiiiiiiiiiiiiiiiiiiiWg",
        "fffgfffgffffgfffgffffgfffgffffgWiiiiiiiiiiiiiiiiiiiiWF",
        "fFFffffgfffgffffgfffgffffgfffgfWiiiiiiiiiiiiiiiiiiiiWf",
        "FfgfFFgffFFgffFFfffFFfffFFfffFFWWWWWWWWWWWWWWWWWWWWWWf",
        "fgFFffgFFfgfFFfgfFFgffFFgffFFfffFFfffFFfffFFffgFFffgFF",
        "FFfffFFfffFFffgFFffgFFfgfFFfgfFFgffFFgffFFfffFFfffFFff",
    },file="map.bmp"},deploy={unselectables={{position={8,18},hero="ChuZhuangWang51"},{position={20,18},hero="GongZiCe51"},{position={12,14},hero="ShenShuShi55"},{position={12,22},hero="ShenXi55"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=11000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("HuaYuan50",1,Enum.force.enemy,{44,18});game:set_unit_invulnerable("HuaYuan50",true)
 many(game,"ChuSiegeGuard55",{{7,15},{7,21},{11,16},{11,20},{16,14},{16,22},{21,14},{21,22}},Enum.force.own)
 many(game,"ChuSiegeArcher55",{{9,12},{9,24},{15,12},{15,24},{23,15},{23,21}},Enum.force.own)
 many(game,"SongGateGuard55",{{29,16},{29,19},{32,16},{32,19},{34,17},{34,18}},Enum.force.enemy)
 many(game,"SongCityArcher55",{{33,12},{33,24},{38,14},{38,22},{46,14},{46,22}},Enum.force.enemy)
end
function on_update(game)
 if not siege_started and not game:has_unit("SongGateGuard55")then siege_started=true;siege_turn=game:get_turn_current();game:push_cmd_speak(0,"西门外防线已破，维持五回合围攻态势。")end
 if siege_started and not peace_ready and game:get_turn_current()>=siege_turn+5 then peace_ready=true;game:push_cmd_speak(0,"双方粮尽，华元今夜将潜入子反土堙议和。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)if game:get_num_commanders_alive()<#gcommanders then return Enum.status.defeat end if peace_ready then return Enum.status.victory end return Enum.status.undecided end
