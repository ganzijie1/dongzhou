from pathlib import Path


ROOT = Path(r"C:\mengde")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


config_path = ROOT / "game/sce/dongzhou/config.lua"
config = config_path.read_text(encoding="utf-8")
assert 'id = "BaiTun46"' not in config
hero_anchor = '        ,{ id = "DiArcher45", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-blue" }'
hero_block = hero_anchor + '''
        ,{ id = "BaiTun46", class = "Lord", stat = {88, 94, 80, 86, 84}, model = "lord-1-blue" }
        ,{ id = "JinChariot46", class = "Infantry", stat = {86, 90, 80, 88, 84}, model = "infantry-1-red" }
        ,{ id = "JinGuard46", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinArcher46", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "DiCavalry46", class = "Cavalry", stat = {83, 89, 78, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "DiArcher46", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-blue" }
        ,{ id = "XianBo46", class = "Infantry", stat = {84, 92, 78, 86, 84}, model = "infantry-1-red" }
        ,{ id = "JinRetainer46", class = "Infantry", stat = {82, 88, 78, 84, 82}, model = "infantry-1-red" }
        ,{ id = "QinPengyaGuard46", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "QinPengyaCavalry46", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "QinPengyaArcher46", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "QinGuard46", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-red" }
        ,{ id = "QinCavalry46", class = "Cavalry", stat = {85, 91, 80, 86, 83}, model = "cavalry-1-red" }
        ,{ id = "QinArcher46", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "WangguanCommander46", class = "Cavalry", stat = {86, 92, 82, 87, 84}, model = "cavalry-1-blue" }
        ,{ id = "WangguanGuard46", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "WangguanArcher46", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-blue" }'''
config = replace_once(config, hero_anchor, hero_block, "chapter46 heroes")
config = replace_once(config, ', "44", "45a", "45b" }',
                      ', "44", "45a", "45b", "46a", "46b", "46c" }', "chapter46 stages")
config_path.write_text(config, encoding="utf-8", newline="")


stage45b_path = ROOT / "game/sce/dongzhou/stage/45b.lua"
stage45b = stage45b_path.read_text(encoding="utf-8")
stage45b = stage45b.replace("白屯", "白暾")
stage45b_path.write_text(stage45b, encoding="utf-8", newline="")


stage46b_path = ROOT / "game/sce/dongzhou/stage/46b.lua"
stage46b = stage46b_path.read_text(encoding="utf-8")
stage46b = replace_once(stage46b, "charge_started = false\nqin_retreat = false\n",
                        "charge_started = false\nqin_retreat = false\nretreat_announced = {}\n", "retreat state")
stage46b = stage46b.replace("QinGuard46", "QinPengyaGuard46")
stage46b = stage46b.replace("QinCavalry46", "QinPengyaCavalry46")
stage46b = stage46b.replace("QinArcher46", "QinPengyaArcher46")
for line in (
    '    game:set_unit_invulnerable("MengMingShi26", true)\n',
    '    game:set_unit_invulnerable("XiQiShu26", true)\n',
    '    game:set_unit_invulnerable("BaiYiBing26", true)\n',
):
    stage46b = replace_once(stage46b, line, "", "remove commander invulnerability")
stage46b = stage46b.replace("孟明视、西乞术、白乙丙只撤退，不可击杀", "孟明视、西乞术、白乙丙均可击退，结局统一为撤退")
stage46b = stage46b.replace("秦国三帅生命归零会原地恢复，胜利时统一按撤退处理。", "秦国三帅均可正常击退，退出战场后统一按撤退处理，不计为历史阵亡。")
old_update = '''    if charge_started and not qin_retreat and qin_regular_alive(game) <= 3 then
        qin_retreat = true
        game:push_cmd_speak(0, "秦军车阵已乱，孟明视命三帅收拢残兵向西撤退。狼瞫伤重倒下，晋军停止追击。")
    end
'''
new_update = '''    local qin_named = {
        { "MengMingShi26", "孟明视" },
        { "XiQiShu26", "西乞术" },
        { "BaiYiBing26", "白乙丙" }
    }
    for _, item in ipairs(qin_named) do
        if not retreat_announced[item[1]] and not game:has_unit(item[1]) then
            retreat_announced[item[1]] = true
            game:push_cmd_speak(0, item[2] .. "已被击退，率领身边残兵退出彭衙战场。")
        end
    end
    if charge_started and not qin_retreat and qin_regular_alive(game) <= 3
        and not game:has_unit("MengMingShi26") and not game:has_unit("XiQiShu26")
        and not game:has_unit("BaiYiBing26") then
        qin_retreat = true
        game:push_cmd_speak(0, "秦国三帅都已退出战场，剩余车阵向西溃退。狼瞫伤重倒下，晋军停止追击。")
    end
'''
stage46b = replace_once(stage46b, old_update, new_update, "commander retreat logic")
stage46b_path.write_text(stage46b, encoding="utf-8", newline="")


gui_path = ROOT / "rl/play_gui.py"
gui = gui_path.read_text(encoding="utf-8")
assert '"BaiTun46": "白暾"' not in gui
anchor = 'if _original_name == "__main__":'
block = '''_LARGE_BATTLE_MAPS["m070.png"] = (38, 26, 48)
_LARGE_BATTLE_MAPS["m071.png"] = (42, 28, 48)
_LARGE_BATTLE_MAPS["m072.png"] = (36, 28, 48)

HERO_LABELS.update({
    "BaiTun46": "白暾", "JinChariot46": "晋军战车", "JinGuard46": "晋军甲士",
    "JinArcher46": "晋军弓手", "DiCavalry46": "翟军骑兵", "DiArcher46": "翟军射手",
    "XianBo46": "鲜伯", "JinRetainer46": "狼瞫私属",
    "QinPengyaGuard46": "秦军甲士", "QinPengyaCavalry46": "秦军骑兵", "QinPengyaArcher46": "秦军弓手",
    "QinGuard46": "秦军甲士", "QinCavalry46": "秦军骑兵", "QinArcher46": "秦军弓手",
    "WangguanCommander46": "王官守将", "WangguanGuard46": "王官守军", "WangguanArcher46": "王官弓手",
})
HERO_BIOS.update({
    "BaiTun46": "白部胡之弟，曾劝兄长不可伐晋。兄死后以先轸遗体换回首级，再战失利，被狐射姑念旧放归。",
    "XianBo46": "狼瞫之友。彭衙之战率私属百余人与狼瞫直犯秦阵，冲锋中被白乙丙杀死。",
    "WangguanCommander46": "晋国王官边城守将。秦穆公亲征、孟明焚舟攻城时率军坚守，援兵不至后撤离。",
    "JinChariot46": "大谷阵前连车屯列的晋军战车，以密集阵线抵挡白暾骑兵冲击。",
    "JinRetainer46": "随狼瞫、鲜伯直犯秦阵的私属勇士。",
    "QinPengyaGuard46": "随秦国三帅到彭衙雪耻的甲士。",
    "QinPengyaCavalry46": "彭衙秦军车骑部队，遭狼瞫私属冲乱前阵。",
    "QinPengyaArcher46": "在彭衙列阵迎击晋军的秦国弓手。",
    "WangguanGuard46": "依托连续城墙和南门防守王官的晋国甲士。",
    "WangguanArcher46": "驻守王官城墙内街的晋国弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "BaiTun46": 7, "XianBo46": 49, "WangguanCommander46": 35,
})
SPEAKER_PORTRAIT_INDEX.update({
    "白暾": 7, "阳处父": 35, "斗勃": 49, "成大心": 33, "楚成王": 8,
    "商臣": 6, "潘崇": 42, "江芈": 18, "公子职": 31, "鲜伯": 49,
    "王官守将": 35, "繇余": 42, "周襄王": 8,
})
HISTORICAL_DEATH_HEROES.update({"DouBo33", "ChuChengWang33", "XianBo46", "LangTan45"})
_CHARIOT_UNITS.add("JinChariot46")

'''
gui = replace_once(gui, anchor, block + anchor, "chapter46 GUI block")
gui_path.write_text(gui, encoding="utf-8", newline="")

print("Applied chapter46 configuration, GUI mappings, and retreat logic.")
