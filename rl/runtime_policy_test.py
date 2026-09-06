"""Regression tests for rolling planning and learned-policy fallbacks."""

from pathlib import Path
from tempfile import TemporaryDirectory

import torch

from rl.mengde_env import MengdeEnv
from rl.offline_rl import CQL
from rl.rolling_beam import RollingBeamPlanner
from rl.runtime_policy import RuntimeBattlePolicy


class FlakyPlanner:
    def __init__(self) -> None:
        self.calls = 0
        self.delegate = RollingBeamPlanner()

    def choose(self, env, actions, width, height):
        self.calls += 1
        if self.calls == 1:
            raise ValueError("transient planning input failure")
        return self.delegate.choose(env, actions, width, height)


def main() -> None:
    executable = Path("build/rl-vcpkg/game/src/rl/Release/mengde_rl.exe")
    with MengdeEnv(executable, max_episode_actions=20) as env:
        observation, _ = env.reset(seed=2026)
        actions = env.list_actions()
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])

        primary = RuntimeBattlePolicy()
        action = primary.choose(env, actions, observation, width, height)
        assert primary.backend == "rolling-beam"
        assert primary.last_plan is not None
        assert primary.last_plan.stats.expanded > 0
        assert any(int(item["index"]) == action for item in actions)

        with TemporaryDirectory() as directory:
            cql_path = Path(directory) / "cql.pt"
            cql = CQL(len(observation), seed=2026)
            torch.save(
                {"q1": cql.q1.state_dict(), "q2": cql.q2.state_dict()},
                cql_path,
            )
            fallback = RuntimeBattlePolicy(
                happo_path=Path(directory) / "missing-happo.pt",
                cql_path=cql_path,
                enable_planner=False,
            )
            action = fallback.choose(env, actions, observation, width, height)
            assert fallback.backend == "cql"
            assert any(int(item["index"]) == action for item in actions)

            transient = RuntimeBattlePolicy(
                happo_path=Path(directory) / "missing-happo.pt",
                cql_path=cql_path,
                planner=FlakyPlanner(),
            )
            transient.choose(env, actions, observation, width, height)
            assert transient.backend == "cql"
            transient.choose(env, actions, observation, width, height)
            assert transient.backend == "rolling-beam"
            assert transient.planner_error is None
    print("runtime policy ok: rolling beam primary and CQL fallback select legal actions")


if __name__ == "__main__":
    main()
