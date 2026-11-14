from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from dongzhou_integration.app import build_application
from dongzhou_integration.config import Settings
from dongzhou_integration.security import stable_player_id
from dongzhou_integration.store import Store


class AdviserUpstreams:
    def __init__(self) -> None:
        self.questions: list[dict] = []
        self.feedback: list[dict] = []
        self.guide_decisions: list[dict] = []
        self.guide_cancellations: list[dict] = []

    async def health(self):
        return {
            "orgFlow": {"online": True},
            "aiNpc": {"online": True},
            "knowledge": {"online": True},
        }

    async def close(self):
        return None

    async def ask_ai_helper(self, payload):
        self.questions.append(payload)
        return {"code": 200, "data": {"taskId": payload["taskId"]}}

    async def stage_knowledge(self, stage_id):
        return [{
            "id": "dongzhou_stage_001",
            "summary": "周郑交质以王子狐与公子忽互为质。",
            "objective": "理解周郑关系。",
            "people": ["周平王", "郑庄公"],
            "sourceDetails": [{"work": "《左传·隐公三年》"}],
        }]

    async def submit_ai_helper_feedback(self, payload):
        self.feedback.append(payload)
        return {"code": 200, "data": {"taskId": payload["taskId"]}}

    async def decide_ai_helper_guide(self, payload):
        self.guide_decisions.append(payload)
        return {"code": 200, "data": {"guideSessionId": payload["guideSessionId"]}}

    async def cancel_ai_helper_guide(self, payload):
        self.guide_cancellations.append(payload)
        return {"code": 200, "data": {"guideSessionId": payload["guideSessionId"]}}


def test_adviser_async_answer_is_isolated_idempotent_and_reviewable() -> None:
    with TemporaryDirectory() as directory, patch.dict(
        "os.environ",
        {
            "DONGZHOU_ENV": "development",
            "DONGZHOU_WEB_ROOT": directory,
            "DONGZHOU_PUBLIC_ORIGIN": "http://testserver",
            "DONGZHOU_DATABASE_PATH": str(Path(directory) / "gateway.sqlite3"),
        },
        clear=True,
    ):
        settings = Settings.from_env()
        upstreams = AdviserUpstreams()
        application = build_application(
            settings,
            store=Store(settings.database_path),
            upstreams=upstreams,
        )
        question_id = uuid4()
        with TestClient(application) as client:
            guest = client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
            player_id = UUID(guest.json()["playerId"])
            asked = client.post(
                "/api/dongzhou/v1/adviser/questions",
                json={
                    "client_request_id": str(question_id),
                    "question": "本关的关键人物是谁？",
                    "stage_id": "001",
                    "stage_title": "周郑交质",
                    "stage_index": 1,
                },
            )
            assert asked.status_code == 200, asked.text
            assert asked.json()["state"] == "PROCESSING"
            assert upstreams.questions[0]["taskId"] == str(question_id)
            context = upstreams.questions[0]["playerState"]["tasks"][0]
            assert context["authority"] == "knowledge-jizhan-published-aku"
            assert context["people"] == ["周平王", "郑庄公"]
            assert client.get(
                f"/api/dongzhou/v1/adviser/questions/{question_id}"
            ).json()["state"] == "PROCESSING"

            callback = {
                "game_server_id": int(settings.game_server_id),
                "player_id": stable_player_id(settings.ainpc_game_server_id, player_id),
                "answer": "关键人物是周平王与郑庄公。",
                "task_id": str(question_id),
                "chat_id": f"dongzhou-adviser-{question_id}",
                "intent_type": "role",
                "guide_session_id": "not-applicable-to-tactics",
                "guide_started": False,
                "reason": "",
            }
            loading = client.post(
                "/api/v2/NDLLMSendLittleElfMessage",
                json={**callback, "answer": "正在查阅史料……", "intent_type": "loading"},
            )
            assert loading.status_code == 200
            assert client.get(
                f"/api/dongzhou/v1/adviser/questions/{question_id}"
            ).json()["state"] == "PROCESSING"
            mismatch = client.post(
                "/api/v2/NDLLMSendLittleElfMessage",
                json={**callback, "player_id": 1},
            )
            assert mismatch.json() == {
                "success": False,
                "errorCode": "adviser_player_mismatch",
            }
            delivered = client.post(
                "/api/v2/NDLLMSendLittleElfMessage", json=callback
            )
            assert delivered.status_code == 200, delivered.text
            assert delivered.json()["success"] is True
            replayed = client.post(
                "/api/v2/NDLLMSendLittleElfMessage", json=callback
            )
            assert replayed.json()["talkId"] == delivered.json()["talkId"]
            conflict = client.post(
                "/api/v2/NDLLMSendLittleElfMessage",
                json={**callback, "answer": "不同答案"},
            )
            assert conflict.status_code == 409

            answer = client.get(
                f"/api/dongzhou/v1/adviser/questions/{question_id}"
            )
            assert answer.json()["state"] == "ANSWERED"
            assert answer.json()["guideIgnored"] is False
            assert answer.json()["guide"] == {
                "available": True,
                "sessionId": "not-applicable-to-tactics",
                "status": "AVAILABLE",
                "started": False,
            }

            guide_action_id = uuid4()
            accepted = client.post(
                f"/api/dongzhou/v1/adviser/questions/{question_id}/guide",
                json={"action_id": str(guide_action_id), "decision": "ACCEPT"},
            )
            assert accepted.status_code == 200, accepted.text
            assert accepted.json()["state"] == "ACCEPTED"
            assert accepted.json()["guide"]["decision"] == "ACCEPT"
            assert accepted.json()["guide"]["kernel"]["module"] == "dongzhou_adviser_guide"
            assert accepted.json()["guide"]["kernel"]["state"] == "SEALED"
            assert upstreams.guide_decisions == [{
                "taskId": str(question_id),
                "gameServerId": settings.game_server_id,
                "playerId": str(stable_player_id(settings.ainpc_game_server_id, player_id)),
                "chatId": f"dongzhou-adviser-{question_id}",
                "guideSessionId": "not-applicable-to-tactics",
                "confirm": True,
            }]
            replayed_guide = client.post(
                f"/api/dongzhou/v1/adviser/questions/{question_id}/guide",
                json={"action_id": str(guide_action_id), "decision": "ACCEPT"},
            )
            assert replayed_guide.json()["replayed"] is True
            duplicate_decision = client.post(
                f"/api/dongzhou/v1/adviser/questions/{question_id}/guide",
                json={"action_id": str(uuid4()), "decision": "REJECT"},
            )
            assert duplicate_decision.status_code == 409
            assert duplicate_decision.json()["error"]["code"] == "adviser_guide_already_decided"

            started = client.post(
                "/api/v2/NDLLMSendLittleElfMessage",
                json={
                    **callback,
                    "answer": "Guide started.",
                    "intent_type": "guide_started",
                    "guide_started": True,
                },
            )
            assert started.status_code == 200, started.text
            guide_status = client.get(
                f"/api/dongzhou/v1/adviser/guides/{guide_action_id}"
            )
            assert guide_status.json()["state"] == "RUNNING"
            assert guide_status.json()["guide"]["eventType"] == "guide_started"
            assert guide_status.json()["guide"]["guideStarted"] is True

            completed = client.post(
                "/api/v2/NDLLMSendLittleElfMessage",
                json={
                    **callback,
                    "answer": "Guide completed.",
                    "intent_type": "guide_completed",
                    "guide_started": True,
                },
            )
            assert completed.status_code == 200, completed.text
            guide_status = client.get(
                f"/api/dongzhou/v1/adviser/guides/{guide_action_id}"
            )
            assert guide_status.json()["state"] == "COMPLETED"
            assert guide_status.json()["guide"]["eventType"] == "guide_completed"
            assert guide_status.json()["guide"]["message"] == "Guide completed."

            action_id = uuid4()
            reviewed = client.post(
                f"/api/dongzhou/v1/adviser/questions/{question_id}/feedback",
                json={"action_id": str(action_id), "rating": "accurate", "reason": ""},
            )
            assert reviewed.status_code == 200, reviewed.text
            assert reviewed.json()["state"] == "RECORDED"
            assert client.post(
                f"/api/dongzhou/v1/adviser/questions/{question_id}/feedback",
                json={"action_id": str(action_id), "rating": "accurate", "reason": ""},
            ).json()["replayed"] is True
            assert len(upstreams.feedback) == 1

            cancel_question_id = uuid4()
            cancel_asked = client.post(
                "/api/dongzhou/v1/adviser/questions",
                json={
                    "client_request_id": str(cancel_question_id),
                    "question": "Guide me to the next objective.",
                    "stage_id": "001",
                    "stage_title": "Stage One",
                    "stage_index": 1,
                },
            )
            assert cancel_asked.status_code == 200, cancel_asked.text
            cancel_callback = {
                **callback,
                "task_id": str(cancel_question_id),
                "chat_id": f"dongzhou-adviser-{cancel_question_id}",
                "answer": "A guide is available.",
                "guide_session_id": "cancel-guide-session",
            }
            assert client.post(
                "/api/v2/NDLLMSendLittleElfMessage", json=cancel_callback
            ).status_code == 200
            cancel_guide_action_id = uuid4()
            assert client.post(
                f"/api/dongzhou/v1/adviser/questions/{cancel_question_id}/guide",
                json={
                    "action_id": str(cancel_guide_action_id),
                    "decision": "ACCEPT",
                },
            ).json()["state"] == "ACCEPTED"
            cancel_action_id = uuid4()
            cancelled = client.post(
                f"/api/dongzhou/v1/adviser/guides/{cancel_guide_action_id}/cancel",
                json={
                    "action_id": str(cancel_action_id),
                    "reason": "player_changed_plan",
                },
            )
            assert cancelled.status_code == 200, cancelled.text
            assert cancelled.json()["state"] == "CANCELLED"
            assert cancelled.json()["guide"]["eventType"] == "guide_cancelled"
            assert upstreams.guide_cancellations == [{
                "gameServerId": settings.game_server_id,
                "playerId": str(stable_player_id(settings.ainpc_game_server_id, player_id)),
                "guideSessionId": "cancel-guide-session",
                "reason": "player_changed_plan",
            }]
            assert client.post(
                f"/api/dongzhou/v1/adviser/guides/{cancel_guide_action_id}/cancel",
                json={
                    "action_id": str(cancel_action_id),
                    "reason": "player_changed_plan",
                },
            ).json()["replayed"] is True
            assert client.get(
                f"/api/dongzhou/v1/adviser/guides/{cancel_guide_action_id}"
            ).json()["state"] == "CANCELLED"

            client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
            assert client.get(
                f"/api/dongzhou/v1/adviser/questions/{question_id}"
            ).status_code == 404
