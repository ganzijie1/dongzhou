"""真实网关冒烟验收：独立访客存档，不派差、不推进共享游戏时钟。"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import httpx
import json
from pathlib import Path
import re
import sys
from uuid import uuid4


NPC_EXECUTION_FIELDS = {
    "available",
    "running",
    "paused",
    "waitingForReport",
    "executionId",
    "phase",
    "outcome",
    "scheduleId",
    "scheduleName",
    "scheduleDate",
    "actionChainId",
    "currentActionUid",
    "currentActionId",
    "currentActionIndex",
    "totalActions",
    "updatedAt",
}
NPC_EXECUTION_OUTCOMES = {None, "unconfirmed", "succeeded", "failed"}


def validate_npc_execution(value: object) -> dict:
    assert isinstance(value, dict), "NPC execution projection is missing"
    assert isinstance(value.get("available"), bool), "NPC execution availability is invalid"
    unexpected = set(value) - NPC_EXECUTION_FIELDS
    assert not unexpected, f"NPC execution leaked fields: {sorted(unexpected)}"
    assert value.get("outcome") in NPC_EXECUTION_OUTCOMES, "NPC execution outcome is invalid"
    if value["available"]:
        assert isinstance(value.get("running"), bool), "NPC execution running state is invalid"
        assert isinstance(value.get("paused"), bool), "NPC execution paused state is invalid"
        assert isinstance(value.get("waitingForReport"), bool), "NPC execution report state is invalid"
    return {
        "available": value["available"],
        "phase": value.get("phase"),
        "outcome": value.get("outcome"),
        "publicFields": len(value),
    }

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import verify_four_service_runtime as four_service_delivery


def validate_dongzhou_schedule(schedule: dict) -> dict:
    """校验真实日程内容；不能把有 90 条旧游戏日程当作东周接入成功。"""
    assert schedule.get("code") in (0, 200, "0", "200"), "schedule business request failed"
    data = schedule.get("data", {})
    days = data.get("schedules", [])
    assert isinstance(days, list) and len(days) == 90, "expected 90 schedule days"
    assert all(isinstance(day, dict) for day in days), "invalid schedule day"
    assert [day.get("day") for day in days] == list(range(1, 91)), "schedule days are missing, duplicated or unordered"
    try:
        first_date = date.fromisoformat(data["start_date"])
        dates = [date.fromisoformat(day["date"]) for day in days]
        end_date = date.fromisoformat(data["end_date"])
    except (KeyError, TypeError, ValueError):
        raise AssertionError("schedule dates are missing or invalid") from None
    assert dates == [first_date + timedelta(days=offset) for offset in range(90)], "schedule dates are not 90 consecutive days"
    assert dates[-1] == end_date, "schedule end date does not match its days"
    transaction_ids = set()
    temporary_transaction_ids = set()
    event_ids = set()
    event_count = 0
    for day in days:
        events = day.get("events")
        assert isinstance(events, list) and events, "schedule day has no events"
        for event in events:
            assert isinstance(event, dict), "invalid schedule event"
            event_id, todo_id = event.get("id"), event.get("todo_id")
            assert isinstance(event_id, str) and event_id.strip() and event_id == todo_id, "schedule event has no matching execution IDs"
            assert event_id not in event_ids, "schedule repeats an execution ID"
            event_ids.add(event_id)
            assert type(event.get("duration_minutes")) is int and event["duration_minutes"] > 0, "schedule event has no valid duration"
            identifier = event.get("transaction_id")
            assert type(identifier) is int, "schedule contains non-Dongzhou transaction IDs"
            if 10001 <= identifier <= 10009:
                extra = event.get("extra_data")
                assert (
                    event.get("type") == "temp"
                    and event.get("transaction_type") == "temp"
                    and event_id.startswith("temp_event:")
                    and isinstance(extra, dict)
                    and extra.get("source") == "event_report"
                    and isinstance(extra.get("event_id"), str)
                    and extra["event_id"].startswith("dongzhou-")
                ), "schedule contains an unbound temporary transaction"
                temporary_transaction_ids.add(identifier)
            else:
                assert 9100101 <= identifier <= 9100112, "schedule contains non-Dongzhou transaction IDs"
            transaction_ids.add(identifier)
            event_count += 1
    text = json.dumps(data, ensure_ascii=False)
    foreign_game_patterns = (
        r"机体",
        r"银河币",
        r"飞船",
        r"(?:普通|困难|精英|挑战|每日|组队)天关",
        r"天关(?:副本|关卡|奖励|挑战|首领)",
    )
    assert not any(re.search(pattern, text) for pattern in foreign_game_patterns), "schedule contains another game's content"
    return {"hero": "ZuoRu", "days": len(days), "events": event_count,
            "transactionIds": sorted(transaction_ids),
            "temporaryTransactionIds": sorted(temporary_transaction_ids),
            "dongzhouContentVerified": True}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8780")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    checks = []

    def check(name, action):
        try:
            detail = action()
        except Exception as error:
            # 不输出响应正文、Cookie、凭据或上游请求载荷。
            checks.append({"name": name, "result": "FAIL", "reason": str(error) if isinstance(error, AssertionError) else type(error).__name__})
        else:
            checks.append({"name": name, "result": "PASS", "detail": detail})

    with httpx.Client(base_url=args.url, timeout=45, follow_redirects=False) as client:
        def request(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            assert response.is_success, f"{path}: HTTP {response.status_code}"
            body = response.json()
            return body.get("data", body) if body.get("success") is True else body

        def health():
            body = request("GET", "/health/ready")
            four_service_delivery.validate_gateway_readiness(body)
            return {
                "status": body["status"],
                "requiredServices": body["requiredServices"],
            }

        check("upstream_readiness", health)
        def guest():
            result = request("POST", "/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())})
            assert result.get("playerId"), "guest session has no player identity"
            return True
        check("guest_session", guest)

        def source_provenance():
            status = request("GET", "/api/dongzhou/v1/integration/status")
            return four_service_delivery.validate_live_status(
                status,
                four_service_delivery.expected_source_seal(),
            )

        check("four_service_source_provenance", source_provenance)

        def organization_inventory():
            body = request("GET", "/api/dongzhou/v1/organization/inventory")
            assert body.get("organizationId"), "organization inventory has no organization identity"
            assert str(body.get("gameServerId")) == "91001", "organization inventory crossed game-server boundary"
            assert type(body.get("revision")) is int and body["revision"] > 0, "organization inventory has no valid revision"
            accounts = body.get("accounts")
            assert isinstance(accounts, list), "organization inventory accounts are invalid"
            resource_keys = []
            for account in accounts:
                assert isinstance(account, dict), "organization inventory account is invalid"
                resource_key = account.get("resourceKey")
                assert isinstance(resource_key, str) and resource_key.strip(), "organization inventory account has no resource key"
                assert type(account.get("balance")) is int and account["balance"] >= 0, "organization inventory account has an invalid balance"
                assert type(account.get("version")) is int and account["version"] > 0, "organization inventory account has an invalid version"
                resource_keys.append(resource_key)
            assert len(resource_keys) == len(set(resource_keys)), "organization inventory repeats a resource account"
            return {"revision": body["revision"], "accounts": len(accounts), "resourceKeys": resource_keys}

        check("organization_inventory", organization_inventory)

        def save_roundtrip():
            path = "/api/dongzhou/v1/save"
            previous = request("GET", path)
            payload = {"integrationValidation": str(uuid4()), "completed": []}
            submitted = {
                **payload,
                "sourceProvenance": {"digest": "0" * 64, "services": {}},
            }
            written = request(
                "PUT",
                path,
                json={"expected_version": previous["version"], "payload": submitted},
            )
            restored = request("GET", path)["payload"]
            receipt = restored.get("sourceProvenance")
            detail = four_service_delivery.validate_source_provenance_receipt(receipt)
            business_payload = {
                key: value for key, value in restored.items() if key != "sourceProvenance"
            }
            assert (
                business_payload == payload
            ), "save business payload did not round trip"
            assert (
                written["payload"].get("sourceProvenance") == receipt
            ), "save response and readback provenance differ"
            stale = client.put(path, json={"expected_version": previous["version"], "payload": {}})
            assert stale.status_code == 409, "stale save did not return 409"
            with httpx.Client(base_url=args.url, timeout=15) as other:
                other.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}).raise_for_status()
                isolated = other.get(path)
                isolated.raise_for_status()
                isolated_save = isolated.json()
                assert isinstance(isolated_save.get("payload"), dict) and "version" in isolated_save, "other player save response is invalid"
                assert "integrationValidation" not in isolated_save["payload"], "save leaked to another player"
            return {
                "version": written["version"],
                "conflict": 409,
                "playerIsolation": True,
                "sourceSealDigest": detail["sourceSealDigest"],
            }

        check("save_roundtrip_and_isolation", save_roundtrip)

        for stage_id in ("01", "03b", "108"):
            def stage(stage_id=stage_id):
                body = request("GET", f"/api/dongzhou/v1/knowledge/stages/{stage_id}")
                items = body.get("results", [])
                assert body.get("mode") == "connected" and items, "no published stage knowledge"
                assert all(item.get("stageId") == stage_id and item.get("id", "").startswith("dongzhou_stage_") for item in items), "knowledge crossed stage or game boundary"
                return {"count": len(items), "ids": [item["id"] for item in items]}
            check(f"published_stage_{stage_id}", stage)

        def search():
            body = request("POST", "/api/dongzhou/v1/knowledge/search", json={"query": "杜伯 东郊索命", "limit": 3})
            assert body.get("mode") == "connected" and body.get("results"), "search did not return published knowledge"
            return {"count": len(body["results"])}
        check("ai_knowledge_search", search)

        def npc_state():
            body = request("GET", "/api/dongzhou/v1/npcs/ZuoRu/state")
            for key in ("emotion", "affection", "relationships"):
                assert body.get(key, {}).get("code") in (0, 200, "0", "200"), f"{key} business request failed"
            return {
                "hero": "ZuoRu",
                "components": 3,
                "execution": validate_npc_execution(body.get("execution")),
            }
        check("npc_state", npc_state)

        def npc_schedule():
            body = request("GET", "/api/dongzhou/v1/npcs/ZuoRu/schedule")
            return validate_dongzhou_schedule(body.get("schedule", {}))
        check("npc_schedule", npc_schedule)

    report = {"scope": "live_read_and_save_smoke_not_full_production_acceptance",
              "at": datetime.now(timezone.utc).isoformat(), "url": args.url,
              "result": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL", "checks": checks}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
