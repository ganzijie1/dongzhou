gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 0 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 0 }
}

gcommanders = { "ZhouYouWang", "GuoShiFu" }
gsites = {}

gstory = {
    chapter = "第二回",
    title = "褒人赎罪献美女 幽王烽火戏诸侯",
    battle_title = "骊山烽火",
    objective = "观看第二回剧情",
    map_asset = "m001.jpg",
    story_only = true,
    intro = {
        { speaker = "旁白", text = "宣王自东郊遇杜伯、左儒索命，抱病回宫，闭眼便见二鬼。三日后病势愈重，自知不起，召尹吉甫、召虎入宫托孤。" },
        { speaker = "周宣王", text = "朕在位四十六年，赖诸卿南征北伐，四海安宁。太子宫涅性情暗昧，二卿务必尽力辅佐，勿替周家世业。" },
        { speaker = "召虎", text = "杜伯厉鬼持朱弓赤矢，正应了从前童谣。大王恐怕难过此劫。" },
        { speaker = "伯阳父", text = "妖星隐伏紫微，宣王一身尚不足当此祸，周室还将有更大的变故。" },
        { speaker = "尹吉甫", text = "天定可以胜人，人定也能胜天。若只谈天数而不尽人事，还要三公六卿何用？" },
        { speaker = "旁白", text = "当夜宣王驾崩，太子宫涅即位，是为周幽王；立申伯之女为后，宜臼为太子，申伯进爵为申侯。姜后不久病逝，幽王居丧仍亲近群小、饮酒食肉，继而耽于声色、不理朝政。申侯屡谏不听退回申国，尹吉甫、召虎等老臣又相继去世，虢石父、祭公易、尹球居于三公逢迎王意，只有司徒郑伯友仍守臣节。" },
        { speaker = "岐山守臣", text = "启奏大王：泾、河、洛三川同日震动，岐山又有崩裂之声！" },
        { speaker = "周幽王", text = "山崩地震不过常事，何必惊动寡人？" },
        { speaker = "伯阳父", text = "三川发源岐山，如今震动，水源必将闭塞。昔伊、洛竭而夏亡，河竭而商亡；此祸不出十年。" },
        { speaker = "赵叔带", text = "天子不恤国政，又任用佞臣。我身居言官，即使大王不听，也必须尽臣节进谏。" },
        { speaker = "虢石父", text = "伯阳父、赵叔带私议国运，诽谤朝廷，不过是借灾异惑众。" },
        { speaker = "旁白", text = "数日后，三川果然枯竭，岐山崩塌，压坏许多民居。幽王全不畏惧，反命左右访求美女充实后宫。" },
        { speaker = "赵叔带", text = "山崩川竭，是脂血俱枯、高危下坠之兆。大王应勤政恤民、访求贤才，怎能反去访求美色？" },
        { speaker = "周幽王", text = "妖言惑众！将赵叔带革职逐出朝廷。" },
        { speaker = "赵叔带", text = "危邦不入，乱邦不居。我不忍坐看宗周变作禾黍废墟，今日便携家投奔晋国。" },
        { speaker = "褒珦", text = "赵叔带忠言无罪。大王不畏天变、黜逐贤臣，长此以往，国家空虚，社稷难保！" },
        { speaker = "旁白", text = "幽王大怒，将褒珦囚入镐京牢狱。褒珦被囚三年，朝中谏路断绝，贤臣纷纷离去。与此同时，当年抱走清水河弃婴的男子逃到褒地，将女婴送给姒大夫妇抚养，取名褒姒；十四年后，褒姒已长成绝色女子。" },
        { speaker = "洪德", text = "父亲因直谏获罪，并非犯下不赦之罪。若将褒姒献给天子，或许可以仿效散宜生赎回文王。" },
        { speaker = "旁白", text = "洪德用布帛三百匹买下褒姒，教以宫廷礼数，又用金银打通虢石父关节，将她带到镐京献上。" },
        { speaker = "洪德", text = "臣父褒珦自知忤旨，臣特访得美人褒姒献入宫中，只求大王赦免父罪。" },
        { speaker = "周幽王", text = "世间竟有如此美人！即刻释放褒珦，恢复官爵；褒姒留居别宫。" },
        { speaker = "旁白", text = "幽王得褒姒后十日不朝，群臣终日守候宫门也见不到天子。三个月间，他更未踏入申后正宫一步。" },
        { speaker = "申后", text = "何方女子，竟敢不朝正宫，又与天子并坐不起？宫中嫡庶礼法，岂能任你践踏！" },
        { speaker = "周幽王", text = "这是寡人新纳的美人，尚未定下位次。王后不必动怒。" },
        { speaker = "旁白", text = "褒姒次日仍不拜见申后。太子宜臼为母出气，命宫人采摘琼台花木，将褒姒引出，亲自上前打骂。" },
        { speaker = "褒姒", text = "太子今日几乎取妾性命。妾已有两月身孕，一身便是两命；若大王不能庇护，请放妾出宫。" },
        { speaker = "周幽王", text = "太子好勇无礼，暂逐往申国，交申侯管教。东宫师傅辅导无方，也一并削职！" },
        { speaker = "旁白", text = "宜臼被逐后，申后孤立无援。褒姒生下伯服，虢石父与尹球揣摩王意，暗中答应扶伯服取代宜臼。" },
        { speaker = "尹球", text = "太子已经逐居申国，伯服才是大王所爱。宫内有娘娘，朝外有我与虢公，东宫之位何愁不成？" },
        { speaker = "旁白", text = "申后思念宜臼，托善医术的温媪秘密送信申国。温媪出宫时被褒姒耳目搜出书信，当场押回琼台。" },
        { speaker = "褒姒", text = "申后信中说要与太子别作计较，分明是要谋害妾与伯服。请大王为我们母子做主！" },
        { speaker = "旁白", text = "幽王认出申后笔迹，不问缘由便拔剑杀死温媪。褒姒又日夜哭诉，逼幽王公开商议废后、废太子。" },
        { speaker = "虢石父", text = "申后德不称位，应当废去；既然母亲被废，宜臼也不应再居东宫。臣等愿扶伯服为太子。" },
        { speaker = "周幽王", text = "将申后退入冷宫，废宜臼为庶人；立褒姒为后、伯服为太子。再有进谏者，皆以宜臼党羽治罪！" },
        { speaker = "伯阳父", text = "夫妇、父子、君臣三纲俱绝，周室灭亡已经可以屈指等待。老臣今日告退。" },
        { speaker = "旁白", text = "群臣明知王意已决，进谏只是白白送死，于是多人弃职归田。朝中只剩虢石父、尹球、祭公易等佞臣。" },
        { speaker = "褒姒", text = "钟鼓歌舞都不能使妾欢喜。妾只记得从前手裂彩缯，那声音倒十分清脆。" },
        { speaker = "旁白", text = "幽王命司库每日送入彩缯百匹，让宫人不断撕裂取悦褒姒；彩缯耗费无数，褒姒却依旧不笑。" },
        { speaker = "周幽王", text = "不论宫内宫外，谁能让王后一笑，寡人赏赐千金！" },
        { speaker = "虢石父", text = "骊山有先王防备西戎的烽火台。大王若夜举烽烟，诸侯援兵必至；见他们奔走落空，王后必笑。" },
        { speaker = "郑伯友", text = "烽火是先王取信诸侯、召兵救急之物。今日无故举烽，异日真有外寇，诸侯必不再信！" },
        { speaker = "周幽王", text = "天下太平，哪会有事？寡人不过与王后在骊宫消遣，传令举烽、擂鼓！" },
        { speaker = "旁白", text = "鼓声如雷，烽火烛天。畿内诸侯以为镐京有变，连夜点兵赶到骊山，却只听见楼阁中的管弦宴乐。" },
        { speaker = "周幽王", text = "幸而并无外寇，有劳诸侯跋涉。诸位各自回国吧。" },
        { speaker = "褒姒", text = "列国诸侯慌忙而来，又卷旗而去，原来只为这一场空……实在可笑。" },
        { speaker = "旁白", text = "幽王终于博得褒姒一笑，将千金赏给虢石父。诸侯面面相觑、含怒而归，王室号令从此失信。" },
        { speaker = "申侯", text = "夏桀宠妹喜而亡夏，商纣宠妲己而亡商。大王宠褒姒、废嫡立庶，正重蹈桀纣覆辙，请收回乱命！" },
        { speaker = "虢石父", text = "申侯因女儿与外孙被废，早有怨望谋叛之心。应削去爵位，发兵讨罪，以绝后患。" },
        { speaker = "周幽王", text = "准奏。削申侯之爵，命虢石父整顿兵车，准备讨伐申国！" },
        { speaker = "旁白", text = "烽火失信，申国结怨，犬戎又在西陲窥伺。废嫡、逐贤、戏诸侯三祸汇于一处，西周覆亡已不可避免。" },
        { speaker = "下回预告", text = "第三回：犬戎主大闹镐京，周平王东迁洛邑。" }
    },
    victory = {},
    defeat = {}
}

gstage = {
    title_id = "LiShanBeacon",
    turn_limit = 99,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "FFFFFFFFFFFFFFFFFFF", "FggggggfffffggggggF", "FggFgggfffffgggFggF",
            "FggggggfffffggggggF", "FffffffffffFfffffff", "Ffffffgggggggffffff",
            "FffffggfffffggffffF", "FffffggfffffggffffF", "Ffffffgggggggffffff",
            "FffffffffFffffffffF", "FggggggfffffggggggF", "FggFgggfffffgggFggF",
            "FggggggfffffggggggF", "FFFFFFFFFFFFFFFFFFF"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {8, 7}, hero = "ZhouYouWang" },
            { position = {10, 7}, hero = "GuoShiFu" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 0 }
}

function on_deploy(game)
    game:appoint_hero("ZhouYouWang", 25)
    game:appoint_hero("GuoShiFu", 24)
end

function on_begin(game)
end

function on_update(game) end

function on_victory(game)
end

function on_defeat(game)
end

function end_condition(game)
    return Enum.status.undecided
end
