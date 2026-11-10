"""No-network safety tests for controlled live acceptance journals."""
import copy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("controlled", Path(__file__).with_name("verify-controlled-acceptance.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def plan():
    start = date(771, 1, 1)
    return {"code": 200, "data": {"start_date": start.isoformat(), "end_date": (start + timedelta(days=89)).isoformat(), "schedules": [
        {"day": n, "date": (start + timedelta(days=n-1)).isoformat(), "events": [{"id": str(n), "todo_id": str(n), "duration_minutes": 30, "transaction_id": 9100101, "name": "听政"}]} for n in range(1, 91)]}}


class Client:
    def __init__(self, handler):
        self.handler, self.calls = handler, []
    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        data = self.handler(method, path, kwargs)
        class Response:
            def raise_for_status(self): pass
            def json(self): return data
        return Response()
    def __enter__(self): return self
    def __exit__(self, *_): pass


class ControlledTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "private.json"
        self.state = {}

    def test_prepare_accepts_all_three_unique_predecessors(self):
        paths = []
        for n in range(3):
            path = Path(self.temp.name) / f'prior-{n}.json'
            path.write_text(json.dumps({"installation": f'old-{n}', "remoteTask": f'task-{n}'}))
            paths.append(path)
        prior = module.prepare_predecessors(paths)
        self.assertEqual(len(prior), 3)
        with self.assertRaises(RuntimeError): module.prepare_predecessors([])
        with self.assertRaises(RuntimeError): module.prepare_predecessors([paths[0], paths[0]])
        paths[2].write_text(paths[0].read_text())
        with self.assertRaises(RuntimeError): module.prepare_predecessors(paths)

    def test_any_noninvalidated_predecessor_blocks_dispatch(self):
        for bad in range(3):
            state = {"installation": 'new-installation', "predecessors": [{"installation": f'old-{n}', "remoteTask": f'task-{n}'} for n in range(3)]}
            module.write_journal(self.path, state)
            def handle(method, path, kwargs):
                if path.endswith('/sessions/guest'): return {}
                return {"result": {"state": "IN_PROGRESS" if path.endswith(f'task-{bad}') else "INVALIDATED"}}
            client = Client(handle)
            with patch.object(sys, 'argv', ['controlled', 'order-submit', '--journal', str(self.path)]), patch.object(module, 'deployment_gate'), patch.object(module.httpx, 'Client', return_value=client):
                with self.assertRaisesRegex(RuntimeError, 'not invalidated'):
                    module.main()
            self.assertFalse(any(method == 'POST' and path.endswith('/organization/tasks') for method, path, _ in client.calls))

    def test_reusing_predecessor_installation_is_rejected_before_requests(self):
        client = Client(lambda *_: {})
        with self.assertRaisesRegex(RuntimeError, 'reuse'):
            module.verify_predecessors(client, {"installation": 'old', "predecessors": [{"installation": 'old', "remoteTask": 'task'}]})
        self.assertEqual(client.calls, [])

    def test_force_timeout_is_never_resent(self):
        old = plan()
        old["data"]["schedules"][0]["events"][0]["transaction_id"] = 200
        def handle(method, path, kwargs):
            if method == "POST":
                self.assertIn("scheduleAttempt", json.loads(self.path.read_text()))
                raise TimeoutError()
            return {"schedule": old}
        client = Client(handle)
        result = module.schedule_action(client, self.state, self.path, True)
        self.assertEqual(result["state"], "send_unknown_read_only_followup")
        restored = json.loads(self.path.read_text())
        result = module.schedule_action(client, restored, self.path, True)
        self.assertEqual(result["state"], "await_readback_no_resend")
        self.assertEqual(sum(method == "POST" for method, _, _ in client.calls), 1)
        client.handler = lambda *_: {"schedule": plan()}
        result = module.schedule_action(client, restored, self.path)
        self.assertEqual(result["state"], "verified")
        self.assertTrue(result["changed"])

    def test_valid_schedule_never_force_regenerated(self):
        client = Client(lambda *_: {"schedule": plan()})
        result = module.schedule_action(client, self.state, self.path, True)
        self.assertEqual(result["state"], "verified")
        self.assertTrue(all(method == "GET" for method, _, _ in client.calls))

    def test_order_retry_uses_frozen_request_and_stops_after_acceptance(self):
        self.state = {"orderRequest": {"client_request_id": "same-id"}}
        attempts = []
        def handle(method, path, kwargs):
            if method == "POST":
                attempts.append(copy.deepcopy(kwargs["json"]))
                if len(attempts) == 1:
                    raise TimeoutError()
                return {"state": "ACCEPTED", "taskId": "one-task"}
            return {"result": {"state": "MEMBER_RESPONSE_PENDING"}}
        client = Client(handle)
        with self.assertRaises(TimeoutError):
            module.order_action(client, self.state, self.path, "order-submit")
        restored = json.loads(self.path.read_text())
        module.order_action(client, restored, self.path, "order-submit")
        module.order_action(client, restored, self.path, "order-submit")
        self.assertEqual(attempts, [{"client_request_id": "same-id"}] * 2)

    def test_terminal_or_waiting_task_never_reports(self):
        for state in ["INVALIDATED", "FAILED", "SUCCEEDED", "MEMBER_RESPONSE_PENDING"]:
            client = Client(lambda *_: {"result": {"state": state}})
            result = module.order_action(client, {"remoteTask": "one-task"}, self.path, "report")
            self.assertEqual(result["state"], "not_executing_no_report")
            self.assertEqual(len(client.calls), 1)

    def test_concurrent_journal_owner_is_rejected(self):
        with module.locked(self.path):
            with self.assertRaises(FileExistsError):
                with module.locked(self.path): pass
        self.assertFalse(self.path.with_suffix(".lock").exists())

    def test_worker_requires_current_execution_evidence(self):
        row = {"State": {"Running": True, "StartedAt": "2026-11-08T20:00:00Z"}, "RestartCount": 0}
        with patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
            with self.assertRaises(RuntimeError):
                module.verify_worker_activity(row, "worker")
        with patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="organization_virtual_task_worker_phase_deferred", stderr="")):
            module.verify_worker_activity(row, "worker")
            row["RestartCount"] = 1
            with self.assertRaises(RuntimeError):
                module.verify_worker_activity(row, "worker")

    def test_report_does_not_advance_shared_clock(self):
        def handle(method, path, kwargs):
            if path.endswith("one-task"):
                return {"result": {"state": "IN_PROGRESS"}}
            return {"virtualTime": "0771-01-30T23:59:00"}
        client = Client(handle)
        with self.assertRaises(RuntimeError):
            module.order_action(client, {"remoteTask": "one-task"}, self.path, "report")
        self.assertFalse(any(method == "PUT" for method, _, _ in client.calls))

    def test_report_later_clock_date_requires_inspection(self):
        def handle(method, path, kwargs):
            if path.endswith("one-task"):
                return {"result": {"state": "IN_PROGRESS"}}
            return {"virtualTime": "0771-02-01T00:00:00"}
        client = Client(handle)
        with self.assertRaisesRegex(RuntimeError, "verified 0771-01-31"):
            module.order_action(client, {"remoteTask": "one-task"}, self.path, "report")
        self.assertFalse(any(path.endswith("/save") for _, path, _ in client.calls))

    def test_clock_request_uses_frozen_server_id_and_legacy_default(self):
        for frozen, expected in [(None, "91001"), ("91002", "91002")]:
            def handle(method, path, kwargs):
                if path.endswith("one-task"):
                    return {"result": {"state": "IN_PROGRESS"}}
                self.assertEqual(method, "POST")
                self.assertTrue(path.endswith("QueryGameTimeAndTimeScale"))
                self.assertEqual(kwargs["json"], {"serverID": expected})
                return {"virtualTime": "0771-02-01T00:00:00"}
            client = Client(handle)
            state = {"remoteTask": "one-task"}
            if frozen is not None:
                state["gameServerId"] = frozen
            with self.assertRaisesRegex(RuntimeError, "verified 0771-01-31"):
                module.order_action(client, state, self.path, "report")
            self.assertEqual(len(client.calls), 2)

    def test_report_unknown_save_does_not_replay(self):
        def handle(method, path, kwargs):
            if path.endswith("one-task"):
                return {"result": {"state": "IN_PROGRESS"}}
            if path.endswith("QueryGameTimeAndTimeScale"):
                return {"virtualTime": "0771-01-31T00:00:00"}
            return {"version": 0, "payload": {}}
        client = Client(handle)
        with self.assertRaises(RuntimeError):
            module.order_action(client, {"remoteTask": "one-task", "localTask": "local", "reportAttempted": True}, self.path, "report")
        self.assertFalse(any(method == "PUT" for method, _, _ in client.calls))

    def test_report_save_reads_back_current_task_without_claiming_settlement(self):
        cloud = {"version": 0, "payload": {}}
        task_reads = 0
        def handle(method, path, kwargs):
            nonlocal task_reads
            if path.endswith("one-task"):
                task_reads += 1
                return {"result": {"state": "IN_PROGRESS", "final_result": None}}
            if path.endswith("QueryGameTimeAndTimeScale"):
                return {"virtualTime": "0771-01-31T00:00:00"}
            if method == "PUT":
                cloud.update(version=1, payload=kwargs["json"]["payload"])
            return copy.deepcopy(cloud)
        client = Client(handle)
        result = module.order_action(client, {"remoteTask": "one-task", "localTask": "local"}, self.path, "report")
        self.assertEqual(task_reads, 2)
        self.assertTrue(result["reportVerified"])
        self.assertEqual(result["state"], "IN_PROGRESS")
        self.assertIsNone(result["finalResult"])
        self.assertEqual(sum(method == "PUT" for method, _, _ in client.calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
