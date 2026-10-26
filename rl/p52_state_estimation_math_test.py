import numpy as np

from rl.p52_state_estimation_math import (
    ekf_predict,
    ekf_update,
    hinfinity_information_covariance,
    imm_mixing_probabilities,
    particle_filter_update,
    scaled_sigma_points,
    unscented_transform,
)


def test_linear_ekf_predict_and_update_reduce_uncertainty():
    predicted = ekf_predict([0.0], [[1.0]], lambda x: x + 1.0, lambda x: [[1.0]], [[0.1]])
    updated = ekf_update(predicted.mean, predicted.covariance, [1.2], lambda x: x, lambda x: [[1.0]], [[0.2]])
    assert np.allclose(predicted.mean, [1.0])
    assert updated.mean[0] > 1.0
    assert updated.covariance[0, 0] < predicted.covariance[0, 0]


def test_unscented_sigma_points_recover_mean_and_covariance():
    points, wm, wc = scaled_sigma_points([1.0, -2.0], [[2.0, 0.3], [0.3, 1.0]], alpha=0.5)
    estimate = unscented_transform(points, wm, wc)
    assert np.allclose(estimate.mean, [1.0, -2.0])
    assert np.allclose(estimate.covariance, [[2.0, 0.3], [0.3, 1.0]])


def test_particle_resampling_and_imm_mixing_are_normalized():
    rng = np.random.default_rng(7)
    update = particle_filter_update([[0.0], [1.0], [2.0], [3.0]], [0.25] * 4, [1.0, 0.0, 0.0, 0.0], rng=rng)
    assert update.resampled
    assert np.all(update.particles == 0.0)
    predicted, mixing = imm_mixing_probabilities([0.75, 0.25], [[0.8, 0.2], [0.4, 0.6]])
    assert np.allclose(predicted, [0.7, 0.3])
    assert np.allclose(mixing.sum(axis=0), 1.0)


def test_hinfinity_large_gamma_approaches_information_filter_update():
    covariance = hinfinity_information_covariance([[1.0]], [[1.0]], [[1.0]], gamma=1e6)
    assert np.allclose(covariance, [[0.5]], atol=1e-10)
