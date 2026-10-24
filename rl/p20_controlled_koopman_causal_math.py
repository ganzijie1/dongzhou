"""P20 controlled Koopman models, viability, and causal discovery diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import isfinite
from typing import Callable, Sequence

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.stats import f_oneway, levene, norm, t


@dataclass(frozen=True)
class DMDcResult:
    state_matrix: np.ndarray
    control_matrix: np.ndarray
    singular_values: np.ndarray
    relative_residual: float
    rank: int

    def predict(self, state: Sequence[float], control: Sequence[float]) -> np.ndarray:
        state_array = np.asarray(state, dtype=np.float64)
        control_array = np.asarray(control, dtype=np.float64)
        if (
            state_array.shape != (self.state_matrix.shape[1],)
            or control_array.shape != (self.control_matrix.shape[1],)
        ):
            raise ValueError("DMDc prediction dimensions are inconsistent")
        return self.state_matrix @ state_array + self.control_matrix @ control_array


def dynamic_mode_decomposition_with_control(
    current_snapshots: Sequence,
    controls: Sequence,
    next_snapshots: Sequence,
    *,
    rank: int | None = None,
) -> DMDcResult:
    """Least-squares DMDc for column-oriented snapshot matrices."""

    current = np.asarray(current_snapshots, dtype=np.float64)
    control = np.asarray(controls, dtype=np.float64)
    future = np.asarray(next_snapshots, dtype=np.float64)
    if (
        current.ndim != 2
        or control.ndim != 2
        or future.shape != current.shape
        or current.shape[1] == 0
        or control.shape[1] != current.shape[1]
        or np.any(~np.isfinite(current))
        or np.any(~np.isfinite(control))
        or np.any(~np.isfinite(future))
    ):
        raise ValueError("DMDc snapshots are inconsistent")
    augmented = np.vstack((current, control))
    left, singular, right = np.linalg.svd(augmented, full_matrices=False)
    if rank is None:
        tolerance = max(augmented.shape) * np.finfo(float).eps * singular[0]
        retained = int(np.count_nonzero(singular > tolerance))
    else:
        if rank <= 0:
            raise ValueError("DMDc rank must be positive")
        retained = min(rank, singular.size)
    if retained == 0:
        raise ValueError("DMDc augmented snapshots have zero numerical rank")
    inverse = right[:retained].T @ np.diag(1.0 / singular[:retained]) @ left[:, :retained].T
    operator = future @ inverse
    state_dimension = current.shape[0]
    state_matrix = operator[:, :state_dimension]
    control_matrix = operator[:, state_dimension:]
    residual = np.linalg.norm(future - operator @ augmented) / max(
        1.0, np.linalg.norm(future)
    )
    return DMDcResult(
        state_matrix,
        control_matrix,
        singular,
        float(residual),
        retained,
    )


@dataclass(frozen=True)
class EDMDcResult:
    koopman_matrix: np.ndarray
    control_matrix: np.ndarray
    lifted_current: np.ndarray
    lifted_next: np.ndarray
    relative_residual: float
    observables: tuple[Callable[[np.ndarray], float], ...]

    def lift(self, state: Sequence[float]) -> np.ndarray:
        values = np.asarray(state, dtype=np.float64)
        return np.asarray(
            [observable(values) for observable in self.observables], dtype=np.float64
        )


def extended_dynamic_mode_decomposition_with_control(
    current_states: Sequence,
    controls: Sequence,
    next_states: Sequence,
    observables: Sequence[Callable[[np.ndarray], float]],
    *,
    ridge: float = 0.0,
) -> EDMDcResult:
    """EDMDc using caller-supplied scalar observables and ridge regression."""

    current = np.asarray(current_states, dtype=np.float64)
    control = np.asarray(controls, dtype=np.float64)
    future = np.asarray(next_states, dtype=np.float64)
    if (
        current.ndim != 2
        or future.shape != current.shape
        or control.ndim != 2
        or control.shape[0] != current.shape[0]
        or current.shape[0] == 0
        or not observables
        or np.any(~np.isfinite(current))
        or np.any(~np.isfinite(control))
        or np.any(~np.isfinite(future))
        or not isfinite(ridge)
        or ridge < 0.0
    ):
        raise ValueError("EDMDc inputs are invalid")

    def lift_samples(samples: np.ndarray) -> np.ndarray:
        lifted = np.asarray(
            [[observable(sample) for observable in observables] for sample in samples],
            dtype=np.float64,
        )
        if lifted.shape != (samples.shape[0], len(observables)) or np.any(
            ~np.isfinite(lifted)
        ):
            raise ValueError("EDMDc observables must return finite scalars")
        return lifted.T

    lifted_current = lift_samples(current)
    lifted_next = lift_samples(future)
    augmented = np.vstack((lifted_current, control.T))
    gram = augmented @ augmented.T + ridge * np.eye(augmented.shape[0])
    operator = lifted_next @ augmented.T @ np.linalg.pinv(gram)
    observable_count = len(observables)
    prediction = operator @ augmented
    residual = np.linalg.norm(lifted_next - prediction) / max(
        1.0, np.linalg.norm(lifted_next)
    )
    return EDMDcResult(
        operator[:, :observable_count],
        operator[:, observable_count:],
        lifted_current,
        lifted_next,
        float(residual),
        tuple(observables),
    )


@dataclass(frozen=True)
class KoopmanMPCResult:
    controls: np.ndarray
    trajectory: np.ndarray
    cost: float
    sequences_evaluated: int


def koopman_mpc(
    koopman_matrix: Sequence[Sequence[float]],
    control_matrix: Sequence[Sequence[float]],
    initial_lifted_state: Sequence[float],
    control_candidates: Sequence[Sequence[float]],
    target_lifted_state: Sequence[float],
    state_cost: Sequence[Sequence[float]],
    control_cost: Sequence[Sequence[float]],
    *,
    horizon: int,
    terminal_cost: Sequence[Sequence[float]] | None = None,
    max_sequences: int = 1_000_000,
) -> KoopmanMPCResult:
    """Enumerate finite controls for quadratic MPC in lifted coordinates."""

    operator = np.asarray(koopman_matrix, dtype=np.float64)
    control_operator = np.asarray(control_matrix, dtype=np.float64)
    initial = np.asarray(initial_lifted_state, dtype=np.float64)
    candidates = np.asarray(control_candidates, dtype=np.float64)
    target = np.asarray(target_lifted_state, dtype=np.float64)
    q = np.asarray(state_cost, dtype=np.float64)
    r = np.asarray(control_cost, dtype=np.float64)
    terminal = q if terminal_cost is None else np.asarray(terminal_cost, dtype=np.float64)
    if (
        operator.ndim != 2
        or operator.shape[0] != operator.shape[1]
        or control_operator.ndim != 2
        or control_operator.shape[0] != operator.shape[0]
        or initial.shape != (operator.shape[0],)
        or target.shape != initial.shape
        or candidates.ndim != 2
        or candidates.shape[0] == 0
        or candidates.shape[1] != control_operator.shape[1]
        or q.shape != operator.shape
        or terminal.shape != operator.shape
        or r.shape != (control_operator.shape[1], control_operator.shape[1])
        or any(
            np.any(~np.isfinite(value))
            for value in (operator, control_operator, initial, candidates, target, q, r, terminal)
        )
        or horizon <= 0
        or max_sequences <= 0
    ):
        raise ValueError("Koopman MPC inputs are invalid")
    sequence_count = candidates.shape[0] ** horizon
    if sequence_count > max_sequences:
        raise ValueError("Koopman MPC sequence budget exceeded")
    best_controls = None
    best_trajectory = None
    best_cost = np.inf
    best_indices = None
    for indices in product(range(candidates.shape[0]), repeat=horizon):
        state = initial.copy()
        trajectory = [state.copy()]
        cost = 0.0
        controls = []
        for index in indices:
            control = candidates[index]
            difference = state - target
            cost += float(difference @ q @ difference + control @ r @ control)
            state = operator @ state + control_operator @ control
            trajectory.append(state.copy())
            controls.append(control.copy())
        difference = state - target
        cost += float(difference @ terminal @ difference)
        if cost < best_cost - 1e-12 or (
            np.isclose(cost, best_cost) and (best_indices is None or indices < best_indices)
        ):
            best_cost = cost
            best_controls = np.asarray(controls)
            best_trajectory = np.asarray(trajectory)
            best_indices = indices
    return KoopmanMPCResult(
        best_controls, best_trajectory, best_cost, sequence_count
    )


@dataclass(frozen=True)
class UlamTransferResult:
    transition_matrix: np.ndarray
    stationary_distribution: np.ndarray
    current_bins: np.ndarray
    next_bins: np.ndarray
    discarded_samples: int


def ulam_transfer_operator(
    current_states: Sequence,
    next_states: Sequence,
    bin_edges: Sequence[Sequence[float]],
    *,
    pseudocount: float = 0.0,
) -> UlamTransferResult:
    """Estimate a Perron-Frobenius/Ulam Markov operator on a rectangular grid."""

    current = np.asarray(current_states, dtype=np.float64)
    future = np.asarray(next_states, dtype=np.float64)
    if (
        current.ndim != 2
        or future.shape != current.shape
        or current.shape[0] == 0
        or len(bin_edges) != current.shape[1]
        or np.any(~np.isfinite(current))
        or np.any(~np.isfinite(future))
        or not isfinite(pseudocount)
        or pseudocount < 0.0
    ):
        raise ValueError("Ulam inputs are invalid")
    edges = tuple(np.asarray(value, dtype=np.float64) for value in bin_edges)
    if any(
        value.ndim != 1
        or value.size < 2
        or np.any(~np.isfinite(value))
        or not np.all(np.diff(value) > 0.0)
        for value in edges
    ):
        raise ValueError("Ulam bin edges are invalid")
    bin_counts = tuple(value.size - 1 for value in edges)

    def assign(samples: np.ndarray) -> np.ndarray:
        coordinates = []
        valid = np.ones(samples.shape[0], dtype=bool)
        for dimension, dimension_edges in enumerate(edges):
            coordinate = np.searchsorted(
                dimension_edges, samples[:, dimension], side="right"
            ) - 1
            coordinate[samples[:, dimension] == dimension_edges[-1]] = (
                dimension_edges.size - 2
            )
            valid &= (coordinate >= 0) & (coordinate < dimension_edges.size - 1)
            coordinates.append(coordinate)
        result = np.full(samples.shape[0], -1, dtype=np.int64)
        if np.any(valid):
            result[valid] = np.ravel_multi_index(
                tuple(coordinate[valid] for coordinate in coordinates), bin_counts
            )
        return result

    current_bins = assign(current)
    next_bins = assign(future)
    valid = (current_bins >= 0) & (next_bins >= 0)
    total_bins = int(np.prod(bin_counts))
    counts = np.full((total_bins, total_bins), pseudocount)
    for source, target in zip(current_bins[valid], next_bins[valid], strict=True):
        counts[source, target] += 1.0
    transition = np.zeros_like(counts)
    row_mass = counts.sum(axis=1)
    for state in range(total_bins):
        if row_mass[state] > 0.0:
            transition[state] = counts[state] / row_mass[state]
        else:
            transition[state, state] = 1.0
    eigenvalues, eigenvectors = np.linalg.eig(transition.T)
    stationary_index = int(np.argmin(np.abs(eigenvalues - 1.0)))
    stationary = np.maximum(eigenvectors[:, stationary_index].real, 0.0)
    if stationary.sum() <= 1e-15:
        stationary = np.abs(eigenvectors[:, stationary_index].real)
    stationary /= stationary.sum()
    return UlamTransferResult(
        transition,
        stationary,
        current_bins,
        next_bins,
        int(np.count_nonzero(~valid)),
    )


@dataclass(frozen=True)
class ViabilityKernelResult:
    viable_states: tuple[int, ...]
    viable_actions: tuple[tuple[int, ...], ...]
    iterations: int
    minimum_probability: float


def stochastic_viability_kernel(
    transition: Sequence,
    safe_states: Sequence[int] | Sequence[bool],
    *,
    minimum_probability: float = 1.0,
) -> ViabilityKernelResult:
    """Greatest controlled-invariant subset under a one-step probability level."""

    kernel = np.asarray(transition, dtype=np.float64)
    if kernel.ndim != 3:
        raise ValueError("viability transition must be three-dimensional")
    states, actions, next_states = kernel.shape
    safe_array = np.asarray(safe_states)
    if safe_array.dtype == bool:
        if safe_array.shape != (states,):
            raise ValueError("viability safe mask has the wrong shape")
        safe = safe_array.copy()
    else:
        safe = np.zeros(states, dtype=bool)
        indices = [int(value) for value in safe_states]
        if any(value < 0 or value >= states for value in indices):
            raise ValueError("viability safe state is out of range")
        safe[indices] = True
    if (
        next_states != states
        or np.any(~np.isfinite(kernel))
        or np.any(kernel < 0.0)
        or not np.allclose(kernel.sum(axis=2), 1.0)
        or not 0.0 <= minimum_probability <= 1.0
    ):
        raise ValueError("viability inputs are invalid")
    viable = safe.copy()
    for iteration in range(1, states + 2):
        next_viable = viable.copy()
        for state in np.flatnonzero(viable):
            probabilities = kernel[state, :, viable].sum(axis=1)
            if np.max(probabilities, initial=0.0) < minimum_probability - 1e-12:
                next_viable[state] = False
        if np.array_equal(next_viable, viable):
            break
        viable = next_viable
    viable_actions = []
    for state in range(states):
        if not viable[state]:
            viable_actions.append(())
            continue
        probabilities = kernel[state, :, viable].sum(axis=1)
        viable_actions.append(
            tuple(
                int(action)
                for action in np.flatnonzero(
                    probabilities >= minimum_probability - 1e-12
                )
            )
        )
    return ViabilityKernelResult(
        tuple(int(value) for value in np.flatnonzero(viable)),
        tuple(viable_actions),
        iteration,
        minimum_probability,
    )


@dataclass(frozen=True)
class NotearsResult:
    adjacency: np.ndarray
    acyclicity: float
    loss: float
    iterations: int
    converged: bool


def notears_linear(
    samples: Sequence[Sequence[float]],
    *,
    l1_penalty: float = 0.01,
    edge_threshold: float = 0.05,
    acyclicity_tolerance: float = 1e-8,
    max_outer_iterations: int = 20,
) -> NotearsResult:
    """Linear NOTEARS with an augmented Lagrangian acyclicity constraint."""

    data = np.asarray(samples, dtype=np.float64)
    if (
        data.ndim != 2
        or data.shape[0] < 2
        or data.shape[1] < 2
        or np.any(~np.isfinite(data))
        or l1_penalty < 0.0
        or edge_threshold < 0.0
        or acyclicity_tolerance <= 0.0
        or max_outer_iterations <= 0
    ):
        raise ValueError("NOTEARS inputs are invalid")
    observations, variables = data.shape
    centered = data - data.mean(axis=0, keepdims=True)
    rho = 1.0
    alpha = 0.0
    previous_h = np.inf
    weights = np.zeros((variables, variables))
    bounds = [
        (0.0, 0.0) if row == column else (None, None)
        for row in range(variables)
        for column in range(variables)
    ]

    def loss_gradient(matrix: np.ndarray) -> tuple[float, np.ndarray]:
        residual = centered - centered @ matrix
        loss = 0.5 / observations * float(np.sum(residual**2))
        gradient = -(centered.T @ residual) / observations
        return loss, gradient

    def acyclicity(matrix: np.ndarray) -> tuple[float, np.ndarray]:
        exponential = expm(matrix * matrix)
        value = float(np.trace(exponential) - variables)
        gradient = exponential.T * (2.0 * matrix)
        return value, gradient

    iteration = 0
    for iteration in range(1, max_outer_iterations + 1):
        while rho < 1e16:
            def augmented(flat: np.ndarray) -> tuple[float, np.ndarray]:
                matrix = flat.reshape(variables, variables)
                loss, loss_grad = loss_gradient(matrix)
                h, h_grad = acyclicity(matrix)
                smooth_abs = np.sqrt(matrix**2 + 1e-12)
                objective = (
                    loss
                    + l1_penalty * float(smooth_abs.sum())
                    + alpha * h
                    + 0.5 * rho * h * h
                )
                gradient = (
                    loss_grad
                    + l1_penalty * matrix / smooth_abs
                    + (alpha + rho * h) * h_grad
                )
                return objective, gradient.ravel()

            solved = minimize(
                lambda value: augmented(value)[0],
                weights.ravel(),
                jac=lambda value: augmented(value)[1],
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": 1_000, "ftol": 1e-12},
            )
            weights = solved.x.reshape(variables, variables)
            h, _ = acyclicity(weights)
            if h <= 0.25 * previous_h:
                break
            rho *= 10.0
        alpha += rho * h
        previous_h = h
        if h <= acyclicity_tolerance:
            break
    adjacency = weights.copy()
    adjacency[np.abs(adjacency) < edge_threshold] = 0.0
    np.fill_diagonal(adjacency, 0.0)
    h, _ = acyclicity(adjacency)
    loss, _ = loss_gradient(adjacency)
    return NotearsResult(
        adjacency,
        h,
        loss,
        iteration,
        h <= acyclicity_tolerance,
    )


@dataclass(frozen=True)
class PartialCorrelationResult:
    correlation: float
    z_statistic: float
    p_value: float
    degrees_of_freedom: int


def partial_correlation_test(
    samples: Sequence[Sequence[float]],
    left: int,
    right: int,
    conditioning: Sequence[int] = (),
) -> PartialCorrelationResult:
    """Gaussian partial-correlation conditional-independence test."""

    data = np.asarray(samples, dtype=np.float64)
    condition = tuple(dict.fromkeys(int(value) for value in conditioning))
    if (
        data.ndim != 2
        or data.shape[0] < 4
        or np.any(~np.isfinite(data))
        or not 0 <= left < data.shape[1]
        or not 0 <= right < data.shape[1]
        or left == right
        or left in condition
        or right in condition
        or any(value < 0 or value >= data.shape[1] for value in condition)
    ):
        raise ValueError("partial-correlation inputs are invalid")
    if condition:
        design = np.c_[np.ones(data.shape[0]), data[:, condition]]
        left_residual = data[:, left] - design @ np.linalg.lstsq(
            design, data[:, left], rcond=None
        )[0]
        right_residual = data[:, right] - design @ np.linalg.lstsq(
            design, data[:, right], rcond=None
        )[0]
    else:
        left_residual = data[:, left] - data[:, left].mean()
        right_residual = data[:, right] - data[:, right].mean()
    correlation = float(np.corrcoef(left_residual, right_residual)[0, 1])
    correlation = float(np.clip(correlation, -1.0 + 1e-12, 1.0 - 1e-12))
    degrees = data.shape[0] - len(condition) - 3
    if degrees <= 0:
        raise ValueError("not enough samples for conditioned correlation test")
    statistic = np.sqrt(degrees) * np.arctanh(correlation)
    p_value = 2.0 * float(norm.sf(abs(statistic)))
    return PartialCorrelationResult(correlation, float(statistic), p_value, degrees)


@dataclass(frozen=True)
class PCSkeletonResult:
    adjacency: np.ndarray
    separating_sets: dict[tuple[int, int], tuple[int, ...]]
    tests_performed: int


def pc_skeleton(
    samples: Sequence[Sequence[float]],
    *,
    significance: float = 0.05,
    maximum_conditioning: int | None = None,
) -> PCSkeletonResult:
    """PC-stable style Gaussian skeleton discovery without edge orientation."""

    data = np.asarray(samples, dtype=np.float64)
    if (
        data.ndim != 2
        or data.shape[1] < 2
        or np.any(~np.isfinite(data))
        or not 0.0 < significance < 1.0
    ):
        raise ValueError("PC skeleton inputs are invalid")
    variables = data.shape[1]
    maximum = variables - 2 if maximum_conditioning is None else maximum_conditioning
    if maximum < 0:
        raise ValueError("maximum conditioning size cannot be negative")
    adjacency = np.ones((variables, variables), dtype=bool)
    np.fill_diagonal(adjacency, False)
    separating: dict[tuple[int, int], tuple[int, ...]] = {}
    tests = 0
    for size in range(maximum + 1):
        snapshot = adjacency.copy()
        any_testable = False
        for left in range(variables):
            for right in range(left + 1, variables):
                if not snapshot[left, right]:
                    continue
                neighbors = [
                    value
                    for value in range(variables)
                    if value != right and snapshot[left, value]
                ]
                if len(neighbors) < size:
                    continue
                any_testable = True
                for condition in combinations(neighbors, size):
                    tests += 1
                    result = partial_correlation_test(
                        data, left, right, condition
                    )
                    if result.p_value > significance:
                        adjacency[left, right] = adjacency[right, left] = False
                        separating[(left, right)] = tuple(condition)
                        separating[(right, left)] = tuple(condition)
                        break
        if not any_testable:
            break
    return PCSkeletonResult(adjacency, separating, tests)


@dataclass(frozen=True)
class InvariantCausalPredictionResult:
    accepted_sets: tuple[tuple[int, ...], ...]
    invariant_predictors: tuple[int, ...]
    p_values: dict[tuple[int, ...], tuple[float, float]]


def invariant_causal_prediction(
    environments: Sequence[Sequence[Sequence[float]]],
    target: int,
    candidate_predictors: Sequence[int],
    *,
    significance: float = 0.05,
    maximum_subset_size: int | None = None,
) -> InvariantCausalPredictionResult:
    """Small linear ICP by residual mean/variance invariance tests."""

    samples = tuple(np.asarray(value, dtype=np.float64) for value in environments)
    predictors = tuple(dict.fromkeys(int(value) for value in candidate_predictors))
    if (
        len(samples) < 2
        or any(value.ndim != 2 or value.shape[0] < 3 for value in samples)
        or len({value.shape[1] for value in samples}) != 1
        or any(np.any(~np.isfinite(value)) for value in samples)
        or not 0 <= target < samples[0].shape[1]
        or target in predictors
        or any(value < 0 or value >= samples[0].shape[1] for value in predictors)
        or not 0.0 < significance < 1.0
    ):
        raise ValueError("ICP inputs are invalid")
    maximum = len(predictors) if maximum_subset_size is None else maximum_subset_size
    if not 0 <= maximum <= len(predictors):
        raise ValueError("ICP maximum subset size is invalid")
    pooled = np.vstack(samples)
    accepted = []
    p_values = {}
    for size in range(maximum + 1):
        for subset in combinations(predictors, size):
            if subset:
                design = np.c_[np.ones(pooled.shape[0]), pooled[:, subset]]
            else:
                design = np.ones((pooled.shape[0], 1))
            coefficient = np.linalg.lstsq(design, pooled[:, target], rcond=None)[0]
            residuals = []
            for environment in samples:
                local_design = (
                    np.c_[np.ones(environment.shape[0]), environment[:, subset]]
                    if subset
                    else np.ones((environment.shape[0], 1))
                )
                residuals.append(
                    environment[:, target] - local_design @ coefficient
                )
            mean_p = float(f_oneway(*residuals).pvalue)
            variance_p = float(levene(*residuals, center="median").pvalue)
            p_values[subset] = (mean_p, variance_p)
            if min(mean_p, variance_p) >= significance:
                accepted.append(subset)
    if not accepted:
        invariant = ()
    else:
        invariant_set = set(accepted[0])
        for subset in accepted[1:]:
            invariant_set &= set(subset)
        invariant = tuple(value for value in predictors if value in invariant_set)
    return InvariantCausalPredictionResult(tuple(accepted), invariant, p_values)


@dataclass(frozen=True)
class OmittedVariableSensitivityResult:
    adjusted_estimate_interval: tuple[float, float]
    confidence_interval: tuple[float, float]
    maximum_bias: float
    adjusted_standard_error: float


def omitted_variable_sensitivity(
    estimate: float,
    standard_error: float,
    degrees_of_freedom: int,
    *,
    treatment_confounder_partial_r2: float,
    outcome_confounder_partial_r2: float,
    confidence: float = 0.95,
) -> OmittedVariableSensitivityResult:
    """Conservative omitted-variable bias interval from partial-R2 strengths."""

    r2_treatment = float(treatment_confounder_partial_r2)
    r2_outcome = float(outcome_confounder_partial_r2)
    if (
        not isfinite(estimate)
        or not isfinite(standard_error)
        or standard_error < 0.0
        or degrees_of_freedom <= 0
        or not 0.0 <= r2_treatment < 1.0
        or not 0.0 <= r2_outcome < 1.0
        or not 0.0 < confidence < 1.0
    ):
        raise ValueError("omitted-variable sensitivity inputs are invalid")
    bias_factor = np.sqrt(
        r2_outcome * r2_treatment / max(1e-15, 1.0 - r2_treatment)
    )
    maximum_bias = bias_factor * standard_error * np.sqrt(degrees_of_freedom)
    adjusted_standard_error = standard_error * np.sqrt(
        max(0.0, (1.0 - r2_outcome) / (1.0 - r2_treatment))
    )
    adjusted = (estimate - maximum_bias, estimate + maximum_bias)
    critical = float(t.ppf(0.5 + confidence / 2.0, degrees_of_freedom))
    confidence_interval = (
        adjusted[0] - critical * adjusted_standard_error,
        adjusted[1] + critical * adjusted_standard_error,
    )
    return OmittedVariableSensitivityResult(
        adjusted, confidence_interval, maximum_bias, adjusted_standard_error
    )


def discounted_model_transfer_bound(
    reward_error: float,
    transition_total_variation: float,
    reward_bound: float,
    *,
    discount: float,
) -> float:
    """Simulation-lemma value error bound for two discounted finite MDPs."""

    if (
        not isfinite(reward_error)
        or reward_error < 0.0
        or not isfinite(transition_total_variation)
        or not 0.0 <= transition_total_variation <= 1.0
        or not isfinite(reward_bound)
        or reward_bound < 0.0
        or not 0.0 <= discount < 1.0
    ):
        raise ValueError("model-transfer bound inputs are invalid")
    return reward_error / (1.0 - discount) + (
        2.0
        * discount
        * reward_bound
        * transition_total_variation
        / (1.0 - discount) ** 2
    )
