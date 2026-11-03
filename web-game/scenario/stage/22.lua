gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "JiYou22" }
gduel_enabled = true
gduels = {
    {
        attacker = "JiYou22", defender = "YingNa22", exp = 70, outcome = "kill",
        attacker_speech = "嬴拿，两军争胜何必多伤士卒？你我各释兵刃，徒手定个雌雄！",
        defender_speech = "季友，你自称鲁国柱石，今日便让莒人看看你的本事！",
        result_speech = "行父高呼‘孟劳何在’，季友拔出宝刀，回身斩杀嬴拿。",
        text = "季友与嬴拿徒手相搏五十余合，佯退诱敌，以孟劳宝刀斩杀嬴拿。"
    }
}

gsites = {
    { id = "li_lu_camp", name = "鲁军行营", position = {4, 11}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "li_ju_camp", name = "莒军行营", position = {14, 2}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十二回",
    title = "公子友两定鲁君 齐皇子独对委蛇",
    battle_title = "郦地退莒",
    objective = "击败莒公子嬴拿；季友与嬴拿相邻可触发孟劳单挑",
    map_asset = "m037.png",
    intro = {
        { speaker = "", text = "鲁庄公病重，先问叔牙身后之事。叔牙力劝立庆父，季友则坚持奉公子般继位。" },
        { speaker = "季友", text = "庆父残忍无亲，叔牙又私附其兄。臣当以死奉般，不使鲁国社稷落入逆党之手。" },
        { speaker = "", text = "季友假传庄公之命，迫叔牙饮鸩。庄公当夜薨逝，公子般主持丧事。" },
        { speaker = "", text = "庆父收买曾受鞭刑的圉人荦。荦潜入党氏，刺杀公子般，自己也被家众乱刃斩死。" },
        { speaker = "", text = "季友识破庆父主谋，暂奔陈国。庆父立年仅八岁的公子启为闵公，与哀姜继续把持鲁政。" },
        { speaker = "鲁闵公", text = "庆父内乱日急，国内只有季友可以托付。还请齐侯作主，召季友回鲁辅政。" },
        { speaker = "齐桓公", text = "季友贤而忠，寡人命鲁国召回复相。庆父若敢阻挠，便是公然与齐国为敌。" },
        { speaker = "", text = "季友回国后，庆父仍不死心，又令卜齮伏刺闵公。国人罢市聚众，杀卜齮全家，庆父逃往莒国。" },
        { speaker = "", text = "季友带公子申返回鲁国。齐桓公遣高傒率甲士三千观变，确认公子申可以主社稷，遂拥立为鲁僖公。" },
        { speaker = "鲁僖公", text = "叔父两度安定鲁国，内除逆臣，外联齐国。今日莒人索取未曾立下的谢赂，又该如何处置？" },
        { speaker = "季友", text = "莒国贪赂逐走庆父，并未擒送逆贼，安得居功？臣愿领兵迎敌，不使新立之国受其胁迫。" },
        { speaker = "", text = "莒子之弟嬴拿率兵逼近鲁境。鲁国新君方立，若正面混战失利，人心必再度动摇。" },
        { speaker = "季友", text = "嬴拿多力却少谋。我先邀他阵前徒手相搏，鲁军守住两翼；他若倒下，莒军自然瓦解。" },
        { speaker = "公子行父", text = "父亲带上主公所赐的孟劳宝刀。若徒手久战不能取胜，孩儿会在阵旁提醒。" },
        { speaker = "嬴拿", text = "鲁国才经两次弑君，哪还有可战之兵？交出许诺莒国的宝器，我便退军。" },
        { speaker = "季友", text = "鲁国不以社稷贿人。你我今日在郦地决胜，胜者自可率军而归！" },
        { speaker = "军令", text = "季友战败则本关失败。击败嬴拿即可使莒军全体撤退；与其相邻时可触发历史单挑。" }
    },
    victory = {
        { speaker = "", text = "季友与嬴拿各自放下兵器，在两军阵前徒手相搏，一来一往五十余合，仍不分胜负。" },
        { speaker = "公子行父", text = "孟劳何在？父亲，孟劳何在！" },
        { speaker = "", text = "季友闻声醒悟，故意卖出破绽。嬴拿抢进一步，季友转身拔刀，削去其半边天灵。" },
        { speaker = "鲁军甲士", text = "嬴拿已死！莒军无主，正向北面溃逃！" },
        { speaker = "", text = "莒兵见主将倒地，不待交锋便各自奔逃。季友全胜回朝，鲁僖公亲自迎于郊外。" },
        { speaker = "鲁僖公", text = "叔父再安鲁国，又退莒军。寡人拜叔父为上相，以费邑和汶阳之田为采地。" },
        { speaker = "季友", text = "臣为社稷鸩叔牙、逼庆父自缢，实出不得已。请为二人立后，不绝桓公一脉。" },
        { speaker = "", text = "僖公准其所请。孟孙、叔孙与季孙三家由此并立，后世称为鲁国三桓。" },
        { speaker = "", text = "齐桓公又遣竖貂送哀姜归鲁。哀姜自知无颜入太庙，在夷地馆舍自缢。" },
        { speaker = "", text = "其后齐桓公在大泽见怪物而得病，齐野人皇子说那是委蛇，见者必霸天下，桓公闻言病愈。" },
        { speaker = "皇子", text = "齐侯尊王攘夷，使百姓不误农时，臣做一个治世农夫已经足够，不愿受爵为官。" },
        { speaker = "齐桓公", text = "任独者暗，任众者明。若无仲父广求贤者，寡人也听不到皇子这一番话。" },
        { speaker = "", text = "同年狄人先破邢国，又移兵伐卫。齐国北伐创伤未复，迟疑之间，卫国急报已经传来。" },
        { speaker = "下回预告", text = "第二十三回：卫懿公好鹤失政，狄军攻破卫国；齐桓公随后合诸侯南伐楚国。" }
    },
    defeat = {
        { speaker = "", text = "季友败于嬴拿，鲁军新立未稳，诸军闻讯动摇。" },
        { speaker = "鲁僖公", text = "叔父若有不测，鲁国再无人可以主持社稷。立即收兵守城！" }
    }
}

gstage = {
    title_id = "LiFieldDuel22", turn_limit = 16,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrrrrr",
            "rmmmFgggggggggFmmmr",
            "rmmFggggggggggeFmmr",
            "rmFgggffffffggggFmr",
            "rFgggffffffffggggFr",
            "rgggfffffffffffgggr",
            "rggffffffffffffgggr",
            "rggffffffffffffgggr",
            "rgggfffffffffffgggr",
            "rFggggffffffffgggFr",
            "rmFgggggggggggggFmr",
            "rmmFeggggggggggFmmr",
            "rmmmFgggggggggFmmmr",
            "rrrrrrrrrrrrrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 11}, hero = "JiYou22" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 1700 }
}

function on_deploy(game)
    game:appoint_hero("JiYou22", 1)
end

function on_begin(game)
    game:generate_unit("LuGuard22", 1, Enum.force.own, {6, 12})
    game:generate_unit("LuGuard22", 1, Enum.force.own, {5, 12})
    game:generate_unit("LuArcher22", 1, Enum.force.own, {7, 11})
    game:generate_unit("YingNa22", 1, Enum.force.enemy, {14, 2})
    game:generate_unit("JuGuard22", 1, Enum.force.enemy, {12, 3})
    game:generate_unit("JuGuard22", 1, Enum.force.enemy, {14, 4})
    game:generate_unit("JuGuard22", 1, Enum.force.enemy, {16, 3})
    game:generate_unit("JuArcher22", 1, Enum.force.enemy, {11, 4})
    game:generate_unit("JuArcher22", 1, Enum.force.enemy, {17, 4})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("YingNa22") then return Enum.status.victory end
    return Enum.status.undecided
end
