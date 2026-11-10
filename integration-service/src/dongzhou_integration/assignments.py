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
        "importance": max(0, min(100, _integer(event.get("importance")))),
        "state": {
            "emotion": str(dominant.get("emotion_type") or "calm"),
            "intensity": max(0.0, _number(dominant.get("intensity"))),
            "affectionCount": _count(npc_state.get("affection")),
            "relationshipCount": _count(npc_state.get("relationships")),
        },
    }
