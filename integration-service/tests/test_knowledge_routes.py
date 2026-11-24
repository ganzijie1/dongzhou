import json
import sqlite3
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import (
    BattleDeploymentModule,
    BattleReadinessModule,
    ServiceProvenanceModule,
    _canonical_digest,
    build_application,
)
from dongzhou_integration.config import Settings
from dongzhou_integration.security import stable_npc_id
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

    def __init__(self):
        self.events = []
        self.online_ids = set()
        self.memory_queries = []
        self.memory_items = [{
            "idempotency_key": "memory-dongzhou-stage-001",
            "source_type": "dialogue_choice",
            "fact_kind": "event",
            "timestamp": "0771-01-01T14:00:00",
            "content": "旧议曾引 dongzhou_stage_001 与《史记·周本纪》筹划东郊之战。",
        }]

    async def health(self):
        return {
            name: {"online": True, "sourceAttested": True}
            for name in ("orgFlow", "aiNpc", "knowledge")
        }

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

    async def organization_roster(self, organization_id):
        return {"data": {
            "name": "Dongzhou Court", "state": "ACTIVE", "hierarchy_version": 1,
            "growth_contribution_points": 0,
            "positions": [{
                "position_slot_id": "officer", "position_display_name": "史官",
                "role_display_name": "officer", "level_key": "L1",
            }],
            "members": [{
                "member_id": "00000000-0000-4000-8000-000000000101",
                "position_slot_id": "officer", "direct_manager_member_id": None,
                "contribution_balance": 0, "contribution_lifetime_earned": 0,
                "contribution_lifetime_spent": 0,
            }],
        }}

    async def online_npc_ids(self):
        return set(self.online_ids)

    async def send_game_event(self, kind, payload):
        self.events.append((kind, payload))
        return {"data": True}

    async def query_npc_memories(self, npc_id, *, source_type, limit=20):
        self.memory_queries.append((npc_id, source_type, limit))
        return [item for item in self.memory_items if item["source_type"] == source_type]


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
    with patch.dict("os.environ", {
        "DONGZHOU_ENV": "test",
        "DONGZHOU_WEB_ROOT": str(tmp_path),
        "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
        "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
        "DONGZHOU_ORGFLOW_HERO_MEMBERS": (
            "DuBo=00000000-0000-4000-8000-000000000101"
        ),
    }, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    upstreams.online_ids = {
        str(stable_npc_id(settings.ainpc_game_server_id, "DuBo"))
    }
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
        assert accepted.json()["receipt"]["kernel"]["moduleVersion"] == "1.3.0"
        assert accepted.json()["receipt"]["kernel"]["nexusKernelVersion"]
        assert accepted.json()["receipt"]["kernel"]["state"] == "SEALED"
        assert len(accepted.json()["receipt"]["digest"]) == 64
        assert len(accepted.json()["receipt"]["attestation"]) == 64
        assert accepted.json()["receipt"]["sourceProvenance"] == accepted.json()["sourceProvenance"]
        assert accepted.json()["sourceProvenance"]["kernel"]["module"] == "dongzhou_service_provenance"
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

        readiness = client.post(
            "/api/dongzhou/v1/battle-readiness", json={"stage_id": "02"}
        )
        assert readiness.status_code == 200, readiness.json()
        deployed = client.post("/api/dongzhou/v1/battle-deployment", json={
            "stage_id": "02",
            "battle_readiness": readiness.json(),
            "campaign_route": guided.json(),
        })
        assert deployed.status_code == 200, deployed.json()
        deployment = deployed.json()
        assert deployment["routeDigest"] == guided.json()["receipt"]["digest"]
        assert deployment["battlePlan"] == {
            "formation": "balanced",
            "vanguardHeroId": None,
            "supportIds": [],
            "supportEffect": {
                "provisions": 0,
                "morale": 0,
                "attack": 0,
                "defense": 0,
                "recon": 0,
            },
        }

        report = {
            "id": deployment["reportId"],
            "stageId": "02",
            "won": True,
            "turns": 8,
            "ownLosses": 1,
            "terminalReason": "victory",
            "campaignRoute": guided.json(),
            "battleReadiness": readiness.json(),
            "battleDeployment": deployment,
            "battlePlan": deployment["battlePlan"],
        }
        saved = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 2,
            "payload": {"completed": ["01", "02"], "organization": {"battleReports": [report]}},
        })
        assert saved.status_code == 200, saved.json()
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


def test_battle_readiness_seals_all_four_services_and_rejects_tampering(tmp_path):
    scenario = tmp_path / "scenario"
    scenario.mkdir()
    (scenario / "campaign.json").write_text(json.dumps({
        "stages": [{
            "id": "01", "index": 1, "battleTitle": "东郊索命",
            "stage": {"deploy": {
                "unselectables": [{"hero": "DuBo"}],
                "selectables": [],
            }},
        }],
    }, ensure_ascii=False), encoding="utf-8")
    org_id = "00000000-0000-4000-8000-000000000100"
    member_id = "00000000-0000-4000-8000-000000000101"
    with patch.dict("os.environ", {
        "DONGZHOU_ENV": "test",
        "DONGZHOU_WEB_ROOT": str(tmp_path),
        "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
        "DONGZHOU_ORGFLOW_ORG_ID": org_id,
        "DONGZHOU_ORGFLOW_HERO_MEMBERS": f"DuBo={member_id}",
    }, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    upstreams.online_ids = {
        str(stable_npc_id(settings.ainpc_game_server_id, "DuBo"))
    }
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        path = "/api/dongzhou/v1/battle-readiness"
        assert client.post(path, json={"stage_id": "01"}).status_code == 401
        session = client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        )
        assert session.status_code == 200
        player_id = session.json()["playerId"]
        remote_task_id = str(uuid4())
        closure_digest = "c" * 64
        planned = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 1,
            "payload": {
                "formation": "assault",
                "stageVanguards": {"01": "DuBo"},
                "organization": {
                    "members": [{"id": "DuBo", "name": "DuBo"}],
                    "tasks": [{
                        "id": "support-01",
                        "remoteResult": remote_task_id,
                        "stageId": "01",
                        "assigneeId": "DuBo",
                        "closureReceipt": {"digest": closure_digest},
                    }],
                    "pendingSupport": [{
                    "id": "support-01",
                    "stageId": "01",
                    "memberId": "DuBo",
                    "source": "军需预备",
                    "provisions": 24,
                }],
                },
            },
        })
        assert planned.status_code == 200, planned.json()
        with sqlite3.connect(settings.database_path) as database:
            database.execute(
                "INSERT INTO requests "
                "(player_id,request_id,kind,state,request_payload,response_payload,external_id) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    player_id,
                    str(uuid4()),
                    "organization_task",
                    "COMPLETED",
                    json.dumps({
                        "task_type": "supply",
                        "stage_id": "01",
                        "assignee_hero_id": "DuBo",
                    }),
                    json.dumps({"terminal": {
                        "settlement": {"result": "SUCCESS"},
                        "closureReceipt": {
                            "state": "SEALED",
                            "digest": closure_digest,
                        },
                    }}),
                    remote_task_id,
                ),
            )
        prepared = client.post(path, json={"stage_id": "01"})
        assert prepared.status_code == 200
        receipt = prepared.json()
        assert receipt["state"] == "READY"
        assert receipt["knowledge"]["knowledgeIds"] == ["dongzhou_stage_001"]
        assert receipt["organization"] == {
            "organizationId": org_id,
            "state": "ACTIVE",
            "hierarchyVersion": 1,
            "activeHeroIds": ["DuBo"],
        }
        assert receipt["aiNpc"] == {"readyHeroIds": ["DuBo"]}
        assert receipt["kernel"]["module"] == "dongzhou_battle_readiness"
        assert receipt["kernel"]["moduleVersion"] == "1.2.0"
        assert receipt["kernel"]["state"] == "SEALED"
        assert len(receipt["readinessId"]) == 36
        assert len(receipt["playerDigest"]) == 64
        assert len(receipt["digest"]) == 64
        readiness_trace = {
            key: json.loads(json.dumps(value))
            for key, value in receipt.items()
            if key not in {"digest", "kernel"}
        }
        legacy_readiness_trace = json.loads(json.dumps(readiness_trace))
        legacy_readiness_trace.pop("readinessId")
        legacy_readiness_trace.pop("playerDigest")
        for legacy_version in ("1.0.0", "1.1.0"):
            assert BattleReadinessModule.verify({
                **legacy_readiness_trace,
                "digest": _canonical_digest(legacy_readiness_trace),
                "kernel": {
                    **receipt["kernel"],
                    "moduleVersion": legacy_version,
                },
            })

        with sqlite3.connect(settings.database_path) as database:
            original_payload = database.execute(
                "SELECT payload FROM saves WHERE player_id=?", (player_id,)
            ).fetchone()[0]
            tampered_payload = json.loads(original_payload)
            tampered_payload["organization"]["pendingSupport"][0]["provisions"] = 200
            database.execute(
                "UPDATE saves SET payload=? WHERE player_id=?",
                (json.dumps(tampered_payload), player_id),
            )
        tampered_deployment = client.post(
            "/api/dongzhou/v1/battle-deployment",
            json={
                "stage_id": "01",
                "battle_readiness": receipt,
                "campaign_route": None,
            },
        )
        assert tampered_deployment.status_code == 409
        assert tampered_deployment.json()["error"]["code"] == (
            "battle_deployment_support_effect_mismatch"
        )
        with sqlite3.connect(settings.database_path) as database:
            database.execute(
                "UPDATE saves SET payload=? WHERE player_id=?",
                (original_payload, player_id),
            )

        unissued_trace = json.loads(json.dumps(readiness_trace))
        unissued_trace["readinessId"] = str(uuid4())
        unissued_readiness = BattleReadinessModule.seal(unissued_trace)
        unissued_deployment = client.post(
            "/api/dongzhou/v1/battle-deployment",
            json={
                "stage_id": "01",
                "battle_readiness": unissued_readiness,
                "campaign_route": None,
            },
        )
        assert unissued_deployment.status_code == 409
        assert unissued_deployment.json()["error"]["code"] == (
            "battle_deployment_readiness_invalid"
        )

        deployed = client.post("/api/dongzhou/v1/battle-deployment", json={
            "stage_id": "01",
            "battle_readiness": receipt,
            "campaign_route": None,
        })
        assert deployed.status_code == 200, deployed.json()
        deployment = deployed.json()
        assert deployment["state"] == "AUTHORIZED"
        assert deployment["stageId"] == "01"
        assert deployment["readinessDigest"] == receipt["digest"]
        assert deployment["routeDigest"] is None
        assert deployment["battlePlan"] == {
            "formation": "assault",
            "vanguardHeroId": "DuBo",
            "supportIds": ["support-01"],
            "supportEffect": {
                "provisions": 24,
                "morale": 0,
                "attack": 0,
                "defense": 0,
                "recon": 0,
            },
        }
        assert deployment["reportId"] == (
            "battle:01:" + deployment["deploymentId"]
        )
        assert deployment["kernel"]["module"] == "dongzhou_battle_deployment"
        assert deployment["kernel"]["moduleVersion"] == "1.2.0"
        current_trace = {
            key: json.loads(json.dumps(value))
            for key, value in deployment.items()
            if key not in {"digest", "kernel"}
        }
        legacy_11_trace = json.loads(json.dumps(current_trace))
        legacy_11_trace["battlePlan"].pop("supportEffect")
        legacy_11 = {
            **legacy_11_trace,
            "digest": _canonical_digest(legacy_11_trace),
            "kernel": {
                **deployment["kernel"],
                "moduleVersion": "1.1.0",
            },
        }
        assert BattleDeploymentModule.verify(legacy_11)
        legacy_10_trace = json.loads(json.dumps(legacy_11_trace))
        legacy_10_trace.pop("battlePlan")
        legacy_10 = {
            **legacy_10_trace,
            "digest": _canonical_digest(legacy_10_trace),
            "kernel": {
                **deployment["kernel"],
                "moduleVersion": "1.0.0",
            },
        }
        assert BattleDeploymentModule.verify(legacy_10)

        report = {
            "id": deployment["reportId"],
            "stageId": "01",
            "won": True,
            "turns": 6,
            "ownLosses": 0,
            "terminalReason": "victory",
            "support": {
                "provisions": 24,
                "morale": 0,
                "attack": 0,
                "defense": 0,
                "recon": 0,
                "orders": [{
                    "id": "support-01",
                    "memberId": "DuBo",
                    "source": "军需预备",
                }],
            },
            "battleReadiness": receipt,
            "battleDeployment": deployment,
            "battlePlan": deployment["battlePlan"],
        }
        saved = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 2,
            "payload": {"organization": {"battleReports": [report]}},
        })
        assert saved.status_code == 200, saved.json()
        sealed_report = saved.json()["payload"]["organization"]["battleReports"][0]
        assert sealed_report["battleReadiness"]["digest"] == receipt["digest"]
        assert sealed_report["battleDeployment"]["digest"] == deployment["digest"]
        assert sealed_report["kernelReceipt"]["kernel"]["state"] == "SEALED"

        forged_readiness = json.loads(json.dumps(receipt))
        forged_readiness["aiNpc"]["readyHeroIds"] = []
        forged = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    **report,
                    "id": "battle:01:forged-readiness",
                    "battleReadiness": forged_readiness,
                }]},
            },
        })
        assert forged.status_code == 409
        assert forged.json()["error"]["code"] == "battle_readiness_invalid"

        forged_deployment = json.loads(json.dumps(deployment))
        forged_deployment["reportId"] = "battle:01:forged-deployment"
        forged = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    **report,
                    "id": "battle:01:forged-deployment",
                    "battleDeployment": forged_deployment,
                }]},
            },
        })
        assert forged.status_code == 409
        assert forged.json()["error"]["code"] == "battle_deployment_invalid"

        forged_plan = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    **report,
                    "id": "battle:01:forged-plan",
                    "battlePlan": {
                        **deployment["battlePlan"],
                        "supportIds": [],
                    },
                }]},
            },
        })
        assert forged_plan.status_code == 409
        assert forged_plan.json()["error"]["code"] == "battle_deployment_invalid"

        missing_deployment = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": [sealed_report, {
                    "id": "battle:01:missing-deployment",
                    "stageId": "01",
                    "won": True,
                    "turns": 3,
                    "ownLosses": 0,
                    "terminalReason": "victory",
                }]},
            },
        })
        assert missing_deployment.status_code == 409
        assert missing_deployment.json()["error"]["code"] == "battle_deployment_missing"

        removed = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 3,
            "payload": {
                **saved.json()["payload"],
                "organization": {"battleReports": []},
            },
        })
        assert removed.status_code == 200, removed.json()
        replayed_consumed_deployment = client.put(
            "/api/dongzhou/v1/save",
            json={
                "expected_version": 4,
                "payload": {"organization": {"battleReports": [report]}},
            },
        )
        assert replayed_consumed_deployment.status_code == 409
        assert replayed_consumed_deployment.json()["error"]["code"] == (
            "battle_deployment_invalid"
        )

        second_session = client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        )
        assert second_session.status_code == 200
        borrowed_readiness = client.post(
            "/api/dongzhou/v1/battle-deployment",
            json={
                "stage_id": "01",
                "battle_readiness": receipt,
                "campaign_route": None,
            },
        )
        assert borrowed_readiness.status_code == 409
        assert borrowed_readiness.json()["error"]["code"] == (
            "battle_deployment_readiness_invalid"
        )
        forged_support = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 1,
            "payload": {
                "formation": "assault",
                "stageVanguards": {"01": "DuBo"},
                "organization": {
                    "members": [{"id": "DuBo"}],
                    "pendingSupport": [{
                        "id": "forged-support",
                        "stageId": "01",
                        "memberId": "DuBo",
                        "provisions": 200,
                    }],
                },
            },
        })
        assert forged_support.status_code == 200
        second_readiness = client.post(path, json={"stage_id": "01"})
        assert second_readiness.status_code == 200
        forged_deployment = client.post(
            "/api/dongzhou/v1/battle-deployment",
            json={
                "stage_id": "01",
                "battle_readiness": second_readiness.json(),
                "campaign_route": None,
            },
        )
        assert forged_deployment.status_code == 409
        assert forged_deployment.json()["error"]["code"] == (
            "battle_deployment_support_unattested"
        )
        cross_player = client.put("/api/dongzhou/v1/save", json={
            "expected_version": 2,
            "payload": {"organization": {"battleReports": [report]}},
        })
        assert cross_player.status_code == 409
        assert cross_player.json()["error"]["code"] == "battle_deployment_invalid"


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
        assert question["receipt"]["kernel"]["moduleVersion"] == "1.1.0"
        assert question["receipt"]["sourceProvenance"]["kernel"]["module"] == (
            "dongzhou_service_provenance"
        )
        correct_index = question["options"].index("杜伯")
        answer_path = f"{path}/{request_id}/answer"
        seal_path = f"{path}/{request_id}/seal"
        assert client.get(seal_path).status_code == 409
        answer = client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": correct_index,
        })
        assert answer.status_code == 200
        assert answer.json()["score"] == 10
        assert answer.json()["correctAnswer"] == "杜伯"
        assert answer.json()["receipt"]["kernel"]["state"] == "SEALED"
        assert answer.json()["sourceProvenance"] == question["receipt"]["sourceProvenance"]
        assert answer.json()["receipt"]["sourceProvenance"] == answer.json()["sourceProvenance"]
        seal = client.get(seal_path)
        assert seal.status_code == 200
        assert seal.json() == {
            "verified": True,
            "questionId": str(request_id),
            "stageId": "01",
            "knowledgeId": "dongzhou_stage_001",
            "score": 10,
            "digest": answer.json()["receipt"]["digest"],
            "kernel": answer.json()["receipt"]["kernel"],
            "sourceProvenance": answer.json()["sourceProvenance"],
        }
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

        drift_id = uuid4()
        drift_started = client.post(
            path,
            json={"client_request_id": str(drift_id), "stage_id": "01"},
        )
        assert drift_started.status_code == 200
        with sqlite3.connect(settings.database_path) as database:
            row = database.execute(
                "SELECT request_payload FROM requests WHERE request_id=?",
                (str(drift_id),),
            ).fetchone()
            payload = json.loads(row[0])
            drift_trace = {
                "schemaVersion": payload["sourceProvenance"]["schemaVersion"],
                "services": payload["sourceProvenance"]["services"],
            }
            drift_trace["services"]["knowledge"]["sourceRevision"] = "0" * 40
            payload["sourceProvenance"] = ServiceProvenanceModule.seal(drift_trace)
            database.execute(
                "UPDATE requests SET request_payload=? WHERE request_id=?",
                (json.dumps(payload, ensure_ascii=False), str(drift_id)),
            )
            database.commit()
        drifted = client.post(
            f"{path}/{drift_id}/answer",
            json={
                "action_id": drift_started.json()["action"]["actionId"],
                "answer_index": drift_started.json()["question"]["options"].index("杜伯"),
            },
        )
        assert drifted.status_code == 409
        assert drifted.json()["error"]["code"] == "knowledge_quiz_source_drift"

        client.cookies.clear()
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        assert client.get(seal_path).status_code == 404
        assert client.post(answer_path, json={
            "action_id": started.json()["action"]["actionId"],
            "answer_index": correct_index,
        }).status_code == 404


def test_history_commendation_is_roster_bound_sealed_and_idempotent(tmp_path):
    with patch.dict("os.environ", {
        "DONGZHOU_ENV": "test",
        "DONGZHOU_WEB_ROOT": str(tmp_path),
        "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
        "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
        "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000101",
    }, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        path = "/api/dongzhou/v1/npcs/DuBo/commendations"
        body = {"stage_id": "01", "knowledge_id": "dongzhou_stage_001"}
        response = client.post(path, json=body)
        assert response.status_code == 200
        result = response.json()
        assert result["state"] == "COMPLETED"
        assert result["replayed"] is False
        assert result["commendation"]["affectionType"] == "appreciation"
        assert result["commendation"]["affectionDelta"] == 2
        assert result["commendation"]["kernel"] == {
            "module": "dongzhou_npc_commendation",
            "moduleVersion": "1.1.0",
            "state": "SEALED",
        }
        assert result["commendation"]["sourceProvenance"]["kernel"]["module"] == (
            "dongzhou_service_provenance"
        )
        assert len(upstreams.events) == 1
        replay = client.post(path, json=body)
        assert replay.status_code == 200
        assert replay.json()["replayed"] is True
        assert replay.json()["commendation"]["digest"] == result["commendation"]["digest"]
        assert len(upstreams.events) == 1
        assert client.post(path, json={**body, "knowledge_id": "missing"}).status_code == 409
        assert client.post("/api/dongzhou/v1/npcs/Unknown/commendations", json=body).status_code == 404


def test_history_recollection_uses_authoritative_memory_and_seals_receipt(tmp_path):
    with patch.dict("os.environ", {
        "DONGZHOU_ENV": "test",
        "DONGZHOU_WEB_ROOT": str(tmp_path),
        "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
        "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
        "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000101",
    }, clear=True):
        settings = Settings.from_env()
    upstreams = PublishedKnowledge()
    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        assert client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code == 200
        path = "/api/dongzhou/v1/npcs/DuBo/recollections"
        body = {"stage_id": "01", "knowledge_id": "dongzhou_stage_001"}
        response = client.post(path, json=body)
        assert response.status_code == 200
        result = response.json()
        receipt = result["recollection"]
        assert result["state"] == "COMPLETED"
        assert receipt["heroId"] == "DuBo"
        assert receipt["memoryId"] == "memory-dongzhou-stage-001"
        assert receipt["memoryType"] == "dialogue_choice"
        assert receipt["matchMode"] == "knowledge_dialogue"
        assert receipt["memoryReceipt"] == {
            "idempotencyKey": receipt["memoryId"],
            "sourceType": receipt["memoryType"],
            "factKind": "event",
            "timestamp": receipt["memoryTimestamp"],
            "content": receipt["memoryContent"],
            "digest": receipt["memoryDigest"],
        }
        assert len(receipt["memoryDigest"]) == 64
        assert len(receipt["digest"]) == 64
        assert receipt["kernel"]["module"] == "dongzhou_npc_recollection"
        assert receipt["kernel"]["moduleVersion"] == "1.2.0"
        assert receipt["kernel"]["state"] == "SEALED"
        assert receipt["sourceProvenance"]["kernel"]["module"] == (
            "dongzhou_service_provenance"
        )
        assert upstreams.memory_queries == [(int(receipt["npcId"]), "dialogue_choice", 50)]

        replay = client.post(path, json=body)
        assert replay.status_code == 200
        assert replay.json()["recollection"]["digest"] == receipt["digest"]
        upstreams.memory_items = []
        missing = client.post(path, json=body)
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "npc_recollection_not_found"
        assert client.post(path, json={**body, "knowledge_id": "missing"}).status_code == 409
        assert client.post("/api/dongzhou/v1/npcs/Unknown/recollections", json=body).status_code == 404
