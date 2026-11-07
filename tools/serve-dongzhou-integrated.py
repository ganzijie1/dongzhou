#!/usr/bin/env python3
"""Serve Dongzhou H5 and proxy optional organization, NPC, and knowledge services."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web-game"
KNOWLEDGE_FILE = WEB_ROOT / "scenario" / "dongzhou-knowledge.json"


def env_url(name: str, default: str) -> str:
    return os.getenv(name, default).rstrip("/")


class Services:
    def __init__(self) -> None:
        self.org = env_url("DONGZHOU_ORGFLOW_URL", "http://127.0.0.1:8030")
        self.ainpc = env_url("DONGZHOU_AINPC_URL", "http://127.0.0.1:8000")
        self.knowledge = env_url("DONGZHOU_KNOWLEDGE_URL", "http://127.0.0.1:8080")
        self.token = os.getenv("DONGZHOU_ORGFLOW_TOKEN", "")
        self.actor = os.getenv("DONGZHOU_ORGFLOW_ACTOR", "dongzhou-game")
        self.org_id = os.getenv("DONGZHOU_ORGFLOW_ORG_ID", "").strip()

    @staticmethod
    def request(url: str, method: str = "GET", payload: dict | None = None, headers: dict | None = None, timeout: float = 2.5) -> dict:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        request_headers = {"Accept": "application/json", **(headers or {})}
        if body is not None:
            request_headers["Content-Type"] = "application/json; charset=utf-8"
        request = Request(url, data=body, method=method, headers=request_headers)
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def org_headers(self, idempotency: bool = False) -> dict:
        headers = {"X-Actor-Id": self.actor}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if idempotency:
            headers["Idempotency-Key"] = secrets.token_hex(16)
        return headers

    def health(self) -> dict:
        probes = {
            "orgFlow": (f"{self.org}/health/live", "组织治理"),
            "aiNpc": (f"{self.ainpc}/health", "属官推演"),
            "knowledge": (f"{self.knowledge}/health", "史官知识"),
        }
        result = {}
        for key, (url, label) in probes.items():
            try:
                self.request(url, timeout=1.2)
                result[key] = {"online": True, "label": label}
            except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                result[key] = {"online": False, "label": label}
        result["mode"] = "connected" if any(item["online"] for item in result.values() if isinstance(item, dict)) else "local"
        result["organizationId"] = self.org_id
        return result

    def knowledge_search(self, query: str, limit: int = 6) -> dict:
        payload = {"query": query, "channel_top_k": {"vector": limit, "bm25": limit, "entity": 3, "category": 3, "schedule_tag": 2, "graph": 3, "graph_max_depth": 2}}
        try:
            response = self.request(f"{self.knowledge}/api/v1/player/search", "POST", payload)
            channels = response.get("data", {}).get("channels", {})
            ids = []
            for entries in channels.values():
                for entry in entries or []:
                    if entry.get("id") and entry["id"] not in ids:
                        ids.append(entry["id"])
            details = self.request(f"{self.knowledge}/api/v1/aku/batch_get", "POST", {"ids": ids[:limit]}) if ids else {}
            return {"mode": "connected", "query": query, "results": details.get("data", details) or []}
        except (HTTPError, URLError, TimeoutError, ValueError, OSError):
            return self.local_search(query, limit)

    @staticmethod
    def local_search(query: str, limit: int) -> dict:
        data = json.loads(KNOWLEDGE_FILE.read_text(encoding="utf-8")) if KNOWLEDGE_FILE.exists() else {"entries": []}
        terms = [term.lower() for term in query.split() if term]
        scored = []
        for entry in data.get("entries", []):
            haystack = " ".join(str(entry.get(key, "")) for key in ("name", "summary", "content", "keywords")).lower()
            score = sum(haystack.count(term) for term in terms) if terms else 0
            if score or not terms:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], int(item[1].get("index", 9999))))
        return {"mode": "local", "query": query, "results": [item[1] for item in scored[:limit]]}

    def forward_task(self, payload: dict) -> dict:
        org_id = str(payload.pop("organization_id", "")).strip() or self.org_id
        if not org_id:
            return {"mode": "local", "accepted": False, "reason": "organization_id_missing"}
        now = int(time.time())
        task = {
            "task_type": "TEMPORARY",
            "source": "STORY",
            "title": str(payload.get("title", "东周军府差事"))[:200],
            "description": str(payload.get("description", ""))[:10000],
            "assignee_id": payload.get("assignee_id") or None,
            "start_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "due_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + max(60, int(payload.get("duration_seconds", 3600))))),
            "difficulty": max(1, min(10, int(payload.get("difficulty", 3)))),
            "resource_units": max(0, int(payload.get("resource_units", 0))),
            "reward_units": max(0, int(payload.get("reward_units", 0))),
            "execution_method": str(payload.get("execution_method", "由军府属官自主筹划"))[:2000],
            "execution_location": str(payload.get("execution_location", "东周列国"))[:500],
            "bypass_ai_review": False,
        }
        try:
            result = self.request(f"{self.org}/api/v1/organizations/{org_id}/tasks", "POST", task, self.org_headers(True))
            return {"mode": "connected", "accepted": True, "result": result}
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            return {"mode": "local", "accepted": False, "reason": type(error).__name__}


class Handler(SimpleHTTPRequestHandler):
    services = Services()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = min(int(self.headers.get("Content-Length", "0") or 0), 1_000_000)
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/dongzhou/integration/health":
            self.send_json(self.services.health())
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            if path == "/api/dongzhou/knowledge/search":
                self.send_json(self.services.knowledge_search(str(payload.get("query", "")).strip(), max(1, min(10, int(payload.get("limit", 6))))))
                return
            if path == "/api/dongzhou/organization/tasks":
                self.send_json(self.services.forward_task(dict(payload)))
                return
            self.send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json({"error": "invalid_request", "message": str(error)}, HTTPStatus.BAD_REQUEST)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Dongzhou integrated server: http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
