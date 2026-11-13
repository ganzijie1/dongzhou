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
            assert answer.json()["guideIgnored"] is True

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

            client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
            assert client.get(
                f"/api/dongzhou/v1/adviser/questions/{question_id}"
            ).status_code == 404
