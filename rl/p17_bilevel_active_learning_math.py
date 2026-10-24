"""P17 bilevel optimization, implicit differentiation, and active learning."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.stats import chi2


@dataclass(frozen=True)
class BilevelLinearResult:
    upper_choice: int
    lower_decision: np.ndarray
    upper_value: float
    lower_value: float
    tie_breaking: str
    feasible_upper_choices: tuple[int, ...]


def solve_finite_bilevel_linear(
    upper_costs: Sequence[Sequence[float]],
    lower_costs: Sequence[Sequence[float]],
    constraint_matrices: Sequence[Sequence],
    constraint_bounds: Sequence[Sequence[float]],
    *,
    variable_bounds: Sequence[tuple[float | None, float | None]] | None = None,
    upper_offsets: Sequence[float] | None = None,
    lower_offsets: Sequence[float] | None = None,
    tie_breaking: str = "optimistic",
    tolerance: float = 1e-9,
) -> BilevelLinearResult:
    """Solve a discrete-upper, continuous-lower bilevel LP exactly by enumeration.

    Both levels minimize.  The lower-level optimal face is resolved in the
    upper level's favor for optimistic ties and against it for pessimistic ties.
    """

    upper = np.asarray(upper_costs, dtype=np.float64)
    lower = np.asarray(lower_costs, dtype=np.float64)
    if (
        upper.ndim != 2
        or upper.shape != lower.shape
        or min(upper.shape) == 0
        or np.any(~np.isfinite(upper))
        or np.any(~np.isfinite(lower))
        or len(constraint_matrices) != upper.shape[0]
        or len(constraint_bounds) != upper.shape[0]
        or tie_breaking not in {"optimistic", "pessimistic"}
        or tolerance < 0.0
    ):
        raise ValueError("bilevel LP inputs are invalid")
    choices, variables = upper.shape
    if variable_bounds is None:
        bounds = [(None, None)] * variables
    else:
        bounds = list(variable_bounds)
        if len(bounds) != variables:
            raise ValueError("bilevel LP variable bounds are inconsistent")
    upper_constant = (
        np.zeros(choices)
        if upper_offsets is None
        else np.asarray(upper_offsets, dtype=np.float64)
    )
    lower_constant = (
        np.zeros(choices)
        if lower_offsets is None
        else np.asarray(lower_offsets, dtype=np.float64)
    )
    if (
        upper_constant.shape != (choices,)
        or lower_constant.shape != (choices,)
        or np.any(~np.isfinite(upper_constant))
        or np.any(~np.isfinite(lower_constant))
    ):
        raise ValueError("bilevel LP offsets are inconsistent")
    candidates = []
    feasible = []
    for choice in range(choices):
        matrix = np.asarray(constraint_matrices[choice], dtype=np.float64)
        rhs = np.asarray(constraint_bounds[choice], dtype=np.float64)
        if (
            matrix.ndim != 2
            or matrix.shape[1] != variables
            or rhs.shape != (matrix.shape[0],)
            or np.any(~np.isfinite(matrix))
            or np.any(~np.isfinite(rhs))
        ):
            raise ValueError("bilevel LP constraints are inconsistent")
        lower_solution = linprog(
            lower[choice], A_ub=matrix, b_ub=rhs, bounds=bounds, method="highs"
        )
        if not lower_solution.success or lower_solution.x is None:
            continue
        lower_optimum = float(lower_solution.fun)
        face_matrix = np.vstack((matrix, lower[choice]))
        face_rhs = np.r_[rhs, lower_optimum + tolerance]
        face_objective = (
            upper[choice]
            if tie_breaking == "optimistic"
            else -upper[choice]
        )
        selected = linprog(
            face_objective,
            A_ub=face_matrix,
            b_ub=face_rhs,
            bounds=bounds,
            method="highs",
        )
        if not selected.success or selected.x is None:
            raise RuntimeError("failed to resolve a lower-level optimal face")
        decision = np.asarray(selected.x, dtype=np.float64)
        feasible.append(choice)
        candidates.append(
            BilevelLinearResult(
                choice,
                decision,
                float(upper_constant[choice] + upper[choice] @ decision),
                float(lower_constant[choice] + lower[choice] @ decision),
                tie_breaking,
                (),
            )
        )
    if not candidates:
        raise RuntimeError("all bilevel lower-level problems are infeasible")
    best = min(
        candidates,
        key=lambda result: (
            result.upper_value,
            result.lower_value,
            result.upper_choice,
        ),
    )
    return BilevelLinearResult(
        best.upper_choice,
        best.lower_decision,
        best.upper_value,
        best.lower_value,
        best.tie_breaking,
        tuple(feasible),
    )


@dataclass(frozen=True)
class LinearKKTCertificate:
    primal_violation: float
    dual_violation: float
    stationarity_residual: float
    complementarity_residual: float
    certified: bool


def linear_program_kkt_certificate(
    objective: Sequence[float],
    constraint_matrix: Sequence[Sequence[float]],
    constraint_bound: Sequence[float],
    decision: Sequence[float],
    dual: Sequence[float],
    *,
    tolerance: float = 1e-7,
) -> LinearKKTCertificate:
    """Validate KKT conditions for ``min c @ x`` subject to ``A @ x <= b``."""

    cost = np.asarray(objective, dtype=np.float64)
    matrix = np.asarray(constraint_matrix, dtype=np.float64)
    bound = np.asarray(constraint_bound, dtype=np.float64)
    point = np.asarray(decision, dtype=np.float64)
    multiplier = np.asarray(dual, dtype=np.float64)
    if (
        matrix.ndim != 2
        or cost.shape != (matrix.shape[1],)
        or bound.shape != (matrix.shape[0],)
        or point.shape != cost.shape
        or multiplier.shape != bound.shape
        or any(
            np.any(~np.isfinite(value))
            for value in (cost, matrix, bound, point, multiplier)
        )
        or tolerance < 0.0
    ):
        raise ValueError("linear KKT certificate inputs are invalid")
    residual = matrix @ point - bound
    primal = float(max(0.0, np.max(residual, initial=0.0)))
    dual_violation = float(max(0.0, -np.min(multiplier, initial=0.0)))
    stationarity = float(np.max(np.abs(cost + matrix.T @ multiplier)))
    complementarity = float(
        np.max(np.abs(multiplier * residual), initial=0.0)
    )
    return LinearKKTCertificate(
        primal,
        dual_violation,
        stationarity,
        complementarity,
        max(primal, dual_violation, stationarity, complementarity) <= tolerance,
    )


@dataclass(frozen=True)
class HypergradientResult:
    hypergradient: np.ndarray
    inner_sensitivity: np.ndarray
    hessian_condition: float
    used_pseudoinverse: bool


def implicit_hypergradient(
    outer_gradient_parameter: Sequence[float],
    outer_gradient_inner: Sequence[float],
    inner_hessian: Sequence[Sequence[float]],
    mixed_inner_parameter: Sequence[Sequence[float]],
    *,
    condition_limit: float = 1e12,
) -> HypergradientResult:
    """Differentiate an unconstrained smooth lower optimum by the IFT."""

    direct = np.asarray(outer_gradient_parameter, dtype=np.float64)
    outer_inner = np.asarray(outer_gradient_inner, dtype=np.float64)
    hessian = np.asarray(inner_hessian, dtype=np.float64)
    mixed = np.asarray(mixed_inner_parameter, dtype=np.float64)
    if (
        hessian.ndim != 2
        or hessian.shape[0] != hessian.shape[1]
        or outer_inner.shape != (hessian.shape[0],)
        or mixed.shape != (hessian.shape[0], direct.size)
        or direct.ndim != 1
        or any(
            np.any(~np.isfinite(value))
            for value in (direct, outer_inner, hessian, mixed)
        )
        or condition_limit <= 1.0
    ):
        raise ValueError("implicit hypergradient inputs are invalid")
    condition = float(np.linalg.cond(hessian))
    use_pseudoinverse = not isfinite(condition) or condition > condition_limit
    if use_pseudoinverse:
        sensitivity = -np.linalg.pinv(hessian) @ mixed
    else:
        sensitivity = -np.linalg.solve(hessian, mixed)
    return HypergradientResult(
        direct + outer_inner @ sensitivity,
        sensitivity,
        condition,
        use_pseudoinverse,
    )


@dataclass(frozen=True)
class EqualityQPSensitivityResult:
    decision: np.ndarray
    dual: np.ndarray
    decision_jacobian: np.ndarray
    dual_jacobian: np.ndarray
    kkt_residual: float
    kkt_condition: float


def equality_qp_sensitivity(
    quadratic: Sequence[Sequence[float]],
    linear_cost: Sequence[float],
    equality_matrix: Sequence[Sequence[float]],
    equality_bound: Sequence[float],
    cost_jacobian: Sequence,
    bound_jacobian: Sequence,
) -> EqualityQPSensitivityResult:
    """Solve and differentiate a strictly convex equality-constrained QP."""

    q = np.asarray(quadratic, dtype=np.float64)
    c = np.asarray(linear_cost, dtype=np.float64)
    a = np.asarray(equality_matrix, dtype=np.float64)
    b = np.asarray(equality_bound, dtype=np.float64)
    dc = np.asarray(cost_jacobian, dtype=np.float64)
    db = np.asarray(bound_jacobian, dtype=np.float64)
    if (
        q.ndim != 2
        or q.shape[0] != q.shape[1]
        or c.shape != (q.shape[0],)
        or a.ndim != 2
        or a.shape[1] != q.shape[0]
        or b.shape != (a.shape[0],)
        or dc.ndim != 2
        or dc.shape[0] != q.shape[0]
        or db.shape != (a.shape[0], dc.shape[1])
        or any(np.any(~np.isfinite(value)) for value in (q, c, a, b, dc, db))
        or not np.allclose(q, q.T)
    ):
        raise ValueError("equality-QP sensitivity inputs are invalid")
    variables = q.shape[0]
    constraints = a.shape[0]
    kkt = np.block(
        [[q, a.T], [a, np.zeros((constraints, constraints))]]
    )
    rhs = np.r_[-c, b]
    try:
        solution = np.linalg.solve(kkt, rhs)
        derivative = np.linalg.solve(kkt, np.vstack((-dc, db)))
    except np.linalg.LinAlgError as error:
        raise ValueError("equality-QP KKT matrix is singular") from error
    residual = float(np.max(np.abs(kkt @ solution - rhs), initial=0.0))
    return EqualityQPSensitivityResult(
        solution[:variables],
        solution[variables:],
        derivative[:variables],
        derivative[variables:],
        residual,
        float(np.linalg.cond(kkt)),
    )


@dataclass(frozen=True)
class ActiveSetSensitivityResult:
    decision_jacobian: np.ndarray
    active_rank: int
    nullity: int
    residual: float
    unique: bool


def linear_program_active_set_sensitivity(
    active_normals: Sequence[Sequence[float]],
    active_bound_jacobian: Sequence,
) -> ActiveSetSensitivityResult:
    """Differentiate a fixed LP vertex from ``A_active dx = db``."""

    normals = np.asarray(active_normals, dtype=np.float64)
    derivative = np.asarray(active_bound_jacobian, dtype=np.float64)
    if (
        normals.ndim != 2
        or min(normals.shape) == 0
        or derivative.ndim != 2
        or derivative.shape[0] != normals.shape[0]
        or np.any(~np.isfinite(normals))
        or np.any(~np.isfinite(derivative))
    ):
        raise ValueError("LP active-set sensitivity inputs are invalid")
    rank = int(np.linalg.matrix_rank(normals))
    jacobian = np.linalg.pinv(normals) @ derivative
    residual = float(
        np.max(np.abs(normals @ jacobian - derivative), initial=0.0)
    )
    variables = normals.shape[1]
    return ActiveSetSensitivityResult(
        jacobian,
        rank,
        variables - rank,
        residual,
        rank == variables and residual <= 1e-8,
    )


def logistic_preference_fisher_information(
    feature_differences: Sequence[Sequence[float]],
    parameter: Sequence[float],
    *,
    precision: float = 1.0,
    weights: Sequence[float] | None = None,
) -> np.ndarray:
    """Expected Fisher information for pairwise logistic preferences."""

    design = np.asarray(feature_differences, dtype=np.float64)
    estimate = np.asarray(parameter, dtype=np.float64)
    if (
        design.ndim != 2
        or design.shape[0] == 0
        or estimate.shape != (design.shape[1],)
        or np.any(~np.isfinite(design))
        or np.any(~np.isfinite(estimate))
        or not isfinite(precision)
        or precision <= 0.0
    ):
        raise ValueError("preference Fisher inputs are invalid")
    if weights is None:
        sample_weights = np.ones(design.shape[0])
    else:
        sample_weights = np.asarray(weights, dtype=np.float64)
        if (
            sample_weights.shape != (design.shape[0],)
            or np.any(~np.isfinite(sample_weights))
            or np.any(sample_weights < 0.0)
        ):
            raise ValueError("preference Fisher weights are invalid")
    logits = np.clip(precision * (design @ estimate), -700.0, 700.0)
    probabilities = 1.0 / (1.0 + np.exp(-logits))
    curvature = sample_weights * precision**2 * probabilities * (1.0 - probabilities)
    return design.T @ (curvature[:, None] * design)


@dataclass(frozen=True)
class OptimalDesignResult:
    selected_indices: tuple[int, ...]
    information_matrix: np.ndarray
    objective_history: tuple[float, ...]
    criterion: str
    condition_number: float


def greedy_optimal_design(
    candidate_features: Sequence[Sequence[float]],
    sample_count: int,
    *,
    prior_precision: float | Sequence[Sequence[float]] = 1e-6,
    criterion: str = "d",
) -> OptimalDesignResult:
    """Greedy D- or A-optimal design for rank-one information increments."""

    candidates = np.asarray(candidate_features, dtype=np.float64)
    if (
        candidates.ndim != 2
        or candidates.shape[0] == 0
        or np.any(~np.isfinite(candidates))
        or not 0 < sample_count <= candidates.shape[0]
        or criterion not in {"d", "a"}
    ):
        raise ValueError("optimal-design inputs are invalid")
    dimension = candidates.shape[1]
    if np.isscalar(prior_precision):
        precision_value = float(prior_precision)
        if not isfinite(precision_value) or precision_value <= 0.0:
            raise ValueError("scalar prior precision must be positive")
        information = precision_value * np.eye(dimension)
    else:
        information = np.asarray(prior_precision, dtype=np.float64).copy()
        if (
            information.shape != (dimension, dimension)
            or np.any(~np.isfinite(information))
            or np.min(np.linalg.eigvalsh(0.5 * (information + information.T))) <= 0.0
        ):
            raise ValueError("prior precision must be positive definite")

    def score(matrix: np.ndarray) -> float:
        if criterion == "d":
            sign, value = np.linalg.slogdet(matrix)
            return float(value) if sign > 0 else -np.inf
        return -float(np.trace(np.linalg.inv(matrix)))

    selected = []
    history = []
    available = set(range(candidates.shape[0]))
    for _ in range(sample_count):
        best_index = max(
            available,
            key=lambda index: (
                score(information + np.outer(candidates[index], candidates[index])),
                -index,
            ),
        )
        information += np.outer(candidates[best_index], candidates[best_index])
        selected.append(best_index)
        available.remove(best_index)
        history.append(score(information))
    return OptimalDesignResult(
        tuple(selected),
        information,
        tuple(history),
        criterion,
        float(np.linalg.cond(information)),
    )


@dataclass(frozen=True)
class ExpectedInformationGainResult:
    information_gain: np.ndarray
    best_experiment: int
    predictive_outcomes: np.ndarray


def expected_information_gain(
    hypothesis_prior: Sequence[float],
    experiment_likelihoods: Sequence,
) -> ExpectedInformationGainResult:
    """Mutual information between a finite hypothesis and each experiment."""

    prior = np.asarray(hypothesis_prior, dtype=np.float64)
    likelihood = np.asarray(experiment_likelihoods, dtype=np.float64)
    if (
        prior.ndim != 1
        or prior.size == 0
        or likelihood.ndim != 3
        or likelihood.shape[1] != prior.size
        or likelihood.shape[0] == 0
        or likelihood.shape[2] == 0
        or np.any(~np.isfinite(prior))
        or np.any(~np.isfinite(likelihood))
        or np.any(prior < 0.0)
        or np.any(likelihood < 0.0)
        or not np.isclose(prior.sum(), 1.0)
        or not np.allclose(likelihood.sum(axis=2), 1.0)
    ):
        raise ValueError("expected-information-gain inputs are invalid")
    predictive = np.einsum("h,eho->eo", prior, likelihood)
    gains = np.zeros(likelihood.shape[0])
    for experiment in range(likelihood.shape[0]):
        for hypothesis in range(prior.size):
            for outcome in range(likelihood.shape[2]):
                probability = likelihood[experiment, hypothesis, outcome]
                marginal = predictive[experiment, outcome]
                if prior[hypothesis] > 0.0 and probability > 0.0 and marginal > 0.0:
                    gains[experiment] += (
                        prior[hypothesis]
                        * probability
                        * np.log(probability / marginal)
                    )
    return ExpectedInformationGainResult(
        gains, int(np.argmax(gains)), predictive
    )


def active_irl_query(
    reward_hypotheses: Sequence[Sequence[float]],
    query_feature_differences: Sequence[Sequence[float]],
    hypothesis_prior: Sequence[float],
    *,
    precision: float = 1.0,
) -> ExpectedInformationGainResult:
    """Select a trajectory-pair query under finite reward hypotheses.

    Each query row is the discounted feature count of option zero minus option
    one.  The demonstrator chooses option zero with a Boltzmann probability.
    """

    hypotheses = np.asarray(reward_hypotheses, dtype=np.float64)
    differences = np.asarray(query_feature_differences, dtype=np.float64)
    prior = np.asarray(hypothesis_prior, dtype=np.float64)
    if (
        hypotheses.ndim != 2
        or hypotheses.shape[0] == 0
        or differences.ndim != 2
        or differences.shape[0] == 0
        or differences.shape[1] != hypotheses.shape[1]
        or prior.shape != (hypotheses.shape[0],)
        or np.any(~np.isfinite(hypotheses))
        or np.any(~np.isfinite(differences))
        or np.any(~np.isfinite(prior))
        or np.any(prior < 0.0)
        or not np.isclose(prior.sum(), 1.0)
        or not isfinite(precision)
        or precision <= 0.0
    ):
        raise ValueError("active IRL query inputs are invalid")
    logits = np.clip(precision * (differences @ hypotheses.T), -700.0, 700.0)
    choose_zero = 1.0 / (1.0 + np.exp(-logits))
    likelihood = np.stack((choose_zero, 1.0 - choose_zero), axis=2)
    return expected_information_gain(prior, likelihood)


@dataclass(frozen=True)
class WaldConfidenceResult:
    estimate: np.ndarray
    covariance: np.ndarray
    precision: np.ndarray
    radius_squared: float
    rank: int
    null_space: np.ndarray
    confidence: float

    def contains(self, parameter: Sequence[float], *, tolerance: float = 1e-9) -> bool:
        value = np.asarray(parameter, dtype=np.float64)
        if value.shape != self.estimate.shape or np.any(~np.isfinite(value)):
            raise ValueError("confidence query parameter is invalid")
        difference = value - self.estimate
        # The confidence set is a cylinder along unidentified null directions.
        return float(difference @ self.precision @ difference) <= (
            self.radius_squared + tolerance
        )


def wald_confidence_ellipsoid(
    estimate: Sequence[float],
    information_matrix: Sequence[Sequence[float]],
    *,
    confidence: float = 0.95,
    rank_tolerance: float = 1e-10,
) -> WaldConfidenceResult:
    """Construct an identifiable-subspace Wald ellipsoid with null-space output."""

    center = np.asarray(estimate, dtype=np.float64)
    information = np.asarray(information_matrix, dtype=np.float64)
    if (
        center.ndim != 1
        or information.shape != (center.size, center.size)
        or np.any(~np.isfinite(center))
        or np.any(~np.isfinite(information))
        or not np.allclose(information, information.T)
        or not 0.0 < confidence < 1.0
        or rank_tolerance <= 0.0
    ):
        raise ValueError("Wald confidence inputs are invalid")
    eigenvalues, eigenvectors = np.linalg.eigh(information)
    if np.min(eigenvalues) < -rank_tolerance:
        raise ValueError("information matrix must be positive semidefinite")
    active = eigenvalues > rank_tolerance
    rank = int(np.count_nonzero(active))
    if rank == 0:
        raise ValueError("information matrix has no identifiable direction")
    covariance = (
        eigenvectors[:, active]
        @ np.diag(1.0 / eigenvalues[active])
        @ eigenvectors[:, active].T
    )
    null_space = eigenvectors[:, ~active]
    return WaldConfidenceResult(
        center,
        covariance,
        information,
        float(chi2.ppf(confidence, rank)),
        rank,
        null_space,
        confidence,
    )
