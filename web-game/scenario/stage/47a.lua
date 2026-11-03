trap_triggered = false
ambush_ready = false

gsupply_enabled = false
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ShuSunDeChen47", "FuFuZhongSheng47" }
gduel_enabled = false
gevents_enabled = true
gduels = {
    {
        attacker = "FuFuZhongSheng47", defender = "QiaoRu47", exp = 100, outcome = "kill",
        attacker_speech = "长翟已经陷入雪坑，铜头铁额也护不住咽喉！",
        defender_speech = "小小陷坑也想困住我？待我跃出坑来，踏平鲁军！",
        result_speech = "富父终甥挺戈直刺侨如咽喉，长翟倒在深坑之中。",
        text = "原著明载侨如坠入陷坑，富父终甥以戈刺其喉而杀之。"
    }
}
gsites = {}

gstory = {
    chapter = "第四十七回·上",
    title = "弄玉吹箫双跨凤 赵盾背秦立灵公",
    battle_title = "雪夜陷长翟",
    objective = "让富父终甥把侨如引到地图中央（18，13）两格范围内。陷坑触发前侨如不可被击退；触发后伏兵出现，富父终甥与侨如相邻可发动史实单挑。击杀侨如并把翟军普通部队压至三人以内即可获胜，我方两名具名将领任一被击退则失败。",
    map_asset = "m073.png",
    intro = {
        { speaker = "", text = "秦穆公称霸西戎以后，周襄王赐金鼓相贺。繇余病卒，公孙枝告老，穆公把国政逐渐交给孟明视。" },
        { speaker = "秦穆公", text = "寡人年事已高，西戎既定，兵革之事可稍息。孟明历经败绩而能自强，今后国政由你用心料理。" },
        { speaker = "", text = "穆公幼女弄玉善吹碧玉笙，声如凤鸣。她立誓只嫁能以笙箫相和之人，穆公遍访诸国，始终不得。" },
        { speaker = "弄玉", text = "若不能以音律相知，虽王侯之子也非所愿。昨夜西南箫声与笙声相和，梦中人说中秋必来相见。" },
        { speaker = "", text = "孟明依梦中形貌登太华山，在明星岩寻到羽冠鹤氅的萧史，将他迎入凤台。" },
        { speaker = "萧史", text = "臣只善吹箫，不通朝政。箫声本取凤凰清鸣，若能与公主玉笙相和，便是前缘。" },
        { speaker = "", text = "萧史奏第一曲清风徐来，第二曲彩云四合，第三曲白鹤、孔雀与百鸟群集。穆公遂把弄玉许配给他。" },
        { speaker = "秦穆公", text = "今日正是中秋，月圆于上，人圆于下。此乃天缘，便在凤楼成婚。" },
        { speaker = "", text = "半年后，夫妻月下合奏，紫凤与赤龙降临凤台。萧史乘龙、弄玉跨凤，自此飞入太华云间。" },
        { speaker = "", text = "穆公自此厌言兵革，三年后梦见萧史与弄玉来迎，醒后染疾而薨。太子罃即位，是为秦康公。" },
        { speaker = "", text = "秦国依西戎旧俗，以一百七十七人殉葬，贤臣奄息、仲行、鍼虎也在其中。国人为三良作《黄鸟》哀悼。" },
        { speaker = "", text = "晋国方面，赵衰、栾枝、先且居、胥臣相继去世。襄公重整三军，先任狐射姑为中军元帅，又听阳处父进言，改以赵盾统帅。" },
        { speaker = "臾骈", text = "为帅贵在和众。刚愎自矜正是成得臣败于城濮的根由，请狐帅虚心询问诸将。" },
        { speaker = "狐射姑", text = "号令初下，你便在军前乱言！拖下去鞭打一百，以肃军纪。" },
        { speaker = "", text = "狐射姑被改为赵盾副将后怀恨阳处父。襄公去世，又因拥立公子乐与赵盾争权，赵盾派公孙杵臼在路上杀死公子乐。" },
        { speaker = "", text = "狐鞫居趁阳处父宿于郊外，夜间越墙将其刺杀。赵盾查明凶手后斩狐鞫居，狐射姑惧罪逃往白暾所在的翟国。" },
        { speaker = "", text = "翟国有长人侨如，身高一丈五尺，力举千钧。白暾命他率兵侵鲁，鲁文公遣叔孙得臣迎战。" },
        { speaker = "叔孙得臣", text = "侨如铜头铁额，正面硬战只会徒损士卒。今夜冻雾沉重，天明前必有大雪，可依富父终甥之计诱敌。" },
        { speaker = "富父终甥", text = "中央要道已掘九处深坑，上铺草蓐和浮土。大雪会抹平痕迹，我先劫寨诈败，引侨如沿预定路线追来。" },
        { speaker = "侨如", text = "鲁军不堪一击，前队已经向东南逃走！我亲自追杀，莫让叔孙得臣逃回曲阜。" },
        { speaker = "军令", text = "先以富父终甥接近中央陷坑诱敌，不必攻击无敌的侨如。侨如进入（18，13）两格范围后陷坑与两翼伏兵同时触发；雪地中的树林、山地会增加移动消耗。" }
    },
    events = {
        { id = "snow_trap", trigger = "approach", position = {18,13}, radius = 2, speaker = "富父终甥", text = "侨如已经踏入覆雪陷坑！两翼伏兵尽起，封住翟军退路！" }
    },
    victory = {
        { speaker = "", text = "侨如只顾追赶富父终甥，踏破草蓐坠入深坑。叔孙得臣伏兵四起，翟军在风雪中阵脚大乱。" },
        { speaker = "富父终甥", text = "长翟虽能举千钧，陷在深坑也无法施展。我从坑沿直刺咽喉，为鲁国除此强敌！" },
        { speaker = "", text = "侨如被刺死后，叔孙得臣把尸体装上大车。见者都惊骇，以为古代防风氏巨骨重现。" },
        { speaker = "", text = "叔孙得臣适逢长子出生，便为他取名叔孙侨如，以记此次军功。鲁国随后联合齐、卫继续进攻翟地。" },
        { speaker = "", text = "白暾兵败身死，翟国覆亡。狐射姑转投赤翟潞国大夫酆舒，赵盾仍念狐氏从亡旧功，命臾骈护送其妻子与财物出境。" },
        { speaker = "臾骈", text = "狐射姑昔日虽鞭我百下，元帅如今托我护送其家。乘人之危非仁，违令泄愤非智，谁也不得侵夺一物。" },
        { speaker = "", text = "狐射姑听说臾骈毫无报复，叹息自己有贤人而不能识。赵盾也由此更加器重臾骈。" },
        { speaker = "军令", text = "雪夜陷长翟完成，获得6200金币。侨如依原著阵亡；下一关转入晋国迎立之争与令狐夜袭。" }
    },
    defeat = {
        { speaker = "", text = "陷坑尚未合围，鲁军具名将领先被击退。侨如识破伏兵路线，鲁军只能退回城中。" }
    }
}

gstage = {
    title_id = "SnowTrapGiantDi47", turn_limit = 22,
    map = { blocked_edges = {}, size = {36, 26}, terrain = {
        "FgFffFgFffFgFffFgFffFgFwwFwFffFgFffF",
        "FffFgFffFgFffFgFffFgFffFwFwwFgFffFgF",
        "fFgFffFgFffFgFffFgFffFwFwwFgFffFgFff",
        "gFffmgfffmgfffmgfffmgfwwmwwffmgfffFg",
        "ffFgfffmgfffmgfffmgffwmwwwfmgfffmgFf",
        "FgFffggfffggfffggfffgwwwwwgfffggfffF",
        "FffmgfffggfffggfffggwwwwwfffggfffFgF",
        "fFgfffggfffggfffggffwwwwwfggfffmgFff",
        "gFffmgfffggfffggfffwwwwwggfffggfffFg",
        "ffFgfffggfffggfffggwwwwwfffggfffmgFf",
        "FgFffggfffggfffggfwwwwwffggfffggfffF",
        "FffmgfffggfffggfffwwwwwggfffggfffFgF",
        "fFgfffggfffggfffgwwwwwgfffggfffmgFff",
        "gFffmgfffggfffggfwwwwwffggfffggfffFg",
        "ffFgfffggfffggffwwwwwfggfffggfffmgFf",
        "FgFffggfffggfffgwwwwwgfffggfffggfffF",
        "FffmgfffggfffggwwwwwfffggfffggfffFgF",
        "fFgfffggfffggffwwwwwfggfffggfffmgFff",
        "gFffmgfffggfffwwwwwggfffggfffggfffFg",
        "ffFgfffggfffggwwwwwfffggfffggfffmgFf",
        "FgFffggfffggfwwwwwffggfffggfffggfffF",
        "FffmgfffmgfffmwwwwmgfffmgfffmgfffFgF",
        "fFgfffmgfffmwwwwmgfffmgfffmgfffmgFff",
        "gFffFgFffFgFwwFwFffFgFffFgFffFgFffFg",
        "ffFgFffFgFfwFwFwfFgFffFgFffFgFffFgFf",
        "FgFffFgFffFwFwwFgFffFgFffFgFffFgFffF"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {27,18}, hero = "ShuSunDeChen47" },
        { position = {25,16}, hero = "FuFuZhongSheng47" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6200 }
}

local function generate_many(game, hero, positions, force)
    for _, position in ipairs(positions) do game:generate_unit(hero, 1, force, position) end
end

function on_deploy(game)
    for _, hero in ipairs(gcommanders) do game:appoint_hero(hero, 1) end
end

function on_begin(game)
    game:generate_unit("QiaoRu47", 1, Enum.force.enemy, {8,7})
    game:set_unit_invulnerable("QiaoRu47", true)
    generate_many(game, "DiGuard47", {{6,6},{10,6},{5,9},{11,9},{7,11},{12,10}}, Enum.force.enemy)
    generate_many(game, "DiCavalry47", {{7,5},{9,8},{5,12},{13,8}}, Enum.force.enemy)
    generate_many(game, "DiArcher47", {{4,7},{11,5},{4,10},{13,11}}, Enum.force.enemy)
    generate_many(game, "LuGuard47", {{26,18},{28,17},{29,19}}, Enum.force.own)
    generate_many(game, "LuArcher47", {{24,19},{27,20}}, Enum.force.own)
end

local function di_regular_alive(game)
    return game:get_num_units_alive("DiGuard47") + game:get_num_units_alive("DiCavalry47")
        + game:get_num_units_alive("DiArcher47")
end

function on_update(game)
    if not trap_triggered and game:is_unit_within("QiaoRu47", {18,13}, 2) then
        trap_triggered = true
        gduel_enabled = true
        game:set_unit_invulnerable("QiaoRu47", false)
        game:push_cmd_speak(0, "侨如踏破草蓐坠入深坑！叔孙得臣伏兵从雪地两翼杀出，富父终甥可以与其相邻发动单挑。")
        generate_many(game, "LuGuard47", {{14,11},{14,15},{21,11},{21,15}}, Enum.force.own)
        generate_many(game, "LuArcher47", {{15,9},{15,17},{22,10},{22,16}}, Enum.force.own)
        ambush_ready = true
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if ambush_ready and not game:has_unit("QiaoRu47") and di_regular_alive(game) <= 3 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end
