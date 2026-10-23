import numpy as np

from rl.p14_tensor_completion_math import (
    complete_cp_weighted,
    complete_snn_halrtc,
    complete_tensor_train_projection,
    complete_tubal_tnn,
    complete_tucker_projection,
    completion_metrics,
    cp_reconstruct,
    fold,
    inverse_propensity_weighted_loss,
    missingness_diagnostics,
    tensor_train_svd,
    tubal_nuclear_prox,
    unfold,
)


def _rank_one_tensor():
    return np.einsum("i,j,k->ijk", [1.0, 2.0, 3.0], [1.0, 1.5, 2.0], [1.0, 0.5, 2.0])


def _mask_with_diagonal_holes(shape):
    mask = np.ones(shape, dtype=bool)
    for index in range(min(shape)):
        mask[index, index, index] = False
    return mask


def test_unfold_fold_round_trip_and_missingness_diagnostics():
    tensor = np.arange(24.0).reshape(2, 3, 4)
    for mode in range(3):
        assert np.array_equal(fold(unfold(tensor, mode), mode, tensor.shape), tensor)
    mask = np.ones_like(tensor, dtype=bool)
    mask[0] = False
    diagnostics = missingness_diagnostics(mask)
    assert diagnostics.observed_fraction == 0.5
    assert diagnostics.mode_zero_fibers[0] == 0
    assert diagnostics.completely_missing_slices[0] == 1


def test_cp_reconstruction_and_observed_entry_completion():
    truth = _rank_one_tensor()
    mask = _mask_with_diagonal_holes(truth.shape)
    result = complete_cp_weighted(truth, mask, rank=1, seed=4, max_iterations=2000)
    assert np.array_equal(result.completed[mask], truth[mask])
    assert result.observed_rmse < 1e-4
    assert completion_metrics(truth, result.completed, ~mask).relative_error < 1e-3
    assert cp_reconstruct(result.factors).shape == truth.shape


def test_snn_and_tucker_preserve_observations_and_recover_low_rank_tensor():
    truth = _rank_one_tensor()
    mask = _mask_with_diagonal_holes(truth.shape)
    snn = complete_snn_halrtc(truth, mask, rho=2.0, max_iterations=1000)
    tucker = complete_tucker_projection(truth, mask, [1, 1, 1], max_iterations=1000)
    assert snn.observed_rmse == 0.0
    assert np.array_equal(tucker.completed[mask], truth[mask])
    assert completion_metrics(truth, snn.completed, ~mask).relative_error < 0.15
    assert completion_metrics(truth, tucker.completed, ~mask).relative_error < 1e-3


def test_tensor_train_svd_and_completion():
    truth = _rank_one_tensor()
    train = tensor_train_svd(truth, [1, 1])
    assert train.relative_error < 1e-12
    assert np.allclose(train.reconstruct(), truth)
    mask = _mask_with_diagonal_holes(truth.shape)
    result = complete_tensor_train_projection(truth, mask, [1, 1], max_iterations=1000)
    assert np.array_equal(result.completed[mask], truth[mask])
    assert completion_metrics(truth, result.completed, ~mask).relative_error < 1e-3


def test_tubal_prox_and_tnn_completion():
    base = np.array([[1.0, 2.0], [2.0, 4.0]])
    truth = np.stack([base, 2.0 * base, 0.5 * base], axis=2)
    prox = tubal_nuclear_prox(truth, 0.0)
    assert np.allclose(prox, truth)
    mask = np.ones_like(truth, dtype=bool)
    mask[1, 1, 1] = False
    result = complete_tubal_tnn(truth, mask, rho=2.0, max_iterations=1000)
    assert np.array_equal(result.completed[mask], truth[mask])
    baseline = np.where(mask, truth, np.mean(truth[mask]))
    assert (
        completion_metrics(truth, result.completed, ~mask).rmse
        < completion_metrics(truth, baseline, ~mask).rmse
    )


def test_inverse_propensity_weighted_loss_and_metrics():
    truth = np.array([[1.0, 2.0], [3.0, 4.0]])
    estimate = truth + 1.0
    mask = np.array([[True, False], [True, False]])
    propensities = np.full_like(truth, 0.5)
    assert np.isclose(
        inverse_propensity_weighted_loss(truth, estimate, mask, propensities), 2.0
    )
    metrics = completion_metrics(truth, estimate, mask)
    assert metrics.rmse == 1.0 and metrics.mae == 1.0 and metrics.count == 2
