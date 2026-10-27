"""P71 zonotopes, constrained zonotopes, support functions, and Taylor models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class Zonotope:
    center: np.ndarray
    generators: np.ndarray

    def __post_init__(self) -> None:
        center = np.asarray(self.center, dtype=np.float64)
        generators = np.asarray(self.generators, dtype=np.float64)
        if center.ndim != 1 or generators.ndim != 2 or generators.shape[0] != center.size or np.any(~np.isfinite(center)) or np.any(~np.isfinite(generators)):
            raise ValueError("zonotope inputs are invalid")
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "generators", generators)

    def affine_map(self, matrix: Sequence, offset: Sequence[float] | None = None) -> "Zonotope":
        transform = np.asarray(matrix, dtype=np.float64)
        shift = np.zeros(transform.shape[0]) if offset is None else np.asarray(offset, dtype=np.float64)
        if transform.ndim != 2 or transform.shape[1] != self.center.size or shift.shape != (transform.shape[0],):
            raise ValueError("affine map inputs are invalid")
        return Zonotope(transform @ self.center + shift, transform @ self.generators)

    def minkowski_sum(self, other: "Zonotope") -> "Zonotope":
        if self.center.shape != other.center.shape:
            raise ValueError("zonotope dimensions do not match")
        return Zonotope(self.center + other.center, np.concatenate((self.generators, other.generators), axis=1))

    def interval_hull(self) -> tuple[np.ndarray, np.ndarray]:
        radius = np.abs(self.generators).sum(axis=1)
        return self.center - radius, self.center + radius

    def support(self, direction: Sequence[float]) -> float:
        vector = np.asarray(direction, dtype=np.float64)
        if vector.shape != self.center.shape:
            raise ValueError("support direction is invalid")
        return float(vector @ self.center + np.abs(self.generators.T @ vector).sum())

    def reduce_box(self, maximum_generators: int) -> "Zonotope":
        if maximum_generators < self.center.size or maximum_generators >= self.generators.shape[1]:
            raise ValueError("generator budget is invalid")
        keep_count = maximum_generators - self.center.size
        scores = np.linalg.norm(self.generators, ord=1, axis=0)
        keep = np.argsort(scores)[::-1][:keep_count]
        reduce = np.setdiff1d(np.arange(self.generators.shape[1]), keep)
        box = np.diag(np.abs(self.generators[:, reduce]).sum(axis=1))
        return Zonotope(self.center, np.concatenate((self.generators[:, keep], box), axis=1))


@dataclass(frozen=True)
class ConstrainedZonotope:
    center: np.ndarray
    generators: np.ndarray
    constraint_matrix: np.ndarray
    constraint_vector: np.ndarray

    def __post_init__(self) -> None:
        center = np.asarray(self.center, dtype=np.float64)
        generators = np.asarray(self.generators, dtype=np.float64)
        matrix = np.asarray(self.constraint_matrix, dtype=np.float64)
        vector = np.asarray(self.constraint_vector, dtype=np.float64)
        if center.ndim != 1 or generators.ndim != 2 or generators.shape[0] != center.size or matrix.ndim != 2 or matrix.shape[1] != generators.shape[1] or vector.shape != (matrix.shape[0],):
            raise ValueError("constrained zonotope inputs are invalid")
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "generators", generators)
        object.__setattr__(self, "constraint_matrix", matrix)
        object.__setattr__(self, "constraint_vector", vector)

    def is_feasible(self) -> bool:
        result = linprog(np.zeros(self.generators.shape[1]), A_eq=self.constraint_matrix, b_eq=self.constraint_vector, bounds=[(-1.0, 1.0)] * self.generators.shape[1], method="highs")
        return bool(result.success)

    def intersect_hyperplane(self, normal: Sequence[float], value: float) -> "ConstrainedZonotope":
        vector = np.asarray(normal, dtype=np.float64)
        if vector.shape != self.center.shape or not np.isfinite(value):
            raise ValueError("hyperplane inputs are invalid")
        matrix = np.vstack((self.constraint_matrix, vector @ self.generators))
        target = np.append(self.constraint_vector, value - vector @ self.center)
        return ConstrainedZonotope(self.center, self.generators, matrix, target)


@dataclass(frozen=True)
class TaylorModel:
    coefficients: np.ndarray
    remainder: tuple[float, float]

    def __post_init__(self) -> None:
        coefficients = np.asarray(self.coefficients, dtype=np.float64)
        if coefficients.ndim != 1 or coefficients.size == 0 or self.remainder[0] > self.remainder[1] or np.any(~np.isfinite(coefficients)):
            raise ValueError("Taylor model inputs are invalid")
        object.__setattr__(self, "coefficients", coefficients)

    def add(self, other: "TaylorModel") -> "TaylorModel":
        size = max(self.coefficients.size, other.coefficients.size)
        coefficients = np.zeros(size)
        coefficients[: self.coefficients.size] += self.coefficients
        coefficients[: other.coefficients.size] += other.coefficients
        return TaylorModel(coefficients, (self.remainder[0] + other.remainder[0], self.remainder[1] + other.remainder[1]))

    def multiply(self, other: "TaylorModel", maximum_order: int) -> "TaylorModel":
        if maximum_order < 0:
            raise ValueError("Taylor order is invalid")
        full = np.convolve(self.coefficients, other.coefficients)
        kept = full[: maximum_order + 1]
        tail = float(np.abs(full[maximum_order + 1 :]).sum())
        self_bound = np.abs(self.coefficients).sum() + max(map(abs, self.remainder))
        other_bound = np.abs(other.coefficients).sum() + max(map(abs, other.remainder))
        polynomial_bound = np.abs(self.coefficients).sum() * np.abs(other.coefficients).sum()
        remainder = max(0.0, self_bound * other_bound - polynomial_bound) + tail
        return TaylorModel(kept, (-remainder, remainder))

    def evaluate_interval(self, domain: tuple[float, float]) -> tuple[float, float]:
        if domain[0] > domain[1]:
            raise ValueError("Taylor domain is invalid")
        interval = np.array([0.0, 0.0])
        for order, coefficient in enumerate(self.coefficients):
            candidates = [domain[0] ** order, domain[1] ** order]
            if domain[0] <= 0.0 <= domain[1] and order > 0:
                candidates.append(0.0)
            term = np.sort(coefficient * np.asarray(candidates))[[0, -1]]
            interval += term
        return float(interval[0] + self.remainder[0]), float(interval[1] + self.remainder[1])


def linear_reachable_step(state: Zonotope, transition: Sequence, control: Zonotope, input_matrix: Sequence, disturbance: Zonotope) -> Zonotope:
    propagated = state.affine_map(transition)
    actuated = control.affine_map(input_matrix)
    return propagated.minkowski_sum(actuated).minkowski_sum(disturbance)
