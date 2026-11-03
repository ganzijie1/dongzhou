pass_exchange_spoken = false
zhou_zhiqiao_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "LiKe25", "XunXi25" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "xiayang_gate", name = "下阳关门", position = {9, 5}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "xiayang_storehouse", name = "下阳府库", position = {6, 3}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "jin_forward_camp", name = "晋军行营", position = {9, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "spirit_powder", amount = 1 } } }
}

gstory = {
    chapter = "第二十五回·上",
    title = "智荀息假途灭虢 穷百里饲牛拜相",
    battle_title = "下阳破关",
    objective = "里克、荀息突破下阳关并击退舟之侨；二人任一被击退则失败",
    map_asset = "m042.png",
    intro = {
        { speaker = "", text = "葵邱会盟之后，晋献公病势日重，仍受骊姬与优施蛊惑，渐渐疏远世子申生而亲近奚齐。" },
        { speaker = "骊姬", text = "申生在曲沃施惠于民，又屡次领兵有功。若不先除去他，奚齐终究无法继位。" },
        { speaker = "优施", text = "世子慈仁而好洁，最怕背负不孝恶名。夫人可先假意称赞，再暗示他有夺国之心。" },
        { speaker = "", text = "骊姬夜半泣诉，借周平王代幽王之事诬陷申生。晋献公虽未全信，却已生出试探之意。" },
        { speaker = "骊姬", text = "赤狄皋落氏屡犯晋境，可命申生独自将兵。若败便可问罪；若胜，更能看出他是否得众。" },
        { speaker = "里克", text = "太子本应留国监政，怎可专制一军远征？主公此命，只会让国人怀疑储位将变。" },
        { speaker = "晋献公", text = "寡人有子九人，尚未决定谁为太子。申生既已数次从军，再领一军又有何妨？" },
        { speaker = "", text = "狐突写信劝申生避祸，申生却不肯违背父命，在稷桑击败皋落氏并献捷。骊姬的忌恨因此更深。" },
        { speaker = "", text = "晋国南境与虞、虢相邻。虞虢同姓相援，犹如唇齿；虢公丑却好兵骄纵，屡次侵扰晋境。" },
        { speaker = "荀息", text = "虞虢互为援助，强攻一国必受另一国夹击。可先以女乐惑虢，使其疏远忠臣，再买通犬戎扰境。" },
        { speaker = "", text = "虢公收下晋国女乐，日夜宴饮，不理朝政；忠臣舟之侨再三进谏，反被赶去镇守下阳关。" },
        { speaker = "", text = "犬戎受晋国贿赂侵扰虢境，先败于渭汭，继而倾国再来。虢公率主力与犬戎相持于桑田。" },
        { speaker = "晋献公", text = "戎虢正在相持，此时可否一举攻虢？" },
        { speaker = "荀息", text = "虞虢之交还没有断绝。臣愿献垂棘之璧、屈产之乘贿赂虞公，借道先取虢，再回师取虞。" },
        { speaker = "晋献公", text = "璧马都是晋国至宝，怎能轻易送人？" },
        { speaker = "荀息", text = "虞亡之后，璧仍归府、马仍归厩，不过暂寄在外。若舍不得诱饵，便钓不到两国。" },
        { speaker = "", text = "虞公见到璧马立即转怒为喜，答应借道。宫之奇以唇亡齿寒再三进谏，虞公始终不听。" },
        { speaker = "宫之奇", text = "虢国今日灭亡，灾祸明日必到虞国。晋国吞并同姓诸国，怎会唯独厚待我们？" },
        { speaker = "百里奚", text = "把嘉言献给愚人，如同把珠玉丢在大道。君上既不肯听，你再强谏只会招来杀身之祸。" },
        { speaker = "", text = "宫之奇带着全族离开虞国。百里奚不愿二人同走加重罪名，决定留下等待时机。" },
        { speaker = "里克", text = "虢都虽在上阳，下阳却是它的门户。虞军已经随我们进兵，只要破关，虢国便再无屏障。" },
        { speaker = "荀息", text = "舟之侨早知晋国图谋，绝不会轻易开关。弓手压制城头，步卒只从关门推进，不得攀越城墙。" },
        { speaker = "舟之侨", text = "我早说晋国女乐是钓饵，主公偏偏不听。今日虽被弃守下阳，仍要尽到守臣之责！" },
        { speaker = "军令", text = "城墙不可跨越，下阳关门可通行并补给。击退守门校尉和舟之侨即可迫使虢军放弃关城。" }
    },
    events = {
        { id = "xiayang_gate_exchange", trigger = "approach", position = {9, 5}, radius = 2,
          speaker = "舟之侨", text = "晋军果然借虞道而来！关门各队收缩，不要让他们打开通往上阳的道路！" }
    },
    victory = {
        { speaker = "下阳守门校尉", text = "关门守备已经崩溃！晋军从正面涌入，左右城楼也无法继续相援！" },
        { speaker = "舟之侨", text = "下阳已失，回到上阳只会被虢公问罪。里克若能保全关中军民，我愿归降晋国。" },
        { speaker = "里克", text = "放下兵器者一概不杀。晋军只取关城，不得侵扰百姓；舟之侨仍统旧部维持秩序。" },
        { speaker = "荀息", text = "下阳一破，虢国门户已经洞开。但虢公主力尚在桑田，此时不可急攻上阳。" },
        { speaker = "", text = "三年后，晋国再次借道。虢公在桑田听闻晋军破关，急忙班师，却被犬戎从后掩杀，只得退守上阳。" },
        { speaker = "", text = "里克筑起长围，从八月困至十二月。上阳柴薪断绝、士卒疲敝，城中百姓日夜号哭。" },
        { speaker = "里克", text = "虢公若肯出城，晋国可以保全其家眷与百姓；继续困守，只会让全城一同受苦。" },
        { speaker = "虢公丑", text = "先君曾为周王卿士，我不能向诸侯投降！今夜开城突围，前往京师求天子庇护。" },
        { speaker = "", text = "虢公乘夜携家眷奔往京师。里克没有追赶，入城安民，留下守军，并把三成府库和女乐献给虞公。" },
        { speaker = "虞公", text = "晋国果然守信，不但借我兵威灭虢，还分来许多财物。宫之奇所谓唇亡齿寒，不过危言耸听。" },
        { speaker = "荀息", text = "虞公已经完全失去戒心。里克暂称有病留兵城外，主公再约他到箕山较猎，便可乘虚取城。" },
        { speaker = "下关提示", text = "第二十五回·下：虞公倾城出猎，晋军趁虚袭破国都；虞军回师会在第四回合抵达。" }
    },
    defeat = {
        { speaker = "荀息", text = "下阳未破，虞军已经开始怀疑晋国真正的意图。假道之计再难继续。" },
        { speaker = "", text = "里克或荀息被击退，本关失败。" }
    }
}

gstage = {
    title_id = "CaptureXiayang25", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "mmmmmmmmmmmmmmmmmmm",
            "mmmmWWWWWWWWWWWmmmm",
            "mmmmWiiiiiiiiiWmmmm",
            "mmmmWibiiiiiiiWmmmm",
            "mmmmWiiiiiiiiiWmmmm",
            "mmmmWWWWWGWWWWWmmmm",
            "mmmgggfffwfffgggmmm",
            "mmgggffffwffffgggmm",
            "mgggFFFFfwfFFFFgggm",
            "mgggFFFFfwfFFFFgggm",
            "mggggffffwffffggggm",
            "mggggffffwffffggggm",
            "mggggffffeffffggggm",
            "mmmmgggggfffgggmmmm"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {8, 12}, hero = "LiKe25" },
            { position = {10, 12}, hero = "XunXi25" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2400 }
}

function on_deploy(game)
    game:appoint_hero("LiKe25", 1)
    game:appoint_hero("XunXi25", 1)
end

function on_begin(game)
    game:generate_unit("JinGuard25", 1, Enum.force.own, {7, 12})
    game:generate_unit("JinGuard25", 1, Enum.force.own, {11, 12})
    game:generate_unit("JinArcher25", 1, Enum.force.own, {8, 11})
    game:generate_unit("JinArcher25", 1, Enum.force.own, {10, 11})
    game:generate_unit("YuAuxiliary25", 1, Enum.force.ally, {6, 11})
    game:generate_unit("YuAuxiliary25", 1, Enum.force.ally, {12, 11})

    zhou_zhiqiao_id = game:generate_unit("ZhouZhiQiao25", 1, Enum.force.enemy, {9, 3})
    game:generate_unit("XiayangCaptain25", 1, Enum.force.enemy, {9, 5})
    game:generate_unit("GuoGuard25", 1, Enum.force.enemy, {8, 4})
    game:generate_unit("GuoGuard25", 1, Enum.force.enemy, {10, 4})
    game:generate_unit("GuoArcher25", 1, Enum.force.enemy, {7, 3})
    game:generate_unit("GuoArcher25", 1, Enum.force.enemy, {11, 3})
end

function on_update(game)
    if not pass_exchange_spoken and game:is_force_within(Enum.force.own, {9, 5}, 2) then
        pass_exchange_spoken = true
        game:push_cmd_speak(zhou_zhiqiao_id, "下阳是上阳门户，关门若失，虢国便无险可守！弓手集中射击中央道路！")
        game:push_cmd_speak(0, "城墙不能跨越！弓手压住城头，步卒沿中央道路夺门，不要堵住后队射界！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("XiayangCaptain25") and not game:has_unit("ZhouZhiQiao25") then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
