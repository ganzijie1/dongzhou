gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "YingKaoShu6", "GongZiLu6", "GaoQuMi6", "LuGongZiHui6" }

gsites = {
    {
        id = "allied_camp", name = "联军营寨", position = {20, 7},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "allied_camp_west", name = "联军营寨", position = {19, 7},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "allied_camp_northwest", name = "联军营寨", position = {19, 6},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "allied_camp_northeast", name = "联军营寨", position = {20, 6},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "gao_storehouse", name = "郜城宝物库", position = {18, 25},
        restore_hp = 25, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } }
    },
    { id = "gao_gate", name = "郜城城门", position = {20, 22}, restore_hp = 20, restore_mp = 5, rewards = {} },
    { id = "gao_west_gate", name = "郜城西门", position = {14, 25}, restore_hp = 20, restore_mp = 5, rewards = {} },
    { id = "gao_castle", name = "郜城城池", position = {20, 25}, restore_hp = 25, restore_mp = 15, rewards = {} }
}

gstory = {
    chapter = "第六回",
    title = "卫石碏大义灭亲 郑庄公假命伐宋",
    battle_title = "攻取郜城",
    objective = "突破郜城城门，击败全部宋军守备",
    map_asset = "m006.jpg",
    intro = {
        { speaker = "旁白", text = "五国联军围郑五日便各自撤兵。州吁虽号称得胜，卫国百姓仍不肯归心。" },
        { speaker = "石厚", text = "主公位势未安，唯有取得周天子承认，方可堵住国人之口。父亲必有良策。" },
        { speaker = "石碏", text = "陈侯深得周王信任。你们若亲往陈国，请陈侯代为奏请，君位自然可定。" },
        { speaker = "旁白", text = "石厚不知是计，欣然告知州吁。石碏却暗写密书，先遣心腹送往陈国。" },
        { speaker = "陈桓公", text = "州吁弑君自立，石厚助逆，卫国老臣请我代为除害。子针，可依计行事。" },
        { speaker = "子针", text = "臣已在太庙设下伏兵。待二人入庙行礼，便关闭庙门，一并拿下。" },
        { speaker = "旁白", text = "州吁、石厚抵达陈国，在太庙中猝然被擒。随行徒众见大势已去，顷刻逃散。" },
        { speaker = "石厚", text = "父亲！孩儿纵有大罪，也望念父子之情，留我一命！" },
        { speaker = "石碏", text = "州吁弑君，石厚从逆。若因私情废国家大义，我还有何面目立于卫国？" },
        { speaker = "右宰丑", text = "卫国公议已定。我奉命赴陈，诛杀逆贼州吁。" },
        { speaker = "獳羊肩", text = "石大夫不肯以家法掩国法。石厚由我行刑，使乱臣贼子同伏其罪。" },
        { speaker = "旁白", text = "州吁、石厚伏诛，卫人迎公子晋回国即位，是为卫宣公。石碏大义灭亲之名传于诸侯。" },
        { speaker = "卫宣公", text = "内乱虽平，卫国当休养生息，不可再为州吁旧党所误。" },
        { speaker = "旁白", text = "郑庄公记恨宋国助卫攻郑，意欲报复，先遣使者向陈国求和，却被陈桓公拒绝。" },
        { speaker = "郑庄公", text = "陈国不肯讲和，便遣兵略其边鄙。颍考叔若能胜陈，再将俘获送还，陈侯自会改意。" },
        { speaker = "颍考叔", text = "臣已击败陈军，俘获尽数送回。陈侯果然遣公子佗来盟，郑、陈从此息兵。" },
        { speaker = "旁白", text = "郑庄公随后入周朝见。周桓王仍怨郑国割取麦禾，只赐十车陈谷，礼数极为轻慢。" },
        { speaker = "周桓王", text = "郑伯既来朝觐，赐陈谷十车，退朝罢。" },
        { speaker = "周公黑肩", text = "郑伯且留步。王室尚有先王所遗彩缯，我取十二端相赠，稍全朝聘之礼。" },
        { speaker = "祭足", text = "有天子所赐彩缯，又有先王旧弓，便可称奉王命讨宋。诸侯不敢不从。" },
        { speaker = "郑庄公", text = "宋国久不朝周，又曾兴兵犯郑。传檄齐、鲁，就说我奉天子之命伐宋！" },
        { speaker = "齐僖公", text = "郑伯持有王赐彩缯，讨宋亦合我齐国之利。命夷仲年率军赴会。" },
        { speaker = "鲁公子翚", text = "鲁国也发兵相助。宋军若来争路，我先在老挑迎击，为联军打开通道。" },
        { speaker = "旁白", text = "鲁公子翚在老挑击退宋军。郑庄公命颍考叔、公子翚进攻郜城，高渠弥领兵接应。" },
        { speaker = "公子吕", text = "郜城东面城垣坚固，西门却可直入。各军合力夺门，不可让守军据城久守！" },
        { speaker = "郜城守将", text = "郜城乃宋国屏障。各门守军依城列阵，不得让联军踏入城中一步！" },
        { speaker = "军令", text = "由西南联军营寨出发，经西门攻入郜城，击败地图上的全部宋军守备。" }
    },
    victory = {
        { speaker = "颍考叔", text = "西门已破，郜城守军尽数败退！联军可以入城整顿。" },
        { speaker = "鲁公子翚", text = "郜城已下。公孙阏与夷仲年进攻防城，也传来捷报。" },
        { speaker = "郑庄公", text = "两城皆克，伐宋初战得胜。命三军严守营垒，防备宋国援兵。" },
        { speaker = "旁白", text = "正当联军乘胜之时，急报传来：宋大司马孔父嘉联合卫国右宰丑，趁虚攻入郑境。" },
        { speaker = "孔父嘉", text = "郑军主力在外，国内空虚。此时攻郑，正可迫使郑庄公从宋境撤兵。" },
        { speaker = "下回预告", text = "第七回：公孙阏争车射考叔，公子翚献谄贼隐公。" }
    },
    defeat = {
        { speaker = "公子吕", text = "城门前阵势已乱，继续强攻只会徒增伤亡。先退回营寨重整！" },
        { speaker = "旁白", text = "郜城尚未攻克，郑、齐、鲁联军必须重新部署攻城次序。" }
    }
}

gstage = {
    title_id = "CaptureGaoCity",
    turn_limit = 20,
    map = {
        blocked_edges = {
            { from = {12, 2}, to = {12, 3} }, { from = {13, 2}, to = {13, 3} },
            { from = {14, 2}, to = {14, 3} }, { from = {15, 2}, to = {15, 3} },
            { from = {11, 3}, to = {12, 3} }, { from = {11, 4}, to = {12, 4} },
            { from = {11, 5}, to = {12, 5} }, { from = {11, 6}, to = {12, 6} },
            { from = {22, 2}, to = {22, 3} }, { from = {23, 2}, to = {23, 3} },
            { from = {24, 2}, to = {24, 3} }, { from = {25, 2}, to = {25, 3} },
            { from = {11, 8}, to = {12, 8} }, { from = {11, 9}, to = {12, 9} },
            { from = {11, 10}, to = {12, 10} },
            { from = {12, 10}, to = {12, 11} }, { from = {13, 10}, to = {13, 11} },
            { from = {14, 10}, to = {14, 11} }, { from = {15, 10}, to = {15, 11} },
            { from = {22, 10}, to = {22, 11} }, { from = {23, 10}, to = {23, 11} },
            { from = {24, 10}, to = {24, 11} }, { from = {25, 10}, to = {25, 11} },
            { from = {14, 21}, to = {14, 22} }, { from = {15, 21}, to = {15, 22} },
            { from = {16, 21}, to = {16, 22} }, { from = {17, 21}, to = {17, 22} },
            { from = {18, 21}, to = {18, 22} }, { from = {19, 21}, to = {19, 22} },
            { from = {21, 21}, to = {21, 22} }, { from = {22, 21}, to = {22, 22} },
            { from = {23, 21}, to = {23, 22} }, { from = {24, 21}, to = {24, 22} },
            { from = {25, 21}, to = {25, 22} },
            { from = {13, 22}, to = {14, 22} }, { from = {13, 23}, to = {14, 23} },
            { from = {13, 24}, to = {14, 24} }, { from = {13, 26}, to = {14, 26} },
            { from = {13, 27}, to = {14, 27} }
        },
        size = {26, 28},        terrain = {
            "FFFFFFFFFFFFFFFfffffffffff",
            "FFFFFFFFFFFFFFFfffffffffff",
            "FFFFFFFFFFFFFFFfffffffffff",
            "FFFFFFFFFFFFPPPPffffffPPPP",
            "FFFFFFFFFFffPffeffffffeffP",
            "FFFFFFFfffffPfeeffbffffffP",
            "FFFFFfffffffPffffffeeffffP",
            "FFFFfffffffffffffffeefeeef",
            "FFFfffffffffPfffffffffeeeP",
            "FFffffffffffPffffffffffffP",
            "FFFFFffffFFFPPPPFfffffPPPP",
            "FFFFFffFFFFFFFFFFfffffffff",
            "FFFffffFFFFFFFFFFFFFFFFfff",
            "FffffffFFFFFFFFFFFFFFFFfff",
            "ffffffffffFFFFFf~~~ff~~~ff",
            "fffffffffffffff~~~~ff~~~~f",
            "fffffffffffff~~~~~~ff~~~~~",
            "ffffffffffff~~~~~FFFFFF~~~",
            "fffffffffff~~~~FFFFFFFFFF~",
            "fffffffff~~~~~FFFFFFFFffff",
            "ff~~~ff~~~~~~fffffffffffff",
            "f~~~~ff~~~~~ffffffffffffff",
            "~~~fffffffffffWWWWWWGWWWWW",
            "~~ffffffffffffWiiiiiiiiiii",
            "~fffffffffffffWiiiiiiiiiii",
            "ffffffffffffffGiiibiCiiiii",
            "ffffffffffffffWiiiiiiiiiii",
            "ffffffffffffffWiiiiiiiiiii"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {20, 6}, hero = "YingKaoShu6" },
            { position = {19, 7}, hero = "GongZiLu6" },
            { position = {19, 6}, hero = "GaoQuMi6" },
            { position = {20, 7}, hero = "LuGongZiHui6" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 360 }
}

function on_deploy(game)
    game:appoint_hero("YingKaoShu6", 1)
    game:appoint_hero("GongZiLu6", 1)
    game:appoint_hero("GaoQuMi6", 1)
    game:appoint_hero("LuGongZiHui6", 1)
end

function on_begin(game)
    game:generate_unit("GaoCityCommander6", 1, Enum.force.enemy, {20, 25})
    game:generate_unit("SongDefender", 1, Enum.force.enemy, {20, 22})
    game:generate_unit("SongDefender", 1, Enum.force.enemy, {14, 25})
    game:generate_unit("SongDefender", 1, Enum.force.enemy, {16, 23})
    game:generate_unit("SongDefender", 1, Enum.force.enemy, {23, 23})
    game:generate_unit("SongDefender", 1, Enum.force.enemy, {20, 24})
    game:generate_unit("SongArcher", 1, Enum.force.enemy, {16, 24})
    game:generate_unit("SongArcher", 1, Enum.force.enemy, {18, 23})
    game:generate_unit("SongArcher", 1, Enum.force.enemy, {22, 24})
    game:generate_unit("SongArcher", 1, Enum.force.enemy, {23, 25})
end

function on_update(game) end

function on_victory(game)
end

function on_defeat(game)
end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then
        return Enum.status.defeat
    end
    if game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end

