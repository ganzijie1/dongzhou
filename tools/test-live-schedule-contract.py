"""真实冒烟的日程门禁回归，不连接服务、不生成 NPC 日程。"""
import copy
import importlib.util
from pathlib import Path
import unittest
from datetime import date, timedelta

spec = importlib.util.spec_from_file_location("live_smoke", Path(__file__).with_name("verify-live-integration.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ScheduleAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.schedule = {"code": 200, "data": {"start_date": "0771-01-01", "end_date": "0771-03-31", "schedules": [
            {"day": day, "date": (date(771, 1, 1) + timedelta(days=day-1)).isoformat(),
             "events": [{"id": f"event-{day}", "todo_id": f"event-{day}",
                         "duration_minutes": 30, "transaction_id": 9100101, "name": "军粮转运"}]}
            for day in range(1, 91)]}}

    def test_dongzhou_plan_passes(self):
        result = module.validate_dongzhou_schedule(self.schedule)
        self.assertEqual(result["events"], 90)
        self.assertTrue(result["dongzhouContentVerified"])

    def test_old_plan_does_not_pass_on_day_count(self):
        self.schedule["data"]["schedules"][0]["events"][0]["transaction_id"] = 200
        with self.assertRaisesRegex(AssertionError, "non-Dongzhou"):
            module.validate_dongzhou_schedule(self.schedule)

    def test_other_game_text_fails_even_with_correct_ids(self):
        for field in ("description", "reward_desc"):
            with self.subTest(field=field):
                schedule = copy.deepcopy(self.schedule)
                schedule["data"][field] = "奖励银河币"
                with self.assertRaisesRegex(AssertionError, "another game's"):
                    module.validate_dongzhou_schedule(schedule)

        schedule = copy.deepcopy(self.schedule)
        schedule["data"]["description"] = "完成普通天关挑战"
        with self.assertRaisesRegex(AssertionError, "another game's"):
            module.validate_dongzhou_schedule(schedule)

    def test_daytime_key_phrase_is_not_misclassified_as_tianguan_content(self):
        self.schedule["data"]["schedules"][-1]["rationale"] = "严格集中在白天关键节点"
        result = module.validate_dongzhou_schedule(self.schedule)
        self.assertTrue(result["dongzhouContentVerified"])

    def test_missing_duplicate_and_empty_days_fail(self):
        for change in ("short", "duplicate", "empty_events"):
            with self.subTest(change=change):
                schedule = copy.deepcopy(self.schedule)
                days = schedule["data"]["schedules"]
                if change == "short":
                    days.pop()
                elif change == "duplicate":
                    days[-1]["day"] = 89
                else:
                    days[-1]["events"] = []
                with self.assertRaises(AssertionError):
                    module.validate_dongzhou_schedule(schedule)

    def test_business_error_fails(self):
        self.schedule["code"] = 500
        with self.assertRaisesRegex(AssertionError, "business request failed"):
            module.validate_dongzhou_schedule(self.schedule)

    def test_repeated_dates_and_incorrect_end_date_fail(self):
        for change in ("repeated", "end"):
            with self.subTest(change=change):
                schedule = copy.deepcopy(self.schedule)
                if change == "repeated":
                    schedule["data"]["schedules"][-1]["date"] = "0771-01-01"
                else:
                    schedule["data"]["end_date"] = "0771-04-01"
                with self.assertRaisesRegex(AssertionError, "date"):
                    module.validate_dongzhou_schedule(schedule)

    def test_unexecutable_or_duplicate_events_fail(self):
        for field, value in (("id", None), ("todo_id", "different"), ("duration_minutes", 0)):
            with self.subTest(field=field):
                schedule = copy.deepcopy(self.schedule)
                schedule["data"]["schedules"][0]["events"][0][field] = value
                with self.assertRaises(AssertionError):
                    module.validate_dongzhou_schedule(schedule)
        self.schedule["data"]["schedules"][-1]["events"] = copy.deepcopy(self.schedule["data"]["schedules"][0]["events"])
        with self.assertRaisesRegex(AssertionError, "repeats"):
            module.validate_dongzhou_schedule(self.schedule)


if __name__ == "__main__":
    unittest.main()
