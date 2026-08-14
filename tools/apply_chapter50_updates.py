import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def rows(name):
    data = json.loads((ROOT / "assets/lzc/map_sources" / name).read_text(encoding="utf-8"))
    return "\n".join(f'        "{row}",' for row in data["terrain_rows"])


STAGE_50A = r'''gally_hold_position = true
gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "GongZiGuiSheng50" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十回·上",
    title = "东门遂援立子倭 赵宣子桃园强谏",
    battle_title = "大棘之战",
    objective = "郑公子归生率军击破宋军并击退右师华元。华元被击退按原著判定为被俘，不计阵亡；公子归生被击退则失败。",
    map_asset = "m078.png",
    intro = {
        { speaker = "", text = "仲遂与叔孙得臣到齐国拜贺新君。齐惠公问起鲁国嗣君恶，仲遂趁机称公子倭贤孝而得国人之心。" },
        { speaker = "仲遂", text = "鲁国虽有立嫡旧礼，先君真正喜爱的却是长子倭。上国若肯援立，鲁国愿世代事齐。" },
        { speaker = "叔孙得臣", text = "齐鲁再结婚姻，公子倭便有外援。只要国内有人主持，改立之事即可成功。" },
        { speaker = "齐惠公", text = "公子倭若真贤孝，寡人愿与他结为甥舅。二位大夫主持于内，齐国自会相助。" },
        { speaker = "", text = "仲遂回鲁后与敬嬴定计，在内厩埋伏勇士，以观看新生马驹为名，诱公子恶、公子视入内。" },
        { speaker = "", text = "勇士突然持木棍杀死公子恶与公子视。仲遂又假传君命，将太傅叔仲彭生召入宫中。" },
        { speaker = "公冉务人", text = "太傅不可入宫！若真是君命，自然不会杀你；若是假命，白白赴死又有什么名义？" },
        { speaker = "叔仲彭生", text = "既称君命，臣子便不能逃避。纵然是死，我也要亲自入宫问个明白。" },
        { speaker = "", text = "彭生绝袂登车，也被伏兵杀死，尸体埋入马粪。叔孙得臣后来掘出兄长遗体，以忠臣之礼安葬。" },
        { speaker = "季孙行父", text = "仲遂此事太毒，我不忍听闻。若晋国借弑君之名问罪，鲁国又如何应对？" },
        { speaker = "仲遂", text = "齐宋弑君尚无人真讨，两个孺子又能引来什么大军？今日当先立公子倭，稳定朝廷。" },
        { speaker = "", text = "百官不敢反对，公子倭即位，是为鲁宣公。嫡夫人姜氏痛失二子，离开鲁国，大市百姓为之罢市。" },
        { speaker = "出姜", text = "贼遂杀嫡立庶，我母子何罪！今日与鲁国百姓永诀，此生不再踏入鲁境。" },
        { speaker = "", text = "鲁宣公同母弟叔肹不肯朝贺，也不受爵禄粮帛，靠织草鞋维生，却终身不公开指斥兄长。" },
        { speaker = "叔肹", text = "我见兄长便想起死去的弟弟，因此不忍入朝；但兄长未绝我，我也不能背弃宗国。" },
        { speaker = "", text = "仲遂又到齐国迎娶姜氏，并以济西田地换取齐惠公在平州会见鲁宣公，鲁国新君之位由此得到承认。" },
        { speaker = "", text = "楚庄王即位三年，日夜田猎饮酒，并悬令禁止进谏。大夫申无畏用三年不飞不鸣的大鸟试探。" },
        { speaker = "楚庄王", text = "此鸟三年不飞，飞必冲天；三年不鸣，鸣必惊人。寡人在等待时机，你且看以后。" },
        { speaker = "", text = "苏从随后冒死直谏，指出楚王以一时酒色抛弃万世基业，愚蠢远胜甘愿死谏的臣子。" },
        { speaker = "苏从", text = "臣被杀，后世仍称臣为忠；大王若亡国，求做匹夫也不可得。请借佩剑，让臣死在王前！" },
        { speaker = "楚庄王", text = "忠言逆耳，却能救国。撤去钟鼓，疏远郑姬、蔡女，立樊姬主持宫政，寡人今日开始理政。" },
        { speaker = "", text = "楚庄王任用蒍贾、潘尪、屈荡，分薄斗越椒权势；又命郑国公子归生攻宋，在大棘与宋军交锋。" },
        { speaker = "公子归生", text = "宋国刚经历孟诸政变，军心未稳。击破右师华元，将他生擒，郑国便可向楚王复命。" },
        { speaker = "华元", text = "宋文公新立，诸侯都想趁虚而入。今日唯有背水一战，不能让郑军踏过大棘。" },
        { speaker = "军令", text = "击退华元即可取胜；华元按原著判定为被俘，其他宋国具名角色若出现也统一按撤退处理。公子归生不得被击退。" }
    },
    events = {
        { id = "daji_contact", trigger = "approach", position = {8,14}, radius = 7, speaker = "华元", text = "郑军已逼近中军！宋军列阵，不可让公子归生轻易得手！" }
    },
    victory = {
        { speaker = "", text = "郑军击破宋国中军，右师华元力竭被俘。原著只记其被擒，并未在此阵亡。" },
        { speaker = "公子归生", text = "押送华元回营，约束士卒，不得滥杀。大棘之胜足以向楚王交令。" },
        { speaker = "", text = "楚庄王又命蒍贾救郑，在北林击败晋军，俘虏晋将解扬；一年之后，解扬获释归晋。" },
        { speaker = "", text = "楚国接连取胜，庄王声势日盛，开始萌生争夺中原霸权之志。" },
        { speaker = "", text = "晋国赵盾想联合秦国抗楚。赵穿建议先攻秦国属国崇，以逼秦出兵，再趁机议和。" },
        { speaker = "赵朔", text = "秦晋积怨未消，如今再攻其属国，只会激怒秦君，未必能够换来和议。" },
        { speaker = "韩厥", text = "攻崇未必为了和秦。赵相国更想让赵穿掌握兵权，以巩固赵氏宗族。" },
        { speaker = "", text = "秦国果然没有救崇，反而直接出兵晋国，包围焦城。赵穿只得率军回援。" },
        { speaker = "军令", text = "大棘之战完成，获得600金币。下一战转入焦城解围，华元保留存活与后续出场资格。" }
    },
    defeat = {{ speaker = "", text = "公子归生被击退，郑军失去指挥，只得退出大棘。" }}
}

gstage = {
    title_id = "BattleOfDaji50", turn_limit = 22,
    map = { blocked_edges = {}, size = {42,28}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {{ position = {34,13}, hero = "GongZiGuiSheng50" }}, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 6000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end

function on_deploy(game) game:appoint_hero("GongZiGuiSheng50", 1) end
function on_begin(game)
    game:generate_unit("HuaYuan50", 1, Enum.force.enemy, {8,14})
    many(game, "ZhengGuard50", {{31,10},{31,12},{31,15},{31,17},{35,10},{35,16}}, Enum.force.own)
    many(game, "ZhengCavalry50", {{33,9},{33,17},{37,12},{37,15}}, Enum.force.own)
    many(game, "ZhengArcher50", {{30,9},{30,18},{36,9},{36,18}}, Enum.force.own)
    many(game, "SongGuard50", {{5,11},{5,14},{5,17},{9,11},{9,17},{12,13},{12,15}}, Enum.force.enemy)
    many(game, "SongCavalry50", {{7,9},{7,19},{11,10},{11,18}}, Enum.force.enemy)
    many(game, "SongArcher50", {{4,9},{4,19},{10,12},{10,16},{13,11},{13,17}}, Enum.force.enemy)
end
function on_update(game) end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if not game:has_unit("HuaYuan50") then return Enum.status.victory end
    return Enum.status.undecided
end
'''


STAGE_50B = r'''relief_started = false
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
__ROWS__
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
'''


STAGE_50C = r'''dog_defeated = false
ti_fallen = false
ling_zhe_arrived = false

gally_hold_position = true
gsupply_enabled = false
gitems = {
    { id = "medicine", name = "恢复用药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "ZhaoDun47" }
gduel_enabled = false
gevents_enabled = true
gduels = {}
gsites = {}

gstory = {
    chapter = "第五十回·下",
    title = "东门遂援立子倭 赵宣子桃园强谏",
    battle_title = "桃园脱险",
    objective = "护送赵盾从桃园宫墙西门突围并到达西侧出口（1,13）。灵獒必须先被击退；提弥明按原著留下断后并阵亡，之后灵辄出现接应。赵盾被击退则失败，晋灵公与屠岸贾不可被击退。",
    map_asset = "m080.png",
    intro = {
        { speaker = "", text = "晋灵公成年后荒淫暴虐，重税营建，在绛州城内修桃园与绛霄楼，宠任善于逢迎的屠岸贾。" },
        { speaker = "晋灵公", text = "弹鸟有什么意思？今日与屠卿各执弹弓，以园外百姓为目标，中眼者胜！" },
        { speaker = "", text = "弹丸如雨落入人群，百姓有人破头、伤眼、落齿。晋灵公在高台俯视奔逃惨状，反而大笑。" },
        { speaker = "", text = "晋灵公又豢养一头赤色猛犬灵獒，由獒奴牵随左右，稍有过失便纵犬咬人。" },
        { speaker = "", text = "一次晋灵公嫌熊掌没有煮熟，以铜斗杀死宰夫，又将尸体支解装入竹笼，命内侍弃于野外。" },
        { speaker = "赵盾", text = "主上视人命如草芥，国家危亡只在旦夕。我与士会若再沉默，晋国便无人敢进忠言。" },
        { speaker = "士会", text = "让我先谏。若主上不听，相国再继续进言，不能让忠谏一次便断绝。" },
        { speaker = "", text = "晋灵公见士会便抢先声称知错。次日却免朝前往桃园，赵盾只得拦在园门强谏。" },
        { speaker = "赵盾", text = "有道之君以快乐百姓，无道之君只求自身享乐。纵犬弹人、支解膳夫，桀纣之祸将及君身！" },
        { speaker = "晋灵公", text = "相国暂退，容寡人今日最后游玩一次，明日早朝再依你的话改革。" },
        { speaker = "屠岸贾", text = "车驾既到桃园，岂能空返？相国挡住园门，反使国君在百姓面前失去威严。" },
        { speaker = "", text = "赵盾无奈让路。屠岸贾随即向晋灵公献计，派刺客鉏麑在五更潜入赵府。" },
        { speaker = "鉏麑", text = "赵盾端坐待朝、不忘恭敬，是百姓之主。杀他不忠，弃君命不信，我只能以死两全。" },
        { speaker = "", text = "鉏麑在赵府门前触槐自尽，临死高声示警。赵盾明知有变，仍按礼入朝。" },
        { speaker = "", text = "屠岸贾又在宫宴后壁埋伏甲士，准备诱使赵盾解剑，再诬称他拔剑弑君。" },
        { speaker = "提弥明", text = "臣侍君宴，礼不过三爵！相国不可在酒后解剑，立即起身离席！" },
        { speaker = "", text = "赵盾醒悟离席。屠岸贾命獒奴放出灵獒追咬紫袍者，宫墙后的伏兵也一齐冲出。" },
        { speaker = "提弥明", text = "相国快走！我先折断恶犬之颈，再挡住伏甲。只要赵氏还有人接应，晋国便仍有希望。" },
        { speaker = "军令", text = "西侧宫墙连续不可跨越，只有两格西门G可通行。先击退灵獒；提弥明阵亡后灵辄倒戈接应，赵盾本人必须到达（1,13）。" }
    },
    events = {
        { id = "ling_ao_defeated", trigger = "unit_defeated", unit = "LingAo50", speaker = "提弥明", text = "恶犬已死！相国立即穿过西门，我留下抵挡伏甲！" },
        { id = "ling_zhe_rescue", trigger = "unit_defeated", unit = "TiMiMing50", speaker = "灵辄", text = "相国莫怕！我是翳桑饿人灵辄，今日混在公徒之中，正为报昔日一饭之恩！" }
    },
    victory = {
        { speaker = "", text = "提弥明双手折断灵獒之颈，以身体护住赵盾，独自迎战宫中伏甲。" },
        { speaker = "", text = "赵盾退出宫门后，提弥明寡不敌众，遍体受伤，最终力尽而死。" },
        { speaker = "灵辄", text = "相国还记得翳桑那个饿了三日、却仍想把饭留给母亲的人吗？我便是灵辄。" },
        { speaker = "", text = "五年前赵盾曾救济灵辄与其母。灵辄如今身在伏兵之中，念旧恩倒戈，背负赵盾冲出朝门。" },
        { speaker = "赵盾", text = "一饭之恩，你竟以性命相报。随我同车离城，赵氏绝不会亏待义士！" },
        { speaker = "", text = "灵辄不愿受报，转身隐入人群。赵朔率赵府家丁驾车赶到，伏甲见人多势众，不敢再追。" },
        { speaker = "赵朔", text = "父亲不能再回府了。西门道路尚未封锁，我们先离开绛州，再决定投奔翟国还是秦国。" },
        { speaker = "赵盾", text = "晋君既要杀我，此刻只能出奔。家国后事暂托诸卿，待局势有变再作打算。" },
        { speaker = "", text = "赵盾父子同出西门向西而去。晋国正卿被迫流亡，灵公与赵氏的冲突已无法挽回。" },
        { speaker = "军令", text = "桃园脱险完成，获得800金币。提弥明与灵獒按原著记入阵亡；晋灵公、屠岸贾和其余伏甲均保留后续出场。" }
    },
    defeat = {{ speaker = "", text = "赵盾未能穿过桃园西门，宫中伏甲将他围住，晋国赵氏遭受重创。" }}
}

gstage = {
    title_id = "TaoyuanEscape50", turn_limit = 18,
    map = { blocked_edges = {}, size = {38,26}, terrain = {
__ROWS__
    }, file = "map.bmp" },
    deploy = { unselectables = {{ position = {29,12}, hero = "ZhaoDun47" }}, num_required_selectables = 0, selectables = {} },
    rewards = { equipments = {}, money = 8000 }
}

local function many(game, hero, positions, force)
    for _, p in ipairs(positions) do game:generate_unit(hero, 1, force, p) end
end
function on_deploy(game) game:appoint_hero("ZhaoDun47", 1) end
function on_begin(game)
    game:generate_unit("TiMiMing50", 1, Enum.force.own, {27,13})
    game:generate_unit("JinLingGong50", 1, Enum.force.enemy, {31,7})
    game:generate_unit("TuAnGu50", 1, Enum.force.enemy, {29,7})
    game:generate_unit("LingAo50", 1, Enum.force.enemy, {24,12})
    for _, hero in ipairs({"JinLingGong50", "TuAnGu50"}) do game:set_unit_invulnerable(hero, true) end
    many(game, "PalaceGuard50", {{22,8},{22,11},{22,14},{22,17},{26,6},{26,19},{31,10},{31,16},{34,12}}, Enum.force.enemy)
    many(game, "PalaceArcher50", {{19,7},{19,18},{24,6},{24,19},{28,9},{28,17},{33,9},{33,17}}, Enum.force.enemy)
end
function on_update(game)
    if not dog_defeated and not game:has_unit("LingAo50") then
        dog_defeated = true
        game:push_cmd_speak(0, "提弥明已经折断灵獒之颈。赵盾立即向西门撤离，提弥明留下抵挡宫中伏甲。")
        many(game, "PalaceGuard50", {{17,10},{17,12},{17,14},{17,16}}, Enum.force.enemy)
    end
    if dog_defeated and not ti_fallen and game:is_unit_within("ZhaoDun47", {12,13}, 1) then
        ti_fallen = true
        game:generate_unit("LingZhe50", 1, Enum.force.ally, {10,13})
        ling_zhe_arrived = true
        game:push_cmd_speak(0, "赵盾已经穿过西门，提弥明转身留下断后。灵辄从伏甲中倒戈，在门外接应赵盾。")
    end
end
function on_victory(game) end
function on_defeat(game) end
function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if dog_defeated and ti_fallen and game:is_unit_within("ZhaoDun47", {1,13}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
'''


def write_stages():
    stage_dir = ROOT / "game/sce/dongzhou/stage"
    (stage_dir / "50a.lua").write_text(STAGE_50A.replace("__ROWS__", rows("m078_ch50a_manifest.json")), encoding="utf-8")
    (stage_dir / "50b.lua").write_text(STAGE_50B.replace("__ROWS__", rows("m079_ch50b_manifest.json")), encoding="utf-8")
    (stage_dir / "50c.lua").write_text(STAGE_50C.replace("__ROWS__", rows("m080_ch50c_manifest.json")), encoding="utf-8")


def update_config():
    path = ROOT / "game/sce/dongzhou/config.lua"
    heroes = '''        ,{ id = "GongZiGuiSheng50", class = "Lord", stat = {88, 90, 90, 90, 88}, model = "lord-1-red" }
        ,{ id = "HuaYuan50", class = "Strategist", stat = {92, 86, 98, 96, 94}, model = "Strategist-1-blue" }
        ,{ id = "ZhengGuard50", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ZhengCavalry50", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-red" }
        ,{ id = "ZhengArcher50", class = "Archer", stat = {83, 89, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "SongGuard50", class = "Infantry", stat = {84, 89, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "SongCavalry50", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "SongArcher50", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
        ,{ id = "QinSiegeCaptain50", class = "Cavalry", stat = {87, 92, 84, 88, 86}, model = "cavalry-1-blue" }
        ,{ id = "JiaoDefender50", class = "Infantry", stat = {84, 89, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "JinReliefGuard50", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "JinReliefCavalry50", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-red" }
        ,{ id = "JinReliefArcher50", class = "Archer", stat = {83, 89, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "QinSiegeGuard50", class = "Infantry", stat = {84, 89, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "QinSiegeCavalry50", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "QinSiegeArcher50", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
        ,{ id = "TiMiMing50", class = "Infantry", stat = {92, 98, 78, 94, 90}, model = "infantry-1-red" }
        ,{ id = "JinLingGong50", class = "Lord", stat = {84, 82, 76, 78, 74}, model = "lord-1-blue" }
        ,{ id = "TuAnGu50", class = "Strategist", stat = {86, 84, 92, 88, 82}, model = "Strategist-1-blue" }
        ,{ id = "LingAo50", class = "Cavalry", stat = {82, 94, 55, 88, 80}, model = "cavalry-1-blue" }
        ,{ id = "LingZhe50", class = "Infantry", stat = {88, 92, 86, 90, 90}, model = "infantry-1-red" }
        ,{ id = "PalaceGuard50", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "PalaceArcher50", class = "Archer", stat = {83, 89, 84, 85, 83}, model = "archer-1-blue" }
'''
    replace_once(path, "    },\n    equipments = {},", heroes + "    },\n    equipments = {},")
    replace_once(path, '"48a", "48b", "49" }', '"48a", "48b", "49", "50a", "50b", "50c" }')


def update_gui():
    path = ROOT / "rl/play_gui.py"
    block = '''_LARGE_BATTLE_MAPS["m078.png"] = (42, 28, 48)
_LARGE_BATTLE_MAPS["m079.png"] = (46, 30, 48)
_LARGE_BATTLE_MAPS["m080.png"] = (38, 26, 48)

HERO_LABELS.update({
    "GongZiGuiSheng50": "公子归生", "HuaYuan50": "华元",
    "ZhengGuard50": "郑军甲士", "ZhengCavalry50": "郑军骑兵", "ZhengArcher50": "郑军弓手",
    "SongGuard50": "宋军甲士", "SongCavalry50": "宋军骑兵", "SongArcher50": "宋军弓手",
    "QinSiegeCaptain50": "秦军主将", "JiaoDefender50": "焦城守将",
    "JinReliefGuard50": "晋军甲士", "JinReliefCavalry50": "晋军骑兵", "JinReliefArcher50": "晋军弓手",
    "QinSiegeGuard50": "秦军甲士", "QinSiegeCavalry50": "秦军骑兵", "QinSiegeArcher50": "秦军弓手",
    "TiMiMing50": "提弥明", "JinLingGong50": "晋灵公", "TuAnGu50": "屠岸贾",
    "LingAo50": "灵獒", "LingZhe50": "灵辄", "PalaceGuard50": "宫中伏甲", "PalaceArcher50": "宫中弓手",
})
HERO_BIOS.update({
    "GongZiGuiSheng50": "郑穆公时执政公子归生。奉楚庄王之命伐宋，在大棘击败宋军并俘虏右师华元。",
    "HuaYuan50": "宋国右师，历仕昭公、文公。大棘之战兵败被俘，此后仍长期主持宋国军政与外交。",
    "QinSiegeCaptain50": "率秦军越过属国崇、直接围攻晋国焦城的将领；赵穿回援后因围城无望撤军。",
    "JiaoDefender50": "坚守焦城、等待赵穿援军打通东门的晋国守将。",
    "TiMiMing50": "赵盾车右，勇力过人。桃园宴伏中折杀灵獒，以身护卫赵盾突围，独战伏甲而死。",
    "JinLingGong50": "晋国国君夷皋。成年后荒淫暴虐，宠信屠岸贾，在桃园设伏谋杀正卿赵盾。",
    "TuAnGu50": "晋灵公宠臣。修建桃园、纵容暴政，又先后安排鉏麑刺杀与宫宴伏甲，意图除掉赵盾。",
    "LingAo50": "晋灵公豢养的赤色猛犬，由獒奴牵引咬杀有罪之人；追击赵盾时被提弥明折颈杀死。",
    "LingZhe50": "赵盾昔日在翳桑救济的饿者。后成为晋国公徒，在桃园伏甲中倒戈报恩，背负赵盾脱险。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "GongZiGuiSheng50": 35, "HuaYuan50": 49, "QinSiegeCaptain50": 38, "JiaoDefender50": 25,
    "TiMiMing50": 34, "JinLingGong50": 7, "TuAnGu50": 45, "LingAo50": 17, "LingZhe50": 39,
})
SPEAKER_PORTRAIT_INDEX.update({
    "仲遂": 45, "叔孙得臣": 42, "齐惠公": 7, "公冉务人": 39, "叔仲彭生": 25,
    "季孙行父": 49, "出姜": 12, "叔肹": 31, "楚庄王": 7, "苏从": 42,
    "公子归生": 35, "华元": 49, "赵朔": 37, "韩厥": 42, "秦军主将": 38,
    "焦城守将": 25, "赵穿": 35, "晋灵公": 7, "赵盾": 42, "士会": 31,
    "屠岸贾": 45, "鉏麑": 38, "提弥明": 34, "灵辄": 39,
})
HISTORICAL_DEATH_HEROES.update({"TiMiMing50", "LingAo50"})

'''
    replace_once(path, 'if _original_name == "__main__":', block + 'if _original_name == "__main__":')


def update_prior_test():
    path = ROOT / "rl/chapter49_test.py"
    replace_once(path, 'assert \'"47a", "47b", "48a", "48b", "49" }\' in config',
                 'assert \'"47a", "47b", "48a", "48b", "49", "50a", "50b", "50c" }\' in config')


def main():
    write_stages()
    update_config()
    update_gui()
    update_prior_test()
    print("Chapter 50 stages, config, GUI metadata, and prior regression anchor updated.")


if __name__ == "__main__":
    main()
