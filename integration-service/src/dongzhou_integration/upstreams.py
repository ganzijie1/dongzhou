from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx

from .config import Settings
from .security import sign_orgflow_request


class UpstreamUnavailable(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, error_code: str | None = None, response_payload: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_payload = response_payload


class Upstreams:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(settings.upstream_timeout_seconds, connect=3),
            follow_redirects=False,
        )
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"} if token else {}

    async def _json(self, method: str, url: str, *, token: str = "", payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None, content: bytes | None = None) -> dict[str, Any]:
        try:
            request_headers = {**self._headers(token), **(headers or {})}
            response = await self.client.request(method, url, headers=request_headers, params=params, json=payload if content is None else None, content=content)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("upstream response is not an object")
            return data
        except httpx.HTTPStatusError as error:
            error_code = None
            response_payload = None
            try:
                decoded = error.response.json()
                if isinstance(decoded, dict):
                    response_payload = decoded
                    if isinstance(decoded.get("error"), dict):
                        error_code = decoded["error"].get("code")
            except ValueError:
                pass
            raise UpstreamUnavailable(
                f"{url}: {type(error).__name__}",
                status_code=error.response.status_code,
                error_code=error_code if isinstance(error_code, str) else None,
                response_payload=response_payload,
            ) from error
        except (httpx.HTTPError, ValueError) as error:
            raise UpstreamUnavailable(f"{url}: {type(error).__name__}") from error

    async def health(self) -> dict[str, dict[str, Any]]:
        probes = {
            "orgFlow": f"{self.settings.orgflow_url}/health/ready",
            "aiNpc": f"{self.settings.ainpc_url}/readiness",
            "knowledge": f"{self.settings.knowledge_url}/health",
        }
        async def probe(name: str, url: str) -> tuple[str, dict[str, Any]]:
            try:
                payload = await self._json("GET", url)
                if name == "aiNpc" and payload.get("ready") is not True:
                    raise UpstreamUnavailable("AINPC gateway readiness is false")
                return name, {"online": True}
            except UpstreamUnavailable as error:
                return name, {"online": False, "reason": str(error)}

        return dict(await asyncio.gather(*(probe(name, url) for name, url in probes.items())))

    async def send_game_event(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        if kind == "ORG_REPORT_START":
            snapshot = await self.get_virtual_task(
                self.settings.orgflow_org_id, str(payload["task_id"])
            )
            task = snapshot.get("data", snapshot)
            task_state = task.get("state") if isinstance(task, dict) else None
            terminal_states = {
                "SUCCEEDED", "PARTIALLY_COMPLETED", "FAILED", "REJECTED",
                "CANCELLED", "INVALIDATED",
            }
            if task_state in terminal_states:
                # 组织真值已终结，不再创建会被拒绝的复命对话。
                return {"state": "TASK_TERMINAL", "task": task}
            if task_state != "IN_PROGRESS":
                # AINPC 只接受执行中的任务复命。提前创建会把稳定操作永久置为 FAILED。
                raise UpstreamUnavailable(
                    "Organization task is not ready for a report.",
                    error_code="organization_report_not_ready",
                )
            report_payload = {
                key: value for key, value in payload.items() if key != "npc_outcome"
            }
            response = await self._json(
                "POST",
                self.settings.ainpc_url
                + "/internal/v1/organization-tasks/dialogues/report",
                token=self.settings.ainpc_task_token,
                payload=report_payload,
            )
            record = response.get("record")
            if not isinstance(record, dict) and isinstance(response.get("data"), dict):
                record = response["data"].get("record", response["data"])
            state = record.get("state") if isinstance(record, dict) else None
            task = record.get("task") if isinstance(record, dict) else None
            task_state = task.get("state") if isinstance(task, dict) else None
            management = record.get("management") if isinstance(record, dict) else None
            permanently_failed = (
                state == "FAILED"
                and isinstance(management, dict)
                and management.get("can_recover") is False
            )
            if state not in {"COMPLETED", "CLOSED"} and task_state not in {
                "SUCCEEDED",
                "PARTIALLY_COMPLETED",
                "FAILED",
                "REJECTED",
                "CANCELLED",
                "INVALIDATED",
            } and not permanently_failed:
                raise UpstreamUnavailable(
                    "AINPC report dialogue is still in progress.",
                    error_code="ainpc_report_dialogue_pending",
                    response_payload=response,
                )
            return response
        if kind == "NPC_TASK_OUTCOME":
            response = await self._json(
                "POST",
                self.settings.ainpc_url + "/callback/game-reports/emergency",
                token=self.settings.ainpc_token,
                payload=payload,
            )
            if response.get("code") not in (0, 200, "0", "200"):
                raise UpstreamUnavailable(
                    "AINPC rejected the organization outcome event.",
                    error_code="ainpc_outcome_rejected",
                    response_payload=response,
                )
            return response
        paths = {
            "CHAT_START": "/api/v1/social-interaction/chat",
            "CHAT_TURN": "/api/v1/social-interaction/chat",
            "DELIVERY_RESULT": "/callback/social-interaction/chat/delivery-result",
        }
        path = paths.get(kind)
        if path is None:
            raise ValueError("unsupported_game_event_kind")
        return await self._json(
            "POST",
            self.settings.ainpc_url + path,
            token=self.settings.ainpc_token,
            payload=payload,
        )

    async def search_knowledge(self, query: str, limit: int) -> tuple[str, list[dict[str, Any]]]:
        recall_limit = max(20, min(limit * 8, 100))
        payload = {
            "query": query,
            "channel_top_k": {"vector": recall_limit, "bm25": recall_limit, "entity": min(recall_limit, 20), "category": min(recall_limit, 20), "schedule_tag": min(recall_limit, 12), "graph": min(recall_limit, 20), "graph_max_depth": 2},
        }
        try:
            response = await self._json("POST", f"{self.settings.knowledge_url}/api/v1/player/search", token=self.settings.knowledge_token, payload=payload)
            channels = response.get("data", {}).get("channels", {})
            ids: list[str] = []
            for values in channels.values() if isinstance(channels, dict) else ():
                for item in values if isinstance(values, list) else ():
                    identifier = str(item.get("id") or item.get("aku_id") or "") if isinstance(item, dict) else ""
                    if identifier and identifier not in ids:
                        ids.append(identifier)
            if not ids:
                return "connected", []
            details = await self._json("POST", f"{self.settings.knowledge_url}/api/v1/aku/batch_get", token=self.settings.knowledge_token, payload={"ids": ids[:recall_limit]})
            raw = details.get("data", details)
            if isinstance(raw, dict):
                raw = raw.get("items", raw.get("akus", list(raw.values())))
            items = (
                [item for item in raw if self._is_dongzhou_knowledge(item)][:limit]
                if isinstance(raw, list)
                else []
            )
            if self.settings.knowledge_file.exists():
                catalog = json.loads(self.settings.knowledge_file.read_text(encoding="utf-8"))
                metadata = {str(entry["id"]): entry for entry in catalog.get("entries", [])}
                items = [
                    {
                        **item,
                        "stageId": metadata.get(str(item["id"]), {}).get("stageId", ""),
                        "sourceDetails": metadata.get(str(item["id"]), {}).get("sources", []),
                    }
                    for item in items
                ]
            return "connected", items
        except UpstreamUnavailable:
            if not self.settings.offline_knowledge_enabled:
                raise
            return "offline", self._local_search(query, limit, self.settings.knowledge_file)

    async def stage_knowledge(self, stage_id: str) -> list[dict[str, Any]]:
        # 本地目录只提供关卡到 AKU 的映射，正文始终从正式知识服务读取。
        catalog = json.loads(self.settings.knowledge_file.read_text(encoding="utf-8"))
        metadata = {
            str(entry["id"]): entry
            for entry in catalog.get("entries", [])
            if entry.get("stageId") == stage_id and self._is_dongzhou_knowledge(entry)
        }
        ids = list(metadata)
        if not ids:
            return []
        response = await self._json(
            "POST", f"{self.settings.knowledge_url}/api/v1/aku/batch_get",
            token=self.settings.knowledge_token, payload={"ids": ids},
        )
        data = response.get("data", response)
        items = data.get("items", []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            raise UpstreamUnavailable("Knowledge stage response has invalid items")
        return [
            {
                **item,
                "stageId": stage_id,
                "sourceDetails": metadata.get(str(item.get("id")), {}).get("sources", []),
            }
            for item in items
            if isinstance(item, dict) and item.get("id") in ids
        ]

    @staticmethod
    def _is_dongzhou_knowledge(item: Any) -> bool:
        if not isinstance(item, dict):
            return False
        identifier = str(item.get("id") or item.get("aku_id") or "")
        return identifier.startswith("dongzhou_stage_")

    @staticmethod
    def _local_search(query: str, limit: int, path: Path) -> list[dict[str, Any]]:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"entries": []}
        terms = [term.casefold() for term in query.split() if term]
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in data.get("entries", []):
            haystack = " ".join(str(entry.get(key, "")) for key in ("name", "summary", "content", "keywords")).casefold()
            score = sum(haystack.count(term) for term in terms)
            if score or not terms:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], int(item[1].get("index", 9999))))
        return [item[1] for item in scored[:limit]]

    async def register_npcs(self, npcs: list[dict[str, str]]) -> dict[str, Any]:
        payload = {"npc_data_list": [{"npc_id": npc["npcId"], "status": "active"} for npc in npcs]}
        return await self._json("POST", f"{self.settings.ainpc_url}/ai/npc/register/batch", token=self.settings.ainpc_token, payload=payload)

    async def set_npcs_online(
        self, npcs: list[dict[str, str]], game_time: str, login_round: str
    ) -> list[dict[str, Any]]:
        semaphore = asyncio.Semaphore(8)

        async def activate(npc: dict[str, str]) -> dict[str, Any]:
            async with semaphore:
                receipt = await self._json(
                    "POST",
                    f"{self.settings.ainpc_url}/callback/npc-lifecycle/online_state",
                    token=self.settings.ainpc_token,
                    payload={
                        "npcId": npc["npcId"],
                        "npcName": npc["name"],
                        "gameTime": game_time,
                        "gameServerId": str(self.settings.ainpc_game_server_id),
                        "state": 1,
                        "loginRequestId": f"{login_round}-{npc['npcId']}",
                    },
                )
                if receipt.get("code") not in (0, 200, "0", "200"):
                    raise UpstreamUnavailable("AINPC rejected the NPC online callback")
                return {"npcId": npc["npcId"], "receipt": receipt}

        return list(await asyncio.gather(*(activate(npc) for npc in npcs)))

    async def request_npc_relogin(self, npc_id: int, request_id: str) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"{self.settings.ainpc_url}/api/v1/npc-lifecycle/relogin",
            token=self.settings.ainpc_token,
            payload={"game_server_id": str(self.settings.ainpc_game_server_id), "npc_id": str(npc_id), "request_id": request_id},
        )

    async def request_npc_relogins(self, npcs: list[tuple[int, str]]) -> list[dict[str, Any]]:
        semaphore = asyncio.Semaphore(8)

        async def relogin(npc_id: int, request_id: str) -> dict[str, Any]:
            async with semaphore:
                receipt = await self.request_npc_relogin(npc_id, request_id)
                return {"npcId": str(npc_id), "receipt": receipt}

        return list(await asyncio.gather(*(relogin(npc_id, request_id) for npc_id, request_id in npcs)))

    async def online_npc_ids(self) -> set[str]:
        page = 1
        page_size = 100
        online_ids: set[str] = set()
        observed = 0
        while True:
            response = await self._json(
                "GET",
                f"{self.settings.ainpc_url}/admin/npc-lifecycle/online-npcs",
                token=self.settings.ainpc_token,
                params={
                    "game_server_id": str(self.settings.ainpc_game_server_id),
                    "page": page,
                    "page_size": page_size,
                },
            )
            data = response.get("data")
            if not isinstance(data, dict) or data.get("complete") is not True:
                raise UpstreamUnavailable("AINPC online actor snapshot is incomplete")
            items = data.get("items")
            total = data.get("total")
            if not isinstance(items, list) or not isinstance(total, int) or total < 0:
                raise UpstreamUnavailable("AINPC online actor snapshot is invalid")
            observed += len(items)
            online_ids.update(
                str(item["npc_id"])
                for item in items
                if isinstance(item, dict)
                and item.get("online") is True
                and item.get("npc_id") is not None
            )
            if observed >= total:
                return online_ids
            if not items:
                raise UpstreamUnavailable("AINPC online actor snapshot pagination is incomplete")
            page += 1

    async def npc_state(self, npc_id: int) -> dict[str, Any]:
        base = self.settings.ainpc_url
        server = self.settings.ainpc_game_server_id
        emotion, affection, relationships = await asyncio.gather(
            self._json("GET", f"{base}/api/v1/emotion/current/{server}/{npc_id}", token=self.settings.ainpc_token),
            self._json("GET", f"{base}/api/v1/affection/targets/{server}/{npc_id}", token=self.settings.ainpc_token),
            self._json("GET", f"{base}/api/v1/relationship/all/{server}/{npc_id}", token=self.settings.ainpc_token),
        )
        return {"emotion": emotion, "affection": affection, "relationships": relationships}

    async def npc_schedule(self, npc_id: int) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"{self.settings.ainpc_url}/api/v1/schedule-planning/current",
            token=self.settings.ainpc_token,
            payload={"game_server_id": str(self.settings.ainpc_game_server_id), "npc_id": str(npc_id)},
        )

    async def generate_npc_schedule(self, npc_id: int, force_regenerate: bool) -> dict[str, Any]:
        return await self._json(
            "POST",
            f"{self.settings.ainpc_url}/api/v1/schedule-planning/long-term/generate",
            token=self.settings.ainpc_token,
            payload={"game_server_id": str(self.settings.ainpc_game_server_id), "npc_id": str(npc_id), "force_regenerate": force_regenerate},
        )

    async def choose_dialogue(self, npc_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self._json(
            "POST",
            f"{self.settings.ainpc_url}/callback/npc-dialogue/choice",
            token=self.settings.ainpc_token,
            payload={"game_server_id": str(self.settings.ainpc_game_server_id), "npc_id": str(npc_id), **payload},
        )
        # AINPC 的旧版合同以 HTTP 200 包装业务失败，不能据 HTTP 状态记为军议完成。
        decision = response.get("data")
        if response.get("code") != 200 or not isinstance(decision, dict):
            raise UpstreamUnavailable(
                "AINPC did not complete the decision.",
                error_code="ainpc_decision_failed",
            )
        options = [
            option
            for dialogue in payload.get("dialogues", [])
            for option in dialogue.get("options", [])
        ]
        if (
            isinstance(decision.get("index"), bool)
            or not isinstance(decision.get("index"), int)
            or not any(
                option.get("index") == decision["index"]
                and option.get("type") == decision.get("type")
                for option in options
            )
        ):
            raise UpstreamUnavailable(
                "AINPC returned an invalid decision option.",
                error_code="ainpc_decision_invalid",
            )
        return response

    async def trigger_virtual_task(self, organization_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = f"/internal/v1/organization-administration/organizations/{organization_id}/virtual-task-triggers"

        async def submit(candidate: dict[str, Any]) -> dict[str, Any]:
            body = json.dumps(candidate, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
            return await self._json(
                "POST",
                f"{self.settings.orgflow_url}{path}",
                headers=sign_orgflow_request(method="POST", path_and_query=path, audience=self.settings.orgflow_audience, key_id=self.settings.orgflow_hmac_key_id, secret=self.settings.orgflow_hmac_secret, body=body),
                content=body,
            )

        try:
            return await submit(payload)
        except UpstreamUnavailable as error:
            if error.error_code != "organization_virtual_task_parameters_invalid":
                raise
            parameters = payload.get("parameters")
            if not isinstance(parameters, dict):
                raise
            compatible = dict(payload)
            compatible["parameters"] = {
                "assignee_hero_id": "unassigned",
                "assignee_name": "Unassigned",
                "resource_units": 0,
                "stage_id": "unknown",
                "stage_title": "Unknown stage",
            }
            context = json.dumps(parameters, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            compatible["brief"] = f"{str(payload.get('brief') or '').strip()} [Dongzhou context: {context}]".strip()
            return await submit(compatible)

    async def get_virtual_task(self, organization_id: str, task_id: str) -> dict[str, Any]:
        path = f"/internal/v1/organization-administration/organizations/{organization_id}/virtual-tasks/{task_id}"
        return await self._json(
            "GET",
            f"{self.settings.orgflow_url}{path}",
            headers=sign_orgflow_request(method="GET", path_and_query=path, audience=self.settings.orgflow_audience, key_id=self.settings.orgflow_hmac_key_id, secret=self.settings.orgflow_hmac_secret, body=b""),
            content=b"",
        )
