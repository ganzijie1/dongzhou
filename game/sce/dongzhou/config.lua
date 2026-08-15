gconfig = {
    id = "DongZhou",
    unit_classes = {
        { id = "Lord", promotions = 3, stat_grades = "AAAAA", attack_range = "Adjacent4", move = 6, hp = {100, 5}, mp = {20, 1} },
        { id = "Infantry", promotions = 3, stat_grades = "BASBB", attack_range = "Adjacent8", move = 5, hp = {110, 6}, mp = {10, 1} },
        { id = "Cavalry", promotions = 3, stat_grades = "SBABB", attack_range = "Adjacent4", move = 6, hp = {100, 5}, mp = {10, 1} },
        { id = "Archer", promotions = 3, stat_grades = "ABBBS", attack_range = "Distance2_8", move = 5, hp = {90, 4}, mp = {10, 1} },
        { id = "Strategist", promotions = 3, stat_grades = "BSBBB", attack_range = "Adjacent4", move = 5, hp = {90, 4}, mp = {40, 2} },
        { id = "Support", promotions = 3, stat_grades = "CSCAA", attack_range = "Adjacent4", move = 5, hp = {80, 3}, mp = {50, 2} },
        { id = "King", promotions = 3, stat_grades = "AAAAA", attack_range = "Adjacent4", move = 6, hp = {105, 5}, mp = {45, 2} }
    },
    terrains = {
        { id = "Flatland", char = "f" },
        { id = "Grass", char = "g" },
        { id = "Snow", char = "s" },
        { id = "Forest", char = "F" },
        { id = "Wasteland", char = "w" },
        { id = "Mountain", char = "m" },
        { id = "RockyMountain", char = "r" },
        { id = "Wall", char = "W" },
        { id = "Water", char = "~" },
        { id = "ShallowRiver", char = "v" },
        { id = "Watchtower", char = "c" },
        { id = "Storehouse", char = "b" },
        { id = "Camp", char = "e" },
        { id = "Gate", char = "G" },
        { id = "DeerFort", char = "D" },
        { id = "Fence", char = "P" },
        { id = "CityInterior", char = "i" },
        { id = "Residence", char = "h" },
        { id = "Castle", char = "C" }
    },
    terrain_movecost = {
        {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {2, 2, 3, 2, 2, 2, 2}, {2, 1, 2, 1, 1, 1, 2}, {2, 1, 2, 1, 1, 1, 2},
        {3, 2, 3, 2, 2, 2, 3}, {255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255}, {3, 2, 4, 2, 2, 2, 3},
        {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1},
        {255, 255, 255, 255, 255, 255, 255}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}
    },
    terrain_effect = {
        {100, 100, 110, 100, 100, 100, 100}, {100, 100, 105, 100, 100, 100, 100}, {95, 100, 90, 100, 100, 100, 95}, {100, 110, 85, 110, 110, 110, 100}, {95, 105, 90, 105, 105, 105, 95},
        {90, 110, 70, 105, 105, 105, 90}, {100, 100, 100, 100, 100, 100, 100}, {110, 115, 85, 110, 100, 100, 110}, {100, 100, 100, 100, 100, 100, 100},
        {90, 100, 80, 100, 100, 100, 90}, {110, 110, 105, 110, 110, 110, 110}, {100, 100, 100, 100, 100, 100, 100}, {105, 105, 100, 105, 105, 105, 105}, {105, 105, 100, 105, 105, 105, 105}, {110, 110, 105, 110, 110, 110, 110},
        {100, 100, 100, 100, 100, 100, 100}, {105, 105, 100, 105, 105, 105, 105}, {105, 105, 100, 105, 105, 105, 105}, {110, 110, 105, 110, 110, 110, 110}
    },
    magics = {
        { id = "fire_0", target = "enemy", accuracy = "always", range = "Distance4_Incl", mp = 8,
          learnat = { { class = "Strategist", level = 1 }, { class = "Lord", level = 3 } },
          type = "deal", power = 55 },
        { id = "heal_0", target = "ally", accuracy = "always", range = "Distance4_Incl", mp = 8,
          learnat = { { class = "Support", level = 1 }, { class = "King", level = 1 } },
          type = "heal", power = 48 },
        { id = "buff_dex", target = "ally", accuracy = "always", range = "Distance3_Incl", mp = 6,
          learnat = { { class = "Support", level = 1 } },
          type = "stat_mod", stat = "dex", amount = 15, turns = 2 },
        { id = "baqi_0", target = "ally", accuracy = "always", range = "Distance3_Incl", mp = 10,
          learnat = { { class = "King", level = 1 } },
          type = "stat_mod", stat = "all", amount = 12, turns = 2 },
        { id = "inspire_0", target = "ally", accuracy = "always", range = "Distance3_Incl", mp = 7,
          learnat = { { class = "Lord", level = 1 } },
          type = "stat_mod", stat = "mor", amount = 15, turns = 2 }
    },
    heroes = {
        { id = "DuBo", class = "Strategist", stat = {92, 84, 76, 82, 95}, model = "Strategist-1-red" },
        { id = "ZuoRu", class = "Support", stat = {86, 80, 82, 90, 92}, model = "support-1-red" },
        { id = "ZhouXuanWang", class = "King", stat = {78, 90, 76, 72, 68}, model = "lord-1-blue" },
        { id = "YinJiFu", class = "Strategist", stat = {84, 88, 80, 82, 78}, model = "Strategist-1-blue" },
        { id = "ZhaoHu", class = "Cavalry", stat = {80, 84, 82, 76, 80}, model = "cavalry-1-blue" },
        { id = "RoyalGuard", class = "Infantry", stat = {72, 74, 70, 55, 65}, model = "infantry-1-blue" }
        ,{ id = "ZhouYouWang", class = "King", stat = {76, 72, 68, 58, 55}, model = "lord-1-red" }
        ,{ id = "GuoShiFu", class = "Cavalry", stat = {78, 75, 76, 82, 62}, model = "cavalry-1-red" }
        ,{ id = "ZhengBoYou", class = "Infantry", stat = {82, 86, 84, 88, 90}, model = "infantry-1-blue" }
        ,{ id = "ShenHou", class = "Lord", stat = {84, 78, 86, 88, 80}, model = "lord-1-red" }
        ,{ id = "QuanRongLord", class = "Lord", stat = {90, 92, 78, 72, 86}, model = "lord-1-red" }
        ,{ id = "QuanRongWarrior", class = "Infantry", stat = {80, 86, 70, 68, 72}, model = "infantry-1-red" }
        ,{ id = "QuanRongWarrior2", class = "Infantry", stat = {78, 84, 72, 70, 74}, model = "infantry-1-red" }
        ,{ id = "QuanRongArcher", class = "Archer", stat = {76, 82, 74, 72, 76}, model = "archer-1-red" }
        ,{ id = "QuanRongLeftWarrior", class = "Infantry", stat = {77, 83, 71, 69, 73}, model = "infantry-1-red" }
        ,{ id = "QuanRongRightWarrior", class = "Infantry", stat = {77, 83, 71, 69, 73}, model = "infantry-1-red" }
        ,{ id = "ZhengHuanGong", class = "Lord", stat = {88, 90, 86, 92, 84}, model = "lord-1-blue" }
        ,{ id = "ZhengZhuangGong", class = "Lord", stat = {90, 88, 94, 92, 86}, model = "lord-1-red" }
        ,{ id = "GongZiLu", class = "Cavalry", stat = {86, 89, 82, 84, 80}, model = "cavalry-1-red" }
        ,{ id = "ZhengVanguard", class = "Infantry", stat = {78, 82, 76, 72, 78}, model = "infantry-1-red" }
        ,{ id = "ZhengVanguard2", class = "Infantry", stat = {76, 80, 78, 74, 76}, model = "infantry-1-red" }
        ,{ id = "GongShuDuan", class = "Cavalry", stat = {88, 92, 80, 78, 84}, model = "cavalry-1-blue" }
        ,{ id = "DuanGuard", class = "Infantry", stat = {76, 80, 72, 70, 74}, model = "infantry-1-blue" }
        ,{ id = "DuanArcher", class = "Archer", stat = {74, 78, 74, 72, 76}, model = "archer-1-blue" }
        ,{ id = "GaoQuMi", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "GongZiLu5", class = "Cavalry", stat = {86, 89, 82, 84, 80}, model = "cavalry-1-red" }
        ,{ id = "ZhengEastGuard", class = "Infantry", stat = {78, 82, 76, 74, 78}, model = "infantry-1-red" }
        ,{ id = "ZhengEastArcher", class = "Archer", stat = {80, 78, 82, 80, 84}, model = "archer-1-red" }
        ,{ id = "WeiVanguard", class = "Cavalry", stat = {80, 84, 74, 78, 76}, model = "cavalry-1-blue" }
,{ id = "CoalitionGuard", class = "Infantry", stat = {76, 80, 72, 70, 74}, model = "infantry-1-blue" }
        ,{ id = "ZhouXu5", class = "Lord", stat = {86, 90, 76, 80, 78}, model = "lord-1-blue" }
        ,{ id = "ShiHou5", class = "Strategist", stat = {78, 74, 88, 84, 80}, model = "Strategist-1-blue" }
        ,{ id = "YingKaoShu6", class = "Infantry", stat = {88, 91, 80, 84, 86}, model = "infantry-1-red" }
        ,{ id = "GongZiLu6", class = "Cavalry", stat = {86, 89, 82, 84, 80}, model = "cavalry-1-red" }
        ,{ id = "GaoQuMi6", class = "Infantry", stat = {84, 87, 80, 82, 81}, model = "infantry-1-red" }
        ,{ id = "LuGongZiHui6", class = "Cavalry", stat = {82, 86, 78, 80, 79}, model = "cavalry-1-red" }
        ,{ id = "GaoCityCommander6", class = "Lord", stat = {84, 86, 82, 80, 84}, model = "lord-1-blue" }
        ,{ id = "SongDefender", class = "Infantry", stat = {78, 82, 74, 76, 76}, model = "infantry-1-blue" }
        ,{ id = "SongArcher", class = "Archer", stat = {76, 79, 80, 78, 78}, model = "archer-1-blue" }
        ,{ id = "ZhengZhuangGong7", class = "Lord", stat = {90, 88, 94, 92, 86}, model = "lord-1-red" }
        ,{ id = "YingKaoShu7", class = "Infantry", stat = {88, 91, 80, 84, 86}, model = "infantry-1-red" }
        ,{ id = "GaoQuMi7", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "GongSunE7", class = "Cavalry", stat = {86, 90, 84, 88, 82}, model = "cavalry-1-red" }
        ,{ id = "YouZaiChou7", class = "Cavalry", stat = {82, 84, 76, 78, 75}, model = "cavalry-1-blue" }
        ,{ id = "SongGuard7", class = "Infantry", stat = {72, 76, 68, 70, 70}, model = "infantry-1-blue" }
        ,{ id = "WeiGuard7", class = "Cavalry", stat = {74, 78, 68, 72, 70}, model = "cavalry-1-blue" }
        ,{ id = "CaiArcher7", class = "Archer", stat = {70, 72, 74, 72, 73}, model = "archer-1-blue" }
        ,{ id = "ZhengShiZiHu8", class = "Lord", stat = {88, 86, 84, 87, 83}, model = "lord-1-red" }
        ,{ id = "GaoQuMi8", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "ZhuDan8", class = "Archer", stat = {84, 88, 83, 85, 82}, model = "archer-1-red" }
        ,{ id = "GongZiYuan8", class = "Cavalry", stat = {82, 84, 80, 82, 80}, model = "cavalry-1-red" }
        ,{ id = "GongSunDaiZhong8", class = "Infantry", stat = {83, 85, 82, 84, 81}, model = "infantry-1-red" }
        ,{ id = "DaLiang8", class = "Cavalry", stat = {82, 86, 76, 80, 78}, model = "cavalry-1-blue" }
        ,{ id = "XiaoLiang8", class = "Cavalry", stat = {80, 84, 78, 82, 77}, model = "cavalry-1-blue" }
        ,{ id = "BeiRongWarrior8", class = "Infantry", stat = {72, 76, 70, 72, 70}, model = "infantry-1-blue" }
        ,{ id = "BeiRongArcher8", class = "Archer", stat = {70, 74, 72, 74, 71}, model = "archer-1-blue" }
        ,{ id = "ZhengZhuangGong9", class = "Lord", stat = {90, 88, 94, 92, 86}, model = "lord-1-red" }
        ,{ id = "GaoQuMi9", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "ZhuDan9", class = "Archer", stat = {84, 88, 83, 85, 82}, model = "archer-1-red" }
        ,{ id = "JiZu9", class = "Infantry", stat = {78, 82, 92, 88, 84}, model = "infantry-1-red" }
        ,{ id = "ManBo9", class = "Infantry", stat = {84, 88, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "ZhengGongZiYuan9", class = "Cavalry", stat = {82, 85, 88, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "ZhouHuanWang9", class = "King", stat = {84, 86, 82, 78, 80}, model = "lord-1-blue" }
        ,{ id = "GuoGongLinFu9", class = "Cavalry", stat = {82, 84, 86, 80, 78}, model = "cavalry-1-blue" }
        ,{ id = "ZhouGongHeiJian9", class = "Infantry", stat = {80, 82, 88, 78, 80}, model = "infantry-1-blue" }
        ,{ id = "BoYuanZhu9", class = "Cavalry", stat = {80, 83, 78, 80, 76}, model = "cavalry-1-blue" }
        ,{ id = "ChenSoldier9", class = "Infantry", stat = {72, 75, 70, 72, 70}, model = "infantry-1-blue" }
        ,{ id = "CaiWeiSoldier9", class = "Infantry", stat = {74, 77, 70, 72, 71}, model = "infantry-1-blue" }
        ,{ id = "RoyalGuard9", class = "Infantry", stat = {76, 80, 74, 72, 74}, model = "infantry-1-blue" }
        ,{ id = "ZhengWuGong", class = "Lord", stat = {88, 91, 84, 86, 86}, model = "lord-1-red" }
        ,{ id = "GongZiCheng3", class = "Strategist", stat = {78, 74, 92, 88, 84}, model = "Strategist-1-red" }
        ,{ id = "WeiWuGong", class = "Lord", stat = {86, 80, 96, 94, 92}, model = "lord-1-blue" }
        ,{ id = "JinWenHou", class = "Cavalry", stat = {88, 90, 86, 84, 86}, model = "cavalry-1-blue" }
        ,{ id = "WeiGuard31", class = "Infantry", stat = {76, 80, 74, 76, 78}, model = "infantry-1-red" }
        ,{ id = "JinGuard31", class = "Cavalry", stat = {78, 82, 72, 76, 76}, model = "cavalry-1-red" }
        ,{ id = "ZhengGuard31", class = "Infantry", stat = {77, 82, 74, 76, 78}, model = "infantry-1-red" }
        ,{ id = "CoalitionArcher31", class = "Archer", stat = {76, 80, 76, 78, 78}, model = "archer-1-red" }
        ,{ id = "QinXiangGong", class = "Lord", stat = {86, 88, 82, 84, 80}, model = "lord-1-red" }
        ,{ id = "QinVanguard41", class = "Cavalry", stat = {78, 82, 72, 76, 74}, model = "cavalry-1-red" }
        ,{ id = "QinVanguard42", class = "Infantry", stat = {76, 80, 74, 76, 75}, model = "infantry-1-red" }
        ,{ id = "QinArcher41", class = "Archer", stat = {74, 78, 76, 74, 76}, model = "archer-1-red" }
        ,{ id = "QuanRongLord41", class = "Lord", stat = {86, 90, 74, 76, 82}, model = "lord-1-blue" }
        ,{ id = "BoDing41", class = "Cavalry", stat = {84, 88, 72, 78, 78}, model = "cavalry-1-blue" }
        ,{ id = "ManYeSu41", class = "Infantry", stat = {82, 86, 76, 74, 77}, model = "infantry-1-blue" }
        ,{ id = "RongWarrior41", class = "Infantry", stat = {74, 78, 68, 72, 70}, model = "infantry-1-blue" }
        ,{ id = "RongArcher41", class = "Archer", stat = {72, 76, 70, 74, 72}, model = "archer-1-blue" }
        ,{ id = "ZhengZhuangGong72", class = "Lord", stat = {90, 88, 94, 92, 86}, model = "lord-1-red" }
        ,{ id = "GaoQuMi72", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "XiaShuYing72", class = "Infantry", stat = {86, 89, 80, 84, 84}, model = "infantry-1-red" }
        ,{ id = "QiXiGong72", class = "Lord", stat = {84, 82, 88, 84, 82}, model = "lord-1-red" }
        ,{ id = "LuYinGong72", class = "Lord", stat = {82, 80, 86, 82, 80}, model = "lord-1-red" }
        ,{ id = "AlliedGuard72", class = "Infantry", stat = {76, 80, 72, 74, 75}, model = "infantry-1-red" }
        ,{ id = "AlliedArcher72", class = "Archer", stat = {75, 78, 78, 76, 77}, model = "archer-1-red" }
        ,{ id = "XuZhuangGong72", class = "Lord", stat = {82, 80, 86, 82, 80}, model = "lord-1-blue" }
        ,{ id = "BaiLi72", class = "Infantry", stat = {80, 84, 78, 80, 79}, model = "infantry-1-blue" }
        ,{ id = "XuGuard72", class = "Infantry", stat = {74, 78, 72, 74, 74}, model = "infantry-1-blue" }
        ,{ id = "XuArcher72", class = "Archer", stat = {72, 76, 74, 76, 75}, model = "archer-1-blue" }
        ,{ id = "HuaDu81", class = "Lord", stat = {82, 80, 88, 84, 78}, model = "lord-1-red" }
        ,{ id = "SongMutineer81", class = "Infantry", stat = {76, 80, 70, 74, 72}, model = "infantry-1-red" }
        ,{ id = "SongMutineer82", class = "Cavalry", stat = {76, 80, 70, 74, 72}, model = "cavalry-1-red" }
        ,{ id = "SongMutineerArcher81", class = "Archer", stat = {74, 78, 72, 76, 74}, model = "archer-1-red" }
        ,{ id = "KongFuJia81", class = "Infantry", stat = {86, 88, 84, 86, 82}, model = "infantry-1-blue" }
        ,{ id = "SongShangGong81", class = "Lord", stat = {84, 84, 80, 80, 78}, model = "lord-1-blue" }
        ,{ id = "SongPalaceGuard81", class = "Infantry", stat = {76, 80, 72, 76, 74}, model = "infantry-1-blue" }
        ,{ id = "SongPalaceArcher81", class = "Archer", stat = {74, 78, 74, 78, 75}, model = "archer-1-blue" }
        ,{ id = "CaiJi101", class = "Cavalry", stat = {84, 86, 86, 88, 82}, model = "cavalry-1-red" }
        ,{ id = "CaiHunter101", class = "Archer", stat = {76, 80, 72, 78, 74}, model = "archer-1-red" }
        ,{ id = "CaiHunter102", class = "Archer", stat = {76, 80, 72, 78, 74}, model = "archer-1-red" }
        ,{ id = "CaiHunter103", class = "Archer", stat = {75, 79, 73, 77, 75}, model = "archer-1-red" }
        ,{ id = "CaiHunterArcher101", class = "Archer", stat = {76, 80, 76, 80, 76}, model = "archer-1-red" }
        ,{ id = "ChenGongZiTuo101", class = "Lord", stat = {84, 82, 74, 80, 76}, model = "lord-1-blue" }
        ,{ id = "ChenEscort101", class = "Cavalry", stat = {76, 80, 70, 76, 74}, model = "cavalry-1-blue" }
        ,{ id = "ChenArcher101", class = "Archer", stat = {74, 78, 72, 78, 74}, model = "archer-1-blue" }
        ,{ id = "XiongTong102", class = "Lord", stat = {92, 91, 86, 88, 86}, model = "lord-1-red" }
        ,{ id = "DouBoBi102", class = "Archer", stat = {78, 76, 94, 88, 84}, model = "archer-1-red" }
        ,{ id = "QuXia102", class = "Cavalry", stat = {86, 88, 88, 86, 82}, model = "cavalry-1-red" }
        ,{ id = "DouDan102", class = "Cavalry", stat = {88, 92, 78, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "ChuGuard102", class = "Infantry", stat = {78, 82, 72, 76, 76}, model = "infantry-1-red" }
        ,{ id = "ChuArcher102", class = "Archer", stat = {76, 80, 76, 78, 78}, model = "archer-1-red" }
        ,{ id = "SuiHou102", class = "Lord", stat = {82, 82, 84, 80, 80}, model = "lord-1-blue" }
        ,{ id = "JiLiang102", class = "Archer", stat = {74, 72, 96, 86, 84}, model = "archer-1-blue" }
        ,{ id = "ShaoShi102", class = "Cavalry", stat = {84, 88, 68, 82, 76}, model = "cavalry-1-blue" }
        ,{ id = "SuiGuard102", class = "Infantry", stat = {76, 80, 72, 74, 74}, model = "infantry-1-blue" }
        ,{ id = "SuiArcher102", class = "Archer", stat = {74, 78, 74, 76, 75}, model = "archer-1-blue" }
        ,{ id = "LuHuanGong11", class = "Lord", stat = {84, 82, 86, 82, 80}, model = "lord-1-red" }
        ,{ id = "ZhengLiGong11", class = "Lord", stat = {86, 84, 88, 86, 82}, model = "lord-1-red" }
        ,{ id = "GongZiNi11", class = "Cavalry", stat = {84, 88, 78, 82, 80}, model = "cavalry-1-red" }
        ,{ id = "YuanFan11", class = "Cavalry", stat = {83, 86, 82, 84, 81}, model = "cavalry-1-red" }
        ,{ id = "QinZi11", class = "Archer", stat = {80, 82, 84, 82, 82}, model = "archer-1-red" }
        ,{ id = "LiangZi11", class = "Archer", stat = {82, 86, 82, 84, 86}, model = "archer-1-red" }
        ,{ id = "TanBo11", class = "Infantry", stat = {82, 86, 80, 82, 81}, model = "infantry-1-red" }
        ,{ id = "AlliedGuard11", class = "Infantry", stat = {76, 80, 72, 76, 75}, model = "infantry-1-red" }
        ,{ id = "AlliedArcher11", class = "Archer", stat = {75, 79, 75, 77, 76}, model = "archer-1-red" }
        ,{ id = "SongZhuangGong11", class = "Lord", stat = {84, 84, 80, 82, 78}, model = "lord-1-blue" }
        ,{ id = "NangongChangWan11", class = "Cavalry", stat = {90, 94, 72, 82, 86}, model = "cavalry-1-blue" }
        ,{ id = "MengHuo11", class = "Infantry", stat = {84, 90, 70, 80, 78}, model = "infantry-1-blue" }
        ,{ id = "NangongNiu11", class = "Cavalry", stat = {82, 86, 76, 82, 79}, model = "cavalry-1-blue" }
        ,{ id = "HuaDu11", class = "Lord", stat = {82, 78, 88, 82, 76}, model = "lord-1-blue" }
        ,{ id = "SongGuard11", class = "Infantry", stat = {76, 80, 72, 75, 74}, model = "infantry-1-blue" }
        ,{ id = "SongArcher11", class = "Archer", stat = {74, 78, 74, 76, 75}, model = "archer-1-blue" }
        ,{ id = "JiHou11", class = "Lord", stat = {80, 78, 84, 80, 80}, model = "lord-1-red" }
        ,{ id = "YingJi11", class = "Cavalry", stat = {82, 86, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "JiGuard11", class = "Infantry", stat = {76, 80, 74, 76, 75}, model = "infantry-1-red" }
        ,{ id = "QiXiGong11", class = "Lord", stat = {86, 84, 88, 84, 82}, model = "lord-1-blue" }
        ,{ id = "GongZiPengSheng11", class = "Cavalry", stat = {88, 92, 76, 84, 84}, model = "cavalry-1-blue" }
        ,{ id = "YanBo11", class = "Lord", stat = {80, 80, 78, 80, 78}, model = "lord-1-blue" }
        ,{ id = "WeiHuiGong11", class = "Lord", stat = {82, 82, 78, 80, 79}, model = "lord-1-blue" }
        ,{ id = "QiGuard11", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "CoalitionArcher11", class = "Archer", stat = {76, 80, 76, 78, 76}, model = "archer-1-blue" }
        ,{ id = "JiZu11", class = "Strategist", stat = {78, 76, 94, 88, 84}, model = "Strategist-1-red" }
        ,{ id = "QiangChu11", class = "Infantry", stat = {82, 88, 78, 84, 82}, model = "infantry-1-red" }
        ,{ id = "GongZiE11", class = "Cavalry", stat = {84, 88, 82, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "JiClanGuard11", class = "Infantry", stat = {76, 80, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "JiClanArcher11", class = "Archer", stat = {75, 79, 77, 78, 77}, model = "archer-1-red" }
        ,{ id = "YongJiu11", class = "Cavalry", stat = {82, 86, 74, 82, 76}, model = "cavalry-1-blue" }
        ,{ id = "ZhengAmbusher11", class = "Infantry", stat = {76, 80, 72, 78, 74}, model = "infantry-1-blue" }
        ,{ id = "ZhengAmbushArcher11", class = "Archer", stat = {74, 78, 76, 78, 75}, model = "archer-1-blue" }
        ,{ id = "FuXia12", class = "Cavalry", stat = {82, 86, 80, 84, 81}, model = "cavalry-1-red" }
        ,{ id = "ZhengZhaoGong12", class = "Lord", stat = {84, 82, 86, 80, 82}, model = "lord-1-blue" }
        ,{ id = "GaoQuMi12", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-red" }
        ,{ id = "ZhengAmbusher12", class = "Infantry", stat = {78, 82, 74, 76, 76}, model = "infantry-1-red" }
        ,{ id = "ZhengAmbushArcher12", class = "Archer", stat = {76, 80, 76, 78, 78}, model = "archer-1-red" }
        ,{ id = "LuHuanGong13", class = "Lord", stat = {84, 82, 86, 82, 80}, model = "lord-1-red" }
        ,{ id = "WenJiang13", class = "Support", stat = {72, 62, 86, 92, 78}, model = "support-1-blue" }
        ,{ id = "GongZiPengSheng13", class = "Infantry", stat = {88, 94, 72, 76, 82}, model = "infantry-1-blue" }
        ,{ id = "QiXiangGong13", class = "Lord", stat = {88, 90, 82, 86, 78}, model = "lord-1-red" }
        ,{ id = "WangZiChengFu13", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "GuanZhiFu13", class = "Infantry", stat = {82, 86, 82, 84, 80}, model = "infantry-1-red" }
        ,{ id = "QiDeadman13", class = "Infantry", stat = {78, 84, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "QiArcher13", class = "Archer", stat = {76, 82, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "ZiWei13", class = "Lord", stat = {80, 76, 82, 78, 72}, model = "lord-1-blue" }
        ,{ id = "GaoQuMi13", class = "Cavalry", stat = {84, 87, 80, 82, 81}, model = "cavalry-1-blue" }
        ,{ id = "ZhengEscort13", class = "Infantry", stat = {76, 80, 74, 76, 75}, model = "infantry-1-blue" }
        ,{ id = "ZhengArcher13", class = "Archer", stat = {75, 79, 77, 78, 76}, model = "archer-1-blue" }
        ,{ id = "QiXiangGong14", class = "Lord", stat = {88, 90, 82, 86, 78}, model = "lord-1-red" }
        ,{ id = "WeiHuiGong14", class = "Lord", stat = {82, 82, 78, 80, 79}, model = "lord-1-red" }
        ,{ id = "LuZhuangGong14", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "SongMinGong14", class = "Lord", stat = {82, 82, 80, 80, 78}, model = "lord-1-red" }
        ,{ id = "ChenXuanGong14", class = "Lord", stat = {82, 80, 84, 82, 80}, model = "lord-1-red" }
        ,{ id = "CaiAiHou14", class = "Lord", stat = {82, 80, 82, 84, 80}, model = "lord-1-red" }
        ,{ id = "CoalitionGuard14", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "CoalitionArcher14", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "QianMou14", class = "Lord", stat = {82, 80, 84, 82, 80}, model = "lord-1-blue" }
        ,{ id = "GongZiXie14", class = "Infantry", stat = {82, 86, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "GongZiZhi14", class = "Cavalry", stat = {84, 88, 78, 82, 80}, model = "cavalry-1-blue" }
        ,{ id = "NingGui14", class = "Strategist", stat = {78, 76, 88, 86, 82}, model = "Strategist-1-blue" }
        ,{ id = "WeiGuard14", class = "Infantry", stat = {76, 80, 74, 76, 75}, model = "infantry-1-blue" }
        ,{ id = "WeiArcher14", class = "Archer", stat = {75, 79, 77, 78, 76}, model = "archer-1-blue" }
        ,{ id = "ZiTu14", class = "Cavalry", stat = {88, 92, 86, 90, 90}, model = "cavalry-1-blue" }
        ,{ id = "RoyalChariot14", class = "Cavalry", stat = {80, 84, 76, 80, 78}, model = "cavalry-1-blue" }
        ,{ id = "LianCheng14", class = "Infantry", stat = {86, 92, 78, 82, 84}, model = "infantry-1-red" }
        ,{ id = "GuanZhiFu14", class = "Infantry", stat = {82, 86, 82, 84, 80}, model = "infantry-1-red" }
        ,{ id = "KuikouGuard14", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "RebelArcher14", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "QiXiangGong142", class = "Lord", stat = {88, 90, 82, 86, 78}, model = "lord-1-blue" }
        ,{ id = "ShiZhiFenRu14", class = "Cavalry", stat = {86, 90, 78, 84, 84}, model = "cavalry-1-blue" }
        ,{ id = "TuRenFei14", class = "Infantry", stat = {82, 88, 76, 84, 86}, model = "infantry-1-blue" }
        ,{ id = "MengYang14", class = "Infantry", stat = {84, 88, 78, 86, 88}, model = "infantry-1-blue" }
        ,{ id = "QiPalaceGuard14", class = "Infantry", stat = {76, 80, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "QiPalaceArcher14", class = "Archer", stat = {75, 79, 77, 80, 77}, model = "archer-1-blue" }
        ,{ id = "QiHuanGong15", class = "Lord", stat = {92, 88, 90, 92, 88}, model = "lord-1-red" }
        ,{ id = "BaoShuYa15", class = "Strategist", stat = {84, 80, 96, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "YongLin15", class = "Infantry", stat = {82, 86, 88, 86, 84}, model = "infantry-1-red" }
        ,{ id = "WangZiChengFu15", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "DongGuoYa15", class = "Cavalry", stat = {84, 88, 88, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "NingYue15", class = "Cavalry", stat = {82, 86, 86, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "ZhongSunJiu15", class = "Strategist", stat = {80, 78, 90, 88, 84}, model = "Strategist-1-red" }
        ,{ id = "QiAmbusher15", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "QiAmbushArcher15", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "LuZhuangGong15", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-blue" }
        ,{ id = "CaoMo15", class = "Cavalry", stat = {88, 94, 82, 88, 90}, model = "cavalry-1-blue" }
        ,{ id = "QinZi15", class = "Archer", stat = {80, 82, 84, 82, 82}, model = "archer-1-blue" }
        ,{ id = "LiangZi15", class = "Archer", stat = {82, 86, 82, 84, 86}, model = "archer-1-blue" }
        ,{ id = "GongZiJiu15", class = "Lord", stat = {84, 82, 86, 84, 82}, model = "lord-1-blue" }
        ,{ id = "GuanYiWu15", class = "Strategist", stat = {82, 78, 98, 96, 88}, model = "Strategist-1-blue" }
        ,{ id = "ZhaoHuQi15", class = "Infantry", stat = {84, 88, 84, 86, 86}, model = "infantry-1-blue" }
        ,{ id = "LuGuard15", class = "Infantry", stat = {76, 80, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "LuArcher15", class = "Archer", stat = {75, 79, 77, 80, 77}, model = "archer-1-blue" }
        ,{ id = "WangZiChengFu152", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "DongGuoYa152", class = "Cavalry", stat = {84, 88, 88, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "QiPursuer15", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-red" }
        ,{ id = "QiPursuitArcher15", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "LuZhuangGong152", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-blue" }
        ,{ id = "CaoMo152", class = "Cavalry", stat = {88, 94, 82, 88, 90}, model = "cavalry-1-blue" }
        ,{ id = "QinZi152", class = "Archer", stat = {80, 82, 84, 82, 82}, model = "archer-1-blue" }
        ,{ id = "GuanYiWu152", class = "Strategist", stat = {82, 78, 98, 96, 88}, model = "Strategist-1-blue" }
        ,{ id = "GongZiJiu152", class = "Lord", stat = {84, 82, 86, 84, 82}, model = "lord-1-blue" }
        ,{ id = "ZhaoHuQi152", class = "Infantry", stat = {84, 88, 84, 86, 86}, model = "infantry-1-blue" }
        ,{ id = "LuRearGuard15", class = "Infantry", stat = {76, 80, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "LuRearArcher15", class = "Archer", stat = {75, 79, 77, 80, 77}, model = "archer-1-blue" }
        ,{ id = "LuZhuangGong16", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "CaoGui16", class = "Strategist", stat = {82, 76, 98, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "LuGuard16", class = "Infantry", stat = {77, 81, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "LuArcher16", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "BaoShuYa16", class = "Strategist", stat = {84, 80, 96, 94, 90}, model = "Strategist-1-blue" }
        ,{ id = "QiVanguard16", class = "Cavalry", stat = {80, 84, 76, 78, 78}, model = "cavalry-1-blue" }
        ,{ id = "QiGuard16", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "QiArcher16", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "SongHuanGong17", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "XiaoShuDaXin17", class = "Strategist", stat = {84, 82, 92, 90, 88}, model = "Strategist-1-red" }
        ,{ id = "SongClanGuard17", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "SongArcher17", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "CaoGuard17", class = "Cavalry", stat = {80, 84, 76, 80, 78}, model = "cavalry-1-red" }
        ,{ id = "NanGongNiu17", class = "Cavalry", stat = {86, 92, 76, 84, 84}, model = "cavalry-1-blue" }
        ,{ id = "MengHuo17", class = "Infantry", stat = {84, 90, 72, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "ZiYou17", class = "Lord", stat = {80, 78, 82, 80, 76}, model = "lord-1-blue" }
        ,{ id = "RebelGuard17", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "RebelArcher17", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "QiHuanGong18", class = "Lord", stat = {92, 88, 90, 92, 88}, model = "lord-1-red" }
        ,{ id = "GuanYiWu18", class = "Strategist", stat = {82, 78, 98, 96, 88}, model = "Strategist-1-red" }
        ,{ id = "BaoShuYa18", class = "Strategist", stat = {84, 80, 96, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "WangZiChengFu18", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "QiGuard18", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "QiArcher18", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "SongHuanGong18", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "SongGuard18", class = "Infantry", stat = {77, 81, 75, 78, 77}, model = "infantry-1-red" }
        ,{ id = "SongArcher18", class = "Archer", stat = {76, 80, 77, 79, 77}, model = "archer-1-red" }
        ,{ id = "SuiLord18", class = "Lord", stat = {82, 80, 84, 82, 80}, model = "lord-1-blue" }
        ,{ id = "SuiGuard18", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-blue" }
,{ id = "SuiArcher18", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "ZhengLiGong19", class = "Lord", stat = {88, 86, 90, 88, 84}, model = "lord-1-red" }
        ,{ id = "BinXuWu19", class = "Cavalry", stat = {84, 88, 82, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "QiGuard19", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "QiArcher19", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "FuXia19", class = "Cavalry", stat = {82, 86, 78, 82, 78}, model = "cavalry-1-blue" }
        ,{ id = "ZhengGuard19", class = "Infantry", stat = {77, 81, 75, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "ZhengArcher19", class = "Archer", stat = {75, 79, 77, 79, 77}, model = "archer-1-blue" }
        ,{ id = "XiGuoGong19", class = "Lord", stat = {86, 84, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "ShiShu19", class = "Strategist", stat = {80, 76, 92, 90, 86}, model = "Strategist-1-red" }
        ,{ id = "ZhengGuard192", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "GuoGuard19", class = "Infantry", stat = {78, 82, 75, 78, 77}, model = "infantry-1-red" }
        ,{ id = "GuoArcher19", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "ZhouHuiWang19", class = "King", stat = {82, 78, 86, 84, 80}, model = "lord-1-red" }
        ,{ id = "WangZiTui19", class = "Lord", stat = {80, 78, 76, 74, 72}, model = "lord-1-blue" }
        ,{ id = "WeiGuo19", class = "Strategist", stat = {82, 76, 88, 86, 80}, model = "Strategist-1-blue" }
        ,{ id = "BianBo19", class = "Cavalry", stat = {82, 86, 78, 82, 78}, model = "cavalry-1-blue" }
        ,{ id = "ShiSu19", class = "Infantry", stat = {80, 84, 78, 80, 78}, model = "infantry-1-blue" }
        ,{ id = "ZhanFu19", class = "Archer", stat = {78, 82, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "ZiQin19", class = "Infantry", stat = {79, 83, 80, 81, 79}, model = "infantry-1-blue" }
        ,{ id = "RoyalRebelGuard19", class = "Infantry", stat = {77, 81, 75, 78, 76}, model = "infantry-1-blue" }
,{ id = "RoyalRebelArcher19", class = "Archer", stat = {75, 79, 77, 79, 77}, model = "archer-1-blue" }
        ,{ id = "WeiYiGong20", class = "Lord", stat = {82, 80, 82, 80, 78}, model = "lord-1-blue" }
        ,{ id = "WeiKaiFang20", class = "Cavalry", stat = {80, 84, 78, 82, 80}, model = "cavalry-1-blue" }
        ,{ id = "WeiGuard20", class = "Infantry", stat = {77, 81, 75, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "WeiArcher20", class = "Archer", stat = {75, 79, 77, 79, 77}, model = "archer-1-blue" }
        ,{ id = "JinXianGong20", class = "Lord", stat = {90, 88, 86, 88, 82}, model = "lord-1-red" }
        ,{ id = "ShenSheng20", class = "Lord", stat = {86, 88, 90, 86, 84}, model = "lord-1-red" }
        ,{ id = "JinGuard20", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "JinArcher20", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "LiRongLord20", class = "Lord", stat = {84, 86, 78, 80, 82}, model = "lord-1-blue" }
        ,{ id = "LiRongGuard20", class = "Infantry", stat = {78, 82, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "LiRongArcher20", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "ZhaoSu20", class = "Cavalry", stat = {84, 88, 82, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "BiWan20", class = "Cavalry", stat = {84, 86, 84, 82, 84}, model = "cavalry-1-red" }
        ,{ id = "JinGuard202", class = "Infantry", stat = {79, 83, 76, 79, 78}, model = "infantry-1-red" }
        ,{ id = "JinArcher202", class = "Archer", stat = {77, 81, 78, 80, 79}, model = "archer-1-red" }
        ,{ id = "DiChief20", class = "Lord", stat = {82, 86, 74, 78, 80}, model = "lord-1-blue" }
        ,{ id = "DiGuard20", class = "Infantry", stat = {77, 82, 73, 76, 75}, model = "infantry-1-blue" }
        ,{ id = "DiArcher20", class = "Archer", stat = {76, 80, 76, 78, 77}, model = "archer-1-blue" }
        ,{ id = "HuoLord20", class = "Lord", stat = {82, 80, 82, 80, 78}, model = "lord-1-blue" }
        ,{ id = "HuoGuard20", class = "Infantry", stat = {77, 81, 75, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "HuoArcher20", class = "Archer", stat = {75, 79, 77, 79, 77}, model = "archer-1-blue" }
        ,{ id = "WeiLord20", class = "Lord", stat = {82, 82, 80, 82, 80}, model = "lord-1-blue" }
        ,{ id = "WeiGuard202", class = "Infantry", stat = {78, 82, 75, 78, 77}, model = "infantry-1-blue" }
        ,{ id = "WeiArcher202", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "DouGuWuTu20", class = "Strategist", stat = {86, 82, 96, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "DouBan20", class = "Cavalry", stat = {84, 90, 80, 84, 84}, model = "cavalry-1-red" }
        ,{ id = "DouLian20", class = "Strategist", stat = {82, 80, 90, 88, 86}, model = "Strategist-1-red" }
        ,{ id = "DouYuJiang20", class = "Cavalry", stat = {82, 86, 80, 82, 82}, model = "cavalry-1-red" }
        ,{ id = "ZiYuan20", class = "Lord", stat = {86, 88, 82, 84, 78}, model = "lord-1-blue" }
        ,{ id = "ZiYuanGuard20", class = "Infantry", stat = {78, 83, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "ZiYuanArcher20", class = "Archer", stat = {76, 81, 77, 80, 78}, model = "archer-1-blue" }
        ,{ id = "HuErBan21", class = "Cavalry", stat = {86, 92, 78, 84, 86}, model = "cavalry-1-red" }
        ,{ id = "BinXuWu21", class = "Cavalry", stat = {84, 88, 82, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "XiPeng21", class = "Strategist", stat = {80, 76, 96, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "GaoHei21", class = "Infantry", stat = {84, 88, 78, 82, 82}, model = "infantry-1-red" }
        ,{ id = "YanZhuangGong21", class = "Lord", stat = {82, 80, 88, 84, 82}, model = "lord-1-red" }
        ,{ id = "QiGuard21", class = "Infantry", stat = {78, 82, 76, 78, 78}, model = "infantry-1-red" }
        ,{ id = "QiArcher21", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "WuZhongWarrior21", class = "Infantry", stat = {80, 86, 74, 80, 80}, model = "infantry-1-red" }
        ,{ id = "MiLu21", class = "Lord", stat = {86, 90, 78, 82, 84}, model = "lord-1-blue" }
        ,{ id = "SuMai21", class = "Cavalry", stat = {84, 90, 76, 82, 82}, model = "cavalry-1-blue" }
        ,{ id = "ShanRongCavalry21", class = "Cavalry", stat = {78, 84, 72, 78, 78}, model = "cavalry-1-blue" }
        ,{ id = "ShanRongArcher21", class = "Archer", stat = {76, 80, 74, 78, 76}, model = "archer-1-blue" }
        ,{ id = "HuangHua21", class = "Cavalry", stat = {90, 94, 80, 86, 86}, model = "cavalry-1-blue" }
        ,{ id = "DaLiHe21", class = "Lord", stat = {86, 88, 84, 84, 82}, model = "lord-1-blue" }
        ,{ id = "WuLvGu21", class = "Strategist", stat = {78, 74, 94, 90, 86}, model = "Strategist-1-blue" }
        ,{ id = "GuzhuGuard21", class = "Infantry", stat = {78, 82, 76, 78, 77}, model = "infantry-1-blue" }
        ,{ id = "GuzhuArcher21", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "JiYou22", class = "Lord", stat = {90, 86, 96, 94, 92}, model = "lord-1-red" }
        ,{ id = "LuGuard22", class = "Infantry", stat = {78, 82, 76, 80, 78}, model = "infantry-1-red" }
        ,{ id = "LuArcher22", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "YingNa22", class = "Cavalry", stat = {86, 94, 76, 82, 82}, model = "cavalry-1-blue" }
        ,{ id = "JuGuard22", class = "Infantry", stat = {78, 84, 74, 78, 76}, model = "infantry-1-blue" }
        ,{ id = "JuArcher22", class = "Archer", stat = {76, 81, 76, 79, 77}, model = "archer-1-blue" }
        ,{ id = "WeiYiGong23", class = "Lord", stat = {82, 80, 82, 80, 78}, model = "lord-1-red" }
        ,{ id = "QuKong23", class = "Strategist", stat = {84, 88, 82, 84, 82}, model = "Strategist-1-red" }
        ,{ id = "YuBo23", class = "Cavalry", stat = {82, 87, 78, 82, 80}, model = "cavalry-1-red" }
        ,{ id = "HuangYi23", class = "Infantry", stat = {84, 90, 76, 82, 82}, model = "infantry-1-red" }
        ,{ id = "KongYingQi23", class = "Archer", stat = {80, 84, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "WeiGuard23", class = "Infantry", stat = {78, 82, 75, 78, 77}, model = "infantry-1-red" }
        ,{ id = "WeiArcher23", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-red" }
        ,{ id = "SouMan23", class = "Lord", stat = {88, 92, 82, 84, 86}, model = "lord-1-blue" }
        ,{ id = "DiCavalry23", class = "Cavalry", stat = {80, 86, 74, 80, 80}, model = "cavalry-1-blue" }
        ,{ id = "DiAmbusher23", class = "Infantry", stat = {79, 85, 74, 80, 79}, model = "infantry-1-blue" }
        ,{ id = "DiArcher23", class = "Archer", stat = {77, 82, 76, 80, 78}, model = "archer-1-blue" }
        ,{ id = "DouZhang23", class = "Cavalry", stat = {86, 90, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "DouLian23", class = "Strategist", stat = {84, 86, 92, 90, 86}, model = "Strategist-1-red" }
        ,{ id = "ChuGuard23", class = "Infantry", stat = {79, 84, 76, 80, 79}, model = "infantry-1-red" }
        ,{ id = "ChuArcher23", class = "Archer", stat = {77, 81, 79, 81, 79}, model = "archer-1-red" }
        ,{ id = "DanBo23", class = "Strategist", stat = {84, 82, 90, 88, 84}, model = "Strategist-1-blue" }
        ,{ id = "ZhengGuard23", class = "Infantry", stat = {78, 83, 76, 79, 78}, model = "infantry-1-blue" }
        ,{ id = "ZhengArcher23", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "QiHuanGong24", class = "Lord", stat = {92, 88, 90, 92, 88}, model = "lord-1-red" }
        ,{ id = "GuanYiWu24", class = "Strategist", stat = {82, 78, 98, 96, 88}, model = "Strategist-1-red" }
        ,{ id = "BaoShuYa24", class = "Strategist", stat = {84, 80, 96, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "WangZiChengFu24", class = "Cavalry", stat = {86, 92, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "CoalitionGuard24", class = "Infantry", stat = {79, 84, 77, 80, 80}, model = "infantry-1-red" }
        ,{ id = "CoalitionArcher24", class = "Archer", stat = {78, 82, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "ZhengWenGong24", class = "Lord", stat = {84, 80, 88, 84, 80}, model = "lord-1-blue" }
        ,{ id = "KongShu24", class = "Strategist", stat = {82, 78, 94, 92, 88}, model = "Strategist-1-blue" }
        ,{ id = "ShenHou24", class = "Support", stat = {78, 74, 90, 88, 80}, model = "support-1-blue" }
        ,{ id = "XinmiGateCaptain24", class = "Infantry", stat = {82, 86, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "ZhengGateGuard24", class = "Infantry", stat = {79, 84, 76, 80, 78}, model = "infantry-1-blue" }
        ,{ id = "ZhengArcher24", class = "Archer", stat = {77, 81, 79, 81, 79}, model = "archer-1-blue" }
        ,{ id = "XuXiGong24", class = "Lord", stat = {84, 82, 88, 84, 84}, model = "lord-1-red" }
        ,{ id = "XuGuard24", class = "Infantry", stat = {79, 83, 78, 80, 80}, model = "infantry-1-red" }
        ,{ id = "XuArcher24", class = "Archer", stat = {77, 81, 80, 81, 80}, model = "archer-1-red" }
        ,{ id = "ChuChengWang24", class = "King", stat = {92, 90, 92, 90, 88}, model = "lord-1-blue" }
        ,{ id = "ZiWen24", class = "Strategist", stat = {86, 82, 98, 96, 92}, model = "Strategist-1-blue" }
        ,{ id = "DouLian24", class = "Strategist", stat = {84, 86, 92, 90, 86}, model = "Strategist-1-blue" }
        ,{ id = "ChuGuard24", class = "Infantry", stat = {80, 85, 77, 81, 80}, model = "infantry-1-blue" }
        ,{ id = "ChuArcher24", class = "Archer", stat = {78, 82, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "LiKe25", class = "Cavalry", stat = {88, 92, 86, 88, 84}, model = "cavalry-1-red" }
        ,{ id = "XunXi25", class = "Strategist", stat = {84, 80, 98, 94, 88}, model = "Strategist-1-red" }
        ,{ id = "JinGuard25", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "JinArcher25", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "YuAuxiliary25", class = "Infantry", stat = {77, 81, 76, 79, 78}, model = "infantry-1-red" }
        ,{ id = "ZhouZhiQiao25", class = "Strategist", stat = {84, 82, 92, 90, 86}, model = "Strategist-1-blue" }
        ,{ id = "XiayangCaptain25", class = "Infantry", stat = {82, 87, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "GuoGuard25", class = "Infantry", stat = {79, 84, 76, 80, 78}, model = "infantry-1-blue" }
        ,{ id = "GuoArcher25", class = "Archer", stat = {77, 82, 79, 81, 79}, model = "archer-1-blue" }
        ,{ id = "YuGong25", class = "Lord", stat = {78, 76, 72, 76, 74}, model = "lord-1-blue" }
        ,{ id = "BailiXi25", class = "Strategist", stat = {82, 74, 98, 96, 92}, model = "Strategist-1-blue" }
        ,{ id = "YuCapitalCaptain25", class = "Infantry", stat = {81, 85, 78, 81, 79}, model = "infantry-1-blue" }
        ,{ id = "YuGuard25", class = "Infantry", stat = {78, 82, 76, 79, 78}, model = "infantry-1-blue" }
        ,{ id = "YuArcher25", class = "Archer", stat = {76, 80, 78, 80, 78}, model = "archer-1-blue" }
        ,{ id = "MengMingShi26", class = "Cavalry", stat = {88, 94, 84, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "XiQiShu26", class = "Infantry", stat = {86, 90, 82, 88, 84}, model = "infantry-1-red" }
        ,{ id = "BaiYiBing26", class = "Archer", stat = {84, 88, 84, 86, 84}, model = "archer-1-red" }
        ,{ id = "YouYu26", class = "Strategist", stat = {80, 76, 98, 96, 90}, model = "Strategist-1-red" }
        ,{ id = "QinGuard26", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QinArcher26", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "WuLi26", class = "Lord", stat = {86, 91, 78, 84, 84}, model = "lord-1-blue" }
        ,{ id = "JiangRongGuard26", class = "Infantry", stat = {79, 84, 75, 79, 78}, model = "infantry-1-blue" }
        ,{ id = "JiangRongCavalry26", class = "Cavalry", stat = {80, 86, 74, 80, 79}, model = "cavalry-1-blue" }
        ,{ id = "JiangRongArcher26", class = "Archer", stat = {77, 82, 77, 80, 78}, model = "archer-1-blue" }
        ,{ id = "ChiBan26", class = "Lord", stat = {90, 93, 84, 88, 86}, model = "lord-1-blue" }
        ,{ id = "XiRongGuard26", class = "Infantry", stat = {80, 85, 77, 80, 80}, model = "infantry-1-blue" }
        ,{ id = "XiRongCavalry26", class = "Cavalry", stat = {81, 87, 76, 81, 80}, model = "cavalry-1-blue" }
        ,{ id = "XiRongArcher26", class = "Archer", stat = {78, 83, 79, 81, 79}, model = "archer-1-blue" }
        ,{ id = "ChongEr27", class = "Lord", stat = {92, 88, 94, 92, 90}, model = "lord-1-red" }
        ,{ id = "HuMao27", class = "Strategist", stat = {82, 78, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "HuYan27", class = "Strategist", stat = {84, 80, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "ZhaoShuai27", class = "Strategist", stat = {86, 84, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "XuChen27", class = "Support", stat = {82, 78, 92, 90, 88}, model = "support-1-red" }
        ,{ id = "WeiChou27", class = "Cavalry", stat = {90, 96, 78, 88, 88}, model = "cavalry-1-red" }
        ,{ id = "HuSheGu27", class = "Archer", stat = {84, 90, 84, 88, 86}, model = "archer-1-red" }
        ,{ id = "DianJie27", class = "Infantry", stat = {84, 90, 76, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JieZiTui27", class = "Infantry", stat = {82, 86, 88, 86, 90}, model = "infantry-1-red" }
        ,{ id = "XianZhen27", class = "Cavalry", stat = {88, 92, 94, 92, 88}, model = "cavalry-1-red" }
        ,{ id = "PuGuard27", class = "Infantry", stat = {79, 84, 76, 80, 79}, model = "infantry-1-red" }
        ,{ id = "BoDi27", class = "Cavalry", stat = {88, 94, 80, 88, 86}, model = "cavalry-1-blue" }
        ,{ id = "JinGuard27", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "JinCavalry27", class = "Cavalry", stat = {81, 87, 76, 82, 81}, model = "cavalry-1-blue" }
        ,{ id = "JinArcher27", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "DiGuard27", class = "Infantry", stat = {79, 84, 76, 80, 79}, model = "infantry-1-red" }
        ,{ id = "DiArcher27", class = "Archer", stat = {77, 82, 79, 81, 79}, model = "archer-1-red" }
        ,{ id = "LiKe28", class = "Cavalry", stat = {88, 92, 86, 88, 84}, model = "cavalry-1-red" }
        ,{ id = "PiZhengFu28", class = "Strategist", stat = {84, 82, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "TuAnYi28", class = "Infantry", stat = {88, 98, 72, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ZhuiTuan28", class = "Cavalry", stat = {84, 88, 86, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "GongHua28", class = "Infantry", stat = {82, 86, 82, 84, 82}, model = "infantry-1-red" }
        ,{ id = "CoupGuard28", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "CoupArcher28", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "DongGuanWu28", class = "Cavalry", stat = {84, 88, 78, 84, 80}, model = "cavalry-1-blue" }
        ,{ id = "LiangWu28", class = "Infantry", stat = {84, 90, 76, 84, 80}, model = "infantry-1-blue" }
        ,{ id = "XunXi28", class = "Strategist", stat = {84, 80, 98, 94, 88}, model = "Strategist-1-blue" }
        ,{ id = "PalaceGuard28", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "PalaceArcher28", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "DongshiGuard28", class = "Infantry", stat = {79, 84, 77, 81, 79}, model = "infantry-1-blue" }
        ,{ id = "DongshiArcher28", class = "Archer", stat = {77, 82, 79, 81, 79}, model = "archer-1-blue" }
        ,{ id = "QinMuGong29", class = "Lord", stat = {94, 90, 92, 94, 90}, model = "lord-1-red" }
        ,{ id = "BailiXi29", class = "Strategist", stat = {82, 74, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "JinHuiGong29", class = "Lord", stat = {82, 78, 84, 82, 78}, model = "lord-1-red" }
        ,{ id = "XiRui29", class = "Strategist", stat = {84, 82, 92, 90, 86}, model = "Strategist-1-red" }
        ,{ id = "GuanYiWu29", class = "Strategist", stat = {82, 78, 98, 96, 88}, model = "Strategist-1-red" }
        ,{ id = "QinGuard29", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QinArcher29", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "JinGuard29", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "JinArcher29", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "QiGuard29", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QiArcher29", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "ZhouXiangWang29", class = "King", stat = {88, 82, 90, 88, 86}, model = "lord-1-blue" }
        ,{ id = "ZhouGongKong29", class = "Strategist", stat = {84, 80, 94, 92, 88}, model = "Strategist-1-blue" }
        ,{ id = "ShaoBoLiao29", class = "Strategist", stat = {82, 80, 92, 90, 86}, model = "Strategist-1-blue" }
        ,{ id = "RoyalGuard29", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "RoyalArcher29", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "YiLuoRongLord29", class = "Lord", stat = {88, 92, 80, 84, 84}, model = "lord-1-blue" }
        ,{ id = "YiLuoRongGuard29", class = "Infantry", stat = {80, 86, 74, 80, 78}, model = "infantry-1-blue" }
        ,{ id = "YiLuoRongCavalry29", class = "Cavalry", stat = {82, 88, 74, 82, 80}, model = "cavalry-1-blue" }
        ,{ id = "YiLuoRongArcher29", class = "Archer", stat = {78, 84, 78, 81, 79}, model = "archer-1-blue" }
        ,{ id = "QiHuanGong30", class = "Lord", stat = {94, 88, 96, 94, 92}, model = "lord-1-red" }
        ,{ id = "BaoShuYa30", class = "Strategist", stat = {88, 82, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "WangZiChengFu30", class = "Cavalry", stat = {88, 94, 84, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "QiHou30", class = "Lord", stat = {80, 76, 84, 82, 80}, model = "lord-1-red" }
        ,{ id = "QiGuard30", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QiArcher30", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "HuaiYiLord30", class = "Lord", stat = {86, 90, 78, 82, 82}, model = "lord-1-blue" }
        ,{ id = "HuaiYiGuard30", class = "Infantry", stat = {79, 84, 76, 80, 79}, model = "infantry-1-blue" }
        ,{ id = "HuaiYiArcher30", class = "Archer", stat = {77, 82, 79, 81, 79}, model = "archer-1-blue" }
        ,{ id = "HuaiYiCavalry30", class = "Cavalry", stat = {81, 87, 76, 81, 80}, model = "cavalry-1-blue" }
        ,{ id = "QinMuGong30", class = "Lord", stat = {94, 90, 92, 94, 90}, model = "lord-1-red" }
        ,{ id = "BailiXi30", class = "Strategist", stat = {82, 74, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "XiQiShu30", class = "Infantry", stat = {86, 90, 82, 88, 84}, model = "infantry-1-red" }
        ,{ id = "BaiYiBing30", class = "Archer", stat = {84, 88, 84, 86, 84}, model = "archer-1-red" }
        ,{ id = "GongSunZhi30", class = "Cavalry", stat = {90, 96, 88, 92, 88}, model = "cavalry-1-red" }
        ,{ id = "GongZiZhi30", class = "Strategist", stat = {86, 82, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "QinGuard30", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QinArcher30", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "WildWarrior30", class = "Infantry", stat = {82, 90, 74, 82, 84}, model = "infantry-1-red" }
        ,{ id = "WildArcher30", class = "Archer", stat = {80, 86, 76, 82, 82}, model = "archer-1-red" }
        ,{ id = "JinHuiGong30", class = "Lord", stat = {82, 78, 84, 82, 78}, model = "lord-1-blue" }
        ,{ id = "TuAnYi30", class = "Infantry", stat = {88, 98, 72, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "GuoShe30", class = "Strategist", stat = {82, 80, 90, 86, 82}, model = "Strategist-1-blue" }
        ,{ id = "HanJian30", class = "Cavalry", stat = {86, 90, 88, 88, 84}, model = "cavalry-1-blue" }
        ,{ id = "LiangYaoMi30", class = "Cavalry", stat = {84, 90, 80, 86, 82}, model = "cavalry-1-blue" }
        ,{ id = "JiaPuTu30", class = "Infantry", stat = {84, 88, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "XiBuYang30", class = "Cavalry", stat = {84, 88, 82, 86, 82}, model = "cavalry-1-blue" }
        ,{ id = "JinGuard30", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "JinCavalry30", class = "Cavalry", stat = {81, 87, 76, 82, 81}, model = "cavalry-1-blue" }
        ,{ id = "JinArcher30", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "Assassin31", class = "Infantry", stat = {82, 88, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "AssassinArcher31", class = "Archer", stat = {80, 86, 80, 84, 82}, model = "archer-1-blue" }
        ,{ id = "GongZiZhao32", class = "Lord", stat = {88, 84, 92, 90, 88}, model = "lord-1-red" }
        ,{ id = "CuiYao32", class = "Cavalry", stat = {84, 90, 80, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "PrinceGuard32", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "PrinceArcher32", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "YiYa32", class = "Strategist", stat = {82, 76, 92, 90, 84}, model = "Strategist-1-blue" }
        ,{ id = "ShuDiao32", class = "Support", stat = {80, 74, 90, 88, 82}, model = "support-1-blue" }
        ,{ id = "PalaceGuard32", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "PalaceArcher32", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "SongXiangGong33", class = "Lord", stat = {88, 86, 88, 86, 84}, model = "lord-1-red" }
        ,{ id = "GongZiDang33", class = "Infantry", stat = {86, 92, 80, 86, 84}, model = "infantry-1-red" }
        ,{ id = "GongSunGu33", class = "Cavalry", stat = {88, 94, 82, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "HuaYuShi33", class = "Archer", stat = {84, 90, 84, 86, 84}, model = "archer-1-red" }
        ,{ id = "GaoHu33", class = "Strategist", stat = {84, 78, 96, 94, 90}, model = "Strategist-1-red" }
        ,{ id = "SongGuard33", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "SongArcher33", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-red" }
        ,{ id = "GongZiYuan33", class = "Lord", stat = {86, 84, 86, 84, 82}, model = "lord-1-blue" }
        ,{ id = "GongZiPan33", class = "Cavalry", stat = {84, 90, 80, 86, 82}, model = "cavalry-1-blue" }
        ,{ id = "GongZiShangRen33", class = "Infantry", stat = {86, 88, 88, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "QiClanGuard33", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "QiClanArcher33", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "GongZiMuYi33", class = "Strategist", stat = {84, 78, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "ChuChengWang33", class = "King", stat = {94, 92, 94, 92, 90}, model = "lord-1-blue" }
        ,{ id = "ChengDeChen33", class = "Cavalry", stat = {90, 96, 84, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "DouBo33", class = "Infantry", stat = {88, 94, 80, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "ChuAmbusher33", class = "Infantry", stat = {81, 87, 78, 83, 81}, model = "infantry-1-blue" }
        ,{ id = "ChuArcher33", class = "Archer", stat = {79, 84, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "SongPrinceChen34", class = "Lord", stat = {84, 82, 88, 86, 86}, model = "lord-1-red" }
        ,{ id = "LePuYi34", class = "Infantry", stat = {86, 92, 82, 88, 84}, model = "infantry-1-red" }
        ,{ id = "HuaXiuLao34", class = "Archer", stat = {84, 90, 84, 86, 84}, model = "archer-1-red" }
        ,{ id = "XiangZiShou34", class = "Cavalry", stat = {86, 92, 82, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "LuChen34", class = "Cavalry", stat = {88, 94, 82, 88, 86}, model = "cavalry-1-blue" }
        ,{ id = "ChuGuard34", class = "Infantry", stat = {82, 88, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "ChuArcher34", class = "Archer", stat = {80, 86, 80, 84, 82}, model = "archer-1-blue" }
        ,{ id = "HumanBear35", class = "Infantry", stat = {88, 96, 58, 82, 78}, model = "infantry-1-blue" }
        ,{ id = "MoBeast35", class = "Infantry", stat = {94, 98, 62, 76, 84}, model = "infantry-1-blue" }
        ,{ id = "ChuHunter35", class = "Archer", stat = {80, 84, 80, 82, 82}, model = "archer-1-blue" }
        ,{ id = "PiBao36", class = "Cavalry", stat = {88, 95, 80, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "DengHun36", class = "Infantry", stat = {82, 88, 76, 84, 80}, model = "infantry-1-blue" }
        ,{ id = "LuanZhi36", class = "Strategist", stat = {84, 82, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "LvSheng36", class = "Strategist", stat = {84, 82, 92, 90, 84}, model = "Strategist-1-blue" }
        ,{ id = "XiRui36", class = "Strategist", stat = {86, 84, 94, 90, 84}, model = "Strategist-1-blue" }
        ,{ id = "QinGuard36", class = "Infantry", stat = {81, 86, 78, 82, 80}, model = "infantry-1-red" }
        ,{ id = "QinArcher36", class = "Archer", stat = {79, 84, 81, 82, 80}, model = "archer-1-red" }
        ,{ id = "LinghuGuard36", class = "Infantry", stat = {81, 87, 76, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "LinghuArcher36", class = "Archer", stat = {79, 84, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "RebelGuard36", class = "Infantry", stat = {82, 88, 76, 83, 80}, model = "infantry-1-blue" }
        ,{ id = "RebelArcher36", class = "Archer", stat = {80, 85, 80, 83, 80}, model = "archer-1-blue" }
        ,{ id = "JinClanGuard36", class = "Infantry", stat = {81, 86, 78, 82, 82}, model = "infantry-1-red" }
        ,{ id = "JinClanArcher36", class = "Archer", stat = {79, 84, 82, 82, 82}, model = "archer-1-red" }
        ,{ id = "FuChen38", class = "Strategist", stat = {88, 82, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "JianShiFu38", class = "Strategist", stat = {84, 80, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "ZuoYanFu38", class = "Strategist", stat = {82, 80, 92, 90, 88}, model = "Strategist-1-red" }
        ,{ id = "ChiDing38", class = "Lord", stat = {90, 94, 82, 88, 86}, model = "lord-1-blue" }
        ,{ id = "ChiFengZi38", class = "Cavalry", stat = {86, 92, 78, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "DiGuard38", class = "Infantry", stat = {82, 88, 76, 83, 80}, model = "infantry-1-blue" }
        ,{ id = "DiCavalry38", class = "Cavalry", stat = {84, 90, 76, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "DiArcher38", class = "Archer", stat = {80, 85, 80, 83, 80}, model = "archer-1-blue" }
        ,{ id = "XiZhen38", class = "Strategist", stat = {86, 84, 94, 92, 88}, model = "Strategist-1-red" }
        ,{ id = "TaiShuDai38", class = "Lord", stat = {90, 94, 86, 88, 84}, model = "lord-1-blue" }
        ,{ id = "WeiHou38", class = "Archer", stat = {82, 86, 88, 86, 82}, model = "archer-1-blue" }
        ,{ id = "WenRebelGuard38", class = "Infantry", stat = {82, 88, 76, 83, 80}, model = "infantry-1-blue" }
        ,{ id = "WenRebelArcher38", class = "Archer", stat = {80, 85, 80, 83, 80}, model = "archer-1-blue" }
        ,{ id = "JinGuard38", class = "Infantry", stat = {82, 87, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinArcher38", class = "Archer", stat = {80, 85, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "YuanBoGuan38", class = "Lord", stat = {84, 82, 90, 88, 86}, model = "lord-1-blue" }
        ,{ id = "YuanGuard38", class = "Infantry", stat = {80, 84, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "YuanArcher38", class = "Archer", stat = {78, 82, 82, 82, 80}, model = "archer-1-blue" }
        ,{ id = "CaoGongGong39", class = "Lord", stat = {84, 82, 86, 82, 78}, model = "lord-1-blue" }
        ,{ id = "YuLang39", class = "Strategist", stat = {80, 78, 90, 86, 76}, model = "Strategist-1-blue" }
        ,{ id = "XiFuJi39", class = "Strategist", stat = {84, 76, 92, 90, 88}, model = "Strategist-1-red" }
        ,{ id = "CaoGateGuard39", class = "Infantry", stat = {82, 87, 78, 83, 80}, model = "infantry-1-blue" }
        ,{ id = "CaoArcher39", class = "Archer", stat = {80, 85, 82, 83, 80}, model = "archer-1-blue" }
        ,{ id = "JinGuard39", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinArcher39", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "QiMan40", class = "Infantry", stat = {84, 90, 78, 85, 82}, model = "infantry-1-red" }
        ,{ id = "GuoGuiFu40", class = "Cavalry", stat = {88, 92, 88, 89, 86}, model = "cavalry-1-red" }
        ,{ id = "XiaoZiYin40", class = "Cavalry", stat = {88, 92, 86, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "DouYiShen40", class = "Cavalry", stat = {88, 94, 84, 88, 86}, model = "cavalry-1-blue" }
        ,{ id = "ChengDaXin40", class = "Cavalry", stat = {86, 92, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "DouYueJiao40", class = "Archer", stat = {90, 96, 88, 90, 86}, model = "archer-1-blue" }
        ,{ id = "YuanXuan40", class = "Cavalry", stat = {82, 88, 78, 83, 80}, model = "cavalry-1-blue" }
        ,{ id = "GongZiYin40", class = "Cavalry", stat = {82, 88, 78, 83, 80}, model = "cavalry-1-blue" }
        ,{ id = "ShiGui40", class = "Infantry", stat = {81, 86, 82, 83, 80}, model = "infantry-1-blue" }
        ,{ id = "BaiChou40", class = "Infantry", stat = {80, 85, 80, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "ChuGuard40", class = "Infantry", stat = {82, 88, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "ChuCavalry40", class = "Cavalry", stat = {83, 89, 78, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "ChuArcher40", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "ChenGuard40", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "ChenCavalry40", class = "Cavalry", stat = {81, 87, 78, 82, 80}, model = "cavalry-1-blue" }
        ,{ id = "ChenArcher40", class = "Archer", stat = {79, 84, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "CaiGuard40", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "CaiCavalry40", class = "Cavalry", stat = {81, 87, 78, 82, 80}, model = "cavalry-1-blue" }
        ,{ id = "CaiArcher40", class = "Archer", stat = {79, 84, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "XuXiGong43", class = "Lord", stat = {82, 78, 86, 82, 80}, model = "lord-1-blue" }
        ,{ id = "XuGuard43", class = "Infantry", stat = {81, 86, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "XuArcher43", class = "Archer", stat = {79, 84, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "JinGuard43", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinArcher43", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "ZhuZhiWu43", class = "Strategist", stat = {76, 68, 99, 98, 94}, model = "Strategist-1-red" }
        ,{ id = "ZhengWenGong43", class = "Lord", stat = {84, 78, 88, 84, 82}, model = "lord-1-blue" }
        ,{ id = "ShuZhan43", class = "Strategist", stat = {82, 78, 94, 92, 88}, model = "Strategist-1-blue" }
        ,{ id = "YiZhiHu43", class = "Strategist", stat = {80, 76, 96, 94, 90}, model = "Strategist-1-blue" }
        ,{ id = "QinGuard43", class = "Infantry", stat = {82, 87, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinPatrol43", class = "Cavalry", stat = {82, 88, 80, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "BaoManZi44", class = "Cavalry", stat = {86, 94, 76, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinXiangGong45", class = "Lord", stat = {88, 90, 88, 88, 86}, model = "lord-1-red" }
        ,{ id = "XianQieJu45", class = "Cavalry", stat = {88, 94, 84, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "TuJi45", class = "Infantry", stat = {84, 90, 80, 86, 84}, model = "infantry-1-red" }
        ,{ id = "XuYing45", class = "Cavalry", stat = {84, 90, 84, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "HuJuJu45", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "HanZiYu45", class = "Archer", stat = {82, 88, 86, 86, 84}, model = "archer-1-red" }
        ,{ id = "LiangHong45", class = "Cavalry", stat = {86, 92, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "LaiJu45", class = "Cavalry", stat = {84, 90, 80, 84, 82}, model = "cavalry-1-red" }
        ,{ id = "LangTan45", class = "Infantry", stat = {88, 96, 78, 88, 86}, model = "infantry-1-red" }
        ,{ id = "LuanDun45", class = "Cavalry", stat = {84, 90, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "XiQue45", class = "Archer", stat = {86, 92, 90, 90, 88}, model = "archer-1-red" }
        ,{ id = "BaiBuHu45", class = "Lord", stat = {90, 96, 78, 88, 86}, model = "lord-1-blue" }
        ,{ id = "JinGuard45", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "JinArcher45", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "QinGuard45", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "QinCavalry45", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "QinArcher45", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "DiCavalry45", class = "Cavalry", stat = {83, 89, 78, 84, 82}, model = "cavalry-1-blue" }
        ,{ id = "DiArcher45", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-blue" }
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
        ,{ id = "WangguanArcher46", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "QinGuard44", class = "Infantry", stat = {82, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "QinArcher44", class = "Archer", stat = {80, 86, 82, 84, 82}, model = "archer-1-red" }
        ,{ id = "HuaGong44", class = "Lord", stat = {80, 76, 84, 80, 78}, model = "lord-1-blue" }
        ,{ id = "HuaGuard44", class = "Infantry", stat = {80, 85, 78, 82, 80}, model = "infantry-1-blue" }
        ,{ id = "HuaArcher44", class = "Archer", stat = {78, 83, 80, 82, 80}, model = "archer-1-blue" }
        ,{ id = "ShuSunDeChen47", class = "Lord", stat = {86, 90, 88, 88, 86}, model = "lord-1-red" }
        ,{ id = "FuFuZhongSheng47", class = "Strategist", stat = {82, 88, 94, 92, 90}, model = "Strategist-1-red" }
        ,{ id = "QiaoRu47", class = "Infantry", stat = {92, 98, 70, 90, 86}, model = "infantry-1-blue" }
        ,{ id = "LuGuard47", class = "Infantry", stat = {83, 88, 80, 84, 82}, model = "infantry-1-red" }
        ,{ id = "LuArcher47", class = "Archer", stat = {81, 86, 84, 84, 82}, model = "archer-1-red" }
        ,{ id = "DiGuard47", class = "Infantry", stat = {83, 89, 78, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "DiCavalry47", class = "Cavalry", stat = {85, 91, 78, 85, 83}, model = "cavalry-1-blue" }
        ,{ id = "DiArcher47", class = "Archer", stat = {80, 86, 80, 83, 81}, model = "archer-1-blue" }
        ,{ id = "ZhaoDun47", class = "Strategist", stat = {92, 88, 98, 96, 92}, model = "Strategist-1-red" }
        ,{ id = "XianKe47", class = "Cavalry", stat = {86, 92, 84, 88, 86}, model = "cavalry-1-red" }
        ,{ id = "XunLinFu47", class = "Cavalry", stat = {88, 90, 94, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "XianDu47", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "GongZiYong47", class = "Lord", stat = {88, 86, 90, 88, 86}, model = "lord-1-blue" }
        ,{ id = "XianMie47", class = "Strategist", stat = {84, 82, 92, 90, 88}, model = "Strategist-1-blue" }
        ,{ id = "ShiHui47", class = "Strategist", stat = {90, 86, 98, 96, 94}, model = "Strategist-1-blue" }
        ,{ id = "JinGuard47", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-red" }
        ,{ id = "JinCavalry47", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinArcher47", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "QinGuard47", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "QinCavalry47", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "QinArcher47", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
        ,{ id = "DouYueJiao48", class = "Cavalry", stat = {90, 96, 88, 90, 86}, model = "cavalry-1-red" }
        ,{ id = "WeiJia48", class = "Strategist", stat = {88, 82, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "StrawDecoy48", class = "Infantry", stat = {60, 60, 60, 60, 60}, model = "infantry-1-red" }
        ,{ id = "GongZiJian48", class = "Lord", stat = {85, 88, 84, 86, 84}, model = "lord-1-blue" }
        ,{ id = "GongZiPang48", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "YueEr48", class = "Archer", stat = {82, 88, 86, 85, 84}, model = "archer-1-blue" }
        ,{ id = "ChuGuard48", class = "Infantry", stat = {84, 90, 80, 85, 83}, model = "infantry-1-red" }
        ,{ id = "ChuCavalry48", class = "Cavalry", stat = {85, 91, 80, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "ChuArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "ZhengGuard48", class = "Infantry", stat = {83, 89, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "ZhengCavalry48", class = "Cavalry", stat = {84, 90, 80, 85, 82}, model = "cavalry-1-blue" }
        ,{ id = "ZhengArcher48", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "QinKangGong48", class = "Lord", stat = {88, 86, 92, 88, 86}, model = "lord-1-blue" }
        ,{ id = "YuPian48", class = "Strategist", stat = {86, 80, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "XuJia48", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ZhaoChuan48", class = "Cavalry", stat = {86, 94, 76, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "HanJue48", class = "Strategist", stat = {88, 88, 94, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "JinGuard48", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-red" }
        ,{ id = "JinCavalry48", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "JinArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "QinGuard48", class = "Infantry", stat = {84, 90, 82, 85, 83}, model = "infantry-1-blue" }
        ,{ id = "QinCavalry48", class = "Cavalry", stat = {85, 91, 82, 86, 84}, model = "cavalry-1-blue" }
        ,{ id = "QinArcher48", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-blue" }
        ,{ id = "HuaOu49", class = "Cavalry", stat = {88, 92, 82, 89, 86}, model = "cavalry-1-red" }
        ,{ id = "SongZhaoGong49", class = "Lord", stat = {84, 82, 78, 80, 76}, model = "lord-1-blue" }
        ,{ id = "DangYiZhu49", class = "Infantry", stat = {90, 94, 78, 92, 88}, model = "infantry-1-blue" }
        ,{ id = "SongCoupGuard49", class = "Infantry", stat = {84, 89, 80, 85, 83}, model = "infantry-1-red" }
        ,{ id = "SongCoupCavalry49", class = "Cavalry", stat = {85, 91, 80, 86, 84}, model = "cavalry-1-red" }
        ,{ id = "SongCoupArcher49", class = "Archer", stat = {82, 88, 84, 85, 83}, model = "archer-1-red" }
        ,{ id = "RoyalRetainer49", class = "Infantry", stat = {83, 88, 80, 84, 82}, model = "infantry-1-blue" }
        ,{ id = "RoyalArcher49", class = "Archer", stat = {81, 87, 82, 84, 82}, model = "archer-1-blue" }
        ,{ id = "GongZiGuiSheng50", class = "Lord", stat = {88, 90, 90, 90, 88}, model = "lord-1-red" }
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
        ,{ id = "ChuZhuangWang51", class = "King", stat = {94, 92, 96, 96, 94}, model = "lord-1-red" }
        ,{ id = "GongZiCe51", class = "Strategist", stat = {92, 88, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "GongZiYingQi51", class = "Cavalry", stat = {91, 94, 88, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "PanWang51", class = "Cavalry", stat = {88, 92, 84, 89, 86}, model = "cavalry-1-red" }
        ,{ id = "LeBo51", class = "Cavalry", stat = {88, 94, 82, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "YangYouJi51", class = "Archer", stat = {94, 99, 90, 96, 94}, model = "archer-1-red" }
        ,{ id = "DouBenHuang51", class = "Cavalry", stat = {90, 94, 90, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "ChuRoyalGuard51", class = "Infantry", stat = {86, 91, 84, 87, 85}, model = "infantry-1-red" }
        ,{ id = "ChuRoyalArcher51", class = "Archer", stat = {84, 90, 86, 87, 85}, model = "archer-1-red" }
        ,{ id = "ChuAmbushGuard51", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-red" }
        ,{ id = "ChuAmbushCavalry51", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-red" }
        ,{ id = "ChuAmbushArcher51", class = "Archer", stat = {83, 89, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "RuoAoGuard51", class = "Infantry", stat = {85, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "RuoAoCavalry51", class = "Cavalry", stat = {86, 92, 82, 87, 85}, model = "cavalry-1-blue" }
        ,{ id = "RuoAoArcher51", class = "Archer", stat = {84, 90, 86, 87, 85}, model = "archer-1-blue" }
        ,{ id = "ZhengXiangGong52", class = "Lord", stat = {89, 82, 91, 91, 90}, model = "lord-1-red" }
        ,{ id = "GongZiQuJi52", class = "Strategist", stat = {91, 86, 94, 92, 91}, model = "Strategist-1-red" }
        ,{ id = "JinReliefGuard52", class = "Infantry", stat = {86, 90, 84, 88, 86}, model = "infantry-1-red" }
        ,{ id = "JinReliefCavalry52", class = "Cavalry", stat = {87, 92, 83, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "JinReliefArcher52", class = "Archer", stat = {84, 90, 87, 88, 86}, model = "archer-1-red" }
        ,{ id = "ZhengGuard52", class = "Infantry", stat = {84, 88, 83, 86, 85}, model = "infantry-1-red" }
        ,{ id = "ZhengArcher52", class = "Archer", stat = {82, 88, 85, 86, 84}, model = "archer-1-red" }
        ,{ id = "ChuLiufenGuard52", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-blue" }
        ,{ id = "ChuLiufenCavalry52", class = "Cavalry", stat = {88, 94, 84, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "ChuLiufenArcher52", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-blue" }
        ,{ id = "QuWu53", class = "Strategist", stat = {93, 88, 96, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "XiaZhengShu53", class = "Archer", stat = {88, 96, 84, 90, 88}, model = "archer-1-blue" }
        ,{ id = "ChuExpeditionGuard53", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-red" }
        ,{ id = "ChuExpeditionCavalry53", class = "Cavalry", stat = {88, 94, 84, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "ChuExpeditionArcher53", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-red" }
        ,{ id = "XiaHouseGuard53", class = "Infantry", stat = {84, 90, 82, 86, 84}, model = "infantry-1-blue" }
        ,{ id = "XiaHouseArcher53", class = "Archer", stat = {83, 91, 84, 86, 84}, model = "archer-1-blue" }
        ,{ id = "ChuSiegeGuard53", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-red" }
        ,{ id = "ChuSiegeCavalry53", class = "Cavalry", stat = {89, 95, 85, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "ChuSiegeArcher53", class = "Archer", stat = {86, 93, 88, 90, 88}, model = "archer-1-red" }
        ,{ id = "ZhengHuangmenGuard53", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "ZhengCityGuard53", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "ZhengCityArcher53", class = "Archer", stat = {85, 92, 87, 89, 87}, model = "archer-1-blue" }
        ,{ id = "XunYing54", class = "Cavalry", stat = {87, 92, 91, 90, 89}, model = "cavalry-1-blue" }
        ,{ id = "XunShou54", class = "Archer", stat = {91, 96, 92, 94, 92}, model = "archer-1-red" }
        ,{ id = "WeiQi54", class = "Cavalry", stat = {87, 93, 84, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "XiangLao54", class = "Cavalry", stat = {88, 93, 86, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "GongZiGuChen54", class = "Cavalry", stat = {87, 92, 87, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "ChuBiGuard54", class = "Infantry", stat = {89, 94, 87, 91, 89}, model = "infantry-1-red" }
        ,{ id = "ChuBiCavalry54", class = "Cavalry", stat = {90, 95, 86, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "ChuBiArcher54", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-red" }
        ,{ id = "JinCenterGuard54", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "JinCenterCavalry54", class = "Cavalry", stat = {89, 94, 85, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "JinCenterArcher54", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-blue" }
        ,{ id = "XunFamilyGuard54", class = "Infantry", stat = {87, 93, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinReturnArcher54", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-red" }
        ,{ id = "ChuSalvageGuard54", class = "Infantry", stat = {86, 91, 84, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "ChuSalvageCavalry54", class = "Cavalry", stat = {87, 92, 84, 89, 87}, model = "cavalry-1-blue" }
        ,{ id = "ShenShuShi55", class = "Strategist", stat = {93, 86, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "ShenXi55", class = "Cavalry", stat = {84, 89, 84, 87, 86}, model = "cavalry-1-red" }
        ,{ id = "WeiKe55", class = "Cavalry", stat = {90, 94, 92, 93, 91}, model = "cavalry-1-red" }
        ,{ id = "DuHui55", class = "Infantry", stat = {86, 99, 86, 93, 90}, model = "infantry-1-blue" }
        ,{ id = "ChuSiegeGuard55", class = "Infantry", stat = {89, 94, 87, 91, 89}, model = "infantry-1-red" }
        ,{ id = "ChuSiegeArcher55", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-red" }
        ,{ id = "SongGateGuard55", class = "Infantry", stat = {88, 93, 87, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "SongCityArcher55", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-blue" }
        ,{ id = "JinAmbushGuard55", class = "Infantry", stat = {87, 93, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinAmbushArcher55", class = "Archer", stat = {86, 92, 88, 89, 87}, model = "archer-1-red" }
        ,{ id = "QinAxeGuard55", class = "Infantry", stat = {88, 95, 84, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "QinGuard55", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "SunLiangFu56", class = "Cavalry", stat = {88, 92, 90, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "ShiJi56", class = "Strategist", stat = {88, 86, 94, 92, 90}, model = "Strategist-1-red" }
        ,{ id = "ZhongShuYuXi56", class = "Cavalry", stat = {86, 91, 87, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "GuoZuo56", class = "Strategist", stat = {91, 87, 96, 94, 92}, model = "Strategist-1-blue" }
        ,{ id = "GaoGu56", class = "Cavalry", stat = {88, 95, 84, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "XiKe56", class = "Archer", stat = {92, 94, 96, 95, 93}, model = "archer-1-red" }
        ,{ id = "JiSunXingFu56", class = "Strategist", stat = {92, 84, 98, 96, 94}, model = "Strategist-1-red" }
        ,{ id = "QiQingGong56", class = "King", stat = {88, 92, 88, 91, 89}, model = "lord-1-blue" }
        ,{ id = "FengChouFu56", class = "Cavalry", stat = {90, 93, 90, 92, 91}, model = "cavalry-1-blue" }
        ,{ id = "WeiRaidGuard56", class = "Infantry", stat = {86, 91, 85, 88, 86}, model = "infantry-1-red" }
        ,{ id = "QiAmbushGuard56", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "QiAmbushCavalry56", class = "Cavalry", stat = {89, 94, 85, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "WeiReliefGuard56", class = "Infantry", stat = {86, 92, 86, 89, 87}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionGuard56", class = "Infantry", stat = {89, 94, 88, 91, 89}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher56", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-red" }
        ,{ id = "QiCenterChariot56", class = "Cavalry", stat = {89, 95, 87, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "QiArcher56", class = "Archer", stat = {87, 94, 89, 91, 89}, model = "archer-1-blue" }
        ,{ id = "PalaceDoctor57", class = "Strategist", stat = {76, 66, 92, 90, 88}, model = "Strategist-1-red" }
        ,{ id = "PalaceSearchGuard57", class = "Infantry", stat = {88, 93, 82, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "PalaceSearchArcher57", class = "Archer", stat = {86, 91, 86, 89, 87}, model = "archer-1-blue" }
        ,{ id = "JinLiGong58", class = "Lord", stat = {88, 90, 86, 87, 84}, model = "lord-1-red" }
        ,{ id = "LuanShu58", class = "Strategist", stat = {93, 88, 97, 95, 93}, model = "Strategist-1-red" }
        ,{ id = "ShiXie58", class = "Strategist", stat = {92, 85, 98, 94, 92}, model = "Strategist-1-red" }
        ,{ id = "LuanZhen58", class = "Cavalry", stat = {89, 95, 88, 92, 91}, model = "cavalry-1-red" }
        ,{ id = "XiZhi58", class = "Cavalry", stat = {90, 94, 94, 93, 91}, model = "cavalry-1-red" }
        ,{ id = "XiQi58", class = "Cavalry", stat = {88, 93, 86, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "XunYan58", class = "Cavalry", stat = {89, 93, 92, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "ChuGongWang58", class = "King", stat = {94, 92, 96, 95, 93}, model = "lord-1-blue" }
        ,{ id = "GongZiRenFu58", class = "Cavalry", stat = {90, 94, 88, 91, 89}, model = "cavalry-1-blue" }
        ,{ id = "XiongFa58", class = "Cavalry", stat = {87, 94, 82, 89, 87}, model = "cavalry-1-blue" }
        ,{ id = "PanDang58", class = "Archer", stat = {90, 97, 88, 93, 91}, model = "archer-1-blue" }
        ,{ id = "GongYinXiang58", class = "Cavalry", stat = {88, 93, 85, 90, 88}, model = "cavalry-1-blue" }
        ,{ id = "JinYanlingGuard58", class = "Infantry", stat = {89, 94, 88, 91, 89}, model = "infantry-1-red" }
        ,{ id = "JinYanlingArcher58", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-red" }
        ,{ id = "ChuYanlingGuard58", class = "Infantry", stat = {90, 95, 89, 92, 90}, model = "infantry-1-blue" }
        ,{ id = "ChuYanlingCavalry58", class = "Cavalry", stat = {91, 96, 88, 93, 91}, model = "cavalry-1-blue" }
        ,{ id = "ChuYanlingArcher58", class = "Archer", stat = {88, 94, 91, 92, 90}, model = "archer-1-blue" }
        ,{ id = "XuTong59", class = "Strategist", stat = {91, 79, 95, 90, 86}, model = "Strategist-1-blue" }
        ,{ id = "YiYangWu59", class = "Cavalry", stat = {86, 91, 78, 86, 83}, model = "cavalry-1-blue" }
        ,{ id = "QingFeiTui59", class = "Infantry", stat = {88, 96, 75, 88, 84}, model = "infantry-1-blue" }
        ,{ id = "ChengHua59", class = "Cavalry", stat = {88, 94, 84, 89, 87}, model = "cavalry-1-red" }
        ,{ id = "CoupGuard59", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-red" }
        ,{ id = "CoupArcher59", class = "Archer", stat = {85, 92, 88, 89, 87}, model = "archer-1-red" }
        ,{ id = "RoyalEscort59", class = "Infantry", stat = {88, 94, 85, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "RoyalArcher59", class = "Archer", stat = {86, 93, 89, 90, 88}, model = "archer-1-blue" }
        ,{ id = "ZhaoWu59", class = "Cavalry", stat = {92, 90, 95, 92, 91}, model = "cavalry-1-red" }
        ,{ id = "ChengYing59", class = "Strategist", stat = {94, 78, 98, 95, 96}, model = "Strategist-1-red" }
        ,{ id = "TuHouseGuard59", class = "Infantry", stat = {87, 92, 84, 89, 87}, model = "infantry-1-blue" }
        ,{ id = "TuHouseArcher59", class = "Archer", stat = {85, 92, 88, 89, 87}, model = "archer-1-blue" }
        ,{ id = "JinDaoGong60", class = "Lord", stat = {95, 90, 98, 96, 95}, model = "lord-1-red" }
        ,{ id = "LuanYan60", class = "Cavalry", stat = {91, 95, 90, 93, 90}, model = "cavalry-1-red" }
        ,{ id = "XiangShu60", class = "Strategist", stat = {93, 87, 97, 94, 93}, model = "Strategist-1-red" }
        ,{ id = "ZhongSunMie60", class = "Strategist", stat = {92, 86, 96, 93, 92}, model = "Strategist-1-red" }
        ,{ id = "YuShi60", class = "Strategist", stat = {88, 84, 92, 89, 86}, model = "Strategist-1-blue" }
        ,{ id = "XiangWeiRen60", class = "Infantry", stat = {87, 91, 83, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "LinZhu60", class = "Archer", stat = {86, 90, 87, 88, 86}, model = "archer-1-blue" }
        ,{ id = "XiangDai60", class = "Cavalry", stat = {88, 92, 84, 89, 87}, model = "cavalry-1-blue" }
        ,{ id = "YuFu60", class = "Infantry", stat = {87, 91, 84, 88, 86}, model = "infantry-1-blue" }
        ,{ id = "JinCoalitionGuard60", class = "Infantry", stat = {88, 93, 86, 90, 88}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher60", class = "Archer", stat = {86, 92, 89, 90, 88}, model = "archer-1-red" }
        ,{ id = "SongCoalitionGuard60", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-red" }
        ,{ id = "PengchengGuard60", class = "Infantry", stat = {87, 92, 85, 89, 87}, model = "infantry-1-blue" }
        ,{ id = "PengchengArcher60", class = "Archer", stat = {86, 92, 89, 90, 88}, model = "archer-1-blue" }
        ,{ id = "ZhuFan60", class = "Lord", stat = {92, 93, 90, 92, 91}, model = "lord-1-red" }
        ,{ id = "YiMei60", class = "Cavalry", stat = {89, 94, 85, 90, 88}, model = "cavalry-1-red" }
        ,{ id = "YuJi60", class = "Cavalry", stat = {90, 95, 87, 91, 89}, model = "cavalry-1-red" }
        ,{ id = "DengLiao60", class = "Cavalry", stat = {91, 96, 88, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "YinQi60", class = "Strategist", stat = {90, 88, 95, 92, 90}, model = "Strategist-1-blue" }
        ,{ id = "WuMarine60", class = "Infantry", stat = {87, 93, 84, 89, 88}, model = "infantry-1-red" }
        ,{ id = "WuArcher60", class = "Archer", stat = {86, 92, 88, 90, 88}, model = "archer-1-red" }
        ,{ id = "ChuMarine60", class = "Infantry", stat = {88, 94, 85, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "ChuRiverArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }
        ,{ id = "ShiGai60", class = "Cavalry", stat = {91, 95, 89, 92, 90}, model = "cavalry-1-red" }
        ,{ id = "ShuLiangHe60", class = "Infantry", stat = {90, 97, 84, 91, 91}, model = "infantry-1-red" }
        ,{ id = "QinJinFu60", class = "Infantry", stat = {89, 95, 85, 90, 89}, model = "infantry-1-red" }
        ,{ id = "DiSiMi60", class = "Infantry", stat = {89, 95, 84, 90, 89}, model = "infantry-1-red" }
        ,{ id = "YunBan60", class = "Cavalry", stat = {91, 96, 88, 92, 90}, model = "cavalry-1-blue" }
        ,{ id = "BiYangLord60", class = "Lord", stat = {88, 87, 90, 89, 88}, model = "lord-1-blue" }
        ,{ id = "BiYangGuard60", class = "Infantry", stat = {88, 94, 86, 90, 88}, model = "infantry-1-blue" }
        ,{ id = "BiYangArcher60", class = "Archer", stat = {87, 93, 90, 91, 89}, model = "archer-1-blue" }
        ,{ id = "GongSunXia61", class = "Cavalry", stat = {91,94,91,92,91}, model = "cavalry-1-red" }
        ,{ id = "ZiChan61", class = "Strategist", stat = {94,82,99,96,96}, model = "Strategist-1-red" }
        ,{ id = "GongSunChai61", class = "Cavalry", stat = {90,94,89,91,90}, model = "cavalry-1-red" }
        ,{ id = "WeiZhi61", class = "Cavalry", stat = {87,92,85,89,86}, model = "cavalry-1-blue" }
        ,{ id = "SiChen61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-blue" }
        ,{ id = "HouJin61", class = "Archer", stat = {85,90,87,88,86}, model = "archer-1-blue" }
        ,{ id = "ZhengHouseGuard61", class = "Infantry", stat = {87,92,85,89,87}, model = "infantry-1-red" }
        ,{ id = "ZhengRebel61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-blue" }
        ,{ id = "ZhengRebelArcher61", class = "Archer", stat = {85,90,87,88,86}, model = "archer-1-blue" }
        ,{ id = "FanYang61", class = "Cavalry", stat = {91,95,92,93,91}, model = "cavalry-1-red" }
        ,{ id = "QinJingGong61", class = "Lord", stat = {93,91,94,93,92}, model = "lord-1-blue" }
        ,{ id = "YingZhan61", class = "Cavalry", stat = {91,96,88,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GongZiWuDi61", class = "Cavalry", stat = {90,95,87,91,89}, model = "cavalry-1-blue" }
        ,{ id = "QinYulinGuard61", class = "Infantry", stat = {88,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QinYulinArcher61", class = "Archer", stat = {87,93,90,91,89}, model = "archer-1-blue" }
        ,{ id = "WeiXianGong61", class = "Lord", stat = {88,89,84,87,83}, model = "lord-1-red" }
        ,{ id = "GongSunDing61", class = "Archer", stat = {91,98,90,94,92}, model = "archer-1-red" }
        ,{ id = "SunKuai61", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "SunJia61", class = "Cavalry", stat = {88,93,85,89,87}, model = "cavalry-1-blue" }
        ,{ id = "GengGongCha61", class = "Archer", stat = {90,97,88,92,90}, model = "archer-1-blue" }
        ,{ id = "YinGongTuo61", class = "Archer", stat = {88,95,86,90,88}, model = "archer-1-blue" }
        ,{ id = "GongZiZhuan61", class = "Cavalry", stat = {87,92,86,89,87}, model = "cavalry-1-red" }
        ,{ id = "WeiPalaceGuard61", class = "Infantry", stat = {86,91,84,88,86}, model = "infantry-1-red" }
        ,{ id = "SunPursuer61", class = "Cavalry", stat = {87,92,84,89,87}, model = "cavalry-1-blue" }
        ,{ id = "SunArcher61", class = "Archer", stat = {86,91,87,89,87}, model = "archer-1-blue" }
        ,{ id = "HanQi62", class = "Strategist", stat = {95,90,99,96,95}, model = "Strategist-1-red" }
        ,{ id = "WeiJiang62", class = "Cavalry", stat = {93,96,92,94,93}, model = "cavalry-1-red" }
        ,{ id = "ZhouChuo62", class = "Cavalry", stat = {90,96,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "LuanYing62", class = "Cavalry", stat = {91,95,90,93,91}, model = "cavalry-1-red" }
        ,{ id = "QiLingGong62", class = "Lord", stat = {91,89,88,89,86}, model = "lord-1-blue" }
        ,{ id = "XiGuiFu62", class = "Cavalry", stat = {91,95,90,92,90}, model = "cavalry-1-blue" }
        ,{ id = "ZhiChuo62", class = "Cavalry", stat = {90,96,88,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GuoZui62", class = "Cavalry", stat = {89,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "CuiZhu62", class = "Strategist", stat = {94,87,98,95,92}, model = "Strategist-1-blue" }
        ,{ id = "QingFeng62", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "QiCoalitionGuard62", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-blue" }
        ,{ id = "QiCoalitionArcher62", class = "Archer", stat = {88,94,92,91,90}, model = "archer-1-blue" }
        ,{ id = "JinCoalitionGuard62", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "JinCoalitionArcher62", class = "Archer", stat = {88,94,92,91,90}, model = "archer-1-red" }
        ,{ id = "QiZhuangGong62", class = "Lord", stat = {94,95,91,94,92}, model = "lord-1-red" }
        ,{ id = "GongLou62", class = "Infantry", stat = {87,90,90,89,91}, model = "infantry-1-red" }
        ,{ id = "SuShaWei62", class = "Cavalry", stat = {90,94,86,90,87}, model = "cavalry-1-blue" }
        ,{ id = "GaotangGuard62", class = "Infantry", stat = {88,93,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "GaotangArcher62", class = "Archer", stat = {87,92,89,90,88}, model = "archer-1-blue" }
        ,{ id = "ShuHu62", class = "Cavalry", stat = {89,94,85,90,87}, model = "cavalry-1-blue" }
        ,{ id = "JiYi62", class = "Infantry", stat = {88,93,84,89,87}, model = "infantry-1-blue" }
        ,{ id = "HuangYuan62", class = "Cavalry", stat = {88,93,85,89,87}, model = "cavalry-1-blue" }
        ,{ id = "XunWu62", class = "Cavalry", stat = {92,95,93,93,92}, model = "cavalry-1-red" }
        ,{ id = "JinArrestGuard62", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "WeiShu63", class = "Cavalry", stat = {93,94,94,94,92}, model = "cavalry-1-red" }
        ,{ id = "DuRong63", class = "Infantry", stat = {91,99,82,93,91}, model = "infantry-1-blue" }
        ,{ id = "LuanLe63", class = "Archer", stat = {90,98,87,93,90}, model = "archer-1-blue" }
        ,{ id = "LuanFang63", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "LuanRong63", class = "Infantry", stat = {87,92,84,89,86}, model = "infantry-1-blue" }
        ,{ id = "XuWu63", class = "Strategist", stat = {89,81,94,91,89}, model = "Strategist-1-blue" }
        ,{ id = "FeiBao63", class = "Infantry", stat = {90,97,87,92,91}, model = "infantry-1-red" }
        ,{ id = "XieYong63", class = "Infantry", stat = {87,93,84,89,87}, model = "infantry-1-red" }
        ,{ id = "XieSu63", class = "Infantry", stat = {87,93,84,89,87}, model = "infantry-1-red" }
        ,{ id = "MuGang63", class = "Infantry", stat = {88,95,83,90,88}, model = "infantry-1-red" }
        ,{ id = "MuJin63", class = "Infantry", stat = {88,95,83,90,88}, model = "infantry-1-red" }
        ,{ id = "LuanRebelGuard63", class = "Infantry", stat = {89,94,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "LuanRebelArcher63", class = "Archer", stat = {88,94,90,91,89}, model = "archer-1-blue" }
        ,{ id = "JinGugongGuard63", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "JinGugongArcher63", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "QuwoGuard63", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QuwoArcher63", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "WangSunHui64", class = "Cavalry", stat = {91,94,91,92,90}, model = "cavalry-1-red" }
        ,{ id = "ShenXianYu64", class = "Strategist", stat = {91,86,96,93,92}, model = "Strategist-1-red" }
        ,{ id = "YanMao64", class = "Cavalry", stat = {88,93,86,90,88}, model = "cavalry-1-red" }
        ,{ id = "ZhaoSheng64", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "ZhaoPursuer64", class = "Cavalry", stat = {89,94,85,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ZhaoArcher64", class = "Archer", stat = {88,93,90,90,89}, model = "archer-1-blue" }
        ,{ id = "QiRetreatGuard64", class = "Infantry", stat = {89,94,86,90,89}, model = "infantry-1-red" }
        ,{ id = "QiRetreatArcher64", class = "Archer", stat = {88,93,90,90,89}, model = "archer-1-red" }
        ,{ id = "HuaZhou64", class = "Infantry", stat = {91,98,85,92,91}, model = "infantry-1-red" }
        ,{ id = "QiLiang64", class = "Infantry", stat = {92,98,87,93,92}, model = "infantry-1-red" }
        ,{ id = "XiHouZhong64", class = "Infantry", stat = {89,96,84,90,90}, model = "infantry-1-red" }
        ,{ id = "JuLiBiGong64", class = "Lord", stat = {89,91,90,90,88}, model = "lord-1-blue" }
        ,{ id = "JuGateCaptain64", class = "Archer", stat = {89,95,90,91,89}, model = "archer-1-blue" }
        ,{ id = "JuGuard64", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "JuArcher64", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "TangWuJiu65", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "CuiCheng65", class = "Cavalry", stat = {88,93,85,90,87}, model = "cavalry-1-red" }
        ,{ id = "CuiJiang65", class = "Cavalry", stat = {89,94,85,90,88}, model = "cavalry-1-red" }
        ,{ id = "DongGuoYan65", class = "Strategist", stat = {91,84,96,92,90}, model = "Strategist-1-red" }
        ,{ id = "JiaJu65", class = "Cavalry", stat = {89,95,84,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ZhouChuoQi65", class = "Cavalry", stat = {91,97,86,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GongSunAo65", class = "Infantry", stat = {90,96,84,91,89}, model = "infantry-1-blue" }
        ,{ id = "LouYan65", class = "Infantry", stat = {88,94,83,89,87}, model = "infantry-1-blue" }
        ,{ id = "CuiAmbusher65", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "QiBraveGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "NiuChen65", class = "Archer", stat = {90,96,89,92,90}, model = "archer-1-red" }
        ,{ id = "ChaoGuard65", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "WuGateGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "WuGateArcher65", class = "Archer", stat = {88,94,90,91,89}, model = "archer-1-blue" }
        ,{ id = "NingXi65", class = "Strategist", stat = {93,87,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "YouZaiGu65", class = "Strategist", stat = {91,84,96,92,91}, model = "Strategist-1-red" }
        ,{ id = "BeiGongYi65", class = "Cavalry", stat = {90,94,88,91,89}, model = "cavalry-1-red" }
        ,{ id = "SunXiang65", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "ChuDai65", class = "Archer", stat = {90,96,88,92,90}, model = "archer-1-blue" }
        ,{ id = "YongChu65", class = "Infantry", stat = {89,94,85,90,88}, model = "infantry-1-blue" }
        ,{ id = "WeiShangGong65", class = "Lord", stat = {88,90,86,88,85}, model = "lord-1-blue" }
        ,{ id = "TaiZiJiao65", class = "Cavalry", stat = {87,92,83,88,86}, model = "cavalry-1-blue" }
        ,{ id = "SunHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "SunHouseArcher65", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "NingHouseGuard65", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }
        ,{ id = "GongSunMianYu66", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-red" }
        ,{ id = "LuPuBie66", class = "Strategist", stat = {93,88,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "QuJian66", class = "Strategist", stat = {94,88,98,95,93}, model = "Strategist-1-red" }
        ,{ id = "ZiJiang66", class = "Cavalry", stat = {91,95,90,92,90}, model = "cavalry-1-red" }
        ,{ id = "XiHuan66", class = "Strategist", stat = {90,87,96,92,90}, model = "Strategist-1-red" }
        ,{ id = "QuHuYong66", class = "Strategist", stat = {93,86,97,94,91}, model = "Strategist-1-blue" }
        ,{ id = "ShuJiuLord66", class = "Lord", stat = {87,86,89,88,86}, model = "lord-1-blue" }
        ,{ id = "ChuanFengShu66", class = "Cavalry", stat = {91,96,87,92,90}, model = "cavalry-1-red" }
        ,{ id = "GongZiWei66", class = "Cavalry", stat = {92,95,93,93,91}, model = "cavalry-1-red" }
        ,{ id = "HuangJie66", class = "Cavalry", stat = {89,94,87,90,88}, model = "cavalry-1-blue" }
        ,{ id = "SunAmbusher66", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-red" }
        ,{ id = "WeiRaider66", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "NingGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-red" }
        ,{ id = "CuiGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "ChuShujuGuard66", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChuShujuArcher66", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "WuReliefGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "WuReliefArcher66", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "ZhengGuard66", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "LuPuGui67", class = "Cavalry", stat = {94,96,94,95,93}, model = "cavalry-1-red" }
        ,{ id = "GaoChai67", class = "Strategist", stat = {93,86,97,94,92}, model = "Strategist-1-red" }
        ,{ id = "LuanZao67", class = "Strategist", stat = {92,87,96,93,91}, model = "Strategist-1-red" }
        ,{ id = "QingShe67", class = "Cavalry", stat = {92,98,88,94,91}, model = "cavalry-1-blue" }
        ,{ id = "QingSi67", class = "Cavalry", stat = {89,94,86,90,88}, model = "cavalry-1-blue" }
        ,{ id = "QingYi67", class = "Cavalry", stat = {88,93,86,90,87}, model = "cavalry-1-blue" }
        ,{ id = "GongSunHei67", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-red" }
        ,{ id = "SiDai67", class = "Cavalry", stat = {90,95,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "YinDuan67", class = "Infantry", stat = {91,94,90,92,90}, model = "infantry-1-red" }
        ,{ id = "LiangXiao67", class = "Cavalry", stat = {93,96,94,94,91}, model = "cavalry-1-blue" }
        ,{ id = "QiCoalitionGuard67", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "QiCoalitionArcher67", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "QingTempleGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingCounterGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "QingCounterArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "ZhengGateGuard67", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ZhengGateArcher67", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "LiangHouseGuard67", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "LiangHouseArcher67", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "ChenWuYu68", class = "Strategist", stat = {95,88,98,96,94}, model = "Strategist-1-red" }
        ,{ id = "BaoGuo68", class = "Archer", stat = {92,95,93,94,92}, model = "archer-1-red" }
        ,{ id = "WangHei68", class = "Cavalry", stat = {91,96,89,93,91}, model = "cavalry-1-red" }
        ,{ id = "LuanShi68", class = "Cavalry", stat = {91,95,89,92,90}, model = "cavalry-1-blue" }
        ,{ id = "GaoQiang68", class = "Cavalry", stat = {90,94,87,91,88}, model = "cavalry-1-blue" }
        ,{ id = "ChenBaoGuard68", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChenBaoArcher68", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "LuanGaoGuard68", class = "Infantry", stat = {89,94,86,90,88}, model = "infantry-1-blue" }
        ,{ id = "LuanGaoArcher68", class = "Archer", stat = {88,94,91,91,89}, model = "archer-1-blue" }
        ,{ id = "QiCitizenGuard68", class = "Infantry", stat = {88,93,86,90,88}, model = "infantry-1-red" }
        ,{ id = "QiCitizenArcher68", class = "Archer", stat = {87,93,90,90,89}, model = "archer-1-red" }
        ,{ id = "ChuLingWang69", class = "King", stat = {94,94,91,92,88}, model = "lord-1-red" }
        ,{ id = "WuJu69", class = "Strategist", stat = {96,88,99,96,95}, model = "Strategist-1-red" }
        ,{ id = "GongZiQiJi69", class = "Lord", stat = {95,94,97,95,94}, model = "lord-1-red" }
        ,{ id = "CaiLingHou69", class = "Lord", stat = {89,88,84,86,82}, model = "lord-1-blue" }
        ,{ id = "CaiShiZiYou69", class = "Lord", stat = {91,92,88,90,91}, model = "lord-1-blue" }
        ,{ id = "GongSunGuiSheng69", class = "Strategist", stat = {94,86,97,94,94}, model = "Strategist-1-blue" }
        ,{ id = "CaiWei69", class = "Cavalry", stat = {90,92,90,91,93}, model = "cavalry-1-blue" }
        ,{ id = "ChaoWu69", class = "Strategist", stat = {92,84,96,93,92}, model = "Strategist-1-blue" }
        ,{ id = "ChuSiegeGuard69", class = "Infantry", stat = {90,95,88,92,90}, model = "infantry-1-red" }
        ,{ id = "ChuSiegeArcher69", class = "Archer", stat = {89,94,92,92,91}, model = "archer-1-red" }
        ,{ id = "CaiGuard69", class = "Infantry", stat = {89,94,88,91,90}, model = "infantry-1-blue" }
        ,{ id = "CaiArcher69", class = "Archer", stat = {88,93,91,91,90}, model = "archer-1-blue" }
        ,{ id = "ZiGan70", class = "Lord", stat = {93,91,92,91,90}, model = "lord-1-red" }
        ,{ id = "ZiXi70", class = "Strategist", stat = {92,85,96,93,92}, model = "Strategist-1-red" }
        ,{ id = "XiaNie70", class = "Cavalry", stat = {91,95,88,92,90}, model = "cavalry-1-red" }
        ,{ id = "XuWuMou70", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "DouChengRan70", class = "Strategist", stat = {93,88,96,94,92}, model = "Strategist-1-red" }
        ,{ id = "WeiPi70", class = "Strategist", stat = {92,85,94,92,90}, model = "Strategist-1-blue" }
        ,{ id = "ShiZiLu70", class = "Lord", stat = {89,90,86,88,86}, model = "lord-1-blue" }
        ,{ id = "GongZiBa70", class = "Infantry", stat = {88,92,84,89,86}, model = "infantry-1-blue" }
        ,{ id = "TianKaiJiang71", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-red" }
        ,{ id = "GuYeZi71", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-red" }
        ,{ id = "YingShuang71", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "XuJun71", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-blue" }
        ,{ id = "QiGuard71", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-red" }
        ,{ id = "QiArcher71", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-red" }
        ,{ id = "XuGuard71", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "XuArcher71", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "WuYuan72", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "GongZiSheng72", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-red" }
        ,{ id = "HuangFuNe72", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "ZhaoGuanCaptain72", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "ZhaoGuard72", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "ZhaoArcher72", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "JiGuang73", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-red" }
        ,{ id = "GongZiGai73", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-red" }
        ,{ id = "XiaNie73", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "WeiYue73", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "HuGong73", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-blue" }
        ,{ id = "ShenGong73", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-blue" }
        ,{ id = "WuGuard73", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-red" }
        ,{ id = "WuArcher73", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-red" }
        ,{ id = "CoalitionGuard73", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "CoalitionArcher73", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "WuHelu79", class = "King", stat = {94,88,90,94,92}, model = "lord-1-red" }
        ,{ id = "SunWu75", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "FuGai75", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-red" }
        ,{ id = "BoPi75", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "NangWa75", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-blue" }
        ,{ id = "ShenYinShu75", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "TangHou75", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-blue" }
        ,{ id = "ChuGuard75", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "ChuArcher75", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "QinRelief75", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "LuDingGong78", class = "Lord", stat = {94,88,90,94,92}, model = "lord-1-red" }
        ,{ id = "JiSunSi78", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "YangHu78", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "YangYue78", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "GongShanBuNiu78", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "ShuSunZhe78", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-blue" }
        ,{ id = "LuGuard78", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-red" }
        ,{ id = "LuRebel78", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "LuRebelArcher78", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "GouJian79", class = "King", stat = {94,88,90,94,92}, model = "lord-1-red" }
        ,{ id = "LingGuFu79", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-red" }
        ,{ id = "FanLi79", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "WenZhong79", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-red" }
        ,{ id = "WuZiXu79", class = "Strategist", stat = {94,88,98,94,92}, model = "Strategist-1-blue" }
        ,{ id = "ZhuanYi79", class = "Cavalry", stat = {90,96,90,94,92}, model = "cavalry-1-blue" }
        ,{ id = "FuChai80", class = "King", stat = {94,88,90,94,92}, model = "lord-1-blue" }
        ,{ id = "YueGuard79", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-red" }
        ,{ id = "YueArcher79", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-red" }
        ,{ id = "WuGuard79", class = "Infantry", stat = {90,96,90,94,92}, model = "infantry-1-blue" }
        ,{ id = "WuArcher79", class = "Archer", stat = {90,96,90,94,92}, model = "archer-1-blue" }
        ,{ id = "ChenCaiGuard70", class = "Infantry", stat = {89,94,87,91,89}, model = "infantry-1-red" }
        ,{ id = "ChenCaiArcher70", class = "Archer", stat = {88,94,91,91,90}, model = "archer-1-red" }
        ,{ id = "ChuPalaceGuard70", class = "Infantry", stat = {89,94,88,91,90}, model = "infantry-1-blue" }
        ,{ id = "ChuPalaceArcher70", class = "Archer", stat = {88,93,91,91,89}, model = "archer-1-blue" }    },
    equipments = {},
    consumables = {},
    stages = { "01", "02", "03", "03b", "04a", "04", "05", "06", "07", "07b", "08a", "08", "09", "10a", "10b", "11a", "11b", "11c", "12a", "12b", "13a", "13b", "14a", "14b", "15a", "16", "17", "18", "19a", "19b", "20a", "20b", "20c", "20d", "21a", "21b", "21c", "22", "23a", "23b", "24a", "24b", "25a", "25b", "26a", "26b", "27a", "27b", "28", "29", "30a", "30b", "31", "32", "33a", "33b", "34a", "34b", "35", "36a", "36b", "38a", "38b", "39", "40", "42", "43a", "43b", "44", "45a", "45b", "46a", "46b", "46c", "47a", "47b", "48a", "48b", "49", "50a", "50b", "50c", "51", "52", "53a", "53b", "54a", "54b", "55a", "55b", "56a", "56b", "57", "58", "59a", "59b", "60a", "60b", "60c", "61a", "61b", "61c", "62a", "62b", "62c", "63a", "63b", "64a", "64b", "65a", "65b", "65c", "66a", "66b", "66c", "66d", "66e", "67a", "67b", "68", "69", "70", "71", "72", "73", "75", "78", "79", "80" }
}
