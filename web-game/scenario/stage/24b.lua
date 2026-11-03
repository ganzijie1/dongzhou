relief_clash_spoken = false
chu_king_id = -1
ziwen_id = -1

gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = { "QiHuanGong24", "GuanYiWu24", "WangZiChengFu24" }
gduel_enabled = false
gduels = {}

gsites = {
    { id = "xu_castle", name = "许城城池", position = {9, 1}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "xu_storehouse", name = "许城府库", position = {13, 2}, restore_hp = 15, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 }, { item = "spirit_powder", amount = 1 } } },
    { id = "xu_south_gate", name = "许城南门", position = {9, 4}, restore_hp = 15, restore_mp = 5, rewards = {} },
    { id = "qi_relief_camp", name = "齐军援营", position = {4, 12}, restore_hp = 20, restore_mp = 15,
      rewards = { { item = "medicine", amount = 1 } } },
    { id = "allied_relief_camp", name = "诸侯援营", position = {14, 12}, restore_hp = 20, restore_mp = 10,
      rewards = { { item = "medicine", amount = 1 } } }
}

gstory = {
    chapter = "第二十四回·下",
    title = "盟召陵礼款楚大夫 会葵邱义戴周天子",
    battle_title = "许城解围",
    objective = "保护许僖公并击退楚成王；齐桓公、管仲或许僖公被击退则失败",
    map_asset = "m041.png",
    intro = {
        { speaker = "", text = "郑文公逃离首止后暗通楚国。齐桓公率诸侯围攻新密，楚成王依子文之计亲自转兵围许。" },
        { speaker = "令尹子文", text = "许穆公病死在召陵军中，齐侯最怜许国。大王攻许，诸侯必定舍郑来救，新密之围便会自解。" },
        { speaker = "楚成王", text = "此战不求攻灭许国，只要迫使齐军撤离郑境。各部围住南门，准备迎击诸侯援军。" },
        { speaker = "许僖公", text = "先君抱病随齐侯伐楚，未回国便卒于军中。如今楚军报复而来，许国绝不能辱没先君之志。" },
        { speaker = "许国守将", text = "北面城墙依山完整，楚军主力都在南门外。臣等坚守城内，等待齐国诸侯军抵达。" },
        { speaker = "", text = "齐桓公得到急报，当即从新密撤围。齐军先行，宋、鲁、陈、卫等诸侯随后分道赶往许城。" },
        { speaker = "齐桓公", text = "许国最先响应伐楚，穆公又卒于军中。今日若不能救许，召陵盟约还有什么信用？" },
        { speaker = "管仲", text = "楚军志在解郑，不会死守。集中兵力攻击楚王中军，只要迫其后退，许城之围自然解除。" },
        { speaker = "王子成父", text = "我率骑兵切断楚军东侧退路；弓手沿中路推进，不要堵住步卒接近楚王的道路。" },
        { speaker = "楚成王", text = "齐侯来得果然快。楚军列阵城南，先挫其前锋；若诸侯大队齐至，再从容退回汉南。" },
        { speaker = "令尹子文", text = "召陵刚刚结盟，不宜再开全面战端。大王若受伤，诸部立即收兵，不得恋战。" },
        { speaker = "军令", text = "许城墙不可跨越，南门可以通行并补给。保护城内许僖公，击退楚成王即可使楚军全体撤退。" }
    },
    victory = {
        { speaker = "楚成王", text = "诸侯后军已经接近，围许解郑之计也已达成。楚军依次后撤，不必在城下与八国决战！" },
        { speaker = "令尹子文", text = "收拢两翼，退回汉南。今日既保全郑国，又没有破坏召陵盟书，已经足够。" },
        { speaker = "许僖公", text = "先君以病躯赴召陵，今日盟主又从新密驰援。许国上下永不忘齐侯之德。" },
        { speaker = "齐桓公", text = "楚军既退，诸侯不得追入楚境。回师整顿，再问郑国为何反复背盟。" },
        { speaker = "", text = "次年齐军再次伐郑。辕涛涂写信揭发申侯反复卖国，郑文公悔不听孔叔，斩申侯并函首请罪。" },
        { speaker = "孔叔", text = "申侯已经伏诛，郑国愿恢复与齐国的旧好，请盟主停止攻城，使百姓免受兵祸。" },
        { speaker = "管仲", text = "郑国既肯悔过，不必再战。诸侯移师宁母听命，以盟约重新约束郑国。" },
        { speaker = "", text = "郑文公仍顾忌周惠王密命，只派世子华赴宁母。子华竟想借齐侯之力除掉孔叔等三良，以郑为齐国附庸。" },
        { speaker = "管仲", text = "子背父命是不礼，借友邦谋乱是不信。三良素得郑人拥戴，盟主绝不能为一名世子破坏礼信。" },
        { speaker = "", text = "齐侯拒绝子华并泄露其谋。郑文公将子华囚杀，公子臧也死于逃亡途中，孔叔再赴齐国致谢。" },
        { speaker = "", text = "周惠王病危，世子郑担心惠后与叔带作乱，命王子虎向齐国告急。惠王死后，八国大夫入周共立世子，是为周襄王。" },
        { speaker = "周襄王", text = "齐侯翼戴王储、安定周室，朕命太宰周公孔赐胙，以彰伯舅尊王之功。" },
        { speaker = "", text = "齐桓公大会诸侯于葵邱。宋襄公墨衰赴会，齐侯认为他贤而守礼，便把公子昭托付给他。" },
        { speaker = "齐桓公", text = "寡人诸子皆庶出，愿立贤者公子昭。异日齐国若有内乱，请宋公主持，使他继承社稷。" },
        { speaker = "宋襄公", text = "君侯以国事相托，兹父虽不敢自任，若真有危难，必不负今日之言。" },
        { speaker = "", text = "葵邱坛上设天王虚位。周公孔赐下祭肉，齐桓公不敢受免拜之礼，仍疾趋下阶再拜，诸侯无不叹服。" },
        { speaker = "管仲", text = "盟书重申五禁：不得壅塞水源、阻绝粮运、擅换储君、以妾为妻、使妇人干预国政。" },
        { speaker = "", text = "桓公志得意满，又想封禅泰山。管仲以祥瑞未至、蓬蒿反盛婉言劝止，才没有越过天子礼制。" },
        { speaker = "鲍叔牙", text = "主公宫室服御日益近于王者，仲父又筑三归台替他分谤。霸业极盛之时，更应警惕骄心。" },
        { speaker = "", text = "晋献公赶来葵邱时会盟已经结束。周公孔说齐侯盛极将衰，献公只得西归，途中染病，回国不久便去世。" },
        { speaker = "下回预告", text = "第二十五回：晋献公身后骊姬乱政渐起，荀息又将假道于虞、借兵灭虢。" }
    },
    defeat = {
        { speaker = "许僖公", text = "盟军尚未击退楚王，许城中军已经崩溃。先君在召陵结下的盟约，今日竟不能保全许国！" },
        { speaker = "", text = "齐桓公、管仲或许僖公被击退，本关失败。" }
    }
}

gstage = {
    title_id = "ReliefOfXu24", turn_limit = 18,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "mmmmWWWWWWWWWWWWmmm",
            "mmmmWiiiiCiiiiiWmmm",
            "mmmmWiiiiiiiibiWmmm",
            "mmmmWiiiiiiiiiiWmmm",
            "mmmmWWWWWGWWWWWWmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmggggggwggggggmmm",
            "mmmgeggggwggggegmmm",
            "mmmggggggwggggggmmm"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {4, 12}, hero = "QiHuanGong24" },
            { position = {5, 12}, hero = "GuanYiWu24" },
            { position = {6, 11}, hero = "WangZiChengFu24" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 2300 }
}

function on_deploy(game)
    game:appoint_hero("QiHuanGong24", 1)
    game:appoint_hero("GuanYiWu24", 1)
    game:appoint_hero("WangZiChengFu24", 1)
end

function on_begin(game)
    game:generate_unit("CoalitionGuard24", 1, Enum.force.own, {3, 11})
    game:generate_unit("CoalitionArcher24", 1, Enum.force.own, {7, 12})
    game:generate_unit("CoalitionGuard24", 1, Enum.force.own, {14, 12})
    game:generate_unit("CoalitionArcher24", 1, Enum.force.own, {15, 11})
    game:generate_unit("XuXiGong24", 1, Enum.force.ally, {9, 1})
    game:generate_unit("XuGuard24", 1, Enum.force.ally, {8, 3})
    game:generate_unit("XuGuard24", 1, Enum.force.ally, {10, 3})
    game:generate_unit("XuArcher24", 1, Enum.force.ally, {7, 2})
    game:generate_unit("XuArcher24", 1, Enum.force.ally, {11, 2})
    chu_king_id = game:generate_unit("ChuChengWang24", 1, Enum.force.enemy, {9, 8})
    ziwen_id = game:generate_unit("ZiWen24", 1, Enum.force.enemy, {11, 8})
    game:generate_unit("DouLian24", 1, Enum.force.enemy, {7, 8})
    game:generate_unit("ChuGuard24", 1, Enum.force.enemy, {8, 7})
    game:generate_unit("ChuGuard24", 1, Enum.force.enemy, {10, 7})
    game:generate_unit("ChuGuard24", 1, Enum.force.enemy, {6, 7})
    game:generate_unit("ChuArcher24", 1, Enum.force.enemy, {7, 9})
    game:generate_unit("ChuArcher24", 1, Enum.force.enemy, {11, 9})
end

function on_update(game)
    if not relief_clash_spoken
       and (game:get_turn_current() >= 3 or game:is_force_within(Enum.force.own, {9, 8}, 3)) then
        relief_clash_spoken = true
        game:push_cmd_speak(chu_king_id, "齐侯前锋已经逼近中军，诸侯后队也在路上。楚军不可被拖入久战！")
        game:push_cmd_speak(ziwen_id, "两翼保持退路。若大王受伤，立即解除许城之围，依次撤回汉南！")
        game:push_cmd_speak(0, "楚军阵形已经动摇！集中攻击楚王中军，不必在侧翼消耗兵力！")
    end
end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders or not game:has_unit("XuXiGong24") then
        return Enum.status.defeat
    end
    if not game:has_unit("ChuChengWang24") then return Enum.status.victory end
    return Enum.status.undecided
end