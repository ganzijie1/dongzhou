from __future__ import annotations

from copy import deepcopy

import numpy as np

from rl.beam_mpc import BeamMPC, BeamMPCConfig


class FakeEnv:
    max_units = 2

    def __init__(self) -> None:
        self.state = {"depth": 0, "hp": 10, "enemy_hp": 10}

    def snapshot(self):
        return deepcopy(self.state)

    def restore(self, snapshot, *, restart_process=True):
        del restart_process
        self.state = deepcopy(snapshot)
        return np.asarray([self.state["depth"]], np.float32), {"status": 2}

    def unit_info(self):
        return [
            {"id": 0, "force": 1, "hp": self.state["hp"], "max_hp": 10, "class": "Lord"},
            {"id": 1, "force": 4, "hp": self.state["enemy_hp"], "max_hp": 10, "class": "Lord"},
        ]

    def list_actions(self):
        if self.state["depth"] == 0:
            return [
                {"index": 0, "unit": 0, "type": 1, "x": 0, "y": 0, "target": 1},
                {"index": 1, "unit": 0, "type": 0, "x": 1, "y": 0},
            ]
        return [
            {"index": 0, "unit": 0, "type": 1, "x": 0, "y": 0, "target": 1},
            {"index": 1, "unit": 0, "type": 3, "x": 0, "y": 0},
        ]

    def step(self, action):
        if self.state["depth"] == 0 and action == 0:
            self.state["enemy_hp"] -= 1
        elif self.state["depth"] == 0 and action == 1:
            self.state["hp"] += 0
        elif self.state["depth"] == 1 and action == 0:
            self.state["enemy_hp"] -= 8 if self.state["enemy_hp"] == 10 else 1
        self.state["depth"] += 1
        return np.asarray([self.state["depth"]], np.float32), 0.0, False, False, {"status": 2}


def test_beam_looks_past_greedy_first_action_and_restores_root():
    env = FakeEnv()
    original = env.snapshot()
    planner = BeamMPC(BeamMPCConfig(horizon=2, beam_width=4, candidates_per_node=2))
    result = planner.search(env, np.asarray([0], np.float32))
    assert result.action == 1
    assert result.expanded_nodes == 6
    assert env.snapshot() == original


def test_prior_can_break_equal_search_values():
    env = FakeEnv()
    planner = BeamMPC(BeamMPCConfig(
        horizon=1, beam_width=2, candidates_per_node=2, leaf_weight=0.0,
        prior_weight=1.0,
    ))

    def prior(_env, _observation, _decision):
        return np.asarray([-2.0, -0.1], np.float32)

    result = planner.search(env, np.asarray([0], np.float32), prior=prior)
    assert result.action == 1


def main() -> None:
    test_beam_looks_past_greedy_first_action_and_restores_root()
    test_prior_can_break_equal_search_values()
    print("beam MPC ok: finite-horizon choice, prior, and root restoration")


if __name__ == "__main__":
    main()
