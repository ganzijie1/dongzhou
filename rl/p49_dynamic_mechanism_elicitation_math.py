"""P49 dynamic mechanism-design, participation, and information-elicitation tools."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np


def promised_utility(
    current_utility: Sequence[float],
    continuation_utility: Sequence[float],
    transition_probabilities: Sequence[float],
    *,
    discount: float,
) -> float:
    current = np.asarray(current_utility, dtype=np.float64)
    continuation = np.asarray(continuation_utility, dtype=np.float64)
    probabilities = np.asarray(transition_probabilities, dtype=np.float64)
    if current.shape != continuation.shape or current.shape != probabilities.shape or current.ndim != 1 or np.any(~np.isfinite(current)) or np.any(~np.isfinite(continuation)) or np.any(~np.isfinite(probabilities)) or np.any(probabilities < 0.0) or not np.isclose(probabilities.sum(), 1.0) or not isfinite(discount) or not 0.0 <= discount <= 1.0:
        raise ValueError("promised-utility inputs are invalid")
    return float(probabilities @ (current + discount * continuation))


@dataclass(frozen=True)
class IncentiveAudit:
    truthful_utilities: np.ndarray
    best_deviation_utilities: np.ndarray
    regrets: np.ndarray
    incentive_compatible: bool


def dynamic_ic_audit(
    utilities_by_type_and_report: Sequence,
    truthful_reports: Sequence[int] | None = None,
    *,
    tolerance: float = 1e-10,
) -> IncentiveAudit:
    utilities = np.asarray(utilities_by_type_and_report, dtype=np.float64)
    if utilities.ndim != 2 or utilities.shape[0] == 0 or np.any(~np.isfinite(utilities)):
        raise ValueError("utility matrix is invalid")
    reports = np.arange(utilities.shape[0]) if truthful_reports is None else np.asarray(truthful_reports)
    if reports.shape != (utilities.shape[0],) or np.any(reports != np.floor(reports)) or np.any(reports < 0) or np.any(reports >= utilities.shape[1]):
        raise ValueError("truthful reports are invalid")
    reports = reports.astype(int)
    truthful = utilities[np.arange(utilities.shape[0]), reports]
    best = np.max(utilities, axis=1)
    regrets = np.maximum(best - truthful, 0.0)
    return IncentiveAudit(truthful, best, regrets, bool(np.all(regrets <= tolerance)))


def participation_audit(promised_utilities: Sequence[float], outside_options: Sequence[float], *, tolerance: float = 1e-10) -> tuple[np.ndarray, bool]:
    promised = np.asarray(promised_utilities, dtype=np.float64)
    outside = np.asarray(outside_options, dtype=np.float64)
    if promised.shape != outside.shape or promised.ndim != 1 or np.any(~np.isfinite(promised)) or np.any(~np.isfinite(outside)):
        raise ValueError("participation inputs are invalid")
    slack = promised - outside
    return slack, bool(np.all(slack >= -tolerance))


def dynamic_pivot_payment(welfare_without_agent: float, other_agents_welfare_with_agent: float) -> float:
    if not isfinite(welfare_without_agent) or not isfinite(other_agents_welfare_with_agent):
        raise ValueError("pivot welfare values must be finite")
    return welfare_without_agent - other_agents_welfare_with_agent


def logarithmic_score(reported_probability: float, outcome: int, *, floor: float = 1e-15) -> float:
    if not 0.0 <= reported_probability <= 1.0 or outcome not in (0, 1) or not 0.0 < floor < 0.5:
        raise ValueError("log-score inputs are invalid")
    probability = reported_probability if outcome == 1 else 1.0 - reported_probability
    return float(np.log(max(probability, floor)))


def brier_score(reported_probability: float, outcome: int) -> float:
    if not 0.0 <= reported_probability <= 1.0 or outcome not in (0, 1):
        raise ValueError("Brier-score inputs are invalid")
    return -float((reported_probability - outcome) ** 2)


def expected_binary_score(true_probability: float, report: float, *, rule: str = "brier") -> float:
    if not 0.0 <= true_probability <= 1.0:
        raise ValueError("true probability is invalid")
    scorer = brier_score if rule == "brier" else logarithmic_score if rule == "log" else None
    if scorer is None:
        raise ValueError("unknown scoring rule")
    return true_probability * scorer(report, 1) + (1.0 - true_probability) * scorer(report, 0)


def peer_prediction_payments(
    reports: Sequence[int], conditional_peer_beliefs: Sequence, *, rule: str = "log"
) -> np.ndarray:
    values = np.asarray(reports)
    beliefs = np.asarray(conditional_peer_beliefs, dtype=np.float64)
    if values.ndim != 1 or values.size < 2 or np.any(values != np.floor(values)) or np.any(values < 0) or beliefs.ndim != 2 or beliefs.shape[0] != beliefs.shape[1] or np.any(values >= beliefs.shape[0]) or np.any(~np.isfinite(beliefs)) or np.any(beliefs < 0.0) or not np.allclose(beliefs.sum(axis=1), 1.0):
        raise ValueError("peer-prediction inputs are invalid")
    values = values.astype(int)
    payments = np.empty(values.size)
    for index, report in enumerate(values):
        peer_report = values[(index + 1) % values.size]
        probability = float(beliefs[report, peer_report])
        if rule == "log":
            payments[index] = np.log(max(probability, 1e-15))
        elif rule == "brier":
            forecast = beliefs[report]
            target = np.zeros(beliefs.shape[1])
            target[peer_report] = 1.0
            payments[index] = -float(np.sum((forecast - target) ** 2))
        else:
            raise ValueError("unknown scoring rule")
    return payments
