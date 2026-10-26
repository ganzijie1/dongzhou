import numpy as np

from rl.p59_wasserstein_fokker_planck_math import (
    boltzmann_entropy,
    fokker_planck_no_flux_step,
    free_energy_dissipation_rate,
    jko_gaussian_heat_standard_deviation,
    relative_fisher_information,
    wasserstein_1d,
)


def test_weighted_one_dimensional_wasserstein_distance():
    assert np.isclose(wasserstein_1d([0.0], [1.0], [2.0], [1.0]), 2.0)
    assert np.isclose(wasserstein_1d([0.0, 2.0], [0.5, 0.5], [1.0], [1.0]), 1.0)


def test_entropy_and_gaussian_jko_step_have_expected_values():
    assert np.isclose(boltzmann_entropy([0.5, 0.5]), -np.log(2.0))
    sigma = jko_gaussian_heat_standard_deviation(1.0, 1.0)
    assert np.isclose(sigma, (1.0 + np.sqrt(5.0)) / 2.0)
    assert sigma > 1.0


def test_no_flux_step_preserves_constant_density_and_mass():
    density = np.ones(5) / 5.0
    updated = fokker_planck_no_flux_step(density, np.zeros(5), diffusion=1.0, grid_spacing=1.0, time_step=0.1)
    assert np.allclose(updated, density)
    assert np.isclose(updated.sum(), density.sum())


def test_fisher_and_dissipation_vanish_at_constant_ratio():
    grid = np.linspace(0.0, 1.0, 5)
    density = np.ones(5)
    assert np.isclose(relative_fisher_information(density, density, grid), 0.0)
    assert np.isclose(free_energy_dissipation_rate(density, np.ones(5), 0.25), 0.0)
