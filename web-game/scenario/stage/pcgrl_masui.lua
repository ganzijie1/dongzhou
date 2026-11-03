gitems = {
    {id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},
    {id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}
}
gcommanders = {"JinLiGong58","LuanShu58","ShiXie58","HanJue48","XiQi58","XiZhi58","XunYing54"}
gduel_enabled = false
gduels = {}
gevents_enabled = true
gsites = {}
gsupply_enabled = false
gstage = {title_id="PcgrlMasuiExercise",turn_limit=24,map={blocked_edges={},size={19,14},terrain={
    "fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff",
    "fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff",
    "fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff","fffffffffffffffffff",
    "fffffffffffffffffff","fffffffffffffffffff"
},file="generated"},deploy={unselectables={
    {position={2,6},hero="JinLiGong58"},{position={3,4},hero="LuanShu58"},
    {position={3,6},hero="ShiXie58"},{position={3,8},hero="HanJue48"},
    {position={4,3},hero="XiQi58"},{position={4,9},hero="XiZhi58"},
    {position={5,5},hero="XunYing54"}
},num_required_selectables=0,selectables={}},rewards={equipments={},money=0}}

function on_deploy(game)
    for _,hero in ipairs(gcommanders) do game:appoint_hero(hero,1) end
end

function on_begin(game)
    game:generate_unit("QinHuanGongMasui",1,Enum.force.enemy,{16,6})
    game:set_unit_invulnerable("QinHuanGongMasui",true)
    game:generate_unit("ChengChaMasui",1,Enum.force.enemy,{15,5})
    game:generate_unit("NvFuMasui",1,Enum.force.enemy,{15,7})
    game:generate_unit("QinMasuiGuard",1,Enum.force.enemy,{14,4})
    game:generate_unit("QinMasuiGuard",1,Enum.force.enemy,{14,8})
    game:generate_unit("QinMasuiArcher",1,Enum.force.enemy,{13,6})
end

function on_update(game)
    if not game:has_unit("ChengChaMasui") and not game:has_unit("NvFuMasui") then
        game:set_unit_invulnerable("QinHuanGongMasui",false)
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if not game:has_unit("JinLiGong58") then return Enum.status.defeat end
    if not game:has_unit("ChengChaMasui") and not game:has_unit("NvFuMasui") then return Enum.status.victory end
    return Enum.status.undecided
end
