"""Verify player/enemy turn hand-off and native terrain data."""

from __future__ import annotations

from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable


def main() -> None:
    executable = find_executable(None)
    with MengdeEnv(executable, interactive=True, max_episode_actions=1000) as env:
        observation, info = env.reset()
        assert info["current_force"] == 1
        map_info = env.map_info()
        assert (map_info["width"], map_info["height"]) == (19, 16)
        assert len(map_info["terrain"]) == 19 * 16

        player_actions = 0
        while info["current_force"] == 1:
            actions = env.list_actions()
            wait = next(action for action in actions if int(action["type"]) == 0)
            observation, _, terminated, truncated, info = env.step(int(wait["index"]))
            assert not terminated and not truncated
            player_actions += 1
            assert player_actions <= 32

        assert info["current_force"] == 4
        enemy_actions = env.list_actions()
        assert enemy_actions
        model_path = Path("rl/models/enemy_ppo.zip")
        if model_path.is_file():
            from sb3_contrib import MaskablePPO
            model = MaskablePPO.load(model_path)
            selected, _ = model.predict(
                observation, action_masks=env.action_masks(), deterministic=True
            )
            enemy_action = int(selected)
        else:
            enemy_action = int(enemy_actions[0]["index"])
        observation, _, terminated, truncated, info = env.step(enemy_action)
        assert not terminated and not truncated
        print(
            f"interactive protocol passed: player_actions={player_actions}, "
            f"enemy_actions={len(enemy_actions)}, selected={enemy_action}, "
            f"next_force={info['current_force']}"
        )


if __name__ == "__main__":
    main()
