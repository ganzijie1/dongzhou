#!/usr/bin/env python3
"""Audit every character identity reference before it can drive cloning or conversion."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from voice_quality_metrics import analyze_audio


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
OUTPUT_PATH = ROOT / "output" / "voice-production" / "identity-reference-audit.json"


def load_evaluation_helpers():
    path = ROOT / "tools" / "evaluate-contextual-voice-candidates.py"
    spec = importlib.util.spec_from_file_location("dongzhou_voice_evaluator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load voice evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_demographic_model, module.classify_demographics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--speakers", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output", default="")
    parser.add_argument("--reference-attempt", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import soundfile as sf

    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    selected = [card for card in cards if not speakers or card["speaker"] in speakers]
    selected = selected[max(0, args.offset):]
    selected = selected[: args.limit or None]
    load_demographic_model, classify_demographics = load_evaluation_helpers()
    demographic_model = load_demographic_model(args.device)
    records = []
    for index, card in enumerate(selected, start=1):
        reference = (
            ROOT / "output" / "voice-production" / "reference-candidates" / card["id"] / f"attempt-{args.reference_attempt}.wav"
            if args.reference_attempt > 0 else ROOT / card["referenceFile"]
        )
        if not reference.is_file():
            records.append({
                "voiceCardId": card["id"], "speaker": card["speaker"], "file": card["referenceFile"],
                "hardReject": True, "hardRejectReasons": ["missing_reference"],
            })
            continue
        waveform, sample_rate = sf.read(reference, dtype="float32")
        delivery = {"pace": 1.0, "intensity": 0.4, "pauseStrength": 0.5}
        analysis = analyze_audio(waveform, sample_rate, card["referenceText"], delivery, card)
        demographics = classify_demographics(demographic_model, reference, card, args.device)
        probabilities = demographics["classProbabilities"]
        expected = card["gender"]
        opposite = "female" if expected == "male" else "male"
        f0 = analysis["pitch"]["medianF0Hz"]
        acoustic_conflict = (
            expected == "male" and (
                probabilities.get("female", 0) >= 0.97
                or (probabilities.get("female", 0) >= 0.90 and f0 >= 210.0)
            )
        ) or (
            expected == "female" and (
                probabilities.get("male", 0) >= 0.97
                or (probabilities.get("male", 0) >= 0.90 and 0 < f0 <= 165.0)
            )
        )
        predicted_age = float(demographics.get("predictedAgeYears") or 0.0)
        age_band = card["ageBand"]
        extreme_age_drift = (
            (age_band == "child" and predicted_age >= 30.0)
            or (age_band == "young_adult" and predicted_age >= 50.0)
            or (age_band == "mature" and 0 < predicted_age < 25.0)
            or (age_band == "late_middle" and 0 < predicted_age < 35.0)
            or (age_band == "elder" and 0 < predicted_age < 38.0)
        )
        reasons = []
        if not analysis["waveformGate"]:
            reasons.append("invalid_waveform")
        if analysis["broadcastCadence"]["hardReject"]:
            reasons.append("broadcast_cadence")
        if acoustic_conflict:
            reasons.append(f"high_confidence_{opposite}_voice")
        records.append({
            "voiceCardId": card["id"],
            "speaker": card["speaker"],
            "expectedGender": expected,
            "expectedAgeBand": card["ageBand"],
            "file": str(reference.relative_to(ROOT)).replace("\\", "/"),
            "analysis": analysis,
            "demographicEvidence": demographics,
            "hardReject": bool(reasons),
            "hardRejectReasons": reasons,
            "ageReviewRequired": "possible_age_mismatch" in demographics["softAlerts"],
            "priorityRetryReasons": ["extreme_age_drift"] if extreme_age_drift else [],
            "humanReview": "pending_identity_anchor_listening",
            "eligibleForConversion": False,
        })
        print(f"[{index}/{len(selected)}] {card['speaker']} {'REJECT' if reasons else 'triage-pass'}", flush=True)

    reason_counts = Counter(reason for record in records for reason in record.get("hardRejectReasons", []))
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "policy": {
            "automaticHardReject": "Broken audio, high-confidence acoustic sex conflict, or high-confidence broadcast cadence.",
            "demographics": "Age/gender inference remains research evidence; only agreement with an extreme F0 conflict triggers automatic rejection.",
            "promotion": "Triage-pass references still require identity-anchor listening before production conversion.",
        },
        "summary": {
            "cards": len(records),
            "present": sum("missing_reference" not in record.get("hardRejectReasons", []) for record in records),
            "hardRejected": sum(bool(record.get("hardReject")) for record in records),
            "triagePassed": sum(not record.get("hardReject") for record in records),
            "ageReviewRequired": sum(bool(record.get("ageReviewRequired")) for record in records),
            "priorityRetry": sum(bool(record.get("priorityRetryReasons")) for record in records),
            "hardRejectReasons": dict(sorted(reason_counts.items())),
        },
        "entries": records,
    }
    output_path = Path(args.output).resolve() if args.output else (
        OUTPUT_PATH.with_name(f"identity-reference-audit-attempt-{args.reference_attempt}.json")
        if args.reference_attempt > 0 else OUTPUT_PATH
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
