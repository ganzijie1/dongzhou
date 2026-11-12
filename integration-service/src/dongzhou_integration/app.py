from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
import hashlib
from importlib.metadata import version
import json
import re
from typing import Annotated, Any
from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import APIRouter, Cookie, Depends, Header, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nexus_kernel.config import ApplicationSettings
from nexus_kernel.gateway import ApiError, create_app
from nexus_kernel.kernel import Kernel, LoadedModule, Module, ModuleContext

from .config import Settings
from .assignments import AssignmentUnavailable, select_assignment
from .models import AinpcAliveQuery, AinpcAllLoginRequest, AinpcChatStartRequest, AinpcLoginReadyRequest, AinpcNearbyQuery, AinpcNpcDirectoryQuery, AinpcPrivateChatRuntimeQuery, AinpcPrivateChatRuntimeResetRequest, AinpcPrivateMessageDeliveryQuery, AinpcPrivateMessageRequest, AinpcSingleLoginRequest, AinpcTaskStatusQuery, CampaignRouteRequest, CourtMandateRequest, CourtMandateResumeRequest, CourtMandateScheduleRequest, GameClockQuery, GuestSessionRequest, KnowledgeQuizAnswerRequest, KnowledgeQuizStartRequest, KnowledgeSearchRequest, NpcDecisionRequest, NpcInteractionPreferenceRequest, NpcMessageRequest, NpcScheduleGenerateRequest, NpcSyncRequest, NpcThoughtRequest, OrganizationInventoryRequisitionRequest, OrganizationTaskRequest, OrganizationTaskReviewRequest, SaveWriteRequest
from .security import InvalidSession, issue_session, stable_event_id, stable_npc_id, stable_player_id, verify_session
from .store import GameClockConflict, Store, VersionConflict
from .upstreams import UpstreamUnavailable, Upstreams


_NEXUS_KERNEL_VERSION = version("nexus-kernel-starter")


class RuntimeModule(Module):
    name = "dongzhou_runtime"
    version = "1.0.0"

    def __init__(self, store: Store, upstreams: Upstreams, settings: Settings) -> None:
        super().__init__()
        self.store = store
        self.upstreams = upstreams
        self.settings = settings
        self.services: dict[str, dict[str, Any]] = {}
        self._health_task: asyncio.Task[None] | None = None
        self._game_event_task: asyncio.Task[None] | None = None
        self._npc_reconcile_task: asyncio.Task[None] | None = None
        self._npc_relogin_tasks: set[asyncio.Task[None]] = set()

    async def on_start(self, context: ModuleContext) -> None:
        await self.store.start()
        await self._backfill_npc_memories()
        await self._backfill_npc_qualities()
        self.services = await self.upstreams.health()
        self._health_task = asyncio.create_task(self._poll_health(), name="dongzhou-upstream-health")
        self._game_event_task = asyncio.create_task(
            self._dispatch_game_events(), name="dongzhou-game-event-outbox"
        )
        self._npc_reconcile_task = asyncio.create_task(
            self._reconcile_npcs(), name="dongzhou-npc-reconcile"
        )

    async def on_stop(self, context: ModuleContext) -> None:
        tasks = [
            task
            for task in (
                self._health_task,
                self._game_event_task,
                self._npc_reconcile_task,
            )
            if task
        ] + list(self._npc_relogin_tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.upstreams.close()

    def schedule_npc_relogin(
        self, npcs: list[dict[str, str]], game_time: str, login_round: str
    ) -> None:
        async def replay() -> None:
            await self.upstreams.set_npcs_online(npcs, game_time, login_round)

        task = asyncio.create_task(replay(), name=f"dongzhou-npc-relogin-{login_round}")
        self._npc_relogin_tasks.add(task)
        task.add_done_callback(self._npc_relogin_tasks.discard)

    async def _poll_health(self) -> None:
        while True:
            await asyncio.sleep(10)
            self.services = await self.upstreams.health()

    async def _backfill_npc_memories(self) -> None:
        for outcome in await self.store.npc_outcomes_missing_memory():
            event_id = str(outcome.get("eventId") or "")
            if not event_id.startswith("npc-outcome:"):
                continue
            task_id = event_id.removeprefix("npc-outcome:")
            payload = outcome.get("payload")
            if task_id and isinstance(payload, dict):
                await self.store.enqueue_game_event(
                    "npc-memory:" + task_id,
                    "NPC_TASK_MEMORY",
                    _npc_memory_from_event(payload),
                )

    async def _backfill_npc_qualities(self) -> None:
        for outcome in await self.store.npc_outcomes_missing_quality():
            event_id = str(outcome.get("eventId") or "")
            if not event_id.startswith("npc-outcome:"):
                continue
            task_id = event_id.removeprefix("npc-outcome:")
            payload = outcome.get("payload")
            if task_id and isinstance(payload, dict):
                await self.store.enqueue_game_event(
                    "npc-quality:" + task_id,
                    "NPC_QUALITY_SETTLEMENT",
                    _npc_quality_from_event(payload),
                )

    async def _dispatch_game_events(self) -> None:
        while True:
            events = await self.store.pending_game_events()
            if not events:
                await asyncio.sleep(0.25)
                continue
            for event in events:
                try:
                    receipt = await self.upstreams.send_game_event(
                        event["kind"], event["payload"]
                    )
                    if event["kind"] == "ORG_REPORT_START":
                        outcome = event["payload"].get("npc_outcome")
                        if isinstance(outcome, dict):
                            final_result = _organization_final_result(receipt)
                            final_result = final_result or str(
                                outcome.get("planned_result") or "FAILURE"
                            )
                            task_id = str(outcome.get("task_id") or "")
                            if task_id:
                                await self.store.enqueue_game_event(
                                    "npc-outcome:" + task_id,
                                    "NPC_TASK_OUTCOME",
                                    _npc_outcome_event(outcome, final_result),
                                )
                                await self.store.enqueue_game_event(
                                    "npc-memory:" + task_id,
                                    "NPC_TASK_MEMORY",
                                    _npc_outcome_memory(outcome, final_result),
                                )
                                await self.store.enqueue_game_event(
                                    "npc-quality:" + task_id,
                                    "NPC_QUALITY_SETTLEMENT",
                                    _npc_outcome_quality(outcome, final_result),
                                )
                                await self.store.enqueue_game_event(
                                    "npc-motivation:" + task_id,
                                    "NPC_MOTIVATION_SETTLEMENT",
                                    _npc_outcome_motivation(outcome, final_result),
                                )
                except Exception as error:
                    await self.store.retry_game_event(event["eventId"], type(error).__name__)
                else:
                    await self.store.finish_game_event(event["eventId"])

    async def _reconcile_npcs(self) -> None:
        force_relogin = True
        while True:
            try:
                await self._reconcile_npcs_once(force_relogin=force_relogin)
            except Exception:
                await asyncio.sleep(5)
                continue
            force_relogin = False
            await asyncio.sleep(30)


    async def _reconcile_npcs_once(self, *, force_relogin: bool = False) -> None:
        login_round = "dongzhou-recovery-" + datetime.now(UTC).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        rows = await self.store.list_npcs(
            self.settings.game_server_id,
            include_offline=True,
        )
        if not rows:
            return
        npcs = [
            {
                "heroId": str(row["heroId"]),
                "name": str(row["name"]),
                "npcId": str(row["id"]),
            }
            for row in rows
        ]
        online_ids = await self.upstreams.online_npc_ids()
        missing = [npc for npc in npcs if npc["npcId"] not in online_ids]
        pending = npcs if force_relogin else missing
        if missing:
            await self.upstreams.register_npcs(missing)
        if pending:
            clock = await self.store.read_game_clock()
            await self.upstreams.set_npcs_online(
                pending,
                str(clock["virtualTime"]),
                login_round,
            )
        try:
            await _sync_organization_supervision(self.upstreams, self.settings, npcs)
        except UpstreamUnavailable:
            # Organization hierarchy is eventually consistent and must not turn a
            # healthy NPC actor recovery into a repeated relogin loop.
            pass


class MandateWorkflowModule(Module):
    name = "dongzhou_mandate_workflow"
    version = "1.7.0"
    dependencies = (RuntimeModule.name,)

    @staticmethod
    def draft(trace: dict[str, Any], digest: str) -> dict[str, Any]:
        action_id = uuid5(NAMESPACE_URL, f"dongzhou-mandate-action:{digest}")
        return {
            "state": "REQUIRES_ACTION",
            "mandate": {**trace, "digest": digest, "state": "DRAFT"},
            "action": {
                "actionId": str(action_id),
                "code": "seal_court_mandate",
                "type": "confirmation",
                "prompt": "Confirm issuance of this court mandate?",
                "options": ["APPROVE", "REJECT"],
            },
        }

    @staticmethod
    def resume(response: dict[str, Any], decision: str) -> dict[str, Any]:
        mandate = response.get("mandate")
        if not isinstance(mandate, dict):
            raise ValueError("missing mandate draft")
        state = "ISSUED" if decision == "APPROVE" else "REJECTED"
        return {"state": state, "mandate": {**mandate, "state": state}}

    @staticmethod
    def draft_inventory_requisition(
        trace: dict[str, Any], digest: str
    ) -> dict[str, Any]:
        action_id = uuid5(
            NAMESPACE_URL,
            f"dongzhou-inventory-requisition-action:{digest}",
        )
        return {
            "state": "REQUIRES_ACTION",
            "requestId": trace["requestId"],
            "stageId": trace["stageId"],
            "requisition": {**trace, "digest": digest, "state": "DRAFT"},
            "action": {
                "actionId": str(action_id),
                "code": "approve_inventory_requisition",
                "type": "confirmation",
                "prompt": "Approve this public inventory requisition?",
                "options": ["APPROVE", "REJECT"],
            },
        }

    @staticmethod
    def review_settlement(
        task_id: str,
        settlement: dict[str, Any],
        closure: dict[str, Any],
    ) -> dict[str, Any]:
        settlement_id = str(settlement["settlementId"])
        closure_digest = str(closure["digest"])
        action_id = uuid5(
            NAMESPACE_URL,
            f"dongzhou-settlement-action:{task_id}:{settlement_id}:{closure_digest}",
        )
        return {
            "state": "REQUIRES_ACTION",
            "review": {
                "id": f"dongzhou:review:{settlement_id}",
                "taskId": task_id,
                "settlementId": settlement_id,
                "finalResult": settlement["result"],
                "closureDigest": closure_digest,
                "state": "PENDING",
                "kernel": {
                    "module": MandateWorkflowModule.name,
                    "moduleVersion": MandateWorkflowModule.version,
                    "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                    "state": "REQUIRES_ACTION",
                },
            },
            "action": {
                "actionId": str(action_id),
                "code": "review_organization_settlement",
                "type": "confirmation",
                "prompt": "Accept this sealed organization report or censure its outcome?",
                "options": ["ACCEPT", "CENSURE"],
            },
        }

    @staticmethod
    def resume_settlement_review(response: dict[str, Any], decision: str) -> dict[str, Any]:
        review = response.get("review")
        if not isinstance(review, dict):
            raise ValueError("missing organization settlement review")
        state = "ACCEPTED" if decision == "ACCEPT" else "CENSURED"
        trace = {**review, "decision": decision, "state": state}
        digest = hashlib.sha256(
            json.dumps(trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        return {
            "state": state,
            "review": {
                **trace,
                "digest": digest,
                "kernel": {**dict(review.get("kernel") or {}), "state": state},
            },
        }


class KnowledgeTournamentModule(Module):
    name = "dongzhou_knowledge_tournament"
    version = "1.0.0"
    dependencies = (RuntimeModule.name,)

    @staticmethod
    def seal_question(trace: dict[str, Any]) -> dict[str, Any]:
        digest = hashlib.sha256(
            json.dumps(trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        action_id = uuid5(NAMESPACE_URL, f"dongzhou-knowledge-quiz:{digest}")
        public_question = {
            key: trace[key]
            for key in ("id", "stageId", "knowledgeId", "title", "prompt", "options", "deadlineAt")
        }
        return {
            "state": "READY",
            "question": {
                **public_question,
                "receipt": {
                    "digest": digest,
                    "kernel": {
                        "module": KnowledgeTournamentModule.name,
                        "moduleVersion": KnowledgeTournamentModule.version,
                        "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                        "state": "READY",
                    },
                },
            },
            "action": {
                "actionId": str(action_id),
                "code": "answer_knowledge_quiz",
                "type": "selection",
            },
        }

    @staticmethod
    def seal_result(question_digest: str, selected_index: int, correct_index: int, state: str) -> dict[str, Any]:
        correct = state == "COMPLETED" and selected_index == correct_index
        score = 10 if correct else 0
        trace = {
            "questionDigest": question_digest,
            "selectedIndex": selected_index,
            "correctIndex": correct_index,
            "state": state,
            "correct": correct,
            "score": score,
        }
        digest = hashlib.sha256(
            json.dumps(trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        return {
            **trace,
            "receipt": {
                "digest": digest,
                "kernel": {
                    "module": KnowledgeTournamentModule.name,
                    "moduleVersion": KnowledgeTournamentModule.version,
                    "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                    "state": "SEALED",
                },
            },
        }


class CampaignRouteModule(Module):
    name = "dongzhou_campaign_route"
    version = "1.0.0"
    dependencies = (RuntimeModule.name,)

    @staticmethod
    def seal_selection(trace: dict[str, Any]) -> dict[str, Any]:
        digest = hashlib.sha256(
            json.dumps(trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        return {
            "digest": digest,
            "kernel": {
                "module": CampaignRouteModule.name,
                "moduleVersion": CampaignRouteModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": "SEALED",
            },
        }


class NpcSettlementModule(Module):
    name = "dongzhou_npc_settlement"
    version = "1.0.0"
    dependencies = (RuntimeModule.name,)

    @staticmethod
    def seal_delivery(
        task_id: str,
        final_result: str,
        outcome: dict[str, Any],
    ) -> dict[str, Any]:
        normalized_result = str(final_result).upper()
        if normalized_result not in {"SUCCESS", "PARTIAL", "FAILURE"}:
            raise ValueError("invalid organization task result")
        UUID(task_id)
        event_ids = {
            "event": "npc-outcome:" + task_id,
            "memory": "npc-memory:" + task_id,
            "quality": "npc-quality:" + task_id,
            "motivation": "npc-motivation:" + task_id,
        }
        deliveries: dict[str, dict[str, Any]] = {}
        for name, event_id in event_ids.items():
            status = outcome.get(name)
            if not isinstance(status, dict) or status.get("state") != "DELIVERED":
                raise ValueError(f"NPC settlement part is not delivered: {name}")
            attempts = status.get("attempts")
            if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
                raise ValueError(f"NPC settlement attempts are invalid: {name}")
            deliveries[name] = {"eventId": event_id, "attempts": attempts}
        trace = {
            "taskId": task_id,
            "finalResult": normalized_result,
            "deliveries": deliveries,
        }
        digest = hashlib.sha256(
            json.dumps(
                trace,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return {
            "state": "SEALED",
            "digest": digest,
            **trace,
            "kernel": {
                "module": NpcSettlementModule.name,
                "moduleVersion": NpcSettlementModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": "SEALED",
            },
        }


def _correspondence_evidence(message: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        "messageId": str(message.get("messageId") or ""),
        "chatId": str(message.get("chatId") or ""),
        "taskId": str(message.get("taskId") or ""),
        "speakerId": str(message.get("speakerId") or ""),
        "speakerName": str(message.get("speakerName") or "")[:100],
        "targetId": str(message.get("targetId") or ""),
        "targetName": str(message.get("targetName") or "")[:100],
        "targetType": str(message.get("targetType") or "")[:16],
        "content": str(message.get("content") or "")[:2000],
        "emotion": str(message.get("emotion") or "")[:100],
        "topic": str(message.get("topic") or "")[:1000],
        "deliveredAt": str(message.get("deliveredAt") or ""),
    }
    evidence["digest"] = hashlib.sha256(
        json.dumps(evidence, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    return evidence


def _payload(value: BaseModel) -> dict[str, Any]:
    return value.model_dump(mode="json")


def _canonical_digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()


def _repair_utf8_mojibake(value: Any) -> str:
    text = str(value or "")
    for _ in range(5):
        def repair_span(match: re.Match[str]) -> str:
            try:
                return match.group(0).encode("latin-1").decode("utf-8")
            except UnicodeDecodeError:
                return match.group(0)

        repaired = re.sub(r"[\x00-\xff]+", repair_span, text)
        if repaired == text:
            break
        text = repaired
    return text


def _npc_memory_receipt(item: dict[str, Any]) -> dict[str, Any]:
    """Expose only stable, player-usable memory fields and seal their exact value."""

    receipt = {
        "idempotencyKey": str(item.get("idempotency_key") or ""),
        "sourceType": str(item.get("source_type") or ""),
        "factKind": str(item.get("fact_kind") or ""),
        "timestamp": str(item.get("timestamp") or ""),
        "content": _repair_utf8_mojibake(item.get("content"))[:1000],
    }
    receipt["digest"] = _canonical_digest(receipt)
    return receipt


def _npc_memory_items(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    items = snapshot.get("items") if isinstance(snapshot, dict) else None
    receipts = [
        _npc_memory_receipt(item)
        for item in items or []
        if isinstance(item, dict)
        and str(item.get("idempotency_key") or "")
        and str(item.get("content") or "")
    ]
    return [receipt for receipt in receipts if "???" not in receipt["content"]]


def _council_source_record_id(
    game_server_id: int, npc_id: int, player_id: UUID, request_id: UUID
) -> str:
    return f"dongzhou-council:{game_server_id}:{npc_id}:{player_id}:{request_id}"


def _council_question_digest(
    request_payload: dict[str, Any], selected_option: dict[str, Any]
) -> str:
    return _canonical_digest(
        {
            "question": str(request_payload.get("question") or ""),
            "options": request_payload.get("options") or [],
            "selected": selected_option,
        }
    )


_ORGANIZATION_TASK_BASE_CHANCE = {
    "supply": 72,
    "drill": 68,
    "patrol": 74,
    "intelligence": 64,
    "diplomacy": 60,
}

_ORGANIZATION_TASK_OFFICES = {
    "supply": "司徒",
    "drill": "司马",
    "patrol": "司寇",
    "intelligence": "行人",
    "diplomacy": "上卿",
}

_TASK_EVIDENCE_KEYWORDS = {
    "supply": ("军粮", "粮秣", "粮", "补给", "转运", "辎重"),
    "drill": ("整军", "军阵", "操练", "训练", "强攻", "攻防", "战场", "调度"),
    "patrol": ("巡察", "巡", "营垒", "警戒", "守备", "防守"),
    "intelligence": ("探察", "军情", "情报", "谍", "侦察", "耳报", "心理"),
    "diplomacy": ("遣使", "使者", "诸侯", "盟", "议和", "交质", "交涉", "出使"),
}


def _evidence_task_fit(
    task_type: str,
    source: dict[str, Any],
    council_text: str,
    *,
    has_search_receipt: bool = False,
) -> dict[str, Any]:
    keywords = _TASK_EVIDENCE_KEYWORDS.get(task_type, ())
    tier = str(source.get("tier") or "")
    scope = str(source.get("scope") or "")
    signals: list[dict[str, Any]] = []
    factor = 0.0

    if any(marker in tier for marker in ("史实", "编年", "正史")):
        factor += 2.0
        signals.append({"kind": "sourceTier", "label": tier, "factor": 2.0})
    elif tier:
        factor += 1.0
        signals.append({"kind": "sourceTier", "label": tier, "factor": 1.0})

    scope_matches = [keyword for keyword in keywords if keyword in scope]
    if scope_matches:
        factor += 2.0
        signals.append({"kind": "sourceScope", "label": scope_matches[0], "factor": 2.0})

    council_matches = [keyword for keyword in keywords if keyword in council_text]
    if council_matches:
        factor += 4.0
        signals.append({"kind": "councilChoice", "label": council_matches[0], "factor": 4.0})

    if has_search_receipt:
        factor += 1.0
        signals.append({"kind": "searchReceipt", "label": "verified", "factor": 1.0})

    factor = min(9.0, factor)
    return {
        "taskType": task_type,
        "factor": factor,
        "band": "strong" if factor >= 7 else "aligned" if factor >= 4 else "weak",
        "signals": signals,
    }


def _stable_roll(value: str) -> int:
    result = 2166136261
    for byte in value.encode("utf-8"):
        result ^= byte
        result = (result * 16777619) & 0xFFFFFFFF
    return result % 100


def _organization_task_chance(
    task: dict[str, Any],
    task_type: str,
    member: dict[str, Any],
    mandate: dict[str, Any] | None = None,
) -> float:
    office_fit = 8 if str(member.get("office") or "") == _ORGANIZATION_TASK_OFFICES.get(task_type) else 0
    evidence_fit = mandate.get("evidenceFit") if isinstance(mandate, dict) else None
    knowledge_fit = (
        max(0.0, min(9.0, float(evidence_fit.get("factor"))))
        if isinstance(evidence_fit, dict)
        and evidence_fit.get("taskType") == task_type
        and isinstance(evidence_fit.get("factor"), (int, float))
        and not isinstance(evidence_fit.get("factor"), bool)
        else 6.0
        if task.get("knowledgeId")
        else 0.0
    )
    correspondence_fit = (
        8
        if isinstance(mandate, dict)
        and isinstance(mandate.get("correspondence"), dict)
        and task_type in {"diplomacy", "intelligence"}
        else 4
        if isinstance(mandate, dict)
        and isinstance(mandate.get("correspondence"), dict)
        else 0
    )
    loyalty = max(20.0, min(100.0, float(member.get("loyalty", 68) or 68)))
    fatigue = max(0.0, min(100.0, float(member.get("fatigue", 0) or 0)))
    assignment = mandate.get("assignment") if isinstance(mandate, dict) else None
    readiness = assignment.get("readiness") if isinstance(assignment, dict) else None
    readiness_score = (
        max(25.0, min(95.0, float(readiness.get("score"))))
        if isinstance(readiness, dict)
        and isinstance(readiness.get("score"), (int, float))
        and not isinstance(readiness.get("score"), bool)
        else 65.0
    )
    emergency = mandate.get("emergency") if isinstance(mandate, dict) else None
    emergency_fit = (
        8
        if isinstance(emergency, dict)
        and emergency.get("urgent") is True
        and task_type in {"intelligence", "patrol"}
        else 5
        if isinstance(emergency, dict) and emergency.get("urgent") is True
        else 0
    )
    return max(
        25.0,
        min(
            95.0,
            _ORGANIZATION_TASK_BASE_CHANCE.get(task_type, 60)
            + office_fit
            + knowledge_fit
            + correspondence_fit
            + emergency_fit
            + (loyalty - 60) * 0.2
            - fatigue * 0.22
            + (readiness_score - 65) * 0.5,
        ),
    )


def _organization_task_succeeds(
    task: dict[str, Any],
    task_type: str,
    member: dict[str, Any],
    mandate: dict[str, Any] | None = None,
) -> bool:
    loyalty = max(20.0, min(100.0, float(member.get("loyalty", 68) or 68)))
    chance = _organization_task_chance(task, task_type, member, mandate)
    roll_key = f"{task.get('id', '')}:{task.get('dueMonth', '')}:{int(loyalty) if loyalty.is_integer() else loyalty}"
    return _stable_roll(roll_key) < chance


def _organization_final_result(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    final_result = value.get("final_result") or value.get("finalResult")
    if isinstance(final_result, str) and final_result:
        return final_result
    state = str(value.get("state") or "").upper()
    mapped = {
        "SUCCEEDED": "SUCCESS",
        "PARTIALLY_COMPLETED": "PARTIAL",
        "FAILED": "FAILURE",
        "REJECTED": "FAILURE",
        "CANCELLED": "FAILURE",
        "INVALIDATED": "FAILURE",
    }.get(state)
    if mapped:
        return mapped
    for key in ("task", "record", "data", "result"):
        nested = _organization_final_result(value.get(key))
        if nested:
            return nested
    return None


def _organization_roster_view(
    snapshot: Any,
    settings: Settings,
    *,
    player_subject_id: str | None = None,
) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("roster snapshot must be an object")
    positions = snapshot.get("positions")
    members = snapshot.get("members")
    if not isinstance(positions, list) or not isinstance(members, list):
        raise ValueError("roster snapshot is incomplete")
    hero_by_member = {member_id: hero_id for hero_id, member_id in settings.orgflow_hero_members.items()}
    position_by_slot = {
        str(position.get("position_slot_id")): position
        for position in positions
        if isinstance(position, dict) and position.get("position_slot_id")
    }
    sanitized_members: list[dict[str, Any]] = []
    player_membership: dict[str, Any] | None = None
    for member in members:
        if not isinstance(member, dict):
            continue
        hero_id = hero_by_member.get(str(member.get("member_id") or ""))
        is_player = (
            player_subject_id is not None
            and member.get("subject_type") == "PLAYER"
            and str(member.get("subject_id") or "") == player_subject_id
        )
        if not hero_id and not is_player:
            continue
        position = position_by_slot.get(str(member.get("position_slot_id") or ""), {})
        manager_hero_id = hero_by_member.get(str(member.get("direct_manager_member_id") or ""))
        values = {
            key: member.get(source, 0)
            for key, source in (
                ("contributionBalance", "contribution_balance"),
                ("lifetimeEarned", "contribution_lifetime_earned"),
                ("lifetimeSpent", "contribution_lifetime_spent"),
            )
        }
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values.values()):
            raise ValueError("roster contribution account is invalid")
        if is_player:
            player_membership = {
                "office": str(position.get("position_display_name") or ""),
                "role": str(position.get("role_display_name") or ""),
                "level": str(position.get("level_key") or ""),
                "directManagerHeroId": manager_hero_id,
                **values,
            }
            continue
        sanitized_members.append(
            {
                "heroId": hero_id,
                "office": str(position.get("position_display_name") or ""),
                "role": str(position.get("role_display_name") or ""),
                "level": str(position.get("level_key") or ""),
                "directManagerHeroId": manager_hero_id,
                **values,
            }
        )
    growth = snapshot.get("growth_contribution_points", 0)
    hierarchy_version = snapshot.get("hierarchy_version", 0)
    if (
        isinstance(growth, bool)
        or not isinstance(growth, int)
        or isinstance(hierarchy_version, bool)
        or not isinstance(hierarchy_version, int)
    ):
        raise ValueError("roster organization account is invalid")
    return {
        "organization": {
            "name": str(snapshot.get("name") or ""),
            "state": str(snapshot.get("state") or ""),
            "hierarchyVersion": hierarchy_version,
            "growthContribution": growth,
        },
        "members": sanitized_members,
        "playerMembership": player_membership,
        "openPositions": [
            {
                "office": str(position.get("position_display_name") or ""),
                "role": str(position.get("role_display_name") or ""),
                "level": str(position.get("level_key") or ""),
            }
            for position in positions
            if isinstance(position, dict)
            and position.get("state") == "OPEN"
            and str(position.get("level_key") or "").lower() != "owner"
        ],
    }


def _organization_inventory_view(snapshot: Any, settings: Settings) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("inventory snapshot must be an object")
    organization_id = str(snapshot.get("organization_id") or "")
    game_server_id = str(snapshot.get("game_server_id") or "")
    revision = snapshot.get("revision")
    accounts = snapshot.get("accounts")
    if organization_id != settings.orgflow_org_id or game_server_id != str(settings.game_server_id):
        raise ValueError("inventory identity does not match configuration")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0 or not isinstance(accounts, list):
        raise ValueError("inventory snapshot is incomplete")
    sanitized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for account in accounts:
        if not isinstance(account, dict):
            raise ValueError("inventory account must be an object")
        resource_key = str(account.get("resource_key") or "").strip()
        balance = account.get("balance")
        version = account.get("version")
        if (
            not resource_key
            or resource_key in seen
            or isinstance(balance, bool)
            or not isinstance(balance, int)
            or balance < 0
            or isinstance(version, bool)
            or not isinstance(version, int)
            or version < 1
        ):
            raise ValueError("inventory account is invalid")
        seen.add(resource_key)
        sanitized.append({"resourceKey": resource_key, "balance": balance, "version": version})
    sanitized.sort(key=lambda item: item["resourceKey"])
    return {
        "organizationId": organization_id,
        "gameServerId": game_server_id,
        "revision": revision,
        "accounts": sanitized,
    }


def _organization_inventory_reward_view(
    snapshot: Any,
    settings: Settings,
    *,
    resource_key: str,
    delta_units: int,
) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("inventory reward must be an object")
    entry_id = str(snapshot.get("entry_id") or "")
    organization_id = str(snapshot.get("organization_id") or "")
    game_server_id = str(snapshot.get("game_server_id") or "")
    balance_after = snapshot.get("balance_after")
    account_version = snapshot.get("account_version_after")
    inventory_revision = snapshot.get("inventory_revision_after")
    try:
        UUID(entry_id)
    except ValueError as error:
        raise ValueError("inventory reward entry id is invalid") from error
    if (
        organization_id != settings.orgflow_org_id
        or game_server_id != str(settings.game_server_id)
        or snapshot.get("resource_key") != resource_key
        or snapshot.get("reason_code") != "TASK_SETTLEMENT_ACCEPTED"
        or snapshot.get("delta_units") != delta_units
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in (balance_after, account_version, inventory_revision)
        )
    ):
        raise ValueError("inventory reward does not match settlement")
    return {
        "entryId": entry_id,
        "resourceKey": resource_key,
        "delta": delta_units,
        "balanceAfter": balance_after,
        "accountVersion": account_version,
        "inventoryRevision": inventory_revision,
    }


def _organization_inventory_requisition_view(
    snapshot: Any,
    settings: Settings,
    *,
    resource_key: str,
    delta_units: int,
) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("inventory requisition must be an object")
    entry_id = str(snapshot.get("entry_id") or "")
    balance_after = snapshot.get("balance_after")
    account_version = snapshot.get("account_version_after")
    inventory_revision = snapshot.get("inventory_revision_after")
    try:
        UUID(entry_id)
    except ValueError as error:
        raise ValueError("inventory requisition entry id is invalid") from error
    if (
        str(snapshot.get("organization_id") or "") != settings.orgflow_org_id
        or str(snapshot.get("game_server_id") or "") != str(settings.game_server_id)
        or snapshot.get("resource_key") != resource_key
        or snapshot.get("reason_code") != "CAMPAIGN_REQUISITION_APPROVED"
        or snapshot.get("delta_units") != delta_units
        or isinstance(balance_after, bool)
        or not isinstance(balance_after, int)
        or balance_after < 0
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in (account_version, inventory_revision)
        )
    ):
        raise ValueError("inventory requisition does not match request")
    return {
        "entryId": entry_id,
        "resourceKey": resource_key,
        "delta": delta_units,
        "balanceAfter": balance_after,
        "accountVersion": account_version,
        "inventoryRevision": inventory_revision,
    }


def _organization_supervision_links(
    roster: dict[str, Any], mapped_npcs: list[dict[str, str]], organization_id: str,
) -> list[dict[str, Any]]:
    npc_by_hero = {npc["heroId"]: npc["npcId"] for npc in mapped_npcs}
    links: list[dict[str, str]] = []
    for member in roster.get("members", []):
        if not isinstance(member, dict):
            continue
        hero_id = str(member.get("heroId") or "")
        manager_hero_id = str(member.get("directManagerHeroId") or "")
        subordinate_npc_id = npc_by_hero.get(hero_id)
        manager_npc_id = npc_by_hero.get(manager_hero_id)
        if not subordinate_npc_id or (manager_npc_id is not None and subordinate_npc_id == manager_npc_id):
            continue
        links.append({
            "heroId": hero_id,
            "managerHeroId": manager_hero_id,
            "subordinateNpcId": subordinate_npc_id,
            "managerNpcId": manager_npc_id,
            "sourceEventId": f"orgflow:{organization_id}:supervision:{hero_id}:{manager_hero_id or 'none'}",
        })
    return links


async def _sync_organization_supervision(
    upstreams: Upstreams, settings: Settings, mapped_npcs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    if not settings.orgflow_org_id or not settings.orgflow_hero_members:
        return []
    roster_response = await upstreams.organization_roster(settings.orgflow_org_id)
    roster = _organization_roster_view(roster_response.get("data"), settings)
    links = _organization_supervision_links(roster, mapped_npcs, settings.orgflow_org_id)
    receipts = await asyncio.gather(*(
        upstreams.ensure_organization_supervision(
            subordinate_npc_id=link["subordinateNpcId"],
            manager_npc_id=link["managerNpcId"],
            source_event_id=link["sourceEventId"],
        )
        for link in links
    ))
    return [
        {
            **link,
            "created": receipt["created"],
            "deactivatedManagerNpcIds": receipt.get("deactivatedManagerNpcIds", []),
            "relationshipIds": receipt["relationshipIds"],
        }
        for link, receipt in zip(links, receipts, strict=True)
    ]


_SETTLING_RESULTS = {"SUCCESS", "PARTIAL", "FAILURE", "REJECTED"}
_SETTLEMENT_SOURCES = {
    "PLAYER_CONFIRMATION",
    "NPC_CONFIRMATION",
    "AI_TIMEOUT",
    "RULE_FALLBACK",
    "SYSTEM_RULE",
}


def _bounded_settlement_delta(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{field}_invalid")
    text = str(value)
    if not text or text == "-0" or (
        text[0] == "-" and (len(text) == 1 or not text[1:].isdigit())
    ) or (text[0] != "-" and not text.isdigit()):
        raise ValueError(f"{field}_invalid")
    if (text.startswith("0") and len(text) > 1) or text.startswith("-0"):
        raise ValueError(f"{field}_invalid")
    parsed = int(text)
    if abs(parsed) > 1_000_000:
        raise ValueError(f"{field}_invalid")
    return parsed


def _authoritative_settlement(
    snapshot: dict[str, Any],
    *,
    task_id: str,
    organization_id: str,
    member_id: str,
) -> dict[str, Any] | None:
    final_result = snapshot.get("final_result")
    if final_result not in _SETTLING_RESULTS:
        return None
    settlement = snapshot.get("settlement")
    if not isinstance(settlement, dict):
        if snapshot.get("contribution_eligible") is False:
            return None
        raise ValueError("settlement_missing")
    settlement_id = str(settlement.get("settlement_id") or "")
    try:
        UUID(settlement_id)
    except ValueError as error:
        raise ValueError("settlement_id_invalid") from error
    if (
        str(snapshot.get("task_id") or "") != task_id
        or str(snapshot.get("organization_id") or "") != organization_id
        or snapshot.get("contribution_eligible") is not True
        or str(snapshot.get("responsible_member_id") or member_id) != member_id
        or str(settlement.get("task_id") or "") != task_id
        or str(settlement.get("organization_id") or "") != organization_id
        or str(settlement.get("member_id") or "") != member_id
        or settlement.get("result") != final_result
        or settlement.get("source") not in _SETTLEMENT_SOURCES
    ):
        raise ValueError("settlement_ownership_invalid")
    organization_delta = _bounded_settlement_delta(
        settlement.get("organization_delta"), "organization_delta"
    )
    member_delta = _bounded_settlement_delta(
        settlement.get("member_delta"), "member_delta"
    )
    if final_result in {"SUCCESS", "PARTIAL"} and (
        organization_delta < 0 or member_delta < 0
    ):
        raise ValueError("settlement_delta_invalid")
    if final_result == "FAILURE" and (
        organization_delta > 0 or member_delta != 0
    ):
        raise ValueError("settlement_delta_invalid")
    if final_result == "REJECTED" and (
        organization_delta != 0 or member_delta > 0
    ):
        raise ValueError("settlement_delta_invalid")
    source_event_id = str(settlement.get("source_event_id") or "")
    settled_at = str(settlement.get("settled_at") or "")
    if not source_event_id or len(source_event_id) > 256 or not settled_at:
        raise ValueError("settlement_evidence_invalid")
    return {
        "settlementId": settlement_id,
        "taskId": task_id,
        "organizationId": organization_id,
        "memberId": member_id,
        "result": final_result,
        "organizationDelta": organization_delta,
        "memberDelta": member_delta,
        "source": settlement["source"],
        "sourceEventId": source_event_id,
        "settledGameTime": settlement.get("settled_game_time"),
        "settledClockEpoch": settlement.get("settled_clock_epoch"),
        "settledAt": settled_at,
    }


def _closure_receipt(
    *,
    task_id: str,
    original: dict[str, Any],
    settlement: dict[str, Any],
) -> dict[str, Any]:
    parameters = original.get("parameters")
    parameters = parameters if isinstance(parameters, dict) else {}
    trace = {
        "taskId": task_id,
        "mandateId": parameters.get("mandate_id"),
        "mandateDigest": parameters.get("mandate_digest"),
        "settlement": settlement,
        "kernel": {
            "module": RuntimeModule.name,
            "moduleVersion": RuntimeModule.version,
            "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
        },
    }
    digest = hashlib.sha256(
        json.dumps(
            trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()
    return {
        "receiptId": "dongzhou:closure:" + settlement["settlementId"],
        **trace,
        "digest": digest,
        "state": "SEALED",
    }


def _derived_follow_ups(
    task_id: str,
    original: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    derivations = snapshot.get("derivations")
    if derivations is None:
        return []
    if not isinstance(derivations, list) or len(derivations) > 8:
        raise ValueError("organization_derivations_invalid")
    final_result = str(snapshot.get("final_result") or "")
    expected_source = {
        "SUCCESS": "FOLLOW_UP",
        "PARTIAL": "FOLLOW_UP",
        "FAILURE": "REMEDIATION",
    }.get(final_result)
    source_task_type = str(original.get("task_type") or "")
    follow_up_targets = {
        "diplomacy": "intelligence",
        "drill": "supply",
        "intelligence": "patrol",
        "patrol": "drill",
        "supply": "patrol",
    }
    success_targets = {
        "diplomacy": "supply",
        "drill": "patrol",
        "intelligence": "diplomacy",
        "patrol": "intelligence",
        "supply": "patrol",
    }
    if source_task_type not in follow_up_targets:
        raise ValueError("organization_derivation_source_invalid")
    expected_target = (
        success_targets[source_task_type]
        if final_result == "SUCCESS"
        else follow_up_targets[source_task_type]
    )
    expected_rule_suffix = {
        "SUCCESS": "success_follow_up",
        "PARTIAL": "partial_follow_up",
        "FAILURE": "failure_remediation",
    }.get(final_result)
    expected_defaults = {
        "assignee_hero_id": "unassigned",
        "assignee_name": "Unassigned",
        "resource_units": 0,
        "stage_id": "unknown",
        "stage_title": "Unknown stage",
    }
    follow_ups: list[dict[str, Any]] = []
    for derivation in derivations:
        if not isinstance(derivation, dict):
            raise ValueError("organization_derivation_invalid")
        if str(derivation.get("predecessor_task_id") or "") != task_id:
            continue
        if (
            expected_source is None
            or derivation.get("state") not in {"PENDING", "CREATED", "SKIPPED"}
            or str(derivation.get("root_task_id") or "") != task_id
            or derivation.get("generation_depth") != 1
            or derivation.get("trigger_result") != final_result
            or derivation.get("source") != expected_source
            or derivation.get("target_position_selector") != "SAME_POSITION"
            or derivation.get("parameter_strategy") != "TARGET_DEFAULTS"
            or derivation.get("target_position_slot_id") != snapshot.get("position_slot_id")
            or derivation.get("target_default_parameters") != expected_defaults
        ):
            raise ValueError("organization_derivation_invalid")
        target_code = str(derivation.get("target_task_code") or "")
        task_type = target_code.removeprefix("dongzhou.")
        expected_rule = f"dongzhou_{source_task_type}_{expected_rule_suffix}"
        if task_type != expected_target or derivation.get("rule_id") != expected_rule:
            raise ValueError("organization_derivation_target_invalid")
        state = str(derivation["state"])
        intent_id = str(derivation.get("intent_id") or "")
        planned_task_id = str(derivation.get("planned_task_id") or "")
        created_task_id = str(derivation.get("created_task_id") or "")
        UUID(intent_id)
        UUID(planned_task_id)
        if state == "CREATED":
            if created_task_id != planned_task_id:
                raise ValueError("organization_derivation_task_invalid")
            UUID(created_task_id)
        elif created_task_id:
            raise ValueError("organization_derivation_task_invalid")
        follow_ups.append(
            {
                "intentId": intent_id,
                "taskId": created_task_id or None,
                "state": state,
                "source": expected_source,
                "taskType": task_type,
                "ruleId": expected_rule,
                "stageId": str(original.get("stage_id") or ""),
                "stageTitle": str(original.get("stage_title") or ""),
                "assigneeHeroId": str(original.get("assignee_hero_id") or ""),
            }
        )
    return follow_ups


def _npc_outcome_event(outcome: dict[str, Any], final_result: str) -> dict[str, Any]:
    normalized = str(final_result or "FAILURE").upper()
    if normalized in {"SUCCESS", "SUCCEEDED"}:
        normalized = "SUCCESS"
        result_text = "办成"
    elif normalized in {"PARTIAL", "PARTIALLY_COMPLETED"}:
        normalized = "PARTIAL"
        result_text = "部分办成"
    else:
        normalized = "FAILURE"
        result_text = "未能办成"
    task_id = str(outcome["task_id"])
    event_digest = hashlib.sha256(
        f"dongzhou-org-outcome:{task_id}".encode("utf-8")
    ).digest()
    event_id = int.from_bytes(event_digest[:4], "big") & 0x7FFFFFFF or 1
    npc_name = str(outcome.get("npc_name") or outcome.get("hero_id") or "属官")
    task_name = str(outcome.get("task_name") or outcome.get("task_type") or "官署差事")
    stage_title = str(outcome.get("stage_title") or outcome.get("stage_id") or "本关")
    description = f"{npc_name}在《{stage_title}》的官署差事“{task_name}”{result_text}。"
    metadata = {
        key: outcome[key]
        for key in (
            "task_id",
            "task_type",
            "stage_id",
            "stage_title",
            "hero_id",
            "manager_npc_id",
            "mandate_id",
            "mandate_digest",
            "knowledge_id",
            "evidence_source",
            "readiness",
            "planned_result",
        )
        if outcome.get(key) is not None
    }
    metadata.update(
        {
            "source_module": "dongzhou_integration",
            "final_result": normalized,
            "description": description,
            "motivation_policy": "external_authoritative",
        }
    )
    return {
        "game_server_id": str(outcome["game_server_id"]),
        "npc_id": str(outcome["npc_id"]),
        "npc_name": npc_name,
        "game_time": str(outcome["game_time"]),
        "events": [
            {
                "source_record_id": task_id,
                "timestamp": str(outcome["game_time"]),
                "event_id": event_id,
                "event_name": "官署差事复命",
                "event_type": "organization_task_result",
                "params": description,
                "metadata": metadata,
                "interrupt_trace_id": "dongzhou-org-outcome:" + task_id,
            }
        ],
    }


def _npc_outcome_memory(outcome: dict[str, Any], final_result: str) -> dict[str, Any]:
    return _npc_memory_from_event(_npc_outcome_event(outcome, final_result))


def _npc_quality_from_event(event: dict[str, Any]) -> dict[str, Any]:
    detail = event["events"][0]
    metadata = detail.get("metadata") if isinstance(detail.get("metadata"), dict) else {}
    final_result = str(metadata.get("final_result") or "FAILURE").upper()
    task_type = str(metadata.get("task_type") or "").casefold()
    quality = {
        "intelligence": "trustworthiness",
        "diplomacy": "fairness",
    }.get(task_type, "responsibility")
    delta = 2.0 if final_result == "SUCCESS" else 0.5 if final_result == "PARTIAL" else -1.0
    task_id = str(detail["source_record_id"])
    return {
        "settlement_effect_id": "dongzhou-org-quality:" + task_id + ":v1",
        "game_server_id": str(event["game_server_id"]),
        "npc_id": str(event["npc_id"]),
        "quality": quality,
        "delta": delta,
        "reason": f"authoritative organization duty result: {final_result.casefold()}",
        "related_event_id": str(detail["event_id"]),
        "confidence": 1.0,
    }


def _npc_outcome_quality(outcome: dict[str, Any], final_result: str) -> dict[str, Any]:
    return _npc_quality_from_event(_npc_outcome_event(outcome, final_result))


def _npc_motivation_from_event(event: dict[str, Any]) -> dict[str, Any]:
    detail = event["events"][0]
    metadata = detail.get("metadata") if isinstance(detail.get("metadata"), dict) else {}
    final_result = str(metadata.get("final_result") or "FAILURE").upper()
    task_type = str(metadata.get("task_type") or "").casefold()
    motive_name = {
        "supply": "再办军粮转运",
        "drill": "再整训军阵",
        "patrol": "再巡察营垒",
        "intelligence": "再核验情报",
        "diplomacy": "再周旋诸侯",
    }.get(task_type, "再尽官署职责")
    score, urgency, importance = {
        "SUCCESS": (8.0, "low", 35.0),
        "PARTIAL": (18.0, "medium", 55.0),
        "FAILURE": (30.0, "high", 75.0),
    }.get(final_result, (30.0, "high", 75.0))
    task_id = str(detail["source_record_id"])
    return {
        "npc_id": str(event["npc_id"]),
        "operation_id": "dongzhou-org-motivation:" + task_id + ":v1",
        "game_server_id": str(event["game_server_id"]),
        "source": "dongzhou_org_task",
        "urgency_level": urgency,
        "event_description": str(detail.get("params") or "authoritative organization duty result"),
        "event_importance": importance,
        "motive_updates": [{
            "motive_name": motive_name,
            "score": score,
            "reason": f"authoritative organization duty result: {final_result.casefold()}",
        }],
        "current_time": str(event.get("game_time") or detail.get("timestamp") or ""),
        "extra_data": {
            "task_id": task_id,
            "task_type": task_type,
            "final_result": final_result,
            "event_id": str(detail["event_id"]),
        },
    }


def _npc_outcome_motivation(outcome: dict[str, Any], final_result: str) -> dict[str, Any]:
    return _npc_motivation_from_event(_npc_outcome_event(outcome, final_result))


def _npc_censure_events(
    settings: Settings,
    player_id: UUID,
    *,
    task_id: str,
    hero_id: str,
    npc_name: str,
    game_time: str,
    review_digest: str,
) -> list[dict[str, Any]]:
    npc_id = str(stable_npc_id(settings.ainpc_game_server_id, hero_id))
    player_target_id = str(stable_player_id(settings.ainpc_game_server_id, player_id))
    identity_digest = hashlib.sha256(
        f"{player_id}\n{task_id}\n{hero_id}\n{review_digest}\ncensure-v1".encode("utf-8")
    ).hexdigest()
    source_record_id = "dongzhou-censure:" + identity_digest[:48]
    event_id = int.from_bytes(bytes.fromhex(identity_digest[:8]), "big") & 0x7FFFFFFF or 1
    description = f"{npc_name}因官署差事复命遭主君申斥，功过照录但本次战前助益不予采纳。"
    outcome = {
        "game_server_id": str(settings.ainpc_game_server_id),
        "npc_id": npc_id,
        "npc_name": npc_name,
        "game_time": game_time,
        "events": [{
            "source_record_id": source_record_id,
            "timestamp": game_time,
            "event_id": event_id,
            "event_name": "官署复命遭申斥",
            "event_type": "organization_review_censure",
            "params": description,
            "metadata": {
                "standard_event_authority": "game_server",
                "event_instance_id": source_record_id,
                "actor_id": player_target_id,
                "target_id": npc_id,
                "behavior_parent": "insult",
                "behavior_sub": "official_censure",
                "motivation": "organization_accountability",
                "result": "censured",
                "result_confirmed": True,
                "severity": 58,
                "confidence": 1.0,
                "source_module": "dongzhou_settlement_review",
                "task_id": task_id,
                "hero_id": hero_id,
                "review_digest": review_digest,
                "description": description,
            },
            "interrupt_trace_id": source_record_id,
        }],
    }
    memory = {
        "game_server_id": str(settings.ainpc_game_server_id),
        "npc_id": npc_id,
        "npc_name": npc_name,
        "game_time": game_time,
        "messages": [{
            "timestamp": game_time,
            "content": description,
            "message_id": "dongzhou-censure-memory:" + identity_digest[:48],
        }],
    }
    affection = {
        "settlement_effect_id": "dongzhou-censure-affection:" + identity_digest,
        "game_server_id": str(settings.ainpc_game_server_id),
        "npc_id": npc_id,
        "target_id": player_target_id,
        "changes": [{
            "affection_type": "annoyance",
            "delta": 5.8,
            "reason": "confirmed official censure for organization accountability",
            "confidence": 1.0,
        }],
        "related_event_id": str(event_id),
    }
    return [
        {"eventId": "settlement-censure:" + identity_digest, "kind": "NPC_TASK_OUTCOME", "payload": outcome},
        {"eventId": "settlement-censure-memory:" + identity_digest, "kind": "NPC_TASK_MEMORY", "payload": memory},
        {"eventId": "settlement-censure-affection:" + identity_digest, "kind": "NPC_AFFECTION_SETTLEMENT", "payload": affection},
    ]


def _npc_memory_from_event(event: dict[str, Any]) -> dict[str, Any]:
    detail = event["events"][0]
    task_id = str(detail["source_record_id"])
    return {
        "game_server_id": event["game_server_id"],
        "npc_id": event["npc_id"],
        "npc_name": event["npc_name"],
        "game_time": event["game_time"],
        "messages": [
            {
                "timestamp": event["game_time"],
                "content": detail["params"],
                "message_id": "dongzhou-org-outcome:" + task_id,
            }
        ],
    }


class BattleReceiptConflict(ValueError):
    pass


def _battle_report_signature(report: dict[str, Any]) -> dict[str, Any]:
    support = report.get("support") if isinstance(report.get("support"), dict) else {}

    def references(entries: Any, hero_key: str) -> list[dict[str, str]]:
        if not isinstance(entries, list):
            return []
        return sorted(
            (
                {
                    "id": str(entry.get("id") or ""),
                    "heroId": str(entry.get(hero_key) or ""),
                }
                for entry in entries
                if isinstance(entry, dict)
            ),
            key=lambda entry: (entry["id"], entry["heroId"]),
        )

    return {
        "reportId": str(report.get("id") or ""),
        "stageId": str(report.get("stageId") or ""),
        "won": report.get("won"),
        "turns": report.get("turns"),
        "ownLosses": report.get("ownLosses"),
        "terminalReason": str(report.get("terminalReason") or ""),
        "month": report.get("month"),
        "councils": references(report.get("councils"), "memberId"),
        "mandates": references(report.get("mandates"), "heroId"),
        "orders": references(support.get("orders"), "memberId"),
    }


def _digest_json(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _knowledge_quiz_trace(
    request_id: UUID,
    stage_id: str,
    entries: list[dict[str, Any]],
    catalog_path: Any,
    deadline_at: datetime,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    published = next((entry for entry in entries if isinstance(entry, dict)), None)
    if published is None:
        raise ValueError("published_stage_knowledge_missing")
    entities = published.get("entities")
    raw_npcs = entities.get("npcs", []) if isinstance(entities, dict) else []
    current_people = []
    for item in raw_npcs:
        name = item.get("name") if isinstance(item, dict) else item
        name = str(name or "").strip()
        if name and name not in current_people:
            current_people.append(name)
    if not current_people:
        raise ValueError("published_stage_people_missing")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    distractors: list[str] = []
    for entry in catalog.get("entries", []):
        if not isinstance(entry, dict) or str(entry.get("stageId") or "") == stage_id:
            continue
        for person in entry.get("people", []):
            person = str(person or "").strip()
            if person and person not in current_people and person not in distractors:
                distractors.append(person)
    if len(distractors) < 3:
        raise ValueError("knowledge_quiz_distractors_missing")

    seed = hashlib.sha256(f"{request_id}:{stage_id}".encode("utf-8")).hexdigest()
    correct_name = current_people[int(seed[:8], 16) % len(current_people)]
    distractors.sort(
        key=lambda name: hashlib.sha256(f"{seed}:distractor:{name}".encode("utf-8")).hexdigest()
    )
    options = [correct_name, *distractors[:3]]
    options.sort(
        key=lambda name: hashlib.sha256(f"{seed}:option:{name}".encode("utf-8")).hexdigest()
    )
    source_details = published.get("sourceDetails")
    source = next(
        (item for item in source_details or [] if isinstance(item, dict)),
        None,
    )
    knowledge_id = str(published.get("id") or published.get("aku_id") or "")
    title = str(published.get("name") or "本回史录")
    trace = {
        "id": str(request_id),
        "stageId": stage_id,
        "knowledgeId": knowledge_id,
        "title": title,
        "prompt": f"下列哪位人物见于《{title}》的已发布人物录？",
        "options": options,
        "correctIndex": options.index(correct_name),
        "deadlineAt": deadline_at.isoformat().replace("+00:00", "Z"),
    }
    return trace, source


async def _battle_support_attestations(
    store: Store,
    player_id: UUID,
    previous_payload: dict[str, Any],
    submitted_payload: dict[str, Any],
) -> dict[str, set[str]]:
    organization = submitted_payload.get("organization")
    previous_organization = previous_payload.get("organization")
    if not isinstance(organization, dict) or not isinstance(previous_organization, dict):
        return {"councils": set(), "mandates": set(), "orders": set()}

    reports = organization.get("battleReports")
    if not isinstance(reports, list):
        return {"councils": set(), "mandates": set(), "orders": set()}
    councils: dict[str, tuple[str, str]] = {}
    mandates: dict[str, tuple[str, str]] = {}
    orders: dict[str, str] = {}
    for report in reports[-40:]:
        if not isinstance(report, dict):
            continue
        report_councils = report.get("councils")
        for council in report_councils if isinstance(report_councils, list) else []:
            if isinstance(council, dict) and council.get("id"):
                councils[str(council["id"])] = (
                    str(council.get("memberId") or ""),
                    str(report.get("stageId") or ""),
                )
        report_mandates = report.get("mandates")
        for mandate in report_mandates if isinstance(report_mandates, list) else []:
            if isinstance(mandate, dict) and mandate.get("id"):
                mandates[str(mandate["id"])] = (
                    str(mandate.get("heroId") or ""),
                    str(mandate.get("digest") or ""),
                )
        support = report.get("support")
        if not isinstance(support, dict):
            continue
        support_orders = support.get("orders")
        for order in support_orders if isinstance(support_orders, list) else []:
            if isinstance(order, dict) and order.get("id") and order.get("memberId"):
                orders[str(order["id"])] = str(order["memberId"])

    attested = {"councils": set(), "mandates": set(), "orders": set()}
    previous_councils = {
        str(council.get("id")): council
        for council in previous_organization.get("councils", [])
        if isinstance(council, dict) and council.get("id")
    }
    for council_id, (hero_id, stage_id) in councils.items():
        try:
            request_id = UUID(council_id)
        except ValueError:
            continue
        record = await store.read_request(player_id, request_id, "npc_decision")
        request = record.get("request") if record else None
        response = record.get("response") if record else None
        raw_decision = response.get("decision") if isinstance(response, dict) else None
        decision = raw_decision.get("data", raw_decision) if isinstance(raw_decision, dict) else None
        source = previous_councils.get(council_id)
        request_options = request.get("options") if isinstance(request, dict) else None
        source_options = source.get("options") if isinstance(source, dict) else None
        option_texts = [
            str(option.get("text") or "")
            for option in request_options
            if isinstance(option, dict)
        ] if isinstance(request_options, list) else []
        selected_index = decision.get("index") if isinstance(decision, dict) else None
        selected_text = (
            option_texts[selected_index]
            if isinstance(selected_index, int) and 0 <= selected_index < len(option_texts)
            else None
        )
        if (
            record
            and record.get("state") == "COMPLETED"
            and isinstance(request, dict)
            and isinstance(source, dict)
            and isinstance(decision, dict)
            and str(request.get("hero_id") or "") == hero_id
            and str(request.get("stage_id") or "") == stage_id
            and str(source.get("memberId") or "") == hero_id
            and str(source.get("stageId") or "") == stage_id
            and request.get("question") == source.get("question")
            and option_texts == source_options
            and decision.get("type") == "OPTION"
            and selected_index == source.get("index")
            and selected_text == source.get("text")
        ):
            attested["councils"].add(council_id)

    for mandate_id, (hero_id, digest) in mandates.items():
        try:
            request_id = UUID(mandate_id.rsplit(":", 1)[-1])
        except ValueError:
            continue
        record = await store.read_request(player_id, request_id, "court_mandate")
        response = record.get("response") if record else None
        mandate = response.get("mandate") if isinstance(response, dict) else None
        if (
            record
            and record.get("state") == "ISSUED"
            and isinstance(mandate, dict)
            and mandate.get("id") == mandate_id
            and mandate.get("state") == "ISSUED"
            and str(mandate.get("heroId") or "") == hero_id
            and str(mandate.get("digest") or "") == digest
        ):
            attested["mandates"].add(mandate_id)

    previous_tasks = {
        str(task.get("id")): task
        for task in previous_organization.get("tasks", [])
        if isinstance(task, dict) and task.get("id")
    }
    for order_id, hero_id in orders.items():
        task = previous_tasks.get(order_id)
        remote_id = str(task.get("remoteResult") or "") if task else ""
        if not task or not remote_id:
            continue
        record = await store.read_external_request_record(
            player_id, remote_id, "organization_task"
        )
        original = record.get("request") if record else None
        response = record.get("response") if record else None
        terminal = response.get("terminal") if isinstance(response, dict) else None
        settlement = terminal.get("settlement") if isinstance(terminal, dict) else None
        closure = terminal.get("closureReceipt") if isinstance(terminal, dict) else None
        task_closure = task.get("closureReceipt")
        if (
            isinstance(original, dict)
            and isinstance(settlement, dict)
            and isinstance(closure, dict)
            and isinstance(task_closure, dict)
            and str(original.get("assignee_hero_id") or "") == hero_id
            and str(original.get("stage_id") or "") == str(task.get("stageId") or "")
            and settlement.get("result") in {"SUCCESS", "PARTIAL"}
            and closure.get("state") == "SEALED"
            and closure.get("digest") == task_closure.get("digest")
        ):
            attested["orders"].add(order_id)
    return attested


def _seal_battle_reports(
    player_id: UUID,
    previous_payload: dict[str, Any],
    submitted_payload: dict[str, Any],
    attestations: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    payload = deepcopy(submitted_payload)
    organization = payload.get("organization")
    if not isinstance(organization, dict):
        return payload
    reports = organization.get("battleReports")
    if not isinstance(reports, list):
        return payload

    previous_organization = previous_payload.get("organization")
    if not isinstance(previous_organization, dict):
        previous_organization = {}
    previous_reports = {
        str(report.get("id")): report
        for report in previous_organization.get("battleReports", [])
        if isinstance(report, dict) and report.get("id")
    }
    previous_councils = {
        str(council.get("id")): council
        for council in previous_organization.get("councils", [])
        if isinstance(council, dict) and council.get("id")
    }
    previous_mandates = {
        str(mandate.get("id")): mandate
        for mandate in previous_organization.get("mandates", [])
        if isinstance(mandate, dict) and mandate.get("id")
    }
    previous_tasks = {
        str(task.get("id")): task
        for task in previous_organization.get("tasks", [])
        if isinstance(task, dict) and task.get("id")
    }
    previous_members = {
        str(member.get("id"))
        for member in previous_organization.get("members", [])
        if isinstance(member, dict) and member.get("id")
    }
    previous_support = {
        str(entry.get("id")): entry
        for entry in previous_organization.get("pendingSupport", [])
        if isinstance(entry, dict) and entry.get("id")
    }

    for report in reports[-40:]:
        if not isinstance(report, dict):
            continue
        report_id = str(report.get("id") or "").strip()
        stage_id = str(report.get("stageId") or "").strip()
        if not report_id or not stage_id or not isinstance(report.get("won"), bool):
            report.pop("kernelReceipt", None)
            continue
        signature = _battle_report_signature(report)
        report_digest = _digest_json(signature)
        previous_report = previous_reports.get(report_id)
        if previous_report is not None:
            previous_receipt = previous_report.get("kernelReceipt")
            if not isinstance(previous_receipt, dict):
                report.pop("kernelReceipt", None)
                continue
            receipt_trace = {
                key: value
                for key, value in previous_receipt.items()
                if key != "digest"
            }
            if (
                previous_receipt.get("digest") != _digest_json(receipt_trace)
                or previous_receipt.get("reportDigest") != report_digest
            ):
                raise BattleReceiptConflict("battle_report_changed_after_seal")
            report["kernelReceipt"] = deepcopy(previous_receipt)
            continue

        report.pop("kernelReceipt", None)
        eligible_support = {
            support_id: entry
            for support_id, entry in previous_support.items()
            if not entry.get("stageId") or str(entry.get("stageId")) == stage_id
        }
        verified_councils: list[dict[str, str]] = []
        verified_mandates: list[dict[str, str]] = []
        verified_orders: list[dict[str, str]] = []
        rejected_support: list[dict[str, str]] = []
        participants: set[str] = set()

        report_councils = report.get("councils")
        for council in report_councils if isinstance(report_councils, list) else []:
            if not isinstance(council, dict):
                raise BattleReceiptConflict("battle_council_reference_invalid")
            council_id = str(council.get("id") or "")
            hero_id = str(council.get("memberId") or "")
            source = previous_councils.get(council_id)
            support_match = any(
                isinstance(entry.get("council"), dict)
                and str(entry["council"].get("id") or "") == council_id
                for entry in eligible_support.values()
            )
            if (
                not source
                or not support_match
                or str(source.get("stageId") or "") != stage_id
                or str(source.get("memberId") or "") != hero_id
                or hero_id not in previous_members
            ):
                raise BattleReceiptConflict("battle_council_reference_invalid")
            if attestations is not None and council_id not in attestations.get("councils", set()):
                rejected_support.append({
                    "kind": "council",
                    "id": council_id,
                    "reason": "server_attestation_missing",
                })
                continue
            verified_councils.append({"id": council_id, "heroId": hero_id})
            participants.add(hero_id)

        report_mandates = report.get("mandates")
        for mandate in report_mandates if isinstance(report_mandates, list) else []:
            if not isinstance(mandate, dict):
                raise BattleReceiptConflict("battle_mandate_reference_invalid")
            mandate_id = str(mandate.get("id") or "")
            hero_id = str(mandate.get("heroId") or "")
            source = previous_mandates.get(mandate_id)
            support_match = any(
                isinstance(entry.get("mandate"), dict)
                and str(entry["mandate"].get("id") or "") == mandate_id
                for entry in eligible_support.values()
            )
            if (
                not source
                or not support_match
                or str(source.get("stageId") or "") != stage_id
                or str(source.get("heroId") or "") != hero_id
                or str(source.get("digest") or "") != str(mandate.get("digest") or "")
                or hero_id not in previous_members
            ):
                raise BattleReceiptConflict("battle_mandate_reference_invalid")
            if attestations is not None and mandate_id not in attestations.get("mandates", set()):
                rejected_support.append({
                    "kind": "mandate",
                    "id": mandate_id,
                    "reason": "server_attestation_missing",
                })
                continue
            verified_mandates.append(
                {"id": mandate_id, "heroId": hero_id, "digest": str(source.get("digest"))}
            )
            participants.add(hero_id)

        support = report.get("support") if isinstance(report.get("support"), dict) else {}
        support_orders = support.get("orders")
        for order in support_orders if isinstance(support_orders, list) else []:
            if not isinstance(order, dict):
                raise BattleReceiptConflict("battle_order_reference_invalid")
            order_id = str(order.get("id") or "")
            hero_id = str(order.get("memberId") or "")
            support_entry = eligible_support.get(order_id)
            task = previous_tasks.get(order_id)
            if not support_entry:
                raise BattleReceiptConflict("battle_order_reference_invalid")
            expected_hero = str(support_entry.get("memberId") or "")
            if hero_id != expected_hero:
                raise BattleReceiptConflict("battle_order_reference_invalid")
            if hero_id and (
                not task
                or str(task.get("stageId") or "") != stage_id
                or str(task.get("assigneeId") or "") != hero_id
                or hero_id not in previous_members
            ):
                raise BattleReceiptConflict("battle_order_reference_invalid")
            if (
                hero_id
                and attestations is not None
                and order_id not in attestations.get("orders", set())
            ):
                rejected_support.append({
                    "kind": "order",
                    "id": order_id,
                    "reason": "server_attestation_missing",
                })
                continue
            verified_orders.append({"id": order_id, "heroId": hero_id})
            if hero_id:
                participants.add(hero_id)

        receipt_trace = {
            "id": str(
                uuid5(
                    NAMESPACE_URL,
                    f"dongzhou-battle-receipt:{player_id}:{report_id}",
                )
            ),
            "reportId": report_id,
            "reportDigest": report_digest,
            "stageId": stage_id,
            "won": report["won"],
            "turns": report.get("turns"),
            "ownLosses": report.get("ownLosses"),
            "terminalReason": str(report.get("terminalReason") or ""),
            "month": report.get("month"),
            "verifiedParticipants": sorted(participants),
            "verifiedSupport": {
                "councils": sorted(verified_councils, key=lambda entry: entry["id"]),
                "mandates": sorted(verified_mandates, key=lambda entry: entry["id"]),
                "orders": sorted(verified_orders, key=lambda entry: entry["id"]),
            },
            "rejectedSupport": sorted(
                rejected_support,
                key=lambda entry: (entry["kind"], entry["id"]),
            ),
            "kernel": {
                "module": MandateWorkflowModule.name,
                "moduleVersion": MandateWorkflowModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": "SEALED",
            },
        }
        report["kernelReceipt"] = {
            **receipt_trace,
            "digest": _digest_json(receipt_trace),
        }
    return payload


def _battle_game_events(
    settings: Settings,
    player_id: UUID,
    payload: dict[str, Any],
    game_time: str,
) -> list[dict[str, Any]]:
    def bounded_count(value: Any) -> int:
        if isinstance(value, bool):
            return 0
        try:
            return max(0, min(10_000, int(value or 0)))
        except (TypeError, ValueError, OverflowError):
            return 0

    organization = payload.get("organization")
    if not isinstance(organization, dict):
        return []
    members = organization.get("members")
    reports = organization.get("battleReports")
    if not isinstance(members, list) or not isinstance(reports, list):
        return []
    member_names = {
        str(member.get("id")): str(member.get("name") or member.get("id"))[:100]
        for member in members
        if isinstance(member, dict) and str(member.get("id") or "")
    }
    events: list[dict[str, Any]] = []
    for report in reports[-40:]:
        if not isinstance(report, dict) or not isinstance(report.get("won"), bool):
            continue
        report_id = str(report.get("id") or "").strip()
        stage_id = str(report.get("stageId") or "").strip()
        if not report_id or not stage_id:
            continue
        receipt = report.get("kernelReceipt")
        if not isinstance(receipt, dict):
            continue
        receipt_trace = {key: value for key, value in receipt.items() if key != "digest"}
        kernel = receipt.get("kernel")
        if (
            receipt.get("digest") != _digest_json(receipt_trace)
            or receipt.get("reportDigest") != _digest_json(_battle_report_signature(report))
            or not isinstance(kernel, dict)
            or kernel.get("module") != MandateWorkflowModule.name
            or kernel.get("state") != "SEALED"
        ):
            continue
        participant_ids = {
            str(hero_id)
            for hero_id in receipt.get("verifiedParticipants", [])
            if str(hero_id) in member_names
        } if isinstance(receipt.get("verifiedParticipants"), list) else set()
        if not participant_ids:
            continue
        turns = bounded_count(report.get("turns"))
        own_losses = bounded_count(report.get("ownLosses"))
        won = bool(report["won"])
        stage_title = str(report.get("stageTitle") or stage_id).strip()[:160]
        battle_game_time = game_time
        report_month = report.get("month")
        if (
            not isinstance(report_month, bool)
            and isinstance(report_month, int)
            and 1 <= report_month <= 10_000
        ):
            virtual_date = date(771, 1, 1) + timedelta(days=(report_month - 1) * 30)
            battle_game_time = (
                f"{virtual_date.year:04d}-{virtual_date.month:02d}-{virtual_date.day:02d} "
                "14:00:00"
            )
        sources = [
            str(item).strip()[:120]
            for item in report.get("sources", [])[:8]
            if str(item).strip()
        ] if isinstance(report.get("sources"), list) else []
        verified_support = receipt.get("verifiedSupport")
        mandate_entries = verified_support.get("mandates", []) if isinstance(verified_support, dict) else []
        mandate_ids = [
            str(item.get("id"))[:128]
            for item in mandate_entries[:8]
            if isinstance(item, dict) and item.get("id")
        ] if isinstance(mandate_entries, list) else []
        result_text = "告捷" if won else "失利"
        player_target_id = str(
            stable_player_id(settings.ainpc_game_server_id, player_id)
        )
        content = (
            f"{stage_title}{result_text}，历时{turns}回合，己方折损{own_losses}部。"
            + (f"战前筹备：{'、'.join(sources[:3])}。" if sources else "")
        )[:1000]
        for hero_id in sorted(participant_ids):
            identity_digest = hashlib.sha256(
                f"{player_id}\n{report_id}\n{hero_id}".encode("utf-8")
            ).hexdigest()
            outcome_digest = hashlib.sha256(
                f"{identity_digest}\nbattle-semantics-v3\n{receipt['digest']}".encode("utf-8")
            ).hexdigest()
            outcome_source_record_id = "dongzhou-battle-v3:" + outcome_digest[:48]
            memory_source_record_id = "dongzhou-battle:" + identity_digest[:48]
            event_id = int.from_bytes(
                bytes.fromhex(outcome_digest[:8]), "big"
            ) & 0x7FFFFFFF
            if event_id == 0:
                event_id = 1
            npc_id = str(stable_npc_id(settings.ainpc_game_server_id, hero_id))
            npc_name = member_names[hero_id]
            outcome = {
                "game_server_id": str(settings.ainpc_game_server_id),
                "npc_id": npc_id,
                "npc_name": npc_name,
                "game_time": battle_game_time,
                "events": [{
                    "source_record_id": outcome_source_record_id,
                    "timestamp": battle_game_time,
                    "event_id": event_id,
                    "event_name": "东周战役" + result_text,
                    "event_type": "battle_result",
                    "params": content,
                    "metadata": {
                        "standard_event_authority": "game_server",
                        "event_instance_id": outcome_source_record_id,
                        "actor_id": npc_id,
                        "target_id": player_target_id,
                        "behavior_parent": "protect" if won else "system",
                        "behavior_sub": "support" if won else "battle_loss",
                        "motivation": "campaign_duty",
                        "result": "success" if won else "failure",
                        "result_confirmed": True,
                        "severity": 78 if won else 72,
                        "confidence": 1.0,
                        "source_module": "dongzhou_battle",
                        "kernel_receipt_id": receipt["id"],
                        "kernel_receipt_digest": receipt["digest"],
                        "description": content,
                        "stage_id": stage_id[:64],
                        "stage_title": stage_title,
                        "won": won,
                        "turns": turns,
                        "own_losses": own_losses,
                        "hero_id": hero_id,
                        "mandate_ids": mandate_ids,
                        "sources": sources,
                    },
                    "interrupt_trace_id": outcome_source_record_id,
                }],
            }
            memory = {
                "game_server_id": str(settings.ainpc_game_server_id),
                "npc_id": npc_id,
                "npc_name": npc_name,
                "game_time": battle_game_time,
                "messages": [{
                    "timestamp": battle_game_time,
                    "content": content,
                    "message_id": memory_source_record_id,
                }],
            }
            events.extend((
                {
                    "eventId": "battle-outcome-v3:" + outcome_digest,
                    "kind": "NPC_BATTLE_OUTCOME",
                    "payload": outcome,
                },
                {
                    "eventId": "battle-memory:" + identity_digest,
                    "kind": "NPC_BATTLE_MEMORY",
                    "payload": memory,
                },
            ))
    return events


def _npc_outcome_status(
    event: dict[str, Any] | None,
    memory: dict[str, Any] | None,
    affection: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    motivation: dict[str, Any] | None = None,
    *,
    require_affection: bool = False,
    require_quality: bool = False,
    require_motivation: bool = False,
) -> dict[str, Any] | None:
    if (
        event is None
        and memory is None
        and affection is None
        and quality is None
        and motivation is None
    ):
        return None
    parts = {"event": event, "memory": memory}
    if affection is not None or require_affection:
        parts["affection"] = affection
    if quality is not None or require_quality:
        parts["quality"] = quality
    if motivation is not None or require_motivation:
        parts["motivation"] = motivation
    states = [part.get("state") for part in parts.values() if isinstance(part, dict)]
    delivered = len(states) == len(parts) and all(state == "DELIVERED" for state in states)
    last_error = next(
        (
            part.get("lastError")
            for part in parts.values()
            if isinstance(part, dict) and part.get("lastError")
        ),
        None,
    )
    result = {
        "state": "DELIVERED" if delivered else "PENDING",
        "attempts": sum(
            int(part.get("attempts") or 0)
            for part in parts.values()
            if isinstance(part, dict)
        ),
        "lastError": last_error,
        "event": event,
        "memory": memory,
    }
    if affection is not None or require_affection:
        result["affection"] = affection
    if quality is not None or require_quality:
        result["quality"] = quality
    if motivation is not None or require_motivation:
        result["motivation"] = motivation
    return result


async def _prepare_due_organization_reports(
    store: Store,
    settings: Settings,
    player_id: UUID,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    organization = payload.get("organization")
    if not isinstance(organization, dict):
        return reports
    month = organization.get("month")
    tasks = organization.get("tasks")
    if isinstance(month, bool) or not isinstance(month, int) or not isinstance(tasks, list):
        return reports
    manager_hero_id = next(
        (
            hero_id
            for hero_id, member_id in settings.orgflow_hero_members.items()
            if member_id == settings.orgflow_manager_member_id
        ),
        None,
    )
    if manager_hero_id is None:
        return reports
    manager_npc_id = str(stable_npc_id(settings.ainpc_game_server_id, manager_hero_id))
    members = organization.get("members")
    member_names = {
        str(item.get("id")): str(item.get("name") or item.get("id"))
        for item in members
        if isinstance(item, dict) and item.get("id")
    } if isinstance(members, list) else {}
    members_by_id = {
        str(item.get("id")): item
        for item in members
        if isinstance(item, dict) and item.get("id")
    } if isinstance(members, list) else {}
    clock = await store.read_game_clock()
    for task in tasks:
        if not isinstance(task, dict):
            continue
        settlement = task.get("pendingSettlement")
        terminal_result = (
            str(settlement.get("result") or "")
            if isinstance(settlement, dict)
            else ""
        )
        review = task.get("review")
        if not terminal_result and isinstance(review, dict):
            terminal_result = str(review.get("finalResult") or "")
        pending_review = task.get("pendingReview")
        pending_review_record = (
            pending_review.get("review")
            if isinstance(pending_review, dict)
            else None
        )
        if not terminal_result and isinstance(pending_review_record, dict):
            terminal_result = str(pending_review_record.get("finalResult") or "")
        if terminal_result not in {"SUCCESS", "PARTIAL", "FAILURE"}:
            terminal_result = ""
        if task.get("status") != "active" and not terminal_result:
            continue
        task_id = str(task.get("remoteResult") or "")
        due_month = task.get("dueMonth")
        try:
            UUID(task_id)
        except ValueError:
            continue
        if (
            isinstance(due_month, bool)
            or not isinstance(due_month, int)
            or (due_month > month and not terminal_result)
        ):
            continue
        original = await store.read_external_request(
            player_id, task_id, "organization_task"
        )
        if not original:
            continue
        task_type = str(original.get("task_type") or "")
        assignee = str(original.get("assignee_hero_id") or "")
        if assignee not in settings.orgflow_hero_members:
            continue
        mandate = None
        parameters = original.get("parameters")
        mandate_id = parameters.get("mandate_id") if isinstance(parameters, dict) else None
        mandate_digest = parameters.get("mandate_digest") if isinstance(parameters, dict) else None
        if isinstance(mandate_id, str) and isinstance(mandate_digest, str):
            try:
                mandate_request_id = UUID(mandate_id.rsplit(":", 1)[-1])
            except ValueError:
                mandate_request_id = None
            if mandate_request_id is not None:
                mandate_record = await store.read_request(
                    player_id, mandate_request_id, "court_mandate"
                )
                candidate = (
                    mandate_record.get("response", {}).get("mandate")
                    if mandate_record
                    else None
                )
                if isinstance(candidate, dict) and candidate.get("digest") == mandate_digest:
                    mandate = candidate
        planned_result = terminal_result or (
            "SUCCESS"
            if _organization_task_succeeds(
                task, task_type, members_by_id.get(assignee, {}), mandate
            )
            else "FAILURE"
        )
        task_name = str(task.get("name") or task_type or "organization assignment")
        stage_title = str(original.get("stage_title") or "the assigned stage")
        if planned_result == "SUCCESS":
            content = (
                f"The {task_name} assignment for {stage_title} was completed successfully. "
                "Report completion truthfully to the direct manager."
            )
        elif planned_result == "PARTIAL":
            content = (
                f"The {task_name} assignment for {stage_title} was only partly completed. "
                "Report the completed work and remaining obstacles truthfully to the direct manager."
            )
        else:
            content = (
                f"The {task_name} assignment for {stage_title} could not be completed. "
                "Report the failure truthfully to the direct manager."
            )
        assignment = mandate.get("assignment") if isinstance(mandate, dict) else None
        readiness = assignment.get("readiness") if isinstance(assignment, dict) else None
        if isinstance(readiness, dict) and isinstance(readiness.get("score"), int):
            content += f" The sealed duty readiness was {readiness['score']}/100."
        operation_id = str(uuid5(NAMESPACE_URL, f"dongzhou-org-report:{task_id}"))
        report = {
            "operation_id": operation_id,
            "game_server_id": str(settings.ainpc_game_server_id),
            "manager_npc_id": manager_npc_id,
            "worker_npc_id": str(
                stable_npc_id(settings.ainpc_game_server_id, assignee)
            ),
            "purpose": "report",
            "task_id": task_id,
            "content": content,
            "player_info": {
                "playerId": manager_npc_id,
                "playerName": member_names.get(manager_hero_id, manager_hero_id)[:15],
            },
            "npc_outcome": {
                "task_id": task_id,
                "task_type": task_type,
                "task_name": task_name,
                "stage_id": str(original.get("stage_id") or ""),
                "stage_title": stage_title,
                "hero_id": assignee,
                "npc_id": str(
                    stable_npc_id(settings.ainpc_game_server_id, assignee)
                ),
                "npc_name": member_names.get(assignee, assignee),
                "manager_npc_id": manager_npc_id,
                "game_server_id": str(settings.ainpc_game_server_id),
                "game_time": str(clock["virtualTime"]),
                "mandate_id": mandate.get("id") if isinstance(mandate, dict) else None,
                "mandate_digest": (
                    mandate.get("digest") if isinstance(mandate, dict) else None
                ),
                "knowledge_id": str(original.get("knowledge_id") or ""),
                "evidence_source": (
                    mandate.get("evidence", {}).get("source")
                    if isinstance(mandate, dict)
                    and isinstance(mandate.get("evidence"), dict)
                    else None
                ),
                "readiness": readiness if isinstance(readiness, dict) else None,
                "planned_result": planned_result,
            },
        }
        reports.append(report)
    return reports


def build_application(settings: Settings | None = None, *, store: Store | None = None, upstreams: Upstreams | None = None):
    settings = settings or Settings.from_env()
    store = store or Store(settings.database_path)
    upstreams = upstreams or Upstreams(settings)
    module = RuntimeModule(store, upstreams, settings)
    mandate_workflow = MandateWorkflowModule()
    knowledge_tournament = KnowledgeTournamentModule()
    campaign_routes = CampaignRouteModule()
    npc_settlement = NpcSettlementModule()
    kernel = Kernel(
        [
            LoadedModule(module=module, required=True, original_index=0),
            LoadedModule(module=mandate_workflow, required=True, original_index=1),
            LoadedModule(module=knowledge_tournament, required=True, original_index=2),
            LoadedModule(module=campaign_routes, required=True, original_index=3),
            LoadedModule(module=npc_settlement, required=True, original_index=4),
        ]
    )
    router = APIRouter(prefix="/api/dongzhou/v1")
    game_clock_router = APIRouter()
    manager_hero_id = next(
        (
            hero_id
            for hero_id, member_id in settings.orgflow_hero_members.items()
            if member_id == settings.orgflow_manager_member_id
        ),
        None,
    )
    manager_npc_id = (
        str(stable_npc_id(settings.ainpc_game_server_id, manager_hero_id))
        if manager_hero_id
        else None
    )

    def service_statuses(external: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        kernel_snapshot = kernel.health_status()
        runtime = next(
            (
                item
                for item in kernel_snapshot.get("modules", [])
                if item.get("name") == RuntimeModule.name
            ),
            {},
        )
        runtime_state = str(runtime.get("state") or "unknown").lower()
        workflow = next(
            (
                item
                for item in kernel_snapshot.get("modules", [])
                if item.get("name") == MandateWorkflowModule.name
            ),
            {},
        )
        workflow_state = str(workflow.get("state") or "unknown").lower()
        tournament = next(
            (
                item
                for item in kernel_snapshot.get("modules", [])
                if item.get("name") == KnowledgeTournamentModule.name
            ),
            {},
        )
        tournament_state = str(tournament.get("state") or "unknown").lower()
        route_module = next(
            (
                item
                for item in kernel_snapshot.get("modules", [])
                if item.get("name") == CampaignRouteModule.name
            ),
            {},
        )
        route_state = str(route_module.get("state") or "unknown").lower()
        return {
            **external,
            "nexusKernel": {
                "online": runtime_state in {"ready", "degraded"}
                and workflow_state in {"ready", "degraded"}
                and tournament_state in {"ready", "degraded"}
                and route_state in {"ready", "degraded"},
                "mode": "embedded",
                "version": _NEXUS_KERNEL_VERSION,
                "runtimeState": runtime_state,
                "workflowModule": MandateWorkflowModule.name,
                "workflowState": workflow_state,
                "knowledgeTournamentModule": KnowledgeTournamentModule.name,
                "knowledgeTournamentState": tournament_state,
                "campaignRouteModule": CampaignRouteModule.name,
                "campaignRouteState": route_state,
            },
        }

    @game_clock_router.post("/api/v1/QueryServers")
    async def query_servers() -> dict[str, Any]:
        return {
            "servers": [settings.game_server_id],
            "serverNames": ["Dongzhou"],
            "gameVersions": [{"version": {"game": "1.0.0"}}],
        }

    @game_clock_router.post("/api/v1/QueryGameTimeAndTimeScale")
    async def query_game_time(request: GameClockQuery) -> dict[str, Any]:
        if request.server_id != settings.game_server_id:
            raise ApiError("game_server_not_found", "Game server is not configured.", status_code=404)
        snapshot = await store.read_game_clock()
        return {"virtualTime": snapshot["virtualTime"], "timeScale": snapshot["timeScale"]}

    @game_clock_router.post("/api/v1/ainpc/login-ready")
    async def ainpc_login_ready(request: AinpcLoginReadyRequest) -> dict[str, Any]:
        if request.game_server_id != settings.game_server_id:
            raise ApiError("game_server_not_found", "Game server is not configured.", status_code=404)
        if (request.instance_id is None) != (request.instance_count is None):
            raise ApiError("invalid_instance_identity", "Instance ID and count must be supplied together.", status_code=422)
        if request.instance_id is not None and request.instance_id >= request.instance_count:
            raise ApiError("invalid_instance_identity", "Instance ID is outside the instance range.", status_code=422)
        await store.mark_npc_ready(
            request.game_server_id,
            request.ai_id,
            request.login_request_id,
            request.instance_id,
            request.instance_count,
            request.startup_id,
        )
        return {"success": True, "state": "READY"}

    async def npc_is_ready(request: AinpcAliveQuery) -> bool:
        runtime = await store.read_npc_runtime(settings.game_server_id, request.ai_id)
        return runtime is not None and runtime.get("state") == "READY"

    @game_clock_router.post("/api/v2/QueryNDLLMIsAlive")
    async def query_npc_alive(request: AinpcAliveQuery) -> dict[str, bool]:
        return {"isAlive": await npc_is_ready(request)}

    @game_clock_router.post("/api/v2/QueryNDLLMIsOnline")
    async def query_npc_online(request: AinpcAliveQuery) -> dict[str, bool]:
        return {"isOnline": await npc_is_ready(request)}

    @game_clock_router.post("/api/v2/QueryNDLLMTaskInfoByStatus")
    async def query_npc_tasks(request: AinpcTaskStatusQuery) -> dict[str, Any]:
        # Organization orders are owned by orgFlow, not resumable game-server
        # behavior-tree tasks, so they must not be mixed into this contract.
        return {"taskInfos": []}

    def npc_wire(row: dict[str, Any]) -> dict[str, str]:
        return {"heroId": str(row["heroId"]), "name": str(row["name"]), "npcId": str(row["id"])}

    @game_clock_router.post("/api/v1/NDLLMAllAILogin")
    async def login_all_npcs(request: AinpcAllLoginRequest) -> dict[str, Any]:
        directed = request.instance_id is not None or request.instance_count is not None or request.startup_id is not None
        if directed and (request.instance_id is None or request.instance_count is None or request.startup_id is None):
            raise ApiError("invalid_instance_identity", "Instance ID, count, and startup ID are required together.", status_code=422)
        if request.instance_id is not None and request.instance_id >= request.instance_count:
            raise ApiError("invalid_instance_identity", "Instance ID is outside the instance range.", status_code=422)
        rows = await store.list_npcs(settings.game_server_id, include_offline=True)
        if request.instance_count is not None:
            rows = [
                row for row in rows
                if int.from_bytes(
                    hashlib.sha256(f"{settings.game_server_id}:{row['id']}".encode("utf-8")).digest(),
                    byteorder="big",
                    signed=False,
                ) % request.instance_count == request.instance_id
            ]
        npcs = [npc_wire(row) for row in rows]
        await store.clear_npc_runtime(
            settings.game_server_id,
            [npc["npcId"] for npc in npcs],
        )
        clock = await store.read_game_clock()
        login_round = request.startup_id or "dongzhou-manual-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        module.schedule_npc_relogin(npcs, str(clock["virtualTime"]), login_round)
        return {"success": True, "state": "ACCEPTED", "acceptedCount": len(npcs), "startupId": request.startup_id}

    @game_clock_router.post("/api/v1/NDLLMSingleAILogin")
    async def login_single_npc(request: AinpcSingleLoginRequest) -> dict[str, Any]:
        if request.game_server_id != settings.game_server_id:
            raise ApiError("game_server_not_found", "Game server is not configured.", status_code=404)
        rows = await store.list_npcs(settings.game_server_id, include_offline=True)
        row = next((item for item in rows if str(item["id"]) == request.ai_id), None)
        if row is None:
            raise ApiError("npc_not_found", "NPC is not registered.", status_code=404)
        await store.clear_npc_runtime(settings.game_server_id, [request.ai_id])
        clock = await store.read_game_clock()
        await upstreams.set_npcs_online([npc_wire(row)], str(clock["virtualTime"]), request.request_id)
        return {
            "gameServerId": request.game_server_id,
            "aiId": request.ai_id,
            "requestId": request.request_id,
            "accepted": True,
        }

    @game_clock_router.post("/api/v1/QueryNPCS")
    async def query_npcs(request: AinpcNpcDirectoryQuery) -> dict[str, Any]:
        if request.server_id != settings.game_server_id:
            raise ApiError("game_server_not_found", "Game server is not configured.", status_code=404)
        return {
            "infos": await store.list_npcs(
                request.server_id, include_offline=request.include_offline
            )
        }

    @game_clock_router.post("/api/v2/QueryNDLLMNearbyPlayerInfo")
    async def query_nearby(request: AinpcNearbyQuery) -> dict[str, Any]:
        filters = {item.filter_type for item in request.filters}
        if "FILTER_ONLY_PLAYER" in filters:
            return {"players": []}
        rows = await store.list_npcs(settings.game_server_id)
        return {
            "players": [
                {"playerId": row["id"], "playerName": row["name"]}
                for row in rows
                if row["id"] != request.ai_id
            ]
        }

    @game_clock_router.post("/api/v2/QueryNDLLMFriendInfo")
    async def query_friends(request: AinpcAliveQuery) -> dict[str, Any]:
        rows = await store.list_npcs(settings.game_server_id)
        return {
            "friends": [
                {"playerId": row["id"], "playerName": row["name"]}
                for row in rows
                if row["id"] != request.ai_id
            ]
        }

    @game_clock_router.post("/api/v2/NDLLMChatWithPlayer")
    async def start_private_chat(request: AinpcChatStartRequest) -> dict[str, Any]:
        runtime = await store.read_npc_runtime(settings.game_server_id, request.ai_id)
        if runtime is None or runtime["loginRequestId"] != request.login_request_id:
            return {"success": False, "errorCode": "npc_login_round_changed"}
        target_id = str(request.player_info.player_id)
        if request.is_npc and await store.read_npc_runtime(settings.game_server_id, target_id) is None:
            return {"success": False, "errorCode": "target_npc_offline"}
        digest = hashlib.sha256(
            f"{settings.game_server_id}\n{request.ai_id}\n{target_id}\n{request.topic}".encode("utf-8")
        ).hexdigest()
        clock = await store.read_game_clock()
        payload = {
            "gameServerId": settings.game_server_id,
            "npcId": request.ai_id,
            "source": settings.game_server_id,
            "speakerId": request.ai_id,
            "taskId": "orgchat-" + digest[:32],
            "chatId": f"{request.ai_id}_{target_id}",
            "serverName": "Dongzhou",
            "status": "start",
            "currTime": clock["virtualTime"],
            "topic": request.topic,
            "participants": [
                {"id": request.ai_id, "name": request.ai_id, "type": "NPC"},
                {
                    "id": target_id,
                    "name": request.player_info.player_name,
                    "type": "NPC" if request.is_npc else "PLAYER",
                },
            ],
            "messages": [],
        }
        try:
            await store.register_private_chat(payload)
        except VersionConflict as exc:
            if str(exc) != "private_chat_pair_busy":
                raise
            return {
                "success": False,
                "errorCode": "private_chat_pair_busy",
                "message": "already in reply",
            }
        await store.enqueue_game_event(
            "chat-start:" + digest,
            "CHAT_START",
            payload,
            requeue_delivered=True,
        )
        return {"success": True, "chatId": payload["chatId"], "taskId": payload["taskId"]}

    @game_clock_router.post("/api/v2/NDLLMSendPrivateMessage")
    async def send_private_message(request: AinpcPrivateMessageRequest) -> dict[str, Any]:
        runtime = await store.read_npc_runtime(settings.game_server_id, request.ai_id)
        if runtime is None or runtime["loginRequestId"] != request.login_request_id:
            return {"success": False, "errorCode": "npc_login_round_changed"}
        message = request.data.get("message")
        if not isinstance(message, dict) and {
            "id", "speakerId"
        }.issubset(request.data):
            # The original V1 client places the message directly under data;
            # durable delivery wraps it as data.message.
            message = request.data
        if not isinstance(message, dict) or str(message.get("speakerId")) != request.ai_id:
            raise ApiError("private_message_invalid", "Private message identity is invalid.", status_code=422)
        message_id = str(message.get("id") or "").strip()
        if not message_id:
            raise ApiError("private_message_invalid", "Private message ID is required.", status_code=422)
        wire = request.model_dump(mode="json", by_alias=True)
        wire["gameServerId"] = settings.game_server_id
        if not isinstance(wire["data"].get("message"), dict):
            wire["data"] = {"message": message}
        await store.record_private_message(wire, route_to_npc=request.is_npc)
        if request.delivery_attempt_id is not None:
            callback_id = hashlib.sha256(
                f"{message_id}\n{request.delivery_attempt_id}\n{request.attempt}".encode("utf-8")
            ).hexdigest()[:32]
            callback = {
                "gameServerId": settings.game_server_id,
                "npcId": request.ai_id,
                "chatId": request.chat_id,
                "taskId": request.task_id,
                "messageId": message_id,
                "deliveryAttemptId": request.delivery_attempt_id,
                "attempt": request.attempt,
                "callbackId": callback_id,
                "status": "delivered",
                "occurredAt": datetime.now(UTC).isoformat(),
            }
            await store.enqueue_game_event(
                "delivery:" + request.delivery_attempt_id, "DELIVERY_RESULT", callback
            )
        return {"success": True, "messageId": message_id}

    @game_clock_router.post("/api/v2/QueryNDLLMPrivateMessageDelivery")
    async def query_private_message_delivery(
        request: AinpcPrivateMessageDeliveryQuery,
    ) -> dict[str, Any]:
        return await store.query_private_message_delivery(
            game_server_id=settings.game_server_id,
            npc_id=request.ai_id,
            chat_id=request.chat_id,
            task_id=request.task_id,
            message_id=request.message_id,
            delivery_attempt_id=request.delivery_attempt_id,
            attempt=request.attempt,
        )

    @game_clock_router.post("/api/v2/QueryPrivateChatRuntimeState")
    async def query_private_chat_runtime_state(
        request: AinpcPrivateChatRuntimeQuery,
    ) -> dict[str, Any]:
        return await store.private_chat_runtime_state(
            settings.game_server_id, request.ai_id
        )

    @game_clock_router.post("/api/v2/ResetPrivateChatRuntimeState")
    async def reset_private_chat_runtime_state(
        request: AinpcPrivateChatRuntimeResetRequest,
    ) -> dict[str, Any]:
        released = await store.reset_private_chat_pair_lease(
            settings.game_server_id, request.ai_id, request.target_id
        )
        state = await store.private_chat_runtime_state(
            settings.game_server_id, request.ai_id
        )
        return {
            "success": True,
            "message": "private chat pair lease released" if released else "runtime state already clear",
            "endedWaitingReplyCount": 0,
            "clearedPendingMessageCount": int(released),
            "clearedQueuedSendCount": 0,
            "uncancelledSendingCount": 0,
            "state": state,
        }

    def player(
        authorization: Annotated[str | None, Header()] = None,
        dongzhou_session: Annotated[str | None, Cookie()] = None,
    ) -> UUID:
        scheme, _, bearer = (authorization or "").partition(" ")
        token = bearer if scheme.lower() == "bearer" else dongzhou_session
        if not token:
            raise ApiError("authentication_required", "A valid player session is required.", status_code=401)
        try:
            return verify_session(token, settings.session_secret)
        except InvalidSession as error:
            raise ApiError("invalid_session", str(error), status_code=401) from error

    @router.post("/sessions/guest")
    async def create_guest_session(request: GuestSessionRequest, response: Response) -> dict[str, Any]:
        player_id = await store.get_or_create_player(request.installation_id)
        token = issue_session(player_id, settings.session_secret)
        response.set_cookie(
            "dongzhou_session",
            token,
            max_age=86400,
            httponly=True,
            secure=settings.environment == "production",
            samesite="strict",
            path="/api/dongzhou/v1",
        )
        return {"playerId": str(player_id), "expiresIn": 86400}

    @router.get("/integration/status")
    async def integration_status(player_id: UUID = Depends(player)) -> dict[str, Any]:
        services = service_statuses(await upstreams.health())
        return {"mode": "connected", "services": services, "playerId": str(player_id), "organizationId": settings.orgflow_org_id or None}

    @router.get("/save")
    async def read_save(player_id: UUID = Depends(player)) -> dict[str, Any]:
        try:
            return await store.read_save(player_id)
        except KeyError as error:
            raise ApiError("player_not_found", "Player does not exist.", status_code=404) from error

    @router.put("/save")
    async def write_save(request: SaveWriteRequest, player_id: UUID = Depends(player)) -> dict[str, Any]:
        try:
            previous = await store.read_save(player_id)
            if previous["version"] != request.expected_version:
                raise VersionConflict("save_version_conflict")
            attestations = await _battle_support_attestations(
                store,
                player_id,
                previous["payload"],
                request.payload,
            )
            sealed_payload = _seal_battle_reports(
                player_id,
                previous["payload"],
                request.payload,
                attestations,
            )
            reports = await _prepare_due_organization_reports(
                store, settings, player_id, sealed_payload
            )
            clock = await store.read_game_clock()
            battle_events = _battle_game_events(
                settings,
                player_id,
                sealed_payload,
                str(clock["virtualTime"]),
            )
            return await store.write_save(
                player_id,
                request.expected_version,
                sealed_payload,
                organization_reports=reports,
                game_events=battle_events,
            )
        except VersionConflict as error:
            raise ApiError("save_version_conflict", "The save has changed; reload before writing.", status_code=409) from error
        except GameClockConflict as error:
            raise ApiError(str(error), "Organization month must advance exactly one step at a time.", status_code=409) from error
        except BattleReceiptConflict as error:
            raise ApiError(str(error), "Battle support provenance is invalid or the sealed report changed.", status_code=409) from error

    @router.post("/knowledge/search")
    async def search_knowledge(request: KnowledgeSearchRequest, player_id: UUID = Depends(player)) -> dict[str, Any]:
        body = _payload(request)
        if request.client_request_id is not None:
            try:
                created, previous = await store.begin_request(
                    player_id, request.client_request_id, "knowledge_search", body
                )
            except VersionConflict as error:
                raise ApiError(
                    "idempotency_conflict",
                    "The request identifier was already used with different input.",
                    status_code=409,
                ) from error
            if not created:
                if previous and previous.get("state") == "PENDING":
                    raise ApiError(
                        "request_in_progress",
                        "The same knowledge search is still running.",
                        status_code=409,
                    )
                return {"replayed": True, **(previous or {})}
        try:
            mode, results = await upstreams.search_knowledge(request.query, request.limit)
        except UpstreamUnavailable as error:
            if request.client_request_id is not None:
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE", "requestId": str(request.client_request_id)},
                    str(error),
                )
            raise ApiError("knowledge_unavailable", "Knowledge search is temporarily unavailable.", status_code=503) from error
        await store.add_codex(player_id, results)
        response: dict[str, Any] = {"mode": mode, "query": request.query, "results": results}
        if request.client_request_id is not None:
            receipt_id = stable_event_id(player_id, request.client_request_id)
            receipt_trace = {
                "id": receipt_id,
                "requestId": str(request.client_request_id),
                "stageId": request.stage_id,
                "query": request.query,
                "results": [
                    {
                        "id": str(item.get("id") or item.get("aku_id") or ""),
                        "stageId": str(item.get("stageId") or ""),
                        "retrieval": item.get("retrieval"),
                    }
                    for item in results
                    if isinstance(item, dict)
                ],
            }
            receipt_digest = hashlib.sha256(
                json.dumps(receipt_trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
            ).hexdigest()
            receipt = {**receipt_trace, "digest": receipt_digest}
            response = {
                **response,
                "searchReceipt": receipt,
                "results": [
                    {**item, "searchReceipt": {"id": receipt_id, "digest": receipt_digest}}
                    for item in results
                ],
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "COMPLETED",
                response,
                external_id=receipt_id,
            )
        return response

    @router.get("/knowledge/stages/{stage_id}")
    async def stage_knowledge(stage_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        try:
            entries = await upstreams.stage_knowledge(stage_id)
        except (UpstreamUnavailable, OSError, ValueError) as error:
            raise ApiError("knowledge_unavailable", "Published stage knowledge is temporarily unavailable.", status_code=503) from error
        await store.add_codex(player_id, entries)
        return {"mode": "connected", "stageId": stage_id, "results": entries}

    @router.post("/knowledge/quiz")
    async def start_knowledge_quiz(
        request: KnowledgeQuizStartRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        existing = await store.read_request(
            player_id, request.client_request_id, "knowledge_quiz"
        )
        if existing is not None:
            if existing.get("request", {}).get("stageId") != request.stage_id:
                raise ApiError(
                    "idempotency_conflict",
                    "The quiz request identifier was used for another stage.",
                    status_code=409,
                )
            if existing.get("state") == "PENDING" or not existing.get("response"):
                raise ApiError(
                    "request_in_progress",
                    "The same quiz is still being prepared.",
                    status_code=409,
                )
            return {"replayed": True, **existing["response"]}
        try:
            entries = await upstreams.stage_knowledge(request.stage_id)
            trace, source = _knowledge_quiz_trace(
                request.client_request_id,
                request.stage_id,
                entries,
                settings.knowledge_file,
                datetime.now(UTC) + timedelta(seconds=30),
            )
        except UpstreamUnavailable as error:
            raise ApiError(
                "knowledge_unavailable",
                "Published stage knowledge is temporarily unavailable.",
                status_code=503,
            ) from error
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise ApiError(
                "knowledge_quiz_unavailable",
                "This stage cannot produce a verified history question.",
                status_code=409,
            ) from error
        internal = {**trace, "source": source}
        try:
            created, previous = await store.begin_request(
                player_id,
                request.client_request_id,
                "knowledge_quiz",
                internal,
            )
        except VersionConflict as error:
            raise ApiError(
                "idempotency_conflict",
                "The quiz request identifier was already used.",
                status_code=409,
            ) from error
        if not created:
            return {"replayed": True, **(previous or {})}
        response = KnowledgeTournamentModule.seal_question(trace)
        await store.finish_request(
            player_id,
            request.client_request_id,
            "READY",
            response,
        )
        return response

    @router.post("/knowledge/quiz/{question_id}/answer")
    async def answer_knowledge_quiz(
        question_id: UUID,
        request: KnowledgeQuizAnswerRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        record = await store.read_request(player_id, question_id, "knowledge_quiz")
        if record is None:
            raise ApiError("knowledge_quiz_not_found", "History question not found.", status_code=404)
        internal = record.get("request") or {}
        ready = KnowledgeTournamentModule.seal_question(
            {key: internal[key] for key in ("id", "stageId", "knowledgeId", "title", "prompt", "options", "correctIndex", "deadlineAt")}
        )
        expected_action_id = ready["action"]["actionId"]
        if str(request.action_id) != expected_action_id:
            raise ApiError("knowledge_quiz_action_invalid", "History answer action is invalid.", status_code=409)
        if record.get("state") == "ANSWERED":
            previous = record.get("response") or {}
            if int(previous.get("selectedIndex", -1)) != request.answer_index:
                raise ApiError("knowledge_quiz_already_answered", "History question was already answered.", status_code=409)
            return {"replayed": True, **previous}
        if record.get("state") != "READY":
            raise ApiError("knowledge_quiz_not_ready", "History question is not ready.", status_code=409)
        deadline = datetime.fromisoformat(str(internal["deadlineAt"]).replace("Z", "+00:00"))
        state = "EXPIRED" if datetime.now(UTC) > deadline else "COMPLETED"
        result = KnowledgeTournamentModule.seal_result(
            str(ready["question"]["receipt"]["digest"]),
            request.answer_index,
            int(internal["correctIndex"]),
            state,
        )
        response = {
            **result,
            "questionId": str(question_id),
            "stageId": str(internal["stageId"]),
            "knowledgeId": str(internal["knowledgeId"]),
            "correctAnswer": internal["options"][int(internal["correctIndex"])],
            "source": internal.get("source"),
        }
        transitioned = await store.transition_request(
            player_id,
            question_id,
            "knowledge_quiz",
            "READY",
            "ANSWERED",
            response,
        )
        if not transitioned:
            latest = await store.read_request(player_id, question_id, "knowledge_quiz")
            previous = latest.get("response") if latest else None
            if previous and int(previous.get("selectedIndex", -1)) == request.answer_index:
                return {"replayed": True, **previous}
            raise ApiError("knowledge_quiz_already_answered", "History question was already answered.", status_code=409)
        return response

    @router.post("/knowledge/routes")
    async def campaign_route(
        request: CampaignRouteRequest, player_id: UUID = Depends(player)
    ) -> dict[str, Any]:
        saved = await store.read_save(player_id)
        payload = saved.get("payload", {})
        completed = payload.get("completed", []) if isinstance(payload, dict) else []
        if request.from_stage_id not in completed:
            raise ApiError(
                "campaign_route_locked",
                "The preceding campaign stage is not complete.",
                status_code=409,
            )
        from_map_id = 900000 + request.from_stage_index
        to_map_id = 900000 + request.to_stage_index
        methods = ("campaign_progression", "fixed_point", "npc_dialog")
        try:
            results = await asyncio.gather(
                *(upstreams.campaign_route(from_map_id, to_map_id, method) for method in methods)
            )
        except UpstreamUnavailable as error:
            raise ApiError(
                "knowledge_route_unavailable",
                "Campaign route verification is temporarily unavailable.",
                status_code=503,
            ) from error
        route_options: list[dict[str, Any]] = []
        route_rules = {
            "campaign_progression": {"label": "奉诏直进", "provisionCost": 2, "moraleDelta": 0},
            "fixed_point": {"label": "官道驿行", "provisionCost": 3, "moraleDelta": 6},
            "npc_dialog": {"label": "向导引路", "provisionCost": 1, "moraleDelta": -4},
        }
        for method, result in zip(methods, results):
            route = None
            for plan in result.get("plans", []):
                if not isinstance(plan, dict):
                    continue
                for step in plan.get("steps", []):
                    if not isinstance(step, dict):
                        continue
                    route = next(
                        (
                            candidate
                            for candidate in step.get("routes", [])
                            if isinstance(candidate, dict) and candidate.get("method") == method
                        ),
                        None,
                    )
                    if route is not None:
                        break
                if route is not None:
                    break
            if route is None:
                route = next(
                    (
                        candidate
                        for candidate in result.get("routes", [])
                        if isinstance(candidate, dict) and candidate.get("method") == method
                    ),
                    None,
                )
            if (
                result.get("found") is not True
                or result.get("from") != from_map_id
                or result.get("to") != to_map_id
                or route is None
            ):
                raise ApiError(
                    "campaign_route_not_found",
                    f"No published {method} route joins these stages.",
                    status_code=404,
                )
            detail = route.get("detail")
            if not isinstance(detail, dict):
                raise ApiError("campaign_route_invalid", "Published route detail is invalid.", status_code=502)
            if method == "campaign_progression":
                expected = {
                    "from_stage_id": request.from_stage_id,
                    "to_stage_id": request.to_stage_id,
                    "requires_completed_stage_id": request.from_stage_id,
                }
                if any(detail.get(key) != value for key, value in expected.items()) or detail.get("provision_cost") != 2:
                    raise ApiError("campaign_route_invalid", "Published campaign route is invalid.", status_code=502)
            elif method == "fixed_point":
                if any(isinstance(detail.get(key), bool) or not isinstance(detail.get(key), int) for key in ("x", "y")):
                    raise ApiError("campaign_route_invalid", "Published fixed-point route is invalid.", status_code=502)
            else:
                npc = detail.get("npc")
                dialog = detail.get("dialog_path")
                target = detail.get("target")
                if (
                    not isinstance(npc, dict)
                    or not str(npc.get("name") or "").strip()
                    or not isinstance(dialog, list)
                    or not dialog
                    or not all(isinstance(item, dict) and str(item.get("selected_option") or "").strip() for item in dialog)
                    or not isinstance(target, dict)
                ):
                    raise ApiError("campaign_route_invalid", "Published guide route is invalid.", status_code=502)
            rule = route_rules[method]
            route_options.append({
                "method": method,
                "routeId": route.get("route_id"),
                "label": rule["label"],
                "provisionCost": rule["provisionCost"],
                "moraleDelta": rule["moraleDelta"],
                **({"guideName": detail["npc"]["name"]} if method == "npc_dialog" else {}),
            })
        selected = next(option for option in route_options if option["method"] == request.route_method)
        selection_trace = {
            "fromStageId": request.from_stage_id,
            "toStageId": request.to_stage_id,
            "fromMapId": from_map_id,
            "toMapId": to_map_id,
            **selected,
        }
        return {
            "mode": "connected",
            "found": True,
            "fromStageId": request.from_stage_id,
            "toStageId": request.to_stage_id,
            "fromMapId": from_map_id,
            "toMapId": to_map_id,
            **selected,
            "options": route_options,
            "receipt": campaign_routes.seal_selection(selection_trace),
        }

    @router.get("/knowledge/codex")
    async def list_codex(player_id: UUID = Depends(player)) -> dict[str, Any]:
        return {"results": await store.list_codex(player_id)}

    @router.post("/npcs/sync")
    async def sync_npcs(request: NpcSyncRequest, player_id: UUID = Depends(player)) -> dict[str, Any]:
        mapped = [{"heroId": npc.hero_id, "name": npc.name, "npcId": str(stable_npc_id(settings.ainpc_game_server_id, npc.hero_id))} for npc in request.npcs]
        existing = {
            str(row["id"]): row
            for row in await store.list_npcs(settings.game_server_id, include_offline=True)
        }
        await store.upsert_npc_directory(settings.game_server_id, mapped)
        changed = [
            npc for npc in mapped
            if npc["npcId"] not in existing or existing[npc["npcId"]]["name"] != npc["name"]
        ]
        try:
            online_ids = await upstreams.online_npc_ids()
            pending = [npc for npc in mapped if npc["npcId"] not in online_ids]
            result = await upstreams.register_npcs(changed) if changed else {"code": 200, "state": "UNCHANGED"}
            activation: list[dict[str, Any]] = []
            if pending:
                clock = await store.read_game_clock()
                activation = await upstreams.set_npcs_online(
                    pending, str(clock["virtualTime"]), f"dongzhou-{player_id.hex}"
                )
        except UpstreamUnavailable as error:
            raise ApiError("ainpc_unavailable", "NPC service is temporarily unavailable.", status_code=503) from error
        try:
            relationship_sync: list[dict[str, Any]] | dict[str, Any] = (
                await _sync_organization_supervision(upstreams, settings, mapped)
            )
        except UpstreamUnavailable:
            relationship_sync = {"state": "UNAVAILABLE", "retryable": True}
        ready = not pending
        return {"playerId": str(player_id), "gameServerId": str(settings.ainpc_game_server_id), "npcs": mapped, "registration": result, "activation": activation, "relationshipSync": relationship_sync, "ready": ready, "state": "READY" if ready else "INITIALIZING"}

    @router.post("/npcs/interaction-preference")
    async def set_npc_interaction_preference(
        request: NpcInteractionPreferenceRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        ai_player_id = stable_player_id(settings.ainpc_game_server_id, player_id)
        try:
            preference = await upstreams.sync_player_ai_interaction(
                ai_player_id, request.enabled
            )
        except UpstreamUnavailable as error:
            raise ApiError(
                "ainpc_interaction_preference_unavailable",
                "NPC interaction preference is temporarily unavailable.",
                status_code=503,
            ) from error
        if preference["enabled"] is not request.enabled:
            raise ApiError(
                "ainpc_interaction_preference_not_applied",
                "NPC interaction preference was not applied.",
                status_code=503,
            )
        return {
            "playerId": str(player_id),
            "aiPlayerId": str(ai_player_id),
            **preference,
        }

    @router.get("/npcs/{hero_id}/state")
    async def read_npc_state(hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        try:
            state = await upstreams.npc_state(npc_id)
        except UpstreamUnavailable as error:
            raise ApiError("ainpc_unavailable", "NPC state is temporarily unavailable.", status_code=503) from error
        runtime = await store.read_npc_runtime(settings.game_server_id, str(npc_id))
        known_npc_ids = {
            known_hero_id: str(stable_npc_id(settings.ainpc_game_server_id, known_hero_id))
            for known_hero_id in settings.orgflow_hero_members
        }
        memories = state.pop("memories", {"available": False, "items": []})
        return {
            "playerId": str(player_id),
            "heroId": hero_id,
            "npcId": str(npc_id),
            "knownNpcIds": known_npc_ids,
            "runtime": runtime or {"state": "INITIALIZING"},
            **state,
            "memories": {
                "available": memories.get("available") is True,
                "items": _npc_memory_items(memories),
            },
        }

    @router.get("/npcs/{hero_id}/correspondence")
    async def read_npc_correspondence(
        hero_id: str, limit: int = 20, player_id: UUID = Depends(player)
    ) -> dict[str, Any]:
        if limit < 1 or limit > 50:
            raise ApiError("correspondence_limit_invalid", "Correspondence limit must be between 1 and 50.", status_code=422)
        npc_id = str(stable_npc_id(settings.ainpc_game_server_id, hero_id))
        player_peer_id = str(stable_player_id(settings.ainpc_game_server_id, player_id))
        messages = await store.list_npc_correspondence(
            settings.game_server_id,
            npc_id,
            limit=limit,
            player_peer_id=player_peer_id,
        )
        return {
            "playerId": str(player_id),
            "heroId": hero_id,
            "npcId": npc_id,
            "messages": [_correspondence_evidence(message) for message in messages],
        }

    @router.post("/npcs/{hero_id}/messages")
    async def send_npc_message(
        hero_id: str,
        request: NpcMessageRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        npc_id = str(stable_npc_id(settings.ainpc_game_server_id, hero_id))
        player_peer_id = str(stable_player_id(settings.ainpc_game_server_id, player_id))
        runtime = await store.read_npc_runtime(settings.game_server_id, npc_id)
        if runtime is None or runtime.get("state") != "READY":
            raise ApiError(
                "npc_unavailable",
                "NPC state is temporarily unavailable.",
                status_code=503,
            )
        directory = await store.list_npcs(settings.game_server_id, include_offline=True)
        npc = next((item for item in directory if str(item.get("id")) == npc_id), None)
        if npc is None:
            raise ApiError("npc_not_found", "NPC is not registered.", status_code=404)
        clock = await store.read_game_clock()
        task_id = "playerchat-" + hashlib.sha256(
            f"{player_id}\n{request.client_request_id}".encode("utf-8")
        ).hexdigest()[:32]
        chat_id = f"{npc_id}_{player_peer_id}"
        message_id = "player-" + request.client_request_id.hex
        payload = {
            "gameServerId": settings.game_server_id,
            "npcId": npc_id,
            "source": settings.game_server_id,
            "speakerId": npc_id,
            "taskId": task_id,
            "chatId": chat_id,
            "serverName": "Dongzhou",
            "status": "inProgress",
            "currTime": str(clock["virtualTime"]),
            "topic": "府中问答",
            "participants": [
                {"id": npc_id, "name": str(npc.get("name") or hero_id), "type": "NPC"},
                {"id": player_peer_id, "name": "主君", "type": "PLAYER"},
            ],
            "messages": [
                {
                    "id": message_id,
                    "time": str(clock["virtualTime"]),
                    "content": request.content,
                    "speakerId": player_peer_id,
                    "speakerName": "主君",
                    "speakerEmotion": "calm",
                    "isStopped": False,
                }
            ],
        }
        try:
            await store.register_private_chat(payload)
            accepted = await upstreams.send_game_event("CHAT_TURN", payload)
        except VersionConflict as error:
            raise ApiError(
                "npc_message_conflict", "The message identity conflicts with an existing turn.", status_code=409
            ) from error
        except UpstreamUnavailable as error:
            raise ApiError(
                "ainpc_unavailable", "NPC service is temporarily unavailable.", status_code=503
            ) from error
        data = accepted.get("data", accepted)
        if not isinstance(data, dict) or data.get("accepted") is False:
            raise ApiError("npc_message_rejected", "NPC service rejected the message.", status_code=502)
        return {
            "state": "ACCEPTED",
            "heroId": hero_id,
            "npcId": npc_id,
            "chatId": chat_id,
            "taskId": task_id,
            "messageId": message_id,
        }

    @router.get("/npcs/{hero_id}/schedule")
    async def read_npc_schedule(hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        try:
            result = await upstreams.npc_schedule(npc_id)
        except UpstreamUnavailable as error:
            raise ApiError("ainpc_schedule_unavailable", "NPC schedule is temporarily unavailable.", status_code=503) from error
        return {"playerId": str(player_id), "heroId": hero_id, "npcId": str(npc_id), "schedule": result}

    @router.post("/npcs/{hero_id}/schedule")
    async def generate_npc_schedule(request: NpcScheduleGenerateRequest, hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        try:
            result = await upstreams.generate_npc_schedule(npc_id, request.force_regenerate)
        except UpstreamUnavailable as error:
            raise ApiError("ainpc_schedule_unavailable", "NPC schedule generation is temporarily unavailable.", status_code=503) from error
        return {"playerId": str(player_id), "heroId": hero_id, "npcId": str(npc_id), "schedule": result}

    async def resolve_npc_assignment(
        hero_id: str, task_type: str, stage_id: str
    ) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        try:
            npc_state, schedule, quality = await asyncio.gather(
                upstreams.npc_state(npc_id),
                upstreams.npc_schedule(npc_id),
                upstreams.npc_quality(npc_id, auto_initialize=True),
            )
            runtime = await store.read_npc_runtime(
                settings.game_server_id, str(npc_id)
            )
            return select_assignment(
                hero_id=hero_id,
                npc_id=str(npc_id),
                task_type=task_type,
                stage_id=stage_id,
                npc_state=npc_state,
                schedule_response=schedule,
                runtime=runtime,
                personality=npc_state.get("personality"),
                motivation=npc_state.get("motivation"),
                quality=quality,
                manager_npc_id=manager_npc_id,
            )
        except UpstreamUnavailable as error:
            raise ApiError(
                "ainpc_assignment_unavailable",
                "NPC state or schedule is temporarily unavailable.",
                status_code=503,
            ) from error
        except AssignmentUnavailable as error:
            raise ApiError(
                "ainpc_assignment_unavailable",
                str(error),
                status_code=503,
            ) from error

    @router.get("/npcs/{hero_id}/assignments/{task_type}")
    async def read_npc_assignment(
        hero_id: str,
        task_type: str,
        stage_id: str,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        assignment = await resolve_npc_assignment(hero_id, task_type, stage_id)
        return {
            "playerId": str(player_id),
            "stageId": stage_id,
            "taskType": task_type,
            "assignment": assignment,
        }

    @router.post("/npcs/{hero_id}/thoughts")
    async def generate_npc_thought(
        request: NpcThoughtRequest,
        hero_id: str,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        body = _payload(request)
        try:
            created, previous = await store.begin_request(
                player_id,
                request.client_request_id,
                "npc_spontaneous_thought",
                {"hero_id": hero_id, **body},
            )
        except VersionConflict as error:
            raise ApiError(
                "idempotency_conflict",
                "The request identifier was already used with different input.",
                status_code=409,
            ) from error
        if not created:
            if previous and previous.get("state") == "PENDING":
                raise ApiError(
                    "request_in_progress",
                    "The same NPC thought is still being generated.",
                    status_code=409,
                )
            return {"replayed": True, **(previous or {})}

        try:
            entries, assignment = await asyncio.gather(
                upstreams.stage_knowledge(request.stage_id),
                resolve_npc_assignment(hero_id, request.task_type, request.stage_id),
            )
        except (UpstreamUnavailable, ApiError, OSError, ValueError) as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "npc_thought_context_unavailable",
                "The NPC duty or published knowledge is temporarily unavailable.",
                status_code=503,
            ) from error
        evidence = next(
            (
                entry
                for entry in entries
                if isinstance(entry, dict)
                and str(entry.get("id") or entry.get("aku_id") or "")
                == request.knowledge_id
                and str(entry.get("stageId") or request.stage_id) == request.stage_id
            ),
            None,
        )
        source_details = evidence.get("sourceDetails") if isinstance(evidence, dict) else None
        source = (
            source_details[request.evidence_source_index]
            if isinstance(source_details, list)
            and request.evidence_source_index < len(source_details)
            else None
        )
        if evidence is None or not isinstance(source, dict) or not str(source.get("work") or "").strip():
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "npc_thought_evidence_unverified",
            )
            raise ApiError(
                "npc_thought_evidence_unverified",
                "The NPC thought must use published evidence for this stage.",
                status_code=422,
            )

        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        directory = await store.list_npcs(settings.game_server_id, include_offline=True)
        npc_row = next((item for item in directory if str(item.get("id")) == str(npc_id)), None)
        npc_name = str((npc_row or {}).get("name") or hero_id)
        personality = assignment.get("personality") if isinstance(assignment.get("personality"), dict) else {}
        motivation = assignment.get("motivation") if isinstance(assignment.get("motivation"), dict) else {}
        canonical_source = {
            "index": request.evidence_source_index,
            "work": str(source.get("work") or ""),
            "tier": str(source.get("tier") or "来源"),
            "scope": str(source.get("scope") or ""),
            "url": str(source.get("url") or ""),
        }
        clock = await store.read_game_clock()
        operation_id = f"dongzhou-thought:{player_id}:{request.client_request_id}"
        thought_payload = {
            "operation_id": operation_id,
            "npc_context": {
                "npc_name": npc_name,
                "background": str(personality.get("backgroundNote") or ""),
                "personality": list(personality.get("dominantTraits") or []),
                "profession": _ORGANIZATION_TASK_OFFICES[request.task_type],
                "profession_description": f"承担{assignment['name']}，就当前军情向主君进言。",
                "current_location": request.stage_title,
                "environment_description": str(evidence.get("summary") or evidence.get("content") or "")[:1200],
                "recent_events": [
                    f"本回任务：{assignment['name']}",
                    f"所据史料：{canonical_source['work']}｜{canonical_source['scope']}",
                ],
                "knowledge_context": [
                    str(evidence.get("name") or evidence.get("title") or request.knowledge_id),
                    str(evidence.get("summary") or evidence.get("content") or "")[:1800],
                ],
                "motivation_state": motivation,
                "properties_summary": (
                    f"情绪={assignment['state']['emotion']}；胜任度={assignment['readiness']['score']}；"
                    f"职责={assignment['name']}"
                ),
            },
            "current_schedule_description": assignment["name"],
            "current_schedule_importance": assignment["importance"],
            "current_time": str(clock.get("virtualTime") or ""),
        }
        try:
            generated = await upstreams.generate_spontaneous_thought(npc_id, thought_payload)
        except UpstreamUnavailable as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "ainpc_thought_unavailable",
                "AINPC could not form a verified thought; the request can be retried.",
                status_code=503,
            ) from error
        receipt = {
            "requestId": str(request.client_request_id),
            "operationId": operation_id,
            "heroId": hero_id,
            "npcId": str(npc_id),
            "stageId": request.stage_id,
            "taskType": request.task_type,
            "knowledgeId": request.knowledge_id,
            "source": canonical_source,
            "assignment": {
                "planId": assignment["planId"],
                "eventId": assignment["eventId"],
                "name": assignment["name"],
            },
            **generated,
        }
        receipt["councilProposal"] = (
            f"采纳{npc_name}进言，依本回史料执行{assignment['name']}"
        )[:48]
        receipt["digest"] = hashlib.sha256(
            json.dumps(receipt, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        response = {
            "state": "COMPLETED",
            "requestId": str(request.client_request_id),
            "thoughtReceipt": receipt,
        }
        await store.finish_request(
            player_id, request.client_request_id, "COMPLETED", response
        )
        return response

    @router.post("/npcs/{hero_id}/decisions")
    async def decide_with_npc(request: NpcDecisionRequest, hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        body = _payload(request)
        existing = await store.read_request(
            player_id, request.client_request_id, "npc_decision"
        )
        try:
            created, previous = await store.begin_request(player_id, request.client_request_id, "npc_decision", {"hero_id": hero_id, **body})
        except VersionConflict as error:
            raise ApiError("idempotency_conflict", "The request identifier was already used with different input.", status_code=409) from error
        if not created:
            if previous and previous.get("state") == "PENDING":
                raise ApiError("request_in_progress", "The same NPC decision is still being processed.", status_code=409)
            return {"replayed": True, **(previous or {})}
        memory_receipt: dict[str, Any] | None = None
        if request.memory_idempotency_key and request.memory_digest:
            try:
                memory_snapshot = await upstreams.npc_memories(npc_id, limit=100)
            except UpstreamUnavailable as error:
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE", "requestId": str(request.client_request_id)},
                    str(error),
                )
                raise ApiError(
                    "ainpc_memory_unavailable",
                    "AINPC memory is temporarily unavailable; the council can be retried.",
                    status_code=503,
                ) from error
            memory_receipt = next(
                (
                    item
                    for item in _npc_memory_items(memory_snapshot)
                    if item["idempotencyKey"] == request.memory_idempotency_key
                    and item["digest"] == request.memory_digest
                ),
                None,
            )
            if (
                memory_receipt is None
                or request.memory_digest[:12] not in request.question
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED", "requestId": str(request.client_request_id)},
                    "ainpc_memory_unverified",
                )
                raise ApiError(
                    "ainpc_memory_unverified",
                    "The council memory reference is no longer verifiable.",
                    status_code=422,
                )
        dialogue = {
            "dialogues": [{
                "question": request.question,
                "options": [{"index": option.index, "type": "OPTION", "text": option.text} for option in request.options],
                "text_max_length": 0,
            }],
            "metadata": {"source": "dongzhou", "topic": request.topic, "player_id": str(player_id), "request_id": str(request.client_request_id)},
        }
        frozen_response = (
            existing.get("response")
            if existing and existing.get("state") == "RETRYABLE"
            else None
        )
        result = (
            frozen_response.get("decision")
            if isinstance(frozen_response, dict)
            and isinstance(frozen_response.get("decision"), dict)
            else None
        )
        draft = (
            frozen_response.get("dialogueReportDraft")
            if isinstance(frozen_response, dict)
            and isinstance(frozen_response.get("dialogueReportDraft"), dict)
            else None
        )
        if result is None:
            try:
                result = await upstreams.choose_dialogue(npc_id, dialogue)
            except UpstreamUnavailable as error:
                response = {"state": "RETRYABLE", "requestId": str(request.client_request_id)}
                await store.finish_request(player_id, request.client_request_id, "RETRYABLE", response, str(error))
                raise ApiError("ainpc_dialogue_unavailable", "NPC decision is retained for retry.", status_code=503) from error
        raw_decision = result.get("data", result)
        selected_option = next(
            (
                option
                for option in body["options"]
                if isinstance(raw_decision, dict)
                and option["index"] == raw_decision.get("index")
                and raw_decision.get("type") == "OPTION"
            ),
            None,
        )
        if selected_option is None:
            await store.finish_request(
                player_id,
                request.client_request_id,
                "FAILED",
                {"state": "FAILED", "requestId": str(request.client_request_id)},
                "ainpc_decision_invalid",
            )
            raise ApiError(
                "ainpc_decision_invalid",
                "AINPC returned a decision outside the offered council options.",
                status_code=502,
            )
        if draft is None:
            directory = await store.list_npcs(
                settings.game_server_id, include_offline=True
            )
            npc_row = next(
                (item for item in directory if str(item.get("id")) == str(npc_id)),
                None,
            )
            clock = await store.read_game_clock()
            draft = {
                "sourceRecordId": _council_source_record_id(
                    settings.ainpc_game_server_id,
                    npc_id,
                    player_id,
                    request.client_request_id,
                ),
                "gameTime": str(clock.get("virtualTime") or ""),
                "npcName": str((npc_row or {}).get("name") or hero_id),
            }
        report_payload = {
            "npc_name": draft["npcName"],
            "game_time": draft["gameTime"],
            "dialogues": [
                {
                    "source_record_id": draft["sourceRecordId"],
                    "timestamp": draft["gameTime"],
                    "dialogue_npc_id": npc_id,
                    "dialogue_npc_name": draft["npcName"],
                    "question": request.question,
                    "options": [
                        {"index": option.index, "type": "OPTION", "text": option.text}
                        for option in request.options
                    ],
                    "metadata": {
                        "source": "dongzhou",
                        "topic": request.topic,
                        "stage_id": request.stage_id,
                        "player_id": str(player_id),
                        "request_id": str(request.client_request_id),
                    },
                    "select": {
                        "index": selected_option["index"],
                        "type": "OPTION",
                        "text": selected_option["text"],
                    },
                }
            ],
        }
        try:
            report_result = await upstreams.report_dialogue_choice(
                npc_id, report_payload
            )
        except UpstreamUnavailable as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
                "decision": result,
                "dialogueReportDraft": draft,
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "ainpc_dialogue_report_unavailable",
                "The selected council decision is retained until AINPC records it.",
                status_code=503,
            ) from error
        try:
            archived_memory = _npc_memory_receipt(
                await upstreams.remember_dialogue(
                    npc_id, draft["gameTime"], report_payload["dialogues"]
                )
            )
        except UpstreamUnavailable as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
                "decision": result,
                "dialogueReportDraft": draft,
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "ainpc_memory_archive_unavailable",
                "The selected council decision is retained until AINPC remembers it.",
                status_code=503,
            ) from error
        dialogue_receipt = {
            "state": "RECORDED",
            "sourceRecordId": draft["sourceRecordId"],
            "npcId": str(npc_id),
            "gameTime": draft["gameTime"],
            "questionDigest": _council_question_digest(body, selected_option),
            "memoryArchive": archived_memory,
            **report_result,
        }
        dialogue_receipt["digest"] = _canonical_digest(dialogue_receipt)
        response = {
            "state": "COMPLETED",
            "requestId": str(request.client_request_id),
            "decision": result,
            "dialogueReceipt": dialogue_receipt,
            **({"memoryReceipt": memory_receipt} if memory_receipt else {}),
        }
        await store.finish_request(player_id, request.client_request_id, "COMPLETED", response)
        return response

    @router.post("/court/mandates")
    async def issue_court_mandate(
        request: CourtMandateRequest, player_id: UUID = Depends(player)
    ) -> dict[str, Any]:
        kernel_snapshot = kernel.health_status()
        workflow_status = next(
            (
                item
                for item in kernel_snapshot.get("modules", [])
                if item.get("name") == MandateWorkflowModule.name
            ),
            None,
        )
        if not workflow_status or workflow_status.get("state") not in {"ready", "degraded"}:
            raise ApiError(
                "nexus_kernel_unavailable",
                "NexusKernel is not ready to issue a court mandate.",
                status_code=503,
            )
        body = _payload(request)
        try:
            created, previous = await store.begin_request(
                player_id, request.client_request_id, "court_mandate", body
            )
        except VersionConflict as error:
            raise ApiError(
                "idempotency_conflict",
                "The request identifier was already used with different input.",
                status_code=409,
            ) from error
        if not created:
            if previous and previous.get("state") == "PENDING":
                raise ApiError(
                    "request_in_progress",
                    "The same court mandate is still being issued.",
                    status_code=409,
                )
            return {"replayed": True, **(previous or {})}

        council = await store.read_request(
            player_id, request.council_request_id, "npc_decision"
        )
        council_request = council.get("request") if council else None
        council_response = council.get("response") if council else None
        raw_decision = council_response.get("decision") if isinstance(council_response, dict) else None
        decision = raw_decision.get("data", raw_decision) if isinstance(raw_decision, dict) else None
        options = council_request.get("options") if isinstance(council_request, dict) else None
        selected_option = next(
            (
                option
                for option in options or []
                if isinstance(option, dict) and option.get("index") == request.decision_index
            ),
            None,
        )
        if (
            not council
            or council.get("state") != "COMPLETED"
            or council_request.get("hero_id") != request.hero_id
            or not isinstance(decision, dict)
            or decision.get("type") != "OPTION"
            or decision.get("index") != request.decision_index
            or selected_option is None
        ):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_council_unverified",
            )
            raise ApiError(
                "court_council_unverified",
                "The mandate must reference this player's completed NPC council decision.",
                status_code=422,
            )

        dialogue_receipt = (
            council_response.get("dialogueReceipt")
            if isinstance(council_response, dict)
            else None
        )
        expected_source_record_id = _council_source_record_id(
            settings.ainpc_game_server_id,
            stable_npc_id(settings.ainpc_game_server_id, request.hero_id),
            player_id,
            request.council_request_id,
        )
        receipt_without_digest = (
            {key: value for key, value in dialogue_receipt.items() if key != "digest"}
            if isinstance(dialogue_receipt, dict)
            else {}
        )
        inserted_count = (
            dialogue_receipt.get("insertedCount")
            if isinstance(dialogue_receipt, dict)
            else None
        )
        skipped_count = (
            dialogue_receipt.get("skippedCount")
            if isinstance(dialogue_receipt, dict)
            else None
        )
        if (
            not isinstance(dialogue_receipt, dict)
            or dialogue_receipt.get("state") != "RECORDED"
            or dialogue_receipt.get("sourceRecordId") != expected_source_record_id
            or dialogue_receipt.get("npcId")
            != str(stable_npc_id(settings.ainpc_game_server_id, request.hero_id))
            or not str(dialogue_receipt.get("gameTime") or "")
            or dialogue_receipt.get("questionDigest")
            != _council_question_digest(council_request, selected_option)
            or dialogue_receipt.get("digest")
            != _canonical_digest(receipt_without_digest)
            or isinstance(inserted_count, bool)
            or not isinstance(inserted_count, int)
            or inserted_count < 0
            or isinstance(skipped_count, bool)
            or not isinstance(skipped_count, int)
            or skipped_count < 0
            or inserted_count + skipped_count != 1
        ):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_council_dialogue_unrecorded",
            )
            raise ApiError(
                "court_council_dialogue_unrecorded",
                "The mandate requires a verified AINPC dialogue archive receipt.",
                status_code=422,
            )

        current_memories: list[dict[str, Any]] = []
        archived_memory = dialogue_receipt.get("memoryArchive")
        if archived_memory is not None:
            try:
                memory_snapshot = await upstreams.npc_memories(
                    stable_npc_id(settings.ainpc_game_server_id, request.hero_id),
                    limit=100,
                )
            except UpstreamUnavailable as error:
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE"},
                    str(error),
                )
                raise ApiError(
                    "ainpc_memory_unavailable",
                    "AINPC memory is temporarily unavailable; mandate issuance can be retried.",
                    status_code=503,
                ) from error
            current_memories = _npc_memory_items(memory_snapshot)
            if not isinstance(archived_memory, dict) or not any(
                item["idempotencyKey"] == archived_memory.get("idempotencyKey")
                and item["digest"] == archived_memory.get("digest")
                for item in current_memories
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED"},
                    "court_council_memory_archive_unverified",
                )
                raise ApiError(
                    "court_council_memory_archive_unverified",
                    "The council dialogue is not present in AINPC memory.",
                    status_code=422,
                )

        selected_memory = (
            council_response.get("memoryReceipt")
            if isinstance(council_response, dict)
            else None
        )
        if selected_memory is not None:
            if not isinstance(selected_memory, dict) or not any(
                item["idempotencyKey"] == selected_memory.get("idempotencyKey")
                and item["digest"] == selected_memory.get("digest")
                for item in current_memories
            ) or str(selected_memory.get("digest") or "")[:12] not in str(
                council_request.get("question") or ""
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED"},
                    "court_council_memory_unverified",
                )
                raise ApiError(
                    "court_council_memory_unverified",
                    "The council did not retain a verified AINPC memory reference.",
                    status_code=422,
                )

        thought_receipt: dict[str, Any] | None = None
        if request.thought_request_id is not None and request.thought_digest is not None:
            thought_record = await store.read_request(
                player_id, request.thought_request_id, "npc_spontaneous_thought"
            )
            thought_response = thought_record.get("response") if thought_record else None
            candidate = (
                thought_response.get("thoughtReceipt")
                if isinstance(thought_response, dict)
                else None
            )
            candidate_thought = candidate.get("thought") if isinstance(candidate, dict) else None
            candidate_source = candidate.get("source") if isinstance(candidate, dict) else None
            if (
                not thought_record
                or thought_record.get("state") != "COMPLETED"
                or not isinstance(candidate, dict)
                or candidate.get("requestId") != str(request.thought_request_id)
                or candidate.get("digest") != request.thought_digest
                or candidate.get("heroId") != request.hero_id
                or candidate.get("stageId") != request.stage_id
                or candidate.get("taskType") != request.task_type
                or candidate.get("knowledgeId") != request.knowledge_id
                or not isinstance(candidate_source, dict)
                or candidate_source.get("index") != request.evidence_source_index
                or not isinstance(candidate_thought, dict)
                or candidate_thought.get("hasThought") is not True
                or candidate.get("councilProposal") != selected_option.get("text")
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED"},
                    "court_thought_unverified",
                )
                raise ApiError(
                    "court_thought_unverified",
                    "The mandate thought is not a verified selected proposal from this NPC.",
                    status_code=422,
                )
            thought_receipt = candidate

        correspondence: dict[str, Any] | None = None
        if request.correspondence_message_id and request.correspondence_digest:
            raw_correspondence = await store.read_correspondence_message(
                settings.game_server_id, request.correspondence_message_id
            )
            if raw_correspondence is not None:
                correspondence = _correspondence_evidence(raw_correspondence)
            npc_id = str(stable_npc_id(settings.ainpc_game_server_id, request.hero_id))
            if (
                correspondence is None
                or correspondence["digest"] != request.correspondence_digest
                or npc_id not in {correspondence["speakerId"], correspondence["targetId"]}
                or f"耳报印记：{request.correspondence_digest[:12]}" not in str(council_request.get("question") or "")
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED"},
                    "court_correspondence_unverified",
                )
                raise ApiError(
                    "court_correspondence_unverified",
                    "The selected AINPC correspondence is not a verified source for this mandate.",
                    status_code=422,
                )

        try:
            entries = await upstreams.stage_knowledge(request.stage_id)
        except (UpstreamUnavailable, OSError, ValueError) as error:
            response = {"state": "RETRYABLE", "requestId": str(request.client_request_id)}
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "knowledge_unavailable",
                "Published knowledge is temporarily unavailable; the mandate can be retried.",
                status_code=503,
            ) from error
        evidence = next(
            (
                entry
                for entry in entries
                if isinstance(entry, dict)
                and str(entry.get("id") or entry.get("aku_id") or "")
                == request.knowledge_id
                and str(entry.get("stageId") or request.stage_id) == request.stage_id
            ),
            None,
        )
        if evidence is None:
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_knowledge_unverified",
            )
            raise ApiError(
                "court_knowledge_unverified",
                "The mandate must reference published knowledge for this stage.",
                status_code=422,
            )

        source_details = evidence.get("sourceDetails")
        if not isinstance(source_details, list) or not source_details:
            source_details = [
                {"work": str(value), "tier": "来源", "scope": "", "url": str(value)}
                for value in evidence.get("sources", [])
                if isinstance(value, str) and value
            ]
        source = (
            source_details[request.evidence_source_index]
            if request.evidence_source_index < len(source_details)
            else None
        )
        if not isinstance(source, dict) or not str(source.get("work") or "").strip():
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_evidence_source_unverified",
            )
            raise ApiError(
                "court_evidence_source_unverified",
                "The selected source is not published with this knowledge entry.",
                status_code=422,
            )
        canonical_source = {
            "index": request.evidence_source_index,
            "work": str(source.get("work") or ""),
            "tier": str(source.get("tier") or "来源"),
            "scope": str(source.get("scope") or ""),
            "url": str(source.get("url") or ""),
        }
        retrieval: dict[str, Any] | None = None
        retrieval_receipt: dict[str, str] | None = None
        if bool(request.knowledge_search_receipt_id) != bool(request.knowledge_search_receipt_digest):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_knowledge_receipt_incomplete",
            )
            raise ApiError(
                "court_knowledge_receipt_incomplete",
                "A knowledge search receipt requires both its ID and digest.",
                status_code=422,
            )
        if request.knowledge_search_receipt_id and request.knowledge_search_receipt_digest:
            receipt_id = request.knowledge_search_receipt_id
            receipt_request = await store.read_external_request(
                player_id, receipt_id, "knowledge_search"
            )
            try:
                receipt_request_id = UUID(receipt_id.rsplit(":", 1)[-1])
            except ValueError:
                receipt_request_id = None
            receipt_record = (
                await store.read_request(player_id, receipt_request_id, "knowledge_search")
                if receipt_request_id is not None
                else None
            )
            receipt_response = receipt_record.get("response") if receipt_record else None
            receipt = receipt_response.get("searchReceipt") if isinstance(receipt_response, dict) else None
            receipt_result = next(
                (
                    item
                    for item in receipt_response.get("results", [])
                    if isinstance(item, dict)
                    and str(item.get("id") or item.get("aku_id") or "") == request.knowledge_id
                    and str(item.get("stageId") or "") == request.stage_id
                ),
                None,
            ) if isinstance(receipt_response, dict) else None
            if (
                receipt_request is None
                or receipt_record is None
                or receipt_record.get("state") != "COMPLETED"
                or receipt_record.get("externalId") != receipt_id
                or not isinstance(receipt, dict)
                or receipt.get("digest") != request.knowledge_search_receipt_digest
                or receipt.get("stageId") != request.stage_id
                or not isinstance(receipt_result, dict)
                or not isinstance(receipt_result.get("retrieval"), dict)
            ):
                await store.finish_request(
                    player_id,
                    request.client_request_id,
                    "REJECTED",
                    {"state": "REJECTED"},
                    "court_knowledge_receipt_unverified",
                )
                raise ApiError(
                    "court_knowledge_receipt_unverified",
                    "The knowledge search receipt does not prove this stage evidence.",
                    status_code=422,
                )
            retrieval = receipt_result["retrieval"]
            retrieval_receipt = {
                "id": receipt_id,
                "digest": request.knowledge_search_receipt_digest,
            }
        source_marker = f"选证：{canonical_source['work']}｜{canonical_source['tier']}"
        if source_marker not in str(council_request.get("question") or ""):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_council_source_unverified",
            )
            raise ApiError(
                "court_council_source_unverified",
                "The NPC council did not deliberate on the selected published source.",
                status_code=422,
            )
        if retrieval_receipt and f"检索回执：{retrieval_receipt['digest'][:12]}" not in str(council_request.get("question") or ""):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_council_retrieval_unverified",
            )
            raise ApiError(
                "court_council_retrieval_unverified",
                "The NPC council did not deliberate on the sealed retrieval evidence.",
                status_code=422,
            )

        try:
            assignment = await resolve_npc_assignment(
                request.hero_id, request.task_type, request.stage_id
            )
        except ApiError as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise
        if (
            assignment["planId"] != request.schedule_plan_id
            or assignment["eventId"] != request.schedule_event_id
        ):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_schedule_assignment_stale",
            )
            raise ApiError(
                "court_schedule_assignment_stale",
                "The selected NPC duty is no longer current; refresh the schedule before issuing the mandate.",
                status_code=422,
            )

        emergency_description = " ".join(
            part.strip()
            for part in (
                request.stage_title,
                str(evidence.get("name") or evidence.get("title") or ""),
                str(evidence.get("summary") or evidence.get("content") or ""),
                str(selected_option.get("text") or ""),
                request.task_type,
            )
            if part.strip()
        )[:1200]
        clock = await store.read_game_clock()
        emergency_timestamp = str(clock.get("virtualTime") or "")
        try:
            emergency = await upstreams.evaluate_emergency(
                stable_npc_id(settings.ainpc_game_server_id, request.hero_id),
                emergency_timestamp,
                emergency_description,
            )
        except UpstreamUnavailable as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "ainpc_emergency_unavailable",
                "AINPC could not assess this military report; the mandate can be retried.",
                status_code=503,
            ) from error
        emergency = {
            **emergency,
            "assessedAt": emergency_timestamp,
            "event": emergency_description,
        }

        mandate_id = stable_event_id(player_id, request.client_request_id)
        evidence_trace = {
            "id": request.knowledge_id,
            "name": str(evidence.get("name") or evidence.get("title") or request.knowledge_id),
            "summary": str(evidence.get("summary") or evidence.get("content") or ""),
            "source": canonical_source,
        }
        if retrieval is not None and retrieval_receipt is not None:
            evidence_trace["retrieval"] = retrieval
            evidence_trace["searchReceipt"] = retrieval_receipt
        evidence_fit = _evidence_task_fit(
            request.task_type,
            canonical_source,
            str(selected_option.get("text") or ""),
            has_search_receipt=retrieval_receipt is not None,
        )
        trace = {
            "id": mandate_id,
            "stageId": request.stage_id,
            "stageTitle": request.stage_title,
            "heroId": request.hero_id,
            "taskType": request.task_type,
            "evidence": evidence_trace,
            "evidenceFit": evidence_fit,
            "council": {
                "requestId": str(request.council_request_id),
                "question": str(council_request.get("question") or ""),
                "index": request.decision_index,
                "text": str(selected_option.get("text") or ""),
                "dialogueReceipt": dialogue_receipt,
                **({"memory": selected_memory} if selected_memory else {}),
            },
            "assignment": assignment,
            "emergency": emergency,
            "kernel": {
                "module": MandateWorkflowModule.name,
                "moduleVersion": MandateWorkflowModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": str(workflow_status["state"]).upper(),
            },
        }
        if thought_receipt is not None:
            trace["thought"] = thought_receipt
            trace["council"]["thought"] = {
                "requestId": thought_receipt["requestId"],
                "digest": thought_receipt["digest"],
            }
        if correspondence is not None:
            trace["correspondence"] = correspondence
            trace["council"]["correspondence"] = correspondence
        if selected_memory is not None:
            trace["memory"] = selected_memory
            trace["council"]["memory"] = selected_memory
        if request.operation is not None:
            trace["operation"] = request.operation.model_dump(mode="json")
        # Canonical JSON keeps the seal stable across retries and process restarts.
        digest = hashlib.sha256(
            json.dumps(trace, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        response = mandate_workflow.draft(trace, digest)
        await store.finish_request(
            player_id,
            request.client_request_id,
            "REQUIRES_ACTION",
            response,
            external_id=mandate_id,
        )
        return response

    @router.post("/court/mandates/{mandate_id}/resume")
    async def resume_court_mandate(
        mandate_id: str,
        request: CourtMandateResumeRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        original = await store.read_external_request(
            player_id, mandate_id, "court_mandate"
        )
        try:
            request_id = UUID(mandate_id.rsplit(":", 1)[-1])
        except ValueError as error:
            raise ApiError(
                "court_mandate_not_found",
                "The court mandate was not found.",
                status_code=404,
            ) from error
        record = await store.read_request(player_id, request_id, "court_mandate")
        if original is None or record is None or record.get("externalId") != mandate_id:
            raise ApiError(
                "court_mandate_not_found",
                "The court mandate was not found.",
                status_code=404,
            )
        response = record.get("response")
        if record.get("state") in {"ISSUED", "REJECTED"} and isinstance(response, dict):
            return {"replayed": True, **response}
        action = response.get("action") if isinstance(response, dict) else None
        if record.get("state") != "REQUIRES_ACTION" or not isinstance(action, dict):
            raise ApiError(
                "court_mandate_not_resumable",
                "The court mandate is not waiting for player action.",
                status_code=409,
            )
        if action.get("actionId") != str(request.action_id):
            raise ApiError(
                "court_mandate_action_mismatch",
                "The player action does not match this court mandate.",
                status_code=409,
            )
        result = mandate_workflow.resume(response, request.decision)
        transitioned = await store.transition_request(
            player_id,
            request_id,
            "court_mandate",
            "REQUIRES_ACTION",
            result["state"],
            result,
        )
        if not transitioned:
            latest = await store.read_request(player_id, request_id, "court_mandate")
            latest_response = latest.get("response") if latest else None
            if latest and latest.get("state") in {"ISSUED", "REJECTED"} and isinstance(latest_response, dict):
                return {"replayed": True, **latest_response}
            raise ApiError(
                "court_mandate_not_resumable",
                "The court mandate is not waiting for player action.",
                status_code=409,
            )
        return result

    @router.post("/court/mandates/{mandate_id}/schedule")
    async def schedule_court_mandate(
        mandate_id: str,
        request: CourtMandateScheduleRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        try:
            mandate_request_id = UUID(mandate_id.rsplit(":", 1)[-1])
        except ValueError as error:
            raise ApiError(
                "court_mandate_not_found",
                "The court mandate was not found.",
                status_code=404,
            ) from error
        mandate_record = await store.read_request(
            player_id, mandate_request_id, "court_mandate"
        )
        mandate_response = mandate_record.get("response") if mandate_record else None
        mandate = (
            mandate_response.get("mandate")
            if isinstance(mandate_response, dict)
            else None
        )
        if (
            not mandate_record
            or mandate_record.get("externalId") != mandate_id
            or mandate_record.get("state") != "ISSUED"
            or not isinstance(mandate, dict)
            or mandate.get("state") != "ISSUED"
        ):
            raise ApiError(
                "court_mandate_not_issued",
                "Only an issued court mandate can interrupt an NPC schedule.",
                status_code=409,
            )
        if mandate.get("digest") != request.mandate_digest:
            raise ApiError(
                "court_mandate_mismatch",
                "The court mandate seal does not match this schedule request.",
                status_code=422,
            )

        request_body = request.model_dump(mode="json")
        try:
            created, existing = await store.begin_request(
                player_id,
                request.client_request_id,
                "court_mandate_schedule",
                {"mandateId": mandate_id, **request_body},
            )
        except VersionConflict as error:
            raise ApiError(
                "idempotency_conflict",
                "The request identifier was already used with different input.",
                status_code=409,
            ) from error
        if not created:
            if existing and existing.get("state") == "COMPLETED":
                return {"replayed": True, **existing}
            raise ApiError(
                "court_schedule_in_progress",
                "The same schedule interruption is still being applied.",
                status_code=409,
            )

        assignment = mandate.get("assignment")
        emergency = mandate.get("emergency")
        thought_receipt = mandate.get("thought")
        thought = (
            thought_receipt.get("thought")
            if isinstance(thought_receipt, dict)
            else None
        )
        if not isinstance(assignment, dict) or not isinstance(emergency, dict):
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "court_mandate_trace_invalid",
            )
            raise ApiError(
                "court_mandate_trace_invalid",
                "The issued mandate lacks a verified duty or emergency trace.",
                status_code=422,
            )

        event_id = f"dongzhou-mandate-{request.mandate_digest[:32]}"
        clock = await store.read_game_clock()
        event_description = str(emergency.get("event") or mandate.get("stageTitle") or "")
        event_importance = float(emergency.get("score") or assignment.get("importance") or 0)
        current_importance = float(assignment.get("importance") or 0)
        target_motives = (
            thought.get("targetMotives")
            if isinstance(thought, dict) and isinstance(thought.get("targetMotives"), list)
            else []
        )
        try:
            interruption = await upstreams.interrupt_npc_schedule(
                stable_npc_id(
                    settings.ainpc_game_server_id, str(mandate.get("heroId") or "")
                ),
                {
                    "event_id": event_id,
                    "event_source": "event_report",
                    "event_description": event_description[:2000],
                    "event_importance": max(0.0, min(100.0, event_importance)),
                    "urgency_level": "urgent" if emergency.get("urgent") is True else "normal",
                    "target_motives": target_motives,
                    "current_schedule_description": str(assignment.get("name") or "")[:1000],
                    "current_schedule_importance": max(0.0, min(100.0, current_importance)),
                    "current_time": str(clock.get("virtualTime") or ""),
                    "raw_data": {
                        "mandate_id": mandate_id,
                        "mandate_digest": request.mandate_digest,
                        "stage_id": str(mandate.get("stageId") or ""),
                        "task_type": str(mandate.get("taskType") or ""),
                    },
                },
            )
        except UpstreamUnavailable as error:
            retryable = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
                "mandateId": mandate_id,
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                retryable,
                str(error),
            )
            raise ApiError(
                "ainpc_schedule_interruption_unavailable",
                "AINPC could not apply the issued mandate to the NPC schedule; it can be retried.",
                status_code=503,
            ) from error
        if interruption["eventId"] != event_id:
            await store.finish_request(
                player_id,
                request.client_request_id,
                "REJECTED",
                {"state": "REJECTED"},
                "ainpc_schedule_interruption_mismatch",
            )
            raise ApiError(
                "ainpc_schedule_interruption_mismatch",
                "AINPC returned a schedule result for a different mandate event.",
                status_code=502,
            )

        receipt = {
            "requestId": str(request.client_request_id),
            "mandateId": mandate_id,
            "mandateDigest": request.mandate_digest,
            "heroId": str(mandate.get("heroId") or ""),
            "npcId": str(
                stable_npc_id(
                    settings.ainpc_game_server_id, str(mandate.get("heroId") or "")
                )
            ),
            "eventId": event_id,
            "action": interruption["action"],
            "scheduleId": interruption["scheduleId"],
            "scheduleName": interruption["scheduleName"],
            "duplicate": interruption["duplicate"],
            "reason": interruption["reason"],
            "appliedAt": str(clock.get("virtualTime") or ""),
        }
        receipt["digest"] = hashlib.sha256(
            json.dumps(
                receipt,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        response = {"state": "COMPLETED", "scheduleReceipt": receipt}
        await store.finish_request(
            player_id,
            request.client_request_id,
            "COMPLETED",
            response,
            external_id=event_id,
        )
        return response

    @router.get("/organization/roster")
    async def read_organization_roster(
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        if not settings.orgflow_org_id or not settings.orgflow_hero_members:
            raise ApiError(
                "organization_not_configured",
                "Organization integration is not configured.",
                status_code=503,
            )
        try:
            response = await upstreams.organization_roster(settings.orgflow_org_id)
            if not isinstance(response, dict):
                raise ValueError("roster response must be an object")
            return _organization_roster_view(
                response.get("data"),
                settings,
                player_subject_id=str(
                    stable_player_id(settings.ainpc_game_server_id, player_id)
                ),
            )
        except UpstreamUnavailable as error:
            raise ApiError(
                "organization_roster_unavailable",
                "Organization roster is temporarily unavailable.",
                status_code=503,
            ) from error
        except ValueError as error:
            raise ApiError(
                "organization_roster_contract_invalid",
                "Organization roster response is invalid.",
                status_code=502,
            ) from error
        except (AttributeError, ValueError) as error:
            raise ApiError(
                "organization_roster_contract_invalid",
                "Organization roster response is invalid.",
                status_code=502,
            ) from error

    @router.get("/organization/inventory")
    async def read_organization_inventory(
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        del player_id
        if not settings.orgflow_org_id:
            raise ApiError(
                "organization_not_configured",
                "Organization integration is not configured.",
                status_code=503,
            )
        try:
            response = await upstreams.organization_inventory(settings.orgflow_org_id)
            if not isinstance(response, dict):
                raise ValueError("inventory response must be an object")
            return _organization_inventory_view(response.get("data"), settings)
        except UpstreamUnavailable as error:
            raise ApiError(
                "organization_inventory_unavailable",
                "Organization inventory is temporarily unavailable.",
                status_code=503,
            ) from error
        except (AttributeError, ValueError) as error:
            raise ApiError(
                "organization_inventory_contract_invalid",
                "Organization inventory response is invalid.",
                status_code=502,
            ) from error

    @router.post("/organization/inventory/requisitions")
    async def requisition_organization_inventory(
        request: OrganizationInventoryRequisitionRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        if not settings.orgflow_org_id:
            raise ApiError(
                "organization_not_configured",
                "Organization integration is not configured.",
                status_code=503,
            )
        payload = request.model_dump(mode="json")
        try:
            should_process, previous = await store.begin_request(
                player_id,
                request.client_request_id,
                "organization_inventory_requisition",
                payload,
                retry_states=(),
                reclaim_pending=False,
            )
        except VersionConflict as error:
            raise ApiError(
                "organization_inventory_requisition_conflict",
                "This inventory requisition ID was already used with different input.",
                status_code=409,
            ) from error
        if not should_process:
            if isinstance(previous, dict) and (
                previous.get("state") in {"COMPLETED", "REJECTED"}
                or isinstance(previous.get("requisition"), dict)
            ):
                return {"replayed": True, **previous}
            raise ApiError(
                "organization_inventory_requisition_in_progress",
                "This inventory requisition is already in progress.",
                status_code=409,
            )

        resource_key = "task.execution"
        provisions = request.units * 3 // 5
        requisition_id = (
            f"dongzhou:requisition:{player_id}:{request.client_request_id}"
        )
        trace = {
            "id": requisition_id,
            "requestId": str(request.client_request_id),
            "stageId": request.stage_id,
            "resourceKey": resource_key,
            "units": request.units,
            "effect": {"provisions": provisions},
            "kernel": {
                "module": MandateWorkflowModule.name,
                "moduleVersion": MandateWorkflowModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": "REQUIRES_ACTION",
            },
        }
        digest = hashlib.sha256(
            json.dumps(
                trace,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        result = mandate_workflow.draft_inventory_requisition(trace, digest)
        await store.finish_request(
            player_id,
            request.client_request_id,
            "REQUIRES_ACTION",
            result,
            external_id=requisition_id,
        )
        return result

    @router.post("/organization/inventory/requisitions/{requisition_id}/resume")
    async def resume_organization_inventory_requisition(
        requisition_id: str,
        request: CourtMandateResumeRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        if not settings.orgflow_org_id:
            raise ApiError(
                "organization_not_configured",
                "Organization integration is not configured.",
                status_code=503,
            )
        try:
            request_id = UUID(requisition_id.rsplit(":", 1)[-1])
        except ValueError as error:
            raise ApiError(
                "organization_inventory_requisition_not_found",
                "The inventory requisition was not found.",
                status_code=404,
            ) from error
        record = await store.read_request(
            player_id,
            request_id,
            "organization_inventory_requisition",
        )
        if record is None or record.get("externalId") != requisition_id:
            raise ApiError(
                "organization_inventory_requisition_not_found",
                "The inventory requisition was not found.",
                status_code=404,
            )
        previous = record.get("response")
        if record.get("state") in {"COMPLETED", "REJECTED"} and isinstance(
            previous, dict
        ):
            return {"replayed": True, **previous}
        action = previous.get("action") if isinstance(previous, dict) else None
        requisition = (
            previous.get("requisition") if isinstance(previous, dict) else None
        )
        if not isinstance(action, dict) or not isinstance(requisition, dict):
            raise ApiError(
                "organization_inventory_requisition_not_resumable",
                "The inventory requisition is not waiting for player action.",
                status_code=409,
            )
        if action.get("actionId") != str(request.action_id):
            raise ApiError(
                "organization_inventory_requisition_action_mismatch",
                "The player action does not match this inventory requisition.",
                status_code=409,
            )
        request_payload = record.get("request") or {}
        units = request_payload.get("units")
        stage_id = request_payload.get("stage_id")
        if isinstance(units, bool) or not isinstance(units, int) or not stage_id:
            raise ApiError(
                "organization_inventory_requisition_contract_invalid",
                "The stored inventory requisition is invalid.",
                status_code=500,
            )
        if request.decision == "REJECT":
            if record.get("state") != "REQUIRES_ACTION":
                raise ApiError(
                    "organization_inventory_requisition_not_rejectable",
                    "An approved inventory requisition cannot be rejected while it is settling.",
                    status_code=409,
                )
            result = {
                "state": "REJECTED",
                "requestId": str(request_id),
                "stageId": str(requisition["stageId"]),
                "requisition": {
                    **requisition,
                    "state": "REJECTED",
                    "kernel": {
                        **dict(requisition.get("kernel") or {}),
                        "state": "REJECTED",
                    },
                },
            }
            transitioned = await store.transition_request(
                player_id,
                request_id,
                "organization_inventory_requisition",
                "REQUIRES_ACTION",
                "REJECTED",
                result,
            )
            if transitioned:
                return result
            latest = await store.read_request(
                player_id, request_id, "organization_inventory_requisition"
            )
            latest_response = latest.get("response") if latest else None
            if latest and latest.get("state") == "REJECTED" and isinstance(
                latest_response, dict
            ):
                return {"replayed": True, **latest_response}
            raise ApiError(
                "organization_inventory_requisition_not_rejectable",
                "The inventory requisition is already settling.",
                status_code=409,
            )

        pending = {
            **previous,
            "state": "PENDING",
            "requisition": {
                **requisition,
                "state": "APPROVING",
                "kernel": {
                    **dict(requisition.get("kernel") or {}),
                    "state": "APPROVING",
                },
            },
        }
        claimed = await store.claim_request(
            player_id,
            request_id,
            "organization_inventory_requisition",
            ("REQUIRES_ACTION", "RETRYABLE"),
            pending,
        )
        if not claimed:
            latest = await store.read_request(
                player_id, request_id, "organization_inventory_requisition"
            )
            latest_response = latest.get("response") if latest else None
            if latest and latest.get("state") in {"COMPLETED", "REJECTED"} and isinstance(
                latest_response, dict
            ):
                return {"replayed": True, **latest_response}
            raise ApiError(
                "organization_inventory_requisition_in_progress",
                "This inventory requisition is already settling.",
                status_code=409,
            )

        resource_key = "task.execution"
        delta_units = -units
        provisions = units * 3 // 5
        try:
            upstream_response = await upstreams.adjust_organization_inventory(
                settings.orgflow_org_id,
                {
                    "resource_key": resource_key,
                    "delta_units": delta_units,
                    "reason_code": "CAMPAIGN_REQUISITION_APPROVED",
                },
                idempotency_key=(
                    f"dongzhou-campaign-requisition:{player_id}:"
                    f"{request_id}"
                ),
            )
            receipt = _organization_inventory_requisition_view(
                upstream_response.get("data")
                if isinstance(upstream_response, dict)
                else None,
                settings,
                resource_key=resource_key,
                delta_units=delta_units,
            )
        except UpstreamUnavailable as error:
            insufficient = (
                error.status_code == 409
                and error.error_code == "organization_inventory_balance_insufficient"
            )
            await store.finish_request(
                player_id,
                request_id,
                "RETRYABLE",
                {
                    **previous,
                    "state": "RETRYABLE",
                    "requisition": {
                        **requisition,
                        "state": "APPROVAL_RETRYABLE",
                        "kernel": {
                            **dict(requisition.get("kernel") or {}),
                            "state": "APPROVAL_RETRYABLE",
                        },
                    },
                },
                error=(
                    "organization_inventory_insufficient"
                    if insufficient
                    else "organization_inventory_unavailable"
                ),
                external_id=requisition_id,
            )
            raise ApiError(
                "organization_inventory_insufficient"
                if insufficient
                else "organization_inventory_unavailable",
                "The public inventory does not have enough task credit."
                if insufficient
                else "The organization inventory is temporarily unavailable.",
                status_code=409 if insufficient else 503,
            ) from error
        except (AttributeError, TypeError, ValueError) as error:
            await store.finish_request(
                player_id,
                request_id,
                "RETRYABLE",
                {
                    **previous,
                    "state": "RETRYABLE",
                    "requisition": {
                        **requisition,
                        "state": "APPROVAL_RETRYABLE",
                        "kernel": {
                            **dict(requisition.get("kernel") or {}),
                            "state": "APPROVAL_RETRYABLE",
                        },
                    },
                },
                error="organization_inventory_contract_invalid",
                external_id=requisition_id,
            )
            raise ApiError(
                "organization_inventory_contract_invalid",
                "The organization inventory returned an invalid requisition receipt.",
                status_code=502,
            ) from error

        result = {
            "state": "COMPLETED",
            "requestId": str(request_id),
            "stageId": str(stage_id),
            "requisition": {
                **requisition,
                "state": "COMPLETED",
                "kernel": {
                    **dict(requisition.get("kernel") or {}),
                    "state": "COMPLETED",
                },
            },
            "inventoryDebit": receipt,
            "effect": {"provisions": provisions},
        }
        await store.finish_request(
            player_id,
            request_id,
            "COMPLETED",
            result,
            external_id=requisition_id,
        )
        return result

    @router.post("/organization/tasks")
    async def create_organization_task(request: OrganizationTaskRequest, player_id: UUID = Depends(player)) -> dict[str, Any]:
        if not settings.orgflow_org_id or not settings.orgflow_manager_member_id:
            raise ApiError("organization_not_configured", "Organization integration is not configured.", status_code=503)
        slot_id = settings.orgflow_hero_slots.get(request.assignee_hero_id)
        member_id = settings.orgflow_hero_members.get(request.assignee_hero_id)
        if not slot_id or not member_id:
            raise ApiError("organization_hero_unconfigured", "The selected hero is not mapped to an active organization member and position.", status_code=422)
        mandate_id = request.parameters.mandate_id
        mandate_digest = request.parameters.mandate_digest
        mandate: dict[str, Any] | None = None
        if bool(mandate_id) != bool(mandate_digest):
            raise ApiError(
                "court_mandate_incomplete",
                "Organization orders must provide both mandate ID and digest.",
                status_code=422,
            )
        if mandate_id and mandate_digest:
            mandate_record = await store.read_external_request(
                player_id, mandate_id, "court_mandate"
            )
            try:
                mandate_request_id = UUID(mandate_id.rsplit(":", 1)[-1])
            except ValueError as error:
                raise ApiError(
                    "court_mandate_mismatch",
                    "The court mandate does not match this organization order.",
                    status_code=422,
                ) from error
            mandate_result = await store.read_request(
                player_id, mandate_request_id, "court_mandate"
            )
            mandate = (
                mandate_result.get("response", {}).get("mandate")
                if mandate_result
                else None
            )
            if (
                mandate_record is None
                or mandate_result.get("state") != "ISSUED"
                or not isinstance(mandate, dict)
                or mandate.get("state") != "ISSUED"
                or mandate.get("digest") != mandate_digest
                or mandate_record.get("stage_id") != request.stage_id
                or mandate_record.get("hero_id") != request.assignee_hero_id
                or mandate_record.get("task_type") != request.task_type
            ):
                raise ApiError(
                    "court_mandate_mismatch",
                    "The court mandate does not match this organization order.",
                    status_code=422,
                )
            schedule_event_id = f"dongzhou-mandate-{mandate_digest[:32]}"
            schedule_request = await store.read_external_request(
                player_id, schedule_event_id, "court_mandate_schedule"
            )
            if (
                not isinstance(schedule_request, dict)
                or schedule_request.get("mandateId") != mandate_id
                or schedule_request.get("mandate_digest") != mandate_digest
            ):
                raise ApiError(
                    "court_mandate_schedule_required",
                    "The issued mandate must receive an AINPC schedule decision before organization dispatch.",
                    status_code=409,
                )
        body = _payload(request)
        try:
            created, previous = await store.begin_request(player_id, request.client_request_id, "organization_task", body)
        except VersionConflict as error:
            raise ApiError("idempotency_conflict", "The request identifier was already used with different input.", status_code=409) from error
        if not created:
            if previous and previous.get("state") == "PENDING":
                raise ApiError("request_in_progress", "The same organization order is still being processed.", status_code=409)
            return {"replayed": True, **(previous or {})}
        effective_parameters = request.parameters.model_dump(
            exclude={"mandate_id", "mandate_digest"}
        )
        brief = request.brief
        operation = mandate.get("operation") if isinstance(mandate, dict) else None
        if isinstance(operation, dict) and operation.get("kind") == "diplomacy":
            operation_reference = hashlib.sha256(
                json.dumps(operation, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
            ).hexdigest()[:16]
            brief = (
                "Conduct the sealed fictional Dongzhou diplomacy mission for polity "
                f"{operation['target_id']}. Nexus operation reference {operation_reference}. "
                "Report only the in-game outcome."
            )
        assignment = mandate.get("assignment") if isinstance(mandate, dict) else None
        if isinstance(assignment, dict):
            readiness = assignment.get("readiness")
            readiness_note = (
                f" Readiness {readiness.get('score')}/100 ({readiness.get('band')})."
                if isinstance(readiness, dict)
                else ""
            )
            personality = assignment.get("personality")
            fit = personality.get("fit") if isinstance(personality, dict) else None
            personality_note = (
                f" Personality task fit {fit.get('score')}/100 ({fit.get('band')})."
                if isinstance(fit, dict) and fit.get("available") is True
                else ""
            )
            motivation = assignment.get("motivation")
            willingness = motivation.get("fit") if isinstance(motivation, dict) else None
            motivation_note = (
                f" Motivation task willingness {willingness.get('score')}/100 ({willingness.get('band')})."
                if isinstance(willingness, dict) and willingness.get("available") is True
                else ""
            )
            quality = assignment.get("quality")
            quality_fit = quality.get("fit") if isinstance(quality, dict) else None
            quality_note = (
                f" Stable quality task fit {quality_fit.get('score')}/100 ({quality_fit.get('band')})."
                if isinstance(quality_fit, dict) and quality_fit.get("available") is True
                else ""
            )
            duty_note = (
                f" Bound AINPC duty {assignment.get('eventId')} "
                f"({assignment.get('name')}) on {assignment.get('date')} from plan "
                f"{assignment.get('planId')}.{readiness_note}{personality_note}{motivation_note}{quality_note}"
            )
            brief = brief.rstrip()[: max(0, 1000 - len(duty_note))] + duty_note
        evidence_fit = mandate.get("evidenceFit") if isinstance(mandate, dict) else None
        if isinstance(evidence_fit, dict):
            evidence_note = (
                f" Sealed evidence fit {evidence_fit.get('factor')}/9 "
                f"({evidence_fit.get('band')}) for {evidence_fit.get('taskType')}."
            )
            brief = brief.rstrip()[: max(0, 1000 - len(evidence_note))] + evidence_note
        emergency = mandate.get("emergency") if isinstance(mandate, dict) else None
        if isinstance(emergency, dict):
            emergency_note = (
                f" AINPC emergency assessment: "
                f"{'urgent' if emergency.get('urgent') is True else 'routine'}, "
                f"score {emergency.get('score')}, trace "
                f"{emergency.get('interruptTraceId') or 'none'}."
            )
            brief = brief.rstrip()[: max(0, 1000 - len(emergency_note))] + emergency_note
        try:
            roster_response = await upstreams.organization_roster(
                settings.orgflow_org_id
            )
            roster = _organization_roster_view(
                roster_response.get("data"), settings
            )
            hierarchy_version = roster["organization"]["hierarchyVersion"]
        except UpstreamUnavailable as error:
            response = {
                "state": "RETRYABLE",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "RETRYABLE",
                response,
                str(error),
            )
            raise ApiError(
                "organization_roster_unavailable",
                "The order is retained until the current organization hierarchy can be read.",
                status_code=503,
            ) from error
        except (KeyError, TypeError, ValueError) as error:
            response = {
                "state": "FAILED",
                "requestId": str(request.client_request_id),
            }
            await store.finish_request(
                player_id,
                request.client_request_id,
                "FAILED",
                response,
                str(error),
            )
            raise ApiError(
                "organization_roster_contract_invalid",
                "Organization roster response is invalid.",
                status_code=502,
            ) from error
        trigger = {
            "source": "ORGANIZATION_EVENT",
            "source_event_id": stable_event_id(player_id, request.client_request_id),
            "manager_member_id": settings.orgflow_manager_member_id,
            "target_position_slot_id": slot_id,
            "direct_responsible_member_id": member_id,
            "expected_recipient_subject_type": "NPC",
            "expected_recipient_subject_id": str(
                stable_npc_id(settings.ainpc_game_server_id, request.assignee_hero_id)
            ),
            "task_code": f"dongzhou.{request.task_type}",
            "expected_hierarchy_version": hierarchy_version,
            "parameters": {**effective_parameters, "stage_id": request.stage_id, "stage_title": request.stage_title, "assignee_hero_id": request.assignee_hero_id},
            "brief": brief,
        }
        try:
            result = await upstreams.trigger_virtual_task(settings.orgflow_org_id, trigger)
        except UpstreamUnavailable as error:
            if error.status_code in {400, 404, 409, 422}:
                code = error.error_code or "organization_task_rejected"
                detail = error.response_payload or {}
                upstream_error = detail.get("error") if isinstance(detail.get("error"), dict) else {}
                message = str(upstream_error.get("message") or detail.get("message") or "The organization rejected this order.")
                response = {"state": "REJECTED", "requestId": str(request.client_request_id), "error": {"code": code, "message": message}}
                await store.finish_request(player_id, request.client_request_id, "REJECTED", response, message)
                raise ApiError(code, message, status_code=error.status_code) from error
            response = {"state": "RETRYABLE", "requestId": str(request.client_request_id)}
            await store.finish_request(player_id, request.client_request_id, "RETRYABLE", response, str(error))
            raise ApiError("organization_unavailable", "The order is retained and can be retried with the same request ID.", status_code=503) from error
        task_snapshot = result.get("data", result)
        task_id = str(task_snapshot.get("task_id") or "") if isinstance(task_snapshot, dict) else ""
        if not task_id:
            await store.finish_request(player_id, request.client_request_id, "FAILED", {"state": "FAILED"}, "orgflow_task_id_missing")
            raise ApiError("organization_contract_invalid", "Organization service returned no task ID.", status_code=502)
        response = {"state": "ACCEPTED", "requestId": str(request.client_request_id), "taskId": task_id, "result": result}
        await store.finish_request(player_id, request.client_request_id, "ACCEPTED", response, external_id=task_id)
        return response

    async def _organization_task_state(task_key: str, player_id: UUID) -> dict[str, Any]:
        original = await store.read_external_request(
            player_id, task_key, "organization_task"
        )
        if original is None:
            raise ApiError("organization_task_not_found", "Task does not belong to this player.", status_code=404)
        try:
            result = await upstreams.get_virtual_task(settings.orgflow_org_id, task_key)
        except UpstreamUnavailable as error:
            raise ApiError("organization_unavailable", "Organization task state is temporarily unavailable.", status_code=503) from error
        snapshot = result.get("data", result) if isinstance(result, dict) else None
        if not isinstance(snapshot, dict):
            raise ApiError(
                "organization_contract_invalid",
                "Organization service returned an invalid task snapshot.",
                status_code=502,
            )
        try:
            follow_ups = _derived_follow_ups(task_key, original, snapshot)
            for follow_up in follow_ups:
                if follow_up["state"] != "CREATED" or not follow_up["taskId"]:
                    continue
                parameters = original.get("parameters")
                parameters = parameters if isinstance(parameters, dict) else {}
                await store.register_derived_external_request(
                    player_id,
                    follow_up["taskId"],
                    "organization_task",
                    {
                        "task_type": follow_up["taskType"],
                        "assignee_hero_id": follow_up["assigneeHeroId"],
                        "stage_id": follow_up["stageId"],
                        "stage_title": follow_up["stageTitle"],
                        "brief": "Automatic organization follow-up for " + task_key,
                        "parameters": {
                            "resource_units": 0,
                            "assignee_name": str(
                                parameters.get("assignee_name")
                                or follow_up["assigneeHeroId"]
                            ),
                        },
                        "derived_from_task_id": task_key,
                        "derivation_intent_id": follow_up["intentId"],
                        "derivation_source": follow_up["source"],
                        "derivation_rule_id": follow_up["ruleId"],
                    },
                )
        except (TypeError, ValueError, VersionConflict) as error:
            raise ApiError(
                "organization_task_derivation_invalid",
                "The organization follow-up lineage is invalid.",
                status_code=502,
            ) from error
        assignee = str(original.get("assignee_hero_id") or "")
        member_id = settings.orgflow_hero_members.get(assignee, "")
        if original.get("derived_from_task_id"):
            responsible_member_id = str(snapshot.get("responsible_member_id") or "")
            authoritative_assignee = next(
                (
                    hero_id
                    for hero_id, configured_member_id in settings.orgflow_hero_members.items()
                    if configured_member_id == responsible_member_id
                ),
                "",
            )
            if not authoritative_assignee:
                raise ApiError(
                    "organization_task_assignee_invalid",
                    "The organization follow-up has an unknown responsible member.",
                    status_code=502,
                )
            assignee = authoritative_assignee
            member_id = responsible_member_id
        try:
            settlement = _authoritative_settlement(
                snapshot,
                task_id=task_key,
                organization_id=settings.orgflow_org_id,
                member_id=member_id,
            )
        except ValueError as error:
            raise ApiError(
                "organization_settlement_invalid",
                "Organization settlement does not match the original order.",
                status_code=502,
            ) from error
        closure = (
            _closure_receipt(
                task_id=task_key, original=original, settlement=settlement
            )
            if settlement is not None
            else None
        )
        review = None
        if settlement is not None and closure is not None:
            pending_review = mandate_workflow.review_settlement(
                task_key, settlement, closure
            )
            review_id = uuid5(
                NAMESPACE_URL,
                "dongzhou-settlement-review:"
                f"{player_id}:{task_key}:{settlement['settlementId']}:{closure['digest']}",
            )
            record = await store.read_request(
                player_id, review_id, "organization_settlement_review"
            )
            recorded_response = record.get("response") if record else None
            review = (
                recorded_response
                if record
                and record.get("state") in {"ACCEPTED", "CENSURED"}
                and isinstance(recorded_response, dict)
                else pending_review
            )
        outcome = _npc_outcome_status(
            await store.game_event_status("npc-outcome:" + task_key),
            await store.game_event_status("npc-memory:" + task_key),
            quality=await store.game_event_status("npc-quality:" + task_key),
            motivation=await store.game_event_status("npc-motivation:" + task_key),
            require_quality=True,
            require_motivation=True,
        )
        if (
            isinstance(outcome, dict)
            and outcome.get("state") == "DELIVERED"
            and isinstance(settlement, dict)
        ):
            outcome["receipt"] = npc_settlement.seal_delivery(
                task_key,
                str(settlement.get("result") or ""),
                outcome,
            )
        task_state = {
            "taskId": task_key,
            "assigneeHeroId": assignee,
            "result": result,
            "settlement": settlement,
            "closureReceipt": closure,
            "npcOutcome": outcome,
            "review": review,
            "followUps": follow_ups,
        }
        consequence = review.get("npcConsequence") if isinstance(review, dict) else None
        if isinstance(consequence, dict):
            consequence_event = await store.game_event_status(str(consequence.get("eventId") or ""))
            consequence_memory = await store.game_event_status(str(consequence.get("memoryEventId") or ""))
            consequence_affection = await store.game_event_status(str(consequence.get("affectionEventId") or ""))
            consequence_status = _npc_outcome_status(
                consequence_event,
                consequence_memory,
                consequence_affection,
                require_affection=True,
            )
            task_state["npcConsequence"] = {
                **consequence,
                "state": consequence_status["state"] if consequence_status else "MISSING",
                "event": consequence_event,
                "memory": consequence_memory,
                "affection": consequence_affection,
            }
        if settlement is not None and closure is not None:
            await store.cache_external_request_result(
                player_id,
                task_key,
                "organization_task",
                "terminal",
                task_state,
            )
        return task_state

    @router.get("/organization/tasks/{task_id}")
    async def read_organization_task(task_id: UUID, player_id: UUID = Depends(player)) -> dict[str, Any]:
        return await _organization_task_state(str(task_id), player_id)

    @router.post("/organization/tasks/{task_id}/review")
    async def review_organization_task(
        task_id: UUID,
        request: OrganizationTaskReviewRequest,
        player_id: UUID = Depends(player),
    ) -> dict[str, Any]:
        task_key = str(task_id)
        task_state = await _organization_task_state(task_key, player_id)
        settlement = task_state.get("settlement")
        closure = task_state.get("closureReceipt")
        review = task_state.get("review")
        if not isinstance(settlement, dict) or not isinstance(closure, dict):
            raise ApiError(
                "organization_settlement_not_ready",
                "The organization task has no sealed terminal settlement to review.",
                status_code=409,
            )
        expected_review = mandate_workflow.review_settlement(task_key, settlement, closure)
        expected_action = expected_review["action"]
        if expected_action["actionId"] != str(request.action_id):
            raise ApiError(
                "organization_review_action_mismatch",
                "The player action does not match this organization report.",
                status_code=409,
            )
        if isinstance(review, dict) and review.get("state") in {"ACCEPTED", "CENSURED"}:
            recorded_decision = review.get("review", {}).get("decision")
            if recorded_decision != request.decision:
                raise ApiError(
                    "organization_review_conflict",
                    "This organization report was already reviewed with a different decision.",
                    status_code=409,
                )
            return {"replayed": True, **review}
        action = review.get("action") if isinstance(review, dict) else None
        if not isinstance(review, dict) or review.get("state") != "REQUIRES_ACTION" or not isinstance(action, dict):
            raise ApiError(
                "organization_review_not_resumable",
                "The organization report is not waiting for player action.",
                status_code=409,
            )
        review_id = uuid5(
            NAMESPACE_URL,
            "dongzhou-settlement-review:"
            f"{player_id}:{task_key}:{settlement['settlementId']}:{closure['digest']}",
        )
        payload = {
            "taskId": task_key,
            "settlementId": settlement["settlementId"],
            "closureDigest": closure["digest"],
            "actionId": str(request.action_id),
            "decision": request.decision,
        }
        try:
            should_process, previous = await store.begin_request(
                player_id, review_id, "organization_settlement_review", payload
            )
        except VersionConflict as error:
            raise ApiError(
                "organization_review_conflict",
                "This organization report was already reviewed with different input.",
                status_code=409,
            ) from error
        if not should_process:
            if isinstance(previous, dict) and previous.get("state") in {"ACCEPTED", "CENSURED"}:
                return {"replayed": True, **previous}
            raise ApiError(
                "organization_review_in_progress",
                "This organization report review is already in progress.",
                status_code=409,
            )
        result = mandate_workflow.resume_settlement_review(review, request.decision)
        consequence_events: list[dict[str, Any]] = []
        reward_units = settlement["organizationDelta"] if request.decision == "ACCEPT" else 0
        if reward_units > 0:
            resource_key = "task.execution"
            idempotency_key = f"dongzhou-settlement-reward:{settlement['settlementId']}"
            try:
                reward_response = await upstreams.adjust_organization_inventory(
                    settings.orgflow_org_id,
                    {
                        "resource_key": resource_key,
                        "delta_units": reward_units,
                        "reason_code": "TASK_SETTLEMENT_ACCEPTED",
                    },
                    idempotency_key=idempotency_key,
                )
                reward = _organization_inventory_reward_view(
                    reward_response.get("data") if isinstance(reward_response, dict) else None,
                    settings,
                    resource_key=resource_key,
                    delta_units=reward_units,
                )
            except UpstreamUnavailable as error:
                await store.finish_request(
                    player_id,
                    review_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE"},
                    error="organization_inventory_unavailable",
                    external_id=task_key,
                )
                raise ApiError(
                    "organization_inventory_unavailable",
                    "The organization reward ledger is temporarily unavailable.",
                    status_code=503,
                ) from error
            except (AttributeError, TypeError, ValueError) as error:
                await store.finish_request(
                    player_id,
                    review_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE"},
                    error="organization_inventory_contract_invalid",
                    external_id=task_key,
                )
                raise ApiError(
                    "organization_inventory_contract_invalid",
                    "The organization reward ledger returned an invalid receipt.",
                    status_code=502,
                ) from error
            result["inventoryReward"] = reward
        if request.decision == "CENSURE":
            original = await store.read_external_request(player_id, task_key, "organization_task")
            parameters = original.get("parameters") if isinstance(original, dict) else None
            parameters = parameters if isinstance(parameters, dict) else {}
            hero_id = str(task_state.get("assigneeHeroId") or "")
            npc_name = str(parameters.get("assignee_name") or hero_id or "属官")[:100]
            game_time = str((await store.read_game_clock())["virtualTime"])
            if not hero_id:
                await store.finish_request(
                    player_id,
                    review_id,
                    "RETRYABLE",
                    {"state": "RETRYABLE"},
                    error="organization_censure_contract_invalid",
                    external_id=task_key,
                )
                raise ApiError(
                    "organization_censure_contract_invalid",
                    "The organization report cannot identify its censured officer.",
                    status_code=502,
                )
            consequence_events = _npc_censure_events(
                settings,
                player_id,
                task_id=task_key,
                hero_id=hero_id,
                npc_name=npc_name,
                game_time=game_time,
                review_digest=str(result["review"]["digest"]),
            )
            result["npcConsequence"] = {
                "state": "QUEUED",
                "heroId": hero_id,
                "npcId": str(stable_npc_id(settings.ainpc_game_server_id, hero_id)),
                "targetId": str(stable_player_id(settings.ainpc_game_server_id, player_id)),
                "eventId": consequence_events[0]["eventId"],
                "memoryEventId": consequence_events[1]["eventId"],
                "affectionEventId": consequence_events[2]["eventId"],
                "affectionType": "annoyance",
                "affectionDelta": 5.8,
                "severity": 58,
            }
        await store.finish_request(
            player_id,
            review_id,
            result["state"],
            result,
            external_id=task_key,
            game_events=consequence_events,
        )
        return result

    application_settings = ApplicationSettings.model_validate({
        "service": {"name": "Dongzhou Integration Service", "version": "1.0.0"},
        # 检索、派差兼容调用可连续访问上游；入口预算须容纳上游等待及结果落库。
        "server": {"port": 8765, "max_request_body_bytes": 2 * 1024 * 1024, "request_timeout_seconds": settings.upstream_timeout_seconds * 4 + 15.0},
        "monitoring": {"metrics_prefix": "dongzhou_integration"},
        "cors": {"enabled": True, "allow_origins": [settings.public_origin], "allow_methods": ["GET", "POST", "PUT"], "allow_headers": ["Authorization", "Content-Type"]},
    })
    def health() -> dict[str, Any]:
        snapshot = kernel.health_status()
        services = service_statuses(module.services)
        snapshot["services"] = services
        if not module.services or not all(item.get("online") for item in services.values()):
            snapshot["status"] = "degraded"
        return snapshot

    app = create_app(settings=application_settings, kernel=kernel, routers=(game_clock_router, router), health_provider=health)

    app.state.dongzhou_settings = settings
    app.mount("/", StaticFiles(directory=settings.web_root, html=True), name="dongzhou-web")
    return app


app = build_application()
