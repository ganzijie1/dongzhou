import numpy as np

from rl.p60_multiobjective_value_math import (
    chebyshev_loss,
    hypervolume_2d,
    hypervolume_contributions_2d,
    nondominated,
    nondominated_bellman_backup,
    weighted_minkowski_sum,
)


def test_nondominated_filter_removes_dominated_and_duplicate_values():
    values = nondominated([[2.0, 1.0], [1.0, 2.0], [1.0, 1.0], [2.0, 1.0]])
    assert {tuple(value) for value in values} == {(2.0, 1.0), (1.0, 2.0)}


def test_weighted_minkowski_and_bellman_backup_preserve_tradeoffs():
    combined = weighted_minkowski_sum([[[1.0, 0.0]], [[0.0, 1.0]]], [0.25, 0.75])
    assert np.allclose(combined, [[0.25, 0.75]])
    transitions = [[1.0, 0.0], [0.0, 1.0]]
    rewards = np.zeros((2, 2, 2))
    backup = nondominated_bellman_backup(transitions, rewards, [[[1.0, 0.0]], [[0.0, 1.0]]], discount=0.9)
    assert {tuple(value) for value in backup.values} == {(0.9, 0.0), (0.0, 0.9)}
    assert set(backup.actions.tolist()) == {0, 1}


def test_chebyshev_selects_balanced_point():
    values = [[1.0, 0.0], [0.6, 0.6], [0.0, 1.0]]
    losses = chebyshev_loss(values, [0.5, 0.5], [1.0, 1.0])
    assert np.argmin(losses) == 1


def test_two_dimensional_hypervolume_and_contributions():
    values = [[2.0, 5.0], [4.0, 3.0], [1.0, 1.0]]
    assert np.isclose(hypervolume_2d(values, [0.0, 0.0]), 16.0)
    contributions = hypervolume_contributions_2d(values, [0.0, 0.0])
    assert contributions[0] > 0.0 and contributions[1] > 0.0
    assert np.isclose(contributions[2], 0.0)
