#!/usr/bin/env python3

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("serve-dongzhou-integrated.py")
SPEC = importlib.util.spec_from_file_location("dongzhou_bridge", MODULE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"DONGZHOU_ORGFLOW_ORG_ID": "court-01", "DONGZHOU_ORGFLOW_TOKEN": "test-token"}, clear=False)
        self.env.start()
        self.services = bridge.Services()

    def tearDown(self):
        self.env.stop()

    def test_local_chinese_search(self):
        result = self.services.local_search("东郊索命 杜伯", 3)
        self.assertEqual(result["mode"], "local")
        self.assertEqual(result["results"][0]["stageId"], "01")

    def test_health_reports_configured_organization(self):
        with patch.object(self.services, "request", return_value={"ok": True}):
            result = self.services.health()
        self.assertTrue(result["orgFlow"]["online"])
        self.assertTrue(result["aiNpc"]["online"])
        self.assertTrue(result["knowledge"]["online"])
        self.assertEqual(result["organizationId"], "court-01")

    def test_orgflow_task_contract(self):
        captured = {}

        def fake_request(url, method="GET", payload=None, headers=None, timeout=2.5):
            captured.update(url=url, method=method, payload=payload, headers=headers)
            return {"data": {"task_id": "remote-task"}}

        with patch.object(self.services, "request", side_effect=fake_request):
            result = self.services.forward_task({"title": "转运军粮", "description": "东郊索命", "assignee_id": "DuBo", "difficulty": 2, "resource_units": 8, "reward_units": 11})
        self.assertTrue(result["accepted"])
        self.assertTrue(captured["url"].endswith("/api/v1/organizations/court-01/tasks"))
        self.assertEqual(captured["payload"]["task_type"], "TEMPORARY")
        self.assertEqual(captured["payload"]["source"], "STORY")
        self.assertEqual(captured["payload"]["assignee_id"], "DuBo")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-token")
        self.assertIn("Idempotency-Key", captured["headers"])


if __name__ == "__main__":
    unittest.main()
