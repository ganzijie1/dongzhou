from __future__ import annotations


STAGES = [
    dict(id="82", chapter=82, map="m128", battle="艾陵之战", objective="击破齐军中阵并生擒国书。", own=[("FuChai80", "吴王夫差"), ("XuMenChao82", "胥门巢")], enemy=("GuoShu82", "国书"), outcome="capture", theme="river", focus="吴、鲁联军在艾陵以鸣金为进军号，反分齐军三阵；伍员苦谏伐越不从，战后被赐剑自尽。"),
    dict(id="83", chapter=83, map="m129", battle="笠泽灭吴", objective="渡过笠泽，合围姑苏并迫使夫差请降。", own=[("GouJian79", "越王勾践"), ("FanLi79", "范蠡"), ("WenZhong79", "文种")], enemy=("FuChai80", "吴王夫差"), outcome="capture", theme="river", focus="白公胜之乱由叶公平定；越军随后分三阵渡江，长期围困姑苏，夫差败亡而勾践北会诸侯称霸。"),
    dict(id="84", chapter=84, map="m130", battle="晋阳之战", objective="守住晋阳水城，策反韩魏后击杀智伯。", own=[("ZhaoWuXu84", "赵无恤"), ("ZhangMengTan84", "张孟谈")], enemy=("ZhiBo84", "智伯瑶"), outcome="death", theme="flood", focus="智伯决晋水灌城，张孟谈夜出说韩魏倒戈；赵氏反决水淹智营，三家灭智氏，豫让随后三次报主。"),
    dict(id="85", chapter=85, map="m131", battle="中山之战", objective="突破中山三道营垒并俘获中山君。", own=[("LeYang85", "乐羊"), ("XiMenBao85", "西门豹")], enemy=("ZhongShanJun85", "中山君"), outcome="capture", theme="mountain", focus="魏文侯任乐羊伐中山，乐羊忍食其子之羹以明无私；西门豹治邺，惩治河伯娶妇的巫祝豪强。"),
    dict(id="86", chapter=86, map="m132", battle="鲁齐之战", objective="坚守鲁境并击退齐军主力。", own=[("WuQi86", "吴起"), ("LuMuGong86", "鲁穆公")], enemy=("QiJiang86", "齐军主将"), outcome="retreat", theme="field", focus="吴起杀妻求将，率鲁军破齐；入魏后训练武卒守西河，遭谗离魏，后在楚变法强兵。"),
    dict(id="87", chapter=87, map="m133", battle="商於拓境", objective="攻破楚军边营，夺取商於六百里。", own=[("ShangYang87", "卫鞅"), ("QinXiaoGong87", "秦孝公")], enemy=("ChuBianJiang87", "楚国边将"), outcome="retreat", theme="mountain", focus="卫鞅入秦徙木立信，推行军功、县制与连坐，迁都咸阳；秦国富强后攻取楚国商於之地。"),
    dict(id="88", chapter=88, map="m134", battle="桂陵之战", objective="诱庞涓进入颠倒八门阵并迫其撤退。", own=[("TianJi88", "田忌"), ("SunBin88", "孙膑")], enemy=("PangJuan88", "庞涓"), outcome="retreat", theme="forest", focus="孙膑遭庞涓刖刑后佯狂脱魏，入齐助田忌赛马；围魏救赵，于桂陵设八门阵重创魏军。"),
    dict(id="89", chapter=89, map="m135", battle="马陵之战", objective="封锁马陵道，以万弩伏击并击杀庞涓。", own=[("TianJi88", "田忌"), ("SunBin88", "孙膑")], enemy=("PangJuan88", "庞涓"), outcome="death", theme="forest", focus="孙膑以减灶诱敌深入马陵，万弩齐发，庞涓中箭自尽，太子申被俘；商鞅后来在咸阳受车裂。"),
    dict(id="91", chapter=91, sources=(90, 91), map="m136", battle="齐军平燕", objective="平定子之党羽并控制燕都。", own=[("KuangZhang91", "匡章"), ("QiXuanWang91", "齐宣王")], enemy=("ZiZhi91", "子之"), outcome="death", theme="city", focus="苏秦合纵六国、张仪入秦以连横相抗；燕王哙让国子之引发内乱，齐军乘乱入燕，燕国几近覆亡。"),
    dict(id="92", chapter=92, map="m137", battle="丹阳之战", objective="击破楚军丹阳防线并俘获屈匄。", own=[("WeiZhang92", "魏章"), ("QinHuiWenWang92", "秦惠文王")], enemy=("QuGai92", "屈匄"), outcome="capture", theme="river", focus="秦楚争衡，秦军在丹阳大破楚军；秦武王举鼎绝胫而死，楚怀王后来赴武关会盟，被秦扣留。"),
    dict(id="93", chapter=93, map="m138", battle="沙丘宫变", objective="攻破沙丘宫，诛杀公子章并控制宫门。", own=[("GongZiCheng93", "公子成"), ("LiDui93", "李兑")], enemy=("ZhaoZhang93", "公子章"), outcome="death", theme="palace", focus="赵武灵王传位后卷入公子章之乱，公子成、李兑围沙丘宫；主父被困百日饿死，孟尝君则以鸡鸣狗盗脱秦。"),
    dict(id="94", chapter=94, map="m139", battle="五国伐宋", objective="突破睢阳外郭，生擒宋康王。", own=[("MengChangJun94", "孟尝君"), ("QiMinWang94", "齐湣王")], enemy=("SongKangWang94", "宋康王"), outcome="capture", theme="city", focus="冯谖营造孟尝君狡兔三窟，使其复相齐国；齐联合诸侯攻灭暴宋，宋康王出奔后被擒。"),
    dict(id="95a", chapter=95, slice=(0.0, 0.56), map="m140", battle="乐毅伐齐", objective="连破齐军主力，推进至即墨城外。", own=[("LeYi95", "乐毅"), ("YanZhaoWang95", "燕昭王")], enemy=("QiMinWang94", "齐湣王"), outcome="retreat", theme="field", focus="燕昭王筑黄金台招贤，乐毅统五国军济西破齐，连下七十余城；齐湣王逃入莒城后身死。"),
    dict(id="95b", chapter=95, slice=(0.44, 1.0), map="m141", battle="即墨火牛阵", objective="放出火牛冲阵并击杀骑劫，收复齐地。", own=[("TianDan95", "田单"), ("QiXiangWang95", "齐襄王")], enemy=("QiJie95", "骑劫"), outcome="death", theme="city", focus="燕惠王中反间计撤乐毅，以骑劫代将；田单守即墨，以火牛阵夜袭燕营，乘胜收复齐国七十余城。"),
    dict(id="96", chapter=96, map="m142", battle="阏与之战", objective="越过狭道驰援阏与，击退秦军。", own=[("ZhaoShe96", "赵奢"), ("LianPo96", "廉颇")], enemy=("HuShang96", "胡伤"), outcome="retreat", theme="mountain", focus="蔺相如完璧归赵、渑池抗秦并与廉颇将相和；赵奢出奇疾进阏与，占北山大破秦军。"),
    dict(id="97", chapter=97, map="m143", battle="华阳之战", objective="合围华阳联军并迫使魏将撤退。", own=[("BaiQi97", "白起"), ("FanJu97", "范雎")], enemy=("MangMao97", "芒卯"), outcome="retreat", theme="field", focus="范雎受魏齐迫害，诈死逃秦化名张禄，提出远交近攻；秦军在华阳击破赵魏联军，魏国被迫割地。"),
    dict(id="98", chapter=98, map="m144", battle="长平之战", objective="截断赵军粮道，合围并击杀赵括。", own=[("BaiQi97", "白起"), ("WangHe98", "王龁")], enemy=("ZhaoKuo98", "赵括"), outcome="death", theme="trench", focus="秦赵相持长平，赵王以赵括代廉颇；白起断粮围困赵军，赵括突围中箭身亡，降卒遭坑杀。"),
    dict(id="99", chapter=99, map="m145", battle="邯郸保卫战", objective="守住邯郸城门并击退王陵。", own=[("PingYuanJun99", "平原君"), ("LianPo96", "廉颇")], enemy=("WangLing99", "王陵"), outcome="retreat", theme="city", focus="白起拒绝再攻邯郸，被秦昭王赐死杜邮；赵国军民固守邯郸，秦军久攻不克，吕不韦则谋迎异人归秦。"),
    dict(id="100", chapter=100, map="m146", battle="窃符救赵", objective="夺取晋鄙兵权，渡河击退围邯郸秦军。", own=[("XinLingJun100", "信陵君"), ("ZhuHai100", "朱亥")], enemy=("QinJiang100", "秦军主将"), outcome="retreat", theme="river", focus="鲁仲连拒尊秦为帝；信陵君采侯嬴之计窃兵符，朱亥击杀晋鄙，夺魏军北上解邯郸之围。"),
    dict(id="101", chapter=101, map="m147", battle="鄗代之战", objective="击溃燕军并斩杀栗腹。", own=[("LianPo96", "廉颇"), ("YueCheng101", "乐乘")], enemy=("LiFu101", "栗腹"), outcome="death", theme="field", focus="秦灭东周迁九鼎，周室亡；燕王误判赵国长平后虚弱而兴兵，廉颇、乐乘分军反击，在鄗、代大败燕军。"),
    dict(id="102a", chapter=102, slice=(0.0, 0.58), map="m148", battle="华阴破秦", objective="联合五国越过华阴，击退蒙骜。", own=[("XinLingJun100", "信陵君"), ("PangNuan102", "庞煖")], enemy=("MengAo102", "蒙骜"), outcome="retreat", theme="mountain", focus="信陵君留赵多年后返魏，合五国兵败蒙骜于河外，追至函谷关；秦以反间使魏王疏远信陵君。"),
    dict(id="102b", chapter=102, slice=(0.42, 1.0), map="m149", battle="葫芦河之战", objective="诱燕军渡河，合围并击杀剧辛。", own=[("PangNuan102", "庞煖"), ("ZhaoDaoXiangWang102", "赵悼襄王")], enemy=("JuXin102", "剧辛"), outcome="death", theme="river", focus="燕将剧辛轻视故交庞煖，率军攻赵；庞煖在葫芦河设伏，待燕军半渡出击，剧辛兵败被斩。"),
    dict(id="103", chapter=103, map="m150", battle="咸阳讨逆", objective="击破叛军前锋，迫使樊於期出奔燕国。", own=[("QinWangZheng103", "秦王政"), ("WangJian103", "王翦")], enemy=("FanYuQi103", "樊於期"), outcome="retreat", theme="city", focus="楚相春申君黄歇遭李园伏杀；樊於期获罪秦廷，传檄讨秦失败后出奔燕国，成为荆轲刺秦计划的关键。"),
    dict(id="104", chapter=104, map="m151", battle="嫪毐之乱", objective="夺回咸阳宫门并生擒嫪毐。", own=[("QinWangZheng103", "秦王政"), ("ChangPingJun104", "昌平君")], enemy=("LaoAi104", "嫪毐"), outcome="capture", theme="palace", focus="甘罗十二岁出使赵国立功；嫪毐伪为宦者入宫，封长信侯后盗玺发兵作乱，秦王政调兵平叛。"),
    dict(id="105", chapter=105, map="m152", battle="肥下之战", objective="坚守营垒诱秦军深入，击退桓齮。", own=[("LiMu105", "李牧"), ("ZhaoCong105", "赵葱")], enemy=("HuanYi105", "桓齮"), outcome="retreat", theme="mountain", focus="茅焦冒死劝秦王迎回太后；李牧守边善用奇兵，在肥下设伏大破桓齮，保存赵国最后精锐。"),
    dict(id="106", chapter=106, map="m153", battle="井陉抗秦", objective="守住井陉关，迫使王翦暂退。", own=[("LiMu105", "李牧"), ("SiMaShang106", "司马尚")], enemy=("WangJian103", "王翦"), outcome="retreat", theme="mountain", focus="李牧、司马尚据险拒秦，王敖以反间令赵王疑将，李牧被杀；燕太子丹求刺客，田光刎颈荐荆轲。"),
    dict(id="107", chapter=107, map="m154", battle="城父败李信", objective="守住城父两营，击破李信前锋并迫其撤军。", own=[("XiangYan107", "项燕"), ("ChangPingJun104", "昌平君")], enemy=("LiXin107", "李信"), outcome="retreat", theme="forest", focus="荆轲持督亢图刺秦失败；秦王欲灭楚，李信轻兵深入，项燕尾追三日，在城父大破秦军，王翦随后受命。"),
    dict(id="108", chapter=108, map="m155", battle="六国归一", objective="攻破齐都临淄，生擒齐王建完成统一。", own=[("WangJian103", "王翦"), ("MengTian108", "蒙恬")], enemy=("QiWangJian108", "齐王建"), outcome="capture", theme="city", focus="王翦率六十万灭楚，项燕与昌平君战死；秦继而并燕、代、齐，秦王政统一六国，建立郡县称始皇帝。"),
]


EXISTING_HEROES = {
    "FuChai80", "GouJian79", "FanLi79", "WenZhong79", "WuYuan72", "BoPi75"
}

STRATEGISTS = {
    "ZhangMengTan84", "XiMenBao85", "ShangYang87", "SunBin88", "FanJu97",
    "MengChangJun94", "TianDan95", "ZhuHai100", "ChangPingJun104",
}

RULERS = {
    "LuMuGong86", "QinXiaoGong87", "QiXuanWang91", "QinHuiWenWang92",
    "YanZhaoWang95", "QiXiangWang95", "ZhaoDaoXiangWang102", "QinWangZheng103",
    "QiWangJian108", "SongKangWang94", "ZhongShanJun85",
}

HISTORICAL_DEATHS = {
    "ZhiBo84", "PangJuan88", "ZiZhi91", "ZhaoZhang93", "QiJie95",
    "ZhaoKuo98", "LiFu101", "JuXin102", "LaoAi104", "XiangYan107",
}

GENERIC_HEROES = [
    ("LateZhouGuardOwn", "Infantry", "infantry-1-red", "后期诸侯甲士", "战国后期各国主力步卒。", 25),
    ("LateZhouArcherOwn", "Archer", "archer-1-red", "后期诸侯弓弩手", "战国后期各国弓弩部队。", 33),
    ("LateZhouGuardEnemy", "Infantry", "infantry-1-blue", "敌军甲士", "本关敌军主力步卒。", 25),
    ("LateZhouArcherEnemy", "Archer", "archer-1-blue", "敌军弓弩手", "本关敌军弓弩部队。", 33),
]


def all_new_heroes() -> list[tuple[str, str, str, str, str, int]]:
    roles: dict[str, tuple[str, str, str]] = {}
    for spec in STAGES:
        for hero_id, label in spec["own"]:
            roles.setdefault(hero_id, (label, "red", spec["battle"]))
        hero_id, label = spec["enemy"]
        roles.setdefault(hero_id, (label, "blue", spec["battle"]))
    heroes = list(GENERIC_HEROES)
    for hero_id, (label, color, battle) in roles.items():
        if hero_id in EXISTING_HEROES:
            continue
        if hero_id in RULERS:
            klass, model, portrait = "Lord", f"lord-1-{color}", 7
        elif hero_id in STRATEGISTS:
            klass, model, portrait = "Strategist", f"Strategist-1-{color}", 49
        else:
            klass, model, portrait = "Cavalry", f"cavalry-1-{color}", 35
        bio = f"{label}，参与{battle}，其行动与结局依《东周列国志》本回叙事呈现。"
        heroes.append((hero_id, klass, model, label, bio, portrait))
    return heroes


STAGE_IDS = [spec["id"] for spec in STAGES]
MAP_IDS = [spec["map"] for spec in STAGES]
