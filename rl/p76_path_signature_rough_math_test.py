import numpy as np

from rl.p76_path_signature_rough_math import combine_level_two, controlled_euler, lead_lag_transform, logsignature_dimension, logsignature_level_two, one_dimensional_signature, shuffle_residual, signature_dimension, signature_level_two


def test_signature_dimensions_and_one_dimensional_formula():
    assert signature_dimension(2, 2) == 7
    assert logsignature_dimension(2, 2) == 3
    assert np.allclose(one_dimensional_signature(2.0, 3), [1.0, 2.0, 2.0, 4.0 / 3.0])


def test_chen_shuffle_and_logsignature_area():
    path = np.array([[0, 0], [1, 0], [1, 1]], dtype=float)
    full = signature_level_two(path)
    left = signature_level_two(path[:2])
    right = signature_level_two(path[1:])
    combined = combine_level_two(left, right)
    assert np.allclose(full[0], combined[0]) and np.allclose(full[1], combined[1])
    assert shuffle_residual(*full) < 1e-12
    _, log_two = logsignature_level_two(path)
    assert np.isclose(log_two[0, 1], 0.5) and np.isclose(log_two[1, 0], -0.5)


def test_lead_lag_and_controlled_euler():
    transformed = lead_lag_transform([[0.0], [1.0], [3.0]])
    assert transformed.shape == (5, 2)
    trajectory = controlled_euler([[0.0], [1.0], [3.0]], [2.0], lambda state: np.array([[state[0]]]))
    assert np.allclose(trajectory[:, 0], [2.0, 4.0, 12.0])
