#!/usr/bin/env python3
"""Build deterministic character voice cards and a full dialogue production plan."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from runtime_speech import extract_runtime_speech


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"
EXTRA_STORY_PATHS = (ROOT / "web-game" / "scenario" / "map-elites-chuisha.json",)
STAGE_DIR = ROOT / "web-game" / "scenario" / "stage"
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
SECTIONS = ("intro", "events", "victory", "defeat")
NARRATION_SPEAKERS = {"", "旁白", "原著", "史官"}
SYSTEM_SPEAKERS = {"军令", "下回预告", "下一回预告", "下关提示"}
EXCLUDED_SPEAKERS = NARRATION_SPEAKERS | SYSTEM_SPEAKERS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


FIRST_CHAPTER_OVERRIDES = {
    "周宣王": {
        "gender": "male",
        "ageBand": "late_middle",
        "role": "ruler",
        "ageBasis": "《史记·周本纪》称太子静在召公家长大，共和十四年后即位；本关跨宣王三十九年至四十六年，因此即使按共和初年尚幼的下限估计，此时也已年过五旬。",
        "ageConfidence": "medium",
        "estimatedAgeRange": "宣王三十九年约53-65岁以上；四十六年约60-72岁以上",
        "ageSources": ["《史记·周本纪》共和十四年、太子静长于召公家", "《史记·周本纪》宣王三十九年千亩之败", "《东周列国志》第一回宣王三十九年至四十六年"],
        "identityDirection": "年过五旬的男性君主，明确的低沉男中音；气息仍完整，但经历长期在位与千亩败绩后已有疲惫和猜忌。威势来自判断与停顿，不是青年公子式的轻快、漂亮或玩世不恭。",
    },
    "伯阳父": {
        "gender": "male",
        "ageBand": "mature",
        "role": "scholar_minister",
        "ageBasis": "《国语·周语上》记伯阳父在幽王二年仍以太史身份论三川震；小说把他前置到宣王三十九年，约早九年。此时应是能长期任职的成熟男性史官，但没有证据把他处理成衰老者。",
        "ageConfidence": "low",
        "estimatedAgeRange": "约45-60岁，仅为任职跨度下的宽区间推测",
        "ageSources": ["《国语·周语上》幽王二年伯阳父论三川震", "《东周列国志》第一回宣王三十九年太史伯阳父"],
        "identityDirection": "四十至六十岁的成熟男性史官，清晰的中低男声，理性、干燥而稳定；解释灾异像在向君主陈述判断，不用老婆婆声、柔弱气声、神秘腔或衰老颤音。",
    },
    "杜伯": {
        "gender": "male",
        "ageBand": "elder",
        "role": "senior_minister",
        "ageBasis": "用户明确指定为老臣；《墨子·明鬼下》只证其为宣王臣、无罪被杀及临刑誓言，不载确切年龄。",
        "ageConfidence": "medium",
        "identityDirection": "年长老臣，中低音，气息完整，阅历深而精神锐利；悲愤来自论理和克制，不靠粗嗓或哭喊。",
    },
    "左儒": {
        "gender": "male",
        "ageBand": "elder",
        "role": "senior_minister",
        "ageBasis": "用户明确指定为老臣；人物年龄缺少可靠数字，按与杜伯同朝相谏的资深臣僚关系推断。",
        "ageConfidence": "medium",
        "identityDirection": "年长老臣，音色比杜伯略亮，语势更急但气息稳定；忠直来自清楚的判断，不用夸张哭腔。",
    },
    "尹吉甫": {
        "gender": "male",
        "ageBand": "elder",
        "role": "senior_general",
        "ageBasis": "周宣王时期资深卿士与军事统帅；确切出生年不详，按剧情末期的长期任事经历推断。",
        "ageConfidence": "medium",
        "identityDirection": "年长武臣，胸腔共鸣稳，警示王驾时果断清楚，不用武夫吼腔。",
    },
    "乡民": {
        "gender": "male",
        "ageBand": "adult",
        "role": "commoner",
        "ageBasis": "剧情能确认他是携妻入城售卖桑弓箕袋、能独自远行逃难的已婚成年乡民；没有确切年龄记载。",
        "ageConfidence": "high",
        "estimatedAgeRange": "约30-50岁，仅依据婚姻、劳作与逃难能力作宽区间推测",
        "ageSources": ["《东周列国志》第一回乡民夫妇入城售卖桑弓箕袋、妻被处死、本人逃亡"],
        "identityDirection": "三十至五十岁的男性乡民和体力劳作者，中低男声，不是明亮轻快的现代都市青年。妻子刚被官府无理处死，他正仓皇逃命：惊惧、悲痛和被权力压住的愤怒落在短促呼吸、迟疑与压低的重音里；不要广告腔、偶像剧腔、少年感、滑稽农民腔或夸张哭喊。",
    },
}

HISTORICAL_ELDER_OVERRIDES = {
    "百里奚": "叙事传统明确强调其年高而后入秦任政，按老年贤臣处理。",
    "蹇叔": "叙事中为百里奚故交并以老臣身份谏伐郑，按老年谋臣处理。",
    "王翦": "后期剧情直接称王翦为老将，按老年统帅处理。",
    "烛之武": "《左传》叙事中的资深郑臣形象，确切年龄不详，按年长使臣保守处理。",
}

FEMALE_NAMES = {
    "褒姒", "申后", "文姜", "宣姜", "庄姜", "戴妫", "夷姜", "息妫", "骊姬", "穆姬",
    "齐姜", "怀嬴", "文嬴", "夏姬", "赵庄姬", "孟嬴", "伯嬴", "西施", "郑旦", "贾君",
    "叔隗", "季隗", "桃花夫人", "许穆夫人", "定姜", "声姜", "哀姜", "少姜", "南子",
    "太后", "王后", "夫人", "宫女", "祭氏", "穆嬴", "向夫人", "秦姬", "越女",
}

REFERENCE_TEXT = "今日风声清朗，远近人声都听得分明；我把话说完，请诸位从容决断。"
FORBIDDEN_STYLE = ["刻意粗哑", "衰弱颤音", "戏曲腔", "评书腔", "新闻播音腔", "短视频腔", "无依据的方言", "夸张哭喊"]


FIRST_CHAPTER_PERFORMANCE = {
    ("周宣王", "市井孩童唱的是何等妖言？速召百官入朝解说！"): {
        "speechAct": "alarmed_command", "emotion": "wary_suspicion", "intensity": 0.62,
        "pace": 1.02, "pauseStrength": 0.58, "dominance": 0.66, "styleAnchor": "wary_command",
        "emotionAfter": "suspicion_hardened", "subtext": "战败后的不安被童谣刺中，急于让群臣给出可控制的解释。",
        "pivotWords": ["何等妖言", "速召百官"], "focusWords": ["妖言", "百官", "解说"],
        "pausePlan": "在质问后短停；命令段更短，不使用播报式四字等时。",
        "longMemory": "千亩战败后王师伤亡惨重，宣王由中兴之主转为疲惫多疑。",
    },
    ("周宣王", "传旨天下：严禁制造贩卖檿弧箕箙，见者即拿；并搜捕宫中弃女。"): {
        "speechAct": "cold_command", "emotion": "controlled_fear", "intensity": 0.46,
        "pace": 0.94, "pauseStrength": 0.62, "dominance": 0.76, "styleAnchor": "cold_command",
        "emotionAfter": "fear_externalized_as_control", "subtext": "把无法确认的恐惧转化为分条行政命令。",
        "pivotWords": ["传旨天下", "并搜捕"], "focusWords": ["严禁", "见者即拿", "弃女"],
        "pausePlan": "冒号后短停，分号处中停；每项命令长度不同，句尾收紧。",
        "longMemory": "童谣与龙漦传说使宣王相信王室将受女子威胁。",
    },
    ("周宣王", "那弃女至今无踪，司市官杜伯办事不力，推出斩首！"): {
        "speechAct": "scapegoating_sentence", "emotion": "cold_blame", "intensity": 0.54,
        "pace": 0.92, "pauseStrength": 0.64, "dominance": 0.82, "styleAnchor": "cold_threat",
        "emotionAfter": "authoritarian_certainty", "subtext": "以杜伯承担搜捕失败，借处刑恢复君权确定性。",
        "pivotWords": ["办事不力", "推出斩首"], "focusWords": ["杜伯", "不力", "斩首"],
        "pausePlan": "前两分句平冷；宣判前停顿，斩首二字短硬，不喊。",
        "longMemory": "弃女多年无踪，梦兆再次触发宣王对失控的恐惧。",
    },
    ("周宣王", "君叫臣死，臣不得不死。再敢多言，与杜伯同罪！"): {
        "speechAct": "authoritarian_threat", "emotion": "cold_intimidation", "intensity": 0.52,
        "pace": 0.88, "pauseStrength": 0.70, "dominance": 0.88, "styleAnchor": "cold_threat",
        "emotionAfter": "opposition_suppressed", "subtext": "拒绝讨论杜伯有罪与否，以君权迫使左儒闭嘴。",
        "pivotWords": ["再敢多言"], "focusWords": ["死", "同罪"],
        "pausePlan": "前句缓慢陈说既定秩序；句号后停顿，再压低音量发出威胁。",
        "longMemory": "左儒公开挑战处刑决定，宣王需要立即压制朝堂反对。",
    },
    ("周宣王", "今日围猎，众卿随寡人尽兴而归！"): {
        "speechAct": "public_ceremonial_command", "emotion": "performed_ease", "intensity": 0.40,
        "pace": 0.98, "pauseStrength": 0.42, "dominance": 0.62, "styleAnchor": "ceremonial_restraint",
        "emotionAfter": "public_ease_masking_fear", "subtext": "在百官面前维持君主从容，并不知道复仇者已出现。",
        "pivotWords": ["尽兴而归"], "focusWords": ["众卿", "寡人"],
        "pausePlan": "自然招呼群臣，不使用新闻开场腔，不持续高声。",
        "longMemory": "杜伯伏诛已三年，宣王表面恢复日常王者仪态。",
    },
    ("杜伯", "臣奉命搜访多年，并无踪迹。无罪而杀臣，何以服天下？"): {
        "speechAct": "reasoned_remonstrance", "emotion": "restrained_indignation", "intensity": 0.50,
        "pace": 0.88, "pauseStrength": 0.72, "dominance": 0.54, "styleAnchor": "reasoned_remonstrance",
        "emotionAfter": "dignified_defiance", "subtext": "仍按臣礼陈述事实，同时逼问处刑的正当性。",
        "pivotWords": ["无罪而杀臣"], "focusWords": ["奉命", "无踪迹", "无罪", "服天下"],
        "pausePlan": "事实陈述后停顿；质问逐步加压，句尾不扬成普通疑问句。",
        "longMemory": "杜伯奉命搜访多年而无结果，如今被当作搜捕失败的替罪者。",
    },
    ("杜伯", "若死者无知，此事便休；若死者有知，三年之内，必使王知妄杀之报。"): {
        "speechAct": "cold_vow", "emotion": "grief_to_resolve", "intensity": 0.58,
        "pace": 0.82, "pauseStrength": 0.82, "dominance": 0.70, "styleAnchor": "cold_vow",
        "emotionAfter": "resolved_vengeance", "subtext": "停止向君王求理，转而以死后复仇建立最后的裁决。",
        "pivotWords": ["若死者有知", "三年之内"], "focusWords": ["三年之内", "妄杀之报"],
        "pausePlan": "分号处长停并改变重心；后半更确定但不提高整体音量，句尾收紧。",
        "longMemory": "杜伯申辩失败、被无罪处死，左儒也因收尸自刎。",
    },
    ("杜伯", "赤弓在手，白矢已发。周王，偿还你滥杀忠良的血债吧！"): {
        "speechAct": "vengeance_accusation", "emotion": "controlled_vengeance", "intensity": 0.72,
        "pace": 0.94, "pauseStrength": 0.66, "dominance": 0.84, "styleAnchor": "accusatory_action",
        "emotionAfter": "vengeance_in_motion", "subtext": "复仇已经开始，不再寻求解释，只宣告因果。",
        "pivotWords": ["周王"], "focusWords": ["白矢已发", "滥杀忠良", "血债"],
        "pausePlan": "动作陈述短促；称呼周王后停顿，再把血债落到句尾。",
        "longMemory": "三年前临刑誓报，如今以赤弓白矢在东郊兑现誓言。",
    },
    ("杜伯", "周王，白矢在此！"): {
        "speechAct": "battle_strike", "emotion": "decisive_action", "intensity": 0.76,
        "pace": 1.06, "pauseStrength": 0.42, "dominance": 0.86, "styleAnchor": "battle_action",
        "emotionAfter": "strike_released", "subtext": "出手瞬间确认目标，不再解释旧案。",
        "pivotWords": ["周王"], "focusWords": ["白矢", "在此"],
        "pausePlan": "称呼后极短停，后半一气完成；短促有动作感。",
        "longMemory": "杜伯已突破王师护卫，正兑现三年前的誓言。",
    },
    ("左儒", "杜伯无罪。王若必杀忠臣，臣愿以死相谏！"): {
        "speechAct": "sacrificial_remonstrance", "emotion": "urgent_moral_resolve", "intensity": 0.58,
        "pace": 0.90, "pauseStrength": 0.74, "dominance": 0.60, "styleAnchor": "sacrificial_remonstrance",
        "emotionAfter": "resolve_to_die", "subtext": "最后一次以臣礼阻止处刑，并公开承担同死风险。",
        "pivotWords": ["王若必杀忠臣"], "focusWords": ["无罪", "忠臣", "以死相谏"],
        "pausePlan": "第一句先定案；条件句后停顿，再清楚说出自己的选择。",
        "longMemory": "左儒亲见杜伯奉命多年却因无结果被处刑。",
    },
    ("左儒", "昏王可还记得无罪而死的杜大夫？今日东郊，正是鸣冤之时！"): {
        "speechAct": "vengeance_interrogation", "emotion": "contained_accusation", "intensity": 0.68,
        "pace": 0.86, "pauseStrength": 0.76, "dominance": 0.74, "styleAnchor": "accusatory",
        "emotionAfter": "vengeance_declared", "subtext": "迫使宣王重新面对被压下的旧案，并宣告复仇时刻。",
        "pivotWords": ["今日东郊"], "focusWords": ["可还记得", "无罪", "鸣冤之时"],
        "pausePlan": "逼问句尾不做普通上扬；问句后长停，再冷静宣告。",
        "longMemory": "左儒为杜伯收尸后自刎，三年后与杜伯一同现身东郊。",
    },
    ("左儒", "他们护的是王驾，我们讨的是公道。不要滥伤军士，直取那位不肯听谏的人！"): {
        "speechAct": "disciplined_battle_command", "emotion": "principled_resolve", "intensity": 0.62,
        "pace": 0.96, "pauseStrength": 0.60, "dominance": 0.72, "styleAnchor": "disciplined_command",
        "emotionAfter": "focused_action", "subtext": "复仇对象是拒谏的君王，不把普通军士当作泄愤目标。",
        "pivotWords": ["不要滥伤军士"], "focusWords": ["公道", "军士", "直取"],
        "pausePlan": "先区分立场，再清楚限制伤害范围；最后下达目标明确的命令。",
        "longMemory": "左儒索命但仍坚持旧日进谏时的道德边界。",
    },
    ("左儒", "王师势众，今日未能使沉冤昭雪……"): {
        "speechAct": "exhausted_withdrawal", "emotion": "spent_grief", "intensity": 0.34,
        "pace": 0.78, "pauseStrength": 0.78, "dominance": 0.34, "styleAnchor": "exhausted_defeat",
        "emotionAfter": "unresolved_grievance", "subtext": "行动失败但旧案没有结束，不是哭诉或认罪。",
        "pivotWords": ["未能"], "focusWords": ["沉冤", "昭雪"],
        "pausePlan": "气息逐步耗散，省略号自然退出；不使用衰弱老人颤音。",
        "longMemory": "复仇行动受挫，王师仍占优势，沉冤暂未昭雪。",
    },
}


STYLE_ANCHOR_DIRECTIONS = {
    "wary_command": ("殿外的风声不对。传近臣入内，我要听清来由。", "战败后警觉而疲惫，质问后迅速下令，不使用播报节拍。"),
    "cold_command": ("此事分三路查办。先封路，再验人，最后回报。", "低能量、分条、冷静的行政命令，停顿不等长。"),
    "cold_threat": ("话已经说尽。再越一步，便按旧令处置。", "压低音量，以确定性威胁，不咆哮。"),
    "ceremonial_restraint": ("诸卿随行，今日只循旧礼，不必喧哗。", "公开场合的克制从容，不像新闻主持。"),
    "reasoned_remonstrance": ("臣只陈事实，再请问一句：此令何以服众？", "年长老臣先论理后质问，受辱但保持清晰。"),
    "cold_vow": ("若此理已绝，我便不再申辩；余下之事，自有后来。", "从申辩转为冷静誓言，分号处长停，句尾收紧。"),
    "accusatory_action": ("旧案未结，今日便当面说清。欠下的债，现在来还。", "控诉已经转为行动，重音确定但不持续高声。"),
    "battle_action": ("目标已近。看准这一箭，出手！", "短句、动作感、呼吸完整，不喊成口号。"),
    "sacrificial_remonstrance": ("此人无罪。若仍要行刑，臣愿承担进谏之罪。", "保留臣礼的冒死进谏，急迫但不哭腔。"),
    "accusatory": ("你可还记得旧日之事？今日我只问这一句。", "压住悲愤的逼问，问句后长停。"),
    "disciplined_command": ("不要伤及旁人。守住道路，只取真正的目标。", "有原则的战场指令，清楚限制伤害范围。"),
    "exhausted_defeat": ("今日未成，只得暂退。此事并没有结束……", "受挫后的能量耗散，保持男性老臣声纹，不做衰弱颤音。"),
}


def stable_hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def split_story_text(text: str, max_length: int = 110) -> list[str]:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if not clean:
        return []
    if len(clean) <= max_length:
        return [clean]
    sentences = re.findall(r"[^。！？；]+[。！？；]?", clean) or [clean]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) > max_length:
            chunks.append(current)
            current = ""
        if len(sentence) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(sentence[index:index + max_length] for index in range(0, len(sentence), max_length))
        else:
            current += sentence
    if current:
        chunks.append(current)
    return chunks


def normalized_entries(raw: object) -> list[dict]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        return [item for item in raw.values() if isinstance(item, dict)]
    return []


def infer_gender(speaker: str) -> tuple[str, str]:
    if speaker in FEMALE_NAMES or re.search(r"夫人|王后|太后|王妃|公主|女|姬$|妫$|姜$|嬴$", speaker):
        return "female", "name_or_title"
    return "male", "historical_office_default"


def infer_role(speaker: str, all_text: str) -> str:
    if re.search(r"王$|王政$|公$|侯$|君$|天子$|皇帝$", speaker):
        return "ruler"
    if re.search(r"后$|太后|夫人|王妃|公主", speaker):
        return "royal_woman"
    if re.search(r"太子|世子|公子|王子|储君", speaker):
        return "royal_heir"
    if re.search(r"将军|守将|先锋|都尉|司马|武士|勇士|军士|士卒|守军|骑|卒", speaker + all_text[:80]):
        return "military"
    if re.search(r"百姓|乡民|村民|樵夫|渔父|商人|宫女|内侍|寺人|使者|传令", speaker):
        return "commoner_or_attendant"
    if re.search(r"史|卜|太宰|太师|太傅|国老", speaker):
        return "scholar_minister"
    return "minister_or_gentry"


def infer_age(speaker: str, role: str, all_text: str) -> tuple[str, str, str]:
    if speaker in HISTORICAL_ELDER_OVERRIDES:
        return "elder", HISTORICAL_ELDER_OVERRIDES[speaker], "medium"
    context = all_text[:1200]
    if re.search(rf"{re.escape(speaker)}[^。]{{0,12}}(?:年老|老迈|老臣|老将|高龄)|(?:老臣|老将)[^。]{{0,12}}{re.escape(speaker)}", context):
        return "elder", "同关文本直接出现年老、老臣或老将描述。", "high"
    if re.search(rf"{re.escape(speaker)}[^。]{{0,12}}(?:尚幼|年幼|孺子)|(?:尚幼|年幼|孺子)[^。]{{0,12}}{re.escape(speaker)}", context):
        return "child", "同关文本直接出现尚幼、年幼或孺子描述。", "high"
    if role == "royal_heir":
        return "young_adult", "仅由公子、世子或太子身份保守推断；该称谓不等同于确切年龄。", "low"
    if role in {"ruler", "scholar_minister"}:
        return "mature", "史料未提供本场确切年龄，按已任国君或高级职官的成年阶段保守处理。", "low"
    return "adult", "史料与本关文本未提供确切年龄，仅确认其承担成年社会或军事职责。", "low"


def identity_direction(gender: str, age_band: str, role: str, variant: int) -> str:
    age = {
        "child": "少年声线，发声自然，不使用成人装嫩腔",
        "young_adult": "青年声线，气息清楚，不轻浮",
        "adult": "成年声线，气息稳定",
        "mature": "成熟声线，重心稳定，保留自然口语感",
        "late_middle": "晚中年声线，中低区更扎实，但不刻意压嗓",
        "elder": "年长声线，气息完整、精神清楚，不用衰弱颤音表现年龄",
    }[age_band]
    gender_text = "女性" if gender == "female" else "男性"
    role_text = {
        "ruler": "久居上位，威势来自停顿与判断",
        "royal_woman": "礼制环境中表达克制，避免宫斗剧模板",
        "royal_heir": "受过礼仪训练，称谓与句读清楚",
        "military": "军旅人物，声音有穿透力但不持续吼叫",
        "commoner_or_attendant": "自然生活化，不采用播音式字正腔圆",
        "scholar_minister": "文臣语气，论理清楚而非说教",
        "senior_minister": "资深臣僚，判断清楚、情绪内收",
        "senior_general": "资深武臣，胸腔稳定、命令简洁",
        "minister_or_gentry": "士大夫语气，清楚克制",
        "commoner": "朴素自然，反应真实",
    }.get(role, "表达自然克制")
    resonance = ("音色偏清瘦", "音色中性温厚", "音色偏沉静", "音色明晰而不尖锐")[variant % 4]
    return f"{gender_text}，{age}；{role_text}；{resonance}。"


def hard_acoustic_constraint(gender: str, age_band: str) -> str:
    if gender == "male":
        age_target = {
            "child": "a naturally young male child voice",
            "young_adult": "a clearly male young-adult voice, not androgynous",
            "adult": "a clearly adult male voice with stable chest resonance",
            "mature": "a mature male baritone or low tenor with full breath support",
            "late_middle": "a late-middle-aged male baritone with a lower center of gravity",
            "elder": "an older male voice with full breath support, never a grandmother voice",
        }[age_band]
        return (
            f"HARD ACOUSTIC CONSTRAINT: the speaker is male; use {age_target}. "
            "Never generate a female, grandmotherly, falsetto, breathy-high, boyish, or androgynous voice."
        )
    return (
        "HARD ACOUSTIC CONSTRAINT: the speaker is female; use a natural female vocal identity matching the stated age. "
        "Never generate a male, falsetto imitation, or age-inappropriate voice."
    )


def conservative_age_range(age_band: str) -> str:
    return {
        "child": "少年阶段；缺少可核验生年，不给具体岁数",
        "young_adult": "青年阶段；缺少可核验生年，不给具体岁数",
        "adult": "成年阶段；缺少可核验生年，不给具体岁数",
        "mature": "成熟至中年阶段；缺少可核验生年，不给具体岁数",
        "late_middle": "晚中年阶段；缺少可核验生年，不给具体岁数",
        "elder": "老年阶段；缺少可核验生年，不给具体岁数",
    }[age_band]


def social_performance_constraint(role: str) -> str:
    return {
        "ruler": "权力位置高，语气由决断、停顿和他人服从构成，不采用浮夸贵公子或暴君模板。",
        "royal_woman": "处于宗法和宫廷礼制中，表达需结合处境，不套用柔弱、妖媚或宫斗模板。",
        "royal_heir": "受礼制约束但权力尚不稳，区分礼仪训练、个人判断与处境压力。",
        "military": "军旅身份通过命令效率、呼吸和现场压力体现，不用持续吼叫或粗嗓模板。",
        "commoner_or_attendant": "结合劳作、服役及权力距离表现，不用现代客服腔、都市青年腔或滑稽底层模板。",
        "scholar_minister": "以论理、观察和对君主的风险判断体现身份，不用神秘算命腔或说教播音腔。",
        "senior_minister": "资深臣僚的分量来自判断和进谏风险，不用衰弱老人或脸谱忠臣腔。",
        "senior_general": "资深统帅保持完整气息和指令清晰度，不把年龄等同于虚弱或沙哑。",
        "minister_or_gentry": "结合礼制、政治风险与对话对象表达，不使用统一士大夫播音模板。",
        "commoner": "结合劳作、家庭损失和官府压力表达，不用现代都市青年、广告或滑稽农民模板。",
    }.get(role, "依据场景中的权力关系和现实后果表达，不使用职业脸谱腔。")


def make_card(speaker: str, texts: list[str], stage_context: str) -> dict:
    if speaker in FIRST_CHAPTER_OVERRIDES:
        data = dict(FIRST_CHAPTER_OVERRIDES[speaker])
        gender_basis = "manual_historical_review"
    else:
        gender, gender_basis = infer_gender(speaker)
        role = infer_role(speaker, stage_context)
        age_band, age_basis, age_confidence = infer_age(speaker, role, stage_context)
        data = {
            "gender": gender,
            "ageBand": age_band,
            "role": role,
            "ageBasis": age_basis,
            "ageConfidence": age_confidence,
        }
        data["identityDirection"] = identity_direction(gender, age_band, role, int(stable_hash(speaker, 4), 16))
    data.setdefault("estimatedAgeRange", conservative_age_range(data["ageBand"]))
    data.setdefault("ageSources", ["本地关卡剧情文本与角色职掌；未发现可核验的精确生年"])
    data["identityReviewStatus"] = "manual_historical_review" if speaker in FIRST_CHAPTER_OVERRIDES else "inferred_requires_review"
    data["genderConfidence"] = "high" if gender_basis in {"manual_historical_review", "name_or_title"} else "low"
    data["socialPerformanceConstraint"] = social_performance_constraint(data["role"])
    direction = data["identityDirection"]
    acoustic_constraint = hard_acoustic_constraint(data["gender"], data["ageBand"])
    instruction = (
        f"{acoustic_constraint} 为中国先秦历史叙事游戏设计角色声音。人物：{speaker}。{direction}"
        f"社会处境：{data['socialPerformanceConstraint']}"
        "使用自然现代普通话承载古代称谓，句读清楚，表演克制且有人际对象感。"
        f"禁止：{'、'.join(FORBIDDEN_STYLE)}。不模仿任何现实演员、主播或名人。"
    )
    card = {
        "id": f"spk-{stable_hash(speaker, 12)}",
        "speaker": speaker,
        **data,
        "genderBasis": gender_basis,
        "historicalStatus": "documented" if data["ageConfidence"] == "high" else "inferred_and_labeled",
        "lineCount": len(texts),
        "referenceText": REFERENCE_TEXT,
        "voiceDesignInstruction": instruction,
        "hardAcousticConstraint": acoustic_constraint,
        "forbiddenStyle": FORBIDDEN_STYLE,
        "referenceFile": f"output/voice-production/references/{stable_hash(speaker, 16)}.wav",
    }
    anchor_names = sorted({
        spec["styleAnchor"]
        for (name, _), spec in FIRST_CHAPTER_PERFORMANCE.items()
        if name == speaker
    })
    if anchor_names:
        card["styleAnchors"] = [{
            "id": name,
            "referenceText": STYLE_ANCHOR_DIRECTIONS[name][0],
            "direction": STYLE_ANCHOR_DIRECTIONS[name][1],
            "referenceFile": f"output/voice-production/style-anchors/{stable_hash(speaker, 12)}/{name}.wav",
            "reviewStatus": "candidate_requires_identity_and_human_review",
            "approvedForCloning": False,
        } for name in anchor_names]
    return card


def infer_speech_act(speaker: str, text: str, section: str) -> str:
    curated = FIRST_CHAPTER_PERFORMANCE.get((speaker, text))
    if curated:
        return curated["speechAct"]
    if section == "defeat":
        return "concede_or_withdraw"
    if re.search(r"不可久留|快走|逃|避开|小心", text):
        return "flee_or_warning"
    if re.search(r"？|何以|为何|岂|可曾|怎", text):
        return "question_or_challenge"
    if re.search(r"臣愿|请|望|恳|相谏|不可", text):
        return "appeal_or_remonstrance"
    if re.search(r"传旨|速|快|退|守住|拿下|斩|杀|不得|务必", text):
        return "command"
    if re.search(r"报|知|见|闻|前方|已经|无踪", text):
        return "report"
    if re.search(r"必|誓|偿还|血债|昭雪", text):
        return "vow_or_accusation"
    return "statement"


def infer_scene(section: str, text: str, stage_title: str) -> str:
    if section == "victory":
        return "battle_resolution"
    if section == "defeat":
        return "failed_withdrawal"
    if re.search(r"王驾|围猎|军士|弓|箭|攻|守|退", text):
        return "field_or_battle"
    if re.search(r"臣|百官|传旨|入朝|寡人|大王", text):
        return "court_or_audience"
    if re.search(r"妻|乡民|入城|河边|宫女", text):
        return "civilian_incident"
    return f"historical_narrative:{stage_title}" if stage_title else "historical_narrative"


def infer_relationship(speaker: str, previous_speaker: str, card: dict, previous_card: dict | None) -> str:
    if not previous_speaker or previous_speaker in EXCLUDED_SPEAKERS:
        return "addresses_scene"
    if previous_speaker == speaker:
        return "continues_own_turn"
    role = card.get("role", "")
    previous_role = (previous_card or {}).get("role", "")
    if role == "ruler":
        return "ruler_to_subject"
    if previous_role == "ruler" and role in {"senior_minister", "senior_general", "scholar_minister", "minister_or_gentry"}:
        return "subject_to_ruler"
    if role in {"military", "senior_general"} or previous_role in {"military", "senior_general"}:
        return "military_counterpart"
    return "historical_counterpart"


def infer_delivery(speaker: str, text: str, section: str, speech_act: str = "statement") -> dict:
    curated = FIRST_CHAPTER_PERFORMANCE.get((speaker, text))
    if curated:
        return {
            **curated,
            "performanceRule": "保持固定声纹与年龄；沿剧情状态变化停顿、重音、能量和语速，禁止新闻播音、评书拖腔和持续高声。",
        }
    if re.search(r"……|\.\.\.$", text):
        emotion, intensity = "subdued_or_fading", 0.35
    elif re.search(r"死|亡|冤|哭|痛|悲|恨", text):
        emotion, intensity = "grief_or_grievance", 0.58
    elif re.search(r"！|速|快|杀|攻|退|守住|传令", text):
        emotion, intensity = "urgent_or_commanding", 0.68
    elif re.search(r"？|何以|为何|岂", text):
        emotion, intensity = "questioning_or_challenging", 0.52
    else:
        emotion, intensity = "restrained", 0.38
    if section == "defeat":
        emotion, intensity = "defeat_without_melodrama", min(intensity, 0.45)
    pace = 1.08 if speech_act in {"command", "flee_or_warning"} else 0.92 if emotion in {"subdued_or_fading", "grief_or_grievance", "defeat_without_melodrama"} else 1.0
    pause = 0.38
    pause += 0.18 if "；" in text else 0
    pause += 0.12 if re.search(r"……|\.\.\.$", text) else 0
    pause += 0.08 if "？" in text else 0
    pause += 0.14 if speech_act in {"appeal_or_remonstrance", "vow_or_accusation"} else 0
    pause = min(0.85, round(pause, 2))
    dominance = 0.72 if speech_act in {"command", "vow_or_accusation"} else 0.48
    return {
        "emotion": emotion,
        "intensity": intensity,
        "pace": pace,
        "pauseStrength": pause,
        "dominance": dominance,
        "emotionAfter": emotion,
        "subtext": "依据当前言语行为自然回应场内人物，而不是向观众朗读。",
        "pivotWords": [],
        "focusWords": [],
        "pausePlan": "依据标点和语义分组自然停连，避免每个短语等时。",
        "styleAnchor": "neutral",
        "longMemory": "无额外人工标注；保留关卡时间线作为上下文。",
        "performanceRule": "保持角色固定声纹；情绪作用于停顿、重音、能量和语速，不通过改变年龄、方言或夸张音色表现。",
    }


def context_instruction(card: dict, context: dict, delivery: dict) -> str:
    act_labels = {
        "alarmed_command": "受到威胁后警觉地质问并立刻下令，前后两段节奏不同",
        "cold_command": "用冷静的行政命令掩饰恐惧，分条清楚但不作播报",
        "scapegoating_sentence": "先冷静归责，再以短硬的宣判终止讨论",
        "authoritarian_threat": "压低能量，用君权确定性威胁，不咆哮",
        "public_ceremonial_command": "在公开场合维持从容，保留真实交流感",
        "reasoned_remonstrance": "先陈事实，再以克制但有压力的质问进谏",
        "cold_vow": "由申辩转为誓言，转折后更确定而非更响",
        "vengeance_accusation": "旧案控诉已经转为行动，明确对象和因果",
        "battle_strike": "出手时的短促确认，呼吸完整，不喊成口号",
        "sacrificial_remonstrance": "保留臣礼的冒死进谏，急迫但不哭腔",
        "vengeance_interrogation": "压住悲愤逼问，问句后停顿再宣告",
        "disciplined_battle_command": "在战场上清楚限定伤害范围并指定目标",
        "exhausted_withdrawal": "行动失败后的能量耗散，不使用衰弱老人颤音",
        "command": "下达命令，重点清楚，避免持续高声",
        "flee_or_warning": "在悲痛中急于离开或示警，语速可以加快但不要喊成口号",
        "question_or_challenge": "向明确对象追问，句尾有压力但不表演化",
        "appeal_or_remonstrance": "以论理进谏，克制中保留急迫",
        "report": "报告所见，信息层次清楚",
        "vow_or_accusation": "陈明誓言或控诉，以停顿和重音表现决绝",
        "concede_or_withdraw": "受挫后收束气息，不哭腔、不拖长",
        "statement": "自然陈述，对场内人物说话而非对观众播报",
    }
    scene_labels = {
        "court_or_audience": "朝堂或君臣议事",
        "field_or_battle": "军阵或野外冲突",
        "civilian_incident": "民间突发事件",
        "battle_resolution": "战斗结果已明",
        "failed_withdrawal": "行动受挫撤退",
    }
    relationship_labels = {
        "addresses_scene": "向在场众人发言",
        "continues_own_turn": "继续自己的上一轮发言",
        "ruler_to_subject": "君主对臣属",
        "subject_to_ruler": "臣属对君主",
        "military_counterpart": "军阵中的对手或同僚",
        "historical_counterpart": "对场内另一人物",
    }
    previous = "；".join(f"{turn['speaker']}：{turn['text'][:56]}" for turn in context["previousTurns"][-4:]) or "无"
    following = "；".join(f"{turn['speaker']}：{turn['text'][:56]}" for turn in context["nextTurns"][:2]) or "无"
    scene = scene_labels.get(context["scene"], "历史叙事场景")
    relationship = relationship_labels.get(context["relationship"], "对场内人物")
    pivot_words = "、".join(delivery.get("pivotWords") or []) or "按语义自然转折"
    focus_words = "、".join(delivery.get("focusWords") or []) or "按句义选择，不平均加重"
    return (
        f"{card['hardAcousticConstraint']} This constraint outranks emotion and acting style. "
        f"保持角色身份：{card['identityDirection']}"
        f"年龄目标：{card['estimatedAgeRange']}；社会处境：{card['socialPerformanceConstraint']}"
        f"长期剧情记忆：{delivery['longMemory']}"
        f"场景：{scene}；关系：{relationship}。前文：{previous}。此句之后：{following}。"
        f"此句功能：{act_labels.get(context['speechAct'], act_labels['statement'])}。"
        f"潜台词：{delivery['subtext']}"
        f"状态从{delivery['emotionBefore']}转为{delivery['emotionAfter']}；转折词：{pivot_words}；重音词：{focus_words}。"
        f"停连：{delivery['pausePlan']}情绪强度约{delivery['intensity']:.2f}，语速倍率约{delivery['pace']:.2f}。"
        "让呼吸、停顿长度、语速和能量随语义变化；禁止新闻播音式首尾、四字等时、平均重音和每句同一语气。"
        "情绪不能改变性别、年龄和固定声纹。"
    )


def extract_time_markers(turns: list[dict]) -> list[str]:
    markers: list[str] = []
    pattern = re.compile(r"(?:在位)?[一二三四五六七八九十百〇零两\d]{1,5}年|多年后|数年后|三年后|当年|次年|翌年|晚年|年老|尚幼")
    for turn in turns:
        for marker in pattern.findall(turn.get("text", "")):
            if marker not in markers:
                markers.append(marker)
    return markers


def main() -> None:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    story_stages = list(campaign.get("stages", []))
    story_stages.extend(json.loads(path.read_text(encoding="utf-8")) for path in EXTRA_STORY_PATHS if path.exists())
    occurrences: list[dict] = []
    speaker_texts: dict[str, list[str]] = defaultdict(list)
    speaker_contexts: dict[str, list[str]] = defaultdict(list)
    stage_timelines: dict[str, list[dict]] = defaultdict(list)
    excluded_counts: Counter[str] = Counter()
    all_story_speakers = sorted({
        str(entry.get("speaker") or "").strip()
        for stage in story_stages
        for section in SECTIONS
        for entry in normalized_entries((stage.get("story") or {}).get(section, []))
        if str(entry.get("speaker") or "").strip() not in EXCLUDED_SPEAKERS
    })
    runtime_occurrences = 0

    for stage in story_stages:
        story = stage.get("story") or {}
        stage_entries: list[dict] = []
        for section in SECTIONS:
            for source_index, entry in enumerate(normalized_entries(story.get(section, []))):
                speaker = str(entry.get("speaker") or "").strip()
                text = str(entry.get("text") or "").strip()
                if not text:
                    continue
                stage_entries.append({"speaker": speaker, "text": text})
                for chunk_index, chunk in enumerate(split_story_text(text)):
                    timeline = stage_timelines[str(stage.get("id") or "")]
                    timeline_index = len(timeline)
                    timeline.append({
                        "speaker": speaker or "旁白",
                        "text": chunk,
                        "section": section,
                    })
                    if speaker in EXCLUDED_SPEAKERS:
                        excluded_counts[speaker or "<empty_narration>"] += 1
                        continue
                    occurrence = {
                        "stageId": str(stage.get("id") or ""),
                        "chapter": str(story.get("chapter") or stage.get("chapter") or ""),
                        "stageTitle": str(story.get("title") or stage.get("title") or ""),
                        "section": section,
                        "sourceIndex": source_index,
                        "chunkIndex": chunk_index,
                        "timelineIndex": timeline_index,
                        "speaker": speaker,
                        "text": chunk,
                    }
                    occurrences.append(occurrence)
                    speaker_texts[speaker].append(chunk)
        runtime_calls = extract_runtime_speech(stage, STAGE_DIR, all_story_speakers)
        runtime_occurrences += len(runtime_calls)
        for runtime_call in runtime_calls:
            speaker = runtime_call["speaker"]
            text = runtime_call["text"]
            stage_entries.append({"speaker": speaker, "text": text})
            for chunk_index, chunk in enumerate(split_story_text(text)):
                timeline = stage_timelines[str(stage.get("id") or "")]
                timeline_index = len(timeline)
                timeline.append({
                    "speaker": speaker,
                    "text": chunk,
                    "section": "runtime",
                })
                occurrence = {
                    "stageId": str(stage.get("id") or ""),
                    "chapter": str((stage.get("story") or {}).get("chapter") or stage.get("chapter") or ""),
                    "stageTitle": str((stage.get("story") or {}).get("title") or stage.get("title") or ""),
                    "section": "runtime",
                    "sourceIndex": runtime_call["sourceIndex"],
                    "chunkIndex": chunk_index,
                    "timelineIndex": timeline_index,
                    "speaker": speaker,
                    "text": chunk,
                }
                occurrences.append(occurrence)
                speaker_texts[speaker].append(chunk)
        stage_context = "".join(item["speaker"] + item["text"] for item in stage_entries)
        for speaker in {item["speaker"] for item in stage_entries if item["speaker"] and item["speaker"] not in EXCLUDED_SPEAKERS}:
            speaker_contexts[speaker].append(stage_context)

    cards = {
        speaker: make_card(speaker, texts, "".join(speaker_contexts[speaker]))
        for speaker, texts in sorted(speaker_texts.items())
    }
    unique_entries: dict[str, dict] = {}
    occurrence_refs: list[dict] = []
    speaker_states: dict[tuple[str, str], str] = {}
    for occurrence in occurrences:
        key = f"{occurrence['speaker']}\0{occurrence['text']}"
        entry_id = f"line-{stable_hash(key)}"
        card = cards[occurrence["speaker"]]
        timeline = stage_timelines[occurrence["stageId"]]
        timeline_index = occurrence["timelineIndex"]
        previous_turns = timeline[max(0, timeline_index - 3):timeline_index]
        next_turns = timeline[timeline_index + 1:timeline_index + 3]
        previous_speaker = previous_turns[-1]["speaker"] if previous_turns else ""
        speech_act = infer_speech_act(occurrence["speaker"], occurrence["text"], occurrence["section"])
        delivery = infer_delivery(occurrence["speaker"], occurrence["text"], occurrence["section"], speech_act)
        state_key = (occurrence["stageId"], occurrence["speaker"])
        delivery["emotionBefore"] = speaker_states.get(state_key, "scene_baseline")
        speaker_states[state_key] = delivery["emotionAfter"]
        relationship = infer_relationship(
            occurrence["speaker"], previous_speaker, card,
            cards.get(previous_speaker),
        )
        context = {
            "id": f"ctx-{stable_hash('|'.join((occurrence['stageId'], occurrence['section'], str(timeline_index), occurrence['speaker'], occurrence['text'])), 12)}",
            "scene": infer_scene(occurrence["section"], occurrence["text"], occurrence["stageTitle"]),
            "speechAct": speech_act,
            "relationship": relationship,
            "previousTurns": previous_turns,
            "nextTurns": next_turns,
            "historicalSituation": {
                "chapter": occurrence["chapter"],
                "stageTitle": occurrence["stageTitle"],
                "timeMarkers": extract_time_markers(timeline[max(0, timeline_index - 5):timeline_index + 2]),
            },
            "speakerAtScene": {
                "ageBand": card["ageBand"],
                "estimatedAgeRange": card["estimatedAgeRange"],
                "ageConfidence": card["ageConfidence"],
                "identityReviewStatus": card["identityReviewStatus"],
                "socialPerformanceConstraint": card["socialPerformanceConstraint"],
            },
            "performanceState": {
                "emotionBefore": delivery["emotionBefore"],
                "emotionAfter": delivery["emotionAfter"],
                "subtext": delivery["subtext"],
                "pivotWords": delivery["pivotWords"],
                "focusWords": delivery["focusWords"],
                "pausePlan": delivery["pausePlan"],
                "styleAnchor": delivery["styleAnchor"],
                "longMemory": delivery["longMemory"],
            },
        }
        context["synthesisInstruction"] = context_instruction(card, context, delivery)
        occurrence_ref = {
            **{k: occurrence[k] for k in ("stageId", "chapter", "stageTitle", "section", "sourceIndex", "chunkIndex", "timelineIndex", "speaker", "text")},
            "entryId": entry_id,
            "contextId": context["id"],
        }
        occurrence_refs.append(occurrence_ref)
        if key in unique_entries:
            existing = unique_entries[key]
            if context["id"] not in existing["contextVariantIds"]:
                existing["contextVariantIds"].append(context["id"])
                existing["contextVariants"].append({
                    "contextId": context["id"],
                    "occurrence": {k: occurrence[k] for k in ("stageId", "chapter", "stageTitle", "section", "sourceIndex", "chunkIndex", "timelineIndex")},
                })
            continue
        unique_entries[key] = {
            "id": entry_id,
            "speaker": occurrence["speaker"],
            "text": occurrence["text"],
            "voiceCardId": card["id"],
            "file": f"audio/dialogue/full/{entry_id[5:7]}/{entry_id}.ogg",
            "firstOccurrence": {k: occurrence[k] for k in ("stageId", "chapter", "stageTitle", "section", "sourceIndex", "chunkIndex", "timelineIndex")},
            "delivery": delivery,
            "context": context,
            "contextVariantIds": [context["id"]],
            "contextVariants": [{
                "contextId": context["id"],
                "occurrence": {k: occurrence[k] for k in ("stageId", "chapter", "stageTitle", "section", "sourceIndex", "chunkIndex", "timelineIndex")},
            }],
        }

    plan = {
        "schemaVersion": 4,
        "source": [str(CAMPAIGN_PATH.relative_to(ROOT)).replace("\\", "/"), *(str(path.relative_to(ROOT)).replace("\\", "/") for path in EXTRA_STORY_PATHS), "web-game/scenario/stage/*.lua"],
        "modelPlan": {
            "voiceDesign": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "voiceClone": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            "method": "context-compiled-multi-candidate-with-gated-promotion",
        },
        "policy": {
            "excludedSpeakers": sorted(EXCLUDED_SPEAKERS),
            "narrationExcluded": True,
            "ageEvidenceOrder": ["explicit stage text", "historical override", "role-based conservative inference"],
            "unknownAgeRule": "Do not invent a numeric age; retain an explicit low-confidence inference label.",
            "contextVariantRule": "Runtime resolves an exact occurrence or context ID first, then falls back to speaker plus text while unpromoted variants remain under review.",
            "promotionRule": "Custom candidates cannot replace shipped audio until identity, text, prosody and gender review gates pass.",
            "historicalReviewRule": "Every speaker carries age evidence, confidence, social-position direction and review status; inferred cards remain explicitly pending.",
            "sceneAgeRule": "Each occurrence stores chapter time markers and the age target in force for that scene; long-lived characters must not rely on an unchanging numeric age.",
        },
        "summary": {
            "campaignStages": len(campaign.get("stages", [])),
            "experimentalStages": len(story_stages) - len(campaign.get("stages", [])),
            "characterSpeakers": len(cards),
            "characterLineOccurrences": len(occurrences),
            "uniqueCharacterAudio": len(unique_entries),
            "runtimeSpeechOccurrences": runtime_occurrences,
            "excludedOccurrences": sum(excluded_counts.values()),
            "excludedBySpeaker": dict(excluded_counts),
            "ageBandCounts": dict(sorted(Counter(card["ageBand"] for card in cards.values()).items())),
            "identityReviewCounts": dict(sorted(Counter(card["identityReviewStatus"] for card in cards.values()).items())),
            "genderConfidenceCounts": dict(sorted(Counter(card["genderConfidence"] for card in cards.values()).items())),
        },
        "entries": list(unique_entries.values()),
        "occurrences": occurrence_refs,
    }
    card_document = {
        "schemaVersion": 3,
        "referencePolicy": "One historically reviewed identity reference per speaker; contextual candidates remain separate until acoustic and human review.",
        "cards": list(cards.values()),
    }
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CARDS_PATH.write_text(json.dumps(card_document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
