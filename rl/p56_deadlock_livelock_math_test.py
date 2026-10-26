import numpy as np

from rl.p56_deadlock_livelock_math import (
    diagnose_behavior_window,
    periodicity_score,
    wait_for_cycles,
    winding_number,
)


def test_wait_for_cycle_finds_module_deadlock():
    graph = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
    assert wait_for_cycles(graph) == ((0, 1),)


def test_stuck_and_legal_wait_are_distinguished():
    stuck = diagnose_behavior_window([[0.0, 0.0]] * 4, [[1.0, 0.0]] * 3, [0.0] * 4)
    assert stuck.stuck and not stuck.idle
    waiting = diagnose_behavior_window([[0.0, 0.0]] * 4, [[0.0, 0.0]] * 3, [0.0] * 4, legal_wait=True)
    assert not waiting.idle


def test_winding_and_periodicity_detect_orbiting_livelock():
    angles = np.linspace(0.0, 2.0 * np.pi, 17)
    path = np.c_[np.cos(angles), np.sin(angles)]
    assert np.isclose(winding_number(path, [0.0, 0.0]), 1.0)
    diagnostic = diagnose_behavior_window(path, np.diff(path, axis=0), np.zeros(path.shape[0]), obstacle_center=[0.0, 0.0])
    assert diagnostic.orbiting and diagnostic.livelock
    period, score = periodicity_score(["a", "b", "a", "b", "a", "b"], max_period=3)
    assert period == 2 and np.isclose(score, 1.0)
