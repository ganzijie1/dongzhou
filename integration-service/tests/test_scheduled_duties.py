from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid4, uuid5

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings


class ScheduledDutyUpstreams:
    def __init__(self) -> None:
        legacy_rule_id = uuid5(
            NAMESPACE_URL,
            "dongzhou:91001:scheduled-duty:monthly-patrol:v1",
        )
        self.rules = [
            {
                "rule_id": str(legacy_rule_id),
                "state": "ACTIVE",
                "version": 1,
                "frequency": "DAILY",
                "trigger_minute": 780,
                "template": {"task_code": "dongzhou.patrol"},
            }
        ]
        self.create_calls = []
        self.status_calls = []
        self.schedule_append_calls = []
        self.schedule_events = {}

    async def health(self):
        return {name: {"online": True} for name in ("orgFlow", "aiNpc", "knowledge")}

    async def close(self):
        pass

    async def query_organization_scheduled_task_rules(self, payload):
        rules = [
            {"rule": rule, "latest_trigger": None}
            for rule in self.rules
        ]
        return {"data": {"rules": rules}}

    async def register_organization_scheduled_task_rule(self, payload):
        self.create_calls.append(payload)
        rule = {
            "rule_id": payload["rule_id"],
            "state": "ACTIVE",
            "frequency": payload["frequency"],
            "trigger_minute": payload["trigger_minute"],
            "template": {"task_code": payload["task_code"]},
        }
        self.rules.append(rule)
        return {"data": {"rule": rule}}

    async def update_organization_scheduled_task_rule_status(self, payload):
        self.status_calls.append(payload)
        rule = next(
            rule for rule in self.rules if rule["rule_id"] == payload["rule_id"]
        )
        rule["state"] = payload["status"]
        rule["version"] += 1
        return {"data": {"rule": rule}}

    async def npc_schedule(self, npc_id):
        is_worker = str(npc_id) == "5445994056112890376"
        return {
            "code": 200,
            "data": {
                "schedules": [
                    {
                        "date": "0771-01-01",
                        "events": (
                            [{"time_slot": "14:00-14:45"}] if is_worker else []
                        )
                        + self.schedule_events.get(str(npc_id), []),
                    }
                ]
            },
        }

    async def generate_npc_schedule(self, npc_id, force_regenerate):
        return {"code": 200, "data": {"npc_id": str(npc_id)}}

    async def append_npc_schedule_duty(self, npc_id, *, date, activity):
        self.schedule_append_calls.append((npc_id, date, activity))
        self.schedule_events.setdefault(str(npc_id), []).append(activity)
        return {"date": date, "events": [activity]}


def test_scheduled_duty_is_registered_once_and_returned(tmp_path):
    with patch.dict(
        "os.environ",
        {
            "DONGZHOU_ENV": "test",
            "DONGZHOU_WEB_ROOT": str(tmp_path),
            "DONGZHOU_DATABASE_PATH": str(tmp_path / "save.db"),
            "DONGZHOU_GAME_SERVER_ID": "91001",
            "DONGZHOU_AINPC_GAME_SERVER_ID": "91001",
            "DONGZHOU_ORGFLOW_ORG_ID": "596354f7-c343-5c78-958d-757a9e58fde6",
            "DONGZHOU_ORGFLOW_HERO_MEMBERS": (
                "DuBo=bb531833-924f-5a59-a148-5d33e3fbface,"
                "ZuoRu=e3419e13-7498-5a6b-9259-a2c30aeb5a19"
            ),
        },
        clear=True,
    ):
        settings = Settings.from_env()
    upstreams = ScheduledDutyUpstreams()
    route = "/api/dongzhou/v1/organization/scheduled-duties"

    with TestClient(build_application(settings, upstreams=upstreams)) as client:
        assert client.get(route).status_code == 401
        session = client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        )
        assert session.status_code == 200
        first = client.get(route)
        second = client.get(route)

    assert first.status_code == 200
    assert first.json()["state"] == "ACTIVE"
    assert first.json()["managerHeroId"] == "DuBo"
    assert first.json()["workerHeroId"] == "ZuoRu"
    assert first.json()["taskCode"] == "dongzhou.intelligence"
    assert second.json()["ruleId"] == first.json()["ruleId"]
    assert len(upstreams.create_calls) == 1
    assert len(upstreams.status_calls) == 1
    assert upstreams.status_calls[0]["status"] == "DISABLED"
    assert len(upstreams.schedule_append_calls) == 1
    assert upstreams.schedule_append_calls[0][2]["time_slot"] == "14:00-14:45"
    assert upstreams.create_calls[0]["parameters"]["assignee_hero_id"] == "ZuoRu"
