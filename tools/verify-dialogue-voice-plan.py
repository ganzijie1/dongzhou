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

    if plan.get("schemaVersion") != 2:
        raise RuntimeError("Voice plan schema must be 2")
    if len(entry_ids) != len(entries):
        raise RuntimeError("Duplicate voice-plan entry IDs")
    if any(entry["speaker"] in EXCLUDED for entry in entries):
        raise RuntimeError("Narration or system text leaked into character voice plan")
    if any(item["entryId"] not in entry_ids for item in occurrences):
        raise RuntimeError("Occurrence references an unknown voice-plan entry")
    if any(entry["voiceCardId"] not in cards_by_id for entry in entries):
        raise RuntimeError("Voice-plan entry references an unknown character card")
    if len({card["speaker"] for card in cards}) != len(cards):
        raise RuntimeError("Duplicate character voice cards")
    required_card_fields = {"ageBand", "ageBasis", "ageConfidence", "role", "voiceDesignInstruction", "forbiddenStyle"}
    for card in cards:
        missing = required_card_fields - card.keys()
        if missing:
            raise RuntimeError(f"Card {card['speaker']} is missing fields: {sorted(missing)}")
        if not {"戏曲腔", "评书腔", "短视频腔"}.issubset(set(card["forbiddenStyle"])):
            raise RuntimeError(f"Card {card['speaker']} lacks anti-caricature constraints")
    for speaker in ("杜伯", "左儒", "伯阳父", "尹吉甫"):
        card = next(item for item in cards if item["speaker"] == speaker)
        if card["ageBand"] != "elder":
            raise RuntimeError(f"First-chapter senior minister is not elder-directed: {speaker}")

    expected_occurrences = plan["summary"]["characterLineOccurrences"]
    if expected_occurrences != len(occurrences):
        raise RuntimeError("Character occurrence count mismatch")
    stage_counts = Counter(item["stageId"] for item in occurrences)
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
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
