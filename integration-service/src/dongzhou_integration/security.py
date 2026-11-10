from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from uuid import UUID, uuid4


class InvalidSession(ValueError):
    pass


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def issue_session(player_id: UUID, secret: str, *, lifetime_seconds: int = 86400) -> str:
    payload = {"sub": str(player_id), "exp": int(time.time()) + lifetime_seconds, "v": 1}
    body = _encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    signature = _encode(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{signature}"


def verify_session(token: str, secret: str) -> UUID:
    body, separator, signature = token.partition(".")
    expected = _encode(hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest())
    if not separator or not hmac.compare_digest(signature, expected):
        raise InvalidSession("invalid session signature")
    try:
        payload = json.loads(_decode(body))
        if payload.get("v") != 1 or int(payload["exp"]) < int(time.time()):
            raise InvalidSession("session expired")
        return UUID(payload["sub"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        if isinstance(error, InvalidSession):
            raise
        raise InvalidSession("invalid session payload") from error


def stable_npc_id(game_server_id: int, hero_id: str) -> int:
    digest = hashlib.blake2b(f"dongzhou:{game_server_id}:{hero_id}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") & ((1 << 63) - 1) or 1


def stable_event_id(player_id: UUID, client_request_id: UUID) -> str:
    return f"dongzhou:{player_id}:{client_request_id}"


def sign_orgflow_request(
    *,
    method: str,
    path_and_query: str,
    audience: str,
    key_id: str,
    secret: str,
    body: bytes,
) -> dict[str, str]:
    request_time = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    nonce = uuid4().hex + uuid4().hex
    material = "\n".join(
        (
            method.upper(),
            path_and_query,
            audience,
            key_id,
            request_time,
            nonce,
            hashlib.sha256(body).hexdigest(),
        )
    ).encode("ascii")
    return {
        "Content-Type": "application/json",
        "X-Org-Service-Key-Id": key_id,
        "X-Org-Service-Time": request_time,
        "X-Org-Service-Nonce": nonce,
        "X-Org-Service-Signature": hmac.new(secret.encode(), material, hashlib.sha256).hexdigest(),
    }
