from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


class PublishedKnowledge:
    unavailable = False
    route_detail = {
        "from_stage_id": "01",
        "from_stage_title": "第一回",
        "to_stage_id": "02",
        "to_stage_title": "第二回",
        "requires_completed_stage_id": "01",
        "provision_cost": 2,
    }

    async def health(self):
        return {name: {"online": True} for name in ("orgFlow", "aiNpc", "knowledge")}

    async def close(self):
        pass

    async def stage_knowledge(self, stage_id):
        if self.unavailable:
            raise UpstreamUnavailable("not ready")
        return [{"id": "dongzhou_stage_004", "stageId": stage_id, "name": "本回史料"}] if stage_id == "03b" else []

    async def campaign_route(self, from_map_id, to_map_id):
        if self.unavailable:
            raise UpstreamUnavailable("not ready")
        return {
            "found": True,
            "plans": [{
                "steps": [{
                    "from": from_map_id,
                    "to": to_map_id,
                    "routes": [{
                        "route_id": f"campaign_progression_{from_map_id}_{to_map_id}",
                        "method": "campaign_progression",
                        "detail": dict(self.route_detail),
                    }],
                }],
            }],
        }


def test_published_knowledge_requires_session_and_codex_is_player_scoped(tmp_path):
    with patch.dict("os.environ", {"DONGZHOU_ENV": "test", "DONGZHOU_WEB_ROOT": str(tmp_path), "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db")}, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        route = "/api/dongzhou/v1/knowledge/stages/03b"
        assert client.get(route).status_code == 401
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        response = client.get(route)
        assert response.status_code == 200
        assert response.json()["mode"] == "connected"
        entries = response.json()["results"]
        assert entries[0]["stageId"] == "03b"
        assert client.get("/api/dongzhou/v1/knowledge/codex").json()["results"] == entries
        assert client.get(route).status_code == 200
        assert len(client.get("/api/dongzhou/v1/knowledge/codex").json()["results"]) == 1
        assert client.get("/api/dongzhou/v1/knowledge/stages/unknown").json()["results"] == []
        upstreams.unavailable = True
        assert client.get(route).status_code == 503
        assert client.get("/api/dongzhou/v1/knowledge/codex").json()["results"] == entries
        client.cookies.clear()
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        assert client.get("/api/dongzhou/v1/knowledge/codex").json()["results"] == []


def test_campaign_route_requires_completed_predecessor_and_validates_published_detail(tmp_path):
    with patch.dict("os.environ", {"DONGZHOU_ENV": "test", "DONGZHOU_WEB_ROOT": str(tmp_path), "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db")}, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    request = {
        "from_stage_id": "01",
        "from_stage_index": 1,
        "to_stage_id": "02",
        "to_stage_index": 2,
    }
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        path = "/api/dongzhou/v1/knowledge/routes"
        assert client.post(path, json=request).status_code == 401
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        locked = client.post(path, json=request)
        assert locked.status_code == 409
        assert locked.json()["error"]["code"] == "campaign_route_locked"
        assert client.put("/api/dongzhou/v1/save", json={"expected_version": 1, "payload": {"completed": ["01"]}}).status_code == 200
        accepted = client.post(path, json=request)
        assert accepted.status_code == 200
        assert accepted.json()["routeId"] == "campaign_progression_900001_900002"
        assert accepted.json()["provisionCost"] == 2

        upstreams.route_detail = {**upstreams.route_detail, "to_stage_id": "wrong"}
        invalid = client.post(path, json=request)
        assert invalid.status_code == 502
        assert invalid.json()["error"]["code"] == "campaign_route_invalid"

        upstreams.unavailable = True
        unavailable = client.post(path, json=request)
        assert unavailable.status_code == 503
        assert unavailable.json()["error"]["code"] == "knowledge_route_unavailable"
