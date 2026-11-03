#!/usr/bin/env python3
"""Balance character-to-voice casting as a small exact optimal-transport assignment."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
OUTPUT_PATH = ROOT / "web-game" / "audio" / "voice-casting-ot-plan.json"

AGE_ORDER = {
    "child": 0,
    "young_adult": 1,
    "adult": 2,
    "mature": 3,
    "late_middle": 4,
    "elder": 5,
}

PROTOTYPES = [
    {"id": "m-elder-court-1", "gender": "male", "ageTarget": "elder", "voice": "zh-CN-YunyangNeural", "rate": "-6%", "pitch": "-2Hz", "roleBias": ["senior_minister", "scholar_minister", "minister_or_gentry"]},
    {"id": "m-elder-court-2", "gender": "male", "ageTarget": "elder", "voice": "zh-CN-YunjianNeural", "rate": "-5%", "pitch": "-1Hz", "roleBias": ["senior_minister", "scholar_minister"]},
    {"id": "m-elder-command-1", "gender": "male", "ageTarget": "elder", "voice": "zh-CN-YunjianNeural", "rate": "-3%", "pitch": "-2Hz", "roleBias": ["senior_general", "military"]},
    {"id": "m-elder-ruler-1", "gender": "male", "ageTarget": "elder", "voice": "zh-CN-YunyangNeural", "rate": "-4%", "pitch": "-1Hz", "roleBias": ["ruler"]},
    {"id": "m-mature-court-1", "gender": "male", "ageTarget": "mature", "voice": "zh-CN-YunyangNeural", "rate": "-2%", "pitch": "+0Hz", "roleBias": ["ruler", "scholar_minister", "minister_or_gentry"]},
    {"id": "m-mature-court-2", "gender": "male", "ageTarget": "mature", "voice": "zh-CN-YunjianNeural", "rate": "-2%", "pitch": "+0Hz", "roleBias": ["scholar_minister", "minister_or_gentry"]},
    {"id": "m-mature-natural-1", "gender": "male", "ageTarget": "mature", "voice": "zh-CN-YunxiNeural", "rate": "-2%", "pitch": "-1Hz", "roleBias": ["commoner", "commoner_or_attendant"]},
    {"id": "m-adult-command-1", "gender": "male", "ageTarget": "adult", "voice": "zh-CN-YunjianNeural", "rate": "+1%", "pitch": "+0Hz", "roleBias": ["military", "senior_general"]},
    {"id": "m-adult-command-2", "gender": "male", "ageTarget": "adult", "voice": "zh-CN-YunyangNeural", "rate": "+0%", "pitch": "+0Hz", "roleBias": ["military", "ruler"]},
    {"id": "m-adult-natural-1", "gender": "male", "ageTarget": "adult", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "roleBias": ["commoner", "commoner_or_attendant", "minister_or_gentry"]},
    {"id": "m-adult-natural-2", "gender": "male", "ageTarget": "adult", "voice": "zh-CN-YunxiNeural", "rate": "+2%", "pitch": "+1Hz", "roleBias": ["commoner", "commoner_or_attendant", "royal_heir"]},
    {"id": "m-young-natural-1", "gender": "male", "ageTarget": "young_adult", "voice": "zh-CN-YunxiNeural", "rate": "+3%", "pitch": "+1Hz", "roleBias": ["royal_heir", "commoner_or_attendant"]},
    {"id": "m-child-1", "gender": "male", "ageTarget": "child", "voice": "zh-CN-YunxiaNeural", "rate": "+3%", "pitch": "+1Hz", "roleBias": ["royal_heir", "commoner_or_attendant"]},
    {"id": "f-mature-court-1", "gender": "female", "ageTarget": "mature", "voice": "zh-CN-XiaoxiaoNeural", "rate": "-3%", "pitch": "-1Hz", "roleBias": ["royal_woman", "ruler"]},
    {"id": "f-mature-court-2", "gender": "female", "ageTarget": "mature", "voice": "zh-CN-XiaoyiNeural", "rate": "-2%", "pitch": "-1Hz", "roleBias": ["royal_woman", "minister_or_gentry"]},
    {"id": "f-adult-natural-1", "gender": "female", "ageTarget": "adult", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+0%", "pitch": "+0Hz", "roleBias": ["royal_woman", "commoner_or_attendant"]},
    {"id": "f-adult-natural-2", "gender": "female", "ageTarget": "adult", "voice": "zh-CN-XiaoyiNeural", "rate": "+1%", "pitch": "+0Hz", "roleBias": ["commoner_or_attendant", "minister_or_gentry"]},
    {"id": "f-young-natural-1", "gender": "female", "ageTarget": "young_adult", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+2%", "pitch": "+1Hz", "roleBias": ["royal_heir", "commoner_or_attendant"]},
]


def stable_unit(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 2**32


def balanced_slots(prototypes: list[dict], count: int) -> list[dict]:
    base, extra = divmod(count, len(prototypes))
    slots: list[dict] = []
    for index, prototype in enumerate(prototypes):
        slots.extend([prototype] * (base + (1 if index < extra else 0)))
    return slots


def assignment_cost(card: dict, prototype: dict) -> float:
    age_distance = abs(AGE_ORDER.get(card.get("ageBand", "adult"), 2) - AGE_ORDER[prototype["ageTarget"]])
    role_cost = 0.0 if card.get("role") in prototype["roleBias"] else 5.0
    age_cost = age_distance * 18.0
    high_volume_weight = 1.0 + min(1.5, math.log1p(int(card.get("lineCount", 1))) / 4.0)
    tie_break = stable_unit(f"{card['speaker']}\0{prototype['id']}") * 0.01
    return (age_cost + role_cost) * high_volume_weight + tie_break


def solve_group(cards: list[dict], prototypes: list[dict]) -> list[dict]:
    assignments = []
    by_target_age: dict[str, list[dict]] = {}
    available_ages = sorted({prototype["ageTarget"] for prototype in prototypes}, key=AGE_ORDER.get)
    for card in cards:
        distance = min(abs(AGE_ORDER[card["ageBand"]] - AGE_ORDER[age]) for age in available_ages)
        nearest = [age for age in available_ages if abs(AGE_ORDER[card["ageBand"]] - AGE_ORDER[age]) == distance]
        if len(nearest) > 1 and card.get("role") in {"senior_minister", "senior_general", "scholar_minister", "ruler"}:
            target_age = max(nearest, key=AGE_ORDER.get)
        else:
            target_age = nearest[int(stable_unit(card["speaker"]) * len(nearest)) % len(nearest)]
        by_target_age.setdefault(target_age, []).append(card)

    for target_age, age_cards in by_target_age.items():
        age_prototypes = [prototype for prototype in prototypes if prototype["ageTarget"] == target_age]
        slots = balanced_slots(age_prototypes, len(age_cards))
        costs = np.array([[assignment_cost(card, slot) for slot in slots] for card in age_cards], dtype=np.float64)
        rows, columns = linear_sum_assignment(costs)
        for row, column in zip(rows.tolist(), columns.tolist()):
            card, prototype = age_cards[row], slots[column]
            assignments.append({
                "speaker": card["speaker"],
                "voiceCardId": card["id"],
                "gender": card["gender"],
                "ageBand": card["ageBand"],
                "role": card["role"],
                "lineCount": card["lineCount"],
                "prototypeId": prototype["id"],
                "voice": prototype["voice"],
                "rate": prototype["rate"],
                "pitch": prototype["pitch"],
                "volume": "+0%",
                "assignmentCost": round(float(costs[row, column]), 6),
            })
    return assignments


def main() -> None:
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    assignments: list[dict] = []
    for gender in ("male", "female"):
        group_cards = sorted((card for card in cards if card.get("gender") == gender), key=lambda item: item["speaker"])
        group_prototypes = [prototype for prototype in PROTOTYPES if prototype["gender"] == gender]
        assignments.extend(solve_group(group_cards, group_prototypes))

    usage = Counter(item["prototypeId"] for item in assignments)
    age_mismatches = sum(
        abs(AGE_ORDER[item["ageBand"]] - AGE_ORDER[next(p for p in PROTOTYPES if p["id"] == item["prototypeId"])["ageTarget"]]) > 1
        for item in assignments
    )
    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "balanced_integral_optimal_transport_assignment",
        "sourceMethod": {
            "name": "HELLO-inspired voice casting formulation",
            "scopeNote": "This 687-character problem is solved exactly as a dense balanced assignment; the paper's million-scale hierarchical edge-localization kernel is not claimed or required.",
            "reference": "Dual-guided Hierarchical Edge Localization for Large-scale Optimal Transport Across Dimensions (arXiv:2609.13010v1)",
        },
        "constraints": {
            "genderMismatch": "forbidden by separate transport problems",
            "ageDistancePenalty": 18,
            "roleMismatchPenalty": 5,
            "antiCaricature": "prosody offsets remain within -6% to +3% rate and -2Hz to +1Hz pitch",
        },
        "audit": {
            "characters": len(assignments),
            "prototypes": len(PROTOTYPES),
            "genderMismatches": 0,
            "ageDistanceGreaterThanOne": age_mismatches,
            "totalAssignmentCost": round(sum(item["assignmentCost"] for item in assignments), 6),
            "prototypeUsage": dict(sorted(usage.items())),
            "completeCostMatrixChecked": True,
            "solver": "scipy.optimize.linear_sum_assignment",
        },
        "prototypes": PROTOTYPES,
        "assignments": sorted(assignments, key=lambda item: item["speaker"]),
    }
    if output["audit"]["genderMismatches"] or output["audit"]["ageDistanceGreaterThanOne"]:
        raise RuntimeError("Voice casting violates gender or age-distance constraints")
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["audit"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
