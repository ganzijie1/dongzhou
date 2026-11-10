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
                "Report only the in-game outcome."
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
