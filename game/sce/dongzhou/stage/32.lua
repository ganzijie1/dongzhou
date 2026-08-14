palace_reserves_arrived = false
avenue_spoken = false
gate_spoken = false
yiya_id = -1
shudiao_id = -1

gsupply_enabled = true
gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}
gcommanders = { "GongZiZhao32", "CuiYao32" }
gduel_enabled = false
gduels = {}
gsites = {
    { id = "linzi_east_gate", name = "临淄东门", position = {15, 6},
      restore_hp = 15, restore_mp = 5, rewards = {} }
}

gstory = {
    chapter = "第三十二回",
    title = "晏蛾儿逾墙殉节 群公子大闹朝堂",
    battle_title = "临淄夜逃",
    objective = "护送公子昭本人到达东侧出口（18，6）；公子昭或崔夭被击退则失败；第三回合宫甲从西侧增援",
    map_asset = "m053.png",
    intro = {
        { speaker = "", text = "齐桓公违背管仲遗言，重新任用易牙、竖刁、开方。鲍叔牙进谏不从，忧愤病逝，三人从此专权用事，顺从者富贵，反对者被逐。" },
        { speaker = "", text = "郑国名医秦缓游至临淄。世人因他医术高明，将他比作上古扁鹊，也称扁鹊。" },
        { speaker = "扁鹊", text = "君侯之病初在腠理，尚可汤熨；如今已经深入血脉。若仍不治疗，日后药石难及。" },
        { speaker = "齐桓公", text = "寡人身体无恙，医者不过喜欢把无病说成有病，好显示自己的本领。" },
        { speaker = "", text = "扁鹊每隔五日再见，先说病入血脉，继而深入肠胃。第四次望见桓公气色，他转身便走。" },
        { speaker = "扁鹊", text = "病已入骨髓，即使司命也无可奈何。臣不再多言，只能离开齐国。" },
        { speaker = "", text = "齐桓公共有六位如夫人，各有公子。长卫姬之子无亏最年长，郑姬之子昭却早已由桓公托付宋襄公、立为世子。" },
        { speaker = "易牙", text = "主公病势已重。若让世子昭进入寝宫，长公子无亏便再无机会。先封宫门，再隔绝内外。" },
        { speaker = "竖刁", text = "假传君命，就说主公厌恶人声，群臣公子一概不得入宫。我率内侍守门，你率宫甲巡逻。" },
        { speaker = "", text = "易牙、竖刁将桓公身边侍卫尽数逐出，又在寝室周围筑起高墙，只留墙下一处小穴，让内侍探听生死。" },
        { speaker = "晏蛾儿", text = "妾曾受主公一幸之恩，今日纵然翻越三丈高墙，也要到寝宫看主公最后一面。" },
        { speaker = "齐桓公", text = "寡人腹中饥渴，为何连一碗粥、一口热水也无人送来？太子昭又在何处？" },
        { speaker = "晏蛾儿", text = "易牙、竖刁封死宫门，世子也被挡在外面。妾只能逾墙而入，若主公不幸，情愿以死相送。" },
        { speaker = "", text = "齐桓公悔恨未听管仲遗言，以衣袖掩面而死。晏蛾儿覆盖遗体，随后触柱殉节。" },
        { speaker = "易牙", text = "先不要发丧。今夜先拥立无亏，再发兵东宫擒杀世子昭，天亮之前便可定局。" },
        { speaker = "", text = "当夜公子昭梦见晏蛾儿示警，惊醒后离开东宫，赶到上卿高虎府中。宫甲随即包围东宫，开始全城搜捕。" },
        { speaker = "高虎", text = "梦中称先公，主公恐怕已经薨逝。你应立即投奔宋国，宋襄公受过先君托付，必会相助。" },
        { speaker = "公子昭", text = "易牙、竖刁已经封锁宫门，东宫也被包围。临淄四门之中，哪一处还能出城？" },
        { speaker = "高虎", text = "门下士崔夭掌管东门锁钥。我是守国之臣不能同行，他可开门护送世子出境。" },
        { speaker = "崔夭", text = "私放太子也是死罪。与其留下受奸臣诛杀，不如亲自执辔，护送世子投奔宋国。" },
        { speaker = "军令", text = "公子昭本人进入（18，6）才算过关，崔夭先到不会触发胜利。外城墙不可跨越，只有东侧城门可以通行；第三回合西路还有宫甲增援。" }
    },
    events = {
        { id = "palace_reserves", trigger = "turn", turn = 3,
          speaker = "竖刁", text = "东宫没有找到世子！西街巡卒全部转向东门，封住出城大道！" },
        { id = "east_avenue", trigger = "approach", position = {12, 6}, radius = 2,
          speaker = "崔夭", text = "东门已经在望。主路两侧都是宫甲，护住世子继续向东，不要被拖住！" },
        { id = "east_gate", trigger = "approach", position = {15, 6}, radius = 1,
          speaker = "公子昭", text = "城门锁钥已开！崔夭随我出城，直奔宋国，不可再回头！" }
    },
    victory = {
        { speaker = "竖刁", text = "东门已经打开，世子车驾出了临淄！封闭其余城门，绝不能让百官与他会合。" },
        { speaker = "公子昭", text = "父君生死未明，我却只能连夜出奔。若能得到宋公相助，必回临淄清除奸臣。" },
        { speaker = "崔夭", text = "东门已经重新关闭，追兵一时赶不上。我们沿大道昼夜兼程，尽快进入宋境。" },
        { speaker = "", text = "易牙、竖刁搜遍东宫不见公子昭，转而拥立公子无亏。宫中凶信泄露，百官连夜聚集朝堂质问。" },
        { speaker = "管平", text = "无亏从未受命册立，世子昭才是先君储君！今日先诛易牙、竖刁，再迎世子还朝！" },
        { speaker = "竖刁", text = "昭已经畏罪逃走，先君临终命长子无亏继位。再敢抗命者，宫甲当场诛杀！" },
        { speaker = "", text = "管平举笏击打竖刁，数百宫甲随即挥兵冲入百官之中。官员手无兵器，约有十分之三死于朝堂，余者负伤逃散。" },
        { speaker = "公子无亏", text = "朝堂上只有两位拥立之臣，百官又不肯朝贺。即便坐上君位，又如何号令齐国？" },
        { speaker = "", text = "国懿仲、高虎披麻入宫，只肯为先君哭丧，不肯先拜新君。无亏只得令宫甲守住正殿。" },
        { speaker = "公子潘", text = "无亏可以自立，我也同是先君之子。开方已经召集家丁死士，今日便据守右殿。" },
        { speaker = "公子元", text = "太子若回来，我们自然让位；太子不回，齐国江山也不能只由无亏一人独占。" },
        { speaker = "公子商人", text = "我与公子元互为犄角，一人守左殿，一人守朝门。谁想吞并齐国，先问我们的家甲。" },
        { speaker = "", text = "无亏据正殿，潘据右殿，元据左殿，商人据朝门，四方各自列兵。公子雍不愿参与，独自逃往秦国。" },
        { speaker = "", text = "临淄朝中如同敌国，街道断绝行人。四方相持两个多月，无人收殓齐桓公。" },
        { speaker = "高虎", text = "诸公子只知争位，不知治丧。我们召集食齐俸禄的群臣，同入朝堂，以死责他们先尽人子之礼。" },
        { speaker = "国懿仲", text = "立子以长并非无名。无亏若肯主持先君丧事，我们暂奉他主丧，再以大义劝退诸公子兵众。" },
        { speaker = "公子无亏", text = "先君去世六十七日尚未入棺，孤之罪通于天。只要诸弟撤兵，孤愿立即治丧。" },
        { speaker = "", text = "高、国二老率群臣进入寝宫。齐桓公遗体已腐坏生虫，晏蛾儿却面色如生；众人分别收殓，奉无亏主丧。" },
        { speaker = "", text = "公子元、潘、商人见高、国二卿主持丧礼，知道一时无法争胜，便解散兵众，换上丧服入宫哭临。" },
        { speaker = "", text = "公子昭抵达宋国，向宋襄公哭诉易牙、竖刁作乱。宋襄公想起齐桓公当年托孤，决意帮助昭返回齐国。" },
        { speaker = "宋襄公", text = "不救遗孤是不仁，受托而弃是不义。寡人将传檄诸侯，合兵讨齐，迎立世子昭。" },
        { speaker = "公子目夷", text = "宋国地小兵少，贤才与险固都不如齐。救昭是义，借此争当霸主却应谨慎。" },
        { speaker = "", text = "卫文公以世子名分为公义，答应出兵；鲁僖公却主张立长，准备帮助无亏。诸侯立场由此分裂。" },
        { speaker = "", text = "次年三月，宋襄公联合卫、曹、邾三国，奉公子昭进军齐郊。易牙统兵出城，竖刁坐镇临淄。" },
        { speaker = "高虎", text = "当初拥立无亏，只为收殓先君。如今世子已至，又有诸侯相助，应诛竖刁、迎昭复位。" },
        { speaker = "下回预告", text = "第三十三回：高虎、国懿仲将设伏诛除竖刁，宋襄公也将率诸侯之师迎立公子昭。" }
    },
    defeat = {
        { speaker = "崔夭", text = "宫甲已经封住东门，世子无法出城。临淄内外都落入易牙、竖刁掌握。" },
        { speaker = "", text = "公子昭或崔夭被击退，本关失败。" }
    }
}

gstage = {
    title_id = "EscapeLinzi32", turn_limit = 12,
    map = {
        blocked_edges = {}, size = {19, 14},
        terrain = {
            "rrrrrrrrrrrrrrrrrrr",
            "rWWWWWWWWWWWWWWWrrr",
            "rWhhhihhhihhhihWrrr",
            "rWhhiiihhiihhhiWrrr",
            "rWhhiiiihhhihhiWrrr",
            "rWhhiiiiihhihhiWrrr",
            "rWiiiiiiiiiiiiiGfff",
            "rWhhiiiihhhihhiWrrr",
            "rWhhgggihhhihhiWrrr",
            "rWhhgggiiiihhhiWrrr",
            "rWhhgggiiiihhhiWrrr",
            "rWhhhiiihhihhhiWrrr",
            "rWWWWWWWWWWWWWWWrrr",
            "rrrrrrrrrrrrrrrrrrr"
        }, file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {7, 9}, hero = "GongZiZhao32" },
            { position = {8, 9}, hero = "CuiYao32" }
        }, num_required_selectables = 0, selectables = {}
    },
    rewards = { equipments = {}, money = 4000 }
}

function on_deploy(game)
    game:appoint_hero("GongZiZhao32", 1)
    game:appoint_hero("CuiYao32", 1)
end

function on_begin(game)
    game:generate_unit("PrinceGuard32", 1, Enum.force.own, {7, 10})
    game:generate_unit("PrinceArcher32", 1, Enum.force.own, {9, 10})
    yiya_id = game:generate_unit("YiYa32", 1, Enum.force.enemy, {5, 2})
    shudiao_id = game:generate_unit("ShuDiao32", 1, Enum.force.enemy, {9, 2})
    game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {4, 3})
    game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {6, 3})
    game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {11, 6})
    game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {13, 6})
    game:generate_unit("PalaceArcher32", 1, Enum.force.enemy, {14, 5})
    game:generate_unit("PalaceArcher32", 1, Enum.force.enemy, {14, 7})
end

function on_update(game)
    if not palace_reserves_arrived and game:get_turn_current() >= 3 then
        palace_reserves_arrived = true
        game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {2, 6})
        game:generate_unit("PalaceGuard32", 1, Enum.force.enemy, {3, 6})
        game:generate_unit("PalaceArcher32", 1, Enum.force.enemy, {4, 6})
        game:generate_unit("PalaceArcher32", 1, Enum.force.enemy, {5, 6})
        game:push_cmd_speak(shudiao_id, "西街巡卒已经赶到！沿主路向东追，不许公子昭出城！")
        game:push_cmd_speak(0, "宫甲增援从西侧进入。公子昭继续向东门撤离，不要回身恋战！")
    end
    if not avenue_spoken and game:is_unit_within("GongZiZhao32", {12, 6}, 2) then
        avenue_spoken = true
        game:push_cmd_speak(0, "东门主路已经在前！崔夭护住侧翼，公子昭本人继续向出口移动！")
    end
    if not gate_spoken and game:is_unit_within("GongZiZhao32", {15, 6}, 1) then
        gate_spoken = true
        game:push_cmd_speak(0, "东门已开！越过城门后继续走到（18，6）才算完全脱离临淄！")
    end
end

function on_victory(game) end
function on_defeat(game) end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then return Enum.status.defeat end
    if game:is_unit_within("GongZiZhao32", {18, 6}, 0) then return Enum.status.victory end
    return Enum.status.undecided
end
