from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from urllib.parse import urlparse
from uuid import UUID


def _required_secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if len(value) < 32:
        raise RuntimeError(f"{name} must contain at least 32 characters")
    return value


def _upstream_url(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().rstrip("/")
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError(f"{name} must be an absolute HTTP(S) URL without credentials, query, or fragment")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str
    public_origin: str
    database_path: Path
    web_root: Path
    session_secret: str
    orgflow_url: str
    orgflow_hmac_secret: str
    orgflow_hmac_key_id: str
    orgflow_audience: str
    orgflow_org_id: str
    orgflow_manager_member_id: str
    orgflow_hero_slots: dict[str, str]
    orgflow_hero_members: dict[str, str]
    orgflow_hierarchy_version: int
    game_server_id: str
    ainpc_url: str
    ainpc_token: str
    ainpc_game_server_id: int
    knowledge_url: str
    knowledge_token: str
    offline_knowledge_enabled: bool
    knowledge_file: Path
    ainpc_task_token: str = ""
    upstream_timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "Settings":
        environment = os.getenv("DONGZHOU_ENV", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise RuntimeError("DONGZHOU_ENV must be development, test, or production")
        root = Path(__file__).resolve().parents[3]
        secret = os.getenv("DONGZHOU_SESSION_SECRET", "")
        if environment == "production":
            secret = _required_secret("DONGZHOU_SESSION_SECRET")
        elif len(secret) < 32:
            secret = "development-only-change-this-secret"

        def parse_hero_mapping(name: str) -> dict[str, str]:
            mapping: dict[str, str] = {}
            for item in os.getenv(name, "").split(","):
                key, separator, value = item.partition("=")
                if separator and key.strip() and value.strip():
                    mapping[key.strip()] = value.strip()
            return mapping

        slots = parse_hero_mapping("DONGZHOU_ORGFLOW_HERO_SLOTS")
        members = parse_hero_mapping("DONGZHOU_ORGFLOW_HERO_MEMBERS")
        web_root = Path(os.getenv("DONGZHOU_WEB_ROOT", root / "web-game"))
        public_origin = os.getenv("DONGZHOU_PUBLIC_ORIGIN", "http://127.0.0.1:8765").rstrip("/")
        public_origin_parts = urlparse(public_origin)
        if (
            public_origin_parts.scheme not in {"http", "https"}
            or not public_origin_parts.hostname
            or public_origin_parts.username is not None
            or public_origin_parts.password is not None
            or public_origin_parts.path not in {"", "/"}
            or public_origin_parts.query
            or public_origin_parts.fragment
        ):
            raise RuntimeError("DONGZHOU_PUBLIC_ORIGIN must be an HTTP(S) origin without path or credentials")
        org_id = os.getenv("DONGZHOU_ORGFLOW_ORG_ID", "").strip()
        manager_id = os.getenv("DONGZHOU_ORGFLOW_MANAGER_MEMBER_ID", "").strip()
        key_id = os.getenv("DONGZHOU_ORGFLOW_HMAC_KEY_ID", "dongzhou-v1").strip()
        audience = os.getenv("DONGZHOU_ORGFLOW_AUDIENCE", "org-flow-engine-administration").strip()
        hierarchy_version = int(os.getenv("DONGZHOU_ORGFLOW_HIERARCHY_VERSION", "1"))
        upstream_timeout_seconds = float(
            os.getenv("DONGZHOU_UPSTREAM_TIMEOUT_SECONDS", "30")
        )
        game_server_id = os.getenv("DONGZHOU_GAME_SERVER_ID", "91001").strip()
        ainpc_game_server_id = int(os.getenv("DONGZHOU_AINPC_GAME_SERVER_ID", "91001"))
        offline_knowledge_enabled = os.getenv("DONGZHOU_OFFLINE_KNOWLEDGE", "0") == "1"
        orgflow_url = _upstream_url("DONGZHOU_ORGFLOW_URL", "http://127.0.0.1:8030")
        ainpc_url = _upstream_url("DONGZHOU_AINPC_URL", "http://127.0.0.1:8000")
        knowledge_url = _upstream_url("DONGZHOU_KNOWLEDGE_URL", "http://127.0.0.1:8080")
        ainpc_token = os.getenv("DONGZHOU_AINPC_TOKEN", "").strip()
        knowledge_token = os.getenv("DONGZHOU_KNOWLEDGE_TOKEN", "").strip()
        if environment == "production":
            if urlparse(public_origin).scheme != "https":
                raise RuntimeError("DONGZHOU_PUBLIC_ORIGIN must use https in production")
            if not org_id or not manager_id or not slots or not members:
                raise RuntimeError("orgFlow organization, manager, hero-slot, and hero-member mappings are required")
            if slots.keys() != members.keys():
                raise RuntimeError("orgFlow hero-slot and hero-member mappings must contain the same heroes")
            if manager_id not in members.values():
                raise RuntimeError("orgFlow manager must be present in the hero-member mapping")
            if offline_knowledge_enabled:
                raise RuntimeError("DONGZHOU_OFFLINE_KNOWLEDGE must be disabled in production")
            if str(ainpc_game_server_id) != game_server_id:
                raise RuntimeError("DONGZHOU_AINPC_GAME_SERVER_ID must match DONGZHOU_GAME_SERVER_ID")
            ainpc_token = _required_secret("DONGZHOU_AINPC_TOKEN")
            knowledge_token = _required_secret("DONGZHOU_KNOWLEDGE_TOKEN")
        for value in (org_id, manager_id, *slots.values(), *members.values()):
            if value:
                UUID(value)
        if any(
            re.fullmatch(r"[A-Za-z0-9_.:-]+", hero_id) is None
            for hero_id in slots.keys() | members.keys()
        ):
            raise RuntimeError("orgFlow hero mappings contain an invalid hero ID")
        if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", key_id) is None or not audience:
            raise RuntimeError("orgFlow signing identity is invalid")
        if hierarchy_version < 1:
            raise RuntimeError("DONGZHOU_ORGFLOW_HIERARCHY_VERSION must be positive")
        if not 1 <= upstream_timeout_seconds <= 120:
            raise RuntimeError("DONGZHOU_UPSTREAM_TIMEOUT_SECONDS must be between 1 and 120")
        if (
            not game_server_id.isascii()
            or not game_server_id.isdigit()
            or game_server_id.startswith("0")
            or int(game_server_id) >= 2**64
        ):
            raise RuntimeError("DONGZHOU_GAME_SERVER_ID is invalid")
        if ainpc_game_server_id < 1 or ainpc_game_server_id >= 2**64:
            raise RuntimeError("DONGZHOU_AINPC_GAME_SERVER_ID is invalid")
        return cls(
            environment=environment,
            public_origin=public_origin,
            database_path=Path(os.getenv("DONGZHOU_DATABASE_PATH", root / "var" / "dongzhou-integration.sqlite3")),
            web_root=web_root,
            session_secret=secret,
            orgflow_url=orgflow_url,
            orgflow_hmac_secret=(
                _required_secret("DONGZHOU_ORGFLOW_HMAC_SECRET")
                if environment == "production"
                else os.getenv("DONGZHOU_ORGFLOW_HMAC_SECRET", "development-orgflow-shared-secret")
            ),
            orgflow_hmac_key_id=key_id,
            orgflow_audience=audience,
            orgflow_org_id=org_id,
            orgflow_manager_member_id=manager_id,
            orgflow_hero_slots=slots,
            orgflow_hero_members=members,
            orgflow_hierarchy_version=hierarchy_version,
            game_server_id=game_server_id,
            ainpc_url=ainpc_url,
            ainpc_token=ainpc_token,
            ainpc_game_server_id=ainpc_game_server_id,
            knowledge_url=knowledge_url,
            knowledge_token=knowledge_token,
            offline_knowledge_enabled=offline_knowledge_enabled,
            knowledge_file=web_root / "scenario" / "dongzhou-knowledge.json",
            ainpc_task_token=(
                _required_secret("DONGZHOU_AINPC_TASK_TOKEN")
                if environment == "production"
                else os.getenv("DONGZHOU_AINPC_TASK_TOKEN", "").strip()
            ),
            upstream_timeout_seconds=upstream_timeout_seconds,
        )
