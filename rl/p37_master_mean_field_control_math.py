"""P37 master-equation diagnostics, finite-player error, and MFC utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Sequence

import numpy as np
from scipy.special import softmax


@dataclass(frozen=True)
class FiniteStateMFGResult:
    distributions: np.ndarray
    values: np.ndarray
    policies: np.ndarray
    fixed_point_residuals: np.ndarray
    iterations: int
    converged: bool


def solve_finite_state_mfg(
    transition: Sequence,
    base_cost: Sequence,
    initial_distribution: Sequence[float],
    coupling_cost: Callable[[int, np.ndarray], np.ndarray],
    terminal_cost: Callable[[np.ndarray], np.ndarray],
    *,
    horizon: int,
    relaxation: float = 0.5,
    entropy_temperature: float = 0.0,
    tolerance: float = 1e-9,
    max_iterations: int = 10_000,
) -> FiniteStateMFGResult:
    """Solve a discrete-time finite-state MFG by relaxed forward-backward iteration."""

    dynamics = np.asarray(transition, dtype=np.float64)
    cost = np.asarray(base_cost, dtype=np.float64)
    initial = np.asarray(initial_distribution, dtype=np.float64)
    if dynamics.ndim != 3:
        raise ValueError("transition must have state, action, next-state axes")
    states, actions, next_states = dynamics.shape
    if (
        states == 0
        or next_states != states
        or cost.shape != (states, actions)
        or initial.shape != (states,)
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=2), 1.0)
        or np.any(~np.isfinite(cost))
        or np.any(~np.isfinite(initial))
        or np.any(initial < 0.0)
        or not np.isclose(initial.sum(), 1.0)
        or horizon < 1
        or not 0.0 < relaxation <= 1.0
        or entropy_temperature < 0.0
        or tolerance <= 0.0
        or max_iterations < 1
    ):
        raise ValueError("finite-state MFG inputs are invalid")
    distributions = np.tile(initial, (horizon + 1, 1))
    residuals = []
    values = np.zeros((horizon + 1, states))
    policies = np.full((horizon, states, actions), 1.0 / actions)
    for iteration in range(1, max_iterations + 1):
        terminal = np.asarray(terminal_cost(distributions[-1].copy()), dtype=np.float64)
        if terminal.shape != (states,) or np.any(~np.isfinite(terminal)):
            raise ValueError("terminal cost returned an invalid vector")
        values[-1] = terminal
        for time in range(horizon - 1, -1, -1):
            coupling = np.asarray(
                coupling_cost(time, distributions[time].copy()), dtype=np.float64
            )
            if coupling.shape == (states,):
                coupling = np.repeat(coupling[:, None], actions, axis=1)
            if coupling.shape != (states, actions) or np.any(~np.isfinite(coupling)):
                raise ValueError("coupling cost returned an invalid array")
            q_values = cost + coupling + np.einsum(
                "sak,k->sa", dynamics, values[time + 1]
            )
            if entropy_temperature > 0.0:
                policies[time] = softmax(-q_values / entropy_temperature, axis=1)
                values[time] = np.sum(policies[time] * q_values, axis=1)
                values[time] += entropy_temperature * np.sum(
                    policies[time] * np.log(np.maximum(policies[time], 1e-300)),
                    axis=1,
                )
            else:
                chosen = np.argmin(q_values, axis=1)
                policies[time] = 0.0
                policies[time, np.arange(states), chosen] = 1.0
                values[time] = q_values[np.arange(states), chosen]
        candidate = np.zeros_like(distributions)
        candidate[0] = initial
        for time in range(horizon):
            candidate[time + 1] = np.einsum(
                "s,sa,sak->k", candidate[time], policies[time], dynamics
            )
        residual = float(np.max(np.abs(candidate - distributions)))
        residuals.append(residual)
        distributions = (1.0 - relaxation) * distributions + relaxation * candidate
        if residual <= tolerance:
            break
    return FiniteStateMFGResult(
        distributions,
        values.copy(),
        policies.copy(),
        np.asarray(residuals),
        iteration,
        residuals[-1] <= tolerance,
    )


def empirical_lions_derivative(
    functional: Callable[[np.ndarray], float],
    particles: Sequence,
    particle_index: int,
    *,
    epsilon: float = 1e-5,
) -> np.ndarray:
    """Finite-difference Lions derivative from an empirical particle lift."""

    sample = np.asarray(particles, dtype=np.float64)
    if (
        sample.ndim != 2
        or sample.shape[0] == 0
        or np.any(~np.isfinite(sample))
        or not 0 <= particle_index < sample.shape[0]
        or epsilon <= 0.0
    ):
        raise ValueError("empirical Lions-derivative inputs are invalid")
    derivative = np.empty(sample.shape[1])
    for coordinate in range(sample.shape[1]):
        positive = sample.copy()
        negative = sample.copy()
        positive[particle_index, coordinate] += epsilon
        negative[particle_index, coordinate] -= epsilon
        first = float(functional(positive))
        second = float(functional(negative))
        if not isfinite(first) or not isfinite(second):
            raise ValueError("functional returned a non-finite value")
        derivative[coordinate] = sample.shape[0] * (first - second) / (2.0 * epsilon)
    return derivative


def master_equation_residual(
    *,
    time_derivative: float,
    state_laplacian: float,
    hamiltonian: float,
    measure_divergences: Sequence[float],
    measure_drift_products: Sequence[float],
    measure_weights: Sequence[float],
    viscosity: float,
) -> float:
    """Residual for the no-common-noise master equation convention in the guide."""

    divergences = np.asarray(measure_divergences, dtype=np.float64)
    drift = np.asarray(measure_drift_products, dtype=np.float64)
    weights = np.asarray(measure_weights, dtype=np.float64)
    scalars = (time_derivative, state_laplacian, hamiltonian, viscosity)
    if (
        divergences.ndim != 1
        or divergences.shape != drift.shape
        or divergences.shape != weights.shape
        or divergences.size == 0
        or np.any(~np.isfinite(divergences))
        or np.any(~np.isfinite(drift))
        or np.any(~np.isfinite(weights))
        or np.any(weights < 0.0)
        or not np.isclose(weights.sum(), 1.0)
        or any(not isfinite(value) for value in scalars)
        or viscosity < 0.0
    ):
        raise ValueError("master-equation residual inputs are invalid")
    return float(
        -time_derivative
        - viscosity * state_laplacian
        + hamiltonian
        - viscosity * (weights @ divergences)
        - weights @ drift
    )


def mean_field_control_marginal_cost(
    individual_cost: Sequence,
    distribution: Sequence[float],
    coupling_derivative: Sequence,
) -> np.ndarray:
    """Add the social externality sum_y m_y d c_y / d m_x."""

    cost = np.asarray(individual_cost, dtype=np.float64)
    population = np.asarray(distribution, dtype=np.float64)
    derivative = np.asarray(coupling_derivative, dtype=np.float64)
    if cost.ndim != 2:
        raise ValueError("individual cost must have state and action axes")
    states, actions = cost.shape
    if (
        population.shape != (states,)
        or derivative.shape != (states, actions, states)
        or np.any(~np.isfinite(cost))
        or np.any(~np.isfinite(population))
        or np.any(population < 0.0)
        or not np.isclose(population.sum(), 1.0)
        or np.any(~np.isfinite(derivative))
    ):
        raise ValueError("mean-field-control cost inputs are invalid")
    externality = np.einsum("y,yax->xa", population, derivative)
    return cost + externality


@dataclass(frozen=True)
class FinitePlayerError:
    maximum_value_error: float
    root_mean_square_value_error: float
    epsilon_nash: float


def finite_player_error_diagnostic(
    finite_values: Sequence[float],
    master_approximations: Sequence[float],
    unilateral_improvements: Sequence[float],
) -> FinitePlayerError:
    finite = np.asarray(finite_values, dtype=np.float64)
    master = np.asarray(master_approximations, dtype=np.float64)
    improvements = np.asarray(unilateral_improvements, dtype=np.float64)
    if (
        finite.ndim != 1
        or finite.size == 0
        or master.shape != finite.shape
        or improvements.shape != finite.shape
        or np.any(~np.isfinite(finite))
        or np.any(~np.isfinite(master))
        or np.any(~np.isfinite(improvements))
    ):
        raise ValueError("finite-player diagnostic inputs are invalid")
    error = finite - master
    return FinitePlayerError(
        float(np.max(np.abs(error))),
        float(np.sqrt(np.mean(error**2))),
        float(np.max(np.maximum(improvements, 0.0))),
    )


@dataclass(frozen=True)
class ConvergenceRate:
    coefficient: float
    exponent: float
    fitted_errors: np.ndarray


def estimate_finite_player_rate(
    population_sizes: Sequence[int], errors: Sequence[float]
) -> ConvergenceRate:
    """Fit error approximately coefficient * N^(-exponent) on positive data."""

    sizes = np.asarray(population_sizes, dtype=np.float64)
    values = np.asarray(errors, dtype=np.float64)
    if (
        sizes.ndim != 1
        or sizes.size < 2
        or values.shape != sizes.shape
        or np.any(~np.isfinite(sizes))
        or np.any(~np.isfinite(values))
        or np.any(sizes <= 0.0)
        or np.any(values <= 0.0)
    ):
        raise ValueError("convergence-rate inputs must be positive")
    slope, intercept = np.polyfit(np.log(sizes), np.log(values), 1)
    coefficient = float(np.exp(intercept))
    exponent = float(-slope)
    return ConvergenceRate(coefficient, exponent, coefficient * sizes ** (-exponent))
