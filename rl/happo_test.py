"""Smoke checks for heterogeneous sequential HAPPO updates."""

from __future__ import annotations

from pathlib import Path

import torch

from rl.happo import (
    HAPPO, HAPPO_ACTION_FEATURES, PopArtCritic, happo_decision,
)
from rl.mengde_env import MengdeEnv


def main() -> None:
    critic = PopArtCritic(4)
    states = torch.randn(8, 4)
    before = critic(states).detach()
    critic.update_stats(torch.linspace(-20.0, 30.0, 8))
    assert torch.allclose(before, critic(states).detach(), atol=1e-5)

    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        model = HAPPO(int(env.observation_space.shape[0]), seed=2026)
        observation, _ = env.reset(seed=2026)
        map_info = env.map_info()
        decision = happo_decision(
            env, observation, int(map_info["width"]), int(map_info["height"])
        )
        assert decision.candidates.shape[1] == HAPPO_ACTION_FEATURES == 34
        assert {"King", "Support"} <= set(model.actors)
        history = model.learn(
            env, 16, rollout_steps=16, epochs=1, batch_size=8, seed=2026
        )
        update = history[-1]
        assert update["steps"] == 16
        assert {"Lord", "Cavalry", "Strategist", "Fighter"} <= set(update["role_order"])
        assert 0.5 <= float(update["mean_correction"]) <= 2.0
        assert model.parameter_count > 0
        assert model.actors["Lord"] is not model.actors["Cavalry"]
    print("happo ok: heterogeneous actors, randomized sequential update, AEC correction, central critic")


if __name__ == "__main__":
    main()
