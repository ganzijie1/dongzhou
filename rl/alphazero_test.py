"""Smoke tests for deterministic replay and AlphaZero PUCT training."""

from pathlib import Path

import numpy as np

from rl.alphazero import AlphaZero
from rl.mappo import current_decision
from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=12) as env:
        observation, _ = env.reset(seed=2026)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        history, expected = [], []
        for _ in range(3):
            decision = current_decision(env, observation, width, height)
            action = int(decision.actions[0]["index"])
            history.append(action)
            observation, _, _, _, _ = env.step(action)
            expected.append(observation.copy())
        observation, _ = env.reset(seed=2026)
        for action, state in zip(history, expected):
            observation, _, _, _, _ = env.step(action)
            assert np.array_equal(observation, state)

    with (
        MengdeEnv(executable, max_episode_actions=12) as env,
        MengdeEnv(executable, max_episode_actions=12) as simulator,
    ):
        model = AlphaZero(int(env.observation_space.shape[0]), seed=2026)
        samples, metrics = model.self_play_episode(
            env, simulator, seed=2026, simulations=4, temperature_moves=4
        )
        update = model.update(samples, epochs=1, batch_size=8)
        assert samples and metrics["simulator_steps"] > metrics["actions"]
        assert update["samples"] == len(samples)
        assert model.parameter_count > 0
    print("alphazero ok: deterministic replay, PUCT visits, and policy/value update")


if __name__ == "__main__":
    main()
