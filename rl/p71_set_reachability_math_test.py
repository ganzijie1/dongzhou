import numpy as np

from rl.p71_set_reachability_math import ConstrainedZonotope, TaylorModel, Zonotope, linear_reachable_step


def test_zonotope_operations_and_linear_reachability():
    state = Zonotope(np.array([1.0]), np.array([[0.5]]))
    control = Zonotope(np.array([0.0]), np.array([[0.2]]))
    disturbance = Zonotope(np.array([0.0]), np.array([[0.1]]))
    reached = linear_reachable_step(state, [[2.0]], control, [[1.0]], disturbance)
    assert np.allclose(reached.interval_hull(), ([0.7], [3.3]))
    assert np.isclose(reached.support([1.0]), 3.3)


def test_constrained_zonotope_hyperplane_and_feasibility():
    constrained = ConstrainedZonotope(np.zeros(2), np.eye(2), np.empty((0, 2)), np.empty(0))
    sliced = constrained.intersect_hyperplane([1.0, 1.0], 0.0)
    assert sliced.is_feasible()
    impossible = constrained.intersect_hyperplane([1.0, 0.0], 2.0)
    assert not impossible.is_feasible()


def test_taylor_model_arithmetic_contains_samples():
    model = TaylorModel(np.array([1.0, 1.0]), (-0.1, 0.1))
    squared = model.multiply(model, maximum_order=2)
    low, high = squared.evaluate_interval((-1.0, 1.0))
    assert low <= 0.0 and high >= 4.0
