import numpy as np

from rl.p46_polynomial_sos_moment_math import (
    flat_extension_holds,
    localizing_matrix,
    moment_matrix,
    sos_gram_residual,
)


def test_sos_gram_certificate_for_x_squared_minus_one_squared():
    basis = [(0,), (1,), (2,)]
    vector = np.array([-1.0, 0.0, 1.0])
    residual, minimum_eigenvalue = sos_gram_residual(
        {(0,): 1.0, (2,): -2.0, (4,): 1.0}, np.outer(vector, vector), basis
    )
    assert residual < 1e-12
    assert minimum_eigenvalue > -1e-12


def test_moment_and_localizing_matrices_use_multi_indices():
    moments = {(0,): 1.0, (1,): 0.0, (2,): 1.0, (3,): 0.0, (4,): 3.0}
    matrix = moment_matrix(moments, [(0,), (1,), (2,)])
    local = localizing_matrix(moments, {(0,): 1.0, (2,): -1.0}, [(0,), (1,)])
    assert np.allclose(matrix, [[1.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 3.0]])
    assert np.allclose(local, [[0.0, 0.0], [0.0, -2.0]])


def test_flat_extension_detects_equal_numerical_rank():
    assert flat_extension_holds([[1.0]], [[1.0, 2.0], [2.0, 4.0]])
