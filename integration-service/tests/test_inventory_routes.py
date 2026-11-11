from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


class InventoryUpstreams:
    unavailable = False

    def __init__(self, organization_id: str) -> None:
        self.adjustment_calls = []
        self.snapshot = {
            "organization_id": organization_id,
            "game_server_id": "91001",
            "revision": 7,
            "accounts": [
                {"resource_key": "task.execution", "balance": 128, "version": 3},
                {"resource_key": "war.supply", "balance": 44, "version": 1},
            ],
        }

    async def health(self):
        return {name: {"online": True} for name in ("orgFlow", "aiNpc", "knowledge")}

    async def close(self):
        pass

    async def organization_inventory(self, organization_id):
        if self.unavailable:
            raise UpstreamUnavailable("inventory restarting")
        return {"data": self.snapshot}

    async def adjust_organization_inventory(self, organization_id, payload, *, idempotency_key):
        self.adjustment_calls.append((organization_id, payload, idempotency_key))
        account = next(
            item
            for item in self.snapshot["accounts"]
            if item["resource_key"] == payload["resource_key"]
        )
        balance_after = account["balance"] + payload["delta_units"]
        if balance_after < 0:
            raise UpstreamUnavailable(
                "insufficient inventory",
                status_code=409,
                error_code="organization_inventory_balance_insufficient",
            )
        account["balance"] = balance_after
        account["version"] += 1
        self.snapshot["revision"] += 1
        return {
            "data": {
                "entry_id": str(uuid4()),
                "organization_id": organization_id,
                "game_server_id": self.snapshot["game_server_id"],
                "resource_key": payload["resource_key"],
                "delta_units": payload["delta_units"],
                "reason_code": payload["reason_code"],
                "balance_after": balance_after,
                "account_version_after": account["version"],
                "inventory_revision_after": self.snapshot["revision"],
            }
        }


def test_inventory_requires_session_and_validates_authoritative_identity(tmp_path):
    organization_id = "596354f7-c343-5c78-958d-757a9e58fde6"
    with patch.dict(
        "os.environ",
        {
            "DONGZHOU_ENV": "test",
            "DONGZHOU_WEB_ROOT": str(tmp_path),
            "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
            "DONGZHOU_GAME_SERVER_ID": "91001",
            "DONGZHOU_ORGFLOW_ORG_ID": organization_id,
        },
        clear=True,
    ):
        settings = Settings.from_env()
    upstreams = InventoryUpstreams(organization_id)
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        route = "/api/dongzhou/v1/organization/inventory"
        assert client.get(route).status_code == 401
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        response = client.get(route)
        assert response.status_code == 200
        assert response.json() == {
            "organizationId": organization_id,
            "gameServerId": "91001",
            "revision": 7,
            "accounts": [
                {"resourceKey": "task.execution", "balance": 128, "version": 3},
                {"resourceKey": "war.supply", "balance": 44, "version": 1},
            ],
        }
        upstreams.snapshot["organization_id"] = str(uuid4())
        assert client.get(route).status_code == 502
        upstreams.snapshot["organization_id"] = organization_id
        upstreams.snapshot["accounts"].append(
            {"resource_key": "task.execution", "balance": 1, "version": 1}
        )
        assert client.get(route).status_code == 502
        upstreams.snapshot["accounts"].pop()
        upstreams.unavailable = True
        assert client.get(route).status_code == 503


def test_inventory_requisition_is_authoritative_and_idempotent(tmp_path):
    organization_id = "596354f7-c343-5c78-958d-757a9e58fde6"
    with patch.dict(
        "os.environ",
        {
            "DONGZHOU_ENV": "test",
            "DONGZHOU_WEB_ROOT": str(tmp_path),
            "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
            "DONGZHOU_GAME_SERVER_ID": "91001",
            "DONGZHOU_ORGFLOW_ORG_ID": organization_id,
        },
        clear=True,
    ):
        settings = Settings.from_env()
    upstreams = InventoryUpstreams(organization_id)
    request_id = str(uuid4())
    payload = {"client_request_id": request_id, "units": 20, "stage_id": "01"}
    route = "/api/dongzhou/v1/organization/inventory/requisitions"
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        assert client.post(route, json=payload).status_code == 401
        assert client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        ).status_code == 200
        response = client.post(route, json=payload)
        assert response.status_code == 200
        draft = response.json()
        assert draft["state"] == "REQUIRES_ACTION"
        assert draft["requestId"] == request_id
        assert draft["stageId"] == "01"
        assert draft["requisition"]["state"] == "DRAFT"
        assert draft["requisition"]["effect"] == {"provisions": 12}
        assert draft["requisition"]["kernel"]["module"] == "dongzhou_mandate_workflow"
        assert draft["action"]["code"] == "approve_inventory_requisition"
        assert len(upstreams.adjustment_calls) == 0

        approval_route = f"{route}/{draft['requisition']['id']}/resume"
        bad_action = client.post(
            approval_route,
            json={"action_id": str(uuid4()), "decision": "APPROVE"},
        )
        assert bad_action.status_code == 409
        result_response = client.post(
            approval_route,
            json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
        )
        assert result_response.status_code == 200
        result = result_response.json()
        assert result["state"] == "COMPLETED"
        assert result["requisition"]["state"] == "COMPLETED"
        assert result["effect"] == {"provisions": 12}
        assert result["inventoryDebit"]["resourceKey"] == "task.execution"
        assert result["inventoryDebit"]["delta"] == -20
        assert result["inventoryDebit"]["balanceAfter"] == 108
        assert len(upstreams.adjustment_calls) == 1

        replay = client.post(route, json=payload)
        assert replay.status_code == 200
        assert replay.json()["replayed"] is True
        assert len(upstreams.adjustment_calls) == 1

        approval_replay = client.post(
            approval_route,
            json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
        )
        assert approval_replay.status_code == 200
        assert approval_replay.json()["replayed"] is True
        assert len(upstreams.adjustment_calls) == 1

        conflict = client.post(route, json={**payload, "units": 40})
        assert conflict.status_code == 409
        assert len(upstreams.adjustment_calls) == 1

        rejected_payload = {
            "client_request_id": str(uuid4()),
            "units": 20,
            "stage_id": "01",
        }
        rejected_draft = client.post(route, json=rejected_payload).json()
        rejected = client.post(
            f"{route}/{rejected_draft['requisition']['id']}/resume",
            json={
                "action_id": rejected_draft["action"]["actionId"],
                "decision": "REJECT",
            },
        )
        assert rejected.status_code == 200
        assert rejected.json()["state"] == "REJECTED"
        assert rejected.json()["requisition"]["kernel"]["state"] == "REJECTED"
        assert len(upstreams.adjustment_calls) == 1


def test_inventory_requisition_retries_after_insufficient_balance(tmp_path):
    organization_id = "596354f7-c343-5c78-958d-757a9e58fde6"
    with patch.dict(
        "os.environ",
        {
            "DONGZHOU_ENV": "test",
            "DONGZHOU_WEB_ROOT": str(tmp_path),
            "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
            "DONGZHOU_GAME_SERVER_ID": "91001",
            "DONGZHOU_ORGFLOW_ORG_ID": organization_id,
        },
        clear=True,
    ):
        settings = Settings.from_env()
    upstreams = InventoryUpstreams(organization_id)
    account = upstreams.snapshot["accounts"][0]
    account["balance"] = 10
    request_id = str(uuid4())
    payload = {"client_request_id": request_id, "units": 20, "stage_id": "01"}
    route = "/api/dongzhou/v1/organization/inventory/requisitions"
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        )
        draft = client.post(route, json=payload).json()
        approval_route = f"{route}/{draft['requisition']['id']}/resume"
        approval = {
            "action_id": draft["action"]["actionId"],
            "decision": "APPROVE",
        }
        response = client.post(approval_route, json=approval)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "organization_inventory_insufficient"

        replayed_draft = client.post(route, json=payload)
        assert replayed_draft.status_code == 200
        assert replayed_draft.json()["replayed"] is True
        assert replayed_draft.json()["state"] == "RETRYABLE"
        assert replayed_draft.json()["requisition"]["state"] == "APPROVAL_RETRYABLE"
        cannot_reject = client.post(
            approval_route,
            json={**approval, "decision": "REJECT"},
        )
        assert cannot_reject.status_code == 409

        account["balance"] = 30
        retried = client.post(approval_route, json=approval)
        assert retried.status_code == 200
        assert retried.json()["inventoryDebit"]["balanceAfter"] == 10
        assert len(upstreams.adjustment_calls) == 2
