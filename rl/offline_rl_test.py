"""Smoke test for fixed dataset collection and offline IQL/CQL updates."""

from pathlib import Path

from rl.mappo import current_decision
from rl.mengde_env import MengdeEnv
from rl.offline_dataset import collect_offline_dataset
from rl.offline_rl import CQL, IQL


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=16) as env:
        dataset, summary = collect_offline_dataset(env, 4, seed=2026)
        assert len(dataset) > 0 and summary["behavior_counts"]["random"] == 1
        assert dataset.masks.any()
        state_features = int(env.observation_space.shape[0])
        iql, cql = IQL(state_features), CQL(state_features)
        iql_metrics = iql.train(dataset, 8, batch_size=16)
        cql_metrics = cql.train(dataset, 8, batch_size=16)
        observation, _ = env.reset(seed=3030)
        map_info = env.map_info()
        decision = current_decision(
            env, observation, int(map_info["width"]), int(map_info["height"])
        )
        assert 0 <= iql.choose(observation, decision) < len(decision.actions)
        assert 0 <= cql.choose(observation, decision) < len(decision.actions)
        assert iql_metrics["updates"] == cql_metrics["updates"] == 8
    print("offline rl ok: fixed dataset, IQL expectile/AWR, and CQL conservative update")


if __name__ == "__main__":
    main()
