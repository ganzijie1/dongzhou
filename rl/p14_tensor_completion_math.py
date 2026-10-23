"""P14 tensor completion with explicit masks and distinct rank models.

This module separates CP, Tucker, tensor-train, sum-of-unfolding nuclear norm,
and t-SVD/tubal-rank assumptions.  Missing entries are never treated as
observed zeroes, and every completion routine preserves supplied observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import minimize


def unfold(tensor: Sequence, mode: int) -> np.ndarray:
    value = np.asarray(tensor)
    if value.ndim == 0 or not 0 <= mode < value.ndim:
        raise ValueError("tensor unfolding mode is invalid")
    return np.moveaxis(value, mode, 0).reshape(value.shape[mode], -1)


def fold(
    matrix: Sequence[Sequence[float]], mode: int, shape: Sequence[int]
) -> np.ndarray:
    shape_value = tuple(int(value) for value in shape)
    array = np.asarray(matrix)
    if (
        not shape_value
        or any(value <= 0 for value in shape_value)
        or not 0 <= mode < len(shape_value)
        or array.shape
        != (shape_value[mode], int(np.prod(shape_value) // shape_value[mode]))
    ):
        raise ValueError("tensor fold dimensions are invalid")
    moved_shape = (shape_value[mode],) + shape_value[:mode] + shape_value[mode + 1 :]
    return np.moveaxis(array.reshape(moved_shape), 0, mode)


def mode_product(
    tensor: Sequence, matrix: Sequence[Sequence[float]], mode: int
) -> np.ndarray:
    value = np.asarray(tensor, dtype=np.float64)
    factor = np.asarray(matrix, dtype=np.float64)
    if (
        value.ndim == 0
        or not 0 <= mode < value.ndim
        or factor.ndim != 2
        or factor.shape[1] != value.shape[mode]
    ):
        raise ValueError("tensor mode-product dimensions are invalid")
    if np.any(~np.isfinite(value)) or np.any(~np.isfinite(factor)):
        raise ValueError("tensor mode-product inputs must be finite")
    result = np.tensordot(factor, value, axes=(1, mode))
    return np.moveaxis(result, 0, mode)


def _observations(tensor: Sequence, mask: Sequence) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(tensor, dtype=np.float64)
    observed = np.asarray(mask, dtype=bool)
    if (
        values.ndim < 2
        or values.size == 0
        or observed.shape != values.shape
        or not np.any(observed)
    ):
        raise ValueError("tensor observations need a non-empty aligned mask")
    if np.any(~np.isfinite(values[observed])):
        raise ValueError("observed tensor values must be finite")
    return values, observed


def _initial_fill(values: np.ndarray, observed: np.ndarray) -> np.ndarray:
    mean = float(np.mean(values[observed]))
    return np.where(observed, values, mean).astype(np.float64, copy=False)


@dataclass(frozen=True)
class MissingnessDiagnostics:
    observed_fraction: float
    mode_minimum_counts: tuple[int, ...]
    mode_zero_fibers: tuple[int, ...]
    completely_missing_slices: tuple[int, ...]


def missingness_diagnostics(mask: Sequence) -> MissingnessDiagnostics:
    observed = np.asarray(mask, dtype=bool)
    if observed.ndim < 2 or observed.size == 0:
        raise ValueError("missingness mask must be a non-empty tensor")
    minimum_counts = []
    zero_fibers = []
    missing_slices = []
    for mode in range(observed.ndim):
        unfolded = unfold(observed.astype(np.int64), mode)
        slice_counts = unfolded.sum(axis=1)
        fiber_counts = unfolded.sum(axis=0)
        minimum_counts.append(int(slice_counts.min()))
        zero_fibers.append(int(np.sum(fiber_counts == 0)))
        missing_slices.append(int(np.sum(slice_counts == 0)))
    return MissingnessDiagnostics(
        float(observed.mean()),
        tuple(minimum_counts),
        tuple(zero_fibers),
        tuple(missing_slices),
    )


@dataclass(frozen=True)
class CompletionMetrics:
    rmse: float
    mae: float
    relative_error: float
    count: int


def completion_metrics(
    truth: Sequence, estimate: Sequence, evaluation_mask: Sequence
) -> CompletionMetrics:
    expected = np.asarray(truth, dtype=np.float64)
    actual = np.asarray(estimate, dtype=np.float64)
    mask = np.asarray(evaluation_mask, dtype=bool)
    if (
        expected.shape != actual.shape
        or mask.shape != expected.shape
        or not np.any(mask)
    ):
        raise ValueError("completion metric arrays or mask are invalid")
    if np.any(~np.isfinite(expected[mask])) or np.any(~np.isfinite(actual[mask])):
        raise ValueError(
            "completion metric values must be finite on the evaluation mask"
        )
    residual = actual[mask] - expected[mask]
    denominator = float(np.linalg.norm(expected[mask]))
    norm = float(np.linalg.norm(residual))
    return CompletionMetrics(
        float(np.sqrt(np.mean(residual**2))),
        float(np.mean(np.abs(residual))),
        norm / denominator if denominator > 0.0 else norm,
        int(mask.sum()),
    )


def inverse_propensity_weighted_loss(
    truth: Sequence,
    estimate: Sequence,
    observed_mask: Sequence,
    propensities: Sequence,
) -> float:
    expected = np.asarray(truth, dtype=np.float64)
    actual = np.asarray(estimate, dtype=np.float64)
    observed = np.asarray(observed_mask, dtype=bool)
    probability = np.asarray(propensities, dtype=np.float64)
    if (
        expected.shape != actual.shape
        or observed.shape != expected.shape
        or probability.shape != expected.shape
    ):
        raise ValueError("inverse-propensity arrays have inconsistent shapes")
    if (
        not np.any(observed)
        or np.any(~np.isfinite(probability))
        or np.any(probability <= 0.0)
        or np.any(probability > 1.0)
    ):
        raise ValueError("observation propensities must lie in (0, 1]")
    residual = actual[observed] - expected[observed]
    return float(np.mean(residual**2 / probability[observed]))


def _singular_value_threshold(matrix: np.ndarray, threshold: float) -> np.ndarray:
    left, singular, right = np.linalg.svd(matrix, full_matrices=False)
    retained = np.maximum(singular - threshold, 0.0)
    return (left * retained) @ right


@dataclass(frozen=True)
class TensorCompletionResult:
    completed: np.ndarray
    iterations: int
    converged: bool
    observed_rmse: float
    history: tuple[float, ...]


def complete_snn_halrtc(
    tensor: Sequence,
    mask: Sequence,
    *,
    mode_weights: Sequence[float] | None = None,
    rho: float = 1.0,
    tolerance: float = 1e-6,
    max_iterations: int = 500,
) -> TensorCompletionResult:
    """HaLRTC-style ADMM for a sum of unfolding nuclear norms."""
    values, observed = _observations(tensor, mask)
    weights = np.asarray(
        mode_weights
        if mode_weights is not None
        else np.full(values.ndim, 1.0 / values.ndim),
        dtype=np.float64,
    )
    if (
        weights.shape != (values.ndim,)
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not np.isclose(weights.sum(), 1.0)
        or not isfinite(rho)
        or rho <= 0.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("HaLRTC weights or solver controls are invalid")
    completed = _initial_fill(values, observed)
    splits = [completed.copy() for _ in range(values.ndim)]
    duals = [np.zeros_like(completed) for _ in range(values.ndim)]
    history = []
    converged = False
    for iteration in range(1, max_iterations + 1):
        previous = completed.copy()
        for mode in range(values.ndim):
            splits[mode] = fold(
                _singular_value_threshold(
                    unfold(completed + duals[mode], mode), weights[mode] / rho
                ),
                mode,
                values.shape,
            )
        completed = (
            sum(split - dual for split, dual in zip(splits, duals)) / values.ndim
        )
        completed[observed] = values[observed]
        for mode in range(values.ndim):
            duals[mode] += completed - splits[mode]
        change = float(
            np.linalg.norm(completed - previous) / max(1.0, np.linalg.norm(previous))
        )
        history.append(change)
        if change <= tolerance:
            converged = True
            break
    observed_rmse = float(
        np.sqrt(np.mean((completed[observed] - values[observed]) ** 2))
    )
    return TensorCompletionResult(
        completed, iteration, converged, observed_rmse, tuple(history)
    )


def cp_reconstruct(factors: Sequence[Sequence[Sequence[float]]]) -> np.ndarray:
    arrays = tuple(np.asarray(factor, dtype=np.float64) for factor in factors)
    if len(arrays) < 2 or any(array.ndim != 2 for array in arrays):
        raise ValueError("CP factors must be a sequence of matrices")
    rank = arrays[0].shape[1]
    if rank == 0 or any(
        array.shape[1] != rank or np.any(~np.isfinite(array)) for array in arrays
    ):
        raise ValueError("CP factors must share one positive rank and be finite")
    result = np.zeros(tuple(array.shape[0] for array in arrays))
    for component in range(rank):
        term = arrays[0][:, component]
        for factor in arrays[1:]:
            term = np.multiply.outer(term, factor[:, component])
        result += term
    return result


@dataclass(frozen=True)
class CPCompletionResult:
    completed: np.ndarray
    factors: tuple[np.ndarray, ...]
    iterations: int
    converged: bool
    observed_rmse: float
    objective: float


def complete_cp_weighted(
    tensor: Sequence,
    mask: Sequence,
    rank: int,
    *,
    observation_weights: Sequence | None = None,
    regularization: float = 1e-6,
    seed: int = 0,
    tolerance: float = 1e-9,
    max_iterations: int = 1000,
) -> CPCompletionResult:
    """Fit CP factors directly to observed entries with analytic gradients."""
    values, observed = _observations(tensor, mask)
    if rank <= 0 or regularization < 0.0 or tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("CP completion rank or solver controls are invalid")
    weights = (
        np.ones(values.shape)
        if observation_weights is None
        else np.asarray(observation_weights, dtype=np.float64)
    )
    if (
        weights.shape != values.shape
        or np.any(~np.isfinite(weights[observed]))
        or np.any(weights[observed] <= 0.0)
    ):
        raise ValueError(
            "CP observation weights must be positive and finite on observations"
        )
    coordinates = np.argwhere(observed)
    targets = values[observed]
    observation_weight = weights[observed]
    random = np.random.default_rng(seed)
    shapes = [(dimension, rank) for dimension in values.shape]
    offsets = np.cumsum([0] + [int(np.prod(shape)) for shape in shapes])
    initial = np.concatenate(
        [random.normal(0.0, 0.2, size=shape).reshape(-1) for shape in shapes]
    )

    def unpack(vector: np.ndarray) -> tuple[np.ndarray, ...]:
        return tuple(
            vector[offsets[i] : offsets[i + 1]].reshape(shapes[i])
            for i in range(values.ndim)
        )

    def objective_gradient(vector: np.ndarray) -> tuple[float, np.ndarray]:
        factors = unpack(vector)
        selected = [factor[coordinates[:, mode]] for mode, factor in enumerate(factors)]
        component_products = np.ones((coordinates.shape[0], rank))
        for choice in selected:
            component_products *= choice
        prediction = component_products.sum(axis=1)
        residual = prediction - targets
        weighted_residual = observation_weight * residual
        objective = 0.5 * float(np.sum(observation_weight * residual**2))
        gradient_parts = []
        for mode, factor in enumerate(factors):
            other_product = np.ones_like(component_products)
            for other_mode, choice in enumerate(selected):
                if other_mode != mode:
                    other_product *= choice
            gradient = np.zeros_like(factor)
            np.add.at(
                gradient,
                coordinates[:, mode],
                weighted_residual[:, None] * other_product,
            )
            gradient += regularization * factor
            gradient_parts.append(gradient.reshape(-1))
            objective += 0.5 * regularization * float(np.sum(factor**2))
        return objective, np.concatenate(gradient_parts)

    solved = minimize(
        objective_gradient,
        initial,
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": max_iterations, "ftol": tolerance, "gtol": tolerance},
    )
    factors = unpack(solved.x)
    raw = cp_reconstruct(factors)
    completed = raw.copy()
    completed[observed] = values[observed]
    observed_rmse = float(np.sqrt(np.mean((raw[observed] - values[observed]) ** 2)))
    return CPCompletionResult(
        completed,
        factors,
        int(solved.nit),
        bool(solved.success),
        observed_rmse,
        float(solved.fun),
    )


def _truncated_tucker(
    tensor: np.ndarray, ranks: Sequence[int]
) -> tuple[np.ndarray, tuple[np.ndarray, ...], np.ndarray]:
    rank_values = tuple(int(value) for value in ranks)
    if len(rank_values) != tensor.ndim or any(
        rank <= 0 or rank > size for rank, size in zip(rank_values, tensor.shape)
    ):
        raise ValueError("Tucker multilinear ranks are invalid")
    factors = []
    for mode, rank in enumerate(rank_values):
        left, _, _ = np.linalg.svd(unfold(tensor, mode), full_matrices=False)
        factors.append(left[:, :rank])
    core = tensor.copy()
    for mode, factor in enumerate(factors):
        core = mode_product(core, factor.T, mode)
    reconstruction = core.copy()
    for mode, factor in enumerate(factors):
        reconstruction = mode_product(reconstruction, factor, mode)
    return core, tuple(factors), reconstruction


def complete_tucker_projection(
    tensor: Sequence,
    mask: Sequence,
    ranks: Sequence[int],
    *,
    tolerance: float = 1e-7,
    max_iterations: int = 500,
) -> TensorCompletionResult:
    values, observed = _observations(tensor, mask)
    completed = _initial_fill(values, observed)
    history = []
    converged = False
    for iteration in range(1, max_iterations + 1):
        previous = completed.copy()
        _, _, projected = _truncated_tucker(completed, ranks)
        completed = projected
        completed[observed] = values[observed]
        change = float(
            np.linalg.norm(completed - previous) / max(1.0, np.linalg.norm(previous))
        )
        history.append(change)
        if change <= tolerance:
            converged = True
            break
    return TensorCompletionResult(completed, iteration, converged, 0.0, tuple(history))


@dataclass(frozen=True)
class TensorTrain:
    cores: tuple[np.ndarray, ...]
    relative_error: float

    def reconstruct(self) -> np.ndarray:
        result = self.cores[0]
        for core in self.cores[1:]:
            result = np.tensordot(result, core, axes=(-1, 0))
        return np.squeeze(result, axis=(0, -1))


def tensor_train_svd(tensor: Sequence, ranks: Sequence[int]) -> TensorTrain:
    value = np.asarray(tensor, dtype=np.float64)
    rank_values = tuple(int(rank) for rank in ranks)
    if (
        value.ndim < 2
        or len(rank_values) != value.ndim - 1
        or np.any(~np.isfinite(value))
    ):
        raise ValueError("TT-SVD tensor or internal ranks are invalid")
    current = value.copy()
    cores = []
    previous_rank = 1
    for mode in range(value.ndim - 1):
        matrix = current.reshape(previous_rank * value.shape[mode], -1)
        left, singular, right = np.linalg.svd(matrix, full_matrices=False)
        rank = rank_values[mode]
        if rank <= 0 or rank > singular.size:
            raise ValueError("TT rank exceeds an unfolding dimension")
        cores.append(left[:, :rank].reshape(previous_rank, value.shape[mode], rank))
        current = singular[:rank, None] * right[:rank]
        previous_rank = rank
    cores.append(current.reshape(previous_rank, value.shape[-1], 1))
    train = TensorTrain(tuple(cores), 0.0)
    denominator = float(np.linalg.norm(value))
    error = float(np.linalg.norm(value - train.reconstruct()))
    return TensorTrain(train.cores, error / denominator if denominator > 0.0 else error)


def complete_tensor_train_projection(
    tensor: Sequence,
    mask: Sequence,
    ranks: Sequence[int],
    *,
    tolerance: float = 1e-7,
    max_iterations: int = 500,
) -> TensorCompletionResult:
    values, observed = _observations(tensor, mask)
    completed = _initial_fill(values, observed)
    history = []
    converged = False
    for iteration in range(1, max_iterations + 1):
        previous = completed.copy()
        completed = tensor_train_svd(completed, ranks).reconstruct()
        completed[observed] = values[observed]
        change = float(
            np.linalg.norm(completed - previous) / max(1.0, np.linalg.norm(previous))
        )
        history.append(change)
        if change <= tolerance:
            converged = True
            break
    return TensorCompletionResult(completed, iteration, converged, 0.0, tuple(history))


def tubal_nuclear_prox(tensor: Sequence, threshold: float) -> np.ndarray:
    value = np.asarray(tensor, dtype=np.float64)
    if (
        value.ndim != 3
        or np.any(~np.isfinite(value))
        or not isfinite(threshold)
        or threshold < 0.0
    ):
        raise ValueError("t-SVD proximal input must be a finite third-order tensor")
    spectrum = np.fft.fft(value, axis=2)
    result = np.empty_like(spectrum)
    for index in range(value.shape[2]):
        left, singular, right = np.linalg.svd(
            spectrum[:, :, index], full_matrices=False
        )
        result[:, :, index] = (left * np.maximum(singular - threshold, 0.0)) @ right
    return np.fft.ifft(result, axis=2).real


def complete_tubal_tnn(
    tensor: Sequence,
    mask: Sequence,
    *,
    rho: float = 1.0,
    rho_growth: float = 1.0,
    tolerance: float = 1e-6,
    max_iterations: int = 500,
) -> TensorCompletionResult:
    """ADMM completion under the FFT/t-SVD tubal nuclear norm."""
    values, observed = _observations(tensor, mask)
    if (
        values.ndim != 3
        or rho <= 0.0
        or rho_growth < 1.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError(
            "TNN completion needs a third-order tensor and valid solver controls"
        )
    completed = _initial_fill(values, observed)
    low_rank = completed.copy()
    dual = np.zeros_like(completed)
    penalty = float(rho)
    history = []
    converged = False
    for iteration in range(1, max_iterations + 1):
        previous = completed.copy()
        low_rank = tubal_nuclear_prox(completed + dual, 1.0 / penalty)
        completed = low_rank - dual
        completed[observed] = values[observed]
        dual += completed - low_rank
        penalty *= rho_growth
        # Keep the unscaled multiplier rho * dual unchanged when rho changes.
        dual /= rho_growth
        change = float(
            np.linalg.norm(completed - previous) / max(1.0, np.linalg.norm(previous))
        )
        history.append(change)
        if change <= tolerance:
            converged = True
            break
    return TensorCompletionResult(completed, iteration, converged, 0.0, tuple(history))
