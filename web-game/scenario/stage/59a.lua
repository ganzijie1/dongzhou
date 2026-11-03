gally_hold_position=true
local xu_tong_defeated=false
local king_captured=false
gsupply_enabled=false
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"LuanShu58","XunYan58"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={}
gstory={chapter="第五十九回·上",title="宠胥童晋国大乱 诛岸贾赵氏复兴",battle_title="太阴山之变",
 objective="先击退胥童及晋厉公近卫，再令栾书、荀偃任一人接近晋厉公完成生擒。晋厉公不可直接击退；栾书或荀偃被击退则失败。",
 map_asset="m093.png",
 intro={
  {speaker="",text="鄢陵战后，楚军连夜退去，公子侧因醉酒误军自缢。晋厉公凯旋新绛，自恃天下无敌，骄侈日甚。"},
  {speaker="士燮",text="外胜而内忧，国君骄纵、权臣争势，晋国的大乱恐怕就在眼前。"},
  {speaker="",text="士燮忧愤成疾，不肯求医，未几而卒。晋厉公欲拔宠臣胥童为卿，胥童便把三郤视作腾位的障碍。"},
  {speaker="胥童",text="郤氏族大兵强，鄢陵阵前又曾私纵郑君。若不先除，将来必为国患。"},
  {speaker="",text="胥童诱使被俘的熊茷诬告郤至通楚，又设计令郤至在周室公馆与孙周相见，使晋厉公愈加猜忌。"},
  {speaker="",text="寺人孟张夺取郤至车上的鹿，反被郤至射杀。厉公震怒，命长鱼矫、清沸魋假借诉讼接近讲武堂。"},
  {speaker="",text="三郤被杀后，晋厉公任胥童为上军元帅，夷羊五、清沸魋分掌新军，并释放熊茷回楚。"},
  {speaker="",text="栾书、荀偃羞与胥童同列，接连称病不朝。长鱼矫看出厉公不肯斩尽栾荀，预言二人终将反制，随即逃往西戎。"},
  {speaker="",text="清沸魋刺倒郤犨，长鱼矫与清沸魋合杀郤锜，又追斩逃出的郤至。三郤同日遇害，首级悬于朝门。"},
  {speaker="栾书",text="胥童擅引甲士入朝，杀卿执政，今日又想连栾、荀二氏一并诛除。"},
  {speaker="荀偃",text="厉公一时不忍杀我等，胥童却绝不会罢手。与其坐待三郤之祸重演，不如先救晋国社稷。"},
  {speaker="",text="晋厉公与胥童出游匠丽氏，三宿不归。栾书、荀偃假称病愈迎驾，暗令程滑率三百甲士埋伏太阴山两侧。"},
  {speaker="程滑",text="君车进入山道后，两翼同时合围。我先斩胥童，诸军只可擒君，不可乱箭伤及晋侯。"},
  {speaker="军令",text="击退胥童后接近晋厉公完成生擒。两侧岩山不可跨越，中央山道可供车骑通行。"}
 },
 events={{id="ambush",trigger="approach",position={25,17},radius=5,speaker="程滑",text="太阴山伏兵尽起！先断胥童，再围君车！"},{id="capture",trigger="approach",position={25,17},radius=1,speaker="荀偃",text="君侯弃政远游，今日请暂驻山下，听群臣共议晋国安危。"}},
 victory={
  {speaker="",text="程滑一刀斩杀胥童，伏兵堵住前后山道。晋厉公从车上跌落，被甲士生擒于太阴山下。"},
  {speaker="栾书",text="君臣名分不可轻弃，但今日已经骑虎难下。先以君命召士匄、韩厥前来共议。"},
  {speaker="",text="士匄与韩厥都看出使者神色异常，托病不至。当夜，荀偃劝栾书不可中途收手。"},
  {speaker="",text="程滑奉命献鸩酒，晋厉公州蒲死于军中，草草葬于翼城东门之外。"},
  {speaker="",text="栾书召集群臣，决定迎晋襄公之后孙周归国。十四岁的孙周在清原先责群臣必须奉令，诸卿战栗拜服。"},
  {speaker="孙周",text="若只奉寡人之名而不遵寡人之令，不如另立他人。今日的约定，诸卿不可忘记。"},
  {speaker="",text="孙周入新绛即位，是为晋悼公。他斩夷羊五、清沸魋，族逐其党，又以厉公之死治程滑之罪。"},
  {speaker="",text="栾书惊忧致病，告老后去世。晋悼公以韩厥代掌中军，晋国政局由乱转治。"},
  {speaker="军令",text="太阴山之变完成，获得1000金币。下一关：赵氏复仇。"}
 },
 defeat={{speaker="",text="栾书或荀偃被晋侯近卫击退，太阴山伏兵失去统领，政变失败。"}}
}
gstage={title_id="TaiyinCoup59",turn_limit=22,map={blocked_edges={},size={52,34},terrain={
        "rmmmmgffFwwwwwwwgffFmmmmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rmmmmffgfwwwwwwwffFgmmmmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrmmmmgffFwwwwwwwgffFmmmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrmmmmfgffwwwwwwwfFgfmmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrmmmmffFgwwwwwwwffFgmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrmmmmfgffwwwwwwwfFgfmmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrmmmmffFgwwwwwwwffFgmmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrmmmmgffFwwwwwwwFgffmmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrmmmmfFgfwwwwwwwfFgfmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrmmmmgffFwwwwwwwFgffmmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrmmmmfFgfwwwwwwwfFgfmmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrmmmmffFgwwwwwwwgffgmmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrmmmmFgffwwwwwwwFgffmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrmmmmffFgwwwwwwwgffgmmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrmmmmFgffwwwwwwwFgffmmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrmmmmfFgfwwwwwwwffgfmmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmgffgwwwwwwwgffFmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmfFgfwwwwwwwffgfmmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmgffgwwwwwwwgffFmmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmFgffwwwwwwwfgffmmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmffgfwwwwwwwffFgmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmFgffwwwwwwwfgffmmmmrrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmffgfwwwwwwwffFgmmmmrrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmgffFwwwwwwwgfffmmmmrrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmfgffwwwwwwwfFgfmmmmrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmgffFwwwwwwwgfffmmmmrrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmfgffwwwwwwwfFgfmmmmrrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmffFgwwwwwwwfffgmmmmrrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmgfffwwwwwwwFgffmmmmrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmffFgwwwwwwwfffgmmmmrrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmmgfffwwwwwwwFgffmmmmrrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmmmfFgfwwwwwwwffgfmmmmrrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmmmmfffgwwwwwwwgffFmmmmrrrr",
        "rrrrrrrrrrrrrmmmmmmmmmmmmmmmmmFgffwwwwwwwfgffmmmmrrr",
    },file="map.bmp"},deploy={unselectables={{position={12,8},hero="LuanShu58"},{position={35,25},hero="XunYan58"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=10000}}
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("JinLiGong58",1,Enum.force.enemy,{25,17});game:set_unit_invulnerable("JinLiGong58",true)
 game:generate_unit("XuTong59",1,Enum.force.enemy,{23,15});game:generate_unit("YiYangWu59",1,Enum.force.enemy,{27,18});game:generate_unit("QingFeiTui59",1,Enum.force.enemy,{24,19})
 game:generate_unit("ChengHua59",1,Enum.force.ally,{29,21})
 many(game,"CoupGuard59",{{14,10},{16,12},{33,22},{36,24},{38,26},{18,14}},Enum.force.own)
 many(game,"CoupArcher59",{{10,6},{17,9},{37,27},{40,29}},Enum.force.own)
 many(game,"RoyalEscort59",{{20,14},{22,17},{27,15},{29,18},{25,20}},Enum.force.enemy)
 many(game,"RoyalArcher59",{{19,12},{30,20},{27,12}},Enum.force.enemy)
end
function on_update(game)
 if not xu_tong_defeated and not game:has_unit("XuTong59")then xu_tong_defeated=true;game:push_cmd_speak(0,"胥童已被程滑斩杀！两翼合围君车，不得伤及晋侯！")end
 if xu_tong_defeated and not king_captured and (game:is_unit_within("LuanShu58",{25,17},1)or game:is_unit_within("XunYan58",{25,17},1))then king_captured=true;game:push_cmd_speak(0,"晋厉公已被伏兵生擒，太阴山道路全部封锁。")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if king_captured then return Enum.status.victory end
 return Enum.status.undecided
end