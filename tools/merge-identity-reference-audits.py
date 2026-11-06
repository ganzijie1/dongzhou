#!/usr/bin/env python3
"""Merge disjoint identity-reference audit shards without changing verdicts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payloads = [json.loads(Path(name).read_text(encoding="utf-8")) for name in args.inputs]
    entries = [entry for payload in payloads for entry in payload.get("entries", [])]
    card_ids = [entry.get("voiceCardId") for entry in entries]
    if len(card_ids) != len(set(card_ids)):
        raise RuntimeError("Audit shards overlap")
    reason_counts = Counter(reason for entry in entries for reason in entry.get("hardRejectReasons", []))
    result = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "policy": payloads[0].get("policy", {}) if payloads else {},
        "summary": {
            "cards": len(entries),
            "present": sum("missing_reference" not in entry.get("hardRejectReasons", []) for entry in entries),
            "hardRejected": sum(bool(entry.get("hardReject")) for entry in entries),
            "triagePassed": sum(not entry.get("hardReject") for entry in entries),
            "ageReviewRequired": sum(bool(entry.get("ageReviewRequired")) for entry in entries),
            "priorityRetry": sum(bool(entry.get("priorityRetryReasons")) for entry in entries),
            "hardRejectReasons": dict(sorted(reason_counts.items())),
        },
        "entries": entries,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
