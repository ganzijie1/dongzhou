from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


TOOL = Path(__file__).resolve().parents[2] / "tools" / "verify-live-integration.py"
SPEC = importlib.util.spec_from_file_location("verify_live_integration", TOOL)
assert SPEC is not None and SPEC.loader is not None
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def test_execution_projection_accepts_only_public_outcome_fields() -> None:
    detail = verifier.validate_npc_execution({
        "available": True,
        "running": False,
        "paused": False,
        "waitingForReport": False,
        "phase": "ENDED",
        "outcome": "unconfirmed",
        "scheduleName": "校核军令",
    })

    assert detail == {
        "available": True,
        "phase": "ENDED",
        "outcome": "unconfirmed",
        "publicFields": 7,
    }


@pytest.mark.parametrize("field", ["status_message", "terminal_event_payload", "error_message"])
def test_execution_projection_rejects_internal_fields(field: str) -> None:
    with pytest.raises(AssertionError, match="leaked fields"):
        verifier.validate_npc_execution({
            "available": False,
            field: "private",
        })


def test_execution_projection_rejects_unknown_outcome() -> None:
    with pytest.raises(AssertionError, match="outcome is invalid"):
        verifier.validate_npc_execution({
            "available": False,
            "outcome": "assumed_complete",
        })


@pytest.mark.parametrize(("event", "source"), [
    ({"type": "政务", "id": "plan:1", "extra_data": {"schedule_origin": "90_day_plan"}}, "90_day_plan"),
    ({"type": "人才", "id": "duty:1", "extra_data": {
        "source": "dongzhou_scheduled_duty",
        "hero_id": "ZuoRu",
        "rule_id": "bead406a-1797-5cd4-bf2c-ed21bc82bfcf",
        "schedule_origin": "90_day_plan",
    }}, "dongzhou_scheduled_duty"),
    ({"type": "准备工作", "id": "court:1", "extra_data": {
        "source": "dongzhou_court_duty",
        "hero_id": "ZuoRu",
        "task_type": "supply",
        "stage_id": "01",
        "plan_id": "plan-1",
        "schedule_origin": "90_day_plan",
    }}, "dongzhou_court_duty"),
    ({"type": "temp", "transaction_type": "temp", "id": "temp_event:1", "extra_data": {
        "source": "event_report",
        "event_id": "dongzhou-mandate-1",
        "mandate_id": "dongzhou:player:mandate",
        "mandate_digest": "a" * 64,
    }}, "event_report"),
])
def test_schedule_event_sources_require_authoritative_bindings(event: dict, source: str) -> None:
    assert verifier.schedule_event_source(event, "plan-1") == source


@pytest.mark.parametrize("event", [
    {"type": "政务", "id": "bad:1", "extra_data": {"source": "unknown"}},
    {"type": "人才", "id": "bad:2", "extra_data": {
        "source": "dongzhou_scheduled_duty", "hero_id": "ZuoRu", "rule_id": "not-a-uuid",
    }},
    {"type": "准备工作", "id": "bad:3", "extra_data": {
        "source": "dongzhou_court_duty", "hero_id": "ZuoRu", "task_type": "supply",
        "stage_id": "01", "plan_id": "another-plan",
    }},
])
def test_schedule_event_sources_reject_unknown_or_unbound_events(event: dict) -> None:
    with pytest.raises(AssertionError):
        verifier.schedule_event_source(event, "plan-1")
