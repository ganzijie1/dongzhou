from __future__ import annotations


STAGES = [
    dict(id="72a", chapter=72, slice=(0.0, 0.27), map="m156", battle="城父追骑", objective="击退武城黑追骑，护送伍员逃出楚境。", own=[("WuYuan72", "伍员")], enemy=("WuChengHei72", "武城黑"), outcome="retreat", theme="forest", focus="伍奢父子受诬，伍员识破诱召；武城黑率二百精卒追捕，伍员在旷野张弓射退追骑，自此踏上报仇之路。"),
    dict(id="73b", chapter=73, slice=(0.48, 1.0), map="m157", battle="鱼肠刺僚", objective="突破宴席卫士，让专诸接近吴王僚完成刺杀。", own=[("ZhuanZhu73", "专诸"), ("JiGuang73", "公子光")], enemy=("WuWangLiao73", "吴王僚"), outcome="death", theme="palace", focus="公子光伏甲设宴，专诸把鱼肠剑藏入炙鱼腹中，近席刺杀吴王僚；专诸亦死于王僚卫士，公子光遂立为吴王阖闾。"),
    dict(id="74", chapter=74, slice=(0.43, 1.0), map="m158", battle="江上刺庆忌", objective="击破庆忌亲卫，让要离在舟中完成刺杀。", own=[("YaoLi74", "要离")], enemy=("QingJi74", "庆忌"), outcome="death", theme="river", focus="要离断臂杀妻取信庆忌，随军乘舟伐吴；江风大作时以矛刺穿庆忌，庆忌敬其为天下勇士而放之，要离最终伏剑自尽。"),
    dict(id="75", chapter=75, sources=(75, 76), slice=(0.34, 1.0), map="m159", battle="柏举之战", objective="渡过汉水，击破囊瓦中军并迫其逃郑。", own=[("WuHelu79", "吴王阖闾"), ("WuYuan72", "伍员"), ("SunWu75", "孙武"), ("FuGai75", "夫概")], enemy=("NangWa75", "囊瓦"), outcome="retreat", theme="river", focus="孙武整军后联蔡、唐伐楚，夫概率五千锐卒突击楚军食阵；吴军五战五胜，囊瓦弃军逃郑，柏举门户由此洞开。"),
    dict(id="76", chapter=76, slice=(0.43, 1.0), map="m160", battle="郢都攻防", objective="突破郢都城门，迫使楚昭王西奔随国。", own=[("WuHelu79", "吴王阖闾"), ("WuYuan72", "伍员"), ("SunWu75", "孙武")], enemy=("ChuZhaoWang76", "楚昭王"), outcome="retreat", theme="city", focus="柏举败后沈尹戌回军救郢，力战身死；吴军攻入郢都，楚昭王奔云梦、转随国，伍员掘楚平王墓鞭尸报仇。"),
    dict(id="77", chapter=77, map="m161", battle="秦楚复郢", objective="会合楚军击破吴军前营，迫使夫概撤出楚境。", own=[("ShenBaoXu77", "申包胥"), ("ZiPu77", "子蒲")], enemy=("FuGai75", "夫概"), outcome="retreat", theme="mountain", focus="申包胥哭秦庭七日，秦哀公命子蒲、子虎率车五百乘救楚；秦楚联军击败夫概，吴国内外受敌，楚昭王得以返郢。"),
    dict(id="78b", chapter=78, slice=(0.46, 0.88), map="m162", battle="费邑攻宫", objective="守住鲁宫，击退公山不狃与叔孙辄叛军。", own=[("LuDingGong78", "鲁定公"), ("JiSunSi78", "季孙斯")], enemy=("GongShanBuNiu78", "公山不狃"), outcome="retreat", theme="city", focus="阳虎乱鲁平定后，公山不狃、叔孙辄又据费邑攻入国都；孔子调申句须、乐颀反击，叛军败走，继而推行堕三都。"),
    dict(id="82b", chapter=82, slice=(0.58, 1.0), map="m163", battle="子路结缨", objective="突入蒯氏府，击退叛军并逼近石乞。", own=[("ZiLu82", "子路")], enemy=("ShiQi82", "石乞"), outcome="attempt", theme="palace", focus="卫国内乱，蒯聩挟持孔悝夺位；子路不顾劝阻入城救主，与石乞等力战，冠缨被断后从容结缨，最终殉难。"),
    dict(id="83a", chapter=83, slice=(0.0, 0.48), map="m164", battle="叶公平楚", objective="夺回楚宫，击杀白公胜并平定叛军。", own=[("YeGong83", "叶公高")], enemy=("BaiGongSheng83", "白公胜"), outcome="death", theme="city", focus="白公胜因伐郑之议与楚廷决裂，发动宫变劫持惠王；叶公高率方城兵入郢，楚人响应，白公兵败自缢，楚国复定。"),
    dict(id="84b", chapter=84, slice=(0.62, 1.0), map="m165", battle="豫让击衣", objective="清除桥下护卫，让豫让接近赵襄子完成最后一击。", own=[("YuRang84", "豫让")], enemy=("ZhaoWuXu84", "赵襄子"), outcome="attempt", theme="forest", focus="豫让为智伯报仇，漆身吞炭两度行刺赵襄子；桥下伏击失败后，请得襄子衣袍连击三剑，遂伏剑而死。"),
    dict(id="86b", chapter=86, slice=(0.25, 0.58), map="m166", battle="西河攻秦", objective="突破秦军河西防线，夺取五城。", own=[("WuQi86", "吴起")], enemy=("QinXianGong86", "秦献公"), outcome="retreat", theme="mountain", focus="吴起离鲁入魏，任西河守，筑城练武卒；趁秦国内乱发兵攻取河西五城，使魏国西境由守转攻。"),
    dict(id="101a", chapter=101, slice=(0.0, 0.42), map="m167", battle="秦灭西周", objective="突破伊阙残军，迫使周赧王献出三十六城。", own=[("YingJiu101", "嬴樛"), ("ZhangTang101", "张唐")], enemy=("ZhouNanWang101", "周赧王"), outcome="capture", theme="city", focus="周赧王借债合纵攻秦，诸侯观望而散；秦军攻入西周，赧王捧舆图献三十六城，周宗庙九鼎由此迁秦。"),
    dict(id="107a", chapter=107, slice=(0.0, 0.62), map="m168", battle="荆轲刺秦", objective="突破咸阳殿卫，让荆轲持图穷匕首接近秦王。", own=[("JingKe107", "荆轲")], enemy=("QinWangZheng103", "秦王政"), outcome="attempt", theme="palace", focus="荆轲携樊於期首级与督亢地图入秦，图穷匕见，逐秦王绕柱；刺击不中，荆轲被创后倚柱笑骂，最终死于殿上。"),
    dict(id="108a", chapter=108, slice=(0.0, 0.66), map="m169", battle="王翦灭楚", objective="击破兰陵楚军，斩杀项燕并终结楚国。", own=[("WangJian103", "王翦"), ("MengWu108", "蒙武")], enemy=("XiangYan107", "项燕"), outcome="death", theme="city", focus="王翦率六十万坚壁蓄锐，骤击项燕，破寿春、渡江围兰陵；昌平君中箭而死，项燕自刎，秦军平定楚越。"),
]


EXISTING_HEROES = {
    "WuYuan72", "JiGuang73", "WuHelu79", "SunWu75", "FuGai75", "NangWa75",
    "LuDingGong78", "JiSunSi78", "GongShanBuNiu78", "ZhaoWuXu84", "WuQi86",
    "QinWangZheng103", "WangJian103", "XiangYan107",
}

STRATEGISTS = {"ShenBaoXu77"}
RULERS = {"WuWangLiao73", "ChuZhaoWang76", "QinXianGong86", "ZhouNanWang101"}
HISTORICAL_DEATHS = {"WuWangLiao73", "ZhuanZhu73", "QingJi74", "YaoLi74", "ZiLu82", "BaiGongSheng83", "YuRang84", "JingKe107", "XiangYan107"}


def all_new_heroes() -> list[tuple[str, str, str, str, str, int]]:
    roles: dict[str, tuple[str, str, str]] = {}
    for spec in STAGES:
        for hero_id, label in spec["own"]:
            roles.setdefault(hero_id, (label, "red", spec["battle"]))
        hero_id, label = spec["enemy"]
        roles.setdefault(hero_id, (label, "blue", spec["battle"]))
    heroes = []
    for hero_id, (label, color, battle) in roles.items():
        if hero_id in EXISTING_HEROES:
            continue
        if hero_id in RULERS:
            klass, model, portrait = "Lord", f"lord-1-{color}", 7
        elif hero_id in STRATEGISTS:
            klass, model, portrait = "Strategist", f"Strategist-1-{color}", 49
        else:
            klass, model, portrait = "Cavalry", f"cavalry-1-{color}", 35
        bio = f"{label}，参与{battle}；本关行动与结局依《东周列国志》原文呈现。"
        heroes.append((hero_id, klass, model, label, bio, portrait))
    return heroes


STAGE_IDS = [spec["id"] for spec in STAGES]
MAP_IDS = [spec["map"] for spec in STAGES]
