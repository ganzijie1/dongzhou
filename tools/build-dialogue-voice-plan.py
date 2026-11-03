#!/usr/bin/env python3
"""Build deterministic character voice cards and a full dialogue production plan."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"
EXTRA_STORY_PATHS = (ROOT / "web-game" / "scenario" / "map-elites-chuisha.json",)
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
    return {
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


def infer_speech_act(text: str, section: str) -> str:
    if section == "defeat":
        return "concede_or_withdraw"
    if re.search(r"传旨|速|快|退|守住|拿下|斩|杀|不得|务必", text):
        return "command"
    if re.search(r"不可久留|快走|逃|避开|小心", text):
        return "flee_or_warning"
    if re.search(r"？|何以|为何|岂|可曾|怎", text):
        return "question_or_challenge"
    if re.search(r"臣愿|请|望|恳|相谏|不可", text):
        return "appeal_or_remonstrance"
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


def infer_delivery(text: str, section: str, speech_act: str = "statement") -> dict:
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
    pause = 0.68 if speech_act in {"appeal_or_remonstrance", "vow_or_accusation"} else 0.45
    dominance = 0.72 if speech_act in {"command", "vow_or_accusation"} else 0.48
    return {
        "emotion": emotion,
        "intensity": intensity,
        "pace": pace,
        "pauseStrength": pause,
        "dominance": dominance,
        "performanceRule": "保持角色固定声纹；情绪作用于停顿、重音和语速，不通过改变年龄、方言或夸张音色表现。",
    }


def context_instruction(card: dict, context: dict, delivery: dict) -> str:
    act_labels = {
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
    previous = "；".join(f"{turn['speaker']}：{turn['text'][:42]}" for turn in context["previousTurns"][-2:]) or "无"
    following = "；".join(f"{turn['speaker']}：{turn['text'][:42]}" for turn in context["nextTurns"][:1]) or "无"
    scene = scene_labels.get(context["scene"], "历史叙事场景")
    relationship = relationship_labels.get(context["relationship"], "对场内人物")
    return (
        f"{card['hardAcousticConstraint']} This constraint outranks emotion and acting style. "
        f"保持角色身份：{card['identityDirection']}"
        f"年龄目标：{card['estimatedAgeRange']}；社会处境：{card['socialPerformanceConstraint']}"
        f"场景：{scene}；关系：{relationship}。前文：{previous}。此句之后：{following}。"
        f"此句功能：{act_labels.get(context['speechAct'], act_labels['statement'])}。"
        f"情绪强度约{delivery['intensity']:.2f}，语速倍率约{delivery['pace']:.2f}，"
        "用自然停顿、重音和气息表达，不改变性别、年龄与固定声纹。"
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
        stage_context = "".join(item["speaker"] + item["text"] for item in stage_entries)
        for speaker in {item["speaker"] for item in stage_entries if item["speaker"] and item["speaker"] not in EXCLUDED_SPEAKERS}:
            speaker_contexts[speaker].append(stage_context)

    cards = {
        speaker: make_card(speaker, texts, "".join(speaker_contexts[speaker]))
        for speaker, texts in sorted(speaker_texts.items())
    }
    unique_entries: dict[str, dict] = {}
    occurrence_refs: list[dict] = []
    for occurrence in occurrences:
        key = f"{occurrence['speaker']}\0{occurrence['text']}"
        entry_id = f"line-{stable_hash(key)}"
        card = cards[occurrence["speaker"]]
        timeline = stage_timelines[occurrence["stageId"]]
        timeline_index = occurrence["timelineIndex"]
        previous_turns = timeline[max(0, timeline_index - 3):timeline_index]
        next_turns = timeline[timeline_index + 1:timeline_index + 3]
        previous_speaker = previous_turns[-1]["speaker"] if previous_turns else ""
        speech_act = infer_speech_act(occurrence["text"], occurrence["section"])
        delivery = infer_delivery(occurrence["text"], occurrence["section"], speech_act)
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
            continue
        unique_entries[key] = {
            "id": entry_id,
            "speaker": occurrence["speaker"],
            "text": occurrence["text"],
            "voiceCardId": card["id"],
            "file": f"audio/dialogue/full/{entry_id[5:7]}/{entry_id}.ogg",
            "firstOccurrence": {k: occurrence[k] for k in ("stageId", "chapter", "section", "sourceIndex", "chunkIndex")},
            "delivery": delivery,
            "context": context,
            "contextVariantIds": [context["id"]],
        }

    plan = {
        "schemaVersion": 3,
        "source": [str(CAMPAIGN_PATH.relative_to(ROOT)).replace("\\", "/"), *(str(path.relative_to(ROOT)).replace("\\", "/") for path in EXTRA_STORY_PATHS)],
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
            "contextVariantRule": "Runtime currently resolves speaker plus text; synthesize the first occurrence and retain all alternate contexts for review.",
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
        "schemaVersion": 2,
        "referencePolicy": "One historically reviewed identity reference per speaker; contextual candidates remain separate until acoustic and human review.",
        "cards": list(cards.values()),
    }
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CARDS_PATH.write_text(json.dumps(card_document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
