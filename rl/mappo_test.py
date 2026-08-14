"""Smoke checks for parameter-sharing MAPPO on the native environment."""

from __future__ import annotations

from pathlib import Path

from rl.mappo import ACTION_FEATURES, MAPPO, current_decision
from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        observation, _ = env.reset(seed=2026)
        map_info = env.map_info()
        decision = current_decision(
            env, observation, int(map_info["width"]), int(map_info["height"])
        )
        assert decision.actions
        assert all(int(action["unit"]) == decision.agent_id for action in decision.actions)
        assert decision.candidates.shape == (len(decision.actions), ACTION_FEATURES)
        model = MAPPO(int(env.observation_space.shape[0]), seed=2026)
        history = model.learn(
            env, 16, rollout_steps=16, epochs=1, batch_size=8, seed=2026
        )
        assert history[-1]["steps"] == 16.0
        assert model.parameter_count > 0
    print("mappo ok: shared actor, per-unit masks, central critic, and native gradient update")


if __name__ == "__main__":
    main()