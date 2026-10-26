import numpy as np

from rl.p63_robust_stochastic_mpc_math import (
    box_is_robust_invariant,
    empirical_chance_margin,
    minimal_rpi_box_radius,
    scenario_feasible,
    tightened_box_bounds,
)


def test_rpi_box_and_tightening():
    radius = minimal_rpi_box_radius([[0.5]], [1.0])
    assert np.allclose(radius, [2.0])
    assert box_is_robust_invariant([[0.5]], radius, [1.0])
    low, high = tightened_box_bounds([-5.0], [5.0], radius)
    assert np.allclose(low, [-3.0]) and np.allclose(high, [3.0])


def test_scenario_and_empirical_chance_diagnostics():
    feasible, rate = scenario_feasible([[-1.0], [0.2], [-0.3]], maximum_violations=1)
    assert feasible and np.isclose(rate, 1 / 3)
    margin, coverage = empirical_chance_margin([1, 2, 3, 4], 4.0, 0.75)
    assert np.isclose(margin, 0.0) and np.isclose(coverage, 1.0)
