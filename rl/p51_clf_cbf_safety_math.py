"""P51 CLF/CBF affine constraints and minimum-change safety filtering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import minimize


def affine_cbf_constraint(
    gradient_h: Sequence[float],
    drift: Sequence[float],
    control_matrix: Sequence,
    barrier_value: float,
    *,
    alpha: float,
) -> tuple[np.ndarray, float]:
    gradient = np.asarray(gradient_h, dtype=np.float64)
    f = np.asarray(drift, dtype=np.float64)
    g = np.asarray(control_matrix, dtype=np.float64)
    if gradient.ndim != 1 or f.shape != gradient.shape or g.ndim != 2 or g.shape[0] != gradient.size or np.any(~np.isfinite(gradient)) or np.any(~np.isfinite(f)) or np.any(~np.isfinite(g)) or not np.isfinite(barrier_value) or not np.isfinite(alpha) or alpha < 0.0:
        raise ValueError("CBF inputs are invalid")
    return gradient @ g, float(-gradient @ f - alpha * barrier_value)


def affine_clf_constraint(
    gradient_v: Sequence[float],
    drift: Sequence[float],
    control_matrix: Sequence,
    lyapunov_value: float,
    *,
    rate: float,
) -> tuple[np.ndarray, float]:
    gradient = np.asarray(gradient_v, dtype=np.float64)
    f = np.asarray(drift, dtype=np.float64)
    g = np.asarray(control_matrix, dtype=np.float64)
    if gradient.ndim != 1 or f.shape != gradient.shape or g.ndim != 2 or g.shape[0] != gradient.size or np.any(~np.isfinite(gradient)) or np.any(~np.isfinite(f)) or np.any(~np.isfinite(g)) or not np.isfinite(lyapunov_value) or not np.isfinite(rate) or rate < 0.0:
        raise ValueError("CLF inputs are invalid")
    return gradient @ g, float(-gradient @ f - rate * lyapunov_value)


@dataclass(frozen=True)
class SafetyFilterResult:
    control: np.ndarray
    clf_slack: float
    objective: float
    minimum_cbf_margin: float
    maximum_clf_residual: float


def clf_cbf_safety_filter(
    nominal_control: Sequence[float],
    *,
    cbf_matrix: Sequence | None = None,
    cbf_lower_bounds: Sequence[float] | None = None,
    clf_matrix: Sequence | None = None,
    clf_upper_bounds: Sequence[float] | None = None,
    lower_bounds: Sequence[float] | None = None,
    upper_bounds: Sequence[float] | None = None,
    slack_penalty: float = 1_000.0,
) -> SafetyFilterResult:
    nominal = np.asarray(nominal_control, dtype=np.float64)
    if nominal.ndim != 1 or nominal.size == 0 or np.any(~np.isfinite(nominal)) or not np.isfinite(slack_penalty) or slack_penalty <= 0.0:
        raise ValueError("nominal control or slack penalty is invalid")
    dimension = nominal.size
    cbf = np.empty((0, dimension)) if cbf_matrix is None else np.asarray(cbf_matrix, dtype=np.float64)
    cbf_lower = np.empty(0) if cbf_lower_bounds is None else np.asarray(cbf_lower_bounds, dtype=np.float64)
    clf = np.empty((0, dimension)) if clf_matrix is None else np.asarray(clf_matrix, dtype=np.float64)
    clf_upper = np.empty(0) if clf_upper_bounds is None else np.asarray(clf_upper_bounds, dtype=np.float64)
    lower = np.full(dimension, -np.inf) if lower_bounds is None else np.asarray(lower_bounds, dtype=np.float64)
    upper = np.full(dimension, np.inf) if upper_bounds is None else np.asarray(upper_bounds, dtype=np.float64)
    if cbf.ndim != 2 or cbf.shape[1] != dimension or cbf_lower.shape != (cbf.shape[0],) or clf.ndim != 2 or clf.shape[1] != dimension or clf_upper.shape != (clf.shape[0],) or lower.shape != nominal.shape or upper.shape != nominal.shape or np.any(~np.isfinite(cbf)) or np.any(~np.isfinite(cbf_lower)) or np.any(~np.isfinite(clf)) or np.any(~np.isfinite(clf_upper)) or np.any(lower > upper):
        raise ValueError("safety-filter constraints are invalid")

    def objective(z: np.ndarray) -> float:
        return 0.5 * float((z[:dimension] - nominal) @ (z[:dimension] - nominal)) + 0.5 * slack_penalty * float(z[-1] ** 2)

    constraints = []
    if cbf.shape[0]:
        constraints.append({"type": "ineq", "fun": lambda z: cbf @ z[:dimension] - cbf_lower})
    if clf.shape[0]:
        constraints.append({"type": "ineq", "fun": lambda z: clf_upper + z[-1] - clf @ z[:dimension]})
    initial = np.r_[np.clip(nominal, lower, upper), 0.0]
    bounds = list(zip(lower, upper)) + [(0.0, None)]
    result = minimize(objective, initial, method="SLSQP", bounds=bounds, constraints=constraints, options={"ftol": 1e-12, "maxiter": 500})
    if not result.success:
        raise RuntimeError(f"CLF-CBF QP failed: {result.message}")
    control = result.x[:dimension]
    slack = float(result.x[-1])
    cbf_margin = float(np.min(cbf @ control - cbf_lower)) if cbf.shape[0] else float("inf")
    clf_residual = float(np.max(clf @ control - clf_upper - slack)) if clf.shape[0] else float("-inf")
    return SafetyFilterResult(control, slack, objective(result.x), cbf_margin, clf_residual)


def high_order_barrier_chain(values: Sequence[float], gains: Sequence[float]) -> float:
    """Evaluate psi_r = h^(r) + sum gain_i h^(i) from supplied derivatives."""
    derivatives = np.asarray(values, dtype=np.float64)
    coefficients = np.asarray(gains, dtype=np.float64)
    if derivatives.ndim != 1 or derivatives.size < 2 or coefficients.shape != (derivatives.size - 1,) or np.any(~np.isfinite(derivatives)) or np.any(~np.isfinite(coefficients)) or np.any(coefficients < 0.0):
        raise ValueError("high-order barrier inputs are invalid")
    return float(derivatives[-1] + coefficients @ derivatives[:-1])
