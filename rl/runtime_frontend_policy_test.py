"""Exercise the frontend policy override on a real interactive enemy turn."""

from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable
import rl.play_gui as gui


def main() -> None:
    with MengdeEnv(
        find_executable(None), interactive=True, max_episode_actions=1000
    ) as env:
        observation, info = env.reset()
        while int(info["current_force"]) == 1:
            wait = next(
                action for action in env.list_actions() if int(action["type"]) == 0
            )
            observation, _, terminated, truncated, info = env.step(
                int(wait["index"])
            )
            assert not terminated and not truncated
        actions = env.list_actions()
        map_info = env.map_info()
        selected = gui.ppo_tactical_action(
            None, env, actions, observation,
            int(map_info["width"]), int(map_info["height"]),
        )
        assert gui._runtime_battle_policy.backend == "rolling-beam"
        assert any(int(action["index"]) == selected for action in actions)
        _, _, terminated, truncated, _ = env.step(selected)
        assert not terminated and not truncated
    print(
        "frontend runtime policy ok: real enemy turn executed through "
        f"{gui._runtime_battle_policy.backend.upper()}"
    )


if __name__ == "__main__":
    main()
