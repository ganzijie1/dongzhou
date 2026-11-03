medicine_bag_warning=false
handoff_warning=false
gate_warning=false
gsupply_enabled=false
gitems={{id="medicine",name="恢复用药",hp=120,mp=0,price=120,initial=2}}
gcommanders={"PalaceDoctor57","HanJue48"}
gduel_enabled=false gevents_enabled=true gduels={} gsites={}
gstory={chapter="第五十七回",title="娶夏姬巫臣逃晋 围下宫程婴匿孤",battle_title="藏孤出宫",
 objective="护送乔装医者携赵武由新绛宫城东侧双格宫门出城，并抵达东侧接应处（44，15）。医者或韩厥被击退均失败；屠岸贾不可被击退，宫中搜卒被击退按撤退处理。",
 map_asset="m091.png",
 intro={
  {speaker="",text="鞌之战后，晋、鲁、卫、曹联军进抵袁娄。齐顷公急遣国佐求和，愿归还侵占鲁、卫的田地。"},
  {speaker="国佐",text="齐国愿以纪甗、玉磬为礼，并归还汶阳之田与卫国故地，只求诸军止兵。"},
  {speaker="郤克",text="若要议和，先使萧同叔子来晋为质；齐国田亩也须改作东西沟洫，便利晋军车马。"},
  {speaker="国佐",text="萧同叔子是齐君之母，岂能受辱为质？田亩沟洫顺应地势，怎可为了外国战车尽改旧制！"},
  {speaker="国佐",text="齐国虽败，还有余众。若晋国执意相逼，寡君愿再战一次、两次，直到三次，绝不屈服！"},
  {speaker="季孙行父",text="逼人太甚，反会使齐国上下同心死战。既能取回失地，便应留下转圜余地。"},
  {speaker="孙良夫",text="卫国只求故地，不愿因苛刻条件再起大战。请元帅撤去辱母与改田两项。"},
  {speaker="",text="郤克听从鲁、卫二卿劝谏，与国佐盟于袁娄。齐国归还土地、朝聘晋国，联军遂撤。"},
  {speaker="",text="晋景公赏鞌战之功，扩建六军。郤克、士燮、栾书、韩厥等分掌军政，晋国声势更盛。"},
  {speaker="",text="齐顷公经此惨败，减轻赋役、抚恤孤寡、礼遇贤士。数年之后，国力渐渐恢复。"},
  {speaker="",text="晋国后来又把齐国所得之地归还鲁、卫，诸侯看出强国反复逐利，彼此盟信愈发淡薄。"},
  {speaker="",text="楚国方面，夏姬嫁给连尹襄老。襄老战死邲地后，其子黑要又与夏姬私通。"},
  {speaker="夏姬",text="郑国来信，说已寻得襄老尸首。若要迎回遗骨，须由我亲自前往交涉。"},
  {speaker="屈巫",text="我可先向楚王请命出使齐国，再从郑国接你同行。此后不再回楚，另寻安身之地。"},
  {speaker="",text="屈巫暗中促成荀罃与公子谷臣、襄老尸首的交换，使夏姬顺利返回郑国。"},
  {speaker="",text="屈巫行至郑国便停下，与夏姬成婚，携带家财投奔晋国。晋人任他为邢大夫，号申公巫臣。"},
  {speaker="楚共王",text="屈巫欺君逃亡，又拐走夏姬。抄没他在楚国的宗族产业，罪及同党！"},
  {speaker="",text="子反、子重瓜分屈巫家产，并杀其族人与黑要。屈巫闻讯，发誓使二人疲于奔命。"},
  {speaker="屈巫",text="楚国北面有晋牵制，东面尚有吴国。我去教吴人车战，使楚军从此东西奔走，不得安宁。"},
  {speaker="",text="屈巫出使吴国，传授乘车、射御与阵法。吴军由此渐强，开始不断侵扰楚国东境。"},
  {speaker="",text="楚、郑联军一度伐卫侵鲁，鲁国献出工匠织女求和；晋国又转令鲁国攻郑，列国在晋楚之间反复。"},
  {speaker="",text="郑襄公去世，郑悼公即位，转而亲晋。楚令尹公子婴齐攻郑，晋将栾书率军救援。"},
  {speaker="",text="郤克箭伤复发去世，栾书继掌中军。晋景公却日益骄纵，开始宠信灵公旧臣屠岸贾。"},
  {speaker="",text="赵同、赵括驱逐赵婴齐，赵氏内部先乱。梁山崩塌后，屠岸贾又买通卜者，把灾异归罪赵氏。"},
  {speaker="屠岸贾",text="当年弑杀灵公，赵盾虽未亲自动手，却是主谋。今日不清算赵氏，国法何在？"},
  {speaker="韩厥",text="赵朔，屠岸贾已调集甲士。你立刻出城，我还能替赵氏保存一线血脉。"},
  {speaker="赵朔",text="先人有罪无罪，自有后世评说。我不能独逃。庄姬已有身孕，若生男儿，请将军护他成人。"},
  {speaker="",text="程婴护送赵庄姬进入宫中。屠岸贾随即包围下宫，赵朔、赵同、赵括、赵旃及族人尽遭杀害。"},
  {speaker="",text="赵庄姬在宫中生下一子，取名赵武。屠岸贾入宫搜查，宫人只说所生为女且已夭折。"},
  {speaker="赵庄姬",text="先祖若愿保全赵氏，就让这孩子一声不哭；若天意绝赵，就让搜兵听见吧。"},
  {speaker="",text="搜兵走过衣前，赵武始终无声。屠岸贾搜查无获，暂退出宫门，却仍命甲士沿路盘查。"},
  {speaker="韩厥",text="我已备好药囊。可信医者把赵武藏入其中，从东宫门穿过搜查线；我在城外接应。"},
  {speaker="医者",text="药囊里装的是赵氏最后的性命。我只走宫中大道，不与搜卒纠缠，务必把孩子送到韩将军手中。"},
  {speaker="军令",text="护送医者由东侧双格宫门出城并抵达（44，15）。不可击退屠岸贾；医者、韩厥任一被击退即失败。"}
 },
 events={{id="medicine_bag_check",trigger="approach",position={26,16},radius=2,speaker="宫中搜卒",text="站住！药囊中装的什么？打开查验！"},{id="east_gate",trigger="approach",position={39,15},radius=3,speaker="韩厥",text="东宫门就在前方。不要恋战，穿门后继续向东，我在外侧接应！"},{id="handoff",trigger="approach",position={43,15},radius=1,speaker="医者",text="韩将军，赵氏孤儿已经越过宫门，请快接应！"}},
 victory={
  {speaker="",text="医者以药囊藏住赵武，穿过东宫门搜查线。韩厥在宫外接住药囊，将孩子秘密带走。"},
  {speaker="韩厥",text="宫门之外仍有耳目。先去偏僻处藏身，等屠岸贾的人从首阳山回来再作安排。"},
  {speaker="",text="真孤脱宫之后，程婴与公孙杵臼才定下以假孤换真孤之计，以转开屠岸贾的追索。"},
  {speaker="公孙杵臼",text="抚养遗孤比赴死更难。你善医而年轻，留下养育赵武；我带假孤去首阳山承受追捕。"},
  {speaker="程婴",text="我舍下亲子不是求名，只求赵氏尚有血脉。待赵武长成，再让天下知道今日真相。"},
  {speaker="",text="程婴故意向屠岸贾告发公孙杵臼，使搜兵尽奔首阳山。"},
  {speaker="",text="首阳山上，公孙杵臼抱着程婴之子假作赵氏孤儿。屠岸贾赶到后逼问不成，将二人杀害。"},
  {speaker="",text="屠岸贾以为赵氏血脉已绝，撤去宫城搜卒。程婴忍住丧子之痛，返回与韩厥接头。"},
  {speaker="程婴",text="公孙杵臼和我儿已经替赵武赴死。请将军把真孤交给我，往后再不能有半点差错。"},
  {speaker="韩厥",text="你献出亲子保全故主之后，我也会守住秘密。只要韩厥尚在，便不会让屠岸贾找到他。"},
  {speaker="",text="屠岸贾欲以金帛奖赏程婴。程婴只请求收葬赵氏遗骸，借此掩饰自己的真实用意。"},
  {speaker="程婴",text="我不敢求富贵，只愿收拾赵氏尸骨，使他们不至暴露荒野。"},
  {speaker="",text="获准安葬赵氏后，程婴带着赵武远遁盂山藏匿，日夜教养，等待将来复仇雪冤。"},
  {speaker="",text="三年后，晋景公迁都新田，改名新绛。宫室虽新，赵氏冤案却始终压在晋国朝堂之上。"},
  {speaker="",text="景公梦见披发巨鬼闯入宫门，厉声控诉赵氏无罪。他惊惧成疾，从此寝食不安。"},
  {speaker="军令",text="藏孤出宫完成，获得900金币。赵朔等人与公孙杵臼按原著记为阵亡；屠岸贾和宫卫保留后续出场。"}
 },
 defeat={{speaker="",text="医者或韩厥被搜卒击退，赵武落入屠岸贾之手，赵氏最后的血脉未能保全。"}}
}
gstage={title_id="EscortTheZhaoOrphan57",turn_limit=20,map={blocked_edges={},size={48,32},terrain={
        "FFffffFFfffgFFfffgFFffgfFFffgfFFfgffFFfgffFFgfff",
        "gffFFgfffFFgfffFFffffFFffffFFffffFFfffgFFfffgFFf",
        "FFfffgFFffgfFFffgfFFfgffFFfgffFFgfffFFgfffFFffff",
        "ffffWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfffgfFFf",
        "FFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffgfffff",
        "fffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffgffFFg",
        "FFfgWiiiiiiiiiiiiihhhhhhhhhhhhiiiiiiiiiWfgfffffg",
        "ffgfWiiihhhhhhhiiihhhhhhhhhhhhiiiiiiiiiWfgfffFFf",
        "FFgfWiiihhhhhhhiiihhhhhhhhhhhhiiiiiiiiiWgfffffgf",
        "fgffWiiihhhhhhhiiihhhhhhhhhhhhiiiiiiiiiWgffffFFf",
        "FFffWiiihhhhhhhiiihhhhhhhhhhhhiiiiiiiiiWfffffgff",
        "gfffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWffffgFFf",
        "FFffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWffffgfff",
        "ffffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWfffgfFFf",
        "FFffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWfffgffff",
        "ffffWwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwGwwwwwwFf",
        "FFfgWwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwGwwwwwwfg",
        "fffgWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWfgfffFFg",
        "FFgfWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWfgffffgf",
        "ffgfWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWgffffFFf",
        "FFffWiiiiiiiiiiiiiiiiiiwwiiihhhhhhhhiiiWgffffgff",
        "fgffWiiihhhhhhhiiiiiiiiwwiiihhhhhhhhiiiWfffffFFf",
        "FFffWiiihhhhhhhiiiiiiiiwwiiihhhhhhhhiiiWffffgfff",
        "gfffWiiihhhhhhhiiiiiiiiwwiiihhhhhhhhiiiWffffgFFf",
        "FFffWiiihhhhhhhiiiiiiiiwwiiihhhhhhhhiiiWfffgffff",
        "ffffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWfffgfFFf",
        "FFffWiiiiiiiiiiiiiiiiiiwwiiiiiiiiiiiiiiWffgfffff",
        "fffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffgffFFg",
        "FFfgWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWfgfffffg",
        "ffgFFfffgFFffgfFFffgfFFfgffFFfgffFFgfffFFgfffFFf",
        "FFgfffFFffffFFffffFFffffFFfffgFFfffgFFffgfFFffgf",
        "fgfFFffgfFFfgffFFfgffFFgfffFFgfffFFffffFFffffFFf",
    },file="map.bmp"},deploy={unselectables={{position={10,16},hero="PalaceDoctor57"},{position={44,16},hero="HanJue48"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=9000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)game:appoint_hero("PalaceDoctor57",1);game:appoint_hero("HanJue48",1)end
function on_begin(game)
 game:generate_unit("TuAnGu50",1,Enum.force.enemy,{34,13});game:set_unit_invulnerable("TuAnGu50",true)
 many(game,"PalaceSearchGuard57",{{31,15},{31,18},{26,13},{26,19},{21,12},{21,20},{16,14},{16,18}},Enum.force.enemy)
 many(game,"PalaceSearchArcher57",{{36,11},{36,20},{28,10},{28,22}},Enum.force.enemy)
end
function on_update(game)
 if not medicine_bag_warning and game:is_unit_within("PalaceDoctor57",{26,16},2)then medicine_bag_warning=true;game:push_cmd_speak(0,"宫中搜卒喝道：站住！药囊中装的什么？打开查验！");game:push_cmd_speak(0,"医者答道：公主产后的药物，耽误病情，你担得起吗？")end
 if not gate_warning and game:is_unit_within("PalaceDoctor57",{39,15},3)then gate_warning=true;game:push_cmd_speak(0,"东宫门就在前方。不要恋战，穿门后继续向东，我在外侧接应！")end
 if not handoff_warning and game:is_unit_within("PalaceDoctor57",{43,15},1)then handoff_warning=true;game:push_cmd_speak(0,"医者低声道：韩将军，赵氏孤儿已经越过宫门，请快接应！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 if game:get_num_commanders_alive()<#gcommanders then return Enum.status.defeat end
 if game:is_unit_within("PalaceDoctor57",{44,15},1)then return Enum.status.victory end
 return Enum.status.undecided
end
