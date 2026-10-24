"""P22 linearly-solvable control, differentiable equilibria, and continuation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import root
from scipy.special import logsumexp, softmax


ArrayFunction = Callable[[np.ndarray, float], Sequence[float]]


def _stochastic_matrix(value: Sequence[Sequence[float]]) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[0] != matrix.shape[1]
        or np.any(~np.isfinite(matrix))
        or np.any(matrix < 0.0)
        or not np.allclose(matrix.sum(axis=1), 1.0)
    ):
        raise ValueError("passive dynamics must be a finite stochastic matrix")
    return matrix


@dataclass(frozen=True)
class FiniteLMDPResult:
    values: np.ndarray
    desirability: np.ndarray
    controlled_transition: np.ndarray
    bellman_residual: float
    temperature: float


def finite_horizon_lmdp(
    passive_transition: Sequence[Sequence[float]],
    state_cost: Sequence[Sequence[float]],
    terminal_cost: Sequence[float],
    *,
    temperature: float = 1.0,
) -> FiniteLMDPResult:
    """Solve a finite-horizon LMDP without creating unsupported transitions."""

    passive = _stochastic_matrix(passive_transition)
    costs = np.asarray(state_cost, dtype=np.float64)
    terminal = np.asarray(terminal_cost, dtype=np.float64)
    states = passive.shape[0]
    if (
        costs.ndim != 2
        or costs.shape[1] != states
        or costs.shape[0] == 0
        or terminal.shape != (states,)
        or np.any(~np.isfinite(costs))
        or np.any(~np.isfinite(terminal))
        or not isfinite(temperature)
        or temperature <= 0.0
    ):
        raise ValueError("finite-horizon LMDP inputs are invalid")
    horizon = costs.shape[0]
    values = np.empty((horizon + 1, states), dtype=np.float64)
    values[horizon] = terminal
    policies = np.empty((horizon, states, states), dtype=np.float64)
    log_passive = np.full_like(passive, -np.inf)
    positive = passive > 0.0
    log_passive[positive] = np.log(passive[positive])
    for time in range(horizon - 1, -1, -1):
        log_weights = log_passive - values[time + 1][None, :] / temperature
        normalizer = logsumexp(log_weights, axis=1)
        values[time] = costs[time] - temperature * normalizer
        policies[time] = np.exp(log_weights - normalizer[:, None])
    desirability = np.exp(-values / temperature)
    if np.any(~np.isfinite(desirability)):
        raise FloatingPointError("LMDP desirability overflowed; rescale costs")
    rhs = costs - temperature * np.stack(
        [
            logsumexp(
                log_passive - values[time + 1][None, :] / temperature,
                axis=1,
            )
            for time in range(horizon)
        ]
    )
    residual = float(np.max(np.abs(values[:-1] - rhs)))
    return FiniteLMDPResult(
        values,
        desirability,
        policies,
        residual,
        float(temperature),
    )


@dataclass(frozen=True)
class AverageCostLMDPResult:
    average_cost: float
    eigenvalue: float
    desirability: np.ndarray
    controlled_transition: np.ndarray
    eigen_residual: float


def average_cost_lmdp(
    passive_transition: Sequence[Sequence[float]],
    state_cost: Sequence[float],
    *,
    temperature: float = 1.0,
) -> AverageCostLMDPResult:
    """Solve the Perron eigenproblem for an average-cost finite LMDP."""

    passive = _stochastic_matrix(passive_transition)
    costs = np.asarray(state_cost, dtype=np.float64)
    states = passive.shape[0]
    if (
        costs.shape != (states,)
        or np.any(~np.isfinite(costs))
        or not isfinite(temperature)
        or temperature <= 0.0
    ):
        raise ValueError("average-cost LMDP inputs are invalid")
    weighted = np.exp(-costs / temperature)[:, None] * passive
    eigenvalues, eigenvectors = np.linalg.eig(weighted)
    index = int(np.argmax(eigenvalues.real))
    eigenvalue = float(eigenvalues[index].real)
    vector = np.asarray(eigenvectors[:, index].real, dtype=np.float64)
    if eigenvalue <= 0.0 or np.max(np.abs(eigenvalues[index].imag)) > 1e-8:
        raise ValueError("the LMDP has no positive real Perron root")
    if vector[np.argmax(np.abs(vector))] < 0.0:
        vector = -vector
    if np.min(vector) < -1e-8 or np.max(vector) <= 0.0:
        raise ValueError("the Perron eigenvector is not nonnegative")
    desirability = np.maximum(vector, 0.0)
    desirability /= np.max(desirability)
    normalizer = passive @ desirability
    if np.any(normalizer <= 0.0):
        raise ValueError("a passive state cannot reach positive desirability")
    controlled = passive * desirability[None, :] / normalizer[:, None]
    residual = float(
        np.max(np.abs(weighted @ desirability - eigenvalue * desirability))
    )
    return AverageCostLMDPResult(
        -temperature * float(np.log(eigenvalue)),
        eigenvalue,
        desirability,
        controlled,
        residual,
    )


@dataclass(frozen=True)
class ImplicitSensitivityResult:
    sensitivity: np.ndarray
    condition: float
    minimum_singular_value: float
    rank: int
    used_pseudoinverse: bool
    linear_residual: float


def implicit_equilibrium_sensitivity(
    equilibrium_jacobian: Sequence[Sequence[float]],
    parameter_jacobian: Sequence,
    *,
    condition_limit: float = 1e12,
    rank_tolerance: float | None = None,
) -> ImplicitSensitivityResult:
    """Differentiate R(z, theta)=0 through a square local equilibrium system."""

    jacobian = np.asarray(equilibrium_jacobian, dtype=np.float64)
    parameter = np.asarray(parameter_jacobian, dtype=np.float64)
    if parameter.ndim == 1:
        parameter = parameter[:, None]
    if (
        jacobian.ndim != 2
        or jacobian.shape[0] == 0
        or jacobian.shape[0] != jacobian.shape[1]
        or parameter.ndim != 2
        or parameter.shape[0] != jacobian.shape[0]
        or np.any(~np.isfinite(jacobian))
        or np.any(~np.isfinite(parameter))
        or condition_limit <= 1.0
    ):
        raise ValueError("implicit sensitivity inputs are invalid")
    singular = np.linalg.svd(jacobian, compute_uv=False)
    tolerance = (
        np.finfo(float).eps * max(jacobian.shape) * singular[0]
        if rank_tolerance is None
        else float(rank_tolerance)
    )
    if tolerance < 0.0:
        raise ValueError("rank tolerance must be nonnegative")
    rank = int(np.count_nonzero(singular > tolerance))
    condition = float(np.linalg.cond(jacobian))
    use_pseudoinverse = rank < jacobian.shape[0] or condition > condition_limit
    if use_pseudoinverse:
        sensitivity = -np.linalg.pinv(jacobian, rcond=max(tolerance, 1e-15)) @ parameter
    else:
        sensitivity = -np.linalg.solve(jacobian, parameter)
    residual = float(np.max(np.abs(jacobian @ sensitivity + parameter)))
    return ImplicitSensitivityResult(
        sensitivity,
        condition,
        float(singular[-1]),
        rank,
        use_pseudoinverse,
        residual,
    )


def _positive_probabilities(value: Sequence[float], size: int, name: str) -> np.ndarray:
    probabilities = np.asarray(value, dtype=np.float64)
    if (
        probabilities.shape != (size,)
        or np.any(~np.isfinite(probabilities))
        or np.any(probabilities <= 0.0)
        or not np.isclose(probabilities.sum(), 1.0)
    ):
        raise ValueError(f"{name} must be a strictly positive probability vector")
    return probabilities


def _reduced_logits(probabilities: np.ndarray) -> np.ndarray:
    return np.log(probabilities[:-1] / probabilities[-1])


def _from_reduced_logits(logits: np.ndarray) -> np.ndarray:
    return softmax(np.r_[logits, 0.0])


def _numerical_jacobian(
    function: Callable[[np.ndarray], np.ndarray],
    point: np.ndarray,
    step: float = 1e-6,
) -> np.ndarray:
    base = np.asarray(function(point), dtype=np.float64)
    jacobian = np.empty((base.size, point.size), dtype=np.float64)
    for column in range(point.size):
        width = step * max(1.0, abs(float(point[column])))
        plus = point.copy()
        minus = point.copy()
        plus[column] += width
        minus[column] -= width
        jacobian[:, column] = (function(plus) - function(minus)) / (2.0 * width)
    return jacobian


@dataclass(frozen=True)
class LogitQREResult:
    row_strategy: np.ndarray
    column_strategy: np.ndarray
    reduced_logits: np.ndarray
    residual: float
    jacobian: np.ndarray
    minimum_singular_value: float
    beta_sensitivity: np.ndarray
    converged: bool


def solve_bimatrix_logit_qre(
    row_payoff: Sequence[Sequence[float]],
    column_payoff: Sequence[Sequence[float]],
    *,
    row_rationality: float = 1.0,
    column_rationality: float = 1.0,
    initial: tuple[Sequence[float], Sequence[float]] | None = None,
    tolerance: float = 1e-10,
    max_iterations: int = 2_000,
) -> LogitQREResult:
    """Solve a local two-player logit QRE in nonredundant log-odds coordinates."""

    row = np.asarray(row_payoff, dtype=np.float64)
    column = np.asarray(column_payoff, dtype=np.float64)
    if (
        row.ndim != 2
        or min(row.shape) < 2
        or column.shape != row.shape
        or np.any(~np.isfinite(row))
        or np.any(~np.isfinite(column))
        or not isfinite(row_rationality)
        or not isfinite(column_rationality)
        or row_rationality < 0.0
        or column_rationality < 0.0
        or tolerance <= 0.0
        or max_iterations <= 0
    ):
        raise ValueError("QRE inputs are invalid")
    rows, columns = row.shape
    if initial is None:
        row_initial = np.full(rows, 1.0 / rows)
        column_initial = np.full(columns, 1.0 / columns)
    else:
        row_initial = _positive_probabilities(initial[0], rows, "row strategy")
        column_initial = _positive_probabilities(
            initial[1], columns, "column strategy"
        )
    start = np.r_[
        _reduced_logits(row_initial),
        _reduced_logits(column_initial),
    ]

    def residual(logits: np.ndarray) -> np.ndarray:
        row_strategy = _from_reduced_logits(logits[: rows - 1])
        column_strategy = _from_reduced_logits(logits[rows - 1 :])
        row_values = row @ column_strategy
        column_values = row_strategy @ column
        return np.r_[
            logits[: rows - 1]
            - row_rationality * (row_values[:-1] - row_values[-1]),
            logits[rows - 1 :]
            - column_rationality
            * (column_values[:-1] - column_values[-1]),
        ]

    solved = root(
        residual,
        start,
        method="hybr",
        options={"xtol": tolerance, "maxfev": max_iterations},
    )
    logits = np.asarray(solved.x, dtype=np.float64)
    row_strategy = _from_reduced_logits(logits[: rows - 1])
    column_strategy = _from_reduced_logits(logits[rows - 1 :])
    residual_value = residual(logits)
    jacobian = _numerical_jacobian(residual, logits)
    singular = np.linalg.svd(jacobian, compute_uv=False)
    row_values = row @ column_strategy
    column_values = row_strategy @ column
    beta_jacobian = np.zeros((logits.size, 2))
    beta_jacobian[: rows - 1, 0] = -(row_values[:-1] - row_values[-1])
    beta_jacobian[rows - 1 :, 1] = -(
        column_values[:-1] - column_values[-1]
    )
    sensitivity = implicit_equilibrium_sensitivity(
        jacobian, beta_jacobian
    ).sensitivity
    return LogitQREResult(
        row_strategy,
        column_strategy,
        logits,
        float(np.max(np.abs(residual_value))),
        jacobian,
        float(singular[-1]),
        sensitivity,
        bool(solved.success and np.max(np.abs(residual_value)) <= 10.0 * tolerance),
    )


def _ambiguity_vertices(
    value: Sequence,
    players: int,
    scenarios: int,
) -> np.ndarray:
    vertices = np.asarray(value, dtype=np.float64)
    if vertices.ndim == 2:
        vertices = np.broadcast_to(vertices, (players,) + vertices.shape).copy()
    if (
        vertices.ndim != 3
        or vertices.shape[0] != players
        or vertices.shape[2] != scenarios
        or vertices.shape[1] == 0
        or np.any(~np.isfinite(vertices))
        or np.any(vertices < 0.0)
        or not np.allclose(vertices.sum(axis=2), 1.0)
    ):
        raise ValueError("ambiguity vertices must contain probability vectors")
    return vertices


@dataclass(frozen=True)
class RobustNashResult:
    equilibria: tuple[tuple[int, ...], ...]
    robust_costs: np.ndarray
    worst_vertex: np.ndarray
    tolerance: float


def finite_distributionally_robust_nash(
    scenario_costs: Sequence,
    ambiguity_vertices: Sequence,
    *,
    tolerance: float = 1e-10,
) -> RobustNashResult:
    """Enumerate pure Nash equilibria under finite distribution ambiguity vertices."""

    costs = np.asarray(scenario_costs, dtype=np.float64)
    if costs.ndim < 4 or np.any(~np.isfinite(costs)) or tolerance < 0.0:
        raise ValueError("robust Nash costs are invalid")
    players, scenarios = costs.shape[:2]
    action_shape = costs.shape[2:]
    if players != len(action_shape) or min(action_shape) == 0:
        raise ValueError("one action dimension is required for each player")
    vertices = _ambiguity_vertices(ambiguity_vertices, players, scenarios)
    robust = np.empty((players,) + action_shape, dtype=np.float64)
    worst = np.empty((players,) + action_shape, dtype=np.int64)
    for player in range(players):
        expected = np.tensordot(vertices[player], costs[player], axes=(1, 0))
        worst[player] = np.argmax(expected, axis=0)
        robust[player] = np.max(expected, axis=0)
    equilibria = []
    for profile in product(*(range(size) for size in action_shape)):
        stable = True
        for player, size in enumerate(action_shape):
            current = robust[(player,) + profile]
            for action in range(size):
                deviation = list(profile)
                deviation[player] = action
                if robust[(player,) + tuple(deviation)] < current - tolerance:
                    stable = False
                    break
            if not stable:
                break
        if stable:
            equilibria.append(tuple(int(action) for action in profile))
    return RobustNashResult(tuple(equilibria), robust, worst, tolerance)


@dataclass(frozen=True)
class RobustStackelbergResult:
    leader_action: int
    follower_action: int
    leader_cost: float
    follower_cost: float
    follower_best_responses: tuple[tuple[int, ...], ...]
    tie_breaking: str


def finite_distributionally_robust_stackelberg(
    leader_scenario_cost: Sequence,
    follower_scenario_cost: Sequence,
    leader_ambiguity_vertices: Sequence,
    follower_ambiguity_vertices: Sequence,
    *,
    tie_breaking: str = "optimistic",
    tolerance: float = 1e-10,
) -> RobustStackelbergResult:
    """Solve a finite pure-action distributionally robust Stackelberg game."""

    leader = np.asarray(leader_scenario_cost, dtype=np.float64)
    follower = np.asarray(follower_scenario_cost, dtype=np.float64)
    if (
        leader.ndim != 3
        or follower.shape != leader.shape
        or min(leader.shape) == 0
        or np.any(~np.isfinite(leader))
        or np.any(~np.isfinite(follower))
        or tie_breaking not in {"optimistic", "pessimistic"}
        or tolerance < 0.0
    ):
        raise ValueError("robust Stackelberg inputs are invalid")
    scenarios, leader_actions, follower_actions = leader.shape
    leader_vertices = _ambiguity_vertices(
        leader_ambiguity_vertices, 1, scenarios
    )[0]
    follower_vertices = _ambiguity_vertices(
        follower_ambiguity_vertices, 1, scenarios
    )[0]
    robust_leader = np.max(
        np.tensordot(leader_vertices, leader, axes=(1, 0)), axis=0
    )
    robust_follower = np.max(
        np.tensordot(follower_vertices, follower, axes=(1, 0)), axis=0
    )
    responses = []
    candidates = []
    for leader_action in range(leader_actions):
        best_cost = float(np.min(robust_follower[leader_action]))
        best = tuple(
            int(action)
            for action in np.flatnonzero(
                robust_follower[leader_action] <= best_cost + tolerance
            )
        )
        responses.append(best)
        if tie_breaking == "optimistic":
            follower_action = min(
                best, key=lambda action: (robust_leader[leader_action, action], action)
            )
        else:
            follower_action = max(
                best, key=lambda action: (robust_leader[leader_action, action], -action)
            )
        candidates.append(
            (
                float(robust_leader[leader_action, follower_action]),
                leader_action,
                follower_action,
            )
        )
    _, leader_action, follower_action = min(candidates)
    return RobustStackelbergResult(
        int(leader_action),
        int(follower_action),
        float(robust_leader[leader_action, follower_action]),
        float(robust_follower[leader_action, follower_action]),
        tuple(responses),
        tie_breaking,
    )


def _continuation_jacobian(
    residual: ArrayFunction,
    augmented: np.ndarray,
    step: float,
) -> np.ndarray:
    def wrapped(point: np.ndarray) -> np.ndarray:
        return np.asarray(residual(point[:-1], float(point[-1])), dtype=np.float64)

    return _numerical_jacobian(wrapped, augmented, step)


@dataclass(frozen=True)
class ContinuationResult:
    points: np.ndarray
    tangents: np.ndarray
    equilibrium_residuals: np.ndarray
    minimum_singular_values: np.ndarray
    step_sizes: np.ndarray
    fold_indices: tuple[int, ...]
    converged: bool


def pseudo_arclength_continuation(
    residual: ArrayFunction,
    initial_state: Sequence[float],
    initial_parameter: float,
    *,
    steps: int,
    step_size: float = 0.05,
    parameter_direction: int = 1,
    tolerance: float = 1e-9,
    max_newton_iterations: int = 15,
    jacobian_step: float = 1e-6,
    minimum_step: float | None = None,
    maximum_step: float | None = None,
) -> ContinuationResult:
    """Trace a one-dimensional equilibrium branch with pseudo-arclength steps."""

    state = np.asarray(initial_state, dtype=np.float64)
    if (
        state.ndim != 1
        or state.size == 0
        or np.any(~np.isfinite(state))
        or not isfinite(initial_parameter)
        or steps < 0
        or not isfinite(step_size)
        or step_size <= 0.0
        or parameter_direction not in {-1, 1}
        or tolerance <= 0.0
        or max_newton_iterations <= 0
        or jacobian_step <= 0.0
    ):
        raise ValueError("continuation inputs are invalid")
    min_step = step_size / 64.0 if minimum_step is None else float(minimum_step)
    max_step = step_size * 4.0 if maximum_step is None else float(maximum_step)
    if min_step <= 0.0 or max_step < min_step:
        raise ValueError("continuation step bounds are invalid")
    initial_value = np.asarray(residual(state, float(initial_parameter)), dtype=np.float64)
    if initial_value.shape != state.shape or np.any(~np.isfinite(initial_value)):
        raise ValueError("continuation residual has the wrong shape")
    if np.max(np.abs(initial_value)) > 100.0 * tolerance:
        raise ValueError("initial continuation point is not an equilibrium")
    current = np.r_[state, float(initial_parameter)]
    jacobian = _continuation_jacobian(residual, current, jacobian_step)
    _, _, vh = np.linalg.svd(jacobian, full_matrices=True)
    tangent = vh[-1]
    if tangent[-1] * parameter_direction < 0.0:
        tangent = -tangent
    tangent /= np.linalg.norm(tangent)
    points = [current.copy()]
    tangents = [tangent.copy()]
    residuals = [float(np.max(np.abs(initial_value)))]
    state_singular = np.linalg.svd(jacobian[:, :-1], compute_uv=False)
    minimum_singular = [float(state_singular[-1])]
    step_sizes = []
    folds = []
    delta_s = min(max(step_size, min_step), max_step)
    converged = True
    for _ in range(steps):
        accepted = False
        used_iterations = max_newton_iterations
        trial_step = delta_s
        while trial_step >= min_step - 1e-15 and not accepted:
            predicted = current + trial_step * tangent
            corrected = predicted.copy()
            for iteration in range(1, max_newton_iterations + 1):
                value = np.asarray(
                    residual(corrected[:-1], float(corrected[-1])),
                    dtype=np.float64,
                )
                augmented_value = np.r_[
                    value, tangent @ (corrected - predicted)
                ]
                if np.max(np.abs(augmented_value)) <= tolerance:
                    accepted = True
                    used_iterations = iteration
                    break
                derivative = _continuation_jacobian(
                    residual, corrected, jacobian_step
                )
                bordered = np.vstack((derivative, tangent))
                try:
                    correction = np.linalg.solve(bordered, -augmented_value)
                except np.linalg.LinAlgError:
                    correction = np.linalg.lstsq(
                        bordered, -augmented_value, rcond=None
                    )[0]
                corrected += correction
                if np.any(~np.isfinite(corrected)):
                    break
            if not accepted:
                trial_step *= 0.5
        if not accepted:
            converged = False
            break
        new_jacobian = _continuation_jacobian(
            residual, corrected, jacobian_step
        )
        _, _, vh = np.linalg.svd(new_jacobian, full_matrices=True)
        new_tangent = vh[-1]
        if new_tangent @ tangent < 0.0:
            new_tangent = -new_tangent
        new_tangent /= np.linalg.norm(new_tangent)
        if tangent[-1] * new_tangent[-1] < 0.0:
            folds.append(len(points))
        current = corrected
        tangent = new_tangent
        value = np.asarray(residual(current[:-1], float(current[-1])))
        points.append(current.copy())
        tangents.append(tangent.copy())
        residuals.append(float(np.max(np.abs(value))))
        state_singular = np.linalg.svd(new_jacobian[:, :-1], compute_uv=False)
        minimum_singular.append(float(state_singular[-1]))
        step_sizes.append(float(trial_step))
        if used_iterations <= 4:
            delta_s = min(max_step, trial_step * 1.2)
        elif used_iterations >= 9:
            delta_s = max(min_step, trial_step * 0.6)
        else:
            delta_s = trial_step
    return ContinuationResult(
        np.asarray(points),
        np.asarray(tangents),
        np.asarray(residuals),
        np.asarray(minimum_singular),
        np.asarray(step_sizes),
        tuple(folds),
        converged,
    )


@dataclass(frozen=True)
class StaticBifurcationDiagnostic:
    kind: str
    rank: int
    nullity: int
    minimum_singular_value: float
    right_null_vector: np.ndarray
    left_null_vector: np.ndarray
    transversality: float
    quadratic_coefficient: float | None


def classify_static_bifurcation(
    state_jacobian: Sequence[Sequence[float]],
    parameter_derivative: Sequence[float],
    *,
    second_directional: Sequence[float] | None = None,
    tolerance: float = 1e-7,
) -> StaticBifurcationDiagnostic:
    """Classify regular, simple-fold, branch, or higher-nullity candidates."""

    jacobian = np.asarray(state_jacobian, dtype=np.float64)
    parameter = np.asarray(parameter_derivative, dtype=np.float64)
    if (
        jacobian.ndim != 2
        or jacobian.shape[0] == 0
        or jacobian.shape[0] != jacobian.shape[1]
        or parameter.shape != (jacobian.shape[0],)
        or np.any(~np.isfinite(jacobian))
        or np.any(~np.isfinite(parameter))
        or tolerance <= 0.0
    ):
        raise ValueError("static bifurcation inputs are invalid")
    left, singular, right_t = np.linalg.svd(jacobian)
    scale = max(1.0, float(singular[0]))
    rank = int(np.count_nonzero(singular > tolerance * scale))
    nullity = jacobian.shape[0] - rank
    right_null = right_t[-1]
    left_null = left[:, -1]
    transversality = float(left_null @ parameter)
    quadratic = None
    if second_directional is not None:
        second = np.asarray(second_directional, dtype=np.float64)
        if second.shape != parameter.shape or np.any(~np.isfinite(second)):
            raise ValueError("second directional derivative has the wrong shape")
        quadratic = float(left_null @ second)
    if nullity == 0:
        kind = "regular"
    elif nullity > 1:
        kind = "higher_codimension_candidate"
    elif abs(transversality) > tolerance * scale:
        kind = "fold_candidate"
    else:
        kind = "branch_candidate"
    return StaticBifurcationDiagnostic(
        kind,
        rank,
        nullity,
        float(singular[-1]),
        right_null,
        left_null,
        transversality,
        quadratic,
    )


@dataclass(frozen=True)
class DynamicBifurcationDiagnostic:
    candidates: tuple[str, ...]
    eigenvalues: np.ndarray
    spectral_abscissa_or_radius: float
    critical_indices: tuple[int, ...]


def detect_dynamic_bifurcations(
    dynamics_jacobian: Sequence[Sequence[float]],
    *,
    discrete_time: bool = False,
    tolerance: float = 1e-3,
) -> DynamicBifurcationDiagnostic:
    """Detect local continuous- or discrete-time spectral crossing candidates."""

    jacobian = np.asarray(dynamics_jacobian, dtype=np.float64)
    if (
        jacobian.ndim != 2
        or jacobian.shape[0] == 0
        or jacobian.shape[0] != jacobian.shape[1]
        or np.any(~np.isfinite(jacobian))
        or tolerance <= 0.0
    ):
        raise ValueError("dynamic bifurcation inputs are invalid")
    eigenvalues = np.linalg.eigvals(jacobian)
    candidates = []
    critical = set()
    if discrete_time:
        for index, value in enumerate(eigenvalues):
            if abs(value - 1.0) <= tolerance:
                candidates.append("steady_state_candidate")
                critical.add(index)
            if abs(value + 1.0) <= tolerance:
                candidates.append("flip_candidate")
                critical.add(index)
            if (
                abs(abs(value) - 1.0) <= tolerance
                and abs(value.imag) > tolerance
            ):
                candidates.append("neimark_sacker_candidate")
                critical.add(index)
        metric = float(np.max(np.abs(eigenvalues)))
    else:
        for index, value in enumerate(eigenvalues):
            if abs(value.real) <= tolerance and abs(value.imag) <= tolerance:
                candidates.append("steady_state_candidate")
                critical.add(index)
            if abs(value.real) <= tolerance and abs(value.imag) > tolerance:
                candidates.append("hopf_candidate")
                critical.add(index)
        metric = float(np.max(eigenvalues.real))
    return DynamicBifurcationDiagnostic(
        tuple(dict.fromkeys(candidates)),
        eigenvalues,
        metric,
        tuple(sorted(critical)),
    )
