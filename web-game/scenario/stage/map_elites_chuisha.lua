gitems = {
    {id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2},
    {id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}
}
gcommanders = {"KuangZhang91","GongSunXiChuisha","BaoYuanChuisha"}
gstory = {map_asset="contract-map.png"}
gduel_enabled = false
gduels = {}
gevents_enabled = true
gsites = {}
gsupply_enabled = false
gstage = {title_id="MapElitesChuishaExercise",turn_limit=22,map={blocked_edges={},size={19,14},terrain={
    "ffffffffffffgffgfff","fffffffgfffgfffffff","fgffffffffgffffggff","fffffffffffffffgfgf",
    "fffffffffffffffffff","ffffffffffffffffFgf","~~v~~~~~~~~~~~~~v~~","~~v~~~~~~~~~~~~~v~~",
    "ffffffffffgffffffgf","gfffffffffffffffgff","fffffgfffffffffffff","ffffffffFffffgfffff",
    "fgffFffffffffffffgf","ffffffffffffgffffff"
},file="generated"},deploy={unselectables={
    {position={2,2},hero="KuangZhang91"},{position={3,3},hero="GongSunXiChuisha"},{position={4,2},hero="BaoYuanChuisha"},
    {position={5,3},hero="QiHanWeiGuard"},{position={6,2},hero="QiHanWeiGuard"},{position={7,3},hero="QiHanWeiArcher"}
},num_required_selectables=0,selectables={}},rewards={equipments={},money=0}}

function on_deploy(game)
    for _,hero in ipairs(gcommanders) do game:appoint_hero(hero,1) end
end

function on_begin(game)
    game:generate_unit("TangMieChuisha",1,Enum.force.enemy,{16,11})
    game:generate_unit("ChuishaGuard",1,Enum.force.enemy,{15,10})
    game:generate_unit("ChuishaGuard",1,Enum.force.enemy,{14,11})
    game:generate_unit("ChuishaGuard",1,Enum.force.enemy,{13,10})
    game:generate_unit("ChuishaArcher",1,Enum.force.enemy,{12,11})
    game:generate_unit("ChuishaArcher",1,Enum.force.enemy,{11,10})
end

function on_update(game) end
function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if not game:has_unit("KuangZhang91") then return Enum.status.defeat end
    if not game:has_unit("TangMieChuisha") then return Enum.status.victory end
    return Enum.status.undecided
end
