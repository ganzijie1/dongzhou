import numpy as np

from rl.p65_anisotropic_dynamic_field_math import anisotropy_ratio, blend_velocity, closest_approach, dynamic_collision_potential, randers_cost


def test_anisotropic_and_directed_costs():
    assert np.isclose(anisotropy_ratio([[4, 0], [0, 1]]), 2.0)
    forward = randers_cost(np.eye(2), [0.2, 0.0], [1.0, 0.0])
    backward = randers_cost(np.eye(2), [0.2, 0.0], [-1.0, 0.0])
    assert forward > backward


def test_dynamic_potential_and_velocity_cap():
    time, distance = closest_approach([2, 0], [-1, 0], 5.0)
    assert np.isclose(time, 2.0) and np.isclose(distance, 0.0)
    assert dynamic_collision_potential([2, 0], [-1, 0], horizon=5, clearance=0.5) > 1e6
    assert np.isclose(np.linalg.norm(blend_velocity([3, 0], [0, 4], avoidance_weight=1, maximum_speed=2)), 2.0)
