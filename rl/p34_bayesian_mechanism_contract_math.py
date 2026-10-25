"""P34 finite Bayesian mechanisms, VCG/Myerson auctions, and contracts."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class VCGResult:
    outcome: int
    social_welfare: float
    payments: np.ndarray
    utilities: np.ndarray


def vcg_clarke_pivot(valuations: Sequence[Sequence[float]]) -> VCGResult:
    """Efficient finite-outcome VCG mechanism with Clarke pivot payments."""

    values = np.asarray(valuations, dtype=np.float64)
    if values.ndim != 2 or min(values.shape) == 0 or np.any(~np.isfinite(values)):
        raise ValueError("VCG valuations must be a finite player-by-outcome matrix")
    welfare = values.sum(axis=0)
    outcome = int(np.argmax(welfare))
    payments = np.empty(values.shape[0])
    for player in range(values.shape[0]):
        others = welfare - values[player]
        payments[player] = float(np.max(others) - others[outcome])
    utilities = values[:, outcome] - payments
    return VCGResult(outcome, float(welfare[outcome]), payments, utilities)


@dataclass(frozen=True)
class MyersonAuctionResult:
    winner: int | None
    allocation: np.ndarray
    payments: np.ndarray
    revenue: float


def myerson_iid_single_item_auction(
    bids: Sequence[float], *, reserve: float
) -> MyersonAuctionResult:
    """Myerson auction for i.i.d. regular values: second price plus reserve."""

    values = np.asarray(bids, dtype=np.float64)
    if (
        values.ndim != 1
        or values.size == 0
        or np.any(~np.isfinite(values))
        or np.any(values < 0.0)
        or not isfinite(reserve)
        or reserve < 0.0
    ):
        raise ValueError("auction bids or reserve are invalid")
    allocation = np.zeros(values.size)
    payments = np.zeros(values.size)
    winner = int(np.argmax(values))
    if values[winner] < reserve:
        return MyersonAuctionResult(None, allocation, payments, 0.0)
    allocation[winner] = 1.0
    competitors = np.delete(values, winner)
    second = float(np.max(competitors)) if competitors.size else 0.0
    payments[winner] = max(reserve, second)
    return MyersonAuctionResult(winner, allocation, payments, float(payments[winner]))


def regular_virtual_value(
    values: Sequence[float], cdf: Sequence[float], density: Sequence[float]
) -> np.ndarray:
    """Myerson virtual value phi(v)=v-(1-F(v))/f(v)."""

    value = np.asarray(values, dtype=np.float64)
    distribution = np.asarray(cdf, dtype=np.float64)
    pdf = np.asarray(density, dtype=np.float64)
    if (
        value.ndim != 1
        or value.size == 0
        or distribution.shape != value.shape
        or pdf.shape != value.shape
        or np.any(~np.isfinite(value))
        or np.any(~np.isfinite(distribution))
        or np.any(~np.isfinite(pdf))
        or np.any(distribution < 0.0)
        or np.any(distribution > 1.0)
        or np.any(pdf <= 0.0)
    ):
        raise ValueError("virtual-value inputs are invalid")
    return value - (1.0 - distribution) / pdf


@dataclass(frozen=True)
class MechanismAudit:
    minimum_dsic_slack: float
    minimum_bic_slack: float
    minimum_interim_ir_slack: float
    expected_revenue: float
    dsic: bool
    bic: bool
    interim_ir: bool


def audit_two_player_direct_mechanism(
    prior: Sequence,
    allocation: Sequence,
    payments: Sequence,
    valuations: tuple[Sequence, Sequence],
    *,
    outside_options: tuple[Sequence[float], Sequence[float]] | None = None,
    tolerance: float = 1e-10,
) -> MechanismAudit:
    """Audit DSIC, BIC, and interim IR for a finite direct mechanism.

    Positive payments mean money paid by a player to the mechanism.
    """

    type_prior = np.asarray(prior, dtype=np.float64)
    outcome_rule = np.asarray(allocation, dtype=np.float64)
    transfers = np.asarray(payments, dtype=np.float64)
    first_value = np.asarray(valuations[0], dtype=np.float64)
    second_value = np.asarray(valuations[1], dtype=np.float64)
    if type_prior.ndim != 2 or min(type_prior.shape) == 0:
        raise ValueError("prior must have two type axes")
    first_types, second_types = type_prior.shape
    if outcome_rule.ndim != 3 or outcome_rule.shape[:2] != type_prior.shape:
        raise ValueError("allocation shape is invalid")
    outcomes = outcome_rule.shape[2]
    if (
        transfers.shape != (2, first_types, second_types)
        or first_value.shape != (first_types, outcomes)
        or second_value.shape != (second_types, outcomes)
        or np.any(~np.isfinite(type_prior))
        or np.any(type_prior < 0.0)
        or not np.isclose(type_prior.sum(), 1.0)
        or np.any(~np.isfinite(outcome_rule))
        or np.any(outcome_rule < 0.0)
        or not np.allclose(outcome_rule.sum(axis=2), 1.0)
        or np.any(~np.isfinite(transfers))
        or np.any(~np.isfinite(first_value))
        or np.any(~np.isfinite(second_value))
        or tolerance < 0.0
    ):
        raise ValueError("mechanism arrays are invalid")
    if outside_options is None:
        outside = (np.zeros(first_types), np.zeros(second_types))
    else:
        outside = tuple(np.asarray(value, dtype=np.float64) for value in outside_options)
        if (
            outside[0].shape != (first_types,)
            or outside[1].shape != (second_types,)
            or np.any(~np.isfinite(outside[0]))
            or np.any(~np.isfinite(outside[1]))
        ):
            raise ValueError("outside options are invalid")

    values = (first_value, second_value)

    def utility(player: int, true_type: int, report: int, other_report: int) -> float:
        if player == 0:
            expected_value = outcome_rule[report, other_report] @ values[0][true_type]
            return float(expected_value - transfers[0, report, other_report])
        expected_value = outcome_rule[other_report, report] @ values[1][true_type]
        return float(expected_value - transfers[1, other_report, report])

    dsic_slacks = []
    bic_slacks = []
    ir_slacks = []
    for player, own_types in enumerate((first_types, second_types)):
        other_types = second_types if player == 0 else first_types
        for true_type in range(own_types):
            own_mass = (
                type_prior[true_type].sum()
                if player == 0
                else type_prior[:, true_type].sum()
            )
            if own_mass <= 0.0:
                continue
            conditional = (
                type_prior[true_type] / own_mass
                if player == 0
                else type_prior[:, true_type] / own_mass
            )
            truthful_interim = sum(
                conditional[other] * utility(player, true_type, true_type, other)
                for other in range(other_types)
            )
            ir_slacks.append(truthful_interim - outside[player][true_type])
            for report in range(own_types):
                bic_slacks.append(
                    truthful_interim
                    - sum(
                        conditional[other] * utility(player, true_type, report, other)
                        for other in range(other_types)
                    )
                )
                for other in range(other_types):
                    dsic_slacks.append(
                        utility(player, true_type, true_type, other)
                        - utility(player, true_type, report, other)
                    )
    expected_revenue = float(np.sum(type_prior * transfers.sum(axis=0)))
    minimum_dsic = float(min(dsic_slacks, default=0.0))
    minimum_bic = float(min(bic_slacks, default=0.0))
    minimum_ir = float(min(ir_slacks, default=0.0))
    return MechanismAudit(
        minimum_dsic,
        minimum_bic,
        minimum_ir,
        expected_revenue,
        minimum_dsic >= -tolerance,
        minimum_bic >= -tolerance,
        minimum_ir >= -tolerance,
    )


@dataclass(frozen=True)
class PrincipalAgentContract:
    target_action: int
    wages: np.ndarray
    agent_utility: float
    principal_utility: float
    incentive_slacks: np.ndarray


def optimal_hidden_action_contract(
    outcome_probabilities: Sequence,
    action_costs: Sequence[float],
    principal_outcome_values: Sequence[float],
    *,
    outside_option: float = 0.0,
    minimum_wage: float = 0.0,
) -> PrincipalAgentContract:
    """Enumerate induced actions and solve the least-cost limited-liability contract."""

    probabilities = np.asarray(outcome_probabilities, dtype=np.float64)
    costs = np.asarray(action_costs, dtype=np.float64)
    principal_values = np.asarray(principal_outcome_values, dtype=np.float64)
    if probabilities.ndim != 2 or min(probabilities.shape) == 0:
        raise ValueError("outcome probabilities must be action by outcome")
    actions, outcomes = probabilities.shape
    if (
        costs.shape != (actions,)
        or principal_values.shape != (outcomes,)
        or np.any(~np.isfinite(probabilities))
        or np.any(probabilities < 0.0)
        or not np.allclose(probabilities.sum(axis=1), 1.0)
        or np.any(~np.isfinite(costs))
        or np.any(~np.isfinite(principal_values))
        or not isfinite(outside_option)
        or not isfinite(minimum_wage)
    ):
        raise ValueError("contract inputs are invalid")
    best = None
    for target in range(actions):
        constraints = []
        rhs = []
        for alternative in range(actions):
            if alternative == target:
                continue
            constraints.append(-(probabilities[target] - probabilities[alternative]))
            rhs.append(-(costs[target] - costs[alternative]))
        constraints.append(-probabilities[target])
        rhs.append(-(outside_option + costs[target]))
        solved = linprog(
            probabilities[target],
            A_ub=np.asarray(constraints),
            b_ub=np.asarray(rhs),
            bounds=[(minimum_wage, None)] * outcomes,
            method="highs",
        )
        if not solved.success:
            continue
        wages = solved.x
        utilities = probabilities @ wages - costs
        slacks = utilities[target] - utilities
        principal_utility = float(probabilities[target] @ (principal_values - wages))
        candidate = PrincipalAgentContract(
            target,
            wages,
            float(utilities[target]),
            principal_utility,
            slacks,
        )
        if best is None or candidate.principal_utility > best.principal_utility:
            best = candidate
    if best is None:
        raise RuntimeError("no action can be induced by a feasible contract")
    return best
