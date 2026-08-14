$ErrorActionPreference = "Stop"
$utf8 = [Text.UTF8Encoding]::new($false)

function Replace-ExactlyOnce([string]$Text, [string]$Old, [string]$New, [string]$Label) {
    $first = $Text.IndexOf($Old, [StringComparison]::Ordinal)
    if ($first -lt 0) { throw "Missing anchor: $Label" }
    if ($Text.IndexOf($Old, $first + $Old.Length, [StringComparison]::Ordinal) -ge 0) {
        throw "Anchor is not unique: $Label"
    }
    return $Text.Substring(0, $first) + $New + $Text.Substring($first + $Old.Length)
}

$configPath = "C:\mengde\game\sce\dongzhou\config.lua"
$config = [IO.File]::ReadAllText($configPath, $utf8)
$heroAnchor = '        ,{ id = "BaoManZi44", class = "Cavalry", stat = {86, 94, 76, 86, 84}, model = "cavalry-1-red" }'
$heroBlock = @'
        ,{ id = "BaoManZi44", class = "Cavalry", stat = {86, 94, 76, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinXiangGong45", class = "Lord", stat = {88, 90, 88, 88, 86}, model = "lord-1-blue" }
        ,{ id = "XianQieJu45", class = "Cavalry", stat = {88, 94, 84, 88, 86}, model = "cavalry-1-blue" }
        ,{ id = "TuJi45", class = "Infantry", stat = {84, 90, 80, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "XuYing45", class = "Cavalry", stat = {84, 90, 84, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "HuJuJu45", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "HanZiYu45", class = "Archer", stat = {82, 88, 86, 86, 84}, model = "archer-1-blue" }
        ,{ id = "LiangHong45", class = "Cavalry", stat = {86, 92, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "LaiJu45", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "LangTan45", class = "Infantry", stat = {88, 96, 78, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "LuanDun45", class = "Cavalry", stat = {84, 90, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "XiQue45", class = "Archer", stat = {86, 92, 90, 90, 88}, model = "archer-1-blue" }
        ,{ id = "BaiBuHu45", class = "Lord", stat = {90, 96, 78, 88, 86}, model = "lord-1-red" }
        ,{ id = "JinGuard45", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "JinArcher45", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "QinGuard45", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "QinCavalry45", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-red" }
        ,{ id = "QinArcher45", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "DiCavalry45", class = "Cavalry", stat = {83, 89, 78, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "DiArcher45", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-red" }
'@
$config = Replace-ExactlyOnce $config $heroAnchor $heroBlock "chapter45 hero insertion"
$stageAnchor = ', "43a", "43b", "44" }'
$config = Replace-ExactlyOnce $config $stageAnchor ', "43a", "43b", "44", "45a", "45b" }' "chapter45 stage list"
[IO.File]::WriteAllText($configPath, $config, $utf8)

$guiPath = "C:\mengde\rl\play_gui.py"
$gui = [IO.File]::ReadAllText($guiPath, $utf8)
$guiAnchor = 'if _original_name == "__main__":'
$guiBlock = @'
_LARGE_BATTLE_MAPS["m068.png"] = (44, 28, 48)
_LARGE_BATTLE_MAPS["m069.png"] = (36, 26, 48)

HERO_LABELS.update({
    "JinXiangGong45": "晋襄公", "XianQieJu45": "先且居", "TuJi45": "屠击",
    "XuYing45": "胥婴", "HuJuJu45": "狐鞫居", "HanZiYu45": "韩子舆",
    "LiangHong45": "梁弘", "LaiJu45": "莱驹", "LangTan45": "狼瞫",
    "LuanDun45": "栾盾", "XiQue45": "郤缺", "BaiBuHu45": "白部胡",
    "JinGuard45": "晋军甲士", "JinArcher45": "晋军弓手",
    "QinGuard45": "秦军甲士", "QinCavalry45": "秦军骑兵", "QinArcher45": "秦军弓手",
    "DiCavalry45": "翟军骑兵", "DiArcher45": "翟军射手",
})
HERO_BIOS.update({
    "JinXiangGong45": "晋文公之子。即位后墨染丧服亲征，在崤山全歼秦军；能容先轸面斥之失，继续委以军政。",
    "XianQieJu45": "先轸之子，晋国将领。崤山伏左山截击秦军，箕城之战又担任先锋，诈败诱白部胡进入大谷。",
    "TuJi45": "晋国将领。崤山战与先且居率左翼伏兵，见红旗后从山腰突击秦军。",
    "XuYing45": "晋国将领。崤山战与狐鞫居率右翼伏兵，截断秦军侧面通路。",
    "HuJuJu45": "晋国狐氏将领。崤山伏击负责右翼，后又参加箕城御翟，协助封锁大谷退路。",
    "HanZiYu45": "晋国将领。崤山战随狐射姑伏于西口，以弓军和断木封住秦军归路。",
    "LiangHong45": "晋国将领。崤山伏于东口，待秦军全部入谷后封闭后路。",
    "LaiJu45": "晋国勇将。崤山东口遇褒蛮子，依伏击号令暂时放其深入，随后参加合围。",
    "LangTan45": "晋国勇士。崤山斩杀挣缚夺马的褒蛮子；箕城战不因先锋被换而怀怨，以战死证明勇烈。",
    "LuanDun45": "晋国将领。箕城御翟时伏于大谷左翼，待白部胡深入后出击。",
    "XiQue45": "晋国郤氏贤将。箕城战伏于大谷右翼，一箭射杀白部胡，后成为晋国重要卿士。",
    "BaiBuHu45": "白部翟首领，越箕城侵晋，追击先且居进入大谷，被郤缺一箭射中面门而死。",
    "JinGuard45": "参加崤山伏击与箕城御翟的晋国甲士。",
    "JinArcher45": "埋伏在山腰、林缘，负责封锁谷道的晋军弓手。",
    "QinGuard45": "随秦国三帅袭郑、破滑后携带缴获西归的秦军甲士。",
    "QinCavalry45": "困在崤山狭谷、首尾不能相救的秦军骑兵。",
    "QinArcher45": "随秦军辎重队进入崤山的弓手。",
    "DiCavalry45": "跟随白部胡越过箕城、追入大谷的翟军骑兵。",
    "DiArcher45": "跟随白部胡侵晋的翟军射手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "JinXiangGong45": 6, "XianQieJu45": 24, "TuJi45": 49, "XuYing45": 35,
    "HuJuJu45": 25, "HanZiYu45": 17, "LiangHong45": 34, "LaiJu45": 20,
    "LangTan45": 13, "LuanDun45": 45, "XiQue45": 37, "BaiBuHu45": 7,
})
SPEAKER_PORTRAIT_INDEX.update({
    "晋襄公": 6, "先且居": 24, "屠击": 49, "胥婴": 35, "狐鞫居": 25,
    "韩子舆": 17, "梁弘": 34, "莱驹": 20, "狼瞫": 13, "栾盾": 45,
    "郤缺": 37, "白部胡": 7, "文嬴": 18, "阳处父": 35, "白屯": 7,
})
HISTORICAL_DEATH_HEROES.update({"BaoManZi44", "BaiBuHu45", "XianZhen27"})

if _original_name == "__main__":
'@
$gui = Replace-ExactlyOnce $gui $guiAnchor $guiBlock "chapter45 GUI mappings"
[IO.File]::WriteAllText($guiPath, $gui, $utf8)

Write-Output "Updated chapter45 config and GUI mappings."
