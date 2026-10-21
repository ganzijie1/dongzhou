import math

import numpy as np
import pytest

from rl.graph_dynamics import (
    bipartite_consensus_error,
    continuous_altafini_dynamics,
    continuous_graph_dynamics,
    controlled_degroot_dynamics,
    degroot_dynamics,
    discrete_altafini_dynamics,
    graph_laplacian,
    structural_balance,
)


def test_unsigned_laplacian_and_continuous_consensus_preserve_average():
    adjacency = [[0.0, 1.0], [1.0, 0.0]]
    assert np.allclose(graph_laplacian(adjacency), [[1.0, -1.0], [-1.0, 1.0]])
    result = continuous_graph_dynamics(adjacency, [0.0, 2.0], [0.0, 1.0, 10.0])
    assert np.allclose(result.states.sum(axis=1), 2.0)
    assert np.allclose(result.states[-1], [1.0, 1.0], atol=1e-8)


def test_degroot_converges_to_stationary_weighted_consensus():
    result = degroot_dynamics(
        [[0.8, 0.2], [0.4, 0.6]],
        [0.0, 3.0],
        steps=80,
    )
    assert result.ergodic
    assert np.allclose(result.influence, [2.0 / 3.0, 1.0 / 3.0])
    assert math.isclose(result.consensus_value, 1.0)
    assert np.allclose(result.trajectory[-1], [1.0, 1.0], atol=1e-10)
    assert result.consensus_errors[-1] < result.consensus_errors[0]


def test_degroot_reports_periodic_nonconvergence():
    result = degroot_dynamics([[0.0, 1.0], [1.0, 0.0]], [0.0, 1.0], steps=4)
    assert not result.ergodic
    assert result.consensus_value is None
    assert np.array_equal(result.trajectory[0], result.trajectory[2])


def test_structural_balance_finds_two_camps_and_rejects_frustrated_cycle():
    balanced = np.array(
        [
            [0.0, 1.0, -1.0],
            [1.0, 0.0, -1.0],
            [-1.0, -1.0, 0.0],
        ]
    )
    result = structural_balance(balanced)
    assert result.balanced
    assert result.signs is not None
    assert result.signs[0] == result.signs[1]
    assert result.signs[0] == -result.signs[2]

    unbalanced = np.array(
        [
            [0.0, 1.0, -1.0],
            [1.0, 0.0, 1.0],
            [-1.0, 1.0, 0.0],
        ]
    )
    assert not structural_balance(unbalanced).balanced


def test_continuous_altafini_preserves_bipartite_consensus():
    adjacency = np.array([[0.0, -1.0], [-1.0, 0.0]])
    result = continuous_altafini_dynamics(adjacency, [2.0, -2.0], [0.0, 1.0, 5.0])
    assert result.balance.balanced
    assert np.allclose(result.trajectory, [[2.0, -2.0]] * 3)
    assert np.allclose(result.polarization_errors, 0.0)
    assert bipartite_consensus_error([2.0, -2.0], result.balance.signs) == 0.0


def test_unbalanced_altafini_triangle_decays_toward_zero():
    adjacency = np.array(
        [
            [0.0, 1.0, -1.0],
            [1.0, 0.0, 1.0],
            [-1.0, 1.0, 0.0],
        ]
    )
    result = continuous_altafini_dynamics(adjacency, [1.0, 0.5, -0.25], [0.0, 20.0])
    assert not result.balance.balanced
    assert result.gauge_trajectory is None
    assert np.linalg.norm(result.trajectory[-1]) < 1e-8


def test_discrete_altafini_and_controlled_degroot_obey_bounds():
    signed = discrete_altafini_dynamics(
        [[0.5, -0.5], [-0.5, 0.5]],
        [1.0, -1.0],
        steps=5,
    )
    assert np.allclose(signed.trajectory, [[1.0, -1.0]] * 6)

    controlled = controlled_degroot_dynamics(
        [[1.0, 0.0], [0.0, 1.0]],
        [0.0, 0.0],
        [[2.0, -2.0], [0.5, -0.5]],
        clip=(-1.0, 1.0),
    )
    assert np.array_equal(controlled[-1], [1.0, -1.0])
    with pytest.raises(ValueError, match="row sums"):
        degroot_dynamics([[0.7, 0.1], [0.2, 0.2]], [0.0, 1.0])
