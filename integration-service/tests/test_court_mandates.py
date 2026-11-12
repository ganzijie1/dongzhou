from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.security import stable_npc_id, stable_player_id
from dongzhou_integration.store import Store

MANAGER_NPC_ID = str(stable_npc_id(91001, "DuBo"))
ZUORU_NPC_ID = str(stable_npc_id(91001, "ZuoRu"))
QIN_NPC_ID = str(stable_npc_id(91001, "QinXiangGong"))


class MandateUpstreams:
    def __init__(self) -> None:
        self.triggers: list[dict[str, object]] = []
        self.events: list[tuple[str, dict[str, object]]] = []
        self.inventory_adjustments: list[tuple[str, dict[str, object], str]] = []
        self.growth_credits: list[tuple[str, dict[str, object], str]] = []
        self.knowledge_available = True
        self.assignment_available = True
        self.task_snapshot: dict[str, object] | None = None
        self.thoughts: list[tuple[int, dict[str, object]]] = []
        self.interruptions: list[tuple[int, dict[str, object]]] = []
        self.dialogue_reports: list[tuple[int, dict[str, object]]] = []
        self.memories: dict[int, list[dict[str, object]]] = {}
        self.collaboration_available = False
        self.roster_members: list[dict[str, object]] = []

    async def health(self):
        return {
            "orgFlow": {"online": True},
            "aiNpc": {"online": True},
            "knowledge": {"online": True},
        }

    async def close(self):
        return None

    async def send_game_event(self, kind, payload):
        self.events.append((kind, payload))
        return {"code": 200, "data": {"accepted": True, "taskId": payload.get("taskId")}}

    async def online_npc_ids(self):
        return set()

    async def choose_dialogue(self, npc_id, payload):
        assert npc_id > 0
        return {"code": 200, "data": {"index": 1, "type": "OPTION"}}

    async def report_dialogue_choice(self, npc_id, payload):
        self.dialogue_reports.append((npc_id, payload))
        return {"npcId": str(npc_id), "insertedCount": 1, "skippedCount": 0}

    async def remember_dialogue(self, npc_id, game_time, dialogues):
        dialogue = dialogues[0]
        key = hashlib.sha256(
            f"{npc_id}|{dialogue['dialogue_npc_id']}|{dialogue['question']}|{dialogue['timestamp']}".encode()
        ).hexdigest()
        item = {
            "fact_id": key[:32],
            "idempotency_key": key,
            "source_type": "dialogue_choice",
            "fact_kind": "event",
            "timestamp": dialogue["timestamp"],
            "content": f"与{dialogue['dialogue_npc_name']}对话：{dialogue['question']} -> {dialogue['select']['text']}",
        }
        values = self.memories.setdefault(npc_id, [])
        if not any(value["idempotency_key"] == key for value in values):
            values.insert(0, item)
        return item

    async def npc_memories(self, npc_id, limit=20):
        items = self.memories.get(npc_id, [])[:limit]
        return {"available": True, "items": items, "count": len(items)}

    async def generate_spontaneous_thought(self, npc_id, payload):
        self.thoughts.append((npc_id, payload))
        return {
            "npcId": str(npc_id),
            "timestamp": payload["current_time"],
            "routeTo": "delayed",
            "thought": {
                "description": "先据旧闻整军，再试探东郊虚实",
                "scheduleCategory": "军事",
                "importance": 86.0,
                "urgencyLevel": "urgent_but_lower",
                "targetMotives": [
                    {"name": "情报核验", "score": 8.0, "reason": "东郊军情未明"}
                ],
                "reasoning": "史料与当前职责都要求先核实敌情。",
                "hasThought": True,
            },
        }

    async def npc_state(self, npc_id):
        peer_id = QIN_NPC_ID if str(npc_id) == ZUORU_NPC_ID else ZUORU_NPC_ID
        peer_affection = [{
            "target_id": peer_id,
            "dominant_affection_type": "respect",
            "max_value": 80,
            "affection_count": 2,
        }] if self.collaboration_available else []
        peer_relationships = [{
            "target_id": peer_id,
            "relation_type": "organization",
            "relation_sub": "colleague",
            "is_bilateral": True,
        }] if self.collaboration_available else []
        return {
            "emotion": {"code": 200, "dominant": {"emotion_type": "calm", "intensity": 0.25}},
            "affection": {"code": 200, "items": [{
                "target_id": MANAGER_NPC_ID,
                "dominant_affection_type": "respect",
                "max_value": 33.3,
                "affection_count": 1,
            }, *peer_affection], "total": 1 + len(peer_affection)},
            "relationships": {"code": 200, "items": peer_relationships, "total": len(peer_relationships)},
            "personality": {
                "available": True,
                "profileId": "profile-zuoru",
                "traits": {"stubborn": 79.0, "smooth": 48.0},
                "dominantTraits": ["stubborn", "smooth"],
                "templateSource": "identity",
                "backgroundNote": "fixed profile",
                "updatedAt": "2026-11-07T21:56:40.288000",
            },
            "motivation": {
                "available": True,
                "motives": [{"name": "情报核验", "score": 35.0}],
                "revision": 2,
                "updatedAt": "2026-11-10T08:01:52.476000",
                "threshold": 80.0,
            },
            "memories": await self.npc_memories(npc_id),
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

    async def npc_quality(self, npc_id, *, auto_initialize=False):
        assert npc_id > 0
        assert auto_initialize is True
        return {
            "available": True,
            "profileId": "quality-zuoru",
            "qualities": {
                "responsibility": 85.0,
                "cruelty": 54.0,
            },
            "dominantQualities": ["responsibility", "cruelty"],
            "valueOrder": ["responsibility", "cruelty"],
            "templateSource": "identity",
            "backgroundNote": "fixed quality profile",
            "updatedAt": "2026-11-11T00:49:12.279000",
            "autoInitialized": False,
        }

    async def evaluate_emergency(self, npc_id, timestamp, description):
        assert npc_id > 0
        assert timestamp
        assert description
        return {
            "urgent": True,
            "score": 81.25,
            "interruptTraceId": "emergency_evaluate:test-trace",
        }

    async def interrupt_npc_schedule(self, npc_id, payload):
        self.interruptions.append((npc_id, payload))
        return {
            "action": "insert_today",
            "eventId": payload["event_id"],
            "scheduleId": payload["event_id"],
            "scheduleName": "临时军令",
            "duplicate": len(self.interruptions) > 1,
            "reason": None,
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

    async def search_knowledge(self, query, limit):
        return "connected", [{
            "id": "dongzhou_stage_001",
            "stageId": "01",
            "name": "东郊旧闻",
            "summary": "杜伯之谏与东郊军情。",
            "sourceDetails": [{
                "work": "《史记·周本纪》",
                "tier": "史实骨架",
                "scope": "千亩之败与周宣王晚年",
                "url": "https://ctext.org/shiji/zhou-ben-ji",
            }],
            "retrieval": {
                "aggregateScore": 0.47,
                "strongestChannel": "graph",
                "graphRelated": True,
                "channels": [
                    {"channel": "graph", "score": 1.0, "normalizedScore": 1.0, "rank": 1},
                    {"channel": "bm25", "score": 7.0, "normalizedScore": 0.8, "rank": 2},
                ],
            },
        }]

    async def trigger_virtual_task(self, organization_id, payload):
        self.triggers.append(payload)
        return {"data": {"task_id": "00000000-0000-0000-0000-000000000099"}}

    async def organization_roster(self, organization_id):
        return {
            "data": {
                "organization_id": organization_id,
                "game_server_id": "91001",
                "name": "Dongzhou Court",
                "state": "ACTIVE",
                "hierarchy_version": 8,
                "growth_contribution_points": 0,
                "positions": [],
                "members": self.roster_members,
            }
        }

    async def get_virtual_task(self, organization_id, task_id):
        if self.task_snapshot is not None:
            return {"data": self.task_snapshot}
        return {
            "data": {
                "task_id": task_id,
                "organization_id": organization_id,
                "state": "IN_PROGRESS",
                "final_result": None,
                "contribution_eligible": True,
                "responsible_member_id": "00000000-0000-0000-0000-000000000004",
                "position_slot_id": "00000000-0000-0000-0000-000000000003",
                "version": "2",
            }
        }

    async def adjust_organization_inventory(
        self, organization_id, payload, *, idempotency_key
    ):
        self.inventory_adjustments.append(
            (organization_id, dict(payload), idempotency_key)
        )
        return {
            "data": {
                "entry_id": "00000000-0000-4000-8000-000000000088",
                "organization_id": organization_id,
                "game_server_id": "91001",
                "resource_key": payload["resource_key"],
                "reason_code": payload["reason_code"],
                "delta_units": payload["delta_units"],
                "balance_after": payload["delta_units"],
                "account_version_after": 1,
                "inventory_revision_after": 1,
            }
        }

    async def credit_organization_growth(
        self, organization_id, payload, *, idempotency_key
    ):
        self.growth_credits.append(
            (organization_id, dict(payload), idempotency_key)
        )
        return {
            "data": {
                "organization_id": organization_id,
                "game_server_id": "91001",
                "contribution_points": 100,
                "version": 1,
            }
        }


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
        orgflow_hero_slots={
            "DuBo": "00000000-0000-0000-0000-000000000005",
            "ZuoRu": "00000000-0000-0000-0000-000000000003",
        },
        orgflow_hero_members={
            "DuBo": "00000000-0000-0000-0000-000000000002",
            "ZuoRu": "00000000-0000-0000-0000-000000000004",
            "QinXiangGong": "00000000-0000-0000-0000-000000000006",
        },
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


def start_session(client: TestClient, installation_id: str | None = None) -> str:
    installation_id = installation_id or str(uuid4())
    response = client.post(
        "/api/dongzhou/v1/sessions/guest",
        json={"installation_id": installation_id},
    )
    assert response.status_code == 200
    return installation_id


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


def approve_mandate(client: TestClient, draft_response) -> dict[str, object]:
    draft = draft_response.json()
    mandate_id = draft["mandate"]["id"]
    approved = client.post(
        f"/api/dongzhou/v1/court/mandates/{mandate_id}/resume",
        json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
    )
    assert approved.status_code == 200
    assert approved.json()["state"] == "ISSUED"
    return approved.json()["mandate"]


def schedule_mandate(client: TestClient, mandate: dict[str, object]) -> dict[str, object]:
    scheduled = client.post(
        f"/api/dongzhou/v1/court/mandates/{mandate['id']}/schedule",
        json={
            "client_request_id": str(uuid4()),
            "mandate_digest": mandate["digest"],
        },
    )
    assert scheduled.status_code == 200, scheduled.text
    return scheduled.json()["scheduleReceipt"]


def test_collaborative_mandate_seals_roster_relationships_and_both_schedules() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        upstreams.collaboration_available = True
        upstreams.roster_members = [
            {"member_id": "00000000-0000-0000-0000-000000000004", "state": "ACTIVE"},
            {"member_id": "00000000-0000-0000-0000-000000000006", "state": "ACTIVE"},
        ]
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            body = {
                **mandate_body(council_id),
                "support_hero_id": "QinXiangGong",
            }
            drafted = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert drafted.status_code == 200, drafted.text
            collaboration = drafted.json()["mandate"]["collaboration"]
            assert collaboration["primaryHeroId"] == "ZuoRu"
            assert collaboration["supportHeroId"] == "QinXiangGong"
            assert collaboration["primaryNpcId"] == ZUORU_NPC_ID
            assert collaboration["supportNpcId"] == QIN_NPC_ID
            assert collaboration["supportAssignment"]["heroId"] == "QinXiangGong"
            assert collaboration["factor"] > 0
            assert collaboration["score"] == round(50 + collaboration["factor"] * 5)
            assert drafted.json()["mandate"]["kernel"]["moduleVersion"] == "1.9.0"

            mandate = approve_mandate(client, drafted)
            scheduled = client.post(
                f"/api/dongzhou/v1/court/mandates/{mandate['id']}/schedule",
                json={
                    "client_request_id": str(uuid4()),
                    "mandate_digest": mandate["digest"],
                },
            )
            assert scheduled.status_code == 200, scheduled.text
            result = scheduled.json()
            assert result["scheduleReceipt"]["heroId"] == "ZuoRu"
            assert result["scheduleReceipt"]["role"] == "primary"
            assert result["supportScheduleReceipt"]["heroId"] == "QinXiangGong"
            assert result["supportScheduleReceipt"]["role"] == "support"
            assert result["supportScheduleReceipt"]["eventId"].startswith(
                "dongzhou-mandate-support-"
            )
            assert len(upstreams.interruptions) == 2
            assert upstreams.interruptions[0][1]["raw_data"]["collaboration_role"] == "primary"
            assert upstreams.interruptions[1][1]["raw_data"]["collaboration_role"] == "support"

            invalid = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={
                    **body,
                    "client_request_id": str(uuid4()),
                    "support_hero_id": "ZuoRu",
                },
            )
            assert invalid.status_code == 422


def test_council_memory_is_recalled_verified_and_sealed_into_mandate() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            first_council_id, _ = complete_council(client)
            first_record = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/decisions",
                json={
                    "client_request_id": first_council_id,
                    "question": "东郊一战如何部署？\n选证：《史记·周本纪》｜史实骨架",
                    "options": [
                        {"index": 0, "text": "固守军粮"},
                        {"index": 1, "text": "整军强攻"},
                    ],
                    "topic": "court_decision",
                },
            ).json()
            assert first_record["replayed"] is True
            assert first_record["dialogueReceipt"]["memoryArchive"]["sourceType"] == "dialogue_choice"

            state = client.get("/api/dongzhou/v1/npcs/ZuoRu/state")
            assert state.status_code == 200
            memory = state.json()["memories"]["items"][0]
            assert memory["idempotencyKey"] == first_record["dialogueReceipt"]["memoryArchive"]["idempotencyKey"]
            assert len(memory["digest"]) == 64

            second_council_id = str(uuid4())
            recalled = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/decisions",
                json={
                    "client_request_id": second_council_id,
                    "question": (
                        "再议东郊部署。\n选证：《史记·周本纪》｜史实骨架"
                        f"\n记忆印记：{memory['digest'][:12]}\n旧事：{memory['content']}"
                    ),
                    "options": [
                        {"index": 0, "text": "固守军粮"},
                        {"index": 1, "text": "整军强攻"},
                    ],
                    "topic": "court_decision",
                    "memory_idempotency_key": memory["idempotencyKey"],
                    "memory_digest": memory["digest"],
                },
            )
            assert recalled.status_code == 200, recalled.text
            assert recalled.json()["memoryReceipt"]["digest"] == memory["digest"]

            draft = client.post(
                "/api/dongzhou/v1/court/mandates",
                json=mandate_body(second_council_id),
            )
            assert draft.status_code == 200, draft.text
            mandate = draft.json()["mandate"]
            assert mandate["memory"]["digest"] == memory["digest"]
            assert mandate["council"]["memory"]["idempotencyKey"] == memory["idempotencyKey"]
            assert mandate["kernel"]["moduleVersion"] == "1.9.0"


def test_ainpc_correspondence_is_recomputed_and_sealed() -> None:
    with TemporaryDirectory() as directory:
        database = Path(directory) / "gateway.sqlite3"
        settings = configured(database)
        store = Store(database)
        asyncio.run(store.start())
        npc_id = str(stable_npc_id(settings.ainpc_game_server_id, "ZuoRu"))
        session = {
            "gameServerId": settings.game_server_id,
            "chatId": "chat-correspondence",
            "taskId": "task-correspondence",
            "aiId": npc_id,
            "playerInfo": {"playerId": "9002", "playerName": "Du Bo"},
            "topic": "military grain route",
        }
        asyncio.run(store.register_private_chat(session))
        asyncio.run(store.record_private_message({
            **session,
            "data": {"message": {"id": "message-correspondence", "speakerId": npc_id, "speakerName": "Zuo Ru", "content": "The north grain route is ready.", "speakerEmotion": "calm"}, "isFinish": False},
        }))
        upstreams = MandateUpstreams()
        published_source = asyncio.run(upstreams.stage_knowledge("01"))[0]["sourceDetails"][0]
        app = build_application(settings, store=store, upstreams=upstreams)
        with TestClient(app) as client:
            start_session(client)
            listed = client.get("/api/dongzhou/v1/npcs/ZuoRu/correspondence?limit=12")
            assert listed.status_code == 200
            message = listed.json()["messages"][0]
            assert message["messageId"] == "message-correspondence"
            assert message["content"] == "The north grain route is ready."
            assert len(message["digest"]) == 64

            council_id = str(uuid4())
            council = client.post("/api/dongzhou/v1/npcs/ZuoRu/decisions", json={
                "client_request_id": council_id,
                "question": f"Choose a route.\n选证：{published_source['work']}｜{published_source['tier']}\n耳报印记：{message['digest'][:12]}",
                "options": [{"index": 0, "text": "North"}, {"index": 1, "text": "South"}],
                "topic": "court_decision",
            })
            assert council.status_code == 200
            body = {
                **mandate_body(council_id),
                "correspondence_message_id": message["messageId"],
                "correspondence_digest": message["digest"],
            }
            draft = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert draft.status_code == 200, draft.text
            assert draft.json()["mandate"]["correspondence"]["digest"] == message["digest"]
            assert draft.json()["mandate"]["council"]["correspondence"]["messageId"] == message["messageId"]

            tampered = client.post("/api/dongzhou/v1/court/mandates", json={
                **body,
                "client_request_id": str(uuid4()),
                "correspondence_digest": "0" * 64,
            })
            assert tampered.status_code == 422
            assert tampered.json()["error"]["code"] == "court_correspondence_unverified"


def test_player_message_uses_formal_ainpc_contract_and_scopes_reply() -> None:
    with TemporaryDirectory() as directory:
        database = Path(directory) / "gateway.sqlite3"
        settings = configured(database)
        store = Store(database)
        asyncio.run(store.start())
        npc_id = str(stable_npc_id(settings.ainpc_game_server_id, "ZuoRu"))
        asyncio.run(store.upsert_npc_directory(settings.game_server_id, [
            {"heroId": "ZuoRu", "name": "左儒", "npcId": npc_id}
        ]))
        asyncio.run(store.mark_npc_ready(
            settings.game_server_id, npc_id, "login-zuoru", None, None, "startup-1"
        ))
        upstreams = MandateUpstreams()
        app = build_application(settings, store=store, upstreams=upstreams)
        request_id = str(uuid4())
        with TestClient(app) as client:
            guest = client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
            assert guest.status_code == 200
            first_player = UUID(guest.json()["playerId"])
            sent = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/messages",
                json={"client_request_id": request_id, "content": "北路军粮可曾送到？"},
            )
            assert sent.status_code == 200, sent.text
            accepted = sent.json()
            assert accepted["state"] == "ACCEPTED"
            assert upstreams.events[-1][0] == "CHAT_TURN"
            payload = upstreams.events[-1][1]
            player_peer_id = str(stable_player_id(settings.ainpc_game_server_id, first_player))
            assert payload["status"] == "inProgress"
            assert payload["npcId"] == npc_id
            assert payload["messages"][0]["speakerId"] == player_peer_id
            assert payload["participants"][1] == {
                "id": player_peer_id, "name": "主君", "type": "PLAYER"
            }

            replay = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/messages",
                json={"client_request_id": request_id, "content": "北路军粮可曾送到？"},
            )
            assert replay.status_code == 200
            assert replay.json()["taskId"] == accepted["taskId"]

            asyncio.run(store.record_private_message({
                "gameServerId": settings.game_server_id,
                "aiId": npc_id,
                "chatId": accepted["chatId"],
                "taskId": accepted["taskId"],
                "isNpc": False,
                # AINPC delivery callbacks do not repeat playerInfo. The sealed
                # chat session remains the authoritative participant record.
                "playerInfo": None,
                "data": {"message": {
                    "id": "reply-to-player",
                    "speakerId": npc_id,
                    "speakerName": "左儒",
                    "speakerEmotion": "calm",
                    "content": "已由北路入仓。",
                    "time": "0771-01-01 14:00:00",
                }, "isFinish": False},
            }))
            own = client.get("/api/dongzhou/v1/npcs/ZuoRu/correspondence")
            assert own.status_code == 200
            assert [item["messageId"] for item in own.json()["messages"]] == ["reply-to-player"]
            assert own.json()["messages"][0]["targetType"] == "PLAYER"

            start_session(client)
            other = client.get("/api/dongzhou/v1/npcs/ZuoRu/correspondence")
            assert other.status_code == 200
            assert other.json()["messages"] == []


def test_spontaneous_thought_is_idempotent_and_sealed_into_selected_council() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            thought_id = str(uuid4())
            thought_body = {
                "client_request_id": thought_id,
                "stage_id": "01",
                "stage_title": "东郊索命",
                "knowledge_id": "dongzhou_stage_001",
                "evidence_source_index": 0,
                "task_type": "drill",
            }
            generated = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/thoughts", json=thought_body
            )
            assert generated.status_code == 200, generated.text
            receipt = generated.json()["thoughtReceipt"]
            assert receipt["thought"]["description"] == "先据旧闻整军，再试探东郊虚实"
            assert receipt["councilProposal"] == "采纳ZuoRu进言，依本回史料执行检阅军阵"
            assert receipt["source"]["work"] == "《史记·周本纪》"
            assert len(receipt["digest"]) == 64
            assert upstreams.thoughts[0][1]["operation_id"].endswith(thought_id)

            replay = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/thoughts", json=thought_body
            )
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True
            assert len(upstreams.thoughts) == 1

            council_id = str(uuid4())
            council = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/decisions",
                json={
                    "client_request_id": council_id,
                    "question": "东郊一战如何部署？\n选证：《史记·周本纪》｜史实骨架",
                    "options": [
                        {"index": 0, "text": "固守军粮"},
                        {"index": 1, "text": receipt["councilProposal"]},
                    ],
                    "topic": "court_decision",
                },
            )
            assert council.status_code == 200
            body = {
                **mandate_body(council_id),
                "thought_request_id": thought_id,
                "thought_digest": receipt["digest"],
            }
            draft = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert draft.status_code == 200, draft.text
            mandate = draft.json()["mandate"]
            assert mandate["thought"]["digest"] == receipt["digest"]
            assert mandate["council"]["thought"]["requestId"] == thought_id

            tampered = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={
                    **body,
                    "client_request_id": str(uuid4()),
                    "thought_digest": "0" * 64,
                },
            )
            assert tampered.status_code == 422
            assert tampered.json()["error"]["code"] == "court_thought_unverified"


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
            draft = issued.json()
            mandate = draft["mandate"]
            assert draft["state"] == "REQUIRES_ACTION"
            assert mandate["state"] == "DRAFT"
            assert draft["action"]["code"] == "seal_court_mandate"
            assert mandate["kernel"]["state"] in {"READY", "DEGRADED"}
            assert mandate["evidence"]["id"] == "dongzhou_stage_001"
            assert mandate["evidence"]["source"] == {
                "index": 0,
                "work": "《史记·周本纪》",
                "tier": "史实骨架",
                "scope": "千亩之败与周宣王晚年",
                "url": "https://ctext.org/shiji/zhou-ben-ji",
            }
            assert mandate["evidenceFit"] == {
                "taskType": "drill",
                "factor": 6.0,
                "band": "aligned",
                "signals": [
                    {"kind": "sourceTier", "label": "史实骨架", "factor": 2.0},
                    {"kind": "councilChoice", "label": "整军", "factor": 4.0},
                ],
            }
            assert mandate["council"]["text"] == "整军强攻"
            assert mandate["council"]["dialogueReceipt"]["state"] == "RECORDED"
            assert len(mandate["council"]["dialogueReceipt"]["digest"]) == 64
            assert (
                mandate["council"]["dialogueReceipt"]["sourceRecordId"]
                == upstreams.dialogue_reports[0][1]["dialogues"][0]["source_record_id"]
            )
            assert mandate["assignment"]["planId"] == "plan-1"
            assert mandate["assignment"]["eventId"] == "event-drill"
            assert mandate["assignment"]["transactionId"] == 9100102
            assert mandate["assignment"]["state"] == {
                "emotion": "calm",
                "intensity": 0.25,
                "affectionCount": 1,
                "relationshipCount": 0,
            }
            assert mandate["assignment"]["managerSupport"] == {
                "managerNpcId": MANAGER_NPC_ID,
                "affection": {"type": "respect", "value": 33.3, "count": 1},
                "relationships": [],
                "factor": 2.0,
            }
            assert mandate["assignment"]["readiness"] == {
                "score": 61,
                "band": "watch",
                "factors": {"runtime": -12.0, "duty": 8.1, "emotion": 6.0, "support": 2.0, "personality": 1.2, "motivation": 0.0, "quality": 1.0},
            }
            assert mandate["assignment"]["personality"]["profileId"] == "profile-zuoru"
            assert mandate["assignment"]["personality"]["fit"]["score"] == 56
            assert mandate["assignment"]["motivation"]["fit"]["score"] == 50
            assert mandate["assignment"]["quality"]["fit"]["score"] == 55
            assert mandate["emergency"] == {
                "urgent": True,
                "score": 81.25,
                "interruptTraceId": "emergency_evaluate:test-trace",
                "assessedAt": "0771-01-01 14:00:00",
                "event": mandate["emergency"]["event"],
            }
            assert mandate["emergency"]["event"].startswith(mandate["stageTitle"])
            assert len(mandate["digest"]) == 64

            replay = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True
            assert replay.json()["mandate"] == mandate
            assert replay.json()["action"] == draft["action"]

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
            blocked = client.post("/api/dongzhou/v1/organization/tasks", json=order)
            assert blocked.status_code == 422
            assert blocked.json()["error"]["code"] == "court_mandate_mismatch"

            wrong_action = client.post(
                f"/api/dongzhou/v1/court/mandates/{mandate['id']}/resume",
                json={"action_id": str(uuid4()), "decision": "APPROVE"},
            )
            assert wrong_action.status_code == 409
            assert wrong_action.json()["error"]["code"] == "court_mandate_action_mismatch"

            mandate = approve_mandate(client, issued)
            assert mandate["state"] == "ISSUED"
            missing_schedule = client.post(
                "/api/dongzhou/v1/organization/tasks", json=order
            )
            assert missing_schedule.status_code == 409
            assert (
                missing_schedule.json()["error"]["code"]
                == "court_mandate_schedule_required"
            )
            schedule_request_id = str(uuid4())
            scheduled = client.post(
                f"/api/dongzhou/v1/court/mandates/{mandate['id']}/schedule",
                json={
                    "client_request_id": schedule_request_id,
                    "mandate_digest": mandate["digest"],
                },
            )
            assert scheduled.status_code == 200, scheduled.text
            schedule_receipt = scheduled.json()["scheduleReceipt"]
            assert schedule_receipt["action"] == "insert_today"
            assert schedule_receipt["mandateId"] == mandate["id"]
            assert schedule_receipt["mandateDigest"] == mandate["digest"]
            assert schedule_receipt["scheduleName"] == "临时军令"
            assert len(schedule_receipt["digest"]) == 64
            assert upstreams.interruptions == [(
                stable_npc_id(91001, "ZuoRu"),
                upstreams.interruptions[0][1],
            )]
            interruption_payload = upstreams.interruptions[0][1]
            assert interruption_payload["event_source"] == "event_report"
            assert interruption_payload["event_importance"] == 81.25
            assert interruption_payload["current_schedule_description"] == mandate["assignment"]["name"]
            assert interruption_payload["raw_data"]["mandate_digest"] == mandate["digest"]

            replayed_schedule = client.post(
                f"/api/dongzhou/v1/court/mandates/{mandate['id']}/schedule",
                json={
                    "client_request_id": schedule_request_id,
                    "mandate_digest": mandate["digest"],
                },
            )
            assert replayed_schedule.status_code == 200
            assert replayed_schedule.json()["replayed"] is True
            assert replayed_schedule.json()["scheduleReceipt"] == schedule_receipt
            assert len(upstreams.interruptions) == 1

            wrong_schedule_seal = client.post(
                f"/api/dongzhou/v1/court/mandates/{mandate['id']}/schedule",
                json={
                    "client_request_id": str(uuid4()),
                    "mandate_digest": "0" * 64,
                },
            )
            assert wrong_schedule_seal.status_code == 422
            assert wrong_schedule_seal.json()["error"]["code"] == "court_mandate_mismatch"
            accepted = client.post("/api/dongzhou/v1/organization/tasks", json=order)
            assert accepted.status_code == 200
            assert accepted.json()["state"] == "ACCEPTED"
            assert upstreams.triggers[0]["expected_hierarchy_version"] == 8
            assert "mandate_id" not in upstreams.triggers[0]["parameters"]
            assert "mandate_digest" not in upstreams.triggers[0]["parameters"]
            assert "Readiness 61/100 (watch)." in upstreams.triggers[0]["brief"]
            assert "Stable quality task fit 55/100 (steady)." in upstreams.triggers[0]["brief"]
            assert "Personality task fit 56/100 (steady)." in upstreams.triggers[0]["brief"]
            assert "Motivation task willingness 50/100 (neutral)." in upstreams.triggers[0]["brief"]
            assert "AINPC emergency assessment: urgent, score 81.25" in upstreams.triggers[0]["brief"]

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


def test_graph_search_receipt_is_sealed_into_council_and_mandate() -> None:
    with TemporaryDirectory() as directory:
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=MandateUpstreams()
        )
        with TestClient(app) as client:
            start_session(client)
            search_id = str(uuid4())
            search_body = {
                "client_request_id": search_id,
                "stage_id": "01",
                "query": "杜伯 东郊军情",
                "limit": 6,
            }
            searched = client.post("/api/dongzhou/v1/knowledge/search", json=search_body)
            assert searched.status_code == 200
            receipt = searched.json()["searchReceipt"]
            result = searched.json()["results"][0]
            assert result["retrieval"]["graphRelated"] is True
            assert result["searchReceipt"] == {"id": receipt["id"], "digest": receipt["digest"]}
            replay = client.post("/api/dongzhou/v1/knowledge/search", json=search_body)
            assert replay.json()["replayed"] is True
            assert replay.json()["searchReceipt"] == receipt

            council_id = str(uuid4())
            council = client.post(
                "/api/dongzhou/v1/npcs/ZuoRu/decisions",
                json={
                    "client_request_id": council_id,
                    "question": (
                        "东郊一战如何部署？\n选证：《史记·周本纪》｜史实骨架\n"
                        f"检索回执：{receipt['digest'][:12]}"
                    ),
                    "options": [
                        {"index": 0, "text": "固守军粮"},
                        {"index": 1, "text": "整军强攻"},
                    ],
                    "topic": "court_decision",
                },
            )
            assert council.status_code == 200
            body = {
                **mandate_body(council_id),
                "knowledge_search_receipt_id": receipt["id"],
                "knowledge_search_receipt_digest": receipt["digest"],
            }
            drafted = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert drafted.status_code == 200
            evidence = drafted.json()["mandate"]["evidence"]
            assert evidence["retrieval"] == result["retrieval"]
            assert evidence["searchReceipt"] == result["searchReceipt"]

            tampered = client.post(
                "/api/dongzhou/v1/court/mandates",
                json={
                    **body,
                    "client_request_id": str(uuid4()),
                    "knowledge_search_receipt_digest": "b" * 64,
                },
            )
            assert tampered.status_code == 422
            assert tampered.json()["error"]["code"] == "court_knowledge_receipt_unverified"


def test_terminal_task_exposes_authoritative_settlement_and_kernel_closure() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        database = Path(directory) / "gateway.sqlite3"
        app = build_application(
            configured(database), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            draft = client.post(
                "/api/dongzhou/v1/court/mandates",
                json=mandate_body(council_id),
            )
            issued = approve_mandate(client, draft)
            schedule_mandate(client, issued)
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
                    "mandate_id": issued["id"],
                    "mandate_digest": issued["digest"],
                },
            }
            task_id = client.post(
                "/api/dongzhou/v1/organization/tasks", json=order
            ).json()["taskId"]
            settlement_id = str(uuid4())
            upstreams.task_snapshot = {
                "task_id": task_id,
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "state": "SUCCEEDED",
                "final_result": "SUCCESS",
                "contribution_eligible": True,
                "responsible_member_id": "00000000-0000-0000-0000-000000000004",
                "version": "3",
                "settlement": {
                    "settlement_id": settlement_id,
                    "task_id": task_id,
                    "organization_id": "00000000-0000-0000-0000-000000000001",
                    "member_id": "00000000-0000-0000-0000-000000000004",
                    "result": "SUCCESS",
                    "organization_delta": "100",
                    "member_delta": "75",
                    "source": "NPC_CONFIRMATION",
                    "source_event_id": "dongzhou-result-1",
                    "settled_game_time": "24306616800",
                    "settled_clock_epoch": "dongzhou-v1",
                    "settled_at": "2026-11-11T00:00:00Z",
                },
            }
            first = client.get(f"/api/dongzhou/v1/organization/tasks/{task_id}")
            assert first.status_code == 200
            body = first.json()
            assert body["settlement"] == {
                "settlementId": settlement_id,
                "taskId": task_id,
                "organizationId": "00000000-0000-0000-0000-000000000001",
                "memberId": "00000000-0000-0000-0000-000000000004",
                "result": "SUCCESS",
                "organizationDelta": 100,
                "memberDelta": 75,
                "source": "NPC_CONFIRMATION",
                "sourceEventId": "dongzhou-result-1",
                "settledGameTime": "24306616800",
                "settledClockEpoch": "dongzhou-v1",
                "settledAt": "2026-11-11T00:00:00Z",
            }
            closure = body["closureReceipt"]
            assert closure["state"] == "SEALED"
            assert closure["mandateId"] == issued["id"]
            assert closure["mandateDigest"] == issued["digest"]
            assert closure["settlement"]["settlementId"] == settlement_id
            assert len(closure["digest"]) == 64
            review = body["review"]
            assert review["state"] == "REQUIRES_ACTION"
            assert review["review"]["settlementId"] == settlement_id
            assert review["review"]["closureDigest"] == closure["digest"]
            assert review["review"]["kernel"]["moduleVersion"] == "1.9.0"
            wrong_action = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": str(uuid4()), "decision": "ACCEPT"},
            )
            assert wrong_action.status_code == 409
            accepted = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": review["action"]["actionId"], "decision": "ACCEPT"},
            )
            assert accepted.status_code == 200
            assert accepted.json()["state"] == "ACCEPTED"
            assert accepted.json()["review"]["decision"] == "ACCEPT"
            assert len(accepted.json()["review"]["digest"]) == 64
            assert accepted.json()["inventoryReward"] == {
                "entryId": "00000000-0000-4000-8000-000000000088",
                "resourceKey": "task.execution",
                "delta": 100,
                "balanceAfter": 100,
                "accountVersion": 1,
                "inventoryRevision": 1,
            }
            assert upstreams.inventory_adjustments == [(
                "00000000-0000-0000-0000-000000000001",
                {
                    "resource_key": "task.execution",
                    "delta_units": 100,
                    "reason_code": "TASK_SETTLEMENT_ACCEPTED",
                },
                f"dongzhou-settlement-reward:{settlement_id}",
            )]
            growth_reward = accepted.json()["growthReward"]
            assert growth_reward["settlementId"] == settlement_id
            assert growth_reward["taskId"] == task_id
            assert growth_reward["amount"] == 100
            assert growth_reward["contributionPoints"] == 100
            assert growth_reward["accountVersion"] == 1
            assert growth_reward["closureDigest"] == closure["digest"]
            assert growth_reward["kernel"]["moduleVersion"] == "1.9.0"
            assert len(growth_reward["digest"]) == 64
            assert upstreams.growth_credits == [(
                "00000000-0000-0000-0000-000000000001",
                {
                    "source_type": "task.settlement",
                    "source_id": settlement_id,
                    "amount": 100,
                },
                f"dongzhou-settlement-growth:{settlement_id}",
            )]
            connection = sqlite3.connect(database)
            try:
                row = connection.execute(
                    "SELECT player_id,request_id,response_payload FROM requests "
                    "WHERE kind='organization_settlement_review' AND external_id=?",
                    (task_id,),
                ).fetchone()
                assert row is not None
                historical = json.loads(row[2])
                historical.pop("growthReward")
                connection.execute(
                    "UPDATE requests SET response_payload=? WHERE player_id=? AND request_id=?",
                    (json.dumps(historical), row[0], row[1]),
                )
                connection.commit()
            finally:
                connection.close()
            upstreams.growth_credits.clear()
            migrated = client.get(
                f"/api/dongzhou/v1/organization/tasks/{task_id}"
            )
            assert migrated.status_code == 200
            assert migrated.json()["review"]["growthReward"]["settlementId"] == settlement_id
            assert upstreams.growth_credits == [(
                "00000000-0000-0000-0000-000000000001",
                {
                    "source_type": "task.settlement",
                    "source_id": settlement_id,
                    "amount": 100,
                },
                f"dongzhou-settlement-growth:{settlement_id}",
            )]
            replay = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": review["action"]["actionId"], "decision": "ACCEPT"},
            )
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True
            assert len(upstreams.inventory_adjustments) == 1
            assert len(upstreams.growth_credits) == 1
            conflict = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": review["action"]["actionId"], "decision": "CENSURE"},
            )
            assert conflict.status_code == 409
            assert client.get(
                f"/api/dongzhou/v1/organization/tasks/{task_id}"
            ).json()["review"]["state"] == "ACCEPTED"

            upstreams.task_snapshot["settlement"]["member_id"] = str(uuid4())
            invalid = client.get(
                f"/api/dongzhou/v1/organization/tasks/{task_id}"
            )
            assert invalid.status_code == 502
            assert invalid.json()["error"]["code"] == "organization_settlement_invalid"


def test_censured_settlement_records_ainpc_affection_and_memory_once() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        database = Path(directory) / "gateway.sqlite3"
        store = Store(database)
        app = build_application(configured(database), store=store, upstreams=upstreams)
        with TestClient(app) as client:
            session = client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
            assert session.status_code == 200
            player_id = UUID(session.json()["playerId"])
            council_id, _ = complete_council(client)
            draft = client.post(
                "/api/dongzhou/v1/court/mandates",
                json=mandate_body(council_id),
            )
            issued = approve_mandate(client, draft)
            schedule_mandate(client, issued)
            task_id = client.post(
                "/api/dongzhou/v1/organization/tasks",
                json={
                    "client_request_id": str(uuid4()),
                    "task_type": "drill",
                    "assignee_hero_id": "ZuoRu",
                    "stage_id": "01",
                    "stage_title": "Dongzhou stage 01",
                    "brief": "Execute the sealed court mandate.",
                    "parameters": {
                        "resource_units": 6,
                        "assignee_name": "左儒",
                        "mandate_id": issued["id"],
                        "mandate_digest": issued["digest"],
                    },
                },
            ).json()["taskId"]
            settlement_id = str(uuid4())
            upstreams.task_snapshot = {
                "task_id": task_id,
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "state": "FAILED",
                "final_result": "FAILURE",
                "contribution_eligible": True,
                "responsible_member_id": "00000000-0000-0000-0000-000000000004",
                "version": "3",
                "settlement": {
                    "settlement_id": settlement_id,
                    "task_id": task_id,
                    "organization_id": "00000000-0000-0000-0000-000000000001",
                    "member_id": "00000000-0000-0000-0000-000000000004",
                    "result": "FAILURE",
                    "organization_delta": "0",
                    "member_delta": "0",
                    "source": "NPC_CONFIRMATION",
                    "source_event_id": "dongzhou-censure-result-1",
                    "settled_game_time": "0772-10-22 14:00:00",
                    "settled_clock_epoch": "dongzhou-v1",
                    "settled_at": "2026-11-12T00:00:00Z",
                },
                "derivations": [],
            }
            terminal_response = client.get(
                f"/api/dongzhou/v1/organization/tasks/{task_id}"
            )
            assert terminal_response.status_code == 200, terminal_response.text
            terminal = terminal_response.json()
            action_id = terminal["review"]["action"]["actionId"]
            censured = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": action_id, "decision": "CENSURE"},
            )
            assert censured.status_code == 200, censured.text
            body = censured.json()
            assert body["state"] == "CENSURED"
            assert "inventoryReward" not in body
            assert body["npcConsequence"]["affectionType"] == "annoyance"
            assert body["npcConsequence"]["affectionDelta"] == 5.8
            assert body["npcConsequence"]["severity"] == 58
            assert body["npcConsequence"]["npcId"] == str(
                stable_npc_id(91001, "ZuoRu")
            )
            assert body["npcConsequence"]["targetId"] == str(
                stable_player_id(91001, player_id)
            )

            replay = client.post(
                f"/api/dongzhou/v1/organization/tasks/{task_id}/review",
                json={"action_id": action_id, "decision": "CENSURE"},
            )
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True

            deadline = time.monotonic() + 3
            current = None
            while time.monotonic() < deadline:
                current = client.get(
                    f"/api/dongzhou/v1/organization/tasks/{task_id}"
                ).json()
                if current.get("npcConsequence", {}).get("state") == "DELIVERED":
                    break
                time.sleep(0.05)
            assert current["npcConsequence"]["state"] == "DELIVERED"
            assert current["npcConsequence"]["event"]["state"] == "DELIVERED"
            assert current["npcConsequence"]["memory"]["state"] == "DELIVERED"
            assert current["npcConsequence"]["affection"]["state"] == "DELIVERED"
            consequence_events = [
                (kind, payload)
                for kind, payload in upstreams.events
                if kind in {"NPC_TASK_OUTCOME", "NPC_TASK_MEMORY", "NPC_AFFECTION_SETTLEMENT"}
            ]
            assert {kind for kind, _ in consequence_events} == {
                "NPC_TASK_OUTCOME", "NPC_TASK_MEMORY", "NPC_AFFECTION_SETTLEMENT"
            }
            affection_payload = next(
                payload for kind, payload in consequence_events
                if kind == "NPC_AFFECTION_SETTLEMENT"
            )
            assert affection_payload["target_id"] == str(stable_player_id(91001, player_id))
            assert affection_payload["changes"][0]["affection_type"] == "annoyance"
            assert affection_payload["changes"][0]["delta"] == 5.8
            outcome_payload = next(
                payload for kind, payload in consequence_events
                if kind == "NPC_TASK_OUTCOME"
            )
            metadata = outcome_payload["events"][0]["metadata"]
            assert metadata["actor_id"] == str(stable_player_id(91001, player_id))
            assert metadata["target_id"] == str(stable_npc_id(91001, "ZuoRu"))
            assert metadata["behavior_parent"] == "insult"
            assert metadata["behavior_sub"] == "official_censure"
            assert metadata["result_confirmed"] is True
            assert len(upstreams.inventory_adjustments) == 0


def test_failure_task_registers_authoritative_remediation() -> None:
    with TemporaryDirectory() as directory:
        upstreams = MandateUpstreams()
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=upstreams
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            draft = client.post(
                "/api/dongzhou/v1/court/mandates",
                json=mandate_body(council_id),
            )
            issued = approve_mandate(client, draft)
            schedule_mandate(client, issued)
            order = {
                "client_request_id": str(uuid4()),
                "task_type": "drill",
                "assignee_hero_id": "ZuoRu",
                "stage_id": "01",
                "stage_title": "Dongzhou stage 01",
                "brief": "Execute the sealed court mandate.",
                "parameters": {
                    "resource_units": 6,
                    "assignee_name": "Zuo Ru",
                    "mandate_id": issued["id"],
                    "mandate_digest": issued["digest"],
                },
            }
            task_id = client.post(
                "/api/dongzhou/v1/organization/tasks", json=order
            ).json()["taskId"]
            derived_task_id = str(uuid4())
            intent_id = str(uuid4())
            settlement_id = str(uuid4())
            upstreams.task_snapshot = {
                "task_id": task_id,
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "state": "FAILED",
                "final_result": "FAILURE",
                "contribution_eligible": True,
                "responsible_member_id": "00000000-0000-0000-0000-000000000004",
                "position_slot_id": "00000000-0000-0000-0000-000000000003",
                "version": "4",
                "settlement": {
                    "settlement_id": settlement_id,
                    "task_id": task_id,
                    "organization_id": "00000000-0000-0000-0000-000000000001",
                    "member_id": "00000000-0000-0000-0000-000000000004",
                    "result": "FAILURE",
                    "organization_delta": "0",
                    "member_delta": "0",
                    "source": "NPC_CONFIRMATION",
                    "source_event_id": "dongzhou-remediation-result",
                    "settled_game_time": "24306616800",
                    "settled_clock_epoch": "dongzhou-v1",
                    "settled_at": "2026-11-12T00:00:00Z",
                },
                "derivations": [{
                    "intent_id": intent_id,
                    "predecessor_task_id": task_id,
                    "root_task_id": task_id,
                    "planned_task_id": derived_task_id,
                    "created_task_id": derived_task_id,
                    "rule_id": "dongzhou_drill_failure_remediation",
                    "source": "REMEDIATION",
                    "target_task_code": "dongzhou.supply",
                    "target_position_selector": "SAME_POSITION",
                    "target_position_slot_id": "00000000-0000-0000-0000-000000000003",
                    "parameter_strategy": "TARGET_DEFAULTS",
                    "target_default_parameters": {
                        "assignee_hero_id": "unassigned",
                        "assignee_name": "Unassigned",
                        "resource_units": 0,
                        "stage_id": "unknown",
                        "stage_title": "Unknown stage",
                    },
                    "generation_depth": 1,
                    "trigger_result": "FAILURE",
                    "state": "CREATED",
                }],
            }
            response = client.get(
                f"/api/dongzhou/v1/organization/tasks/{task_id}"
            )
            assert response.status_code == 200
            assert response.json()["followUps"] == [{
                "intentId": intent_id,
                "taskId": derived_task_id,
                "state": "CREATED",
                "source": "REMEDIATION",
                "taskType": "supply",
                "ruleId": "dongzhou_drill_failure_remediation",
                "stageId": "01",
                "stageTitle": "Dongzhou stage 01",
                "assigneeHeroId": "ZuoRu",
            }]
            upstreams.task_snapshot = {
                "task_id": derived_task_id,
                "organization_id": "00000000-0000-0000-0000-000000000001",
                "state": "FAILED",
                "final_result": "FAILURE",
                "contribution_eligible": True,
                "responsible_member_id": "00000000-0000-0000-0000-000000000006",
                "version": "1",
                "derivations": [],
                "settlement": {
                    "settlement_id": str(uuid4()),
                    "task_id": derived_task_id,
                    "organization_id": "00000000-0000-0000-0000-000000000001",
                    "member_id": "00000000-0000-0000-0000-000000000006",
                    "result": "FAILURE",
                    "organization_delta": "0",
                    "member_delta": "0",
                    "source": "NPC_CONFIRMATION",
                    "source_event_id": "dongzhou-remediation-child-result",
                    "settled_game_time": "24306616800",
                    "settled_clock_epoch": "dongzhou-v1",
                    "settled_at": "2026-11-12T00:01:00Z",
                },
            }
            child = client.get(
                f"/api/dongzhou/v1/organization/tasks/{derived_task_id}"
            )
            assert child.status_code == 200
            assert child.json()["taskId"] == derived_task_id
            assert child.json()["assigneeHeroId"] == "QinXiangGong"


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
            mandate = approve_mandate(client, issued)
            assert mandate["operation"] == body["operation"]
            schedule_mandate(client, mandate)

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
                    "Readiness 57/100 (watch). "
                    "Personality task fit 48/100 (strained). "
                    "Motivation task willingness 50/100 (neutral). "
                    "Stable quality task fit 46/100 (strained). "
                    "Sealed evidence fit 2.0/9 (weak) for diplomacy. "
                    "AINPC emergency assessment: urgent, score 81.25, "
                    "trace emergency_evaluate:test-trace."
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


def test_mandate_rejection_is_terminal_and_replayed() -> None:
    with TemporaryDirectory() as directory:
        app = build_application(
            configured(Path(directory) / "gateway.sqlite3"), upstreams=MandateUpstreams()
        )
        with TestClient(app) as client:
            start_session(client)
            council_id, _ = complete_council(client)
            body = mandate_body(council_id)
            draft = client.post("/api/dongzhou/v1/court/mandates", json=body).json()
            rejected = client.post(
                f"/api/dongzhou/v1/court/mandates/{draft['mandate']['id']}/resume",
                json={"action_id": draft["action"]["actionId"], "decision": "REJECT"},
            )
            assert rejected.status_code == 200
            assert rejected.json()["state"] == "REJECTED"
            assert rejected.json()["mandate"]["state"] == "REJECTED"
            replay = client.post("/api/dongzhou/v1/court/mandates", json=body)
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True
            assert replay.json()["state"] == "REJECTED"
            contradictory = client.post(
                f"/api/dongzhou/v1/court/mandates/{draft['mandate']['id']}/resume",
                json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
            )
            assert contradictory.status_code == 200
            assert contradictory.json()["replayed"] is True
            assert contradictory.json()["state"] == "REJECTED"


def test_mandate_action_survives_application_restart() -> None:
    with TemporaryDirectory() as directory:
        database = Path(directory) / "gateway.sqlite3"
        installation_id = str(uuid4())
        app = build_application(configured(database), upstreams=MandateUpstreams())
        with TestClient(app) as client:
            start_session(client, installation_id)
            council_id, _ = complete_council(client)
            draft = client.post(
                "/api/dongzhou/v1/court/mandates", json=mandate_body(council_id)
            ).json()

        restarted = build_application(configured(database), upstreams=MandateUpstreams())
        with TestClient(restarted) as client:
            start_session(client, installation_id)
            approved = client.post(
                f"/api/dongzhou/v1/court/mandates/{draft['mandate']['id']}/resume",
                json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
            )
            assert approved.status_code == 200
            assert approved.json()["state"] == "ISSUED"
            terminal_replay = client.post(
                f"/api/dongzhou/v1/court/mandates/{draft['mandate']['id']}/resume",
                json={"action_id": draft["action"]["actionId"], "decision": "APPROVE"},
            )
            assert terminal_replay.status_code == 200
            assert terminal_replay.json()["replayed"] is True
