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
        "ageBasis": "剧情发生在周宣王在位第三十九年，出生年不详；按长期在位阶段作晚年君主处理。",
        "ageConfidence": "medium",
        "identityDirection": "晚年君主，中低音，久居上位而不靠咆哮维持威势，疲惫与疑惧只在停顿中显露。",
    },
    "伯阳父": {
        "gender": "male",
        "ageBand": "elder",
        "role": "scholar_minister",
        "ageBasis": "周室资深史官形象；确切年龄无可靠记载，按剧情中的阅历与职掌保守推断。",
        "ageConfidence": "low",
        "identityDirection": "年长史官，声音清瘦而稳定，解释灾异时审慎，不作神秘腔。",
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
        "ageBasis": "剧情仅能确认其为已婚成年乡民，无法进一步确定年龄。",
        "ageConfidence": "high",
        "identityDirection": "成年平民，朴素自然，遭逢惨变时惊惧急切但不舞台化。",
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
    direction = data["identityDirection"]
    instruction = (
        f"为中国先秦历史叙事游戏设计角色声音。人物：{speaker}。{direction}"
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
        "forbiddenStyle": FORBIDDEN_STYLE,
        "referenceFile": f"output/voice-production/references/{stable_hash(speaker, 16)}.wav",
    }


def infer_delivery(text: str, section: str) -> dict:
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
    return {
        "emotion": emotion,
        "intensity": intensity,
        "performanceRule": "保持角色固定声纹；情绪作用于停顿、重音和语速，不通过改变年龄、方言或夸张音色表现。",
    }


def main() -> None:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    story_stages = list(campaign.get("stages", []))
    story_stages.extend(json.loads(path.read_text(encoding="utf-8")) for path in EXTRA_STORY_PATHS if path.exists())
    occurrences: list[dict] = []
    speaker_texts: dict[str, list[str]] = defaultdict(list)
    speaker_contexts: dict[str, list[str]] = defaultdict(list)
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
                if speaker in EXCLUDED_SPEAKERS:
                    excluded_counts[speaker or "<empty_narration>"] += 1
                    continue
                for chunk_index, chunk in enumerate(split_story_text(text)):
                    occurrence = {
                        "stageId": str(stage.get("id") or ""),
                        "chapter": str(story.get("chapter") or stage.get("chapter") or ""),
                        "section": section,
                        "sourceIndex": source_index,
                        "chunkIndex": chunk_index,
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
        occurrence_refs.append({**occurrence, "entryId": entry_id})
        if key in unique_entries:
            continue
        card = cards[occurrence["speaker"]]
        unique_entries[key] = {
            "id": entry_id,
            "speaker": occurrence["speaker"],
            "text": occurrence["text"],
            "voiceCardId": card["id"],
            "file": f"audio/dialogue/full/{entry_id[5:7]}/{entry_id}.ogg",
            "firstOccurrence": {k: occurrence[k] for k in ("stageId", "chapter", "section", "sourceIndex", "chunkIndex")},
            "delivery": infer_delivery(occurrence["text"], occurrence["section"]),
        }

    plan = {
        "schemaVersion": 2,
        "source": [str(CAMPAIGN_PATH.relative_to(ROOT)).replace("\\", "/"), *(str(path.relative_to(ROOT)).replace("\\", "/") for path in EXTRA_STORY_PATHS)],
        "modelPlan": {
            "voiceDesign": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "voiceClone": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            "method": "design-reference-then-clone",
        },
        "policy": {
            "excludedSpeakers": sorted(EXCLUDED_SPEAKERS),
            "narrationExcluded": True,
            "ageEvidenceOrder": ["explicit stage text", "historical override", "role-based conservative inference"],
            "unknownAgeRule": "Do not invent a numeric age; retain an explicit low-confidence inference label.",
        },
        "summary": {
            "campaignStages": len(campaign.get("stages", [])),
            "experimentalStages": len(story_stages) - len(campaign.get("stages", [])),
            "characterSpeakers": len(cards),
            "characterLineOccurrences": len(occurrences),
            "uniqueCharacterAudio": len(unique_entries),
            "excludedOccurrences": sum(excluded_counts.values()),
            "excludedBySpeaker": dict(excluded_counts),
        },
        "entries": list(unique_entries.values()),
        "occurrences": occurrence_refs,
    }
    card_document = {
        "schemaVersion": 1,
        "referencePolicy": "One designed reference per named speaker, then reusable Base-model cloning for identity consistency.",
        "cards": list(cards.values()),
    }
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CARDS_PATH.write_text(json.dumps(card_document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
