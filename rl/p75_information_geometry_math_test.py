import numpy as np

from rl.p75_information_geometry_math import categorical_fisher_inner_product, categorical_natural_gradient, entropy_mirror_step, fisher_rao_distance, fisher_rao_geodesic, parameter_natural_gradient, probability_floor


def test_fisher_rao_distance_and_geodesic_endpoints():
    p, q = np.array([0.8, 0.2]), np.array([0.2, 0.8])
    assert fisher_rao_distance(p, q) > 0.0
    assert np.allclose(fisher_rao_geodesic(p, q, 0.0), p)
    assert np.allclose(fisher_rao_geodesic(p, q, 1.0), q)
    middle = fisher_rao_geodesic(p, q, 0.5)
    assert np.isclose(middle.sum(), 1.0) and np.all(middle > 0.0)


def test_natural_gradient_mirror_step_and_fisher_inner_product():
    p = [0.5, 0.5]
    direction = categorical_natural_gradient(p, [1.0, -1.0], maximize=True)
    assert np.isclose(direction.sum(), 0.0) and direction[0] > 0.0
    updated = entropy_mirror_step(p, [1.0, -1.0], 0.5, maximize=True)
    assert updated[0] > updated[1]
    assert np.isclose(categorical_fisher_inner_product(p, direction, direction), 1.0)


def test_probability_floor_and_parameter_natural_gradient():
    floored = probability_floor([1.0, 0.0], 0.1)
    assert np.all(floored > 0.0) and np.isclose(floored.sum(), 1.0)
    result, residual = parameter_natural_gradient([[1.0, 0.0], [0.0, 1.0]], [1.0, 2.0])
    assert np.allclose(result, [2.0, 4.0], atol=1e-6) and residual < 1e-10
