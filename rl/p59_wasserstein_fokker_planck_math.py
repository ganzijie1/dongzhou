"""P59 one-dimensional Wasserstein, JKO, entropy, and Fokker-Planck tools."""

from __future__ import annotations

from math import isfinite, sqrt
from typing import Sequence

import numpy as np


def _weighted_measure(support: Sequence[float], weights: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    points = np.asarray(support, dtype=np.float64)
    mass = np.asarray(weights, dtype=np.float64)
    if points.ndim != 1 or points.size == 0 or mass.shape != points.shape or np.any(~np.isfinite(points)) or np.any(~np.isfinite(mass)) or np.any(mass < 0.0) or not np.isclose(mass.sum(), 1.0):
        raise ValueError("weighted measure is invalid")
    order = np.argsort(points)
    return points[order], mass[order]


def wasserstein_1d(
    support_a: Sequence[float],
    weights_a: Sequence[float],
    support_b: Sequence[float],
    weights_b: Sequence[float],
    *,
    order: float = 2.0,
) -> float:
    if not isfinite(order) or order < 1.0:
        raise ValueError("Wasserstein order must be at least one")
    first_x, first_w = _weighted_measure(support_a, weights_a)
    second_x, second_w = _weighted_measure(support_b, weights_b)
    i = j = 0
    remaining_i = first_w[0]
    remaining_j = second_w[0]
    cost = 0.0
    while i < first_x.size and j < second_x.size:
        moved = min(remaining_i, remaining_j)
        cost += moved * abs(first_x[i] - second_x[j]) ** order
        remaining_i -= moved
        remaining_j -= moved
        if remaining_i <= 1e-15:
            i += 1
            if i < first_x.size:
                remaining_i = first_w[i]
        if remaining_j <= 1e-15:
            j += 1
            if j < second_x.size:
                remaining_j = second_w[j]
    return float(cost ** (1.0 / order))


def boltzmann_entropy(probability_masses: Sequence[float], *, cell_volume: float = 1.0) -> float:
    mass = np.asarray(probability_masses, dtype=np.float64)
    if mass.ndim != 1 or mass.size == 0 or np.any(~np.isfinite(mass)) or np.any(mass < 0.0) or not np.isclose(mass.sum(), 1.0) or not isfinite(cell_volume) or cell_volume <= 0.0:
        raise ValueError("entropy inputs are invalid")
    positive = mass > 0.0
    density = mass[positive] / cell_volume
    return float(np.sum(mass[positive] * np.log(density)))


def free_energy(
    probability_masses: Sequence[float],
    potential: Sequence[float],
    *,
    beta: float,
    cell_volume: float = 1.0,
) -> float:
    mass = np.asarray(probability_masses, dtype=np.float64)
    energy = np.asarray(potential, dtype=np.float64)
    if energy.shape != mass.shape or np.any(~np.isfinite(energy)) or not isfinite(beta) or beta <= 0.0:
        raise ValueError("free-energy inputs are invalid")
    return boltzmann_entropy(mass, cell_volume=cell_volume) / beta + float(mass @ energy)


def relative_fisher_information(
    density: Sequence[float], equilibrium_density: Sequence[float], grid: Sequence[float]
) -> float:
    rho = np.asarray(density, dtype=np.float64)
    equilibrium = np.asarray(equilibrium_density, dtype=np.float64)
    points = np.asarray(grid, dtype=np.float64)
    if rho.ndim != 1 or equilibrium.shape != rho.shape or points.shape != rho.shape or rho.size < 3 or np.any(rho <= 0.0) or np.any(equilibrium <= 0.0) or np.any(~np.isfinite(rho)) or np.any(~np.isfinite(equilibrium)) or np.any(np.diff(points) <= 0.0):
        raise ValueError("Fisher-information inputs are invalid")
    gradient = np.gradient(np.log(rho / equilibrium), points)
    return float(np.trapezoid(rho * gradient**2, points))


def jko_gaussian_heat_standard_deviation(previous_standard_deviation: float, time_step: float) -> float:
    """Exact centered-Gaussian minimizer of one heat-equation JKO step."""
    if not isfinite(previous_standard_deviation) or not isfinite(time_step) or previous_standard_deviation <= 0.0 or time_step <= 0.0:
        raise ValueError("Gaussian JKO inputs are invalid")
    return 0.5 * (previous_standard_deviation + sqrt(previous_standard_deviation**2 + 4.0 * time_step))


def fokker_planck_no_flux_step(
    density: Sequence[float],
    potential: Sequence[float],
    *,
    diffusion: float,
    grid_spacing: float,
    time_step: float,
) -> np.ndarray:
    rho = np.asarray(density, dtype=np.float64)
    energy = np.asarray(potential, dtype=np.float64)
    if rho.ndim != 1 or rho.size < 3 or energy.shape != rho.shape or np.any(~np.isfinite(rho)) or np.any(rho < 0.0) or np.any(~np.isfinite(energy)) or not all(isfinite(value) for value in (diffusion, grid_spacing, time_step)) or diffusion < 0.0 or grid_spacing <= 0.0 or time_step <= 0.0:
        raise ValueError("Fokker-Planck inputs are invalid")
    interior_flux = -diffusion * np.diff(rho) / grid_spacing - 0.5 * (rho[:-1] + rho[1:]) * np.diff(energy) / grid_spacing
    flux = np.r_[0.0, interior_flux, 0.0]
    updated = rho - time_step * np.diff(flux) / grid_spacing
    if np.min(updated) < -1e-12:
        raise ValueError("time step violates positivity for this explicit discretization")
    updated = np.maximum(updated, 0.0)
    original_mass = float(rho.sum() * grid_spacing)
    updated_mass = float(updated.sum() * grid_spacing)
    if updated_mass <= 0.0:
        raise ValueError("Fokker-Planck step lost all mass")
    return updated * (original_mass / updated_mass)


def free_energy_dissipation_rate(
    density: Sequence[float],
    first_variation: Sequence[float],
    grid_spacing: float,
) -> float:
    rho = np.asarray(density, dtype=np.float64)
    variation = np.asarray(first_variation, dtype=np.float64)
    if rho.ndim != 1 or variation.shape != rho.shape or rho.size < 3 or np.any(rho < 0.0) or np.any(~np.isfinite(rho)) or np.any(~np.isfinite(variation)) or not isfinite(grid_spacing) or grid_spacing <= 0.0:
        raise ValueError("dissipation inputs are invalid")
    gradient = np.gradient(variation, grid_spacing)
    return float(np.sum(rho * gradient**2) * grid_spacing)
