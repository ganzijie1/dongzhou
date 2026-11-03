gally_hold_position=true
local revenge_open=false
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"HanJue48","ZhaoWu59"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="tu_estate_courtyard",name="屠府中庭",position={30,16},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}
gstory={chapter="第五十九回·下",title="宠胥童晋国大乱 诛岸贾赵氏复兴",battle_title="赵氏复仇",
 objective="韩厥、赵武从屠府南门攻入。赵武接近屠岸贾后触发复仇对话并解除其保护，随后击退屠岸贾，按原著视为斩首。韩厥或赵武被击退则失败。",
 map_asset="m094.png",
 intro={
  {speaker="",text="晋悼公即位后赏善罚恶、整顿百官。韩厥私下奏请追录赵衰、赵盾两世之功。"},
  {speaker="韩厥",text="赵氏辅佐文公、襄公，功在社稷，却被屠岸贾假借弑逆之罪灭族。如今遗孤赵武仍在盂山。"},
  {speaker="晋悼公",text="寡人也曾听先人说起此案。既然赵武尚在，卿可秘密迎他入朝，不可让屠岸贾先得消息。"},
  {speaker="",text="韩厥亲赴盂山迎赵武，程婴驾车同行。由故绛到新绛，程婴见城郭尽非，感念公孙杵臼与亲子之死。"},
  {speaker="",text="晋悼公诈称有疾，召百官入宫问安。当众问起赵氏功劳无人承继，随即命赵武从帷幕后走出。"},
  {speaker="",text="百官起初都说赵氏已灭十五年，待韩厥说明当年被杀的是程婴之子，才知道眼前少年正是真正的赵氏孤儿。"},
  {speaker="",text="屠岸贾见赵武现身，伏地失语。晋悼公当殿宣布其灭族罪状，命韩厥与赵武即刻包围屠府。"},
  {speaker="",text="赵胜也从宋国被召回，恢复邯郸封地；赵氏旧臣与国人得知冤案翻转，无不称快。"},
  {speaker="赵武",text="赵氏十五年血仇，赖公孙杵臼、程婴舍命才留下一线。今日不是私斗，而是为满门洗雪冤屈。"},
  {speaker="晋悼公",text="赵氏灭门皆屠岸贾所为。韩厥、赵武立即领兵围其府第，不得使一人逃散。"},
  {speaker="韩厥",text="屠府围墙连续，只有南面双格正门可以通行。弓手压住门内，赵武随我直取中庭。"},
  {speaker="程婴",text="十五年隐忍只为今日。赵武必须亲眼见到屠岸贾伏法，赵氏才算真正复兴。"},
  {speaker="军令",text="由南门攻入屠府。赵武接近屠岸贾前，他不会被击退；触发对话后再将其击退。"}
 },
 events={{id="south_gate",trigger="approach",position={24,27},radius=2,speaker="韩厥",text="屠府南门已开，左右城墙不可跨越！甲士进门后让开射线。"},{id="zhao_faces_tu",trigger="approach",position={31,11},radius=3,speaker="赵武",text="屠岸贾，我是赵朔之子赵武。十五年前赵氏的血债，今日偿还！"}},
 victory={
  {speaker="",text="赵武率甲士攻入正堂，屠岸贾退无可退，被擒后推出府门斩首。屠氏家兵放下兵器，赵氏冤案昭雪。"},
  {speaker="赵武",text="请将屠岸贾首级赐我，祭告父祖、公孙杵臼以及所有为赵氏而死的人。"},
  {speaker="晋悼公",text="赵氏田禄尽数归还。赵武加冠，拜为司寇；程婴守孤有功，可任军正。"},
  {speaker="程婴",text="当年我没有死，只因赵氏孤儿尚未成人。如今复官报仇，我不能让公孙杵臼独在地下。"},
  {speaker="",text="程婴拒绝官爵，自刎而亡。赵武抚尸痛哭，将程婴与公孙杵臼厚葬于云中山，称为二义冢。"},
  {speaker="",text="晋悼公重新排列群臣：韩厥掌中军，士匄副之；荀罃、荀偃、栾黡、魏绛、祁奚等各居其职。"},
  {speaker="",text="新政蠲逋薄敛、济乏省役，宋、鲁诸国相继来朝。楚共王得知晋国由乱转治，原本的喜悦转为忧虑。"},
  {speaker="公子壬夫",text="若要扰乱晋国霸业，当从宋国着手。可资助鱼石等五名宋国逃臣，以宋人攻宋人。"},
  {speaker="",text="楚共王采纳其策，命公子壬夫为将，以鱼石等为向导率军伐宋，为下一回战事埋下伏笔。"},
  {speaker="军令",text="赵氏复仇完成，获得1200金币。第五十九回结束。"}
 },
 defeat={{speaker="",text="韩厥或赵武被屠府家兵击退，赵氏复仇未成，本关失败。"}}
}
gstage={title_id="ZhaoRestoration59",turn_limit=24,map={blocked_edges={},size={48,32},terrain={
        "FgffFgffFgffgfffgffFgffFgffFgffgfffgffFgffFgffFg",
        "gffgfffgffFgffFgffFgffgfffgffFgffFgffFgffgfffgff",
        "fFgffFgffFgffgfffgffFgffFgffFgffgfffgffFgffFgffF",
        "FgffgfffgffFgffFgffFgffgfffgffFgffFgffFgffgfffgf",
        "ffFgffFgffFgffgfffgffFgffFgffFgffgfffgffFgffFgff",
        "fFgffgfffgffWWWWWWWWWWWWWWWWWWWWWWWWWWWWgffgfffg",
        "gffFgffFgffFWiiiiiiiiiiiiiiiiiiiiiiiiiiWfFgffFgf",
        "ffFgffgfffgfWiiiiiiiiiiiiiiiiiiiiiiiiiiWFgffgfff",
        "fgffFgffFgffWiiiiiiiiiiiiiiiiiiiiiiiiiiWffFgffFg",
        "gffFgffgfffgWiiiiiiiiiiiiiihhhhhhhhiiiiWfFgffgff",
        "ffgffFgffFgfWiiiiiiiiiiiiiihhhhhhhhiiiiWgffFgffF",
        "FgffFgffgfffWiiiiiiiiiiiiiihhhhhhhhiiiiWffFgffgf",
        "fffgffFgffFgWiiiiiiiiiiiiiihhhhhhhhiiiiWfgffFgff",
        "fFgffFgffgffWiiiiiiiiiiiiiihhhhhhhhiiiiWgffFgffg",
        "gfffgffFgffFWiiiiiiiiiiiiiiiiiiiiiiiiiiWffgffFgf",
        "ffFgffFgffgfWiiiiiiiiiiiiiiiiiiiiiiiiiiWFgffFgff",
        "fgfffgffFgffWiiiiiiiiiiiiiiiiiCiiiiiiiiWfffgffFg",
        "gffFgffFgffgWiiiiiiiiiiiiiiiiiiiiiiiiiiWfFgffFgf",
        "ffgfffgffFgfWiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffgffF",
        "FgffFgffFgffWiiiiiiiiiiiiiiiiiiiiiiiiiiWffFgffFg",
        "gffgfffgffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiWfgfffgff",
        "fFgffFgffFgfWiiiiiiiiiiiiiiiiiiiiiiiiiiWgffFgffF",
        "FgffgfffgffFWiiiiiiiiiiiiiiiiiiiiiiiiiiWffgfffgf",
        "ffFgffFgffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiWFgffFgff",
        "fFgffgfffgffWiiiiiiiiiiiiiiiiiiiiiiiiiiWgffgfffg",
        "gffFgffFgffFWiiiiiiiiiiiiiiiiiiiiiiiiiiWfFgffFgf",
        "ffFgffgfffgfWiiiiiiiiiiiiiiiiiiiiiiiiiiWFgffgfff",
        "fgffFgffFgffWWWWWWWWWWWWGGWWWWWWWWWWWWWWffFgffFg",
        "gffFgffgfffgffFgffFgffFgffgfffgffFgffFgffFgffgff",
        "ffgffFgffFgffFgffgfffgffFgffFgffFgffgfffgffFgffF",
        "FgffFgffgfffgffFgffFgffFgffgfffgffFgffFgffFgffgf",
        "fffgffFgffFgffFgffgfffgffFgffFgffFgffgfffgffFgff",
    },file="map.bmp"},deploy={unselectables={{position={21,29},hero="HanJue48"},{position={28,29},hero="ZhaoWu59"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=12000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("ChengYing59",1,Enum.force.ally,{30,16})
 game:generate_unit("TuAnGu50",1,Enum.force.enemy,{31,11});game:set_unit_invulnerable("TuAnGu50",true)
 many(game,"CoupGuard59",{{20,29},{24,30},{30,29},{33,28}},Enum.force.own)
 many(game,"CoupArcher59",{{18,28},{35,29}},Enum.force.own)
 many(game,"TuHouseGuard59",{{24,25},{25,25},{20,22},{29,22},{34,18},{25,15},{36,15},{28,12}},Enum.force.enemy)
 many(game,"TuHouseArcher59",{{18,20},{31,20},{22,17},{36,12}},Enum.force.enemy)
end
function on_update(game)
 if not revenge_open and game:is_unit_within("ZhaoWu59",{31,11},3)then revenge_open=true;game:set_unit_invulnerable("TuAnGu50",false);game:push_cmd_speak(0,"赵武已经当面陈明身份，屠岸贾的保护解除！击退他，为赵氏复仇！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if revenge_open and not game:has_unit("TuAnGu50")then return Enum.status.victory end
 return Enum.status.undecided
end