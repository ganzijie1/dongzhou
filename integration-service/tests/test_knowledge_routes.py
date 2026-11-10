from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


class PublishedKnowledge:
    unavailable = False

    async def health(self):
        return {name: {"online": True} for name in ("orgFlow", "aiNpc", "knowledge")}

    async def close(self):
        pass

    async def stage_knowledge(self, stage_id):
        if self.unavailable:
            raise UpstreamUnavailable("not ready")
        return [{"id": "dongzhou_stage_004", "stageId": stage_id, "name": "本回史料"}] if stage_id == "03b" else []


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
