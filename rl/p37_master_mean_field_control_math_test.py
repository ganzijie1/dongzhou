import numpy as np

from rl.p37_master_mean_field_control_math import (
    empirical_lions_derivative,
    estimate_finite_player_rate,
    finite_player_error_diagnostic,
    master_equation_residual,
    mean_field_control_marginal_cost,
    solve_finite_state_mfg,
)


def test_finite_state_mfg_moves_population_to_low_cost_state():
    transition = np.array(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    result = solve_finite_state_mfg(
        transition,
        [[1.0, 0.2], [0.0, 0.0]],
        [1.0, 0.0],
        lambda _time, _population: np.zeros((2, 2)),
        lambda _population: np.zeros(2),
        horizon=2,
        relaxation=0.7,
    )
    assert result.distributions[-1, 1] > 0.999
    assert result.policies[0, 0, 1] == 1.0


def test_empirical_lions_derivative_scales_particle_lift():
    particles = np.array([[1.0], [2.0], [3.0]])
    derivative = empirical_lions_derivative(
        lambda sample: float(np.mean(sample[:, 0] ** 2)), particles, 1
    )
    assert np.allclose(derivative, [4.0], atol=1e-7)


def test_master_residual_and_social_externality():
    residual = master_equation_residual(
        time_derivative=1.0,
        state_laplacian=2.0,
        hamiltonian=4.0,
        measure_divergences=[1.0, 1.0],
        measure_drift_products=[0.5, 0.5],
        measure_weights=[0.5, 0.5],
        viscosity=1.0,
    )
    assert np.isclose(residual, -0.5)
    population = np.array([0.25, 0.75])
    cost = np.repeat(population[:, None], 2, axis=1)
    derivative = np.zeros((2, 2, 2))
    derivative[0, :, 0] = 1.0
    derivative[1, :, 1] = 1.0
    marginal = mean_field_control_marginal_cost(cost, population, derivative)
    assert np.allclose(marginal[:, 0], 2.0 * population)


def test_finite_player_error_and_rate_distinguish_metrics():
    diagnostic = finite_player_error_diagnostic(
        [1.1, 2.0], [1.0, 2.2], [0.0, 0.05]
    )
    assert np.isclose(diagnostic.maximum_value_error, 0.2)
    assert diagnostic.epsilon_nash == 0.05
    rate = estimate_finite_player_rate([10, 20, 40, 80], [0.1, 0.05, 0.025, 0.0125])
    assert np.isclose(rate.exponent, 1.0, atol=1e-10)
