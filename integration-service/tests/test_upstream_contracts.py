from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from dataclasses import replace
from uuid import UUID, uuid4

import httpx
from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.security import stable_player_id
from dongzhou_integration.upstreams import UpstreamUnavailable, Upstreams


def settings(path: Path) -> Settings:
    return Settings(
        environment="test", public_origin="http://testserver", database_path=path, web_root=path.parent,
        session_secret="s" * 32, orgflow_url="http://org", orgflow_hmac_secret="o" * 32,
        orgflow_hmac_key_id="dongzhou-v1", orgflow_audience="org-flow-engine-administration",
        orgflow_org_id="00000000-0000-0000-0000-000000000001",
        orgflow_manager_member_id="00000000-0000-0000-0000-000000000002",
        orgflow_hero_slots={"DuBo": "00000000-0000-0000-0000-000000000003"},
        orgflow_hero_members={"DuBo": "00000000-0000-0000-0000-000000000004"},
        orgflow_hierarchy_version=7, game_server_id="91001",
        ainpc_url="http://ainpc", ainpc_token="ainpc-token",
        ainpc_game_server_id=91001, knowledge_url="http://knowledge", knowledge_token="knowledge-token",
        offline_knowledge_enabled=False, knowledge_file=path,
        ainpc_task_token="task-token",
    )


class UpstreamContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_roster_route_exposes_mapped_heroes_and_current_player_only(self) -> None:
        class RosterUpstreams:
            player_subject_id = "pending"

            async def health(self):
                return {
                    "orgFlow": {"online": True},
                    "aiNpc": {"online": True},
                    "knowledge": {"online": True},
                }

            async def organization_roster(self, organization_id: str):
                return {
                    "data": {
                        "organization_id": organization_id,
                        "name": "Dongzhou Commandery",
                        "state": "ACTIVE",
                        "hierarchy_version": 7,
                        "growth_contribution_points": 245,
                        "positions": [
                            {
                                "position_slot_id": "00000000-0000-0000-0000-000000000003",
                                "position_display_name": "Marshal",
                                "role_display_name": "Commander",
                                "level_key": "manager",
                            },
                            {
                                "position_slot_id": "00000000-0000-0000-0000-000000000005",
                                "position_display_name": "Court Officer",
                                "role_display_name": "Officer",
                                "level_key": "staff",
                                "state": "OCCUPIED",
                            },
                            {
                                "position_slot_id": "00000000-0000-0000-0000-000000000006",
                                "position_display_name": "Open Court Officer",
                                "role_display_name": "Officer",
                                "level_key": "staff",
                                "state": "OPEN",
                            },
                        ],
                        "members": [
                            {
                                "member_id": "00000000-0000-0000-0000-000000000004",
                                "position_slot_id": "00000000-0000-0000-0000-000000000003",
                                "direct_manager_member_id": None,
                                "contribution_balance": 54,
                                "contribution_lifetime_earned": 80,
                                "contribution_lifetime_spent": 26,
                            },
                            {
                                "member_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                                "subject_type": "PLAYER",
                                "subject_id": self.player_subject_id,
                                "position_slot_id": "00000000-0000-0000-0000-000000000005",
                                "direct_manager_member_id": "00000000-0000-0000-0000-000000000004",
                                "contribution_balance": 9,
                                "contribution_lifetime_earned": 12,
                                "contribution_lifetime_spent": 3,
                            },
                            {
                                "member_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
                                "subject_type": "PLAYER",
                                "subject_id": "unrelated-player",
                                "position_slot_id": "00000000-0000-0000-0000-000000000005",
                                "direct_manager_member_id": None,
                                "contribution_balance": 999,
                                "contribution_lifetime_earned": 999,
                                "contribution_lifetime_spent": 0,
                            },
                        ],
                    }
                }

            async def close(self):
                return None

        with TemporaryDirectory() as directory:
            configured = settings(Path(directory) / "gateway.sqlite3")
            upstreams = RosterUpstreams()
            application = build_application(configured, upstreams=upstreams)
            with TestClient(application) as client:
                session = client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                upstreams.player_subject_id = str(stable_player_id(
                    configured.ainpc_game_server_id,
                    UUID(session.json()["playerId"]),
                ))
                response = client.get("/api/dongzhou/v1/organization/roster")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["organization"]["growthContribution"], 245)
        self.assertEqual(response.json()["members"], [{
            "heroId": "DuBo",
            "office": "Marshal",
            "role": "Commander",
            "level": "manager",
            "directManagerHeroId": None,
            "contributionBalance": 54,
            "lifetimeEarned": 80,
            "lifetimeSpent": 26,
        }])
        self.assertEqual(response.json()["playerMembership"], {
            "office": "Court Officer",
            "role": "Officer",
            "level": "staff",
            "directManagerHeroId": "DuBo",
            "contributionBalance": 9,
            "lifetimeEarned": 12,
            "lifetimeSpent": 3,
        })
        self.assertEqual(response.json()["openPositions"], [{
            "office": "Open Court Officer",
            "role": "Officer",
            "level": "staff",
        }])
        self.assertNotIn("00000000-0000", response.text)
        self.assertNotIn("ffffffff-ffff", response.text)
        self.assertNotIn("unrelated-player", response.text)

    async def test_campaign_route_uses_formal_map_transition_contract(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={"data": {"found": True, "plans": []}})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).campaign_route(900001, 900002)

        self.assertTrue(result["found"])
        self.assertEqual(seen[0].url.path, "/api/v1/map-transition/query")
        self.assertEqual(seen[0].headers["Authorization"], "Bearer knowledge-token")
        self.assertEqual(json.loads(seen[0].content), {
            "from_doc_id": "900001",
            "to_doc_id": "900002",
            "max_depth": 1,
            "methods": ["campaign_progression"],
        })

    async def test_schedule_interruption_uses_formal_ainpc_contract(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={
                "code": 200,
                "message": "accepted",
                "data": {
                    "action": "insert_today",
                    "event_id": "dongzhou-mandate-abc",
                    "schedule_id": "dongzhou-mandate-abc",
                    "schedule_name": "临时军令",
                },
            })

        payload = {
            "event_id": "dongzhou-mandate-abc",
            "event_source": "event_report",
            "event_description": "Urgent court mandate",
            "event_importance": 91.0,
        }
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).interrupt_npc_schedule(42, payload)

        self.assertEqual(result["action"], "insert_today")
        self.assertEqual(result["scheduleName"], "临时军令")
        self.assertEqual(seen[0].url.path, "/api/v1/schedule-interrupts/temp/generate")
        self.assertEqual(seen[0].headers["Authorization"], "Bearer ainpc-token")
        body = json.loads(seen[0].content)
        self.assertEqual(body["game_server_id"], "91001")
        self.assertEqual(body["npc_id"], "42")
        self.assertEqual(body["event_id"], payload["event_id"])

    async def test_health_uses_formal_readiness_endpoints(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append(request.url.path)
            return httpx.Response(200, json={"status": "ready", "ready": True})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).health()

        self.assertTrue(all(item["online"] for item in result.values()))
        self.assertEqual(
            set(paths),
            {"/health/ready", "/readiness", "/health"},
        )

    async def test_health_rejects_false_ainpc_readiness(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"ready": request.url.path != "/readiness"},
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).health()

        self.assertFalse(result["aiNpc"]["online"])
        self.assertTrue(result["orgFlow"]["online"])
        self.assertTrue(result["knowledge"]["online"])

    async def test_npc_state_keeps_persistent_state_when_emotion_actor_is_offline(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.startswith("/api/v1/emotion/current/"):
                return httpx.Response(409, json={"error": {"code": "AINPC_ACTOR_NOT_READY"}})
            if request.url.path.startswith("/api/v1/affection/targets/"):
                return httpx.Response(200, json={"items": [{"target_id": "player-1"}]})
            if request.url.path.startswith("/api/v1/relationship/all/"):
                return httpx.Response(200, json={"items": []})
            return httpx.Response(404, json={"error": {"code": "not_found"}})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            state = await Upstreams(settings(Path("unused")), client).npc_state(42)

        self.assertEqual(state["emotion"], {"available": False})
        self.assertEqual(state["affection"]["items"][0]["target_id"], "player-1")
        self.assertEqual(state["relationships"], {"items": []})

    async def test_online_npc_ids_uses_complete_runtime_snapshot(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={"data": {
                "complete": True,
                "total": 2,
                "items": [
                    {"npc_id": "42", "online": True},
                    {"npc_id": "43", "online": False},
                ],
            }})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            self.assertEqual(await upstreams.online_npc_ids(), {"42"})

        self.assertEqual(seen[0].url.path, "/admin/npc-lifecycle/online-npcs")
        self.assertEqual(seen[0].url.params["game_server_id"], "91001")
        self.assertEqual(seen[0].url.params["page_size"], "100")

    async def test_online_npc_ids_reads_every_snapshot_page(self) -> None:
        seen_pages: list[int] = []

        def handler(request: httpx.Request) -> httpx.Response:
            page = int(request.url.params["page"])
            seen_pages.append(page)
            items = (
                [{"npc_id": str(index), "online": True} for index in range(100)]
                if page == 1
                else [{"npc_id": "100", "online": True}]
            )
            return httpx.Response(200, json={"data": {
                "complete": True,
                "total": 101,
                "items": items,
            }})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            self.assertEqual(len(await upstreams.online_npc_ids()), 101)

        self.assertEqual(seen_pages, [1, 2])

    async def test_online_npc_ids_retries_the_whole_incomplete_snapshot(self) -> None:
        seen_pages: list[int] = []

        def handler(request: httpx.Request) -> httpx.Response:
            page = int(request.url.params["page"])
            seen_pages.append(page)
            complete = len(seen_pages) > 1
            return httpx.Response(200, json={"data": {
                "complete": complete,
                "total": 1,
                "items": [{"npc_id": "42", "online": True}] if complete else [],
            }})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            self.assertEqual(await upstreams.online_npc_ids(), {"42"})

        self.assertEqual(seen_pages, [1, 1])

    async def test_online_npc_ids_rejects_snapshot_after_bounded_retries(self) -> None:
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            return httpx.Response(200, json={"data": {
                "complete": False, "total": 0, "items": [],
            }})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            with self.assertRaisesRegex(
                UpstreamUnavailable, "online actor snapshot is incomplete"
            ):
                await upstreams.online_npc_ids()

        self.assertEqual(attempts, 3)

    def test_failed_decision_is_retryable_with_same_request_id(self) -> None:
        attempts = []

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/callback/npc-dialogue/choice":
                attempts.append(request)
                return httpx.Response(200, json=(
                    {"code": 2, "data": None} if len(attempts) == 1 else
                    {"code": 200, "data": {"index": 0, "type": "OPTION"}}
                ))
            if request.url.path == "/callback/game-reports/dialogue-choice":
                body = json.loads(request.content)
                return httpx.Response(200, json={
                    "code": 200,
                    "data": {
                        "npc_id": body["npc_id"],
                        "count": 1,
                        "inserted_count": 1,
                        "skipped_count": 0,
                    },
                })
            return httpx.Response(200, json={"status": "ok"})

        with TemporaryDirectory() as directory:
            configured = settings(Path(directory) / "db.sqlite")
            upstreams = Upstreams(configured)
            upstreams.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            app = build_application(configured, upstreams=upstreams)
            with TestClient(app) as client:
                self.assertEqual(client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).status_code, 200)
                request = {"client_request_id": str(uuid4()), "question": "Choose", "options": [{"index": 0, "text": "A"}, {"index": 1, "text": "B"}]}
                path = "/api/dongzhou/v1/npcs/DuBo/decisions"
                self.assertEqual(client.post(path, json=request).status_code, 503)
                retried = client.post(path, json=request)
                self.assertEqual(retried.status_code, 200)
                self.assertEqual(retried.json()["state"], "COMPLETED")
                self.assertTrue(client.post(path, json=request).json()["replayed"])
                self.assertEqual(len(attempts), 2)

    def test_dialogue_report_retry_reuses_frozen_decision_and_source_id(self) -> None:
        decisions: list[dict[str, object]] = []
        reports: list[dict[str, object]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            if request.url.path == "/callback/npc-dialogue/choice":
                decisions.append(body)
                return httpx.Response(
                    200,
                    json={"code": 200, "data": {"index": 1, "type": "OPTION"}},
                )
            if request.url.path == "/callback/game-reports/dialogue-choice":
                reports.append(body)
                if len(reports) == 1:
                    return httpx.Response(503, json={"error": {"code": "busy"}})
                return httpx.Response(200, json={
                    "code": 200,
                    "data": {
                        "npc_id": body["npc_id"],
                        "count": 1,
                        "inserted_count": 0,
                        "skipped_count": 1,
                    },
                })
            return httpx.Response(200, json={"status": "ok"})

        with TemporaryDirectory() as directory:
            configured = settings(Path(directory) / "db.sqlite")
            upstreams = Upstreams(configured)
            upstreams.client = httpx.AsyncClient(
                transport=httpx.MockTransport(handler)
            )
            app = build_application(configured, upstreams=upstreams)
            with TestClient(app) as client:
                client.post(
                    "/api/dongzhou/v1/sessions/guest",
                    json={"installation_id": str(uuid4())},
                )
                request = {
                    "client_request_id": str(uuid4()),
                    "stage_id": "01",
                    "question": "Choose",
                    "options": [
                        {"index": 0, "text": "A"},
                        {"index": 1, "text": "B"},
                    ],
                }
                path = "/api/dongzhou/v1/npcs/DuBo/decisions"
                self.assertEqual(client.post(path, json=request).status_code, 503)
                retried = client.post(path, json=request)

        self.assertEqual(retried.status_code, 200)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(len(reports), 2)
        self.assertEqual(
            reports[0]["dialogues"][0]["source_record_id"],
            reports[1]["dialogues"][0]["source_record_id"],
        )
        self.assertEqual(retried.json()["dialogueReceipt"]["skippedCount"], 1)
        self.assertEqual(len(retried.json()["dialogueReceipt"]["digest"]), 64)

    def test_gateway_budget_covers_sequential_upstream_calls(self) -> None:
        with TemporaryDirectory() as directory:
            for timeout in (1.0, 30.0, 120.0):
                configured = replace(settings(Path(directory) / "db.sqlite"), upstream_timeout_seconds=timeout)
                app = build_application(configured, upstreams=object())
                self.assertGreater(app.state.settings.server.request_timeout_seconds, timeout * 2 + 6)

    async def test_stage_knowledge_reads_published_content_and_filters_other_stages(self) -> None:
        seen = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.url.path)
            self.assertEqual(json.loads(request.content), {"ids": ["dongzhou_stage_004"]})
            return httpx.Response(200, json={"data": {"items": [
                {"id": "dongzhou_stage_004", "name": "已发布史料"},
                {"id": "dongzhou_stage_001", "name": "其他战役"},
                {"id": "other_game", "name": "其他游戏"},
            ]}})

        with TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            source = {
                "work": "Records of the Grand Historian",
                "tier": "historical framework",
                "scope": "stage evidence",
                "url": "https://ctext.org/shiji",
            }
            catalog.write_text(json.dumps({"entries": [{"id": "dongzhou_stage_004", "stageId": "03b", "name": "本地旧正文", "sources": [source]}]}), encoding="utf-8")
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                upstreams = Upstreams(settings(catalog), client)
                items = await upstreams.stage_knowledge("03b")
                self.assertEqual(items, [{"id": "dongzhou_stage_004", "name": "已发布史料", "stageId": "03b", "sourceDetails": [source]}])
                self.assertEqual(await upstreams.stage_knowledge("unknown"), [])
        self.assertEqual(seen, ["/api/v1/aku/batch_get"])

    async def test_stage_knowledge_never_falls_back_on_upstream_failure(self) -> None:
        with TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            catalog.write_text(json.dumps({"entries": [{"id": "dongzhou_stage_001", "stageId": "01"}]}), encoding="utf-8")
            async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as client:
                upstreams = Upstreams(settings(catalog), client)
                with self.assertRaises(UpstreamUnavailable):
                    await upstreams.stage_knowledge("01")

    async def test_knowledge_search_filters_other_games_after_broad_recall(self) -> None:
        seen_batch_ids: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/v1/player/search":
                return httpx.Response(200, json={"data": {"channels": {
                    "vector": [{"id": "player_full_1", "score": 0.9, "normalized_score": 1.0}, {"id": "dongzhou_stage_005", "score": 0.8, "normalized_score": 0.8}],
                    "bm25": [{"id": "dongzhou_stage_006", "score": 7.0, "normalized_score": 0.7}],
                    "graph": [{"id": "dongzhou_stage_005", "score": 1.0, "normalized_score": 1.0}],
                }}})
            payload = json.loads(request.content)
            seen_batch_ids.extend(payload["ids"])
            return httpx.Response(200, json={"data": {"items": [
                {"id": "player_full_1", "name": "other game"},
                {"id": "dongzhou_stage_005", "name": "郑伯克段"},
                {"id": "dongzhou_stage_006", "name": "周郑交质"},
            ]}})

        with TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            source = {
                "work": "Zuo Commentary",
                "tier": "historical framework",
                "scope": "diplomatic evidence",
                "url": "https://ctext.org/chun-qiu-zuo-zhuan",
            }
            catalog.write_text(json.dumps({"entries": [
                {"id": "dongzhou_stage_005", "stageId": "04", "sources": [source]},
                {"id": "dongzhou_stage_006", "stageId": "05", "sources": []},
            ]}), encoding="utf-8")
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            upstreams = Upstreams(settings(catalog), client)
            mode, items = await upstreams.search_knowledge("军令", 2)
            await client.aclose()

        self.assertEqual(mode, "connected")
        self.assertEqual([item["id"] for item in items], ["dongzhou_stage_005", "dongzhou_stage_006"])
        self.assertEqual(items[0]["stageId"], "04")
        self.assertEqual(items[0]["sourceDetails"], [source])
        self.assertEqual(items[0]["retrieval"]["strongestChannel"], "graph")
        self.assertTrue(items[0]["retrieval"]["graphRelated"])
        self.assertEqual([item["channel"] for item in items[0]["retrieval"]["channels"]], ["vector", "graph"])
        self.assertEqual(seen_batch_ids, ["dongzhou_stage_005", "player_full_1", "dongzhou_stage_006"])

    async def test_http_business_error_preserves_contract_payload(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(409, json={"error": {"code": "organization_task_conflict", "message": "already active"}})

        with TemporaryDirectory() as directory:
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            upstreams = Upstreams(settings(Path(directory) / "db"), client)
            with self.assertRaises(UpstreamUnavailable) as caught:
                await upstreams.trigger_virtual_task("org-id", {"source_event_id": "stable"})
            await client.aclose()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(caught.exception.error_code, "organization_task_conflict")
        self.assertEqual(caught.exception.response_payload["error"]["message"], "already active")

    async def test_formal_orgflow_and_ainpc_paths(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            if "/virtual-tasks/" in request.url.path:
                return httpx.Response(200, json={"data": {"state": "IN_PROGRESS"}})
            if request.url.path == "/callback/npc-lifecycle/online_state":
                return httpx.Response(200, json={"code": 200, "message": "accepted"})
            if request.url.path == "/internal/v1/organization-tasks/dialogues/report":
                return httpx.Response(200, json={"record": {"state": "COMPLETED"}})
            if request.url.path == "/callback/game-reports/emergency":
                return httpx.Response(200, json={"code": 200, "data": {"accepted": True}})
            if request.url.path == "/callback/game-reports/system-message":
                return httpx.Response(200, json={"code": 200, "data": {"accepted": True}})
            if request.url.path == "/callback/emergency-assessment/evaluate":
                return httpx.Response(200, json={
                    "code": 200,
                    "data": {
                        "results": [True],
                        "scores": [0.875],
                        "interrupt_trace_ids": ["emergency_evaluate:test"],
                    },
                })
            if request.url.path == "/api/v1/personality/profile/91001/42":
                return httpx.Response(200, json={
                    "code": 200,
                    "item": {
                        "game_server_id": "91001",
                        "npc_id": "42",
                        "profile_id": "profile-42",
                        "traits": {"stubborn": 79.0, "smooth": 48.0},
                        "dominant_traits": ["stubborn", "smooth"],
                        "template_source": "identity",
                        "background_note": "fixed profile",
                        "updated_at": "2026-11-07T21:56:40.288000",
                    },
                    "auto_initialized": False,
                })
            if request.url.path == "/api/v1/motivation/snapshot/91001/42":
                return httpx.Response(200, json={
                    "code": 200,
                    "item": {
                        "game_server_id": "91001",
                        "npc_id": "42",
                        "motives": [{"name": "情报核验", "score": 35.0}],
                        "revision": 2,
                        "updated_at": "2026-11-10T08:01:52.476000",
                    },
                    "threshold": 80.0,
                })
            if request.url.path == "/api/v1/quality/profile/91001/42":
                return httpx.Response(200, json={
                    "code": 200,
                    "item": {
                        "game_server_id": "91001",
                        "npc_id": "42",
                        "profile_id": "quality-42",
                        "qualities": {"responsibility": 85.0, "cruelty": 54.0},
                        "dominant_qualities": ["responsibility", "cruelty"],
                        "value_order": ["responsibility", "cruelty"],
                        "template_source": "identity",
                        "background_note": "fixed quality profile",
                        "updated_at": "2026-11-11T00:49:12.279000",
                    },
                    "auto_initialized": request.url.params.get("auto_initialize") == "true",
                })
            if request.url.path == "/api/v1/quality/event-settlement":
                return httpx.Response(200, json={"data": True})
            if request.url.path == "/api/v1/motivation/desire/update":
                body = json.loads(request.content)
                return httpx.Response(200, json={
                    "code": 200,
                    "message": "accepted",
                    "data": {
                        "operation_id": body["operation_id"],
                        "application_status": "applied",
                        "routing_status": "completed",
                        "routed_to": "none",
                    },
                })
            if request.url.path == "/callback/npc-dialogue/choice":
                return httpx.Response(200, json={"code": 200, "data": {"index": 0, "type": "OPTION"}})
            if request.url.path == "/callback/game-reports/dialogue-choice":
                return httpx.Response(200, json={
                    "code": 200,
                    "data": {
                        "npc_id": "42",
                        "count": 1,
                        "inserted_count": 1,
                        "skipped_count": 0,
                    },
                })
            if request.url.path == "/callback/spontaneous-thought/generate":
                body = json.loads(request.content)
                return httpx.Response(200, json={
                    "code": 200,
                    "data": {
                        "npc_id": body["npc_id"],
                        "timestamp": body["current_time"],
                        "route_to": "delayed",
                        "thought": {
                            "thought_description": "先核军情，再定进退",
                            "schedule_category": "军事",
                            "importance": 75,
                            "urgency_level": "urgent_but_lower",
                            "target_motives": [{"motive_name": "情报核验", "score": 5, "reason": "军情未明"}],
                            "reasoning": "当值与史料相合",
                            "has_thought": True,
                            "handler_key": "",
                        },
                    },
                })
            if request.url.path == "/api/v1/relationship/ensure-organization-supervision":
                return httpx.Response(200, json={
                    "code": 200, "created": True, "deactivatedManagerNpcIds": [],
                    "relationshipIds": ["relation-1"],
                })
            if request.url.path == "/ai/npc/player-ai-interaction/sync":
                body = json.loads(request.content)
                return httpx.Response(200, json={
                    "code": 200,
                    "message": "success",
                    "data": {
                        "gameServerId": body["game_server_id"],
                        "playerId": body["player_id"],
                        "enabled": body["enabled"],
                        "source": body["source"],
                        "updatedAt": "2026-11-11T12:00:00Z",
                    },
                })
            return httpx.Response(200, json={"data": {"ok": True}})

        with TemporaryDirectory() as directory:
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            upstreams = Upstreams(settings(Path(directory) / "db"), client)
            await upstreams.trigger_virtual_task("org-id", {"source_event_id": "stable"})
            await upstreams.get_virtual_task("org-id", "task-id")
            await upstreams.organization_roster("org-id")
            await upstreams.organization_inventory("org-id")
            await upstreams.adjust_organization_inventory(
                "org-id",
                {
                    "resource_key": "task.execution",
                    "delta_units": 100,
                    "reason_code": "TASK_SETTLEMENT_ACCEPTED",
                },
                idempotency_key="dongzhou-settlement-reward:settlement-1",
            )
            relationship = await upstreams.ensure_organization_supervision(
                subordinate_npc_id="42",
                manager_npc_id="43",
                source_event_id="orgflow:court:supervision:42:43",
            )
            self.assertTrue(relationship["created"])
            await upstreams.register_npcs([{"npcId": "42", "name": "杜伯"}])
            await upstreams.set_npcs_online(
                [{"npcId": "42", "name": "Test NPC"}],
                "0771-01-01 14:00:00",
                "dongzhou-player",
            )
            await upstreams.request_npc_relogin(42, "dongzhou:test:42")
            preference = await upstreams.sync_player_ai_interaction(42, False)
            self.assertFalse(preference["enabled"])
            await upstreams.npc_state(42)
            await upstreams.npc_schedule(42)
            await upstreams.generate_npc_schedule(42, False)
            await upstreams.evaluate_emergency(
                42, "0771-01-01 14:00:00", "Enemy riders reached the pass."
            )
            await upstreams.choose_dialogue(42, {"dialogues": [{"options": [{"index": 0, "type": "OPTION"}]}], "metadata": {}})
            receipt = await upstreams.report_dialogue_choice(42, {
                "npc_name": "左儒",
                "game_time": "0771-01-01 14:00:00",
                "dialogues": [{"source_record_id": "council-1"}],
            })
            self.assertEqual(receipt["insertedCount"], 1)
            thought = await upstreams.generate_spontaneous_thought(42, {
                "operation_id": "dongzhou-thought:test",
                "npc_context": {"npc_name": "左儒"},
                "current_schedule_description": "检阅军阵",
                "current_schedule_importance": 90,
                "current_time": "0771-01-01 14:00:00",
            })
            self.assertEqual(thought["routeTo"], "delayed")
            self.assertEqual(thought["thought"]["targetMotives"][0]["name"], "情报核验")
            await upstreams.send_game_event(
                "ORG_REPORT_START",
                {
                    "operation_id": "00000000-0000-4000-8000-000000000010",
                    "task_id": "task-id",
                    "game_server_id": "91001",
                },
            )
            await upstreams.send_game_event(
                "NPC_TASK_OUTCOME",
                {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "npc_name": "Test NPC",
                    "game_time": "0771-01-01 14:00:00",
                    "events": [{"event_id": 7001, "event_name": "Task outcome"}],
                },
            )
            await upstreams.send_game_event(
                "NPC_TASK_MEMORY",
                {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "npc_name": "Test NPC",
                    "game_time": "0771-01-01 14:00:00",
                    "messages": [{"timestamp": "0771-01-01 14:00:00", "content": "Task completed", "message_id": "task-id"}],
                },
            )
            await upstreams.send_game_event(
                "NPC_BATTLE_OUTCOME",
                {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "npc_name": "Test NPC",
                    "game_time": "0771-01-01 14:00:00",
                    "events": [{"event_id": 7002, "event_name": "Battle outcome"}],
                },
            )
            await upstreams.send_game_event(
                "NPC_BATTLE_MEMORY",
                {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "npc_name": "Test NPC",
                    "game_time": "0771-01-01 14:00:00",
                    "messages": [{
                        "timestamp": "0771-01-01 14:00:00",
                        "content": "Battle completed",
                        "message_id": "battle-id",
                    }],
                },
            )
            await upstreams.send_game_event(
                "NPC_QUALITY_SETTLEMENT",
                {
                    "settlement_effect_id": "dongzhou-org-quality:task-id:v1",
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "quality": "responsibility",
                    "delta": 2.0,
                    "reason": "authoritative organization duty result: success",
                    "related_event_id": "7001",
                    "confidence": 1.0,
                },
            )
            await upstreams.send_game_event(
                "NPC_MOTIVATION_SETTLEMENT",
                {
                    "npc_id": "42",
                    "operation_id": "dongzhou-org-motivation:task-id:v1",
                    "game_server_id": "91001",
                    "source": "dongzhou_org_task",
                    "urgency_level": "low",
                    "event_description": "Task completed",
                    "event_importance": 35.0,
                    "motive_updates": [{
                        "motive_name": "再办军粮转运",
                        "score": 8.0,
                        "reason": "authoritative organization duty result: success",
                    }],
                    "current_time": "0771-01-01 14:00:00",
                    "extra_data": {"task_id": "task-id"},
                },
            )
            await client.aclose()

        paths = [request.url.path for request in seen]
        self.assertIn("/internal/v1/organization-administration/organizations/org-id/virtual-task-triggers", paths)
        self.assertIn("/internal/v1/organization-administration/organizations/org-id/virtual-tasks/task-id", paths)
        self.assertIn("/internal/v1/organization-administration/organizations/org-id/roster", paths)
        self.assertIn("/internal/v1/organization-administration/organizations/org-id/inventory", paths)
        adjustment_request = next(
            request for request in seen
            if request.url.path.endswith("/inventory-adjustments")
        )
        self.assertEqual(
            adjustment_request.headers.get("idempotency-key"),
            "dongzhou-settlement-reward:settlement-1",
        )
        self.assertEqual(json.loads(adjustment_request.content), {
            "resource_key": "task.execution",
            "delta_units": 100,
            "reason_code": "TASK_SETTLEMENT_ACCEPTED",
        })
        self.assertIn("/ai/npc/register/batch", paths)
        self.assertIn("/callback/npc-lifecycle/online_state", paths)
        self.assertIn("/api/v1/npc-lifecycle/relogin", paths)
        self.assertIn("/ai/npc/player-ai-interaction/sync", paths)
        self.assertIn("/api/v1/motivation/desire/update", paths)
        self.assertIn("/api/v1/emotion/current/91001/42", paths)
        self.assertIn("/api/v1/affection/targets/91001/42", paths)
        self.assertIn("/api/v1/relationship/all/91001/42", paths)
        self.assertIn("/api/v1/relationship/ensure-organization-supervision", paths)
        self.assertIn("/api/v1/personality/profile/91001/42", paths)
        self.assertIn("/api/v1/motivation/snapshot/91001/42", paths)
        self.assertEqual(paths.count("/api/v1/quality/profile/91001/42"), 2)
        self.assertIn("/api/v1/quality/event-settlement", paths)
        self.assertIn("/api/v1/schedule-planning/current", paths)
        self.assertIn("/api/v1/schedule-planning/long-term/generate", paths)
        self.assertIn("/callback/emergency-assessment/evaluate", paths)
        self.assertIn("/callback/npc-dialogue/choice", paths)
        self.assertIn("/callback/game-reports/dialogue-choice", paths)
        self.assertIn("/callback/spontaneous-thought/generate", paths)
        self.assertIn("/internal/v1/organization-tasks/dialogues/report", paths)
        self.assertEqual(paths.count("/callback/game-reports/emergency"), 2)
        self.assertEqual(paths.count("/callback/game-reports/system-message"), 2)
        preference_request = next(
            request for request in seen
            if request.url.path == "/ai/npc/player-ai-interaction/sync"
        )
        self.assertEqual(json.loads(preference_request.content), {
            "game_server_id": "91001",
            "player_id": "42",
            "enabled": False,
            "source": "dongzhou-player-settings",
        })
        org_requests = [request for request in seen if request.url.host == "org"]
        bearer_requests = [request for request in seen if request.url.host != "org"]
        self.assertTrue(all(request.headers.get("x-org-service-signature") for request in org_requests))
        self.assertTrue(all(request.headers.get("authorization", "").startswith("Bearer ") for request in bearer_requests))

    async def test_personality_profile_is_read_only_and_strictly_validated(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={
                "code": 200,
                "item": {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "profile_id": "profile-42",
                    "traits": {"stubborn": 79, "smooth": 48},
                    "dominant_traits": ["stubborn", "smooth"],
                    "template_source": "identity",
                    "background_note": "fixed profile",
                    "updated_at": "2026-11-07T21:56:40.288000",
                },
                "auto_initialized": False,
            })

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).npc_personality(42)
        self.assertTrue(result["available"])
        self.assertEqual(result["dominantTraits"], ["stubborn", "smooth"])
        self.assertEqual(seen[0].url.params.get("auto_initialize"), "false")

        invalid_responses = (
            {
                "code": 200,
                "item": {"game_server_id": "91001", "npc_id": "42", "profile_id": "p", "traits": {"stubborn": 67}, "dominant_traits": ["stubborn"]},
                "auto_initialized": True,
            },
            {
                "code": 200,
                "item": {"game_server_id": "91001", "npc_id": "42", "profile_id": "p", "traits": {"stubborn": 101}, "dominant_traits": ["stubborn"]},
                "auto_initialized": False,
            },
        )
        for response in invalid_responses:
            with self.subTest(response=response):
                async with httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, json=response)
                )) as client:
                    with self.assertRaises(UpstreamUnavailable) as caught:
                        await Upstreams(settings(Path("unused")), client).npc_personality(42)
                    self.assertEqual(caught.exception.error_code, "ainpc_personality_invalid")

    async def test_motivation_snapshot_is_read_only_and_strictly_validated(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={
                "code": 200,
                "item": {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "motives": [{"name": "情报核验", "score": 35}],
                    "revision": 2,
                    "updated_at": "2026-11-10T08:01:52.476000",
                },
                "threshold": 80,
            })

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).npc_motivation(42)
        self.assertEqual(result["motives"], [{"name": "情报核验", "score": 35.0}])
        self.assertEqual(seen[0].method, "GET")
        self.assertEqual(seen[0].url.path, "/api/v1/motivation/snapshot/91001/42")

        invalid_responses = (
            {"code": 200, "item": {"game_server_id": "91001", "npc_id": "wrong", "motives": [], "revision": 0, "updated_at": "now"}, "threshold": 80},
            {"code": 200, "item": {"game_server_id": "91001", "npc_id": "42", "motives": [{"name": "x", "score": True}], "revision": 0, "updated_at": "now"}, "threshold": 80},
        )
        for response in invalid_responses:
            with self.subTest(response=response):
                async with httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, json=response)
                )) as client:
                    with self.assertRaises(UpstreamUnavailable) as caught:
                        await Upstreams(settings(Path("unused")), client).npc_motivation(42)
                    self.assertEqual(caught.exception.error_code, "ainpc_motivation_invalid")

    async def test_quality_profile_supports_explicit_initialization_and_strict_validation(self) -> None:
        seen: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json={
                "code": 200,
                "item": {
                    "game_server_id": "91001",
                    "npc_id": "42",
                    "profile_id": "quality-42",
                    "qualities": {"responsibility": 85, "cruelty": 54},
                    "dominant_qualities": ["responsibility", "cruelty"],
                    "value_order": ["responsibility", "cruelty"],
                    "template_source": "identity",
                    "background_note": "fixed profile",
                    "updated_at": "2026-11-11T00:49:12.279000",
                },
                "auto_initialized": True,
            })

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await Upstreams(settings(Path("unused")), client).npc_quality(
                42, auto_initialize=True
            )
        self.assertEqual(result["qualities"]["responsibility"], 85.0)
        self.assertEqual(result["dominantQualities"], ["responsibility", "cruelty"])
        self.assertTrue(result["autoInitialized"])
        self.assertEqual(seen[0].url.params.get("auto_initialize"), "true")

        invalid = {
            "code": 200,
            "item": {
                "game_server_id": "91001", "npc_id": "42", "profile_id": "quality-42",
                "qualities": {"responsibility": 101},
                "dominant_qualities": ["responsibility"], "value_order": ["responsibility"],
            },
            "auto_initialized": False,
        }
        async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=invalid)
        )) as client:
            with self.assertRaises(UpstreamUnavailable) as caught:
                await Upstreams(settings(Path("unused")), client).npc_quality(42)
        self.assertEqual(caught.exception.error_code, "ainpc_quality_invalid")

    async def test_decision_rejects_business_failures_and_unknown_options(self) -> None:
        payload = {"dialogues": [{"options": [{"index": 0, "type": "OPTION"}]}]}
        for response in (
            {"code": 1, "data": None},
            {"code": 2, "data": None},
            {"code": 200, "data": None},
            {"code": 200, "data": {"index": 99, "type": "OPTION"}},
            {"code": 200, "data": {"index": 0, "type": "INPUT"}},
            {"code": 200, "data": {"index": False, "type": "OPTION"}},
        ):
            with self.subTest(response=response):
                async with httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, json=response)
                )) as client:
                    upstreams = Upstreams(settings(Path("unused")), client)
                    with self.assertRaises(UpstreamUnavailable):
                        await upstreams.choose_dialogue(42, payload)

    async def test_npc_outcome_rejects_business_failure_for_outbox_retry(self) -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"code": 500, "message": "rejected"})
        )) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            with self.assertRaises(UpstreamUnavailable) as caught:
                await upstreams.send_game_event(
                    "NPC_TASK_OUTCOME",
                    {
                        "game_server_id": "91001",
                        "npc_id": "42",
                        "npc_name": "Test NPC",
                        "game_time": "0771-01-01 14:00:00",
                        "events": [],
                    },
                )
        self.assertEqual(caught.exception.error_code, "ainpc_outcome_rejected")

    async def test_report_waits_for_member_acceptance_before_creating_dialogue(self) -> None:
        states = iter(["MEMBER_RESPONSE_PENDING", "IN_PROGRESS"])
        posts = []

        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "GET":
                return httpx.Response(200, json={"data": {"state": next(states)}})
            posts.append(json.loads(request.content))
            return httpx.Response(200, json={"record": {"state": "COMPLETED"}})

        payload = {"task_id": "task-id", "operation_id": "stable-operation"}
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            upstreams = Upstreams(settings(Path("unused")), client)
            with self.assertRaises(UpstreamUnavailable) as caught:
                await upstreams.send_game_event("ORG_REPORT_START", payload)
            self.assertEqual(caught.exception.error_code, "organization_report_not_ready")
            self.assertEqual(posts, [])
            await upstreams.send_game_event("ORG_REPORT_START", payload)
            self.assertEqual(posts, [payload])

    async def test_terminal_organization_tasks_do_not_create_report_dialogues(self) -> None:
        for state in ("SUCCEEDED", "PARTIALLY_COMPLETED", "FAILED", "REJECTED", "CANCELLED", "INVALIDATED"):
            def handler(request: httpx.Request) -> httpx.Response:
                self.assertEqual(request.method, "GET")
                return httpx.Response(200, json={"data": {"state": state}})
            with self.subTest(state=state):
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                    upstreams = Upstreams(settings(Path("unused")), client)
                    result = await upstreams.send_game_event("ORG_REPORT_START", {"task_id": "task-id"})
                    self.assertEqual(result["state"], "TASK_TERMINAL")

    async def test_report_dialogue_remains_retryable_until_terminal(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "GET":
                return httpx.Response(200, json={"data": {"state": "IN_PROGRESS"}})
            return httpx.Response(
                200,
                json={"record": {"state": "AWAITING_CALLBACK", "task": {"state": "IN_PROGRESS"}}},
            )

        with TemporaryDirectory() as directory:
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            upstreams = Upstreams(settings(Path(directory) / "db"), client)
            with self.assertRaises(UpstreamUnavailable) as caught:
                await upstreams.send_game_event(
                    "ORG_REPORT_START",
                    {
                        "operation_id": "00000000-0000-4000-8000-000000000010",
                        "task_id": "task-id",
                        "game_server_id": "91001",
                    },
                )
            await client.aclose()
        self.assertEqual(caught.exception.error_code, "ainpc_report_dialogue_pending")

    async def test_unrecoverable_report_dialogue_failure_is_terminal(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "GET":
                return httpx.Response(200, json={"data": {"state": "IN_PROGRESS"}})
            return httpx.Response(
                200,
                json={"record": {
                    "state": "FAILED",
                    "management": {"can_recover": False, "blocked_reason": "npc_dialogue_task_terminal"},
                }},
            )

        with TemporaryDirectory() as directory:
            client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
            upstreams = Upstreams(settings(Path(directory) / "db"), client)
            result = await upstreams.send_game_event(
                "ORG_REPORT_START",
                {
                    "operation_id": "00000000-0000-4000-8000-000000000010",
                    "task_id": "task-id",
                    "game_server_id": "91001",
                },
            )
            await client.aclose()

        self.assertEqual(result["record"]["state"], "FAILED")


if __name__ == "__main__":
    unittest.main()
