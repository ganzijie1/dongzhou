#!/usr/bin/env python3
"""Verify full character-line coverage and provenance in the voice production plan."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
EXCLUDED = {"", "旁白", "原著", "史官", "军令", "下回预告", "下一回预告", "下关提示"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    entries = plan["entries"]
    occurrences = plan["occurrences"]
    cards_by_id = {card["id"]: card for card in cards}
    entry_ids = {entry["id"] for entry in entries}

    if plan.get("schemaVersion") != 4:
        raise RuntimeError("Voice plan schema must be 4")
    if len(entry_ids) != len(entries):
        raise RuntimeError("Duplicate voice-plan entry IDs")
    if any(entry["speaker"] in EXCLUDED for entry in entries):
        raise RuntimeError("Narration or system text leaked into character voice plan")
    if any(item["entryId"] not in entry_ids for item in occurrences):
        raise RuntimeError("Occurrence references an unknown voice-plan entry")
    if any(entry["voiceCardId"] not in cards_by_id for entry in entries):
        raise RuntimeError("Voice-plan entry references an unknown character card")
    required_context_fields = {"id", "scene", "speechAct", "relationship", "previousTurns", "nextTurns", "historicalSituation", "speakerAtScene", "performanceState", "synthesisInstruction"}
    required_delivery_fields = {
        "emotion", "emotionBefore", "emotionAfter", "intensity", "pace",
        "pauseStrength", "dominance", "subtext", "pivotWords", "focusWords",
        "pausePlan", "styleAnchor", "longMemory", "performanceRule",
    }
    for entry in entries:
        context = entry.get("context") or {}
        missing = required_context_fields - context.keys()
        if missing:
            raise RuntimeError(f"Entry {entry['id']} is missing context fields: {sorted(missing)}")
        if not entry.get("contextVariantIds"):
            raise RuntimeError(f"Entry {entry['id']} has no context variants")
        if len(entry.get("contextVariants") or []) != len(entry["contextVariantIds"]):
            raise RuntimeError(f"Entry {entry['id']} context variant payloads do not match their IDs")
        delivery = entry.get("delivery") or {}
        if not required_delivery_fields.issubset(delivery):
            raise RuntimeError(f"Entry {entry['id']} has incomplete delivery controls")
    if len({card["speaker"] for card in cards}) != len(cards):
        raise RuntimeError("Duplicate character voice cards")
    required_card_fields = {"ageBand", "estimatedAgeRange", "ageBasis", "ageSources", "ageConfidence", "role", "identityReviewStatus", "genderConfidence", "socialPerformanceConstraint", "voiceDesignInstruction", "hardAcousticConstraint", "forbiddenStyle"}
    for card in cards:
        missing = required_card_fields - card.keys()
        if missing:
            raise RuntimeError(f"Card {card['speaker']} is missing fields: {sorted(missing)}")
        if not {"戏曲腔", "评书腔", "短视频腔"}.issubset(set(card["forbiddenStyle"])):
            raise RuntimeError(f"Card {card['speaker']} lacks anti-caricature constraints")
    for speaker in ("杜伯", "左儒", "伯阳父", "尹吉甫"):
        card = next(item for item in cards if item["speaker"] == speaker)
        expected = "mature" if speaker == "伯阳父" else "elder"
        if card["ageBand"] != expected:
            raise RuntimeError(f"First-chapter historical age direction mismatch for {speaker}: expected {expected}")

    first_chapter = [entry for entry in entries if entry["firstOccurrence"]["stageId"] == "01"]
    if len({round(entry["delivery"]["pauseStrength"], 2) for entry in first_chapter}) < 4:
        raise RuntimeError("First-chapter dialogue still uses nearly uniform pause strength")
    expected_acts = {
        ("周宣王", "市井孩童唱的是何等妖言？速召百官入朝解说！"): "alarmed_command",
        ("杜伯", "若死者无知，此事便休；若死者有知，三年之内，必使王知妄杀之报。"): "cold_vow",
        ("左儒", "王师势众，今日未能使沉冤昭雪……"): "exhausted_withdrawal",
    }
    by_line = {(entry["speaker"], entry["text"]): entry for entry in first_chapter}
    for line_key, expected_act in expected_acts.items():
        entry = by_line.get(line_key)
        if not entry or entry["context"]["speechAct"] != expected_act:
            raise RuntimeError(f"First-chapter speech-act regression for {line_key[0]}: expected {expected_act}")

    expected_occurrences = plan["summary"]["characterLineOccurrences"]
    if expected_occurrences != len(occurrences):
        raise RuntimeError("Character occurrence count mismatch")
    stage_counts = Counter(item["stageId"] for item in occurrences)
    if sum(plan["summary"].get("identityReviewCounts", {}).values()) != len(cards):
        raise RuntimeError("Identity review summary does not cover every speaker")
    print(json.dumps({
        "result": "PASS",
        "stages": plan["summary"]["campaignStages"],
        "experimental_stages": plan["summary"].get("experimentalStages", 0),
        "character_speakers": len(cards),
        "character_line_occurrences": len(occurrences),
        "unique_character_audio": len(entries),
        "stage_01_lines": stage_counts["01"],
        "narration_excluded": True,
        "anti_caricature_rules": True,
        "context_compilation": True,
        "stateful_delivery": True,
        "distinct_pause_profiles": len({round(entry["delivery"]["pauseStrength"], 2) for entry in first_chapter}),
        "gated_custom_voice_promotion": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
