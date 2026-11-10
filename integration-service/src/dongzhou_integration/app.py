from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import hashlib
from importlib.metadata import version
import json
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
from .models import AinpcAliveQuery, AinpcAllLoginRequest, AinpcChatStartRequest, AinpcLoginReadyRequest, AinpcNearbyQuery, AinpcNpcDirectoryQuery, AinpcPrivateChatRuntimeQuery, AinpcPrivateChatRuntimeResetRequest, AinpcPrivateMessageDeliveryQuery, AinpcPrivateMessageRequest, AinpcSingleLoginRequest, AinpcTaskStatusQuery, CampaignRouteRequest, CourtMandateRequest, CourtMandateResumeRequest, GameClockQuery, GuestSessionRequest, KnowledgeSearchRequest, NpcDecisionRequest, NpcScheduleGenerateRequest, NpcSyncRequest, OrganizationTaskRequest, SaveWriteRequest
from .security import InvalidSession, issue_session, stable_event_id, stable_npc_id, verify_session
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
        if not pending:
            return
        if missing:
            await self.upstreams.register_npcs(missing)
        clock = await self.store.read_game_clock()
        await self.upstreams.set_npcs_online(
            pending,
            str(clock["virtualTime"]),
            login_round,
        )


class MandateWorkflowModule(Module):
    name = "dongzhou_mandate_workflow"
    version = "1.0.0"
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


def _payload(value: BaseModel) -> dict[str, Any]:
    return value.model_dump(mode="json")


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
    knowledge_fit = 6 if task.get("knowledgeId") else 0
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
    return max(
        25.0,
        min(
            95.0,
            _ORGANIZATION_TASK_BASE_CHANCE.get(task_type, 60)
            + office_fit
            + knowledge_fit
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
        if not isinstance(task, dict) or task.get("status") != "active":
            continue
        task_id = str(task.get("remoteResult") or "")
        due_month = task.get("dueMonth")
        try:
            UUID(task_id)
        except ValueError:
            continue
        if isinstance(due_month, bool) or not isinstance(due_month, int) or due_month > month:
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
        success = _organization_task_succeeds(
            task, task_type, members_by_id.get(assignee, {}), mandate
        )
        task_name = str(task.get("name") or task_type or "organization assignment")
        stage_title = str(original.get("stage_title") or "the assigned stage")
        content = (
            f"The {task_name} assignment for {stage_title} was completed successfully. "
            "Report completion truthfully to the direct manager."
            if success
            else f"The {task_name} assignment for {stage_title} could not be completed. "
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
                "planned_result": "SUCCESS" if success else "FAILURE",
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
    kernel = Kernel(
        [
            LoadedModule(module=module, required=True, original_index=0),
            LoadedModule(module=mandate_workflow, required=True, original_index=1),
        ]
    )
    router = APIRouter(prefix="/api/dongzhou/v1")
    game_clock_router = APIRouter()

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
        return {
            **external,
            "nexusKernel": {
                "online": runtime_state in {"ready", "degraded"}
                and workflow_state in {"ready", "degraded"},
                "mode": "embedded",
                "version": _NEXUS_KERNEL_VERSION,
                "runtimeState": runtime_state,
                "workflowModule": MandateWorkflowModule.name,
                "workflowState": workflow_state,
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
        # Dongzhou persists messages synchronously and has no game-side send queue
        # or waiting-reply record to cancel. The targeted reset is therefore an
        # idempotent no-op, followed by a fresh authoritative runtime snapshot.
        state = await store.private_chat_runtime_state(
            settings.game_server_id, request.ai_id
        )
        return {
            "success": True,
            "message": "runtime state already clear",
            "endedWaitingReplyCount": 0,
            "clearedPendingMessageCount": 0,
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
            reports = await _prepare_due_organization_reports(
                store, settings, player_id, request.payload
            )
            return await store.write_save(
                player_id, request.expected_version, request.payload, organization_reports=reports
            )
        except VersionConflict as error:
            raise ApiError("save_version_conflict", "The save has changed; reload before writing.", status_code=409) from error
        except GameClockConflict as error:
            raise ApiError(str(error), "Organization month must advance exactly one step at a time.", status_code=409) from error

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
        try:
            result = await upstreams.campaign_route(from_map_id, to_map_id)
        except UpstreamUnavailable as error:
            raise ApiError(
                "knowledge_route_unavailable",
                "Campaign route verification is temporarily unavailable.",
                status_code=503,
            ) from error
        route = None
        for plan in result.get("plans", []):
            if not isinstance(plan, dict):
                continue
            for step in plan.get("steps", []):
                if not isinstance(step, dict):
                    continue
                for candidate in step.get("routes", []):
                    if isinstance(candidate, dict) and candidate.get("method") == "campaign_progression":
                        route = candidate
                        break
                if route is not None:
                    break
            if route is not None:
                break
        if route is None:
            for candidate in result.get("routes", []):
                if isinstance(candidate, dict) and candidate.get("method") == "campaign_progression":
                    route = candidate
                    break
        if result.get("found") is not True or route is None:
            raise ApiError(
                "campaign_route_not_found",
                "No published campaign route joins these stages.",
                status_code=404,
            )
        detail = route.get("detail")
        expected = {
            "from_stage_id": request.from_stage_id,
            "to_stage_id": request.to_stage_id,
            "requires_completed_stage_id": request.from_stage_id,
        }
        if not isinstance(detail, dict) or any(detail.get(key) != value for key, value in expected.items()):
            raise ApiError(
                "campaign_route_invalid",
                "The published campaign route does not match these stages.",
                status_code=502,
            )
        provision_cost = detail.get("provision_cost")
        if isinstance(provision_cost, bool) or not isinstance(provision_cost, int) or not 0 <= provision_cost <= 20:
            raise ApiError(
                "campaign_route_invalid",
                "The published campaign route has an invalid provision cost.",
                status_code=502,
            )
        return {
            "mode": "connected",
            "found": True,
            "fromStageId": request.from_stage_id,
            "toStageId": request.to_stage_id,
            "fromMapId": from_map_id,
            "toMapId": to_map_id,
            "routeId": route.get("route_id"),
            "provisionCost": provision_cost,
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
        ready = not pending
        return {"playerId": str(player_id), "gameServerId": str(settings.ainpc_game_server_id), "npcs": mapped, "registration": result, "activation": activation, "ready": ready, "state": "READY" if ready else "INITIALIZING"}

    @router.get("/npcs/{hero_id}/state")
    async def read_npc_state(hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        try:
            state = await upstreams.npc_state(npc_id)
        except UpstreamUnavailable as error:
            raise ApiError("ainpc_unavailable", "NPC state is temporarily unavailable.", status_code=503) from error
        runtime = await store.read_npc_runtime(settings.game_server_id, str(npc_id))
        return {"playerId": str(player_id), "heroId": hero_id, "npcId": str(npc_id), "runtime": runtime or {"state": "INITIALIZING"}, **state}

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
            npc_state, schedule = await asyncio.gather(
                upstreams.npc_state(npc_id),
                upstreams.npc_schedule(npc_id),
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

    @router.post("/npcs/{hero_id}/decisions")
    async def decide_with_npc(request: NpcDecisionRequest, hero_id: str, player_id: UUID = Depends(player)) -> dict[str, Any]:
        npc_id = stable_npc_id(settings.ainpc_game_server_id, hero_id)
        body = _payload(request)
        try:
            created, previous = await store.begin_request(player_id, request.client_request_id, "npc_decision", {"hero_id": hero_id, **body})
        except VersionConflict as error:
            raise ApiError("idempotency_conflict", "The request identifier was already used with different input.", status_code=409) from error
        if not created:
            if previous and previous.get("state") == "PENDING":
                raise ApiError("request_in_progress", "The same NPC decision is still being processed.", status_code=409)
            return {"replayed": True, **(previous or {})}
        dialogue = {
            "dialogues": [{
                "question": request.question,
                "options": [{"index": option.index, "type": "OPTION", "text": option.text} for option in request.options],
                "text_max_length": 0,
            }],
            "metadata": {"source": "dongzhou", "topic": request.topic, "player_id": str(player_id), "request_id": str(request.client_request_id)},
        }
        try:
            result = await upstreams.choose_dialogue(npc_id, dialogue)
        except UpstreamUnavailable as error:
            response = {"state": "RETRYABLE", "requestId": str(request.client_request_id)}
            await store.finish_request(player_id, request.client_request_id, "RETRYABLE", response, str(error))
            raise ApiError("ainpc_dialogue_unavailable", "NPC decision is retained for retry.", status_code=503) from error
        response = {"state": "COMPLETED", "requestId": str(request.client_request_id), "decision": result}
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
        trace = {
            "id": mandate_id,
            "stageId": request.stage_id,
            "stageTitle": request.stage_title,
            "heroId": request.hero_id,
            "taskType": request.task_type,
            "evidence": evidence_trace,
            "council": {
                "requestId": str(request.council_request_id),
                "question": str(council_request.get("question") or ""),
                "index": request.decision_index,
                "text": str(selected_option.get("text") or ""),
            },
            "assignment": assignment,
            "kernel": {
                "module": MandateWorkflowModule.name,
                "moduleVersion": MandateWorkflowModule.version,
                "nexusKernelVersion": _NEXUS_KERNEL_VERSION,
                "state": str(workflow_status["state"]).upper(),
            },
        }
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
            duty_note = (
                f" Bound AINPC duty {assignment.get('eventId')} "
                f"({assignment.get('name')}) on {assignment.get('date')} from plan "
                f"{assignment.get('planId')}.{readiness_note}"
            )
            brief = brief.rstrip()[: max(0, 1000 - len(duty_note))] + duty_note
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
            "expected_hierarchy_version": settings.orgflow_hierarchy_version,
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

    @router.get("/organization/tasks/{task_id}")
    async def read_organization_task(task_id: UUID, player_id: UUID = Depends(player)) -> dict[str, Any]:
        task_key = str(task_id)
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
        assignee = str(original.get("assignee_hero_id") or "")
        member_id = settings.orgflow_hero_members.get(assignee, "")
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
        outcome = await store.game_event_status("npc-outcome:" + task_key)
        return {
            "taskId": task_key,
            "result": result,
            "settlement": settlement,
            "closureReceipt": closure,
            "npcOutcome": outcome,
        }

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
