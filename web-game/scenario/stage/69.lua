gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"GongZiQiJi69"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={{id="shangcai_palace",name="蔡都宫城",position={31,9},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}},{id="shangcai_west",name="蔡都西府",position={21,18},restore_hp=20,restore_mp=10,rewards={}},{id="shangcai_east",name="蔡都东府",position={42,18},restore_hp=20,restore_mp=10,rewards={}}}
gstory={chapter="第六十九回",title="楚灵王挟诈灭陈蔡 晏平仲巧辩服荆蛮",battle_title="蔡都围城",objective="突破蔡都南门，在粮尽总攻阶段击退蔡世子有、公孙归生并清除守军。公子弃疾不得被击退。",map_asset="m118.png",
 intro={
  {speaker="",text="陈哀公病重，公子招、公子过为扶立公子留，命孔奂伏甲宫巷，刺杀世子偃师。哀公闻变自缢，陈国由此大乱。"},
  {speaker="公子胜",text="嫡兄偃师被招、过枉杀，父君亦因此身亡。臣与侄儿公孙吴无处容身，愿请楚王主持公道。"},
  {speaker="伍举",text="奉公孙吴讨逆，名正言顺。陈乱既定，再问蔡般弑父之罪，楚国足以继庄王之业。"},
  {speaker="楚灵王",text="即日起兵伐陈。公子留既已出奔，孤当诛杀招、过之党，重定陈国。"},
  {speaker="",text="楚军抵陈，百姓怜偃师之死，又见公孙吴在军中，纷纷箪食壶浆迎接。公子招杀公子过，将首级献楚求免。"},
  {speaker="公子招",text="杀世子、立公子留，都是公子过所为。臣已斩过谢罪，愿大王收陈为县，臣先回城整治宫室。"},
  {speaker="公子胜",text="主谋本是公子招，行刺者则是孔奂。他如今委罪于死人，只求以陈国土地换取自己的性命。"},
  {speaker="",text="楚灵王入陈，斩孔奂、逐公子招，却没有复立公孙吴，反毁陈宗庙、改陈为县，以穿封戍守陈。陈人方知所谓讨逆只是并吞之名。"},
  {speaker="",text="楚军休兵一年。伍举又劝楚灵王以巡方为名驻军申地，重币卑辞诱蔡灵侯般赴会。"},
  {speaker="公孙归生",text="楚王贪而无信，此次礼重言卑，恐怕是诱君赴死。若不得不往，请先立世子有监国。"},
  {speaker="蔡灵侯",text="蔡国不能抵楚一县，召而不往，只会立刻招来大军。立世子有之后，寡人亲赴申地。"},
  {speaker="",text="申地宴席上，蔡灵侯被灌得大醉。楚灵王掷杯为号，伏甲尽出，将蔡侯与不肯投降的七十名从臣全部擒杀。"},
  {speaker="楚灵王",text="蔡般弑父，孤代天行讨。公子弃疾立即统领大军，长驱入蔡，不得给其整军求援之机。"},
  {speaker="蔡世子有",text="父君虽死，蔡国宗社尚在。授兵登城，闭门固守；公孙归生总理城防，再遣蔡洧向晋国求救。"},
  {speaker="公子弃疾",text="南北弭兵之约约束不了王命。围住蔡都南北通路，先逼其外军退入城中，再逐层压缩守军。"},
  {speaker="军令",text="攻入蔡都并击退蔡世子有、公孙归生及全部守军。第三回合蔡洧突围求援，第六回合朝吴出城游说，第八回合守军粮尽后开始总攻。公子弃疾被击退则失败。"}
 },
 events={
  {id="story_event_1",trigger="scripted",turn=0,hp_percent=0,speaker="蔡洧",text="父仇国难在身，洧今夜缒城北走，必请晋侯合诸侯来援。"},
  {id="story_event_2",trigger="scripted",turn=0,hp_percent=0,speaker="朝吴",text="公子有当璧之祥，何苦替无道之君聚敛天下怨恨？愿反戈救蔡。"},
  {id="story_event_3",trigger="scripted",turn=0,hp_percent=0,speaker="公子弃疾",text="休以巧言离间君臣！姑且留你性命，回城劝世子面缚出降。"}
 },
 victory={
  {speaker="",text="楚军从夏四月围到冬十一月。蔡都粮尽，饿死者过半，公孙归生积劳成病，守军再也无力抵挡蚁附而上的楚军。"},
  {speaker="蔡世子有",text="国君死社稷，正是常理。孤既摄位守国，便与此城共存亡，绝不屈膝仇人。"},
  {speaker="",text="蔡都被攻破，世子有端坐城楼受缚。公子弃疾抚慰居民，将世子与蔡洧押往九冈山报捷，朝吴则被留在军中。"},
  {speaker="申无宇",text="昔日宋襄公以鄫子祭社，诸侯因此离叛。世子有虽是罪人之后，终究是诸侯之嗣，不可当作六畜献祭。"},
  {speaker="楚灵王",text="逆般之子何足与诸侯相比？九冈山神许孤天下，正好用他作为牺牲。"},
  {speaker="",text="楚灵王杀世子有祭神。蔡洧哭泣三日，表面受楚王赏识，心中却因父亲蔡略同死于申地而埋下复仇之志。"},
  {speaker="蔡洧",text="大王既有陈、蔡，与中原接壤，若高筑两国城池、各赋千乘，再图吴越，天下谁敢不服？"},
  {speaker="",text="楚灵王重筑陈、蔡，又建东西不羹城，以公子弃疾为蔡公。太卜占得无成，楚王仍以为天下可以人力强取。"},
  {speaker="",text="诸侯畏楚，小国朝贡、大国修聘。齐国上大夫晏婴奉齐景公之命出使楚国，楚灵王打算借机折辱他以扬国威。"},
  {speaker="薳启疆",text="晏平仲善于应对，一事不足以辱之。可先在东门旁凿五尺小窦，再以武士、群臣轮番压服。"},
  {speaker="晏婴",text="这是狗门，不是人所出入。出使狗国才从狗门走；既然奉命出使楚国，仍请打开人门。"},
  {speaker="",text="楚王第一计反遭讥刺，只得打开东门。又令魁梧武士迎接，晏婴以聘问非攻战为由将其喝退。"},
  {speaker="斗成然",text="齐国兵甲货财本足称霸，为何桓公之后朝晋暮楚？以齐侯之志、平仲之贤，却甘自比臣仆吗？"},
  {speaker="晏婴",text="盛衰自有时运，今日交聘是邻国之礼，何谓臣仆？令祖子文识时通变，足下却为何说出这般悖论？"},
  {speaker="公孙瑕",text="崔、庆作乱时，齐臣多有死义者。你既不讨贼、不避位，也不殉死，难道只是贪恋名位？"},
  {speaker="晏婴",text="君为社稷而死，臣才应从。齐庄公并非为社稷而死，我留下是为安定新君。楚国朝列之臣，人人都是讨贼死难之士吗？"},
  {speaker="薳启疆",text="你身为相国，却穿敝裘、乘羸马，祭礼也极俭薄，这难道不是鄙吝？"},
  {speaker="晏婴",text="我使父族衣裘、母族食肉、妻族无冻馁，又供养七十余家士人。家虽俭而三族肥，这才足以彰君恩。"},
  {speaker="囊瓦",text="古之明君名将多形貌魁梧，你身不满五尺、力不胜鸡，只凭口舌，难道不可耻吗？"},
  {speaker="晏婴",text="秤锤虽小能压千斤，船桨虽长终为水役。身长力大而败亡者不少，我只是有问则答，从未凭形貌自夸。"},
  {speaker="伍举",text="平仲是齐国贤士，诸位不可再以口舌相加。今日楚廷虽欲辱客，反倒尽显晏子的器识。"},
  {speaker="军令",text="蔡都围城完成，获得1600金币。第六十九回结束。"}
 },
 defeat={{speaker="",text="公子弃疾被击退，或二十八回合内未能攻破蔡都，本关失败。"}}
}
local messenger_report=false
local parley_done=false
local final_assault=false
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("CaiShiZiYou69",1,Enum.force.enemy,{31,9});game:generate_unit("GongSunGuiSheng69",1,Enum.force.enemy,{21,18});game:generate_unit("ChaoWu69",1,Enum.force.enemy,{42,18})
 game:set_unit_invulnerable("CaiShiZiYou69",true);game:set_unit_invulnerable("GongSunGuiSheng69",true);game:set_unit_invulnerable("ChaoWu69",true)
 many(game,"ChuSiegeGuard69",{{25,41},{28,42},{35,42},{38,41},{23,43},{40,43}},Enum.force.own);many(game,"ChuSiegeArcher69",{{27,44},{31,44},{32,44},{36,44}},Enum.force.own)
 many(game,"CaiGuard69",{{31,36},{32,36},{26,32},{37,32},{18,28},{45,28},{26,14},{37,14},{31,5},{32,5}},Enum.force.enemy)
 many(game,"CaiArcher69",{{28,34},{35,34},{17,25},{46,25},{27,12},{36,12},{29,7},{34,7}},Enum.force.enemy)
end
function on_update(game)
 local turn=game:get_turn_current()
 if not messenger_report and turn>=3 then messenger_report=true;game:push_cmd_speak(0,"蔡洧已从北门缒城突围，抵达晋国求援；然而晋、齐、宋等国畏惧楚军，只肯遣狐父持书请和。")end
 if not parley_done and turn>=6 then parley_done=true;game:push_cmd_speak(0,"狐父的请和书被楚灵王拒绝。朝吴出城劝公子弃疾反戈，弃疾顾忌当璧之言，只佯怒遣其回城。")end
 if not final_assault and turn>=8 then final_assault=true;game:set_unit_invulnerable("CaiShiZiYou69",false);game:set_unit_invulnerable("GongSunGuiSheng69",false);game:push_cmd_speak(0,"蔡都被围数月，粮食已经耗尽！公孙归生积劳成病，世子有登城死守，楚军总攻开始！")end
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 if not game:has_unit("GongZiQiJi69")then return Enum.status.defeat end
 if final_assault and not game:has_unit("CaiShiZiYou69")and not game:has_unit("GongSunGuiSheng69")and not game:has_unit("CaiGuard69")and not game:has_unit("CaiArcher69")then return Enum.status.victory end
 return Enum.status.undecided
end
gstage={title_id="ShangcaiSiege69",turn_limit=28,map={blocked_edges={},size={64,46},terrain={
        "FgfffFggffffggFffggffffFgfffFggfffggfFffggffffFgfffFgffffggfFffg",
        "ffggffffFgffffggfFfggfFffggffffFgfffggffFfggfFffggfffgFffffggffF",
        "gfFfggffffgFffffFgfffggffFfggffffgFfffgFffffggffFfggfffggFfffgFf",
        "fggffFggfWWWWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWWWWfFggffffg",
        "fffgFfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgfffFgfff",
        "gffffggFfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfggfffgFf",
        "fFgffffggWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfFfggfFfg",
        "fffgFffffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWFffffggff",
        "gffFfggffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfggFfffgg",
        "fggfffFggWiiihhhhhhhhhhhhiiiiiiCiiiiiiihhhhhhhhhhhhiiiWfffggfFff",
        "FffggffffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWFffffFgff",
        "ggfFfggfFWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfggffffgF",
        "ffFgfffggWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWffFggffff",
        "ffffgFfffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWggfffFgff",
        "ggffffggFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFffgg",
        "ffFgfffFgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggfFf",
        "fFffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgFffffggf",
        "ggffFfggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggFfffg",
        "ffggfffFgWiiiiiiiiiiiCiiiiiiiiiiiiiiiiiiiiCiiiiiiiiiiiWfffFggfff",
        "gFffggFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggffffFgf",
        "FggfffggfWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFfggffffg",
        "fffFgfffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWgffFggffF",
        "gffffgFffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWfgFfffggf",
        "FggffFfggWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfffggFffg",
        "fffggfffFWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWgffffggfF",
        "gfFffggffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfgFffffFg",
        "fggffFfggWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfFfggffff",
        "fffgFffffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWgfffFggff",
        "ggfffggFfWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfggffffFg",
        "fFggfffggWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWfFfggfFff",
        "ffffFgfffWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWFgfffggff",
        "ggfFffggfWiiihhhhhhhhhhhhiiiiiiiiiiiiiihhhhhhhhhhhhiiiWffgFfffgg",
        "ffggffFfgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffffggFff",
        "FfffggfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWFgfffFggf",
        "ggfFffggFWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffggffffF",
        "ffFgffffgWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWffFfggfff",
        "gfffgFfffWiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiWggfffFggf",
        "fggfffggFWWWWWWWWWWWWWWWWWWWWWWGGWWWWWWWWWWWWWWWWWWWWWWffggFfffg",
        "ffFggffFggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFf",
        "gFfffggfffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFgfffggf",
        "fggfFffggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFfffg",
        "fffggffFfggfFfggffffgFffffggffFggffFfggffffgFfffggfffFggffFfggff",
        "gFfffgFffffggffFggffffggFfffgFfffggfffFggffffggFffggFfffggfffFgg",
        "FggffffggFfffggfffFgfffFggffffggFffggffffFgfffFggfffggfFffggffff",
        "fffFgffffggfFffggFffggffffFgffffggfFfggfFffggffffFgfffggffFfggfF",
        "ggfffgFffffFgffffggfFfggffffgFffffFgfffggffFfggffffgFfffgFffffgg",
},file="map.bmp"},deploy={unselectables={{position={31,42},hero="GongZiQiJi69"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=16000}}
