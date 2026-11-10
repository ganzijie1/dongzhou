from dongzhou_integration.assignments import AssignmentUnavailable, select_assignment


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
