"""Attribution, global sensitivity, and extreme-value analysis."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import factorial, isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.stats import genextreme


Player = Hashable


@dataclass(frozen=True)
class ShapleyResult:
    values: Mapping[Player, float]
    baseline: float
    total_value: float

    @property
    def explained_value(self) -> float:
        return sum(self.values.values())


def exact_shapley_values(
    players: Sequence[Player],
    value: Callable[[frozenset[Player]], float],
    *,
    maximum_players: int = 15,
) -> ShapleyResult:
    """Compute exact cooperative-game Shapley values by subset enumeration."""

    ordered = tuple(players)
    if len(set(ordered)) != len(ordered):
        raise ValueError("Shapley players must be unique")
    if not ordered:
        baseline = float(value(frozenset()))
        if not isfinite(baseline):
            raise ValueError("coalition values must be finite")
        return ShapleyResult({}, baseline, baseline)
    if maximum_players <= 0 or len(ordered) > maximum_players:
        raise ValueError("exact Shapley player count exceeds configured limit")

    cache: dict[frozenset[Player], float] = {}

    def coalition_value(coalition: frozenset[Player]) -> float:
        if coalition not in cache:
            result = float(value(coalition))
            if not isfinite(result):
                raise ValueError("coalition values must be finite")
            cache[coalition] = result
        return cache[coalition]

    count = len(ordered)
    denominator = factorial(count)
    shapley: dict[Player, float] = {}
    for player in ordered:
        others = tuple(candidate for candidate in ordered if candidate != player)
        contribution = 0.0
        for size in range(count):
            weight = factorial(size) * factorial(count - size - 1) / denominator
            for subset in combinations(others, size):
                coalition = frozenset(subset)
                contribution += weight * (
                    coalition_value(coalition | {player})
                    - coalition_value(coalition)
                )
        shapley[player] = contribution
    baseline = coalition_value(frozenset())
    total = coalition_value(frozenset(ordered))
    return ShapleyResult(shapley, baseline, total)


@dataclass(frozen=True)
class SobolResult:
    first_order: Mapping[str, float]
    total_order: Mapping[str, float]
    output_variance: float
    samples: int


def sobol_sensitivity(
    model: Callable[[Mapping[str, float]], float],
    bounds: Mapping[str, tuple[float, float]],
    *,
    samples: int = 4096,
    seed: int | None = 2026,
) -> SobolResult:
    """Estimate first and total Sobol indices with Saltelli/Jansen estimators."""

    names = tuple(bounds)
    if not names:
        raise ValueError("Sobol analysis needs at least one parameter")
    if samples < 2:
        raise ValueError("Sobol analysis needs at least two samples")
    limits = np.asarray([bounds[name] for name in names], dtype=np.float64)
    if limits.shape != (len(names), 2) or np.any(~np.isfinite(limits)):
        raise ValueError("Sobol bounds must be finite lower/upper pairs")
    if np.any(limits[:, 1] <= limits[:, 0]):
        raise ValueError("Sobol upper bounds must exceed lower bounds")
    rng = np.random.default_rng(seed)
    unit_a = rng.random((samples, len(names)))
    unit_b = rng.random((samples, len(names)))
    lower = limits[:, 0]
    span = limits[:, 1] - lower
    matrix_a = lower + unit_a * span
    matrix_b = lower + unit_b * span

    def evaluate(matrix: np.ndarray) -> np.ndarray:
        results = np.asarray(
            [
                float(model(dict(zip(names, row))))
                for row in matrix
            ],
            dtype=np.float64,
        )
        if results.shape != (samples,) or np.any(~np.isfinite(results)):
            raise ValueError("Sobol model must return one finite scalar per sample")
        return results

    output_a = evaluate(matrix_a)
    output_b = evaluate(matrix_b)
    combined = np.concatenate((output_a, output_b))
    output_mean = float(np.mean(combined))
    variance = float(np.var(combined, ddof=1))
    if variance <= 1e-15:
        raise ValueError("Sobol indices are undefined for constant model output")
    first: dict[str, float] = {}
    total: dict[str, float] = {}
    for column, name in enumerate(names):
        mixed = matrix_a.copy()
        mixed[:, column] = matrix_b[:, column]
        output_mixed = evaluate(mixed)
        first[name] = float(
            np.mean((output_b - output_mean) * (output_mixed - output_a))
            / variance
        )
        total[name] = float(0.5 * np.mean((output_a - output_mixed) ** 2) / variance)
    return SobolResult(first, total, variance, samples)


@dataclass(frozen=True)
class ExtremeValueFit:
    shape: float
    location: float
    scale: float
    observations: int

    def return_level(self, return_period: float) -> float:
        period = float(return_period)
        if not isfinite(period) or period <= 1.0:
            raise ValueError("return period must be finite and greater than one")
        probability = 1.0 - 1.0 / period
        result = float(
            genextreme.ppf(probability, self.shape, loc=self.location, scale=self.scale)
        )
        if not isfinite(result):
            raise ValueError("requested return level is outside the fitted GEV support")
        return result


def fit_block_maxima(values: Sequence[float]) -> ExtremeValueFit:
    """Fit a generalized extreme-value law to independent block maxima."""

    observations = np.asarray(values, dtype=np.float64)
    if observations.ndim != 1 or observations.size < 8:
        raise ValueError("GEV fitting needs at least eight block maxima")
    if np.any(~np.isfinite(observations)) or np.ptp(observations) <= 1e-12:
        raise ValueError("GEV block maxima must be finite and non-constant")
    shape, location, scale = map(float, genextreme.fit(observations))
    if not all(map(isfinite, (shape, location, scale))) or scale <= 0.0:
        raise RuntimeError("GEV fit did not produce valid parameters")
    return ExtremeValueFit(shape, location, scale, int(observations.size))
