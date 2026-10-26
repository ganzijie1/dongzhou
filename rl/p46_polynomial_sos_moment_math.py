"""P46 polynomial, SOS Gram, moment, localizing, and flat-extension checks."""

from __future__ import annotations

from itertools import product
from typing import Mapping, Sequence

import numpy as np


Exponent = tuple[int, ...]


def monomial_powers(variable_count: int, degree: int) -> tuple[Exponent, ...]:
    if variable_count < 1 or degree < 0:
        raise ValueError("monomial dimensions are invalid")
    return tuple(power for power in product(range(degree + 1), repeat=variable_count) if sum(power) <= degree)


def evaluate_polynomial(coefficients: Mapping[Exponent, float], point: Sequence[float]) -> float:
    value = np.asarray(point, dtype=np.float64)
    if value.ndim != 1 or value.size == 0 or np.any(~np.isfinite(value)):
        raise ValueError("evaluation point is invalid")
    result = 0.0
    for exponent, coefficient in coefficients.items():
        if len(exponent) != value.size or any(power < 0 for power in exponent) or not np.isfinite(coefficient):
            raise ValueError("polynomial coefficient is invalid")
        result += float(coefficient) * float(np.prod(value ** np.asarray(exponent)))
    return result


def sos_gram_coefficients(gram: Sequence, basis: Sequence[Exponent]) -> dict[Exponent, float]:
    matrix = np.asarray(gram, dtype=np.float64)
    powers = tuple(tuple(value) for value in basis)
    if matrix.shape != (len(powers), len(powers)) or not np.allclose(matrix, matrix.T) or np.any(~np.isfinite(matrix)):
        raise ValueError("Gram matrix is invalid")
    if powers and any(len(power) != len(powers[0]) for power in powers):
        raise ValueError("basis exponents have inconsistent dimension")
    coefficients: dict[Exponent, float] = {}
    for row, first in enumerate(powers):
        for column, second in enumerate(powers):
            exponent = tuple(a + b for a, b in zip(first, second))
            coefficients[exponent] = coefficients.get(exponent, 0.0) + float(matrix[row, column])
    return coefficients


def sos_gram_residual(
    coefficients: Mapping[Exponent, float], gram: Sequence, basis: Sequence[Exponent]
) -> tuple[float, float]:
    reconstructed = sos_gram_coefficients(gram, basis)
    exponents = set(coefficients) | set(reconstructed)
    coefficient_residual = max((abs(float(coefficients.get(key, 0.0)) - reconstructed.get(key, 0.0)) for key in exponents), default=0.0)
    minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(np.asarray(gram, dtype=np.float64))))
    return coefficient_residual, minimum_eigenvalue


def moment_matrix(moments: Mapping[Exponent, float], basis: Sequence[Exponent]) -> np.ndarray:
    powers = tuple(tuple(value) for value in basis)
    if not powers or any(len(power) != len(powers[0]) for power in powers):
        raise ValueError("moment basis is invalid")
    matrix = np.empty((len(powers), len(powers)), dtype=np.float64)
    for row, first in enumerate(powers):
        for column, second in enumerate(powers):
            exponent = tuple(a + b for a, b in zip(first, second))
            if exponent not in moments or not np.isfinite(moments[exponent]):
                raise ValueError(f"missing finite moment {exponent}")
            matrix[row, column] = moments[exponent]
    return matrix


def localizing_matrix(
    moments: Mapping[Exponent, float], polynomial: Mapping[Exponent, float], basis: Sequence[Exponent]
) -> np.ndarray:
    powers = tuple(tuple(value) for value in basis)
    if (
        not powers
        or any(len(power) != len(powers[0]) for power in powers)
        or any(len(offset) != len(powers[0]) or not np.isfinite(coefficient) for offset, coefficient in polynomial.items())
    ):
        raise ValueError("localizing basis is empty")
    matrix = np.zeros((len(powers), len(powers)), dtype=np.float64)
    for row, first in enumerate(powers):
        for column, second in enumerate(powers):
            for offset, coefficient in polynomial.items():
                exponent = tuple(a + b + c for a, b, c in zip(first, second, offset))
                if exponent not in moments or not np.isfinite(moments[exponent]):
                    raise ValueError(f"missing moment {exponent}")
                matrix[row, column] += float(coefficient) * float(moments[exponent])
    return matrix


def numerical_rank(matrix: Sequence, *, tolerance: float = 1e-9) -> int:
    values = np.linalg.svd(np.asarray(matrix, dtype=np.float64), compute_uv=False)
    return int(np.count_nonzero(values > tolerance))


def flat_extension_holds(lower_moment_matrix: Sequence, higher_moment_matrix: Sequence, *, tolerance: float = 1e-9) -> bool:
    return numerical_rank(lower_moment_matrix, tolerance=tolerance) == numerical_rank(higher_moment_matrix, tolerance=tolerance)
