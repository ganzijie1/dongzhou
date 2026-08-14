"""Smoke checks for collapse-resistant AdaptiveCQL."""

from pathlib import Path

import numpy as np

from rl.adaptive_cql import AdaptiveCQL, CriticAdaptiveCQL, SupportedCQL
from rl.mappo import current_decision
from rl.mengde_env import MengdeEnv
from rl.offline_dataset import OfflineDataset


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=16) as env:
        dataset = OfflineDataset.load(
            "rl/models/offline_iql_cql_comparison/dataset.npz"
        )
        model = AdaptiveCQL(int(env.observation_space.shape[0]), seed=2026)
        metrics = model.train(dataset, 8, batch_size=16)
        observation, _ = env.reset(seed=3030)
        map_info = env.map_info()
        decision = current_decision(
            env, observation, int(map_info["width"]), int(map_info["height"])
        )
        probabilities = model.probabilities(observation, decision)
        assert len(probabilities) == len(decision.actions)
        assert np.isclose(probabilities.sum(), 1.0)
        assert 0 <= model.choose(observation, decision) < len(decision.actions)
        assert 0.0 < float(metrics["normalized_entropy"]) <= 1.0
        assert float(metrics["temperature"]) > 0.0
        assert len(metrics["dataset_action_type_counts"]) == 4

        supported = SupportedCQL(int(env.observation_space.shape[0]), seed=2026)
        supported.load_legacy_values(
            "rl/models/offline_iql_cql_comparison/cql.pt"
        )
        support_metrics = supported.train_support(dataset, 8, batch_size=16)
        support_probability = supported.probabilities(observation, decision)
        assert np.isclose(support_probability.sum(), 1.0)
        assert float(support_metrics["normalized_entropy"]) > 0.0

        critic_adaptive = CriticAdaptiveCQL(
            int(env.observation_space.shape[0]), seed=2026
        )
        critic_metrics = critic_adaptive.train(dataset, 8, batch_size=16)
        critic_probability = critic_adaptive.probabilities(observation, decision)
        assert np.isclose(critic_probability.sum(), 1.0)
        assert 0.05 <= float(critic_metrics["alpha"]) <= 5.0
        assert float(critic_metrics["reward_scale"]) >= 1.0
        assert "q_ood_minus_data" in critic_metrics
    print("adaptive cql ok: balanced replay, entropy actor, conditioned twin Q")


if __name__ == "__main__":
    main()