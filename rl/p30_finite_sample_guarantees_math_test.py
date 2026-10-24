import numpy as np

from rl.p30_finite_sample_guarantees_math import (
    anytime_hoeffding_confidence_sequence,
    binary_kl,
    conformal_risk_control,
    density_ratio_weights,
    effective_sample_size,
    empirical_bernstein_upper,
    pac_bayes_strategy_bound,
    pac_mdp_diagnostics,
    weighted_conformal_quantile,
)


def test_pac_mdp_diagnostic_counts_only_epsilon_violations():
    result = pac_mdp_diagnostics(
        [1.0, 0.7, 0.2], [1.0, 1.0, 1.0], epsilon=0.25, claimed_bad_step_bound=2
    )
    assert result.bad_steps == 2
    assert result.satisfies_claimed_bound
    assert np.isclose(result.maximum_gap, 0.8)


def test_pac_bayes_strategy_bound_contains_empirical_gibbs_risk():
    result = pac_bayes_strategy_bound(
        [0.1, 0.4], [0.8, 0.2], [0.5, 0.5], sample_size=200, delta=0.05
    )
    assert np.isclose(result.empirical_risk, 0.16)
    assert result.kl_to_prior > 0.0
    assert result.empirical_risk < result.upper_risk < 1.0
    assert binary_kl(result.empirical_risk, result.upper_risk) > 0.0


def test_empirical_bernstein_and_anytime_sequence_are_bounded():
    sample = np.tile([0.0, 1.0], 50)
    upper = empirical_bernstein_upper(sample, delta=0.05)
    sequence = anytime_hoeffding_confidence_sequence(sample, delta=0.05)
    assert 0.5 < upper <= 1.0
    assert np.all(sequence.lower >= 0.0)
    assert np.all(sequence.upper <= 1.0)
    assert sequence.radii[-1] < sequence.radii[0]
    assert sequence.lower[-1] <= 0.5 <= sequence.upper[-1]


def test_conformal_risk_control_selects_largest_feasible_control():
    losses = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0],
        ]
    )
    result = conformal_risk_control(
        losses, [0.1, 0.2, 0.3], risk_level=0.4
    )
    assert np.array_equal(result.feasible_indices, [0, 1])
    assert result.selected_index == 1
    assert result.selected_lambda == 0.2


def test_weighted_conformal_quantile_accounts_for_test_mass_at_infinity():
    finite = weighted_conformal_quantile(
        [1.0, 2.0, 3.0], [1.0, 1.0, 1.0], test_weight=0.2, alpha=0.25
    )
    infinite = weighted_conformal_quantile(
        [1.0, 2.0, 3.0], [1.0, 1.0, 1.0], test_weight=2.0, alpha=0.1
    )
    assert finite == 3.0
    assert np.isinf(infinite)


def test_density_ratio_weighting_reports_effective_sample_size():
    weights = density_ratio_weights([0.2, 0.4, 0.4], [0.2, 0.2, 0.6])
    assert np.allclose(weights, [1.0, 2.0, 2.0 / 3.0])
    assert 1.0 < effective_sample_size(weights) < 3.0
