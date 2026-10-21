"""Consensus, DeGroot, and Altafini dynamics on finite weighted graphs."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.linalg import expm


def _square_matrix(values: Sequence[Sequence[float]], name: str) -> np.ndarray:
    matrix = np.asarray(values, dtype=np.float64)
    if (
        matrix.ndim != 2
        or matrix.shape[0] == 0
        or matrix.shape[0] != matrix.shape[1]
        or np.any(~np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite non-empty square matrix")
    return matrix


def _state(values: Sequence[float], size: int, name: str = "state") -> np.ndarray:
    state = np.asarray(values, dtype=np.float64)
    if state.shape != (size,) or np.any(~np.isfinite(state)):
        raise ValueError(f"{name} must be a finite vector aligned with the graph")
    return state


def graph_laplacian(
    adjacency: Sequence[Sequence[float]], *, signed: bool = False
) -> np.ndarray:
    """Return D-A, using absolute weighted degree for a signed graph."""

    matrix = _square_matrix(adjacency, "adjacency")
    if not np.allclose(np.diag(matrix), 0.0):
        raise ValueError("graph adjacency must have a zero diagonal")
    if not signed and np.any(matrix < 0.0):
        raise ValueError("unsigned graph adjacency cannot contain negative weights")
    degree = np.sum(np.abs(matrix) if signed else matrix, axis=1)
    return np.diag(degree) - matrix


@dataclass(frozen=True)
class GraphTrajectory:
    times: np.ndarray
    states: np.ndarray


def continuous_graph_dynamics(
    adjacency: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    times: Sequence[float],
    *,
    signed: bool = False,
) -> GraphTrajectory:
    """Solve x_dot=-Lx exactly at requested non-negative time points."""

    laplacian = graph_laplacian(adjacency, signed=signed)
    initial = _state(initial_state, laplacian.shape[0], "initial state")
    time_points = np.asarray(times, dtype=np.float64)
    if (
        time_points.ndim != 1
        or time_points.size == 0
        or np.any(~np.isfinite(time_points))
        or np.any(time_points < 0.0)
        or np.any(np.diff(time_points) < 0.0)
    ):
        raise ValueError("graph-dynamics times must be finite, non-negative, and sorted")
    states = np.stack([expm(-time * laplacian) @ initial for time in time_points])
    return GraphTrajectory(time_points, states)


def _influence_matrix(
    values: Sequence[Sequence[float]], *, signed: bool
) -> np.ndarray:
    matrix = _square_matrix(values, "influence matrix")
    if not signed and np.any(matrix < 0.0):
        raise ValueError("DeGroot weights must be non-negative")
    row_mass = np.sum(np.abs(matrix) if signed else matrix, axis=1)
    if not np.allclose(row_mass, 1.0, atol=1e-10, rtol=1e-10):
        description = "absolute row sums" if signed else "row sums"
        raise ValueError(f"influence-matrix {description} must equal one")
    return matrix


def stationary_influence(weights: Sequence[Sequence[float]]) -> np.ndarray:
    """Return a normalized non-negative left stationary vector of a DeGroot matrix."""

    matrix = _influence_matrix(weights, signed=False)
    size = matrix.shape[0]
    system = np.vstack([matrix.T - np.eye(size), np.ones((1, size))])
    target = np.r_[np.zeros(size), 1.0]
    influence, *_ = np.linalg.lstsq(system, target, rcond=None)
    influence[np.abs(influence) < 1e-12] = 0.0
    if np.any(influence < -1e-9) or np.linalg.norm(influence @ matrix - influence) > 1e-8:
        raise ValueError("could not recover a valid stationary influence vector")
    influence = np.maximum(influence, 0.0)
    return influence / influence.sum()


@dataclass(frozen=True)
class DeGrootResult:
    trajectory: np.ndarray
    influence: np.ndarray
    consensus_value: float | None
    consensus_errors: np.ndarray
    ergodic: bool
    spectral_contraction: float


def degroot_dynamics(
    weights: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    *,
    steps: int = 100,
    tolerance: float = 1e-10,
) -> DeGrootResult:
    """Simulate DeGroot averaging and diagnose asymptotic consensus."""

    matrix = _influence_matrix(weights, signed=False)
    initial = _state(initial_state, matrix.shape[0], "initial state")
    if steps < 0 or tolerance <= 0.0:
        raise ValueError("DeGroot steps and tolerance are invalid")
    trajectory = np.empty((steps + 1, matrix.shape[0]), dtype=np.float64)
    trajectory[0] = initial
    for step in range(steps):
        trajectory[step + 1] = matrix @ trajectory[step]

    eigenvalues = np.linalg.eigvals(matrix)
    principal = int(np.argmin(np.abs(eigenvalues - 1.0)))
    other_moduli = np.delete(np.abs(eigenvalues), principal)
    contraction = float(np.max(other_moduli, initial=0.0))
    one_is_simple = int(np.sum(np.abs(eigenvalues - 1.0) <= tolerance)) == 1
    ergodic = one_is_simple and contraction < 1.0 - tolerance
    influence = stationary_influence(matrix)
    value = float(influence @ initial) if ergodic else None
    target = np.full(matrix.shape[0], value) if value is not None else trajectory[-1]
    errors = np.linalg.norm(trajectory - target[None, :], axis=1)
    return DeGrootResult(
        trajectory,
        influence,
        value,
        errors,
        ergodic,
        contraction,
    )


@dataclass(frozen=True)
class StructuralBalanceResult:
    balanced: bool
    signs: tuple[int, ...] | None
    components: tuple[frozenset[int], ...]


def structural_balance(
    signed_adjacency: Sequence[Sequence[float]], *, tolerance: float = 1e-12
) -> StructuralBalanceResult:
    """Find a two-camp gauge assignment for a finite directed signed graph."""

    matrix = _square_matrix(signed_adjacency, "signed adjacency")
    if tolerance <= 0.0:
        raise ValueError("structural-balance tolerance must be positive")
    size = matrix.shape[0]
    neighbors: list[list[tuple[int, int]]] = [[] for _ in range(size)]
    balanced = True
    for row in range(size):
        for column in range(size):
            value = matrix[row, column]
            if abs(value) <= tolerance:
                continue
            sign = 1 if value > 0.0 else -1
            if row == column:
                balanced = balanced and sign > 0
                continue
            neighbors[row].append((column, sign))
            neighbors[column].append((row, sign))

    signs = np.zeros(size, dtype=np.int8)
    components = []
    for root in range(size):
        if signs[root] != 0:
            continue
        signs[root] = 1
        component = {root}
        frontier = [root]
        while frontier:
            node = frontier.pop()
            for neighbor, edge_sign in neighbors[node]:
                expected = int(signs[node]) * edge_sign
                if signs[neighbor] == 0:
                    signs[neighbor] = expected
                    component.add(neighbor)
                    frontier.append(neighbor)
                elif signs[neighbor] != expected:
                    balanced = False
        components.append(frozenset(component))
    return StructuralBalanceResult(
        balanced,
        tuple(map(int, signs)) if balanced else None,
        tuple(components),
    )


def bipartite_consensus_error(
    state: Sequence[float], signs: Sequence[int]
) -> float:
    values = np.asarray(state, dtype=np.float64)
    gauge = np.asarray(signs, dtype=np.float64)
    if (
        values.ndim != 1
        or gauge.shape != values.shape
        or np.any(~np.isfinite(values))
        or np.any(~np.isin(gauge, (-1.0, 1.0)))
    ):
        raise ValueError("bipartite consensus needs aligned finite states and signs")
    transformed = gauge * values
    return float(np.linalg.norm(transformed - transformed.mean()))


@dataclass(frozen=True)
class AltafiniResult:
    trajectory: np.ndarray
    balance: StructuralBalanceResult
    gauge_trajectory: np.ndarray | None
    polarization_errors: np.ndarray


def continuous_altafini_dynamics(
    signed_adjacency: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    times: Sequence[float],
) -> AltafiniResult:
    """Solve the continuous Altafini model x_dot=-L_s x."""

    matrix = _square_matrix(signed_adjacency, "signed adjacency")
    trajectory = continuous_graph_dynamics(matrix, initial_state, times, signed=True)
    balance = structural_balance(matrix)
    if balance.signs is None:
        errors = np.linalg.norm(trajectory.states, axis=1)
        return AltafiniResult(trajectory.states, balance, None, errors)
    signs = np.asarray(balance.signs, dtype=np.float64)
    gauge = trajectory.states * signs[None, :]
    errors = np.linalg.norm(gauge - gauge.mean(axis=1, keepdims=True), axis=1)
    return AltafiniResult(trajectory.states, balance, gauge, errors)


def discrete_altafini_dynamics(
    signed_weights: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    *,
    steps: int = 100,
) -> AltafiniResult:
    """Simulate a signed discrete influence matrix with unit absolute row sums."""

    matrix = _influence_matrix(signed_weights, signed=True)
    initial = _state(initial_state, matrix.shape[0], "initial state")
    if steps < 0:
        raise ValueError("Altafini steps must be non-negative")
    trajectory = np.empty((steps + 1, matrix.shape[0]), dtype=np.float64)
    trajectory[0] = initial
    for step in range(steps):
        trajectory[step + 1] = matrix @ trajectory[step]
    balance = structural_balance(matrix)
    if balance.signs is None:
        return AltafiniResult(
            trajectory,
            balance,
            None,
            np.linalg.norm(trajectory, axis=1),
        )
    signs = np.asarray(balance.signs, dtype=np.float64)
    gauge = trajectory * signs[None, :]
    errors = np.linalg.norm(gauge - gauge.mean(axis=1, keepdims=True), axis=1)
    return AltafiniResult(trajectory, balance, gauge, errors)


def controlled_degroot_dynamics(
    weights: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    controls: Sequence[Sequence[float]],
    *,
    input_matrix: Sequence[Sequence[float]] | None = None,
    clip: tuple[float, float] | None = None,
) -> np.ndarray:
    """Simulate x(k+1)=Wx(k)+Bu(k), optionally clipping every state."""

    matrix = _influence_matrix(weights, signed=False)
    initial = _state(initial_state, matrix.shape[0], "initial state")
    control = np.asarray(controls, dtype=np.float64)
    if control.ndim != 2 or np.any(~np.isfinite(control)):
        raise ValueError("controls must be a finite steps-by-inputs matrix")
    inputs = (
        np.eye(matrix.shape[0], dtype=np.float64)
        if input_matrix is None
        else np.asarray(input_matrix, dtype=np.float64)
    )
    if inputs.shape != (matrix.shape[0], control.shape[1]) or np.any(~np.isfinite(inputs)):
        raise ValueError("input matrix must align graph states and controls")
    if clip is not None:
        lower, upper = map(float, clip)
        if not isfinite(lower) or not isfinite(upper) or lower >= upper:
            raise ValueError("control clipping bounds are invalid")
    trajectory = np.empty((control.shape[0] + 1, matrix.shape[0]), dtype=np.float64)
    trajectory[0] = initial
    for step, action in enumerate(control):
        updated = matrix @ trajectory[step] + inputs @ action
        trajectory[step + 1] = (
            np.clip(updated, *clip) if clip is not None else updated
        )
    return trajectory
