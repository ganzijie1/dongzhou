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

# Each value is the maximum point contribution at a trait score of 100.
# Negative values model traits that make a particular duty harder to execute.
_TASK_PERSONALITY_WEIGHTS = {
    "supply": {
        "steady": 14.0,
        "cautious": 12.0,
        "smooth": 10.0,
        "protective": 6.0,
        "impulsive": -12.0,
        "stubborn": -8.0,
    },
    "drill": {
        "decisive": 14.0,
        "dominant": 12.0,
        "steady": 10.0,
        "calm": 8.0,
        "stubborn": 8.0,
        "impulsive": -10.0,
    },
    "patrol": {
        "cautious": 14.0,
        "calm": 12.0,
        "steady": 10.0,
        "sensitive": 8.0,
        "impulsive": -12.0,
    },
    "intelligence": {
        "cautious": 14.0,
        "introverted": 10.0,
        "sensitive": 8.0,
        "smooth": 6.0,
        "impulsive": -12.0,
        "dominant": -6.0,
    },
    "diplomacy": {
        "smooth": 16.0,
        "extroverted": 12.0,
        "calm": 8.0,
        "sensitive": 6.0,
        "stubborn": -12.0,
        "introverted": -8.0,
        "impulsive": -8.0,
    },
}

_TASK_MOTIVATION_KEYWORDS = {
    "supply": ("supply", "provision", "军粮", "粮", "补给", "转运", "仓", "辎重"),
    "drill": ("drill", "training", "整训", "训练", "军阵", "操练", "检阅"),
    "patrol": ("patrol", "guard", "巡察", "巡逻", "营垒", "守卫", "防守", "警戒"),
    "intelligence": ("intelligence", "情报", "核验", "侦察", "探查", "消息", "线索"),
    "diplomacy": ("diplomacy", "外交", "盟", "交涉", "游说", "诸侯", "使者"),
}

# Stable qualities are learned from authoritative duty outcomes and influence
# only the duties whose value contract actually depends on them.
_TASK_QUALITY_WEIGHTS = {
    "supply": {
        "responsibility": 12.0,
        "integrity": 10.0,
        "trustworthiness": 8.0,
        "greed": -10.0,
        "selfishness": -8.0,
        "cruelty": -4.0,
    },
    "drill": {
        "responsibility": 10.0,
        "courage": 12.0,
        "fairness": 6.0,
        "cruelty": -6.0,
    },
    "patrol": {
        "responsibility": 12.0,
        "courage": 10.0,
        "integrity": 8.0,
        "cruelty": -8.0,
    },
    "intelligence": {
        "trustworthiness": 14.0,
        "integrity": 10.0,
        "responsibility": 8.0,
        "hypocrisy": -12.0,
    },
    "diplomacy": {
        "fairness": 12.0,
        "tolerance": 12.0,
        "trustworthiness": 10.0,
        "humility": 6.0,
        "hypocrisy": -12.0,
        "meanness": -8.0,
        "cruelty": -8.0,
    },
}

_POSITIVE_AFFECTIONS = {
    "love", "adoration", "kinship", "friendship", "dependence", "respect", "appreciation"
}
_NEGATIVE_AFFECTIONS = {"annoyance": -4.0, "hatred": -6.0}
_RELATIONSHIP_WEIGHTS = {"family": 3.0, "legal": 2.0, "organization": 2.0, "social": 1.0}


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


def manager_support(npc_state: dict[str, Any], manager_npc_id: str) -> dict[str, Any]:
    manager_id = str(manager_npc_id)
    affection_items = _payload(npc_state.get("affection")).get("items")
    relationship_items = _payload(npc_state.get("relationships")).get("items")
    affection_items = affection_items if isinstance(affection_items, list) else []
    relationship_items = relationship_items if isinstance(relationship_items, list) else []

    affection = next(
        (
            item for item in affection_items
            if isinstance(item, dict) and str(item.get("target_id") or "") == manager_id
        ),
        None,
    )
    affection_factor = 0.0
    affection_snapshot = None
    if isinstance(affection, dict):
        affection_type = str(affection.get("dominant_affection_type") or "").casefold()
        value = max(0.0, min(100.0, _number(affection.get("max_value"))))
        if affection_type in _POSITIVE_AFFECTIONS:
            affection_factor = value * 0.06
        elif affection_type in _NEGATIVE_AFFECTIONS:
            affection_factor = value * _NEGATIVE_AFFECTIONS[affection_type] / 100.0
        affection_snapshot = {
            "type": affection_type,
            "value": round(value, 1),
            "count": max(0, _integer(affection.get("affection_count"))),
        }

    relationships = []
    relationship_factor = 0.0
    for item in relationship_items:
        if (
            not isinstance(item, dict)
            or str(item.get("target_id") or "") != manager_id
            or item.get("is_active") is False
        ):
            continue
        relation_type = str(item.get("relation_type") or "").casefold()
        relationship_factor += _RELATIONSHIP_WEIGHTS.get(relation_type, 0.0)
        if item.get("is_bilateral") is True:
            relationship_factor += 0.5
        relationships.append(
            {
                "type": relation_type,
                "subtype": str(item.get("relation_sub") or ""),
                "title": str(item.get("title") or ""),
                "bilateral": item.get("is_bilateral") is True,
            }
        )
    factor = max(-8.0, min(10.0, affection_factor + min(4.0, relationship_factor)))
    return {
        "managerNpcId": manager_id,
        "affection": affection_snapshot,
        "relationships": relationships,
        "factor": round(factor, 1),
    }


def collaboration_support(
    primary_state: dict[str, Any],
    support_state: dict[str, Any],
    primary_npc_id: str,
    support_npc_id: str,
) -> dict[str, Any]:
    """Build a bounded, symmetric collaboration score from AINPC relationships."""
    primary_to_support = manager_support(primary_state, support_npc_id)
    support_to_primary = manager_support(support_state, primary_npc_id)
    factor = round(
        max(
            -8.0,
            min(
                10.0,
                (
                    float(primary_to_support["factor"])
                    + float(support_to_primary["factor"])
                )
                / 2.0,
            ),
        ),
        1,
    )
    score = round(max(10.0, min(100.0, 50.0 + factor * 5.0)))
    band = (
        "exceptional"
        if factor >= 7
        else "aligned"
        if factor >= 3
        else "neutral"
        if factor > -2
        else "strained"
    )
    return {
        "primaryNpcId": str(primary_npc_id),
        "supportNpcId": str(support_npc_id),
        "score": score,
        "band": band,
        "factor": factor,
        "primaryToSupport": primary_to_support,
        "supportToPrimary": support_to_primary,
    }


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
    support_factor: float | None = None,
    personality_factor: float = 0.0,
    motivation_factor: float = 0.0,
    quality_factor: float = 0.0,
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
    support_factor = (
        min(10.0, max(0, affection_count) * 2.0 + max(0, relationship_count))
        if support_factor is None
        else max(-8.0, min(10.0, support_factor))
    )
    bounded_personality_factor = max(-8.0, min(8.0, personality_factor))
    bounded_motivation_factor = max(-8.0, min(6.0, motivation_factor))
    bounded_quality_factor = max(-6.0, min(6.0, quality_factor))
    score = max(
        25,
        min(
            95,
            round(
                55
                + runtime_factor
                + duty_factor
                + emotion_factor
                + support_factor
                + bounded_personality_factor
                + bounded_motivation_factor
                + bounded_quality_factor
            ),
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
            "personality": round(bounded_personality_factor, 1),
            "motivation": round(bounded_motivation_factor, 1),
            "quality": round(bounded_quality_factor, 1),
        },
    }


def personality_task_fit(
    task_type: str, personality: dict[str, Any] | None
) -> dict[str, Any]:
    if not personality or personality.get("available") is not True:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}
    traits = personality.get("traits")
    weights = _TASK_PERSONALITY_WEIGHTS.get(task_type)
    if not isinstance(traits, dict) or not weights:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}

    signals = []
    adjustment = 0.0
    for trait, weight in weights.items():
        value = max(0.0, min(100.0, _number(traits.get(trait))))
        contribution = weight * value / 100.0
        adjustment += contribution
        if value > 0:
            signals.append(
                {
                    "trait": trait,
                    "value": round(value, 1),
                    "effect": round(contribution, 1),
                }
            )
    signals.sort(key=lambda item: abs(item["effect"]), reverse=True)
    score = max(25, min(90, round(50 + adjustment)))
    factor = max(-8.0, min(8.0, round((score - 50) * 0.2, 1)))
    band = "strong" if score >= 65 else "steady" if score >= 50 else "strained"
    return {
        "available": True,
        "score": score,
        "band": band,
        "factor": factor,
        "signals": signals[:4],
    }


def motivation_task_fit(
    task_type: str, motivation: dict[str, Any] | None
) -> dict[str, Any]:
    if not motivation or motivation.get("available") is not True:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}
    motives = motivation.get("motives")
    keywords = _TASK_MOTIVATION_KEYWORDS.get(task_type)
    if not isinstance(motives, list) or not keywords:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}

    signals = []
    for motive in motives:
        if not isinstance(motive, dict):
            continue
        name = str(motive.get("name") or "").strip()
        folded = name.casefold()
        if name and any(keyword.casefold() in folded for keyword in keywords):
            signals.append({"name": name, "score": round(_number(motive.get("score")), 1)})
    signals.sort(key=lambda item: abs(item["score"]), reverse=True)
    strongest = max((-100.0, min(100.0, signals[0]["score"]))) if signals else 0.0
    score = max(25, min(90, round(50 + strongest * 0.4)))
    factor = max(-8.0, min(6.0, round((score - 50) * 0.15, 1)))
    band = "strong" if score >= 70 else "willing" if score >= 60 else "neutral" if score >= 45 else "reluctant"
    return {
        "available": True,
        "score": score,
        "band": band,
        "factor": factor,
        "signals": signals[:4],
    }


def quality_task_fit(task_type: str, quality: dict[str, Any] | None) -> dict[str, Any]:
    if not quality or quality.get("available") is not True:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}
    qualities = quality.get("qualities")
    weights = _TASK_QUALITY_WEIGHTS.get(task_type)
    if not isinstance(qualities, dict) or not weights:
        return {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []}

    signals = []
    adjustment = 0.0
    for name, weight in weights.items():
        value = max(0.0, min(100.0, _number(qualities.get(name))))
        contribution = weight * value / 100.0
        adjustment += contribution
        if value > 0:
            signals.append({"quality": name, "value": round(value, 1), "effect": round(contribution, 1)})
    signals.sort(key=lambda item: abs(item["effect"]), reverse=True)
    score = max(25, min(90, round(50 + adjustment)))
    factor = max(-6.0, min(6.0, round((score - 50) * 0.2, 1)))
    band = "strong" if score >= 65 else "steady" if score >= 50 else "strained"
    return {
        "available": True,
        "score": score,
        "band": band,
        "factor": factor,
        "signals": signals[:4],
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
    personality: dict[str, Any] | None = None,
    motivation: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    manager_npc_id: str | None = None,
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
    fit = personality_task_fit(task_type, personality)
    willingness = motivation_task_fit(task_type, motivation)
    quality_fit = quality_task_fit(task_type, quality)
    support = manager_support(npc_state, manager_npc_id) if manager_npc_id else {
        "managerNpcId": None, "affection": None, "relationships": [], "factor": 0.0
    }
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
        "personality": {
            **(personality or {"available": False}),
            "fit": fit,
        },
        "motivation": {
            **(motivation or {"available": False}),
            "fit": willingness,
        },
        "quality": {
            **(quality or {"available": False}),
            "fit": quality_fit,
        },
        "managerSupport": support,
        "readiness": assignment_readiness(
            runtime_state=runtime_state,
            importance=importance,
            emotion=state["emotion"],
            intensity=state["intensity"],
            affection_count=state["affectionCount"],
            relationship_count=state["relationshipCount"],
            support_factor=support["factor"],
            personality_factor=fit["factor"],
            motivation_factor=willingness["factor"],
            quality_factor=quality_fit["factor"],
        ),
    }
