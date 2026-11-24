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
