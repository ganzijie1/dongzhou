import numpy as np

from rl.p53_marked_point_process_math import (
    branching_ratio,
    exponential_hawkes_log_likelihood,
    marked_exponential_intensity,
    total_compensator_increments,
)


def test_marked_intensity_supports_cross_excitation_and_inhibition():
    result = marked_exponential_intensity(
        2.0,
        [1.0],
        [0],
        [1.0, 2.0],
        [[1.0, 0.0], [-0.5, 0.0]],
        [[1.0, 1.0], [1.0, 1.0]],
    )
    assert np.allclose(result.raw_intensity, [1.0 + np.exp(-1.0), 2.0 - 0.5 * np.exp(-1.0)])
    assert np.all(result.intensity >= 0.0)


def test_poisson_special_case_has_expected_log_likelihood_and_residuals():
    likelihood = exponential_hawkes_log_likelihood([1.0, 2.0], [0, 0], [1.0], [[0.0]], [[1.0]], 3.0)
    assert np.isclose(likelihood, -3.0)
    increments = total_compensator_increments([1.0, 3.0], [0, 0], [2.0], [[0.0]], [[1.0]])
    assert np.allclose(increments, [2.0, 4.0])


def test_branching_ratio_audits_stationarity_threshold():
    offspring, radius = branching_ratio([[0.2, 0.0], [0.1, 0.3]], [[1.0, 1.0], [1.0, 1.0]])
    assert np.allclose(offspring, [[0.2, 0.0], [0.1, 0.3]])
    assert np.isclose(radius, 0.3)
