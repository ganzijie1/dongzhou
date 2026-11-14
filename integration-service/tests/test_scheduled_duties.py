from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid4, uuid5

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.upstreams import UpstreamUnavailable


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
        self.active_task_id = "00000000-0000-4000-8000-000000000099"

    async def health(self):
        return {name: {"online": True} for name in ("orgFlow", "aiNpc", "knowledge")}

    async def close(self):
        pass

    async def query_organization_scheduled_task_rules(self, payload):
        rules = [
            {
                "rule": rule,
                "latest_trigger": (
                    {
                        "state": "SKIPPED",
                        "failure_code": "duplicate_active_task",
                        "task_id": self.active_task_id,
                    }
                    if rule.get("template", {}).get("task_code")
                    == "dongzhou.intelligence"
                    else None
                ),
            }
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

    async def get_virtual_task(self, organization_id, task_id):
        assert task_id == self.active_task_id
        return {
            "data": {
                "task_id": task_id,
                "organization_id": organization_id,
                "task_code": "dongzhou.intelligence",
                "title": "东周朝廷月例察访",
                "state": "IN_PROGRESS",
                "responsible_member_id": "e3419e13-7498-5a6b-9259-a2c30aeb5a19",
                "final_result": None,
                "updated_at": "2026-11-13T10:00:00Z",
            }
        }

    async def get_virtual_task_trace(self, organization_id, task_id):
        assert task_id == self.active_task_id
        return {
            "data": {
                "task": {
                    "task_id": task_id,
                    "organization_id": organization_id,
                    "state": "IN_PROGRESS",
                    "version": "2",
                    "supplement_count": 0,
                    "execution_exception": None,
                },
                "confirmations": [],
                "timeline": [
                    {
                        "sequence_no": "1",
                        "occurred_at": "2026-11-13T09:00:00Z",
                        "entry_type": "TASK_CREATED",
                        "reference_id": task_id,
                        "case_id": None,
                        "state_code": "GENERATED",
                        "reason_code": None,
                    }
                ],
            }
        }

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
        task = client.get(
            "/api/dongzhou/v1/organization/tasks/" + upstreams.active_task_id
        )

    assert first.status_code == 200
    assert first.json()["state"] == "ACTIVE"
    assert first.json()["managerHeroId"] == "DuBo"
    assert first.json()["workerHeroId"] == "ZuoRu"
    assert first.json()["taskCode"] == "dongzhou.intelligence"
    assert second.json()["activeTask"] == {
        "taskId": upstreams.active_task_id,
        "title": "东周朝廷月例察访",
        "state": "IN_PROGRESS",
        "finalResult": None,
        "updatedAt": "2026-11-13T10:00:00Z",
        "adopted": True,
    }
    assert task.status_code == 200
    assert task.json()["assigneeHeroId"] == "ZuoRu"
    assert task.json()["organizationTrace"]["kernel"]["module"] == (
        "dongzhou_organization_task_trace"
    )
    assert second.json()["ruleId"] == first.json()["ruleId"]
    assert len(upstreams.create_calls) == 1
    assert len(upstreams.status_calls) == 1
    assert upstreams.status_calls[0]["status"] == "DISABLED"
    assert len(upstreams.schedule_append_calls) == 1
    assert upstreams.schedule_append_calls[0][2]["time_slot"] == "14:00-14:45"
    assert upstreams.create_calls[0]["parameters"]["assignee_hero_id"] == "ZuoRu"


def test_scheduled_duty_maps_ainpc_schedule_outage_to_retryable_503(tmp_path):
    class UnavailableScheduleUpstreams(ScheduledDutyUpstreams):
        async def npc_schedule(self, npc_id):
            raise UpstreamUnavailable("AINPC schedule is offline")

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

    with TestClient(
        build_application(settings, upstreams=UnavailableScheduleUpstreams())
    ) as client:
        session = client.post(
            "/api/dongzhou/v1/sessions/guest",
            json={"installation_id": str(uuid4())},
        )
        assert session.status_code == 200
        response = client.get(
            "/api/dongzhou/v1/organization/scheduled-duties"
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ainpc_schedule_unavailable"
