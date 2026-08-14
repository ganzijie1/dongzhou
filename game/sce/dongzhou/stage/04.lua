gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "ZhengZhuangGong", "GongZiLu" }

gsites = {
    {
        id = "zheng_camp", name = "郑军营寨", position = {2, 10},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "gong_storehouse", name = "共城府库", position = {10, 0},
        restore_hp = 10, restore_mp = 10,
        rewards = {
            { item = "medicine", amount = 1 },
            { item = "spirit_powder", amount = 1 }
        }
    },
    { id = "gong_castle", name = "共城城池", position = {9, 0}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "gong_middle_gate", name = "共城中门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "gong_gate", name = "共城南门", position = {9, 7}, restore_hp = 20, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第四回·下",
    title = "秦文公郊天应梦 郑庄公掘地见母",
    battle_title = "郑伯克段",
    objective = "攻破共城，平定共叔段之乱",
    map_asset = "m004.jpg",
    intro = {
        { speaker = "旁白", text = "周平王定都洛邑，四方诸侯入朝称贺。秦襄公辞归时，平王将被犬戎占据的岐丰之地许给秦国。" },
        { speaker = "周平王", text = "卿若能驱逐犬戎，岐丰之地尽归于秦，永作王室西藩。" },
        { speaker = "旁白", text = "秦襄公整军西征，不出三年便击杀犬戎大将孛丁、满也速，犬戎主远遁西荒，秦国由此开地千里。" },
        { speaker = "旁白", text = "襄公死后，秦文公继位。文公梦见黄蛇从天而降，化作童子，自称上帝之子，命秦主西方之祀。" },
        { speaker = "秦文公", text = "既是上帝垂命，便在鄜邑筑台立白帝庙，又于陈仓立陈宝祠，以镇西土。" },
        { speaker = "旁白", text = "秦、鲁相继越礼郊天，周室无力禁止，诸侯从此各擅大权，天下渐入纷争。" },
        { speaker = "旁白", text = "郑武公死后，长子寤生继位，是为郑庄公。武姜偏爱次子段，逼庄公将大城京邑封给他。" },
        { speaker = "祭足", text = "京城地广民众，若封给共叔段，国中便如有二君，日后必成大患。" },
        { speaker = "郑庄公", text = "母命难违。段若不显叛逆，我便不能正其罪；且任他骄纵，待其自取灭亡。" },
        { speaker = "旁白", text = "共叔段收取西鄙、北鄙兵赋，又夺鄢与廪延，暗中与武姜约定袭取郑都。" },
        { speaker = "公子吕", text = "主公可佯称入周。臣伏兵京城附近，待段出兵，先夺其巢；主公再从廪延夹击。" },
        { speaker = "旁白", text = "庄公截获武姜密信，将计就计。共叔段倾巢而出后，公子吕乘城中火起，一举夺回京城。" },
        { speaker = "共叔段", text = "京城已失，军心又散！先退往共城据守，再图后计。" },
        { speaker = "军令", text = "率郑军从南面城门攻入共城，击败共叔段及全部叛军。" }
    },
    victory = {
        { speaker = "共叔段", text = "姜氏误我！事到如今，我还有何面目再见兄长？" },
        { speaker = "旁白", text = "共城顷刻被攻破。共叔段自刎而死，庄公抚尸痛哭，随后将武姜迁往颍地。" },
        { speaker = "郑庄公", text = "不及黄泉，无相见也！话虽出口，寡人心中又岂能不念母亲？" },
        { speaker = "颍考叔", text = "母虽不母，子不可以不子。主公若受黄泉之誓所困，可掘地至泉，在地室中相见。" },
        { speaker = "旁白", text = "颍考叔命壮士掘地十余丈，于泉旁建成地室，先将武姜迎入其中。" },
        { speaker = "郑庄公", text = "寤生不孝，久缺定省，求国母恕罪！" },
        { speaker = "武姜", text = "这是老身之罪，与你无关。今日母子重逢，前怨尽消。" },
        { speaker = "旁白", text = "母子抱头痛哭，一同升梯出穴。庄公亲自为武姜执辔，国人无不称颂颍考叔成全孝道。" },
        { speaker = "旁白", text = "共叔段之子公孙滑逃往卫国借兵。卫桓公闻讯兴师伐郑，新的战事已经逼近。" },
        { speaker = "下回预告", text = "第五回：宠虢公周郑交质，助卫逆鲁宋兴兵。" }
    },
    defeat = {
        { speaker = "公子吕", text = "共城虽小，叛军却在负隅死守。今日攻势受挫，暂退整军！" },
        { speaker = "旁白", text = "若让共叔段重新聚拢军心，郑国将再陷内乱。" }
    }
}

gstage = {
    title_id = "ZhengDefeatsDuan",
    turn_limit = 20,
    map = {
        blocked_edges = {},
        size = {19, 14},
        terrain = {
            "ggWiiiiiiCbiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWiWWWWWGWWWWWiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWiiiiiiiiiiiiiWgg",
            "ggWWWWWWWGWWWWWWWgg",
            "gggggggggffffffffff",
            "ggggfffffffffffffff",
            "ggeefffffffffffffff",
            "ggggfffffffffffffff",
            "ggggggfffffffffffff",
            "ggggggggggggggggggg"
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {2, 10}, hero = "ZhengZhuangGong" },
            { position = {4, 11}, hero = "GongZiLu" },
            { position = {2, 12}, hero = "ZhengVanguard" },
            { position = {5, 9}, hero = "ZhengVanguard2" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 320 }
}

function on_deploy(game)
    game:appoint_hero("ZhengZhuangGong", 1)
    game:appoint_hero("GongZiLu", 1)
    game:appoint_hero("ZhengVanguard", 1)
    game:appoint_hero("ZhengVanguard2", 1)
end

function on_begin(game)
    game:generate_unit("GongShuDuan", 1, Enum.force.enemy, {9, 0})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {4, 2})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {6, 2})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {12, 2})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {14, 2})
game:generate_unit("DuanGuard", 1, Enum.force.enemy, {9, 4})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {9, 7})
    game:generate_unit("DuanGuard", 1, Enum.force.enemy, {9, 6})
    game:generate_unit("DuanArcher", 1, Enum.force.enemy, {7, 1})
    game:generate_unit("DuanArcher", 1, Enum.force.enemy, {11, 1})
    game:generate_unit("DuanArcher", 1, Enum.force.enemy, {7, 5})
    game:generate_unit("DuanArcher", 1, Enum.force.enemy, {11, 5})
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
