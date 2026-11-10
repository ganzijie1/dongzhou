from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings


class MandateUpstreams:
    def __init__(self) -> None:
        self.triggers: list[dict[str, object]] = []
        self.knowledge_available = True
        self.assignment_available = True

    async def health(self):
        return {
            "orgFlow": {"online": True},
            "aiNpc": {"online": True},
            "knowledge": {"online": True},
        }

    async def close(self):
        return None

    async def online_npc_ids(self):
        return set()

    async def choose_dialogue(self, npc_id, payload):
        assert npc_id > 0
        return {"code": 200, "data": {"index": 1, "type": "OPTION"}}

    async def npc_state(self, npc_id):
        return {
            "emotion": {"code": 200, "dominant": {"emotion_type": "calm", "intensity": 0.25}},
            "affection": {"code": 200, "items": [{"target": "army"}], "total": 1},
            "relationships": {"code": 200, "items": [], "total": 0},
        }

    async def npc_schedule(self, npc_id):
        if not self.assignment_available:
            from dongzhou_integration.upstreams import UpstreamUnavailable

            raise UpstreamUnavailable("schedule restarting")
        return {
            "code": 200,
            "data": {
                "plan_id": "plan-1",
                "generation_id": "generation-1",
                "schedules": [{
                    "day": 1,
                    "date": "0772-10-22",
                    "start_level": 1,
                    "end_level": 20,
                    "events": [
                        {"id": "event-supply", "transaction_id": 9100103, "name": "转运军粮", "type": "军需", "importance": 80},
                        {"id": "event-drill", "transaction_id": 9100102, "name": "检阅军阵", "type": "军事", "importance": 95},
                        {"id": "event-patrol", "transaction_id": 9100104, "name": "巡察营垒", "type": "治安", "importance": 75},
                        {"id": "event-intelligence", "transaction_id": 9100105, "name": "访求军情", "type": "谍报", "importance": 85},
                        {"id": "event-diplomacy", "transaction_id": 9100106, "name": "折冲诸侯", "type": "外交", "importance": 90},
                    ],
                }],
            },
        }

    async def stage_knowledge(self, stage_id):
        if not self.knowledge_available:
            from dongzhou_integration.upstreams import UpstreamUnavailable

            raise UpstreamUnavailable("knowledge restarting")
        return [
            {
                "id": "dongzhou_stage_001",
                "stageId": stage_id,
                "name": "东郊旧闻",
                "summary": "杜伯之谏与东郊军情。",
                "sourceDetails": [
                    {
                        "work": "《史记·周本纪》",
                        "tier": "史实骨架",
                        "scope": "千亩之败与周宣王晚年",
                        "url": "https://ctext.org/shiji/zhou-ben-ji",
                    },
                    {
                        "work": "《东周列国志》第一回",
                        "tier": "文学演绎",
                        "scope": "杜伯、左儒化厉索命",
                        "url": "https://zh.wikisource.org/zh-hans/东周列国志/第001回",
                    },
                ],
            }
        ]

    async def trigger_virtual_task(self, organization_id, payload):
        self.triggers.append(payload)
        return {"data": {"task_id": "00000000-0000-0000-0000-000000000099"}}


def configured(path: Path) -> Settings:
    return Settings(
        environment="test",
        public_origin="http://testserver",
        database_path=path,
        web_root=path.parent,
        session_secret="s" * 32,
        orgflow_url="http://org",
        orgflow_hmac_secret="o" * 32,
        orgflow_hmac_key_id="dongzhou-v1",
        orgflow_audience="org-flow-engine-administration",
        orgflow_org_id="00000000-0000-0000-0000-000000000001",
        orgflow_manager_member_id="00000000-0000-0000-0000-000000000002",
        orgflow_hero_slots={"ZuoRu": "00000000-0000-0000-0000-000000000003"},
        orgflow_hero_members={"ZuoRu": "00000000-0000-0000-0000-000000000004"},
        orgflow_hierarchy_version=7,
        game_server_id="91001",
        ainpc_url="http://ainpc",
        ainpc_token="ainpc-token",
        ainpc_game_server_id=91001,
        knowledge_url="http://knowledge",
        knowledge_token="knowledge-token",
        offline_knowledge_enabled=False,
        knowledge_file=path,
        ainpc_task_token="task-token",
    )


def start_session(client: TestClient) -> None:
    response = client.post(
        "/api/dongzhou/v1/sessions/guest",
        json={"installation_id": str(uuid4())},
    )
    assert response.status_code == 200


def complete_council(client: TestClient) -> tuple[str, dict[str, object]]:
    council_id = str(uuid4())
    request = {
        "client_request_id": council_id,
        "question": "东郊一战如何部署？\n选证：《史记·周本纪》｜史实骨架",
        "options": [
            {"index": 0, "text": "固守军粮"},
            {"index": 1, "text": "整军强攻"},
        ],
        "topic": "court_decision",
    }
    response = client.post(
        "/api/dongzhou/v1/npcs/ZuoRu/decisions", json=request
    )
    assert response.status_code == 200
    return council_id, request


def mandate_body(council_id: str, request_id: str | None = None) -> dict[str, object]:
    return {
        "client_request_id": request_id or str(uuid4()),
        "stage_id": "01",
        "stage_title": "东郊索命",
        "hero_id": "ZuoRu",
        "knowledge_id": "dongzhou_stage_001",
        "evidence_source_index": 0,
        "schedule_plan_id": "plan-1",
        "schedule_event_id": "event-drill",
        "council_request_id": council_id,
        "decision_index": 1,
        "task_type": "drill",
    }


def test_mandate_binds_kernel_knowledge_npc_and_organization() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            body = mandate_body(council_id)
            issued = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert issued.status_code == 200
            mandate = issued.json()["mandate"]
            assert mandate["state"] == "ISSUED"
            assert mandate["kernel"]["state"] in {"READY", "DEGRADED"}
            assert mandate["evidence"]["id"] == "dongzhou_stage_001"
            assert mandate["evidence"]["source"] == {
                "index": 0,
                "work": "《史记·周本纪》",
                "tier": "史实骨架",
                "scope": "千亩之败与周宣王晚年",
                "url": "https://ctext.org/shiji/zhou-ben-ji",
            }
            assert mandate["council"]["text"] == "整军强攻"
            assert mandate["assignment"]["planId"] == "plan-1"
            assert mandate["assignment"]["eventId"] == "event-drill"
            assert mandate["assignment"]["transactionId"] == 9100102
            assert mandate["assignment"]["state"] == {
                "emotion": "calm",
                "intensity": 0.25,
                "affectionCount": 1,
                "relationshipCount": 0,
            }
            assert mandate["assignment"]["readiness"] == {
                "score": 59,
                "band": "watch",
                "factors": {"runtime": -12.0, "duty": 8.1, "emotion": 6.0, "support": 2.0},
            }
            assert len(mandate["digest"]) == 64

            replay = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True
            assert replay.json()["mandate"] == mandate

            order = {
                "client_request_id": str(uuid4()),
                "task_type": "drill",
                "assignee_hero_id": "ZuoRu",
                "stage_id": "01",
                "stage_title": "Dongzhou stage 01",
                "brief": "Execute the sealed court mandate.",
                "parameters": {
                    "resource_units": 6,
                    "assignee_name": "左儒",
                    "mandate_id": mandate["id"],
                    "mandate_digest": mandate["digest"],
                },
            }
            accepted = client.post("/api/dongzhou/v1/organization/tasks", json=order)
            assert accepted.status_code == 200
            assert accepted.json()["state"] == "ACCEPTED"
            assert "mandate_id" not in upstreams.triggers[0]["parameters"]
            assert "mandate_digest" not in upstreams.triggers[0]["parameters"]
            assert "Readiness 59/100 (watch)." in upstreams.triggers[0]["brief"]

            mismatched = {
                **order,
                "client_request_id": str(uuid4()),
                "task_type": "patrol",
            }
            rejected = client.post(
                "/api/dongzhou/v1/organization/tasks", json=mismatched
            )
            assert rejected.status_code == 422
            assert rejected.json()["error"]["code"] == "court_mandate_mismatch"


def test_diplomacy_operation_is_sealed_and_drives_orgflow_brief() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            body = {
                **mandate_body(council_id),
                "task_type": "diplomacy",
                "schedule_event_id": "event-diplomacy",
                "operation": {
                    "kind": "diplomacy",
                    "target_id": "zheng",
                    "target_name": "郑国",
                    "proposal": "互通军情，共御强敌",
                },
            }
            issued = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert issued.status_code == 200
            mandate = issued.json()["mandate"]
            assert mandate["operation"] == body["operation"]

            order = {
                "client_request_id": str(uuid4()),
                "task_type": "diplomacy",
                "assignee_hero_id": "ZuoRu",
                "stage_id": "01",
                "stage_title": "Dongzhou stage 01",
                "brief": "This browser text must not replace the sealed operation.",
                "parameters": {
                    "resource_units": 9,
                    "assignee_name": "左儒",
                    "mandate_id": mandate["id"],
                    "mandate_digest": mandate["digest"],
                },
            }
            accepted = client.post("/api/dongzhou/v1/organization/tasks", json=order)
            assert accepted.status_code == 200
            trigger = upstreams.triggers[0]
            operation_reference = hashlib.sha256(
                json.dumps(
                    mandate["operation"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()[:16]
            assert trigger["brief"] == (
                "Conduct the sealed fictional Dongzhou diplomacy mission for polity "
                f"zheng. Nexus operation reference {operation_reference}. "
                "Report only the in-game outcome. "
                "Bound AINPC duty event-diplomacy (折冲诸侯) on 0772-10-22 from plan plan-1. "
                "Readiness 58/100 (watch)."
            )
            assert "郑国" not in trigger["brief"]
            assert "互通军情" not in trigger["brief"]
            assert set(trigger["parameters"]) == {
                "resource_units",
                "assignee_name",
                "stage_id",
                "stage_title",
                "assignee_hero_id",
            }


def test_non_diplomacy_mandate_rejects_diplomacy_operation() -> None:
    with TemporaryDirectory() as directory:
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=MandateUpstreams()
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            response = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={
                    **mandate_body(council_id),
                    "operation": {
                        "kind": "diplomacy",
                        "target_id": "zheng",
                        "target_name": "郑国",
                        "proposal": "互通军情",
                    },
                },
            )
            assert response.status_code == 422


def test_mandate_rejects_source_not_deliberated_by_npc() -> None:
    with TemporaryDirectory() as directory:
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=MandateUpstreams()
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            response = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={**mandate_body(council_id), "evidence_source_index": 1},
            )
            assert response.status_code == 422
            assert response.json()["error"]["code"] == "court_council_source_unverified"


def test_assignment_preview_and_stale_schedule_are_enforced() -> None:
    with TemporaryDirectory() as directory:
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=MandateUpstreams()
        )
        with TestClient(app) as client:
            start_session(client)
            preview = client.get(
                "/api/dongzhou/v1/npcs/ZuoRu/assignments/drill",
                params={"stage_id": "01"},
            )
            assert preview.status_code == 200
            assignment = preview.json()["assignment"]
            assert assignment["eventId"] == "event-drill"
            assert assignment["name"] == "检阅军阵"

            council_id, _ = complete_council(client)
            stale = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={**mandate_body(council_id), "schedule_event_id": "event-old"},
            )
            assert stale.status_code == 422
            assert stale.json()["error"]["code"] == "court_schedule_assignment_stale"


def test_mandate_retries_knowledge_without_changing_request_id() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            request_id = str(uuid4())
            body = mandate_body(council_id, request_id)
            upstreams.knowledge_available = False
            failed = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert failed.status_code == 503
            upstreams.knowledge_available = True
            retried = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert retried.status_code == 200
            assert retried.json()["mandate"]["id"].endswith(request_id)
            UUID(retried.json()["mandate"]["id"].rsplit(":", 1)[-1])


def test_mandate_retries_assignment_without_changing_request_id() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            request_id = str(uuid4())
            body = mandate_body(council_id, request_id)
            upstreams.assignment_available = False
            failed = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert failed.status_code == 503
            upstreams.assignment_available = True
            retried = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert retried.status_code == 200
            assert retried.json()["mandate"]["id"].endswith(request_id)
