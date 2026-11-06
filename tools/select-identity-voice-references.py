#!/usr/bin/env python3
"""Select provisional identity references from audited attempts, preserving originals."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
AUDIT_ROOT = ROOT / "output" / "voice-production"
REPORT_PATH = AUDIT_ROOT / "identity-reference-selection.json"
BACKUP_ROOT = AUDIT_ROOT / "reference-backups" / "pre-automatic-selection"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audits", default="", help="Comma-separated audit JSON paths; default discovers base and attempts.")
    parser.add_argument("--apply", action="store_true", help="Copy selected attempts into formal reference paths.")
    return parser.parse_args()


def candidate_score(record: dict) -> float:
    demographics = record.get("demographicEvidence") or {}
    probabilities = demographics.get("classProbabilities") or {}
    expected = record.get("expectedGender")
    gender_score = float(probabilities.get(expected, 0.0))
    target_age = {
        "child": 14.0, "young_adult": 25.0, "adult": 38.0,
        "mature": 50.0, "late_middle": 60.0, "elder": 68.0,
    }.get(record.get("expectedAgeBand"), 42.0)
    predicted_age = float(demographics.get("predictedAgeYears") or target_age)
    age_score = math.exp(-abs(predicted_age - target_age) / 28.0)
    analysis = record.get("analysis") or {}
    cadence = analysis.get("broadcastCadence") or {}
    quality_score = float(analysis.get("prosodyScore") or 0.0)
    cadence_score = 1.0 - float(cadence.get("riskScore") or 0.0)
    pitch_score = 0.55 if (analysis.get("pitch") or {}).get("warning") else 1.0
    retry_penalty = 0.12 if record.get("priorityRetryReasons") else 0.0
    return (
        0.48 * gender_score
        + 0.17 * age_score
        + 0.15 * quality_score
        + 0.12 * cadence_score
        + 0.08 * pitch_score
        - retry_penalty
    )


def main() -> None:
    args = parse_args()
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    if args.audits:
        audit_paths = [Path(item.strip()).resolve() for item in args.audits.split(",") if item.strip()]
    else:
        audit_paths = sorted(AUDIT_ROOT.glob("identity-reference-audit*.json"))
    if not audit_paths:
        raise RuntimeError("No identity reference audits found")

    candidates: dict[str, list[dict]] = {}
    for audit_path in audit_paths:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        for record in audit.get("entries", []):
            if record.get("hardReject") or not record.get("analysis"):
                continue
            item = dict(record)
            item["audit"] = str(audit_path.relative_to(ROOT)).replace("\\", "/")
            item["selectionScore"] = round(candidate_score(record), 6)
            candidates.setdefault(record["voiceCardId"], []).append(item)

    selections = []
    applied = 0
    unresolved = []
    for card in cards:
        options = sorted(candidates.get(card["id"], []), key=lambda item: item["selectionScore"], reverse=True)
        if not options:
            unresolved.append({"voiceCardId": card["id"], "speaker": card["speaker"], "reason": "no_triage_pass_candidate"})
            continue
        selected = options[0]
        source = ROOT / selected["file"]
        target = ROOT / card["referenceFile"]
        changed = source.resolve() != target.resolve()
        if args.apply and changed:
            backup = BACKUP_ROOT / target.name
            backup.parent.mkdir(parents=True, exist_ok=True)
            if target.is_file() and not backup.exists():
                shutil.copy2(target, backup)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            applied += 1
        selections.append({
            "voiceCardId": card["id"],
            "speaker": card["speaker"],
            "selectedFile": selected["file"],
            "formalReferenceFile": card["referenceFile"],
            "selectionScore": selected["selectionScore"],
            "sourceAudit": selected["audit"],
            "changed": changed,
            "applied": bool(args.apply and changed),
            "selectionStatus": "automatic_provisional_human_listening_pending",
            "alternativeCount": max(0, len(options) - 1),
        })

    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "applied": args.apply,
        "policy": {
            "selection": "Only triage-pass audited references are eligible; sex evidence dominates, with age, prosody, cadence and pitch as secondary evidence.",
            "humanStatus": "Automatic selection never claims human approval.",
            "backup": str(BACKUP_ROOT.relative_to(ROOT)).replace("\\", "/"),
        },
        "summary": {"cards": len(cards), "selected": len(selections), "unresolved": len(unresolved), "appliedChanges": applied},
        "selections": selections,
        "unresolved": unresolved,
    }
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
