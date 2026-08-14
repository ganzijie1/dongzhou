"""Smoke test for behavior cloning and DAgger aggregation."""

from pathlib import Path

from rl.dagger import (
    BehaviorCloning, collect_expert_data, dagger_aggregate, load_happo_expert,
)
from rl.mengde_env import MengdeEnv


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=16) as env:
        expert = load_happo_expert(int(env.observation_space.shape[0]))
        initial, summary = collect_expert_data(env, expert, 3, seed=2026)
        learner = BehaviorCloning(seed=2026)
        update = learner.train(initial, 8, batch_size=16)
        added, aggregation = dagger_aggregate(
            env, expert, learner, 2, beta=0.5, seed=3030
        )
        assert initial and added
        assert update["updates"] == 8
        assert aggregation["new_samples"] == len(added)
        assert 0.0 <= aggregation["disagreement_rate"] <= 1.0
        learner.train(initial + added, 4, batch_size=16)
    print("dagger ok: expert BC, learner rollouts, expert relabeling, and aggregation")


if __name__ == "__main__":
    main()
