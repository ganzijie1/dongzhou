"""Regression checks for the typed in-process battle event queue."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from rl.mengde_env import MengdeEnv


EXECUTABLE = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        replay_path = Path(directory) / "battle-events.jsonl"
        previous_log = os.environ.get("MENGDE_BATTLE_REPLAY_LOG")
        os.environ["MENGDE_BATTLE_REPLAY_LOG"] = str(replay_path)
        try:
            with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
                env.reset()
                snapshot = env.snapshot()
                own = next(unit for unit in snapshot["units"] if int(unit["force"]) == 1)
                enemy = next(unit for unit in snapshot["units"] if int(unit["force"]) == 4)
                enemy["x"], enemy["y"] = int(own["x"]) + 1, int(own["y"])
                env.restore(snapshot)
                env.battle_events()

                attack = next(
                    action for action in env.list_actions()
                    if int(action["unit"]) == int(own["id"])
                    and int(action["type"]) == 2
                    and int(action["target"]) == int(enemy["id"])
                )
                env.step(int(attack["index"]))
                payload = env.battle_events()
                assert payload["enabled"] is True
                events = payload["events"]
                types = [event["type"] for event in events]
                move_index = types.index("move_completed")
                attack_index = types.index("attack_started")
                hit_index = types.index("hit")
                assert move_index < attack_index < hit_index, types
                assert all(
                    int(events[index]["sequence"]) < int(events[index + 1]["sequence"])
                    for index in range(len(events) - 1)
                )
                assert env.battle_events()["events"] == []
        finally:
            if previous_log is None:
                os.environ.pop("MENGDE_BATTLE_REPLAY_LOG", None)
            else:
                os.environ["MENGDE_BATTLE_REPLAY_LOG"] = previous_log

        replay_events = [json.loads(line) for line in replay_path.read_text(encoding="utf-8").splitlines()]
        assert any(event["type"] == "attack_started" for event in replay_events)
        assert any(event["type"] == "hit" for event in replay_events)

    previous_enabled = os.environ.get("MENGDE_BATTLE_EVENTS")
    os.environ["MENGDE_BATTLE_EVENTS"] = "0"
    try:
        with MengdeEnv(EXECUTABLE, scenario="dongzhou", interactive=True) as env:
            env.reset()
            payload = env.battle_events()
            assert payload == {"enabled": False, "events": []}
            wait = next(action for action in env.list_actions() if int(action["type"]) == 0)
            env.step(int(wait["index"]))
    finally:
        if previous_enabled is None:
            os.environ.pop("MENGDE_BATTLE_EVENTS", None)
        else:
            os.environ["MENGDE_BATTLE_EVENTS"] = previous_enabled

    print("battle event queue ok: ordered events, JSONL replay, and CmdQueue-only fallback")


if __name__ == "__main__":
    main()
