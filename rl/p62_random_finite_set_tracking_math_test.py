import numpy as np

from rl.p62_random_finite_set_tracking_math import jpda_marginals, phd_measurement_update, phd_predict, prune_hypotheses


def test_jpda_enforces_one_measurement_per_target():
    marginals = jpda_marginals([[9.0], [1.0]], [1.0, 1.0])
    assert np.allclose(marginals.sum(axis=1), 1.0)
    assert marginals[0, 1] > marginals[1, 1]


def test_phd_prediction_and_update_preserve_intensity_semantics():
    predicted = phd_predict([0.8, 0.2], 0.5, [0.1])
    assert np.allclose(predicted, [0.4, 0.1, 0.1])
    updated = phd_measurement_update(predicted, [1, 1, 1], [1, 0, 0], 0.1)
    assert np.allclose(updated, [0.8, 0.0, 0.0])


def test_hypothesis_pruning_renormalizes():
    indices, weights = prune_hypotheses([0.1, 0.6, 0.3], maximum=2)
    assert set(indices) == {1, 2} and np.isclose(weights.sum(), 1.0)
