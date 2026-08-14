"""Smoke checks for two-level H-PPO on the native battle environment."""

from pathlib import Path

from rl.hppo import HPPO
from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        model = HPPO(
            int(env.observation_space.shape[0]), num_options=4,
            option_horizon=4, seed=2026,
        )
        history = model.learn(
            env, 32, rollout_steps=16, epochs=1, batch_size=8, seed=2026
        )
        final = history[-1]
        assert final["steps"] == 32
        assert final["manager_decisions"] >= 4
        assert len(final["option_usage"]) == 4
        assert abs(sum(final["option_usage"]) - 1.0) < 1e-6
        assert model.parameter_count > 0
    print("hppo ok: temporal manager, option-conditioned worker, and two-level PPO updates")


if __name__ == "__main__":
    main()
