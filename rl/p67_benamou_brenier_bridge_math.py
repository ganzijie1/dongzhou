"""P67 Benamou-Brenier transport and probability-flow bridge helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def continuity_residual(density: Sequence[float], next_density: Sequence[float], face_flux: Sequence[float], *, dt: float, dx: float) -> np.ndarray:
    current = np.asarray(density, dtype=np.float64)
    following = np.asarray(next_density, dtype=np.float64)
    flux = np.asarray(face_flux, dtype=np.float64)
    if current.ndim != 1 or following.shape != current.shape or flux.shape != (current.size + 1,) or dt <= 0.0 or dx <= 0.0:
        raise ValueError("continuity inputs are invalid")
    return (following - current) / dt + np.diff(flux) / dx


def benamou_brenier_action(densities: Sequence, cell_fluxes: Sequence, *, dt: float, dx: float, density_floor: float = 1e-12) -> float:
    density = np.asarray(densities, dtype=np.float64)
    flux = np.asarray(cell_fluxes, dtype=np.float64)
    if density.shape != flux.shape or density.ndim != 2 or np.any(density < 0.0) or dt <= 0.0 or dx <= 0.0 or density_floor <= 0.0:
        raise ValueError("Benamou-Brenier inputs are invalid")
    return float(dt * dx * np.sum(flux**2 / np.maximum(density, density_floor)))


def sinkhorn_coupling(source: Sequence[float], target: Sequence[float], cost: Sequence, *, regularization: float, tolerance: float = 1e-10, max_iterations: int = 10000) -> np.ndarray:
    left = np.asarray(source, dtype=np.float64)
    right = np.asarray(target, dtype=np.float64)
    matrix = np.asarray(cost, dtype=np.float64)
    if left.ndim != 1 or right.ndim != 1 or matrix.shape != (left.size, right.size) or np.any(left < 0.0) or np.any(right < 0.0) or not np.isclose(left.sum(), 1.0) or not np.isclose(right.sum(), 1.0) or regularization <= 0.0:
        raise ValueError("Sinkhorn inputs are invalid")
    kernel = np.exp(-(matrix - matrix.min()) / regularization)
    u = np.ones_like(left)
    v = np.ones_like(right)
    for _ in range(max_iterations):
        previous = u.copy()
        u = left / np.maximum(kernel @ v, 1e-300)
        v = right / np.maximum(kernel.T @ u, 1e-300)
        if np.max(np.abs(u - previous)) <= tolerance:
            coupling = u[:, None] * kernel * v[None, :]
            return coupling
    raise RuntimeError("Sinkhorn iteration did not converge")


def probability_flow_velocity(drift: Sequence[float], diffusion: float, score: Sequence[float]) -> np.ndarray:
    deterministic = np.asarray(drift, dtype=np.float64)
    gradient = np.asarray(score, dtype=np.float64)
    if deterministic.shape != gradient.shape or deterministic.ndim == 0 or diffusion < 0.0:
        raise ValueError("probability-flow inputs are invalid")
    return deterministic - 0.5 * diffusion**2 * gradient


def linear_flow_matching(start: Sequence[float], end: Sequence[float], time: float) -> tuple[np.ndarray, np.ndarray]:
    left = np.asarray(start, dtype=np.float64)
    right = np.asarray(end, dtype=np.float64)
    if left.shape != right.shape or left.ndim == 0 or not 0.0 <= time <= 1.0:
        raise ValueError("flow-matching inputs are invalid")
    return (1.0 - time) * left + time * right, right - left
