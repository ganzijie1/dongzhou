import numpy as np

from rl.p40_dynamic_risk_bsde_math import (
    bsde_backward_euler,
    discrete_cvar,
    entropic_risk,
    nested_cvar_markov_chain,
)


def test_discrete_cvar_selects_exact_worst_tail():
    result = discrete_cvar([0.0, 10.0, 20.0], [0.5, 0.25, 0.25], alpha=0.5)
    assert np.isclose(result.value, 15.0)
    assert np.isclose(result.var, 0.0)
    assert np.allclose(result.tail_weights, [0.0, 0.5, 0.5])


def test_entropic_risk_limits_to_expectation_and_increases_with_aversion():
    mean = entropic_risk([0.0, 2.0], [0.5, 0.5], risk_aversion=0.0)
    cautious = entropic_risk([0.0, 2.0], [0.5, 0.5], risk_aversion=2.0)
    assert np.isclose(mean, 1.0)
    assert cautious > mean


def test_nested_cvar_recurses_over_markov_uncertainty():
    transitions = np.array([[[0.5, 0.5], [0.0, 1.0]]])
    result = nested_cvar_markov_chain(
        transitions, [[1.0, 2.0]], [0.0, 10.0], [1.0, 0.0], alpha=0.5
    )
    assert np.allclose(result.value_functions[0], [11.0, 12.0])
    assert np.isclose(result.initial_value, 11.0)


def test_bsde_euler_conditions_on_information_partition():
    result = bsde_backward_euler(
        [0.0, 2.0, 4.0, 6.0],
        [[1.0, 1.0, 1.0, 1.0]],
        [[0, 0, 1, 1]],
        dt=0.5,
    )
    assert np.allclose(result[0], [1.5, 1.5, 5.5, 5.5])
