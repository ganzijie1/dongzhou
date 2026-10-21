import math

import numpy as np

from rl.p6_games_dynamics import (
    HybridTransition,
    StochasticHybridSystem,
    least_core_allocation,
    maximum_entropy_irl,
    nucleolus_allocation,
    replicator_dynamics,
)


def test_replicator_dynamics_preserves_simplex_and_selects_dominant_strategy():
    result = replicator_dynamics([[2.0, 2.0], [1.0, 1.0]], [0.5, 0.5], steps=300)
    assert np.allclose(result.trajectory.sum(axis=1), 1.0)
    assert np.all(result.trajectory >= 0.0)
    assert result.trajectory[-1, 0] > 0.95


def test_least_core_and_nucleolus_are_symmetric_for_majority_game():
    players = ("a", "b", "c")

    def majority(coalition):
        return 1.0 if len(coalition) >= 2 else 0.0

    least_core = least_core_allocation(players, majority)
    nucleolus = nucleolus_allocation(players, majority)
    assert math.isclose(sum(least_core.allocation.values()), 1.0)
    assert all(math.isclose(value, 1.0 / 3.0, abs_tol=1e-8) for value in nucleolus.allocation.values())
    assert math.isclose(nucleolus.maximum_excess, 1.0 / 3.0, abs_tol=1e-8)


def test_maximum_entropy_irl_prefers_demonstrated_goal_transition():
    transition = np.array(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    result = maximum_entropy_irl(
        transition,
        [[0.0], [1.0]],
        [(0, 1, 1)] * 8,
        iterations=400,
        learning_rate=0.05,
        l2_penalty=0.01,
    )
    assert result.reward_weights[0] > 0.0
    assert result.policy[0, 0, 1] > result.policy[0, 0, 0]


def test_stochastic_hybrid_system_flows_then_switches_mode():
    system = StochasticHybridSystem(
        {
            "march": lambda state, dt, _rng: state + np.array([dt]),
            "fight": lambda state, _dt, _rng: state,
        },
        [HybridTransition("march", "fight", lambda state: state[0] >= 1.0)],
    )
    trajectory = system.simulate("march", [0.0], step_size=0.25, steps=6, seed=7)
    assert trajectory.modes[4] == "fight"
    assert trajectory.modes[-1] == "fight"
    assert math.isclose(trajectory.states[-1, 0], 1.0)
    probability = system.estimate_reach_probability(
        "march",
        [0.0],
        lambda mode, _state: mode == "fight",
        step_size=0.25,
        steps=4,
        samples=20,
        seed=9,
    )
    assert probability == 1.0
