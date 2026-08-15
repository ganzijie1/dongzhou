from __future__ import annotations

import json
from pathlib import Path

import integrate_chapter60 as shared


ROOT = Path(__file__).resolve().parents[1]
STAGE_IDS = ["71", "72", "73", "75", "78", "79", "80"]


HEROES = [
    ("TianKaiJiang71", "Cavalry", "cavalry-1-red", "田开疆", "齐景公勇士，奉命伐徐，在蒲隧阵斩徐将嬴爽；后因二桃之谋与公孙捷、古冶子一同自尽。"),
    ("GuYeZi71", "Infantry", "infantry-1-red", "古冶子", "齐景公勇士，曾在黄河斩鼋救主。随田开疆伐徐，后来卷入二桃杀三士之局。"),
    ("YingShuang71", "Cavalry", "cavalry-1-blue", "嬴爽", "徐国大将，蒲隧迎战齐军，被田开疆斩杀。"),
    ("XuJun71", "Lord", "lord-1-blue", "徐君", "徐国国君，齐军兵临蒲隧后遣使请降。"),
    ("QiGuard71", "Infantry", "infantry-1-red", "齐国甲士", "齐国征徐步卒。"),
    ("QiArcher71", "Archer", "archer-1-red", "齐国弓手", "齐国征徐弓手。"),
    ("XuGuard71", "Infantry", "infantry-1-blue", "徐国甲士", "徐国蒲隧守军。"),
    ("XuArcher71", "Archer", "archer-1-blue", "徐国弓手", "徐国蒲隧守军。"),
    ("WuYuan72", "Strategist", "Strategist-1-red", "伍员", "字子胥，楚臣伍奢之子。父兄被害后逃楚入吴，辅佐阖闾破楚，后谏夫差不纳而死。"),
    ("GongZiSheng72", "Cavalry", "cavalry-1-red", "公子胜", "楚太子建之子，随伍员出逃，后被送往郑国。"),
    ("HuangFuNe72", "Strategist", "Strategist-1-red", "皇甫讷", "东皋公友人，与伍员相貌相似，在昭关以换衣调包之计引开守军。"),
    ("ZhaoGuanCaptain72", "Infantry", "infantry-1-blue", "昭关守将", "奉画像盘查伍员的楚军关将。"),
    ("ZhaoGuard72", "Infantry", "infantry-1-blue", "昭关甲士", "封锁昭关的楚军。"),
    ("ZhaoArcher72", "Archer", "archer-1-blue", "昭关弓手", "驻守关墙的楚军弓手。"),
    ("JiGuang73", "Lord", "lord-1-red", "公子光", "吴王诸樊之子，率军在鸡父击破楚国诸侯联军，后使专诸刺王僚，自立为吴王阖闾。"),
    ("GongZiGai73", "Cavalry", "cavalry-1-red", "公子盖余", "吴国公子，鸡父之战率军分击胡、沈两国。"),
    ("XiaNie73", "Cavalry", "cavalry-1-blue", "夏啮", "楚国将领，鸡父之战率陈军先战，被公子光击杀。"),
    ("WeiYue73", "Cavalry", "cavalry-1-blue", "魏越", "楚国将领，鸡父之战后军溃败，自度不能免罪而死。"),
    ("HuGong73", "Lord", "lord-1-blue", "胡国君", "随楚军攻吴，在鸡父兵败被吴军俘获。"),
    ("ShenGong73", "Lord", "lord-1-blue", "沈国君", "随楚军攻吴，在鸡父兵败被吴军俘获。"),
    ("WuGuard73", "Infantry", "infantry-1-red", "吴军锐士", "吴国鸡父之战步卒。"),
    ("WuArcher73", "Archer", "archer-1-red", "吴军弓手", "吴国鸡父之战弓手。"),
    ("CoalitionGuard73", "Infantry", "infantry-1-blue", "楚属联军", "楚与陈、胡、沈等国联军。"),
    ("CoalitionArcher73", "Archer", "archer-1-blue", "楚属弓手", "楚与属国联军弓手。"),
    ("WuHelu79", "King", "lord-1-red", "吴王阖闾", "吴王诸樊之子公子光。任用伍员、孙武强吴，柏举破楚；后伐越在携李负伤而死。"),
    ("SunWu75", "Strategist", "Strategist-1-red", "孙武", "兵家孙武，著《孙子兵法》。辅佐吴王阖闾整军，在柏举之战以奇正相生大破楚军。"),
    ("FuGai75", "Cavalry", "cavalry-1-red", "夫概", "吴王阖闾之弟，柏举之战力主先击楚军，率部突阵取胜，后曾自立为王。"),
    ("BoPi75", "Strategist", "Strategist-1-red", "伯嚭", "楚臣伯州犁之后，奔吴受伍员举荐。参与破楚，后为吴太宰。"),
    ("NangWa75", "Strategist", "Strategist-1-blue", "囊瓦", "楚令尹子常，贪赂失诸侯，柏举统军屡败，弃军逃郑。"),
    ("ShenYinShu75", "Cavalry", "cavalry-1-blue", "沈尹戌", "楚国贤将，反对囊瓦速战。柏举败后回军救郢，力战重伤，自命部下取首复命。"),
    ("TangHou75", "Lord", "lord-1-blue", "唐成公", "唐国国君，受囊瓦勒索后导吴伐楚；秦兵救楚时战败身亡。"),
    ("ChuGuard75", "Infantry", "infantry-1-blue", "楚军甲士", "柏举战场楚军。"),
    ("ChuArcher75", "Archer", "archer-1-blue", "楚军弓手", "柏举战场楚军。"),
    ("QinRelief75", "Cavalry", "cavalry-1-blue", "秦国援军", "申包胥哭秦庭后赶到楚国的秦军。"),
    ("LuDingGong78", "Lord", "lord-1-red", "鲁定公", "鲁国国君，夹谷会盟时由孔子摄相事，后经历阳虎、公山不狃等国内叛乱。"),
    ("JiSunSi78", "Strategist", "Strategist-1-red", "季孙斯", "鲁国季氏宗主，阳虎专政时受制，后与鲁君合力平叛。"),
    ("YangHu78", "Cavalry", "cavalry-1-blue", "阳虎", "鲁国季氏家臣，专权后发动叛乱，兵败逃亡齐、晋。"),
    ("YangYue78", "Cavalry", "cavalry-1-blue", "阳越", "阳虎同党，攻鲁南门时中箭身亡。"),
    ("GongShanBuNiu78", "Infantry", "infantry-1-blue", "公山不狃", "季氏费邑宰，后来联合叔孙辄攻鲁宫，兵败逃齐。"),
    ("ShuSunZhe78", "Strategist", "Strategist-1-blue", "叔孙辄", "鲁国叔孙氏成员，与公山不狃起兵攻宫，失败后出奔。"),
    ("LuGuard78", "Infantry", "infantry-1-red", "鲁宫甲士", "保卫鲁君的甲士。"),
    ("LuRebel78", "Infantry", "infantry-1-blue", "鲁国叛军", "阳虎及公山不狃部众。"),
    ("LuRebelArcher78", "Archer", "archer-1-blue", "叛军弓手", "鲁国内乱中的弓手。"),
    ("GouJian79", "King", "lord-1-red", "越王勾践", "越王允常之子。携李破吴，后夫椒败而臣吴，归国卧薪尝胆，最终灭吴称霸。"),
    ("LingGuFu79", "Cavalry", "cavalry-1-red", "灵姑浮", "越国勇将，携李之战以戈击伤吴王阖闾足趾。"),
    ("FanLi79", "Strategist", "Strategist-1-red", "范蠡", "越国谋臣，辅佐勾践忍辱图强、灭吴复国；功成后泛舟五湖。"),
    ("WenZhong79", "Strategist", "Strategist-1-red", "文种", "越国大夫，夫椒败后赴吴议和，主持越国政务并助勾践复国。"),
    ("WuZiXu79", "Strategist", "Strategist-1-blue", "伍子胥", "伍员入吴后的称号。辅吴破楚，力谏夫差灭越，最终被赐剑自尽。"),
    ("ZhuanYi79", "Cavalry", "cavalry-1-blue", "专毅", "吴国将领，携李护卫阖闾，负伤后不久身亡。"),
    ("FuChai80", "King", "lord-1-blue", "吴王夫差", "阖闾之子。夫椒大败越军并受勾践臣服，后北上争霸，最终被越国所灭。"),
    ("YueGuard79", "Infantry", "infantry-1-red", "越国甲士", "越军步卒。"),
    ("YueArcher79", "Archer", "archer-1-red", "越国弓手", "越军弓手。"),
    ("WuGuard79", "Infantry", "infantry-1-blue", "吴国甲士", "吴军步卒。"),
    ("WuArcher79", "Archer", "archer-1-blue", "吴国弓手", "吴军弓手。"),
]


def intro71(): return [
    ("", "齐景公欲伐徐国，以田开疆、古冶子为将，率军推进蒲隧。徐军依河与西城列阵。"),
    ("田开疆", "徐将嬴爽已在河东挑战。我先破其前阵，诸军再越浅水逼近徐城。"),
    ("古冶子", "深水不可过，浅河可以通行。弓手压住城头，步卒沿两处滩口并进。"),
    ("嬴爽", "齐军远来，粮道绵长。谁敢越蒲隧一步，我便取谁首级！"),
    ("军令", "击破蒲隧守军。田开疆与嬴爽相邻可触发史实单挑并直接斩杀；两名我方将领被击退则失败。"),
]


def victory71(): return [
    ("", "田开疆临阵斩嬴爽，徐军失去先锋。齐军渡过蒲隧，徐君遣使献地请降。"),
    ("徐君", "徐国愿奉齐国为盟主，岁时纳贡，只求保全宗庙百姓。"),
    ("", "田开疆班师后与公孙捷、古冶子同受齐景公宠信。三人勇力过人，却不知礼数，晏婴深以为忧。"),
    ("晏婴", "三勇士功高而不知君臣之礼，一旦为乱，无人能制。可赐二桃，令三人各叙功劳，自取其桃。"),
    ("", "公孙捷、田开疆先取二桃。古冶子叙说黄河斩鼋救主之功，两人羞惭自刎；古冶子也因独生无义而自尽。"),
    ("齐景公", "寡人只想抑制三士，岂料三人皆死。厚葬他们，以全旧日君臣之情。"),
    ("", "楚平王听信费无极，为太子建聘秦女孟嬴。费无极见孟嬴绝色，竟劝平王自娶，以陪嫁齐女冒充太子妃。"),
    ("伍奢", "夺子之妻、废嫡之母，乱伦败国。费无极只求自固，必将太子逼反。"),
    ("", "楚平王囚伍奢，召其二子伍尚、伍员入郢。伍尚决意赴死，伍员识破诱杀，带太子建之子公子胜出逃。"),
    ("军令", "蒲隧之战完成，获得1600金币。下一关：昭关脱逃。"),
]


def intro72(): return [
    ("", "伍奢与伍尚在郢都被杀，太子建先逃宋国，后因宋国内乱转入郑国。晋人令太子建为内应，太子建谋泄被郑定公处死。"),
    ("伍员", "父兄与太子皆死，公子胜是伍氏和太子唯一血脉。我必须带他穿过昭关，东投吴国。"),
    ("", "楚国沿途悬挂伍员画像。伍员困在东皋公家中七日，一夜须发尽白。东皋公请来相貌相似的皇甫讷。"),
    ("黄甫讷", "我穿你的衣服先过关，引守军追赶。你换上我的衣冠、白发遮面，趁乱带公子胜通过。"),
    ("公子胜", "关外还有大江。只要到了吴境，父仇与伍氏之仇终有报答之日。"),
    ("军令", "护送伍员与公子胜穿过双格关门并抵达北方出口。不要恋战；任一人被击退则失败。"),
]


def victory72(): return [
    ("", "皇甫讷故意露形奔走，关吏追错了人。伍员白发换装，带公子胜从另一列车马中通过昭关。"),
    ("伍员", "昭关已过，前面却是长江。楚军追骑将至，若没有舟楫仍难脱身。"),
    ("", "一名渔父驾小舟接伍员渡江，又拒绝百金宝剑。为断绝伍员疑心，渔父覆舟自沉。"),
    ("", "伍员一路乞食吹箫来到吴市。公子光听说楚国逃臣有大才，遣人暗中相访。"),
    ("公子光", "楚平王与囊瓦乱政，吴国正可西向。先生若能为我筹吴国之事，我也愿助先生报父兄之仇。"),
    ("军令", "昭关脱逃完成，获得1400金币。下一关：鸡父之战。"),
]


def intro73(): return [
    ("", "楚国率陈、蔡、胡、沈、顿、许等国攻吴。吴王僚命公子光迎战鸡父，伍员献疲兵分击之策。"),
    ("公子光", "楚属七国号令不一。先用三千罪卒冲阵扰乱其前军，再分兵击胡、沈，最后合攻楚军。"),
    ("公子盖余", "我从北路包抄胡、沈两君。主军击夏啮时，我部不必恋战，只要断其归路。"),
    ("夏啮", "吴军以罪人当先，不过乌合之众。陈军先击破他们，诸国随后推进！"),
    ("魏越", "诸军营垒分散，若陈军先败，后军恐怕各自奔逃。"),
    ("军令", "先击退夏啮及陈军前锋，随后合围胡、沈两君并击破魏越。两名吴军主将被击退则失败。"),
]


def victory73(): return [
    ("", "三千罪卒反复冲击，陈军阵形散乱。公子光乘势斩夏啮，吴军两翼又擒胡、沈两君。"),
    ("", "许、蔡、顿军见两君被俘，各自逃散。魏越收兵不及，自知回楚必获罪，最终自尽。"),
    ("伍员", "鸡父一胜，楚东境门户已开。但大王若仍在，公子光终究不能专行伐楚大计。"),
    ("", "伍员向公子光推荐勇士专诸。专诸把匕首藏入炙鱼腹中，在宴席刺杀吴王僚，自己也被卫士杀死。"),
    ("公子光", "专诸以身成事，其子当世袭卿位。自今日起我即吴王阖闾，任伍员、孙武整军，准备西破强楚。"),
    ("", "王僚之子庆忌逃到艾城聚众。要离断臂杀妻以取信庆忌，最终在舟中刺死庆忌，自己亦伏剑而死。"),
    ("军令", "鸡父之战完成，获得1800金币。下一关：柏举之战。"),
]


def intro75(): return [
    ("", "第七十四回中，囊瓦畏谤诛杀费无极与鄢将师，楚国却未能因此复振。蔡昭侯受囊瓦索裘，唐成公又被索马，蔡、唐遂决意导吴伐楚。"),
    ("", "吴王阖闾任孙武为将、伍员为谋，夫概与伯嚭统军，水陆三万沿淮而上。蔡、唐军在汉东会合。"),
    ("孙武", "楚军二十万而令不一。先弃舟登陆，使其不能料我进退；渡汉水后沿小别、大别山疾行，直取柏举。"),
    ("伍员", "囊瓦贪而无谋，沈尹戌却是强敌。他若先毁吴舟再夹击，我军便危险，必须在两军会合前速破囊瓦。"),
    ("夫概", "楚军阵脚已动。虽未得王命，我愿率本部五千先击其卒食之时；若一战破阵，全军随后压上。"),
    ("囊瓦", "吴军远来，利在速战。若让沈尹戌独得破敌之功，我还有何面目执掌楚政？立即渡汉列阵！"),
    ("沈尹戌", "不可！我军应坚守汉水，我率方城军毁其舟楫，再从背后夹击。子常若贪功先战，必败。"),
    ("军令", "本关合并第75至77回。第一阶段击破柏举楚中军；第二阶段追击至郢都；第三阶段抵御申包胥请来的秦援军并安全撤出。"),
]


def victory75(): return [
    ("", "夫概五千人突击楚军食阵，阖闾见前军得手，下令全军渡汉。楚军五战五败，囊瓦弃军逃郑。"),
    ("", "沈尹戌回军救郢，在雍澨三度击破吴军，终因伤重被围。他命吴句卑取下自己的首级，免遭吴军侮辱。"),
    ("", "吴军攻入郢都，楚昭王先奔云梦，又转随国。伍员掘开楚平王墓，鞭尸三百，以报父兄之仇。"),
    ("申包胥", "子能覆楚，我必能复楚。我要到秦庭痛哭，哪怕七日不饮不食，也要请来救兵。"),
    ("", "申包胥哭秦庭七日，秦哀公终于发兵。秦楚联军在稷地击败夫概，唐成公战死，吴军腹背受敌。"),
    ("", "越军趁机攻吴，夫概又先归国自立。阖闾不得不撤出楚境，楚昭王返回郢都。"),
    ("", "楚昭王赏赐复国诸臣，申包胥却辞赏隐居。伍员与申包胥虽各为其主，仍彼此敬重。"),
    ("", "这一场大战贯穿汉水、柏举、郢都与秦援反击。吴国虽破楚都，却没能灭楚，楚国也从此元气大伤。"),
    ("军令", "柏举大战完成，获得3200金币。下一关：鲁国平叛。"),
]


def intro78(): return [
    ("", "孔子摄相事随鲁定公会齐于夹谷，以礼制止齐国莱人劫盟，又迫齐归还侵鲁土地。齐国转而以女乐离间鲁政。"),
    ("", "鲁国先有阳虎专权。阳虎挟持季孙斯失败，遂集结叛军攻向国都南门，企图控制鲁君与三桓。"),
    ("鲁定公", "城墙不可跨越，叛军只能从南门进入。宫军守住门内街道，不能让阳虎接近王宫。"),
    ("季孙斯", "阳虎熟知鲁都门户，必会分兵冲击。先击退阳越与前锋，再围攻阳虎。"),
    ("阳虎", "季氏多年把持鲁政，我今日夺其家兵，另立国政。破南门，直取宫府！"),
    ("军令", "第一阶段击破阳虎军；第二阶段公山不狃、叔孙辄攻宫。鲁定公与季孙斯任一被击退则失败。"),
]


def victory78(): return [
    ("", "阳越在南门中箭身亡，阳虎军溃败。阳虎先奔齐，后投晋国赵氏。"),
    ("", "数年后公山不狃与叔孙辄又据费邑起兵，直攻鲁宫。孔子指挥申句须、乐颀反击，叛军再败。"),
    ("公山不狃", "鲁国终究不容我等。叔孙辄向齐境退，我自往吴国求存。"),
    ("", "孔子建议堕毁三都，以削弱家臣叛乱根基。叔孙、季孙先后响应，孟孙氏却暗中阻止成邑被毁。"),
    ("", "齐国送来女乐与良马，鲁定公、季桓子沉迷观赏，多日不朝。孔子失望离鲁，开始周游列国。"),
    ("军令", "鲁国平叛完成，获得1900金币。下一关：携李之战。"),
]


def intro79(): return [
    ("", "越王允常去世，勾践即位。吴王阖闾乘丧伐越，伍员虽谏丧国不宜轻敌，吴军仍进至携李。"),
    ("勾践", "吴军强盛，正面久战不利。先以敢死队三次冲击，扰乱其心，再由全军从河湾反击。"),
    ("范蠡", "吴军主力在东北林地，阖闾居中。灵姑浮若能突入王旗，可迫吴军全线撤退。"),
    ("灵姑浮", "我只认吴王大纛。若能以戈伤他，越国今日便可保全。"),
    ("伍子胥", "越兵阵前自刎，是要乱我军心。大王不可前出，应保持阵形等待其气衰。"),
    ("军令", "击破吴军前锋，使灵姑浮接近阖闾触发史实负伤撤退。勾践、范蠡、灵姑浮任一被击退则失败。"),
]


def victory79(): return [
    ("", "越国敢死队在阵前自刎，吴军惊愕。越军乘势冲锋，灵姑浮以戈击中阖闾足趾。"),
    ("吴王阖闾", "我伤势难支，立即退兵。夫差务必记住，是越王勾践使我至此！"),
    ("", "吴军退至陉地，阖闾伤重去世，专毅也因护主负伤而亡。夫差即位，日夜命人提醒父仇。"),
    ("吴王夫差", "三年之内若不能报越，我何以立于吴国！伍员整军，伯嚭治粮，准备再战。"),
    ("军令", "携李之战完成，获得2100金币。下一关：夫椒会稽。"),
]


def intro80(): return [
    ("", "夫差整军三年，在夫椒大败越军。勾践仅余五千甲士，退守会稽山城。"),
    ("勾践", "今日不是争胜之时。范蠡护军沿浅水撤向会稽，文种设法向吴国求和。"),
    ("范蠡", "河中深水不可过。穿过西门进入会稽后据山坚守，等文种说服伯嚭。"),
    ("文种", "吴太宰伯嚭贪财，可以重赂；夫差想北上争霸，也未必愿在山中消耗兵力。"),
    ("伍子胥", "越王困兽犹斗，此时不灭，日后必为吴患。大王万不可因小利释勾践！"),
    ("吴王夫差", "越国愿为臣妾，勾践又亲入吴服役。只要他确有诚意，寡人可以留其宗祀。"),
    ("军令", "护送勾践、范蠡、文种进入会稽城池并守到第十二回合。任一具名将领被击退则失败。"),
]


def victory80(): return [
    ("", "文种重赂伯嚭，夫差接受越国请降。勾践入吴为臣，亲自尝粪问疾，终于骗得夫差信任。"),
    ("伍子胥", "飞鸟在青云之上，尚有矰缴之忧；潜鱼在深渊之下，尚有钓网之患。越王不可放归！"),
    ("", "夫差不听，三年后放勾践归越。勾践卧薪尝胆，与百姓同劳，范蠡练兵，文种治国。"),
    ("勾践", "越国今日不与吴争锋。十年生聚、十年教训，待吴国北上空虚，再报会稽之耻。"),
    ("", "孔子周游至卫、曹、宋、陈、蔡之间，屡遭困厄；与此同时，吴越两国的兴亡也进入新的阶段。"),
    ("军令", "夫椒会稽完成，获得2200金币。第八十回结束。"),
]


def lua_units(items):
    groups = {}
    for hero, force, pos in items:
        groups.setdefault((hero, force), []).append(pos)
    lines = []
    for (hero, force), positions in groups.items():
        if len(positions) == 1:
            lines.append(f'game:generate_unit("{hero}",1,Enum.force.{force},{{{positions[0][0]},{positions[0][1]}}})')
        else:
            points = ",".join("{%d,%d}" % tuple(pos) for pos in positions)
            lines.append(f'many(game,"{hero}",{{{points}}},Enum.force.{force})')
    return ";".join(lines)


def stage(stage_id, title, chapter, battle_title, objective, map_id, suffix, commanders, deploy, intro, victory,
          units, update, end_condition, turn_limit, money, events=(), sites="{}", duels="{}"):
    data = json.loads((ROOT / f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").read_text(encoding="utf-8"))
    head = shared.stage_head(stage_id, title, chapter, battle_title, objective, f"{map_id}.png", intro, list(events), victory,
                             "具名我军将领被击退，或未能完成关卡目标，本关失败。", commanders, sites)
    if duels != "{}":
        head = head.replace("gduel_enabled=false\ngduels={}", f"gduel_enabled=true\ngduels={duels}")
    terrain = shared.terrain_block(data)
    deploy_rows = ",".join(f'{{position={{{x},{y}}},hero="{hero}"}}' for hero, x, y in deploy)
    return head + f'''local phase=1
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
{lua_units(units)}
end
function on_update(game)
{update}
end
function on_victory(game)end function on_defeat(game)end
function end_condition(game)
 {end_condition}
end
gstage={{title_id="Dongzhou{stage_id}",turn_limit={turn_limit},map={{blocked_edges={{}},size={{{data['grid'][0]},{data['grid'][1]}}},terrain={{
{terrain}
}},file="map.bmp"}},deploy={{unselectables={{{deploy_rows}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money={money}}}}}
'''


def build_stages():
    stages = {}
    stages["71"] = stage("71", "晏平仲二桃杀三士 楚平王娶媳逐世子", "第七十一回", "蒲隧之战",
        "田开疆斩嬴爽，击破徐军并迫使徐君请降。", "m120", "ch71", ["TianKaiJiang71", "GuYeZi71"],
        [("TianKaiJiang71",7,29),("GuYeZi71",10,31)], intro71(), victory71(),
        [("YingShuang71","enemy",[28,17]),("XuJun71","enemy",[43,14])], "",
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if game:get_num_enemies_alive()==0 then return Enum.status.victory end return Enum.status.undecided', 24, 16000,
        [("田开疆","嬴爽已经出阵。斩将后直取徐城！")],
        '{{id="xu_castle",name="徐城",position={43,14},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}}}',
        '{{attacker="TianKaiJiang71",defender="YingShuang71",exp=90,outcome="kill",attacker_speech="嬴爽，蒲隧便是你的葬身之地！",defender_speech="田开疆休得夸口！",result_speech="田开疆突入徐阵，斩杀嬴爽！",text="田开疆阵斩嬴爽。"}}')
    # Add rank-and-file after constructing the compact historical core.
    stages["71"] = stages["71"].replace('game:generate_unit("XuJun71",1,Enum.force.enemy,{43,14})',
        'game:generate_unit("XuJun71",1,Enum.force.enemy,{43,14});many(game,"QiGuard71",{{5,27},{8,33},{12,28},{13,34}},Enum.force.own);many(game,"QiArcher71",{{4,31},{11,31}},Enum.force.own);many(game,"XuGuard71",{{25,15},{26,19},{34,14},{35,18},{39,11},{39,20}},Enum.force.enemy);many(game,"XuArcher71",{{29,13},{31,21},{42,9},{46,18}},Enum.force.enemy)')
    stages["72"] = stage("72", "棠公尚捐躯奔父难 伍子胥微服过昭关", "第七十二回", "昭关脱逃",
        "护送伍员、公子胜穿过昭关并抵达北方出口。", "m121", "ch72", ["WuYuan72","GongZiSheng72"],
        [("WuYuan72",31,32),("GongZiSheng72",34,32)], intro72(), victory72(),
        [("HuangFuNe72","ally",[25,20]),("ZhaoGuanCaptain72","enemy",[31,13]),("ZhaoGuard72","enemy",[27,13]),("ZhaoGuard72","enemy",[36,13]),("ZhaoArcher72","enemy",[23,14]),("ZhaoArcher72","enemy",[41,14])],
        'if phase==1 and game:is_unit_within("WuYuan72",{31,15},2)then phase=2;game:push_cmd_speak(0,"皇甫讷已引走关吏，伍员白发换装，立即穿关！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if game:is_unit_within("WuYuan72",{32,1},1)and game:is_unit_within("GongZiSheng72",{32,1},2)then return Enum.status.victory end return Enum.status.undecided', 26, 14000,
        [("皇甫讷","我先引开守军，伍员趁乱从双格关门通过。")],
        '{{id="zhao_post",name="昭关驿舍",position={44,8},restore_hp=20,restore_mp=15,rewards={{item="spirit_powder",amount=1}}}}')
    stages["73"] = stage("73", "伍员吹箫乞吴市 专诸进炙刺王僚", "第七十三回", "鸡父之战",
        "击破夏啮前锋，再合围胡、沈两君与魏越。", "m122", "ch73", ["JiGuang73","GongZiGai73"],
        [("JiGuang73",8,21),("GongZiGai73",10,24)], intro73(), victory73(),
        [("XiaNie73","enemy",[48,13]),("WeiYue73","enemy",[57,31]),("HuGong73","enemy",[58,11]),("ShenGong73","enemy",[57,33])]
        + [("WuGuard73","own",p) for p in ([5,18],[6,24],[10,18],[11,27],[14,21],[15,25])]
        + [("WuArcher73","own",p) for p in ([4,21],[9,29],[16,18])]
        + [("CoalitionGuard73","enemy",p) for p in ([43,11],[46,16],[50,10],[52,15],[53,28],[55,35],[61,27],[62,34],[60,8],[63,13])]
        + [("CoalitionArcher73","enemy",p) for p in ([45,9],[50,18],[54,30],[61,32],[63,10])],
        'if phase==1 and not game:has_unit("XiaNie73")then phase=2;game:push_cmd_speak(0,"夏啮已死，陈军前锋崩溃！公子盖余从北路合围胡、沈两军！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if not game:has_unit("XiaNie73")and not game:has_unit("WeiYue73")and not game:has_unit("HuGong73")and not game:has_unit("ShenGong73")then return Enum.status.victory end return Enum.status.undecided', 30, 18000,
        [("公子光","罪卒扰乱前军后，全军分击诸侯营垒。")],
        '{{id="wu_north_camp",name="吴军北营",position={12,11},restore_hp=20,restore_mp=10,rewards={}},{id="wu_south_camp",name="吴军南营",position={14,33},restore_hp=20,restore_mp=10,rewards={}},{id="hu_camp",name="胡军大营",position={58,11},restore_hp=20,restore_mp=10,rewards={}},{id="shen_camp",name="沈军大营",position={57,33},restore_hp=20,restore_mp=10,rewards={}}}')
    stages["75"] = stage("75", "孙武子演阵斩美姬 申包胥哭秦庭复楚", "第七十五至七十七回", "柏举大战",
        "依次击破柏举楚军、攻入郢都，再抵御秦楚援军并撤出战场。", "m123", "ch75_77", ["WuHelu79","WuYuan72","SunWu75","FuGai75","BoPi75"],
        [("WuHelu79",83,29),("WuYuan72",82,33),("SunWu75",86,31),("FuGai75",80,36),("BoPi75",86,35)], intro75(), victory75(),
        [("NangWa75","enemy",[60,30]),("ShenYinShu75","enemy",[56,37]),("TangHou75","ally",[70,12])]
        + [("WuGuard73","own",p) for p in ([78,25],[80,28],[81,32],[78,39],[85,25],[88,29],[88,37],[84,40])]
        + [("WuArcher73","own",p) for p in ([77,31],[82,24],[89,33],[81,41])]
        + [("ChuGuard75","enemy",p) for p in ([64,25],[66,28],[63,32],[65,36],[58,27],[58,34],[53,25],[52,39],[56,30],[47,36])]
        + [("ChuArcher75","enemy",p) for p in ([62,23],[68,32],[60,39],[54,29],[59,34])],
        'if phase==1 and not game:has_unit("NangWa75")and not game:has_unit("ShenYinShu75")then phase=2;many(game,"ChuGuard75",{{31,45},{31,49},{28,42},{27,54},{21,38},{18,57}},Enum.force.enemy);many(game,"ChuArcher75",{{32,43},{32,53},{24,41},{21,56}},Enum.force.enemy);game:push_cmd_speak(0,"柏举楚军已溃，囊瓦逃郑、沈尹戌战死。全军西进郢都！")elseif phase==2 and game:get_num_enemies_alive()==0 then phase=3;many(game,"QinRelief75",{{68,48},{72,45},{76,48},{80,51},{84,48},{74,54},{79,57},{85,55}},Enum.force.enemy);many(game,"ChuGuard75",{{65,52},{69,56},{82,45},{87,49}},Enum.force.enemy);game:push_cmd_speak(0,"申包胥哭秦庭七日，秦楚援军从稷地杀来！击退援军后沿东北道路撤离！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==3 and game:get_num_enemies_alive()==0 and game:is_unit_within("WuHelu79",{88,8},5)then return Enum.status.victory end return Enum.status.undecided', 48, 32000,
        [("孙武","先破囊瓦，再入郢都；秦援到来后不可恋战。"),("申包胥","秦兵已至，楚国尚有复国之望！")],
        '{{id="ying_palace",name="郢都王宫",position={15,48},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=2}}},{id="tang_camp",name="唐军营寨",position={70,12},restore_hp=20,restore_mp=10,rewards={}},{id="junxiang",name="军祥营地",position={74,50},restore_hp=20,restore_mp=10,rewards={}}}')
    stages["78"] = stage("78", "会夹谷孔子却齐 堕三都闻人伏法", "第七十八回", "鲁国平叛",
        "先击破阳虎军，再守卫鲁宫击退公山不狃与叔孙辄。", "m124", "ch78", ["LuDingGong78","JiSunSi78"],
        [("LuDingGong78",29,11),("JiSunSi78",22,17)], intro78(), victory78(),
        [("YangHu78","enemy",[28,37]),("YangYue78","enemy",[34,35])]
        + [("LuGuard78","own",p) for p in ([25,15],[32,15],[20,20],[38,20],[25,27],[32,27])]
        + [("LuRebel78","enemy",p) for p in ([23,36],[26,38],[31,38],[37,36],[21,39],[40,39])]
        + [("LuRebelArcher78","enemy",p) for p in ([24,40],[35,40],[20,35],[39,35])],
        'if phase==1 and not game:has_unit("YangHu78")and not game:has_unit("YangYue78")then phase=2;game:generate_unit("GongShanBuNiu78",1,Enum.force.enemy,{28,34});game:generate_unit("ShuSunZhe78",1,Enum.force.enemy,{29,34});many(game,"LuRebel78",{{18,31},{22,33},{35,33},{40,30}},Enum.force.enemy);many(game,"LuRebelArcher78",{{16,28},{42,28}},Enum.force.enemy);game:push_cmd_speak(0,"阳虎败逃后，公山不狃、叔孙辄又从费邑攻入南门！守住鲁宫！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("GongShanBuNiu78")and not game:has_unit("ShuSunZhe78")then return Enum.status.victory end return Enum.status.undecided', 32, 19000,
        [("鲁定公","南门是唯一通路，宫军依街巷迎击。")],
        '{{id="lu_palace",name="鲁国宫府",position={29,11},restore_hp=25,restore_mp=15,rewards={{item="spirit_powder",amount=1}}},{id="jishi_manor",name="季氏府",position={20,22},restore_hp=20,restore_mp=10,rewards={}},{id="shusun_manor",name="叔孙氏府",position={38,22},restore_hp=20,restore_mp=10,rewards={}}}')
    stages["79"] = stage("79", "归女乐黎弥阻孔子 栖会稽文种通宰嚭", "第七十九回", "携李之战",
        "击破吴军前锋，灵姑浮接近阖闾触发负伤撤退。", "m125", "ch79", ["GouJian79","LingGuFu79","FanLi79"],
        [("GouJian79",9,29),("LingGuFu79",14,26),("FanLi79",11,33)], intro79(), victory79(),
        [("WuHelu79","enemy",[51,11]),("WuZiXu79","enemy",[46,15]),("ZhuanYi79","enemy",[42,18])]
        + [("YueGuard79","own",p) for p in ([6,25],[8,32],[12,24],[15,31],[18,28])]
        + [("YueArcher79","own",p) for p in ([5,29],[12,35],[17,24])]
        + [("WuGuard79","enemy",p) for p in ([38,16],[41,12],[44,9],[47,11],[48,18],[52,16],[55,13],[57,9])]
        + [("WuArcher79","enemy",p) for p in ([40,9],[44,19],[50,8],[55,17])],
        'if phase==1 and game:is_unit_within("LingGuFu79",{51,11},1)then phase=2;game:set_unit_invulnerable("WuHelu79",false);game:push_cmd_speak(0,"灵姑浮突至王旗，以戈击中阖闾足趾！击退阖闾，吴军便会撤退！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and not game:has_unit("WuHelu79")then return Enum.status.victory end return Enum.status.undecided', 28, 21000,
        [("灵姑浮","我将直取吴王大纛。")],
        '{{id="yue_camp",name="越军营寨",position={9,29},restore_hp=25,restore_mp=15,rewards={{item="medicine",amount=1}}},{id="wu_camp",name="吴军营寨",position={51,11},restore_hp=20,restore_mp=10,rewards={}}}')
    stages["79"] = stages["79"].replace('game:generate_unit("WuHelu79",1,Enum.force.enemy,{51,11})', 'game:generate_unit("WuHelu79",1,Enum.force.enemy,{51,11});game:set_unit_invulnerable("WuHelu79",true)')
    stages["80"] = stage("80", "夫差违谏释越 勾践竭力事吴", "第八十回", "夫椒会稽",
        "护送勾践、范蠡、文种进入会稽并坚守至第十二回合。", "m126", "ch80", ["GouJian79","FanLi79","WenZhong79"],
        [("GouJian79",8,25),("FanLi79",10,28),("WenZhong79",10,22)], intro80(), victory80(),
        [("FuChai80","enemy",[20,21]),("WuZiXu79","enemy",[18,27])]
        + [("YueGuard79","own",p) for p in ([5,21],[5,28],[8,18],[9,32],[13,20],[14,30])]
        + [("YueArcher79","own",p) for p in ([4,24],[7,34],[14,24])]
        + [("WuGuard79","enemy",p) for p in ([16,18],[16,23],[16,31],[20,16],[21,26],[22,33],[29,18],[30,29])]
        + [("WuArcher79","enemy",p) for p in ([18,14],[23,20],[23,30],[30,24])],
        'if phase==1 and game:is_unit_within("GouJian79",{58,23},2)and game:is_unit_within("FanLi79",{58,23},4)and game:is_unit_within("WenZhong79",{58,23},4)then phase=2;game:push_cmd_speak(0,"越王与二大夫已进入会稽。依山坚守到第十二回合，等待文种议和！")end',
        'for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end if phase==2 and game:get_turn_current()>=12 then return Enum.status.victory end return Enum.status.undecided', 26, 22000,
        [("文种","只要守住会稽，我便能以重赂说服伯嚭。")],
        '{{id="yue_field_camp",name="越军残营",position={8,25},restore_hp=20,restore_mp=10,rewards={{item="medicine",amount=1}}},{id="huiji_castle",name="会稽城池",position={58,23},restore_hp=30,restore_mp=20,rewards={{item="spirit_powder",amount=1}}}}')
    return stages


def patch_project():
    stages = build_stages()
    for stage_id, content in stages.items():
        (ROOT / f"game/sce/dongzhou/stage/{stage_id}.lua").write_text(content, encoding="utf-8")

    config_path = ROOT / "game/sce/dongzhou/config.lua"
    config = config_path.read_text(encoding="utf-8")
    if 'id = "TianKaiJiang71"' not in config:
        hero_rows = "\n".join(f'        ,{{ id = "{hid}", class = "{klass}", stat = {{{94 if klass in {"King","Lord","Strategist"} else 90},{96 if klass in {"Cavalry","Infantry","Archer"} else 88},{98 if klass == "Strategist" else 90},94,92}}, model = "{model}" }}' for hid, klass, model, _, _ in HEROES)
        marker = '        ,{ id = "GongZiBa70", class = "Infantry", stat = {88,92,84,89,86}, model = "infantry-1-blue" }'
        config = config.replace(marker, marker + "\n" + hero_rows)
    config = config.replace('"68", "69", "70" }', '"68", "69", "70", "71", "72", "73", "75", "78", "79", "80" }')
    config_path.write_text(config, encoding="utf-8")

    save_path = ROOT / "rl/save_system.py"
    save = save_path.read_text(encoding="utf-8")
    save = save.replace("STAGE_TABLE_VERSION = 14", "STAGE_TABLE_VERSION = 15")
    save = save.replace('"68","69","70"\n)', '"68","69","70","71","72","73","75","78","79","80"\n)')
    save_path.write_text(save, encoding="utf-8")

    gui_path = ROOT / "rl/play_gui.py"
    gui = gui_path.read_text(encoding="utf-8")
    if '_LARGE_BATTLE_MAPS["m120.png"]' not in gui:
        labels = {hid: name for hid, _, _, name, _ in HEROES}
        bios = {hid: bio for hid, _, _, _, bio in HEROES}
        portraits = {hid: (7 if klass in {"King","Lord"} else 49 if klass == "Strategist" else 35 if klass == "Cavalry" else 33 if klass == "Archer" else 25) for hid, klass, _, _, _ in HEROES}
        speakers = {name: portraits[hid] for hid, _, _, name, _ in HEROES}
        block = "\n" + "\n".join(f'_LARGE_BATTLE_MAPS["m{n:03d}.png"]={size}' for n, size in zip(range(120,127), ["(52,38,48)","(64,36,48)","(72,44,48)","(92,64,48)","(58,42,48)","(62,42,48)","(70,50,48)"]))
        block += "\nHERO_LABELS.update(" + repr(labels) + ")"
        block += "\nHERO_BIOS.update(" + repr(bios) + ")"
        block += "\nPORTRAIT_INDEX_BY_HERO.update(" + repr(portraits) + ")"
        block += "\nSPEAKER_PORTRAIT_INDEX.update(" + repr(speakers) + ")"
        block += '\nHISTORICAL_DEATH_HEROES.update({"YingShuang71","XiaNie73","WeiYue73","ShenYinShu75","TangHou75","YangYue78","WuHelu79","ZhuanYi79"})\n'
        gui = gui.replace('\nif _original_name == "__main__":', block + '\nif _original_name == "__main__":')
    gui_path.write_text(gui, encoding="utf-8")


def main():
    patch_project()
    print("chapters 71-80 integrated: 71,72,73,75,78,79,80")


if __name__ == "__main__":
    main()
