"""P31 variational inequalities, splitting, and stochastic approximation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence

import numpy as np

ArrayFunction = Callable[[np.ndarray], np.ndarray]


def project_simplex(values: Sequence[float]) -> np.ndarray:
    """Euclidean projection onto the probability simplex."""

    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0 or np.any(~np.isfinite(vector)):
        raise ValueError("simplex projection needs a finite non-empty vector")
    ordered = np.sort(vector)[::-1]
    cumulative = np.cumsum(ordered)
    support = np.nonzero(
        ordered - (cumulative - 1.0) / np.arange(1, vector.size + 1) > 0.0
    )[0]
    threshold = (cumulative[support[-1]] - 1.0) / (support[-1] + 1)
    projected = np.maximum(vector - threshold, 0.0)
    return projected / projected.sum()


def _box_projection(lower: np.ndarray, upper: np.ndarray) -> ArrayFunction:
    return lambda value: np.clip(value, lower, upper)


def _vector(value: Sequence[float], name: str) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != 1 or result.size == 0 or np.any(~np.isfinite(result)):
        raise ValueError(f"{name} must be a finite non-empty vector")
    return result


@dataclass(frozen=True)
class FirstOrderResult:
    point: np.ndarray
    residuals: np.ndarray
    iterations: int
    converged: bool


def mirror_descent_simplex(
    initial: Sequence[float],
    gradient: ArrayFunction,
    step_sizes: Sequence[float],
    *,
    tolerance: float = 1e-10,
) -> FirstOrderResult:
    """Entropic mirror descent for a differentiable simplex objective."""

    point = _vector(initial, "initial point")
    if np.any(point < 0.0) or point.sum() <= 0.0 or tolerance <= 0.0:
        raise ValueError("mirror-descent inputs are invalid")
    point = point / point.sum()
    steps = _vector(step_sizes, "step sizes")
    if np.any(steps <= 0.0):
        raise ValueError("step sizes must be positive")
    residuals = []
    for step in steps:
        direction = np.asarray(gradient(point.copy()), dtype=np.float64)
        if direction.shape != point.shape or np.any(~np.isfinite(direction)):
            raise ValueError("gradient returned an invalid vector")
        logits = np.log(np.maximum(point, np.finfo(float).tiny)) - step * direction
        logits -= np.max(logits)
        updated = np.exp(logits)
        updated /= updated.sum()
        residuals.append(float(np.max(np.abs(updated - point))))
        point = updated
    return FirstOrderResult(
        point,
        np.asarray(residuals),
        len(steps),
        bool(residuals and residuals[-1] <= tolerance),
    )


def extragradient(
    operator: ArrayFunction,
    initial: Sequence[float],
    *,
    step_size: float,
    iterations: int,
    lower: Sequence[float] | None = None,
    upper: Sequence[float] | None = None,
    tolerance: float = 1e-10,
) -> FirstOrderResult:
    """Korpelevich extragradient for a monotone variational inequality."""

    point = _vector(initial, "initial point")
    if not isfinite(step_size) or step_size <= 0.0 or iterations < 1 or tolerance <= 0.0:
        raise ValueError("extragradient settings are invalid")
    if (lower is None) != (upper is None):
        raise ValueError("both box bounds must be provided")
    if lower is None:
        def projection(value: np.ndarray) -> np.ndarray:
            return np.asarray(value, dtype=np.float64)
    else:
        low = _vector(lower, "lower bound")
        high = _vector(upper, "upper bound")
        if low.shape != point.shape or high.shape != point.shape or np.any(low > high):
            raise ValueError("box bounds are invalid")
        projection = _box_projection(low, high)
        point = projection(point)
    residuals = []
    for _ in range(iterations):
        first = np.asarray(operator(point.copy()), dtype=np.float64)
        if first.shape != point.shape or np.any(~np.isfinite(first)):
            raise ValueError("operator returned an invalid vector")
        prediction = projection(point - step_size * first)
        second = np.asarray(operator(prediction.copy()), dtype=np.float64)
        if second.shape != point.shape or np.any(~np.isfinite(second)):
            raise ValueError("operator returned an invalid vector")
        updated = projection(point - step_size * second)
        residuals.append(float(np.linalg.norm(updated - point)))
        point = updated
        if residuals[-1] <= tolerance:
            break
    return FirstOrderResult(
        point,
        np.asarray(residuals),
        len(residuals),
        residuals[-1] <= tolerance,
    )


def optimistic_gradient(
    gradients: Sequence[Sequence[float]],
    initial: Sequence[float],
    *,
    step_size: float,
    lower: Sequence[float] | None = None,
    upper: Sequence[float] | None = None,
) -> np.ndarray:
    """Online optimistic gradient descent using the previous gradient predictor."""

    point = _vector(initial, "initial point")
    data = np.asarray(gradients, dtype=np.float64)
    if (
        data.ndim != 2
        or data.shape[1:] != point.shape
        or data.shape[0] == 0
        or np.any(~np.isfinite(data))
        or not isfinite(step_size)
        or step_size <= 0.0
    ):
        raise ValueError("optimistic-gradient inputs are invalid")
    if lower is None and upper is None:
        def projection(value: np.ndarray) -> np.ndarray:
            return np.asarray(value, dtype=np.float64)
    elif lower is not None and upper is not None:
        low = _vector(lower, "lower bound")
        high = _vector(upper, "upper bound")
        if low.shape != point.shape or high.shape != point.shape or np.any(low > high):
            raise ValueError("box bounds are invalid")
        projection = _box_projection(low, high)
    else:
        raise ValueError("both box bounds must be provided")
    path = [projection(point)]
    previous = np.zeros_like(point)
    anchor = path[0]
    for current in data:
        played = projection(anchor - step_size * previous)
        anchor = projection(anchor - step_size * current)
        path.append(played)
        previous = current
    return np.asarray(path)


@dataclass(frozen=True)
class VIGap:
    stampacchia: float
    minty: float


def variational_inequality_gap(
    operator: ArrayFunction,
    point: Sequence[float],
    comparison_points: Sequence[Sequence[float]],
) -> VIGap:
    """Finite-set Stampacchia and Minty gap diagnostics."""

    current = _vector(point, "point")
    candidates = np.asarray(comparison_points, dtype=np.float64)
    if (
        candidates.ndim != 2
        or candidates.shape[1:] != current.shape
        or candidates.shape[0] == 0
        or np.any(~np.isfinite(candidates))
    ):
        raise ValueError("comparison points are invalid")
    current_operator = np.asarray(operator(current), dtype=np.float64)
    if current_operator.shape != current.shape or np.any(~np.isfinite(current_operator)):
        raise ValueError("operator returned an invalid vector")
    stampacchia = max(
        0.0,
        max(float(current_operator @ (current - candidate)) for candidate in candidates),
    )
    minty = 0.0
    for candidate in candidates:
        value = np.asarray(operator(candidate), dtype=np.float64)
        if value.shape != current.shape or np.any(~np.isfinite(value)):
            raise ValueError("operator returned an invalid vector")
        minty = max(minty, float(value @ (current - candidate)))
    return VIGap(stampacchia, minty)


def affine_proximal_point(
    matrix: Sequence[Sequence[float]],
    offset: Sequence[float],
    initial: Sequence[float],
    *,
    step_size: float,
    iterations: int,
    tolerance: float = 1e-10,
) -> FirstOrderResult:
    """Proximal point for the affine monotone operator F(x)=Ax+b."""

    linear = np.asarray(matrix, dtype=np.float64)
    bias = _vector(offset, "offset")
    point = _vector(initial, "initial point")
    if (
        linear.shape != (point.size, point.size)
        or bias.shape != point.shape
        or np.any(~np.isfinite(linear))
        or step_size <= 0.0
        or iterations < 1
        or tolerance <= 0.0
    ):
        raise ValueError("proximal-point inputs are invalid")
    system = np.eye(point.size) + step_size * linear
    residuals = []
    for _ in range(iterations):
        updated = np.linalg.solve(system, point - step_size * bias)
        residuals.append(float(np.linalg.norm(linear @ updated + bias)))
        point = updated
        if residuals[-1] <= tolerance:
            break
    return FirstOrderResult(
        point,
        np.asarray(residuals),
        len(residuals),
        residuals[-1] <= tolerance,
    )


def douglas_rachford(
    prox_first: ArrayFunction,
    prox_second: ArrayFunction,
    initial: Sequence[float],
    *,
    iterations: int,
    relaxation: float = 1.0,
    tolerance: float = 1e-10,
) -> FirstOrderResult:
    """Douglas-Rachford splitting for two supplied proximal operators."""

    iterate = _vector(initial, "initial point")
    if iterations < 1 or not 0.0 < relaxation < 2.0 or tolerance <= 0.0:
        raise ValueError("Douglas-Rachford settings are invalid")
    residuals = []
    shadow = iterate.copy()
    for _ in range(iterations):
        first = np.asarray(prox_first(iterate.copy()), dtype=np.float64)
        if first.shape != iterate.shape or np.any(~np.isfinite(first)):
            raise ValueError("first proximal operator is invalid")
        second = np.asarray(prox_second(2.0 * first - iterate), dtype=np.float64)
        if second.shape != iterate.shape or np.any(~np.isfinite(second)):
            raise ValueError("second proximal operator is invalid")
        updated = iterate + relaxation * (second - first)
        shadow = first
        residuals.append(float(np.linalg.norm(updated - iterate)))
        iterate = updated
        if residuals[-1] <= tolerance:
            break
    return FirstOrderResult(
        shadow,
        np.asarray(residuals),
        len(residuals),
        residuals[-1] <= tolerance,
    )


def robbins_monro(
    initial: Sequence[float],
    noisy_operator: Callable[[int, np.ndarray], np.ndarray],
    step_sizes: Sequence[float],
) -> np.ndarray:
    """Return the full Robbins-Monro iterate path for root finding."""

    point = _vector(initial, "initial point")
    steps = _vector(step_sizes, "step sizes")
    if np.any(steps <= 0.0):
        raise ValueError("Robbins-Monro step sizes must be positive")
    path = [point.copy()]
    for index, step in enumerate(steps):
        value = np.asarray(noisy_operator(index, point.copy()), dtype=np.float64)
        if value.shape != point.shape or np.any(~np.isfinite(value)):
            raise ValueError("noisy operator returned an invalid vector")
        point = point - step * value
        path.append(point.copy())
    return np.asarray(path)


@dataclass(frozen=True)
class TwoTimescaleResult:
    slow_path: np.ndarray
    fast_path: np.ndarray
    averaged_slow: np.ndarray


def two_timescale_stochastic_approximation(
    initial_slow: Sequence[float],
    initial_fast: Sequence[float],
    slow_operator: Callable[[int, np.ndarray, np.ndarray], np.ndarray],
    fast_operator: Callable[[int, np.ndarray, np.ndarray], np.ndarray],
    slow_steps: Sequence[float],
    fast_steps: Sequence[float],
    *,
    average_burn_in: int = 0,
) -> TwoTimescaleResult:
    """Generic two-timescale recursion; convention is x <- x - step * F."""

    slow = _vector(initial_slow, "slow initial point")
    fast = _vector(initial_fast, "fast initial point")
    alpha = _vector(slow_steps, "slow step sizes")
    beta = _vector(fast_steps, "fast step sizes")
    if (
        alpha.shape != beta.shape
        or np.any(alpha <= 0.0)
        or np.any(beta <= 0.0)
        or not 0 <= average_burn_in < alpha.size + 1
    ):
        raise ValueError("two-timescale settings are invalid")
    slow_path = [slow.copy()]
    fast_path = [fast.copy()]
    for index, (slow_step, fast_step) in enumerate(zip(alpha, beta, strict=True)):
        fast_value = np.asarray(fast_operator(index, slow.copy(), fast.copy()))
        slow_value = np.asarray(slow_operator(index, slow.copy(), fast.copy()))
        if (
            fast_value.shape != fast.shape
            or slow_value.shape != slow.shape
            or np.any(~np.isfinite(fast_value))
            or np.any(~np.isfinite(slow_value))
        ):
            raise ValueError("two-timescale operator returned invalid values")
        fast = fast - fast_step * fast_value
        slow = slow - slow_step * slow_value
        fast_path.append(fast.copy())
        slow_path.append(slow.copy())
    slow_array = np.asarray(slow_path)
    return TwoTimescaleResult(
        slow_array,
        np.asarray(fast_path),
        slow_array[average_burn_in:].mean(axis=0),
    )


def polyak_ruppert_average(
    iterates: Sequence[Sequence[float]], *, burn_in: int = 0
) -> np.ndarray:
    """Polyak-Ruppert average of a vector iterate sequence."""

    values = np.asarray(iterates, dtype=np.float64)
    if (
        values.ndim != 2
        or values.shape[0] == 0
        or np.any(~np.isfinite(values))
        or not 0 <= burn_in < values.shape[0]
    ):
        raise ValueError("averaging inputs are invalid")
    return values[burn_in:].mean(axis=0)


@dataclass(frozen=True)
class StabilityDiagnostic:
    radial_drifts: np.ndarray
    maximum_outer_drift: float
    stable_outside_radius: bool


def borkar_meyn_stability_diagnostic(
    points: Sequence[Sequence[float]],
    drifts: Sequence[Sequence[float]],
    *,
    radius: float,
) -> StabilityDiagnostic:
    """Empirical radial-drift check; a diagnostic, not a stability proof."""

    states = np.asarray(points, dtype=np.float64)
    fields = np.asarray(drifts, dtype=np.float64)
    if (
        states.ndim != 2
        or states.shape != fields.shape
        or states.shape[0] == 0
        or np.any(~np.isfinite(states))
        or np.any(~np.isfinite(fields))
        or radius < 0.0
    ):
        raise ValueError("stability diagnostic inputs are invalid")
    radial = np.einsum("ij,ij->i", states, fields)
    outer = radial[np.linalg.norm(states, axis=1) >= radius]
    maximum = float(np.max(outer)) if outer.size else float("nan")
    return StabilityDiagnostic(radial, maximum, bool(outer.size and maximum < 0.0))
