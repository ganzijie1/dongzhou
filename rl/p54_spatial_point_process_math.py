"""P54 Poisson, Cox, DPP, coverage, and nearest-neighbor primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, gamma, pi
from typing import Sequence

import numpy as np


def unit_ball_volume(dimension: int) -> float:
    if not isinstance(dimension, int) or dimension <= 0:
        raise ValueError("dimension must be positive")
    return pi ** (dimension / 2.0) / gamma(dimension / 2.0 + 1.0)


def poisson_void_probability(intensity: float, volume: float) -> float:
    if not np.isfinite(intensity) or not np.isfinite(volume) or intensity < 0.0 or volume < 0.0:
        raise ValueError("Poisson inputs are invalid")
    return exp(-intensity * volume)


def poisson_nearest_distance_cdf(radius: float, intensity: float, *, dimension: int = 2) -> float:
    if not np.isfinite(radius) or radius < 0.0:
        raise ValueError("radius is invalid")
    return 1.0 - poisson_void_probability(intensity, unit_ball_volume(dimension) * radius**dimension)


def thomas_pair_correlation(radii: Sequence[float], parent_intensity: float, cluster_sigma: float) -> np.ndarray:
    radius = np.asarray(radii, dtype=np.float64)
    if radius.ndim != 1 or np.any(~np.isfinite(radius)) or np.any(radius < 0.0) or not np.isfinite(parent_intensity) or parent_intensity <= 0.0 or not np.isfinite(cluster_sigma) or cluster_sigma <= 0.0:
        raise ValueError("Thomas-process inputs are invalid")
    return 1.0 + np.exp(-(radius**2) / (4.0 * cluster_sigma**2)) / (4.0 * pi * parent_intensity * cluster_sigma**2)


@dataclass(frozen=True)
class DPPKernelAudit:
    eigenvalues: np.ndarray
    valid_marginal_kernel: bool
    expected_cardinality: float


def audit_dpp_marginal_kernel(kernel: Sequence, *, tolerance: float = 1e-10) -> DPPKernelAudit:
    matrix = np.asarray(kernel, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0 or np.any(~np.isfinite(matrix)) or not np.allclose(matrix, matrix.T):
        raise ValueError("DPP kernel is invalid")
    eigenvalues = np.linalg.eigvalsh(matrix)
    valid = bool(np.all(eigenvalues >= -tolerance) and np.all(eigenvalues <= 1.0 + tolerance))
    return DPPKernelAudit(eigenvalues, valid, float(np.trace(matrix)))


def dpp_pair_inclusion_probability(kernel: Sequence, first: int, second: int) -> float:
    matrix = np.asarray(kernel, dtype=np.float64)
    audit = audit_dpp_marginal_kernel(matrix)
    if not audit.valid_marginal_kernel or first == second or min(first, second) < 0 or max(first, second) >= matrix.shape[0]:
        raise ValueError("pair inclusion inputs are invalid")
    return float(matrix[first, first] * matrix[second, second] - matrix[first, second] ** 2)


def l_ensemble_subset_probability(l_kernel: Sequence, subset: Sequence[int]) -> float:
    matrix = np.asarray(l_kernel, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0 or np.any(~np.isfinite(matrix)) or not np.allclose(matrix, matrix.T) or np.min(np.linalg.eigvalsh(matrix)) < -1e-10:
        raise ValueError("L-ensemble kernel is invalid")
    indices = np.asarray(subset)
    if indices.ndim != 1 or np.any(indices != np.floor(indices)) or np.any(indices < 0) or np.any(indices >= matrix.shape[0]) or np.unique(indices).size != indices.size:
        raise ValueError("subset indices are invalid")
    indices = indices.astype(int)
    numerator = 1.0 if indices.size == 0 else float(np.linalg.det(matrix[np.ix_(indices, indices)]))
    denominator = float(np.linalg.det(np.eye(matrix.shape[0]) + matrix))
    return numerator / denominator


def nearest_neighbor_distances(points: Sequence) -> np.ndarray:
    coordinates = np.asarray(points, dtype=np.float64)
    if coordinates.ndim != 2 or coordinates.shape[0] < 2 or coordinates.shape[1] == 0 or np.any(~np.isfinite(coordinates)):
        raise ValueError("point coordinates are invalid")
    differences = coordinates[:, None, :] - coordinates[None, :, :]
    distances = np.linalg.norm(differences, axis=2)
    np.fill_diagonal(distances, np.inf)
    return np.min(distances, axis=1)


def contact_distances(points: Sequence, queries: Sequence) -> np.ndarray:
    coordinates = np.asarray(points, dtype=np.float64)
    query = np.asarray(queries, dtype=np.float64)
    if coordinates.ndim != 2 or coordinates.shape[0] == 0 or query.ndim != 2 or query.shape[1] != coordinates.shape[1] or np.any(~np.isfinite(coordinates)) or np.any(~np.isfinite(query)):
        raise ValueError("contact-distance inputs are invalid")
    return np.min(np.linalg.norm(query[:, None, :] - coordinates[None, :, :], axis=2), axis=1)
