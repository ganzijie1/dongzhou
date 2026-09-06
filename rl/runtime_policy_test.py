"""Regression tests for HAPPO runtime selection and CQL fallback."""

from pathlib import Path

from rl.mengde_env import MengdeEnv
from rl.runtime_policy import RuntimeBattlePolicy


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    cql_path = Path("rl/models/offline_iql_cql_comparison/cql.pt")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        observation, _ = env.reset(seed=2026)
        actions = env.list_actions()
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])

        primary = RuntimeBattlePolicy()
        action = primary.choose(env, actions, observation, width, height)
        assert primary.backend == "happo"
        assert any(int(item["index"]) == action for item in actions)

        fallback = RuntimeBattlePolicy(
            happo_path=Path("rl/models/missing-happo.pt"), cql_path=cql_path
        )
        action = fallback.choose(env, actions, observation, width, height)
        assert fallback.backend == "cql"
        assert any(int(item["index"]) == action for item in actions)
    print("runtime policy ok: HAPPO primary and CQL fallback select legal actions")


if __name__ == "__main__":
    main()
