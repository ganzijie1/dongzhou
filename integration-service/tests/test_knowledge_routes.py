import json
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


class PublishedKnowledge:
    unavailable = False
    missing_stage = None
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
        if stage_id == self.missing_stage:
            return []
        if stage_id == "01":
            return [{
                "id": "dongzhou_stage_001",
                "stageId": "01",
                "name": "第一回·东郊索命",
                "entities": {"npcs": [{"name": "杜伯"}]},
                "sourceDetails": [{"work": "《史记·周本纪》", "tier": "史官骨架", "scope": "杜伯之死"}],
            }]
        if stage_id == "02":
            return [{
                "id": "dongzhou_stage_002",
                "stageId": "02",
                "name": "第二回史料",
                "sourceDetails": [{"work": "史记", "tier": "史实骨架", "scope": "骊山之变"}],
            }]
        return [{"id": "dongzhou_stage_004", "stageId": stage_id, "name": "本回史料"}] if stage_id == "03b" else []

    async def campaign_route(self, from_map_id, to_map_id, method="campaign_progression"):
        if self.unavailable:
            raise UpstreamUnavailable("not ready")
        details = {
            "campaign_progression": dict(self.route_detail),
            "fixed_point": {"x": 1, "y": 1},
            "npc_dialog": {
                "npc": {"id": 90000103, "name": "乡民", "x": 3, "y": 1},
                "dialog_path": [{"selected_option": "请为我军引路。"}],
                "target": {"x": 1, "y": 1},
            },
        }
        return {
            "found": True,
            "from": from_map_id,
            "to": to_map_id,
            "plans": [{
                "steps": [{
                    "from": from_map_id,
                    "to": to_map_id,
                    "routes": [{
                        "route_id": (
                            f"campaign_progression_{from_map_id}_{to_map_id}"
                            if method == "campaign_progression"
                            else f"dongzhou_{method}_{from_map_id}_{to_map_id}"
                        ),
                        "method": method,
                        "detail": details[method],
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
    scenario = tmp_path / "scenario"
    scenario.mkdir()
    (scenario / "campaign.json").write_text(json.dumps({
        "stages": [{"id": "01", "index": 1}, {"id": "02", "index": 2}],
    }), encoding="utf-8")
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
        assert accepted.json()["receipt"]["kernel"]["module"] == "dongzhou_campaign_route"
        assert accepted.json()["receipt"]["kernel"]["moduleVersion"] == "1.2.0"
        assert accepted.json()["receipt"]["kernel"]["nexusKernelVersion"]
        assert accepted.json()["receipt"]["kernel"]["state"] == "SEALED"
        assert len(accepted.json()["receipt"]["digest"]) == 64
        assert len(accepted.json()["receipt"]["attestation"]) == 64
        assert accepted.json()["knowledgeWitnesses"]["from"]["knowledgeIds"] == ["dongzhou_stage_001"]
        assert accepted.json()["knowledgeWitnesses"]["to"]["knowledgeIds"] == ["dongzhou_stage_002"]
        assert len(accepted.json()["knowledgeWitnesses"]["from"]["digest"]) == 64
        assert len(accepted.json()["options"]) == 3
        assert {item["method"] for item in accepted.json()["options"]} == {
            "campaign_progression", "fixed_point", "npc_dialog"
        }
        assert next(item for item in accepted.json()["options"] if item["method"] == "fixed_point")["moraleDelta"] == 6
        guided = client.post(path, json={**request, "route_method": "npc_dialog"})
        assert guided.status_code == 200
        assert guided.json()["routeId"] == "dongzhou_npc_dialog_900001_900002"
        assert guided.json()["provisionCost"] == 1
        assert guided.json()["moraleDelta"] == -4
        assert guided.json()["guideName"] == "乡民"
        guided_replay = client.post(path, json={**request, "route_method": "npc_dialog"})
        assert guided_replay.json()["receipt"]["digest"] == guided.json()["receipt"]["digest"]
        assert guided.json()["receipt"]["digest"] != accepted.json()["receipt"]["digest"]
        assert guided.json()["receipt"]["digest"] != accepted.json()["receipt"]["digest"]
        repeated = client.post(path, json={**request, "route_method": "npc_dialog"})
        assert repeated.json()["receipt"] == guided.json()["receipt"]

        report = {
            "id": "battle:02:route-attested",
            "stageId": "02",
            "won": True,
            "turns": 8,
            "ownLosses": 1,
            "terminalReason": "victory",
            "campaignRoute": guided.json(),
        }
        saved = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 2,
            "payload": {"completed": ["01", "02"], "organization": {"battleReports": [report]}},
        })
        assert saved.status_code == 200
        sealed_report = saved.json()["payload"]["organization"]["battleReports"][0]
        assert sealed_report["campaignRoute"]["receipt"]["attestation"] == guided.json()["receipt"]["attestation"]
        assert sealed_report["kernelReceipt"]["kernel"]["state"] == "SEALED"

        missing_route = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    **report,
                    "id": "battle:02:missing-route",
                    "campaignRoute": None,
                }]},
            },
        })
        assert missing_route.status_code == 409
        assert missing_route.json()["error"]["code"] == "battle_campaign_route_missing"

        forged_route = json.loads(json.dumps(accepted.json()))
        forged_route["provisionCost"] = 0
        forged = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    **report,
                    "id": "battle:02:forged-route",
                    "campaignRoute": forged_route,
                }]},
            },
        })
        assert forged.status_code == 409
        assert forged.json()["error"]["code"] == "battle_campaign_route_invalid"

        upstreams.missing_stage = "02"
        missing = client.post(path, json=request)
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "campaign_route_knowledge_missing"
        upstreams.missing_stage = None

        upstreams.route_detail = {**upstreams.route_detail, "to_stage_id": "wrong"}
        invalid = client.post(path, json=request)
        assert invalid.status_code == 502
        assert invalid.json()["error"]["code"] == "campaign_route_invalid"

        upstreams.unavailable = True
        unavailable = client.post(path, json=request)
        assert unavailable.status_code == 503
        assert unavailable.json()["error"]["code"] == "knowledge_route_unavailable"


def test_knowledge_quiz_hides_answer_and_is_idempotent_and_player_scoped(tmp_path):
    scenario = tmp_path / "scenario"
    scenario.mkdir()
    (scenario / "dongzhou-knowledge.json").write_text(json.dumps({
        "entries": [
            {"stageId": "01", "people": ["杜伯"]},
            {"stageId": "02", "people": ["周幽王", "褒姒", "申侯", "郑桓公"]},
        ]
    }, ensure_ascii=False), encoding="utf-8")
    with patch.dict("os.environ", {
        "DONGZHOU_ENV": "test",
        "DONGZHOU_WEB_ROOT": str(tmp_path),
        "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
    }, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    request_id = uuid4()
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        path = "/api/dongzhou/v1/knowledge/quiz"
        body = {"client_request_id": str(request_id), "stage_id": "01"}
        assert client.post(path, json=body).status_code == 401
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        started = client.post(path, json=body)
        assert started.status_code == 200
        question = started.json()["question"]
        assert len(question["options"]) == 4
        assert "correctIndex" not in json.dumps(started.json())
        assert question["receipt"]["kernel"]["module"] == "dongzhou_knowledge_tournament"
        correct_index = question["options"].index("杜伯")
        answer_path = f"{path}/{request_id}/answer"
        answer = client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": correct_index,
        })
        assert answer.status_code == 200
        assert answer.json()["score"] == 10
        assert answer.json()["correctAnswer"] == "杜伯"
        assert answer.json()["receipt"]["kernel"]["state"] == "SEALED"
        replay = client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": correct_index,
        })
        assert replay.status_code == 200
        assert replay.json()["replayed"] is True
        changed = client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": (correct_index + 1) % 4,
        })
        assert changed.status_code == 409
        replay_start = client.post(path, json=body)
        assert replay_start.status_code == 200
        assert replay_start.json()["state"] == "COMPLETED"

        client.cookies.clear()
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        assert client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": correct_index,
        }).status_code == 404
