#!/usr/bin/env python3
"""Refresh card-dependent demographic expectations without rerunning acoustic inference."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
DEFAULT_AUDIT = ROOT / "output" / "voice-production" / "identity-reference-audit.json"
AGE_RANGES = {
    "child": (0.0, 17.0), "young_adult": (18.0, 38.0), "adult": (25.0, 52.0),
    "mature": (35.0, 62.0), "late_middle": (48.0, 78.0), "elder": (58.0, 100.0),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT))
    return parser.parse_args()


def extreme_age_drift(age_band: str, age: float) -> bool:
    return (
        (age_band == "child" and age >= 30.0)
        or (age_band == "young_adult" and age >= 50.0)
        or (age_band == "mature" and 0 < age < 25.0)
        or (age_band == "late_middle" and 0 < age < 35.0)
        or (age_band == "elder" and 0 < age < 38.0)
    )


def main() -> None:
    args = parse_args()
    path = Path(args.audit).resolve()
    audit = json.loads(path.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    for record in audit.get("entries", []):
        card = cards_by_id[record["voiceCardId"]]
        record["expectedGender"] = card["gender"]
        record["expectedAgeBand"] = card["ageBand"]
        demographics = record.get("demographicEvidence") or {}
        age = float(demographics.get("predictedAgeYears") or 0.0)
        top = demographics.get("topClass")
        probabilities = demographics.get("classProbabilities") or {}
        f0 = float(((record.get("analysis") or {}).get("pitch") or {}).get("medianF0Hz") or 0.0)
        opposite = "female" if card["gender"] == "male" else "male"
        opposite_probability = float(probabilities.get(opposite, 0.0))
        acoustic_conflict = (
            opposite_probability >= 0.97
            or (card["gender"] == "male" and opposite_probability >= 0.90 and f0 >= 210.0)
            or (card["gender"] == "female" and opposite_probability >= 0.90 and 0 < f0 <= 165.0)
        )
        alerts = []
        if top and top != card["gender"]:
            alerts.append("possible_gender_mismatch")
        age_range = AGE_RANGES.get(card["ageBand"])
        if age_range and not age_range[0] <= age <= age_range[1]:
            alerts.append("possible_age_mismatch")
        demographics["expectedGender"] = card["gender"]
        demographics["expectedAgeBand"] = card["ageBand"]
        demographics["softAlerts"] = alerts
        demographics["status"] = "soft_alert" if alerts else "no_soft_alert"
        record["ageReviewRequired"] = "possible_age_mismatch" in alerts
        record["priorityRetryReasons"] = ["extreme_age_drift"] if extreme_age_drift(card["ageBand"], age) else []
        reasons = [reason for reason in record.get("hardRejectReasons", []) if not reason.startswith("high_confidence_")]
        if acoustic_conflict:
            reasons.append(f"high_confidence_{opposite}_voice")
        record["hardRejectReasons"] = reasons
        record["hardReject"] = bool(reasons)
    entries = audit.get("entries", [])
    reasons = Counter(reason for record in entries for reason in record.get("hardRejectReasons", []))
    audit["generatedAt"] = datetime.now(timezone.utc).isoformat()
    audit["refreshedFromExistingAcousticEvidence"] = True
    audit["summary"] = {
        "cards": len(entries),
        "present": sum("missing_reference" not in record.get("hardRejectReasons", []) for record in entries),
        "hardRejected": sum(bool(record.get("hardReject")) for record in entries),
        "triagePassed": sum(not record.get("hardReject") for record in entries),
        "ageReviewRequired": sum(bool(record.get("ageReviewRequired")) for record in entries),
        "priorityRetry": sum(bool(record.get("priorityRetryReasons")) for record in entries),
        "hardRejectReasons": dict(sorted(reasons.items())),
    }
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
