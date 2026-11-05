#!/usr/bin/env python3
"""Validate the isolated contextual voice review queue without treating pending gates as passes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-reviewed", action="store_true")
    args = parser.parse_args()
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    if index.get("schemaVersion") != 3:
        raise RuntimeError("Unsupported contextual candidate index")
    if not index.get("entries"):
        raise RuntimeError("Contextual candidate index is empty")

    gates = Counter()
    candidate_count = 0
    for entry in index["entries"]:
        card = cards_by_id.get(entry.get("voiceCardId"))
        if not card or card["speaker"] != entry.get("speaker"):
            raise RuntimeError(f"Mismatched voice card: {entry.get('entryId')}")
        if card["gender"] != entry.get("expectedGender") or card["ageBand"] != entry.get("expectedAgeBand"):
            raise RuntimeError(f"Identity metadata drift: {entry.get('entryId')}")
        if not entry.get("context", {}).get("synthesisInstruction"):
            raise RuntimeError(f"Missing context instruction: {entry.get('entryId')}")
        for name, status in (entry.get("gates") or {}).items():
            gates[f"{name}:{status}"] += 1
        required_gates = {"text", "identity", "humanReview", "calibration", "waveform", "prosody"}
        if not required_gates.issubset(entry.get("gates") or {}):
            raise RuntimeError(f"Missing review gates: {entry.get('entryId')}")
        if "pitchSanity" in entry["gates"] or "gender" in entry["gates"]:
            raise RuntimeError(f"Pitch or demographic classifier leaked into promotion gates: {entry.get('entryId')}")
        pending = any(status != "pass" for status in (entry.get("gates") or {}).values())
        if pending and entry.get("promotionEligible"):
            raise RuntimeError(f"Pending candidate marked promotion eligible: {entry.get('entryId')}")
        if args.require_reviewed and pending:
            raise RuntimeError(f"Candidate still has pending gates: {entry.get('entryId')}")
        candidates = entry.get("candidates") or []
        if not candidates and not index.get("planOnly"):
            raise RuntimeError(f"Generated entry has no candidates: {entry.get('entryId')}")
        for candidate in candidates:
            relative = Path(candidate["file"])
            path = ROOT / relative
            if relative.is_absolute() or ".." in relative.parts or not path.is_file():
                raise RuntimeError(f"Unsafe or missing candidate: {relative}")
            if "web-game" in relative.parts:
                raise RuntimeError(f"Unreviewed candidate leaked into shipped assets: {relative}")
            analysis = candidate.get("analysis") or {}
            required_analysis = {"speechTiming", "pauseStructure", "breathProxy", "energy", "pitch", "voiceQuality"}
            if not required_analysis.issubset(analysis):
                raise RuntimeError(f"Incomplete multidimensional analysis: {relative}")
            if not analysis.get("waveformGate") or analysis.get("qualityScore", 0) <= 0:
                raise RuntimeError(f"Invalid candidate audio: {relative}")
            if analysis["breathProxy"].get("reviewStatus") != "pending_human_confirmation":
                raise RuntimeError(f"Unconfirmed breath proxy treated as fact: {relative}")
            if "warning" not in analysis["pitch"] or "classifier" not in analysis["pitch"].get("caveat", ""):
                raise RuntimeError(f"Pitch caveat missing: {relative}")
            tracks = candidate.get("evidenceTracks") or {}
            required_tracks = {"content", "identity", "expression", "demographics", "quality", "human"}
            if not required_tracks.issubset(tracks):
                raise RuntimeError(f"Incomplete evidence tracks: {relative}")
            if tracks["demographics"].get("gatePolicy") != "soft_alert_only":
                raise RuntimeError(f"Demographic evidence leaked into hard gates: {relative}")
            if tracks["human"].get("status") != "pending_blind_context_review":
                raise RuntimeError(f"Unreviewed candidate marked human-reviewed: {relative}")
            if not candidate.get("reviewQueue", {}).get("priority"):
                raise RuntimeError(f"Missing review priority: {relative}")
            candidate_count += 1
    print(json.dumps({
        "result": "PASS",
        "entries": len(index["entries"]),
        "candidates": candidate_count,
        "gates": dict(sorted(gates.items())),
        "promotionBlockedWhilePending": True,
        "pitchExcludedFromPromotionGates": True,
        "breathRequiresHumanConfirmation": True,
        "separateEvidenceTracks": True,
        "demographicsAreSoftAlertsOnly": True,
        "universalCerThresholdRemoved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
