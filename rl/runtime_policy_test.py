"""Regression tests for HAPPO runtime selection and CQL fallback."""

from pathlib import Path
from tempfile import TemporaryDirectory

import torch

from rl.happo import HAPPO
from rl.mengde_env import MengdeEnv
from rl.offline_rl import CQL
from rl.runtime_policy import RuntimeBattlePolicy


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        observation, _ = env.reset(seed=2026)
        actions = env.list_actions()
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])

        state_features = len(observation)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            happo_path = root / "happo.pt"
            cql_path = root / "cql.pt"
            happo = HAPPO(state_features, seed=2026)
            cql = CQL(state_features, seed=2026)
            torch.save(
                {
                    "actors": happo.actors.state_dict(),
                    "critic": happo.critic.state_dict(),
                },
                happo_path,
            )
            torch.save(
                {"q1": cql.q1.state_dict(), "q2": cql.q2.state_dict()},
                cql_path,
            )

            primary = RuntimeBattlePolicy(
                happo_path=happo_path, cql_path=cql_path
            )
            selected = primary.choose(
                env, actions, observation, width, height
            )
            assert primary.backend == "joint-mapf+happo"
            assert any(int(item["index"]) == selected for item in actions)

            fallback = RuntimeBattlePolicy(
                happo_path=root / "missing-happo.pt", cql_path=cql_path
            )
            selected = fallback.choose(
                env, actions, observation, width, height
            )
            assert fallback.backend == "joint-mapf+cql"
            assert any(int(item["index"]) == selected for item in actions)
    print(
        "runtime policy ok: joint MAPF uses HAPPO primary and CQL fallback "
        "while selecting native legal actions"
    )


if __name__ == "__main__":
    main()
