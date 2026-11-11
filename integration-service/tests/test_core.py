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
    RuntimeModule,
    _evidence_task_fit,
    _npc_outcome_event,
    _npc_outcome_memory,
    _npc_outcome_status,
    _organization_supervision_links,
    _organization_task_chance,
    _prepare_due_organization_reports,
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


class _CapturingUpstreams(_HealthyUpstreams):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    async def send_game_event(self, kind, payload):
        self.events.append((kind, payload))
        return {"code": 200}


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
            application = build_application(
                settings,
                store=Store(settings.database_path),
                upstreams=_HealthyUpstreams(),
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
        await self.store.finish_request(player_id, request_id, "ACCEPTED", {"state": "ACCEPTED"})
        created, replay = await self.store.begin_request(player_id, request_id, "organization_task", {"type": "supply"})
        self.assertFalse(created)
        self.assertEqual(replay, {"state": "ACCEPTED"})
        with self.assertRaises(VersionConflict):
            await self.store.begin_request(player_id, request_id, "organization_task", {"type": "drill"})

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
            while len(upstreams.events) < 3 and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.01)
        finally:
            dispatch.cancel()
            await asyncio.gather(dispatch, return_exceptions=True)
        self.assertEqual(
            {kind for kind, _ in upstreams.events},
            {"ORG_REPORT_START", "NPC_TASK_OUTCOME", "NPC_TASK_MEMORY"},
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
        self.assertEqual(await self.store.pending_game_events(), [])

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
