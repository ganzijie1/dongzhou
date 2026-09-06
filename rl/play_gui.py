"""Bootstrap the preserved full GUI runtime.

The fixed bytecode payload is loaded with marshal so normal Python cache
invalidation cannot overwrite it. Keep this wrapper Python 3.10-only until the
original GUI source is reconstructed.
"""

from __future__ import annotations

import marshal
import sys
from pathlib import Path

_RUNTIME = Path(__file__).with_name("_play_gui_runtime.cpython-310.pyc")
if not _RUNTIME.is_file():
    raise FileNotFoundError(f"Missing GUI runtime payload: {_RUNTIME}")

_original_name = __name__
with _RUNTIME.open("rb") as _stream:
    _stream.read(16)
    _code = marshal.load(_stream)

# Prevent the preserved module's own __main__ guard from firing before overrides.
globals()["__name__"] = "rl._play_gui_runtime"
exec(_code, globals(), globals())
globals()["__name__"] = _original_name

# The preserved GUI created MengdeEnv with its old 32-unit observation limit.
# Large battles still existed in the native game, but only the first 32 units
# reached rendering and hit-testing (22 allied units left room for 10 enemies
# at Chengpu). Keep enough observation slots for future Warring States battles.
_original_env_init = MengdeEnv.__init__


def _large_battle_env_init(self, *args, **kwargs):
    kwargs["max_units"] = max(999, int(kwargs.get("max_units", 32)))
    return _original_env_init(self, *args, **kwargs)


MengdeEnv.__init__ = _large_battle_env_init

from rl.mengde_env import MengdeProtocolError as _MengdeProtocolError

_original_restore = MengdeEnv.restore


def _stable_restore(self, snapshot):
    try:
        return _original_restore(self, snapshot)
    except _MengdeProtocolError as error:
        raise ValueError(f"读档失败：{error}") from error


MengdeEnv.restore = _stable_restore

_terrain_layers = []
_original_map_info = MengdeEnv.map_info


def _map_info_with_terrain_layers(self):
    global _terrain_layers
    result = _original_map_info(self)
    _terrain_layers = list(result.get("terrain_layers", []))
    return result


MengdeEnv.map_info = _map_info_with_terrain_layers


class _ForceAwareColors(dict):
    """Resolve the preserved runtime's generic HP color from its current unit."""

    def __getitem__(self, key):
        if key == "hp":
            force_key = sys._getframe(1).f_locals.get("force_key", "own")
            return dict.__getitem__(self, f"hp_{force_key}")
        return dict.__getitem__(self, key)


COLORS.update({
    "hp_own": (48, 196, 92),
    "hp_ally": (55, 184, 214),
    "hp_enemy": (225, 72, 72),
})
COLORS = _ForceAwareColors(COLORS)

HERO_LABELS.update({
    "GaoCityCommander6": "郜城守将",
    "QinVanguard42": "秦军步卒",
    "SongMutineer82": "宋都乱兵",
    "CaiHunter102": "蔡国伏兵",
    "CaiHunter103": "蔡国伏兵",
    "LuHuanGong11": "鲁桓公", "ZhengLiGong11": "郑厉公", "GongZiNi11": "公子溺",
    "YuanFan11": "原繁", "QinZi11": "秦子", "LiangZi11": "梁子", "TanBo11": "檀伯",
    "AlliedGuard11": "鲁郑联军", "AlliedArcher11": "鲁郑弓手",
    "SongZhuangGong11": "宋庄公", "NangongChangWan11": "南宫长万", "MengHuo11": "猛获",
    "NangongNiu11": "南宫牛", "HuaDu11": "华督", "SongGuard11": "宋军甲士",
    "SongArcher11": "宋军弓手", "JiHou11": "纪侯", "YingJi11": "嬴季",
    "JiGuard11": "纪国守军", "QiXiGong11": "齐僖公", "GongZiPengSheng11": "公子彭生",
    "YanBo11": "燕伯", "WeiHuiGong11": "卫惠公", "QiGuard11": "齐军甲士",
    "CoalitionArcher11": "联军弓手", "JiZu11": "祭足", "QiangChu11": "强鉏",
    "GongZiE11": "公子阏", "JiClanGuard11": "祭氏家兵", "JiClanArcher11": "祭氏弓手",
    "YongJiu11": "雍纠", "ZhengAmbusher11": "郑国伏兵", "ZhengAmbushArcher11": "伏兵弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "GaoCityCommander6": 25,
    "QinVanguard42": 24,
    "SongMutineer82": 49,
    "SongMutineerArcher81": 17,
    "CaiHunter102": 49,
    "CaiHunter103": 15,
    "LuHuanGong11": 7, "ZhengLiGong11": 9, "GongZiNi11": 31, "YuanFan11": 33,
    "QinZi11": 20, "LiangZi11": 25, "TanBo11": 37, "SongZhuangGong11": 8,
    "NangongChangWan11": 34, "MengHuo11": 38, "NangongNiu11": 39, "HuaDu11": 21,
    "JiHou11": 10, "YingJi11": 35, "QiXiGong11": 11, "GongZiPengSheng11": 36,
    "YanBo11": 12, "WeiHuiGong11": 13, "JiZu11": 22, "QiangChu11": 40,
    "GongZiE11": 32, "YongJiu11": 41,
})
HERO_BIOS.update({
    "GaoCityCommander6": "宋国驻守郜城的主将，史书未载其名。奉命据守城门，抵御郑、齐、鲁联军进攻。",
    "QinXiangGong": "秦国君主，护送周平王东迁，率军驱逐犬戎，奠定秦国诸侯基业。",
    "LuHuanGong11": "鲁国国君，联合郑国伐宋，又率军救援被四国围攻的纪国。",
    "ZhengLiGong11": "郑庄公之子公子突，在宋国扶持下即位，后因谋杀祭足失败而出奔。",
    "GongZiNi11": "鲁国公子，随鲁桓公伐宋救纪，曾在纪城与齐将公子彭生交锋。",
    "YuanFan11": "郑国将领，参与伐宋和救纪之战，擅长率骑兵迂回突击。",
    "QinZi11": "鲁国将领，纪城大战中驰援公子溺，与梁子协力抵挡齐军。",
    "LiangZi11": "鲁国善射将领，伐宋时射中猛获右臂并将其擒获。",
    "TanBo11": "郑国将领，与原繁突击齐营，为纪城解围立功。",
    "SongZhuangGong11": "宋国国君，因索取郑国重赂不遂而屡次构兵。",
    "NangongChangWan11": "宋国勇将，力大善战，伐宋之役在西门设伏擒获郑将。",
    "MengHuo11": "宋军先锋，与公子溺、原繁交战，右臂中箭后被擒。",
    "NangongNiu11": "宋国将领，奉命诈败诱敌，为南宫长万的伏兵创造战机。",
    "HuaDu11": "宋国权臣，曾弑宋殇公拥立庄公，在宋国政局中权势极重。",
    "JiHou11": "纪国国君，面对齐宋卫燕联军围攻，向鲁国求援。",
    "YingJi11": "纪侯之弟，纪城大战中率城内守军出击，夹攻四国联军。",
    "QiXiGong11": "齐国国君，联合宋、卫、燕攻纪，企图吞并纪国。",
    "GongZiPengSheng11": "齐国勇将，在纪城力压公子溺，乱军中中箭负伤。",
    "YanBo11": "燕国国君，参与四国攻纪，见战局不利率先撤军。",
    "WeiHuiGong11": "卫国国君，随齐国出兵攻纪，燕军撤退后卫军也随之溃散。",
    "JiZu11": "郑国上卿祭足，拥立公子突后掌国政，又识破雍纠的毒酒之谋。",
    "QiangChu11": "祭足部将，率勇士赴东郊宴席，擒住并处决雍纠。",
    "GongZiE11": "郑国公子阏，率百名家兵埋伏宴亭之外，击破雍纠伏兵。",
    "YongJiu11": "郑厉公女婿，受命以毒酒谋杀祭足，事泄后被擒杀。",
})
TERRAIN_LABELS.update({"Snow": "雪地", "ShallowRiver": "小河", "Water": "大河", "Gate": "城门", "DeerFort": "鹿砦", "Fence": "栅栏", "CityInterior": "城内", "Residence": "民居", "Castle": "城池"})
HERO_LABELS.update({
    "ZhouXu5": "州吁",
    "ShiHou5": "石厚",
    "WeiVanguard": "卫军前锋",
    "CoalitionGuard": "诸侯联军",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ZhouXu5": 38,
    "ShiHou5": 40,
    "WeiVanguard": 15,
    "CoalitionGuard": 25,
})
HERO_BIOS.update({
    "ZhouXu5": "卫庄公庶子，弑杀卫桓公自立，联合宋、鲁、陈、蔡四国攻郑，企图以战功压服卫人。",
    "ShiHou5": "卫国大夫石碏之子，协助州吁弑君夺位并谋划攻郑，后随州吁逃回卫国。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "州吁": 38,
    "石厚": 40,
})
HERO_LABELS.update({
    "ZhengVanguard": "郑军前锋",
    "ZhengVanguard2": "郑军前锋",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ZhengVanguard": 49,
    "ZhengVanguard2": 24,
})
HERO_LABELS.update({"DuanArcher": "共城弓手"})
PORTRAIT_INDEX_BY_HERO.update({"DuanArcher": 17})
HERO_LABELS.update({"QuanRongArcher": "犬戎弓兵"})
PORTRAIT_INDEX_BY_HERO.update({"QuanRongArcher": 17})
HERO_LABELS.update({"QuanRongLeftWarrior": "犬戎伏兵", "QuanRongRightWarrior": "犬戎伏兵", "BoDing41": "伯丁", "ManYeSu41": "满也速"})
PORTRAIT_INDEX_BY_HERO.update({"QuanRongLeftWarrior": 17, "QuanRongRightWarrior": 17, "BoDing41": 38, "ManYeSu41": 39})
PORTRAIT_INDEX_BY_HERO["ZhengHuanGong"] = 42
SPEAKER_PORTRAIT_INDEX["\u90d1\u6853\u516c"] = 42
HERO_BIOS.update({"BoDing41": "犬戎将领，奉命率伏兵夹击勤王诸侯，善于率骑兵迂回突击。", "ManYeSu41": "犬戎将领，统领步兵接应犬戎主，曾在镐京之战中返身救援。"})
HERO_LABELS.update({
    "ZhengWuGong": "郑掘突", "GongZiCheng3": "公子成", "WeiWuGong": "卫武公",
    "JinWenHou": "晋文侯", "WeiGuard31": "卫国甲士", "JinGuard31": "晋国骑兵",
    "ZhengGuard31": "郑国甲士", "CoalitionArcher31": "勤王弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ZhengWuGong": 35, "GongZiCheng3": 22, "WeiWuGong": 55,
    "JinWenHou": 36, "QinXiangGong": 37,
    "WeiGuard31": 24, "JinGuard31": 15, "ZhengGuard31": 49, "CoalitionArcher31": 17,
})
HERO_BIOS.update({
    "ZhengWuGong": "郑桓公之子掘突，父死骊山后率军复仇，参与收复镐京，后袭爵为郑武公。",
    "GongZiCheng3": "郑国公子，劝掘突休整待援，并随军参与收复镐京之战。",
    "WeiWuGong": "卫国国君姬和，年逾八十仍率军勤王，主持收复镐京，并力谏平王勿弃西都。",
    "JinWenHou": "晋国国君姬仇，率北路兵马勤王，与卫、秦、郑诸军合力驱逐犬戎。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "郑掘突": 35, "公子成": 22, "卫武公": 55, "晋文侯": 36,
    "秦襄公": 37, "周平王": 2, "太宰咺": 22, "犬戎主": 38,
})
SPEAKER_PORTRAIT_INDEX.update({
    "申后": 12, "太子宜臼": 31, "郑伯友": 43, "虢石父": 31,
    "申侯": 6, "尹球": 42, "尹吉甫": 42, "召虎": 54,
})
CLASS_LABELS.update({"Support": "\u672f\u58eb"})
UNIT_VISUAL_ANCHORS[(13, 2)] = (-0.17, 0.0)
UNIT_VISUAL_ANCHORS[(15, 1)] = (0.0, 0.0)
UNIT_VISUAL_ANCHORS[(16, 1)] = (0.0, 0.0)
UNIT_VISUAL_ANCHORS[(17, 1)] = (0.0, 0.0)


HERO_LABELS.update({
    "CaiHunter101": "蔡国猎手",
    "CaiHunter102": "蔡国猎手",
    "CaiHunter103": "蔡国猎手",
})

HERO_LABELS.update({
    "FuXia12": "\u5085\u7455",
    "ZhengZhaoGong12": "\u90d1\u662d\u516c",
    "GaoQuMi12": "\u9ad8\u6e20\u5f25",
    "ZhengAmbusher12": "\u90d1\u56fd\u6b7b\u58eb",
    "ZhengAmbushArcher12": "\u90d1\u56fd\u4f0f\u5f29\u624b",
})
PORTRAIT_INDEX_BY_HERO.update({
    "FuXia12": 33,
    "ZhengZhaoGong12": 9,
    "GaoQuMi12": 34,
})
HERO_BIOS.update({
    "FuXia12": "\u90d1\u56fd\u5927\u592b\uff0c\u5949\u90d1\u662d\u516c\u547d\u9a7b\u5b88\u5927\u9675\uff0c\u4e0e\u796d\u8db3\u5408\u529b\u62b5\u5fa1\u5b8b\u3001\u9c81\u3001\u8521\u3001\u536b\u56db\u56fd\u8054\u519b\u3002",
    "ZhengZhaoGong12": "\u90d1\u5e84\u516c\u4e16\u5b50\u5ffd\uff0c\u4e24\u5ea6\u5373\u4f4d\u4e3a\u90d1\u541b\uff0c\u51ac\u796d\u51fa\u884c\u65f6\u88ab\u9ad8\u6e20\u5f25\u4f0f\u5175\u5f11\u6740\u3002",
    "GaoQuMi12": "\u90d1\u56fd\u5927\u592b\uff0c\u4e0e\u516c\u5b50\u4eb9\u4ea4\u597d\uff0c\u8d81\u796d\u8db3\u51fa\u4f7f\u65f6\u4f0f\u6740\u90d1\u662d\u516c\uff0c\u6539\u7acb\u516c\u5b50\u4eb9\u3002",
})
SPEAKER_PORTRAIT_INDEX.update({
    "\u516c\u5b50\u5bff": 25,
    "\u5b8b\u5e84\u516c": 8,
    "\u796d\u8db3": 22,
    "\u5085\u7455": 33,
    "\u9ad8\u6e20\u5f25": 34,
    "\u516c\u5b50\u4eb9": 31,
    "\u90d1\u662d\u516c": 9,
})
HISTORICAL_DEATH_HEROES.add("ZhengZhaoGong12")

HERO_LABELS.update({
    "LuHuanGong13": "鲁桓公",
    "WenJiang13": "文姜",
    "GongZiPengSheng13": "公子彭生",
    "QiXiangGong13": "齐襄公",
    "WangZiChengFu13": "王子成父",
    "GuanZhiFu13": "管至父",
    "QiDeadman13": "齐国死士",
    "QiArcher13": "齐军弓手",
    "ZiWei13": "子亹",
    "GaoQuMi13": "高渠弥",
    "ZhengEscort13": "郑国随从",
    "ZhengArcher13": "郑国弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "LuHuanGong13": 7,
    "WenJiang13": 12,
    "GongZiPengSheng13": 38,
    "QiXiangGong13": 8,
    "WangZiChengFu13": 34,
    "GuanZhiFu13": 39,
    "ZiWei13": 31,
    "GaoQuMi13": 34,
})
HERO_BIOS.update({
    "LuHuanGong13": "鲁国国君，携夫人文姜赴齐议婚，因识破齐襄公与文姜私情，在牛山归途中被彭生杀害。",
    "WenJiang13": "齐僖公之女、鲁桓公夫人，与兄齐襄公私通。桓公遇害后羞归鲁宫，长期居于齐鲁边境。",
    "GongZiPengSheng13": "齐国公子，膂力过人。奉齐襄公密令在车中杀害鲁桓公，事后被齐侯推出顶罪斩首。",
    "QiXiangGong13": "齐国国君，勇悍而残忍。借首止会盟诱杀郑君子亹与高渠弥，以诛逆之名压服国人。",
    "WangZiChengFu13": "齐国将领，奉齐襄公之命率死士环列首止盟坛，参与围杀郑国君臣。",
    "GuanZhiFu13": "齐国将领，与王子成父各领百余死士埋伏首止，在盟誓时封锁郑使退路。",
    "ZiWei13": "郑庄公之子。高渠弥弑昭公后拥立其为君，赴首止会齐时遭齐襄公伏杀。",
    "GaoQuMi13": "郑国大夫，弑杀郑昭公并拥立子亹。随子亹赴首止会盟，被齐襄公擒获后车裂。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "申繻": 33,
    "鲁桓公": 7,
    "文姜": 12,
    "齐襄公": 8,
    "公子彭生": 38,
    "施伯": 22,
    "周公黑肩": 20,
    "祭足": 22,
    "原繁": 33,
    "子亹": 31,
    "高渠弥": 34,
})
HISTORICAL_DEATH_HEROES.update({
    "LuHuanGong13", "GongZiPengSheng13", "ZiWei13", "GaoQuMi13"
})

HERO_LABELS.update({
    "QiXiangGong14": "齐襄公", "WeiHuiGong14": "卫惠公", "LuZhuangGong14": "鲁庄公",
    "SongMinGong14": "宋闵公", "ChenXuanGong14": "陈宣公", "CaiAiHou14": "蔡哀侯",
    "CoalitionGuard14": "五国联军", "CoalitionArcher14": "联军弓手",
    "QianMou14": "公子黔牟", "GongZiXie14": "公子泄", "GongZiZhi14": "公子职",
    "NingGui14": "宁跪", "WeiGuard14": "卫国守军", "WeiArcher14": "卫国弓手",
    "ZiTu14": "子突", "RoyalChariot14": "王师战车",
    "LianCheng14": "连称", "GuanZhiFu14": "管至父", "KuikouGuard14": "葵丘戍卒",
    "RebelArcher14": "葵丘弓手", "QiXiangGong142": "齐襄公", "ShiZhiFenRu14": "石之纷如",
    "TuRenFei14": "徒人费", "MengYang14": "孟阳", "QiPalaceGuard14": "离宫卫士",
    "QiPalaceArcher14": "离宫弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiXiangGong14": 8, "WeiHuiGong14": 13, "LuZhuangGong14": 7, "SongMinGong14": 10,
    "ChenXuanGong14": 11, "CaiAiHou14": 12, "QianMou14": 31, "GongZiXie14": 34,
    "GongZiZhi14": 39, "NingGui14": 33, "ZiTu14": 40, "LianCheng14": 34,
    "GuanZhiFu14": 39, "QiXiangGong142": 8, "ShiZhiFenRu14": 38,
    "TuRenFei14": 37, "MengYang14": 25,
})
HERO_BIOS.update({
    "QiXiangGong14": "齐国国君，联合诸侯复立卫惠公，后因拒绝瓜时代戍之约，在姑棼离宫兵变中被杀。",
    "WeiHuiGong14": "卫宣公之子公子朔，曾因谗害兄长出奔，后借齐、鲁、宋、陈、蔡五国兵力复位。",
    "LuZhuangGong14": "鲁桓公之子，鲁国国君。参与五国伐卫，后成为春秋时期重要诸侯。",
    "SongMinGong14": "宋庄公之子，参与五国伐卫、迎卫惠公复位，后死于宋国内乱。",
    "ChenXuanGong14": "陈国国君，参与五国伐卫，辅佐卫惠公复位。",
    "CaiAiHou14": "蔡国国君，名献舞，参与五国伐卫，后来与楚国发生长期纠葛。",
    "QianMou14": "卫宣公之子，卫惠公出奔后被国人拥立。五国破卫后获释，逃往周王室。",
    "GongZiXie14": "卫国公子，与公子职共同拥立黔牟。五国攻破卫城后被齐军处死。",
    "GongZiZhi14": "卫国公子，与公子泄共同拥立黔牟。卫惠公复位后被齐军处死。",
    "NingGui14": "卫国大夫，辅佐公子黔牟抵抗五国联军。卫城失陷后逃往秦国。",
    "ZiTu14": "周王室将领，奉王命率二百乘救卫，孤军奋战杀敌数十，兵败后自刎。",
    "LianCheng14": "齐国将领，戍守葵丘久不得代，与管至父发动兵变并杀死齐襄公。",
    "GuanZhiFu14": "齐国将领，与连称戍守葵丘。因齐襄公失信不肯换防，参与姑棼宫变。",
    "QiXiangGong142": "齐国国君，出猎遇彭生鬼影坠车伤足，退居姑棼离宫后死于兵变。",
    "ShiZhiFenRu14": "齐国宫廷武士，姑棼兵变时守卫寝宫，与连称交战十余合后战死。",
    "TuRenFei14": "齐襄公近侍，虽曾受鞭笞，兵变时仍冒险报信并奋力护主。",
    "MengYang14": "齐襄公近臣，兵变时穿君服卧于榻上，以身代君而死。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "卫惠公": 13, "齐襄公": 8, "公子黔牟": 31, "宁跪": 33, "子突": 40,
    "管至父": 39, "孟阳": 25, "连称": 34, "公孙无知": 31,
})
HISTORICAL_DEATH_HEROES.update({
    "GongZiXie14", "GongZiZhi14", "ZiTu14", "QiXiangGong142",
    "ShiZhiFenRu14", "TuRenFei14", "MengYang14",
})

HERO_LABELS.update({
    "QiHuanGong15": "齐桓公", "BaoShuYa15": "鲍叔牙", "YongLin15": "雍廪",
    "WangZiChengFu15": "王子成父", "DongGuoYa15": "东郭牙", "NingYue15": "宁越",
    "ZhongSunJiu15": "仲孙湫", "QiAmbusher15": "齐军伏兵", "QiAmbushArcher15": "齐军伏弩手",
    "LuZhuangGong15": "鲁庄公", "CaoMo15": "曹沫", "QinZi15": "秦子", "LiangZi15": "梁子",
    "GongZiJiu15": "公子纠", "GuanYiWu15": "管夷吾", "ZhaoHuQi15": "召忽",
    "LuGuard15": "鲁军甲士", "LuArcher15": "鲁军弓手",
    "WangZiChengFu152": "王子成父", "DongGuoYa152": "东郭牙", "QiPursuer15": "齐军追兵",
    "QiPursuitArcher15": "齐军追弩手", "LuZhuangGong152": "鲁庄公", "CaoMo152": "曹沫",
    "QinZi152": "秦子", "GuanYiWu152": "管夷吾", "GongZiJiu152": "公子纠",
    "ZhaoHuQi152": "召忽", "LuRearGuard15": "鲁军后卫", "LuRearArcher15": "鲁军后队弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiHuanGong15": 8, "BaoShuYa15": 22, "YongLin15": 37, "WangZiChengFu15": 34,
    "DongGuoYa15": 35, "NingYue15": 39, "ZhongSunJiu15": 33,
    "LuZhuangGong15": 7, "CaoMo15": 34, "QinZi15": 20, "LiangZi15": 25,
    "GongZiJiu15": 31, "GuanYiWu15": 22, "ZhaoHuQi15": 37,
    "WangZiChengFu152": 34, "DongGuoYa152": 35, "LuZhuangGong152": 7,
    "CaoMo152": 34, "QinZi152": 20, "GuanYiWu152": 22,
    "GongZiJiu152": 31, "ZhaoHuQi152": 37,
})
HERO_BIOS.update({
    "QiHuanGong15": "齐国公子小白，先于公子纠返回临淄即位。乾时击败鲁军，后来成为春秋五霸之一。",
    "BaoShuYa15": "齐国大夫，辅佐公子小白即位，深知管仲之才，在乾时设伏击败鲁军。",
    "YongLin15": "齐国大夫，联合高傒等诛杀公孙无知，乾时之战担任先锋，诈败诱鲁军入伏。",
    "WangZiChengFu15": "齐国将领，乾时之战率右军绕袭鲁军后路，后在汶阳截击败军。",
    "DongGuoYa15": "齐国大夫，参与诛杀无知，又在乾时与汶阳之战率军包抄鲁军。",
    "NingYue15": "齐国将领，乾时伏于侧翼，截获梁子并献其于齐桓公。",
    "ZhongSunJiu15": "齐国大夫仲孙湫，乾时率伏兵夹击鲁军，战后参与向鲁国索取公子纠。",
    "LuZhuangGong15": "鲁国国君，护送公子纠争夺齐君之位，在乾时中伏大败，微服逃回鲁国。",
    "CaoMo15": "鲁国勇将，乾时追敌陷入重围，身中两箭仍突围；汶阳断后时再负刀伤。",
    "QinZi15": "鲁国将领，乾时保护鲁庄公突围，汶阳断后迎战王子成父，最终战死。",
    "LiangZi15": "鲁国将领，乾时举鲁侯旗号引开齐军，掩护庄公逃走，随后被俘处死。",
    "GongZiJiu15": "齐襄公长子，获鲁国支持争夺齐君之位，因小白先入临淄而败。",
    "GuanYiWu15": "字仲，辅佐公子纠。即墨射中小白带钩，乾时战败后护送鲁军撤退。",
    "ZhaoHuQi15": "齐国大夫召忽，与管夷吾共同辅佐公子纠，随公子纠居于鲁国。",
    "WangZiChengFu152": "齐国将领，乾时之战率右军绕袭鲁军后路，后在汶阳截击败军。",
    "DongGuoYa152": "齐国大夫，参与诛杀无知，又在乾时与汶阳之战率军包抄鲁军。",
    "LuZhuangGong152": "鲁国国君，护送公子纠争位，在乾时中伏后由管夷吾、曹沫等护送撤退。",
    "CaoMo152": "鲁国勇将，汶阳退兵时迎战东郭牙，左臂中刀仍率残部突出包围。",
    "QinZi152": "鲁国将领，在汶阳截击战中迎战王子成父，为掩护鲁庄公撤退而战死。",
    "GuanYiWu152": "字仲，乾时战败后命军士抛弃辎重，诱使齐军争夺，护鲁侯与公子纠脱身。",
    "GongZiJiu152": "齐襄公长子，获鲁国支持争位，乾时败后随鲁军退回鲁国。",
    "ZhaoHuQi152": "齐国大夫召忽，汶阳撤退时保护公子纠返回鲁国。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "鲍叔牙": 22, "齐桓公": 8, "鲁庄公": 7, "管夷吾": 22,
    "曹沫": 34, "秦子": 20, "王子成父": 34,
})
HERO_LABELS.update({
    "LuZhuangGong16": "鲁庄公", "CaoGui16": "曹刿", "BaoShuYa16": "鲍叔牙",
    "LuGuard16": "鲁军甲士", "LuArcher16": "鲁军弓手",
    "QiVanguard16": "齐军先锋", "QiGuard16": "齐军甲士", "QiArcher16": "齐军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "LuZhuangGong16": 7, "CaoGui16": 40, "BaoShuYa16": 22,
    "LuGuard16": 49, "LuArcher16": 17, "QiVanguard16": 15,
    "QiGuard16": 24, "QiArcher16": 37,
})
HERO_BIOS.update({
    "LuZhuangGong16": "鲁国国君，乾时败后起兵伐齐，在长勺听从曹刿之谋，以逸待劳击败齐军。",
    "CaoGui16": "鲁国东平隐士，主张取信于民，长勺之战以一鼓作气之理制胜，并察辙望旗后追敌。",
    "BaoShuYa16": "齐国贤臣，荐管仲为相；长勺之战率军攻鲁，因轻敌连续三鼓，被曹刿乘其气竭击败。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "施伯": 33, "公孙隰朋": 32, "召忽": 25, "曹刿": 40,
    "鲍叔牙": 22, "管夷吾": 22, "齐桓公": 8, "鲁庄公": 7,
})
HERO_LABELS.update({
    "SongHuanGong17": "宋桓公", "XiaoShuDaXin17": "萧叔大心",
    "SongClanGuard17": "宋国族兵", "SongArcher17": "宋军弓手", "CaoGuard17": "曹国援军",
    "NanGongNiu17": "南宫牛", "MengHuo17": "猛获", "ZiYou17": "公子游",
    "RebelGuard17": "叛军甲士", "RebelArcher17": "叛军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "SongHuanGong17": 31, "XiaoShuDaXin17": 40, "SongClanGuard17": 49,
    "SongArcher17": 17, "CaoGuard17": 15, "NanGongNiu17": 34,
    "MengHuo17": 24, "ZiYou17": 13, "RebelGuard17": 25, "RebelArcher17": 37,
})
HERO_BIOS.update({
    "SongHuanGong17": "名御说，宋庄公之子。南宫长万作乱后逃往亳邑，得萧叔大心与五族拥立为宋君。",
    "XiaoShuDaXin17": "宋国萧邑大夫，联合戴、武、宣、穆、庄五族与曹国援军平定南宫长万之乱。",
    "NanGongNiu17": "南宫长万亲族，奉命与猛获围攻亳邑，在五族与曹军内外夹击中战死。",
    "MengHuo17": "宋国勇将，曾随南宫长万伐鲁；参与拥立公子游，亳城败后逃往卫国。",
    "ZiYou17": "宋闵公从弟，被南宫长万拥立为君；五族攻入国都后被杀。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "鲁庄公": 7, "公子偃": 34, "宋闵公": 13, "仇牧": 40,
    "萧叔大心": 40, "公子御说": 31, "南宫牛": 34, "猛获": 24,
    "息侯": 31, "楚文王": 8, "蔡哀侯": 13, "息妫": 12,
})
HERO_LABELS.update({
    "QiHuanGong18": "齐桓公", "GuanYiWu18": "管夷吾", "BaoShuYa18": "鲍叔牙",
    "WangZiChengFu18": "王子成父", "QiGuard18": "齐军甲士", "QiArcher18": "齐军弓手",
    "SongHuanGong18": "宋桓公", "SongGuard18": "宋军甲士", "SongArcher18": "宋军弓手",
    "SuiLord18": "遂国君", "SuiGuard18": "遂国甲士", "SuiArcher18": "遂国弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiHuanGong18": 8, "GuanYiWu18": 22, "BaoShuYa18": 40,
    "WangZiChengFu18": 34, "QiGuard18": 49, "QiArcher18": 17,
    "SongHuanGong18": 31, "SongGuard18": 25, "SongArcher18": 20,
    "SuiLord18": 13, "SuiGuard18": 24, "SuiArcher18": 37,
})
HERO_BIOS.update({
    "QiHuanGong18": "齐国国君，任用管仲改革国政，奉周王命会诸侯于北杏，逐步奠定春秋霸业。",
    "GuanYiWu18": "字仲，齐国相国。主张尊王室、守盟信，以北杏会盟和归还鲁地建立齐国威望。",
    "BaoShuYa18": "齐国贤臣，深知管仲之才；北杏会盟后参与整军问罪遂国。",
    "WangZiChengFu18": "齐国将领，受管仲整军之法训练，随齐桓公征遂并维护北杏盟约。",
    "SongHuanGong18": "名御说，南宫长万之乱平定后即位，赴北杏会盟并协助齐国问罪遂国。",
    "SuiLord18": "遂国国君，拒绝齐桓公以王命召集的北杏之会，遂邑因此遭齐宋联军讨伐。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "齐桓公": 8, "管夷吾": 22, "鲍叔牙": 40, "宋桓公": 31,
    "遂国君": 13, "鲁庄公": 7, "曹沫": 34, "文姜": 12, "宁戚": 40,
})
HERO_LABELS.update({
    "ZhengLiGong19": "郑厉公", "BinXuWu19": "宾须无", "QiGuard19": "齐军甲士",
    "QiArcher19": "齐军弓手", "FuXia19": "傅瑕", "ZhengGuard19": "郑军甲士",
    "ZhengArcher19": "郑军弓手", "XiGuoGong19": "西虢公", "ShiShu19": "师叔",
    "ZhengGuard192": "郑军甲士", "GuoGuard19": "虢军甲士", "GuoArcher19": "虢军弓手",
    "ZhouHuiWang19": "周惠王", "WangZiTui19": "王子颓", "WeiGuo19": "蔿国",
    "BianBo19": "边伯", "ShiSu19": "石速", "ZhanFu19": "詹父", "ZiQin19": "子禽",
    "RoyalRebelGuard19": "王城叛军", "RoyalRebelArcher19": "王城叛军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ZhengLiGong19": 31, "BinXuWu19": 35, "QiGuard19": 49, "QiArcher19": 17,
    "FuXia19": 38, "ZhengGuard19": 25, "ZhengArcher19": 37,
    "XiGuoGong19": 8, "ShiShu19": 42, "ZhengGuard192": 49,
    "GuoGuard19": 15, "GuoArcher19": 20, "ZhouHuiWang19": 7,
    "WangZiTui19": 13, "WeiGuo19": 40, "BianBo19": 34, "ShiSu19": 24,
    "ZhanFu19": 39, "ZiQin19": 22, "RoyalRebelGuard19": 25, "RoyalRebelArcher19": 37,
})
HERO_BIOS.update({
    "ZhengLiGong19": "名突，郑庄公之子。流亡栎城十九年，在齐国相助下复位，后又扶周惠王平定子颓之乱。",
    "BinXuWu19": "齐国将领，奉齐桓公之命援助郑厉公，在栎城击败并擒获傅瑕。",
    "FuXia19": "郑国大夫，兵败被擒后答应迎厉公复位，杀子仪开城，终因反复无常被厉公处死。",
    "XiGuoGong19": "西虢国国君，与郑厉公分路进攻成周，诛杀王子颓及五大夫，迎周惠王复位。",
    "ShiShu19": "郑国大夫，奉郑厉公之命入周探查王子颓叛军虚实，为郑、虢联军提供军情。",
    "ZhouHuiWang19": "周王室天子，因五大夫拥立王子颓而出奔郑国，后由郑厉公、西虢公护送复位。",
    "WangZiTui19": "周庄王庶子，受蔿国等五大夫拥立，占据成周僭称天子，最终兵败被杀。",
    "WeiGuo19": "周王室大夫，因园圃被收而怨恨惠王，联合四大夫拥立王子颓。",
    "BianBo19": "周王室大夫，参与拥立王子颓并据守成周，郑、虢联军入城后战死。",
    "ShiSu19": "周王室大夫，王子颓之乱的主谋之一，联合卫、燕兵马攻逐周惠王。",
    "ZhanFu19": "周王室大夫，参与王子颓之乱，负责王城内街守备，兵败后被杀。",
    "ZiQin19": "周王室大夫，王子颓之党，随五大夫据守成周，最终与王子颓一同覆灭。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "郑厉公": 31, "宾须无": 35, "傅瑕": 38, "西虢公": 8, "师叔": 42,
    "周惠王": 7, "王子颓": 13, "蔿国": 40, "边伯": 34, "管夷吾": 22,
    "齐桓公": 8,
})
HERO_LABELS.update({
    "WeiYiGong20": "卫懿公", "WeiKaiFang20": "公子开方", "WeiGuard20": "卫国甲士",
    "WeiArcher20": "卫国弓手", "JinXianGong20": "晋献公", "ShenSheng20": "申生",
    "JinGuard20": "晋军甲士", "JinArcher20": "晋军弓手", "LiRongLord20": "骊戎主",
    "LiRongGuard20": "骊戎战士", "LiRongArcher20": "骊戎弓手", "ZhaoSu20": "赵夙",
    "BiWan20": "毕万", "JinGuard202": "晋国下军", "JinArcher202": "晋国弓手",
    "DiChief20": "狄首", "DiGuard20": "狄寨战士", "DiArcher20": "狄寨弓手",
    "HuoLord20": "霍君", "HuoGuard20": "霍国甲士", "HuoArcher20": "霍国弓手",
    "WeiLord20": "魏君", "WeiGuard202": "魏国甲士", "WeiArcher202": "魏国弓手",
    "DouGuWuTu20": "斗谷於菟", "DouBan20": "斗班", "DouLian20": "斗廉",
    "DouYuJiang20": "斗御疆", "ZiYuan20": "子元", "ZiYuanGuard20": "子元家甲",
    "ZiYuanArcher20": "子元家弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "WeiYiGong20": 13, "WeiKaiFang20": 35, "WeiGuard20": 25, "WeiArcher20": 37,
    "JinXianGong20": 8, "ShenSheng20": 31, "JinGuard20": 49, "JinArcher20": 17,
    "LiRongLord20": 39, "LiRongGuard20": 24, "LiRongArcher20": 20,
    "ZhaoSu20": 34, "BiWan20": 38, "JinGuard202": 15, "JinArcher202": 17,
    "DiChief20": 24, "DiGuard20": 25, "DiArcher20": 37, "HuoLord20": 11,
    "HuoGuard20": 49, "HuoArcher20": 20, "WeiLord20": 10, "WeiGuard202": 15,
    "WeiArcher202": 17, "DouGuWuTu20": 42, "DouBan20": 34, "DouLian20": 40,
    "DouYuJiang20": 38, "ZiYuan20": 13, "ZiYuanGuard20": 25, "ZiYuanArcher20": 37,
})
HERO_BIOS.update({
    "WeiYiGong20": "卫国国君，卫惠公之子。齐桓公奉周王命伐卫时出兵迎战，败后献金帛请和。",
    "WeiKaiFang20": "卫懿公长子，卫军战败后向齐求和，随后舍弃储位投奔齐桓公。",
    "JinXianGong20": "晋国国君，整顿曲沃旧族并扩建绛都，伐骊戎、建二军，使晋国迅速强盛。",
    "ShenSheng20": "晋献公世子，品行贤孝，统领晋国下军灭狄、霍、魏三国，军功日盛。",
    "LiRongLord20": "骊戎首领，据守骊山抵挡晋军，兵败后请和并将骊姬、少姬献给晋献公。",
    "ZhaoSu20": "晋国将领，随申生征灭三国，以战功获赐狄地，为赵氏早期先祖。",
    "BiWan20": "晋国将领，随申生攻灭魏国，受封魏地，其后族人发展为战国魏氏。",
    "DiChief20": "北境狄部首领，与霍、魏互相呼应，遭晋国下军分路进攻而败。",
    "HuoLord20": "霍国国君，据守石城抵抗晋国下军，申生三路并进后国亡。",
    "WeiLord20": "魏国国君，依托河畔城邑与狄、霍互援，最终被申生所率下军攻灭。",
    "DouGuWuTu20": "字子文，楚国贤臣。率甲士平定子元逼宫之乱，后任令尹，改革楚政。",
    "DouBan20": "楚国将领，随斗谷於菟入宫靖难，在宫中交战并亲手斩杀子元。",
    "DouLian20": "楚国正直大夫，因斥责子元寝处王宫而被拘，乱平后推举子文为令尹。",
    "DouYuJiang20": "楚国将领，曾随子元伐郑，后协助斗谷於菟入宫靖难。",
    "ZiYuan20": "楚文王之弟、楚成王叔父，任令尹后图谋文夫人与王位，挟兵入宫而被诛。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "卫懿公": 13, "公子开方": 35, "晋献公": 8, "申生": 31, "里克": 40,
    "骊戎主": 39, "骊姬": 12, "郭偃": 22, "史苏": 40, "优施": 21,
    "士蔿": 33, "赵夙": 34, "毕万": 38, "狄首": 24, "霍君": 11,
    "魏君": 10, "文夫人": 12, "子元": 13, "斗廉": 40, "斗谷於菟": 42,
    "斗班": 34, "楚成王": 8, "子文": 42, "叔詹": 42,
})
HISTORICAL_DEATH_HEROES.add("ZiYuan20")
HISTORICAL_DEATH_HEROES.update({
    "FuXia19", "WangZiTui19", "WeiGuo19", "BianBo19", "ShiSu19", "ZhanFu19", "ZiQin19"
})

HISTORICAL_DEATH_HEROES.update({"NanGongNiu17", "ZiYou17"})
HISTORICAL_DEATH_HEROES.update({"LiangZi15", "QinZi152"})
HISTORICAL_DEATH_HEROES.add("GuoShiFu")

_original_unit_sprite_role = unit_sprite_role
_CHARIOT_UNITS = {"WeiGuard7", "ChenEscort101", "RoyalChariot14"}
_STRATEGIST_UNITS = {"ZhengHuanGong"}
_OFFICIAL_WHITE_UNITS = {"GuoShiFu"}


def unit_sprite_role(detail):
    if detail is None:
        return _original_unit_sprite_role(detail)
    if str(detail.get("name")) in _STRATEGIST_UNITS:
        return "strategist"
    if str(detail.get("name")) in _OFFICIAL_WHITE_UNITS:
        return "official_white"
    if str(detail.get("name")) in _CHARIOT_UNITS:
        return "chariot"
    role = _original_unit_sprite_role(detail)
    if str(detail.get("class")) == "Archer" and role == "cavalry":
        return "elite_archer"
    return role


_original_load_unit_sprites = load_unit_sprites


def _load_chariot_sprites():
    root = Path(__file__).resolve().parent / "assets" / "unit_anim" / "chariot"

    def load(name):
        return pygame.image.load(str(root / name)).convert_alpha()

    animation = {
        "down": tuple(load(f"down_{index}.png") for index in range(2)),
        "up": tuple(load(f"up_{index}.png") for index in range(2)),
        "left": tuple(load(f"left_{index}.png") for index in range(2)),
        "stand_down": (load("stand_down.png"),),
        "stand_up": (load("stand_up.png"),),
        "stand_left": (load("stand_left.png"),),
        "weak": tuple(load(f"weak_{index}.png") for index in range(2)),
        "hit_failed": (load("hit_failed.png"),),
    }
    animation["right"] = tuple(pygame.transform.flip(frame, True, False) for frame in animation["left"])
    animation["stand_right"] = tuple(
        pygame.transform.flip(frame, True, False) for frame in animation["stand_left"]
    )
    for direction in ("down", "up", "left"):
        animation[f"attack_{direction}"] = tuple(
            load(f"attack_{direction}_{index}.png") for index in range(4)
        )
        animation[f"hit_{direction}"] = (load(f"hit_{direction}.png"),)
    animation["attack_right"] = tuple(
        pygame.transform.flip(frame, True, False) for frame in animation["attack_left"]
    )
    animation["hit_right"] = tuple(
        pygame.transform.flip(frame, True, False) for frame in animation["hit_left"]
    )
    return animation


def load_unit_sprites():
    animations = _original_load_unit_sprites()
    animations["chariot"] = _load_chariot_sprites()
    return animations


_original_run_shop_menu = run_shop_menu


def _draw_training_menu(screen, fonts, background, candidate, index, total):
    screen.blit(background, (0, 0))
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((8, 10, 11, 212))
    screen.blit(shade, (0, 0))
    width, height = screen.get_size()
    panel = pygame.Rect(0, 0, min(760, width - 80), 430)
    panel.center = (width // 2, height // 2)
    pygame.draw.rect(screen, (28, 31, 32), panel, border_radius=6)
    pygame.draw.rect(screen, (128, 110, 71), panel, 1, border_radius=6)

    hero_id = str(candidate["hero_id"])
    name = HERO_LABELS.get(hero_id, hero_id)
    current = int(candidate["current_level"])
    target = int(candidate["target_level"])
    penalty = int(candidate["penalty"])
    title = fonts["heading"].render("战前培养", True, COLORS["accent"])
    screen.blit(title, (panel.x + 42, panel.y + 32))
    counter = fonts["body"].render(f"{index + 1} / {total}", True, COLORS["muted"])
    screen.blit(counter, (panel.right - counter.get_width() - 42, panel.y + 42))
    hero = fonts["title"].render(name, True, COLORS["text"])
    screen.blit(hero, (panel.x + 42, panel.y + 104))
    detail = fonts["body"].render(
        f"当前 Lv {current}    本关平均 Lv {target}", True, COLORS["text"]
    )
    screen.blit(detail, (panel.x + 42, panel.y + 164))
    note = fonts["body"].render(
        f"选择培养追平后升至 Lv {target}", True, COLORS["muted"]
    )
    cost = fonts["body"].render(
        f"培养代价：五维永久各降低 {penalty} 点", True, COLORS["muted"]
    )
    screen.blit(note, (panel.x + 42, panel.y + 208))
    screen.blit(cost, (panel.x + 42, panel.y + 246))

    keep_rect = pygame.Rect(panel.x + 42, panel.bottom - 92, 280, 52)
    train_rect = pygame.Rect(panel.right - 322, panel.bottom - 92, 280, 52)
    pygame.draw.rect(screen, (67, 72, 75), keep_rect, border_radius=4)
    pygame.draw.rect(screen, (128, 110, 71), train_rect, border_radius=4)
    keep = fonts["title"].render("保持原等级", True, COLORS["text"])
    train = fonts["title"].render("培养追平", True, COLORS["text"])
    screen.blit(keep, keep.get_rect(center=keep_rect.center))
    screen.blit(train, train.get_rect(center=train_rect.center))
    pygame.display.flip()
    return keep_rect, train_rect


def run_training_menu(screen, fonts, background, env):
    candidates = env.training_options()
    clock = pygame.time.Clock()
    for index, candidate in enumerate(candidates):
        decided = False
        while not decided:
            keep_rect, train_rect = _draw_training_menu(
                screen, fonts, background, candidate, index, len(candidates)
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        decided = True
                    elif event.key == pygame.K_RETURN:
                        env.train_commander(str(candidate["hero_id"]))
                        decided = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if keep_rect.collidepoint(event.pos):
                        decided = True
                    elif train_rect.collidepoint(event.pos):
                        env.train_commander(str(candidate["hero_id"]))
                        decided = True
            clock.tick(60)
    return "continue"


def run_shop_menu(screen, fonts, background, env):
    pygame.display.set_mode(SCREEN_SIZE)
    if env.training_options():
        if run_training_menu(screen, fonts, background, env) == "quit":
            return "quit", env.supply_info()
    return _original_run_shop_menu(screen, fonts, background, env)

# Playable enemy turns use rolling beam, then HAPPO/CQL if planning is unavailable.
from rl.runtime_policy import RuntimeBattlePolicy


_runtime_battle_policy = RuntimeBattlePolicy()


def ppo_tactical_action(model, env, actions, observation, width, height):
    del model
    perspective = enemy_perspective(observation)
    return _runtime_battle_policy.choose(
        env, actions, perspective, width, height
    )
if getattr(sys, "frozen", False):
    _bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    DEFAULT_ASSETS_ROOT = _bundle_root / "assets" / "lzc"

    def find_executable(value):
        if value is not None:
            return Path(value)
        executable = _bundle_root / "native" / "mengde_rl.exe"
        if not executable.is_file():
            raise FileNotFoundError(f"Bundled battle engine is missing: {executable}")
        return executable

# Battle commands now live beside the acting unit; the legacy right panel is clipped.
SCREEN_SIZE = (1280, 756)
BATTLE_SCREEN_SIZE = (1280, 756)
BATTLE_LOAD_BUTTON = pygame.Rect(1136, 560, 124, 34)
CAMERA_UP_BUTTON = pygame.Rect(994, 516, 124, 34)
CAMERA_DOWN_BUTTON = pygame.Rect(1136, 516, 124, 34)
STORY_DIALOG_RECT = pygame.Rect(20, 500, 932, 226)
_original_run_slot_menu = run_slot_menu
_battle_load_requested = False


def run_slot_menu(screen, fonts, background, mode):
    """Reuse the slot screen for in-battle loading without leaving the battle loop."""
    global _battle_context_enabled, _battle_load_requested
    caller = sys._getframe(1)
    requested_battle_load = bool(mode == "save" and _battle_load_requested)
    _battle_load_requested = False
    previous_context = _battle_context_enabled
    _battle_context_enabled = False
    try:
        action, slot = _original_run_slot_menu(
            screen, fonts, background, "load" if requested_battle_load else mode
        )
    finally:
        _battle_context_enabled = previous_context

    if not requested_battle_load or action != "load" or slot is None:
        return action, slot

    loader = caller.f_locals.get("load_saved_game")
    if not callable(loader):
        return "cancel", None
    try:
        loader(int(slot))
    except (SaveFormatError, ValueError, OSError) as error:
        battle_log = caller.f_locals.get("log")
        if isinstance(battle_log, list):
            battle_log.append(str(error))
    return "cancel", None


def _draw_docked_story_dialogue(screen, fonts, story, portraits):
    if isinstance(story, dict):
        title = str(story.get("speaker", ""))
        body = str(story.get("text", ""))
        footer = str(story.get("footer", ""))
    else:
        values = list(story) + ["", "", ""]
        title, body, footer = (str(values[0]), str(values[1]), str(values[2]))

    panel = STORY_DIALOG_RECT
    pygame.draw.rect(screen, (20, 23, 25), panel)
    pygame.draw.rect(screen, (130, 114, 75), panel, 2)
    portrait = portrait_for_speaker(title, portraits)
    content_x = panel.x + 28
    if portrait is not None:
        face = pygame.transform.smoothscale(portrait, (112, 112))
        screen.blit(face, (panel.x + 24, panel.y + 48))
        pygame.draw.rect(screen, (130, 114, 75), pygame.Rect(panel.x + 24, panel.y + 48, 112, 112), 1)
        content_x = panel.x + 160

    show_title = bool(title and title not in NO_PORTRAIT_SPEAKERS)
    body_y = panel.y + 30
    if show_title:
        screen.blit(fonts["title"].render(title, True, COLORS["accent"]), (content_x, body_y))
        body_y += 38
    max_width = panel.right - content_x - 28
    for line in wrap_text_to_width(body, fonts["body"], max_width)[:5]:
        screen.blit(fonts["body"].render(line, True, COLORS["text"]), (content_x, body_y))
        body_y += 28
    if footer:
        footer_surface = fonts["small"].render(footer, True, COLORS["muted"])
        screen.blit(footer_surface, (panel.right - footer_surface.get_width() - 24, panel.bottom - 30))
_original_context_run_title_menu = run_title_menu


def run_title_menu(screen, fonts, background, can_continue):
    pygame.display.set_mode(SCREEN_SIZE)
    return _original_context_run_title_menu(screen, fonts, background, can_continue)
TITLE_NEW_BUTTON.update(910, 416, 270, 48)
TITLE_CONTINUE_BUTTON.update(910, 474, 270, 48)
TITLE_LOAD_BUTTON.update(910, 532, 270, 48)
TITLE_EXIT_BUTTON.update(910, 590, 270, 48)
CLASS_LABELS.update({"King": "\u541b\u738b"})
SKILL_LABELS.update({"inspire_0": "\u9f13\u821e", "baqi_0": "\u9738\u6c14"})
SKILL_RANGES.update({"inspire_0": 3, "baqi_0": 3})
STATUS_BUTTON = pygame.Rect(-200, -200, 92, 34)
ITEM_BUTTON = pygame.Rect(-200, -200, 92, 34)
SKILL_BUTTON = pygame.Rect(-200, -200, 92, 34)
CONTEXT_CLOSE_BUTTON = pygame.Rect(-200, -200, 34, 34)
ITEM_BACK_BUTTON = pygame.Rect(-200, -200, 92, 32)
SKILL_OPTION_BUTTONS = [pygame.Rect(-200, -200, 174, 32) for _ in range(3)]
SKILL_BACK_BUTTON = pygame.Rect(-200, -200, 174, 30)
CANCEL_BUTTON = pygame.Rect(-300, -300, 1, 1)
_active_cell = 48
_context_view_mode = None
_context_selected_id = None
_context_auto_inspected_id = None
_context_menu_active = False
_context_has_skills = False
_battle_context_enabled = False
_context_selected_cell = None
_original_event_get = pygame.event.get


def _hide_context_buttons():
    for rect in (
        STATUS_BUTTON, ITEM_BUTTON, SKILL_BUTTON, WAIT_BUTTON, ATTACK_BUTTON,
        HP_ITEM_BUTTON, MP_ITEM_BUTTON, ITEM_BACK_BUTTON, SKILL_BACK_BUTTON,
        CONTEXT_CLOSE_BUTTON, *SKILL_OPTION_BUTTONS,
    ):
        rect.update(-300, -300, max(1, rect.width), max(1, rect.height))


def _click_hits_selected_unit(frame, position):
    """Recognize a selected-unit click only outside skill target mode."""
    state = frame.f_locals
    selected = state.get("selected_unit")
    if selected is None or state.get("target_mode") is not None:
        return False
    detail = _selected_detail(state.get("unit_details", []), selected)
    if detail is None:
        return False
    cell_x = (int(position[0]) - BOARD_ORIGIN[0]) // _active_cell
    cell_y = (int(position[1]) - BOARD_ORIGIN[1]) // _active_cell
    return (cell_x, cell_y) == (int(detail["x"]), int(detail["y"]))

def _cancel_selection_from_frame(frame):
    global _context_view_mode, _context_menu_active, _context_selected_cell
    state = frame.f_locals
    cleared_cell = _context_selected_cell is not None
    _context_selected_cell = None
    reset_selection = state.get("reset_selection")
    if (
        state.get("selected_unit") is None
        or state.get("action_animation") is not None
        or state.get("preview_move") is not None
        or not callable(reset_selection)
    ):
        return cleared_cell
    reset_selection()
    _context_view_mode = None
    _context_menu_active = False
    return True



def _context_event_get(*args, **kwargs):
    global _context_view_mode, _context_menu_active, _battle_context_enabled, _battle_load_requested, _context_has_skills
    global _context_selected_cell
    events = _original_event_get(*args, **kwargs)
    if not _battle_context_enabled:
        return events

    caller = sys._getframe(1)
    forwarded = []
    for event in events:
        if _battle_camera["map"] is not None:
            step = max(32, _active_cell * 4)
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and CAMERA_UP_BUTTON.collidepoint(event.pos)
            ):
                _move_battle_camera(dy=-_DEFAULT_BOARD_LIMIT[1])
                continue
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and CAMERA_DOWN_BUTTON.collidepoint(event.pos)
            ):
                _move_battle_camera(dy=_DEFAULT_BOARD_LIMIT[1])
                continue
            if event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    _move_battle_camera(dx=-event.y * step)
                else:
                    _move_battle_camera(dy=-event.y * step)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                _move_battle_camera(dy=(-step if event.button == 4 else step))
                continue
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                pygame.K_PAGEUP, pygame.K_PAGEDOWN,
            ):
                if event.key == pygame.K_UP:
                    _move_battle_camera(dy=-step)
                elif event.key == pygame.K_DOWN:
                    _move_battle_camera(dy=step)
                elif event.key == pygame.K_LEFT:
                    _move_battle_camera(dx=-step)
                elif event.key == pygame.K_RIGHT:
                    _move_battle_camera(dx=step)
                elif event.key == pygame.K_PAGEUP:
                    _move_battle_camera(dy=-_DEFAULT_BOARD_LIMIT[1])
                else:
                    _move_battle_camera(dy=_DEFAULT_BOARD_LIMIT[1])
                continue
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if _context_view_mode is not None:
                _context_view_mode = None
                continue
            if _cancel_selection_from_frame(caller):
                continue
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if _context_view_mode is not None:
                _context_view_mode = None
                continue
            if _cancel_selection_from_frame(caller):
                continue
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            forwarded.append(event)
            continue
        if BATTLE_LOAD_BUTTON.collidepoint(event.pos):
            _context_selected_cell = None
            _battle_load_requested = True
            forwarded.append(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"button": 1, "pos": BATTLE_SAVE_BUTTON.center},
            ))
            continue
        if BATTLE_SAVE_BUTTON.collidepoint(event.pos):
            forwarded.append(event)
            continue
        if BATTLE_TITLE_BUTTON.collidepoint(event.pos):
            _context_selected_cell = None
            _context_view_mode = None
            _context_menu_active = False
            _battle_context_enabled = False
            forwarded.append(event)
            continue
        if _context_view_mode == "status":
            if CONTEXT_CLOSE_BUTTON.collidepoint(event.pos):
                _context_view_mode = None
            continue
        if _context_view_mode == "items" and ITEM_BACK_BUTTON.collidepoint(event.pos):
            _context_view_mode = None
            continue
        if _context_view_mode == "skills":
            if SKILL_BACK_BUTTON.collidepoint(event.pos):
                _context_view_mode = None
                continue
            clicked_index = next(
                (index for index, rect in enumerate(SKILL_OPTION_BUTTONS) if rect.collidepoint(event.pos)),
                None,
            )
            if clicked_index is not None:
                _context_view_mode = None
                forwarded.append(pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    {"button": 1, "pos": (PANEL_X + 8, 520 + clicked_index * 30)},
                ))
                continue
        if _context_menu_active and STATUS_BUTTON.collidepoint(event.pos):
            _context_view_mode = "status"
            continue
        if _context_menu_active and ITEM_BUTTON.collidepoint(event.pos):
            _context_view_mode = "items"
            continue
        if _context_menu_active and _context_has_skills and SKILL_BUTTON.collidepoint(event.pos):
            _context_view_mode = "skills"
            continue
        # The clipped legacy panel must not retain invisible click targets.
        if event.pos[0] >= 972:
            continue
        cell = _grid_cell_at_screen_position(caller.f_locals.get("terrain", []), event.pos)
        if cell is not None:
            cell_x, cell_y, _ = cell
            occupied = any(
                int(detail.get("x", -1)) == cell_x
                and int(detail.get("y", -1)) == cell_y
                and not detail.get("dead", False)
                for detail in caller.f_locals.get("unit_details", [])
            )
            if occupied or caller.f_locals.get("selected_unit") is not None:
                _context_selected_cell = None
            elif (
                caller.f_locals.get("target_mode") is None
                and caller.f_locals.get("action_animation") is None
                and caller.f_locals.get("preview_move") is None
            ):
                _context_selected_cell = (cell_x, cell_y)
        # A second left click on the selected unit confirms its current cell.
        # The preserved battle loop then opens the action menu without moving.
        forwarded.append(event)
    return forwarded


pygame.event.get = _context_event_get


def _selected_detail(unit_details, selected_unit):
    if selected_unit is None:
        return None
    return next(
        (detail for detail in unit_details if int(detail["id"]) == int(selected_unit)),
        None,
    )


def _place_context_menu(destination):
    global STATUS_BUTTON, ITEM_BUTTON, SKILL_BUTTON, WAIT_BUTTON, ATTACK_BUTTON
    cell_x = BOARD_ORIGIN[0] + int(destination[0]) * _active_cell
    cell_y = BOARD_ORIGIN[1] + int(destination[1]) * _active_cell
    width, height, gap = 92, 34, 4
    menu_w, menu_h = width * 2 + gap, height * 3 + gap * 2
    x = cell_x + _active_cell + 8
    if x + menu_w > 972:
        x = cell_x - menu_w - 8
    x = max(20, min(972 - menu_w, x))
    y = max(36, min(716 - menu_h, cell_y - 12))
    STATUS_BUTTON.update(x, y, width, height)
    ITEM_BUTTON.update(x + width + gap, y, width, height)
    ATTACK_BUTTON.update(x, y + height + gap, width, height)
    WAIT_BUTTON.update(x + width + gap, y + height + gap, width, height)
    SKILL_BUTTON.update(x, y + (height + gap) * 2, menu_w, height)


def _place_item_menu(destination):
    cell_x = BOARD_ORIGIN[0] + int(destination[0]) * _active_cell
    cell_y = BOARD_ORIGIN[1] + int(destination[1]) * _active_cell
    width = 174
    x = cell_x + _active_cell + 8
    if x + width > 972:
        x = cell_x - width - 8
    x = max(20, min(972 - width, x))
    y = max(36, min(716 - 110, cell_y - 8))
    HP_ITEM_BUTTON.update(x, y, width, 34)
    MP_ITEM_BUTTON.update(x, y + 38, width, 34)
    ITEM_BACK_BUTTON.update(x, y + 76, width, 30)


def _place_skill_menu(destination):
    cell_x = BOARD_ORIGIN[0] + int(destination[0]) * _active_cell
    cell_y = BOARD_ORIGIN[1] + int(destination[1]) * _active_cell
    width = 174
    x = cell_x + _active_cell + 8
    if x + width > 972:
        x = cell_x - width - 8
    x = max(20, min(972 - width, x))
    y = max(36, min(716 - 140, cell_y - 8))
    for index, rect in enumerate(SKILL_OPTION_BUTTONS):
        rect.update(x, y + index * 34, width, 32)
    SKILL_BACK_BUTTON.update(x, y + 104, width, 30)


def _draw_context_commands(screen, fonts, detail, destination, inventory):
    if _context_view_mode == "items":
        medicine = int(inventory.get("medicine", {}).get("count", 0))
        powder = int(inventory.get("spirit_powder", {}).get("count", 0))
        can_use = int(detail["force"]) == 1 and not bool(detail["done"])
        button(screen, fonts["small"], HP_ITEM_BUTTON, f"金疮药  x{medicine}", can_use and medicine > 0)
        button(screen, fonts["small"], MP_ITEM_BUTTON, f"清心散  x{powder}", can_use and powder > 0)
        button(screen, fonts["small"], ITEM_BACK_BUTTON, "返回", True)
        return

    if _context_view_mode == "skills":
        skills = sorted(detail.get("skills", []), key=lambda skill: str(skill.get("id", "")))[:3]
        for index, rect in enumerate(SKILL_OPTION_BUTTONS):
            if index >= len(skills):
                continue
            skill = skills[index]
            skill_id = str(skill.get("id", ""))
            mp_cost = int(skill.get("mp", 0))
            label = SKILL_LABELS.get(skill_id, skill_id)
            enabled = int(detail.get("mp", 0)) >= mp_cost
            button(screen, fonts["small"], rect, f"{label}  MP {mp_cost}", enabled)
        if not skills:
            button(screen, fonts["small"], SKILL_OPTION_BUTTONS[0], "无可用技能", False)
        button(screen, fonts["small"], SKILL_BACK_BUTTON, "返回", True)
        return
    button(screen, fonts["small"], STATUS_BUTTON, "状态", True)
    button(screen, fonts["small"], ITEM_BUTTON, "物品", True)
    button(screen, fonts["small"], ATTACK_BUTTON, "攻击", True)
    button(screen, fonts["small"], WAIT_BUTTON, "待机", True)
    button(screen, fonts["small"], SKILL_BUTTON, "技能", bool(detail.get("skills", [])))


def _draw_status_window(screen, fonts, detail, portraits):
    panel = pygame.Rect(174, 126, 646, 464)
    pygame.draw.rect(screen, (24, 27, 29), panel, border_radius=4)
    pygame.draw.rect(screen, (134, 121, 82), panel, 1, border_radius=4)
    CONTEXT_CLOSE_BUTTON.update(panel.right - 44, panel.y + 10, 32, 32)
    pygame.draw.rect(screen, (54, 58, 60), CONTEXT_CLOSE_BUTTON, border_radius=3)
    close_text = fonts["title"].render("×", True, COLORS["text"])
    screen.blit(close_text, close_text.get_rect(center=CONTEXT_CLOSE_BUTTON.center))

    portrait = portrait_for_unit(detail, portraits)
    if portrait is not None:
        face = pygame.transform.smoothscale(portrait, (112, 112))
        screen.blit(face, (panel.x + 30, panel.y + 36))

    hero_id = str(detail.get("name", ""))
    name = HERO_LABELS.get(hero_id, hero_id)
    unit_class = CLASS_LABELS.get(str(detail.get("class", "")), str(detail.get("class", "")))
    heading = fonts["heading"].render(name, True, COLORS["accent"])
    screen.blit(heading, (panel.x + 166, panel.y + 38))
    subtitle = fonts["body"].render(
        f"{unit_class}    Lv.{int(detail.get('level', 1))}    EXP {int(detail.get('exp', 0))}/100",
        True, COLORS["text"],
    )
    screen.blit(subtitle, (panel.x + 166, panel.y + 82))
    hp_mp = fonts["body"].render(
        f"HP {int(detail.get('hp', 0))}/{int(detail.get('max_hp', 0))}    "
        f"MP {int(detail.get('mp', 0))}/{int(detail.get('max_mp', 0))}",
        True, COLORS["text"],
    )
    screen.blit(hp_mp, (panel.x + 166, panel.y + 118))

    stats = (
        f"攻击 {int(detail.get('atk', 0))}    防御 {int(detail.get('def', 0))}    "
        f"精神 {int(detail.get('int', 0))}    爆发 {int(detail.get('dex', 0))}    "
        f"士气 {int(detail.get('mor', 0))}"
    )
    screen.blit(fonts["body"].render(stats, True, COLORS["text"]), (panel.x + 30, panel.y + 184))
    terrain = _unit_terrain_display(detail)
    terrain_line = (
        f"地形：{terrain}    能力 {int(detail.get('terrain_effect', 100))}%    "
        f"移动消耗 {int(detail.get('move_cost', 1))}"
    )
    screen.blit(fonts["body"].render(terrain_line, True, COLORS["muted"]), (panel.x + 30, panel.y + 224))

    skills = detail.get("skills", [])
    skill_names = [
        SKILL_LABELS.get(
            str(skill.get("id", "")) if isinstance(skill, dict) else str(skill),
            str(skill.get("id", "")) if isinstance(skill, dict) else str(skill),
        )
        for skill in skills
    ]
    skill_line = "策略：" + ("、".join(skill_names) if skill_names else "无")
    screen.blit(fonts["body"].render(skill_line, True, COLORS["text"]), (panel.x + 30, panel.y + 266))

    bio = HERO_BIOS.get(hero_id, "暂无生平记载。")
    screen.blit(fonts["body"].render("生平", True, COLORS["accent"]), (panel.x + 30, panel.y + 316))
    for index, line in enumerate(wrap_text_to_width(bio, fonts["body"], panel.width - 60)[:4]):
        rendered = fonts["body"].render(line, True, COLORS["text"])
        screen.blit(rendered, (panel.x + 30, panel.y + 352 + index * 27))


def _terrain_display_name(primary, index=None):
    primary = str(primary or "")
    return TERRAIN_LABELS.get(primary, primary)


def _unit_terrain_display(detail):
    primary = str(detail.get("primary_terrain", detail.get("terrain", "")))
    return TERRAIN_LABELS.get(primary, primary)


def _grid_cell_at_screen_position(terrain, position):
    if not terrain:
        return None
    mouse_x, mouse_y = position
    if not (20 <= mouse_x < 972 and 36 <= mouse_y < 716):
        return None
    cell_x = (mouse_x - BOARD_ORIGIN[0]) // _active_cell
    cell_y = (mouse_y - BOARD_ORIGIN[1]) // _active_cell
    if cell_x < 0 or cell_y < 0:
        return None
    if _battle_camera["map"] is not None:
        width = max(1, int(_battle_camera["width"]) // _active_cell)
    else:
        width = max(1, int(BOARD_LIMIT[0]) // _active_cell)
    index = int(cell_y) * width + int(cell_x)
    if index < 0 or index >= len(terrain):
        return None
    return int(cell_x), int(cell_y), str(terrain[index])


def _terrain_at_screen_position(terrain, position):
    cell = _grid_cell_at_screen_position(terrain, position)
    return cell[2] if cell is not None else None


def _terrain_index_for_cell(cell, terrain):
    if cell is None or not terrain:
        return None
    if _battle_camera["map"] is not None:
        width = max(1, int(_battle_camera["width"]) // _active_cell)
    else:
        width = max(1, int(BOARD_LIMIT[0]) // _active_cell)
    index = int(cell[1]) * width + int(cell[0])
    return index if 0 <= index < len(terrain) else None


def _draw_selected_cell_highlight(screen, terrain):
    if _context_selected_cell is None or not terrain:
        return
    cell_x, cell_y = _context_selected_cell
    rect = pygame.Rect(
        BOARD_ORIGIN[0] + cell_x * _active_cell,
        BOARD_ORIGIN[1] + cell_y * _active_cell,
        _active_cell,
        _active_cell,
    )
    viewport = pygame.Rect(20, 36, 952, 680)
    if not viewport.contains(rect):
        return
    fill = pygame.Surface(rect.size, pygame.SRCALPHA)
    fill.fill((*COLORS["accent"], 48))
    screen.blit(fill, rect.topleft)
    pygame.draw.rect(screen, COLORS["accent"], rect, 3)


def _draw_fixed_info_panel(
    screen, fonts, info, unit_details, selected_unit, portraits,
    battle_title, objective, enemy_name, log, terrain,
):
    panel = pygame.Rect(984, 0, 296, 756)
    gutter = pygame.Rect(972, 0, 12, 756)
    screen.fill((13, 15, 17), gutter)
    screen.fill((24, 27, 30), panel)
    pygame.draw.line(screen, (119, 108, 76), (984, 0), (984, 756), 2)
    inner_x = 994
    max_width = 266

    current_force = int(info.get("current_force", 1))
    force_name = {1: "我方回合", 2: "友军回合", 4: "敌方回合"}.get(current_force, "回合切换")
    screen.blit(fonts["heading"].render(str(battle_title), True, COLORS["text"]), (inner_x, 24))
    force_color = COLORS["accent"] if current_force == 1 else COLORS["enemy"]
    screen.blit(fonts["title"].render(force_name, True, force_color), (inner_x, 66))
    turn_line = f"第 {int(info.get('turn_current', 1))} / {int(info.get('turn_limit', 20))} 回合"
    screen.blit(fonts["body"].render(turn_line, True, COLORS["text"]), (inner_x, 102))

    y = 140
    screen.blit(fonts["small"].render("目标", True, COLORS["accent"]), (inner_x, y))
    y += 25
    for line in wrap_text_to_width(str(objective), fonts["small"], max_width)[:3]:
        screen.blit(fonts["small"].render(line, True, COLORS["text"]), (inner_x, y))
        y += 22
    screen.blit(fonts["tiny"].render(f"敌军控制：{enemy_name}", True, COLORS["muted"]), (inner_x, y + 4))
    y += 36
    pygame.draw.line(screen, (68, 73, 76), (inner_x, y), (1260, y), 1)
    y += 14

    detail = _selected_detail(unit_details, selected_unit)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_cell = _grid_cell_at_screen_position(terrain, (mouse_x, mouse_y))
    hovered_terrain = hovered_cell[2] if hovered_cell is not None else None
    hovered_index = _terrain_index_for_cell(hovered_cell, terrain)
    if 20 <= mouse_x < 972 and 36 <= mouse_y < 716:
        cell_x = (mouse_x - BOARD_ORIGIN[0]) // _active_cell
        cell_y = (mouse_y - BOARD_ORIGIN[1]) // _active_cell
        hovered = next(
            (entry for entry in unit_details
             if int(entry["x"]) == cell_x and int(entry["y"]) == cell_y
             and not entry.get("dead", False)),
            None,
        )
        if hovered is not None:
            detail = hovered

    selected_terrain = None
    if _context_selected_cell is not None and terrain:
        selected_x, selected_y = _context_selected_cell
        if _battle_camera["map"] is not None:
            map_width = max(1, int(_battle_camera["width"]) // _active_cell)
        else:
            map_width = max(1, int(BOARD_LIMIT[0]) // _active_cell)
        selected_index = selected_y * map_width + selected_x
        if 0 <= selected_index < len(terrain):
            selected_terrain = str(terrain[selected_index])

    shown_terrain = selected_terrain or hovered_terrain
    shown_index = selected_index if selected_terrain is not None else hovered_index
    if detail is None and shown_terrain is not None:
        terrain_name = _terrain_display_name(shown_terrain, shown_index)
        heading = "已选地格" if selected_terrain is not None else "鼠标位置"
        screen.blit(fonts["small"].render(heading, True, COLORS["accent"]), (inner_x, y))
        screen.blit(fonts["title"].render(terrain_name, True, COLORS["text"]), (inner_x, y + 28))
        if selected_terrain is not None:
            coordinate = f"第 {selected_x + 1} 列，第 {selected_y + 1} 行"
            screen.blit(fonts["tiny"].render(coordinate, True, COLORS["muted"]), (inner_x, y + 55))
        y += 82

    if detail is not None:
        hero_id = str(detail.get("name", ""))
        name = HERO_LABELS.get(hero_id, hero_id)
        unit_class = CLASS_LABELS.get(str(detail.get("class", "")), str(detail.get("class", "")))
        portrait = portrait_for_unit(detail, portraits)
        if portrait is not None:
            face = pygame.transform.smoothscale(portrait, (58, 58))
            screen.blit(face, (inner_x + 208, y))
            pygame.draw.rect(screen, COLORS["accent"], pygame.Rect(inner_x + 208, y, 58, 58), 1)
        screen.blit(fonts["title"].render(name, True, COLORS["text"]), (inner_x, y))
        screen.blit(
            fonts["small"].render(
                f"{unit_class}  Lv.{int(detail.get('level', 1))}  EXP {int(detail.get('exp', 0))}/100",
                True, COLORS["muted"],
            ),
            (inner_x, y + 34),
        )
        y += 72
        lines = [
            f"HP {int(detail.get('hp', 0))}/{int(detail.get('max_hp', 0))}   MP {int(detail.get('mp', 0))}/{int(detail.get('max_mp', 0))}",
            f"攻击 {int(detail.get('atk', 0))}   防御 {int(detail.get('def', 0))}   精神 {int(detail.get('int', 0))}",
            f"爆发 {int(detail.get('dex', 0))}   士气 {int(detail.get('mor', 0))}",
            f"地形 {_unit_terrain_display(detail)}   能力 {int(detail.get('terrain_effect', 100))}%",
        ]
        for line in lines:
            screen.blit(fonts["small"].render(line, True, COLORS["text"]), (inner_x, y))
            y += 23
        bio = HERO_BIOS.get(hero_id)
        if bio:
            y += 4
            screen.blit(fonts["small"].render("生平", True, COLORS["accent"]), (inner_x, y))
            y += 23
            for line in wrap_text_to_width(str(bio), fonts["tiny"], max_width)[:4]:
                screen.blit(fonts["tiny"].render(line, True, COLORS["muted"]), (inner_x, y))
                y += 18

    CAMERA_UP_BUTTON.update(inner_x, 516, 124, 34)
    CAMERA_DOWN_BUTTON.update(inner_x + 142, 516, 124, 34)
    button(screen, fonts["small"], CAMERA_UP_BUTTON, "↑ 上一屏", _battle_camera["y"] > 0)
    camera_max_y = max(0, int(_battle_camera["height"]) - _DEFAULT_BOARD_LIMIT[1])
    button(
        screen, fonts["small"], CAMERA_DOWN_BUTTON, "↓ 下一屏",
        _battle_camera["map"] is not None and int(_battle_camera["y"]) < camera_max_y,
    )

    BATTLE_SAVE_BUTTON.update(inner_x, 560, 124, 34)
    BATTLE_LOAD_BUTTON.update(inner_x + 142, 560, 124, 34)
    button(screen, fonts["small"], BATTLE_SAVE_BUTTON, "存档", True)
    button(screen, fonts["small"], BATTLE_LOAD_BUTTON, "读档", True)

    log_y = 620
    pygame.draw.line(screen, (68, 73, 76), (inner_x, log_y - 12), (1260, log_y - 12), 1)
    screen.blit(fonts["small"].render("战况", True, COLORS["accent"]), (inner_x, log_y))
    log_y += 25
    for entry in [str(value) for value in log[-4:]]:
        for line in wrap_text_to_width(entry, fonts["tiny"], max_width)[:2]:
            if log_y > 738:
                break
            screen.blit(fonts["tiny"].render(line, True, COLORS["muted"]), (inner_x, log_y))
            log_y += 18

def _draw_hover_summary(screen, fonts, unit_details, terrain):
    if _context_view_mode is not None:
        return
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if not (20 <= mouse_x < 972 and 36 <= mouse_y < 716):
        return
    cell_x = (mouse_x - BOARD_ORIGIN[0]) // _active_cell
    cell_y = (mouse_y - BOARD_ORIGIN[1]) // _active_cell
    detail = next(
        (entry for entry in unit_details if int(entry["x"]) == cell_x and int(entry["y"]) == cell_y and not entry.get("dead", False)),
        None,
    )
    if detail is None:
        terrain_cell = _grid_cell_at_screen_position(terrain, (mouse_x, mouse_y))
        if terrain_cell is None:
            return
        terrain_id = terrain_cell[2]
        terrain_index = _terrain_index_for_cell(terrain_cell, terrain)
        text = f"地形  {_terrain_display_name(terrain_id, terrain_index)}"
        surface = fonts["small"].render(text, True, COLORS["text"])
        rect = surface.get_rect()
        rect.x = min(972 - rect.width - 16, mouse_x + 16)
        rect.y = max(36, mouse_y - rect.height - 12)
        background = rect.inflate(16, 10)
        pygame.draw.rect(screen, (25, 28, 30), background, border_radius=3)
        pygame.draw.rect(screen, (113, 104, 76), background, 1, border_radius=3)
        screen.blit(surface, rect)
        return
    hero_id = str(detail.get("name", ""))
    name = HERO_LABELS.get(hero_id, hero_id)
    unit_class = CLASS_LABELS.get(str(detail.get("class", "")), str(detail.get("class", "")))
    text = f"{name}  {unit_class}  Lv.{int(detail.get('level', 1))}  HP {int(detail.get('hp', 0))}/{int(detail.get('max_hp', 0))}"
    surface = fonts["small"].render(text, True, COLORS["text"])
    rect = surface.get_rect()
    rect.x = min(972 - rect.width - 16, mouse_x + 16)
    rect.y = max(36, mouse_y - rect.height - 12)
    background = rect.inflate(16, 10)
    pygame.draw.rect(screen, (25, 28, 30), background, border_radius=3)
    pygame.draw.rect(screen, (113, 104, 76), background, 1, border_radius=3)
    screen.blit(surface, rect)

_DEFAULT_BOARD_ORIGIN = (20, 36)
_DEFAULT_BOARD_LIMIT = (952, 680)
_LARGE_BATTLE_MAPS = {
    "m006.jpg": (26, 28, 48),
    "m008-large-v2.png": (30, 22, 48),
}
_battle_camera = {"map": None, "x": 0, "y": 0, "width": 0, "height": 0}

_original_load_battle_map = load_battle_map
_original_fit_battle_map = fit_battle_map
_original_draw = draw


def load_battle_map(assets_root, map_name):
    """Select a native-sized scrolling canvas for maps larger than the viewport."""
    global BOARD_ORIGIN, BOARD_LIMIT
    surface = _original_load_battle_map(assets_root, map_name)
    layout = _LARGE_BATTLE_MAPS.get(map_name)
    if layout is None:
        _battle_camera.update(map=None, x=0, y=0, width=0, height=0)
        BOARD_ORIGIN = _DEFAULT_BOARD_ORIGIN
        BOARD_LIMIT = _DEFAULT_BOARD_LIMIT
        return surface

    width, height, cell = layout
    _battle_camera.update(
        map=map_name,
        x=(17 * cell if map_name == "m064.png" else 0),
        y=(4 * cell if map_name == "m064.png" else 0),
        width=width * cell,
        height=height * cell,
    )
    BOARD_LIMIT = (width * cell, height * cell)
    BOARD_ORIGIN = _DEFAULT_BOARD_ORIGIN
    return surface


def fit_battle_map(source, width, height, cell):
    global _active_cell
    _active_cell = cell
    target_size = (width * cell, height * cell)
    if _battle_camera["map"] is not None and source.get_size() == target_size:
        return source.copy()
    return _original_fit_battle_map(source, width, height, cell)


def _clamp_battle_camera():
    if _battle_camera["map"] is None:
        return
    view_w, view_h = _DEFAULT_BOARD_LIMIT
    max_x = max(0, int(_battle_camera["width"]) - view_w)
    max_y = max(0, int(_battle_camera["height"]) - view_h)
    _battle_camera["x"] = max(0, min(max_x, int(_battle_camera["x"])))
    _battle_camera["y"] = max(0, min(max_y, int(_battle_camera["y"])))


def _move_battle_camera(dx=0, dy=0):
    if _battle_camera["map"] is None:
        return
    _battle_camera["x"] = int(_battle_camera["x"]) + int(dx)
    _battle_camera["y"] = int(_battle_camera["y"]) + int(dy)
    _clamp_battle_camera()


def _scroll_large_battle_map():
    global BOARD_ORIGIN
    if _battle_camera["map"] is None:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()
    view_x, view_y = _DEFAULT_BOARD_ORIGIN
    view_w, view_h = _DEFAULT_BOARD_LIMIT
    horizontal_edge = 64
    top_edge = 64
    bottom_edge = 104

    def scroll_speed(distance, edge):
        proximity = max(0.0, min(1.0, (edge - distance) / edge))
        return int(10 + 24 * proximity)

    if view_y <= mouse_y < view_y + view_h:
        left_distance = mouse_x - view_x
        right_distance = view_x + view_w - 1 - mouse_x
        if 0 <= left_distance < horizontal_edge:
            _battle_camera["x"] -= scroll_speed(left_distance, horizontal_edge)
        elif 0 <= right_distance < horizontal_edge:
            _battle_camera["x"] += scroll_speed(right_distance, horizontal_edge)
    if view_x <= mouse_x < view_x + view_w:
        top_distance = mouse_y - view_y
        bottom_distance = view_y + view_h - 1 - mouse_y
        if 0 <= top_distance < top_edge:
            _battle_camera["y"] -= scroll_speed(top_distance, top_edge)
        elif 0 <= bottom_distance < bottom_edge:
            _battle_camera["y"] += scroll_speed(bottom_distance, bottom_edge)

    max_x = max(0, _battle_camera["width"] - view_w)
    max_y = max(0, _battle_camera["height"] - view_h)
    _battle_camera["x"] = max(0, min(max_x, _battle_camera["x"]))
    _battle_camera["y"] = max(0, min(max_y, _battle_camera["y"]))
    BOARD_ORIGIN = (
        view_x - _battle_camera["x"],
        view_y - _battle_camera["y"],
    )


def _ensure_chengpu_camera(terrain, battle_map):
    global BOARD_ORIGIN, BOARD_LIMIT
    if len(terrain or []) != 64 * 42:
        return
    if battle_map is not None and hasattr(battle_map, "get_size"):
        if tuple(battle_map.get_size()) != (64 * 32, 42 * 32):
            return
    if _battle_camera["map"] != "m064.png":
        _battle_camera.update(
            map="m064.png", x=17 * 32, y=4 * 32,
            width=64 * 32, height=42 * 32,
        )
    BOARD_LIMIT = (64 * 32, 42 * 32)
    BOARD_ORIGIN = (
        _DEFAULT_BOARD_ORIGIN[0] - int(_battle_camera["x"]),
        _DEFAULT_BOARD_ORIGIN[1] - int(_battle_camera["y"]),
    )


def draw(*args, **kwargs):
    global _context_view_mode, _context_selected_id, _context_auto_inspected_id
    global _context_menu_active, _battle_context_enabled
    global _context_has_skills
    global _context_selected_cell
    global draw_overlay
    story = kwargs.get("story", args[18] if len(args) > 18 else None)
    selected_unit = kwargs.get("selected_unit", args[5] if len(args) > 5 else None)
    destination = kwargs.get("destination", args[6] if len(args) > 6 else None)
    target_mode = kwargs.get("target_mode", args[7] if len(args) > 7 else None)
    unit_details = kwargs.get("unit_details", args[14] if len(args) > 14 else [])
    unit_facings = kwargs.get("unit_facings", args[21] if len(args) > 21 else {})
    direction_names = {1: "left", 2: "right", 3: "up", 4: "down"}
    for unit in unit_details:
        direction = direction_names.get(int(unit.get("direction", 4)))
        if direction is not None:
            unit_facings[int(unit["id"])] = direction
    terrain = kwargs.get("terrain", args[10] if len(args) > 10 else [])
    info = kwargs.get("info", args[3] if len(args) > 3 else {})
    detail = _selected_detail(unit_details, selected_unit)
    screen = kwargs.get("screen", args[0])
    battle_map = kwargs.get("battle_map", args[8] if len(args) > 8 else None)
    target_screen_size = SCREEN_SIZE if story is not None else BATTLE_SCREEN_SIZE
    if screen.get_size() != target_screen_size:
        pygame.display.set_mode(target_screen_size)

    if story is None:
        _ensure_chengpu_camera(terrain, battle_map)
        _scroll_large_battle_map()
        _battle_context_enabled = True
    else:
        _battle_context_enabled = False
        _context_selected_cell = None

    selected_id = int(detail["id"]) if detail is not None else None
    if selected_id is not None:
        _context_selected_cell = None
    elif _context_selected_cell is not None:
        selected_x, selected_y = _context_selected_cell
        if any(
            int(entry.get("x", -1)) == selected_x
            and int(entry.get("y", -1)) == selected_y
            and not entry.get("dead", False)
            for entry in unit_details
        ):
            _context_selected_cell = None
    if selected_id != _context_selected_id:
        _context_selected_id = selected_id
        _context_view_mode = None
        _context_auto_inspected_id = None

    operable = bool(
        detail is not None
        and int(detail.get("force", 0)) == 1
        and not bool(detail.get("done", False))
        and int(info.get("current_force", 1)) == 1
    )
    if detail is not None and not operable and _context_auto_inspected_id != selected_id:
        _context_view_mode = "status"
        _context_auto_inspected_id = selected_id

    _context_has_skills = bool(detail is not None and detail.get("skills", []))
    _hide_context_buttons()
    _context_menu_active = bool(
        story is None and operable and destination is not None and target_mode is None
    )
    if _context_menu_active:
        if _context_view_mode == "items":
            _place_item_menu(destination)
        elif _context_view_mode == "skills":
            _place_skill_menu(destination)
        else:
            _place_context_menu(destination)

    # The preserved renderer presents internally. Suppress that first present so
    # the legacy panel and the replacement overlays are committed atomically.
    present = pygame.display.flip
    preserved_story_overlay = draw_overlay
    pygame.display.flip = lambda: None
    if story is not None:
        draw_overlay = lambda *overlay_args, **overlay_kwargs: None
    try:
        result = _original_draw(*args, **kwargs)
    finally:
        draw_overlay = preserved_story_overlay
        pygame.display.flip = present

    if story is not None:
        screen = kwargs.get("screen", args[0])
        fonts = kwargs.get("fonts", args[1])
        portraits = kwargs.get("portraits", args[11])
        battle_title = kwargs.get("battle_title", args[23] if len(args) > 23 else "")
        objective = kwargs.get("objective", args[24] if len(args) > 24 else "")
        enemy_name = kwargs.get("enemy_name", args[16] if len(args) > 16 else "")
        log = kwargs.get("log", args[17] if len(args) > 17 else [])
        _draw_fixed_info_panel(
            screen, fonts, info, unit_details, selected_unit, portraits,
            battle_title, objective, enemy_name, log, terrain,
        )
        _draw_docked_story_dialogue(screen, fonts, story, portraits)
        present()
        return result

    screen = kwargs.get("screen", args[0])
    fonts = kwargs.get("fonts", args[1])
    portraits = kwargs.get("portraits", args[11])
    inventory = kwargs.get("inventory", args[25] if len(args) > 25 else {})
    battle_title = kwargs.get("battle_title", args[23] if len(args) > 23 else "")
    objective = kwargs.get("objective", args[24] if len(args) > 24 else "")
    enemy_name = kwargs.get("enemy_name", args[16] if len(args) > 16 else "")
    log = kwargs.get("log", args[17] if len(args) > 17 else [])
    _draw_selected_cell_highlight(screen, terrain)
    _draw_fixed_info_panel(
        screen, fonts, info, unit_details, selected_unit, portraits,
        battle_title, objective, enemy_name, log, terrain,
    )

    if _context_menu_active and detail is not None:
        _draw_context_commands(screen, fonts, detail, destination, inventory)
    if _context_view_mode == "status" and detail is not None:
        _draw_status_window(screen, fonts, detail, portraits)
    else:
        _draw_hover_summary(screen, fonts, unit_details, terrain)
    present()
    return result

HERO_LABELS.update({
    "HuErBan21": "虎儿斑", "BinXuWu21": "宾须无", "XiPeng21": "公孙隰朋",
    "GaoHei21": "高黑", "YanZhuangGong21": "燕庄公", "QiGuard21": "齐军甲士",
    "QiArcher21": "齐军弓手", "WuZhongWarrior21": "无终勇士",
    "MiLu21": "密卢", "SuMai21": "速买", "ShanRongCavalry21": "山戎骑兵",
    "ShanRongArcher21": "山戎射手", "HuangHua21": "黄花元帅",
    "DaLiHe21": "答里呵", "WuLvGu21": "兀律古", "GuzhuGuard21": "孤竹甲士",
    "GuzhuArcher21": "孤竹射手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "HuErBan21": 35, "BinXuWu21": 34, "XiPeng21": 42, "GaoHei21": 49,
    "YanZhuangGong21": 31, "QiGuard21": 49, "QiArcher21": 17,
    "WuZhongWarrior21": 15, "MiLu21": 13, "SuMai21": 38,
    "ShanRongCavalry21": 24, "ShanRongArcher21": 37, "HuangHua21": 35,
    "DaLiHe21": 7, "WuLvGu21": 40, "GuzhuGuard21": 25, "GuzhuArcher21": 20,
})
HERO_BIOS.update({
    "HuErBan21": "无终国大将，擅使长柄铁瓜锤。受召为齐军向导，北伐中先后参与伏龙山、卑耳溪与无棣城诸战。",
    "BinXuWu21": "齐国将领，随桓公北伐。奉管仲之命绕行芝麻岭，在黄台山战役中从西路突入令支。",
    "XiPeng21": "齐国大夫公孙隰朋，熟知物候地理。曾依冬蚁居山阳之理掘得泉水，又建议以老马引军走出迷谷。",
    "GaoHei21": "齐国牙将，负责由葵兹转运军粮。追随黄花时遭其擒获，拒绝投降孤竹，最终被杀。",
    "YanZhuangGong21": "燕国国君，山戎侵境后向齐国求援。随齐桓公北伐，战后获令支、孤竹之地，使燕国扩为北方大国。",
    "MiLu21": "令支国主，统山戎骑兵侵扰燕境。兵败投奔孤竹，后被黄花为取信齐军而斩杀。",
    "SuMai21": "令支将领，惯用山谷伏兵和断水守隘之计。密卢被杀后投奔虎儿斑，因不被信任而遭斩。",
    "HuangHua21": "孤竹国大将，武艺勇猛。设计诈降诱齐军进入旱海迷谷，后守无棣城突围，力尽战死。",
    "DaLiHe21": "孤竹国主，收留兵败的密卢并协助山戎。无棣城破后从北门逃走，被王子成父伏兵生擒。",
    "WuLvGu21": "孤竹国相，献出空城诱敌、旱海迷谷之计，企图不战而困死齐军，最终死于无棣城乱军。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "虎儿斑": 35, "宾须无": 34, "公孙隰朋": 42, "高黑": 49,
    "燕庄公": 31, "密卢": 13, "速买": 38, "黄花": 35,
    "答里呵": 7, "兀律古": 40, "王子成父": 34,
})
HERO_LABELS.update({
    "JiYou22": "季友", "LuGuard22": "鲁军甲士", "LuArcher22": "鲁军弓手",
    "YingNa22": "莒公子嬴拿", "JuGuard22": "莒军甲士", "JuArcher22": "莒军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "JiYou22": 31, "LuGuard22": 49, "LuArcher22": 17,
    "YingNa22": 35, "JuGuard22": 25, "JuArcher22": 20,
})
HERO_BIOS.update({
    "JiYou22": "鲁庄公之弟，字季友。两度扶立鲁君，诛叔牙、逐庆父，郦地斩嬴拿，奠定季孙氏在鲁国的地位。",
    "YingNa22": "莒国公子，勇力过人。率军索取鲁国谢赂，在郦地与季友徒手相搏，后被孟劳宝刀斩杀。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "季友": 31, "鲁僖公": 7, "鲁闵公": 6, "公子行父": 10,
    "莒公子嬴拿": 35, "嬴拿": 35, "皇子": 45,
})
HERO_LABELS.update({
    "WeiYiGong23": "卫懿公", "QuKong23": "渠孔", "YuBo23": "于伯",
    "HuangYi23": "黄夷", "KongYingQi23": "孔婴齐",
    "WeiGuard23": "卫军甲士", "WeiArcher23": "卫军弓手",
    "SouMan23": "瞍瞒", "DiCavalry23": "北狄骑兵",
    "DiAmbusher23": "北狄伏兵", "DiArcher23": "北狄射手",
    "DouZhang23": "斗章", "DouLian23": "斗廉",
    "ChuGuard23": "楚军甲士", "ChuArcher23": "楚军弓手",
    "DanBo23": "聃伯", "ZhengGuard23": "郑军甲士", "ZhengArcher23": "郑军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "WeiYiGong23": 6, "QuKong23": 42, "YuBo23": 34,
    "HuangYi23": 49, "KongYingQi23": 17,
    "WeiGuard23": 49, "WeiArcher23": 17,
    "SouMan23": 13, "DiCavalry23": 24, "DiAmbusher23": 25, "DiArcher23": 20,
    "DouZhang23": 35, "DouLian23": 40, "ChuGuard23": 15, "ChuArcher23": 37,
    "DanBo23": 42, "ZhengGuard23": 25, "ZhengArcher23": 20,
})
HERO_BIOS.update({
    "WeiYiGong23": "卫国国君，沉迷养鹤、厚敛失政。北狄入侵后亲征荥泽，卫军中伏，全军覆没。",
    "QuKong23": "卫国大夫，任荥泽之战主将。治军严厉而不得士心，中伏后劝懿公偃旗突围，最终一同战死。",
    "YuBo23": "卫国大夫，荥泽之战副将。随中军抵抗北狄伏兵，乱战中中箭坠车而亡。",
    "HuangYi23": "卫国将领，担任荥泽之战先锋。北狄伏兵截断卫军后率前队死战，最终阵亡。",
    "KongYingQi23": "卫国将领，负责荥泽之战后队。见前后军俱溃，自知无法救援卫懿公，拔剑自尽。",
    "SouMan23": "北狄首领，控弦数万。先破邢国，后在荥泽设伏歼灭卫军，导致卫国一度灭亡。",
    "DouZhang23": "楚国大夫，奉命伐郑。先退兵诱使郑军松懈，随后返身突袭，在纯门击倒并俘获聃伯。",
    "DouLian23": "楚国将领，斗章之兄。奉王命问罪斗章，却献出回师突袭之计，并率后队绕袭郑军。",
    "DanBo23": "郑国大夫，奉郑文公之命守纯门。点阅兵马时遭楚军前后夹击，力战不支，被斗章俘获。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "卫懿公": 6, "石祁子": 42, "宁速": 40, "渠孔": 42, "于伯": 34,
    "黄夷": 49, "孔婴齐": 17, "瞍瞒": 13, "弘演": 45, "卫文公": 7,
    "齐桓公": 6, "管仲": 42, "楚成王": 7, "令尹子文": 40,
    "斗章": 35, "斗廉": 40, "郑文公": 7, "聃伯": 42,
    "孔叔": 45, "竖貂": 10, "屈完": 45,
})
HERO_LABELS.update({
    "QiHuanGong24": "齐桓公", "GuanYiWu24": "管仲", "BaoShuYa24": "鲍叔牙",
    "WangZiChengFu24": "王子成父", "CoalitionGuard24": "诸侯军甲士",
    "CoalitionArcher24": "诸侯军弓手", "ZhengWenGong24": "郑文公",
    "KongShu24": "孔叔", "ShenHou24": "申侯", "XinmiGateCaptain24": "新密守门校尉",
    "ZhengGateGuard24": "郑军守卒", "ZhengArcher24": "郑军弓手",
    "XuXiGong24": "许僖公", "XuGuard24": "许军守卒", "XuArcher24": "许军弓手",
    "ChuChengWang24": "楚成王", "ZiWen24": "令尹子文", "DouLian24": "斗廉",
    "ChuGuard24": "楚军甲士", "ChuArcher24": "楚军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiHuanGong24": 8, "GuanYiWu24": 22, "BaoShuYa24": 40,
    "WangZiChengFu24": 34, "CoalitionGuard24": 49, "CoalitionArcher24": 17,
    "ZhengWenGong24": 7, "KongShu24": 45, "ShenHou24": 42,
    "XinmiGateCaptain24": 25, "ZhengGateGuard24": 25, "ZhengArcher24": 20,
    "XuXiGong24": 11, "XuGuard24": 15, "XuArcher24": 37,
    "ChuChengWang24": 8, "ZiWen24": 42, "DouLian24": 40,
    "ChuGuard24": 25, "ChuArcher24": 20,
})
HERO_BIOS.update({
    "QiHuanGong24": "春秋齐国国君，任用管仲推行改革，尊王攘夷。召陵不战服楚，首止、葵邱会盟使霸业达到极盛。",
    "GuanYiWu24": "字仲，齐国相国。以包茅责楚、避免南北大战，又主持首止定储和葵邱会盟，是齐桓公霸业核心。",
    "BaoShuYa24": "齐国大夫，以知人著称。召陵退兵途中向管仲请教问楚之策，并在霸业极盛时警惕齐侯骄奢。",
    "WangZiChengFu24": "齐国名将，长期统率齐军征伐。随桓公南至召陵，后参与围郑、救许，负责诸侯军前锋。",
    "ZhengWenGong24": "郑国国君。受周惠王密令逃离首止、暗通楚国，招致齐军两次伐郑，后斩申侯向齐请罪。",
    "KongShu24": "郑国贤大夫，反对郑文公背齐事楚，多次以嫡长大义和盟信进谏，后代表郑国向齐国请和。",
    "ShenHou24": "郑国大夫，早年仕楚。献计使郑背齐联楚，自称解新密之围有功，最终被郑文公斩首谢罪。",
    "XuXiGong24": "许穆公之子。父亲病逝于召陵军中后继位，楚军围许时坚守城池，等待齐国诸侯军救援。",
    "ChuChengWang24": "楚国君王。召陵接受盟约后仍争衡中原，依子文之计围许解郑，见诸侯援军到达便主动撤退。",
    "ZiWen24": "楚国令尹，治国持重。劝楚王信守召陵承诺，又以围许调动齐军解救郑国，避免与八国全面决战。",
    "DouLian24": "楚国将领，曾与斗章在纯门俘获聃伯。围许时随楚王列阵城南，负责约束侧翼与撤军秩序。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "许僖公": 11, "许国守将": 15, "许国使者": 45,
    "郑文公": 7, "申侯": 42, "新密守门校尉": 25,
    "周襄王": 8, "宋襄公": 6, "鲍叔牙": 40, "公孙隰朋": 42,
})
HERO_LABELS.update({
    "LiKe25": "里克", "XunXi25": "荀息", "JinGuard25": "晋军甲士",
    "JinArcher25": "晋军弓手", "YuAuxiliary25": "虞军助战兵",
    "ZhouZhiQiao25": "舟之侨", "XiayangCaptain25": "下阳守门校尉",
    "GuoGuard25": "虢军守卒", "GuoArcher25": "虢军弓手",
    "YuGong25": "虞公", "BailiXi25": "百里奚",
    "YuCapitalCaptain25": "虞都守将", "YuGuard25": "虞军甲士",
    "YuArcher25": "虞军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "LiKe25": 34, "XunXi25": 40, "JinGuard25": 49, "JinArcher25": 17,
    "YuAuxiliary25": 15, "ZhouZhiQiao25": 42, "XiayangCaptain25": 25,
    "GuoGuard25": 25, "GuoArcher25": 20, "YuGong25": 7,
    "BailiXi25": 22, "YuCapitalCaptain25": 35, "YuGuard25": 15,
    "YuArcher25": 37,
})
HERO_BIOS.update({
    "LiKe25": "晋国大夫兼主将，率军借道虞国攻取下阳、围灭虢国，又驻兵虢境配合晋献公乘虚袭虞。",
    "XunXi25": "晋国大夫，献璧马贿虞、假道灭虢之策。虞亡后将垂棘之璧与屈产之马重新归还晋国。",
    "ZhouZhiQiao25": "虢国忠臣，识破晋国女乐诱国之计。因进谏获罪出守下阳，关城失陷后转而归降晋国。",
    "YuGong25": "虞国国君，贪图晋国璧马而借道伐虢，不听宫之奇唇亡齿寒之谏，最终在箕山出猎时亡国。",
    "BailiXi25": "虞国大夫，字井伯。亡国后辗转入楚牧牛，秦穆公以五张羊皮赎回，拜为上卿，号五羖大夫。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "骊姬": 10, "优施": 45, "晋献公": 8, "里克": 34, "荀息": 40,
    "舟之侨": 42, "宫之奇": 45, "百里奚": 22, "虞公": 7,
    "虢公丑": 6, "杜氏": 18, "蹇叔": 42, "楚成王": 8,
    "秦穆公": 11, "公孙枝": 40, "下阳守门校尉": 25, "虞都守将": 35,
})
HERO_LABELS.update({
    "MengMingShi26": "孟明视", "XiQiShu26": "西乞术", "BaiYiBing26": "白乙丙",
    "YouYu26": "繇余", "QinGuard26": "秦军甲士", "QinArcher26": "秦军弓手",
    "WuLi26": "姜戎主吾离", "JiangRongGuard26": "姜戎步卒",
    "JiangRongCavalry26": "姜戎骑兵", "JiangRongArcher26": "姜戎射手",
    "ChiBan26": "西戎主赤斑", "XiRongGuard26": "西戎步卒",
    "XiRongCavalry26": "西戎骑兵", "XiRongArcher26": "西戎射手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "MengMingShi26": 35, "XiQiShu26": 49, "BaiYiBing26": 17,
    "YouYu26": 42, "QinGuard26": 15, "QinArcher26": 37,
    "WuLi26": 13, "JiangRongGuard26": 25, "JiangRongCavalry26": 24,
    "JiangRongArcher26": 20, "ChiBan26": 7, "XiRongGuard26": 25,
    "XiRongCavalry26": 24, "XiRongArcher26": 20,
})
HERO_BIOS.update({
    "MengMingShi26": "百里奚之子，名视字孟明。与西乞术、白乙丙并称秦国三帅，首次统兵击败姜戎并参与收服西戎。",
    "XiQiShu26": "秦国三帅之一，擅长统领步军稳定阵线。随孟明视攻取瓜州，又依繇余所指道路征服西戎。",
    "BaiYiBing26": "蹇叔之子，名丙字白乙。精通武艺，入秦后成为三帅之一，负责弓军压阵并参与两次西征。",
    "YouYu26": "原为晋人，仕西戎后出使秦国。受赤斑猜疑转投秦穆公，献出西戎地形兵势及征服诸戎之策。",
    "WuLi26": "姜戎首领，骄横侵掠秦境。秦国三帅首次出征时兵败，率残部逃往晋国，瓜州由此归秦。",
    "ChiBan26": "西戎诸部领袖，沉迷秦国女乐并疏远繇余。秦军按繇余所献道路进兵后无法抵抗，最终纳土归秦。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "秦穆公": 11, "百里奚": 22, "蹇叔": 42, "公子絷": 45,
    "蹇丙": 34, "杜氏": 18, "孟明视": 35, "西乞术": 49,
    "白乙丙": 17, "姜戎主吾离": 13, "吾离": 13, "繇余": 42,
    "内史廖": 40, "西戎主赤斑": 7, "赤斑": 7,
})
HERO_LABELS.update({
    "ChongEr27": "重耳", "HuMao27": "狐毛", "HuYan27": "狐偃",
    "ZhaoShuai27": "赵衰", "XuChen27": "胥臣", "WeiChou27": "魏犨",
    "HuSheGu27": "狐射姑", "DianJie27": "颠颉", "JieZiTui27": "介子推",
    "XianZhen27": "先轸", "PuGuard27": "蒲城守卒", "BoDi27": "寺人勃鞮",
    "JinGuard27": "晋军甲士", "JinCavalry27": "晋军骑兵",
    "JinArcher27": "晋军弓手", "DiGuard27": "翟军甲士", "DiArcher27": "翟军射手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ChongEr27": 6, "HuMao27": 42, "HuYan27": 40, "ZhaoShuai27": 22,
    "XuChen27": 45, "WeiChou27": 35, "HuSheGu27": 17, "DianJie27": 49,
    "JieZiTui27": 25, "XianZhen27": 34, "PuGuard27": 15, "BoDi27": 24,
    "JinGuard27": 25, "JinCavalry27": 24, "JinArcher27": 20,
    "DiGuard27": 49, "DiArcher27": 37,
})
HERO_BIOS.update({
    "ChongEr27": "晋献公之子。申生遇害后从蒲城出奔翟国，聚集赵衰、狐偃等随从，开始长期流亡。",
    "HuMao27": "晋国狐氏大夫，狐偃之兄。勃鞮攻蒲时协助重耳越墙脱险，后长期追随重耳流亡。",
    "HuYan27": "字子犯，重耳舅父兼核心谋臣。蒲城危急时力主出奔，此后一路辅佐重耳周游列国。",
    "ZhaoShuai27": "字子余，晋国赵氏先祖。重耳入翟后前来追随，善于谋划与治政，是流亡集团的重要谋臣。",
    "XuChen27": "晋国大夫，重耳的重要随从。随公子出奔翟国，长期参与军政谋划，后来成为晋国卿士。",
    "WeiChou27": "晋国勇将，勇力过人。随重耳流亡十九年，负责近卫与骑战，后成为晋文公麾下将领。",
    "HuSheGu27": "狐氏将领，又名贾季。善射，随重耳出亡，后来在晋国军中任职并参与军政争论。",
    "DianJie27": "重耳随从之一，以勇猛著称。蒲城之变后追随重耳奔翟，在流亡队伍中负责近战护卫。",
    "JieZiTui27": "重耳忠臣，随主流亡多年而不言禄。后不愿争功，隐居绵山，留下割股奉君的传说。",
    "XianZhen27": "晋国名将，富有战略眼光。早年随重耳流亡，后来主持城濮之战，奠定晋国霸业。",
    "BoDi27": "晋献公寺人，又称披。奉命攻蒲、追杀重耳，挥戈斩断其衣袖，后又追兵进入翟境。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "重耳": 6, "狐毛": 42, "狐偃": 40, "赵衰": 22, "胥臣": 45,
    "魏犨": 35, "狐射姑": 17, "颠颉": 49, "介子推": 25,
    "先轸": 34, "勃鞮": 24, "寺人勃鞮": 24, "翟军守将": 49,
    "申生": 31, "晋献公": 8, "骊姬": 10, "荀息": 40, "里克": 34,
    "夷吾": 7, "晋军传令": 25,
})
HERO_LABELS.update({
    "LiKe28": "里克", "PiZhengFu28": "丕郑父", "TuAnYi28": "屠岸夷",
    "ZhuiTuan28": "骓遄", "GongHua28": "共华", "CoupGuard28": "里氏家甲",
    "CoupArcher28": "晋国义弓手", "DongGuanWu28": "东关五",
    "LiangWu28": "梁五", "XunXi28": "荀息", "PalaceGuard28": "晋宫卫士",
    "PalaceArcher28": "晋宫弓手", "DongshiGuard28": "东市甲士",
    "DongshiArcher28": "东市弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "LiKe28": 34, "PiZhengFu28": 42, "TuAnYi28": 49, "ZhuiTuan28": 35,
    "GongHua28": 25, "CoupGuard28": 15, "CoupArcher28": 17,
    "DongGuanWu28": 24, "LiangWu28": 13, "XunXi28": 40,
    "PalaceGuard28": 25, "PalaceArcher28": 20,
    "DongshiGuard28": 15, "DongshiArcher28": 37,
})
HERO_BIOS.update({
    "LiKe28": "晋国重臣。献公死后联合丕郑父诛奚齐、卓子及骊姬党羽，先后派人迎立重耳、夷吾。",
    "PiZhengFu28": "晋国大夫，与里克同谋清除骊姬党羽。夷吾即位后背约，他出使秦国谋迎重耳。",
    "TuAnYi28": "东关五门客，勇力绝伦。受骓遄劝说后反戈，杀东关五与荀息，协助里克攻入晋宫。",
    "ZhuiTuan28": "晋国大夫，识破梁五借屠岸夷杀忠臣之谋，劝其佯诺反戈，并率家甲参与宫变。",
    "GongHua28": "晋国左行大夫。里克等攻入朝门时率家甲来援，共同清除梁五、东关五一党。",
    "DongGuanWu28": "晋献公宠臣，与梁五、优施依附骊姬。献公死后企图伏兵杀里克，在东市被屠岸夷折颈。",
    "LiangWu28": "晋献公宠臣，参与驱逐三公子。宫变时欲护卓子出奔，被屠岸夷擒住后由里克斩杀。",
    "XunXi28": "晋国大夫，曾献假道灭虢之策。受献公托孤后坚持拥立奚齐、卓子，最终死于晋宫。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "里克": 34, "丕郑父": 42, "屠岸夷": 49, "骓遄": 35, "共华": 25,
    "东关五": 24, "梁五": 13, "荀息": 40, "狐突": 45,
    "梁繇靡": 42, "郤芮": 40, "公子絷": 45, "晋惠公": 7,
    "吕饴甥": 42,
})
HERO_LABELS.update({
    "QinMuGong29": "秦穆公", "BailiXi29": "百里奚", "JinHuiGong29": "晋惠公",
    "XiRui29": "郤芮", "GuanYiWu29": "管仲", "QinGuard29": "秦军甲士",
    "QinArcher29": "秦军弓手", "JinGuard29": "晋军甲士", "JinArcher29": "晋军弓手",
    "QiGuard29": "齐军甲士", "QiArcher29": "齐军弓手", "ZhouXiangWang29": "周襄王",
    "ZhouGongKong29": "周公孔", "ShaoBoLiao29": "召伯廖", "RoyalGuard29": "王师护卫",
    "RoyalArcher29": "王师弓手", "YiLuoRongLord29": "伊洛戎主",
    "YiLuoRongGuard29": "伊洛戎步卒", "YiLuoRongCavalry29": "伊洛戎骑兵",
    "YiLuoRongArcher29": "伊洛戎射手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QinMuGong29": 11, "BailiXi29": 22, "JinHuiGong29": 7, "XiRui29": 40,
    "GuanYiWu29": 42, "QinGuard29": 49, "QinArcher29": 17,
    "JinGuard29": 25, "JinArcher29": 20, "QiGuard29": 15, "QiArcher29": 37,
    "ZhouXiangWang29": 8, "ZhouGongKong29": 45, "ShaoBoLiao29": 22,
    "RoyalGuard29": 49, "RoyalArcher29": 17, "YiLuoRongLord29": 38,
    "YiLuoRongGuard29": 25, "YiLuoRongCavalry29": 24, "YiLuoRongArcher29": 20,
})
HERO_BIOS.update({
    "QinMuGong29": "秦国国君。任用百里奚、蹇叔振兴秦国，本回率军勤王，并拒绝趁机夜袭晋军。",
    "BailiXi29": "秦国上卿，号五羖大夫。本回随秦穆公救援王城，并反对因丕豹私怨贸然伐晋。",
    "JinHuiGong29": "晋献公之子夷吾。依靠秦国入晋即位，随后背弃割地与封田承诺并清洗旧臣。",
    "XiRui29": "晋惠公亲信大夫。构陷里克，又设计屠岸夷取得丕郑父等人的迎立手书。",
    "GuanYiWu29": "齐国名相管仲。辅佐齐桓公称霸，本回率军勤王，病中论定隰朋并警告远离三奸。",
    "ZhouXiangWang29": "东周天子。王子带勾结伊洛之戎围攻王城时向诸侯告急，获秦晋齐三国救援。",
    "ZhouGongKong29": "周室卿士。伊洛之戎围攻王城时与召伯廖率王师固守，保护周襄王。",
    "ShaoBoLiao29": "周室大夫。王城遭伊洛之戎围攻时协助周公孔坚守城门，等待诸侯勤王。",
    "YiLuoRongLord29": "伊洛诸戎首领。受王子带引诱围攻周王城，见秦、晋、齐援军齐至后撤兵请和。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "秦穆公": 11, "百里奚": 22, "晋惠公": 7, "郤芮": 40, "吕饴甥": 42,
    "周襄王": 8, "周公孔": 45, "召伯廖": 22, "伊洛戎主": 38,
    "管仲": 42, "齐桓公": 6, "丕豹": 35, "里克": 34, "丕郑父": 42,
    "屠岸夷": 49,
})
HERO_LABELS.update({
    "QiHuanGong30": "齐桓公", "BaoShuYa30": "鲍叔牙", "WangZiChengFu30": "王子成父", "QiHou30": "杞侯",
    "HuaiYiLord30": "淮夷主", "QinMuGong30": "秦穆公", "BailiXi30": "百里奚", "XiQiShu30": "西乞术",
    "BaiYiBing30": "白乙丙", "GongSunZhi30": "公孙枝", "GongZiZhi30": "公子絷", "JinHuiGong30": "晋惠公",
    "TuAnYi30": "屠岸夷", "GuoShe30": "虢射", "HanJian30": "韩简", "LiangYaoMi30": "梁繇靡",
    "JiaPuTu30": "家仆徒", "XiBuYang30": "郤步扬", "WildWarrior30": "岐山野人", "WildArcher30": "岐山义弓手",
    "QiGuard30": "齐军甲士", "QiArcher30": "齐军弓手", "HuaiYiGuard30": "淮夷步卒",
    "HuaiYiArcher30": "淮夷射手", "HuaiYiCavalry30": "淮夷骑兵", "QinGuard30": "秦军甲士",
    "QinArcher30": "秦军弓手", "JinGuard30": "晋军甲士", "JinCavalry30": "晋军骑兵", "JinArcher30": "晋军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiHuanGong30": 6, "BaoShuYa30": 40, "WangZiChengFu30": 34, "QiHou30": 7, "HuaiYiLord30": 38,
    "QinMuGong30": 11, "BailiXi30": 22, "XiQiShu30": 49, "BaiYiBing30": 17, "GongSunZhi30": 35,
    "GongZiZhi30": 45, "JinHuiGong30": 7, "TuAnYi30": 49, "GuoShe30": 40, "HanJian30": 34,
    "LiangYaoMi30": 35, "JiaPuTu30": 25, "XiBuYang30": 24, "WildWarrior30": 15, "WildArcher30": 37,
    "QiGuard30": 49, "QiArcher30": 17, "HuaiYiGuard30": 25, "HuaiYiArcher30": 20,
    "HuaiYiCavalry30": 24, "QinGuard30": 49, "QinArcher30": 17, "JinGuard30": 25,
    "JinCavalry30": 24, "JinArcher30": 20,
})
HERO_BIOS.update({
    "QiHuanGong30": "齐国国君。管仲去世后任用鲍叔牙维持霸政，会合七国救援杞国并迁其都于缘陵。",
    "BaoShuYa30": "齐国贤臣。管仲、隰朋相继去世后主持国政，坚持先罢斥易牙、竖刁、开方。",
    "WangZiChengFu30": "齐国名将，长期追随齐桓公征战。本回护送杞侯和百姓穿过河道迁往缘陵。",
    "QiHou30": "杞国国君。淮夷入侵后向齐国求援，在诸侯保护下将都城迁至缘陵。",
    "HuaiYiLord30": "淮夷首领，率部侵犯杞国并试图截断迁都道路，面对七国联军后败退。",
    "QinMuGong30": "秦国国君。以泛舟之役救晋饥荒，后因晋国拒粮背德亲征韩原并生擒晋惠公。",
    "BailiXi30": "秦国上卿，主张救灾恤邻。晋国背约后协助穆公筹划韩原之战，并反对轻率冒进。",
    "XiQiShu30": "秦国三帅之一，韩原之战护卫中军，遭韩简、蛾晰夹击受伤后被岐山野人救回。",
    "BaiYiBing30": "秦国三帅之一。韩原大战与屠岸夷恶战五十余合，滚入土窟仍扭打不休。",
    "GongSunZhi30": "秦国大夫，字子桑。韩原击败晋侯车右并生擒夷吾，战后力主割地送质后放还。",
    "GongZiZhi30": "秦穆公使臣公子絷。韩原战后主张废夷吾、迎重耳，后接受公孙枝的长远处置方案。",
    "JinHuiGong30": "晋国国君夷吾。三受秦恩却拒绝售粮，韩原决战时小驷陷泥，被公孙枝生擒。",
    "TuAnYi30": "晋国勇将。韩原挥铁枪冲击秦阵，与白乙丙力战被俘，因弑卓子、杀里克之罪被斩。",
    "GuoShe30": "晋惠公国舅，主张乘秦饥荒反攻。韩原随中军出战，晋侯陷车后与车驾一同被俘。",
    "HanJian30": "晋国将领，准确判断秦军斗气十倍于晋。战中一度围住秦穆公，后因救驾未及而降。",
    "LiangYaoMi30": "晋国将领，韩原协助韩简冲击秦国中军；晋惠公被俘后放下兵器投降。",
    "JiaPuTu30": "晋惠公车右。韩原与公孙枝交战不敌，护卫晋侯陷入泥泞后被秦军俘获。",
    "XiBuYang30": "晋惠公御者。驾驶郑国所献小驷出战，战马受惊陷泥，最终与晋侯一同被俘。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "齐桓公": 6, "鲍叔牙": 40, "王子成父": 34, "杞侯": 7, "淮夷主": 38,
    "秦穆公": 11, "百里奚": 22, "西乞术": 49, "白乙丙": 17, "公孙枝": 35,
    "公子絷": 45, "晋惠公": 7, "屠岸夷": 49, "虢射": 40, "韩简": 34,
    "梁繇靡": 35, "家仆徒": 25, "郤步扬": 24, "岐山野人": 15, "穆姬": 18,
    "庆郑": 42, "郤芮": 40,
})
HERO_LABELS.update({
    "Assassin31": "晋国刺客", "AssassinArcher31": "晋国刺客弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "Assassin31": 25, "AssassinArcher31": 20,
})
SPEAKER_PORTRAIT_INDEX.update({
    "季隗": 18, "卫文公": 7, "蛾晰": 34, "长卫姬": 10,
    "易牙": 45, "竖刁": 24, "开方": 35,
})
HERO_LABELS.update({
    "GongZiZhao32": "公子昭", "CuiYao32": "崔夭",
    "PrinceGuard32": "东宫卫士", "PrinceArcher32": "东宫弓手",
    "YiYa32": "易牙", "ShuDiao32": "竖刁",
    "PalaceGuard32": "齐宫甲士", "PalaceArcher32": "齐宫弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "GongZiZhao32": 7, "CuiYao32": 35, "PrinceGuard32": 49,
    "PrinceArcher32": 17, "YiYa32": 45, "ShuDiao32": 24,
    "PalaceGuard32": 25, "PalaceArcher32": 20,
})
HERO_BIOS.update({
    "GongZiZhao32": "齐桓公之子，名昭。受立为世子并托付宋襄公，桓公死后遭易牙、竖刁追杀，连夜出奔宋国。",
    "CuiYao32": "高虎门下士，掌管临淄东门锁钥。宫变之夜打开城门，亲自执辔护送公子昭投奔宋国。",
    "YiYa32": "又名雍巫，善于调味而获齐桓公宠信。桓公病重时与竖刁封锁宫门，拥立无亏并追杀世子昭。",
    "ShuDiao32": "齐桓公宠臣，自宫入侍。管仲曾警告不可亲近，桓公晚年复用后，他与易牙发动宫变。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "扁鹊": 42, "晏蛾儿": 18, "公子昭": 7, "高虎": 42,
    "崔夭": 35, "易牙": 45, "竖刁": 24, "公子无亏": 6,
    "管平": 34, "国懿仲": 22, "公子潘": 7, "公子元": 13,
    "公子商人": 38, "公子雍": 11, "公子目夷": 42,
})
HERO_LABELS.update({
    "SongXiangGong33": "宋襄公", "GongZiDang33": "公子荡",
    "GongSunGu33": "公孙固", "HuaYuShi33": "华御事", "GaoHu33": "高虎",
    "SongGuard33": "宋军甲士", "SongArcher33": "宋军弓手",
    "GongZiYuan33": "公子元", "GongZiPan33": "公子潘",
    "GongZiShangRen33": "公子商人", "QiClanGuard33": "齐国宗兵",
    "QiClanArcher33": "齐国宗弓手", "GongZiMuYi33": "公子目夷",
    "ChuChengWang33": "楚成王", "ChengDeChen33": "成得臣",
    "DouBo33": "斗勃", "ChuAmbusher33": "楚国伏兵", "ChuArcher33": "楚国弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "SongXiangGong33": 6, "GongZiDang33": 34, "GongSunGu33": 49,
    "HuaYuShi33": 17, "GaoHu33": 42, "SongGuard33": 15, "SongArcher33": 37,
    "GongZiYuan33": 13, "GongZiPan33": 24, "GongZiShangRen33": 38,
    "QiClanGuard33": 25, "QiClanArcher33": 20, "GongZiMuYi33": 42,
    "ChuChengWang33": 8, "ChengDeChen33": 35, "DouBo33": 49,
    "ChuAmbusher33": 25, "ChuArcher33": 20,
})
HERO_BIOS.update({
    "SongXiangGong33": "宋国国君。受齐桓公托付扶立公子昭，平定齐国内乱后急于继承霸业，盂地会盟遭楚军劫持。",
    "GongZiDang33": "宋襄公臣弟，齐郊夜战驻守前营，遭三公子突袭后撤；后来多次奉命领兵和出使楚国。",
    "GongSunGu33": "宋国大将。齐郊夜战率中军救援公子荡，与华御事、高虎夹击齐国四家党羽。",
    "HuaYuShi33": "宋国将领。齐郊夜战统领后军，与公孙固、高虎相互接应，护送公子昭进入临淄。",
    "GaoHu33": "齐国上卿。设计诛杀竖刁，迎接公子昭；三公子闭城后再次求宋援助，协助孝公复位。",
    "GongZiYuan33": "齐桓公之子。与公子潘、商人联合无亏旧党拒绝公子昭，齐郊夜战失败后逃往卫国。",
    "GongZiPan33": "齐桓公之子，葛嬴所生。受开方支持争夺君位，齐郊败后将责任推给公子元并获赦。",
    "GongZiShangRen33": "齐桓公之子，密姬所生。善于收买人心，齐郊夜战联合诸兄拒昭，后来成为齐国国君。",
    "GongZiMuYi33": "宋桓公长子，字子鱼，让国于宋襄公。多次劝阻急于称霸，盂地劫盟时奉命突围守国。",
    "ChuChengWang33": "楚国国君。接受成得臣伏兵劫盟之计，在盂地纵兵生擒宋襄公，借此震慑中原诸侯。",
    "ChengDeChen33": "楚国令尹子玉。主张在盂地伏甲劫持宋襄公，亲率勇士登坛，是楚国重要统帅。",
    "DouBo33": "楚国将领。与成得臣各选五百勇士藏甲赴会，盂地盟坛上协助擒拿宋襄公。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "齐孝公": 7, "公子荡": 34, "公孙固": 49, "华御事": 17,
    "公子元": 13, "公子潘": 24, "公子商人": 38,
    "公子目夷": 42, "楚成王": 8, "成得臣": 35, "斗勃": 49,
    "子文": 40,
})
HERO_LABELS.update({
    "SongPrinceChen34": "世子王臣", "LePuYi34": "乐仆伊",
    "HuaXiuLao34": "华秀老", "XiangZiShou34": "向訾守",
    "LuChen34": "蒍氏吕臣", "ChuGuard34": "楚军甲士", "ChuArcher34": "楚军弓手",
})
PORTRAIT_INDEX_BY_HERO.update({
    "SongPrinceChen34": 13, "LePuYi34": 24, "HuaXiuLao34": 17,
    "XiangZiShou34": 35, "LuChen34": 34, "ChuGuard34": 25, "ChuArcher34": 20,
})
HERO_BIOS.update({
    "SongPrinceChen34": "宋襄公世子。宋公被楚军俘获时留守睢阳，在公子目夷摄政和公孙固守城期间维系宋国宗庙。",
    "LePuYi34": "宋国大夫。随宋襄公伐郑并参加泓水之战，混战中率军牵制楚将，掩护公孙固进入重围救主。",
    "HuaXiuLao34": "宋国将领。泓水败阵时接替乐仆伊牵制斗勃，为公孙固救出负伤的宋襄公争取时间。",
    "XiangZiShou34": "宋国将领。泓水之战身负重伤仍引导公孙固找到被围的宋襄公，随后率门官断后。",
    "LuChen34": "楚国将领蒍吕臣。泓水之战从楚阵冲出接战乐仆伊，协助成得臣完成对宋国中军的包围。",
    "SongXiangGong33": "宋国国君。扶立齐孝公后急于称霸，盂地被楚军俘获；泓水之战拒绝攻击半渡之师，负伤惨败。",
    "GongZiDang33": "宋襄公臣弟。随军参加泓水之战，深入楚阵保护主君，身受致命重伤后托付公孙固救走宋襄公。",
    "GongSunGu33": "宋国大司马。协助公子目夷守住睢阳；泓水败阵时突入重围，以身遮护负伤的宋襄公撤退。",
    "GongZiMuYi33": "宋桓公长子，字子鱼。盂地劫盟后摄政守国，以另立新君之计使楚国挟持宋襄公失去价值。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "世子王臣": 13, "乐仆伊": 24, "华秀老": 17, "向訾守": 35,
    "蒍氏吕臣": 34, "鲁僖公": 7, "仲遂": 42, "郑文公": 6,
    "叔詹": 40, "齐姜": 18, "狐偃": 42, "重耳": 7,
})
# Chapter 35: native Yunmeng map and independent beast art.
_LARGE_BATTLE_MAPS["m058.png"] = (23, 16, 48)

HERO_LABELS.update({
    "HumanBear35": "人熊",
    "MoBeast35": "貘",
    "ChuHunter35": "楚国猎手",
})
HERO_BIOS.update({
    "HumanBear35": "云梦泽中的猛兽，体形巨大、力能掀车。围猎时冲散楚军，最终被重耳一箭贯穿右掌。",
    "MoBeast35": "云梦异兽，形似熊而鼻长，皮肉坚韧。魏犨徒手扼颈生擒，赵衰以火熏鼻使其伏地。",
    "ChuHunter35": "楚成王围猎云梦时随行的猎手，熟悉泽地路径，负责驱兽、警戒与远射。",
})
SPEAKER_PORTRAIT_INDEX.update({
    "重耳": 7, "狐偃": 42, "赵衰": 22, "魏犨": 35,
    "僖负羁": 17, "公孙固": 49, "叔詹": 40,
    "楚成王": 8, "楚猎手": 49, "成得臣": 35,
})
HISTORICAL_DEATH_HEROES.add("HumanBear35")

_chapter35_previous_unit_sprite_role = unit_sprite_role


def unit_sprite_role(detail):
    name = str(detail.get("name")) if detail is not None else ""
    if name == "HumanBear35":
        return "bear"
    if name == "MoBeast35":
        return "mo_beast"
    return _chapter35_previous_unit_sprite_role(detail)


def _load_chapter35_beast_sprites(role):
    root = Path(__file__).resolve().parent / "assets" / "unit_anim" / role

    def load(name):
        return pygame.image.load(str(root / name)).convert_alpha()

    animation = {
        "down": tuple(load(f"down_{index}.png") for index in range(2)),
        "up": tuple(load(f"up_{index}.png") for index in range(2)),
        "left": tuple(load(f"left_{index}.png") for index in range(2)),
        "stand_down": (load("stand_down.png"),),
        "stand_up": (load("stand_up.png"),),
        "stand_left": (load("stand_left.png"),),
        "weak": tuple(load(f"weak_{index}.png") for index in range(2)),
        "hit_failed": (load("hit_failed.png"),),
        "hit_recover": (load("hit_recover.png"),),
    }
    right_files = (root / "right_0.png", root / "right_1.png", root / "stand_right.png")
    if all(path.is_file() for path in right_files):
        animation["right"] = tuple(load(f"right_{index}.png") for index in range(2))
        animation["stand_right"] = (load("stand_right.png"),)
    else:
        animation["right"] = tuple(pygame.transform.flip(frame, True, False) for frame in animation["left"])
        animation["stand_right"] = tuple(pygame.transform.flip(frame, True, False) for frame in animation["stand_left"])
    for direction in ("down", "up", "left", "right"):
        animation[f"attack_{direction}"] = tuple(load(f"attack_{direction}_{index}.png") for index in range(4))
        animation[f"hit_{direction}"] = (load(f"hit_{direction}.png"),)
    return animation


_chapter35_previous_load_unit_sprites = load_unit_sprites


def load_unit_sprites():
    animations = _chapter35_previous_load_unit_sprites()
    animations["bear"] = _load_chapter35_beast_sprites("bear")
    animations["mo_beast"] = _load_chapter35_beast_sprites("mo_beast")
    return animations


_chapter35_previous_portrait_for_unit = portrait_for_unit
_chapter35_portrait_cache = {}


def portrait_for_unit(detail, portraits):
    name = str(detail.get("name")) if detail is not None else ""
    custom = {
        "HumanBear35": "chapter35-human-bear.png",
        "MoBeast35": "chapter35-mo-beast.png",
    }.get(name)
    if custom is None:
        return _chapter35_previous_portrait_for_unit(detail, portraits)
    if custom not in _chapter35_portrait_cache:
        source = Path(__file__).resolve().parent / "assets" / "portraits" / custom
        _chapter35_portrait_cache[custom] = pygame.image.load(str(source)).convert_alpha()
    return _chapter35_portrait_cache[custom]


_LARGE_BATTLE_MAPS["m059.png"] = (21, 15, 64)
_LARGE_BATTLE_MAPS["m060.png"] = (21, 15, 64)

HERO_LABELS.update({
    "PiBao36": "丕豹",
    "DengHun36": "邓惛",
    "LuanZhi36": "栾枝",
    "LvSheng36": "吕省",
    "XiRui36": "郤芮",
    "QinGuard36": "秦军甲士",
    "QinArcher36": "秦军弓手",
    "LinghuGuard36": "令狐守军",
    "LinghuArcher36": "令狐弓手",
    "RebelGuard36": "纵火叛军",
    "RebelArcher36": "叛军弓手",
    "JinClanGuard36": "晋国族兵",
    "JinClanArcher36": "晋族弓手",
})
HERO_BIOS.update({
    "PiBao36": "秦将丕豹，丕郑之子。随秦军护送重耳返晋，攻破令狐，擒斩守将邓惛。",
    "DengHun36": "晋怀公部将，奉命守卫令狐，拒绝重耳入境。城破后被丕豹擒获斩首。",
    "LuanZhi36": "晋国栾氏将领，参与迎立重耳。绛宫火变时联络国内诸族，协助平定叛乱。",
    "LvSheng36": "晋国大夫，先事怀公，后迎重耳。因畏惧清算，与郤芮谋焚公宫，最终伏诛。",
    "XiRui36": "晋国大夫，吕省同党。参与谋害晋文公，宫变失败后被骗至王城处死。",
    "QinGuard36": "秦穆公派遣护送重耳返晋的甲士。",
    "QinArcher36": "秦军远射部队，为令狐攻城队伍提供掩护。",
    "LinghuGuard36": "邓惛统领的令狐守军，奉晋怀公之命拒守城池。",
    "LinghuArcher36": "驻守令狐城垣和门道的弓手。",
    "RebelGuard36": "受吕省、郤芮驱使，参与夜焚绛宫的叛军。",
    "RebelArcher36": "纵火叛军中的弓手，负责封锁宫门两翼。",
    "JinClanGuard36": "听从栾枝号召赶来救火平乱的晋国族兵。",
    "JinClanArcher36": "晋国诸族派出的弓手，第三回合从两侧增援。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "PiBao36": 35,
    "DengHun36": 34,
    "LuanZhi36": 42,
    "LvSheng36": 40,
    "XiRui36": 42,
})
SPEAKER_PORTRAIT_INDEX.update({
    "丕豹": 35,
    "邓惛": 34,
    "栾枝": 42,
    "吕省": 40,
    "郤芮": 42,
    "勃鞮": 35,
    "公子絷": 40,
})
HISTORICAL_DEATH_HEROES.add("DengHun36")


SPEAKER_PORTRAIT_INDEX.update({
    "头须": 35,
    "晋文公": 7,
    "赵姬": 13,
    "壶叔": 17,
    "介子推母": 11,
    "解张": 40,
    "绵山农夫": 18,
    "富辰": 45,
    "颓叔": 22,
    "隗后": 14,
    "太叔带": 49,
    "小东": 12,
})


_LARGE_BATTLE_MAPS["m061.png"] = (23, 16, 64)
_LARGE_BATTLE_MAPS["m062.png"] = (27, 17, 64)

HERO_LABELS.update({
    "FuChen38": "富辰", "JianShiFu38": "简师父", "ZuoYanFu38": "左鄢父",
    "ChiDing38": "赤丁", "ChiFengZi38": "赤风子",
    "DiGuard38": "翟军甲士", "DiCavalry38": "翟军骑兵", "DiArcher38": "翟军弓手",
    "XiZhen38": "郤溱", "TaiShuDai38": "太叔带", "WeiHou38": "隗后",
    "WenRebelGuard38": "温城叛军", "WenRebelArcher38": "温城弓手",
    "JinGuard38": "晋军甲士", "JinArcher38": "晋军弓手",
    "YuanBoGuan38": "原伯贯", "YuanGuard38": "原城守军", "YuanArcher38": "原城弓手",
})
HERO_BIOS.update({
    "FuChen38": "周襄王大夫，屡谏不可借翟攻郑、迎娶翟女。王城被围时率族人死战，掩护襄王出奔。",
    "JianShiFu38": "周襄王近臣，随天子出奔氾地，奉命赴晋告难，请晋文公兴兵勤王。",
    "ZuoYanFu38": "周室大夫，护送襄王避居郑国，并奉命前往秦国请求勤王。",
    "ChiDing38": "翟国大将，率步骑五千拥太叔带伐周，击败王师并围困王城。",
    "ChiFengZi38": "赤丁之子，善使骑兵诈败诱敌，在翠云山伏击原伯贯所部。",
    "DiGuard38": "随赤丁进攻王城的翟军步卒。",
    "DiCavalry38": "翟国骑兵，负责追击周王与包抄王师。",
    "DiArcher38": "翟军远射部队，参与封锁王城南门。",
    "XiZhen38": "晋国大夫，早年与栾枝迎接重耳。勤王时统右军围温，后任温大夫。",
    "TaiShuDai38": "周襄王庶弟，私通隗后，借翟兵逐兄自立。温城败亡时被魏犨斩杀。",
    "WeiHou38": "翟君之女后叔隗，嫁周襄王后私通太叔带。温城败亡时被晋军弓手射杀。",
    "WenRebelGuard38": "追随太叔带据守温城的亲兵。",
    "WenRebelArcher38": "太叔带留在温城内街的弓手。",
    "JinGuard38": "晋文公勤王部队中的甲士。",
    "JinArcher38": "随晋军进入温城讨逆的弓手。",
    "YuanBoGuan38": "周室原邑大夫。原邑划归晋国后闭城观望，最终因晋文公守信退兵而率众归降。",
    "YuanGuard38": "驻守原城的甲士，奉命闭门坚守，不主动出城参战。",
    "YuanArcher38": "原城城内弓手，仅负责守卫城池，不支援温城叛军。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "FuChen38": 45, "JianShiFu38": 40, "ZuoYanFu38": 42,
    "ChiDing38": 38, "ChiFengZi38": 39, "XiZhen38": 22,
    "TaiShuDai38": 49, "WeiHou38": 14,
    "YuanBoGuan38": 40,
})
SPEAKER_PORTRAIT_INDEX.update({
    "赤丁": 38, "赤风子": 39, "简师父": 40, "左鄢父": 42,
    "郤溱": 22, "温城百姓": 18, "晋军司粮": 17,
    "原伯贯": 40,
})
HISTORICAL_DEATH_HEROES.update({"FuChen38", "TaiShuDai38", "WeiHou38"})



_LARGE_BATTLE_MAPS["m063.png"] = (25, 19, 64)

HERO_LABELS.update({
    "CaoGongGong39": "曹共公", "YuLang39": "于朗", "XiFuJi39": "僖负羁",
    "CaoGateGuard39": "曹国守军", "CaoArcher39": "曹军弓手",
    "JinGuard39": "晋军甲士", "JinArcher39": "晋军弓手",
})
HERO_BIOS.update({
    "CaoGongGong39": "曹国国君。重耳流亡过曹时曾窥看其骈胁；晋军伐曹后误用于朗诈降之计，城破被魏犨生擒。",
    "YuLang39": "曹国大夫。晋军围曹时献诈降陷坑之计，杀死勃鞮与三百晋军；曹城陷落后被颠颉斩杀。",
    "XiFuJi39": "曹国大夫。重耳过曹时曾赠璧馈食；晋文公破曹后下令保护其家，后因魏犨、颠颉违令纵火而死。",
    "CaoGateGuard39": "驻守曹都四门的甲士，利用城门与街巷抵挡晋军四路突入。",
    "CaoArcher39": "曹都守军中的弓手，分布在四门内侧和宫城周围。",
    "JinGuard39": "晋文公三军中的甲士，随四路攻城队乘丧车扰乱门禁之机突入曹都。",
    "JinArcher39": "晋军攻曹弓手，负责在狭窄城门通道外压制守军。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "CaoGongGong39": 7, "YuLang39": 42, "XiFuJi39": 45,
})
SPEAKER_PORTRAIT_INDEX.update({
    "臧孙辰": 40, "展喜": 42, "齐孝公": 7, "楚成王": 6,
    "子文": 45, "蒍贾": 40, "晋文公": 7, "郤縠": 22,
    "赵衰": 40, "先轸": 35, "狐偃": 40, "狐毛": 42,
    "栾枝": 42, "颠颉": 34, "魏犨": 35,
    "曹共公": 7, "于朗": 42, "僖负羁": 45,
})
HISTORICAL_DEATH_HEROES.update({"YuLang39", "XiFuJi39"})



_LARGE_BATTLE_MAPS["m064.png"] = (64, 42, 32)

HERO_LABELS.update({
    "QiMan40": "祁瞒", "GuoGuiFu40": "国归父", "XiaoZiYin40": "小子憖",
    "DouYiShen40": "斗宜申", "ChengDaXin40": "成大心", "DouYueJiao40": "斗越椒",
    "YuanXuan40": "辕选", "GongZiYin40": "公子印", "ShiGui40": "石癸", "BaiChou40": "百俦",
    "ChuGuard40": "楚军甲士", "ChuCavalry40": "楚军车骑", "ChuArcher40": "楚军弓手",
    "ChenGuard40": "陈军甲士", "ChenCavalry40": "陈军车骑", "ChenArcher40": "陈军弓手",
    "CaiGuard40": "蔡军甲士", "CaiCavalry40": "蔡军车骑", "CaiArcher40": "蔡军弓手",
})
HERO_BIOS.update({
    "QiMan40": "晋军中军将领。城濮之战奉命坚守阵门，后因轻视成大心而擅自出战，被斗越椒射中盔缨。",
    "GuoGuiFu40": "齐国上卿国懿仲之子。齐孝公命其率军会晋，在城濮协助晋军夹击楚师。",
    "XiaoZiYin40": "秦穆公次子。奉命率秦军援晋救宋，在城濮与晋、齐联军共同对抗楚军。",
    "DouYiShen40": "楚国大夫，率申邑之师并郑、许军组成楚左师。中晋军诱敌夹击之计后弃车翻山撤退。",
    "ChengDaXin40": "成得臣之子，年仅十五而勇于交锋。城濮之战在楚中军阵前挑战祁瞒。",
    "DouYueJiao40": "楚国名将，善射。城濮之战助成大心，以一箭射中祁瞒盔缨并率中军突进。",
    "YuanXuan40": "陈国将领。随楚军围宋，在城濮右师前队与蔡军争先出战，遭虎皮车阵冲乱。",
    "GongZiYin40": "蔡国公子。随楚右师参加城濮之战，战马被虎皮车惊乱，随后被晋将胥臣斩杀。",
    "ShiGui40": "郑国将领。率郑军编入斗宜申左师，追击晋军疑兵时遭到两面夹击。",
    "BaiChou40": "许国将领。率许军协助楚左师，城濮之战随斗宜申深入后败退。",
    "ChuGuard40": "成得臣统率的楚国步卒，分属左军和中军。",
    "ChuCavalry40": "楚军车骑部队，承担两翼追击与中军突击任务。",
    "ChuArcher40": "楚军中军及两翼弓手，负责掩护战车推进。",
    "ChenGuard40": "陈国附庸步卒，编入楚右师前队。",
    "ChenCavalry40": "陈国车骑，随辕选参加城濮之战。",
    "ChenArcher40": "陈军远射部队，协助楚右师作战。",
    "CaiGuard40": "蔡国附庸步卒，编入楚右师前队。",
    "CaiCavalry40": "蔡国车骑，随公子印参加城濮之战。",
    "CaiArcher40": "蔡军远射部队，协助楚右师作战。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "QiMan40": 34, "GuoGuiFu40": 35, "XiaoZiYin40": 38,
    "DouYiShen40": 39, "ChengDaXin40": 33, "DouYueJiao40": 37,
    "YuanXuan40": 35, "GongZiYin40": 38, "ShiGui40": 34, "BaiChou40": 39,
})
SPEAKER_PORTRAIT_INDEX.update({
    "魏犨": 35, "晋文公": 7, "楚成王": 6, "门尹般": 40,
    "先轸": 35, "成得臣": 39, "斗越椒": 37, "栾枝": 42,
    "狐偃": 40, "胥臣": 22, "祁瞒": 34, "斗宜申": 39,
    "白乙丙": 38, "成大心": 33,
})
HISTORICAL_DEATH_HEROES.update({"DianJie27", "GongZiYin40"})

SPEAKER_PORTRAIT_INDEX.update({
    "\u536b\u6210\u516c": 7, "\u6b47\u72ac": 34, "\u5143\u89d2": 33, "\u5143\u54ba": 42,
    "\u53f8\u9a6c\u7792": 35, "\u53d4\u6b66": 38, "\u5b81\u4fde": 40, "\u957f\u7257": 34,
    "\u821f\u4e4b\u4fa8": 34, "\u8340\u6797\u7236": 35, "\u5468\u8944\u738b": 8, "\u738b\u5b50\u864e": 45,
    "\u9f50\u662d\u516c": 6, "\u5b8b\u6210\u516c": 7, "\u9c81\u50d6\u516c": 6, "\u8521\u5e84\u516c": 7,
    "\u79e6\u7a46\u516c": 11, "\u90d1\u6587\u516c": 7, "\u9648\u5171\u516c": 6, "\u937c\u5e84\u5b50": 40,
    "\u58eb\u8363": 42, "\u516c\u5b50\u7455": 38,
})


_LARGE_BATTLE_MAPS["m065.png"] = (32, 24, 48)
_LARGE_BATTLE_MAPS["m066.png"] = (36, 26, 48)

HERO_LABELS.update({
    "XuXiGong43": "许僖公", "XuGuard43": "许国甲士", "XuArcher43": "许国弓手",
    "JinGuard43": "晋军甲士", "JinArcher43": "晋军弓手",
    "ZhuZhiWu43": "烛之武", "ZhengWenGong43": "郑文公", "ShuZhan43": "叔詹",
    "YiZhiHu43": "佚之狐", "QinGuard43": "秦军宿卫", "JinPatrol43": "晋军巡骑",
})
HERO_BIOS.update({
    "XuXiGong43": "许国国君。河阳会盟失期后遭九国围攻，楚援不至，最终面缚衔璧向晋文公请降，得以保全社稷。",
    "ZhuZhiWu43": "郑国大夫。年老才被重用，秦晋围郑时夜缒出城，以亡郑利晋害秦之理说服秦穆公退兵。",
    "ZhengWenGong43": "郑国国君。晋秦围郑时向烛之武谢过求贤，使其夜赴秦营，终于解除东面包围。",
    "ShuZhan43": "郑国大夫。面对秦晋围城，主张以辞令离间强敌，促成烛之武出使秦营。",
    "YiZhiHu43": "郑国大夫。深知烛之武辩才，在国危时向郑文公举荐，留下国危矣若使烛之武见秦君的名论。",
    "XuGuard43": "驻守颍阳南门与内城街巷的许国甲士。",
    "XuArcher43": "依托颍阳城墙和内街压制诸侯军的许国弓手。",
    "JinGuard43": "随晋文公参加九国围许的晋军甲士。",
    "JinArcher43": "在颍阳南门外为攻城部队提供掩护的晋军弓手。",
    "QinGuard43": "守卫氾南秦营门道与中军幕府的宿卫。",
    "JinPatrol43": "夜间巡查郑城郊外的晋军骑兵，发现使者便会鸣号示警。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "XuXiGong43": 7, "ZhuZhiWu43": 42, "ZhengWenGong43": 7,
    "ShuZhan43": 40, "YiZhiHu43": 45,
})
SPEAKER_PORTRAIT_INDEX.update({
    "许僖公": 7, "晋文公": 7, "赵衰": 35, "先轸": 34, "秦穆公": 11,
    "曹共公": 7, "郑文公": 7, "叔詹": 40, "佚之狐": 45,
    "烛之武": 42, "百里奚": 40,
})
_LARGE_BATTLE_MAPS["m067.png"] = (32, 24, 48)

HERO_LABELS.update({
    "BaoManZi44": "褒蛮子", "QinGuard44": "秦军甲士", "QinArcher44": "秦军弓手",
    "HuaGong44": "滑君", "HuaGuard44": "滑国甲士", "HuaArcher44": "滑国弓手",
})
HERO_BIOS.update({
    "BaoManZi44": "秦军前哨牙将，骁勇善于超乘。随孟明视千里袭郑，计划泄露后参加三路夜袭滑国。",
    "HuaGong44": "滑国国君。秦军放弃袭郑后转攻滑城，城破逃往翟地，滑国随后不能复国。",
    "QinGuard44": "随秦国三帅千里东进的甲士，夜间分三路突袭无备的滑城。",
    "QinArcher44": "秦军远射部队，负责压制滑国三门及城内街巷守军。",
    "HuaGuard44": "仓促守卫滑国西、南、东三门和内街的甲士。",
    "HuaArcher44": "依托滑城门道与内街阻击秦军的弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "BaoManZi44": 34, "HuaGong44": 7,
})
SPEAKER_PORTRAIT_INDEX.update({
    "叔詹": 40, "晋文公": 7, "郑文公": 7, "石申父": 42, "郤缺": 35,
    "先轸": 34, "秦穆公": 11, "蹇叔": 40, "百里奚": 40, "弦高": 42,
    "孟明视": 35, "西乞术": 49, "白乙丙": 17, "滑君": 7, "烛之武": 42,
})
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

_LARGE_BATTLE_MAPS["m070.png"] = (38, 26, 48)
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

_LARGE_BATTLE_MAPS["m073.png"] = (36, 26, 48)
_LARGE_BATTLE_MAPS["m074.png"] = (42, 28, 48)

HERO_LABELS.update({
    "ShuSunDeChen47": "叔孙得臣", "FuFuZhongSheng47": "富父终甥", "QiaoRu47": "侨如",
    "LuGuard47": "鲁军甲士", "LuArcher47": "鲁军弓手",
    "DiGuard47": "翟军甲士", "DiCavalry47": "翟军骑兵", "DiArcher47": "翟军射手",
    "ZhaoDun47": "赵盾", "XianKe47": "先克", "XunLinFu47": "荀林父", "XianDu47": "先都",
    "GongZiYong47": "公子雍", "XianMie47": "先蔑", "ShiHui47": "士会",
    "JinGuard47": "晋军甲士", "JinCavalry47": "晋军骑兵", "JinArcher47": "晋军弓手",
    "QinGuard47": "秦军甲士", "QinCavalry47": "秦军骑兵", "QinArcher47": "秦军弓手",
})
HERO_BIOS.update({
    "ShuSunDeChen47": "鲁国卿大夫。长翟侨如侵鲁时统兵迎战，采纳富父终甥的雪夜陷坑之计，杀散翟军并载回侨如巨尸。",
    "FuFuZhongSheng47": "鲁国大夫。预判夜间降雪，以草蓐浮土掩盖陷坑，诈败诱侨如追赶，待其坠坑后持戈刺喉。",
    "QiaoRu47": "翟国长人，身高一丈五尺，力举千钧，人称长翟。受白暾之命侵鲁，追敌时坠入雪坑，被富父终甥刺死。",
    "ZhaoDun47": "赵衰之子，晋国正卿。先迎公子雍，后迫于穆嬴改立夷皋，并率晋军夜袭令狐秦营。",
    "XianKe47": "先且居之子，晋军将领。令狐之战担任赵盾中军副将，后因部将蒯得贪进失车而依法处分。",
    "XunLinFu47": "晋国将领。曾预言迎雍之事将变；令狐之战独领上军，战后又为先蔑、士会送还家眷财物。",
    "XianDu47": "晋国将领，先蔑族人。令狐之战独领下军参与夜袭，后因不满赵盾专权而卷入晋国内乱。",
    "GongZiYong47": "晋文公庶子，母为贤德的杜祁，在秦任亚卿。被晋卿迎立又遭背弃，最终死于令狐夜袭乱军。",
    "XianMie47": "晋国下军元帅，字士伯。奉命入秦迎公子雍，赵盾改立灵公后仍不肯背弃使命，战后留秦为臣。",
    "ShiHui47": "晋国大夫，又称随会、士季。随先蔑迎公子雍，令狐兵败后与先蔑一同留秦，后来成为晋国名臣。",
    "LuGuard47": "埋伏在雪地陷坑两侧、等候长翟深入的鲁国甲士。",
    "LuArcher47": "依托雪原林缘封锁翟军退路的鲁军弓手。",
    "DiGuard47": "随长翟侨如侵入鲁境的翟军甲士。",
    "DiCavalry47": "追击富父终甥诱敌部队的翟军骑兵。",
    "DiArcher47": "在雪夜为侨如前队提供远射掩护的翟军射手。",
    "JinGuard47": "衔枚潜行、从东门突入令狐秦营的晋军甲士。",
    "JinCavalry47": "负责冲散秦营车阵并向刳首追击的晋军骑兵。",
    "JinArcher47": "在营门与外围压制仓促迎战秦军的晋军弓手。",
    "QinGuard47": "护送公子雍返晋、夜宿令狐营寨的秦军甲士。",
    "QinCavalry47": "秦康公拨给公子雍的车骑护卫，遭晋军三更突袭。",
    "QinArcher47": "令狐营中来不及完成列阵的秦军弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ShuSunDeChen47": 24, "FuFuZhongSheng47": 49, "QiaoRu47": 34,
    "ZhaoDun47": 42, "XianKe47": 35, "XunLinFu47": 37, "XianDu47": 25,
    "GongZiYong47": 7, "XianMie47": 40, "ShiHui47": 31,
})
SPEAKER_PORTRAIT_INDEX.update({
    "弄玉": 18, "萧史": 31, "秦康公": 7, "臾骈": 49, "狐射姑": 45,
    "叔孙得臣": 24, "富父终甥": 49, "侨如": 34, "赵盾": 42,
    "先克": 35, "荀林父": 37, "先都": 25, "公子雍": 7,
    "先蔑": 40, "士会": 31, "穆嬴": 18,
})
HISTORICAL_DEATH_HEROES.update({"QiaoRu47", "GongZiYong47"})

_LARGE_BATTLE_MAPS["m075.png"] = (40, 28, 48)
_LARGE_BATTLE_MAPS["m076.png"] = (54, 32, 48)

HERO_LABELS.update({
    "DouYueJiao48": "斗越椒", "WeiJia48": "蔿贾", "StrawDecoy48": "草人疑兵",
    "GongZiJian48": "公子坚", "GongZiPang48": "公子庞", "YueEr48": "乐耳",
    "ChuGuard48": "楚军甲士", "ChuCavalry48": "楚军骑兵", "ChuArcher48": "楚军弓手",
    "ZhengGuard48": "郑军甲士", "ZhengCavalry48": "郑军骑兵", "ZhengArcher48": "郑军弓手",
    "QinKangGong48": "秦康公", "YuPian48": "臾骈", "XuJia48": "胥甲",
    "ZhaoChuan48": "赵穿", "HanJue48": "韩厥",
    "JinGuard48": "晋军甲士", "JinCavalry48": "晋军骑兵", "JinArcher48": "晋军弓手",
    "QinGuard48": "秦军甲士", "QinCavalry48": "秦军骑兵", "QinArcher48": "秦军弓手",
})
HERO_BIOS.update({
    "DouYueJiao48": "楚国若敖氏名将，字伯棼。奉楚穆王命攻郑，以空营诱敌，配合蔿贾生擒郑国三将。",
    "WeiJia48": "楚国名臣，字伯嬴。善察人谋，辅佐斗越椒设空营伏兵，迫使郑、陈重新服楚。",
    "GongZiJian48": "郑国公子，奉郑穆公命迎击楚军，因争功深入空营，被楚军伏兵生擒后释放。",
    "GongZiPang48": "郑国将领，与公子坚、乐耳共同追入楚军空营，遭南北合围被俘，郑服楚后获释。",
    "YueEr48": "郑国将领，随公子坚迎战楚军，虽怀疑空营有诈，仍陷伏兵，后随二公子获释。",
    "QinKangGong48": "秦穆公之子。为报令狐之败率军攻晋，在河曲与晋军相持，识破半渡伏击后夜间撤军。",
    "YuPian48": "晋国上军主将，河曲之战主张坚壁不战；后从秦使神色中判断敌情，提出半渡而击。",
    "XuJia48": "晋国下军主将，河曲之战参与接应赵穿，后来因泄露臾骈的半渡伏击之谋而获罪。",
    "ZhaoChuan48": "晋国将领，赵夙之后。河曲之战不耐秦军挑战而擅自出营，迫使晋国三军共同接应。",
    "HanJue48": "晋国将领，执法严明。河曲列阵时斩赵盾乱阵车右而不避权贵，获得赵盾器重。",
    "StrawDecoy48": "楚军设置在空营中军帐内的草人假将，用旗鼓和假阵吸引郑军深入。",
    "ChuGuard48": "埋伏于空营南北两翼、负责封锁郑军退路的楚国甲士。",
    "ChuCavalry48": "在郑军进入空营后迅速合围东门的楚国骑兵。",
    "ChuArcher48": "依托营寨围栏压制郑军、以生擒三将为目标的楚军弓手。",
    "ZhengGuard48": "随郑国三将进入楚军空营的甲士。",
    "ZhengCavalry48": "争先追击楚军疑兵、陷入伏击的郑国骑兵。",
    "ZhengArcher48": "为郑国追击部队提供远射支援的弓手。",
    "JinGuard48": "河曲之战中依托东侧营寨坚守并接应赵穿的晋军甲士。",
    "JinCavalry48": "从晋营出击接应赵穿、随后掩护全军回营的晋军骑兵。",
    "JinArcher48": "驻守晋营门口、压制秦军追兵的晋军弓手。",
    "QinGuard48": "随秦康公进至河曲、负责守卫西侧大营的秦军甲士。",
    "QinCavalry48": "按照士会之计挑战赵穿并准备两翼合围的秦军骑兵。",
    "QinArcher48": "在河曲中央压制晋军接应部队的秦军弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "DouYueJiao48": 34, "WeiJia48": 49, "GongZiJian48": 7, "GongZiPang48": 35,
    "YueEr48": 24, "QinKangGong48": 7, "YuPian48": 45, "XuJia48": 25,
    "ZhaoChuan48": 35, "HanJue48": 42,
})
SPEAKER_PORTRAIT_INDEX.update({
    "先都": 25, "箕郑父": 45, "赵盾": 42, "狐射姑": 35, "楚穆王": 7,
    "斗越椒": 34, "蔿贾": 49, "郑穆公": 7, "公子坚": 7, "公子庞": 35,
    "乐耳": 24, "秦康公": 7, "臾骈": 45, "胥甲": 25, "赵穿": 35,
    "韩厥": 42, "荀林父": 37, "郤缺": 31, "士会": 31, "寿馀": 49, "绕朝": 40,
})

_LARGE_BATTLE_MAPS["m077.png"] = (44, 30, 48)

HERO_LABELS.update({
    "HuaOu49": "华耦", "SongZhaoGong49": "宋昭公", "DangYiZhu49": "荡意诸",
    "SongCoupGuard49": "拥鲍甲士", "SongCoupCavalry49": "拥鲍骑兵", "SongCoupArcher49": "拥鲍弓手",
    "RoyalRetainer49": "昭公近卫", "RoyalArcher49": "昭公弓手",
})
HERO_BIOS.update({
    "HuaOu49": "宋国司马华耦。宋昭公出猎孟诸时，奉襄夫人与公子鲍之命召集国人追击；事成回城后突发心疾而死。",
    "SongZhaoGong49": "宋国国君，名杵臼。疏远宗族而失去国人支持，出猎孟诸时遭华耦追杀，与忠臣荡意诸一同遇害。",
    "DangYiZhu49": "宋国大夫。曾避祸奔鲁，获宋昭公赦免后归国；孟诸之变中拒绝逃生，独自护主直至战死。",
    "SongCoupGuard49": "受公子鲍恩惠、随华耦追击宋昭公的宋国甲士。",
    "SongCoupCavalry49": "沿孟诸林道追赶宋昭公车驾的拥鲍骑兵。",
    "SongCoupArcher49": "随华耦封锁孟诸林间退路的拥鲍弓手。",
    "RoyalRetainer49": "随宋昭公出猎孟诸的近卫，昭公命其带走财物自行逃生。",
    "RoyalArcher49": "保护宋昭公车驾、在孟诸抵挡追兵的弓手。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "HuaOu49": 34, "SongZhaoGong49": 7, "DangYiZhu49": 25,
})
SPEAKER_PORTRAIT_INDEX.update({
    "赵朔": 37, "士会": 31, "郤缺": 42, "公子商人": 7, "公子元": 18,
    "鲁文公": 7, "襄夫人": 12, "公子鲍": 18, "荡意诸": 25, "宋昭公": 7,
    "公子须": 35, "华耦": 34, "宋文公": 18, "华元": 49, "郑穆公": 7,
    "邴歜": 38, "阎职": 39, "仲遂": 45,
})
HISTORICAL_DEATH_HEROES.update({"DangYiZhu49", "SongZhaoGong49"})

_LARGE_BATTLE_MAPS["m078.png"] = (42, 28, 48)
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

_chapter50_previous_unit_sprite_role = unit_sprite_role


def unit_sprite_role(detail):
    name = str(detail.get("name")) if detail is not None else ""
    if name == "LingAo50":
        return "lingao"
    return _chapter50_previous_unit_sprite_role(detail)


_chapter50_previous_load_unit_sprites = load_unit_sprites


def load_unit_sprites():
    animations = _chapter50_previous_load_unit_sprites()
    animations["lingao"] = _load_chapter35_beast_sprites("lingao")
    return animations


_chapter50_previous_portrait_for_unit = portrait_for_unit
_chapter50_lingao_portrait_cache = {}


def portrait_for_unit(detail, portraits):
    name = str(detail.get("name")) if detail is not None else ""
    if name != "LingAo50":
        return _chapter50_previous_portrait_for_unit(detail, portraits)
    filename = "chapter50-lingao.png"
    if filename not in _chapter50_lingao_portrait_cache:
        source = Path(__file__).resolve().parent / "assets" / "portraits" / filename
        _chapter50_lingao_portrait_cache[filename] = pygame.image.load(str(source)).convert_alpha()
    return _chapter50_lingao_portrait_cache[filename]


_LARGE_BATTLE_MAPS["m081.png"] = (48, 34, 48)

HERO_LABELS.update({
    "ChuZhuangWang51": "楚庄王", "GongZiCe51": "公子侧", "GongZiYingQi51": "公子婴齐",
    "PanWang51": "潘尪", "LeBo51": "乐伯", "YangYouJi51": "养由基", "DouBenHuang51": "斗贲皇",
    "ChuRoyalGuard51": "楚王亲卫", "ChuRoyalArcher51": "楚王弓手",
    "ChuAmbushGuard51": "楚军伏兵", "ChuAmbushCavalry51": "楚军伏骑", "ChuAmbushArcher51": "楚军伏弓",
    "RuoAoGuard51": "若敖甲士", "RuoAoCavalry51": "若敖骑兵", "RuoAoArcher51": "若敖弓手",
})
HERO_BIOS.update({
    "ChuZhuangWang51": "楚国君王熊侣。即位后整顿朝政，平定斗越椒叛乱，任用孙叔敖，逐渐奠定楚国霸业。",
    "GongZiCe51": "楚国王族名将，字子反。清河桥之战与公子婴齐分率两翼伏兵，合围饥疲的斗氏叛军。",
    "GongZiYingQi51": "楚国王族名将，字子重。斗越椒叛乱时统率一翼伏军，协助楚庄王截断清河退路。",
    "PanWang51": "楚国将领。初战与斗旗交锋，诈退阶段故意为斗越椒让路，将叛军继续引向青山伏击圈。",
    "LeBo51": "楚国大将。清河桥南阻截斗越椒，并接受部将养由基请战，以箭术决定叛军主将生死。",
    "YangYouJi51": "楚国神射手，字叔。清河桥隔河与斗越椒较射，避过三箭后仅发一矢便贯脑杀敌。",
    "DouBenHuang51": "斗越椒之子。清河兵败后逃往晋国，被任为大夫，食邑于苗，后称苗贲皇。",
})
PORTRAIT_INDEX_BY_HERO.update({
    "ChuZhuangWang51": 8, "GongZiCe51": 49, "GongZiYingQi51": 35,
    "PanWang51": 33, "LeBo51": 34, "YangYouJi51": 24, "DouBenHuang51": 38,
})
SPEAKER_PORTRAIT_INDEX.update({
    "赵穿": 35, "晋灵公": 7, "士会": 31, "赵盾": 42, "董狐": 49,
    "楚庄王": 8, "王孙满": 45, "苏从": 42, "斗越椒": 34, "公子侧": 49,
    "公子婴齐": 35, "熊负羁": 25, "乐伯": 34, "养由基": 24, "斗克黄": 31,
    "许姬": 12, "虞邱": 45, "蒍敖之母": 12,
})
HISTORICAL_DEATH_HEROES.add("DouYueJiao40")

_LARGE_BATTLE_MAPS["m082.png"] = (46, 30, 48)

HERO_LABELS.update({
    "ZhengXiangGong52": "郑襄公", "GongZiQuJi52": "公子去疾",
    "JinReliefGuard52": "晋军甲士", "JinReliefCavalry52": "晋军轻骑", "JinReliefArcher52": "晋军弓手",
    "ZhengGuard52": "郑军守卒", "ZhengArcher52": "郑军弓手",
    "ChuLiufenGuard52": "楚军甲士", "ChuLiufenCavalry52": "楚军骑兵", "ChuLiufenArcher52": "楚军弓手",
})
HERO_BIOS.update({
    "ZhengXiangGong52": "郑国国君，名坚。郑灵公遇弑后即位，任用诸位兄弟参与国政，在晋楚争霸之间维持郑国生存。",
    "GongZiQuJi52": "郑穆公之子，字子良。拒绝越次即位，劝郑襄公保全公族，后查明公子宋弑君之罪并加以诛讨。",
})
PORTRAIT_INDEX_BY_HERO.update({"ZhengXiangGong52": 7, "GongZiQuJi52": 45})
SPEAKER_PORTRAIT_INDEX.update({
    "公子宋": 34, "公子归生": 42, "郑灵公": 7, "公子去疾": 45, "郑襄公": 7,
    "郤缺": 37, "楚庄王": 8, "孔宁": 38, "陈灵公": 9, "仪行父": 31, "泄冶": 49,
})

_LARGE_BATTLE_MAPS["m083.png"] = (46, 30, 48)
_LARGE_BATTLE_MAPS["m084.png"] = (52, 34, 48)

HERO_LABELS.update({
    "QuWu53": "屈巫", "XiaZhengShu53": "夏征舒",
    "ChuExpeditionGuard53": "楚国甲士", "ChuExpeditionCavalry53": "楚国骑兵", "ChuExpeditionArcher53": "楚国弓手",
    "XiaHouseGuard53": "夏氏家兵", "XiaHouseArcher53": "夏氏弓手",
    "ChuSiegeGuard53": "楚军攻城卒", "ChuSiegeCavalry53": "楚军游骑", "ChuSiegeArcher53": "楚军强弓",
    "ZhengHuangmenGuard53": "皇门守卒", "ZhengCityGuard53": "郑都守军", "ZhengCityArcher53": "郑都弓手",
})
HERO_BIOS.update({
    "QuWu53": "楚国公族大夫，字子灵，文武兼备。伐陈时劝楚庄王不可纳夏姬，后来受封申公。",
    "XiaZhengShu53": "陈国司马，夏御叔与夏姬之子，勇力善射。因陈灵公在株林辱及父母，射杀灵公，后被楚军擒获车裂。",
})
PORTRAIT_INDEX_BY_HERO.update({"QuWu53": 45, "XiaZhengShu53": 24})
SPEAKER_PORTRAIT_INDEX.update({
    "陈灵公": 9, "孔宁": 38, "仪行父": 31, "泄冶": 49, "夏征舒": 24, "夏姬": 12,
    "屈巫": 45, "孙叔敖": 45, "楚庄王": 8, "辕颇": 42, "申叔时": 49,
    "唐狡": 35, "乐伯": 34, "公子婴齐": 35, "郑襄公": 7, "公子去疾": 45, "伍参": 31,
})
HISTORICAL_DEATH_HEROES.add("XiaZhengShu53")

_LARGE_BATTLE_MAPS["m085.png"] = (58, 36, 48)
_LARGE_BATTLE_MAPS["m086.png"] = (52, 34, 48)
HERO_LABELS.update({"XunYing54":"荀罃","XunShou54":"荀首","WeiQi54":"魏锜","XiangLao54":"襄老","GongZiGuChen54":"公子谷臣","ChuBiGuard54":"楚中军甲士","ChuBiCavalry54":"楚中军战骑","ChuBiArcher54":"楚中军强弓","JinCenterGuard54":"晋中军甲士","JinCenterCavalry54":"晋中军战骑","JinCenterArcher54":"晋中军弓手","XunFamilyGuard54":"荀氏家兵","JinReturnArcher54":"晋军弓手","ChuSalvageGuard54":"楚军收车卒","ChuSalvageCavalry54":"楚军巡骑"})
HERO_BIOS.update({"XunYing54":"晋国荀氏将领，荀首之子。邲之战被熊负羁生擒，后由父亲以楚国俘虏交换归晋。","XunShou54":"晋国下军大夫，善射。邲战败退后为救子折返楚军，射杀襄老并生擒谷臣。","WeiQi54":"晋国将领。邲战前擅自赴楚挑战，败退时协助荀首生擒公子谷臣。","XiangLao54":"楚国连尹。邲战后收取晋军遗车，被折返的荀首一箭射杀。","GongZiGuChen54":"楚国王族将领。救援襄老时被射伤右腕、魏锜生擒，后用于交换荀罃。"})
PORTRAIT_INDEX_BY_HERO.update({"XunYing54":35,"XunShou54":37,"WeiQi54":33,"XiangLao54":34,"GongZiGuChen54":38})
SPEAKER_PORTRAIT_INDEX.update({"荀林父":37,"士会":31,"先谷":35,"韩厥":45,"栾书":42,"乐伯":34,"鲍癸":38,"孙叔敖":45,"潘党":33,"楚庄王":8,"荀首":37,"魏锜":33,"孙安":31})
HISTORICAL_DEATH_HEROES.add("XiangLao54")

_LARGE_BATTLE_MAPS["m087.png"] = (54, 36, 48)
_LARGE_BATTLE_MAPS["m088.png"] = (48, 32, 48)
HERO_LABELS.update({"ShenShuShi55":"申叔时","ShenXi55":"申犀","WeiKe55":"魏颗","DuHui55":"杜回","ChuSiegeGuard55":"楚军攻城卒","ChuSiegeArcher55":"楚军楼车弓手","SongGateGuard55":"睢阳守卒","SongCityArcher55":"宋军城弓手","JinAmbushGuard55":"晋军伏兵","JinAmbushArcher55":"晋军伏弓","QinAxeGuard55":"秦国刀斧手","QinGuard55":"秦军甲士"})
HERO_BIOS.update({"ShenShuShi55":"楚国贤臣。围宋粮尽时建议筑室耕田，以长期围困假象迫使宋国议和。","ShenXi55":"楚臣申舟之子。父亲奉命过宋被杀，随楚庄王伐宋，请求君王践诺报仇。","WeiKe55":"晋国将领，魏犨之子。遵父亲清醒时遗命保全祖姬，后在青草坡获老人结草相助，生擒杜回。","DuHui55":"秦国力士，惯使一百二十斤开山大斧，率三百刀斧手冲阵，最终在青草坡被魏颗生擒处斩。"})
PORTRAIT_INDEX_BY_HERO.update({"ShenShuShi55":45,"ShenXi55":35,"WeiKe55":33,"DuHui55":25})
SPEAKER_PORTRAIT_INDEX.update({"公子婴齐":35,"申舟":49,"华元":49,"楚庄王":8,"解扬":42,"申犀":35,"申叔时":45,"公子侧":49,"魏颗":33,"魏锜":33,"杜回":25,"老人":31,"羊舌职":45})
HISTORICAL_DEATH_HEROES.add("DuHui55")

_LARGE_BATTLE_MAPS["m089.png"] = (48, 32, 48)
_LARGE_BATTLE_MAPS["m090.png"] = (60, 38, 48)
HERO_LABELS.update({"SunLiangFu56":"孙良夫","ShiJi56":"石稷","ZhongShuYuXi56":"仲叔于奚","GuoZuo56":"国佐","GaoGu56":"高固","XiKe56":"郤克","JiSunXingFu56":"季孙行父","QiQingGong56":"齐顷公","FengChouFu56":"逢丑父","WeiRaidGuard56":"卫军夜袭卒","QiAmbushGuard56":"齐军伏兵","QiAmbushCavalry56":"齐军伏骑","WeiReliefGuard56":"新筑援军","JinCoalitionGuard56":"晋国联军甲士","JinCoalitionArcher56":"晋国联军弓手","QiCenterChariot56":"齐中军战车","QiArcher56":"齐军强弓"})
HERO_BIOS.update({"SunLiangFu56":"卫国上卿。因出使齐国遭嘲笑而誓报其辱，新筑夜袭中遭齐军伏击，后赴晋国请兵。","ShiJi56":"卫国将领。劝孙良夫不可轻敌未被采纳，夜袭失败后率军断后。","ZhongShuYuXi56":"卫国新筑大夫。率本境百余乘救援孙良夫，迫使齐军停止追击。","GuoZuo56":"齐国上卿。多次劝齐顷公守礼，后统军参与新筑、鞌地战事。","GaoGu56":"齐国猛将。鞌战前单车闯入晋营，以巨石击敌并夺车而返。","XiKe56":"晋国郤氏主将。出使齐国受辱后主张伐齐，鞌之战负伤仍击鼓，最终大破齐军。","JiSunXingFu56":"鲁国正卿季文子。出使齐国受辱，与晋卫曹使臣歃血盟誓伐齐。","QiQingGong56":"齐国君主无野。因侮辱四国使臣引发鞌之战，兵败后借逢丑父换衣脱身。","FengChouFu56":"齐顷公车右。鞌之战与君主换衣，代齐侯被韩厥俘获，因忠义获释。"})
PORTRAIT_INDEX_BY_HERO.update({"SunLiangFu56":35,"ShiJi56":45,"ZhongShuYuXi56":33,"GuoZuo56":49,"GaoGu56":34,"XiKe56":37,"JiSunXingFu56":42,"QiQingGong56":7,"FengChouFu56":38})
SPEAKER_PORTRAIT_INDEX.update({"羊舌职":45,"国佐":49,"郤克":37,"石稷":45,"孙良夫":35,"高固":34,"齐顷公":7,"解张":31,"韩厥":42,"逢丑父":38})

_LARGE_BATTLE_MAPS["m091.png"] = (48, 32, 48)
_LARGE_BATTLE_MAPS["m092.png"] = (64, 44, 48)
HERO_LABELS.update({
    "JinLiGong58":"晋厉公","LuanShu58":"栾书","ShiXie58":"士燮","LuanZhen58":"栾鍼","XiZhi58":"郤至","XiQi58":"郤锜","XunYan58":"荀偃",
    "ChuGongWang58":"楚共王","GongZiRenFu58":"公子壬夫","XiongFa58":"熊茷","PanDang58":"潘党","GongYinXiang58":"工尹襄",
    "JinYanlingGuard58":"晋军甲士","JinYanlingArcher58":"晋军弓手","ChuYanlingGuard58":"楚军甲士","ChuYanlingCavalry58":"楚军战骑","ChuYanlingArcher58":"楚军强弓"
})
HERO_BIOS.update({
    "JinLiGong58":"晋国君主州蒲，晋景公之子。即位后依仗三郤与嬖臣，亲率六军与楚国战于鄢陵。",
    "LuanShu58":"晋国中军元帅。鄢陵战前采纳士匄平灶填井之策，使晋军能在营内从容列阵。",
    "ShiXie58":"晋国上军将领范文子。忧虑晋国内政，认为鄢陵获胜反会加速权臣争斗。",
    "LuanZhen58":"栾书幼子。出使楚国时以“整、暇”概括晋军之长，鄢陵混战后仍遣人向子重献酒。",
    "XiZhi58":"晋国新军副将温季，三郤之一。主张讨伐反复从楚的郑国，鄢陵之战参与中军作战。",
    "XiQi58":"晋国上军元帅，三郤之一。鄢陵之战率上军迎击楚国左军。",
    "XunYan58":"晋国将领荀偃，荀林父之子。随晋厉公出征郑国并参加鄢陵之战。",
    "ChuGongWang58":"楚国君主熊审。亲率三军救郑，在鄢陵被魏锜射中左眼，仍令诸军继续作战。",
    "GongZiRenFu58":"楚国右尹，鄢陵之战统率右军，与韩厥所率晋下军交锋。",
    "XiongFa58":"楚共王之子。鄢陵初战追击陷入泥淖的晋厉公，被栾书军追上生擒。",
    "PanDang58":"楚国善射将领，能一箭贯穿七层坚甲；与养由基较艺后心服其百步穿杨之技。",
    "GongYinXiang58":"楚国将领。鄢陵阵前与魏锜交战，魏锜舍他转射楚王。"
})
PORTRAIT_INDEX_BY_HERO.update({"JinLiGong58":7,"LuanShu58":42,"ShiXie58":49,"LuanZhen58":35,"XiZhi58":33,"XiQi58":34,"XunYan58":37,"ChuGongWang58":8,"GongZiRenFu58":38,"XiongFa58":24,"PanDang58":33,"GongYinXiang58":34})
SPEAKER_PORTRAIT_INDEX.update({"晋景公":7,"桑门大巫":31,"屠岸贾":45,"魏相":49,"秦桓公":7,"高缓":45,"华元":49,"栾书":42,"栾鍼":35,"公子侧":49,"士燮":49,"郤至":33,"士匄":35,"潘党":33,"养由基":24,"晋厉公":7,"楚共王":8,"公子婴齐":35,"苗贲皇":45,"魏锜":33})
HISTORICAL_DEATH_HEROES.add("WeiQi54")

_LARGE_BATTLE_MAPS["m093.png"] = (52, 34, 48)
_LARGE_BATTLE_MAPS["m094.png"] = (48, 32, 48)
HERO_LABELS.update({
    "XuTong59":"胥童","YiYangWu59":"夷羊五","QingFeiTui59":"清沸魋","ChengHua59":"程滑",
    "CoupGuard59":"太阴山伏兵","CoupArcher59":"太阴山伏弓","RoyalEscort59":"晋侯近卫","RoyalArcher59":"晋侯弓卫",
    "ZhaoWu59":"赵武","ChengYing59":"程婴","TuHouseGuard59":"屠府家兵","TuHouseArcher59":"屠府弓手"
})
HERO_BIOS.update({
    "XuTong59":"晋厉公宠臣，巧言构陷三郤并引兵入朝；太阴山政变时随厉公出游，被程滑斩杀。",
    "YiYangWu59":"晋厉公嬖臣，参与谋杀三郤，事后被任命为新军元帅；晋悼公即位后以逢君于恶之罪处斩。",
    "QingFeiTui59":"晋国力士，协助长鱼矫刺杀郤犨、郤锜；晋悼公即位后被斩，族人逐出境外。",
    "ChengHua59":"栾书部将，率三百甲士伏于太阴山，斩胥童、擒晋厉公，后奉命献鸩，终被晋悼公治罪。",
    "ZhaoWu59":"赵朔遗子，由程婴、公孙杵臼舍命保全。晋悼公时复官司寇，领兵诛灭屠岸贾，为赵氏雪冤。",
    "ChengYing59":"赵氏门客，以亲子代赵氏孤儿赴死，秘密抚养赵武十五年；赵氏复兴后自刎追随公孙杵臼。"
})
PORTRAIT_INDEX_BY_HERO.update({"XuTong59":45,"YiYangWu59":34,"QingFeiTui59":25,"ChengHua59":38,"ZhaoWu59":35,"ChengYing59":49})
SPEAKER_PORTRAIT_INDEX.update({"胥童":45,"士燮":49,"栾书":42,"荀偃":37,"程滑":38,"孙周":7,"韩厥":42,"晋悼公":7,"赵武":35,"程婴":49,"公子壬夫":38})
HISTORICAL_DEATH_HEROES.update({"XuTong59","YiYangWu59","QingFeiTui59","ChengHua59","TuAnGu50","ChengYing59"})
HERO_LABELS.update({"PalaceDoctor57":"医者","PalaceSearchGuard57":"宫中搜卒","PalaceSearchArcher57":"宫中弓卫"})
HERO_BIOS.update({
    "PalaceDoctor57":"韩厥亲信，乔装医者，以药囊藏匿赵武穿越宫门搜查线，将赵氏孤儿安全送出宫城。",
    "PalaceSearchGuard57":"奉屠岸贾之命搜查宫城的晋国甲士；被击退按撤退处理，不计作史实阵亡。",
    "PalaceSearchArcher57":"封锁宫中大道与东门的晋国弓卫；被击退按撤退处理，不计作史实阵亡。",
})
PORTRAIT_INDEX_BY_HERO.update({"PalaceDoctor57":45})
SPEAKER_PORTRAIT_INDEX.update({
    "国佐":49,"郤克":37,"季孙行父":42,"孙良夫":35,"夏姬":12,"屈巫":45,"楚共王":8,
    "屠岸贾":45,"韩厥":42,"赵朔":35,"赵庄姬":12,"公孙杵臼":31,"程婴":49,"医者":45,
})


_LARGE_BATTLE_MAPS["m095.png"] = (54, 38, 48)
_LARGE_BATTLE_MAPS["m096.png"] = (62, 40, 48)
_LARGE_BATTLE_MAPS["m097.png"] = (56, 42, 48)
HERO_LABELS.update({
    "JinDaoGong60":"晋悼公","LuanYan60":"栾黡","XiangShu60":"向戌","ZhongSunMie60":"仲孙蔑",
    "YuShi60":"鱼石","XiangWeiRen60":"向为人","LinZhu60":"鳞朱","XiangDai60":"向带","YuFu60":"鱼府",
    "JinCoalitionGuard60":"晋国联军甲士","JinCoalitionArcher60":"晋国联军弓手","SongCoalitionGuard60":"宋国联军",
    "PengchengGuard60":"彭城楚军","PengchengArcher60":"彭城楚弓手","ZhuFan60":"诸樊","YiMei60":"夷昧","YuJi60":"余祭",
    "DengLiao60":"邓廖","YinQi60":"尹齐","WuMarine60":"吴国舟师","WuArcher60":"吴国弓手","ChuMarine60":"楚国舟师",
    "ChuRiverArcher60":"楚国舟弓手","ShiGai60":"士匄","ShuLiangHe60":"叔梁纥","QinJinFu60":"秦堇父","DiSiMi60":"狄虒弥",
    "YunBan60":"云般","BiYangLord60":"偪阳君","BiYangGuard60":"偪阳守军","BiYangArcher60":"偪阳弓手"
})
HERO_BIOS.update({
    "JinDaoGong60":"晋国君主周，整顿厉公乱政，任用韩厥、智罃、魏绛等人，多次会合诸侯，恢复晋国霸业。",
    "LuanYan60":"晋国卿大夫栾黡，栾书之子。晋悼公时期参与彭城、偪阳等诸侯会战。",
    "XiangShu60":"宋国大夫向戌。彭城被楚军占据后，以临冲楼车晓谕城中百姓，促使百姓开门擒拿五名叛臣。",
    "ZhongSunMie60":"鲁国正卿仲孙蔑，即孟献子。参与诸侯收复彭城及围攻偪阳，治政崇尚俭朴。",
    "YuShi60":"宋国逃臣鱼石，借楚军攻占彭城，与向为人等据城，后被城中百姓擒获并处死。",
    "XiangWeiRen60":"宋国逃臣向为人，随鱼石依附楚国并据守彭城，诸侯收复彭城后被擒。",
    "LinZhu60":"宋国逃臣鳞朱，依楚返宋据守彭城，最终与鱼石等一同被擒。",
    "XiangDai60":"宋国逃臣向带，参与据守彭城，城中百姓开门后被诸侯联军擒获。",
    "YuFu60":"宋国逃臣鱼府，借楚力据守彭城，城破后与其余四人一同伏法。",
    "ZhuFan60":"吴王寿梦长子诸樊。寿梦病重时主持军政，命夷昧诱敌、余祭伏击，在采石大破楚军。",
    "YiMei60":"吴王寿梦之子夷昧。采石之战率少量舟师诱使邓廖深入，为余祭伏兵创造夹击机会。",
    "YuJi60":"吴王寿梦之子余祭。率舟师埋伏采石，待邓廖深入后截断归路，协助吴军大破楚师。",
    "DengLiao60":"楚国将领，率组甲、被练深入吴境，在采石遭吴军伏击被俘，拒绝投降而死。",
    "YinQi60":"楚国司马尹齐，攻取鸠兹并遣邓廖深入吴境；邓廖败亡、鸠兹失守后忧愤成疾。",
    "ShiGai60":"晋国卿大夫士匄，范文子之子。偪阳久攻不克时请限期督战，最终率联军完成总攻。",
    "ShuLiangHe60":"鲁国勇士叔梁纥，孔子之父。偪阳攻城时力举落下的悬门，使诸侯军得以穿门入城。",
    "QinJinFu60":"鲁国将领秦堇父，偪阳攻城时与狄虒弥奋勇先登，率军突入城中。",
    "DiSiMi60":"鲁国勇士狄虒弥，偪阳之战随秦堇父攀城先登，在北门突破中建立战功。",
    "YunBan60":"偪阳守将云般。城中箭石耗尽后仍率死士巷战，最终战死，偪阳随即投降。",
    "BiYangLord60":"偪阳小国之君。守城二十余日后军民力竭，于云般战死后献城投降。"
})
PORTRAIT_INDEX_BY_HERO.update({"JinDaoGong60":7,"LuanYan60":35,"XiangShu60":49,"ZhongSunMie60":42,"YuShi60":45,"XiangWeiRen60":34,"LinZhu60":33,"XiangDai60":38,"YuFu60":25,"ZhuFan60":7,"YiMei60":35,"YuJi60":38,"DengLiao60":34,"YinQi60":45,"ShiGai60":35,"ShuLiangHe60":25,"QinJinFu60":33,"DiSiMi60":34,"YunBan60":38,"BiYangLord60":8})
SPEAKER_PORTRAIT_INDEX.update({"晋悼公":7,"向戌":49,"仲孙蔑":42,"鱼石":45,"栾黡":35,"尹齐":45,"邓廖":34,"诸樊":7,"夷昧":35,"余祭":38,"智罃":35,"荀偃":37,"士匄":35,"叔梁纥":25,"秦堇父":33,"云般":38,"偪阳君":8})
HISTORICAL_DEATH_HEROES.update({"YuShi60","XiangWeiRen60","LinZhu60","XiangDai60","YuFu60","DengLiao60","YinQi60","YunBan60"})

_LARGE_BATTLE_MAPS["m098.png"]=(50,34,48)
_LARGE_BATTLE_MAPS["m099.png"]=(62,40,48)
_LARGE_BATTLE_MAPS["m100.png"]=(64,38,48)
HERO_LABELS.update({"GongSunXia61":"公孙夏","ZiChan61":"子产","GongSunChai61":"公孙虿","WeiZhi61":"尉止","SiChen61":"司臣","HouJin61":"侯晋","ZhengHouseGuard61":"郑国家甲","ZhengRebel61":"尉氏乱兵","ZhengRebelArcher61":"尉氏弓手","FanYang61":"范鞅","QinJingGong61":"秦景公","YingZhan61":"嬴詹","GongZiWuDi61":"公子无地","QinYulinGuard61":"秦军甲士","QinYulinArcher61":"秦军弓手","WeiXianGong61":"卫献公","GongSunDing61":"公孙丁","SunKuai61":"孙蒯","SunJia61":"孙嘉","GengGongCha61":"庾公差","YinGongTuo61":"尹公佗","GongZiZhuan61":"公子鱄","WeiPalaceGuard61":"卫侯宫甲","SunPursuer61":"孙氏追兵","SunArcher61":"孙氏弓手"})
HERO_BIOS.update({"GongSunXia61":"郑国大夫，字子西。父亲公子騑被尉止杀害后，率家甲攻灭乱党。","ZiChan61":"郑国名臣公孙侨，字子产。尉止之乱时率家甲平乱，后来执政郑国。","GongSunChai61":"郑国公族大夫，尉止之乱中率众协助平乱。","WeiZhi61":"郑国大夫，发动西宫之乱，最终兵败被诛。","FanYang61":"晋国大夫范鞅，随栾鍼突入秦阵，脱围后暂奔秦国。","QinJingGong61":"秦国君主，棫林之役率四百乘迎战诸侯，后接纳范鞅。","YingZhan61":"秦国大将，棫林之役随秦景公合围栾鍼、范鞅。","GongZiWuDi61":"秦国公子，棫林秦军前锋。","WeiXianGong61":"卫国君主衎，轻慢孙林父、宁殖而引发内乱，被逐后逃往齐国。","GongSunDing61":"卫国神射手，护送卫献公出奔，以尹公佗来箭反射将其击杀。","SunKuai61":"孙林父长子，率兵追击出奔的卫献公。","SunJia61":"孙林父之子，与孙蒯一同追击卫献公。","GengGongCha61":"孙氏家臣，公孙丁弟子，去镞发四箭而不伤恩师。","YinGongTuo61":"庾公差弟子，执意追杀卫献公，被公孙丁反射杀死。","GongZiZhuan61":"卫献公同母弟，卫侯出奔时冒死赶来从驾。"})
PORTRAIT_INDEX_BY_HERO.update({"GongSunXia61":35,"ZiChan61":49,"GongSunChai61":38,"WeiZhi61":34,"SiChen61":25,"HouJin61":33,"FanYang61":35,"QinJingGong61":8,"YingZhan61":34,"GongZiWuDi61":38,"WeiXianGong61":7,"GongSunDing61":33,"SunKuai61":35,"SunJia61":38,"GengGongCha61":24,"YinGongTuo61":34,"GongZiZhuan61":25})
SPEAKER_PORTRAIT_INDEX.update({"公孙夏":35,"子产":49,"公孙虿":38,"智罃":35,"栾黡":35,"公子蟜":38,"荀偃":37,"栾鍼":35,"范鞅":35,"秦景公":8,"孙林父":42,"卫献公":7,"公孙丁":33,"尹公佗":34,"庾公差":24})
HISTORICAL_DEATH_HEROES.update({"WeiZhi61","SiChen61","HouJin61","LuanZhen58","YinGongTuo61"})

_LARGE_BATTLE_MAPS["m101.png"]=(86,56,48)
_LARGE_BATTLE_MAPS["m102.png"]=(58,42,48)
_LARGE_BATTLE_MAPS["m103.png"]=(50,36,48)
HERO_LABELS.update({"HanQi62":"韩起","WeiJiang62":"魏绛","ZhouChuo62":"周绰","LuanYing62":"栾盈","QiLingGong62":"齐灵公","XiGuiFu62":"析归父","ZhiChuo62":"殖绰","GuoZui62":"郭最","CuiZhu62":"崔杼","QingFeng62":"庆封","QiCoalitionGuard62":"齐军甲士","QiCoalitionArcher62":"齐军弓手","JinCoalitionGuard62":"晋盟甲士","JinCoalitionArcher62":"晋盟弓手","QiZhuangGong62":"齐庄公","GongLou62":"公娄","SuShaWei62":"肃沙卫","GaotangGuard62":"高唐守军","GaotangArcher62":"高唐弓手","ShuHu62":"叔虎","JiYi62":"箕遗","HuangYuan62":"黄渊","XunWu62":"荀吴","JinArrestGuard62":"晋国甲士"})
HERO_BIOS.update({"HanQi62":"晋国正卿韩起，参与伐齐与诸侯会盟，后来执掌晋政。","WeiJiang62":"晋国名将魏绛，辅佐晋悼公和晋平公，主张和戎以安诸夏。","ZhouChuo62":"晋国勇士，伐齐时追至石门，击败并俘获殖绰、郭最。","LuanYing62":"晋国栾氏之主，受范氏构陷出奔楚国，后来返晋作乱。","QiLingGong62":"齐国君主，恃强与晋争霸，遭十二国联军围攻临淄。","XiGuiFu62":"齐国将领，率军据防门沟壕抵御晋国联军。","ZhiChuo62":"齐国勇将，石门战败被俘，后逃归齐国，又参与高唐夜袭。","GuoZui62":"齐国勇将，与殖绰同守石门被俘，后从高唐东北城角先登入城。","CuiZhu62":"齐国权臣，迎立齐庄公，后来专擅齐国国政。","QingFeng62":"齐国大夫，与崔杼共同迎立齐庄公。","QiZhuangGong62":"齐国君主光，平定高唐肃沙卫之乱，稳定新政。","GongLou62":"高唐工匠，为齐军内应，夜间从东北城角垂绳接引。","SuShaWei62":"齐国叛臣，据高唐坚守一月有余，城破后被处死。","ShuHu62":"晋国栾氏党羽，遭范鞅包围府第，突围被俘后处死。","JiYi62":"晋国栾氏党羽，与叔虎一同冲出府门，被射伤擒获。","HuangYuan62":"晋国栾氏党羽，企图接应叔虎，被荀吴截获。","XunWu62":"晋国大夫，中行氏将领，叔虎府之变中截获黄渊。"})
PORTRAIT_INDEX_BY_HERO.update({"HanQi62":49,"WeiJiang62":35,"ZhouChuo62":38,"LuanYing62":34,"QiLingGong62":8,"XiGuiFu62":34,"ZhiChuo62":35,"GuoZui62":38,"CuiZhu62":49,"QingFeng62":34,"QiZhuangGong62":7,"GongLou62":25,"SuShaWei62":34,"ShuHu62":35,"JiYi62":25,"HuangYuan62":38,"XunWu62":35})
SPEAKER_PORTRAIT_INDEX.update({"荀偃":35,"士匄":35,"赵武":35,"韩起":49,"析归父":34,"殖绰":35,"郭最":38,"齐灵公":8,"齐庄公":7,"公娄":25,"肃沙卫":34,"范鞅":35,"叔虎":35,"箕遗":25,"黄渊":38,"荀吴":35})
HISTORICAL_DEATH_HEROES.update({"SuShaWei62","ShuHu62","JiYi62","HuangYuan62"})

_LARGE_BATTLE_MAPS["m104.png"]=(74,52,48)
_LARGE_BATTLE_MAPS["m105.png"]=(58,42,48)
HERO_LABELS.update({"WeiShu63":"魏舒","DuRong63":"督戎","LuanLe63":"栾乐","LuanFang63":"栾鲂","LuanRong63":"栾荣","XuWu63":"胥午","FeiBao63":"斐豹","XieYong63":"解雍","XieSu63":"解肃","MuGang63":"牟刚","MuJin63":"牟劲","LuanRebelGuard63":"栾氏甲士","LuanRebelArcher63":"栾氏弓手","JinGugongGuard63":"固宫甲士","JinGugongArcher63":"固宫弓手","QuwoGuard63":"曲沃甲士","QuwoArcher63":"曲沃弓手"})
HERO_BIOS.update({"WeiShu63":"晋国魏氏大夫，原欲接应栾盈，被范鞅挟持入固宫后参与平乱。","DuRong63":"栾盈麾下第一勇士，使双戟攻固宫，连败晋将，最终中斐豹伏击而死。","LuanLe63":"栾氏善射猛将，北关火攻一度得手，追射范鞅时翻车被杀。","LuanFang63":"栾氏将领，护栾盈退回曲沃，城破后缒城逃往宋国。","LuanRong63":"栾氏族人，曲沃城破后与栾盈一同被擒处死。","XuWu63":"曲沃守臣，受栾氏旧恩，助栾盈起兵，城破后伏剑自尽。","FeiBao63":"晋国隶人，以免除丹书罪籍为请，设计击杀勇士督戎，升为牙将。","XieYong63":"赵武部将，与弟解肃出战督戎，重伤而死。","XieSu63":"赵武部将，督戎阵前折枪后逃归固宫。","MuGang63":"荀吴部下勇士，与解肃等合战督戎。","MuJin63":"荀吴部下勇士，合战督戎时战死。"})
PORTRAIT_INDEX_BY_HERO.update({"WeiShu63":35,"DuRong63":25,"LuanLe63":33,"LuanFang63":34,"LuanRong63":25,"XuWu63":49,"FeiBao63":25,"XieYong63":25,"XieSu63":38,"MuGang63":25,"MuJin63":38})
SPEAKER_PORTRAIT_INDEX.update({"魏舒":35,"督戎":25,"栾乐":33,"栾鲂":34,"栾盈":34,"胥午":49,"斐豹":25,"辛俞":49})
HISTORICAL_DEATH_HEROES.update({"DuRong63","LuanLe63","LuanYing62","LuanRong63","XuWu63","XieYong63","MuJin63"})

_LARGE_BATTLE_MAPS["m106.png"]=(60,40,48)
_LARGE_BATTLE_MAPS["m107.png"]=(68,46,48)
HERO_LABELS.update({"WangSunHui64":"王孙挥","ShenXianYu64":"申鲜虞","YanMao64":"晏氂","ZhaoSheng64":"赵胜","ZhaoPursuer64":"邯郸骑兵","ZhaoArcher64":"邯郸弓手","QiRetreatGuard64":"齐军甲士","QiRetreatArcher64":"齐军弓手","HuaZhou64":"华周","QiLiang64":"杞梁","XiHouZhong64":"隰侯重","JuLiBiGong64":"莒黎比公","JuGateCaptain64":"且于门将","JuGuard64":"莒国甲士","JuArcher64":"莒国弓手"})
HERO_BIOS.update({"WangSunHui64":"齐国大夫，齐庄公伐晋时统率前军，经孟门登太行。","ShenXianYu64":"齐国将领，随王孙挥统率伐晋前队。","YanMao64":"齐国将领，太行撤军时负责断后，兵败于赵胜而死。","ZhaoSheng64":"晋国邯郸大夫，起本邑之兵追击撤退齐军，斩杀晏氂。","HuaZhou64":"齐国勇士，与杞梁单车深入莒境，身中数十箭后被俘。","QiLiang64":"齐国勇士，且于门冒箭死战，重伤而亡，后世故事广为流传。","XiHouZhong64":"齐国小卒，慕华周、杞梁之勇，以盾伏火沟助二人越过，焚身而死。","JuLiBiGong64":"莒国君主，在莒郊率甲士迎战齐军，后退守且于门。","JuGateCaptain64":"莒国且于门守将，率弓手依托火沟夹门伏射。"})
PORTRAIT_INDEX_BY_HERO.update({"WangSunHui64":35,"ShenXianYu64":49,"YanMao64":34,"ZhaoSheng64":35,"HuaZhou64":25,"QiLiang64":38,"XiHouZhong64":25,"JuLiBiGong64":8,"JuGateCaptain64":33})
SPEAKER_PORTRAIT_INDEX.update({"王孙挥":35,"申鲜虞":49,"晏氂":34,"赵胜":35,"华周":25,"杞梁":38,"隰侯重":25,"莒黎比公":8,"齐庄公":7})
HISTORICAL_DEATH_HEROES.update({"YanMao64","QiLiang64","XiHouZhong64"})

_LARGE_BATTLE_MAPS["m108.png"]=(50,38,48)
_LARGE_BATTLE_MAPS["m109.png"]=(52,36,48)
_LARGE_BATTLE_MAPS["m110.png"]=(70,48,48)
HERO_LABELS.update({"TangWuJiu65":"棠无咎","CuiCheng65":"崔成","CuiJiang65":"崔疆","DongGuoYan65":"东郭偃","JiaJu65":"贾举","ZhouChuoQi65":"州绰","GongSunAo65":"公孙敖","LouYan65":"偻堙","CuiAmbusher65":"崔氏伏甲","QiBraveGuard65":"齐国勇士","NiuChen65":"牛臣","ChaoGuard65":"巢城守军","WuGateGuard65":"吴军甲士","WuGateArcher65":"吴军弓手","NingXi65":"宁喜","YouZaiGu65":"右宰谷","BeiGongYi65":"北宫遗","SunXiang65":"孙襄","ChuDai65":"褚带","YongChu65":"雍鉏","WeiShangGong65":"卫殇公","TaiZiJiao65":"世子角","SunHouseGuard65":"孙氏家甲","SunHouseArcher65":"孙氏弓手","NingHouseGuard65":"宁氏家甲"})
HERO_BIOS.update({"TangWuJiu65":"崔杼继室之子，奉命伏甲崔府，射杀越墙逃走的齐庄公。","CuiCheng65":"崔杼长子，参与崔府伏击，遭公孙敖奋力折断手臂。","CuiJiang65":"崔杼之子，在崔府中门击杀贾举，又以长戈刺死公孙敖。","DongGuoYan65":"崔杼家臣，负责在府门外稳住齐国勇士并暗中夺走兵器。","JiaJu65":"齐庄公勇爵之士，随君入崔府，中伏被杀。","ZhouChuoQi65":"齐庄公勇爵之首，崔府之变中不肯投降，以头触墙殉君。","GongSunAo65":"齐国勇士，崔府中拔系马柱死战，最终被崔疆刺杀。","LouYan65":"齐国勇爵之士，崔府之变中受伤后战死。","NiuChen65":"楚国巢邑守将，藏身短墙之后发箭，射杀攻门的吴王诸樊。","NingXi65":"卫国宁氏大夫，奉父遗命迎献公复位，诛孙襄、废卫殇公后专政。","YouZaiGu65":"卫国右宰，参与攻打孙氏府与迎复卫献公。","BeiGongYi65":"卫国大夫，协助宁喜夜攻孙氏府并发动复位之变。","SunXiang65":"孙林父之子，守孙氏府时中公孙丁一箭，伤重而死。","ChuDai65":"孙氏家将，善射守府，孙襄死后被宁氏乱军杀死。","YongChu65":"孙氏家将，孙府失守后越后墙逃往戚邑。","WeiShangGong65":"卫国君主剽，在位十三年，宁喜迎献公复位时被废杀。","TaiZiJiao65":"卫殇公世子，持剑救父，被公孙丁击杀。"})
PORTRAIT_INDEX_BY_HERO.update({"TangWuJiu65":25,"CuiCheng65":34,"CuiJiang65":38,"DongGuoYan65":49,"JiaJu65":34,"ZhouChuoQi65":35,"GongSunAo65":25,"LouYan65":38,"NiuChen65":33,"NingXi65":49,"YouZaiGu65":49,"BeiGongYi65":35,"SunXiang65":34,"ChuDai65":33,"YongChu65":25,"WeiShangGong65":7,"TaiZiJiao65":38})
SPEAKER_PORTRAIT_INDEX.update({"棠无咎":25,"东郭偃":49,"齐庄公":7,"州绰":35,"牛臣":33,"吴王诸樊":7,"吴王馀祭":7,"宁喜":49,"右宰谷":49,"褚带":33,"公孙丁":33,"卫殇公":7})
HISTORICAL_DEATH_HEROES.update({"QiZhuangGong62","JiaJu65","ZhouChuoQi65","GongSunAo65","LouYan65","ZhuFan60","SunXiang65","ChuDai65","WeiShangGong65","TaiZiJiao65"})

_LARGE_BATTLE_MAPS["m111.png"]=(56,40,48)
_LARGE_BATTLE_MAPS["m112.png"]=(50,38,48)
_LARGE_BATTLE_MAPS["m113.png"]=(68,46,48)
_LARGE_BATTLE_MAPS["m114.png"]=(60,42,48)
HERO_LABELS.update({"GongSunMianYu66":"公孙免馀","LuPuBie66":"卢蒲嫳","QuJian66":"屈建","ZiJiang66":"子疆","XiHuan66":"息桓","QuHuYong66":"屈狐庸","ShuJiuLord66":"舒鸠君","ChuanFengShu66":"穿封戍","GongZiWei66":"公子围","HuangJie66":"皇颉","SunAmbusher66":"孙氏伏弩","WeiRaider66":"卫国袭兵","NingGuard66":"宁氏家甲","QingGuard66":"庆氏家甲","CuiGuard66":"崔氏家甲","ChuShujuGuard66":"楚军甲士","ChuShujuArcher66":"楚军弓手","WuReliefGuard66":"吴国援兵","WuReliefArcher66":"吴国弓手","ZhengGuard66":"郑军甲士"})
HERO_BIOS.update({"GongSunMianYu66":"卫国大夫，趁宁府开门率家甲攻入，杀右宰谷、宁喜。","LuPuBie66":"庆封家臣，诱崔成、崔疆开门后将二人斩首，助庆氏独掌齐政。","QuJian66":"楚国令尹，舒鸠之战设伏栭山，击退吴国援军并灭舒鸠。","ZiJiang66":"楚国将领，奉屈建之命诈败诱吴军进入栭山伏击圈。","XiHuan66":"楚国大夫，随养由基出征舒鸠，收拾败军参与后续伏击。","QuHuYong66":"吴国相国，率兵救援舒鸠，在栭山救出夷昧后败退。","ShuJiuLord66":"舒鸠国君，受吴国诱使叛楚，吴援失败后亡国。","ChuanFengShu66":"楚国县尹，棘泽阵前亲手俘获郑将皇颉，却被公子围争功。","GongZiWei66":"楚康王之弟，棘泽之战与穿封戍争夺擒将之功。","HuangJie66":"郑国将领，棘泽兵败被穿封戍擒获，后在伯州犁暗示下改口。"})
PORTRAIT_INDEX_BY_HERO.update({"GongSunMianYu66":35,"LuPuBie66":49,"QuJian66":49,"ZiJiang66":35,"XiHuan66":49,"QuHuYong66":49,"ShuJiuLord66":8,"ChuanFengShu66":35,"GongZiWei66":38,"HuangJie66":34})
SPEAKER_PORTRAIT_INDEX.update({"雍鉏":25,"孙蒯":35,"殖绰":35,"公孙免馀":35,"宁喜":49,"卢蒲嫳":49,"崔成":34,"屈建":49,"子疆":35,"穿封戍":35,"公子围":38,"皇颉":34})
HISTORICAL_DEATH_HEROES.update({"ZhiChuo62","NingXi65","YouZaiGu65","CuiCheng65","CuiJiang65","TangWuJiu65","DongGuoYan65","CuiZhu62"})

_LARGE_BATTLE_MAPS["m115.png"]=(68,44,48)
_LARGE_BATTLE_MAPS["m116.png"]=(62,42,48)
HERO_LABELS.update({"LuPuGui67":"卢蒲癸","GaoChai67":"高虿","LuanZao67":"栾灶","QingShe67":"庆舍","QingSi67":"庆嗣","QingYi67":"庆遗","GongSunHei67":"公孙黑","SiDai67":"驷带","YinDuan67":"印段","LiangXiao67":"良霄","QiCoalitionGuard67":"齐国四姓甲士","QiCoalitionArcher67":"齐国四姓弓手","QingTempleGuard67":"庆氏庙卫","QingCounterGuard67":"庆氏回援甲士","QingCounterArcher67":"庆氏回援弓手","ZhengGateGuard67":"郑国门卫","ZhengGateArcher67":"郑国守城弓手","LiangHouseGuard67":"良氏家甲","LiangHouseArcher67":"良氏弓手"})
HERO_BIOS.update({"LuPuGui67":"齐国勇士，为报齐庄公之仇潜入庆氏，太庙尝祭时从背后刺杀庆舍。","GaoChai67":"齐国大夫，字子尾，联合栾、陈、鲍诸族围攻太庙，驱逐庆封。","LuanZao67":"齐国大夫，字子雅，与高虿共同反对庆氏专政，参与太庙之变。","QingShe67":"庆封之子，力大勇猛而刚愎，太庙尝祭时被卢蒲癸、王何合击而死。","QingSi67":"庆封族人，随庆封赴东莱田猎，临淄事变后参与西门反攻。","QingYi67":"庆封族人，随庆封出猎并参与西门反攻，失败后随庆氏逃亡。","GongSunHei67":"郑国大夫，与良霄冲突并焚毁良府，后来继续乱政，被子产依法处死。","SiDai67":"公孙黑之侄，奉命与印段守卫郑国北门，击败返攻的良霄。","YinDuan67":"郑国大夫，与驷带共同率勇士在北门迎击良氏家甲。","LiangXiao67":"郑国上卿，字伯有，奢侈嗜酒；良府被焚后返攻北门，战败被杀。"})
PORTRAIT_INDEX_BY_HERO.update({"LuPuGui67":35,"GaoChai67":49,"LuanZao67":49,"QingShe67":34,"QingSi67":35,"QingYi67":34,"GongSunHei67":35,"SiDai67":35,"YinDuan67":34,"LiangXiao67":49})
SPEAKER_PORTRAIT_INDEX.update({"卢蒲癸":35,"卢蒲嫳":49,"高虿":49,"庆姜":27,"庆舍":34,"庆封":38,"晏婴":49,"公孙黑":35,"良霄":49,"驷带":35,"印段":34,"子产":49})
HISTORICAL_DEATH_HEROES.update({"QingShe67","LiangXiao67"})

_LARGE_BATTLE_MAPS["m117.png"]=(72,44,48)
HERO_LABELS.update({"ChenWuYu68":"陈无宇","BaoGuo68":"鲍国","WangHei68":"王黑","LuanShi68":"栾施","GaoQiang68":"高彊","ChenBaoGuard68":"陈鲍家甲","ChenBaoArcher68":"陈鲍弓手","LuanGaoGuard68":"栾高家甲","LuanGaoArcher68":"栾高弓手","QiCitizenGuard68":"齐国义民","QiCitizenArcher68":"齐国义民弓手"})
HERO_BIOS.update({"ChenWuYu68":"齐国陈氏宗主，联合鲍国驱逐栾、高，献出所得财产并广施恩惠，奠定陈氏取齐基础。","BaoGuo68":"齐国鲍氏大夫，误信小竖告密后与陈无宇联兵，参与虎门、东门之战。","WangHei68":"齐国大夫，奉齐景公之命率公徒支援陈、鲍，在东门追逐栾施、高彊。","LuanShi68":"齐国栾氏大夫，嗜酒专政，与高彊结党；虎门兵败后从东门逃往鲁国。","GaoQiang68":"齐国高氏大夫，年轻嗜酒，与栾施共同攻打虎门，败后随栾氏奔鲁。"})
PORTRAIT_INDEX_BY_HERO.update({"ChenWuYu68":49,"BaoGuo68":35,"WangHei68":35,"LuanShi68":34,"GaoQiang68":35})
SPEAKER_PORTRAIT_INDEX.update({"申无宇":49,"楚灵王":8,"薳启疆":49,"鲁昭公":8,"卫灵公":8,"师涓":49,"师旷":49,"晋平公":8,"子产":49,"陈无宇":49,"鲍国":35,"王黑":35,"晏婴":49})

_LARGE_BATTLE_MAPS["m118.png"]=(64,46,48)
HERO_LABELS.update({"ChuLingWang69":"楚灵王","WuJu69":"伍举","GongZiQiJi69":"公子弃疾","CaiLingHou69":"蔡灵侯","CaiShiZiYou69":"蔡世子有","GongSunGuiSheng69":"公孙归生","CaiWei69":"蔡洧","ChaoWu69":"朝吴","ChuSiegeGuard69":"楚国攻城甲士","ChuSiegeArcher69":"楚国攻城弓手","CaiGuard69":"蔡国守军","CaiArcher69":"蔡国弓手"})
HERO_BIOS.update({"ChuLingWang69":"楚共王次子熊围，弑侄自立为楚灵王。扩建章华宫，又借讨逆吞并陈、蔡，国势虽盛而失尽人心。","WuJu69":"楚国大夫伍举，曾直谏楚王，亦为灵王谋划伐陈、诱蔡。其谋使楚国扩地，也助长灵王骄暴。","GongZiQiJi69":"楚共王幼子，受命围攻蔡都，素有当璧之祥。后联合陈蔡旧族推翻楚灵王，即位为楚平王。","CaiLingHou69":"蔡灵侯般，早年弑父自立。被楚灵王诱至申地，醉后与七十名从臣一同被杀。","CaiShiZiYou69":"蔡灵侯之子，父死后摄位守国。蔡都粮尽城破后被俘，终被楚灵王作为九冈山祭品杀害。","GongSunGuiSheng69":"蔡国大夫，曾劝蔡灵侯提防楚王。围城时主持防务、遣使求晋，积劳成疾，于城破前后去世。","CaiWei69":"蔡国大夫蔡洧，父亲蔡略死于申地。奉命突围向晋求援未果，后表面仕楚，暗怀复仇之志。","ChaoWu69":"蔡国大夫公孙归生之子。出城游说公子弃疾反楚，以当璧之祥相劝，蔡亡后留事弃疾。"})
PORTRAIT_INDEX_BY_HERO.update({"ChuLingWang69":8,"WuJu69":49,"GongZiQiJi69":7,"CaiLingHou69":8,"CaiShiZiYou69":7,"GongSunGuiSheng69":49,"CaiWei69":35,"ChaoWu69":42})
SPEAKER_PORTRAIT_INDEX.update({"公子胜":35,"伍举":49,"楚灵王":8,"公子招":49,"公孙归生":49,"蔡灵侯":8,"蔡世子有":7,"公子弃疾":7,"蔡洧":35,"朝吴":42,"申无宇":49,"薳启疆":49,"晏婴":49,"斗成然":35,"公孙瑕":49,"囊瓦":35})

_LARGE_BATTLE_MAPS["m119.png"]=(68,46,48)
HERO_LABELS.update({"ZiGan70":"子干","ZiXi70":"子皙","XiaNie70":"夏啮","XuWuMou70":"须务牟","DouChengRan70":"斗成然","WeiPi70":"薳罢","ShiZiLu70":"世子禄","GongZiBa70":"公子罢","ChenCaiGuard70":"陈蔡义军","ChenCaiArcher70":"陈蔡弓手","ChuPalaceGuard70":"楚宫甲士","ChuPalaceArcher70":"楚宫弓手"})
HERO_BIOS.update({"ZiGan70":"楚共王之子、楚灵王之弟，流亡晋国后被迎回郢都即位，旋因诈报灵王返城而自尽。","ZiXi70":"楚共王之子，流亡郑国。随子干返楚任令尹，误信灵王归来，先于兄长自刎。","XiaNie70":"陈国夏征舒后裔，响应复陈之举，率陈人协助公子弃疾袭取郢都。","XuWuMou70":"公子弃疾家臣，担任陈蔡联军先锋，率精甲先行突入郢都。","DouChengRan70":"楚国郊尹，与公子弃疾交好，郢都兵变时为内应，后参与诈报并迎立楚平王。","WeiPi70":"楚灵王所任令尹，郢都失守时欲奉世子禄出奔，不能进入王宫，最终自刎。","ShiZiLu70":"楚灵王太子，奉命留守郢都。公子弃疾联军入宫后被杀。","GongZiBa70":"楚灵王之子，郢都兵变中与世子禄一同守宫，被公子弃疾军杀死。"})
PORTRAIT_INDEX_BY_HERO.update({"ZiGan70":7,"ZiXi70":49,"XiaNie70":35,"XuWuMou70":25,"DouChengRan70":49,"WeiPi70":42,"ShiZiLu70":8,"GongZiBa70":34})
SPEAKER_PORTRAIT_INDEX.update({"郑丹":49,"观从":49,"朝吴":42,"公子弃疾":7,"夏啮":35,"须务牟":25,"蔡洧":35,"子干":7,"子皙":49,"斗成然":49,"楚平王":7,"申亥":35,"楚灵王":8,"晏婴":49,"羊舌肸":49,"齐景公":8})
HISTORICAL_DEATH_HEROES.update({"WeiPi70","ShiZiLu70","GongZiBa70"})

_LARGE_BATTLE_MAPS["m120.png"]=(52,38,48)
_LARGE_BATTLE_MAPS["m121.png"]=(64,36,48)
_LARGE_BATTLE_MAPS["m122.png"]=(72,44,48)
_LARGE_BATTLE_MAPS["m123.png"]=(92,64,48)
_LARGE_BATTLE_MAPS["m124.png"]=(58,42,48)
_LARGE_BATTLE_MAPS["m125.png"]=(62,42,48)
_LARGE_BATTLE_MAPS["m126.png"]=(70,50,48)
HERO_LABELS.update({'TianKaiJiang71': '田开疆', 'GuYeZi71': '古冶子', 'YingShuang71': '嬴爽', 'XuJun71': '徐君', 'QiGuard71': '齐国甲士', 'QiArcher71': '齐国弓手', 'XuGuard71': '徐国甲士', 'XuArcher71': '徐国弓手', 'WuYuan72': '伍员', 'GongZiSheng72': '公子胜', 'HuangFuNe72': '皇甫讷', 'ZhaoGuanCaptain72': '昭关守将', 'ZhaoGuard72': '昭关甲士', 'ZhaoArcher72': '昭关弓手', 'JiGuang73': '公子光', 'GongZiGai73': '公子盖余', 'XiaNie73': '夏啮', 'WeiYue73': '魏越', 'HuGong73': '胡国君', 'ShenGong73': '沈国君', 'WuGuard73': '吴军锐士', 'WuArcher73': '吴军弓手', 'CoalitionGuard73': '楚属联军', 'CoalitionArcher73': '楚属弓手', 'WuHelu79': '吴王阖闾', 'SunWu75': '孙武', 'FuGai75': '夫概', 'BoPi75': '伯嚭', 'NangWa75': '囊瓦', 'ShenYinShu75': '沈尹戌', 'TangHou75': '唐成公', 'ChuGuard75': '楚军甲士', 'ChuArcher75': '楚军弓手', 'QinRelief75': '秦国援军', 'LuDingGong78': '鲁定公', 'JiSunSi78': '季孙斯', 'YangHu78': '阳虎', 'YangYue78': '阳越', 'GongShanBuNiu78': '公山不狃', 'ShuSunZhe78': '叔孙辄', 'LuGuard78': '鲁宫甲士', 'LuRebel78': '鲁国叛军', 'LuRebelArcher78': '叛军弓手', 'GouJian79': '越王勾践', 'LingGuFu79': '灵姑浮', 'FanLi79': '范蠡', 'WenZhong79': '文种', 'WuZiXu79': '伍子胥', 'ZhuanYi79': '专毅', 'FuChai80': '吴王夫差', 'YueGuard79': '越国甲士', 'YueArcher79': '越国弓手', 'WuGuard79': '吴国甲士', 'WuArcher79': '吴国弓手'})
HERO_BIOS.update({'TianKaiJiang71': '齐景公勇士，奉命伐徐，在蒲隧阵斩徐将嬴爽；后因二桃之谋与公孙捷、古冶子一同自尽。', 'GuYeZi71': '齐景公勇士，曾在黄河斩鼋救主。随田开疆伐徐，后来卷入二桃杀三士之局。', 'YingShuang71': '徐国大将，蒲隧迎战齐军，被田开疆斩杀。', 'XuJun71': '徐国国君，齐军兵临蒲隧后遣使请降。', 'QiGuard71': '齐国征徐步卒。', 'QiArcher71': '齐国征徐弓手。', 'XuGuard71': '徐国蒲隧守军。', 'XuArcher71': '徐国蒲隧守军。', 'WuYuan72': '字子胥，楚臣伍奢之子。父兄被害后逃楚入吴，辅佐阖闾破楚，后谏夫差不纳而死。', 'GongZiSheng72': '楚太子建之子，随伍员出逃，后被送往郑国。', 'HuangFuNe72': '东皋公友人，与伍员相貌相似，在昭关以换衣调包之计引开守军。', 'ZhaoGuanCaptain72': '奉画像盘查伍员的楚军关将。', 'ZhaoGuard72': '封锁昭关的楚军。', 'ZhaoArcher72': '驻守关墙的楚军弓手。', 'JiGuang73': '吴王诸樊之子，率军在鸡父击破楚国诸侯联军，后使专诸刺王僚，自立为吴王阖闾。', 'GongZiGai73': '吴国公子，鸡父之战率军分击胡、沈两国。', 'XiaNie73': '楚国将领，鸡父之战率陈军先战，被公子光击杀。', 'WeiYue73': '楚国将领，鸡父之战后军溃败，自度不能免罪而死。', 'HuGong73': '随楚军攻吴，在鸡父兵败被吴军俘获。', 'ShenGong73': '随楚军攻吴，在鸡父兵败被吴军俘获。', 'WuGuard73': '吴国鸡父之战步卒。', 'WuArcher73': '吴国鸡父之战弓手。', 'CoalitionGuard73': '楚与陈、胡、沈等国联军。', 'CoalitionArcher73': '楚与属国联军弓手。', 'WuHelu79': '吴王诸樊之子公子光。任用伍员、孙武强吴，柏举破楚；后伐越在携李负伤而死。', 'SunWu75': '兵家孙武，著《孙子兵法》。辅佐吴王阖闾整军，在柏举之战以奇正相生大破楚军。', 'FuGai75': '吴王阖闾之弟，柏举之战力主先击楚军，率部突阵取胜，后曾自立为王。', 'BoPi75': '楚臣伯州犁之后，奔吴受伍员举荐。参与破楚，后为吴太宰。', 'NangWa75': '楚令尹子常，贪赂失诸侯，柏举统军屡败，弃军逃郑。', 'ShenYinShu75': '楚国贤将，反对囊瓦速战。柏举败后回军救郢，力战重伤，自命部下取首复命。', 'TangHou75': '唐国国君，受囊瓦勒索后导吴伐楚；秦兵救楚时战败身亡。', 'ChuGuard75': '柏举战场楚军。', 'ChuArcher75': '柏举战场楚军。', 'QinRelief75': '申包胥哭秦庭后赶到楚国的秦军。', 'LuDingGong78': '鲁国国君，夹谷会盟时由孔子摄相事，后经历阳虎、公山不狃等国内叛乱。', 'JiSunSi78': '鲁国季氏宗主，阳虎专政时受制，后与鲁君合力平叛。', 'YangHu78': '鲁国季氏家臣，专权后发动叛乱，兵败逃亡齐、晋。', 'YangYue78': '阳虎同党，攻鲁南门时中箭身亡。', 'GongShanBuNiu78': '季氏费邑宰，后来联合叔孙辄攻鲁宫，兵败逃齐。', 'ShuSunZhe78': '鲁国叔孙氏成员，与公山不狃起兵攻宫，失败后出奔。', 'LuGuard78': '保卫鲁君的甲士。', 'LuRebel78': '阳虎及公山不狃部众。', 'LuRebelArcher78': '鲁国内乱中的弓手。', 'GouJian79': '越王允常之子。携李破吴，后夫椒败而臣吴，归国卧薪尝胆，最终灭吴称霸。', 'LingGuFu79': '越国勇将，携李之战以戈击伤吴王阖闾足趾。', 'FanLi79': '越国谋臣，辅佐勾践忍辱图强、灭吴复国；功成后泛舟五湖。', 'WenZhong79': '越国大夫，夫椒败后赴吴议和，主持越国政务并助勾践复国。', 'WuZiXu79': '伍员入吴后的称号。辅吴破楚，力谏夫差灭越，最终被赐剑自尽。', 'ZhuanYi79': '吴国将领，携李护卫阖闾，负伤后不久身亡。', 'FuChai80': '阖闾之子。夫椒大败越军并受勾践臣服，后北上争霸，最终被越国所灭。', 'YueGuard79': '越军步卒。', 'YueArcher79': '越军弓手。', 'WuGuard79': '吴军步卒。', 'WuArcher79': '吴军弓手。'})
PORTRAIT_INDEX_BY_HERO.update({'TianKaiJiang71': 35, 'GuYeZi71': 25, 'YingShuang71': 35, 'XuJun71': 7, 'QiGuard71': 25, 'QiArcher71': 33, 'XuGuard71': 25, 'XuArcher71': 33, 'WuYuan72': 49, 'GongZiSheng72': 35, 'HuangFuNe72': 49, 'ZhaoGuanCaptain72': 25, 'ZhaoGuard72': 25, 'ZhaoArcher72': 33, 'JiGuang73': 7, 'GongZiGai73': 35, 'XiaNie73': 35, 'WeiYue73': 35, 'HuGong73': 7, 'ShenGong73': 7, 'WuGuard73': 25, 'WuArcher73': 33, 'CoalitionGuard73': 25, 'CoalitionArcher73': 33, 'WuHelu79': 7, 'SunWu75': 49, 'FuGai75': 35, 'BoPi75': 49, 'NangWa75': 49, 'ShenYinShu75': 35, 'TangHou75': 7, 'ChuGuard75': 25, 'ChuArcher75': 33, 'QinRelief75': 35, 'LuDingGong78': 7, 'JiSunSi78': 49, 'YangHu78': 35, 'YangYue78': 35, 'GongShanBuNiu78': 25, 'ShuSunZhe78': 49, 'LuGuard78': 25, 'LuRebel78': 25, 'LuRebelArcher78': 33, 'GouJian79': 7, 'LingGuFu79': 35, 'FanLi79': 49, 'WenZhong79': 49, 'WuZiXu79': 49, 'ZhuanYi79': 35, 'FuChai80': 7, 'YueGuard79': 25, 'YueArcher79': 33, 'WuGuard79': 25, 'WuArcher79': 33})
SPEAKER_PORTRAIT_INDEX.update({'田开疆': 35, '古冶子': 25, '嬴爽': 35, '徐君': 7, '齐国甲士': 25, '齐国弓手': 33, '徐国甲士': 25, '徐国弓手': 33, '伍员': 49, '公子胜': 35, '皇甫讷': 49, '昭关守将': 25, '昭关甲士': 25, '昭关弓手': 33, '公子光': 7, '公子盖余': 35, '夏啮': 35, '魏越': 35, '胡国君': 7, '沈国君': 7, '吴军锐士': 25, '吴军弓手': 33, '楚属联军': 25, '楚属弓手': 33, '吴王阖闾': 7, '孙武': 49, '夫概': 35, '伯嚭': 49, '囊瓦': 49, '沈尹戌': 35, '唐成公': 7, '楚军甲士': 25, '楚军弓手': 33, '秦国援军': 35, '鲁定公': 7, '季孙斯': 49, '阳虎': 35, '阳越': 35, '公山不狃': 25, '叔孙辄': 49, '鲁宫甲士': 25, '鲁国叛军': 25, '叛军弓手': 33, '越王勾践': 7, '灵姑浮': 35, '范蠡': 49, '文种': 49, '伍子胥': 49, '专毅': 35, '吴王夫差': 7, '越国甲士': 25, '越国弓手': 33, '吴国甲士': 25, '吴国弓手': 33})
HISTORICAL_DEATH_HEROES.update({"YingShuang71","XiaNie73","WeiYue73","ShenYinShu75","TangHou75","YangYue78","WuHelu79","ZhuanYi79"})


# Dongzhou chapter 81 metadata
_LARGE_BATTLE_MAPS["m127.png"]=(60,42,48)
HERO_LABELS.update({'ChenQi81': '陈乞', 'BaoMu81': '鲍牧', 'GaoZhang81': '高张', 'GuoXia81': '国夏', 'QiClanGuard81': '齐国大夫家甲', 'QiClanArcher81': '齐国大夫弓手', 'GaoHouseGuard81': '高氏家甲', 'GaoHouseArcher81': '高氏弓手', 'GuoHouseGuard81': '国氏家甲', 'GuoHouseArcher81': '国氏弓手', 'GongZiYangSheng81': '公子阳生', 'XiShi81': '西施', 'YueNv81': '南林处女', 'ChenYin81': '陈音', 'ChenHeng81': '陈恒', 'ZiGong81': '子贡'})
HERO_BIOS.update({'ChenQi81': '齐国陈氏宗主，联合鲍氏攻高、国二族，废安孺子而立齐悼公。', 'BaoMu81': '齐国鲍氏大夫，与陈乞共同攻高、国，后遭齐悼公猜忌诛杀。', 'GaoZhang81': '齐景公托孤重臣，与国夏辅佐安孺子，在高国之乱中战死。', 'GuoXia81': '齐景公托孤重臣，高张被杀后出奔莒国。', 'QiClanGuard81': '陈、鲍及齐国诸大夫召集的家甲。', 'QiClanArcher81': '陈、鲍及齐国诸大夫麾下弓手。', 'GaoHouseGuard81': '守卫高张府邸的齐国甲士。', 'GaoHouseArcher81': '守卫高张府邸的齐国弓手。', 'GuoHouseGuard81': '守卫国夏府邸的齐国甲士。', 'GuoHouseArcher81': '守卫国夏府邸的齐国弓手。', 'GongZiYangSheng81': '齐景公长子，被陈乞迎回临淄，废安孺子即位为齐悼公。', 'XiShi81': '越国苎萝山施氏女，被献入吴宫，成为越国美人计的关键人物。', 'YueNv81': '南林剑术高手，受越王聘请训练越军三千人。', 'ChenYin81': '避仇入越的楚国射师，为越国训练连弩手三千。', 'ChenHeng81': '陈乞之子，毒杀齐悼公，后被子贡说服移兵强吴。', 'ZiGong81': '孔子弟子端木赐，为救鲁周游齐、吴、越、晋。'})
PORTRAIT_INDEX_BY_HERO.update({'ChenQi81': 49, 'BaoMu81': 35, 'GaoZhang81': 34, 'GuoXia81': 42, 'QiClanGuard81': 25, 'QiClanArcher81': 33, 'GaoHouseGuard81': 25, 'GaoHouseArcher81': 33, 'GuoHouseGuard81': 25, 'GuoHouseArcher81': 33, 'GongZiYangSheng81': 7, 'XiShi81': 21, 'YueNv81': 24, 'ChenYin81': 33, 'ChenHeng81': 49, 'ZiGong81': 45})
SPEAKER_PORTRAIT_INDEX.update({'陈乞': 49, '鲍牧': 35, '高张': 34, '国夏': 42, '齐国大夫家甲': 25, '齐国大夫弓手': 33, '高氏家甲': 25, '高氏弓手': 33, '国氏家甲': 25, '国氏弓手': 33, '公子阳生': 7, '西施': 21, '南林处女': 24, '陈音': 33, '陈恒': 49, '子贡': 45})
HISTORICAL_DEATH_HEROES.update({"GaoZhang81"})


# Dongzhou chapters 82-108 metadata
_LARGE_BATTLE_MAPS.update({'m128.png': (48, 34, 48), 'm129.png': (52, 38, 48), 'm130.png': (56, 42, 48), 'm131.png': (60, 34, 48), 'm132.png': (48, 38, 48), 'm133.png': (52, 42, 48), 'm134.png': (56, 34, 48), 'm135.png': (60, 38, 48), 'm136.png': (52, 42, 48), 'm137.png': (52, 34, 48), 'm138.png': (60, 38, 48), 'm139.png': (64, 42, 48), 'm140.png': (48, 34, 48), 'm141.png': (56, 38, 48), 'm142.png': (56, 42, 48), 'm143.png': (60, 34, 48), 'm144.png': (48, 38, 48), 'm145.png': (56, 42, 48), 'm146.png': (56, 34, 48), 'm147.png': (60, 38, 48), 'm148.png': (48, 42, 48), 'm149.png': (52, 34, 48), 'm150.png': (60, 38, 48), 'm151.png': (64, 42, 48), 'm152.png': (48, 34, 48), 'm153.png': (52, 38, 48), 'm154.png': (56, 42, 48), 'm155.png': (64, 34, 48)})
HERO_LABELS.update({'LateZhouGuardOwn': '后期诸侯甲士', 'LateZhouArcherOwn': '后期诸侯弓弩手', 'LateZhouGuardEnemy': '敌军甲士', 'LateZhouArcherEnemy': '敌军弓弩手', 'XuMenChao82': '胥门巢', 'GuoShu82': '国书', 'ZhaoWuXu84': '赵无恤', 'ZhangMengTan84': '张孟谈', 'ZhiBo84': '智伯瑶', 'LeYang85': '乐羊', 'XiMenBao85': '西门豹', 'ZhongShanJun85': '中山君', 'WuQi86': '吴起', 'LuMuGong86': '鲁穆公', 'QiJiang86': '齐军主将', 'ShangYang87': '卫鞅', 'QinXiaoGong87': '秦孝公', 'ChuBianJiang87': '楚国边将', 'TianJi88': '田忌', 'SunBin88': '孙膑', 'PangJuan88': '庞涓', 'KuangZhang91': '匡章', 'QiXuanWang91': '齐宣王', 'ZiZhi91': '子之', 'WeiZhang92': '魏章', 'QinHuiWenWang92': '秦惠文王', 'QuGai92': '屈匄', 'GongZiCheng93': '公子成', 'LiDui93': '李兑', 'ZhaoZhang93': '公子章', 'MengChangJun94': '孟尝君', 'QiMinWang94': '齐湣王', 'SongKangWang94': '宋康王', 'LeYi95': '乐毅', 'YanZhaoWang95': '燕昭王', 'TianDan95': '田单', 'QiXiangWang95': '齐襄王', 'QiJie95': '骑劫', 'ZhaoShe96': '赵奢', 'LianPo96': '廉颇', 'HuShang96': '胡伤', 'BaiQi97': '白起', 'FanJu97': '范雎', 'MangMao97': '芒卯', 'WangHe98': '王龁', 'ZhaoKuo98': '赵括', 'PingYuanJun99': '平原君', 'WangLing99': '王陵', 'XinLingJun100': '信陵君', 'ZhuHai100': '朱亥', 'QinJiang100': '秦军主将', 'YueCheng101': '乐乘', 'LiFu101': '栗腹', 'PangNuan102': '庞煖', 'MengAo102': '蒙骜', 'ZhaoDaoXiangWang102': '赵悼襄王', 'JuXin102': '剧辛', 'QinWangZheng103': '秦王政', 'WangJian103': '王翦', 'FanYuQi103': '樊於期', 'ChangPingJun104': '昌平君', 'LaoAi104': '嫪毐', 'LiMu105': '李牧', 'ZhaoCong105': '赵葱', 'HuanYi105': '桓齮', 'SiMaShang106': '司马尚', 'XiangYan107': '项燕', 'LiXin107': '李信', 'MengTian108': '蒙恬', 'QiWangJian108': '齐王建'})
HERO_BIOS.update({'LateZhouGuardOwn': '战国后期各国主力步卒。', 'LateZhouArcherOwn': '战国后期各国弓弩部队。', 'LateZhouGuardEnemy': '本关敌军主力步卒。', 'LateZhouArcherEnemy': '本关敌军弓弩部队。', 'XuMenChao82': '胥门巢，参与艾陵之战，其行动与结局依《东周列国志》本回叙事呈现。', 'GuoShu82': '国书，参与艾陵之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoWuXu84': '赵无恤，参与晋阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhangMengTan84': '张孟谈，参与晋阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhiBo84': '智伯瑶，参与晋阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'LeYang85': '乐羊，参与中山之战，其行动与结局依《东周列国志》本回叙事呈现。', 'XiMenBao85': '西门豹，参与中山之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhongShanJun85': '中山君，参与中山之战，其行动与结局依《东周列国志》本回叙事呈现。', 'WuQi86': '吴起，参与鲁齐之战，其行动与结局依《东周列国志》本回叙事呈现。', 'LuMuGong86': '鲁穆公，参与鲁齐之战，其行动与结局依《东周列国志》本回叙事呈现。', 'QiJiang86': '齐军主将，参与鲁齐之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ShangYang87': '卫鞅，参与商於拓境，其行动与结局依《东周列国志》本回叙事呈现。', 'QinXiaoGong87': '秦孝公，参与商於拓境，其行动与结局依《东周列国志》本回叙事呈现。', 'ChuBianJiang87': '楚国边将，参与商於拓境，其行动与结局依《东周列国志》本回叙事呈现。', 'TianJi88': '田忌，参与桂陵之战，其行动与结局依《东周列国志》本回叙事呈现。', 'SunBin88': '孙膑，参与桂陵之战，其行动与结局依《东周列国志》本回叙事呈现。', 'PangJuan88': '庞涓，参与桂陵之战，其行动与结局依《东周列国志》本回叙事呈现。', 'KuangZhang91': '匡章，参与齐军平燕，其行动与结局依《东周列国志》本回叙事呈现。', 'QiXuanWang91': '齐宣王，参与齐军平燕，其行动与结局依《东周列国志》本回叙事呈现。', 'ZiZhi91': '子之，参与齐军平燕，其行动与结局依《东周列国志》本回叙事呈现。', 'WeiZhang92': '魏章，参与丹阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'QinHuiWenWang92': '秦惠文王，参与丹阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'QuGai92': '屈匄，参与丹阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'GongZiCheng93': '公子成，参与沙丘宫变，其行动与结局依《东周列国志》本回叙事呈现。', 'LiDui93': '李兑，参与沙丘宫变，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoZhang93': '公子章，参与沙丘宫变，其行动与结局依《东周列国志》本回叙事呈现。', 'MengChangJun94': '孟尝君，参与五国伐宋，其行动与结局依《东周列国志》本回叙事呈现。', 'QiMinWang94': '齐湣王，参与五国伐宋，其行动与结局依《东周列国志》本回叙事呈现。', 'SongKangWang94': '宋康王，参与五国伐宋，其行动与结局依《东周列国志》本回叙事呈现。', 'LeYi95': '乐毅，参与乐毅伐齐，其行动与结局依《东周列国志》本回叙事呈现。', 'YanZhaoWang95': '燕昭王，参与乐毅伐齐，其行动与结局依《东周列国志》本回叙事呈现。', 'TianDan95': '田单，参与即墨火牛阵，其行动与结局依《东周列国志》本回叙事呈现。', 'QiXiangWang95': '齐襄王，参与即墨火牛阵，其行动与结局依《东周列国志》本回叙事呈现。', 'QiJie95': '骑劫，参与即墨火牛阵，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoShe96': '赵奢，参与阏与之战，其行动与结局依《东周列国志》本回叙事呈现。', 'LianPo96': '廉颇，参与阏与之战，其行动与结局依《东周列国志》本回叙事呈现。', 'HuShang96': '胡伤，参与阏与之战，其行动与结局依《东周列国志》本回叙事呈现。', 'BaiQi97': '白起，参与华阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'FanJu97': '范雎，参与华阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'MangMao97': '芒卯，参与华阳之战，其行动与结局依《东周列国志》本回叙事呈现。', 'WangHe98': '王龁，参与长平之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoKuo98': '赵括，参与长平之战，其行动与结局依《东周列国志》本回叙事呈现。', 'PingYuanJun99': '平原君，参与邯郸保卫战，其行动与结局依《东周列国志》本回叙事呈现。', 'WangLing99': '王陵，参与邯郸保卫战，其行动与结局依《东周列国志》本回叙事呈现。', 'XinLingJun100': '信陵君，参与窃符救赵，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhuHai100': '朱亥，参与窃符救赵，其行动与结局依《东周列国志》本回叙事呈现。', 'QinJiang100': '秦军主将，参与窃符救赵，其行动与结局依《东周列国志》本回叙事呈现。', 'YueCheng101': '乐乘，参与鄗代之战，其行动与结局依《东周列国志》本回叙事呈现。', 'LiFu101': '栗腹，参与鄗代之战，其行动与结局依《东周列国志》本回叙事呈现。', 'PangNuan102': '庞煖，参与华阴破秦，其行动与结局依《东周列国志》本回叙事呈现。', 'MengAo102': '蒙骜，参与华阴破秦，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoDaoXiangWang102': '赵悼襄王，参与葫芦河之战，其行动与结局依《东周列国志》本回叙事呈现。', 'JuXin102': '剧辛，参与葫芦河之战，其行动与结局依《东周列国志》本回叙事呈现。', 'QinWangZheng103': '秦王政，参与咸阳讨逆，其行动与结局依《东周列国志》本回叙事呈现。', 'WangJian103': '王翦，参与咸阳讨逆，其行动与结局依《东周列国志》本回叙事呈现。', 'FanYuQi103': '樊於期，参与咸阳讨逆，其行动与结局依《东周列国志》本回叙事呈现。', 'ChangPingJun104': '昌平君，参与嫪毐之乱，其行动与结局依《东周列国志》本回叙事呈现。', 'LaoAi104': '嫪毐，参与嫪毐之乱，其行动与结局依《东周列国志》本回叙事呈现。', 'LiMu105': '李牧，参与肥下之战，其行动与结局依《东周列国志》本回叙事呈现。', 'ZhaoCong105': '赵葱，参与肥下之战，其行动与结局依《东周列国志》本回叙事呈现。', 'HuanYi105': '桓齮，参与肥下之战，其行动与结局依《东周列国志》本回叙事呈现。', 'SiMaShang106': '司马尚，参与井陉抗秦，其行动与结局依《东周列国志》本回叙事呈现。', 'XiangYan107': '项燕，参与城父败李信，其行动与结局依《东周列国志》本回叙事呈现。', 'LiXin107': '李信，参与城父败李信，其行动与结局依《东周列国志》本回叙事呈现。', 'MengTian108': '蒙恬，参与六国归一，其行动与结局依《东周列国志》本回叙事呈现。', 'QiWangJian108': '齐王建，参与六国归一，其行动与结局依《东周列国志》本回叙事呈现。'})
PORTRAIT_INDEX_BY_HERO.update({'LateZhouGuardOwn': 25, 'LateZhouArcherOwn': 33, 'LateZhouGuardEnemy': 25, 'LateZhouArcherEnemy': 33, 'XuMenChao82': 35, 'GuoShu82': 35, 'ZhaoWuXu84': 35, 'ZhangMengTan84': 49, 'ZhiBo84': 35, 'LeYang85': 35, 'XiMenBao85': 49, 'ZhongShanJun85': 7, 'WuQi86': 35, 'LuMuGong86': 7, 'QiJiang86': 35, 'ShangYang87': 49, 'QinXiaoGong87': 7, 'ChuBianJiang87': 35, 'TianJi88': 35, 'SunBin88': 49, 'PangJuan88': 35, 'KuangZhang91': 35, 'QiXuanWang91': 7, 'ZiZhi91': 35, 'WeiZhang92': 35, 'QinHuiWenWang92': 7, 'QuGai92': 35, 'GongZiCheng93': 35, 'LiDui93': 35, 'ZhaoZhang93': 35, 'MengChangJun94': 49, 'QiMinWang94': 35, 'SongKangWang94': 7, 'LeYi95': 35, 'YanZhaoWang95': 7, 'TianDan95': 49, 'QiXiangWang95': 7, 'QiJie95': 35, 'ZhaoShe96': 35, 'LianPo96': 35, 'HuShang96': 35, 'BaiQi97': 35, 'FanJu97': 49, 'MangMao97': 35, 'WangHe98': 35, 'ZhaoKuo98': 35, 'PingYuanJun99': 35, 'WangLing99': 35, 'XinLingJun100': 35, 'ZhuHai100': 49, 'QinJiang100': 35, 'YueCheng101': 35, 'LiFu101': 35, 'PangNuan102': 35, 'MengAo102': 35, 'ZhaoDaoXiangWang102': 7, 'JuXin102': 35, 'QinWangZheng103': 7, 'WangJian103': 35, 'FanYuQi103': 35, 'ChangPingJun104': 49, 'LaoAi104': 35, 'LiMu105': 35, 'ZhaoCong105': 35, 'HuanYi105': 35, 'SiMaShang106': 35, 'XiangYan107': 35, 'LiXin107': 35, 'MengTian108': 35, 'QiWangJian108': 7})
SPEAKER_PORTRAIT_INDEX.update({'后期诸侯甲士': 25, '后期诸侯弓弩手': 33, '敌军甲士': 25, '敌军弓弩手': 33, '胥门巢': 35, '国书': 35, '赵无恤': 35, '张孟谈': 49, '智伯瑶': 35, '乐羊': 35, '西门豹': 49, '中山君': 7, '吴起': 35, '鲁穆公': 7, '齐军主将': 35, '卫鞅': 49, '秦孝公': 7, '楚国边将': 35, '田忌': 35, '孙膑': 49, '庞涓': 35, '匡章': 35, '齐宣王': 7, '子之': 35, '魏章': 35, '秦惠文王': 7, '屈匄': 35, '公子成': 35, '李兑': 35, '公子章': 35, '孟尝君': 49, '齐湣王': 35, '宋康王': 7, '乐毅': 35, '燕昭王': 7, '田单': 49, '齐襄王': 7, '骑劫': 35, '赵奢': 35, '廉颇': 35, '胡伤': 35, '白起': 35, '范雎': 49, '芒卯': 35, '王龁': 35, '赵括': 35, '平原君': 35, '王陵': 35, '信陵君': 35, '朱亥': 49, '秦军主将': 35, '乐乘': 35, '栗腹': 35, '庞煖': 35, '蒙骜': 35, '赵悼襄王': 7, '剧辛': 35, '秦王政': 7, '王翦': 35, '樊於期': 35, '昌平君': 49, '嫪毐': 35, '李牧': 35, '赵葱': 35, '桓齮': 35, '司马尚': 35, '项燕': 35, '李信': 35, '蒙恬': 35, '齐王建': 7})
HISTORICAL_DEATH_HEROES.update({'QiJie95', 'JuXin102', 'XiangYan107', 'ZhaoKuo98', 'LiFu101', 'ZiZhi91', 'ZhiBo84', 'LaoAi104', 'PangJuan88', 'ZhaoZhang93'})






# Dongzhou supplemental chapters 71-108 metadata
_LARGE_BATTLE_MAPS.update({'m156.png': (48, 38, 48), 'm157.png': (56, 42, 48), 'm158.png': (56, 34, 48), 'm159.png': (60, 38, 48), 'm160.png': (52, 42, 48), 'm161.png': (52, 34, 48), 'm162.png': (60, 38, 48), 'm163.png': (64, 42, 48), 'm164.png': (52, 34, 48), 'm165.png': (52, 38, 48), 'm166.png': (56, 42, 48), 'm167.png': (64, 34, 48), 'm168.png': (52, 38, 48), 'm169.png': (56, 42, 48)})
HERO_LABELS.update({'WuChengHei72': '武城黑', 'ZhuanZhu73': '专诸', 'WuWangLiao73': '吴王僚', 'YaoLi74': '要离', 'QingJi74': '庆忌', 'ChuZhaoWang76': '楚昭王', 'ShenBaoXu77': '申包胥', 'ZiPu77': '子蒲', 'ZiLu82': '子路', 'ShiQi82': '石乞', 'YeGong83': '叶公高', 'BaiGongSheng83': '白公胜', 'YuRang84': '豫让', 'QinXianGong86': '秦献公', 'YingJiu101': '嬴樛', 'ZhangTang101': '张唐', 'ZhouNanWang101': '周赧王', 'JingKe107': '荆轲', 'MengWu108': '蒙武'})
HERO_BIOS.update({'WuChengHei72': '武城黑，参与城父追骑；本关行动与结局依《东周列国志》原文呈现。', 'ZhuanZhu73': '专诸，参与鱼肠刺僚；本关行动与结局依《东周列国志》原文呈现。', 'WuWangLiao73': '吴王僚，参与鱼肠刺僚；本关行动与结局依《东周列国志》原文呈现。', 'YaoLi74': '要离，参与江上刺庆忌；本关行动与结局依《东周列国志》原文呈现。', 'QingJi74': '庆忌，参与江上刺庆忌；本关行动与结局依《东周列国志》原文呈现。', 'ChuZhaoWang76': '楚昭王，参与郢都攻防；本关行动与结局依《东周列国志》原文呈现。', 'ShenBaoXu77': '申包胥，参与秦楚复郢；本关行动与结局依《东周列国志》原文呈现。', 'ZiPu77': '子蒲，参与秦楚复郢；本关行动与结局依《东周列国志》原文呈现。', 'ZiLu82': '子路，参与子路结缨；本关行动与结局依《东周列国志》原文呈现。', 'ShiQi82': '石乞，参与子路结缨；本关行动与结局依《东周列国志》原文呈现。', 'YeGong83': '叶公高，参与叶公平楚；本关行动与结局依《东周列国志》原文呈现。', 'BaiGongSheng83': '白公胜，参与叶公平楚；本关行动与结局依《东周列国志》原文呈现。', 'YuRang84': '豫让，参与豫让击衣；本关行动与结局依《东周列国志》原文呈现。', 'QinXianGong86': '秦献公，参与西河攻秦；本关行动与结局依《东周列国志》原文呈现。', 'YingJiu101': '嬴樛，参与秦灭西周；本关行动与结局依《东周列国志》原文呈现。', 'ZhangTang101': '张唐，参与秦灭西周；本关行动与结局依《东周列国志》原文呈现。', 'ZhouNanWang101': '周赧王，参与秦灭西周；本关行动与结局依《东周列国志》原文呈现。', 'JingKe107': '荆轲，参与荆轲刺秦；本关行动与结局依《东周列国志》原文呈现。', 'MengWu108': '蒙武，参与王翦灭楚；本关行动与结局依《东周列国志》原文呈现。'})
PORTRAIT_INDEX_BY_HERO.update({'WuChengHei72': 35, 'ZhuanZhu73': 35, 'WuWangLiao73': 7, 'YaoLi74': 35, 'QingJi74': 35, 'ChuZhaoWang76': 7, 'ShenBaoXu77': 49, 'ZiPu77': 35, 'ZiLu82': 35, 'ShiQi82': 35, 'YeGong83': 35, 'BaiGongSheng83': 35, 'YuRang84': 35, 'QinXianGong86': 7, 'YingJiu101': 35, 'ZhangTang101': 35, 'ZhouNanWang101': 7, 'JingKe107': 35, 'MengWu108': 35})
SPEAKER_PORTRAIT_INDEX.update({'武城黑': 35, '专诸': 35, '吴王僚': 7, '要离': 35, '庆忌': 35, '楚昭王': 7, '申包胥': 49, '子蒲': 35, '子路': 35, '石乞': 35, '叶公高': 35, '白公胜': 35, '豫让': 35, '秦献公': 7, '嬴樛': 35, '张唐': 35, '周赧王': 7, '荆轲': 35, '蒙武': 35})
HISTORICAL_DEATH_HEROES.update({'JingKe107', 'QingJi74', 'XiangYan107', 'WuWangLiao73', 'BaiGongSheng83', 'YaoLi74', 'ZhuanZhu73', 'YuRang84', 'ZiLu82'})

if _original_name == "__main__":
    if getattr(sys, "frozen", False) and "--scenario" not in sys.argv:
        sys.argv.extend(["--scenario", "dongzhou"])
    main()
