from __future__ import annotations

import asyncio
import json
import hashlib
import hmac
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
import httpx
from pydantic import ValidationError

from dongzhou_integration.app import (
    BattleReceiptConflict,
    CampaignRouteModule,
    NpcCollaborationRelationshipModule,
    NpcReviewRelationshipModule,
    NpcSettlementModule,
    OrganizationTaskTraceModule,
    RuntimeModule,
    _battle_support_attestations,
    _battle_game_events,
    _evidence_task_fit,
    _npc_outcome_event,
    _npc_outcome_memory,
    _npc_outcome_status,
    _npc_collaboration_affection_events,
    _organization_supervision_links,
    _organization_task_trace_view,
    _organization_task_chance,
    _prepare_due_organization_reports,
    _repair_utf8_mojibake,
    _seal_battle_reports,
    _organization_task_succeeds,
    build_application,
)
from dongzhou_integration.config import Settings
from dongzhou_integration.models import GuestSessionRequest, NpcDecisionRequest, OrganizationTaskRequest
from dongzhou_integration.security import issue_session, sign_orgflow_request, stable_event_id, stable_npc_id, stable_player_id, verify_session
from dongzhou_integration.store import GameClockConflict, Store, VersionConflict
from dongzhou_integration.upstreams import UpstreamUnavailable, Upstreams


class _HealthyUpstreams:
    async def health(self):
        return {
            "orgFlow": {"online": True},
            "aiNpc": {"online": True},
            "knowledge": {"online": True},
        }

    async def close(self):
        return None

    async def report_action_execution_result(self, payload):
        return {"code": 200, "data": {"received": True}}

    async def sync_action_catalog(self, payload):
        return {"code": 200, "data": {"count": 1}}

    async def get_virtual_task_trace(self, organization_id, task_id):
        return {
            "data": {
                "task": {
                    "task_id": task_id,
                    "organization_id": organization_id,
                    "state": "IN_PROGRESS",
                    "version": "2",
                    "supplement_count": 0,
                    "execution_exception": None,
                },
                "confirmations": [],
                "timeline": [
                    {
                        "sequence_no": "1",
                        "occurred_at": "2026-11-13T00:00:00Z",
                        "entry_type": "TASK_CREATED",
                        "reference_id": task_id,
                        "case_id": None,
                        "state_code": "GENERATED",
                        "reason_code": None,
                    }
                ],
            }
        }


class _CapturingUpstreams(_HealthyUpstreams):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    async def send_game_event(self, kind, payload):
        self.events.append((kind, payload))
        return {"code": 200}

    async def choose_dialogue(self, npc_id, payload):
        return {"data": {"type": "OPTION", "index": 0}}

    async def report_dialogue_choice(self, npc_id, payload):
        return {"npcId": str(npc_id), "insertedCount": 1, "skippedCount": 0}

    async def remember_dialogue(self, npc_id, game_time, dialogues):
        dialogue = dialogues[0]
        return {
            "idempotency_key": "memory-" + dialogue["source_record_id"],
            "source_type": "dialogue_choice",
            "fact_kind": "event",
            "timestamp": dialogue["timestamp"],
            "content": dialogue["question"],
        }


class _BehaviorUpstreams(_HealthyUpstreams):
    def __init__(self) -> None:
        self.action_results: list[dict[str, object]] = []

    async def report_action_execution_result(self, payload):
        self.action_results.append(payload)
        return {"code": 200, "data": {"received": True}}


class _NpcPreferenceUpstreams(_HealthyUpstreams):
    def __init__(self, *, applied_enabled=None) -> None:
        self.calls: list[tuple[int, bool]] = []
        self.applied_enabled = applied_enabled

    async def sync_player_ai_interaction(self, player_id, enabled):
        self.calls.append((player_id, enabled))
        applied = enabled if self.applied_enabled is None else self.applied_enabled
        return {
            "enabled": applied,
            "source": "dongzhou-player-settings",
            "updatedAt": "2026-11-11T12:00:00Z",
        }


class _NpcRecoveryUpstreams(_HealthyUpstreams):
    def __init__(self, online_ids=(), roster=None, *, roster_unavailable=False) -> None:
        self.registrations: list[list[dict[str, str]]] = []
        self.activations: list[tuple[list[dict[str, str]], str, str]] = []
        self.online_ids = set(online_ids)
        self.roster = roster or {
            "data": {
                "name": "Dongzhou Court", "state": "ACTIVE", "hierarchy_version": 1,
                "growth_contribution_points": 0, "positions": [], "members": [],
            }
        }
        self.supervision: list[dict[str, object]] = []
        self.roster_unavailable = roster_unavailable

    async def online_npc_ids(self):
        return set(self.online_ids)

    async def register_npcs(self, npcs):
        self.registrations.append(npcs)
        return {"code": 200}

    async def set_npcs_online(self, npcs, game_time, login_round):
        self.activations.append((npcs, game_time, login_round))
        return []

    async def organization_roster(self, organization_id):
        if self.roster_unavailable:
            raise UpstreamUnavailable("organization roster is restarting")
        return self.roster

    async def ensure_organization_supervision(self, **values):
        self.supervision.append(values)
        return {
            "code": 200, "created": False, "deactivatedManagerNpcIds": [],
            "relationshipIds": ["existing"] if values["manager_npc_id"] else [],
        }


class SecurityTests(unittest.TestCase):
    def test_nested_utf8_mojibake_is_repaired_without_changing_chinese(self) -> None:
        expected = "与左儒对话：先固军粮"
        broken = expected.encode("utf-8").decode("latin-1")
        nested = broken.encode("utf-8").decode("latin-1")
        self.assertEqual(_repair_utf8_mojibake(expected), expected)
        self.assertEqual(_repair_utf8_mojibake("旧事：" + nested), "旧事：" + expected)

    def test_http_uuid_fields_accept_json_strings(self) -> None:
        request_id = "00000000-0000-4000-8000-000000000001"
        self.assertEqual(str(GuestSessionRequest(installation_id=request_id).installation_id), request_id)
        decision = NpcDecisionRequest(
            client_request_id=request_id,
            question="Choose",
            options=[{"index": 0, "text": "A"}, {"index": 1, "text": "B"}],
        )
        self.assertEqual(str(decision.client_request_id), request_id)
        task = OrganizationTaskRequest(
            client_request_id=request_id,
            task_type="patrol",
            assignee_hero_id="ZuoRu",
            stage_id="01",
            stage_title="Patrol",
            brief="Inspect the route",
            parameters={"resource_units": 1, "assignee_name": "Zuo Ru"},
        )
        self.assertEqual(str(task.client_request_id), request_id)

        with self.assertRaises(ValidationError):
            OrganizationTaskRequest(
                client_request_id=request_id,
                task_type="survey",
                assignee_hero_id="ZuoRu",
                stage_id="01",
                stage_title="Survey",
                brief="Unsupported organization task",
                parameters={"resource_units": 1, "assignee_name": "Zuo Ru"},
            )

    def test_session_round_trip_and_stable_ids(self) -> None:
        player_id = uuid4()
        secret = "s" * 32
        self.assertEqual(verify_session(issue_session(player_id, secret), secret), player_id)
        self.assertEqual(stable_npc_id(91001, "DuBo"), stable_npc_id(91001, "DuBo"))
        self.assertNotEqual(stable_npc_id(91001, "DuBo"), stable_npc_id(91001, "ZuoRu"))
        self.assertGreaterEqual(stable_player_id(91001, player_id), 1 << 63)
        self.assertLess(stable_npc_id(91001, "DuBo"), 1 << 63)
        self.assertEqual(stable_player_id(91001, player_id), stable_player_id(91001, player_id))
        request_id = uuid4()
        self.assertEqual(stable_event_id(player_id, request_id), stable_event_id(player_id, request_id))


class OrganizationOutcomeTests(unittest.TestCase):
    def test_battle_reports_create_deduplicated_events_for_participating_npcs(self) -> None:
        settings = type("SettingsView", (), {"ainpc_game_server_id": 91001})()
        player_id = UUID("00000000-0000-4000-8000-000000000123")
        payload = {
            "organization": {
                "members": [
                    {"id": "DuBo", "name": "杜伯"},
                    {"id": "ZuoRu", "name": "左儒"},
                    {"id": "SiTu", "name": "司徒"},
                ],
                "battleReports": [{
                    "id": "battle:02:1000",
                    "stageId": "02",
                    "stageTitle": "繻葛之战",
                    "won": True,
                    "turns": 8,
                    "ownLosses": 1,
                    "month": 4,
                    "councils": [
                        {"memberId": "ZuoRu"},
                        {"memberId": "Unknown"},
                    ],
                    "mandates": [{"id": "mandate-1", "heroId": "ZuoRu"}],
                    "sources": ["左儒军议", "军粮转运"],
                    "support": {
                        "orders": [
                            {"memberId": "DuBo"},
                            {"memberId": "ZuoRu"},
                        ]
                    },
                }],
            }
        }
        report = payload["organization"]["battleReports"][0]
        report["councils"] = [{"id": "council-1", "memberId": "ZuoRu"}]
        report["mandates"] = [{
            "id": "mandate-1",
            "heroId": "ZuoRu",
            "digest": "a" * 64,
        }]
        report["support"]["orders"] = [{"id": "order-1", "memberId": "DuBo"}]
        campaign_routes = CampaignRouteModule("test-route-attestation-secret")
        route = {
            "fromStageId": "01",
            "toStageId": "02",
            "fromMapId": 900001,
            "toMapId": 900002,
            "knowledgeWitnesses": {
                "from": {"stageId": "01", "knowledgeIds": ["dongzhou_stage_001"], "digest": "1" * 64},
                "to": {"stageId": "02", "knowledgeIds": ["dongzhou_stage_002"], "digest": "2" * 64},
            },
            "method": "npc_dialog",
            "routeId": "dongzhou_npc_dialog_900001_900002",
            "label": "向导引路",
            "provisionCost": 1,
            "moraleDelta": -4,
            "guideName": "乡民",
        }
        route["receipt"] = campaign_routes.seal_selection(route)
        report["campaignRoute"] = route
        previous_payload = {
            "organization": {
                "members": payload["organization"]["members"],
                "councils": [{
                    "id": "council-1",
                    "stageId": "02",
                    "memberId": "ZuoRu",
                }],
                "mandates": [{
                    "id": "mandate-1",
                    "stageId": "02",
                    "heroId": "ZuoRu",
                    "digest": "a" * 64,
                    "collaboration": {
                        "primaryHeroId": "ZuoRu",
                        "supportHeroId": "SiTu",
                    },
                }],
                "tasks": [{
                    "id": "order-1",
                    "stageId": "02",
                    "assigneeId": "DuBo",
                }],
                "pendingSupport": [{
                    "id": "order-1",
                    "stageId": "02",
                    "memberId": "DuBo",
                    "council": {"id": "council-1"},
                    "mandate": {"id": "mandate-1"},
                }],
                "battleReports": [],
            }
        }
        payload = _seal_battle_reports(
            player_id,
            previous_payload,
            payload,
            campaign_routes=campaign_routes,
            route_required_stages={"02"},
        )
        first = _battle_game_events(
            settings, player_id, payload, "0771-01-01 14:00:00"
        )
        replay = _battle_game_events(
            settings, player_id, payload, "0772-01-01 14:00:00"
        )

        self.assertEqual(first, replay)
        self.assertEqual(
            [event["kind"] for event in first],
            [
                "NPC_BATTLE_OUTCOME",
                "NPC_BATTLE_MEMORY",
                "NPC_BATTLE_OUTCOME",
                "NPC_BATTLE_MEMORY",
                "NPC_BATTLE_OUTCOME",
                "NPC_BATTLE_MEMORY",
            ],
        )
        self.assertEqual(
            {event["payload"]["npc_name"] for event in first},
            {"杜伯", "左儒", "司徒"},
        )
        receipt = payload["organization"]["battleReports"][0]["kernelReceipt"]
        self.assertEqual(receipt["verifiedParticipants"], ["DuBo", "SiTu", "ZuoRu"])
        self.assertEqual(receipt["verifiedSupport"]["mandates"][0]["supportHeroId"], "SiTu")
        outcome = next(
            event["payload"]
            for event in first
            if event["kind"] == "NPC_BATTLE_OUTCOME"
            and event["payload"]["npc_name"] == "左儒"
        )
        detail = outcome["events"][0]
        outcome_entry = next(
            event for event in first if event["kind"] == "NPC_BATTLE_OUTCOME"
        )
        self.assertTrue(outcome_entry["eventId"].startswith("battle-outcome-v3:"))
        self.assertTrue(detail["source_record_id"].startswith("dongzhou-battle-v3:"))
        self.assertEqual(outcome["game_time"], "0771-04-01 14:00:00")
        self.assertEqual(detail["event_type"], "battle_result")
        self.assertEqual(detail["metadata"]["standard_event_authority"], "game_server")
        self.assertEqual(detail["metadata"]["actor_id"], outcome["npc_id"])
        self.assertEqual(
            detail["metadata"]["target_id"],
            str(stable_player_id(settings.ainpc_game_server_id, player_id)),
        )
        self.assertEqual(detail["metadata"]["behavior_parent"], "protect")
        self.assertEqual(detail["metadata"]["behavior_sub"], "support")
        self.assertEqual(detail["metadata"]["result"], "success")
        self.assertIs(detail["metadata"]["result_confirmed"], True)
        self.assertEqual(detail["metadata"]["mandate_ids"], ["mandate-1"])
        self.assertEqual(
            detail["metadata"]["kernel_receipt_digest"],
            payload["organization"]["battleReports"][0]["kernelReceipt"]["digest"],
        )
        self.assertIn("繻葛之战告捷", detail["params"])
        self.assertIn("行军采用向导引路", detail["params"])
        self.assertIn("dongzhou_stage_001、dongzhou_stage_002", detail["params"])
        self.assertEqual(
            detail["metadata"]["campaign_route_id"],
            "dongzhou_npc_dialog_900001_900002",
        )
        self.assertEqual(detail["metadata"]["campaign_route_method"], "npc_dialog")
        self.assertEqual(
            detail["metadata"]["campaign_route_knowledge_ids"],
            ["dongzhou_stage_001", "dongzhou_stage_002"],
        )
        memory = next(
            event["payload"]["messages"][0]["content"]
            for event in first
            if event["kind"] == "NPC_BATTLE_MEMORY"
            and event["payload"]["npc_name"] == "左儒"
        )
        self.assertIn("双史料见证", memory)
        self.assertEqual(detail["source_record_id"], detail["interrupt_trace_id"])
        self.assertNotIn(str(player_id), detail["source_record_id"])

    def test_battle_receipt_rejects_forged_support_and_sealed_report_changes(self) -> None:
        player_id = UUID("00000000-0000-4000-8000-000000000123")
        previous = {
            "organization": {
                "members": [{"id": "DuBo", "name": "Du Bo"}],
                "councils": [],
                "mandates": [],
                "tasks": [],
                "pendingSupport": [],
                "battleReports": [],
            }
        }
        forged = {
            "organization": {
                **previous["organization"],
                "battleReports": [{
                    "id": "battle:forged",
                    "stageId": "01",
                    "won": True,
                    "turns": 1,
                    "ownLosses": 0,
                    "councils": [],
                    "mandates": [],
                    "support": {"orders": [{"id": "missing", "memberId": "DuBo"}]},
                }],
            }
        }
        with self.assertRaisesRegex(BattleReceiptConflict, "battle_order_reference_invalid"):
            _seal_battle_reports(player_id, previous, forged)

        clean = json.loads(json.dumps(forged))
        clean["organization"]["battleReports"][0]["support"]["orders"] = []
        sealed = _seal_battle_reports(player_id, previous, clean)
        changed = json.loads(json.dumps(sealed))
        changed["organization"]["battleReports"][0]["won"] = False
        with self.assertRaisesRegex(BattleReceiptConflict, "battle_report_changed_after_seal"):
            _seal_battle_reports(player_id, sealed, changed)

    def test_battle_receipt_excludes_support_without_server_attestation(self) -> None:
        player_id = UUID("00000000-0000-4000-8000-000000000123")
        council_id = str(uuid4())
        previous = {
            "organization": {
                "members": [{"id": "ZuoRu", "name": "Zuo Ru"}],
                "councils": [{
                    "id": council_id,
                    "stageId": "01",
                    "memberId": "ZuoRu",
                }],
                "mandates": [],
                "tasks": [],
                "pendingSupport": [{
                    "id": "support-1",
                    "stageId": "01",
                    "council": {"id": council_id},
                }],
                "battleReports": [],
            }
        }
        submitted = json.loads(json.dumps(previous))
        submitted["organization"]["pendingSupport"] = []
        submitted["organization"]["battleReports"] = [{
            "id": "battle:unattested",
            "stageId": "01",
            "won": True,
            "turns": 3,
            "ownLosses": 0,
            "councils": [{"id": council_id, "memberId": "ZuoRu"}],
            "mandates": [],
            "support": {"orders": []},
        }]
        sealed = _seal_battle_reports(
            player_id,
            previous,
            submitted,
            {"councils": set(), "mandates": set(), "orders": set()},
        )
        receipt = sealed["organization"]["battleReports"][0]["kernelReceipt"]
        self.assertEqual(receipt["verifiedParticipants"], [])
        self.assertEqual(receipt["verifiedSupport"]["councils"], [])
        self.assertEqual(receipt["rejectedSupport"], [{
            "kind": "council",
            "id": council_id,
            "reason": "server_attestation_missing",
        }])

    def test_battle_receipt_accepts_consumed_support_with_server_attestation(self) -> None:
        player_id = UUID("00000000-0000-4000-8000-000000000123")
        previous = {
            "organization": {
                "members": [
                    {"id": "ZuoRu", "name": "Zuo Ru"},
                    {"id": "SiTu", "name": "Si Tu"},
                    {"id": "DuBo", "name": "Du Bo"},
                ],
                "councils": [{
                    "id": "council-consumed",
                    "stageId": "01",
                    "memberId": "ZuoRu",
                }],
                "mandates": [{
                    "id": "mandate-consumed",
                    "stageId": "01",
                    "heroId": "ZuoRu",
                    "digest": "b" * 64,
                    "collaboration": {
                        "primaryHeroId": "ZuoRu",
                        "supportHeroId": "SiTu",
                    },
                }],
                "tasks": [{
                    "id": "order-consumed",
                    "stageId": "01",
                    "assigneeId": "DuBo",
                }],
                "pendingSupport": [],
                "battleReports": [],
            }
        }
        submitted = json.loads(json.dumps(previous))
        submitted["organization"]["battleReports"] = [{
            "id": "battle:consumed",
            "stageId": "01",
            "won": True,
            "turns": 2,
            "ownLosses": 0,
            "councils": [{"id": "council-consumed", "memberId": "ZuoRu"}],
            "mandates": [{
                "id": "mandate-consumed",
                "heroId": "ZuoRu",
                "digest": "b" * 64,
            }],
            "support": {
                "orders": [{"id": "order-consumed", "memberId": "DuBo"}],
            },
        }]
        sealed = _seal_battle_reports(
            player_id,
            previous,
            submitted,
            {
                "councils": {"council-consumed"},
                "mandates": {"mandate-consumed"},
                "orders": {"order-consumed"},
                "mandateCollaborators": {"mandate-consumed": "SiTu"},
            },
        )
        receipt = sealed["organization"]["battleReports"][0]["kernelReceipt"]
        self.assertEqual(receipt["verifiedParticipants"], ["DuBo", "SiTu", "ZuoRu"])
        self.assertEqual(receipt["rejectedSupport"], [])

    def test_organization_supervision_links_use_only_synced_direct_reports(self) -> None:
        links = _organization_supervision_links(
            {"members": [
                {"heroId": "DuBo", "directManagerHeroId": None},
                {"heroId": "ZuoRu", "directManagerHeroId": "DuBo"},
                {"heroId": "Unknown", "directManagerHeroId": "DuBo"},
            ]},
            [
                {"heroId": "DuBo", "name": "Du Bo", "npcId": "10"},
                {"heroId": "ZuoRu", "name": "Zuo Ru", "npcId": "20"},
            ],
            "court-1",
        )
        self.assertEqual(links, [{
            "heroId": "DuBo",
            "managerHeroId": "",
            "subordinateNpcId": "10",
            "managerNpcId": None,
            "sourceEventId": "orgflow:court-1:supervision:DuBo:none",
        }, {
            "heroId": "ZuoRu",
            "managerHeroId": "DuBo",
            "subordinateNpcId": "20",
            "managerNpcId": "10",
            "sourceEventId": "orgflow:court-1:supervision:ZuoRu:DuBo",
        }])

    def test_evidence_fit_rewards_task_relevant_source_and_council_choice(self) -> None:
        fit = _evidence_task_fit(
            "diplomacy",
            {"tier": "编年史实", "scope": "诸侯交质与盟约"},
            "遣使交涉，再定进退",
            has_search_receipt=True,
        )
        self.assertEqual(fit, {
            "taskType": "diplomacy",
            "factor": 9.0,
            "band": "strong",
            "signals": [
                {"kind": "sourceTier", "label": "编年史实", "factor": 2.0},
                {"kind": "sourceScope", "label": "诸侯", "factor": 2.0},
                {"kind": "councilChoice", "label": "遣使", "factor": 4.0},
                {"kind": "searchReceipt", "label": "verified", "factor": 1.0},
            ],
        })

    def test_sealed_evidence_fit_replaces_legacy_flat_knowledge_bonus(self) -> None:
        task = {"id": "evidence-task", "dueMonth": 2, "knowledgeId": "dongzhou_stage_001"}
        member = {"office": "none", "loyalty": 68, "fatigue": 10}
        baseline = {"assignment": {"readiness": {"score": 65}}}
        weak = {**baseline, "evidenceFit": {"taskType": "intelligence", "factor": 2.0}}
        strong = {**baseline, "evidenceFit": {"taskType": "intelligence", "factor": 9.0}}
        self.assertEqual(
            _organization_task_chance(task, "intelligence", member, strong),
            _organization_task_chance(task, "intelligence", member, weak) + 7,
        )
        self.assertEqual(
            _organization_task_chance(task, "intelligence", member, baseline),
            _organization_task_chance(task, "intelligence", member, weak) + 4,
        )

    def test_sealed_knowledge_mastery_adds_verified_task_chance(self) -> None:
        task = {"id": "mastery-task", "dueMonth": 2, "knowledgeId": "dongzhou_stage_001"}
        member = {"office": "none", "loyalty": 68, "fatigue": 10}
        baseline = {"assignment": {"readiness": {"score": 65}}}
        sealed = {
            **baseline,
            "knowledgeMastery": {
                "state": "SEALED",
                "score": 10,
                "bonus": 3.0,
                "resultDigest": "d" * 64,
            },
        }
        wrong_score = {
            **baseline,
            "knowledgeMastery": {"state": "SEALED", "score": 0},
        }
        self.assertEqual(
            _organization_task_chance(task, "drill", member, sealed),
            _organization_task_chance(task, "drill", member, baseline) + 3,
        )
        self.assertEqual(
            _organization_task_chance(task, "drill", member, wrong_score),
            _organization_task_chance(task, "drill", member, baseline),
        )

    def test_preparation_and_office_fit_materially_change_outcome(self) -> None:
        prepared = {"id": "task-4", "dueMonth": 2, "knowledgeId": "dongzhou_stage_004"}
        unprepared = {**prepared, "knowledgeId": None}
        capable = {"office": "司徒", "loyalty": 80, "fatigue": 5}
        exhausted = {"office": "司马", "loyalty": 35, "fatigue": 95}

        self.assertTrue(_organization_task_succeeds(prepared, "supply", capable))
        self.assertFalse(_organization_task_succeeds(unprepared, "supply", exhausted))

    def test_sealed_ainpc_readiness_materially_changes_task_chance(self) -> None:
        task = {"id": "readiness-task", "dueMonth": 2, "knowledgeId": "dongzhou_stage_001"}
        member = {"office": "司徒", "loyalty": 68, "fatigue": 10}
        steady = {"assignment": {"readiness": {"score": 90}}}
        strained = {"assignment": {"readiness": {"score": 30}}}
        self.assertGreater(
            _organization_task_chance(task, "supply", member, steady),
            _organization_task_chance(task, "supply", member, strained) + 25,
        )
        self.assertEqual(
            _organization_task_chance(task, "supply", member),
            _organization_task_chance(task, "supply", member, {"assignment": {}}),
        )

    def test_sealed_correspondence_adds_task_specific_chance(self) -> None:
        task = {"id": "correspondence-task", "dueMonth": 2, "knowledgeId": "dongzhou_stage_001"}
        member = {"office": "none", "loyalty": 68, "fatigue": 10}
        baseline = {"assignment": {"readiness": {"score": 65}}}
        sealed = {**baseline, "correspondence": {"messageId": "message-1", "digest": "d" * 64}}
        self.assertEqual(
            _organization_task_chance(task, "intelligence", member, sealed),
            _organization_task_chance(task, "intelligence", member, baseline) + 8,
        )
        self.assertEqual(
            _organization_task_chance(task, "supply", member, sealed),
            _organization_task_chance(task, "supply", member, baseline) + 4,
        )

    def test_sealed_emergency_assessment_prioritizes_response(self) -> None:
        task = {"id": "emergency-task", "dueMonth": 2, "knowledgeId": "dongzhou_stage_001"}
        member = {"office": "none", "loyalty": 68, "fatigue": 10}
        baseline = {"assignment": {"readiness": {"score": 65}}}
        urgent = {**baseline, "emergency": {"urgent": True, "score": 0.8}}
        routine = {**baseline, "emergency": {"urgent": False, "score": 0.2}}
        self.assertEqual(
            _organization_task_chance(task, "intelligence", member, urgent),
            _organization_task_chance(task, "intelligence", member, baseline) + 8,
        )
        self.assertEqual(
            _organization_task_chance(task, "supply", member, urgent),
            _organization_task_chance(task, "supply", member, baseline) + 5,
        )
        self.assertEqual(
            _organization_task_chance(task, "patrol", member, routine),
            _organization_task_chance(task, "patrol", member, baseline),
        )

    def test_npc_outcome_event_is_deterministic_and_normalizes_failure(self) -> None:
        outcome = {
            "task_id": "00000000-0000-4000-8000-000000000099",
            "game_server_id": "91001",
            "npc_id": "42",
            "npc_name": "Zuo Ru",
            "game_time": "0771-01-01 14:00:00",
            "task_name": "Supply transport",
            "stage_title": "Eastern Outskirts",
        }
        first = _npc_outcome_event(outcome, "REJECTED")
        replay = _npc_outcome_event(outcome, "FAILED")
        self.assertEqual(
            first["events"][0]["event_id"], replay["events"][0]["event_id"]
        )
        self.assertEqual(first["events"][0]["metadata"]["final_result"], "FAILURE")

        memory = _npc_outcome_memory(outcome, "REJECTED")
        self.assertEqual(memory["messages"][0]["content"], first["events"][0]["params"])
        self.assertEqual(
            memory["messages"][0]["message_id"],
            "dongzhou-org-outcome:00000000-0000-4000-8000-000000000099",
        )
        self.assertTrue(first["events"][0]["interrupt_trace_id"])

    def test_npc_outcome_status_requires_event_and_memory(self) -> None:
        delivered = {"state": "DELIVERED", "attempts": 1, "lastError": None}
        pending = {"state": "PENDING", "attempts": 2, "lastError": "temporary"}
        self.assertEqual(_npc_outcome_status(delivered, None)["state"], "PENDING")
        combined = _npc_outcome_status(delivered, pending)
        self.assertEqual(combined["state"], "PENDING")
        self.assertEqual(combined["attempts"], 3)
        self.assertEqual(combined["lastError"], "temporary")
        self.assertEqual(_npc_outcome_status(delivered, delivered)["state"], "DELIVERED")

    def test_npc_outcome_status_waits_for_authoritative_motivation(self) -> None:
        delivered = {"state": "DELIVERED", "attempts": 1, "lastError": None}
        pending = {"state": "PENDING", "attempts": 2, "lastError": "motivation busy"}
        incomplete = _npc_outcome_status(
            delivered,
            delivered,
            quality=delivered,
            motivation=pending,
            require_quality=True,
            require_motivation=True,
        )
        self.assertEqual(incomplete["state"], "PENDING")
        self.assertEqual(incomplete["lastError"], "motivation busy")
        self.assertEqual(incomplete["motivation"], pending)
        complete = _npc_outcome_status(
            delivered,
            delivered,
            quality=delivered,
            motivation=delivered,
            require_quality=True,
            require_motivation=True,
        )
        self.assertEqual(complete["state"], "DELIVERED")
        self.assertEqual(complete["attempts"], 4)

    def test_nexus_seals_all_four_npc_settlement_parts_deterministically(self) -> None:
        task_id = "00000000-0000-4000-8000-000000000077"
        delivered = {"state": "DELIVERED", "attempts": 1, "lastError": None}
        outcome = {
            "state": "DELIVERED",
            "event": delivered,
            "memory": delivered,
            "quality": delivered,
            "motivation": delivered,
        }
        first = NpcSettlementModule.seal_delivery(task_id, "SUCCESS", outcome)
        replay = NpcSettlementModule.seal_delivery(task_id, "SUCCESS", outcome)
        self.assertEqual(first, replay)
        self.assertEqual(first["state"], "SEALED")
        self.assertEqual(first["kernel"]["module"], "dongzhou_npc_settlement")
        self.assertEqual(len(first["digest"]), 64)
        self.assertEqual(
            set(first["deliveries"]),
            {"event", "memory", "quality", "motivation"},
        )
        support_ids = {
            "event": "npc-outcome-support:" + task_id + ":SiTu",
            "memory": "npc-memory-support:" + task_id + ":SiTu",
            "quality": "npc-quality-support:" + task_id + ":SiTu",
            "motivation": "npc-motivation-support:" + task_id + ":SiTu",
        }
        support = NpcSettlementModule.seal_delivery(
            task_id,
            "SUCCESS",
            outcome,
            event_ids=support_ids,
            participant_hero_id="SiTu",
        )
        self.assertEqual(support["participantHeroId"], "SiTu")
        self.assertEqual(
            {entry["eventId"] for entry in support["deliveries"].values()},
            set(support_ids.values()),
        )
        pending = {**outcome, "motivation": {"state": "PENDING", "attempts": 1}}
        with self.assertRaisesRegex(ValueError, "motivation"):
            NpcSettlementModule.seal_delivery(task_id, "SUCCESS", pending)

    def test_nexus_seals_review_relationship_after_all_three_deliveries(self) -> None:
        task_id = "00000000-0000-4000-8000-000000000077"
        delivered = {"state": "DELIVERED", "attempts": 1, "lastError": None}
        relationship = {
            "npcId": "91001001",
            "targetId": "91001999",
            "affectionType": "appreciation",
            "affectionDelta": 6.0,
            "event": delivered,
            "memory": delivered,
            "affection": delivered,
        }
        event_ids = {
            "event": "settlement-accept:event",
            "memory": "settlement-accept:memory",
            "affection": "settlement-accept:affection",
        }
        first = NpcReviewRelationshipModule.seal_delivery(
            task_id,
            "ACCEPT",
            "a" * 64,
            relationship,
            event_ids=event_ids,
        )
        replay = NpcReviewRelationshipModule.seal_delivery(
            task_id,
            "ACCEPT",
            "a" * 64,
            relationship,
            event_ids=event_ids,
        )
        self.assertEqual(first, replay)
        self.assertEqual(first["state"], "SEALED")
        self.assertEqual(first["kernel"]["module"], "dongzhou_npc_review_relationship")
        self.assertEqual(first["affectionType"], "appreciation")
        self.assertEqual(first["affectionDelta"], 6.0)
        self.assertEqual(len(first["digest"]), 64)
        pending = {
            **relationship,
            "affection": {"state": "PENDING", "attempts": 1},
        }
        with self.assertRaisesRegex(ValueError, "affection"):
            NpcReviewRelationshipModule.seal_delivery(
                task_id,
                "ACCEPT",
                "a" * 64,
                pending,
                event_ids=event_ids,
            )


class UpstreamCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_restart_reconciles_persisted_npc_directory(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            roster = [{"heroId": "DuBo", "name": "Du Bo", "npcId": "42"}]
            await store.upsert_npc_directory(settings.game_server_id, roster)
            upstreams = _NpcRecoveryUpstreams()

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once()

        self.assertEqual(upstreams.registrations, [roster])
        self.assertEqual(upstreams.activations[0][0], roster)
        self.assertEqual(upstreams.activations[0][1], "0771-01-01 14:00:00")
        self.assertTrue(upstreams.activations[0][2].startswith("dongzhou-recovery-"))

    async def test_restart_reactivates_persisted_ready_npc_when_actor_is_offline(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            roster = [{"heroId": "DuBo", "name": "Du Bo", "npcId": "42"}]
            await store.upsert_npc_directory(settings.game_server_id, roster)
            await store.mark_npc_ready(settings.game_server_id, "42", "login-42", 0, 1, "startup-1")
            upstreams = _NpcRecoveryUpstreams()

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once()

        self.assertEqual(upstreams.registrations, [roster])
        self.assertEqual(upstreams.activations[0][0], roster)

    async def test_restart_does_not_reactivate_ready_online_actor(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            roster = [{"heroId": "DuBo", "name": "Du Bo", "npcId": "42"}]
            await store.upsert_npc_directory(settings.game_server_id, roster)
            await store.mark_npc_ready(settings.game_server_id, "42", "login-42", 0, 1, "startup-1")
            upstreams = _NpcRecoveryUpstreams(online_ids={"42"})

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once()

        self.assertEqual(upstreams.registrations, [])
        self.assertEqual(upstreams.activations, [])

    async def test_periodic_recovery_reconciles_org_hierarchy_without_actor_relogin(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
                "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
                "DONGZHOU_ORGFLOW_MANAGER_MEMBER_ID": "00000000-0000-4000-8000-000000000101",
                "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000101,ZuoRu=00000000-0000-4000-8000-000000000102",
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            du_bo = {"heroId": "DuBo", "name": "Du Bo", "npcId": "10"}
            zuo_ru = {"heroId": "ZuoRu", "name": "Zuo Ru", "npcId": "20"}
            await store.upsert_npc_directory(settings.game_server_id, [du_bo, zuo_ru])
            manager_member = settings.orgflow_hero_members["DuBo"]
            subordinate_member = settings.orgflow_hero_members["ZuoRu"]
            roster = {
                "data": {
                    "name": "Dongzhou Court", "state": "ACTIVE", "hierarchy_version": 2,
                    "growth_contribution_points": 0,
                    "positions": [
                        {"position_slot_id": "manager", "position_display_name": "司马", "role_display_name": "manager", "level_key": "L1"},
                        {"position_slot_id": "worker", "position_display_name": "属官", "role_display_name": "worker", "level_key": "L2"},
                    ],
                    "members": [
                        {"member_id": manager_member, "position_slot_id": "manager", "direct_manager_member_id": None, "contribution_balance": 0, "contribution_lifetime_earned": 0, "contribution_lifetime_spent": 0},
                        {"member_id": subordinate_member, "position_slot_id": "worker", "direct_manager_member_id": manager_member, "contribution_balance": 0, "contribution_lifetime_earned": 0, "contribution_lifetime_spent": 0},
                    ],
                }
            }
            upstreams = _NpcRecoveryUpstreams(online_ids={"10", "20"}, roster=roster)

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once()

        self.assertEqual(upstreams.registrations, [])
        self.assertEqual(upstreams.activations, [])
        self.assertEqual(upstreams.supervision, [
            {
                "subordinate_npc_id": "10", "manager_npc_id": None,
                "source_event_id": f"orgflow:{settings.orgflow_org_id}:supervision:DuBo:none",
            },
            {
                "subordinate_npc_id": "20", "manager_npc_id": "10",
                "source_event_id": f"orgflow:{settings.orgflow_org_id}:supervision:ZuoRu:DuBo",
            },
        ])

    async def test_org_hierarchy_outage_does_not_fail_npc_actor_recovery(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
                "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
                "DONGZHOU_ORGFLOW_MANAGER_MEMBER_ID": "00000000-0000-4000-8000-000000000101",
                "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000101",
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            roster = [{"heroId": "DuBo", "name": "Du Bo", "npcId": "42"}]
            await store.upsert_npc_directory(settings.game_server_id, roster)
            upstreams = _NpcRecoveryUpstreams(roster_unavailable=True)

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once(
                force_relogin=True
            )

        self.assertEqual(len(upstreams.activations), 1)
        self.assertEqual(upstreams.activations[0][0], roster)

    async def test_cold_start_reactivates_actor_despite_stale_online_directory_flag(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            await store.start()
            roster = [{"heroId": "DuBo", "name": "Du Bo", "npcId": "42"}]
            await store.upsert_npc_directory(settings.game_server_id, roster)
            upstreams = _NpcRecoveryUpstreams(online_ids={"42"})

            await RuntimeModule(store, upstreams, settings)._reconcile_npcs_once(
                force_relogin=True
            )

        self.assertEqual(upstreams.registrations, [])
        self.assertEqual(upstreams.activations[0][0], roster)

    async def test_orgflow_v1_catalog_fallback_preserves_context_in_brief(self) -> None:
        observed: list[dict[str, object]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            observed.append(__import__("json").loads(request.content))
            if len(observed) == 1:
                return httpx.Response(
                    422,
                    json={"error": {"code": "organization_virtual_task_parameters_invalid"}},
                )
            return httpx.Response(200, json={"data": {"task_id": str(uuid4())}})

        environment = {
            "DONGZHOU_ENV": "development",
            "DONGZHOU_SESSION_SECRET": "s" * 32,
            "DONGZHOU_ORGFLOW_HMAC_SECRET": "o" * 32,
        }
        with patch.dict("os.environ", environment, clear=True):
            settings = Settings.from_env()
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        upstreams = Upstreams(settings, client=client)
        payload = {
            "source": "ORGANIZATION_EVENT",
            "source_event_id": str(uuid4()),
            "parameters": {
                "assignee_hero_id": "ZuoRu",
                "assignee_name": "Zuo Ru",
                "resource_units": 8,
                "stage_id": "01",
                "stage_title": "Eastern Outskirts",
            },
            "brief": "Move provisions.",
        }
        try:
            result = await upstreams.trigger_virtual_task(str(uuid4()), payload)
        finally:
            await client.aclose()
        self.assertIn("task_id", result["data"])
        self.assertEqual(len(observed), 2)
        self.assertEqual(observed[1]["parameters"]["assignee_hero_id"], "unassigned")
        self.assertIn('"assignee_hero_id":"ZuoRu"', observed[1]["brief"])

    def test_production_configuration_fails_closed_and_validates_hero_slots(self) -> None:
        required = {
            "DONGZHOU_ENV": "production",
            "DONGZHOU_PUBLIC_ORIGIN": "https://dongzhou.example.com",
            "DONGZHOU_SESSION_SECRET": "s" * 32,
            "DONGZHOU_ORGFLOW_HMAC_SECRET": "o" * 32,
            "DONGZHOU_AINPC_TOKEN": "a" * 32,
            "DONGZHOU_AINPC_TASK_TOKEN": "t" * 32,
            "DONGZHOU_ORGFLOW_AINPC_TOOLS_TOKEN": "u" * 32,
            "DONGZHOU_KNOWLEDGE_TOKEN": "k" * 32,
            "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000001",
            "DONGZHOU_ORGFLOW_MANAGER_MEMBER_ID": "00000000-0000-4000-8000-000000000004",
            "DONGZHOU_ORGFLOW_HERO_SLOTS": "DuBo=00000000-0000-4000-8000-000000000003",
            "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000004",
        }
        with patch.dict("os.environ", required, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.orgflow_hero_slots["DuBo"], required["DONGZHOU_ORGFLOW_HERO_SLOTS"].split("=")[1])
        self.assertEqual(settings.orgflow_hero_members["DuBo"], required["DONGZHOU_ORGFLOW_HERO_MEMBERS"].split("=")[1])
        with patch.dict("os.environ", {**required, "DONGZHOU_ORGFLOW_HERO_SLOTS": ""}, clear=True):
            with self.assertRaises(RuntimeError):
                Settings.from_env()
        with patch.dict("os.environ", {"DONGZHOU_ENV": "prodution"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DONGZHOU_ENV"):
                Settings.from_env()
        with patch.dict(
            "os.environ",
            {**required, "DONGZHOU_ORGFLOW_HERO_MEMBERS": "ZuoRu=00000000-0000-4000-8000-000000000004"},
            clear=True,
        ):
            with self.assertRaises(RuntimeError):
                Settings.from_env()
        for override, message in (
            ({"DONGZHOU_OFFLINE_KNOWLEDGE": "1"}, "OFFLINE_KNOWLEDGE"),
            ({"DONGZHOU_AINPC_GAME_SERVER_ID": "91002"}, "must match"),
            ({"DONGZHOU_AINPC_TOKEN": ""}, "AINPC_TOKEN"),
            ({"DONGZHOU_ORGFLOW_AINPC_TOOLS_TOKEN": ""}, "ORGFLOW_AINPC_TOOLS_TOKEN"),
            ({"DONGZHOU_KNOWLEDGE_TOKEN": ""}, "KNOWLEDGE_TOKEN"),
            ({"DONGZHOU_KNOWLEDGE_URL": "http://user:secret@knowledge"}, "absolute HTTP"),
        ):
            with self.subTest(override=override), patch.dict(
                "os.environ", {**required, **override}, clear=True
            ):
                with self.assertRaisesRegex(RuntimeError, message):
                    Settings.from_env()

    def test_orgflow_signature_binds_method_path_audience_nonce_and_body(self) -> None:
        body = b'{"source_event_id":"event-1"}'
        headers = sign_orgflow_request(
            method="POST",
            path_and_query="/internal/task",
            audience="org-flow-engine-administration",
            key_id="dongzhou-v1",
            secret="o" * 32,
            body=body,
        )
        material = "\n".join(
            (
                "POST",
                "/internal/task",
                "org-flow-engine-administration",
                "dongzhou-v1",
                headers["X-Org-Service-Time"],
                headers["X-Org-Service-Nonce"],
                hashlib.sha256(body).hexdigest(),
            )
        ).encode("ascii")
        expected = hmac.new(b"o" * 32, material, hashlib.sha256).hexdigest()
        self.assertEqual(headers["X-Org-Service-Signature"], expected)
        self.assertEqual(len(headers["X-Org-Service-Nonce"]), 64)


class AuthenticationRouteTests(unittest.TestCase):
    def test_save_dispatches_participating_npc_battle_outcome_and_memory(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            upstreams = _CapturingUpstreams()
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=upstreams,
            )
            with TestClient(application) as client:
                client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                council_id = str(uuid4())
                council_response = client.post(
                    "/api/dongzhou/v1/npcs/ZuoRu/decisions",
                    json={
                        "client_request_id": council_id,
                        "stage_id": "01",
                        "question": "How should the campaign be supported?",
                        "options": [
                            {"index": 0, "text": "Hold formation"},
                            {"index": 1, "text": "Advance"},
                        ],
                        "topic": "court_decision",
                    },
                )
                self.assertEqual(council_response.status_code, 200, council_response.text)
                prepared = client.put(
                    "/api/dongzhou/v1/save",
                    json={
                        "expected_version": 1,
                        "payload": {
                            "organization": {
                                "month": 1,
                                "members": [
                                    {"id": "ZuoRu", "name": "Zuo Ru"},
                                    {"id": "DuBo", "name": "Du Bo"},
                                ],
                                "tasks": [],
                                "councils": [{
                                    "id": council_id,
                                    "stageId": "01",
                                    "memberId": "ZuoRu",
                                    "question": "How should the campaign be supported?",
                                    "options": ["Hold formation", "Advance"],
                                    "index": 0,
                                    "text": "Hold formation",
                                }],
                                "mandates": [],
                                "pendingSupport": [{
                                    "id": "support-route",
                                    "stageId": "01",
                                    "council": {"id": council_id},
                                }],
                                "battleReports": [],
                            }
                        },
                    },
                )
                self.assertEqual(prepared.status_code, 200, prepared.text)
                response = client.put(
                    "/api/dongzhou/v1/save",
                    json={
                        "expected_version": 2,
                        "payload": {
                            "organization": {
                                "month": 1,
                                "members": [
                                    {"id": "ZuoRu", "name": "左儒"},
                                    {"id": "DuBo", "name": "杜伯"},
                                ],
                                "tasks": [],
                                "councils": [{
                                    "id": council_id,
                                    "stageId": "01",
                                    "memberId": "ZuoRu",
                                    "question": "How should the campaign be supported?",
                                    "options": ["Hold formation", "Advance"],
                                    "index": 0,
                                    "text": "Hold formation",
                                }],
                                "mandates": [],
                                "pendingSupport": [],
                                "battleReports": [{
                                    "id": "battle:01:route-test",
                                    "stageId": "01",
                                    "stageTitle": "繻葛之战",
                                    "won": False,
                                    "turns": 12,
                                    "ownLosses": 2,
                                    "councils": [{"id": council_id, "memberId": "ZuoRu"}],
                                    "mandates": [],
                                    "sources": ["左儒军议"],
                                    "support": {"orders": []},
                                }],
                            }
                        },
                    },
                )
                self.assertEqual(response.status_code, 200, response.text)
                deadline = time.monotonic() + 2
                while len(upstreams.events) < 2 and time.monotonic() < deadline:
                    time.sleep(0.01)

        self.assertEqual(
            {kind for kind, _ in upstreams.events},
            {"NPC_BATTLE_OUTCOME", "NPC_BATTLE_MEMORY"},
        )
        self.assertEqual({payload["npc_name"] for _, payload in upstreams.events}, {"左儒"})
        outcome = next(
            payload
            for kind, payload in upstreams.events
            if kind == "NPC_BATTLE_OUTCOME"
        )
        self.assertEqual(
            outcome["events"][0]["event_type"],
            "battle_result",
        )

    def test_save_excludes_client_only_battle_support_from_npc_events(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            upstreams = _CapturingUpstreams()
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=upstreams,
            )
            fake_council_id = str(uuid4())
            with TestClient(application) as client:
                client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                prepared = client.put(
                    "/api/dongzhou/v1/save",
                    json={
                        "expected_version": 1,
                        "payload": {"organization": {
                            "month": 1,
                            "members": [{"id": "ZuoRu", "name": "Zuo Ru"}],
                            "councils": [{
                                "id": fake_council_id,
                                "stageId": "01",
                                "memberId": "ZuoRu",
                            }],
                            "mandates": [],
                            "tasks": [],
                            "pendingSupport": [{
                                "id": "fake-support",
                                "stageId": "01",
                                "council": {"id": fake_council_id},
                            }],
                            "battleReports": [],
                        }},
                    },
                )
                self.assertEqual(prepared.status_code, 200, prepared.text)
                submitted = client.put(
                    "/api/dongzhou/v1/save",
                    json={
                        "expected_version": 2,
                        "payload": {"organization": {
                            "month": 1,
                            "members": [{"id": "ZuoRu", "name": "Zuo Ru"}],
                            "councils": [{
                                "id": fake_council_id,
                                "stageId": "01",
                                "memberId": "ZuoRu",
                            }],
                            "mandates": [],
                            "tasks": [],
                            "pendingSupport": [],
                            "battleReports": [{
                                "id": "battle:client-only",
                                "stageId": "01",
                                "won": True,
                                "turns": 2,
                                "ownLosses": 0,
                                "councils": [{
                                    "id": fake_council_id,
                                    "memberId": "ZuoRu",
                                }],
                                "mandates": [],
                                "support": {"orders": []},
                            }],
                        }},
                    },
                )
                self.assertEqual(submitted.status_code, 200, submitted.text)
                receipt = submitted.json()["payload"]["organization"]["battleReports"][0]["kernelReceipt"]
                self.assertEqual(receipt["verifiedParticipants"], [])
                self.assertEqual(receipt["rejectedSupport"][0]["id"], fake_council_id)
                time.sleep(0.05)
                self.assertEqual(upstreams.events, [])

    def test_npc_interaction_preference_persists_only_confirmed_state(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            upstreams = _NpcPreferenceUpstreams()
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=upstreams,
            )
            installation_id = uuid4()
            with TestClient(application) as client:
                guest = client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(installation_id)},
                )
                self.assertEqual(guest.status_code, 200)
                player_id = UUID(guest.json()["playerId"])
                response = client.post(
                    "/api/dongzhou/v1/npcs/interaction-preference",
                    json={"enabled": False},
                )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["enabled"])
        self.assertEqual(
            upstreams.calls,
            [(stable_player_id(settings.ainpc_game_server_id, player_id), False)],
        )

    def test_npc_interaction_preference_rejects_mismatched_state(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=_NpcPreferenceUpstreams(applied_enabled=True),
            )
            with TestClient(application) as client:
                client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                response = client.post(
                    "/api/dongzhou/v1/npcs/interaction-preference",
                    json={"enabled": False},
                )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"]["code"],
            "ainpc_interaction_preference_not_applied",
        )

    def test_npc_sync_stays_available_when_org_hierarchy_is_restarting(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
                "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
                "DONGZHOU_ORGFLOW_MANAGER_MEMBER_ID": "00000000-0000-4000-8000-000000000101",
                "DONGZHOU_ORGFLOW_HERO_MEMBERS": "DuBo=00000000-0000-4000-8000-000000000101",
            },
            clear=True,
        ):
            settings = Settings.from_env()
            upstreams = _NpcRecoveryUpstreams(roster_unavailable=True)
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=upstreams,
            )

            with TestClient(application) as client:
                guest = client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                self.assertEqual(guest.status_code, 200)
                response = client.post(
                    "/api/dongzhou/v1/npcs/sync",
                    json={"npcs": [{"hero_id": "DuBo", "name": "Du Bo"}]},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["relationshipSync"],
            {"state": "UNAVAILABLE", "retryable": True},
        )
        self.assertEqual(len(upstreams.activations), 1)

    def test_ainpc_relogin_contract_replays_only_the_requested_static_shard(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            asyncio.run(store.start())
            roster = [
                {"heroId": "A", "name": "A", "npcId": "101"},
                {"heroId": "B", "name": "B", "npcId": "202"},
                {"heroId": "C", "name": "C", "npcId": "303"},
            ]
            asyncio.run(store.upsert_npc_directory(settings.game_server_id, roster))
            upstreams = _NpcRecoveryUpstreams()
            application = build_application(settings, store=store, upstreams=upstreams)
            with TestClient(application) as client:
                response = client.post(
                    "/api/v1/NDLLMAllAILogin",
                    json={"instanceId": 1, "instanceCount": 2, "startupId": "startup-shard-1"},
                )
                self.assertEqual(response.status_code, 200)
                expected = [
                    npc for npc in roster
                    if int.from_bytes(
                        hashlib.sha256(f"{settings.game_server_id}:{npc['npcId']}".encode()).digest(), "big"
                    ) % 2 == 1
                ]
                deadline = time.time() + 2
                while not any(item[2] == "startup-shard-1" for item in upstreams.activations) and time.time() < deadline:
                    time.sleep(0.01)
                replay = next(item for item in upstreams.activations if item[2] == "startup-shard-1")
                self.assertEqual(replay[0], expected)
                self.assertEqual(response.json()["acceptedCount"], len(expected))
                self.assertEqual(response.json()["state"], "ACCEPTED")

                single = client.post(
                    "/api/v1/NDLLMSingleAILogin",
                    json={"gameServerId": settings.game_server_id, "aiId": "202", "requestId": "single-202"},
                )
                self.assertEqual(single.status_code, 200)
                self.assertEqual(single.json()["requestId"], "single-202")
                self.assertEqual(upstreams.activations[-1][0], [roster[1]])

    def test_cookie_session_satisfies_player_dependency(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            upstreams = _BehaviorUpstreams()
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=upstreams,
            )
            with TestClient(application) as client:
                servers = client.post("/api/v1/QueryServers", json={})
                self.assertEqual(servers.status_code, 200)
                self.assertEqual(servers.json()["servers"], [settings.game_server_id])
                self.assertEqual(servers.json()["serverNames"], ["Dongzhou"])

                game_time = client.post(
                    "/api/v1/QueryGameTimeAndTimeScale",
                    json={"serverID": settings.game_server_id},
                )
                self.assertEqual(game_time.status_code, 200)
                self.assertEqual(game_time.json()["virtualTime"], "0771-01-01 14:00:00")

                login_ready = client.post(
                    "/api/v1/ainpc/login-ready",
                    json={
                        "gameServerId": settings.game_server_id,
                        "aiId": "42",
                        "loginRequestId": "round-42",
                        "instanceId": 1,
                        "instanceCount": 6,
                        "startupId": "startup-1",
                    },
                )
                self.assertEqual(login_ready.status_code, 200)
                self.assertEqual(login_ready.json(), {"success": True, "state": "READY"})
                alive = client.post("/api/v2/QueryNDLLMIsAlive", json={"aiId": "42"})
                self.assertEqual(alive.status_code, 200)
                self.assertEqual(alive.json(), {"isAlive": True})
                absent = client.post("/api/v2/QueryNDLLMIsAlive", json={"aiId": "43"})
                self.assertEqual(absent.status_code, 200)
                self.assertEqual(absent.json(), {"isAlive": False})
                online = client.post("/api/v2/QueryNDLLMIsOnline", json={"aiId": "42"})
                self.assertEqual(online.status_code, 200)
                self.assertEqual(online.json(), {"isOnline": True})
                offline = client.post("/api/v2/QueryNDLLMIsOnline", json={"aiId": "43"})
                self.assertEqual(offline.status_code, 200)
                self.assertEqual(offline.json(), {"isOnline": False})

                target_player = client.post(
                    "/api/v2/QueryNDLLMTargetPlayerInfo",
                    json={"aiId": "42", "targetPlayerId": 123},
                )
                self.assertEqual(target_player.status_code, 200)
                self.assertEqual(
                    target_player.json(),
                    {"playerId": 123, "playerName": "东周玩家"},
                )

                tasks = client.post(
                    "/api/v2/QueryNDLLMTaskInfoByStatus",
                    json={"aiId": "42", "queryTaskStatus": "TASK_STATUS_RUNNING"},
                )
                self.assertEqual(tasks.status_code, 200)
                self.assertEqual(tasks.json(), {"taskInfos": []})
                invalid_tasks = client.post(
                    "/api/v2/QueryNDLLMTaskInfoByStatus",
                    json={"aiId": "42", "queryTaskStatus": "TASK_STATUS_COMPLETED"},
                )
                self.assertEqual(invalid_tasks.status_code, 422)

                valid_sleep = client.post(
                    "/api/v2/ValidateBTParams",
                    json={"treeName": "SleepTree", "params": '{"areaID":0}'},
                )
                self.assertEqual(
                    valid_sleep.json(), {"valid": True, "errorMessage": ""}
                )
                invalid_sleep = client.post(
                    "/api/v2/ValidateBTParams",
                    json={"treeName": "SleepTree", "params": '{"areaID":true}'},
                )
                self.assertEqual(invalid_sleep.json()["valid"], False)
                unsupported = client.post(
                    "/api/v2/ValidateBTParams",
                    json={"treeName": "UnknownTree", "params": "{}"},
                )
                self.assertEqual(unsupported.json()["valid"], False)
                valid_duty = client.post(
                    "/api/v2/ValidateBTParams",
                    json={"treeName": "DongzhouDutyTree", "params": "{}"},
                )
                self.assertEqual(valid_duty.json(), {"valid": True, "errorMessage": ""})

                executed = client.post(
                    "/api/v2/ExecuteBehavior",
                    json={
                        "gameServerId": settings.game_server_id,
                        "aiId": "42",
                        "uid": "sleep-action-42",
                        "actionId": "1100028",
                        "actionName": "Reborn",
                        "actionParams": "{}",
                        "duration": 3,
                        "scheduleId": "0",
                    },
                )
                self.assertEqual(executed.status_code, 200)
                self.assertEqual(
                    executed.json(),
                    {"success": True, "accepted": True, "uid": "sleep-action-42"},
                )
                deadline = time.time() + 1
                while not upstreams.action_results and time.time() < deadline:
                    time.sleep(0.01)
                self.assertEqual(
                    upstreams.action_results,
                    [
                        {
                            "game_server_id": settings.game_server_id,
                            "npc_id": "42",
                            "action_uid": "sleep-action-42",
                            "status_code": 2002,
                            "error_code": 0,
                            "status_message": "Dongzhou behavior completed",
                            "error_message": "",
                        }
                    ],
                )
                sleeping_payload = {
                    "gameServerId": settings.game_server_id,
                    "aiId": "42",
                    "uid": "durable-sleep-42",
                    "actionId": "1100034",
                    "actionName": "SleepTree",
                    "actionParams": '{"areaID":0}',
                    "duration": 60,
                }
                sleeping = client.post(
                    "/api/v2/ExecuteBehavior", json=sleeping_payload
                )
                duplicate_sleeping = client.post(
                    "/api/v2/ExecuteBehavior", json=sleeping_payload
                )
                self.assertEqual(sleeping.status_code, 200)
                self.assertEqual(duplicate_sleeping.status_code, 200)
                time.sleep(0.3)
                self.assertEqual(len(upstreams.action_results), 1)

                duty_payload = {
                    "gameServerId": settings.game_server_id,
                    "aiId": "42",
                    "uid": "durable-duty-42",
                    "actionId": "9100199",
                    "actionName": "DongzhouDutyTree",
                    "actionParams": "{}",
                    "duration": 60,
                    "scheduleId": 9100104,
                    "scheduleName": "巡察营垒",
                    "planId": "duty-plan-42",
                    "actionChainId": "duty-chain-42",
                }
                duty = client.post("/api/v2/ExecuteBehavior", json=duty_payload)
                duplicate_duty = client.post("/api/v2/ExecuteBehavior", json=duty_payload)
                self.assertEqual(duty.status_code, 200)
                self.assertEqual(duplicate_duty.status_code, 200)
                invalid_duty = client.post(
                    "/api/v2/ExecuteBehavior",
                    json={**duty_payload, "uid": "wrong-duty-42", "scheduleName": "转运军粮"},
                )
                self.assertEqual(invalid_duty.status_code, 422)
                self.assertEqual(
                    invalid_duty.json()["error"]["code"],
                    "dongzhou_duty_identity_invalid",
                )
                time.sleep(0.3)
                self.assertEqual(len(upstreams.action_results), 1)

                guest = client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                self.assertEqual(guest.status_code, 200)
                status = client.get("/api/dongzhou/v1/integration/status")
                self.assertEqual(status.status_code, 200)
                self.assertEqual(status.json()["mode"], "connected")
                nexus = status.json()["services"]["nexusKernel"]
                self.assertTrue(nexus["online"])
                self.assertEqual(nexus["mode"], "embedded")
                self.assertRegex(nexus["version"], r"^\d+\.\d+\.\d+")

    def test_private_chat_game_server_contract_is_durable_and_complete(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "development",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            asyncio.run(store.start())
            npcs = [
                {"heroId": "Manager", "name": "Manager", "npcId": "101"},
                {"heroId": "Officer", "name": "Officer", "npcId": "202"},
            ]
            asyncio.run(store.upsert_npc_directory(settings.game_server_id, npcs))
            for npc in npcs:
                asyncio.run(
                    store.mark_npc_ready(
                        settings.game_server_id,
                        npc["npcId"],
                        "login-" + npc["npcId"],
                        None,
                        None,
                        "startup-1",
                    )
                )
            upstreams = _CapturingUpstreams()
            application = build_application(settings, store=store, upstreams=upstreams)

            with TestClient(application) as client:
                directory_response = client.post(
                    "/api/v1/QueryNPCS",
                    json={"serverId": settings.game_server_id, "includeOffline": False},
                )
                self.assertEqual(directory_response.status_code, 200)
                self.assertEqual(
                    [(row["id"], row["isOnline"]) for row in directory_response.json()["infos"]],
                    [("101", 1), ("202", 1)],
                )

                started = client.post(
                    "/api/v2/NDLLMChatWithPlayer",
                    json={
                        "aiId": "101",
                        "playerInfo": {
                            "playerId": "202",
                            "playerName": "Officer",
                            "fleetDuty": 0,
                            "fleetId": 0,
                            "guildDuty": 0,
                            "guildId": 0,
                            "pilotLevel": 0,
                            "pkValue": 0,
                            "posX": 0,
                            "posY": 0,
                            "teamMemberNumber": 0,
                        },
                        "topic": "organization-task:test-notification",
                        "isNpc": True,
                        "loginRequestId": "login-101",
                    },
                )
                self.assertEqual(started.status_code, 200)
                self.assertTrue(started.json()["success"])
                deadline = time.time() + 2
                while len(upstreams.events) < 1 and time.time() < deadline:
                    time.sleep(0.02)
                self.assertEqual(upstreams.events[0][0], "CHAT_START")
                chat_event = upstreams.events[0][1]
                self.assertEqual(chat_event["status"], "start")
                self.assertEqual(chat_event["messages"], [])

                missing = client.post(
                    "/api/v2/QueryNDLLMPrivateMessageDelivery",
                    json={
                        "aiId": "101",
                        "chatId": chat_event["chatId"],
                        "taskId": chat_event["taskId"],
                        "messageId": "orgnotice-test-message",
                        "deliveryAttemptId": "attempt-1",
                        "attempt": 1,
                    },
                )
                self.assertEqual(missing.status_code, 200)
                self.assertEqual(missing.json()["status"], "not_delivered")

                delivered = client.post(
                    "/api/v2/NDLLMSendPrivateMessage",
                    json={
                        "aiId": "101",
                        "loginRequestId": "login-101",
                        "chatId": chat_event["chatId"],
                        "taskId": chat_event["taskId"],
                        "data": {
                            "message": {
                                "id": "orgnotice-test-message",
                                "speakerId": "101",
                                "content": "Proceed.",
                                "time": "0771-01-01 14:00:00",
                            },
                            "isFinish": False,
                        },
                        "deliveryAttemptId": "attempt-1",
                        "attempt": 1,
                        "isMinor": False,
                        "needManualTakeover": False,
                        "isNpc": True,
                        "playerInfo": {"playerId": "202", "playerName": "Officer"},
                    },
                )
                self.assertEqual(delivered.status_code, 200)
                self.assertTrue(delivered.json()["success"])
                confirmed = client.post(
                    "/api/v2/QueryNDLLMPrivateMessageDelivery",
                    json={
                        "aiId": "101",
                        "chatId": chat_event["chatId"],
                        "taskId": chat_event["taskId"],
                        "messageId": "orgnotice-test-message",
                        "deliveryAttemptId": "attempt-1",
                        "attempt": 1,
                    },
                )
                self.assertEqual(confirmed.status_code, 200)
                self.assertEqual(confirmed.json()["status"], "delivered")
                deadline = time.time() + 2
                while not any(kind == "DELIVERY_RESULT" for kind, _ in upstreams.events) and time.time() < deadline:
                    time.sleep(0.02)
                receipt = next(payload for kind, payload in upstreams.events if kind == "DELIVERY_RESULT")
                self.assertEqual(receipt["messageId"], "orgnotice-test-message")
                self.assertEqual(receipt["status"], "delivered")
                deadline = time.time() + 2
                while not any(kind == "CHAT_TURN" for kind, _ in upstreams.events) and time.time() < deadline:
                    time.sleep(0.02)
                turn = next(payload for kind, payload in upstreams.events if kind == "CHAT_TURN")
                self.assertEqual(turn["npcId"], "202")
                self.assertEqual(turn["speakerId"], "202")
                self.assertEqual(turn["status"], "inProgress")
                self.assertEqual(turn["messages"][0]["id"], "orgnotice-test-message")

                peer_reply = client.post(
                    "/api/v2/NDLLMSendPrivateMessage",
                    json={
                        "aiId": "202",
                        "loginRequestId": "login-202",
                        "chatId": turn["chatId"],
                        "taskId": turn["taskId"],
                        "deliveryAttemptId": "attempt-peer-1",
                        "attempt": 1,
                        "data": {
                            "message": {
                                "id": "peer-reply-message",
                                "speakerId": "202",
                                "content": "Accepted.",
                                "time": "0771-01-01 14:00:00",
                            },
                            "isFinish": True,
                        },
                        "need_manual_takeover": False,
                        "isMinor": False,
                        "isNpc": True,
                        "playerInfo": {
                            "id": "101",
                            "name": "Manager",
                            "type": "NPC",
                            "speakerSpeed": 6,
                        },
                    },
                )
                self.assertEqual(peer_reply.status_code, 200)
                self.assertTrue(peer_reply.json()["success"])

                legacy = client.post(
                    "/api/v2/NDLLMSendPrivateMessage",
                    json={
                        "aiId": "101",
                        "loginRequestId": "login-101",
                        "chatId": chat_event["chatId"],
                        "taskId": chat_event["taskId"],
                        "data": {
                            "id": "legacy-message",
                            "speakerId": "101",
                            "content": "Legacy reply.",
                        },
                        "isMinor": False,
                        "needManualTakeover": False,
                    },
                )
                self.assertEqual(legacy.status_code, 200)
                self.assertTrue(legacy.json()["success"])

                runtime = client.post(
                    "/api/v2/QueryPrivateChatRuntimeState",
                    json={"aiId": "101", "revealPii": False},
                )
                self.assertEqual(runtime.status_code, 200)
                runtime_body = runtime.json()
                self.assertEqual(runtime_body["waitingReplyCount"], 0)
                self.assertEqual(runtime_body["pendingMessageCount"], 0)
                self.assertEqual(runtime_body["queuedSendCount"], 0)
                self.assertEqual(len(runtime_body["sessions"]), 1)
                self.assertEqual(runtime_body["sessions"][0]["targetId"], "202")
                self.assertEqual(runtime_body["sessions"][0]["chatId"], chat_event["chatId"])
                self.assertFalse(runtime_body["sessions"][0]["isSending"])

                reset = client.post(
                    "/api/v2/ResetPrivateChatRuntimeState",
                    json={
                        "aiId": "101",
                        "targetId": "202",
                        "action": "EPrivateChatRuntimeResetActionClearPending",
                        "confirmReset": True,
                    },
                )
                self.assertEqual(reset.status_code, 200)
                self.assertTrue(reset.json()["success"])
                self.assertEqual(reset.json()["uncancelledSendingCount"], 0)
                self.assertEqual(reset.json()["state"]["sessions"][0]["targetId"], "202")

                pii = client.post(
                    "/api/v2/QueryPrivateChatRuntimeState",
                    json={"aiId": "101", "revealPii": True},
                )
                self.assertEqual(pii.status_code, 422)

    def test_public_message_requires_current_login_and_is_kernel_sealed(self) -> None:
        with TemporaryDirectory() as directory, patch.dict(
            "os.environ",
            {
                "DONGZHOU_ENV": "test",
                "DONGZHOU_WEB_ROOT": directory,
                "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
                "DONGZHOU_ORGFLOW_ORG_ID": "00000000-0000-4000-8000-000000000100",
                "DONGZHOU_ORGFLOW_HERO_MEMBERS": "ZuoRu=00000000-0000-4000-8000-000000000104",
            },
            clear=True,
        ):
            settings = Settings.from_env()
            store = Store(settings.database_path)
            upstreams = _NpcRecoveryUpstreams(roster={"data": {
                "name": "Dongzhou Court", "state": "ACTIVE", "hierarchy_version": 1,
                "growth_contribution_points": 0, "positions": [],
                "members": [{"member_id": "00000000-0000-4000-8000-000000000104", "state": "ACTIVE"}],
            }})
            application = build_application(settings, store=store, upstreams=upstreams)
            with TestClient(application) as client:
                asyncio.run(store.upsert_npc_directory(settings.game_server_id, [{"npcId": "42", "heroId": "ZuoRu", "name": "左儒"}]))
                ready = client.post("/api/v1/ainpc/login-ready", json={
                    "gameServerId": settings.game_server_id,
                    "aiId": "42",
                    "loginRequestId": "round-42",
                })
                self.assertEqual(ready.status_code, 200)
                stale = client.post("/api/v2/NDLLMSendPublicMessage", json={"aiId": "42", "message": "军粮已至。", "loginRequestId": "old-round"})
                self.assertFalse(stale.json()["success"])
                sent = client.post("/api/v2/NDLLMSendPublicMessage", json={"aiId": "42", "message": "军粮已至。", "loginRequestId": "round-42"})
                self.assertEqual(sent.status_code, 200)
                self.assertTrue(sent.json()["success"])
                replay = client.post("/api/v2/NDLLMSendPublicMessage", json={"aiId": "42", "message": "军粮已至。", "loginRequestId": "round-42"})
                self.assertTrue(replay.json()["duplicate"])
                notices = asyncio.run(store.list_public_messages(settings.game_server_id))
                self.assertEqual(len(notices), 1)
                self.assertEqual(notices[0]["heroId"], "ZuoRu")
                self.assertEqual(notices[0]["kernel"], {"module": "dongzhou_npc_public_notice", "moduleVersion": "1.0.0", "state": "SEALED"})
                self.assertRegex(notices[0]["digest"], r"^[0-9a-f]{64}$")
                self.assertEqual(client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code, 200)
                visible = client.get("/api/dongzhou/v1/organization/public-notices")
                self.assertEqual(visible.status_code, 200, visible.text)
                self.assertEqual(visible.json()["notices"][0]["message"], "军粮已至。")


class StoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "gateway.sqlite3")
        await self.store.start()

    async def asyncTearDown(self) -> None:
        self.temp.cleanup()

    async def test_private_chat_reset_releases_only_requested_pair_lease(self) -> None:
        first = {
            "gameServerId": "91001",
            "npcId": "101",
            "taskId": "task-first",
            "chatId": "101_202",
            "topic": "first",
            "participants": [
                {"id": "101", "type": "NPC"},
                {"id": "202", "type": "NPC"},
            ],
        }
        second = {**first, "taskId": "task-second", "topic": "second"}
        await self.store.register_private_chat(first)
        with self.assertRaisesRegex(VersionConflict, "private_chat_pair_busy"):
            await self.store.register_private_chat(second)

        self.assertTrue(
            await self.store.reset_private_chat_pair_lease("91001", "202", "101")
        )
        self.assertFalse(
            await self.store.reset_private_chat_pair_lease("91001", "101", "202")
        )
        await self.store.register_private_chat(second)

    async def test_session_save_version_and_idempotency(self) -> None:
        installation_id = uuid4()
        player_id = await self.store.get_or_create_player(installation_id)
        self.assertEqual(player_id, await self.store.get_or_create_player(installation_id))
        saved = await self.store.write_save(player_id, 1, {"completed": ["01"]})
        self.assertEqual(saved["version"], 2)
        with self.assertRaises(VersionConflict):
            await self.store.write_save(player_id, 1, {})

        request_id = uuid4()
        created, _ = await self.store.begin_request(player_id, request_id, "organization_task", {"type": "supply"})
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            request_id,
            "ACCEPTED",
            {"state": "ACCEPTED", "taskId": "task-1"},
            external_id="task-1",
        )
        created, replay = await self.store.begin_request(player_id, request_id, "organization_task", {"type": "supply"})
        self.assertFalse(created)
        self.assertEqual(replay, {"state": "ACCEPTED", "taskId": "task-1"})
        self.assertTrue(await self.store.cache_external_request_result(
            player_id,
            "task-1",
            "organization_task",
            "terminal",
            {"settlement": {"result": "SUCCESS"}},
        ))
        record = await self.store.read_external_request_record(
            player_id, "task-1", "organization_task"
        )
        self.assertEqual(record["request"], {"type": "supply"})
        self.assertEqual(
            record["response"]["terminal"]["settlement"]["result"],
            "SUCCESS",
        )
        derived_id = "00000000-0000-4000-8000-000000000099"
        derived_payload = {
            "task_type": "supply",
            "derived_from_task_id": "task-1",
        }
        self.assertTrue(
            await self.store.register_derived_external_request(
                player_id,
                derived_id,
                "organization_task",
                derived_payload,
            )
        )
        self.assertFalse(
            await self.store.register_derived_external_request(
                player_id,
                derived_id,
                "organization_task",
                derived_payload,
            )
        )
        self.assertEqual(
            await self.store.read_external_request(
                player_id, derived_id, "organization_task"
            ),
            derived_payload,
        )
        with self.assertRaises(VersionConflict):
            await self.store.begin_request(player_id, request_id, "organization_task", {"type": "drill"})

    async def test_battle_support_attestations_require_server_records(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        council_id = uuid4()
        created, _ = await self.store.begin_request(
            player_id,
            council_id,
            "npc_decision",
            {
                "hero_id": "ZuoRu",
                "stage_id": "01",
                "question": "Hold or advance?",
                "options": [
                    {"index": 0, "text": "Hold"},
                    {"index": 1, "text": "Advance"},
                ],
            },
        )
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            council_id,
            "COMPLETED",
            {
                "state": "COMPLETED",
                "decision": {"data": {"type": "OPTION", "index": 0}},
            },
        )

        mandate_request_id = uuid4()
        mandate_id = f"dongzhou:{player_id}:{mandate_request_id}"
        mandate_digest = "a" * 64
        created, _ = await self.store.begin_request(
            player_id,
            mandate_request_id,
            "court_mandate",
            {"hero_id": "ZuoRu", "stage_id": "01"},
        )
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            mandate_request_id,
            "ISSUED",
            {
                "state": "ISSUED",
                "mandate": {
                    "id": mandate_id,
                    "state": "ISSUED",
                    "heroId": "ZuoRu",
                    "digest": mandate_digest,
                    "collaboration": {
                        "primaryHeroId": "ZuoRu",
                        "supportHeroId": "SiTu",
                    },
                },
            },
            external_id=mandate_id,
        )

        organization_request_id = uuid4()
        remote_task_id = str(uuid4())
        created, _ = await self.store.begin_request(
            player_id,
            organization_request_id,
            "organization_task",
            {"assignee_hero_id": "ZuoRu", "stage_id": "01"},
        )
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            organization_request_id,
            "ACCEPTED",
            {"state": "ACCEPTED", "taskId": remote_task_id},
            external_id=remote_task_id,
        )
        closure = {"state": "SEALED", "digest": "b" * 64}
        await self.store.cache_external_request_result(
            player_id,
            remote_task_id,
            "organization_task",
            "terminal",
            {
                "settlement": {"result": "SUCCESS"},
                "closureReceipt": closure,
            },
        )

        previous = {
            "organization": {
                "councils": [{
                    "id": str(council_id),
                    "stageId": "01",
                    "memberId": "ZuoRu",
                    "question": "Hold or advance?",
                    "options": ["Hold", "Advance"],
                    "index": 0,
                    "text": "Hold",
                }],
                "tasks": [{
                    "id": "local-order-1",
                    "stageId": "01",
                    "assigneeId": "ZuoRu",
                    "remoteResult": remote_task_id,
                    "closureReceipt": closure,
                }]
            }
        }
        submitted = {
            "organization": {
                "battleReports": [{
                    "stageId": "01",
                    "councils": [{"id": str(council_id), "memberId": "ZuoRu"}],
                    "mandates": [{
                        "id": mandate_id,
                        "heroId": "ZuoRu",
                        "digest": mandate_digest,
                    }],
                    "support": {"orders": [{
                        "id": "local-order-1",
                        "memberId": "ZuoRu",
                    }]},
                }]
            }
        }
        attested = await _battle_support_attestations(
            self.store,
            player_id,
            previous,
            submitted,
        )
        self.assertEqual(attested["councils"], {str(council_id)})
        self.assertEqual(attested["mandates"], {mandate_id})
        self.assertEqual(attested["mandateCollaborators"], {mandate_id: "SiTu"})
        self.assertEqual(attested["orders"], {"local-order-1"})

    async def test_explicit_redelivery_requeues_same_completed_game_event(self) -> None:
        payload = {"taskId": "stable-task", "topic": "stable-topic"}
        self.assertTrue(
            await self.store.enqueue_game_event(
                "chat-start:stable", "CHAT_START", payload
            )
        )
        await self.store.finish_game_event("chat-start:stable")
        self.assertEqual(await self.store.pending_game_events(), [])
        self.assertFalse(
            await self.store.enqueue_game_event(
                "chat-start:stable", "CHAT_START", payload
            )
        )
        self.assertTrue(
            await self.store.enqueue_game_event(
                "chat-start:stable",
                "CHAT_START",
                payload,
                requeue_delivered=True,
            )
        )
        events = await self.store.pending_game_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["eventId"], "chat-start:stable")
        self.assertEqual(events[0]["payload"], payload)

    async def test_private_chat_message_and_peer_turn_are_atomic(self) -> None:
        start = {
            "gameServerId": "91001",
            "npcId": "101",
            "source": "91001",
            "speakerId": "101",
            "taskId": "task-atomic",
            "chatId": "101_202",
            "serverName": "Dongzhou",
            "status": "start",
            "currTime": "0771-01-01 14:00:00",
            "topic": "atomic",
            "participants": [
                {"id": "101", "name": "Manager", "type": "NPC"},
                {"id": "202", "name": "Officer", "type": "NPC"},
            ],
            "messages": [],
        }
        wire = {
            "gameServerId": "91001",
            "aiId": "101",
            "chatId": "101_202",
            "taskId": "task-atomic",
            "playerInfo": {"playerId": "202", "playerName": "Officer"},
            "data": {
                "message": {"id": "message-atomic", "speakerId": "101", "content": "Proceed."},
                "isFinish": False,
            },
        }
        with self.assertRaises(VersionConflict):
            await self.store.record_private_message(wire, route_to_npc=True)
        await self.store.register_private_chat(start)
        await self.store.record_private_message(wire, route_to_npc=True)
        retry = {
            **wire,
            "loginRequestId": "new-login-round",
            "deliveryAttemptId": "new-attempt",
            "attempt": 2,
        }
        await self.store.record_private_message(retry, route_to_npc=True)
        events = await self.store.pending_game_events()
        self.assertEqual([(row["kind"], row["payload"]["npcId"]) for row in events], [("CHAT_TURN", "202")])
        recipient_task_id = events[0]["payload"]["taskId"]
        self.assertTrue(recipient_task_id.startswith("peerchat-"))
        self.assertNotEqual(recipient_task_id, wire["taskId"])

        response = {
            **wire,
            "aiId": "202",
            "taskId": recipient_task_id,
            "playerInfo": {"playerId": "101", "playerName": "Manager"},
            "data": {
                "message": {
                    "id": "message-atomic-response",
                    "speakerId": "202",
                    "content": "Accepted.",
                },
                "isFinish": True,
            },
        }
        await self.store.record_private_message(response, route_to_npc=True)
        events = await self.store.pending_game_events()
        self.assertEqual(len(events), 1)
        self.assertFalse(
            any(event["payload"]["npcId"] == "101" for event in events)
        )

    async def test_npc_pair_lease_blocks_reverse_conversation_until_finish(self) -> None:
        def start(owner: str, target: str, task: str) -> dict:
            return {
                "gameServerId": "91001",
                "npcId": owner,
                "source": "91001",
                "speakerId": owner,
                "taskId": task,
                "chatId": f"{owner}_{target}",
                "serverName": "Dongzhou",
                "status": "start",
                "currTime": "0771-01-01 14:00:00",
                "topic": task,
                "participants": [
                    {"id": owner, "name": owner, "type": "NPC"},
                    {"id": target, "name": target, "type": "NPC"},
                ],
                "messages": [],
            }

        await self.store.register_private_chat(start("101", "202", "report"))
        with self.assertRaisesRegex(VersionConflict, "private_chat_pair_busy"):
            await self.store.register_private_chat(start("202", "101", "notification"))

        await self.store.record_private_message(
            {
                "gameServerId": "91001",
                "aiId": "101",
                "chatId": "101_202",
                "taskId": "report",
                "playerInfo": {"playerId": "202", "playerName": "202"},
                "data": {
                    "message": {
                        "id": "report-finished",
                        "speakerId": "101",
                        "content": "Done.",
                    },
                    "isFinish": True,
                },
            }
        )
        await self.store.register_private_chat(start("202", "101", "notification"))

    async def test_sender_finish_does_not_close_recipient_turn(self) -> None:
        start = {
            "gameServerId": "91001",
            "npcId": "101",
            "source": "91001",
            "speakerId": "101",
            "taskId": "task-terminal-message",
            "chatId": "101_202",
            "serverName": "Dongzhou",
            "status": "start",
            "currTime": "0771-01-01 14:00:00",
            "topic": "organization-task:terminal-message",
            "participants": [
                {"id": "101", "name": "Manager", "type": "NPC"},
                {"id": "202", "name": "Officer", "type": "NPC"},
            ],
            "messages": [],
        }
        wire = {
            "gameServerId": "91001",
            "aiId": "101",
            "chatId": "101_202",
            "taskId": "task-terminal-message",
            "playerInfo": {"playerId": "202", "playerName": "Officer"},
            "data": {
                "message": {
                    "id": "message-terminal",
                    "speakerId": "101",
                    "content": "Please confirm this assignment.",
                    "isStopped": True,
                },
                "isFinish": True,
            },
        }
        await self.store.register_private_chat(start)
        await self.store.record_private_message(wire, route_to_npc=True)

        events = await self.store.pending_game_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "CHAT_TURN")
        self.assertEqual(events[0]["payload"]["npcId"], "202")
        self.assertNotEqual(events[0]["payload"]["taskId"], wire["taskId"])
        self.assertEqual(events[0]["payload"]["status"], "inProgress")
        self.assertTrue(events[0]["payload"]["messages"][0]["isStopped"])

    async def test_concurrent_save_has_one_winner(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        results = await asyncio.gather(
            self.store.write_save(player_id, 1, {"writer": 1}),
            self.store.write_save(player_id, 1, {"writer": 2}),
            return_exceptions=True,
        )
        self.assertEqual(sum(isinstance(item, VersionConflict) for item in results), 1)

    async def test_pending_request_is_leased_and_recovers_after_expiry(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        request_id = uuid4()
        created, _ = await self.store.begin_request(player_id, request_id, "npc_decision", {"value": 1})
        self.assertTrue(created)
        created, replay = await self.store.begin_request(player_id, request_id, "npc_decision", {"value": 1})
        self.assertFalse(created)
        self.assertEqual(replay, {"state": "PENDING"})
        with self.store._connection() as db:
            db.execute(
                "UPDATE requests SET updated_at=datetime('now','-3 minutes') WHERE player_id=? AND request_id=?",
                (str(player_id), str(request_id)),
            )
        created, replay = await self.store.begin_request(player_id, request_id, "npc_decision", {"value": 1})
        self.assertTrue(created)
        self.assertIsNone(replay)

    async def test_game_clock_is_monotonic_and_save_cannot_skip_months(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        initial = await self.store.read_game_clock()
        self.assertEqual(initial["virtualTime"], "0771-01-01 14:00:00")

        saved = await self.store.write_save(player_id, 1, {"organization": {"month": 2}})
        self.assertEqual(saved["version"], 2)
        advanced = await self.store.read_game_clock()
        self.assertEqual(advanced["month"], 2)
        self.assertEqual(advanced["virtualTime"], "0771-01-31 14:00:00")

        replayed = await self.store.write_save(player_id, 2, {"organization": {"month": 2}})
        self.assertEqual(replayed["version"], 3)
        self.assertEqual((await self.store.read_game_clock())["month"], 2)

        late_player = await self.store.get_or_create_player(uuid4())
        await self.store.write_save(late_player, 1, {"organization": {"month": 2}})
        self.assertEqual((await self.store.read_game_clock())["month"], 3)

        with self.assertRaises(GameClockConflict):
            await self.store.write_save(player_id, 3, {"organization": {"month": 4}})
        with self.assertRaises(GameClockConflict):
            await self.store.write_save(player_id, 3, {"organization": {"month": 1}})

    async def test_due_remote_task_enqueues_one_authenticated_report_dialogue(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        task_id = uuid4()
        request_id = uuid4()
        created, _ = await self.store.begin_request(
            player_id,
            request_id,
            "organization_task",
            {
                "task_type": "supply",
                "assignee_hero_id": "ZuoRu",
                "stage_title": "Eastern Outskirts",
            },
        )
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            request_id,
            "ACCEPTED",
            {"taskId": str(task_id)},
            external_id=str(task_id),
        )
        settings = Settings(
            environment="test",
            public_origin="http://testserver",
            database_path=self.store.path,
            web_root=self.store.path.parent,
            session_secret="s" * 32,
            orgflow_url="http://org",
            orgflow_hmac_secret="o" * 32,
            orgflow_hmac_key_id="dongzhou-v1",
            orgflow_audience="org-flow-engine-administration",
            orgflow_org_id=str(uuid4()),
            orgflow_manager_member_id="manager-member",
            orgflow_hero_slots={"DuBo": "manager-slot", "ZuoRu": "worker-slot"},
            orgflow_hero_members={"DuBo": "manager-member", "ZuoRu": "worker-member"},
            orgflow_hierarchy_version=1,
            game_server_id="91001",
            ainpc_url="http://ainpc",
            ainpc_token="",
            ainpc_game_server_id=91001,
            knowledge_url="http://knowledge",
            knowledge_token="",
            offline_knowledge_enabled=False,
            knowledge_file=self.store.path,
            ainpc_task_token="t" * 32,
        )
        profile = {
            "organization": {
                "month": 2,
                "members": [{"id": "DuBo", "name": "Du Bo"}],
                "tasks": [
                    {
                        "status": "active",
                        "remoteResult": str(task_id),
                        "dueMonth": 2,
                        "name": "Supply transport",
                    }
                ],
            }
        }
        reports = await _prepare_due_organization_reports(
            self.store, settings, player_id, profile
        )
        await self.store.write_save(player_id, 1, profile, organization_reports=reports)
        reports[0]["content"] = "Changed after the first frozen outcome"
        await self.store.write_save(player_id, 2, profile, organization_reports=reports)
        events = await self.store.pending_game_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "ORG_REPORT_START")
        self.assertEqual(events[0]["payload"]["task_id"], str(task_id))
        self.assertEqual(events[0]["payload"]["purpose"], "report")
        outcome = events[0]["payload"]["npc_outcome"]
        self.assertEqual(outcome["task_id"], str(task_id))
        self.assertEqual(outcome["npc_id"], str(stable_npc_id(91001, "ZuoRu")))
        self.assertIn(outcome["planned_result"], {"SUCCESS", "FAILURE"})
        self.assertEqual(outcome["game_time"], "0771-01-01 14:00:00")
        self.assertNotEqual(events[0]["payload"]["content"], reports[0]["content"])
        frozen_payload = events[0]["payload"]
        await self.store.finish_game_event(events[0]["eventId"])
        await self.store.write_save(player_id, 3, profile, organization_reports=reports)
        self.assertEqual(await self.store.pending_game_events(), [])
        restored = Store(self.store.path)
        await restored.start()
        self.assertEqual(await restored.pending_game_events(), [])
        with restored._connection() as db:
            row = db.execute(
                "SELECT state,payload,attempts FROM game_server_outbox WHERE event_id=?",
                (events[0]["eventId"],),
            ).fetchone()
        self.assertEqual(row["state"], "DELIVERED")
        self.assertEqual(json.loads(row["payload"]), frozen_payload)
        self.assertEqual(row["attempts"], 1)

        terminal_task_id = uuid4()
        terminal_request_id = uuid4()
        created, _ = await self.store.begin_request(
            player_id,
            terminal_request_id,
            "organization_task",
            {
                "task_type": "supply",
                "assignee_hero_id": "ZuoRu",
                "stage_title": "Eastern Outskirts",
            },
        )
        self.assertTrue(created)
        await self.store.finish_request(
            player_id,
            terminal_request_id,
            "ACCEPTED",
            {"taskId": str(terminal_task_id)},
            external_id=str(terminal_task_id),
        )
        terminal_profile = {
            "organization": {
                "month": 2,
                "members": [{"id": "DuBo", "name": "Du Bo"}],
                "tasks": [
                    {
                        "status": "success",
                        "remoteResult": str(terminal_task_id),
                        "dueMonth": 9,
                        "name": "Supply transport",
                        "review": {
                            "state": "ACCEPTED",
                            "finalResult": "PARTIAL",
                        },
                    }
                ],
            }
        }
        terminal_reports = await _prepare_due_organization_reports(
            self.store, settings, player_id, terminal_profile
        )
        self.assertEqual(len(terminal_reports), 1)
        self.assertEqual(
            terminal_reports[0]["npc_outcome"]["planned_result"], "PARTIAL"
        )
        self.assertIn("partly completed", terminal_reports[0]["content"])

    async def test_terminal_report_chains_one_authoritative_npc_outcome(self) -> None:
        class OutcomeUpstreams(_HealthyUpstreams):
            def __init__(self) -> None:
                self.events = []

            async def send_game_event(self, kind, payload):
                self.events.append((kind, payload))
                if kind == "ORG_REPORT_START":
                    return {"record": {"task": {"final_result": "PARTIAL"}}}
                return {"code": 200}

        task_id = str(uuid4())
        outcome = {
            "task_id": task_id,
            "task_type": "supply",
            "task_name": "Supply transport",
            "stage_id": "01",
            "stage_title": "Eastern Outskirts",
            "hero_id": "ZuoRu",
            "npc_id": "42",
            "npc_name": "Zuo Ru",
            "manager_npc_id": "41",
            "game_server_id": "91001",
            "game_time": "0771-01-01 14:00:00",
            "mandate_id": "mandate-1",
            "mandate_digest": "a" * 64,
            "knowledge_id": "dongzhou_stage_001",
            "evidence_source": {"work": "Records of Zhou", "tier": "history"},
            "readiness": {"score": 72, "band": "watch"},
            "planned_result": "SUCCESS",
        }
        await self.store.enqueue_game_event(
            "org-report:" + task_id,
            "ORG_REPORT_START",
            {"task_id": task_id, "content": "report", "npc_outcome": outcome},
        )
        upstreams = OutcomeUpstreams()
        dispatch = asyncio.create_task(
            RuntimeModule(self.store, upstreams, None)._dispatch_game_events()
        )
        try:
            deadline = asyncio.get_running_loop().time() + 2
            while len(upstreams.events) < 5 and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.01)
        finally:
            dispatch.cancel()
            await asyncio.gather(dispatch, return_exceptions=True)
        self.assertEqual(
            {kind for kind, _ in upstreams.events},
            {
                "ORG_REPORT_START", "NPC_TASK_OUTCOME", "NPC_TASK_MEMORY",
                "NPC_QUALITY_SETTLEMENT", "NPC_MOTIVATION_SETTLEMENT",
            },
        )
        payloads = {kind: payload for kind, payload in upstreams.events}
        event = payloads["NPC_TASK_OUTCOME"]
        self.assertEqual(event["npc_id"], "42")
        self.assertEqual(event["events"][0]["metadata"]["final_result"], "PARTIAL")
        self.assertEqual(event["events"][0]["metadata"]["mandate_digest"], "a" * 64)
        self.assertEqual(event["events"][0]["metadata"]["readiness"]["score"], 72)
        self.assertEqual(event["events"][0]["source_record_id"], task_id)
        self.assertGreater(event["events"][0]["event_id"], 0)
        self.assertEqual(
            event["events"][0]["event_id"],
            _npc_outcome_event(outcome, "PARTIAL")["events"][0]["event_id"],
        )
        status = await self.store.game_event_status("npc-outcome:" + task_id)
        self.assertEqual(status["state"], "DELIVERED")
        self.assertEqual(status["attempts"], 1)
        memory = payloads["NPC_TASK_MEMORY"]
        self.assertEqual(memory["messages"][0]["content"], event["events"][0]["params"])
        memory_status = await self.store.game_event_status("npc-memory:" + task_id)
        self.assertEqual(memory_status["state"], "DELIVERED")
        self.assertEqual(memory_status["attempts"], 1)
        quality = payloads["NPC_QUALITY_SETTLEMENT"]
        self.assertEqual(quality["settlement_effect_id"], "dongzhou-org-quality:" + task_id + ":v1")
        self.assertEqual(quality["quality"], "responsibility")
        self.assertEqual(quality["delta"], 0.5)
        self.assertEqual(quality["related_event_id"], str(event["events"][0]["event_id"]))
        quality_status = await self.store.game_event_status("npc-quality:" + task_id)
        self.assertEqual(quality_status["state"], "DELIVERED")
        self.assertEqual(quality_status["attempts"], 1)
        motivation = payloads["NPC_MOTIVATION_SETTLEMENT"]
        self.assertEqual(
            motivation["operation_id"],
            "dongzhou-org-motivation:" + task_id + ":v1",
        )
        self.assertEqual(motivation["motive_updates"], [{
            "motive_name": "再办军粮转运",
            "score": 18.0,
            "reason": "authoritative organization duty result: partial",
        }])
        self.assertEqual(motivation["urgency_level"], "medium")
        self.assertEqual(motivation["extra_data"]["event_id"], str(event["events"][0]["event_id"]))
        motivation_status = await self.store.game_event_status("npc-motivation:" + task_id)
        self.assertEqual(motivation_status["state"], "DELIVERED")
        self.assertEqual(motivation_status["attempts"], 1)
        self.assertEqual(await self.store.pending_game_events(), [])

    async def test_terminal_report_chains_support_officer_four_part_outcome(self) -> None:
        class OutcomeUpstreams(_HealthyUpstreams):
            def __init__(self) -> None:
                self.events = []

            async def send_game_event(self, kind, payload):
                self.events.append((kind, payload))
                return {"record": {"task": {"final_result": "SUCCESS"}}}

        task_id = str(uuid4())
        primary = {
            "task_id": task_id,
            "task_type": "drill",
            "task_name": "Drill formation",
            "stage_id": "01",
            "stage_title": "Eastern Outskirts",
            "hero_id": "ZuoRu",
            "npc_id": "42",
            "npc_name": "Zuo Ru",
            "manager_npc_id": "41",
            "game_server_id": "91001",
            "game_time": "0771-01-01 14:00:00",
            "planned_result": "SUCCESS",
        }
        support = {
            **primary,
            "effect_id": task_id + ":support:SiTu",
            "hero_id": "SiTu",
            "npc_id": "43",
            "npc_name": "Si Tu",
            "collaboration_role": "support",
            "primary_hero_id": "ZuoRu",
        }
        await self.store.enqueue_game_event(
            "org-report:" + task_id,
            "ORG_REPORT_START",
            {
                "task_id": task_id,
                "content": "report",
                "npc_outcome": primary,
                "support_npc_outcomes": [support],
            },
        )
        upstreams = OutcomeUpstreams()
        dispatch = asyncio.create_task(
            RuntimeModule(self.store, upstreams, None)._dispatch_game_events()
        )
        try:
            deadline = asyncio.get_running_loop().time() + 2
            while len(upstreams.events) < 11 and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.01)
        finally:
            dispatch.cancel()
            await asyncio.gather(dispatch, return_exceptions=True)

        self.assertEqual(len(upstreams.events), 11)
        support_events = [
            payload
            for kind, payload in upstreams.events
            if kind == "NPC_TASK_OUTCOME" and payload.get("npc_id") == "43"
        ]
        self.assertEqual(len(support_events), 1)
        metadata = support_events[0]["events"][0]["metadata"]
        self.assertEqual(metadata["collaboration_role"], "support")
        self.assertEqual(metadata["primary_hero_id"], "ZuoRu")
        support_key = task_id + ":SiTu"
        for prefix in (
            "npc-outcome-support:",
            "npc-memory-support:",
            "npc-quality-support:",
            "npc-motivation-support:",
        ):
            status = await self.store.game_event_status(prefix + support_key)
            self.assertEqual(status["state"], "DELIVERED")
        relationship_events = [
            payload
            for kind, payload in upstreams.events
            if kind == "NPC_AFFECTION_SETTLEMENT"
        ]
        self.assertEqual(len(relationship_events), 2)
        self.assertEqual(
            {(item["npc_id"], item["target_id"]) for item in relationship_events},
            {("42", "43"), ("43", "42")},
        )
        self.assertTrue(all(
            item["changes"] == [{
                "affection_type": "friendship",
                "delta": 4.0,
                "reason": "shared organization duty result: success",
                "confidence": 1.0,
            }]
            for item in relationship_events
        ))
        for event in _npc_collaboration_affection_events(
            task_id=task_id,
            game_server_id="91001",
            primary_hero_id="ZuoRu",
            primary_npc_id="42",
            support_hero_id="SiTu",
            support_npc_id="43",
            final_result="SUCCESS",
        ):
            status = await self.store.game_event_status(event["eventId"])
            self.assertEqual(status["state"], "DELIVERED")
        self.assertEqual(await self.store.pending_game_events(), [])

    def test_collaboration_relationship_receipt_requires_both_directions(self) -> None:
        task_id = str(uuid4())
        delivered = {"state": "DELIVERED", "attempts": 1, "lastError": None}
        relationship = {
            "primaryHeroId": "ZuoRu",
            "supportHeroId": "SiTu",
            "affectionType": "respect",
            "affectionDelta": 1.5,
            "primaryToSupport": delivered,
            "supportToPrimary": delivered,
        }
        receipt = NpcCollaborationRelationshipModule.seal_delivery(
            task_id,
            "PARTIAL",
            relationship,
            event_ids={
                "primaryToSupport": "relationship-primary",
                "supportToPrimary": "relationship-support",
            },
        )
        self.assertEqual(receipt["state"], "SEALED")
        self.assertEqual(receipt["affectionType"], "respect")
        self.assertEqual(receipt["affectionDelta"], 1.5)
        self.assertEqual(
            receipt["kernel"]["module"],
            "dongzhou_npc_collaboration_relationship",
        )
        with self.assertRaisesRegex(ValueError, "supportToPrimary"):
            NpcCollaborationRelationshipModule.seal_delivery(
                task_id,
                "PARTIAL",
                {**relationship, "supportToPrimary": {"state": "PENDING", "attempts": 0}},
                event_ids={
                    "primaryToSupport": "relationship-primary",
                    "supportToPrimary": "relationship-support",
                },
            )

    def test_organization_task_trace_projects_safe_fields_and_seals(self) -> None:
        task_id = str(uuid4())
        organization_id = str(uuid4())
        case_id = str(uuid4())
        trace = _organization_task_trace_view(
            {
                "task": {
                    "task_id": task_id,
                    "organization_id": organization_id,
                    "state": "RESULT_CONFIRMATION_PENDING",
                    "version": "7",
                    "supplement_count": 1,
                    "execution_exception": None,
                },
                "confirmations": [
                    {
                        "case_id": case_id,
                        "business_id": task_id,
                        "organization_id": organization_id,
                        "case_type": "TASK_RESULT_CONFIRMATION",
                        "state": "WAITING_CONFIRMATION",
                        "recipient_subject_type": "NPC",
                        "allowed_actions": ["accept", "return_for_supplement"],
                        "deadline_at": "2026-11-13T01:00:00Z",
                        "final_action": None,
                        "messages": [{"body_snapshot": "must not escape"}],
                    }
                ],
                "timeline": [
                    {
                        "sequence_no": "1",
                        "occurred_at": "2026-11-13T00:00:00Z",
                        "entry_type": "TASK_CREATED",
                        "reference_id": task_id,
                        "case_id": None,
                        "state_code": "GENERATED",
                        "reason_code": None,
                    },
                    {
                        "sequence_no": "2",
                        "occurred_at": "2026-11-13T00:30:00Z",
                        "entry_type": "CONFIRMATION_OPENED",
                        "reference_id": case_id,
                        "case_id": case_id,
                        "state_code": "WAITING_CONFIRMATION",
                        "reason_code": None,
                    },
                ],
            },
            task_id=task_id,
            organization_id=organization_id,
        )
        receipt = OrganizationTaskTraceModule.seal(trace)
        self.assertEqual(receipt["state"], "SEALED")
        self.assertEqual(receipt["supplementCount"], 1)
        self.assertEqual(receipt["activeConfirmations"][0]["type"], "TASK_RESULT_CONFIRMATION")
        self.assertNotIn("messages", receipt["activeConfirmations"][0])
        self.assertEqual(receipt["kernel"]["module"], "dongzhou_organization_task_trace")
        with self.assertRaisesRegex(ValueError, "ownership"):
            _organization_task_trace_view(
                {
                    "task": {
                        "task_id": str(uuid4()),
                        "organization_id": organization_id,
                    },
                    "timeline": [],
                },
                task_id=task_id,
                organization_id=organization_id,
            )

    async def test_startup_backfills_missing_npc_memory_once(self) -> None:
        task_id = str(uuid4())
        outcome = {
            "task_id": task_id,
            "game_server_id": "91001",
            "npc_id": "42",
            "npc_name": "Zuo Ru",
            "game_time": "0771-01-01 14:00:00",
            "task_name": "Supply transport",
            "stage_title": "Eastern Outskirts",
        }
        await self.store.enqueue_game_event(
            "npc-outcome:" + task_id,
            "NPC_TASK_OUTCOME",
            _npc_outcome_event(outcome, "SUCCESS"),
        )
        await self.store.finish_game_event("npc-outcome:" + task_id)
        runtime = RuntimeModule(self.store, _HealthyUpstreams(), None)
        await runtime._backfill_npc_memories()
        first = await self.store.pending_game_events()
        self.assertEqual([item["kind"] for item in first], ["NPC_TASK_MEMORY"])
        self.assertEqual(
            first[0]["payload"]["messages"][0]["message_id"],
            "dongzhou-org-outcome:" + task_id,
        )
        await runtime._backfill_npc_memories()
        replay = await self.store.pending_game_events()
        self.assertEqual(replay, first)

    async def test_startup_backfills_missing_npc_quality_once(self) -> None:
        task_id = str(uuid4())
        outcome = {
            "task_id": task_id,
            "task_type": "intelligence",
            "game_server_id": "91001",
            "npc_id": "42",
            "npc_name": "Zuo Ru",
            "game_time": "0771-01-01 14:00:00",
            "task_name": "Scout the road",
            "stage_title": "Eastern Outskirts",
        }
        await self.store.enqueue_game_event(
            "npc-outcome:" + task_id,
            "NPC_TASK_OUTCOME",
            _npc_outcome_event(outcome, "SUCCESS"),
        )
        await self.store.finish_game_event("npc-outcome:" + task_id)
        runtime = RuntimeModule(self.store, _HealthyUpstreams(), None)
        await runtime._backfill_npc_qualities()
        first = await self.store.pending_game_events()
        self.assertEqual([item["kind"] for item in first], ["NPC_QUALITY_SETTLEMENT"])
        self.assertEqual(first[0]["payload"]["quality"], "trustworthiness")
        self.assertEqual(first[0]["payload"]["delta"], 2.0)
        self.assertEqual(
            first[0]["payload"]["settlement_effect_id"],
            "dongzhou-org-quality:" + task_id + ":v1",
        )
        await runtime._backfill_npc_qualities()
        replay = await self.store.pending_game_events()
        self.assertEqual(replay, first)

    async def test_save_and_report_outbox_roll_back_together(self) -> None:
        import sqlite3
        player_id = await self.store.get_or_create_player(uuid4())
        report = {"task_id": str(uuid4()), "content": "first frozen result"}
        with self.store._connection() as db:
            db.execute("CREATE TRIGGER reject_report BEFORE INSERT ON game_server_outbox "
                       "BEGIN SELECT RAISE(ABORT, 'test outbox failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            await self.store.write_save(
                player_id, 1, {"organization": {"month": 2}}, organization_reports=[report]
            )
        self.assertEqual((await self.store.read_save(player_id))["version"], 1)
        self.assertEqual((await self.store.read_game_clock())["month"], 1)
        self.assertEqual(await self.store.pending_game_events(), [])
        with self.store._connection() as db:
            db.execute("DROP TRIGGER reject_report")
        await self.store.write_save(
            player_id, 1, {"organization": {"month": 2}}, organization_reports=[report]
        )
        restored = Store(self.store.path)
        await restored.start()
        self.assertEqual((await restored.read_save(player_id))["version"], 2)
        self.assertEqual((await restored.pending_game_events())[0]["payload"], report)
        with self.assertRaises(VersionConflict):
            await restored.write_save(player_id, 1, {}, organization_reports=[{"task_id": str(uuid4())}])
        self.assertEqual(len(await restored.pending_game_events()), 1)

    async def test_battle_events_commit_with_save_and_do_not_requeue_after_delivery(self) -> None:
        player_id = await self.store.get_or_create_player(uuid4())
        game_events = [
            {
                "eventId": "battle-outcome:stable",
                "kind": "NPC_BATTLE_OUTCOME",
                "payload": {"events": [{"event_id": 1}]},
            },
            {
                "eventId": "battle-memory:stable",
                "kind": "NPC_BATTLE_MEMORY",
                "payload": {"messages": [{"message_id": "stable"}]},
            },
        ]
        await self.store.write_save(
            player_id,
            1,
            {"completed": ["01"]},
            game_events=game_events,
        )
        pending = await self.store.pending_game_events()
        self.assertEqual(
            {event["kind"] for event in pending},
            {"NPC_BATTLE_OUTCOME", "NPC_BATTLE_MEMORY"},
        )
        await self.store.finish_game_event("battle-outcome:stable")
        await self.store.finish_game_event("battle-memory:stable")
        await self.store.write_save(
            player_id,
            2,
            {"completed": ["01"]},
            game_events=game_events,
        )
        self.assertEqual(await self.store.pending_game_events(), [])
        with self.store._connection() as db:
            rows = db.execute(
                "SELECT state,attempts FROM game_server_outbox ORDER BY event_id"
            ).fetchall()
        self.assertEqual(
            [(row["state"], row["attempts"]) for row in rows],
            [("DELIVERED", 1), ("DELIVERED", 1)],
        )
        conflicting = [
            {**game_events[0], "payload": {"result": "changed"}},
            game_events[1],
        ]
        with self.assertRaisesRegex(
            VersionConflict, "game_event_idempotency_conflict"
        ):
            await self.store.write_save(
                player_id,
                3,
                {"completed": ["01", "02"]},
                game_events=conflicting,
            )
        self.assertEqual((await self.store.read_save(player_id))["version"], 3)

    async def test_npc_ready_callback_is_persisted_idempotently(self) -> None:
        await self.store.mark_npc_ready("91001", "42", "round-1", 1, 6, "startup-1")
        await self.store.mark_npc_ready("91001", "42", "round-2", 2, 6, "startup-2")
        runtime = await self.store.read_npc_runtime("91001", "42")
        self.assertIsNotNone(runtime)
        self.assertEqual(runtime["state"], "READY")
        self.assertEqual(runtime["loginRequestId"], "round-2")
        self.assertEqual(runtime["instanceId"], 2)


if __name__ == "__main__":
    unittest.main()
