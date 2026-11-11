from __future__ import annotations

import asyncio
from contextlib import contextmanager
import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Any, Iterator
from uuid import UUID, uuid4


class VersionConflict(RuntimeError):
    pass


class GameClockConflict(RuntimeError):
    pass


def _organization_month(payload: dict[str, Any]) -> int | None:
    organization = payload.get("organization")
    if not isinstance(organization, dict) or "month" not in organization:
        return None
    month = organization["month"]
    if isinstance(month, bool) or not isinstance(month, int) or month < 1:
        raise GameClockConflict("organization_month_invalid")
    return month


def _private_message_identity(payload: dict[str, Any]) -> dict[str, Any]:
    """Return business identity while excluding retry/login transport metadata."""
    return {
        key: payload.get(key)
        for key in (
            "gameServerId",
            "aiId",
            "chatId",
            "taskId",
            "data",
            "isMinor",
            "needManualTakeover",
            "need_manual_takeover",
            "isNpc",
            "playerInfo",
        )
        if key in payload
    }


def _npc_pair_key(payload: dict[str, Any]) -> str | None:
    participants = payload.get("participants") or []
    npc_ids = sorted(
        str(item.get("id"))
        for item in participants
        if isinstance(item, dict) and item.get("type") == "NPC" and item.get("id")
    )
    return ":".join(npc_ids) if len(npc_ids) == 2 else None


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = asyncio.Lock()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    async def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        async with self._lock:
            with self._connection() as db:
                db.executescript("""
                CREATE TABLE IF NOT EXISTS players (
                  id TEXT PRIMARY KEY, installation_id TEXT NOT NULL UNIQUE,
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS saves (
                  player_id TEXT PRIMARY KEY REFERENCES players(id), version INTEGER NOT NULL,
                  payload TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS requests (
                  player_id TEXT NOT NULL REFERENCES players(id), request_id TEXT NOT NULL,
                  kind TEXT NOT NULL, state TEXT NOT NULL, request_payload TEXT NOT NULL,
                  response_payload TEXT, external_id TEXT, attempts INTEGER NOT NULL DEFAULT 0,
                  last_error TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(player_id, request_id)
                );
                CREATE TABLE IF NOT EXISTS codex (
                  player_id TEXT NOT NULL REFERENCES players(id), aku_id TEXT NOT NULL,
                  payload TEXT NOT NULL, discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(player_id, aku_id)
                );
                CREATE TABLE IF NOT EXISTS player_game_clock (
                  player_id TEXT PRIMARY KEY REFERENCES players(id),
                  month INTEGER NOT NULL CHECK(month >= 1)
                );
                CREATE TABLE IF NOT EXISTS game_clock (
                  singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                  month INTEGER NOT NULL CHECK(month >= 1),
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS npc_runtime (
                  game_server_id TEXT NOT NULL, npc_id TEXT NOT NULL,
                  login_request_id TEXT NOT NULL, instance_id INTEGER,
                  instance_count INTEGER, startup_id TEXT,
                  ready_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(game_server_id, npc_id)
                );
                CREATE TABLE IF NOT EXISTS npc_directory (
                  game_server_id TEXT NOT NULL, npc_id TEXT NOT NULL,
                  hero_id TEXT NOT NULL, npc_name TEXT NOT NULL,
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(game_server_id, npc_id)
                );
                CREATE TABLE IF NOT EXISTS game_server_outbox (
                  event_id TEXT PRIMARY KEY, event_kind TEXT NOT NULL,
                  payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'PENDING',
                  attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT,
                  next_attempt_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS game_server_outbox_pending_idx
                  ON game_server_outbox(state,next_attempt_at,created_at);
                CREATE TABLE IF NOT EXISTS private_chat_messages (
                  message_id TEXT PRIMARY KEY, game_server_id TEXT NOT NULL,
                  npc_id TEXT NOT NULL, chat_id TEXT NOT NULL, task_id TEXT NOT NULL,
                  payload TEXT NOT NULL, delivered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS private_chat_sessions (
                  game_server_id TEXT NOT NULL, chat_id TEXT NOT NULL,
                  task_id TEXT NOT NULL, start_payload TEXT NOT NULL,
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(game_server_id, task_id),
                  UNIQUE(game_server_id, chat_id, task_id)
                );
                CREATE TABLE IF NOT EXISTS private_chat_pair_leases (
                  game_server_id TEXT NOT NULL, pair_key TEXT NOT NULL,
                  task_id TEXT NOT NULL, expires_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(game_server_id, pair_key)
                );
                CREATE INDEX IF NOT EXISTS private_chat_messages_session_idx
                  ON private_chat_messages(game_server_id,chat_id,task_id,delivered_at,message_id);
                """)
                columns = {row[1] for row in db.execute("PRAGMA table_info(requests)")}
                if "external_id" not in columns:
                    db.execute("ALTER TABLE requests ADD COLUMN external_id TEXT")
                db.execute("CREATE INDEX IF NOT EXISTS requests_external_id_idx ON requests(player_id, external_id)")
                db.execute("INSERT OR IGNORE INTO game_clock(singleton, month) VALUES (1, 1)")
                db.execute(
                    "INSERT OR IGNORE INTO player_game_clock(player_id, month) "
                    "SELECT id, 1 FROM players"
                )

    async def mark_npc_ready(
        self,
        game_server_id: str,
        npc_id: str,
        login_request_id: str,
        instance_id: int | None,
        instance_count: int | None,
        startup_id: str | None,
    ) -> None:
        async with self._lock:
            with self._connection() as db:
                db.execute(
                    "INSERT INTO npc_runtime(game_server_id,npc_id,login_request_id,instance_id,instance_count,startup_id) "
                    "VALUES (?,?,?,?,?,?) ON CONFLICT(game_server_id,npc_id) DO UPDATE SET "
                    "login_request_id=excluded.login_request_id,instance_id=excluded.instance_id,"
                    "instance_count=excluded.instance_count,startup_id=excluded.startup_id,ready_at=CURRENT_TIMESTAMP",
                    (game_server_id, npc_id, login_request_id, instance_id, instance_count, startup_id),
                )

    async def read_npc_runtime(self, game_server_id: str, npc_id: str) -> dict[str, Any] | None:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT login_request_id,instance_id,instance_count,startup_id,ready_at "
                    "FROM npc_runtime WHERE game_server_id=? AND npc_id=?",
                    (game_server_id, npc_id),
                ).fetchone()
        if row is None:
            return None
        return {
            "state": "READY",
            "loginRequestId": row["login_request_id"],
            "instanceId": row["instance_id"],
            "instanceCount": row["instance_count"],
            "startupId": row["startup_id"],
            "readyAt": row["ready_at"],
        }

    async def clear_npc_runtime(self, game_server_id: str, npc_ids: list[str]) -> None:
        if not npc_ids:
            return
        async with self._lock:
            with self._connection() as db:
                db.executemany(
                    "DELETE FROM npc_runtime WHERE game_server_id=? AND npc_id=?",
                    [(game_server_id, npc_id) for npc_id in npc_ids],
                )

    async def upsert_npc_directory(
        self, game_server_id: str, npcs: list[dict[str, str]]
    ) -> None:
        async with self._lock:
            with self._connection() as db:
                for npc in npcs:
                    db.execute(
                        "INSERT INTO npc_directory(game_server_id,npc_id,hero_id,npc_name) "
                        "VALUES (?,?,?,?) ON CONFLICT(game_server_id,npc_id) DO UPDATE SET "
                        "hero_id=excluded.hero_id,npc_name=excluded.npc_name,updated_at=CURRENT_TIMESTAMP",
                        (game_server_id, npc["npcId"], npc["heroId"], npc["name"]),
                    )

    async def list_npcs(
        self, game_server_id: str, *, include_offline: bool = False
    ) -> list[dict[str, Any]]:
        condition = "" if include_offline else "WHERE runtime.npc_id IS NOT NULL"
        async with self._lock:
            with self._connection() as db:
                rows = db.execute(
                    "SELECT directory.npc_id,directory.npc_name,directory.hero_id,"
                    "CASE WHEN runtime.npc_id IS NULL THEN 0 ELSE 1 END AS is_online "
                    "FROM npc_directory AS directory LEFT JOIN npc_runtime AS runtime "
                    "ON runtime.game_server_id=directory.game_server_id "
                    "AND runtime.npc_id=directory.npc_id "
                    "WHERE directory.game_server_id=? "
                    + ("" if include_offline else "AND runtime.npc_id IS NOT NULL ")
                    + "ORDER BY directory.npc_id",
                    (game_server_id,),
                ).fetchall()
        return [
            {
                "id": row["npc_id"],
                "name": row["npc_name"],
                "heroId": row["hero_id"],
                "serverId": game_server_id,
                "isOnline": int(row["is_online"]),
            }
            for row in rows
        ]

    async def enqueue_game_event(
        self,
        event_id: str,
        event_kind: str,
        payload: dict[str, Any],
        *,
        requeue_delivered: bool = False,
    ) -> bool:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT event_kind,payload,state FROM game_server_outbox WHERE event_id=?",
                    (event_id,),
                ).fetchone()
                if row is not None:
                    if row["event_kind"] != event_kind or row["payload"] != encoded:
                        raise VersionConflict("game_event_idempotency_conflict")
                    if requeue_delivered and row["state"] == "DELIVERED":
                        db.execute(
                            "UPDATE game_server_outbox SET state='PENDING',"
                            "next_attempt_at=CURRENT_TIMESTAMP,last_error=NULL,"
                            "updated_at=CURRENT_TIMESTAMP WHERE event_id=?",
                            (event_id,),
                        )
                        return True
                    return False
                db.execute(
                    "INSERT INTO game_server_outbox(event_id,event_kind,payload) VALUES (?,?,?)",
                    (event_id, event_kind, encoded),
                )
        return True

    async def pending_game_events(self, limit: int = 20) -> list[dict[str, Any]]:
        async with self._lock:
            with self._connection() as db:
                rows = db.execute(
                    "SELECT event_id,event_kind,payload,attempts FROM game_server_outbox "
                    "WHERE state='PENDING' AND next_attempt_at<=CURRENT_TIMESTAMP "
                    "ORDER BY created_at,event_id LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {
                "eventId": row["event_id"],
                "kind": row["event_kind"],
                "payload": json.loads(row["payload"]),
                "attempts": int(row["attempts"]),
            }
            for row in rows
        ]

    async def finish_game_event(self, event_id: str) -> None:
        async with self._lock:
            with self._connection() as db:
                db.execute(
                    "UPDATE game_server_outbox SET state='DELIVERED',attempts=attempts+1,"
                    "last_error=NULL,updated_at=CURRENT_TIMESTAMP WHERE event_id=?",
                    (event_id,),
                )

    async def game_event_status(self, event_id: str) -> dict[str, Any] | None:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT state,attempts,last_error,updated_at "
                    "FROM game_server_outbox WHERE event_id=?",
                    (event_id,),
                ).fetchone()
        if row is None:
            return None
        return {
            "state": str(row["state"]),
            "attempts": int(row["attempts"]),
            "lastError": row["last_error"],
            "updatedAt": row["updated_at"],
        }

    async def npc_outcomes_missing_memory(self) -> list[dict[str, Any]]:
        async with self._lock:
            with self._connection() as db:
                rows = db.execute(
                    "SELECT event_id,payload FROM game_server_outbox AS outcome "
                    "WHERE event_kind='NPC_TASK_OUTCOME' AND state='DELIVERED' "
                    "AND NOT EXISTS ("
                    "SELECT 1 FROM game_server_outbox AS memory "
                    "WHERE memory.event_id='npc-memory:' || substr(outcome.event_id,13)"
                    ") ORDER BY created_at,event_id"
                ).fetchall()
        return [
            {"eventId": str(row["event_id"]), "payload": json.loads(row["payload"])}
            for row in rows
        ]

    async def retry_game_event(self, event_id: str, error: str) -> None:
        async with self._lock:
            with self._connection() as db:
                db.execute(
                    "UPDATE game_server_outbox SET attempts=attempts+1,last_error=?,"
                    "next_attempt_at=datetime('now','+' || MIN(60,1 << MIN(attempts,5)) || ' seconds'),"
                    "updated_at=CURRENT_TIMESTAMP WHERE event_id=?",
                    (error[:256], event_id),
                )

    async def register_private_chat(self, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            with self._connection() as db:
                pair_key = _npc_pair_key(payload)
                if pair_key is not None:
                    lease = db.execute(
                        "SELECT task_id FROM private_chat_pair_leases "
                        "WHERE game_server_id=? AND pair_key=? AND expires_at > CURRENT_TIMESTAMP",
                        (payload["gameServerId"], pair_key),
                    ).fetchone()
                    if lease is not None and lease["task_id"] != payload["taskId"]:
                        raise VersionConflict("private_chat_pair_busy")
                    db.execute(
                        "INSERT INTO private_chat_pair_leases(game_server_id,pair_key,task_id,expires_at) "
                        "VALUES (?,?,?,datetime('now','+2 minutes')) "
                        "ON CONFLICT(game_server_id,pair_key) DO UPDATE SET "
                        "task_id=excluded.task_id,expires_at=excluded.expires_at,updated_at=CURRENT_TIMESTAMP",
                        (payload["gameServerId"], pair_key, payload["taskId"]),
                    )
                row = db.execute(
                    "SELECT start_payload FROM private_chat_sessions "
                    "WHERE game_server_id=? AND task_id=?",
                    (payload["gameServerId"], payload["taskId"]),
                ).fetchone()
                if row is not None and row["start_payload"] != encoded:
                    raise VersionConflict("private_chat_session_idempotency_conflict")
                db.execute(
                    "INSERT OR IGNORE INTO private_chat_sessions"
                    "(game_server_id,chat_id,task_id,start_payload) VALUES (?,?,?,?)",
                    (
                        payload["gameServerId"],
                        payload["chatId"],
                        payload["taskId"],
                        encoded,
                    ),
                )

    async def record_private_message(
        self, payload: dict[str, Any], *, route_to_npc: bool = False
    ) -> None:
        message = payload.get("data", {}).get("message", {})
        message_id = str(message.get("id") or "").strip()
        if not message_id:
            raise ValueError("private_message_id_missing")
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT payload FROM private_chat_messages WHERE message_id=?",
                    (message_id,),
                ).fetchone()
                if row is not None and _private_message_identity(
                    json.loads(row["payload"])
                ) != _private_message_identity(payload):
                    raise VersionConflict("private_message_idempotency_conflict")
                db.execute(
                    "INSERT OR IGNORE INTO private_chat_messages"
                    "(message_id,game_server_id,npc_id,chat_id,task_id,payload) VALUES (?,?,?,?,?,?)",
                    (
                        message_id,
                        payload["gameServerId"],
                        payload["aiId"],
                        payload["chatId"],
                        payload["taskId"],
                        encoded,
                    ),
                )
                target_id = str((payload.get("playerInfo") or {}).get("playerId") or "")
                if target_id and target_id != str(payload["aiId"]):
                    pair_key = ":".join(sorted((str(payload["aiId"]), target_id)))
                    finished = bool((payload.get("data") or {}).get("isFinish")) or bool(
                        message.get("isStopped")
                    )
                    if finished:
                        db.execute(
                            "DELETE FROM private_chat_pair_leases WHERE game_server_id=? AND pair_key=?",
                            (payload["gameServerId"], pair_key),
                        )
                    else:
                        db.execute(
                            "UPDATE private_chat_pair_leases SET expires_at=datetime('now','+2 minutes'),"
                            "updated_at=CURRENT_TIMESTAMP WHERE game_server_id=? AND pair_key=?",
                            (payload["gameServerId"], pair_key),
                        )
                # peerchat tasks are recipient-side delivery aliases. Their
                # replies are durable callbacks, not another relay turn;
                # forwarding them would create an unbounded NPC ping-pong.
                if not route_to_npc or str(payload["taskId"]).startswith("peerchat-"):
                    return
                session_row = db.execute(
                    "SELECT start_payload FROM private_chat_sessions "
                    "WHERE game_server_id=? AND chat_id=? AND task_id=?",
                    (payload["gameServerId"], payload["chatId"], payload["taskId"]),
                ).fetchone()
                if session_row is None:
                    raise VersionConflict("private_chat_session_not_found")
                session = json.loads(session_row["start_payload"])
                peer = payload.get("playerInfo") or {}
                target_id = str(peer.get("playerId") or "")
                participants = session.get("participants") or []
                if target_id == payload["aiId"] or not any(
                    str(item.get("id")) == target_id and item.get("type") == "NPC"
                    for item in participants
                    if isinstance(item, dict)
                ):
                    raise VersionConflict("private_chat_target_mismatch")
                rows = db.execute(
                    "SELECT payload FROM private_chat_messages "
                    "WHERE game_server_id=? AND chat_id=? AND task_id=? "
                    "ORDER BY delivered_at,message_id",
                    (payload["gameServerId"], payload["chatId"], payload["taskId"]),
                ).fetchall()
                messages = [
                    json.loads(item["payload"])["data"]["message"] for item in rows
                ]
                recipient_digest = hashlib.sha256(
                    f"{payload['gameServerId']}\n{payload['taskId']}\n{target_id}\n{message_id}".encode()
                ).hexdigest()
                recipient_task_id = "peerchat-" + recipient_digest[:32]
                recipient_session = {
                    **session,
                    "npcId": target_id,
                    "speakerId": target_id,
                    "taskId": recipient_task_id,
                    "status": "start",
                    "messages": [],
                }
                recipient_session_encoded = json.dumps(
                    recipient_session,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                recipient_session_row = db.execute(
                    "SELECT start_payload FROM private_chat_sessions "
                    "WHERE game_server_id=? AND task_id=?",
                    (payload["gameServerId"], recipient_task_id),
                ).fetchone()
                if (
                    recipient_session_row is not None
                    and recipient_session_row["start_payload"] != recipient_session_encoded
                ):
                    raise VersionConflict("private_chat_session_idempotency_conflict")
                db.execute(
                    "INSERT OR IGNORE INTO private_chat_sessions"
                    "(game_server_id,chat_id,task_id,start_payload) VALUES (?,?,?,?)",
                    (
                        payload["gameServerId"],
                        payload["chatId"],
                        recipient_task_id,
                        recipient_session_encoded,
                    ),
                )

                turn = {
                    **recipient_session,
                    "npcId": target_id,
                    "speakerId": target_id,
                    # isFinish/isStopped describe the sender's local response. They
                    # must not close the recipient's owner view before it can act
                    # on the delivered message. A recipient-side finish is a
                    # separate chat lifecycle event, not a property of this turn.
                    "status": "inProgress",
                    "messages": messages,
                }
                turn_encoded = json.dumps(
                    turn, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                )
                event_id = "chat-turn:" + hashlib.sha256(
                    f"{payload['gameServerId']}\n{payload['taskId']}\n{target_id}\n{message_id}".encode()
                ).hexdigest()
                event = db.execute(
                    "SELECT event_kind,payload FROM game_server_outbox WHERE event_id=?",
                    (event_id,),
                ).fetchone()
                if event is not None and (
                    event["event_kind"] != "CHAT_TURN" or event["payload"] != turn_encoded
                ):
                    raise VersionConflict("game_event_idempotency_conflict")
                db.execute(
                    "INSERT OR IGNORE INTO game_server_outbox(event_id,event_kind,payload) "
                    "VALUES (?, 'CHAT_TURN', ?)",
                    (event_id, turn_encoded),
                )

    async def query_private_message_delivery(
        self,
        *,
        game_server_id: str,
        npc_id: str,
        chat_id: str,
        task_id: str,
        message_id: str,
        delivery_attempt_id: str,
        attempt: int,
    ) -> dict[str, Any]:
        """Return authoritative evidence from the synchronous game-side ledger."""
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT payload,delivered_at FROM private_chat_messages WHERE message_id=?",
                    (message_id,),
                ).fetchone()
        status = "not_delivered"
        occurred_at = datetime.now(UTC).isoformat()
        if row is not None:
            payload = json.loads(row["payload"])
            expected = (game_server_id, npc_id, chat_id, task_id, delivery_attempt_id, attempt)
            actual = (
                str(payload.get("gameServerId") or ""),
                str(payload.get("aiId") or ""),
                str(payload.get("chatId") or ""),
                str(payload.get("taskId") or ""),
                str(payload.get("deliveryAttemptId") or ""),
                int(payload.get("attempt") or 0),
            )
            if actual != expected:
                raise VersionConflict("private_message_delivery_identity_conflict")
            status = "delivered"
            occurred_at = str(row["delivered_at"]) + "+00:00"
        callback_id = hashlib.sha256(
            f"delivery-query\n{message_id}\n{delivery_attempt_id}\n{attempt}\n{status}".encode()
        ).hexdigest()[:32]
        return {
            "success": True,
            "status": status,
            "gameServerId": game_server_id,
            "npcId": npc_id,
            "chatId": chat_id,
            "taskId": task_id,
            "messageId": message_id,
            "deliveryAttemptId": delivery_attempt_id,
            "attempt": attempt,
            "callbackId": callback_id,
            "occurredAt": occurred_at,
        }

    async def private_chat_runtime_state(
        self, game_server_id: str, npc_id: str
    ) -> dict[str, Any]:
        async with self._lock:
            with self._connection() as db:
                rows = db.execute(
                    "SELECT chat_id,task_id,start_payload FROM private_chat_sessions "
                    "WHERE game_server_id=? ORDER BY created_at,task_id",
                    (game_server_id,),
                ).fetchall()
                sessions_by_chat: dict[str, dict[str, Any]] = {}
                for row in rows:
                    start = json.loads(row["start_payload"])
                    if str(start.get("npcId") or "") != npc_id:
                        continue
                    participants = start.get("participants") or []
                    if not any(
                        isinstance(item, dict)
                        and str(item.get("id")) == npc_id
                        and str(item.get("type", "")).upper() == "NPC"
                        for item in participants
                    ):
                        continue
                    peer = next(
                        (
                            item
                            for item in participants
                            if isinstance(item, dict) and str(item.get("id")) != npc_id
                        ),
                        None,
                    )
                    if peer is None:
                        continue
                    last = db.execute(
                        "SELECT payload FROM private_chat_messages "
                        "WHERE game_server_id=? AND chat_id=? AND task_id=? "
                        "ORDER BY delivered_at DESC,message_id DESC LIMIT 1",
                        (game_server_id, row["chat_id"], row["task_id"]),
                    ).fetchone()
                    terminal = False
                    if last is not None:
                        payload = json.loads(last["payload"])
                        data = payload.get("data") or {}
                        message = data.get("message") or {}
                        terminal = data.get("isFinish") is True or message.get("isStopped") is True
                    # Each relayed turn gets its own task id for AINPC
                    # idempotency, but they are still one logical chat here.
                    sessions_by_chat[row["chat_id"]] = {
                        "targetId": str(peer.get("id")),
                        "chatId": row["chat_id"],
                        "topic": str(start.get("topic") or ""),
                        "inReply": False,
                        "isSending": False,
                        "phase": "finished" if terminal else "active",
                        "waitingReplies": [],
                        "queuedSendCount": 0,
                    }
                sessions = list(sessions_by_chat.values())
        return {
            "sessions": sessions,
            "waitingReplyCount": 0,
            "pendingMessageCount": 0,
            "queuedSendCount": 0,
            "observedAt": datetime.now(UTC).isoformat(),
        }

    async def reset_private_chat_pair_lease(
        self, game_server_id: str, npc_id: str, target_id: str
    ) -> bool:
        """Release only the requested NPC pair while preserving chat history."""
        pair_key = ":".join(sorted((str(npc_id), str(target_id))))
        async with self._lock:
            with self._connection() as db:
                result = db.execute(
                    "DELETE FROM private_chat_pair_leases "
                    "WHERE game_server_id=? AND pair_key=?",
                    (game_server_id, pair_key),
                )
                return result.rowcount > 0

    @staticmethod
    def _correspondence_view(row: sqlite3.Row) -> dict[str, Any] | None:
        payload = json.loads(row["payload"])
        data = payload.get("data") or {}
        message = data.get("message") or {}
        start = json.loads(row["start_payload"]) if row["start_payload"] else {}
        content = str(message.get("content") or "").strip()
        speaker_id = str(message.get("speakerId") or payload.get("aiId") or "")
        participants = start.get("participants") or []
        target = payload.get("playerInfo") or {}
        target_id = str(target.get("playerId") or "")
        if not target_id:
            peers = [
                item
                for item in participants
                if isinstance(item, dict)
                and str(item.get("id") or "")
                and str(item.get("id")) != speaker_id
            ]
            if len(peers) == 1:
                target = peers[0]
                target_id = str(target["id"])
        target_type = next(
            (
                str(item.get("type") or "").upper()
                for item in participants
                if isinstance(item, dict) and str(item.get("id") or "") == target_id
            ),
            "PLAYER" if payload.get("isNpc") is False else "NPC",
        )
        if not content or not speaker_id or not target_id:
            return None
        return {
            "messageId": str(row["message_id"]),
            "chatId": str(row["chat_id"]),
            "taskId": str(row["task_id"]),
            "speakerId": speaker_id,
            "speakerName": str(message.get("speakerName") or speaker_id),
            "targetId": target_id,
            "targetName": str(target.get("playerName") or target.get("name") or target_id),
            "targetType": target_type,
            "content": content[:2000],
            "emotion": str(message.get("speakerEmotion") or ""),
            "topic": str(start.get("topic") or "")[:1000],
            "messageTime": str(message.get("time") or ""),
            "deliveredAt": str(row["delivered_at"]),
            "terminal": data.get("isFinish") is True or message.get("isStopped") is True,
        }

    async def list_npc_correspondence(
        self,
        game_server_id: str,
        npc_id: str,
        *,
        limit: int = 20,
        player_peer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        bounded_limit = max(1, min(int(limit), 50))
        async with self._lock:
            with self._connection() as db:
                rows = db.execute(
                    "SELECT m.message_id,m.chat_id,m.task_id,m.payload,m.delivered_at,"
                    "s.start_payload FROM private_chat_messages m "
                    "LEFT JOIN private_chat_sessions s ON s.game_server_id=m.game_server_id "
                    "AND s.chat_id=m.chat_id AND s.task_id=m.task_id "
                    "WHERE m.game_server_id=? ORDER BY m.delivered_at DESC,m.message_id DESC LIMIT 500",
                    (game_server_id,),
                ).fetchall()
        messages: list[dict[str, Any]] = []
        for row in rows:
            view = self._correspondence_view(row)
            if view is None or npc_id not in {view["speakerId"], view["targetId"]}:
                continue
            if (
                view["targetType"] == "PLAYER"
                and player_peer_id is not None
                and view["targetId"] != player_peer_id
            ):
                continue
            messages.append(view)
            if len(messages) >= bounded_limit:
                break
        return messages

    async def read_correspondence_message(
        self, game_server_id: str, message_id: str
    ) -> dict[str, Any] | None:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT m.message_id,m.chat_id,m.task_id,m.payload,m.delivered_at,"
                    "s.start_payload FROM private_chat_messages m "
                    "LEFT JOIN private_chat_sessions s ON s.game_server_id=m.game_server_id "
                    "AND s.chat_id=m.chat_id AND s.task_id=m.task_id "
                    "WHERE m.game_server_id=? AND m.message_id=?",
                    (game_server_id, message_id),
                ).fetchone()
        return self._correspondence_view(row) if row is not None else None

    async def get_or_create_player(self, installation_id: UUID) -> UUID:
        player_id = uuid4()
        async with self._lock:
            with self._connection() as db:
                existing = db.execute("SELECT id FROM players WHERE installation_id=?", (str(installation_id),)).fetchone()
                if existing:
                    return UUID(existing["id"])
                db.execute("INSERT INTO players(id, installation_id) VALUES (?, ?)", (str(player_id), str(installation_id)))
                db.execute("INSERT INTO saves(player_id, version, payload) VALUES (?, 1, ?)", (str(player_id), "{}"))
                db.execute("INSERT INTO player_game_clock(player_id, month) VALUES (?, 1)", (str(player_id),))
        return player_id

    async def read_save(self, player_id: UUID) -> dict[str, Any]:
        async with self._lock:
            with self._connection() as db:
                row = db.execute("SELECT version, payload, updated_at FROM saves WHERE player_id=?", (str(player_id),)).fetchone()
        if row is None:
            raise KeyError("player_not_found")
        return {"version": row["version"], "payload": json.loads(row["payload"]), "updatedAt": row["updated_at"]}

    async def write_save(
        self, player_id: UUID, expected_version: int, payload: dict[str, Any],
        *, organization_reports: list[dict[str, Any]] | None = None,
        game_events: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        requested_month = _organization_month(payload)
        async with self._lock:
            with self._connection() as db:
                if requested_month is not None:
                    clock = db.execute(
                        "SELECT month FROM player_game_clock WHERE player_id=?",
                        (str(player_id),),
                    ).fetchone()
                    if clock is None:
                        raise KeyError("player_not_found")
                    current_month = int(clock["month"])
                    if requested_month < current_month or requested_month > current_month + 1:
                        raise GameClockConflict("organization_month_out_of_sequence")
                cursor = db.execute(
                    "UPDATE saves SET version=version+1,payload=?,updated_at=CURRENT_TIMESTAMP WHERE player_id=? AND version=?",
                    (encoded, str(player_id), expected_version),
                )
                if cursor.rowcount != 1:
                    raise VersionConflict("save_version_conflict")
                # 存档与到期复命原子提交；首次复命冻结结局，后续疲劳变化不得重写已发事件。
                for report in organization_reports or []:
                    db.execute(
                        "INSERT OR IGNORE INTO game_server_outbox(event_id,event_kind,payload) "
                        "VALUES (?, 'ORG_REPORT_START', ?)",
                        ("org-report:" + str(report["task_id"]),
                         json.dumps(report, ensure_ascii=False, separators=(",", ":"), sort_keys=True)),
                    )
                for event in game_events or []:
                    event_id = str(event["eventId"])
                    event_kind = str(event["kind"])
                    event_payload = json.dumps(
                        event["payload"],
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                    existing_event = db.execute(
                        "SELECT event_kind,payload FROM game_server_outbox WHERE event_id=?",
                        (event_id,),
                    ).fetchone()
                    if existing_event is not None:
                        if (
                            existing_event["event_kind"] != event_kind
                            or existing_event["payload"] != event_payload
                        ):
                            raise VersionConflict("game_event_idempotency_conflict")
                        continue
                    db.execute(
                        "INSERT INTO game_server_outbox(event_id,event_kind,payload) "
                        "VALUES (?,?,?)",
                        (event_id, event_kind, event_payload),
                    )
                if requested_month is not None:
                    db.execute(
                        "UPDATE player_game_clock SET month=? WHERE player_id=?",
                        (requested_month, str(player_id)),
                    )
                    if requested_month == current_month + 1:
                        # The organization clock is a shared world clock. Every player's
                        # first committed one-month advance moves it once; replaying the
                        # same save month is idempotent even when that player joined late.
                        db.execute(
                            "UPDATE game_clock SET month=month+1,updated_at=CURRENT_TIMESTAMP WHERE singleton=1"
                        )
        return await self.read_save(player_id)

    async def read_game_clock(self) -> dict[str, Any]:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT month,updated_at FROM game_clock WHERE singleton=1"
                ).fetchone()
        if row is None:
            raise RuntimeError("game_clock_not_initialized")
        month = int(row["month"])
        virtual_date = date(771, 1, 1) + timedelta(days=(month - 1) * 30)
        return {
            "month": month,
            "virtualTime": (
                f"{virtual_date.year:04d}-{virtual_date.month:02d}-{virtual_date.day:02d} 14:00:00"
            ),
            "timeScale": 0,
            "updatedAt": row["updated_at"],
        }

    async def begin_request(
        self,
        player_id: UUID,
        request_id: UUID,
        kind: str,
        payload: dict[str, Any],
        *,
        retry_states: tuple[str, ...] = ("RETRYABLE",),
        reclaim_pending: bool = True,
    ) -> tuple[bool, dict[str, Any] | None]:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT kind,state,request_payload,response_payload,"
                    "updated_at < datetime('now','-2 minutes') AS lease_expired "
                    "FROM requests WHERE player_id=? AND request_id=?",
                    (str(player_id), str(request_id)),
                ).fetchone()
                if row:
                    if row["kind"] != kind or row["request_payload"] != encoded:
                        raise VersionConflict("idempotency_conflict")
                    if row["state"] in retry_states or (
                        reclaim_pending
                        and row["state"] == "PENDING"
                        and bool(row["lease_expired"])
                    ):
                        db.execute("UPDATE requests SET state='PENDING',updated_at=CURRENT_TIMESTAMP WHERE player_id=? AND request_id=?", (str(player_id), str(request_id)))
                        return True, None
                    return False, json.loads(row["response_payload"]) if row["response_payload"] else {"state": row["state"]}
                db.execute("INSERT INTO requests(player_id,request_id,kind,state,request_payload) VALUES (?,?,?,?,?)", (str(player_id), str(request_id), kind, "PENDING", encoded))
        return True, None

    async def finish_request(self, player_id: UUID, request_id: UUID, state: str, response: dict[str, Any], error: str | None = None, external_id: str | None = None) -> None:
        async with self._lock:
            with self._connection() as db:
                db.execute("UPDATE requests SET state=?,response_payload=?,external_id=COALESCE(?,external_id),attempts=attempts+1,last_error=?,updated_at=CURRENT_TIMESTAMP WHERE player_id=? AND request_id=?", (state, json.dumps(response, ensure_ascii=False, separators=(",", ":")), external_id, error, str(player_id), str(request_id)))

    async def transition_request(
        self,
        player_id: UUID,
        request_id: UUID,
        kind: str,
        expected_state: str,
        state: str,
        response: dict[str, Any],
    ) -> bool:
        async with self._lock:
            with self._connection() as db:
                result = db.execute(
                    "UPDATE requests SET state=?,response_payload=?,attempts=attempts+1,"
                    "last_error=NULL,updated_at=CURRENT_TIMESTAMP "
                    "WHERE player_id=? AND request_id=? AND kind=? AND state=?",
                    (
                        state,
                        json.dumps(response, ensure_ascii=False, separators=(",", ":")),
                        str(player_id),
                        str(request_id),
                        kind,
                        expected_state,
                    ),
                )
        return result.rowcount == 1

    async def claim_request(
        self,
        player_id: UUID,
        request_id: UUID,
        kind: str,
        expected_states: tuple[str, ...],
        response: dict[str, Any],
    ) -> bool:
        if not expected_states:
            raise ValueError("expected_states must not be empty")
        placeholders = ",".join("?" for _ in expected_states)
        async with self._lock:
            with self._connection() as db:
                result = db.execute(
                    "UPDATE requests SET state='PENDING',response_payload=?,"
                    "attempts=attempts+1,last_error=NULL,updated_at=CURRENT_TIMESTAMP "
                    "WHERE player_id=? AND request_id=? AND kind=? AND "
                    f"(state IN ({placeholders}) OR "
                    "(state='PENDING' AND updated_at < datetime('now','-2 minutes')))",
                    (
                        json.dumps(response, ensure_ascii=False, separators=(",", ":")),
                        str(player_id),
                        str(request_id),
                        kind,
                        *expected_states,
                    ),
                )
        return result.rowcount == 1

    async def read_request(
        self, player_id: UUID, request_id: UUID, kind: str
    ) -> dict[str, Any] | None:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT state,request_payload,response_payload,external_id "
                    "FROM requests WHERE player_id=? AND request_id=? AND kind=?",
                    (str(player_id), str(request_id), kind),
                ).fetchone()
        if row is None:
            return None
        return {
            "state": row["state"],
            "request": json.loads(row["request_payload"]),
            "response": json.loads(row["response_payload"]) if row["response_payload"] else None,
            "externalId": row["external_id"],
        }

    async def read_external_request(
        self, player_id: UUID, external_id: str, kind: str
    ) -> dict[str, Any] | None:
        async with self._lock:
            with self._connection() as db:
                row = db.execute(
                    "SELECT request_payload FROM requests "
                    "WHERE player_id=? AND external_id=? AND kind=?",
                    (str(player_id), external_id, kind),
                ).fetchone()
        return None if row is None else json.loads(row["request_payload"])

    async def owns_external_request(self, player_id: UUID, external_id: str, kind: str) -> bool:
        async with self._lock:
            with self._connection() as db:
                row = db.execute("SELECT 1 FROM requests WHERE player_id=? AND external_id=? AND kind=?", (str(player_id), external_id, kind)).fetchone()
        return row is not None

    async def add_codex(self, player_id: UUID, entries: list[dict[str, Any]]) -> None:
        async with self._lock:
            with self._connection() as db:
                for entry in entries:
                    aku_id = str(entry.get("id") or entry.get("aku_id") or "").strip()
                    if aku_id:
                        db.execute("INSERT INTO codex(player_id,aku_id,payload) VALUES (?,?,?) ON CONFLICT(player_id,aku_id) DO UPDATE SET payload=excluded.payload", (str(player_id), aku_id, json.dumps(entry, ensure_ascii=False, separators=(",", ":"))))

    async def list_codex(self, player_id: UUID) -> list[dict[str, Any]]:
        async with self._lock:
            with self._connection() as db:
                rows = db.execute("SELECT payload FROM codex WHERE player_id=? ORDER BY discovered_at DESC", (str(player_id),)).fetchall()
        return [json.loads(row["payload"]) for row in rows]
