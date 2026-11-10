from dongzhou_integration.assignments import AssignmentUnavailable, assignment_readiness, select_assignment


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
            "affection": {"items": [1, 2]},
            "relationships": {"total": 3},
        },
        schedule_response=schedule(
            {"day": 1, "date": "0772-01-01", "start_level": 1, "end_level": 5, "events": [{"id": "old", "transaction_id": 9100105}]},
            {"day": 4, "date": "0772-01-04", "start_level": 10, "end_level": 20, "events": [{"id": "right", "transaction_id": 9100105, "name": "访求军情", "importance": 85}]},
        ),
        runtime={"state": "READY"},
    )
    assert result["eventId"] == "right"
    assert result["runtimeState"] == "READY"
    assert result["state"] == {
        "emotion": "focused",
        "intensity": 0.7,
        "affectionCount": 2,
        "relationshipCount": 3,
    }
    assert result["readiness"] == {
        "score": 74,
        "band": "watch",
        "factors": {"runtime": 6.0, "duty": 6.3, "emotion": 0.0, "support": 7.0},
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
        "factors": {"runtime": 6.0, "duty": 8.1, "emotion": 6.8, "support": 7.0},
    }
    assert strained == {
        "score": 32,
        "band": "strained",
        "factors": {"runtime": -12.0, "duty": -1.8, "emotion": -9.0, "support": 0.0},
    }


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
