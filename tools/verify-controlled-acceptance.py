"""Controlled live acceptance. Preparation is local; mutations require explicit modes.
Never reopens old tasks or retries an uncertain forced plan generation.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from uuid import uuid4
import httpx

spec = importlib.util.spec_from_file_location("live_acceptance", Path(__file__).with_name("verify-live-integration.py"))
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def write_journal(path, state):
    temporary = path.with_suffix(".pending")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def get_json(client, method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def fingerprint(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def schedule_action(client, state, journal, regenerate=False):
    current = get_json(client, "GET", "/api/dongzhou/v1/npcs/ZuoRu/schedule")["schedule"]
    digest = fingerprint(current.get("data", {}))
    try:
        detail = smoke.validate_dongzhou_schedule(current)
    except (AssertionError, TypeError, ValueError, KeyError):
        detail = None
    attempt = state.get("scheduleAttempt")
    if detail is not None:
        changed = bool(attempt and digest != attempt["before"])
        if attempt and not changed:
            return {"phase": "schedule", "state": "unverified_plan_unchanged"}
        state["scheduleVerified"] = {"fingerprint": digest, "changed": changed}
        write_journal(journal, state)
        return {"phase": "schedule", "state": "verified", "changed": changed, **detail}
    if attempt or not regenerate:
        return {"phase": "schedule", "state": "await_readback_no_resend" if attempt else "domain_validation_failed"}
    # The API has no idempotency key. Persist intent BEFORE its single external POST.
    state["scheduleAttempt"] = {"before": digest, "state": "send_unknown"}
    write_journal(journal, state)
    try:
        response = get_json(client, "POST", "/api/dongzhou/v1/npcs/ZuoRu/schedule", json={"force_regenerate": True})
        state["scheduleAttempt"]["responseCode"] = response.get("schedule", {}).get("code")
        state["scheduleAttempt"]["state"] = "response_received_readback_required"
        write_journal(journal, state)
    except Exception:
        # Timeout/error is not evidence that the Actor did not commit a plan.
        return {"phase": "schedule", "state": "send_unknown_read_only_followup"}
    return schedule_action(client, state, journal)


def task_snapshot(client, task_id):
    result = get_json(client, "GET", "/api/dongzhou/v1/organization/tasks/" + task_id)["result"]
    return result.get("data", result)


def prepare_predecessors(paths):
    if not paths or len({path.resolve() for path in paths}) != len(paths):
        raise RuntimeError("Specify all predecessor journals once; at least one is required")
    prior = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    installations = [item["installation"] for item in prior]
    tasks = [item["remoteTask"] for item in prior]
    if len(set(installations)) != len(prior) or len(set(tasks)) != len(prior):
        raise RuntimeError("Duplicate predecessor identity or remote task")
    return [{"installation": item["installation"], "remoteTask": item["remoteTask"]} for item in prior]


def verify_predecessors(client, state):
    if state["installation"] in {old["installation"] for old in state["predecessors"]}:
        raise RuntimeError("Acceptance installation must not reuse a predecessor identity")
    for old in state["predecessors"]:
        get_json(client, "POST", "/api/dongzhou/v1/sessions/guest", json={"installation_id": old["installation"]})
        if task_snapshot(client, old["remoteTask"])["state"] != "INVALIDATED":
            raise RuntimeError("Predecessor is not invalidated; do not dispatch")


def order_action(client, state, journal, mode):
    if mode == "order-submit" and not state.get("remoteTask"):
        state["orderAttempted"] = True
        write_journal(journal, state)
        # Network retries use exactly the frozen request and request ID.
        accepted = get_json(client, "POST", "/api/dongzhou/v1/organization/tasks", json=state["orderRequest"])
        if accepted.get("state") != "ACCEPTED" or not accepted.get("taskId"):
            return {"phase": "order", "state": accepted.get("state", "unknown")}
        state["remoteTask"] = accepted["taskId"]
        write_journal(journal, state)
    if not state.get("remoteTask"):
        return {"phase": "order", "state": "not_submitted"}
    task = task_snapshot(client, state["remoteTask"])
    if mode == "report" and not state.get("reportVerified"):
        if task.get("state") != "IN_PROGRESS":
            return {"phase": "report", "state": "not_executing_no_report", "taskState": task.get("state")}
        clock = get_json(client, "POST", "/api/v1/QueryGameTimeAndTimeScale", json={"serverID": state.get("gameServerId", "91001")})
        if datetime.fromisoformat(clock["virtualTime"]).date() != date(771, 1, 31):
            raise RuntimeError("Report requires the verified 0771-01-31 clock date; inspect current timeline, no write performed")
        saved = get_json(client, "GET", "/api/dongzhou/v1/save")
        payload = {"integrationValidation": True, "campaignResources": {"provisions": 92}, "organization": {"month": 2,
            "members": [{"id": "DuBo", "name": "杜伯", "office": "司马", "loyalty": 80, "fatigue": 0}, {"id": "ZuoRu", "name": "左儒", "office": "司徒", "loyalty": 90, "fatigue": 7}],
            "tasks": [{"id": state["localTask"], "type": "supply", "name": "转运军粮", "status": "active", "assigneeId": "ZuoRu", "assigneeName": "左儒", "stageId": "01", "stageTitle": "东郊索命", "startedMonth": 1, "dueMonth": 2, "cost": 8, "remoteResult": state["remoteTask"]}]}}
        if saved.get("payload") != payload:
            if state.get("reportAttempted"):
                raise RuntimeError("Report save outcome is uncertain; inspect instead of replay")
            state["reportAttempted"] = True
            write_journal(journal, state)
            get_json(client, "PUT", "/api/dongzhou/v1/save", json={"expected_version": saved["version"], "payload": payload})
        if get_json(client, "GET", "/api/dongzhou/v1/save")["payload"] != payload:
            raise RuntimeError("Report save readback mismatch")
        state["reportVerified"] = True
        write_journal(journal, state)
        task = task_snapshot(client, state["remoteTask"])
    return {"phase": "order", "state": task.get("state"), "finalResult": task.get("final_result"), "reportVerified": bool(state.get("reportVerified"))}


def deployment_gate(args):
    if not args.expected_ainpc_image or not args.expected_orgflow_image:
        raise RuntimeError("Explicit deployed image expectations are required before writes")
    names = ["ainpc-v2-gateway-dev", "ainpc-v2-global-dev"] + [f"ainpc-v2-business-{n}-dev" for n in range(6)]
    for name in names + ["org-flow-engine-dev-api-1", "org-flow-engine-dev-worker-1"]:
        row = json.loads(subprocess.check_output(["docker", "inspect", name], text=True))[0]
        expected = args.expected_ainpc_image if name in names else args.expected_orgflow_image
        if row["Config"]["Image"] != expected:
            raise RuntimeError("Deployment image mismatch; no business write performed")
        if name.endswith("-worker-1"):
            verify_worker_activity(row, name)
        elif row["State"].get("Health", {}).get("Status") != "healthy":
            raise RuntimeError("Deployment is not healthy")
        if name == names[0]:
            if "AINPC_CONST_CSV_SCHEDULE_TRANSACTIONS=app2/resources/transaction/dongzhou_schedule_transactions.csv" not in row["Config"]["Env"]:
                raise RuntimeError("Gateway schedule catalog is not configured")


def verify_worker_activity(row, name):
    # The worker role has no HTTP or Docker health probe. A current loop event is
    # only execution evidence, never a claim that delivery or a task succeeded.
    if not row["State"].get("Running") or row.get("RestartCount", 0):
        raise RuntimeError("Worker is stopped or has restarted; inspect before acceptance")
    started = datetime.fromisoformat(row["State"]["StartedAt"].replace("Z", "+00:00"))
    since = max(started, datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
    observed = subprocess.run(["docker", "logs", "--since", since, name], capture_output=True, text=True, encoding="utf-8")
    if observed.returncode or "organization_virtual_task_worker_phase_deferred" not in observed.stdout + observed.stderr:
        raise RuntimeError("No recent worker loop evidence; readiness remains unverified")


def main():
    if not __debug__:
        raise RuntimeError("Optimized Python disables schedule validation assertions; use ordinary Python")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "schedule-read", "schedule-regenerate", "order-read", "order-submit", "report"])
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8780")
    parser.add_argument("--prior-journal", type=Path, action="append", default=[])
    parser.add_argument("--expected-ainpc-image")
    parser.add_argument("--expected-orgflow-image")
    parser.add_argument("--game-server-id", default="91001")
    args = parser.parse_args()
    with locked(args.journal):
        if args.mode == "prepare":
            if args.journal.exists():
                raise RuntimeError("Journal already exists; preserve its request identities")
            prior = prepare_predecessors(args.prior_journal)
            installation = str(uuid4())
            if installation in {item["installation"] for item in prior}:
                raise RuntimeError("Generated installation collides with predecessor")
            state = {"gameServerId": args.game_server_id, "installation": installation, "localTask": "acceptance-" + str(uuid4()), "predecessors": prior,
                "orderRequest": {"client_request_id": str(uuid4()), "task_type": "supply", "assignee_hero_id": "ZuoRu", "stage_id": "01", "stage_title": "东郊索命", "brief": "暂态来源修复后的独立军粮转运验收，按真实流程领命和复命。", "parameters": {"resource_units": 8, "assignee_name": "左儒"}}}
            write_journal(args.journal, state)
            print(json.dumps({"state": "prepared", "businessWrites": 0}))
            return
        state = json.loads(args.journal.read_text(encoding="utf-8"))
        if args.mode in {"schedule-regenerate", "order-submit", "report"}:
            deployment_gate(args)
        with httpx.Client(base_url=args.url, timeout=180, follow_redirects=False) as client:
            if args.mode == "order-submit" and not state.get("remoteTask"):
                verify_predecessors(client, state)
            get_json(client, "POST", "/api/dongzhou/v1/sessions/guest", json={"installation_id": state["installation"]})
            if args.mode.startswith("schedule-"):
                summary = schedule_action(client, state, args.journal, args.mode == "schedule-regenerate")
            else:
                summary = order_action(client, state, args.journal, args.mode)
            print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
