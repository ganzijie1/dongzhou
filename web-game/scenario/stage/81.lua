gally_hold_position=true
gsupply_enabled=true
gitems={{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}
gcommanders={"ChenQi81","BaoMu81"}
gevents_enabled=true
gduel_enabled=false
gduels={}
gsites={
 {id="gao_residence",name="高氏府库",position={49,10},restore_hp=24,restore_mp=14,rewards={{item="medicine",amount=1}}},
 {id="guo_residence",name="国氏府库",position={49,31},restore_hp=24,restore_mp=14,rewards={{item="spirit_powder",amount=1}}},
 {id="gao_gate_north",name="高氏西门",position={38,10},restore_hp=8,restore_mp=4,rewards={}},
 {id="gao_gate_south",name="高氏西门",position={38,11},restore_hp=8,restore_mp=4,rewards={}},
 {id="guo_gate_north",name="国氏西门",position={38,30},restore_hp=8,restore_mp=4,rewards={}},
 {id="guo_gate_south",name="国氏西门",position={38,31},restore_hp=8,restore_mp=4,rewards={}}
}
gstory={chapter="第八十一回",title="美人计吴宫宠西施 言语科子贡说列国",battle_title="临淄高国之乱",objective="击败高张，并让不可击杀的国夏按史实撤出临淄西界。",map_asset="m127.png",
 intro={
  {speaker="",text="越王勾践归国后依文种之策遍访美女，半年得二十余人，复选苎萝山下浣纱的西施、郑旦。范蠡以百金聘二女，送入土城，命老乐师教习歌舞容步三年。"},
  {speaker="范蠡",text="吴强甲于天下，越国尚不能与之争锋。二女入吴不是一朝胜负，而是要让夫差沉湎游乐、疏远忠臣，为越国争得生聚教训的岁月。"},
  {speaker="越王勾践",text="厚待二女及其家人，衣以绮罗、乘以帷车。待技艺尽善，再由先生亲送吴宫；越国今日每一分忍耐，都是来日复国之资。"},
  {speaker="",text="同一时期，齐景公舍长立幼，把安孺子荼托付国夏、高张。陈乞素与长公子阳生相结，先劝阳生奔鲁，又散布高、国将尽逐旧臣的流言。"},
  {speaker="陈乞",text="高、国挟幼君专政，今日若不合诸大夫家甲并攻二府，明日临淄旧臣都要被逐。鲍大夫与我分兵：高张必须伏诛，国夏若弃府西奔莒国，不必穷追。"},
  {speaker="鲍牧",text="我只为解除托孤二臣的专权，并未答应另立新君。先整齐家众，封住南北街口，不得扰害临淄百姓。"},
  {speaker="高张",text="先君命我与国夏共辅孺子，陈乞却以谣言召集私甲。关闭府门，弓手据墙，今日只论君命，不论陈氏强弱！"},
  {speaker="国夏",text="高氏北府若破，我自南府西门撤往莒国保存国氏。陈乞志在改立阳生，绝不只为所谓旧臣自保。"},
  {speaker="军令",text="陈乞、鲍牧任何一人被击退则失败。攻破高氏北府并击败高张；高张死后，国夏将按史实自动撤往西界，不得将其击杀。"},
 },
 events={
  {id="gao_falls",trigger="defeated",unit="GaoZhang81",speaker="陈乞",text="高张已死，国夏弃府西奔莒国；各军让开退路，不必穷追。"},
  {id="guo_retreats",trigger="scripted",turn=0,hp_percent=0,speaker="国夏",text="高氏已破，国氏不能独支。我按西街出城，往莒国保存宗祀！"}
 },
 victory={
  {speaker="",text="高张战死，国夏弃南府出奔莒国。陈乞立国书、高无平延续二氏祭祀，表面安抚齐人，暗中却已召公子阳生自鲁返齐。"},
  {speaker="公子阳生",text="我与子壬、阚止夜抵齐郊，只身藏入陈氏。若诸大夫肯守立长之义，今日便改奉长公子。"},
  {speaker="陈乞",text="诸大夫请看新得精甲！巨囊中不是甲胄，正是齐景公长子阳生。立子以长，今日奉鲍相国之命改事长君。"},
  {speaker="鲍牧",text="我本无此谋，何得乘我酒后相诬！陈乞强拉我下拜，诸大夫也被迫歃血；这场废立终会反噬主持之人。"},
  {speaker="",text="阳生即位为齐悼公，迁安孺子于宫外而杀之，又因疑鲍牧不愿拥立，听陈乞谗言诛杀鲍牧。国人怨悼公杀戮无辜。"},
  {speaker="",text="鲁国季孙斯伐邾，破国执邾子益。齐悼公为妹婿向吴乞师；鲁国旋即释放邾君，齐又请吴罢兵。夫差怒齐前后反复，反与鲁国合兵围齐。"},
  {speaker="陈恒",text="国人怨悼公召寇，又怨他杀鲍牧。我在阅师时进鸩酒，称君上暴疾而死，请吴王息兵；再立其子壬为简公。"},
  {speaker="",text="西施、郑旦学艺三年，范蠡携二女与六名侍女入吴。夫差见二女如神仙下降，伍子胥以妹喜、妲己、褒姒亡国为鉴，力谏不可收受。"},
  {speaker="伍子胥",text="美女是亡国之物。勾践得此绝色而不用，偏献大王，正说明越国所图不小；今日若收二女，吴宫歌舞必压过军国之声。"},
  {speaker="吴王夫差",text="好色人所同心，勾践献其所爱，正是尽忠于吴。相国不必把每一件越国贡物都说成兵刃。"},
  {speaker="西施",text="妾本苎萝山下浣纱之女，今入吴宫，只愿谨守洒扫歌舞之职，不敢过问国政。"},
  {speaker="",text="夫差独宠西施，在灵岩山建馆娃宫、响屧廊、玩花池、采香泾，四时游乐；郑旦郁郁而死。太宰嚭常侍左右，伍子胥求见屡被拒绝。"},
  {speaker="文种",text="越国歉收，请向吴太仓借粟万石。吴若拒绝便失恤邻之名；若肯借粮，则越民得活而吴仓转空。"},
  {speaker="伍子胥",text="今日非吴有越，便是越有吴。勾践早朝晏罢、恤民养士，借粮正为充实越国；大王应当辞绝。"},
  {speaker="吴王夫差",text="越民既是吴民，岂可见饥不救？寡人贷粟万石，明年只令越国如数偿还。"},
  {speaker="文种",text="次年当选粗大精粟蒸熟后归还。夫差见谷种肥美，必散给吴民播种；熟谷不生，吴国来岁自有饥荒。"},
  {speaker="",text="吴人果然尽种越粟，颗粒不生，举国大饥。勾践欲兴兵，文种以吴国忠臣尚在劝止；范蠡则访得南林处女教剑、楚人陈音教弩。"},
  {speaker="南林处女",text="击刺之道，内实精神，外示安佚；见之如好妇，夺之似猛虎。得此道者一人当百、百人当万。"},
  {speaker="",text="南林处女在山阴道以竹枝胜白猿，又在越宫接住百名勇士攒刺之戟，遂教军士三千。岁余辞归南林，再召已不可得。"},
  {speaker="陈音",text="弩生于弓，弓生于弹。臣所授连弩三矢连续而去，使敌不及防；三月之后，越国三千弩手可尽得其巧。"},
  {speaker="",text="伍子胥探知越国练兵，再谏夫差。伯嚭却称治兵只是守国常事。此时齐国陈恒已陈兵汶水，准备伐鲁。"},
  {speaker="子贡",text="鲁城卑池浅、君弱臣庸，正是难伐；吴城高池广、兵甲精利，反而易攻。相国内忧诸大夫势盛，应使他们困于强敌。"},
  {speaker="陈恒",text="先生所言直彻肺腑，只是齐兵已在汶上，忽然转向吴国必惹众疑。若能使吴先来伐齐，我便有名迎战。"},
  {speaker="子贡",text="我先南见吴王，以救鲁、服齐、威晋之利动其心；再东说越王卑辞出师，使吴王不先伐越。"},
  {speaker="吴王夫差",text="败万乘之齐、收千乘之鲁，吴国即可威加强晋。只是越国勤政训武，寡人原想先伐越。"},
  {speaker="子贡",text="畏弱越而避强齐，非勇；逐小利而忘大患，非智。臣愿东见越王，使其献甲从征。"},
  {speaker="越王勾践",text="先生如起死人而肉白骨。寡人愿献精甲、屈卢之矛、步光之剑，并选锐士三千从吴伐齐。"},
  {speaker="",text="子贡又北见晋定公，请晋国修兵休卒。待他返回鲁国，齐军已经与吴军交锋；吴如何败齐，留待第八十二回。"},
  {speaker="军令",text="临淄高国之乱完成，获得2400金币。下一关：艾陵之战。"},
 },
 defeat={{speaker="",text="陈乞或鲍牧被击退，或未能完成高张战死、国夏出奔的历史目标，本关失败。"}}
}
local phase=1
local guoxia_id=0
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 game:generate_unit("GaoZhang81",1,Enum.force.enemy,{49,10});guoxia_id=game:generate_unit("GuoXia81",1,Enum.force.enemy,{49,31});game:set_unit_invulnerable("GuoXia81",true)
 many(game,"QiClanGuard81",{{14,18},{17,16},{17,20},{17,26},{17,30},{23,17},{23,25},{29,18},{29,24}},Enum.force.own)
 many(game,"QiClanArcher81",{{14,24},{20,14},{20,28},{27,15},{27,27}},Enum.force.own)
 many(game,"GaoHouseGuard81",{{40,9},{40,12},{44,7},{44,14},{48,6},{52,7},{52,14},{54,11}},Enum.force.enemy)
 many(game,"GaoHouseArcher81",{{42,5},{42,16},{50,5},{50,16}},Enum.force.enemy)
 many(game,"GuoHouseGuard81",{{40,29},{40,33},{44,26},{44,36},{48,25},{52,27},{52,35},{54,31}},Enum.force.enemy)
 many(game,"GuoHouseArcher81",{{42,25},{42,37},{50,25},{50,37}},Enum.force.enemy)
end
function on_update(game)
 if phase==1 and not game:has_unit("GaoZhang81")then phase=2;game:push_cmd_speak(guoxia_id,"高张已死，国夏弃府出奔莒国！各军让开西街，不必追杀。");game:push_cmd_move(guoxia_id,{1,38})end
end
function on_victory(game)end
function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 if phase==2 and game:is_unit_within("GuoXia81",{1,38},2)then return Enum.status.victory end
 return Enum.status.undecided
end
gstage={title_id="Dongzhou81",turn_limit=30,map={blocked_edges={},size={60,42},terrain={
        "FffgffgFfffgffgfiiiiiiiiiiiiiiiiiiiiffgffgffgffffgffgffffgff",
        "fffFgffgffffgffgiiiiiiiiiiiiiiiiiiiifgffffgffgffffgffgffgfff",
        "gffffgFfgffgffffiiiiiiiiiiiiiiiiiiiiffgffffgffgffgffffgffgff",
        "fgFfgFfffgffgfffiiiiiiiiiiiiiiiiiiiigfWWWWWWWWWWWWWWWWWWWfgf",
        "fFgffgffffgffgffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWffg",
        "fffgFfgffgffffgfiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfff",
        "FfgffffFffgffffgiiiiiiiiiiiiiiiiiiiifgWiiiiiiiiiiiiiiiiiWffg",
        "gffFffFfgffgffgfiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "fgFfgffgffffgffgiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWfgf",
        "gffffFffgffffgffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "fFffffgffgffgfffiiiiiiiiiiiiiiiiiiiigfGiiiiiiiiiiCiiiiiiWfgf",
        "ffgfFgfFffgffgffiiiiiiiiiiiiiiiiiiiifgGiiiiiiiiiiiiiiiiiWffg",
        "FffFffgffffgffgfiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfff",
        "ffffgfFgffgffffgiiiiiiiiiiiiiiiiiiiifgWiiiiiiiiiiiiiiiiiWfff",
        "gfFgffffgffgffffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "fgffgFfffgffgffgiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWfgf",
        "fFgfFgffgffffgffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWffg",
        "FgffffgFfgffffgfiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfgf",
        "ffgFfffgffgffgffiiiiiiiiiiiiiiiiiiiifgWWWWWWWWWWWWWWWWWWWffg",
        "iiiiiiFiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
        "iiFiiFiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
        "iFiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
        "iiiiFiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
        "FfgffgfFffgffgffiiiiiiiiiiiiiiiiiiiiffWWWWWWWWWWWWWWWWWWWffg",
        "fffFffFffgffffgfiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfff",
        "ffFffffgffgffffgiiiiiiiiiiiiiiiiiiiifgWiiiiiiiiiiiiiiiiiWffg",
        "gffgfFffgffgffgfiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "fFffgffgffffgffgiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWfgf",
        "gfffFgfFgffffgffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "FgfFffgffgffgfffiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfgf",
        "ffgffgFfffgffgffiiiiiiiiiiiiiiiiiiiifgGiiiiiiiiiiiiiiiiiWffg",
        "ffFgffgffffgffgfiiiiiiiiiiiiiiiiiiiigfGiiiiiiiiiiCiiiiiiWfff",
        "ffffgFfgffgffffgiiiiiiiiiiiiiiiiiiiifgWiiiiiiiiiiiiiiiiiWfff",
        "gFfgFfffgffgffffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "FgffgffFfgffgffgiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWfgf",
        "ffgFfgffgffffgffiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWffg",
        "fgffffFffgffffgfiiiiiiiiiiiiiiiiiiiigfWiiiiiiiiiiiiiiiiiWfgf",
        "ffFffFfgffgffgffiiiiiiiiiiiiiiiiiiiifgWiiiiiiiiiiiiiiiiiWffg",
        "gFfgffgffffgffgfiiiiiiiiiiiiiiiiiiiiffWiiiiiiiiiiiiiiiiiWgff",
        "ffffFffgffffgffgiiiiiiiiiiiiiiiiiiiifgWWWWWWWWWWWWWWWWWWWfff",
        "FffffgfFgffgffffiiiiiiiiiiiiiiiiiiiiffgffffgffgffgffffgffgff",
        "fgfFgfFffgffgfffiiiiiiiiiiiiiiiiiiiigffgffgffffgffgffffgffgf",
},file="map.bmp"},deploy={unselectables={{position={10,19},hero="ChenQi81"},{position={10,23},hero="BaoMu81"}},num_required_selectables=0,selectables={}},rewards={equipments={},money=24000}}
