from __future__ import annotations

import re
from typing import Any


TASK_TRANSACTION_IDS = {
    "supply": 9100103,
    "drill": 9100102,
    "patrol": 9100104,
    "intelligence": 9100105,
    "diplomacy": 9100106,
}

_POSITIVE_EMOTIONS = {
    "calm": (6.0, 0.0),
    "peace": (4.0, 0.04),
    "joy": (3.0, 0.05),
    "curiosity": (2.0, 0.03),
}
_DISRUPTIVE_EMOTIONS = {"anger", "fear", "sadness", "irritation", "shame"}


class AssignmentUnavailable(ValueError):
    pass


def _stage_number(stage_id: str) -> int:
    match = re.search(r"\d+", stage_id)
    return max(1, int(match.group())) if match else 1


def _payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    data = value.get("data")
    return data if isinstance(data, dict) else value


def _count(value: Any) -> int:
    payload = _payload(value)
    total = payload.get("total")
    if isinstance(total, int) and not isinstance(total, bool) and total >= 0:
        return total
    items = payload.get("items")
    return len(items) if isinstance(items, list) else 0


def _integer(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return fallback


def _number(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, bool):
        return fallback
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback


def assignment_readiness(
    *,
    runtime_state: str,
    importance: int,
    emotion: str,
    intensity: float,
    affection_count: int,
    relationship_count: int,
) -> dict[str, Any]:
    normalized_emotion = emotion.casefold().strip() or "calm"
    bounded_intensity = max(0.0, min(100.0, intensity))
    runtime_factor = 6.0 if runtime_state == "READY" else -12.0
    duty_factor = (max(0, min(100, importance)) - 50) * 0.18
    if normalized_emotion in _POSITIVE_EMOTIONS:
        base, coefficient = _POSITIVE_EMOTIONS[normalized_emotion]
        emotion_factor = base + bounded_intensity * coefficient
    elif normalized_emotion in _DISRUPTIVE_EMOTIONS:
        emotion_factor = -bounded_intensity * 0.1
    elif normalized_emotion == "surprise":
        emotion_factor = -bounded_intensity * 0.03
    else:
        emotion_factor = 0.0
    support_factor = min(
        10.0,
        max(0, affection_count) * 2.0 + max(0, relationship_count),
    )
    score = max(
        25,
        min(
            95,
            round(55 + runtime_factor + duty_factor + emotion_factor + support_factor),
        ),
    )
    band = "steady" if score >= 75 else "watch" if score >= 55 else "strained"
    return {
        "score": score,
        "band": band,
        "factors": {
            "runtime": round(runtime_factor, 1),
            "duty": round(duty_factor, 1),
            "emotion": round(emotion_factor, 1),
            "support": round(support_factor, 1),
        },
    }


def select_assignment(
    *,
    hero_id: str,
    npc_id: str,
    task_type: str,
    stage_id: str,
    npc_state: dict[str, Any],
    schedule_response: dict[str, Any],
    runtime: dict[str, Any] | None,
) -> dict[str, Any]:
    transaction_id = TASK_TRANSACTION_IDS.get(task_type)
    if transaction_id is None:
        raise AssignmentUnavailable("unknown task type")

    plan = _payload(schedule_response)
    plan_id = str(plan.get("plan_id") or "").strip()
    schedules = plan.get("schedules")
    if not plan_id or not isinstance(schedules, list):
        raise AssignmentUnavailable("AINPC returned no usable schedule plan")

    stage_number = _stage_number(stage_id)
    candidates: list[tuple[tuple[int, int, int], dict[str, Any], dict[str, Any]]] = []
    for schedule_index, day in enumerate(schedules):
        if not isinstance(day, dict):
            continue
        start = _integer(day.get("start_level") or day.get("day"), schedule_index + 1)
        end = _integer(day.get("end_level"), start)
        distance = 0 if start <= stage_number <= end else min(abs(stage_number - start), abs(stage_number - end))
        for event_index, event in enumerate(day.get("events") or []):
            if not isinstance(event, dict) or event.get("transaction_id") != transaction_id:
                continue
            candidates.append(((distance, _integer(day.get("day"), schedule_index + 1), event_index), day, event))
    if not candidates:
        raise AssignmentUnavailable("AINPC schedule has no duty matching this task")

    _, day, event = min(candidates, key=lambda item: item[0])
    event_id = str(event.get("id") or event.get("todo_id") or "").strip()
    if not event_id:
        raise AssignmentUnavailable("AINPC schedule duty has no stable event ID")

    emotion = _payload(npc_state.get("emotion"))
    dominant = emotion.get("dominant") if isinstance(emotion.get("dominant"), dict) else {}
    runtime_state = str((runtime or {}).get("state") or "UNKNOWN").upper()
    importance = max(0, min(100, _integer(event.get("importance"))))
    state = {
        "emotion": str(dominant.get("emotion_type") or "calm"),
        "intensity": max(0.0, min(100.0, _number(dominant.get("intensity")))),
        "affectionCount": _count(npc_state.get("affection")),
        "relationshipCount": _count(npc_state.get("relationships")),
    }
    return {
        "heroId": hero_id,
        "npcId": npc_id,
        "runtimeState": runtime_state,
        "planId": plan_id,
        "generationId": str(plan.get("generation_id") or ""),
        "eventId": event_id,
        "transactionId": transaction_id,
        "name": str(event.get("name") or task_type),
        "type": str(event.get("type") or ""),
        "date": str(day.get("date") or ""),
        "day": _integer(day.get("day")),
        "stageRange": {
            "start": _integer(day.get("start_level")),
            "end": _integer(day.get("end_level")),
        },
        "timeSlot": str(event.get("time_slot") or ""),
        "importance": importance,
        "state": state,
        "readiness": assignment_readiness(
            runtime_state=runtime_state,
            importance=importance,
            emotion=state["emotion"],
            intensity=state["intensity"],
            affection_count=state["affectionCount"],
            relationship_count=state["relationshipCount"],
        ),
    }
