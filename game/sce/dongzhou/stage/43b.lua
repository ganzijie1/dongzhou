east_gate_reached = false
qin_gate_reached = false
qin_audience = false
detected = false
gally_hold_position = true

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 1 }
}
gcommanders = { "ZhuZhiWu43" }
gevents_enabled = true
gsites = {
    { id = "zheng_palace_west", name = "郑城城池", position = {16, 7}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "zheng_palace", name = "郑城城池", position = {18, 7}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "zheng_palace_east", name = "郑城城池", position = {20, 7}, restore_hp = 25, restore_mp = 15, rewards = {} },
    { id = "qin_command", name = "秦军行营", position = {31, 11}, restore_hp = 20, restore_mp = 10, rewards = {} },
    { id = "qin_camp", name = "秦军行营", position = {31, 15}, restore_hp = 20, restore_mp = 10, rewards = {} }
}

gstory = {
    chapter = "第四十三回·下",
    title = "老烛武缒城说秦",
    battle_title = "夜缒说秦",
    objective = "只控制烛之武从郑城东门缒下，经东郊进入秦营并接近秦穆公。不得攻击任何单位；进入晋军巡骑两格警戒范围或十二回合内未抵达秦营均失败。",
    map_asset = "m066.png",
    intro = {
        { speaker = "", text = "休兵一年后，晋文公以郑国反复亲楚为由出兵。秦穆公依照围许时的互救之约亲率秦军会师，两国先破郊关，再夹围郑都：晋军驻西面的函陵，秦军驻东面的氾南。" },
        { speaker = "郑文公", text = "两国大军压境，西门是晋营，东门是秦营。郑国兵少城孤，若正面交战，不过数日便要城破。诸卿可有退兵之策？" },
        { speaker = "叔詹", text = "强弱既不相当，只能以利害离其同盟。必须有人越过城墙，先见秦君，再使秦晋彼此生疑。" },
        { speaker = "佚之狐", text = "臣所识之人中，唯烛之武能把天下形势说到秦君心里。他年事虽高，久居下位，却有退百万师的口舌。" },
        { speaker = "郑文公", text = "寡人从前不能早用先生，今日国危才来相求，是寡人之过。若能存郑，愿即拜先生为大夫。" },
        { speaker = "烛之武", text = "臣壮年尚不如人，如今发白齿落，本不敢当此重任。但郑国若亡，臣也无家可归，今夜愿从东城缒下。" },
        { speaker = "", text = "夜色降临，守军用长绳把烛之武从东门内侧缓缓放到城外。秦营并非敌阵终点，而是必须抵达的交涉目标；晋军巡骑散布在南北郊路，听见脚步便会截断使者去路。" },
        { speaker = "军令", text = "本关没有战斗目标，也不能用攻击清路。沿中央道路穿过东门与秦营西门，避开南北巡骑两格警戒圈；抵达秦穆公身边自动进入说秦剧情。" }
    },
    events = {
        { id = "east_gate", trigger = "approach", position = {25, 12}, radius = 0, speaker = "烛之武", text = "绳索已经收回，身后便是郑城。此去只能向前，先沿城根避开晋军巡骑的火把。" },
        { id = "qin_gate", trigger = "approach", position = {28, 13}, radius = 0, speaker = "秦军守卫", text = "深夜从郑城而来的人止步！既称奉郑伯之命，就解下兵器，随我到中军帐前。" }
    },
    victory = {
        { speaker = "烛之武", text = "秦晋围郑，郑国自知必亡。只是郑亡之后，土地尽归晋国，秦国隔着晋境，岂能越国而有郑？邻国更强，便是秦国更弱。" },
        { speaker = "秦穆公", text = "晋侯与寡人同盟而来。晋国得郑，未必便敢负秦；况且你深夜入营，只说亡郑之害，又能给秦国什么益处？" },
        { speaker = "烛之武", text = "若留郑国为秦国东方馆舍，秦使往来可得粮草，秦师东出也有落脚之地。郑不敢望秦为我作战，只愿世代供给行旅。" },
        { speaker = "百里奚", text = "郑国今日惧亡才来求盟，异日晋军一退，未必不会再亲楚背秦。主公不可只听眼前便利。" },
        { speaker = "烛之武", text = "君亦知晋之无厌。晋君当年许秦焦、瑕，朝渡河而暮设版；东封郑后，若再向西拓土，所侵者还能是谁？虞国借道灭虢，最终自己也亡，前鉴不远。" },
        { speaker = "秦穆公", text = "晋国若独吞郑土，确实只会逼近秦境。寡人可与郑结盟，并留杞子、逢孙、杨孙率二千兵助守东门。" },
        { speaker = "", text = "秦穆公与烛之武歃血订盟，当夜撤去氾南大营，故意不向晋军告辞。郑国东面包围就此解除，秦晋同盟也裂开了第一道缝隙。" },
        { speaker = "军令", text = "夜缒说秦完成，获得3600金币。第43回全部完成。" }
    },
    defeat = {
        { speaker = "", text = "晋军巡骑发现了城下使者，号角惊动西营。烛之武无法再秘密接近秦军，离间秦晋的时机已经失去。" }
    }
}

gstage = {
    title_id = "ZhuZhiwuPersuadesQin43", turn_limit = 12,
    map = { blocked_edges = {}, size = {36, 26}, terrain = {
        "mmfffFgFffffFgFfffgFfFffggFfFfggfmfF",
        "FfFfggfFfFggffFfFgfffFgFffffFgFfffgF",
        "ffmgFfffgFfFffggFfFfggfFfFggffFfFgmm",
        "mgffffggffffggffffggffffggffffggffff",
        "ffffggffffWWWWWWWWWWWWWWWWffggffffgg",
        "fmmgffffggWiiiiiiiiiiiiiiWggffffgmmf",
        "ggffffggffWiiiiiiiiiiiiiiWffffggffff",
        "ffffggffffWiiiiiCiCiCiiiiWffggffffgm",
        "mPPPPPPPPgWiiiiiiiiiiiiiiWgPPPPPPPPf",
        "gPffffggPfWiiiiiiiiiiiiiiWfPffggffPf",
        "fPmfggffPfWiiiiiiiiiiiiiiWfPggffffPm",
        "mPggefffPgGiiiiiiiiiiiiiiGgPfffeggPf",
        "gPffffggffGiiiiiiiiiiiiiiGffffggffPf",
        "fPmfggffffWiiiiiiiiiiiiiiWffggfffmPg",
        "fPggffffPgWiiiiiiiiiiiiiiWgPffffggPf",
        "gPffefggPfWiiiiiiiiiiiiiiWfPffgeffPm",
        "mPffggffPfWiiiiiiiiiiiiiiWfPggfffmPg",
        "fPggffffPgWiiiiiiiiiiiiiiWgPffffggPf",
        "gPPPPPPPPfWiiiiiiiiiiiiiiWfPPPPPPPPm",
        "mfffggffffWiiiiiiiiiiiiiiWffggffffgg",
        "ffggffffggWWWWWWWWWWWWWWWWggffffggff",
        "gmmfffggffffggffffggffffggffffggfmmf",
        "ffffggffffggffffggffffggffffggffffgg",
        "ffFgFfffgFfFffggFfFfggfFfFggffFfFgfm",
        "mmffFfFgfffFgFffffFgFfffgFfFffggFmFf",
        "fFffggFfFfggfFfFggffFfFgfffFgFffffFg"
    }, file = "map.bmp" },
    deploy = { unselectables = {
        { position = {23, 12}, hero = "ZhuZhiWu43" }
    }, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 3600 }
}

function on_deploy(game)
    game:appoint_hero("ZhuZhiWu43", 1)
end

function on_begin(game)
    game:generate_unit("ZhengWenGong43", 1, Enum.force.ally, {18, 7})
    game:generate_unit("ShuZhan43", 1, Enum.force.ally, {16, 9})
    game:generate_unit("YiZhiHu43", 1, Enum.force.ally, {20, 9})
    game:generate_unit("QinMuGong29", 1, Enum.force.ally, {31, 11})
    game:generate_unit("BailiXi29", 1, Enum.force.ally, {31, 15})
    game:generate_unit("QinGuard43", 1, Enum.force.ally, {29, 10})
    game:generate_unit("QinGuard43", 1, Enum.force.ally, {29, 16})
    for _, p in ipairs({{26,8},{26,16},{30,21},{30,3}}) do
        game:generate_unit("JinPatrol43", 1, Enum.force.ally, p)
    end
    game:generate_unit("ChongEr27", 1, Enum.force.ally, {4, 11})
    game:generate_unit("HuYan27", 1, Enum.force.ally, {4, 15})
end

function in_patrol_warning(game)
    return game:is_unit_within("ZhuZhiWu43", {26, 8}, 2)
        or game:is_unit_within("ZhuZhiWu43", {26, 16}, 2)
        or game:is_unit_within("ZhuZhiWu43", {30, 21}, 2)
        or game:is_unit_within("ZhuZhiWu43", {30, 3}, 2)
end

function on_update(game)
    if not east_gate_reached and game:is_unit_within("ZhuZhiWu43", {25, 12}, 0) then
        east_gate_reached = true
        game:push_cmd_speak(0, "烛之武已从郑城东门缒下。沿中央暗路向东，不要靠近南北巡骑的火把。")
    end
    if east_gate_reached and not qin_gate_reached and game:is_unit_within("ZhuZhiWu43", {28, 13}, 1) then
        qin_gate_reached = true
        game:push_cmd_speak(0, "秦营守卫已经验明使者身份，前方中军帐便是秦穆公所在。")
    end
    if east_gate_reached and in_patrol_warning(game) then
        detected = true
        game:push_cmd_speak(0, "晋军巡骑的火把照见了城下人影！秘密出使已经暴露。")
    end
    if qin_gate_reached and game:is_unit_within("ZhuZhiWu43", {31, 11}, 1) then
        qin_audience = true
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if detected or game:get_num_commanders_alive() < 1 then return Enum.status.defeat end
    if qin_audience then return Enum.status.victory end
    return Enum.status.undecided
end
