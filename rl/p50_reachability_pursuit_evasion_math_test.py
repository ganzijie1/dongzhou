import numpy as np

from rl.p50_reachability_pursuit_evasion_math import (
    backward_reachable_tube,
    intercept_time,
    stochastic_reach_avoid,
)


def test_backward_tube_requires_one_action_to_survive_every_disturbance():
    successors = np.array(
        [
            [[1, 2], [1, 1]],
            [[3, 3], [2, 3]],
            [[2, 2], [2, 2]],
            [[3, 3], [3, 3]],
        ]
    )
    result = backward_reachable_tube(successors, [3], [2], 2)
    assert result.entry_time.tolist() == [2, 1, -1, 0]
    assert result.policy[2, 0] == 1
    assert result.policy[1, 1] == 0


def test_stochastic_reach_avoid_selects_certain_target_action():
    transitions = np.array(
        [
            [[0.0, 0.5, 0.5], [0.0, 1.0, 0.0]],
            [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    result = stochastic_reach_avoid(transitions, [1], [2], 1)
    assert np.isclose(result.values[1, 0], 1.0)
    assert result.policy[0, 0] == 1


def test_intercept_time_handles_stationary_and_receding_target():
    assert np.isclose(intercept_time([10.0, 0.0], [0.0, 0.0], 2.0), 5.0)
    assert np.isclose(intercept_time([10.0, 0.0], [1.0, 0.0], 2.0), 10.0)
