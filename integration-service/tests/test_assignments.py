from dongzhou_integration.assignments import (
    AssignmentUnavailable,
    assignment_readiness,
    manager_support,
    motivation_task_fit,
    personality_task_fit,
    quality_task_fit,
    select_assignment,
)


def schedule(*days):
    return {"code": 200, "data": {"plan_id": "plan", "generation_id": "gen", "schedules": list(days)}}


def test_selects_matching_duty_nearest_stage_range() -> None:
    result = select_assignment(
        hero_id="ZuoRu",
        npc_id="42",
        task_type="intelligence",
        stage_id="12b",
        npc_state={
            "emotion": {"dominant": {"emotion_type": "focused", "intensity": 0.7}},
            "affection": {"items": [
                {"target_id": "41", "dominant_affection_type": "respect", "max_value": 50, "affection_count": 2},
                {"target_id": "99", "dominant_affection_type": "hatred", "max_value": 100, "affection_count": 4},
            ]},
            "relationships": {"items": [
                {"target_id": "41", "relation_type": "organization", "relation_sub": "superior_subordinate", "is_bilateral": True},
                {"target_id": "99", "relation_type": "family", "is_bilateral": True},
            ]},
        },
        schedule_response=schedule(
            {"day": 1, "date": "0772-01-01", "start_level": 1, "end_level": 5, "events": [{"id": "old", "transaction_id": 9100105}]},
            {"day": 4, "date": "0772-01-04", "start_level": 10, "end_level": 20, "events": [{"id": "right", "transaction_id": 9100105, "name": "访求军情", "importance": 85}]},
        ),
        runtime={"state": "READY"},
        manager_npc_id="41",
    )
    assert result["eventId"] == "right"
    assert result["runtimeState"] == "READY"
    assert result["state"] == {
        "emotion": "focused",
        "intensity": 0.7,
        "affectionCount": 2,
        "relationshipCount": 2,
    }
    assert result["managerSupport"] == {
        "managerNpcId": "41",
        "affection": {"type": "respect", "value": 50.0, "count": 2},
        "relationships": [{
            "type": "organization",
            "subtype": "superior_subordinate",
            "title": "",
            "bilateral": True,
        }],
        "factor": 5.5,
    }
    assert result["readiness"] == {
        "score": 73,
        "band": "watch",
        "factors": {"runtime": 6.0, "duty": 6.3, "emotion": 0.0, "support": 5.5, "personality": 0.0, "motivation": 0.0, "quality": 0.0},
    }
    assert result["personality"] == {
        "available": False,
        "fit": {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []},
    }
    assert result["motivation"] == {
        "available": False,
        "fit": {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []},
    }
    assert result["quality"] == {
        "available": False,
        "fit": {"available": False, "score": None, "band": "unavailable", "factor": 0.0, "signals": []},
    }


def test_manager_support_uses_only_the_named_manager_and_can_be_negative() -> None:
    support = manager_support(
        {
            "affection": {"data": {"items": [
                {"target_id": "manager", "dominant_affection_type": "hatred", "max_value": 100, "affection_count": 3},
                {"target_id": "other", "dominant_affection_type": "love", "max_value": 100, "affection_count": 9},
            ]}},
            "relationships": {"data": {"items": [
                {"target_id": "manager", "relation_type": "organization", "relation_sub": "superior_subordinate", "is_active": True},
                {"target_id": "other", "relation_type": "family", "is_bilateral": True, "is_active": True},
                {"target_id": "manager", "relation_type": "family", "is_bilateral": True, "is_active": False},
            ]}},
        },
        "manager",
    )
    assert support == {
        "managerNpcId": "manager",
        "affection": {"type": "hatred", "value": 100.0, "count": 3},
        "relationships": [{
            "type": "organization",
            "subtype": "superior_subordinate",
            "title": "",
            "bilateral": False,
        }],
        "factor": -4.0,
    }


def test_readiness_uses_live_emotion_relationships_and_runtime() -> None:
    steady = assignment_readiness(
        runtime_state="READY", importance=95, emotion="peace", intensity=70,
        affection_count=2, relationship_count=3,
    )
    strained = assignment_readiness(
        runtime_state="RECOVERING", importance=40, emotion="fear", intensity=90,
        affection_count=0, relationship_count=0,
    )
    assert steady == {
        "score": 83,
        "band": "steady",
        "factors": {"runtime": 6.0, "duty": 8.1, "emotion": 6.8, "support": 7.0, "personality": 0.0, "motivation": 0.0, "quality": 0.0},
    }
    assert strained == {
        "score": 32,
        "band": "strained",
        "factors": {"runtime": -12.0, "duty": -1.8, "emotion": -9.0, "support": 0.0, "personality": 0.0, "motivation": 0.0, "quality": 0.0},
    }


def test_personality_fit_changes_with_duty_and_is_sealed_into_assignment() -> None:
    personality = {
        "available": True,
        "profileId": "profile-zuoru",
        "traits": {"stubborn": 79, "smooth": 48, "impulsive": 0},
        "dominantTraits": ["stubborn", "smooth"],
    }
    drill = personality_task_fit("drill", personality)
    diplomacy = personality_task_fit("diplomacy", personality)
    assert drill == {
        "available": True,
        "score": 56,
        "band": "steady",
        "factor": 1.2,
        "signals": [{"trait": "stubborn", "value": 79.0, "effect": 6.3}],
    }
    assert diplomacy["score"] == 48
    assert diplomacy["factor"] == -0.4
    assert diplomacy["signals"] == [
        {"trait": "stubborn", "value": 79.0, "effect": -9.5},
        {"trait": "smooth", "value": 48.0, "effect": 7.7},
    ]

    assignment = select_assignment(
        hero_id="ZuoRu",
        npc_id="42",
        task_type="drill",
        stage_id="01",
        npc_state={},
        schedule_response=schedule({
            "day": 1,
            "date": "0772-01-01",
            "start_level": 1,
            "end_level": 3,
            "events": [{"id": "drill", "transaction_id": 9100102, "importance": 50}],
        }),
        runtime={"state": "READY"},
        personality=personality,
    )
    assert assignment["personality"]["profileId"] == "profile-zuoru"
    assert assignment["personality"]["fit"] == drill
    assert assignment["readiness"]["factors"]["personality"] == 1.2


def test_motivation_willingness_only_changes_relevant_duty() -> None:
    motivation = {
        "available": True,
        "motives": [{"name": "情报核验", "score": 35.0}],
        "revision": 2,
        "threshold": 80.0,
    }
    intelligence = motivation_task_fit("intelligence", motivation)
    drill = motivation_task_fit("drill", motivation)
    assert intelligence == {
        "available": True,
        "score": 64,
        "band": "willing",
        "factor": 2.1,
        "signals": [{"name": "情报核验", "score": 35.0}],
    }
    assert drill == {
        "available": True,
        "score": 50,
        "band": "neutral",
        "factor": 0.0,
        "signals": [],
    }

    assignment = select_assignment(
        hero_id="ZuoRu",
        npc_id="42",
        task_type="intelligence",
        stage_id="01",
        npc_state={},
        schedule_response=schedule({
            "day": 1,
            "date": "0772-01-01",
            "start_level": 1,
            "end_level": 3,
            "events": [{"id": "intel", "transaction_id": 9100105, "importance": 50}],
        }),
        runtime={"state": "READY"},
        motivation=motivation,
    )
    assert assignment["motivation"]["fit"] == intelligence
    assert assignment["readiness"]["factors"]["motivation"] == 2.1


def test_stable_quality_fit_is_task_specific_and_sealed_into_assignment() -> None:
    quality = {
        "available": True,
        "profileId": "quality-zuoru",
        "qualities": {"responsibility": 85.0, "cruelty": 54.0},
        "dominantQualities": ["responsibility", "cruelty"],
        "valueOrder": ["responsibility", "cruelty"],
    }
    drill = quality_task_fit("drill", quality)
    diplomacy = quality_task_fit("diplomacy", quality)
    assert drill == {
        "available": True,
        "score": 55,
        "band": "steady",
        "factor": 1.0,
        "signals": [
            {"quality": "responsibility", "value": 85.0, "effect": 8.5},
            {"quality": "cruelty", "value": 54.0, "effect": -3.2},
        ],
    }
    assert diplomacy["score"] == 46
    assert diplomacy["factor"] == -0.8

    assignment = select_assignment(
        hero_id="ZuoRu",
        npc_id="42",
        task_type="drill",
        stage_id="01",
        npc_state={},
        schedule_response=schedule({
            "day": 1,
            "date": "0772-01-01",
            "start_level": 1,
            "end_level": 3,
            "events": [{"id": "drill-quality", "transaction_id": 9100102, "importance": 50}],
        }),
        runtime={"state": "READY"},
        quality=quality,
    )
    assert assignment["quality"]["profileId"] == "quality-zuoru"
    assert assignment["quality"]["fit"] == drill
    assert assignment["readiness"]["factors"]["quality"] == 1.0


def test_rejects_schedule_without_matching_duty() -> None:
    try:
        select_assignment(
            hero_id="ZuoRu",
            npc_id="42",
            task_type="diplomacy",
            stage_id="01",
            npc_state={},
            schedule_response=schedule({"day": 1, "events": []}),
            runtime=None,
        )
    except AssignmentUnavailable as error:
        assert "matching" in str(error)
    else:
        raise AssertionError("missing duty must be rejected")
