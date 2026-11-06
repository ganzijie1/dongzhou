#!/usr/bin/env python3
"""Classify anchored dialogue renders into automatic retry and manual-review queues."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "output" / "voice-production" / "anchored-contextual-clone-index.json"
DEFAULT_REPORT = ROOT / "output" / "voice-production" / "anchored-contextual-anomalies.json"
DEFAULT_RETRY_IDS = ROOT / "output" / "voice-production" / "anchored-contextual-retry-ids.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--retry-ids", type=Path, default=DEFAULT_RETRY_IDS)
    return parser.parse_args()


def classify(record: dict) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    soft: list[str] = []
    candidates = record.get("candidates") or []
    if len(candidates) != 1:
        return ["candidate_count_not_one"], soft
    candidate = candidates[0]
    relative = Path(candidate.get("file") or "")
    source = (ROOT / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or ROOT.resolve() not in source.parents or not source.is_file():
        hard.append("missing_or_unsafe_audio")

    analysis = candidate.get("analysis") or {}
    if analysis.get("waveformGate") is not True:
        hard.append("waveform_gate_failed")
    cadence = analysis.get("broadcastCadence") or {}
    if cadence.get("hardReject") is True:
        hard.append("broadcast_cadence_hard_reject")
    elif float(cadence.get("riskScore") or 0) >= 0.65:
        soft.append("broadcast_cadence_review")
    if (analysis.get("pitch") or {}).get("warning"):
        soft.append("pitch_soft_alert")

    text = candidate.get("textValidation") or {}
    if not text:
        hard.append("missing_asr_evidence")
    elif not text.get("normalizedHypothesis"):
        hard.append("empty_asr_hypothesis")
    missing_terms = (text.get("criticalTerms") or {}).get("missingTerms") or []
    if missing_terms:
        hard.append("critical_term_mismatch")
    elif text and not text.get("exactMatch"):
        soft.append("asr_not_exact")

    if not candidate.get("speakerEmbedding"):
        hard.append("missing_ecapa_evidence")
    if not candidate.get("wavlmSpeakerEmbedding"):
        hard.append("missing_wavlm_evidence")
    retrieval = (candidate.get("identityEvidence") or {}).get("identityReferenceRetrieval") or {}
    if retrieval.get("status") == "identity_drift_hard_review":
        soft.append("identity_reference_not_ranked_first")
    dual = ((candidate.get("evidenceTracks") or {}).get("identity") or {}).get("dualModelComparison") or {}
    if dual.get("status") == "uncalibrated_direction_conflict":
        soft.append("speaker_model_direction_conflict")

    emotion = candidate.get("emotionEvidence") or {}
    if not emotion:
        hard.append("missing_emotion_evidence")
    elif emotion.get("status") == "manual_context_review":
        soft.append("coarse_emotion_conflict")

    demographics = candidate.get("demographicEvidence") or {}
    if not demographics:
        hard.append("missing_demographic_evidence")
    else:
        expected = record.get("expectedGender")
        opposite = "female" if expected == "male" else "male"
        probabilities = demographics.get("classProbabilities") or {}
        if float(probabilities.get(opposite) or 0) >= 0.85:
            hard.append("high_confidence_gender_mismatch")
        for alert in demographics.get("softAlerts") or []:
            soft.append(str(alert))

    return sorted(set(hard)), sorted(set(soft))


def main() -> None:
    args = parse_args()
    index = json.loads(args.index.resolve().read_text(encoding="utf-8"))
    hard_records = []
    soft_records = []
    hard_counts: Counter[str] = Counter()
    soft_counts: Counter[str] = Counter()
    for record in index.get("entries") or []:
        hard, soft = classify(record)
        if hard:
            hard_counts.update(hard)
            hard_records.append({"entryId": record["entryId"], "speaker": record["speaker"], "reasons": hard})
        if soft:
            soft_counts.update(soft)
            soft_records.append({"entryId": record["entryId"], "speaker": record["speaker"], "reasons": soft})

    report = {
        "schemaVersion": 1,
        "entries": len(index.get("entries") or []),
        "automaticRetryEntries": len(hard_records),
        "manualReviewEntries": len(soft_records),
        "automaticRetryReasonCounts": dict(sorted(hard_counts.items())),
        "manualReviewReasonCounts": dict(sorted(soft_counts.items())),
        "automaticRetry": hard_records,
        "manualReview": soft_records,
        "policy": {
            "automaticRetry": "Broken audio, missing evidence, confirmed critical-term loss, empty ASR, broadcast hard rejection, or high-confidence opposite-gender evidence.",
            "manualReview": "ASR variants, age, pitch, coarse emotion, and uncalibrated identity metrics remain listening evidence only.",
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.retry_ids.write_text("\n".join(item["entryId"] for item in hard_records) + ("\n" if hard_records else ""), encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "entries", "automaticRetryEntries", "manualReviewEntries",
        "automaticRetryReasonCounts", "manualReviewReasonCounts",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
