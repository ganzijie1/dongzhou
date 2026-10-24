import numpy as np
from scipy.stats import norm

from rl.p29_extreme_tail_importance_math import (
    archimedean_tail_dependence,
    cross_entropy_gaussian_importance_sampling,
    empirical_tail_dependence,
    gev_cdf,
    gev_return_level,
    gpd_conditional_survival,
    pot_tail_probability,
    student_t_tail_dependence,
)


def test_gev_return_level_inverts_cdf_with_xi_convention():
    level = gev_return_level(0.99, location=2.0, scale=1.5, shape=0.2)
    assert np.isclose(
        gev_cdf(level, location=2.0, scale=1.5, shape=0.2), 0.99
    )


def test_gpd_survival_and_pot_scaling():
    conditional = gpd_conditional_survival(2.0, scale=2.0, shape=0.0)
    assert np.isclose(conditional, np.exp(-1.0))
    tail = pot_tail_probability(
        12.0,
        threshold=10.0,
        threshold_exceedance_probability=0.05,
        scale=2.0,
        shape=0.0,
    )
    assert np.isclose(tail, 0.05 * np.exp(-1.0))


def test_tail_copula_coefficients_have_expected_asymmetry():
    lower, upper = archimedean_tail_dependence("clayton", 2.0)
    assert np.isclose(lower, 2.0 ** -0.5)
    assert upper == 0.0
    lower, upper = archimedean_tail_dependence("gumbel", 2.0)
    assert lower == 0.0
    assert np.isclose(upper, 2.0 - np.sqrt(2.0))
    assert student_t_tail_dependence(0.5, 4.0) > 0.0


def test_empirical_tail_dependence_detects_comonotonic_sample():
    sample = np.arange(1_000, dtype=float)
    estimate = empirical_tail_dependence(sample, sample, quantile=0.9)
    assert 0.98 <= estimate <= 1.02


def test_cross_entropy_importance_sampling_estimates_normal_tail():
    result = cross_entropy_gaussian_importance_sampling(
        [0.0],
        [[1.0]],
        lambda sample: sample[:, 0],
        3.0,
        adaptation_samples=3_000,
        evaluation_samples=30_000,
        iterations=6,
        seed=17,
    )
    truth = norm.sf(3.0)
    assert abs(result.probability - truth) <= 5.0 * result.standard_error
    assert result.standard_error < truth * 0.12
    assert result.effective_sample_size > 100.0
    assert result.proposal_mean[0] > 1.5
