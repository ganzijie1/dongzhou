"""P69 assume-guarantee contracts, barrier checks, and risk composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class AssumeGuaranteeContract:
    assumption: frozenset[Hashable]
    guarantee: frozenset[Hashable]
    universe: frozenset[Hashable]

    def __post_init__(self) -> None:
        if not self.assumption <= self.universe or not self.guarantee <= self.universe:
            raise ValueError("contract sets must lie in the universe")

    @property
    def saturated_guarantee(self) -> frozenset[Hashable]:
        return (self.universe - self.assumption) | self.guarantee

    def accepts(self, behaviors: Iterable[Hashable]) -> bool:
        return set(behaviors) <= self.saturated_guarantee

    def refines(self, other: "AssumeGuaranteeContract") -> bool:
        if self.universe != other.universe:
            raise ValueError("contracts need the same universe")
        return other.assumption <= self.assumption and self.saturated_guarantee <= other.saturated_guarantee


def sampled_barrier_certificate(initial_values: Sequence[float], unsafe_values: Sequence[float], boundary_lie_derivatives: Sequence[float], *, tolerance: float = 1e-12) -> bool:
    initial = np.asarray(initial_values, dtype=np.float64)
    unsafe = np.asarray(unsafe_values, dtype=np.float64)
    lie = np.asarray(boundary_lie_derivatives, dtype=np.float64)
    if initial.size == 0 or unsafe.size == 0 or lie.size == 0 or np.any(~np.isfinite(np.concatenate((initial, unsafe, lie)))) or tolerance < 0.0:
        raise ValueError("barrier samples are invalid")
    return bool(np.all(initial <= tolerance) and np.all(unsafe > tolerance) and np.all(lie <= tolerance))


def union_risk_bound(component_risks: Sequence[float]) -> float:
    risks = np.asarray(component_risks, dtype=np.float64)
    if risks.ndim != 1 or np.any((risks < 0.0) | (risks > 1.0)):
        raise ValueError("risk bounds are invalid")
    return float(min(1.0, risks.sum()))


def independent_risk_bound(component_risks: Sequence[float]) -> float:
    risks = np.asarray(component_risks, dtype=np.float64)
    if risks.ndim != 1 or np.any((risks < 0.0) | (risks > 1.0)):
        raise ValueError("risk bounds are invalid")
    return float(1.0 - np.prod(1.0 - risks))


def conditional_contract_failure(assumption_failure: float, guarantee_failure_given_assumption: float) -> float:
    if not 0.0 <= assumption_failure <= 1.0 or not 0.0 <= guarantee_failure_given_assumption <= 1.0:
        raise ValueError("conditional risks are invalid")
    return float(assumption_failure + (1.0 - assumption_failure) * guarantee_failure_given_assumption)


def allocate_risk_budget(total: float, weights: Sequence[float]) -> np.ndarray:
    importance = np.asarray(weights, dtype=np.float64)
    if not 0.0 <= total <= 1.0 or importance.ndim != 1 or importance.size == 0 or np.any(importance < 0.0) or importance.sum() <= 0.0:
        raise ValueError("risk allocation inputs are invalid")
    return total * importance / importance.sum()
