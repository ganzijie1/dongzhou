gsupply_enabled = true

gitems = {
    { id = "medicine", name = "金疮药", hp = 120, mp = 0, price = 120, initial = 2 },
    { id = "spirit_powder", name = "清心散", hp = 0, mp = 30, price = 150, initial = 1 }
}

gcommanders = {
    "ZhengShiZiHu8", "GaoQuMi8", "ZhuDan8", "GongZiYuan8", "GongSunDaiZhong8"
}
ambush_revealed = false

gduel_enabled = true
gevents_enabled = true
gduels = {
    {
        attacker = "ZhuDan8", defender = "XiaoLiang8", exp = 40,
        attacker_speech = "小良休走，且看我这一箭！",
        defender_speech = "郑军弓手，也敢阻我铁骑！",
        result_speech = "小良已死，截断戎兵退路！",
        text = "祝聃引弓一箭，正中小良头颅，小良坠马而死！"
    },
    {
        attacker = "ZhengShiZiHu8", defender = "DaLiang8", exp = 50,
        attacker_speech = "大良，你已陷入重围，还不授首！",
        defender_speech = "黄口孺子，先吃我一刀！",
        result_speech = "戎帅已斩，诸军合围收兵！",
        text = "大良撞上世子忽戎车，措手不及，被世子忽挥兵斩杀！"
    }
}

gsites = {
    {
        id = "qi_ambush_camp", name = "齐军主帐", position = {15, 19},
        restore_hp = 20, restore_mp = 10,
        rewards = { { item = "medicine", amount = 1 } }
    },
    {
        id = "qi_camp_northwest", name = "齐军西北营帐", position = {13, 18},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "qi_camp_northeast", name = "齐军东北营帐", position = {17, 18},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "qi_camp_southwest", name = "齐军西南营帐", position = {13, 20},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "qi_camp_southeast", name = "齐军东南营帐", position = {17, 20},
        restore_hp = 20, restore_mp = 10, rewards = {}
    },
    {
        id = "queyang_storehouse", name = "东侧伏兵主帐", position = {25, 10},
        restore_hp = 25, restore_mp = 10,
        rewards = {
            { item = "medicine", amount = 1 },
            { item = "spirit_powder", amount = 1 }
        }
    },
    {
        id = "east_camp_northwest", name = "东营西北营帐", position = {24, 9},
        restore_hp = 25, restore_mp = 10, rewards = {}
    },
    {
        id = "east_camp_northeast", name = "东营东北营帐", position = {26, 9},
        restore_hp = 25, restore_mp = 10, rewards = {}
    },
    {
        id = "east_camp_southwest", name = "东营西南营帐", position = {24, 12},
        restore_hp = 25, restore_mp = 10, rewards = {}
    },
    {
        id = "east_camp_southeast", name = "东营东南营帐", position = {26, 12},
        restore_hp = 25, restore_mp = 10, rewards = {}
    }
}

gstory = {
    chapter = "第八回·下",
    title = "立新君华督行赂 败戎兵郑忽辞婚",
    battle_title = "鹊山伏击",
    objective = "诱北戎深入伏击圈，击败大良、小良及全部戎兵",
    map_asset = "m008-large-v2.png",
    events = {
        { id = "xiaoliang_defeated", trigger = "defeated", unit = "XiaoLiang8", speaker = "世子忽", text = "小良已亡，北戎阵势动摇，诸军向北收网！" }
    },
    intro = {
        { speaker = "旁白", text = "齐僖公从会稷返回途中忽接急报：北戎元帅大良、小良率军破祝阿，直逼历下。" },
        { speaker = "齐僖公", text = "北戎若得利而归，齐国北境从此永无宁日。速向鲁、卫、郑三国借兵，寡人先往历城拒敌！" },
        { speaker = "郑庄公", text = "齐国每逢郑国用兵必来相助，如今齐有戎患，世子忽当率高渠弥、祝聃星夜救援。" },
        { speaker = "世子忽", text = "戎兵善走而阵形不整，又贪功不相救。可用偏师诈败，引其追入伏地，再首尾夹击。" },
        { speaker = "齐僖公", text = "齐兵伏于东门截其前路，郑兵伏于北面断其归途，此计万无一失。" },
        { speaker = "公孙戴仲", text = "末将先出关挑战，只败不胜，把小良一路引到东门伏兵之处。" },
        { speaker = "公子元", text = "我率齐军藏入东门茨苇。待戎军追兵尽入，便以炮声为号杀出。" },
        { speaker = "高渠弥", text = "戎军受伏必向鹊山逃窜，我在山坳设第二重伏兵，截住大良后队。" },
        { speaker = "祝聃", text = "小良若在乱军中冲阵，我自以强弓取他性命。" },
        { speaker = "世子忽", text = "我在北路最后收网。大良、小良一死，北戎余众自然溃散。" },
        { speaker = "军令", text = "从南面伏兵营地出击，击败全部北戎。世子忽与大良、祝聃与小良相邻时会触发史实单挑。" }
    },
    victory = {
        { speaker = "公孙戴仲", text = "戎兵已经追入东门！公子元，快举伏兵！" },
        { speaker = "公子元", text = "炮声已起，齐军截住前路。敌军前后冲撞，阵势大乱！" },
        { speaker = "高渠弥", text = "鹊山伏兵尽出，大良、小良已无路可逃！" },
        { speaker = "旁白", text = "郑、齐两军前后夹击，北戎大败。小良中祝聃一箭坠马，大良突围时又被世子忽斩杀。" },
        { speaker = "齐僖公", text = "若非世子英雄，齐国何能一战退戎？寡人愿把女儿嫁与世子，永结齐郑之好。" },
        { speaker = "世子忽", text = "昔日无事尚不敢仰攀，今日奉命救齐而受室归国，天下必说我挟功求婚，实不敢从。" },
        { speaker = "高渠弥", text = "齐国强盛，世子若结此婚，日后可得大国援助。还望再三思量。" },
        { speaker = "世子忽", text = "我能自立功业，不愿以婚姻攀附强国。此意已决，不必再劝。" },
        { speaker = "旁白", text = "世子忽回郑复命。祭足担心郑庄公诸子争位，认为世子失去齐援，日后必有内患。" },
        { speaker = "旁白", text = "高渠弥与公子亹本就亲厚，又因世子忽猜疑而渐生嫌隙。祭足只得另谋陈、卫为援，替世子迎娶陈国妫氏。" },
        { speaker = "祭足", text = "齐婚既辞，只能联陈修卫，使三国互为援助。储位之争看似未起，祸根却已暗伏。" },
        { speaker = "下回预告", text = "第九回：齐侯送文姜婚鲁，祝聃射周王中肩。" }
    },
    defeat = {
        { speaker = "世子忽", text = "伏兵尚未合围，戎军却已冲破北路。今日先退回历城重整！" },
        { speaker = "旁白", text = "北戎保住两名元帅，齐国北境仍在危急之中。" }
    }
}

gstage = {
    title_id = "QueShanAmbush",
    turn_limit = 22,
    map = {
        blocked_edges = {},
        size = {30, 22},
        terrain = {
            "FFFmFFFFFFFFFFFFFFFFFFFFFFFmFF",
            "FFFmmFFFffffFFFFFFFFFFFFFFFFmF",
            "FFFmmmFFFffffFfFFFFFFFFFFFFFmF",
            "FmFmmmmffffffffffFFffFFFFFFFFF",
            "mFmmmmmFFffffffffffffFfffffFmF",
            "FmmmmmmFfffffffffffffffffffFmF",
            "mFmmmmmfFfffffffffffffffffffmF",
            "mmFmmmfFffffffffffffffPPPPPPPF",
            "mFmmFfFfffffffffffffffPwwwwwPm",
            "mFFmFFffffffffffffffffPwewewPF",
            "FmFmFffffffffffffffffffwwewwPF",
            "FFmFmffffffffffffffffffwwwwwPF",
            "FmmFFfffffffffffffffffPwewewPF",
            "FFmmFFffffffffffffffffPPPPPPPF",
            "FFFFFfffffffffffffffffffffFffF",
            "FFFFFffffffffffffffffffffffFFF",
            "FFFFfffffffPPPffPPPfffffFffFFF",
            "FFFfFFfffffPwwwwwwPffffffffFFF",
            "FmFmmffffffPwewwwePffffffffffF",
            "FFmFfmfffffPwwwewwPffFfffffffF",
            "FFFFFFFFFFfPwewwwePFFFFFFFFFFF",
            "FFFFFFFFFFFPPPPPPPPFFFFFFFFFFF",
        },
        has_terrain_layers = true,
        terrain_layers = {
            { position = {2, 0}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 0}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 0}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {8, 0}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {9, 0}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {10, 0}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {11, 0}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {26, 0}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {27, 0}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {28, 0}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 1}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 1}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 1}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {5, 1}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {7, 1}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {8, 1}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {9, 1}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {10, 1}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {11, 1}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {12, 1}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {14, 1}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {27, 1}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {28, 1}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {29, 1}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 2}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 2}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 2}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {5, 2}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {6, 2}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {7, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {8, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {9, 2}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {12, 2}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {13, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {14, 2}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {15, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {16, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {19, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {20, 2}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {27, 2}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {28, 2}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {29, 2}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 3}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 3}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {2, 3}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 3}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {6, 3}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {7, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {8, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {13, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {15, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {16, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {17, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {18, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {19, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {20, 3}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {21, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {22, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {23, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {24, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {25, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {26, 3}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {28, 3}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 4}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {1, 4}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 4}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {6, 4}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {7, 4}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {8, 4}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {9, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {17, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {18, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {20, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {21, 4}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {22, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {23, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {24, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {25, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 4}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 4}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {28, 4}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {29, 4}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 5}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 5}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {6, 5}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {7, 5}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {8, 5}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {21, 5}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 5}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 5}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {28, 5}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {29, 5}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 6}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {1, 6}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 6}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {6, 6}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {7, 6}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {8, 6}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {9, 6}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 6}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {28, 6}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {29, 6}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 7}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {2, 7}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 7}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 7}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {5, 7}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {6, 7}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {7, 7}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {8, 7}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 7}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 8}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {1, 8}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 8}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {3, 8}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 8}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {5, 8}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {6, 8}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {7, 8}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 8}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {0, 9}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {1, 9}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 9}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 9}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 9}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {5, 9}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {6, 9}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 9}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {0, 10}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 10}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {2, 10}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 10}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 10}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {5, 10}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {1, 11}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 11}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {3, 11}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {4, 11}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {5, 11}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {0, 12}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 12}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {2, 12}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {3, 12}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {4, 12}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {5, 12}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {1, 13}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 13}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {3, 13}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 13}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {5, 13}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {6, 13}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {2, 14}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 14}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {4, 14}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {5, 14}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {25, 14}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 14}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {27, 14}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {28, 14}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 14}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {4, 15}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {5, 15}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {24, 15}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 15}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 15}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {28, 15}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {3, 16}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {4, 16}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {5, 16}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {23, 16}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {24, 16}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {25, 16}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 16}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 16}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {1, 17}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 17}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {3, 17}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {4, 17}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {5, 17}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {6, 17}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {24, 17}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 17}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 17}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {28, 17}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {0, 18}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {1, 18}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {2, 18}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {3, 18}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {4, 18}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {5, 18}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {21, 18}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 18}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {28, 18}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 18}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {1, 19}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {2, 19}, primary_terrain = "m", secondary_terrain = "F", coverage = 72 },
            { position = {3, 19}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {4, 19}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {5, 19}, primary_terrain = "m", secondary_terrain = "f", coverage = 72 },
            { position = {6, 19}, primary_terrain = "f", secondary_terrain = "m", coverage = 72 },
            { position = {7, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {8, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {9, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {19, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {20, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {21, 19}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {22, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {23, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {24, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {25, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {26, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {27, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {28, 19}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {29, 19}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {2, 20}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {4, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {5, 20}, primary_terrain = "F", secondary_terrain = "m", coverage = 72 },
            { position = {6, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {7, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {8, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {9, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {10, 20}, primary_terrain = "f", secondary_terrain = "F", coverage = 72 },
            { position = {19, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {20, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {22, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {23, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {24, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {25, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {26, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {27, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {28, 20}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
            { position = {10, 21}, primary_terrain = "F", secondary_terrain = "f", coverage = 72 },
        },
        file = "map.bmp"
    },
    deploy = {
        unselectables = {
            { position = {15, 19}, hero = "ZhengShiZiHu8" },
            { position = {14, 19}, hero = "GaoQuMi8" },
            { position = {16, 19}, hero = "ZhuDan8" },
            { position = {14, 18}, hero = "GongZiYuan8" },
            { position = {16, 18}, hero = "GongSunDaiZhong8" }
        },
        num_required_selectables = 0,
        selectables = {}
    },
    rewards = { equipments = {}, money = 440 }
}

function on_deploy(game)
    game:appoint_hero("ZhengShiZiHu8", 1)
    game:appoint_hero("GaoQuMi8", 1)
    game:appoint_hero("ZhuDan8", 1)
    game:appoint_hero("GongZiYuan8", 1)
    game:appoint_hero("GongSunDaiZhong8", 1)
end

function on_begin(game)
    -- 大良部据守东侧营寨。
    game:generate_unit("DaLiang8", 1, Enum.force.enemy, {25, 10})
    game:generate_unit("BeiRongWarrior8", 1, Enum.force.enemy, {24, 11})
    game:generate_unit("BeiRongWarrior8", 1, Enum.force.enemy, {26, 11})
    game:generate_unit("BeiRongArcher8", 1, Enum.force.enemy, {25, 11})

    -- 小良部在北面正面列阵。
    game:generate_unit("XiaoLiang8", 1, Enum.force.enemy, {20, 4})
    game:generate_unit("BeiRongWarrior8", 1, Enum.force.enemy, {19, 5})
    game:generate_unit("BeiRongWarrior8", 1, Enum.force.enemy, {21, 5})
    game:generate_unit("BeiRongArcher8", 1, Enum.force.enemy, {20, 5})
end

function on_update(game)
    if not ambush_revealed and game:has_unit("AlliedGuard72") then
        ambush_revealed = true
    end
    if ambush_revealed then return end
    if not game:is_force_within(Enum.force.own, {25, 10}, 5) then return end

    ambush_revealed = true
    local qi_guard = game:generate_unit("AlliedGuard72", 1, Enum.force.own, {21, 13})
    game:generate_unit("AlliedArcher72", 1, Enum.force.own, {21, 14})
    game:push_cmd_speak(qi_guard, "戎军已入东门伏地，齐军截住前路！")
end

function on_victory(game)
end

function on_defeat(game)
end

function end_condition(game)
    if game:get_num_commanders_alive() < #gcommanders then
        return Enum.status.defeat
    end
    if ambush_revealed and game:get_num_enemies_alive() == 0 then
        return Enum.status.victory
    end
    return Enum.status.undecided
end