import numpy as np

from rl.p67_benamou_brenier_bridge_math import benamou_brenier_action, continuity_residual, linear_flow_matching, probability_flow_velocity, sinkhorn_coupling


def test_continuity_and_action():
    residual = continuity_residual([1.0, 0.0], [0.5, 0.5], [0.0, 0.5, 0.0], dt=1.0, dx=1.0)
    assert np.allclose(residual, [0.0, 0.0])
    assert np.isclose(benamou_brenier_action([[1.0, 1.0]], [[1.0, 2.0]], dt=0.5, dx=1.0), 2.5)


def test_sinkhorn_marginals_and_probability_flow():
    coupling = sinkhorn_coupling([0.5, 0.5], [0.25, 0.75], [[0, 1], [1, 0]], regularization=1.0)
    assert np.allclose(coupling.sum(axis=1), [0.5, 0.5])
    assert np.allclose(coupling.sum(axis=0), [0.25, 0.75])
    assert np.allclose(probability_flow_velocity([1.0], 2.0, [0.25]), [0.5])
    point, velocity = linear_flow_matching([0.0], [2.0], 0.25)
    assert np.allclose(point, [0.5]) and np.allclose(velocity, [2.0])
