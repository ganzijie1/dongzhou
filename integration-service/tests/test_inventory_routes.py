from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


class InventoryUpstreams:
    unavailable = False

    def __init__(self, organization_id: str) -> None:
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
