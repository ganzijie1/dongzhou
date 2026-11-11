from __future__ import annotations

import asyncio
import json
import math
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
        if kind == "NPC_TASK_MEMORY":
            response = await self._json(
                "POST",
                self.settings.ainpc_url + "/callback/game-reports/system-message",
                token=self.settings.ainpc_token,
                payload=payload,
            )
            if response.get("code") not in (0, 200, "0", "200"):
                raise UpstreamUnavailable(
                    "AINPC rejected the organization outcome memory.",
                    error_code="ainpc_outcome_memory_rejected",
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
            channel_weights = {
                "vector": 0.30,
                "bm25": 0.25,
                "entity": 0.15,
                "graph": 0.15,
                "category": 0.10,
                "schedule_tag": 0.05,
            }
            provenance: dict[str, list[dict[str, Any]]] = {}
            aggregates: dict[str, float] = {}
            for channel, weight in channel_weights.items():
                values = channels.get(channel, []) if isinstance(channels, dict) else []
                for rank, item in enumerate(values if isinstance(values, list) else (), start=1):
                    identifier = str(item.get("id") or item.get("aku_id") or "") if isinstance(item, dict) else ""
                    if not identifier:
                        continue
                    raw_score = item.get("score", 0)
                    raw_normalized = item.get("normalized_score", item.get("normalizedScore", 0))
                    score = float(raw_score) if isinstance(raw_score, (int, float)) and not isinstance(raw_score, bool) and math.isfinite(float(raw_score)) else 0.0
                    normalized = float(raw_normalized) if isinstance(raw_normalized, (int, float)) and not isinstance(raw_normalized, bool) and math.isfinite(float(raw_normalized)) else 0.0
                    normalized = max(0.0, min(1.0, normalized))
                    provenance.setdefault(identifier, []).append({
                        "channel": channel,
                        "score": round(score, 6),
                        "normalizedScore": round(normalized, 6),
                        "rank": rank,
                    })
                    aggregates[identifier] = aggregates.get(identifier, 0.0) + normalized * weight
            ids = sorted(provenance, key=lambda identifier: (-aggregates.get(identifier, 0.0), identifier))
            if not ids:
                return "connected", []
            details = await self._json("POST", f"{self.settings.knowledge_url}/api/v1/aku/batch_get", token=self.settings.knowledge_token, payload={"ids": ids[:recall_limit]})
            raw = details.get("data", details)
            if isinstance(raw, dict):
                raw = raw.get("items", raw.get("akus", list(raw.values())))
            hydrated = {
                str(item.get("id") or item.get("aku_id") or ""): item
                for item in raw
                if isinstance(item, dict) and self._is_dongzhou_knowledge(item)
            } if isinstance(raw, list) else {}
            items = [hydrated[identifier] for identifier in ids if identifier in hydrated][:limit]
            if self.settings.knowledge_file.exists():
                catalog = json.loads(self.settings.knowledge_file.read_text(encoding="utf-8"))
                metadata = {str(entry["id"]): entry for entry in catalog.get("entries", [])}
                items = [
                    {
                        **item,
                        "stageId": metadata.get(str(item["id"]), {}).get("stageId", ""),
                        "sourceDetails": metadata.get(str(item["id"]), {}).get("sources", []),
                        "retrieval": {
                            "aggregateScore": round(aggregates.get(str(item["id"]), 0.0), 6),
                            "strongestChannel": max(
                                provenance.get(str(item["id"]), []),
                                key=lambda value: (value["normalizedScore"], channel_weights[value["channel"]]),
                                default={"channel": ""},
                            )["channel"],
                            "graphRelated": any(value["channel"] == "graph" for value in provenance.get(str(item["id"]), [])),
                            "channels": provenance.get(str(item["id"]), []),
                        },
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

    async def campaign_route(
        self, from_map_id: int, to_map_id: int
    ) -> dict[str, Any]:
        response = await self._json(
            "POST",
            f"{self.settings.knowledge_url}/api/v1/map-transition/query",
            token=self.settings.knowledge_token,
            payload={
                "from_doc_id": str(from_map_id),
                "to_doc_id": str(to_map_id),
                "max_depth": 1,
                "methods": ["campaign_progression"],
            },
        )
        data = response.get("data", response)
        if not isinstance(data, dict):
            raise UpstreamUnavailable("Knowledge campaign route response is invalid")
        return data

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

    async def sync_player_ai_interaction(
        self, player_id: int, enabled: bool
    ) -> dict[str, Any]:
        response = await self._json(
            "POST",
            f"{self.settings.ainpc_url}/ai/npc/player-ai-interaction/sync",
            token=self.settings.ainpc_token,
            payload={
                "game_server_id": str(self.settings.ainpc_game_server_id),
                "player_id": str(player_id),
                "enabled": enabled,
                "source": "dongzhou-player-settings",
            },
        )
        data = response.get("data")
        if (
            response.get("code") not in (0, 200, "0", "200")
            or not isinstance(data, dict)
            or str(data.get("gameServerId") or "")
            != str(self.settings.ainpc_game_server_id)
            or str(data.get("playerId") or "") != str(player_id)
            or not isinstance(data.get("enabled"), bool)
            or not str(data.get("updatedAt") or "").strip()
        ):
            raise UpstreamUnavailable(
                "AINPC returned an invalid player interaction preference"
            )
        return {
            "enabled": data["enabled"],
            "source": str(data.get("source") or ""),
            "updatedAt": str(data["updatedAt"]),
        }

    async def ensure_organization_supervision(
        self, *, subordinate_npc_id: str, manager_npc_id: str | None, source_event_id: str,
    ) -> dict[str, Any]:
        response = await self._json(
            "POST",
            f"{self.settings.ainpc_url}/api/v1/relationship/ensure-organization-supervision",
            token=self.settings.ainpc_token,
            payload={
                "game_server_id": str(self.settings.ainpc_game_server_id),
                "npc_id": subordinate_npc_id,
                "manager_npc_id": manager_npc_id,
                "source_event_id": source_event_id,
            },
        )
        if response.get("code") not in (0, 200, "0", "200") or not isinstance(response.get("created"), bool):
            raise UpstreamUnavailable("AINPC returned an invalid organization relationship receipt")
        relationship_ids = response.get("relationshipIds")
        if not isinstance(relationship_ids, list) or not all(isinstance(value, str) and value for value in relationship_ids):
            raise UpstreamUnavailable("AINPC returned an incomplete organization relationship receipt")
        return response

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
        attempts = 3
        for attempt in range(attempts):
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
                    break
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
                    break
                page += 1
            if attempt + 1 < attempts:
                await asyncio.sleep(0.1 * (attempt + 1))
        raise UpstreamUnavailable("AINPC online actor snapshot is incomplete")

    async def npc_state(self, npc_id: int) -> dict[str, Any]:
        base = self.settings.ainpc_url
        server = self.settings.ainpc_game_server_id
        emotion, affection, relationships, personality, motivation = await asyncio.gather(
            self._json("GET", f"{base}/api/v1/emotion/current/{server}/{npc_id}", token=self.settings.ainpc_token),
            self._json("GET", f"{base}/api/v1/affection/targets/{server}/{npc_id}", token=self.settings.ainpc_token),
            self._json("GET", f"{base}/api/v1/relationship/all/{server}/{npc_id}", token=self.settings.ainpc_token),
            self.optional_npc_personality(npc_id),
            self.optional_npc_motivation(npc_id),
        )
        return {
            "emotion": emotion,
            "affection": affection,
            "relationships": relationships,
            "personality": personality,
            "motivation": motivation,
        }

    async def optional_npc_motivation(self, npc_id: int) -> dict[str, Any]:
        try:
            return await self.npc_motivation(npc_id)
        except UpstreamUnavailable:
            return {"available": False}

    async def npc_motivation(self, npc_id: int) -> dict[str, Any]:
        server = str(self.settings.ainpc_game_server_id)
        response = await self._json(
            "GET",
            f"{self.settings.ainpc_url}/api/v1/motivation/snapshot/{server}/{npc_id}",
            token=self.settings.ainpc_token,
        )
        threshold = response.get("threshold")
        valid_threshold = (
            not isinstance(threshold, bool)
            and isinstance(threshold, (int, float))
            and math.isfinite(float(threshold))
            and float(threshold) > 0
        )
        if response.get("code") not in (0, 200, "0", "200") or not valid_threshold:
            raise UpstreamUnavailable(
                "AINPC returned an invalid motivation snapshot.",
                error_code="ainpc_motivation_invalid",
                response_payload=response,
            )
        item = response.get("item")
        if item is None:
            return {"available": False, "threshold": round(float(threshold), 1)}
        motives = item.get("motives") if isinstance(item, dict) else None
        revision = item.get("revision") if isinstance(item, dict) else None
        valid_motives = (
            isinstance(motives, list)
            and len(motives) <= 32
            and all(
                isinstance(motive, dict)
                and isinstance(motive.get("name"), str)
                and 0 < len(motive["name"].strip()) <= 100
                and not isinstance(motive.get("score"), bool)
                and isinstance(motive.get("score"), (int, float))
                and math.isfinite(float(motive["score"]))
                for motive in motives
            )
            and len({motive["name"].strip() for motive in motives}) == len(motives)
        )
        if (
            not isinstance(item, dict)
            or str(item.get("game_server_id") or "") != server
            or str(item.get("npc_id") or "") != str(npc_id)
            or not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision < 0
            or not str(item.get("updated_at") or "").strip()
            or not valid_motives
        ):
            raise UpstreamUnavailable(
                "AINPC returned an invalid motivation snapshot.",
                error_code="ainpc_motivation_invalid",
                response_payload=response,
            )
        return {
            "available": True,
            "motives": [
                {"name": motive["name"].strip(), "score": round(float(motive["score"]), 1)}
                for motive in motives
            ],
            "revision": revision,
            "updatedAt": str(item["updated_at"]),
            "threshold": round(float(threshold), 1),
        }

    async def optional_npc_personality(self, npc_id: int) -> dict[str, Any]:
        try:
            return await self.npc_personality(npc_id)
        except UpstreamUnavailable:
            return {"available": False}

    async def npc_personality(self, npc_id: int) -> dict[str, Any]:
        server = str(self.settings.ainpc_game_server_id)
        response = await self._json(
            "GET",
            f"{self.settings.ainpc_url}/api/v1/personality/profile/{server}/{npc_id}",
            token=self.settings.ainpc_token,
            params={"auto_initialize": "false"},
        )
        if response.get("code") not in (0, 200, "0", "200"):
            raise UpstreamUnavailable(
                "AINPC returned an invalid personality profile.",
                error_code="ainpc_personality_invalid",
                response_payload=response,
            )
        item = response.get("item")
        if item is None:
            return {"available": False}
        traits = item.get("traits") if isinstance(item, dict) else None
        dominant = item.get("dominant_traits") if isinstance(item, dict) else None
        valid_traits = (
            isinstance(traits, dict)
            and all(
                isinstance(key, str)
                and key
                and not isinstance(value, bool)
                and isinstance(value, (int, float))
                and math.isfinite(float(value))
                and 0 <= float(value) <= 100
                for key, value in traits.items()
            )
        )
        valid_dominant = (
            isinstance(dominant, list)
            and len(dominant) <= 8
            and all(isinstance(value, str) and value in traits for value in dominant)
        ) if valid_traits else False
        if (
            not isinstance(item, dict)
            or str(item.get("game_server_id") or "") != server
            or str(item.get("npc_id") or "") != str(npc_id)
            or not str(item.get("profile_id") or "").strip()
            or not valid_traits
            or not valid_dominant
            or response.get("auto_initialized") is not False
        ):
            raise UpstreamUnavailable(
                "AINPC returned an invalid personality profile.",
                error_code="ainpc_personality_invalid",
                response_payload=response,
            )
        return {
            "available": True,
            "profileId": str(item["profile_id"]),
            "traits": {key: round(float(value), 1) for key, value in traits.items()},
            "dominantTraits": list(dominant),
            "templateSource": str(item.get("template_source") or ""),
            "backgroundNote": str(item.get("background_note") or ""),
            "updatedAt": str(item.get("updated_at") or ""),
        }

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

    async def evaluate_emergency(
        self, npc_id: int, timestamp: str, description: str
    ) -> dict[str, Any]:
        response = await self._json(
            "POST",
            f"{self.settings.ainpc_url}/callback/emergency-assessment/evaluate",
            token=self.settings.ainpc_token,
            payload={
                "npc_id": str(npc_id),
                "game_server_id": str(self.settings.ainpc_game_server_id),
                "EmergencyEvents": [
                    {"timestamp": timestamp, "description": description}
                ],
            },
        )
        data = response.get("data")
        results = data.get("results") if isinstance(data, dict) else None
        scores = data.get("scores") if isinstance(data, dict) else None
        trace_ids = data.get("interrupt_trace_ids") if isinstance(data, dict) else None
        if (
            response.get("code") not in (0, 200, "0", "200")
            or not isinstance(results, list)
            or len(results) != 1
            or not isinstance(results[0], bool)
            or not isinstance(scores, list)
            or len(scores) != 1
            or isinstance(scores[0], bool)
            or not isinstance(scores[0], (int, float))
            or not math.isfinite(float(scores[0]))
            or float(scores[0]) < 0
            or not isinstance(trace_ids, list)
            or len(trace_ids) != 1
            or not isinstance(trace_ids[0], str)
            or (results[0] and not trace_ids[0])
        ):
            raise UpstreamUnavailable(
                "AINPC returned an invalid emergency assessment.",
                error_code="ainpc_emergency_assessment_invalid",
                response_payload=response,
            )
        return {
            "urgent": results[0],
            "score": round(float(scores[0]), 6),
            "interruptTraceId": trace_ids[0] or None,
        }

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

    async def organization_roster(self, organization_id: str) -> dict[str, Any]:
        path = f"/internal/v1/organization-administration/organizations/{organization_id}/roster"
        return await self._json(
            "GET",
            f"{self.settings.orgflow_url}{path}",
            headers=sign_orgflow_request(method="GET", path_and_query=path, audience=self.settings.orgflow_audience, key_id=self.settings.orgflow_hmac_key_id, secret=self.settings.orgflow_hmac_secret, body=b""),
            content=b"",
        )

    async def organization_inventory(self, organization_id: str) -> dict[str, Any]:
        path = f"/internal/v1/organization-administration/organizations/{organization_id}/inventory"
        return await self._json(
            "GET",
            f"{self.settings.orgflow_url}{path}",
            headers=sign_orgflow_request(method="GET", path_and_query=path, audience=self.settings.orgflow_audience, key_id=self.settings.orgflow_hmac_key_id, secret=self.settings.orgflow_hmac_secret, body=b""),
            content=b"",
        )

    async def adjust_organization_inventory(
        self,
        organization_id: str,
        payload: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        path = f"/internal/v1/organization-administration/organizations/{organization_id}/inventory-adjustments"
        body = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        headers = sign_orgflow_request(
            method="POST",
            path_and_query=path,
            audience=self.settings.orgflow_audience,
            key_id=self.settings.orgflow_hmac_key_id,
            secret=self.settings.orgflow_hmac_secret,
            body=body,
        )
        headers["Idempotency-Key"] = idempotency_key
        return await self._json(
            "POST",
            f"{self.settings.orgflow_url}{path}",
            headers=headers,
            content=body,
        )
