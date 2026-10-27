import numpy as np

from rl.p74_differential_dynamic_programming_math import backward_control_law, expected_cost_change, finite_difference_jacobians, ilqr_q_derivatives, sqp_kkt_residual, value_derivative_update


def test_ilqr_one_step_matches_scalar_lqr():
    q = ilqr_q_derivatives([[1.0]], [[1.0]], [0.0], [0.0], [[0.0]], [[0.0]], [[1.0]], [2.0], [[2.0]])
    feedforward, feedback, minimum = backward_control_law(q.q_u, q.q_uu, q.q_ux)
    assert np.allclose(feedforward, [-2.0 / 3.0])
    assert np.allclose(feedback, [[-2.0 / 3.0]]) and np.isclose(minimum, 3.0)
    value_x, value_xx = value_derivative_update(q, feedforward, feedback)
    assert value_x.shape == (1,) and value_xx.shape == (1, 1)


def test_expected_change_and_finite_difference_jacobians():
    change = expected_cost_change([[2.0]], [[[4.0]]], [[-0.5]], 1.0)
    assert np.isclose(change, -0.5)
    fx, fu = finite_difference_jacobians(lambda x, u: np.array([x[0] ** 2 + 3.0 * u[0]]), [2.0], [1.0])
    assert np.allclose(fx, [[4.0]], atol=1e-5) and np.allclose(fu, [[3.0]], atol=1e-5)


def test_sqp_kkt_residual_zero_for_exact_solution():
    stationarity, feasibility = sqp_kkt_residual([[1.0]], [0.0], [[1.0]], [-1.0], [1.0], [-1.0])
    assert np.isclose(stationarity, 0.0) and np.isclose(feasibility, 0.0)
