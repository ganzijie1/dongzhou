#!/usr/bin/env python3
"""Build deterministic context-aware music cues for every Dongzhou stage and cutscene."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from runtime_speech import extract_runtime_speech


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"
PLAN_PATH = ROOT / "web-game" / "audio" / "context-music-plan.json"
STAGE_DIR = ROOT / "web-game" / "scenario" / "stage"
SECTIONS = ("intro", "victory", "defeat")


ERA_SPECS = {
    "western-zhou": {
        "label": "西周",
        "mode": "zhi-pentatonic",
        "palette": ["stone-chime", "restrained-bell", "frame-drum", "low-plucked-string"],
        "rule": "礼制秩序、克制钟磬与留白；不得把战国曾侯乙大编钟当作通用音色。",
    },
    "spring-autumn": {
        "label": "春秋",
        "mode": "yu-pentatonic",
        "palette": ["plucked-string", "wood-block", "war-drum", "breath-flute"],
        "rule": "会盟、征伐与礼崩并置，弦乐动机比钟磬更突出。",
    },
    "warring-states": {
        "label": "战国",
        "mode": "shang-pentatonic",
        "palette": ["low-drum", "plucked-string", "bronze-accent", "breath-flute"],
        "rule": "军阵密度、变法压力与兼并感增强，仍避免现代电影预告片式轰鸣。",
    },
}

MOOD_WORDS = {
    "grief": "死 亡 丧 哭 冤 葬 败 伤 悲 自刎 斩首 殉",
    "threat": "围 攻 战 兵 杀 追 伏 袭 危 急 破 敌 叛 乱 戎",
    "ritual": "朝 盟 礼 宗庙 祭 册命 王命 会盟 天子",
    "hope": "救 援 胜 归 保全 解围 复国 守住",
    "intrigue": "谋 计 欺 诡 间 谏 疑 密 诈",
}


def stable_seed(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def as_entries(value) -> list[dict]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    return []


def era_for(index: int) -> str:
    if index <= 4:
        return "western-zhou"
    if index <= 141:
        return "spring-autumn"
    return "warring-states"


def scene_for(text: str) -> str:
    rules = (
        ("siege", r"攻城|守城|城门|围城|城墙|城池|王城"),
        ("escort", r"护送|保护|救援|勤王|接应|保全"),
        ("breakout", r"突围|撤退|逃|脱困|追击|追赶"),
        ("ambush", r"伏击|埋伏|奇袭|夜袭|偷袭"),
        ("court", r"朝堂|入朝|册命|宫中|君臣|会盟"),
        ("ritual", r"祭|宗庙|礼|葬|盟誓"),
    )
    for label, pattern in rules:
        if re.search(pattern, text):
            return label
    return "field"


def mood_for(text: str, kind: str) -> tuple[str, dict[str, int]]:
    scores = {
        mood: sum(text.count(word) for word in words.split())
        for mood, words in MOOD_WORDS.items()
    }
    if kind == "victory":
        scores["hope"] += 4
    elif kind == "defeat":
        scores["grief"] += 4
    elif kind == "event":
        scores["threat"] += 2
    elif kind == "battle":
        scores["threat"] += 3
    mood = max(scores, key=lambda key: (scores[key], key))
    return mood, scores


def density_for(scene: str, mood: str, kind: str) -> float:
    density = 0.46
    if scene in {"siege", "ambush", "breakout"}:
        density += 0.16
    if mood == "threat":
        density += 0.12
    if mood == "grief":
        density -= 0.14
    if kind in {"intro", "defeat"}:
        density -= 0.08
    if kind == "event":
        density += 0.08
    return round(max(0.22, min(0.82, density)), 2)


def tempo_for(stage: dict, kind: str, scene: str, mood: str, seed: int) -> int:
    if kind == "battle":
        base = 82
    elif kind == "event":
        base = 92
    elif kind == "victory":
        base = 72
    elif kind == "defeat":
        base = 56
    else:
        base = 64
    if scene in {"siege", "ambush", "breakout"}:
        base += 6
    if mood == "threat":
        base += 6
    elif mood == "grief":
        base -= 6
    elif mood == "hope":
        base += 2
    return max(48, min(108, base + (seed % 5) - 2))


def duration_for(kind: str, entry_count: int) -> float:
    if kind == "battle":
        return 24.0
    if kind == "event":
        return 8.0
    if kind == "intro":
        return float(max(14, min(24, 12 + entry_count // 3)))
    return 12.0


def make_cue(stage: dict, kind: str, section: str, cue_suffix: str, entries: list[dict], event_id: str = "") -> dict:
    stage_id = str(stage["id"])
    index = int(stage.get("index") or 0)
    era = era_for(index)
    story_text = "".join(str(item.get("speaker") or "") + str(item.get("text") or "") for item in entries)
    context_text = " ".join([
        str(stage.get("chapter") or ""), str(stage.get("title") or ""),
        str(stage.get("battleTitle") or stage.get("story", {}).get("battle_title") or ""),
        str(stage.get("objective") or ""), story_text,
    ])
    scene = scene_for(context_text)
    mood, mood_scores = mood_for(context_text, kind)
    seed = stable_seed(f"{stage_id}|{kind}|{section}|{event_id}|{context_text}")
    cue_id = f"music-{stage_id}-{cue_suffix}"
    path = f"audio/context-music/{stage_id}/{cue_suffix}.ogg"
    speakers = Counter(str(item.get("speaker") or "旁白") for item in entries)
    return {
        "id": cue_id,
        "stageId": stage_id,
        "stageIndex": index,
        "chapter": str(stage.get("chapter") or ""),
        "stageTitle": str(stage.get("title") or ""),
        "battleTitle": str(stage.get("battleTitle") or stage.get("story", {}).get("battle_title") or ""),
        "kind": kind,
        "section": section,
        "eventId": event_id,
        "triggerText": str(entries[0].get("text") or "") if kind == "event" and len(entries) == 1 else "",
        "file": path,
        "loop": kind == "battle",
        "durationTarget": duration_for(kind, len(entries)),
        "era": era,
        "eraLabel": ERA_SPECS[era]["label"],
        "historicalRule": ERA_SPECS[era]["rule"],
        "scene": scene,
        "mood": mood,
        "moodScores": mood_scores,
        "mode": ERA_SPECS[era]["mode"],
        "instrumentPalette": ERA_SPECS[era]["palette"],
        "tempo": tempo_for(stage, kind, scene, mood, seed),
        "density": density_for(scene, mood, kind),
        "seed": seed,
        "entryCount": len(entries),
        "speakerCount": len(speakers),
        "dominantSpeakers": [name for name, _ in speakers.most_common(4)],
        "contextDigest": hashlib.sha256(context_text.encode("utf-8")).hexdigest(),
    }


def build_plan() -> dict:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    cues: list[dict] = []
    all_story_speakers = sorted({
        str(entry.get("speaker") or "").strip()
        for stage in campaign.get("stages", [])
        for section in (*SECTIONS, "events")
        for entry in as_entries((stage.get("story") or {}).get(section))
        if str(entry.get("speaker") or "").strip()
    })
    runtime_event_cues = 0
    for stage in campaign.get("stages", []):
        story = stage.get("story") or {}
        battle_entries = []
        for section in SECTIONS:
            battle_entries.extend(as_entries(story.get(section)))
        battle_entries.extend(as_entries(story.get("events")))
        cues.append(make_cue(stage, "battle", "battle", "battle", battle_entries))
        for section in SECTIONS:
            entries = as_entries(story.get(section))
            if entries:
                cues.append(make_cue(stage, section, section, f"story-{section}", entries))
        for source_index, event in enumerate(as_entries(story.get("events"))):
            event_id = str(event.get("id") or f"event-{source_index:03d}")
            safe_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", event_id).strip("-") or f"event-{source_index:03d}"
            cues.append(make_cue(stage, "event", "events", f"event-{safe_id}", [event], event_id))
        for runtime_call in extract_runtime_speech(stage, STAGE_DIR, all_story_speakers):
            event_id = runtime_call["eventId"]
            cues.append(make_cue(stage, "event", "runtime", f"event-{event_id}", [runtime_call], event_id))
            runtime_event_cues += 1

    counts = Counter(cue["kind"] for cue in cues)
    stages = {cue["stageId"] for cue in cues if cue["kind"] == "battle"}
    return {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": ["scenario/campaign.json", "scenario/stage/*.lua"],
        "generator": "deterministic-context-conditioned-symbolic-audio-v1",
        "policy": {
            "coverage": "one battle loop per stage, one cue per non-empty story section, one cue per campaign or Lua runtime speech event",
            "historicalClaim": "period-informed fictional scoring; no cue is represented as a reconstructed historical composition",
            "dialogueDuckingDb": -9,
            "transitionMs": 900,
        },
        "summary": {
            "campaignStages": len(stages),
            "totalCues": len(cues),
            "luaRuntimeEventCues": runtime_event_cues,
            "byKind": dict(sorted(counts.items())),
            "eras": dict(sorted(Counter(cue["era"] for cue in cues).items())),
        },
        "cues": cues,
    }


def main() -> None:
    plan = build_plan()
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
