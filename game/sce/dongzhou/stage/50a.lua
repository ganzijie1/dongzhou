gally_hold_position = true
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
        "FgFfFfFgFmFfFgFfFfFgFfFfFgFmFfFgFfFfFgFfFf",
        "FfFfFgFfFfFgFfFmFgFfFfFgFfFfFgFfFmFgFfFfFg",
        "fFgFfFfFgFfFmFgFfFfFgFfFfFgFfFmFgFfFfFgFfF",
        "mFffffggfmffggffffmgffffggfmffggffffmgfFfF",
        "FfFfggmfffggfffmggffffggmfffggfffmggffffFg",
        "FfFmffffggffmfggffffgmffffggffmfggffffgmFf",
        "mFffffggffffggffffggffffggffffggffffmgfFfF",
        "fFffggffffggffffggffffggffffggffffggfffFgF",
        "FfFmffffggffffggffffggffffggffffggffffgmFf",
        "FgFfffggffffggffffggffffggffffggffffmgffFf",
        "fFffggffffggffffggffffggffffggffffggfffFgF",
        "fFgmffffggffffggffffggffffggffffggffffgFfF",
        "wwwwwwwwwwwwggffffggffffwwwwwwwwwwwwmgffFf",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
        "mFffffggffffwwwwwwwwwwwwggffffggffffwwwwww",
        "FfFfggffffggffffggffffggffffggffffggffffFg",
        "FfFmffffggffffggffffggffffggffffggffffgmFf",
        "mFffffggffffggffffggffffggffffggffffmgfFfF",
        "fFffggffffggffffggffffggffffggffffggfffFgF",
        "FfFmffffggffffggffffggffffggffffggffffgmFf",
        "FgFfffggffffggffffggffffggffffggffffmgffFf",
        "fFffggmfffggfffmggffffggmfffggfffmggfffFgF",
        "fFgmffffggffmfggffffgmffffggffmfggffffgFfF",
        "FgFfffggfmffggffffmgffffggfmffggffffmgffFf",
        "FfFfFgFfFfFgFfFmFgFfFfFgFfFfFgFfFmFgFfFfFg",
        "fFgFfFfFgFfFmFgFfFfFgFfFfFgFfFmFgFfFfFgFfF",
        "mFfFfFgFfFfFgFfFfFmFfFfFgFfFfFgFfFfFmFfFfF",
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
