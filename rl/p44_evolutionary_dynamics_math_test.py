import numpy as np

from rl.p44_evolutionary_dynamics_math import (
    pure_ess_diagnostic,
    replicator_mutator_rhs,
    replicator_rhs,
    resistance_tree_potentials,
    stationary_distribution,
    stochastically_stable_states,
)


def test_replicator_flow_is_tangent_to_simplex():
    rock_paper_scissors = np.array([[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]])
    rhs = replicator_rhs([0.2, 0.3, 0.5], rock_paper_scissors)
    assert np.isclose(rhs.sum(), 0.0)


def test_replicator_mutator_preserves_total_mass():
    rhs = replicator_mutator_rhs([0.5, 0.5], [[2.0, 0.0], [0.0, 1.0]], [[0.9, 0.1], [0.2, 0.8]])
    assert np.isclose(rhs.sum(), 0.0)


def test_strict_symmetric_nash_is_an_ess():
    result = pure_ess_diagnostic([[2.0, 1.0], [0.0, 1.5]], 0)
    assert result.is_nash
    assert result.is_ess


def test_resistance_trees_select_minimum_stochastic_potential():
    resistance = np.array([[np.inf, 1.0, 3.0], [2.0, np.inf, 1.0], [4.0, 2.0, np.inf]])
    potentials = resistance_tree_potentials(resistance)
    assert np.allclose(potentials, [4.0, 3.0, 2.0])
    assert np.array_equal(stochastically_stable_states(resistance), [2])


def test_stationary_distribution_solves_global_balance():
    transition = np.array([[0.8, 0.2], [0.1, 0.9]])
    distribution = stationary_distribution(transition)
    assert np.allclose(distribution @ transition, distribution)
