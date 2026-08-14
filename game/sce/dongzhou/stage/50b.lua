relief_started = false
relief_turn = 0
qin_retreat = false

gally_hold_position = true
gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoChuan48" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十回·中",
    title = "东门遂援立子倭 赵宣子桃园强谏",
    battle_title = "焦城解围",
    objective = "赵穿率晋军由东向西击破秦军包围，亲自到达焦城东门两格范围内触发解围；随后坚守三回合，秦军撤退。焦城城墙不可跨越，东门两格可以通行。赵穿被击退则失败。",
    map_asset = "m079.png",
    intro = {
        { speaker = "", text = "赵穿率三百乘侵入崇国，秦国却没有按预想救援属国，而是绕过崇地直扑晋国焦城。" },
        { speaker = "秦军主将", text = "晋军主力尚在崇地，焦城防备空虚。围住东门，断绝粮道，逼晋人回兵救援。" },
        { speaker = "焦城守将", text = "城墙尚固，但秦军日夜攻门。若援军再迟数日，城内粮箭都会耗尽。" },
        { speaker = "赵穿", text = "攻崇本为引秦议和，却让焦城陷入重围。全军立即回师，先打通东门，再依城坚守。" },
        { speaker = "赵朔", text = "秦军远来，围城阵线拉得很长。赵穿若集中骑兵冲击东侧，守军再从门内夹击，尚可解围。" },
        { speaker = "韩厥", text = "不要贪图全歼。只要援军抵达城门，秦军发现焦城不可速下，自然会撤退。" },
        { speaker = "军令", text = "连续城墙均为不可通行的整格W；焦城东门是两格G通道。赵穿本人须抵达东门附近，再守三回合完成解围。" }
    },
    events = {
        { id = "relief_reaches_gate", trigger = "approach", position = {15,14}, radius = 2, speaker = "焦城守将", text = "赵穿援军已经抵达东门！城内守军放箭夹击，再坚持三回合，秦军必退！" }
    },
    victory = {
        { speaker = "", text = "赵穿率军冲到焦城东门，与守军内外夹击。秦军见晋国援兵已至，围城无望，开始后撤。" },
        { speaker = "秦军主将", text = "焦城东门已经打通，晋军后续兵马也将赶到。保全主力，撤回秦境！" },
        { speaker = "赵穿", text = "不要越过焦城追击。秦师既退，先补充城防，清点百姓损失。" },
        { speaker = "", text = "焦城之围解除，但赵盾借攻崇求和的策略彻底失败，秦晋关系反而更加恶化。" },
        { speaker = "", text = "臾骈不久病逝，赵穿接替其职，开始正式参与晋国兵政。" },
        { speaker = "军令", text = "焦城解围完成，获得650金币。秦军按原著撤退，不计历史阵亡。下一关转入晋灵公桃园宴伏。" }
    },
    defeat = {{ speaker = "", text = "赵穿在焦城外被击退，援军崩溃，秦军继续围攻东门。" }}
}

gstage = {
    title_id = "ReliefOfJiao50", turn_limit = 20,
    map = { blocked_edges = {}, size = {46,30}, terrain = {
        "FFffgfFFfffgFFgfffFFfgffFFffmfFFmffgFFfgmfFFmf",
        "gffFFffgfFFfffgFFgfffFFfgffFFffmfFFmffgFFfgmfF",
        "FFfgffFFffgfFFfffgFFgfffFFmgffFFffmfFFmffgFFfg",
        "ffgfffgffgfffgffgfffgffgfmfgfmgffmgffmfffmffgF",
        "FFgffgfffgffgfffgffgfffgffgfmfgfmgffmgffmffFmf",
        "fgWWWWWWWWWWWWWWfffgffgfffgffgfffgffgfffgffgfF",
        "FFWiiiiiiiiiiiiWffgfffgffgfffgffgfffgffgfffFff",
        "gfWiiiiiiiiiiiiWffgffgfffgffgfffgffgfffgffgffF",
        "FFWiiiiiiiiiiiiWfgfffgffgfffgffgfffgffgfffgFfg",
        "ffWiiiiiiiiiiiiWfgffgfffgffgfffgffgfffgffgfffF",
        "FFWiiiiiiiiiiiiWgfffgffgfffgffgfffgffgfffgfFgf",
        "ffWiiiiiiiiiiiiWgffgfffgffgfffgffgfffgffgfffgF",
        "FFWiiiiiiiiiiiiWfffgffgfffgffgfffgffgfffgffFff",
        "wwWiiiiiiiiiiiiWwwwwwwwwwwwwwwwwwwwwwwwwwwwwwF",
        "FFWiiiiiiiiiiiiGwwwwwwwwwwwwwwwwwwwwwwwwwwwFww",
        "wwWiiiiiiiiiiiiGwwwwwwwwwwwwwwwwwwwwwwwwwwwwwF",
        "FFWiiiiiiiiiiiiWfgffgfffgffgfffgffgfffgffgfFfg",
        "ffWiiiiiiiiiiiiWgfffgffgfffgffgfffgffgfffgffgF",
        "FFWiiiiiiiiiiiiWgffgfffgffgfffgffgfffgffgffFgf",
        "fgWiiiiiiiiiiiiWfffgffgfffgffgfffgffgfffgffgfF",
        "FFWiiiiiiiiiiiiWffgfffgffgfffgffgfffgffgfffFff",
        "gfWiiiiiiiiiiiiWffgffgfffgffgfffgffgfffgffgffF",
        "FFWiiiiiiiiiiiiWfgfffgffgfffgffgfffgffgfffgFfg",
        "ffWiiiiiiiiiiiiWfgffgfffgffgfffgffgfffgffgfffF",
        "FFWWWWWWWWWWWWWWgfffgffgfffgffgfffgffgfffgfFgf",
        "ffgffgfffgffgfffgffgfffgffgfffgffgfffgffgfffgF",
        "FFfffgffgfffgffgfffgffgfffgffgfffgffgfffgffFff",
        "fgfFFfffgFFgfffFFfgffFFffgfFFgffgFFfgffFFffgfF",
        "FFffgfFFfffgFFgfffFFfgffFFffgfFFgffgFFfgffFFff",
        "gffFFffgfFFfffgFFgfffFFfgffFFffgfFFgffgFFfgffF",
    }, file = "map.bmp" },
    deploy = { unselectables = {{ position = {39,14}, hero = "ZhaoChuan48" }}, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6500 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game) game:appoint_hero("ZhaoChuan48", 1) end
function on_begin(game)
    game:generate_unit("QinSiegeCaptain50", 1, Enum.force.enemy, {22,14})
    game:set_unit_invulnerable("QinSiegeCaptain50", true)
    game:generate_unit("JiaoDefender50", 1, Enum.force.ally, {12,14})
    many(game, "JinReliefGuard50", {{36,10},{36,13},{36,16},{36,19},{40,11},{40,17}}, Enum.force.own)
    many(game, "JinReliefCavalry50", {{38,9},{38,19},{41,13},{41,16}}, Enum.force.own)
    many(game, "JinReliefArcher50", {{34,9},{34,20},{39,11},{39,18}}, Enum.force.own)
    many(game, "QinSiegeGuard50", {{18,9},{18,12},{18,17},{18,20},{22,10},{22,18},{26,12},{26,17}}, Enum.force.enemy)
    many(game, "QinSiegeCavalry50", {{20,8},{20,21},{25,9},{25,20},{29,13},{29,16}}, Enum.force.enemy)
    many(game, "QinSiegeArcher50", {{17,7},{17,22},{21,12},{21,17},{24,11},{24,18},{28,10},{28,19}}, Enum.force.enemy)
end
function on_update(game)
    if not relief_started and game:is_unit_within("ZhaoChuan48", {15,14}, 2) then
        relief_started = true
        relief_turn = game:get_turn_current()
        game:push_cmd_speak(0, "赵穿已抵达焦城东门，守军开始内外夹击。坚守三回合，迫使秦军撤围。")
    end
    if relief_started and not qin_retreat and game:get_turn_current() >= relief_turn + 3 then
        qin_retreat = true
        game:push_cmd_speak(0, "秦军见焦城援兵不断，已经解除包围，向西撤回秦境。")
    end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if qin_retreat then return Enum.status.victory end
    return Enum.status.undecided
end
