"""P39 density-matrix games, EWL protocols, CHSH, and quantum diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, sin, sqrt
from typing import Sequence

import numpy as np


I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
H = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128) / sqrt(2.0)


def density_matrix(state: Sequence[complex]) -> np.ndarray:
    vector = np.asarray(state, dtype=np.complex128)
    if vector.ndim != 1 or vector.size == 0 or np.any(~np.isfinite(vector)):
        raise ValueError("state vector is invalid")
    norm = float(np.vdot(vector, vector).real)
    if norm <= 0.0:
        raise ValueError("state vector has zero norm")
    vector = vector / sqrt(norm)
    return np.outer(vector, vector.conj())


def validate_density_matrix(matrix: Sequence, *, tolerance: float = 1e-10) -> np.ndarray:
    state = np.asarray(matrix, dtype=np.complex128)
    if (
        state.ndim != 2
        or state.shape[0] == 0
        or state.shape[0] != state.shape[1]
        or np.any(~np.isfinite(state))
        or not np.allclose(state, state.conj().T, atol=tolerance)
        or not np.isclose(np.trace(state), 1.0, atol=tolerance)
        or np.min(np.linalg.eigvalsh(state)) < -tolerance
    ):
        raise ValueError("matrix is not a density matrix")
    return state


def partial_trace(
    joint_state: Sequence,
    dimensions: tuple[int, int],
    *,
    trace_out: int,
) -> np.ndarray:
    """Partial trace of one subsystem from a bipartite density matrix."""

    state = validate_density_matrix(joint_state)
    first, second = dimensions
    if first < 1 or second < 1 or first * second != state.shape[0] or trace_out not in (0, 1):
        raise ValueError("partial-trace dimensions are invalid")
    tensor = state.reshape(first, second, first, second)
    if trace_out == 0:
        return np.trace(tensor, axis1=0, axis2=2)
    return np.trace(tensor, axis1=1, axis2=3)


def apply_quantum_channel(state: Sequence, kraus_operators: Sequence[Sequence]) -> np.ndarray:
    """Apply a checked CPTP Kraus channel."""

    density = validate_density_matrix(state)
    operators = tuple(np.asarray(value, dtype=np.complex128) for value in kraus_operators)
    if not operators or any(value.shape != density.shape for value in operators):
        raise ValueError("Kraus operators have invalid shape")
    completeness = sum((value.conj().T @ value for value in operators), np.zeros_like(density))
    if not np.allclose(completeness, np.eye(density.shape[0]), atol=1e-10):
        raise ValueError("Kraus operators are not trace preserving")
    result = sum((value @ density @ value.conj().T for value in operators), np.zeros_like(density))
    result = (result + result.conj().T) / 2.0
    return validate_density_matrix(result)


def povm_probabilities(state: Sequence, measurement: Sequence[Sequence]) -> np.ndarray:
    density = validate_density_matrix(state)
    elements = tuple(np.asarray(value, dtype=np.complex128) for value in measurement)
    if not elements or any(value.shape != density.shape for value in elements):
        raise ValueError("POVM elements have invalid shape")
    if any(
        not np.allclose(value, value.conj().T, atol=1e-10)
        or np.min(np.linalg.eigvalsh(value)) < -1e-10
        for value in elements
    ):
        raise ValueError("POVM elements must be positive semidefinite")
    if not np.allclose(sum(elements, np.zeros_like(density)), np.eye(density.shape[0])):
        raise ValueError("POVM elements do not sum to identity")
    probabilities = np.array([np.trace(value @ density).real for value in elements])
    probabilities = np.maximum(probabilities, 0.0)
    return probabilities / probabilities.sum()


def quantum_expected_payoff(
    state: Sequence,
    measurement: Sequence[Sequence],
    outcome_payoffs: Sequence[float],
) -> float:
    probabilities = povm_probabilities(state, measurement)
    payoffs = np.asarray(outcome_payoffs, dtype=np.float64)
    if payoffs.shape != probabilities.shape or np.any(~np.isfinite(payoffs)):
        raise ValueError("outcome payoffs are invalid")
    return float(probabilities @ payoffs)


def su2(theta: float, phi: float, lam: float) -> np.ndarray:
    if any(not isfinite(value) for value in (theta, phi, lam)):
        raise ValueError("SU(2) parameters must be finite")
    return np.array(
        [
            [cos(theta / 2.0), -np.exp(1j * lam) * sin(theta / 2.0)],
            [np.exp(1j * phi) * sin(theta / 2.0), np.exp(1j * (phi + lam)) * cos(theta / 2.0)],
        ],
        dtype=np.complex128,
    )


@dataclass(frozen=True)
class EWLResult:
    outcome_probabilities: np.ndarray
    expected_payoffs: np.ndarray
    final_state: np.ndarray


def ewl_two_player_game(
    first_strategy: Sequence,
    second_strategy: Sequence,
    first_payoffs: Sequence[Sequence[float]],
    second_payoffs: Sequence[Sequence[float]],
    *,
    entanglement: float,
) -> EWLResult:
    """Eisert-Wilkens-Lewenstein protocol with J=exp(i gamma XxX/2)."""

    first = np.asarray(first_strategy, dtype=np.complex128)
    second = np.asarray(second_strategy, dtype=np.complex128)
    payoff_one = np.asarray(first_payoffs, dtype=np.float64)
    payoff_two = np.asarray(second_payoffs, dtype=np.float64)
    if (
        first.shape != (2, 2)
        or second.shape != (2, 2)
        or not np.allclose(first.conj().T @ first, I2)
        or not np.allclose(second.conj().T @ second, I2)
        or payoff_one.shape != (2, 2)
        or payoff_two.shape != (2, 2)
        or np.any(~np.isfinite(payoff_one))
        or np.any(~np.isfinite(payoff_two))
        or not isfinite(entanglement)
        or not 0.0 <= entanglement <= pi / 2.0
    ):
        raise ValueError("EWL inputs are invalid")
    interaction = np.kron(X, X)
    entangler = cos(entanglement / 2.0) * np.eye(4) + 1j * sin(entanglement / 2.0) * interaction
    initial = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    final = entangler.conj().T @ np.kron(first, second) @ entangler @ initial
    probabilities = np.abs(final) ** 2
    payoffs = np.array(
        [probabilities @ payoff_one.reshape(-1), probabilities @ payoff_two.reshape(-1)]
    )
    return EWLResult(probabilities.reshape(2, 2), payoffs, final)


def ewl_classical_cooperate() -> np.ndarray:
    return I2.copy()


def ewl_classical_defect() -> np.ndarray:
    return 1j * X


def ewl_quantum_strategy() -> np.ndarray:
    return 1j * Z


def _projectors(observable: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return (I2 + observable) / 2.0, (I2 - observable) / 2.0


@dataclass(frozen=True)
class CHSHResult:
    conditional_probabilities: np.ndarray
    winning_probability: float
    no_signalling_residual: float


def chsh_optimal_quantum_strategy() -> CHSHResult:
    """Evaluate the canonical Bell-state CHSH strategy."""

    bell = density_matrix([1.0 / sqrt(2.0), 0.0, 0.0, 1.0 / sqrt(2.0)])
    alice = (_projectors(Z), _projectors(X))
    bob = (
        _projectors((Z + X) / sqrt(2.0)),
        _projectors((Z - X) / sqrt(2.0)),
    )
    conditional = np.zeros((2, 2, 2, 2))
    for question_a in range(2):
        for question_b in range(2):
            for answer_a in range(2):
                for answer_b in range(2):
                    operator = np.kron(
                        alice[question_a][answer_a], bob[question_b][answer_b]
                    )
                    conditional[question_a, question_b, answer_a, answer_b] = np.trace(
                        operator @ bell
                    ).real
    win = 0.0
    for x_value in range(2):
        for y_value in range(2):
            for a_value in range(2):
                for b_value in range(2):
                    if (a_value ^ b_value) == (x_value & y_value):
                        win += 0.25 * conditional[x_value, y_value, a_value, b_value]
    residual = 0.0
    for x_value in range(2):
        for a_value in range(2):
            marginal = conditional[x_value, :, a_value, :].sum(axis=1)
            residual = max(residual, float(np.max(marginal) - np.min(marginal)))
    for y_value in range(2):
        for b_value in range(2):
            marginal = conditional[:, y_value, :, b_value].sum(axis=1)
            residual = max(residual, float(np.max(marginal) - np.min(marginal)))
    return CHSHResult(conditional, float(win), residual)


def depolarizing_channel(state: Sequence, *, probability: float) -> np.ndarray:
    density = validate_density_matrix(state)
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("depolarizing probability is invalid")
    dimension = density.shape[0]
    return (1.0 - probability) * density + probability * np.eye(dimension) / dimension


@dataclass(frozen=True)
class FiniteNashDiagnostic:
    profile_payoffs: np.ndarray
    best_deviation_payoffs: np.ndarray
    regrets: np.ndarray
    is_nash: bool


def finite_quantum_nash_diagnostic(
    payoff_tables: Sequence,
    profile: tuple[int, int],
    *,
    tolerance: float = 1e-10,
) -> FiniteNashDiagnostic:
    """Nash audit after any finite quantum strategy set has been evaluated."""

    payoffs = np.asarray(payoff_tables, dtype=np.float64)
    if (
        payoffs.ndim != 3
        or payoffs.shape[0] != 2
        or min(payoffs.shape[1:]) == 0
        or np.any(~np.isfinite(payoffs))
        or not 0 <= profile[0] < payoffs.shape[1]
        or not 0 <= profile[1] < payoffs.shape[2]
        or tolerance < 0.0
    ):
        raise ValueError("finite Nash diagnostic inputs are invalid")
    current = np.array(
        [payoffs[0, profile[0], profile[1]], payoffs[1, profile[0], profile[1]]]
    )
    best = np.array(
        [
            np.max(payoffs[0, :, profile[1]]),
            np.max(payoffs[1, profile[0], :]),
        ]
    )
    regrets = np.maximum(best - current, 0.0)
    return FiniteNashDiagnostic(current, best, regrets, bool(np.max(regrets) <= tolerance))
